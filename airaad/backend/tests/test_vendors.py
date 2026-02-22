"""
Tests for apps/vendors — model, services, views.
"""

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestVendorModel:
    """Tests for Vendor model behaviour."""

    def test_soft_delete_sets_is_deleted(self, vendor):
        """delete() sets is_deleted=True — never hard-deletes (R6)."""
        vendor_id = vendor.id
        vendor.delete()

        from apps.vendors.models import Vendor
        assert Vendor.all_objects.filter(id=vendor_id, is_deleted=True).exists()

    def test_default_manager_excludes_deleted(self, vendor):
        """Default objects manager excludes is_deleted=True vendors."""
        from apps.vendors.models import Vendor

        vendor.delete()
        assert not Vendor.objects.filter(id=vendor.id).exists()

    def test_all_objects_includes_deleted(self, vendor):
        """all_objects manager includes is_deleted=True vendors."""
        from apps.vendors.models import Vendor

        vendor.delete()
        assert Vendor.all_objects.filter(id=vendor.id).exists()

    def test_str_representation(self, vendor):
        """__str__ includes business_name and qc_status."""
        assert "Test Grill House" in str(vendor)
        assert "PENDING" in str(vendor)


@pytest.mark.django_db
class TestVendorServices:
    """Tests for vendors/services.py."""

    def test_create_vendor_encrypts_phone(self, vendor):
        """Phone is stored encrypted — not as plaintext."""
        assert vendor.phone_number_encrypted != b""
        assert b"+923001234567" not in bytes(vendor.phone_number_encrypted)

    def test_decrypt_phone_returns_plaintext(self, vendor):
        """decrypt_phone() returns the original phone number."""
        from apps.vendors.services import decrypt_phone

        assert decrypt_phone(vendor.phone_number_encrypted) == "+923001234567"

    def test_create_vendor_validates_business_hours(self, city, area, super_admin_user):
        """Invalid business_hours raises ValueError."""
        from apps.vendors.services import create_vendor

        with pytest.raises(ValueError, match="business_hours"):
            create_vendor(
                business_name="Bad Hours Vendor",
                slug="bad-hours-vendor",
                city_id=str(city.id),
                area_id=str(area.id),
                gps_lon=67.06,
                gps_lat=24.82,
                actor=super_admin_user,
                request=None,
                business_hours={"MON": {"open": "18:00", "close": "09:00", "is_closed": False}},
            )

    def test_create_vendor_duplicate_slug_raises(self, vendor, city, area, super_admin_user):
        """Duplicate slug raises ValueError."""
        from apps.vendors.services import create_vendor

        with pytest.raises(ValueError, match="slug"):
            create_vendor(
                business_name="Another Vendor",
                slug="test-grill-house",  # same slug as fixture
                city_id=str(city.id),
                area_id=str(area.id),
                gps_lon=67.06,
                gps_lat=24.82,
                actor=super_admin_user,
                request=None,
            )

    def test_update_qc_status(self, vendor, qa_reviewer_user):
        """update_qc_status() updates status and reviewer fields."""
        from apps.vendors.services import update_qc_status

        updated = update_qc_status(
            vendor=vendor,
            new_status="APPROVED",
            reviewer=qa_reviewer_user,
            request=None,
            notes="Looks good.",
        )
        assert updated.qc_status == "APPROVED"
        assert updated.qc_reviewed_by == qa_reviewer_user
        assert updated.qc_notes == "Looks good."

    def test_update_qc_status_invalid_raises(self, vendor, qa_reviewer_user):
        """Invalid QC status raises ValueError."""
        from apps.vendors.services import update_qc_status

        with pytest.raises(ValueError, match="Invalid QC status"):
            update_qc_status(
                vendor=vendor,
                new_status="INVALID_STATUS",
                reviewer=qa_reviewer_user,
                request=None,
            )

    def test_soft_delete_writes_audit_log(self, vendor, super_admin_user):
        """soft_delete_vendor() writes an AuditLog entry."""
        from apps.audit.models import AuditLog
        from apps.vendors.services import soft_delete_vendor

        before_count = AuditLog.objects.filter(action="VENDOR_DELETED").count()
        soft_delete_vendor(vendor=vendor, actor=super_admin_user, request=None)
        assert AuditLog.objects.filter(action="VENDOR_DELETED").count() == before_count + 1


@pytest.mark.django_db
class TestVendorViews:
    """Integration tests for vendor API endpoints."""

    def test_list_vendors_authenticated(self, auth_client, vendor):
        """GET /api/v1/vendors/ returns paginated vendor list."""
        url = reverse("vendor-list")
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_list_vendors_unauthenticated_returns_401(self, api_client):
        """Unauthenticated request returns 401."""
        url = reverse("vendor-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_vendor_detail_returns_decrypted_phone(self, auth_client, vendor):
        """GET /api/v1/vendors/<pk>/ returns decrypted phone_number."""
        url = reverse("vendor-detail", kwargs={"pk": str(vendor.id)})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["phone_number"] == "+923001234567"

    def test_get_vendor_detail_not_found(self, auth_client):
        """GET with non-existent UUID returns 404."""
        import uuid
        url = reverse("vendor-detail", kwargs={"pk": str(uuid.uuid4())})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_vendor_soft_deletes(self, auth_client, vendor):
        """DELETE /api/v1/vendors/<pk>/ soft-deletes — returns 204."""
        url = reverse("vendor-detail", kwargs={"pk": str(vendor.id)})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        from apps.vendors.models import Vendor
        assert not Vendor.objects.filter(id=vendor.id).exists()
        assert Vendor.all_objects.filter(id=vendor.id, is_deleted=True).exists()

    def test_data_entry_can_delete_vendor(self, data_entry_client, vendor):
        """DATA_ENTRY role can soft-delete vendors — VendorDetailView permits DATA_ENTRY."""
        url = reverse("vendor-detail", kwargs={"pk": str(vendor.id)})
        response = data_entry_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_qc_status_update(self, auth_client, vendor):
        """PATCH /api/v1/vendors/<pk>/qc-status/ updates QC status."""
        url = reverse("vendor-qc-status", kwargs={"pk": str(vendor.id)})
        response = auth_client.patch(
            url,
            {"qc_status": "APPROVED", "qc_notes": "Verified on site."},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["qc_status"] == "APPROVED"
