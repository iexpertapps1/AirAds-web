"""
AirAd — analytics initial migration

Creates AnalyticsEvent model (spec §7.1).
Phase A: model scaffolded — writes deferred to Phase B.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("geo", "0002_area_boundary_polygon_landmark_ar_anchor_points"),
        ("vendors", "0003_vendor_claimed_status_storefront_photo_key"),
    ]

    operations = [
        migrations.CreateModel(
            name="AnalyticsEvent",
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
                    "event_type",
                    models.CharField(
                        choices=[
                            ("AR_VIEW_OPENED", "AR View Opened"),
                            ("VENDOR_MARKER_TAPPED", "Vendor Marker Tapped"),
                            ("VOICE_QUERY_MADE", "Voice Query Made"),
                            ("NAVIGATION_STARTED", "Navigation Started"),
                            ("REEL_VIEWED", "Reel Viewed"),
                            ("PROMOTION_CLICKED", "Promotion Clicked"),
                            ("VENDOR_VIEW", "Vendor View"),
                        ],
                        db_index=True,
                        max_length=30,
                    ),
                ),
                (
                    "vendor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="analytics_events",
                        to="vendors.vendor",
                    ),
                ),
                (
                    "actor_id",
                    models.UUIDField(
                        blank=True,
                        db_index=True,
                        help_text="UUID of the acting user. Null for anonymous events (spec §7.2).",
                        null=True,
                    ),
                ),
                (
                    "gps_lat",
                    models.FloatField(
                        blank=True,
                        help_text="Anonymised latitude. Not linked to actor_id (spec §7.2).",
                        null=True,
                    ),
                ),
                (
                    "gps_lon",
                    models.FloatField(
                        blank=True,
                        help_text="Anonymised longitude. Not linked to actor_id (spec §7.2).",
                        null=True,
                    ),
                ),
                (
                    "area",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="analytics_events",
                        to="geo.area",
                    ),
                ),
                (
                    "metadata",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Event-specific context: distance, tags, query_text, watch_duration, etc.",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                "verbose_name": "Analytics Event",
                "verbose_name_plural": "Analytics Events",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="analyticsevent",
            index=models.Index(
                fields=["event_type", "created_at"], name="analytics_type_created_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="analyticsevent",
            index=models.Index(
                fields=["vendor", "event_type"], name="analytics_vendor_type_idx"
            ),
        ),
    ]
