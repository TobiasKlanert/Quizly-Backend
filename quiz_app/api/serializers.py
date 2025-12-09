"""Serializers for quiz API: URL validation, question structure, and quiz CRUD."""
from rest_framework import serializers
from quiz_app.models import Quiz, Question
from quiz_app.services.utils import YOUTUBE_URL_VALIDATOR


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
    # Accept frontend field name `url` but map it to model field `video_url`.
    url = serializers.URLField(
        write_only=True,
        required=False,
        source="video_url",
        validators=[YOUTUBE_URL_VALIDATOR],
    )

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "video_url",
            "url",
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
