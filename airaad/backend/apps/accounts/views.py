"""
AirAd Backend — Accounts Views

Login, refresh, logout, profile, and admin user creation.
Zero business logic — all delegated to services.py (R4).
Every view uses RolePermission.for_roles() (R3).
Uses django.utils.timezone.now() — never datetime.now().
"""

import logging

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from core.exceptions import success_response

from .models import AdminRole
from .permissions import RolePermission
from .serializers import (
    AdminUserSerializer,
    CreateAdminUserSerializer,
    LoginSerializer,
    LogoutSerializer,
)
from .services import authenticate_user, create_admin_user, logout_user

logger = logging.getLogger(__name__)


class LoginView(APIView):
    """Authenticate an admin user and return JWT access + refresh tokens.

    Lockout is enforced in services.py — 5 failures → 429 + Retry-After.
    """

    authentication_classes: list = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Auth"],
        summary="Admin login — returns JWT tokens",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description="Login successful — returns access and refresh tokens"),
            401: OpenApiResponse(description="Invalid credentials"),
            429: OpenApiResponse(description="Account locked — too many failed attempts"),
        },
    )
    def post(self, request: Request) -> Response:
        """Validate credentials and return JWT tokens.

        Args:
            request: HTTP request with email and password in body.

        Returns:
            200 with access/refresh tokens and user data on success.
            401 on invalid credentials.
            429 on account lockout with Retry-After header.
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user, tokens = authenticate_user(
                request=request._request,
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )
        except ValueError as e:
            error_msg = str(e)
            if "locked" in error_msg.lower():
                # Extract retry_after seconds from message if present
                import re
                match = re.search(r"(\d+) seconds", error_msg)
                retry_after = int(match.group(1)) if match else 900
                response = Response(
                    {
                        "success": False,
                        "data": None,
                        "message": error_msg,
                        "errors": {},
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
                response["Retry-After"] = str(retry_after)
                return response

            return Response(
                {
                    "success": False,
                    "data": None,
                    "message": error_msg,
                    "errors": {},
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return success_response(
            data={
                "user": AdminUserSerializer(user).data,
                "tokens": tokens,
            },
            message="Login successful",
        )


class LogoutView(APIView):
    """Blacklist the provided refresh token to invalidate the session."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Auth"],
        summary="Logout — blacklist refresh token",
        request=LogoutSerializer,
        responses={
            200: OpenApiResponse(description="Logged out successfully"),
            400: OpenApiResponse(description="Invalid or already blacklisted token"),
        },
    )
    def post(self, request: Request) -> Response:
        """Blacklist the refresh token.

        Args:
            request: HTTP request with refresh token in body.

        Returns:
            200 on success, 400 on invalid token.
        """
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            logout_user(
                request=request._request,
                refresh_token=serializer.validated_data["refresh"],
                user=request.user,
            )
        except ValueError as e:
            return Response(
                {
                    "success": False,
                    "data": None,
                    "message": str(e),
                    "errors": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return success_response(message="Logged out successfully")


class ProfileView(APIView):
    """Return the authenticated user's profile."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Auth"],
        summary="Get current user profile",
        responses={
            200: AdminUserSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        """Return the current user's profile data.

        Args:
            request: Authenticated HTTP request.

        Returns:
            200 with AdminUser data.
        """
        serializer = AdminUserSerializer(request.user)
        return success_response(data=serializer.data)


class CreateAdminUserView(APIView):
    """Create a new AdminUser account. SUPER_ADMIN only."""

    permission_classes = [RolePermission.for_roles(AdminRole.SUPER_ADMIN)]

    @extend_schema(
        tags=["Auth"],
        summary="Create admin user (SUPER_ADMIN only)",
        request=CreateAdminUserSerializer,
        responses={
            201: AdminUserSerializer,
            400: OpenApiResponse(description="Validation error or email already in use"),
            403: OpenApiResponse(description="Forbidden — SUPER_ADMIN role required"),
        },
    )
    def post(self, request: Request) -> Response:
        """Create a new AdminUser. Delegates entirely to services.py.

        Args:
            request: HTTP request with user creation data.

        Returns:
            201 with new user data on success.
            400 on validation failure.
        """
        serializer = CreateAdminUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = create_admin_user(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                full_name=serializer.validated_data["full_name"],
                role=serializer.validated_data["role"],
                actor=request.user,
                request=request._request,
            )
        except ValueError as e:
            return Response(
                {
                    "success": False,
                    "data": None,
                    "message": str(e),
                    "errors": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return success_response(
            data=AdminUserSerializer(user).data,
            message="Admin user created successfully",
            status_code=status.HTTP_201_CREATED,
        )


class CustomTokenRefreshView(TokenRefreshView):
    """JWT token refresh — extends SimpleJWT's default view with schema tags."""

    @extend_schema(
        tags=["Auth"],
        summary="Refresh JWT access token",
        responses={
            200: OpenApiResponse(description="New access token returned"),
            401: OpenApiResponse(description="Refresh token invalid or expired"),
        },
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        """Refresh the JWT access token using a valid refresh token.

        Args:
            request: HTTP request with refresh token in body.

        Returns:
            200 with new access token on success.
        """
        return super().post(request, *args, **kwargs)
