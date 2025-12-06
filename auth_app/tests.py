from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User


class AuthApiTests(APITestCase):
    def test_register_creates_user_and_enforces_unique_email(self):
        payload = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "secret123",
            "confirmed_password": "secret123",
        }

        response = self.client.post("/api/register/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(username="alice").exists())

        # Duplicate email should fail
        payload["username"] = "alice2"
        dup_response = self.client.post("/api/register/", payload, format="json")
        self.assertEqual(dup_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", dup_response.data)

    def test_login_sets_http_only_cookies(self):
        user = User.objects.create_user(
            username="bob", email="bob@example.com", password="secret123"
        )

        response = self.client.post(
            "/api/login/",
            {"username": "bob", "password": "secret123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        self.assertEqual(response.data.get("user", {}).get("username"), "bob")

    def test_logout_blacklists_refresh_and_clears_cookies(self):
        user = User.objects.create_user(
            username="charlie", email="charlie@example.com", password="secret123"
        )
        self.client.force_authenticate(user)

        response = self.client.post("/api/logout/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        self.assertEqual(response.cookies["access_token"].value, "")
        self.assertEqual(response.cookies["refresh_token"].value, "")

    def test_refresh_issues_new_access_token_from_cookie(self):
        user = User.objects.create_user(
            username="dana", email="dana@example.com", password="secret123"
        )
        refresh = RefreshToken.for_user(user)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.post("/api/token/refresh/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("access_token", response.cookies)
