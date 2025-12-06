"""Serializers for user registration and JWT login responses.

- `RegistrationSerializer` handles user creation with password confirmation and
  unique email validation.
- `CustomTokenObtainPairSerializer` augments the JWT login response with basic
  user info for convenience on the frontend.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Create a new user while enforcing email uniqueness and password match."""
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirmed_password', 'email']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'email': {
                'required': True
            }
        }

    def validate_confirmed_password(self, value):
        password = self.initial_data.get('password')
        if password and value and password != value:
            raise serializers.ValidationError('Passwords do not match')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def save(self):
        pw = self.validated_data['password']

        account = User(
            email=self.validated_data['email'], username=self.validated_data['username'])
        account.set_password(pw)
        account.save()
        return account


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extend JWT pair response with minimal user details."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email
        }
        return data
