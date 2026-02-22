# TASK_FIX_C04 — Create `tests/test_rbac.py`
**Severity:** 🔴 CRITICAL — Phase A Quality Gate requires parametrized RBAC matrix for all 7 roles
**Session:** A-S8 | **Effort:** 45 min | **Depends on:** TASK_FIX_C02 (factories.py)

---

## PROBLEM

Only 2 RBAC spot-checks exist in `test_accounts.py`. The spec (TASK-029) requires a parametrized matrix covering all 7 `AdminRole` values against every protected endpoint. Without this, the RBAC contract is untested for 5 roles.

---

## FILE TO CREATE

**`tests/test_rbac.py`**

---

## COMPLETE IMPLEMENTATION

```python
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
    """POST /api/v1/vendors/ — permitted: SUPER_ADMIN, DATA_ENTRY."""

    PERMITTED = {AdminRole.SUPER_ADMIN, AdminRole.DATA_ENTRY}

    @pytest.mark.parametrize("role", ALL_ROLES)
    def test_vendor_create(self, role: str, api_client, city, area, category_tag) -> None:
        client, _ = make_auth_client(api_client, role)
        payload = {
            "business_name": "RBAC Test Shop",
            "city": str(city.id),
            "area": str(area.id),
            "longitude": 67.06,
            "latitude": 24.82,
            "phone_number": "+923001234567",
            "business_hours": {
                day: {"open": "09:00", "close": "21:00", "is_closed": False}
                for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            },
        }
        response = client.post("/api/v1/vendors/", payload, format="json")
        expected = 201 if role in self.PERMITTED else 403
        assert response.status_code == expected, (
            f"Role {role}: expected {expected}, got {response.status_code}"
        )


@pytest.mark.django_db
class TestVendorDeleteRBAC:
    """DELETE /api/v1/vendors/{id}/ — permitted: SUPER_ADMIN only."""

    PERMITTED = {AdminRole.SUPER_ADMIN}

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
    """GET /api/v1/imports/ — permitted: SUPER_ADMIN, DATA_ENTRY."""

    PERMITTED = {AdminRole.SUPER_ADMIN, AdminRole.DATA_ENTRY}

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
    """POST /api/v1/imports/ — permitted: SUPER_ADMIN, DATA_ENTRY."""

    PERMITTED = {AdminRole.SUPER_ADMIN, AdminRole.DATA_ENTRY}

    @pytest.mark.parametrize("role", ALL_ROLES)
    def test_import_create(self, role: str, api_client) -> None:
        client, _ = make_auth_client(api_client, role)
        csv_file = io.BytesIO(b"business_name,longitude,latitude\nTest,67.06,24.82\n")
        csv_file.name = "test.csv"
        response = client.post("/api/v1/imports/", {"file": csv_file}, format="multipart")
        expected = 201 if role in self.PERMITTED else 403
        assert response.status_code == expected, (
            f"Role {role}: expected {expected}, got {response.status_code}"
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
    """GET /api/v1/audit/ — permitted: SUPER_ADMIN only."""

    PERMITTED = {AdminRole.SUPER_ADMIN}

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
    """GET /api/v1/field-ops/visits/ — permitted: SUPER_ADMIN, FIELD_AGENT, QA_REVIEWER."""

    PERMITTED = {AdminRole.SUPER_ADMIN, AdminRole.FIELD_AGENT, AdminRole.QA_REVIEWER}

    @pytest.mark.parametrize("role", ALL_ROLES)
    def test_field_visit_list(self, role: str, api_client) -> None:
        client, _ = make_auth_client(api_client, role)
        response = client.get("/api/v1/field-ops/visits/")
        expected = 200 if role in self.PERMITTED else 403
        assert response.status_code == expected, (
            f"Role {role}: expected {expected}, got {response.status_code}"
        )


# ---------------------------------------------------------------------------
# QA Endpoints
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestQAFlagsListRBAC:
    """GET /api/v1/qa/flags/ — permitted: SUPER_ADMIN, QA_REVIEWER."""

    PERMITTED = {AdminRole.SUPER_ADMIN, AdminRole.QA_REVIEWER}

    @pytest.mark.parametrize("role", ALL_ROLES)
    def test_qa_flags_list(self, role: str, api_client) -> None:
        client, _ = make_auth_client(api_client, role)
        response = client.get("/api/v1/qa/flags/")
        expected = 200 if role in self.PERMITTED else 403
        assert response.status_code == expected, (
            f"Role {role}: expected {expected}, got {response.status_code}"
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
        "/api/v1/analytics/kpis/",
        "/api/v1/audit/",
        "/api/v1/field-ops/visits/",
        "/api/v1/qa/flags/",
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
    """Account lockout: 5 failed attempts → 429 with Retry-After header."""

    def test_lockout_after_5_failures_returns_429(self, api_client) -> None:
        user = AdminUserFactory(role=AdminRole.DATA_ENTRY)
        for _ in range(5):
            api_client.post(
                "/api/v1/auth/login/",
                {"email": user.email, "password": "wrong-password"},
                format="json",
            )
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "wrong-password"},
            format="json",
        )
        assert response.status_code == 429

    def test_retry_after_header_present_on_lockout(self, api_client) -> None:
        user = AdminUserFactory(role=AdminRole.DATA_ENTRY)
        for _ in range(5):
            api_client.post(
                "/api/v1/auth/login/",
                {"email": user.email, "password": "wrong-password"},
                format="json",
            )
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "wrong-password"},
            format="json",
        )
        assert "Retry-After" in response, "Locked-out response must include Retry-After header"

    def test_correct_password_after_lockout_still_blocked(self, api_client) -> None:
        user = AdminUserFactory(role=AdminRole.DATA_ENTRY, password="CorrectPass@123!")
        for _ in range(5):
            api_client.post(
                "/api/v1/auth/login/",
                {"email": user.email, "password": "wrong-password"},
                format="json",
            )
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "CorrectPass@123!"},
            format="json",
        )
        assert response.status_code == 429, "Locked account must reject even correct password"
```

---

## CONSTRAINTS

- `make_auth_client()` must create a **fresh** `AdminUserFactory` per test — never reuse users across parametrize iterations
- `ALL_ROLES = list(AdminRole.values)` — must include all 7 roles dynamically, not hardcoded strings
- `PERMITTED` sets use `AdminRole.<NAME>` constants — never raw strings like `"SUPER_ADMIN"`
- `api_client` fixture comes from `conftest.py` — do not redefine it
- For `TestVendorDeleteRBAC`, the `vendor` fixture must be recreated per parametrize iteration — use `VendorFactory()` inside the test if the `vendor` fixture is session-scoped
- The `TestLoginLockout` tests must use `AdminUserFactory` — not the `super_admin_user` fixture (to avoid polluting shared state)

---

## VERIFICATION

```bash
cd airaad/backend
pytest tests/test_rbac.py -v --no-header

# Expected: 7 roles × 8 endpoint groups = 56+ parametrized tests + lockout tests
# All PERMITTED roles → 200/201/204
# All BLOCKED roles → 403
# Unauthenticated → 401
# Lockout → 429 + Retry-After

# Count parametrized cases
pytest tests/test_rbac.py --collect-only -q 2>&1 | tail -3
```

---

## PYTHON EXPERT RULES APPLIED

- **Correctness:** `PERMITTED` sets use `AdminRole` constants — no magic strings
- **Type Safety:** `role: str` parameter type on all test methods
- **Performance:** `make_auth_client()` helper avoids duplicating JWT setup logic
- **Style:** One class per endpoint group; `PERMITTED` class attribute documents the contract
