import os
import json
from django.core.management.base import BaseCommand
from aptitude.models import Topic, Level, TutorialPart
from dotenv import load_dotenv
import google.generativeai as genai
from django.conf import settings

load_dotenv()

GEMINI_API_KEY = getattr(settings, 'GEMINI_API_KEY', os.getenv('GEMINI_API_KEY'))
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not configured")

genai.configure(api_key=GEMINI_API_KEY)

class Command(BaseCommand):
    help = "Generate tutorial parts for all topics and levels"

    def handle(self, *args, **kwargs):
        model = genai.GenerativeModel('gemini-1.5-flash')

        for topic in Topic.objects.all():
            for level in Level.objects.all():
                prompt = f"""
You are a tutor helping students prepare for aptitude exams.

Generate a step-by-step tutorial for the topic "{topic.name}" at the "{level.name}" level. 
Break the tutorial into 3 to 5 parts based on difficulty or type of question.

Each part should include:
- A title
- A concise explanation or method
- Clear progression from basic to advanced

Return only a valid JSON array like:
[
  {{
    "part_title": "Understanding Basic Percentages",
    "content": "Explanation of basic percentage formula and usage..."
  }},
  ...
]
Do NOT include any markdown, preambles, or commentary. Just return the JSON array.
                """

                try:
                    response = model.generate_content(prompt)
                    content = response.text.strip()

                    # Clean markdown
                    if content.startswith("```json"):
                        content = content.strip("```json").strip("```").strip()
                    elif content.startswith("```"):
                        content = content.strip("```").strip()

                    tutorial_parts = json.loads(content)

                    for i, part in enumerate(tutorial_parts):
                        TutorialPart.objects.update_or_create(
                            topic=topic,
                            level=level,
                            order=i + 1,
                            defaults={
                                "part_title": part["part_title"],
                                "content": part["content"]
                            }
                        )
                    self.stdout.write(self.style.SUCCESS(f"✅ Saved tutorial for {topic.name} - {level.name}"))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"❌ Error for {topic.name} - {level.name}: {e}"))
