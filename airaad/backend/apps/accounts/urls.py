"""
AirAd Backend — Accounts URL Configuration
Mounted at: /api/v1/auth/
"""

from django.urls import path

from .views import (
    AdminUserDetailView,
    AdminUserListView,
    CustomTokenRefreshView,
    GDPRAccountDeletionView,
    GDPRDataExportView,
    LoginView,
    LogoutView,
    ProfileView,
    UnlockAdminUserView,
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="auth-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("profile/", ProfileView.as_view(), name="auth-profile"),
    path("users/", AdminUserListView.as_view(), name="auth-user-list"),
    path("users/create/", AdminUserListView.as_view(), name="auth-create-user"),
    path("users/<str:pk>/", AdminUserDetailView.as_view(), name="auth-user-detail"),
    path(
        "users/<str:pk>/unlock/", UnlockAdminUserView.as_view(), name="auth-user-unlock"
    ),
    # GDPR endpoints (spec §10.1)
    path("me/export/", GDPRDataExportView.as_view(), name="gdpr-data-export"),
    path("me/", GDPRAccountDeletionView.as_view(), name="gdpr-account-deletion"),
]
