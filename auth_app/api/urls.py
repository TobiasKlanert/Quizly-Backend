from django.urls import path
from .views import RegistrationView, CookieTokenObtainPairView, LogoutCookieView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', CookieTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutCookieView.as_view(), name='logout')
]