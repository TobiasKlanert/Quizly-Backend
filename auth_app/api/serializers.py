from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for creating a new User while enforcing email uniqueness and password confirmation.
    This ModelSerializer exposes the following fields:
    - username: the desired username for the new account.
    - password: write-only password for the account (will be hashed via set_password()).
    - confirmed_password: write-only field used to verify the password matches.
    - email: required email address which must be unique among users.
    Validation:
    - validate_confirmed_password ensures that the provided password and confirmed_password match,
        raising serializers.ValidationError('Passwords do not match') when they differ.
    - validate_email ensures the provided email is not already in use, raising
        serializers.ValidationError('Email already exists') if a duplicate is found.
    Behavior:
    - On successful validation, save() constructs a new User instance with the given username and email,
        uses set_password() to hash and set the password, saves the instance to the database, and returns it.
    - Password and confirmed_password are write-only and are not exposed in serialized output.
    """
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
    """
    Extend TokenObtainPairSerializer to include minimal user details in the JWT response.
    This serializer delegates authentication and token creation to
    TokenObtainPairSerializer.validate(attrs) and then augments the returned
    data with a "user" mapping containing the authenticated user's id,
    username, and email.
    Returned data:
    - preserves the default token keys produced by the parent (e.g. "access",
        "refresh")
    - adds a "user" dict: {"id": int, "username": str, "email": str}
    Notes:
    - The parent validate() is responsible for authentication and raising any
        authentication errors; this class only enriches the successful response.
    - Avoids exposing additional or sensitive user fields.
    """

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email
        }
        return data
