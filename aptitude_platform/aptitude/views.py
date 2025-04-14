from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai  # Import the google.generativeai library
import os
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
import json  # Import the json library
import requests
from .models import Topic,Level
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)  # Initialize genai here

# client = genai.Client(api_key=GEMINI_API_KEY)
from django.conf import settings 

load_dotenv()

# Load API key from Django settings or environment variables
GEMINI_API_KEY = getattr(settings, 'GEMINI_API_KEY', os.getenv('GEMINI_API_KEY'))

# Configure Gemini API
if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not set. Please configure it in your Django settings or as an environment variable."
    )
genai.configure(api_key=GEMINI_API_KEY)



@api_view(['POST'])
def generate_questions(request):
    topic = request.data.get("topic")
    level = request.data.get("level")

    if not topic or not level:
        return Response({"error": "Topic and level are required."}, status=400)

    prompt = f"""
Generate 5 aptitude questions for topic '{topic}' at '{level}' level.
Your response MUST be a valid JSON array containing 5 JSON objects.
Each JSON object MUST have these keys: "question", "options", "answer", "explanation".
The "options" value MUST be a JSON object with keys "A", "B", "C", "D".
The "answer" value MUST be one of the keys "A", "B", "C", "D".
Ensure all strings use double quotes. Do not include any text, explanations, apologies, or markdown formatting like ```json before or after the JSON array.
The entire response must start with '[' and end with ']'.

Example of one object in the array:
{{
  "question": "Sample question text?",
  "options": {{ "A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D" }},
  "answer": "A",
  "explanation": "Sample explanation text."
}}

Generate the JSON array now.
"""

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)

        # Extract and clean the text
        content = response.text.strip()

        # Remove markdown formatting if present
        if content.startswith("```json"):
            content = content.strip("```json").strip("```").strip()
        elif content.startswith("```"):
            content = content.strip("```").strip()

        try:
            # Try parsing the cleaned content
            questions_data = json.loads(content)
        except json.JSONDecodeError as e:
            print("JSON parsing failed. Gemini Response:")
            # print(content)
            return Response({
                "error": "Question formatting failed from LLM. Please try again.",
                # "raw": content  # Optional: remove this in production
            }, status=200)
        

        formatted_questions = []
        for item in questions_data:
            formatted_questions.append({
                "question": item.get("question"),
                "options": list(item.get("options", {}).values()),
                "answer": item.get("answer"),
                "explanation": item.get("explanation")
            })

        return Response({"questions": formatted_questions}, status=200)

    except Exception as e:
        return Response({"error": f"Server error: {str(e)}"}, status=500)




@api_view(['GET'])
def topic_list(request):
    topics = Topic.objects.all()
    data = [{"id": t.id, "name": t.name} for t in topics]
    return Response(data)

@api_view(['GET'])
def level_list(request):
    levels = Level.objects.all()
    data = [{"id": l.id, "name": l.name} for l in levels]
    return Response(data)
