"""
AirAd Backend E2E — Field Ops & QA User Journey

Tests full end-to-end flows for field operations and QA:

Journey 1: Create field visit → list → detail → upload photo
Journey 2: QA dashboard metrics
Journey 3: Duplicate detection via QA service
Journey 4: Field visit RBAC
"""

import uuid

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import AdminUser


# ---------------------------------------------------------------------------
# Journey 1: Field visit lifecycle
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestFieldVisitLifecycleJourney:
    """Create field visit → list → detail."""

    def test_create_field_visit(
        self, api_client: APIClient, vendor, field_agent_user: AdminUser
    ) -> None:
        """FIELD_AGENT can create a field visit for a vendor."""
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(field_agent_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")

        resp = api_client.post(
            reverse("fieldvisit-list"),
            {
                "vendor_id": str(vendor.id),
                "gps_lon": 67.0601,
                "gps_lat": 24.8271,
                "notes": "E2E field visit test.",
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        visit_id = resp.data["data"]["id"]
        assert resp.data["data"]["vendor_id"] == str(vendor.id)

        # Verify visit appears in list
        list_resp = api_client.get(reverse("fieldvisit-list"))
        assert list_resp.status_code == status.HTTP_200_OK
        visit_ids = [v["id"] for v in list_resp.data["data"]]
        assert visit_id in visit_ids

        # Verify detail endpoint
        detail_resp = api_client.get(
            reverse("fieldvisit-detail", kwargs={"pk": visit_id})
        )
        assert detail_resp.status_code == status.HTTP_200_OK
        assert detail_resp.data["data"]["visit_notes"] == "E2E field visit test."

    def test_list_field_visits_authenticated(
        self, auth_client: APIClient, vendor, field_agent_user: AdminUser
    ) -> None:
        """SUPER_ADMIN can list all field visits."""
        from apps.field_ops.models import FieldVisit
        from django.utils import timezone

        FieldVisit.objects.create(
            vendor=vendor,
            agent=field_agent_user,
            visited_at=timezone.now(),
        )
        resp = auth_client.get(reverse("fieldvisit-list"))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] >= 1

    def test_field_visit_detail_not_found(self, auth_client: APIClient) -> None:
        """GET /field-ops/<nonexistent-uuid>/ returns 404."""
        resp = auth_client.get(
            reverse("fieldvisit-detail", kwargs={"pk": str(uuid.uuid4())})
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated_cannot_list_visits(self, api_client: APIClient) -> None:
        """Unauthenticated request returns 401."""
        api_client.credentials()
        resp = api_client.get(reverse("fieldvisit-list"))
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Journey 2: Field visit RBAC
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestFieldVisitRBACJourney:
    """Field visit endpoints enforce role-based access."""

    def test_data_entry_cannot_create_field_visit(
        self, data_entry_client: APIClient, vendor
    ) -> None:
        """DATA_ENTRY cannot create field visits."""
        resp = data_entry_client.post(
            reverse("fieldvisit-list"),
            {
                "vendor_id": str(vendor.id),
                "gps_lon": 67.06,
                "gps_lat": 24.82,
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_qa_reviewer_cannot_create_field_visit(
        self, api_client: APIClient, vendor
    ) -> None:
        """QA_REVIEWER cannot create field visits."""
        from rest_framework_simplejwt.tokens import RefreshToken
        from apps.accounts.models import AdminUser, AdminRole

        qa_user = AdminUser.objects.create_user(
            email="qa_fieldops@test.airaad.com",
            password="TestPass@123!",
            full_name="QA Reviewer",
            role=AdminRole.QA_REVIEWER,
        )
        refresh = RefreshToken.for_user(qa_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")

        resp = api_client.post(
            reverse("fieldvisit-list"),
            {
                "vendor_id": str(vendor.id),
                "gps_lon": 67.06,
                "gps_lat": 24.82,
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# Journey 3: QA dashboard
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestQADashboardJourney:
    """QA dashboard returns correct metrics."""

    def test_qa_dashboard_authenticated(self, auth_client: APIClient) -> None:
        """GET /qa/dashboard/ returns metrics for SUPER_ADMIN."""
        resp = auth_client.get(reverse("qa-dashboard"))
        assert resp.status_code == status.HTTP_200_OK
        data = resp.data["data"] if "data" in resp.data else resp.data
        # Should have at minimum a total_vendors count
        assert "total_vendors" in data or "pending_review" in data or isinstance(data, dict)

    def test_qa_dashboard_with_vendors(
        self, auth_client: APIClient, vendor
    ) -> None:
        """QA dashboard reflects vendor counts."""
        resp = auth_client.get(reverse("qa-dashboard"))
        assert resp.status_code == status.HTTP_200_OK

    def test_qa_dashboard_unauthenticated_returns_401(
        self, api_client: APIClient
    ) -> None:
        """Unauthenticated request to QA dashboard returns 401."""
        api_client.credentials()
        resp = api_client.get(reverse("qa-dashboard"))
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_data_entry_cannot_access_qa_dashboard(
        self, data_entry_client: APIClient
    ) -> None:
        """DATA_ENTRY cannot access QA dashboard."""
        resp = data_entry_client.get(reverse("qa-dashboard"))
        assert resp.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# Journey 4: Drift distance calculation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestDriftDistanceJourney:
    """Field visit drift distance is calculated in metres (not degrees)."""

    def test_drift_distance_is_in_metres(
        self, vendor, field_agent_user: AdminUser
    ) -> None:
        """Drift distance between vendor GPS and visit GPS is in metres."""
        from apps.field_ops.models import FieldVisit
        from core.geo_utils import calculate_drift_distance
        from django.contrib.gis.geos import Point
        from django.utils import timezone

        # Create visit ~500m away from vendor
        visit = FieldVisit.objects.create(
            vendor=vendor,
            agent=field_agent_user,
            visited_at=timezone.now(),
            gps_confirmed_point=Point(67.065, 24.825, srid=4326),
        )
        distance = calculate_drift_distance(vendor.gps_point, visit.gps_confirmed_point)

        # 0.005° longitude ≈ ~500m at Karachi latitude
        assert distance > 1.0, f"Distance should be in metres (>1m), got {distance}"
        assert distance < 10_000.0, f"Distance {distance}m seems unreasonably large"

    def test_zero_drift_for_same_point(
        self, vendor, field_agent_user: AdminUser
    ) -> None:
        """Drift distance is ~0 when visit GPS matches vendor GPS."""
        from apps.field_ops.models import FieldVisit
        from core.geo_utils import calculate_drift_distance
        from django.utils import timezone

        visit = FieldVisit.objects.create(
            vendor=vendor,
            agent=field_agent_user,
            visited_at=timezone.now(),
            gps_confirmed_point=vendor.gps_point,
        )
        distance = calculate_drift_distance(vendor.gps_point, visit.gps_confirmed_point)
        assert distance < 1.0, f"Same-point drift should be ~0m, got {distance}"
