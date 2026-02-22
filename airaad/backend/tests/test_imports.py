"""
Tests for apps/imports — ImportBatch model, services, tasks.
"""

import pytest
from unittest.mock import MagicMock, patch


@pytest.mark.django_db
class TestImportBatchModel:
    """Tests for ImportBatch model behaviour."""

    def test_import_batch_created_with_queued_status(self, import_batch):
        """ImportBatch is created with QUEUED status."""
        from apps.imports.models import ImportStatus
        assert import_batch.status == ImportStatus.QUEUED

    def test_import_batch_str(self, import_batch):
        """__str__ includes batch ID and status."""
        assert "QUEUED" in str(import_batch)


@pytest.mark.django_db
class TestAppendErrorLog:
    """Tests for imports/services.append_error_log()."""

    def test_append_error_log_adds_entry(self, import_batch):
        """append_error_log() adds an error dict to error_log."""
        from apps.imports.services import append_error_log

        append_error_log(import_batch, {"row": 1, "field": "phone", "msg": "invalid"})
        import_batch.refresh_from_db()
        assert len(import_batch.error_log) == 1
        assert import_batch.error_log[0]["row"] == 1

    def test_append_error_log_cap_at_1000(self, import_batch):
        """append_error_log() silently drops entries beyond 1000 (R9)."""
        from apps.imports.services import append_error_log

        for i in range(1001):
            append_error_log(import_batch, {"row": i, "field": "x", "msg": "err"})

        import_batch.refresh_from_db()
        assert len(import_batch.error_log) == 1000

    def test_append_error_log_updates_error_count(self, import_batch):
        """append_error_log() keeps error_count in sync."""
        from apps.imports.services import append_error_log

        append_error_log(import_batch, {"row": 1, "field": "x", "msg": "err"})
        append_error_log(import_batch, {"row": 2, "field": "y", "msg": "err"})
        import_batch.refresh_from_db()
        assert import_batch.error_count == 2


@pytest.mark.django_db
class TestValidateRow:
    """Tests for imports/tasks._validate_row()."""

    def test_valid_row_returns_no_errors(self):
        """A fully valid row returns an empty error list."""
        from apps.imports.tasks import _validate_row

        row = {
            "business_name": "Test Shop",
            "longitude": "67.06",
            "latitude": "24.82",
            "city_slug": "karachi",
            "area_slug": "dha-phase-6",
        }
        assert _validate_row(row, 1) == []

    def test_missing_business_name_returns_error(self):
        """Missing business_name returns an error dict."""
        from apps.imports.tasks import _validate_row

        row = {
            "business_name": "",
            "longitude": "67.06",
            "latitude": "24.82",
            "city_slug": "karachi",
            "area_slug": "dha-phase-6",
        }
        errors = _validate_row(row, 1)
        assert any(e["field"] == "business_name" for e in errors)

    def test_invalid_longitude_returns_error(self):
        """Non-numeric longitude returns an error dict."""
        from apps.imports.tasks import _validate_row

        row = {
            "business_name": "Test",
            "longitude": "not-a-number",
            "latitude": "24.82",
            "city_slug": "karachi",
            "area_slug": "dha-phase-6",
        }
        errors = _validate_row(row, 1)
        assert any(e["field"] == "longitude" for e in errors)

    def test_missing_city_slug_returns_error(self):
        """Missing city_slug returns an error dict."""
        from apps.imports.tasks import _validate_row

        row = {
            "business_name": "Test",
            "longitude": "67.06",
            "latitude": "24.82",
            "city_slug": "",
            "area_slug": "dha-phase-6",
        }
        errors = _validate_row(row, 1)
        assert any(e["field"] == "city_slug" for e in errors)


@pytest.mark.django_db
class TestProcessImportBatchTask:
    """Tests for process_import_batch Celery task."""

    def test_idempotency_guard_skips_processing_batch(self, import_batch):
        """Task exits early if batch is already PROCESSING."""
        from apps.imports.models import ImportStatus
        from apps.imports.tasks import process_import_batch

        import_batch.status = ImportStatus.PROCESSING
        import_batch.save()

        # Should return without error
        process_import_batch(str(import_batch.id))

        import_batch.refresh_from_db()
        assert import_batch.status == ImportStatus.PROCESSING

    def test_nonexistent_batch_id_does_not_raise(self):
        """Task with non-existent batch_id logs error and returns cleanly."""
        import uuid
        from apps.imports.tasks import process_import_batch

        # Should not raise
        process_import_batch(str(uuid.uuid4()))

    @patch("apps.imports.tasks.boto3.client")
    def test_s3_failure_marks_batch_failed(self, mock_boto, import_batch):
        """S3 fetch failure marks batch as FAILED and retries."""
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
