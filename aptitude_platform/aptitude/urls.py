from django.urls import path
from . import views

urlpatterns = [
    path('topics/', views.topic_list),
    path('levels/', views.level_list),
    path('generate-questions/', views.generate_questions),
]
