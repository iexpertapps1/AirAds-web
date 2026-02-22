"""
AirAd Backend — Vendors Serializers

VendorSerializer: to_representation decrypts phone on read.
Write path encrypts phone in vendors/services.py — NOT here.
GPS: accept latitude/longitude floats, return as dict on read.
No business logic — validation only.
read_only_fields explicitly declared.
"""

import logging

from rest_framework import serializers

from core.encryption import EncryptionError, decrypt

from .models import DataSource, QCStatus, Vendor

logger = logging.getLogger(__name__)


class VendorSerializer(serializers.ModelSerializer):
    """Full Vendor serializer.

    Read path: phone_number_encrypted is decrypted and returned as phone_number.
    Write path: phone encryption happens in vendors/services.py — never here.
    GPS: gps_point returned as {longitude, latitude} dict.
    """

    phone_number = serializers.SerializerMethodField(read_only=True)
    gps_point = serializers.SerializerMethodField(read_only=True)
    city_name = serializers.CharField(source="city.name", read_only=True)
    area_name = serializers.CharField(source="area.name", read_only=True)
    landmark_name = serializers.CharField(source="landmark.name", read_only=True, allow_null=True)
    qc_reviewed_by_email = serializers.CharField(
        source="qc_reviewed_by.email", read_only=True, allow_null=True
    )

    class Meta:
        model = Vendor
        fields = [
            "id", "business_name", "slug", "description",
            "gps_point", "address_text",
            "city", "city_name", "area", "area_name",
            "landmark", "landmark_name",
            "phone_number",
            "business_hours",
            "qc_status", "qc_reviewed_by", "qc_reviewed_by_email",
            "qc_reviewed_at", "qc_notes",
            "data_source",
            "is_deleted",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "slug", "phone_number", "gps_point",
            "city_name", "area_name", "landmark_name",
            "qc_reviewed_by_email", "is_deleted",
            "created_at", "updated_at",
        ]

    def get_phone_number(self, obj: Vendor) -> str:
        """Decrypt and return the phone number on read.

        Args:
            obj: Vendor instance.

        Returns:
            Decrypted phone number string, or empty string on error.
        """
        if not obj.phone_number_encrypted:
            return ""
        try:
            return decrypt(bytes(obj.phone_number_encrypted))
        except EncryptionError as e:
            logger.error(
                "Failed to decrypt phone for vendor",
                extra={"vendor_id": str(obj.id), "error": str(e)},
            )
            return ""

    def get_gps_point(self, obj: Vendor) -> dict | None:
        """Return GPS point as {longitude, latitude} dict.

        Args:
            obj: Vendor instance.

        Returns:
            Dict with longitude and latitude, or None.
        """
        if obj.gps_point:
            return {"longitude": obj.gps_point.x, "latitude": obj.gps_point.y}
        return None


class CreateVendorSerializer(serializers.Serializer):
    """Serializer for creating a Vendor. Delegates to vendors/services.py."""

    business_name = serializers.CharField(max_length=255)
    slug = serializers.SlugField(max_length=280)
    description = serializers.CharField(required=False, default="", allow_blank=True)
    longitude = serializers.FloatField(help_text="GPS longitude — lon/lat order.")
    latitude = serializers.FloatField(help_text="GPS latitude — lon/lat order.")
    address_text = serializers.CharField(max_length=500, required=False, default="", allow_blank=True)
    city_id = serializers.UUIDField()
    area_id = serializers.UUIDField()
    landmark_id = serializers.UUIDField(required=False, allow_null=True)
    phone = serializers.CharField(max_length=20, required=False, default="", allow_blank=True)
    business_hours = serializers.DictField(required=False, allow_null=True)
    data_source = serializers.ChoiceField(
        choices=[s.value for s in DataSource],
        default=DataSource.MANUAL_ENTRY,
    )


class UpdateVendorSerializer(serializers.Serializer):
    """Serializer for updating a Vendor. Delegates to vendors/services.py."""

    business_name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    longitude = serializers.FloatField(required=False)
    latitude = serializers.FloatField(required=False)
    address_text = serializers.CharField(max_length=500, required=False, allow_blank=True)
    city_id = serializers.UUIDField(required=False)
    area_id = serializers.UUIDField(required=False)
    landmark_id = serializers.UUIDField(required=False, allow_null=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    business_hours = serializers.DictField(required=False)

    def validate(self, attrs: dict) -> dict:
        """Validate that longitude and latitude are provided together.

        Args:
            attrs: Validated field data.

        Returns:
            Validated attrs dict.

        Raises:
            ValidationError: If only one of longitude/latitude is provided.
        """
        has_lon = "longitude" in attrs
        has_lat = "latitude" in attrs
        if has_lon != has_lat:
            raise serializers.ValidationError(
                "longitude and latitude must be provided together."
            )
        if has_lon and has_lat:
            attrs["gps_lon"] = attrs.pop("longitude")
            attrs["gps_lat"] = attrs.pop("latitude")
        return attrs


class QCStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating a Vendor's QC status."""

    qc_status = serializers.ChoiceField(choices=[s.value for s in QCStatus])
    qc_notes = serializers.CharField(required=False, default="", allow_blank=True)


class VendorListSerializer(serializers.ModelSerializer):
    """Lightweight Vendor serializer for list views — no phone decryption."""

    gps_point = serializers.SerializerMethodField(read_only=True)
    city_name = serializers.CharField(source="city.name", read_only=True)
    area_name = serializers.CharField(source="area.name", read_only=True)

    class Meta:
        model = Vendor
        fields = [
            "id", "business_name", "slug",
            "gps_point", "city_name", "area_name",
            "qc_status", "data_source",
            "created_at",
        ]
        read_only_fields = fields

    def get_gps_point(self, obj: Vendor) -> dict | None:
        """Return GPS point as {longitude, latitude} dict.

        Args:
            obj: Vendor instance.

        Returns:
            Dict with longitude and latitude, or None.
        """
        if obj.gps_point:
            return {"longitude": obj.gps_point.x, "latitude": obj.gps_point.y}
        return None
