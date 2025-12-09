"""Authentication views using JWT stored in HTTP-only cookies."""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from django.conf import settings
from django.contrib.auth import get_user_model

from .serializers import RegistrationSerializer, CustomTokenObtainPairSerializer


class RegistrationView(APIView):
    """Register a new user account.
    Class-based APIView that accepts registration data, validates it with
    RegistrationSerializer, and creates a new user.
    Behavior
        - permission_classes: [AllowAny] — this endpoint is accessible to
          unauthenticated clients.
        - POST: validates request.data with RegistrationSerializer.
            * On successful validation: calls serializer.save() to persist the user
              and returns Response({'detail': 'User created successfully!'}) with
              a successful HTTP status (default 200 OK).
            * On validation failure: returns Response(serializer.errors,
              status=status.HTTP_400_BAD_REQUEST).
    Expected input
        - A JSON payload containing the fields required by RegistrationSerializer
          (for example: username, password, email). See RegistrationSerializer for
          exact field names and validation rules.
    Side effects
        - Creates a new user record via serializer.save(). Any additional side
          effects implemented in the serializer (e.g., sending confirmation emails,
          creating related objects) will also occur.
    Errors and exceptions
        - Validation errors are returned as serializer.errors with HTTP 400.
        - Other exceptions raised during save/creation are handled by DRF's
          exception handlers unless explicitly caught within the view.
    """
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
    """
    Class-based view that issues a JWT access/refresh pair and sets them as HTTP-only cookies
    on the response. This view delegates authentication and token creation to the parent
    (TokenObtainPairView) using CustomTokenObtainPairSerializer, then mutates the response to:
    - Replace the response body with a simple JSON object containing:
        - "detail": a success message
        - "user": serialized user data returned by the serializer
    - Set two cookies:
        - "access_token": the issued access token (string)
        - "refresh_token": the issued refresh token (string)
    Cookie attributes:
    - httponly=True (prevents JavaScript access)
    - secure=(not settings.DEBUG) (ensures cookies are only sent over HTTPS in production)
    - samesite='Lax' (mitigates CSRF while allowing top-level navigation)
    Behavior and notes:
    - The view preserves the parent view's authentication and validation behavior; any errors or
      status codes produced by TokenObtainPairView (e.g., invalid credentials) will be propagated.
    - Token lifetimes and expiration are governed by the JWT settings (not by cookie attributes).
    - Because cookies are HttpOnly, client-side JavaScript cannot read tokens; use the refresh_token
      cookie to obtain new access tokens via a dedicated refresh endpoint.
    - For production deployments, serve over HTTPS and consider stricter SameSite/CSRF policies
      depending on the application's requirements.
    Attributes:
    - serializer_class: CustomTokenObtainPairSerializer (used to validate credentials and produce tokens)
    """
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
            key='access_token',
            value=str(access),
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax'
        )

        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax'
        )

        return response


class LogoutCookieView(APIView):
    """
    Class-based view that handles user logout by invalidating the refresh token (if present in cookies)
    and clearing authentication cookies.
    Behavior
    - Requires an authenticated user (permission_classes = [IsAuthenticated]).
    - On POST:
        - Reads the 'refresh_token' cookie from request.COOKIES.
        - If a refresh token is present, attempts to blacklist it using RefreshToken(refresh_token).
            Any exception raised during blacklisting is suppressed to ensure logout proceeds.
        - Constructs and returns a Response with HTTP 200 and a confirmation message.
        - Deletes the 'access_token' and 'refresh_token' cookies from the response.
    Side effects
    - May add the provided refresh token to the JWT blacklist (requires Django REST framework SimpleJWT
        blacklist app to be configured).
    - Removes authentication cookies from the client by setting deletion headers in the response.
    Return
    - rest_framework.response.Response with status HTTP_200_OK and a JSON detail message.
    Notes
    - The view assumes JWTs are stored in cookies named 'access_token' and 'refresh_token'.
    - If blacklisting is not enabled or the provided token is invalid/expired, the view will still clear cookies
        and return success to avoid leaving the client in an inconsistent authenticated state.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass

        response = Response(
            {"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


class CookieRefreshView(TokenRefreshView):
    """
    Refresh access token using a refresh token stored in an HTTP cookie.
    This view handles POST requests and attempts to refresh an access token by
    reading the 'refresh_token' cookie from the incoming request. It delegates
    validation and token generation to the underlying serializer obtained via
    self.get_serializer(...).
    Behavior:
    - If the 'refresh_token' cookie is missing, returns a 400 response with a
        descriptive error.
    - If the serializer fails validation (invalid/expired refresh token), returns
        a 401 response indicating an invalid refresh token.
    - On success, returns a 200 response containing the new access token in the
        response body under the 'access' key and sets an HttpOnly 'access_token'
        cookie with the same token.
    Side effects:
    - Sets an 'access_token' cookie with attributes:
        - httponly=True
        - secure=(not settings.DEBUG)
        - samesite='Lax'
    Notes:
    - The serializer is invoked with data={'refresh': refresh_token}.
    - The view is intended to be used with a JWT refresh serializer (e.g. from
        django-rest-framework-simplejwt) that returns 'access' in validated_data.
    """

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data={'refresh': refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response(
                {"detail": "Refresh token invalid!"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        access_token = serializer.validated_data.get('access')

        response = Response({
            "detail": "Token refreshed",
            "access": access_token
            })

        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax'
        )

        return response
