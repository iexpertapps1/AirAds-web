"""
AirAd — geo initial migration
Creates Country, City, Area, Landmark.
ALL PointField columns get GiST spatial indexes via migrations.RunSQL — NOT models.Index.
GiST SQL: CREATE INDEX IF NOT EXISTS <name> ON <table> USING GiST (<col>);
"""

import uuid

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        # -----------------------------------------------------------------------
        # Country
        # -----------------------------------------------------------------------
        migrations.CreateModel(
            name="Country",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "code",
                    models.CharField(
                        db_index=True,
                        help_text="ISO 3166-1 alpha-2",
                        max_length=2,
                        unique=True,
                    ),
                ),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Country",
                "verbose_name_plural": "Countries",
                "ordering": ["name"],
            },
        ),
        # -----------------------------------------------------------------------
        # City
        # -----------------------------------------------------------------------
        migrations.CreateModel(
            name="City",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "country",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="cities",
                        to="geo.country",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(db_index=True, max_length=120, unique=True)),
                (
                    "aliases",
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text="Alternate names for search matching.",
                    ),
                ),
                (
                    "centroid",
                    django.contrib.gis.db.models.fields.PointField(
                        help_text="GPS centre point. GiST index added via RunSQL migration.",
                        srid=4326,
                    ),
                ),
                (
                    "bounding_box",
                    django.contrib.gis.db.models.fields.PolygonField(
                        blank=True,
                        help_text="City boundary polygon for containment queries.",
                        null=True,
                        srid=4326,
                    ),
                ),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                (
                    "display_order",
                    models.PositiveIntegerField(db_index=True, default=0),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "City",
                "verbose_name_plural": "Cities",
                "ordering": ["display_order", "name"],
            },
        ),
        migrations.AddIndex(
            model_name="city",
            index=models.Index(
                fields=["country", "is_active"], name="geo_city_country_active_idx"
            ),
        ),
        # -----------------------------------------------------------------------
        # Area
        # -----------------------------------------------------------------------
        migrations.CreateModel(
            name="Area",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "city",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="areas",
                        to="geo.city",
                    ),
                ),
                (
                    "parent_area",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="child_areas",
                        to="geo.area",
                    ),
                ),
                ("name", models.CharField(max_length=150)),
                ("slug", models.SlugField(db_index=True, max_length=160, unique=True)),
                (
                    "aliases",
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text="Alternate names for search matching.",
                    ),
                ),
                (
                    "centroid",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True,
                        help_text="GPS centre point. GiST index added via RunSQL migration.",
                        null=True,
                        srid=4326,
                    ),
                ),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Area",
                "verbose_name_plural": "Areas",
                "ordering": ["city", "name"],
            },
        ),
        migrations.AddIndex(
            model_name="area",
            index=models.Index(
                fields=["city", "is_active"], name="geo_area_city_active_idx"
            ),
        ),
        # -----------------------------------------------------------------------
        # Landmark
        # -----------------------------------------------------------------------
        migrations.CreateModel(
            name="Landmark",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "area",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="landmarks",
                        to="geo.area",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("slug", models.SlugField(db_index=True, max_length=220, unique=True)),
                (
                    "aliases",
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text="Alternate names. Seed data provides ≥3 aliases per landmark.",
                    ),
                ),
                (
                    "location",
                    django.contrib.gis.db.models.fields.PointField(
                        help_text="GPS point. GiST index added via RunSQL migration.",
                        srid=4326,
                    ),
                ),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Landmark",
                "verbose_name_plural": "Landmarks",
                "ordering": ["area", "name"],
            },
        ),
        migrations.AddIndex(
            model_name="landmark",
            index=models.Index(
                fields=["area", "is_active"], name="geo_landmark_area_active_idx"
            ),
        ),
        # -----------------------------------------------------------------------
        # GiST spatial indexes via RunSQL — NOT models.Index (R1 / GeoDjango requirement)
        # CREATE INDEX IF NOT EXISTS ensures idempotency on re-run.
        # -----------------------------------------------------------------------
        migrations.RunSQL(
            sql="CREATE INDEX IF NOT EXISTS geo_city_centroid_gist ON geo_city USING GiST (centroid);",
            reverse_sql="DROP INDEX IF EXISTS geo_city_centroid_gist;",
        ),
        migrations.RunSQL(
            sql="CREATE INDEX IF NOT EXISTS geo_area_centroid_gist ON geo_area USING GiST (centroid);",
            reverse_sql="DROP INDEX IF EXISTS geo_area_centroid_gist;",
        ),
        migrations.RunSQL(
            sql="CREATE INDEX IF NOT EXISTS geo_landmark_location_gist ON geo_landmark USING GiST (location);",
            reverse_sql="DROP INDEX IF EXISTS geo_landmark_location_gist;",
        ),
    ]
