"""Database models for quizzes and their questions."""

from django.db import models
from django.conf import settings


class Quiz(models.Model):
    """A generated quiz tied to the owning user and source video."""

    title = models.CharField(max_length=255)
    description = models.TextField()
    video_url = models.URLField()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="quizzes",
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Question(models.Model):
    """A multiple-choice question belonging to a quiz."""

    quiz = models.ForeignKey(
        Quiz, related_name="questions", on_delete=models.CASCADE)

    question_title = models.CharField(max_length=500)
    question_options = models.JSONField()
    answer = models.CharField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_title
