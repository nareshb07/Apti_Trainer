from django.urls import path
from . import views

urlpatterns = [
    path('topics/', views.topic_list),
    path('levels/', views.level_list),
    # path('generate-tutorial-and-questions/', views.generate_tutorial_and_questions),
    # path('tutorial_part_view/', views.tutorial_part_view),
    # path('fetch_tutorial_prompt/', views.fetch_tutorial_prompt)

]
