from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth import get_user_model

from .serializers import RegistrationSerializer, CustomTokenObtainPairSerializer


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        msg = {}
        if serializer.is_valid():
            serializer.save()
            msg = {
                'detail': 'User created successfully!'
            }
            return Response(msg)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


User = get_user_model()


class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        data = response.data

        access = data.get("access")
        refresh = data.get("refresh")
        user = data.get("user")

        response.data = {
            "detail": "Login successfully!",
            "user": user
        }

        response.set_cookie(
            "access_token", access, httponly=True, secure=True, samesite="Lax"
        )
        response.set_cookie(
            "refresh_token", refresh, httponly=True, secure=True, samesite="Lax"
        )

        return response
