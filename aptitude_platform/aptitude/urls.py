# aptitude/urls.py (or your app's urls.py)

from django.urls import path
from . import views # Assuming your views are in the same app directory

# It's good practice to define an app_name for namespacing if you have multiple apps
# app_name = 'aptitude'

urlpatterns = [
    # Endpoint to get the list of all available levels (now includes slugs)
    path('levels/', views.level_list, name='level_list_api'),

    # Endpoint to get the list of all available topics (now includes slugs)
    # Consider adding filtering later if needed, e.g., /api/topics/?level=basic
    path('topics/', views.topic_list, name='topic_list_api'),

    # --- NEW/ESSENTIAL Endpoint ---
    # Endpoint to get the tutorial parts for a specific topic and level, using slugs
    # Matches the frontend API call: /api/tutorials/<topic_slug>/<level_slug>/
    path(
        'tutorials/<slug:topic_slug>/<slug:level_slug>/',
        views.tutorial_parts_list, # Use the view you created/adapted for this
        name='tutorial_parts_list_api'
    ),

    # Add other API endpoints your app might need below
    # e.g., path('api/questions/<slug:topic_slug>/<slug:level_slug>/', views.questions_list, name='questions_list_api'),
]