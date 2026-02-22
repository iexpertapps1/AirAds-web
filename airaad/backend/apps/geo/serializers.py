"""
AirAd Backend — Geo Serializers

No business logic — validation only. Delegates to geo/services.py.
GPS: Point(longitude, latitude) — lon/lat order enforced here.
read_only_fields explicitly declared on all serializers.
"""

import logging

from rest_framework import serializers

from .models import Area, City, Country, Landmark

logger = logging.getLogger(__name__)


class CountrySerializer(serializers.ModelSerializer):
    """Serializer for Country model."""

    class Meta:
        model = Country
        fields = ["id", "name", "code", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class CitySerializer(serializers.ModelSerializer):
    """Serializer for City model.

    Accepts latitude/longitude floats for write; returns centroid as lon/lat dict on read.
    """

    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    centroid = serializers.SerializerMethodField(read_only=True)
    country_name = serializers.CharField(source="country.name", read_only=True)

    class Meta:
        model = City
        fields = [
            "id", "country", "country_name", "name", "slug",
            "aliases", "centroid", "latitude", "longitude",
            "is_active", "display_order", "created_at",
        ]
        read_only_fields = ["id", "slug", "centroid", "country_name", "created_at"]

    def get_centroid(self, obj: City) -> dict | None:
        """Return centroid as {longitude, latitude} dict.

        Args:
            obj: City instance.

        Returns:
            Dict with longitude and latitude, or None.
        """
        if obj.centroid:
            return {"longitude": obj.centroid.x, "latitude": obj.centroid.y}
        return None


class AreaSerializer(serializers.ModelSerializer):
    """Serializer for Area model."""

    latitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    longitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    centroid = serializers.SerializerMethodField(read_only=True)
    city_name = serializers.CharField(source="city.name", read_only=True)

    class Meta:
        model = Area
        fields = [
            "id", "city", "city_name", "parent_area", "name", "slug",
            "aliases", "centroid", "latitude", "longitude",
            "is_active", "created_at",
        ]
        read_only_fields = ["id", "slug", "centroid", "city_name", "created_at"]

    def get_centroid(self, obj: Area) -> dict | None:
        """Return centroid as {longitude, latitude} dict.

        Args:
            obj: Area instance.

        Returns:
            Dict with longitude and latitude, or None.
        """
        if obj.centroid:
            return {"longitude": obj.centroid.x, "latitude": obj.centroid.y}
        return None


class LandmarkSerializer(serializers.ModelSerializer):
    """Serializer for Landmark model."""

    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    area_name = serializers.CharField(source="area.name", read_only=True)

    class Meta:
        model = Landmark
        fields = [
            "id", "area", "area_name", "name", "slug",
            "aliases", "location", "latitude", "longitude",
            "is_active", "created_at",
        ]
        read_only_fields = ["id", "slug", "location", "area_name", "created_at"]

    def get_location(self, obj: Landmark) -> dict | None:
        """Return location as {longitude, latitude} dict.

        Args:
            obj: Landmark instance.

        Returns:
            Dict with longitude and latitude, or None.
        """
        if obj.location:
            return {"longitude": obj.location.x, "latitude": obj.location.y}
        return None
