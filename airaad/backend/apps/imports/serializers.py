"""
AirAd Backend — Imports Serializers

No business logic — validation only. Delegates to imports/services.py.
file_key is read-only — set by services.py after S3 upload.
error_log is read-only — written by append_error_log() in services.py.
"""

import logging

from rest_framework import serializers

from .models import ImportBatch

logger = logging.getLogger(__name__)


class ImportBatchSerializer(serializers.ModelSerializer):
    """Read serializer for ImportBatch."""

    created_by_email = serializers.CharField(source="created_by.email", read_only=True, default="")
    uploaded_by_email = serializers.SerializerMethodField()
    area_name = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    vendors_created = serializers.SerializerMethodField()
    vendors_failed = serializers.SerializerMethodField()

    class Meta:
        model = ImportBatch
        fields = [
            "id", "import_type", "file_key", "file_name", "status",
            "total_rows", "processed_rows", "error_count", "error_log",
            "vendors_created", "vendors_failed",
            "search_query", "radius_m", "area_name",
            "created_by", "created_by_email", "uploaded_by_email",
            "created_at", "updated_at",
        ]
        read_only_fields = fields

    def get_area_name(self, obj: ImportBatch) -> str:
        """Return related area name or empty string for CSV imports."""
        if obj.area_id and hasattr(obj, "area") and obj.area:
            return obj.area.name
        return ""

    def get_file_name(self, obj: ImportBatch) -> str:
        """Return a human-readable file name for the import batch."""
        if obj.file_key:
            # Extract basename from S3 key for CSV imports
            return obj.file_key.rsplit("/", 1)[-1] if "/" in obj.file_key else obj.file_key
        area_name = self.get_area_name(obj)
        if obj.import_type == "GOOGLE_PLACES_ENHANCED":
            return f"Enhanced GP — {area_name}" if area_name else "Enhanced Google Places"
        if obj.import_type == "GOOGLE_PLACES":
            return f"Google Places — {area_name}" if area_name else "Google Places"
        return "CSV Import"

    def get_uploaded_by_email(self, obj: ImportBatch) -> str:
        """Return uploader email — alias for created_by.email."""
        if obj.created_by_id and obj.created_by:
            return obj.created_by.email
        return ""

    def get_vendors_created(self, obj: ImportBatch) -> int:
        """Return count of successfully created vendors."""
        return max(obj.processed_rows - obj.error_count, 0)

    def get_vendors_failed(self, obj: ImportBatch) -> int:
        """Return count of failed vendor rows."""
        return obj.error_count


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
