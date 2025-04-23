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


@api_view(['GET'])
def topic_list(request):
    topics = Topic.objects.all()
    data = [{"slug": t.slug, "name": t.name} for t in topics]
    return Response(data)

@api_view(['GET'])
def level_list(request):
    levels = Level.objects.all()
    # data = [{"id": l.id, "name": l.name} for l in levels]
    data = [{"slug": l.slug, "name": l.name} for l in levels]
    return Response(data)
@api_view(['GET'])
def tutorial_parts_list(request, topic_slug, level_slug):
     # Use slugs to filter
     try:
         topic = Topic.objects.get(slug=topic_slug)
         level = Level.objects.get(slug=level_slug)
         parts = TutorialPart.objects.filter(topic=topic, level=level).order_by('order')
         # --- Use a DRF Serializer for better practice ---
         # from .serializers import TutorialPartSerializer
         # serializer = TutorialPartSerializer(parts, many=True)
         # return Response(serializer.data)

         # --- Basic manual serialization (if not using DRF Serializers yet) ---
         data = [
             {
                 "slug": p.slug,
                 "part_name": p.part_name,
                 "order": p.order,
                 "key_concepts": p.key_concepts, # Assuming these fields exist
                 "preparation_strategy": p.preparation_strategy,
                 "explanations": p.explanations,
                 "example_problems": p.example_problems,
                 "common_pitfalls": p.common_pitfalls,
                 "quick_tips": p.quick_tips,
                 # Add other relevant fields
             } for p in parts
         ]
         return Response(data)

     except Topic.DoesNotExist:
         return Response({"error": "Topic not found"}, status=status.HTTP_404_NOT_FOUND)
     except Level.DoesNotExist:
         return Response({"error": "Level not found"}, status=status.HTTP_404_NOT_FOUND)
     except Exception as e:
          return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)