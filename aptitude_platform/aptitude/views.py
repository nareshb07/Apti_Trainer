from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai
import os
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Topic, Level, TutorialPart

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@api_view(['POST'])
@csrf_exempt
def generate_tutorial_content(request):
    try:
        data = json.loads(request.body)
        topic_id = data.get('topic_id')
        level_id = data.get('level_id')
        part_order = data.get('part_order')

        # Validate input
        if not all([topic_id, level_id, part_order]):
            return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)

        # Get tutorial part
        tutorial_part = get_object_or_404(
            TutorialPart,
            topic_id=topic_id,
            level_id=level_id,
            order=part_order
        )

        # Generate prompt for LLM
        prompt = f"""
        Generate a detailed tutorial section about {tutorial_part.topic.name} 
        for {tutorial_part.level.name} level learners.
        
        Part Title: {tutorial_part.part_title}
        Previous Content: {tutorial_part.content}
        
        Include:
        - Clear explanations
        - Relevant examples
        - Practical exercises
        - Common pitfalls to avoid
        """

        # Call Gemini API
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        generated_content = response.text

        # Update and save the tutorial part
        tutorial_part.content = generated_content
        tutorial_part.save()

        return Response({
            "topic": tutorial_part.topic.name,
            "level": tutorial_part.level.name,
            "part_title": tutorial_part.part_title,
            "order": tutorial_part.order,
            "content": generated_content
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
