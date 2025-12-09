"""Serializers for quiz API: URL validation, question structure, and quiz CRUD."""
from rest_framework import serializers
from quiz_app.models import Quiz, Question
from quiz_app.services.utils import YOUTUBE_URL_VALIDATOR


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Question model that enforces structure and validity for quiz questions.
    This ModelSerializer exposes the following fields:
    - id
    - question_title
    - question_options: expected to be a sequence (list) of exactly four option values.
    - answer: expected to be one of the values contained in question_options.
    - created_at
    - updated_at
    Validation:
    - Ensures question_options contains exactly 4 items.
    - Ensures answer is present among the provided question_options.
    - Validation is performed in the object-level validate(attrs) method.
    Raises:
    - serializers.ValidationError: if question_options does not contain exactly four items
        (message: "A question must have exactly 4 options.").
    - serializers.ValidationError: if answer is not one of the provided options
        (message: "The answer must be one of the options.").
    Returns:
    - The validated attrs dict (unchanged) when validation passes.
    """
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
    """
    Serializer for Quiz objects that supports nested question payloads and an alternate
    frontend field name for the quiz video URL.
    Behavior and fields:
    - questions: A nested list of QuestionSerializer objects (many=True). Used to validate
        and accept a list of question payloads on create. The serializer's create() method
        expects this list to be present and will pop it from validated_data.
    - user: Read-only PrimaryKeyRelatedField. The serializer does not accept a user value
        from the incoming payload; instead the creating user is expected to be provided via
        serializer context (self.context.get("user")).
    - video_url: The model field that is exposed for read operations and included in the
        serializer's output fields.
    - url: A write-only URLField accepted from the frontend. It is mapped to the model
        field video_url using source="video_url". Because it is write_only, it will be
        accepted on input but not emitted in serialized output. The field is validated
        using YOUTUBE_URL_VALIDATOR.
    Meta:
    - The serializer is a ModelSerializer for the Quiz model and enumerates the explicit
        fields it includes in input/output: id, title, description, video_url, url,
        created_at, updated_at, questions, and user.
    create(validated_data) behavior:
    - Pops "questions" from validated_data and expects it to be a list of dicts
        corresponding to QuestionSerializer-validated data. If "questions" is missing,
        popping will raise a KeyError.
    - Retrieves the creating user from self.context.get("user") and creates the Quiz
        instance with the remaining validated_data (including a video_url if provided via
        the write-only url field).
    - Iterates the questions_data and creates Question objects associated with the
        created Quiz instance via Question.objects.create(quiz=quiz, **q).
    - Returns the newly created Quiz instance.
    Notes and caveats:
    - Nested updates are not implemented: create() handles only creation; update()
        would need custom logic to reconcile nested question lists.
    - The serializer relies on self.context["user"] being provided for proper ownership;
        if not supplied, user will be None and Quiz creation may fail or assign an
        unintended owner depending on model constraints.
    - Validation for each question is delegated to QuestionSerializer before create() is
        called (i.e., nested payloads are validated), but related object creation is done
        manually rather than via writable nested serializers.
    """
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
