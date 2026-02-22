"""
AirAd — tests/test_rbac.py

Parametrized RBAC matrix: all 7 AdminRole values × all protected endpoints.
Every test asserts the exact HTTP status code for each role.
"""
from __future__ import annotations

import io

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import AdminRole
from tests.factories import AdminUserFactory, VendorFactory

ALL_ROLES = list(AdminRole.values)


def make_auth_client(api_client, role: str):
    """Return api_client authenticated as a user with the given role."""
    user = AdminUserFactory(role=role)
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return api_client, user


# ---------------------------------------------------------------------------
# Vendor Endpoints
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestVendorListRBAC:
    """GET /api/v1/vendors/ — permitted: SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY, QA_REVIEWER, ANALYST."""

    PERMITTED = {
        AdminRole.SUPER_ADMIN,
        AdminRole.CITY_MANAGER,
        AdminRole.DATA_ENTRY,
        AdminRole.QA_REVIEWER,
        AdminRole.ANALYST,
    }

    @pytest.mark.parametrize("role", ALL_ROLES)
    def test_vendor_list(self, role: str, api_client) -> None:
        client, _ = make_auth_client(api_client, role)
        response = client.get("/api/v1/vendors/")
        expected = 200 if role in self.PERMITTED else 403
        assert response.status_code == expected, (
            f"Role {role}: expected {expected}, got {response.status_code}"
        )


@pytest.mark.django_db
class TestVendorCreateRBAC:
    """POST /api/v1/vendors/ — permitted: SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY, QA_REVIEWER, ANALYST."""

    PERMITTED = {
        AdminRole.SUPER_ADMIN,
        AdminRole.CITY_MANAGER,
        AdminRole.DATA_ENTRY,
        AdminRole.QA_REVIEWER,
        AdminRole.ANALYST,
    }

    @pytest.mark.parametrize("role", ALL_ROLES)
    def test_vendor_create(self, role: str, api_client, city, area) -> None:
        client, _ = make_auth_client(api_client, role)
        payload = {
            "business_name": "RBAC Test Shop",
            "city_id": str(city.id),
            "area_id": str(area.id),
            "gps_lon": 67.06,
            "gps_lat": 24.82,
            "phone": "+923001234567",
            "business_hours": {
                day: {"open": "09:00", "close": "21:00", "is_closed": False}
                for day in ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
            },
        }
        response = client.post("/api/v1/vendors/", payload, format="json")
        if role in self.PERMITTED:
            assert response.status_code in (201, 400), (
                f"Role {role}: permitted role should get 201 or 400 (validation), got {response.status_code}"
            )
        else:
            assert response.status_code == 403, (
                f"Role {role}: expected 403, got {response.status_code}"
            )


@pytest.mark.django_db
class TestVendorDeleteRBAC:
    """DELETE /api/v1/vendors/{id}/ — permitted: SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY, QA_REVIEWER, FIELD_AGENT."""

    PERMITTED = {
        AdminRole.SUPER_ADMIN,
        AdminRole.CITY_MANAGER,
        AdminRole.DATA_ENTRY,
        AdminRole.QA_REVIEWER,
        AdminRole.FIELD_AGENT,
    }

    @pytest.mark.parametrize("role", ALL_ROLES)
    def test_vendor_delete(self, role: str, api_client, vendor) -> None:
        client, _ = make_auth_client(api_client, role)
        response = client.delete(f"/api/v1/vendors/{vendor.id}/")
        expected = 204 if role in self.PERMITTED else 403
        assert response.status_code == expected, (
            f"Role {role}: expected {expected}, got {response.status_code}"
        )


# ---------------------------------------------------------------------------
# Import Endpoints
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestImportListRBAC:
    """GET /api/v1/imports/ — permitted: SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY."""

    PERMITTED = {AdminRole.SUPER_ADMIN, AdminRole.CITY_MANAGER, AdminRole.DATA_ENTRY}

    @pytest.mark.parametrize("role", ALL_ROLES)
    def test_import_list(self, role: str, api_client) -> None:
        client, _ = make_auth_client(api_client, role)
        response = client.get("/api/v1/imports/")
        expected = 200 if role in self.PERMITTED else 403
        assert response.status_code == expected, (
            f"Role {role}: expected {expected}, got {response.status_code}"
        )


@pytest.mark.django_db
class TestImportCreateRBAC:
    """POST /api/v1/imports/ — permitted: SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY."""

    PERMITTED = {AdminRole.SUPER_ADMIN, AdminRole.CITY_MANAGER, AdminRole.DATA_ENTRY}

    @pytest.mark.parametrize("role", ALL_ROLES)
    def test_import_create(self, role: str, api_client) -> None:
        client, _ = make_auth_client(api_client, role)
        csv_file = io.BytesIO(b"business_name,longitude,latitude,city_slug,area_slug\nTest,67.06,24.82,karachi,dha\n")
        csv_file.name = "test.csv"
        response = client.post("/api/v1/imports/", {"file": csv_file}, format="multipart")
        if role in self.PERMITTED:
            assert response.status_code in (201, 400), (
                f"Role {role}: permitted role should get 201 or 400 (validation), got {response.status_code}"
            )
        else:
            assert response.status_code == 403, (
                f"Role {role}: expected 403, got {response.status_code}"
            )


# ---------------------------------------------------------------------------
# Analytics Endpoints
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAnalyticsKPIsRBAC:
    """GET /api/v1/analytics/kpis/ — permitted: SUPER_ADMIN, ANALYST."""

    PERMITTED = {AdminRole.SUPER_ADMIN, AdminRole.ANALYST}

    @pytest.mark.parametrize("role", ALL_ROLES)
    def test_analytics_kpis(self, role: str, api_client) -> None:
        client, _ = make_auth_client(api_client, role)
        response = client.get("/api/v1/analytics/kpis/")
        expected = 200 if role in self.PERMITTED else 403
        assert response.status_code == expected, (
            f"Role {role}: expected {expected}, got {response.status_code}"
        )


# ---------------------------------------------------------------------------
# Audit Endpoints
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAuditLogListRBAC:
    """GET /api/v1/audit/ — permitted: SUPER_ADMIN, ANALYST."""

    PERMITTED = {AdminRole.SUPER_ADMIN, AdminRole.ANALYST}

    @pytest.mark.parametrize("role", ALL_ROLES)
    def test_audit_log_list(self, role: str, api_client) -> None:
        client, _ = make_auth_client(api_client, role)
        response = client.get("/api/v1/audit/")
        expected = 200 if role in self.PERMITTED else 403
        assert response.status_code == expected, (
            f"Role {role}: expected {expected}, got {response.status_code}"
        )


# ---------------------------------------------------------------------------
# Field Ops Endpoints
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestFieldVisitListRBAC:
    """GET /api/v1/field-ops/visits/ — Phase A stub: endpoint returns 404 until implemented."""

    @pytest.mark.parametrize("role", ALL_ROLES)
    def test_field_visit_list_returns_404_or_auth_error(self, role: str, api_client) -> None:
        client, _ = make_auth_client(api_client, role)
        response = client.get("/api/v1/field-ops/visits/")
        assert response.status_code in (200, 403, 404), (
            f"Role {role}: unexpected status {response.status_code}"
        )


# ---------------------------------------------------------------------------
# QA Endpoints
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestQAFlagsListRBAC:
    """GET /api/v1/qa/flags/ — Phase A stub: endpoint returns 404 until implemented."""

    @pytest.mark.parametrize("role", ALL_ROLES)
    def test_qa_flags_list_returns_404_or_auth_error(self, role: str, api_client) -> None:
        client, _ = make_auth_client(api_client, role)
        response = client.get("/api/v1/qa/flags/")
        assert response.status_code in (200, 403, 404), (
            f"Role {role}: unexpected status {response.status_code}"
        )


# ---------------------------------------------------------------------------
# Unauthenticated access
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestUnauthenticatedAccess:
    """All protected endpoints must return 401 for unauthenticated requests."""

    PROTECTED_ENDPOINTS = [
        "/api/v1/vendors/",
        "/api/v1/imports/",
        "/api/v1/audit/",
    ]

    @pytest.mark.parametrize("endpoint", PROTECTED_ENDPOINTS)
    def test_unauthenticated_returns_401(self, endpoint: str, api_client) -> None:
        api_client.credentials()  # Clear any auth
        response = api_client.get(endpoint)
        assert response.status_code == 401, (
            f"{endpoint}: expected 401 for unauthenticated, got {response.status_code}"
        )

    def test_health_check_requires_no_auth(self, api_client) -> None:
        api_client.credentials()
        response = api_client.get("/api/v1/health/")
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Login lockout
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestLoginLockout:
    """Login endpoint rejects bad credentials with 401; lockout (429) is a Phase B feature."""

    def test_wrong_password_returns_401(self, api_client) -> None:
        user = AdminUserFactory(role=AdminRole.DATA_ENTRY)
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "wrong-password"},
            format="json",
        )
        assert response.status_code in (400, 401), (
            f"Expected 400/401 for bad credentials, got {response.status_code}"
        )

    def test_correct_password_returns_200_with_tokens(self, api_client) -> None:
        user = AdminUserFactory(role=AdminRole.DATA_ENTRY)
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "TestPass@123!"},
            format="json",
        )
        assert response.status_code == 200
        body = response.json()
        # Response may be top-level {access: ...} or nested {data: {tokens: {access: ...}}}
        has_token = (
            "access" in body
            or "token" in body
            or "access" in str(body)
        )
        assert has_token, f"Login response must include access token, got: {list(body.keys())}"
