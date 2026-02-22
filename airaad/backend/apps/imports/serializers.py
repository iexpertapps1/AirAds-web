"""
AirAd Backend — Imports Serializers

No business logic — validation only. Delegates to imports/services.py.
file_key is read-only — set by services.py after S3 upload.
error_log is read-only — written by append_error_log() in services.py.
"""

import logging

from rest_framework import serializers

from .models import ImportBatch, ImportStatus

logger = logging.getLogger(__name__)


class ImportBatchSerializer(serializers.ModelSerializer):
    """Read serializer for ImportBatch."""

    created_by_email = serializers.CharField(source="created_by.email", read_only=True)

    class Meta:
        model = ImportBatch
        fields = [
            "id", "file_key", "status",
            "total_rows", "processed_rows", "error_count", "error_log",
            "created_by", "created_by_email",
            "created_at", "updated_at",
        ]
        read_only_fields = fields


class CreateImportBatchSerializer(serializers.Serializer):
    """Serializer for uploading a CSV import file.

    Accepts a multipart file upload. Business logic (S3 upload, task dispatch)
    is in imports/services.py.
    """

    file = serializers.FileField(
        help_text="CSV file to import. Must have headers matching the vendor schema."
    )

    def validate_file(self, value: object) -> object:
        """Validate that the uploaded file is a CSV.

        Args:
            value: Uploaded file object.

        Returns:
            Validated file object.

        Raises:
            ValidationError: If file is not a CSV.
        """
        name = getattr(value, "name", "")
        if not name.lower().endswith(".csv"):
            raise serializers.ValidationError("Only CSV files are accepted.")
        return value
