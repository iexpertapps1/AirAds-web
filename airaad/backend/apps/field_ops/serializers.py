"""
AirAd Backend — Field Ops Serializers

No business logic — validation only. Delegates to field_ops/services.py.
s3_key is read-only — set by services.py after S3 upload.
photo_url is a presigned URL generated on read via services.py.
"""

import logging

from rest_framework import serializers

from .models import FieldPhoto, FieldVisit

logger = logging.getLogger(__name__)


class FieldVisitSerializer(serializers.ModelSerializer):
    """Read serializer for FieldVisit."""

    agent_email = serializers.CharField(source="agent.email", read_only=True)
    vendor_name = serializers.CharField(source="vendor.business_name", read_only=True)
    gps_confirmed_point = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FieldVisit
        fields = [
            "id", "vendor", "vendor_name",
            "agent", "agent_email",
            "visited_at", "visit_notes",
            "gps_confirmed_point",
            "created_at",
        ]
        read_only_fields = ["id", "agent", "agent_email", "vendor_name", "gps_confirmed_point", "created_at"]

    def get_gps_confirmed_point(self, obj: FieldVisit) -> dict | None:
        """Return confirmed GPS point as {longitude, latitude} dict.

        Args:
            obj: FieldVisit instance.

        Returns:
            Dict with longitude and latitude, or None.
        """
        if obj.gps_confirmed_point:
            return {"longitude": obj.gps_confirmed_point.x, "latitude": obj.gps_confirmed_point.y}
        return None


class CreateFieldVisitSerializer(serializers.Serializer):
    """Serializer for creating a FieldVisit. Delegates to field_ops/services.py."""

    vendor_id = serializers.UUIDField()
    visited_at = serializers.DateTimeField(required=False, allow_null=True)
    visit_notes = serializers.CharField(required=False, default="", allow_blank=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)

    def validate(self, attrs: dict) -> dict:
        """Validate that longitude and latitude are provided together.

        Args:
            attrs: Validated field data.

        Returns:
            Validated attrs dict.

        Raises:
            ValidationError: If only one of longitude/latitude is provided.
        """
        has_lon = attrs.get("longitude") is not None
        has_lat = attrs.get("latitude") is not None
        if has_lon != has_lat:
            raise serializers.ValidationError("longitude and latitude must be provided together.")
        return attrs


class FieldPhotoSerializer(serializers.ModelSerializer):
    """Read serializer for FieldPhoto — includes presigned URL."""

    photo_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FieldPhoto
        fields = [
            "id", "field_visit", "s3_key",
            "photo_url", "caption", "is_active", "uploaded_at",
        ]
        read_only_fields = ["id", "s3_key", "photo_url", "uploaded_at"]

    def get_photo_url(self, obj: FieldPhoto) -> str:
        """Generate a presigned S3 URL for the photo.

        Args:
            obj: FieldPhoto instance.

        Returns:
            Presigned HTTPS URL string.
        """
        from apps.field_ops.services import get_field_photo_url
        try:
            return get_field_photo_url(obj)
        except Exception as e:
            logger.error("Failed to generate presigned URL", extra={"photo_id": str(obj.id), "error": str(e)})
            return ""


class UploadFieldPhotoSerializer(serializers.Serializer):
    """Serializer for uploading a FieldPhoto. Delegates to field_ops/services.py."""

    file = serializers.ImageField(help_text="Photo file (JPEG, PNG).")
    caption = serializers.CharField(max_length=500, required=False, default="", allow_blank=True)
