# authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import UntypedToken

from django.contrib.auth import get_user_model

User = get_user_model()


class CookieJWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")

        if not access_token:
            return None

        try:
            UntypedToken(access_token)
        except InvalidToken:
            raise exceptions.AuthenticationFailed("Invalid or expired token")

        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(access_token)
        user = jwt_auth.get_user(validated_token)

        if not user or not user.is_active:
            raise exceptions.AuthenticationFailed("User inactive or not found")

        return (user, validated_token)
