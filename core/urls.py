"""Root URL configuration hooking up admin and API routes."""
from django.contrib import admin
from django.urls import path, include

from .views import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('auth_app.api.urls')),
    path('api/', include('quiz_app.api.urls')),
    path('health/', health_check),
]
