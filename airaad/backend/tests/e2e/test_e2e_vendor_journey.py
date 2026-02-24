"""
AirAd Backend E2E — Vendor Management User Journey

Tests full end-to-end flows for vendor lifecycle:

Journey 1: Create vendor → List → Get detail → Update → QC approve → Delete
Journey 2: Create vendor → QC reject → Re-review → Flag
Journey 3: Vendor search and filter flows
Journey 4: Vendor with tags assignment
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import AdminUser


# ---------------------------------------------------------------------------
# Journey 1: Full vendor lifecycle
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestVendorLifecycleJourney:
    """Create → List → Detail → Update → QC Approve → Soft Delete."""

    def test_full_vendor_lifecycle(
        self,
        auth_client: APIClient,
        city,
        area,
        landmark,
        super_admin_user: AdminUser,
        category_tag,
    ) -> None:
        """Complete vendor lifecycle from creation to deletion."""
        # Step 1: Create vendor
        create_resp = auth_client.post(
            reverse("vendor-list"),
            {
                "business_name": "E2E Test Restaurant",
                "city_id": str(city.id),
                "area_id": str(area.id),
                "landmark_id": str(landmark.id),
                "gps_lon": 67.0601,
                "gps_lat": 24.8271,
                "phone": "+923001111111",
                "description": "E2E test vendor description.",
                "address_text": "123 E2E Street, DHA Phase 6",
                "business_hours": {
                    day: {"open": "09:00", "close": "22:00", "is_closed": False}
                    for day in ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
                },
                "data_source": "MANUAL_ENTRY",
            },
            format="json",
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        vendor_id = create_resp.data["data"]["id"]
        assert create_resp.data["data"]["business_name"] == "E2E Test Restaurant"
        assert create_resp.data["data"]["qc_status"] == "PENDING"

        # Step 2: Verify vendor appears in list
        list_resp = auth_client.get(reverse("vendor-list"))
        assert list_resp.status_code == status.HTTP_200_OK
        vendor_ids = [v["id"] for v in list_resp.data["data"]]
        assert vendor_id in vendor_ids

        # Step 3: Get vendor detail — phone should be decrypted
        detail_resp = auth_client.get(
            reverse("vendor-detail", kwargs={"pk": vendor_id})
        )
        assert detail_resp.status_code == status.HTTP_200_OK
        assert detail_resp.data["data"]["phone_number"] == "+923001111111"
        assert detail_resp.data["data"]["business_name"] == "E2E Test Restaurant"
        assert detail_resp.data["data"]["city_name"] == "Karachi"
        assert detail_resp.data["data"]["area_name"] == "DHA Phase 6"

        # Step 4: Update vendor (PATCH)
        update_resp = auth_client.patch(
            reverse("vendor-detail", kwargs={"pk": vendor_id}),
            {"description": "Updated E2E description."},
            format="json",
        )
        assert update_resp.status_code == status.HTTP_200_OK
        assert update_resp.data["data"]["description"] == "Updated E2E description."

        # Step 5: Assign category tag (required by R2 before approval)
        from apps.vendors.models import Vendor as VendorModel
        v = VendorModel.objects.get(id=vendor_id)
        v.tags.add(category_tag)

        # Step 5: QC approve
        qc_resp = auth_client.patch(
            reverse("vendor-qc-status", kwargs={"pk": vendor_id}),
            {"qc_status": "APPROVED", "qc_notes": "Verified on site."},
            format="json",
        )
        assert qc_resp.status_code == status.HTTP_200_OK
        assert qc_resp.data["data"]["qc_status"] == "APPROVED"
        assert qc_resp.data["data"]["qc_notes"] == "Verified on site."

        # Step 6: Verify QC status persisted
        detail_after_qc = auth_client.get(
            reverse("vendor-detail", kwargs={"pk": vendor_id})
        )
        assert detail_after_qc.data["data"]["qc_status"] == "APPROVED"

        # Step 7: Soft delete
        delete_resp = auth_client.delete(
            reverse("vendor-detail", kwargs={"pk": vendor_id})
        )
        assert delete_resp.status_code == status.HTTP_204_NO_CONTENT

        # Step 8: Verify vendor is gone from list (soft deleted)
        from apps.vendors.models import Vendor
        assert not Vendor.objects.filter(id=vendor_id).exists()
        assert Vendor.all_objects.filter(id=vendor_id, is_deleted=True).exists()

        # Step 9: GET on deleted vendor returns 404
        gone_resp = auth_client.get(
            reverse("vendor-detail", kwargs={"pk": vendor_id})
        )
        assert gone_resp.status_code == status.HTTP_404_NOT_FOUND

    def test_vendor_not_in_list_after_soft_delete(
        self, auth_client: APIClient, vendor
    ) -> None:
        """Soft-deleted vendor does not appear in list endpoint."""
        vendor_id = str(vendor.id)

        # Confirm it's in the list
        list_before = auth_client.get(reverse("vendor-list"))
        ids_before = [v["id"] for v in list_before.data["data"]]
        assert vendor_id in ids_before

        # Delete it
        auth_client.delete(reverse("vendor-detail", kwargs={"pk": vendor_id}))

        # Confirm it's gone from list
        list_after = auth_client.get(reverse("vendor-list"))
        ids_after = [v["id"] for v in list_after.data["data"]]
        assert vendor_id not in ids_after


# ---------------------------------------------------------------------------
# Journey 2: QC status transitions
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestQCStatusTransitionJourney:
    """PENDING → REJECTED → NEEDS_REVIEW → APPROVED → FLAGGED."""

    def test_qc_status_transitions(self, auth_client: APIClient, vendor, category_tag) -> None:
        """QC status can transition through all valid states."""
        vendor_id = str(vendor.id)
        qc_url = reverse("vendor-qc-status", kwargs={"pk": vendor_id})

        # PENDING → REJECTED
        resp = auth_client.patch(
            qc_url,
            {"qc_status": "REJECTED", "qc_notes": "Missing info."},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["data"]["qc_status"] == "REJECTED"

        # REJECTED → NEEDS_REVIEW
        resp = auth_client.patch(
            qc_url,
            {"qc_status": "NEEDS_REVIEW", "qc_notes": "Resubmitted."},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["data"]["qc_status"] == "NEEDS_REVIEW"

        # Assign category tag before approval (R2)
        vendor.tags.add(category_tag)

        # NEEDS_REVIEW → APPROVED
        resp = auth_client.patch(
            qc_url,
            {"qc_status": "APPROVED", "qc_notes": "All good."},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["data"]["qc_status"] == "APPROVED"

        # APPROVED → FLAGGED
        resp = auth_client.patch(
            qc_url,
            {"qc_status": "FLAGGED", "qc_notes": "Suspicious duplicate."},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["data"]["qc_status"] == "FLAGGED"

    def test_invalid_qc_status_returns_400(self, auth_client: APIClient, vendor) -> None:
        """Invalid QC status value returns 400."""
        resp = auth_client.patch(
            reverse("vendor-qc-status", kwargs={"pk": str(vendor.id)}),
            {"qc_status": "INVALID_STATUS"},
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_qc_status_update_writes_audit_log(
        self, auth_client: APIClient, vendor, category_tag
    ) -> None:
        """QC status change creates an AuditLog entry."""
        from apps.audit.models import AuditLog

        vendor.tags.add(category_tag)

        before = AuditLog.objects.filter(action="VENDOR_QC_STATUS_CHANGED").count()
        auth_client.patch(
            reverse("vendor-qc-status", kwargs={"pk": str(vendor.id)}),
            {"qc_status": "APPROVED", "qc_notes": "Verified."},
            format="json",
        )
        after = AuditLog.objects.filter(action="VENDOR_QC_STATUS_CHANGED").count()
        assert after == before + 1


# ---------------------------------------------------------------------------
# Journey 3: Vendor search and filter
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestVendorSearchFilterJourney:
    """Vendor list filtering by QC status, city, search term."""

    def test_filter_by_qc_status_pending(self, auth_client: APIClient, vendor) -> None:
        """Filter by qc_status=PENDING returns only PENDING vendors."""
        resp = auth_client.get(reverse("vendor-list"), {"qc_status": "PENDING"})
        assert resp.status_code == status.HTTP_200_OK
        for v in resp.data["data"]:
            assert v["qc_status"] == "PENDING"

    def test_filter_by_qc_status_approved_excludes_pending(
        self, auth_client: APIClient, vendor
    ) -> None:
        """Filter by qc_status=APPROVED excludes PENDING vendors."""
        resp = auth_client.get(reverse("vendor-list"), {"qc_status": "APPROVED"})
        assert resp.status_code == status.HTTP_200_OK
        # Our fixture vendor is PENDING — should not appear
        vendor_ids = [v["id"] for v in resp.data["data"]]
        assert str(vendor.id) not in vendor_ids

    def test_search_by_business_name(self, auth_client: APIClient, vendor) -> None:
        """Search by business_name returns matching vendors."""
        resp = auth_client.get(reverse("vendor-list"), {"search": "Test Grill"})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] >= 1
        names = [v["business_name"] for v in resp.data["data"]]
        assert any("Test Grill" in name for name in names)

    def test_search_no_match_returns_empty(self, auth_client: APIClient, vendor) -> None:
        """Search with no matching term returns empty results."""
        resp = auth_client.get(
            reverse("vendor-list"), {"search": "ZZZNOMATCHXXX"}
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 0

    def test_pagination_page_size(self, auth_client: APIClient, vendor) -> None:
        """page_size param limits results."""
        resp = auth_client.get(reverse("vendor-list"), {"page_size": 1})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["data"]) <= 1


# ---------------------------------------------------------------------------
# Journey 4: Vendor creation audit trail
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestVendorAuditTrailJourney:
    """Creating and modifying vendors writes correct audit log entries."""

    def test_vendor_creation_writes_audit_log(
        self, auth_client: APIClient, city, area
    ) -> None:
        """POST /vendors/ writes VENDOR_CREATED audit log."""
        from apps.audit.models import AuditLog

        before = AuditLog.objects.filter(action="VENDOR_CREATED").count()
        auth_client.post(
            reverse("vendor-list"),
            {
                "business_name": "Audit Trail Vendor",
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
        after = AuditLog.objects.filter(action="VENDOR_CREATED").count()
        assert after == before + 1

    def test_vendor_deletion_writes_audit_log(
        self, auth_client: APIClient, vendor
    ) -> None:
        """DELETE /vendors/<pk>/ writes VENDOR_DELETED audit log."""
        from apps.audit.models import AuditLog

        before = AuditLog.objects.filter(action="VENDOR_DELETED").count()
        auth_client.delete(reverse("vendor-detail", kwargs={"pk": str(vendor.id)}))
        after = AuditLog.objects.filter(action="VENDOR_DELETED").count()
        assert after == before + 1
