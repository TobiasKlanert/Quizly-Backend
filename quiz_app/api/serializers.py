"""Serializers for quiz API: URL validation, question structure, and quiz CRUD."""

import re

from rest_framework import serializers
from quiz_app.models import Quiz, Question


YOUTUBE_REGEX = re.compile(
    r'^(https?://)?(www\.)?'
    r'(youtube\.com/(watch\?v=|shorts/)|youtu\.be/)'
    r'(?P<id>[\w-]{11})'
    r'([&?].*)?$',
    re.IGNORECASE
)


class UrlInputSerializer(serializers.Serializer):
    """Validate a YouTube URL used to generate a quiz."""
    url = serializers.URLField()

    def validate_url(self, value):
        if not YOUTUBE_REGEX.match(value):
            raise serializers.ValidationError("Invalid YouTube-URL.")
        return value


class QuestionSerializer(serializers.ModelSerializer):
    """Serialize a quiz question ensuring exactly four options and a valid answer."""
    class Meta:
        model = Question
        fields = [
            "id",
            "question_title",
            "question_options",
            "answer",
            "created_at",
            "updated_at"
        ]

    def validate(self, attrs):
        options = attrs.get("question_options", [])
        answer = attrs.get("answer")

        if len(options) != 4:
            raise serializers.ValidationError(
                "A question must have exactly 4 options.")

        if answer not in options:
            raise serializers.ValidationError(
                "The answer must be one of the options.")

        return attrs


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "video_url",
            "created_at",
            "updated_at",
            "questions",
            "user",
        ]

    def create(self, validated_data):
        questions_data = validated_data.pop("questions")
        user = self.context.get("user")
        quiz = Quiz.objects.create(user=user, **validated_data)

        for q in questions_data:
            Question.objects.create(quiz=quiz, **q)

        return quiz
