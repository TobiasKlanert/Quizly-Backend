"""URL routes for quiz creation and CRUD operations."""

from django.urls import path
from . import views

urlpatterns = [
    path('createQuiz/', views.QuizCreateAPIView.as_view(), name='quiz-create'),
    path('quizzes/', views.QuizListAPIView.as_view(), name='quiz-list'),
    path('quizzes/<int:pk>/', views.QuizDetailView.as_view(), name='quiz-detail')
]
