"""
Tests for apps/accounts — AdminUser model, RolePermission, auth views.
"""

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestAdminUserModel:
    """Tests for AdminUser model behaviour."""

    def test_create_user_sets_email_and_role(self, super_admin_user):
        """create_user() sets email and role correctly."""
        assert super_admin_user.email == "superadmin@test.airaad.com"
        assert super_admin_user.role == "SUPER_ADMIN"

    def test_is_locked_false_when_no_lockout(self, super_admin_user):
        """is_locked() returns False when locked_until is None."""
        assert super_admin_user.is_locked() is False

    def test_is_locked_true_when_future_lockout(self, super_admin_user):
        """is_locked() returns True when locked_until is in the future."""
        from django.utils import timezone
        from datetime import timedelta

        super_admin_user.locked_until = timezone.now() + timedelta(minutes=15)
        super_admin_user.save()
        assert super_admin_user.is_locked() is True

    def test_is_locked_false_when_past_lockout(self, super_admin_user):
        """is_locked() returns False when locked_until is in the past."""
        from django.utils import timezone
        from datetime import timedelta

        super_admin_user.locked_until = timezone.now() - timedelta(minutes=1)
        super_admin_user.save()
        assert super_admin_user.is_locked() is False

    def test_str_representation(self, super_admin_user):
        """__str__ includes email and role."""
        assert "superadmin@test.airaad.com" in str(super_admin_user)
        assert "SUPER_ADMIN" in str(super_admin_user)

    def test_create_user_empty_email_raises(self):
        """create_user() raises ValueError for empty email."""
        from apps.accounts.models import AdminUser

        with pytest.raises(ValueError, match="email"):
            AdminUser.objects.create_user(email="", password="pass")


@pytest.mark.django_db
class TestRolePermission:
    """Tests for RolePermission.for_roles() factory."""

    def test_for_roles_returns_permission_class(self):
        """for_roles() returns a class, not an instance."""
        from apps.accounts.models import AdminRole
        from apps.accounts.permissions import RolePermission

        perm_class = RolePermission.for_roles(AdminRole.SUPER_ADMIN)
        assert isinstance(perm_class, type)

    def test_for_roles_no_args_raises_value_error(self):
        """for_roles() with no arguments raises ValueError."""
        from apps.accounts.permissions import RolePermission

        with pytest.raises(ValueError):
            RolePermission.for_roles()

    def test_has_permission_correct_role(self, super_admin_user, api_client):
        """has_permission() returns True for a user with an allowed role."""
        from apps.accounts.models import AdminRole
        from apps.accounts.permissions import RolePermission
        from unittest.mock import MagicMock

        perm_class = RolePermission.for_roles(AdminRole.SUPER_ADMIN)
        perm = perm_class()

        request = MagicMock()
        request.user = super_admin_user
        # AdminUser.is_authenticated is a read-only property — do not assign it

        assert perm.has_permission(request, MagicMock()) is True

    def test_has_permission_wrong_role(self, data_entry_user):
        """has_permission() returns False for a user with a disallowed role."""
        from apps.accounts.models import AdminRole
        from apps.accounts.permissions import RolePermission
        from unittest.mock import MagicMock

        perm_class = RolePermission.for_roles(AdminRole.SUPER_ADMIN)
        perm = perm_class()

        request = MagicMock()
        request.user = data_entry_user
        # AdminUser.is_authenticated is a read-only property — do not assign it

        assert perm.has_permission(request, MagicMock()) is False

    def test_has_permission_unauthenticated(self):
        """has_permission() returns False for unauthenticated requests."""
        from apps.accounts.models import AdminRole
        from apps.accounts.permissions import RolePermission
        from unittest.mock import MagicMock

        perm_class = RolePermission.for_roles(AdminRole.SUPER_ADMIN)
        perm = perm_class()

        request = MagicMock()
        request.user = None

        assert perm.has_permission(request, MagicMock()) is False


@pytest.mark.django_db
class TestLoginView:
    """Integration tests for POST /api/v1/auth/login/."""

    def test_login_success_returns_tokens(self, api_client, super_admin_user):
        """Valid credentials return access and refresh tokens."""
        url = reverse("auth-login")
        response = api_client.post(
            url,
            {"email": "superadmin@test.airaad.com", "password": "TestPass@123!"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert "access" in response.data["data"]["tokens"]
        assert "refresh" in response.data["data"]["tokens"]

    def test_login_wrong_password_returns_401(self, api_client, super_admin_user):
        """Wrong password returns 401."""
        url = reverse("auth-login")
        response = api_client.post(
            url,
            {"email": "superadmin@test.airaad.com", "password": "WrongPassword!"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_login_unknown_email_returns_401(self, api_client):
        """Unknown email returns 401."""
        url = reverse("auth-login")
        response = api_client.post(
            url,
            {"email": "nobody@test.airaad.com", "password": "SomePass!"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_fields_returns_400(self, api_client):
        """Missing email/password returns 400."""
        url = reverse("auth-login")
        response = api_client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_lockout_after_5_failures(self, api_client, super_admin_user):
        """Account is locked after 5 consecutive failed login attempts."""
        url = reverse("auth-login")
        for _ in range(5):
            api_client.post(
                url,
                {"email": "superadmin@test.airaad.com", "password": "WrongPassword!"},
                format="json",
            )
        response = api_client.post(
            url,
            {"email": "superadmin@test.airaad.com", "password": "WrongPassword!"},
            format="json",
        )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Retry-After" in response


@pytest.mark.django_db
class TestProfileView:
    """Tests for GET /api/v1/auth/profile/."""

    def test_profile_authenticated_returns_user(self, auth_client, super_admin_user):
        """Authenticated request returns user profile."""
        url = reverse("auth-profile")
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["email"] == "superadmin@test.airaad.com"

    def test_profile_unauthenticated_returns_401(self, api_client):
        """Unauthenticated request returns 401."""
        url = reverse("auth-profile")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
