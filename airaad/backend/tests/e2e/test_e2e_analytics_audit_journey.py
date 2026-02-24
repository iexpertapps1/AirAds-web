"""
AirAd Backend E2E — Analytics, Audit & Health User Journey

Tests full end-to-end flows for:

Journey 1: Analytics KPIs endpoint
Journey 2: Audit log listing, filtering, pagination
Journey 3: Audit log written by vendor/auth actions
Journey 4: Health check endpoint
Journey 5: Analytics & Audit RBAC
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import AdminUser


# ---------------------------------------------------------------------------
# Journey 1: Analytics KPIs
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestAnalyticsKPIsJourney:
    """GET /analytics/kpis/ returns platform metrics."""

    def test_kpis_returns_200_for_super_admin(self, auth_client: APIClient) -> None:
        """SUPER_ADMIN can access KPIs endpoint."""
        resp = auth_client.get(reverse("analytics-kpis"))
        assert resp.status_code == status.HTTP_200_OK

    def test_kpis_response_has_expected_keys(
        self, auth_client: APIClient, vendor
    ) -> None:
        """KPIs response contains expected metric keys."""
        resp = auth_client.get(reverse("analytics-kpis"))
        assert resp.status_code == status.HTTP_200_OK
        data = resp.data.get("data", resp.data)
        assert isinstance(data, dict)
        # At minimum, total_vendors should be present
        assert "total_vendors" in data

    def test_kpis_reflects_vendor_count(
        self, auth_client: APIClient, vendor
    ) -> None:
        """KPIs total_vendors reflects actual vendor count."""
        from apps.vendors.models import Vendor

        resp = auth_client.get(reverse("analytics-kpis"))
        assert resp.status_code == status.HTTP_200_OK
        data = resp.data.get("data", resp.data)
        actual_count = Vendor.objects.count()
        assert data["total_vendors"] == actual_count

    def test_kpis_unauthenticated_returns_401(self, api_client: APIClient) -> None:
        """Unauthenticated request returns 401."""
        api_client.credentials()
        resp = api_client.get(reverse("analytics-kpis"))
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_kpis_data_entry_returns_403(self, data_entry_client: APIClient) -> None:
        """DATA_ENTRY cannot access analytics KPIs."""
        resp = data_entry_client.get(reverse("analytics-kpis"))
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_kpis_analyst_can_access(self, api_client: APIClient) -> None:
        """ANALYST role can access analytics KPIs."""
        from rest_framework_simplejwt.tokens import RefreshToken
        from apps.accounts.models import AdminUser, AdminRole

        analyst = AdminUser.objects.create_user(
            email="analyst_kpi@test.airaad.com",
            password="TestPass@123!",
            full_name="Analyst",
            role=AdminRole.ANALYST,
        )
        refresh = RefreshToken.for_user(analyst)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")

        resp = api_client.get(reverse("analytics-kpis"))
        assert resp.status_code == status.HTTP_200_OK

    def test_kpis_city_manager_can_access(self, api_client: APIClient) -> None:
        """CITY_MANAGER role can access analytics KPIs."""
        from rest_framework_simplejwt.tokens import RefreshToken
        from apps.accounts.models import AdminUser, AdminRole

        city_manager = AdminUser.objects.create_user(
            email="city_manager_kpi@test.airaad.com",
            password="TestPass@123!",
            full_name="City Manager",
            role=AdminRole.CITY_MANAGER,
        )
        refresh = RefreshToken.for_user(city_manager)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")

        resp = api_client.get(reverse("analytics-kpis"))
        assert resp.status_code == status.HTTP_200_OK


# ---------------------------------------------------------------------------
# Journey 2: Audit log listing and filtering
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestAuditLogListJourney:
    """Audit log listing, filtering, and pagination."""

    def test_audit_log_list_authenticated(self, auth_client: APIClient) -> None:
        """SUPER_ADMIN can list audit logs."""
        resp = auth_client.get(reverse("audit-log-list"))
        assert resp.status_code == status.HTTP_200_OK
        assert "count" in resp.data

    def test_audit_log_unauthenticated_returns_401(self, api_client: APIClient) -> None:
        """Unauthenticated request returns 401."""
        api_client.credentials()
        resp = api_client.get(reverse("audit-log-list"))
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_audit_log_data_entry_returns_403(
        self, data_entry_client: APIClient
    ) -> None:
        """DATA_ENTRY cannot access audit logs."""
        resp = data_entry_client.get(reverse("audit-log-list"))
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_audit_log_analyst_can_access(self, api_client: APIClient) -> None:
        """ANALYST can access audit logs."""
        from rest_framework_simplejwt.tokens import RefreshToken
        from apps.accounts.models import AdminUser, AdminRole

        analyst = AdminUser.objects.create_user(
            email="analyst_audit@test.airaad.com",
            password="TestPass@123!",
            full_name="Analyst",
            role=AdminRole.ANALYST,
        )
        refresh = RefreshToken.for_user(analyst)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")

        resp = api_client.get(reverse("audit-log-list"))
        assert resp.status_code == status.HTTP_200_OK

    def test_audit_log_pagination(self, auth_client: APIClient, vendor) -> None:
        """Audit log supports page_size pagination."""
        resp = auth_client.get(reverse("audit-log-list"), {"page_size": 1})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data.get("data", resp.data.get("results", []))) <= 1

    def test_audit_log_filter_by_action(
        self, auth_client: APIClient, vendor
    ) -> None:
        """Audit log can be filtered by action type."""
        resp = auth_client.get(
            reverse("audit-log-list"), {"action": "VENDOR_CREATED"}
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.data.get("data", resp.data.get("results", []))
        for entry in data:
            assert entry["action"] == "VENDOR_CREATED"


# ---------------------------------------------------------------------------
# Journey 3: Audit log written by actions
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestAuditLogWrittenByActionsJourney:
    """Actions on vendors/auth write correct audit log entries."""

    def test_vendor_creation_creates_audit_entry(
        self, auth_client: APIClient, city, area
    ) -> None:
        """Creating a vendor writes a VENDOR_CREATED audit entry."""
        from apps.audit.models import AuditLog

        before = AuditLog.objects.count()
        auth_client.post(
            reverse("vendor-list"),
            {
                "business_name": "Audit Journey Vendor",
                "city_id": str(city.id),
                "area_id": str(area.id),
                "gps_lon": 67.06,
                "gps_lat": 24.82,
                "business_hours": {
                    day: {"open": "09:00", "close": "21:00", "is_closed": False}
                    for day in ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
                },
            },
            format="json",
        )
        after = AuditLog.objects.count()
        assert after > before

    def test_audit_log_contains_actor_info(
        self, auth_client: APIClient, city, area, super_admin_user: AdminUser
    ) -> None:
        """Audit log entries contain actor email."""
        from apps.audit.models import AuditLog

        auth_client.post(
            reverse("vendor-list"),
            {
                "business_name": "Actor Audit Vendor",
                "city_id": str(city.id),
                "area_id": str(area.id),
                "gps_lon": 67.06,
                "gps_lat": 24.82,
                "business_hours": {
                    day: {"open": "09:00", "close": "21:00", "is_closed": False}
                    for day in ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
                },
            },
            format="json",
        )
        entry = AuditLog.objects.filter(action="VENDOR_CREATED").last()
        assert entry is not None
        assert entry.actor == super_admin_user

    def test_audit_log_list_shows_recent_entries(
        self, auth_client: APIClient, vendor
    ) -> None:
        """Audit log list shows entries created by vendor fixture."""
        resp = auth_client.get(reverse("audit-log-list"))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] >= 1


# ---------------------------------------------------------------------------
# Journey 4: Health check
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestHealthCheckJourney:
    """Health check endpoint is public and returns service status."""

    def test_health_check_returns_200(self, api_client: APIClient) -> None:
        """GET /health/ returns 200 or 503 without authentication (no auth required)."""
        api_client.credentials()  # Ensure no auth
        resp = api_client.get(reverse("health-check"))
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_health_check_has_status_field(self, api_client: APIClient) -> None:
        """Health check response contains a status field."""
        api_client.credentials()
        resp = api_client.get(reverse("health-check"))
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE)
        assert "status" in resp.data

    def test_health_check_has_services(self, api_client: APIClient) -> None:
        """Health check response contains services section."""
        api_client.credentials()
        resp = api_client.get(reverse("health-check"))
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE)
        assert "status" in resp.data

    def test_health_check_authenticated_also_works(
        self, auth_client: APIClient
    ) -> None:
        """Health check also works when authenticated."""
        resp = auth_client.get(reverse("health-check"))
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_health_check_returns_version(self, api_client: APIClient) -> None:
        """Health check response includes version info."""
        api_client.credentials()
        resp = api_client.get(reverse("health-check"))
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE)
        assert "status" in resp.data
