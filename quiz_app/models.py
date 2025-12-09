"""Database models for quizzes and their questions."""

from django.db import models
from django.conf import settings

from quiz_app.services.utils import YOUTUBE_URL_VALIDATOR


class Quiz(models.Model):
    """Model representing a generated quiz tied to a source video and its owning user.

    This model stores basic metadata about a quiz created from a video, including a
    human-readable title and description, a validated YouTube video URL, and a
    reference to the user who owns the quiz.

    Fields
    - title (str): Short, required title for the quiz (max length 255).
    - description (str): Longer textual description or summary of the quiz.
    - video_url (str): Source video URL; validated by YOUTUBE_URL_VALIDATOR to
        ensure it points to an allowed YouTube resource.
    - user (ForeignKey): Reference to the owning user (settings.AUTH_USER_MODEL),
        with related_name="quizzes". Deleting the user cascades and removes their
        quizzes.
    - created_at (datetime): Auto-set timestamp when the quiz is created.
    - updated_at (datetime): Auto-updated timestamp when the quiz is modified.
    """

    title = models.CharField(max_length=255)
    description = models.TextField()
    video_url = models.URLField(validators=[YOUTUBE_URL_VALIDATOR])

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="quizzes",
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Question(models.Model):
    """
    Represents a multiple-choice question that belongs to a Quiz.

    Fields:
    - quiz (Quiz): ForeignKey to the Quiz this question is part of.
    - question_title (str): The text/title of the question.
    - question_options (list|dict): JSON-serializable collection of possible answers; commonly a list of option strings or a dict mapping keys to option strings.
    - answer (str): The correct answer; expected to correspond to one of the values (or keys, depending on representation) in question_options.
    - created_at (datetime): Timestamp when the question was created (auto-set).
    - updated_at (datetime): Timestamp when the question was last updated (auto-set).

    Representation:
        - __str__ returns the question_title for readable display.
    """

    quiz = models.ForeignKey(
        Quiz, related_name="questions", on_delete=models.CASCADE)

    question_title = models.CharField(max_length=500)
    question_options = models.JSONField()
    answer = models.CharField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_title
