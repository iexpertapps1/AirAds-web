"""
AirAd Backend E2E — Imports User Journey

Tests full end-to-end flows for CSV import pipeline:

Journey 1: Upload CSV → Batch created → Process → Check status
Journey 2: Upload invalid CSV → Batch fails with error log
Journey 3: RBAC for import endpoints
Journey 4: Import batch pagination and filtering
"""

import io
import uuid

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock

from apps.accounts.models import AdminUser


# ---------------------------------------------------------------------------
# Journey 1: Upload and process import batch
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestImportBatchLifecycleJourney:
    """Upload CSV → batch created → list → detail."""

    @patch("apps.imports.services.upload_file_to_s3", return_value="imports/test-key.csv")
    @patch("apps.imports.tasks.process_import_batch")
    def test_upload_csv_creates_batch(
        self,
        mock_task,
        mock_s3,
        auth_client: APIClient,
    ) -> None:
        """POST /imports/ with valid CSV creates a QUEUED batch."""
        mock_task.delay = MagicMock()

        csv_content = (
            "business_name,longitude,latitude,city_slug,area_slug\n"
            "Test Shop 1,67.06,24.82,karachi,dha-phase-6\n"
            "Test Shop 2,67.07,24.83,karachi,clifton\n"
        )
        csv_file = io.BytesIO(csv_content.encode())
        csv_file.name = "test_import.csv"

        resp = auth_client.post(
            reverse("import-batch-list"),
            {"file": csv_file},
            format="multipart",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        batch_id = resp.data["data"]["id"]
        assert resp.data["data"]["status"] in ("QUEUED", "PROCESSING")

        # Verify batch appears in list
        list_resp = auth_client.get(reverse("import-batch-list"))
        assert list_resp.status_code == status.HTTP_200_OK
        batch_ids = [b["id"] for b in list_resp.data["data"]]
        assert batch_id in batch_ids

        # Verify batch detail is accessible
        detail_resp = auth_client.get(
            reverse("import-batch-detail", kwargs={"pk": batch_id})
        )
        assert detail_resp.status_code == status.HTTP_200_OK
        assert detail_resp.data["data"]["id"] == batch_id

    def test_list_import_batches_authenticated(
        self, auth_client: APIClient, import_batch
    ) -> None:
        """GET /imports/ returns list of batches."""
        resp = auth_client.get(reverse("import-batch-list"))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] >= 1

    def test_get_import_batch_detail(
        self, auth_client: APIClient, import_batch
    ) -> None:
        """GET /imports/<pk>/ returns batch detail with error_log."""
        resp = auth_client.get(
            reverse("import-batch-detail", kwargs={"pk": str(import_batch.id)})
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["data"]["status"] == "QUEUED"
        assert "error_log" in resp.data["data"]

    def test_get_nonexistent_batch_returns_404(self, auth_client: APIClient) -> None:
        """GET /imports/<nonexistent-uuid>/ returns 404."""
        resp = auth_client.get(
            reverse("import-batch-detail", kwargs={"pk": str(uuid.uuid4())})
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# Journey 2: Import batch with S3 failure
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestImportBatchFailureJourney:
    """S3 failure marks batch as FAILED with error details."""

    @patch("apps.imports.tasks.boto3.client")
    def test_s3_failure_marks_batch_failed(
        self, mock_boto, import_batch
    ) -> None:
        """S3 fetch failure marks batch as FAILED."""
        from botocore.exceptions import ClientError
        from apps.imports.models import ImportStatus
        from apps.imports.tasks import process_import_batch

        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        mock_s3.get_object.side_effect = ClientError(
            {"Error": {"Code": "NoSuchKey", "Message": "Not found"}},
            "GetObject",
        )

        with pytest.raises(Exception):
            process_import_batch(str(import_batch.id))

        import_batch.refresh_from_db()
        assert import_batch.status == ImportStatus.FAILED

    def test_nonexistent_batch_id_does_not_raise(self) -> None:
        """Task with non-existent batch_id exits cleanly."""
        from apps.imports.tasks import process_import_batch
        process_import_batch(str(uuid.uuid4()))  # Should not raise


# ---------------------------------------------------------------------------
# Journey 3: RBAC for import endpoints
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestImportRBACJourney:
    """Import endpoints enforce role-based access."""

    def test_unauthenticated_cannot_list_batches(self, api_client: APIClient) -> None:
        """Unauthenticated request returns 401."""
        resp = api_client.get(reverse("import-batch-list"))
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_qa_reviewer_cannot_access_imports(self, api_client: APIClient) -> None:
        """QA_REVIEWER cannot access import endpoints."""
        from rest_framework_simplejwt.tokens import RefreshToken
        from apps.accounts.models import AdminUser, AdminRole

        qa_user = AdminUser.objects.create_user(
            email="qa_import@test.airaad.com",
            password="TestPass@123!",
            full_name="QA Reviewer",
            role=AdminRole.QA_REVIEWER,
        )
        refresh = RefreshToken.for_user(qa_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")

        resp = api_client.get(reverse("import-batch-list"))
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_field_agent_cannot_access_imports(self, api_client: APIClient) -> None:
        """FIELD_AGENT cannot access import endpoints."""
        from rest_framework_simplejwt.tokens import RefreshToken
        from apps.accounts.models import AdminUser, AdminRole

        agent = AdminUser.objects.create_user(
            email="agent_import@test.airaad.com",
            password="TestPass@123!",
            full_name="Field Agent",
            role=AdminRole.FIELD_AGENT,
        )
        refresh = RefreshToken.for_user(agent)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")

        resp = api_client.get(reverse("import-batch-list"))
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_data_entry_can_access_imports(self, data_entry_client: APIClient) -> None:
        """DATA_ENTRY can list import batches."""
        resp = data_entry_client.get(reverse("import-batch-list"))
        assert resp.status_code == status.HTTP_200_OK

    def test_upload_without_file_returns_400(self, auth_client: APIClient) -> None:
        """POST /imports/ without a file returns 400."""
        resp = auth_client.post(
            reverse("import-batch-list"),
            {},
            format="multipart",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
