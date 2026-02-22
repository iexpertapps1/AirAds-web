"""
AirAd Backend — Accounts URL Configuration
Mounted at: /api/v1/auth/
"""

from django.urls import path

from .views import (
    CreateAdminUserView,
    CustomTokenRefreshView,
    LoginView,
    LogoutView,
    ProfileView,
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="auth-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("profile/", ProfileView.as_view(), name="auth-profile"),
    path("users/", CreateAdminUserView.as_view(), name="auth-create-user"),
]
