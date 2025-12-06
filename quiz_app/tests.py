from unittest import mock

from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

from quiz_app.models import Quiz, Question


class QuizApiTests(APITestCase):
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
