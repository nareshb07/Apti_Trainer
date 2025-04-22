      
import re
import json
import time
from django.core.management.base import BaseCommand
from django.utils.text import slugify
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError  # More specific API error
from aptitude.models import Topic, Level, TutorialPart
from dotenv import load_dotenv
import os

load_dotenv()

class Command(BaseCommand):
    help = 'Generate comprehensive tutorial parts for specific topics/levels.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--topic',
            type=str,
            help='Slug of the specific topic to generate tutorials for.'
        )
        parser.add_argument(
            '--level',
            type=str,
            help='Slug of the specific level to generate tutorials for.'
        )
        parser.add_argument(
            '--overwrite',
            action='store_true', # Makes it a boolean flag
            help='Overwrite existing tutorial parts even if marked complete.'
        )
        parser.add_argument(
            '--delay',
            type=int,
            default=2, # Default delay of 2 seconds
            help='Delay in seconds between API calls to avoid rate limits.'
        )

    def _format_examples(self, examples):
        """Format worked examples for database storage"""
        formatted = []
        for i, example in enumerate(examples, 1):
            # Basic validation for example structure
            if not all(k in example for k in ['problem', 'solution_steps', 'final_answer']):
                 self.stdout.write(self.style.WARNING(f"Skipping malformed example {i}: Missing keys."))
                 continue # Skip this malformed example

            example_text = (
                f"EXAMPLE {i}:\n"
                f"Problem: {example['problem']}\n\n"
                "Solution Steps:\n" +
                "\n".join(f"- {step}" for step in example['solution_steps']) +
                f"\n\nAnswer: {example['final_answer']}"
            )
            if example.get('visualization'):
                example_text += f"\n\nVisualization Tip: {example['visualization']}"
            formatted.append(example_text)
        return "\n\n" + "\n\n".join(formatted) + "\n"

    def _validate_json_structure(self, data):
        """Basic validation for the expected JSON structure from the AI."""
        if not isinstance(data, dict):
            raise ValueError("Response is not a JSON object (dictionary).")
        if 'parts' not in data:
            raise ValueError("JSON object is missing the required 'parts' key.")
        if not isinstance(data['parts'], list):
            raise ValueError("The 'parts' key does not contain a list.")

        for i, part in enumerate(data['parts']):
            if not isinstance(part, dict):
                raise ValueError(f"Item {i} in 'parts' list is not a dictionary.")
            required_part_keys = ['part_name', 'key_concepts', 'step_by_step_guide']
            if not all(key in part for key in required_part_keys):
                raise ValueError(f"Part {i} is missing one or more required keys: {required_part_keys}.")
            
            step_guide = part['step_by_step_guide']
            if not isinstance(step_guide, dict):
                 raise ValueError(f"Part {i} 'step_by_step_guide' is not a dictionary.")
            if 'worked_examples' not in step_guide or not isinstance(step_guide['worked_examples'], list):
                 raise ValueError(f"Part {i} 'step_by_step_guide' is missing 'worked_examples' list.")
            if 'approach' not in step_guide:
                 raise ValueError(f"Part {i} 'step_by_step_guide' is missing 'approach' key.")
        # Add more checks as needed for other keys/nested structures

    def parse_response(self, response_text):
      """Improved JSON parsing that handles markdown, validates structure, and escapes LaTeX."""
      json_str = response_text # Start with the raw text
      try:
          # Remove potential whitespace and markdown code fences
          json_str = response_text.strip()
          if json_str.startswith('```json'):
              json_str = json_str[7:-3].strip()
          elif json_str.startswith('```'):
              json_str = json_str[3:-3].strip()

          # Attempt to parse the JSON
          data = json.loads(json_str)

          # Validate the basic structure BEFORE fixing LaTeX
          self._validate_json_structure(data)

          # Recursive function to fix LaTeX expressions in the parsed data
          def fix_latex_strings(obj):
              if isinstance(obj, str):
                  # Replace single backslashes in LaTeX with double backslashes
                  # Handles cases like \frac, \times, \(\), etc.
                  # Ensures already double-slashed \\( \\) are preserved.
                  return re.sub(
                      r'(?<!\\)\\(?!\\)',  # Match single backslashes not preceded/followed by another backslash
                      r'\\\\',
                      obj
                  )
              elif isinstance(obj, dict):
                  return {k: fix_latex_strings(v) for k, v in obj.items()}
              elif isinstance(obj, list):
                  return [fix_latex_strings(item) for item in obj]
              return obj

          # Apply LaTeX fixes
          return fix_latex_strings(data)

      except json.JSONDecodeError as e:
          debug_file = f"failed_response_{int(time.time())}_decode.txt"
          with open(debug_file, 'w', encoding='utf-8') as f:
              f.write(f"Original Response:\n---\n{response_text}\n---\n")
              f.write(f"Attempted Cleaned JSON String:\n---\n{json_str}\n---\n")
          raise ValueError(f"JSON decoding failed. Debug info saved to {debug_file}. Error: {str(e)} at line {e.lineno} col {e.colno}")
      except ValueError as e: # Catch validation errors
          debug_file = f"failed_response_{int(time.time())}_validation.txt"
          with open(debug_file, 'w', encoding='utf-8') as f:
              f.write(f"Original Response:\n---\n{response_text}\n---\n")
              f.write(f"Parsed JSON (before validation failure):\n---\n{json_str}\n---\n") # Show the potentially malformed JSON
          raise ValueError(f"JSON structure validation failed. Debug info saved to {debug_file}. Error: {str(e)}")


    def handle(self, *args, **options):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-1.5-flash') # Or your preferred model

        # Filter topics based on command-line argument
        topics_qs = Topic.objects.all()
        if options['topic']:
            topics_qs = topics_qs.filter(slug=options['topic'])
            if not topics_qs.exists():
                self.stdout.write(self.style.ERROR(f"Topic with slug '{options['topic']}' not found."))
                return

        # Filter levels based on command-line argument
        levels_qs = Level.objects.all()
        if options['level']:
            levels_qs = levels_qs.filter(slug=options['level'])
            if not levels_qs.exists():
                self.stdout.write(self.style.ERROR(f"Level with slug '{options['level']}' not found."))
                return

        overwrite = options['overwrite']
        api_delay = options['delay']

        total_combinations = topics_qs.count() * levels_qs.count()
        current_combination = 0

        for topic in topics_qs:
            for level in levels_qs:
                current_combination += 1
                self.stdout.write(f"\n({current_combination}/{total_combinations}) 📚 Generating {topic.name} ({level.name})...")

                try:
                    prompt = self._build_master_prompt(topic, level)
                    response = model.generate_content(prompt)

                    # Directly use response.text (should be unicode)
                    response_text = response.text

                    tutorial_data = self.parse_response(response_text)
                    self._create_tutorial_parts(topic, level, tutorial_data, overwrite)

                except GoogleAPIError as e:
                    self.stdout.write(self.style.ERROR(f"❌ API Error for {topic.name} {level.name}: {str(e)}"))
                    # Consider adding retry logic or longer sleep here for specific API errors like rate limits
                except ValueError as e: # Catch parsing/validation errors
                    self.stdout.write(self.style.ERROR(f"❌ Data Processing Error for {topic.name} {level.name}: {str(e)}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Unexpected Failed {topic.name} {level.name}: {type(e).__name__} - {str(e)}"))
                    # Optionally log the full traceback here for unexpected errors
                    import traceback
                    traceback.print_exc() # Prints traceback to stderr

                finally:
                    # Add a delay between processing each topic/level combination
                    if total_combinations > 1 and current_combination < total_combinations:
                         self.stdout.write(f"--- Waiting {api_delay}s before next request ---")
                         time.sleep(api_delay)


      
          
    def _build_master_prompt(self, topic, level):
      """Constructs the precise prompt for Gemini AI with strict formatting rules"""
      return f"""Generate a comprehensive tutorial for {topic.name} at {level.name} level.

ABSOLUTELY CRITICAL INSTRUCTIONS - FOLLOW EXACTLY:

1. RESPONSE FORMAT:
   - Your *entire* response MUST be ONLY a single JSON object.
   - Start the JSON block IMMEDIATELY with ```json and end it IMMEDIATELY with ```.
   - NO text, explanations, apologies, summaries, or anything else before ```json or after ```.
   - The JSON content MUST start with {{ and end with }}.

2. LATEX FORMATTING (CRITICAL FOR VALID JSON):
   - Inside JSON string values, ALL LaTeX commands AND math delimiters MUST use DOUBLE BACKSLASHES (`\\\\`).
   - EXAMPLES: `\\\\frac{{n}}{{d}}`, `\\\\sqrt{{x}}`, `\\\\times`, `\\\\pm`, `\\\\(`. `\\\\)`. `\\\\ [`. `\\\\ ]`.
   - SINGLE BACKSLASHES (`\\`) for LaTeX WILL CAUSE an INVALID JSON error. DO NOT USE THEM.
   - Correct example within a JSON string: "Calculate \\\\(\\\\frac{{1}}{{2}}\\\\) times 100."
   - Incorrect (causes error): "Calculate \(\frac{1}{2}\) times 100."
   - For percentage signs *in text* (not LaTeX math): Use `\\%` (e.g., "This is 50\\% effective.")

3. CONTENT STRUCTURE (MANDATORY):
   - Top-level key: "parts" (list of objects).
   - Each part object *MUST* have: 'part_name' (string), 'key_concepts' (list of strings), 'step_by_step_guide' (object).
   - Each 'step_by_step_guide' object *MUST* have: 'approach' (string), 'worked_examples' (list of objects).
   - Each 'worked_examples' object *MUST* have: 'problem' (string), 'solution_steps' (list of strings), 'final_answer' (string).
   - Include 2-3 worked examples per part, each with 3-5 steps.
   - Optional keys (use if relevant): 'learning_roadmap', 'common_pitfalls', 'pro_tips' (in part object); 'visualization' (in worked_example object).

4. JSON STRING CONTENT & ESCAPING:
   - Standard JSON string escaping MUST be used: `\\"` for double quotes, `\\\\` for literal backslashes (as required for LaTeX above), `\\n` for newlines.
   - Do NOT use raw newlines that break the JSON structure. Use `\\n` within strings where a line break is intended in the text content.

EXAMPLE STRUCTURE (Illustrates rules - Pay attention to `\\\\`):
```json
{{
  "parts": [
    {{
      "part_name": "Advanced Topic Example",
      "key_concepts": [
        "Concept one explanation.",
        "Concept two involving \\\\(\\\\sqrt{{a^2 + b^2}}\\\\)."
      ],
      "step_by_step_guide": {{
        "approach": "General approach description.\\nFollow these steps using \\\\(\\\\alpha\\\\) and \\\\(\\\\beta\\\\).",
        "worked_examples": [
          {{
            "problem": "Solve for x: \\\\(x^2 = 9\\\\)",
            "solution_steps": [
              "Take the square root: \\\\(x = \\\\pm\\\\sqrt{{9}}\\\\)",
              "Calculate the roots: \\\\(x = 3\\\\) or \\\\(x = -3\\\\)"
            ],
            "final_answer": "\\\\(\\\\boxed{{x = \\\\pm 3}}\\\\)"
          }}
        ]
      }},
      "common_pitfalls": [
        "Forgetting the negative root when using \\\\(\\\\pm\\\\sqrt{{...}}\\\\).",
        "Incorrectly escaping LaTeX (using single '\\'). MUST USE '\\\\'."
      ]
    }}
  ]
}}

    

IGNORE_WHEN_COPYING_START
Use code with caution. Python
IGNORE_WHEN_COPYING_END

Now, generate the tutorial content strictly following ALL the above critical instructions, especially the DOUBLE BACKSLASH (\\\\) rule for ALL LaTeX, for the topic "{topic.name}" at the "{level.name}" level. Ensure the output is ONLY the JSON within json markers. Failure to use \\\\ for LaTeX will result in invalid JSON.
"""
    
    def _create_tutorial_parts(self, topic, level, data, overwrite=False):
        """Save tutorial parts to the database, respecting the overwrite flag."""
        saved_count = 0
        skipped_count = 0
        failed_count = 0

        for order, part_data in enumerate(data.get('parts', []), start=1):
            part_name = part_data.get('part_name', f"Part {order}") # Default name if missing
            part_slug = slugify(f"{topic.slug}-{level.slug}-{part_name}")

            try:
                # Try to get the object, or prepare to create it
                obj, created = TutorialPart.objects.get_or_create(
                    topic=topic,
                    level=level,
                    slug=part_slug,
                    # Only include identifying fields in get_or_create
                )

                # Decide whether to update based on 'created' or 'overwrite' flag
                if created or overwrite:
                    obj.part_name = part_name
                    obj.key_concepts = "\n".join(part_data.get('key_concepts', []))
                    obj.preparation_strategy = "\n".join(part_data.get('learning_roadmap', [])) # Renamed key? Check model
                    
                    # Safely access nested structure for examples
                    step_guide = part_data.get('step_by_step_guide', {})
                    obj.example_problems = self._format_examples(step_guide.get('worked_examples', []))
                    obj.explanations = step_guide.get('approach', '') # Provide default empty string

                    obj.common_pitfalls = "\n".join(part_data.get('common_pitfalls', []))
                    obj.quick_tips = "\n".join(part_data.get('pro_tips', []))
                    obj.order = order
                    obj.is_complete = True # Mark as complete upon generation/update
                    obj.save()

                    msg = "Created" if created else "Overwritten"
                    self.stdout.write(self.style.SUCCESS(f"  ✅ {msg} part: {part_name}"))
                    saved_count += 1
                else:
                    # Object exists and overwrite is False
                    self.stdout.write(f"  ⏭️ Skipped existing part (use --overwrite to update): {part_name}")
                    skipped_count += 1

            except Exception as e:
                failed_count += 1
                self.stdout.write(self.style.ERROR(f"  ❌ Failed to save part {part_name}: {type(e).__name__} - {str(e)}"))
                continue # Continue to the next part

        summary_style = self.style.SUCCESS if failed_count == 0 else self.style.WARNING
        self.stdout.write(summary_style(
            f"  📊 Summary for {level.name}: {saved_count} Saved/Overwritten, {skipped_count} Skipped, {failed_count} Failed."
        ))