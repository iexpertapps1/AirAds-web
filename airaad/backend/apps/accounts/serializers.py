"""
AirAd Backend — Accounts Serializers

CustomTokenObtainPairSerializer adds role, full_name, email to JWT claims.
LoginSerializer validates credentials and delegates to services.py.
No business logic here — validation only.
"""

import logging

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token

from .models import AdminUser

logger = logging.getLogger(__name__)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT token serializer that injects extra claims into the access token.

    Adds role, full_name, and email to the JWT payload so clients
    can read user context without an extra API call.
    """

    @classmethod
    def get_token(cls, user: AdminUser) -> Token:
        """Build the JWT token with additional AirAd-specific claims.

        Args:
            user: The authenticated AdminUser instance.

        Returns:
            JWT Token with role, full_name, and email claims added.
        """
        token = super().get_token(user)
        token["role"] = user.role
        token["full_name"] = user.full_name
        token["email"] = user.email
        return token


class LoginSerializer(serializers.Serializer):
    """Serializer for the login endpoint.

    Validates that email and password are present.
    Business logic (lockout, credential check) is in services.py.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})


class LogoutSerializer(serializers.Serializer):
    """Serializer for the logout endpoint.

    Requires the refresh token to blacklist it.
    """

    refresh = serializers.CharField(
        help_text="The refresh token to invalidate."
    )


class AdminUserSerializer(serializers.ModelSerializer):
    """Read-only serializer for AdminUser — used in JWT response and profile views."""

    class Meta:
        model = AdminUser
        fields = [
            "id",
            "email",
            "full_name",
            "role",
            "is_active",
            "last_login_ip",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CreateAdminUserSerializer(serializers.Serializer):
    """Serializer for creating a new AdminUser (SUPER_ADMIN only).

    No business logic — delegates to accounts/services.py.
    """

    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )
    full_name = serializers.CharField(max_length=255)
    role = serializers.ChoiceField(
        choices=[r.value for r in __import__("apps.accounts.models", fromlist=["AdminRole"]).AdminRole]
    )
