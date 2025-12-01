from django.urls import path
from . import views

urlpatterns = [
    path('createQuiz/', views.QuizCreateAPIView.as_view(), name='quiz-create'),
]
