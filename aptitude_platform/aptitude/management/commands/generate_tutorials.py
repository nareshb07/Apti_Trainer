import os
import json
import time
import re
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from dotenv import load_dotenv
import google.generativeai as genai
from aptitude.models import Topic, Level, TutorialPart

load_dotenv()

class Command(BaseCommand):
    help = "Generate comprehensive tutorial parts with strict validation"
    
    def __init__(self):
        super().__init__()
        self.api_calls = 0
        self.start_time = datetime.now()
        self.debug_dir = "tutorial_generation_logs"
        os.makedirs(self.debug_dir, exist_ok=True)
        
        # Strict configuration
        self.required_example_keys = {'problem', 'solution', 'analysis', 'complexity'}
        self.allowed_complexities = {'Beginner', 'Intermediate', 'Advanced'}

    def validate_config(self):
        """Verify all required settings are present"""
        if not hasattr(settings, 'GEMINI_API_KEY') and not os.getenv('GEMINI_API_KEY'):
            raise ValueError("Missing GEMINI_API_KEY in settings or .env")
        genai.configure(api_key=getattr(settings, 'GEMINI_API_KEY', os.getenv('GEMINI_API_KEY')))

    def handle(self, *args, **options):
        self.validate_config()
        model = genai.GenerativeModel('gemini-pro')
        
        topics = Topic.objects.all()
        levels = Level.objects.all()
        total = len(topics) * len(levels)
        processed = 0
        
        for topic in topics:
            for level in levels:
                processed += 1
                try:
                    self.generate_for_topic_level(topic, level, model, processed, total)
                except Exception as e:
                    self.log_error(f"Critical failure on {topic.name}/{level.name}: {str(e)}")
                    continue
                    
        self.stdout.write(self.style.SUCCESS(
            f"\nCompleted {processed}/{total} combinations in "
            f"{(datetime.now() - self.start_time).total_seconds():.1f}s\n"
            f"API Calls: {self.api_calls}"
        ))

    def generate_for_topic_level(self, topic, level, model, processed, total):
        """Full generation pipeline for one topic-level combo"""
        debug_id = f"{topic.slug}_{level.slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Step 1: Generate content
            prompt = self.build_strict_prompt(topic, level)
            response = self.safe_api_call(model, prompt)
            
            # Step 2: Parse and validate
            tutorial_data = self.parse_response(response.text, debug_id)
            self.validate_tutorial_structure(tutorial_data, topic, level)
            
            # Step 3: Save to database
            with transaction.atomic():
                self.save_tutorial_parts(topic, level, tutorial_data)
            
            self.stdout.write(self.style.SUCCESS(
                f"[{processed}/{total}] Generated {len(tutorial_data['tutorial_parts'])} "
                f"parts for {topic.name} ({level.name})"
            ))
            
        except Exception as e:
            self.log_error(f"Failed {topic.name}/{level.name}: {str(e)}", debug_id)
            raise

    def build_strict_prompt(self, topic, level):
        """Create a prompt with explicit formatting rules"""
        part_count = self.get_part_count(level)
        
        return f"""You are a strict JSON generator for educational content. Follow these rules exactly:

1. OUTPUT MUST BE VALID JSON ONLY (no markdown, no text outside)
2. Structure:
{{
  "tutorial_parts": [
    {{
      "part_title": "Short title (3-5 words max)",
      "sections": {{
        "explanation": "Detailed explanation with LaTeX formulas like $$E=mc^2$$",
        "examples": [
          {{
            "problem": "Clear problem statement",
            "solution": "Step-by-step solution",
            "analysis": "Why this method works",
            "complexity": "Beginner/Intermediate/Advanced"
          }}
        ],
        "pitfalls": ["Common mistake 1", "Common mistake 2"],
        "tricks": ["Useful trick 1", "Useful trick 2"],
        "practice": "Specific practice instructions",
        "resources": ["Resource 1", "Resource 2"]
      }},
      "is_miscellaneous": false
    }}
  ]
}}

3. Requirements:
- Topic: {topic.name} ({getattr(topic, 'category', 'No category')})
- Level: {level.name}
- Generate exactly {part_count} parts
- Last part must have "is_miscellaneous": true
- Each part must have 3-5 examples
- All example problems must be solvable at {level.name} level
- Escape all special characters properly
- Never use markdown symbols (*, _, ``` etc.)
- Never use single quotes
- Never add trailing commas

4. Example (for a Calculus topic):
{{
  "tutorial_parts": [
    {{
      "part_title": "Limits Fundamentals",
      "sections": {{
        "explanation": "Limits describe... $$\\lim_{{x\\to a}} f(x)$$...",
        "examples": [
          {{
            "problem": "Find $$\\lim_{{x\\to 3}} (x^2-9)/(x-3)$$",
            "solution": "1. Factor numerator...",
            "analysis": "This uses algebraic manipulation...",
            "complexity": "Beginner"
          }}
        ],
        "pitfalls": ["Forgetting to check indeterminate forms"],
        "tricks": ["Try L'Hôpital's rule for 0/0 cases"],
        "practice": "Solve 10 limit problems of each type",
        "resources": ["Khan Academy Limits Course"]
      }},
      "is_miscellaneous": false
    }}
  ]
}}
"""

    def get_part_count(self, level):
        """Determine how many parts to generate based on level"""
        level_name = level.name.lower()
        if "beginner" in level_name:
            return 4-6
        elif "intermediate" in level_name:
            return 6-8
        elif "advanced" in level_name:
            return 8-12
        return 6  # Default

    def safe_api_call(self, model, prompt, max_retries=3):
        """Handle rate limiting and API errors"""
        for attempt in range(max_retries):
            try:
                if self.api_calls >= 15:  # Rate limit guard
                    wait = 60 + (10 * attempt)
                    self.stdout.write(f"⚠️ Rate limit approached. Waiting {wait}s...")
                    time.sleep(wait)
                    self.api_calls = 0

                self.api_calls += 1
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.3,
                        "max_output_tokens": 4000
                    }
                )
                return response
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(min(5 * (attempt + 1), 30))

    def parse_response(self, response_text, debug_id=None):
        """Strict JSON parsing with multiple fallbacks"""
        try:
            # First attempt: Standard JSON
            return json.loads(self.clean_response(response_text))
        except json.JSONDecodeError:
            # Second attempt: Lenient parser
            try:
                import demjson3
                return demjson3.decode(self.clean_response(response_text))
            except:
                self.save_debug_file(f"{debug_id}_failed_parse.txt", response_text)
                raise ValueError("Could not parse response as JSON")

    def clean_response(self, text):
        """Remove all non-JSON content"""
        text = re.sub(r'^[^{]*', '', text.strip())  # Remove prefix
        text = re.sub(r'[^}]*$', '', text)  # Remove suffix
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)  # Remove control chars
        return text.strip()

    def validate_tutorial_structure(self, data, topic, level):
        """Ensure data meets all requirements"""
        if not isinstance(data, dict):
            raise ValueError("Top-level data must be a dictionary")
        
        if 'tutorial_parts' not in data:
            raise ValueError("Missing 'tutorial_parts' key")
            
        parts = data['tutorial_parts']
        if not isinstance(parts, list) or not parts:
            raise ValueError("'tutorial_parts' must be a non-empty list")
            
        for part in parts:
            self.validate_part(part, topic, level)

    def validate_part(self, part, topic, level):
        """Validate an individual tutorial part"""
        required_keys = {'part_title', 'sections', 'is_miscellaneous'}
        if not required_keys.issubset(part.keys()):
            raise ValueError(f"Part missing required keys: {required_keys - part.keys()}")
            
        sections = part['sections']
        if not isinstance(sections, dict):
            raise ValueError("Sections must be a dictionary")
            
        self.validate_examples(sections.get('examples', []))
        
        # Validate misc fields
        if not isinstance(part['is_miscellaneous'], bool):
            raise ValueError("is_miscellaneous must be boolean")

    def validate_examples(self, examples):
        """Ensure examples have correct structure"""
        if not isinstance(examples, list) or len(examples) < 3:
            raise ValueError("Need at least 3 examples per part")
            
        for ex in examples:
            if not self.required_example_keys.issubset(ex.keys()):
                raise ValueError(f"Example missing keys: {self.required_example_keys - ex.keys()}")
            if ex['complexity'] not in self.allowed_complexities:
                raise ValueError(f"Invalid complexity: {ex['complexity']}")

    def save_tutorial_parts(self, topic, level, data):
        """Bulk-create tutorial parts with validation"""
        TutorialPart.objects.filter(topic=topic, level=level).delete()
        
        parts = []
        for order, part in enumerate(data['tutorial_parts'], 1):
            sections = part['sections']
            parts.append(TutorialPart(
                topic=topic,
                level=level,
                order=order,
                part_title=part['part_title'],
                explanation=sections.get('explanation', ''),
                examples=sections.get('examples', []),
                common_pitfalls='\n'.join(sections.get('pitfalls', [])),
                quick_tricks='\n'.join(sections.get('tricks', [])),
                practice_advice=sections.get('practice', ''),
                recommended_resources='\n'.join(sections.get('resources', [])),
                is_miscellaneous=part['is_miscellaneous']
            ))
        
        TutorialPart.objects.bulk_create(parts)

    def log_error(self, message, debug_id=None):
        """Log errors with optional debug info"""
        self.stderr.write(self.style.ERROR(message))
        if debug_id:
            self.save_debug_file(f"{debug_id}_error.txt", message)

    def save_debug_file(self, filename, content):
        """Save debug information"""
        path = os.path.join(self.debug_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(content))