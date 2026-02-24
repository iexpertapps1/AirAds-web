"""
AirAd Backend E2E — Authentication User Journey

Tests full end-to-end flows that chain multiple API calls together,
simulating real user sessions from login through to logout.

Journey 1: Login → Profile → Refresh → Logout
Journey 2: Login → Lockout after 5 failures → Retry-After header
Journey 3: Login → Create user (SUPER_ADMIN) → Login as new user
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import AdminRole, AdminUser


# ---------------------------------------------------------------------------
# Journey 1: Full session lifecycle
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestFullSessionJourney:
    """Login → get profile → refresh token → logout."""

    def test_login_profile_refresh_logout(self, api_client: APIClient, super_admin_user: AdminUser) -> None:
        """Complete session lifecycle: login, profile, refresh, logout."""
        # Step 1: Login
        login_resp = api_client.post(
            reverse("auth-login"),
            {"email": "superadmin@test.airaad.com", "password": "TestPass@123!"},
            format="json",
        )
        assert login_resp.status_code == status.HTTP_200_OK
        tokens = login_resp.data["data"]["tokens"]
        access_token = tokens["access"]
        refresh_token = tokens["refresh"]

        # Step 2: Use access token to fetch profile
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        profile_resp = api_client.get(reverse("auth-profile"))
        assert profile_resp.status_code == status.HTTP_200_OK
        assert profile_resp.data["data"]["email"] == "superadmin@test.airaad.com"
        assert profile_resp.data["data"]["role"] == "SUPER_ADMIN"

        # Step 3: Refresh access token
        api_client.credentials()  # Clear auth
        refresh_resp = api_client.post(
            reverse("auth-refresh"),
            {"refresh": refresh_token},
            format="json",
        )
        assert refresh_resp.status_code == status.HTTP_200_OK
        new_access_token = refresh_resp.data["access"]
        assert new_access_token != access_token  # New token issued

        # Step 4: Verify new token works
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {new_access_token}")
        profile_resp2 = api_client.get(reverse("auth-profile"))
        assert profile_resp2.status_code == status.HTTP_200_OK

        # Step 5: Logout (blacklists refresh token)
        logout_resp = api_client.post(
            reverse("auth-logout"),
            {"refresh": refresh_token},
            format="json",
        )
        assert logout_resp.status_code in (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT, status.HTTP_400_BAD_REQUEST)

        # Step 6: Verify old refresh token is blacklisted
        api_client.credentials()
        reuse_resp = api_client.post(
            reverse("auth-refresh"),
            {"refresh": refresh_token},
            format="json",
        )
        assert reuse_resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_profile_returns_401(self, api_client: APIClient) -> None:
        """Profile endpoint requires authentication."""
        api_client.credentials()
        resp = api_client.get(reverse("auth-profile"))
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_expired_access_token_returns_401(self, api_client: APIClient, super_admin_user: AdminUser) -> None:
        """Tampered/invalid access token returns 401."""
        api_client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token.here")
        resp = api_client.get(reverse("auth-profile"))
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Journey 2: Lockout flow
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestLoginLockoutJourney:
    """5 failed logins → account locked → Retry-After header."""

    def test_lockout_after_5_failures(self, api_client: APIClient, super_admin_user: AdminUser) -> None:
        """Account locks after 5 consecutive wrong passwords."""
        url = reverse("auth-login")
        for _ in range(5):
            resp = api_client.post(
                url,
                {"email": "superadmin@test.airaad.com", "password": "WrongPass!"},
                format="json",
            )
            assert resp.status_code in (
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # 6th attempt should be locked
        locked_resp = api_client.post(
            url,
            {"email": "superadmin@test.airaad.com", "password": "WrongPass!"},
            format="json",
        )
        assert locked_resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Retry-After" in locked_resp

    def test_correct_password_after_lockout_still_fails(
        self, api_client: APIClient, super_admin_user: AdminUser
    ) -> None:
        """Even correct password fails while account is locked."""
        url = reverse("auth-login")
        for _ in range(5):
            api_client.post(
                url,
                {"email": "superadmin@test.airaad.com", "password": "WrongPass!"},
                format="json",
            )

        # Correct password while locked
        resp = api_client.post(
            url,
            {"email": "superadmin@test.airaad.com", "password": "TestPass@123!"},
            format="json",
        )
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS


# ---------------------------------------------------------------------------
# Journey 3: SUPER_ADMIN creates a new user, new user logs in
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestCreateUserAndLoginJourney:
    """SUPER_ADMIN creates DATA_ENTRY user → new user logs in → gets profile."""

    def test_create_user_then_login(self, auth_client: APIClient) -> None:
        """SUPER_ADMIN creates a new user who can then log in."""
        # Step 1: SUPER_ADMIN creates a new DATA_ENTRY user
        create_resp = auth_client.post(
            reverse("auth-create-user"),
            {
                "email": "newdataentry@test.airaad.com",
                "full_name": "New Data Entry",
                "role": "DATA_ENTRY",
            },
            format="json",
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        assert create_resp.data["data"]["email"] == "newdataentry@test.airaad.com"
        assert create_resp.data["data"]["role"] == "DATA_ENTRY"
        assert "temp_password" in create_resp.data["data"]
        temp_password = create_resp.data["data"]["temp_password"]

        # Step 2: New user logs in with the generated temp_password
        new_client = APIClient()
        login_resp = new_client.post(
            reverse("auth-login"),
            {"email": "newdataentry@test.airaad.com", "password": temp_password},
            format="json",
        )
        assert login_resp.status_code == status.HTTP_200_OK
        new_access = login_resp.data["data"]["tokens"]["access"]

        # Step 3: New user fetches their profile
        new_client.credentials(HTTP_AUTHORIZATION=f"Bearer {new_access}")
        profile_resp = new_client.get(reverse("auth-profile"))
        assert profile_resp.status_code == status.HTTP_200_OK
        assert profile_resp.data["data"]["role"] == "DATA_ENTRY"

    def test_non_super_admin_cannot_create_user(self, data_entry_client: APIClient) -> None:
        """DATA_ENTRY cannot create new users."""
        resp = data_entry_client.post(
            reverse("auth-create-user"),
            {
                "email": "another@test.airaad.com",
                "password": "Pass@123!",
                "full_name": "Another User",
                "role": "DATA_ENTRY",
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_duplicate_email_returns_400(self, auth_client: APIClient, super_admin_user: AdminUser) -> None:
        """Creating a user with an existing email returns 400."""
        resp = auth_client.post(
            reverse("auth-create-user"),
            {
                "email": "superadmin@test.airaad.com",  # already exists
                "password": "Pass@123!",
                "full_name": "Duplicate",
                "role": "DATA_ENTRY",
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
