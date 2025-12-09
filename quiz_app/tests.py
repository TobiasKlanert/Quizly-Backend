from unittest import mock

from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

from quiz_app.models import Quiz, Question


class QuizApiTests(APITestCase):
    """
    Test suite for Quiz API endpoints using Django REST Framework's APITestCase.

    This class verifies behavior for creating, listing, viewing, and updating quizzes,
    including ownership and integration with an external YouTube-to-quiz builder.

    SetUp and helpers
    - setUp:
        - Creates two users: `self.user` (owner) and `self.other_user`.
        - Stores a sample YouTube URL in `self.youtube_url`.
    - _sample_quiz_payload():
        - Returns a representative payload (dict) that mimics the data produced by the
          external YouTube-to-quiz builder: a quiz title, description, and two questions
          (each with options and an answer).
    - _create_quiz_for_user(user, title="User quiz"):
        - Creates a Quiz instance associated with `user` and one Question for that quiz,
          using `self.youtube_url` as the video URL. Returns the created Quiz.

    Tests
    - test_create_quiz_from_youtube_url:
        - Patches the external builder function to return the sample payload.
        - Authenticates as `self.user` and POSTs the YouTube URL to the create-quiz endpoint.
        - Asserts a 201 CREATED response, that one Quiz was persisted, that its
          `video_url` matches the provided URL, and that the quiz contains the expected
          number of Question objects (2).

    - test_list_quizzes_returns_only_authenticated_users_items:
        - Creates one quiz for `self.user` and another for `self.other_user`.
        - Authenticates as `self.user` and GETs the quizzes list endpoint.
        - Asserts a 200 OK response and that the returned list contains only the
          authenticated user's quiz (by length and title).

    - test_detail_forbidden_for_non_owner:
        - Creates a quiz owned by `self.other_user`.
        - Authenticates as `self.user` and attempts to GET the detail endpoint for that quiz.
        - Asserts a 403 FORBIDDEN response to enforce that non-owners cannot view details.

    - test_patch_updates_quiz_title:
        - Creates a quiz owned by `self.user`.
        - Authenticates as `self.user` and PATCHes the quiz to change the title.
        - Asserts a 200 OK response and verifies the change persisted in the database.
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username="quizowner", email="owner@example.com", password="secret123"
        )
        self.other_user = User.objects.create_user(
            username="other", email="other@example.com", password="secret123"
        )
        self.youtube_url = "https://youtu.be/dQw4w9WgXcQ"

    def _sample_quiz_payload(self):
        return {
            "title": "Sample Quiz",
            "description": "Short description",
            "questions": [
                {
                    "question_title": "Q1?",
                    "question_options": ["A", "B", "C", "D"],
                    "answer": "A",
                },
                {
                    "question_title": "Q2?",
                    "question_options": ["E", "F", "G", "H"],
                    "answer": "F",
                },
            ],
        }

    def _create_quiz_for_user(self, user, title="User quiz"):
        quiz = Quiz.objects.create(
            user=user,
            title=title,
            description="desc",
            video_url=self.youtube_url,
        )
        Question.objects.create(
            quiz=quiz,
            question_title="Q1?",
            question_options=["A", "B", "C", "D"],
            answer="A",
        )
        return quiz

    @mock.patch("quiz_app.api.views.build_quiz_from_youtube")
    def test_create_quiz_from_youtube_url(self, mock_builder):
        mock_builder.return_value = self._sample_quiz_payload()
        self.client.force_authenticate(self.user)

        response = self.client.post(
            "/api/createQuiz/", {"url": self.youtube_url}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiz.objects.count(), 1)
        quiz = Quiz.objects.first()
        self.assertEqual(quiz.video_url, self.youtube_url)
        self.assertEqual(quiz.questions.count(), 2)

    def test_list_quizzes_returns_only_authenticated_users_items(self):
        self._create_quiz_for_user(self.user, title="Mine")
        self._create_quiz_for_user(self.other_user, title="Not mine")
        self.client.force_authenticate(self.user)

        response = self.client.get("/api/quizzes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Mine")

    def test_detail_forbidden_for_non_owner(self):
        quiz = self._create_quiz_for_user(self.other_user, title="Other quiz")
        self.client.force_authenticate(self.user)

        response = self.client.get(f"/api/quizzes/{quiz.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_updates_quiz_title(self):
        quiz = self._create_quiz_for_user(self.user, title="Old title")
        self.client.force_authenticate(self.user)

        response = self.client.patch(
            f"/api/quizzes/{quiz.id}/", {"title": "New title"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        quiz.refresh_from_db()
        self.assertEqual(quiz.title, "New title")
