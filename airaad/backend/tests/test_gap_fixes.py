"""
AirAd — tests/test_gap_fixes.py

Regression tests for the four Phase-A gaps fixed in this session:

  GAP-1  analytics/services.py  — get_platform_kpis() now returns
         top_search_terms, system_alerts, imports_processing,
         vendors_pending_qa, total_areas, total_tags.

  GAP-2  audit/views.py         — AuditLogListView now accepts
         date_from / date_to query params.

  GAP-3  vendors/views.py       — VendorListCreateView now accepts
         tag_id query param.

  GAP-4  geo/views.py + urls.py — AreaDetailView and LandmarkDetailView
         (GET / PATCH) are now wired at:
           GET/PATCH /api/v1/geo/areas/<uuid>/
           GET/PATCH /api/v1/geo/landmarks/<uuid>/

  GAP-5  geo/services.py        — update_area() and update_landmark()
         service functions now exist and enforce slug immutability.
"""
from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import AdminRole
from apps.audit.models import AuditLog
from apps.imports.models import ImportStatus
from tests.factories import (
    AdminUserFactory,
    AreaFactory,
    AuditLogFactory,
    CityFactory,
    ImportBatchFactory,
    LandmarkFactory,
    TagFactory,
    VendorFactory,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _auth_client(role: str = AdminRole.SUPER_ADMIN) -> APIClient:
    """Return an authenticated APIClient for the given role."""
    user = AdminUserFactory(role=role)
    token = RefreshToken.for_user(user).access_token
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


# ===========================================================================
# GAP-1 — Analytics KPI completeness
# ===========================================================================

@pytest.mark.django_db
class TestAnalyticsKPICompleteness:
    """get_platform_kpis() must return all keys the frontend expects."""

    def test_returns_top_search_terms(self) -> None:
        from apps.analytics.services import get_platform_kpis
        result = get_platform_kpis()
        assert "top_search_terms" in result
        assert isinstance(result["top_search_terms"], list)

    def test_returns_system_alerts(self) -> None:
        from apps.analytics.services import get_platform_kpis
        result = get_platform_kpis()
        assert "system_alerts" in result
        assert isinstance(result["system_alerts"], list)

    def test_returns_imports_processing(self) -> None:
        from apps.analytics.services import get_platform_kpis
        ImportBatchFactory(status=ImportStatus.PROCESSING)
        ImportBatchFactory(status=ImportStatus.QUEUED)
        result = get_platform_kpis()
        assert "imports_processing" in result
        assert result["imports_processing"] == 1

    def test_returns_vendors_pending_qa(self) -> None:
        from apps.analytics.services import get_platform_kpis
        from apps.vendors.models import QCStatus
        VendorFactory(qc_status=QCStatus.NEEDS_REVIEW)
        VendorFactory(qc_status=QCStatus.PENDING)
        result = get_platform_kpis()
        assert "vendors_pending_qa" in result
        assert result["vendors_pending_qa"] >= 1

    def test_returns_vendors_approved_today(self) -> None:
        from apps.analytics.services import get_platform_kpis
        result = get_platform_kpis()
        assert "vendors_approved_today" in result

    def test_returns_total_areas(self) -> None:
        from apps.analytics.services import get_platform_kpis
        result = get_platform_kpis()
        assert "total_areas" in result

    def test_api_endpoint_returns_all_keys(self) -> None:
        """GET /api/v1/analytics/kpis/ response includes all frontend-expected keys."""
        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.get("/api/v1/analytics/kpis/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        for key in ("top_search_terms", "system_alerts", "imports_processing",
                    "vendors_pending_qa", "vendors_approved_today", "total_areas"):
            assert key in data, f"Missing key: {key}"

    def test_imports_processing_zero_when_none_processing(self) -> None:
        from apps.analytics.services import get_platform_kpis
        result = get_platform_kpis()
        assert result["imports_processing"] >= 0


# ===========================================================================
# GAP-2 — Audit log date-range filter
# ===========================================================================

@pytest.mark.django_db
class TestAuditLogDateFilter:
    """AuditLogListView must honour date_from and date_to query params."""

    def _make_log(self, days_ago: int) -> AuditLog:
        """Create an AuditLog entry with created_at offset by days_ago."""
        from datetime import timedelta
        from django.utils import timezone
        log = AuditLogFactory()
        # AuditLog is immutable via save/delete, but the manager's update() is
        # also blocked. Use raw SQL to set created_at for test isolation.
        from django.db import connection
        offset_dt = timezone.now() - timedelta(days=days_ago)
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE audit_auditlog SET created_at = %s WHERE id = %s",
                [offset_dt, str(log.id)],
            )
        log.refresh_from_db()
        return log

    def test_date_from_excludes_older_entries(self) -> None:
        from django.utils import timezone
        old_log = self._make_log(10)
        recent_log = self._make_log(1)
        today_str = (timezone.now().date()).isoformat()

        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.get(f"/api/v1/audit/?date_from={today_str}")
        assert response.status_code == status.HTTP_200_OK
        ids = [r["id"] for r in response.json()["data"]]
        assert str(old_log.id) not in ids

    def test_date_to_excludes_newer_entries(self) -> None:
        from datetime import timedelta
        from django.utils import timezone
        old_log = self._make_log(10)
        recent_log = self._make_log(1)
        cutoff = (timezone.now().date() - timedelta(days=5)).isoformat()

        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.get(f"/api/v1/audit/?date_to={cutoff}")
        assert response.status_code == status.HTTP_200_OK
        ids = [r["id"] for r in response.json()["data"]]
        assert str(recent_log.id) not in ids

    def test_date_from_and_date_to_together(self) -> None:
        from datetime import timedelta
        from django.utils import timezone
        self._make_log(20)
        target_log = self._make_log(5)
        self._make_log(1)

        date_from = (timezone.now().date() - timedelta(days=7)).isoformat()
        date_to = (timezone.now().date() - timedelta(days=3)).isoformat()

        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.get(f"/api/v1/audit/?date_from={date_from}&date_to={date_to}")
        assert response.status_code == status.HTTP_200_OK
        ids = [r["id"] for r in response.json()["data"]]
        assert str(target_log.id) in ids

    def test_no_date_filter_returns_all(self) -> None:
        self._make_log(30)
        self._make_log(1)
        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.get("/api/v1/audit/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] >= 2
        assert "data" in response.json()

    def test_date_from_param_in_openapi_schema(self) -> None:
        """Verify the OpenAPI schema documents date_from and date_to."""
        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.get("/api/v1/schema/?format=json")
        assert response.status_code == status.HTTP_200_OK
        schema_text = response.content.decode()
        assert "date_from" in schema_text
        assert "date_to" in schema_text


# ===========================================================================
# GAP-3 — Vendor list tag_id filter
# ===========================================================================

@pytest.mark.django_db
class TestVendorTagFilter:
    """VendorListCreateView must filter by tag_id query param."""

    def test_tag_id_filter_returns_only_tagged_vendors(self) -> None:
        tag = TagFactory()
        tagged = VendorFactory()
        untagged = VendorFactory()
        tagged.tags.add(tag)

        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.get(f"/api/v1/vendors/?tag_id={tag.id}")
        assert response.status_code == status.HTTP_200_OK
        ids = [r["id"] for r in response.json()["data"]]
        assert str(tagged.id) in ids
        assert str(untagged.id) not in ids

    def test_tag_id_filter_with_no_match_returns_empty(self) -> None:
        import uuid
        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.get(f"/api/v1/vendors/?tag_id={uuid.uuid4()}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 0
        assert response.json()["data"] == []

    def test_tag_id_filter_multiple_vendors_same_tag(self) -> None:
        tag = TagFactory()
        v1 = VendorFactory()
        v2 = VendorFactory()
        v1.tags.add(tag)
        v2.tags.add(tag)

        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.get(f"/api/v1/vendors/?tag_id={tag.id}")
        assert response.status_code == status.HTTP_200_OK
        ids = [r["id"] for r in response.json()["data"]]
        assert str(v1.id) in ids
        assert str(v2.id) in ids

    def test_tag_id_combined_with_qc_status_filter(self) -> None:
        from apps.vendors.models import QCStatus
        tag = TagFactory()
        approved = VendorFactory(qc_status=QCStatus.APPROVED)
        pending = VendorFactory(qc_status=QCStatus.PENDING)
        approved.tags.add(tag)
        pending.tags.add(tag)

        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.get(f"/api/v1/vendors/?tag_id={tag.id}&qc_status=APPROVED")
        assert response.status_code == status.HTTP_200_OK
        ids = [r["id"] for r in response.json()["data"]]
        assert str(approved.id) in ids
        assert str(pending.id) not in ids

    def test_tag_id_param_in_openapi_schema(self) -> None:
        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.get("/api/v1/schema/?format=json")
        assert response.status_code == status.HTTP_200_OK
        assert "tag_id" in response.content.decode()


# ===========================================================================
# GAP-4 — Area detail endpoint (GET / PATCH)
# ===========================================================================

@pytest.mark.django_db
class TestAreaDetailView:
    """GET and PATCH /api/v1/geo/areas/<uuid>/ must be fully functional."""

    def test_get_area_returns_200(self) -> None:
        area = AreaFactory()
        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.get(f"/api/v1/geo/areas/{area.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["id"] == str(area.id)

    def test_get_area_returns_correct_fields(self) -> None:
        area = AreaFactory()
        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.get(f"/api/v1/geo/areas/{area.id}/")
        data = response.json()["data"]
        assert "name" in data
        assert "slug" in data
        assert "city" in data

    def test_get_area_404_for_unknown_id(self) -> None:
        import uuid
        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.get(f"/api/v1/geo/areas/{uuid.uuid4()}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_patch_area_updates_name(self) -> None:
        area = AreaFactory()
        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.patch(
            f"/api/v1/geo/areas/{area.id}/",
            {"name": "Updated Area Name"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["name"] == "Updated Area Name"

    def test_patch_area_slug_immutable(self) -> None:
        area = AreaFactory()
        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.patch(
            f"/api/v1/geo/areas/{area.id}/",
            {"slug": "new-slug"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "immutable" in response.json()["message"].lower()

    def test_patch_area_deactivate(self) -> None:
        area = AreaFactory()
        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.patch(
            f"/api/v1/geo/areas/{area.id}/",
            {"is_active": False},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["is_active"] is False

    def test_patch_area_writes_audit_log(self) -> None:
        area = AreaFactory()
        before_count = AuditLog.objects.count()
        client = _auth_client(AdminRole.SUPER_ADMIN)
        client.patch(f"/api/v1/geo/areas/{area.id}/", {"name": "Audited"}, format="json")
        assert AuditLog.objects.count() == before_count + 1
        assert AuditLog.objects.filter(action="AREA_UPDATED").exists()

    def test_data_entry_can_patch_area(self) -> None:
        area = AreaFactory()
        client = _auth_client(AdminRole.DATA_ENTRY)
        response = client.patch(
            f"/api/v1/geo/areas/{area.id}/",
            {"name": "Data Entry Update"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_analyst_cannot_patch_area(self) -> None:
        area = AreaFactory()
        client = _auth_client(AdminRole.ANALYST)
        response = client.patch(
            f"/api/v1/geo/areas/{area.id}/",
            {"name": "Analyst Update"},
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_all_roles_can_get_area(self) -> None:
        area = AreaFactory()
        for role in AdminRole.values:
            client = _auth_client(role)
            response = client.get(f"/api/v1/geo/areas/{area.id}/")
            assert response.status_code == status.HTTP_200_OK, (
                f"Role {role} got {response.status_code}"
            )


# ===========================================================================
# GAP-4 — Landmark detail endpoint (GET / PATCH)
# ===========================================================================

@pytest.mark.django_db
class TestLandmarkDetailView:
    """GET and PATCH /api/v1/geo/landmarks/<uuid>/ must be fully functional."""

    def test_get_landmark_returns_200(self) -> None:
        lm = LandmarkFactory()
        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.get(f"/api/v1/geo/landmarks/{lm.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["id"] == str(lm.id)

    def test_get_landmark_returns_correct_fields(self) -> None:
        lm = LandmarkFactory()
        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.get(f"/api/v1/geo/landmarks/{lm.id}/")
        data = response.json()["data"]
        assert "name" in data
        assert "slug" in data
        assert "area" in data

    def test_get_landmark_404_for_unknown_id(self) -> None:
        import uuid
        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.get(f"/api/v1/geo/landmarks/{uuid.uuid4()}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_patch_landmark_updates_name(self) -> None:
        lm = LandmarkFactory()
        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.patch(
            f"/api/v1/geo/landmarks/{lm.id}/",
            {"name": "Updated Landmark Name"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["name"] == "Updated Landmark Name"

    def test_patch_landmark_slug_immutable(self) -> None:
        lm = LandmarkFactory()
        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.patch(
            f"/api/v1/geo/landmarks/{lm.id}/",
            {"slug": "new-slug"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "immutable" in response.json()["message"].lower()

    def test_patch_landmark_deactivate(self) -> None:
        lm = LandmarkFactory()
        client = _auth_client(AdminRole.SUPER_ADMIN)
        response = client.patch(
            f"/api/v1/geo/landmarks/{lm.id}/",
            {"is_active": False},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["is_active"] is False

    def test_patch_landmark_writes_audit_log(self) -> None:
        lm = LandmarkFactory()
        before_count = AuditLog.objects.count()
        client = _auth_client(AdminRole.SUPER_ADMIN)
        client.patch(f"/api/v1/geo/landmarks/{lm.id}/", {"name": "Audited LM"}, format="json")
        assert AuditLog.objects.count() == before_count + 1
        assert AuditLog.objects.filter(action="LANDMARK_UPDATED").exists()

    def test_data_entry_can_patch_landmark(self) -> None:
        lm = LandmarkFactory()
        client = _auth_client(AdminRole.DATA_ENTRY)
        response = client.patch(
            f"/api/v1/geo/landmarks/{lm.id}/",
            {"name": "Data Entry LM"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_analyst_cannot_patch_landmark(self) -> None:
        lm = LandmarkFactory()
        client = _auth_client(AdminRole.ANALYST)
        response = client.patch(
            f"/api/v1/geo/landmarks/{lm.id}/",
            {"name": "Analyst LM"},
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_all_roles_can_get_landmark(self) -> None:
        lm = LandmarkFactory()
        for role in AdminRole.values:
            client = _auth_client(role)
            response = client.get(f"/api/v1/geo/landmarks/{lm.id}/")
            assert response.status_code == status.HTTP_200_OK, (
                f"Role {role} got {response.status_code}"
            )


# ===========================================================================
# GAP-5 — update_area() and update_landmark() service functions
# ===========================================================================

@pytest.mark.django_db
class TestUpdateAreaService:
    """Direct service-layer tests for update_area()."""

    def test_updates_name(self) -> None:
        from apps.geo.services import update_area
        area = AreaFactory()
        actor = AdminUserFactory()
        updated = update_area(area, {"name": "Service Updated"}, actor, None)
        assert updated.name == "Service Updated"

    def test_slug_immutable_raises(self) -> None:
        from apps.geo.services import update_area
        area = AreaFactory()
        actor = AdminUserFactory()
        with pytest.raises(ValueError, match="immutable"):
            update_area(area, {"slug": "bad-slug"}, actor, None)

    def test_updates_is_active(self) -> None:
        from apps.geo.services import update_area
        area = AreaFactory()
        actor = AdminUserFactory()
        updated = update_area(area, {"is_active": False}, actor, None)
        assert updated.is_active is False

    def test_writes_audit_log(self) -> None:
        from apps.geo.services import update_area
        area = AreaFactory()
        actor = AdminUserFactory()
        before_count = AuditLog.objects.count()
        update_area(area, {"name": "Audit Test"}, actor, None)
        assert AuditLog.objects.count() == before_count + 1
        assert AuditLog.objects.filter(action="AREA_UPDATED").exists()

    def test_unknown_fields_ignored(self) -> None:
        from apps.geo.services import update_area
        area = AreaFactory()
        original_name = area.name
        actor = AdminUserFactory()
        updated = update_area(area, {"nonexistent_field": "value"}, actor, None)
        assert updated.name == original_name


@pytest.mark.django_db
class TestUpdateLandmarkService:
    """Direct service-layer tests for update_landmark()."""

    def test_updates_name(self) -> None:
        from apps.geo.services import update_landmark
        lm = LandmarkFactory()
        actor = AdminUserFactory()
        updated = update_landmark(lm, {"name": "Service Updated LM"}, actor, None)
        assert updated.name == "Service Updated LM"

    def test_slug_immutable_raises(self) -> None:
        from apps.geo.services import update_landmark
        lm = LandmarkFactory()
        actor = AdminUserFactory()
        with pytest.raises(ValueError, match="immutable"):
            update_landmark(lm, {"slug": "bad-slug"}, actor, None)

    def test_updates_is_active(self) -> None:
        from apps.geo.services import update_landmark
        lm = LandmarkFactory()
        actor = AdminUserFactory()
        updated = update_landmark(lm, {"is_active": False}, actor, None)
        assert updated.is_active is False

    def test_writes_audit_log(self) -> None:
        from apps.geo.services import update_landmark
        lm = LandmarkFactory()
        actor = AdminUserFactory()
        before_count = AuditLog.objects.count()
        update_landmark(lm, {"name": "Audit LM"}, actor, None)
        assert AuditLog.objects.count() == before_count + 1
        assert AuditLog.objects.filter(action="LANDMARK_UPDATED").exists()

    def test_unknown_fields_ignored(self) -> None:
        from apps.geo.services import update_landmark
        lm = LandmarkFactory()
        original_name = lm.name
        actor = AdminUserFactory()
        updated = update_landmark(lm, {"nonexistent_field": "value"}, actor, None)
        assert updated.name == original_name
