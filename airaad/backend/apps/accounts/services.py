"""
AirAd Backend — Accounts Service Layer (R4)

All business logic for authentication lives here.
Views delegate entirely to these functions — zero logic in views.
Every auth event writes an AuditLog entry (R5).
Uses django.utils.timezone.now() — never datetime.now().
"""

import logging
from datetime import timedelta
from typing import Any

from django.contrib.auth import authenticate
from django.http import HttpRequest
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from core.utils import get_client_ip

from .models import AdminRole, AdminUser

logger = logging.getLogger(__name__)

# Lockout policy constants
MAX_FAILED_ATTEMPTS: int = 5
LOCKOUT_DURATION_MINUTES: int = 15


def authenticate_user(
    request: HttpRequest,
    email: str,
    password: str,
) -> tuple[AdminUser, dict[str, str]]:
    """Authenticate an admin user and return JWT tokens.

    Lockout check is performed BEFORE password verification to prevent
    timing attacks that could reveal account existence.

    On 5 consecutive failures the account is locked for 15 minutes.
    On success, failed_login_count is reset to 0 and last_login_ip updated.
    Every attempt (success or failure) writes an AuditLog entry (R5).

    Args:
        request: The incoming HTTP request (used for IP extraction).
        email: The user's email address.
        password: The raw password to verify.

    Returns:
        Tuple of (AdminUser instance, {"access": ..., "refresh": ...}).

    Raises:
        ValueError: If the account is locked, credentials are invalid,
            or the account is inactive.
    """
    from apps.audit.utils import log_action

    ip_address: str = get_client_ip(request)

    # Step 1 — Look up user (do not reveal existence via timing)
    try:
        user = AdminUser.objects.get(email=email)
    except AdminUser.DoesNotExist:
        logger.warning("Login attempt for unknown email", extra={"email": email, "ip": ip_address})
        raise ValueError("Invalid credentials")

    # Step 2 — Lockout check BEFORE password verification (R3 / timing safety)
    if user.is_locked():
        retry_after: int = max(
            0,
            int((user.locked_until - timezone.now()).total_seconds()),  # type: ignore[operator]
        )
        log_action(
            action="AUTH_LOGIN_LOCKED",
            actor=None,
            target_obj=user,
            request=request,
            before={},
            after={"email": email, "ip": ip_address, "retry_after_seconds": retry_after},
        )
        raise ValueError(f"Account locked. Retry after {retry_after} seconds.")

    # Step 3 — Password verification
    authenticated_user = authenticate(request=request, username=email, password=password)

    if authenticated_user is None:
        # Increment failure counter
        user.failed_login_count += 1

        if user.failed_login_count >= MAX_FAILED_ATTEMPTS:
            user.locked_until = timezone.now() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            log_action(
                action="AUTH_ACCOUNT_LOCKED",
                actor=None,
                target_obj=user,
                request=request,
                before={"failed_login_count": user.failed_login_count - 1},
                after={
                    "failed_login_count": user.failed_login_count,
                    "locked_until": user.locked_until.isoformat(),
                    "ip": ip_address,
                },
            )
        else:
            log_action(
                action="AUTH_LOGIN_FAILED",
                actor=None,
                target_obj=user,
                request=request,
                before={"failed_login_count": user.failed_login_count - 1},
                after={"failed_login_count": user.failed_login_count, "ip": ip_address},
            )

        user.save(update_fields=["failed_login_count", "locked_until"])
        raise ValueError("Invalid credentials")

    # Step 4 — Active check
    if not authenticated_user.is_active:
        log_action(
            action="AUTH_LOGIN_INACTIVE",
            actor=None,
            target_obj=authenticated_user,
            request=request,
            before={},
            after={"email": email, "ip": ip_address},
        )
        raise ValueError("Account is inactive")

    # Step 5 — Success: reset counter, update IP
    authenticated_user.failed_login_count = 0
    authenticated_user.locked_until = None
    authenticated_user.last_login_ip = ip_address
    authenticated_user.save(update_fields=["failed_login_count", "locked_until", "last_login_ip"])

    # Step 6 — Generate JWT tokens
    refresh = RefreshToken.for_user(authenticated_user)
    tokens: dict[str, str] = {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }

    log_action(
        action="AUTH_LOGIN_SUCCESS",
        actor=authenticated_user,
        target_obj=authenticated_user,
        request=request,
        before={},
        after={"email": email, "role": authenticated_user.role, "ip": ip_address},
    )

    return authenticated_user, tokens


def logout_user(request: HttpRequest, refresh_token: str, user: AdminUser) -> None:
    """Blacklist the provided refresh token to invalidate the session.

    Args:
        request: The incoming HTTP request.
        refresh_token: The refresh token string to blacklist.
        user: The authenticated AdminUser performing the logout.

    Raises:
        ValueError: If the refresh token is invalid or already blacklisted.
    """
    from apps.audit.utils import log_action

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception as e:
        raise ValueError(f"Invalid or already blacklisted refresh token: {e}") from e

    log_action(
        action="AUTH_LOGOUT",
        actor=user,
        target_obj=user,
        request=request,
        before={},
        after={"email": user.email, "ip": get_client_ip(request)},
    )


def create_admin_user(
    email: str,
    password: str,
    full_name: str,
    role: AdminRole,
    actor: AdminUser,
    request: HttpRequest,
) -> AdminUser:
    """Create a new AdminUser account.

    Args:
        email: Unique email address for the new user.
        password: Raw password (will be hashed).
        full_name: Display name.
        role: AdminRole value to assign.
        actor: The AdminUser performing the creation (for AuditLog).
        request: The incoming HTTP request.

    Returns:
        The newly created AdminUser instance.

    Raises:
        ValueError: If email is already in use.
    """
    from apps.audit.utils import log_action

    if AdminUser.objects.filter(email=email).exists():
        raise ValueError(f"An account with email '{email}' already exists")

    user = AdminUser.objects.create_user(
        email=email,
        password=password,
        full_name=full_name,
        role=role,
    )

    log_action(
        action="ADMIN_USER_CREATED",
        actor=actor,
        target_obj=user,
        request=request,
        before={},
        after={"email": email, "role": role, "full_name": full_name},
    )

    return user
