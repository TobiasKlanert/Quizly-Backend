"""URL routes for authentication: register, login, logout, and token refresh."""

from django.urls import path
from .views import RegistrationView, CookieTokenObtainPairView, LogoutCookieView, CookieRefreshView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', CookieTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutCookieView.as_view(), name='logout'),
    path('token/refresh/', CookieRefreshView.as_view(), name='refresh')
]
