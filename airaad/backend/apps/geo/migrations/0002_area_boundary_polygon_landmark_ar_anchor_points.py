"""
AirAd — geo migration 0002

Adds:
  - Area.boundary_polygon  (PolygonField, nullable) — spec §2.2 "boundary_polygon: GeoJSON for Areas"
  - Landmark.ar_anchor_points (JSONField, default=list) — spec §2.2 "ar_anchor_points for Landmarks"

GiST index for boundary_polygon added via RunSQL (same pattern as 0001_initial).
"""

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("geo", "0001_initial"),
    ]

    operations = [
        # -----------------------------------------------------------------------
        # Area.boundary_polygon — nullable PolygonField (spec §2.2)
        # -----------------------------------------------------------------------
        migrations.AddField(
            model_name="area",
            name="boundary_polygon",
            field=django.contrib.gis.db.models.fields.PolygonField(
                blank=True,
                help_text="Area boundary polygon for containment queries (spec §2.2).",
                null=True,
                srid=4326,
            ),
        ),
        # -----------------------------------------------------------------------
        # Landmark.ar_anchor_points — JSONField array of {lon, lat} dicts (spec §2.2, §5.2)
        # -----------------------------------------------------------------------
        migrations.AddField(
            model_name="landmark",
            name="ar_anchor_points",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Array of AR anchor coordinates [{lon, lat}] for AR clustering (spec §2.2, §5.2).",
            ),
        ),
        # -----------------------------------------------------------------------
        # GiST spatial index for boundary_polygon via RunSQL
        # -----------------------------------------------------------------------
        migrations.RunSQL(
            sql="CREATE INDEX IF NOT EXISTS geo_area_boundary_polygon_gist ON geo_area USING GiST (boundary_polygon);",
            reverse_sql="DROP INDEX IF EXISTS geo_area_boundary_polygon_gist;",
        ),
    ]
