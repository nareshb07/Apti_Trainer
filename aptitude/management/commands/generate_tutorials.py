      
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

    # --- Replace the existing parse_response method in your Command class ---

    def _extract_json_block(self, text):
        """Attempts to extract the JSON string between markdown fences."""
        # 1. Try standard ```json ... ```
        # Using non-greedy match {.*?} to handle potential nested structures better if LLM adds junk after JSON
        match = re.search(r"```json\s*({.*?})\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # 2. Try generic ``` ... ```
        match = re.search(r"```\s*({.*?})\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # 3. Fallback: Try finding the first '{' and last '}'
        start_index = text.find('{')
        end_index = text.rfind('}')
        if start_index != -1 and end_index != -1 and end_index > start_index:
            potential_json = text[start_index : end_index + 1].strip()
            if potential_json.startswith('{') and potential_json.endswith('}'):
                 # Basic check for plausibility - increase confidence it's the main object
                 if '"parts":' in potential_json:
                    self.stdout.write(self.style.WARNING("  ⚠️ Used fallback JSON extraction (finding first { and last })."))
                    return potential_json

        # 4. If nothing is found
        return None

    def _clean_invalid_escapes(self, json_str):
        """
        Attempts to clean known invalid JSON escape sequences
        that the LLM might incorrectly generate based on LaTeX habits.
        """
        # Replace \% with %
        cleaned_str = json_str.replace(r'\%', '%')
        # Replace \$ with $
        cleaned_str = cleaned_str.replace(r'\$', '$')
        # Replace \ ` (backslash-space) with space
        cleaned_str = cleaned_str.replace(r'\ ', ' ')
        # Add any other specific invalid sequences you observe, e.g.:
        # cleaned_str = cleaned_str.replace(r'\&', '&') 
        
        if cleaned_str != json_str:
        # FIX HERE: Escape the backslashes for the output message
            self.stdout.write(self.style.WARNING(r"  ⚠️ Cleaned potential invalid escape sequences (like \\%, \\$, \\ , etc.) before parsing.")) 
        # Alternatively use an r-string: self.stdout.write(self.style.WARNING(r"  ⚠️ Cleaned potential invalid escape sequences (\%, \$, \ , etc.) before parsing."))
        return cleaned_str

    def parse_response(self, response_text):
        """
        Extracts, cleans common invalid escapes, parses, and validates JSON from LLM response.
        """
        original_response = response_text # Keep for debugging
        extracted_json_str = None # To store the extracted part
        cleaned_json_str = None # To store the cleaned part

        try:
            # Step 1: Extract the JSON block using robust methods
            extracted_json_str = self._extract_json_block(original_response)

            if not extracted_json_str:
                raise ValueError("Could not find JSON block within markdown fences or via fallback.")

            # Step 2: Handle potential extra braces ( {{...}} )
            if extracted_json_str.startswith('{{') and extracted_json_str.endswith('}}'):
                 inner_part = extracted_json_str[1:-1].strip()
                 if inner_part.startswith('{') and inner_part.endswith('}'):
                    self.stdout.write(self.style.WARNING("  ⚠️ Corrected double braces {{...}} -> {...} before parsing."))
                    extracted_json_str = inner_part

            # Step 3: Clean known invalid escape sequences BEFORE parsing
            cleaned_json_str = self._clean_invalid_escapes(extracted_json_str)

            # Step 4: Attempt to parse the CLEANED JSON string
            data = json.loads(cleaned_json_str)

            # Step 5: Validate the basic structure
            self._validate_json_structure(data) # Raises ValueError on failure

            # Step 6: Return the parsed and validated data
            return data

        except json.JSONDecodeError as e:
            debug_file = f"failed_response_{int(time.time())}_decode.txt"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(f"Original Response:\n---\n{original_response}\n---\n")
                f.write(f"Attempted Extracted JSON String:\n---\n{extracted_json_str if extracted_json_str else 'EXTRACTION FAILED'}\n---\n")
                # Show the string *after* cleaning attempt, as that's what failed
                f.write(f"Attempted Cleaned JSON String (that failed parsing):\n---\n{cleaned_json_str if cleaned_json_str else 'CLEANING SKIPPED OR FAILED'}\n---\n")
            error_location = f"at line {e.lineno} col {e.colno}"
            raise ValueError(f"JSON decoding failed AFTER cleaning invalid escapes. Debug info saved to {debug_file}. Error: {str(e)} {error_location}") from e

        except ValueError as e: # Catch extraction or validation errors
            error_type = "Extraction" if "Could not find JSON block" in str(e) else "Validation"
            debug_file = f"failed_response_{int(time.time())}_{error_type.lower()}.txt"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(f"Original Response:\n---\n{original_response}\n---\n")
                if extracted_json_str and error_type == "Validation":
                     # Show the cleaned string if validation failed after cleaning
                     f.write(f"Cleaned & Parsed JSON (before validation failure):\n---\n{cleaned_json_str if cleaned_json_str else 'N/A'}\n---\n")
                elif error_type == "Extraction":
                     f.write(f"Attempted Extraction Failed.\n---\n")
            raise ValueError(f"JSON {error_type} failed. Debug info saved to {debug_file}. Error: {str(e)}") from e

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


      
    def _build_master_prompt(self,topic, level):
        """
        Constructs the precise prompt for Gemini AI with strict formatting rules,
        emphasis on beginner clarity, and explicit LaTeX command usage.
        """
        # Determine beginner-friendliness based on level - could be more nuanced
        beginner_focus = "Beginner" in level.name or "Foundation" in level.name or "Basic" in level.name

        detail_instruction = f"""
CONTENT GUIDELINES ({'CRITICAL FOR BEGINNERS' if beginner_focus else 'IMPORTANT'}):
   - **Target Audience:** Assume the reader is encountering this topic for the first time ({level.name} level). Explain everything clearly and simply. Avoid jargon where possible, or explain it immediately.
   - **Key Concepts:** Each concept listed MUST be explained thoroughly in simple terms. Define any new terminology. Use examples.
   - **Approach:** Describe the overall strategy step-by-step conceptually. Explain the 'why' behind the approach, not just the 'how'. Use clear, unambiguous language.
   - **Worked Examples - Solution Steps:** This is crucial for beginners.
     - Break down the solution into small, logical steps (aim for slightly more steps if needed for clarity).
     - For EACH step: Explain *what* you are doing AND *why* you are doing it.
     - Show *all* intermediate calculations explicitly using correct LaTeX commands (like `\\\\times`, `\\\\div`, `\\\\frac`). Do not skip steps.
     - Reference relevant key concepts if applicable.
   - **Worked Examples - Final Answer:** State the answer clearly. Briefly reiterate what the answer means in the context of the original problem. Use `\\\\boxed{{...}}` for the final numerical answer within LaTeX delimiters where appropriate.
   - **Overall Tone:** Be encouraging and clear. The goal is effective learning for someone new to the topic.
"""

    # NOTE: Inside this f-string, backslashes intended for the FINAL JSON output
    # need to be QUADRUPLED (\\\\\\\\) because:
    # Python f-string reads \\\\\\\\ -> \\\\
    # The LLM reads \\\\ -> \\ (which is the desired JSON escaped form for a literal \)
    # We need \\\\ for LaTeX commands/delimiters in the JSON.
    #
    # Backslashes for JSON's own escapes like \" or \n need to be DOUBLED (\\", \\n).
    # Backslashes for LaTeX commands/delimiters (like \frac) need FOUR backslashes (\\\\frac)
    # so they become \\frac in the string sent to the LLM, which then doubles them to \\\\frac for the JSON output.

        return f"""Generate a comprehensive AND highly detailed tutorial for {topic.name} at {level.name} level, specifically designed to be easily understood by a beginner.

ABSOLUTELY CRITICAL INSTRUCTIONS - FOLLOW EXACTLY:

1. RESPONSE FORMAT:
   - Your *entire* response MUST be ONLY a single JSON object.
   - Start the JSON block IMMEDIATELY with ```json and end it IMMEDIATELY with ```.
   - NO text, explanations, apologies, summaries, or anything else before ```json or after ```.
   - The JSON content MUST start with {{{{ and end with }}}}.

2. LATEX FORMATTING (CRITICAL FOR VALID JSON):
   - Use LaTeX math delimiters (`\\\\(` and `\\\\)`) ONLY for mathematical formulas, fractions, specific symbols (like ×, ÷, ±, √), etc., that genuinely require LaTeX rendering.
   - **DO NOT** place simple currency values (like `$50` or `£100`) inside LaTeX delimiters (`\\\\(`...`\\\\)`). Write them as plain text within the JSON string. Example (Correct): `"The price is $50."`. Example (Incorrect): `"The price is \\\\(\\$50\\\\)."`
   - Inside JSON string values, ALL necessary LaTeX commands AND the delimiters themselves (`\\\\(`, `\\\\)`) MUST use DOUBLE BACKSLASHES (`\\\\`) due to JSON escaping requirements.
   - SINGLE BACKSLASHES (`\\`) for LaTeX commands/delimiters WILL CAUSE an INVALID JSON error. DO NOT USE THEM.

   - **LATEX COMMANDS (CRITICAL):**
     - **FRACTIONS:** ALWAYS use `\\\\frac{{numerator}}{{denominator}}`. Example: `\\\\(\\\\frac{{50}}{{100}}\\\\)`. **NEVER** write 'frac' followed directly by numbers (like `frac50100`).
     - **MULTIPLICATION:** ALWAYS use `\\\\times` inside math delimiters `\\\\(`...`\\\\)` for the multiplication symbol (×). Example: `\\\\(2 \\\\times 3 = 6\\\\)`. **NEVER** write the word 'times' as a substitute for the command (like `2times3`).
     - **DIVISION:** ALWAYS use `\\\\div` inside math delimiters `\\\\(`...`\\\\)` for the division symbol (÷). Example: `\\\\(10 \\\\div 2 = 5\\\\)`. **NEVER** write the word 'div' as a substitute for the command (like `10div2`). Use `/` for simple division in text if not using math delimiters.
     - **OTHER COMMANDS:** Ensure standard commands like `\\\\sqrt`, `\\\\pm`, `\\\\boxed` etc., are used correctly with double backslashes.

   - **PERCENTAGE SIGN (%):** Use a plain percent sign `%` both inside AND outside LaTeX math delimiters. DO NOT use `\\%` or `\\\\%` (escaped percent signs), they are INVALID in JSON strings. Example: `"\\\\(50%\\\\)"` or `"A 20% discount"`.

3. CONTENT STRUCTURE (MANDATORY - Use the exact keys specified):
   - Top-level key: "parts" (list of objects).
   - Each part object *MUST* have: 'part_name' (string), 'key_concepts' (list of strings), 'step_by_step_guide' (object).
   - Each 'step_by_step_guide' object *MUST* have: 'approach' (string), 'worked_examples' (list of objects).
   - Each 'worked_examples' object *MUST* have: 'problem' (string), 'solution_steps' (list of strings), 'final_answer' (string).
   - Include 2-3 worked examples per part.
   - Optional keys (use if relevant): 'learning_roadmap', 'common_pitfalls', 'pro_tips' (in part object); 'visualization' (in worked_example object).

{detail_instruction}

4. JSON STRING CONTENT & ESCAPING:
   - Standard JSON string escaping MUST be used: `\\"` for double quotes within strings, `\\\\` for literal backslashes (this is automatically handled by the `\\\\` rule for LaTeX above), `\\n` for newlines within the text content where appropriate for readability (like paragraph breaks).
   - Do NOT use raw newlines that break the JSON structure.

EXAMPLE STRUCTURE (Illustrates ALL rules):
```json
{{
  "parts": [
    {{
      "part_name": "Core Concepts Example",
      "key_concepts": [
        "Concept one: Percentages represent parts of 100. 25% is \\\\(\\\\frac{{25}}{{100}}\\\\).",
        "Concept two: Calculating percentage of a value. Example: 20% of $50 is \\\\(0.20 \\\\times 50 = 10\\\\), resulting in $10."
      ],
      "step_by_step_guide": {{
        "approach": "General strategy description.\\nUse formulas like \\\\(a \\\\times b = c\\\\).",
        "worked_examples": [
          {{
            "problem": "Calculate 15% of 60.",
            "solution_steps": [
              "Step 1: Convert percentage to decimal: \\\\(15% = \\\\frac{{15}}{{100}} = 0.15\\\\).",
              "Step 2: Multiply the decimal by the number: \\\\(0.15 \\\\times 60\\\\).",
              "Step 3: Perform the calculation: \\\\(0.15 \\\\times 60 = 9\\\\)."
            ],
            "final_answer": "15% of 60 is \\\\(\\boxed{{9}}\\\\)."
          }},
          {{
            "problem": "What is 10 divided by 2?",
            "solution_steps": [
              "Step 1: Set up the division: \\\\(10 \\\\div 2\\\\).",
              "Step 2: Calculate the result: \\\\(10 \\\\div 2 = 5\\\\)."
            ],
            "final_answer": "The result is \\\\(\\boxed{{5}}\\\\)."
          }}
        ]
      }},
      "common_pitfalls": [
        "Forgetting JSON requires `\\\\` for LaTeX commands like `\\\\frac`.",
        "Incorrectly writing `frac12` instead of `\\\\frac{{1}}{{2}}`.",
        "Incorrectly writing `5times3` instead of `\\\\(5 \\\\times 3\\\\)`.",
        "Incorrectly writing `10div2` instead of `\\\\(10 \\\\div 2\\\\)`.",
        "Using `\\%` which is invalid JSON.",
        "Putting simple currency like $50 inside \\\\( \\\\)."
      ]
    }}
  ]
}}

Now, generate the tutorial content strictly following ALL the above critical instructions, including the JSON/LaTeX formatting (using LaTeX ONLY for necessary math, using correct commands like \\\\frac, \\\\times, \\\\div, NOT simple currency) AND the detailed, beginner-focused content guidelines, for the topic "{topic.name}" at the "{level.name}" level. Ensure the output is ONLY the JSON within ```json markers. Failure to follow ALL formatting rules will result in unusable output.
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