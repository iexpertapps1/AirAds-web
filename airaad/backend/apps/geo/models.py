"""
AirAd Backend — Geo Models

Country → City → Area → Landmark hierarchy.
ALL PointField columns use GiST spatial indexes via migrations.RunSQL — NOT models.Index.
JSONField defaults use callable `list` — never `[]` (mutable default rule).
slug fields are immutable after creation — enforced in geo/services.py.
"""

import uuid

from django.contrib.gis.db import models as gis_models
from django.db import models


class Country(models.Model):
    """A country in the AirAd geo hierarchy.

    Attributes:
        id: UUID primary key.
        name: Full country name.
        code: ISO 3166-1 alpha-2 country code (e.g. "PK", "IN").
        is_active: Whether this country is active in the platform.
        created_at: Auto-set on creation.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=2, unique=True, db_index=True, help_text="ISO 3166-1 alpha-2")
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class City(models.Model):
    """A city within a country.

    centroid is a PostGIS PointField — GiST index added via migrations.RunSQL.
    bounding_box is a PolygonField for city boundary queries.
    aliases is a JSONField for alternate names — default=list (callable).
    slug is immutable after creation — enforced in geo/services.py.

    Attributes:
        id: UUID primary key.
        country: FK to Country.
        name: City name.
        slug: URL-safe identifier — immutable after creation.
        aliases: List of alternate names (JSONField, default=list).
        centroid: GPS centre point (PostGIS PointField, SRID=4326).
        bounding_box: City boundary polygon (PostGIS PolygonField, nullable).
        is_active: Whether this city is live on the platform.
        display_order: Integer for ordering in UI dropdowns.
        created_at: Auto-set on creation.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="cities")
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, db_index=True)
    aliases = models.JSONField(
        default=list,  # callable — NEVER default=[]
        blank=True,
        help_text="Alternate names for search matching.",
    )
    centroid = gis_models.PointField(
        srid=4326,
        help_text="GPS centre point. GiST index added via RunSQL migration.",
    )
    bounding_box = gis_models.PolygonField(
        srid=4326,
        null=True,
        blank=True,
        help_text="City boundary polygon for containment queries.",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
        ordering = ["display_order", "name"]
        indexes = [
            models.Index(fields=["country", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.name}, {self.country.code}"


class Area(models.Model):
    """A sub-area within a city (neighbourhood, district, zone).

    Supports self-referential parent_area for nested hierarchies.
    centroid is nullable — not all areas have a precise GPS centre.
    GiST index added via migrations.RunSQL when centroid is not null.

    Attributes:
        id: UUID primary key.
        city: FK to City.
        parent_area: Self-referential FK for nested areas (nullable).
        name: Area name.
        slug: URL-safe identifier — immutable after creation.
        aliases: List of alternate names (JSONField, default=list).
        centroid: GPS centre point (nullable PostGIS PointField, SRID=4326).
        is_active: Whether this area is active.
        created_at: Auto-set on creation.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="areas")
    parent_area = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="child_areas",
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True, db_index=True)
    aliases = models.JSONField(
        default=list,  # callable — NEVER default=[]
        blank=True,
        help_text="Alternate names for search matching.",
    )
    centroid = gis_models.PointField(
        srid=4326,
        null=True,
        blank=True,
        help_text="GPS centre point. GiST index added via RunSQL migration.",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Area"
        verbose_name_plural = "Areas"
        ordering = ["city", "name"]
        indexes = [
            models.Index(fields=["city", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.city.name})"


class Landmark(models.Model):
    """A named landmark within an area (market, mall, hospital, etc.).

    location is a PostGIS PointField — GiST index added via migrations.RunSQL.
    Used as a fine-grained location reference for vendors.

    Attributes:
        id: UUID primary key.
        area: FK to Area.
        name: Landmark name.
        slug: URL-safe identifier — immutable after creation.
        aliases: List of alternate names (JSONField, default=list, ≥3 in seed data).
        location: GPS point (PostGIS PointField, SRID=4326).
        is_active: Whether this landmark is active.
        created_at: Auto-set on creation.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="landmarks")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, db_index=True)
    aliases = models.JSONField(
        default=list,  # callable — NEVER default=[]
        blank=True,
        help_text="Alternate names. Seed data provides ≥3 aliases per landmark.",
    )
    location = gis_models.PointField(
        srid=4326,
        help_text="GPS point. GiST index added via RunSQL migration.",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Landmark"
        verbose_name_plural = "Landmarks"
        ordering = ["area", "name"]
        indexes = [
            models.Index(fields=["area", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.area.name})"
