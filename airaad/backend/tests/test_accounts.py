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

    def test_profile_returns_role(self, auth_client, super_admin_user):
        """Profile response includes the user's role."""
        url = reverse("auth-profile")
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["role"] == "SUPER_ADMIN"


@pytest.mark.django_db
class TestTokenRefreshView:
    """Tests for POST /api/v1/auth/token/refresh/."""

    def test_refresh_returns_new_access_token(self, api_client, super_admin_user):
        """Valid refresh token returns a new access token."""
        login_url = reverse("auth-login")
        login_resp = api_client.post(
            login_url,
            {"email": "superadmin@test.airaad.com", "password": "TestPass@123!"},
            format="json",
        )
        assert login_resp.status_code == status.HTTP_200_OK
        refresh_token = login_resp.data["data"]["tokens"]["refresh"]

        refresh_url = reverse("auth-refresh")
        response = api_client.post(refresh_url, {"refresh": refresh_token}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_refresh_with_invalid_token_returns_401(self, api_client):
        """Invalid refresh token returns 401."""
        refresh_url = reverse("auth-refresh")
        response = api_client.post(refresh_url, {"refresh": "invalid.token.here"}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_with_missing_token_returns_400(self, api_client):
        """Missing refresh token returns 400."""
        refresh_url = reverse("auth-refresh")
        response = api_client.post(refresh_url, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogoutView:
    """Tests for POST /api/v1/auth/logout/."""

    def test_logout_blacklists_refresh_token(self, api_client, super_admin_user):
        """Logout blacklists the refresh token — subsequent refresh returns 401."""
        login_url = reverse("auth-login")
        login_resp = api_client.post(
            login_url,
            {"email": "superadmin@test.airaad.com", "password": "TestPass@123!"},
            format="json",
        )
        tokens = login_resp.data["data"]["tokens"]
        access_token = tokens["access"]
        refresh_token = tokens["refresh"]

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        logout_url = reverse("auth-logout")
        logout_resp = api_client.post(logout_url, {"refresh": refresh_token}, format="json")
        assert logout_resp.status_code in (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT)

        # Refresh token must now be blacklisted
        api_client.credentials()
        reuse_resp = api_client.post(
            reverse("auth-refresh"), {"refresh": refresh_token}, format="json"
        )
        assert reuse_resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_unauthenticated_returns_401(self, api_client):
        """Logout without authentication returns 401."""
        api_client.credentials()
        logout_url = reverse("auth-logout")
        response = api_client.post(logout_url, {"refresh": "sometoken"}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserListView:
    """Tests for GET /api/v1/auth/users/."""

    def test_super_admin_can_list_users(self, auth_client, super_admin_user, data_entry_user):
        """SUPER_ADMIN can list all users."""
        url = reverse("auth-user-list")
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        emails = [u["email"] for u in response.data["data"]]
        assert "superadmin@test.airaad.com" in emails

    def test_data_entry_cannot_list_users(self, data_entry_client):
        """DATA_ENTRY cannot list users — returns 403."""
        url = reverse("auth-user-list")
        response = data_entry_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_list_users(self, api_client):
        """Unauthenticated request returns 401."""
        url = reverse("auth-user-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserUpdateView:
    """Tests for PATCH /api/v1/auth/users/<id>/."""

    def test_super_admin_can_deactivate_user(self, auth_client, data_entry_user):
        """SUPER_ADMIN can deactivate a user by setting is_active=False."""
        url = reverse("auth-user-detail", kwargs={"pk": str(data_entry_user.id)})
        response = auth_client.patch(url, {"is_active": False}, format="json")
        assert response.status_code == status.HTTP_200_OK
        data_entry_user.refresh_from_db()
        assert data_entry_user.is_active is False

    def test_super_admin_can_update_user_role(self, auth_client, data_entry_user):
        """SUPER_ADMIN can change a user's role."""
        url = reverse("auth-user-detail", kwargs={"pk": str(data_entry_user.id)})
        response = auth_client.patch(url, {"role": "QA_REVIEWER"}, format="json")
        assert response.status_code == status.HTTP_200_OK
        data_entry_user.refresh_from_db()
        assert data_entry_user.role == "QA_REVIEWER"

    def test_data_entry_cannot_update_users(self, data_entry_client, super_admin_user):
        """DATA_ENTRY cannot update other users."""
        url = reverse("auth-user-detail", kwargs={"pk": str(super_admin_user.id)})
        response = data_entry_client.patch(url, {"is_active": False}, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_nonexistent_user_returns_404(self, auth_client):
        """PATCH on non-existent user UUID returns 404."""
        import uuid
        url = reverse("auth-user-detail", kwargs={"pk": str(uuid.uuid4())})
        response = auth_client.patch(url, {"is_active": False}, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND
