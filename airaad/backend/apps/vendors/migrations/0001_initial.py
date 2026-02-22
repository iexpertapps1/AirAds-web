"""
AirAd — vendors initial migration
Creates Vendor with BinaryField phone, soft delete, composite indexes.
gps_point GiST index added via RunSQL — NOT models.Index.
"""

import uuid

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        ("geo", "0001_initial"),
        ("tags", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Vendor",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("business_name", models.CharField(db_index=True, max_length=255)),
                ("slug", models.SlugField(db_index=True, max_length=280, unique=True)),
                ("description", models.TextField(blank=True)),
                (
                    "gps_point",
                    django.contrib.gis.db.models.fields.PointField(
                        help_text="GPS location. GiST index added via RunSQL migration.",
                        srid=4326,
                    ),
                ),
                ("address_text", models.CharField(blank=True, max_length=500)),
                (
                    "city",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="vendors",
                        to="geo.city",
                    ),
                ),
                (
                    "area",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="vendors",
                        to="geo.area",
                    ),
                ),
                (
                    "landmark",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="vendors",
                        to="geo.landmark",
                    ),
                ),
                (
                    "phone_number_encrypted",
                    models.BinaryField(
                        blank=True,
                        help_text="AES-256-GCM encrypted phone number. Encrypt/decrypt in services.py only.",
                    ),
                ),
                (
                    "business_hours",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="7-day hours dict. Validated by BusinessHoursSchema in services.py.",
                    ),
                ),
                (
                    "qc_status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("APPROVED", "Approved"),
                            ("REJECTED", "Rejected"),
                            ("NEEDS_REVIEW", "Needs Review"),
                        ],
                        db_index=True,
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                (
                    "qc_reviewed_by",
                    models.ForeignKey(
                        blank=True,
                        help_text="FK to AdminUser — NOT a raw UUID field.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="qc_reviewed_vendors",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("qc_reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("qc_notes", models.TextField(blank=True)),
                (
                    "data_source",
                    models.CharField(
                        choices=[
                            ("CSV_IMPORT", "CSV Import"),
                            ("GOOGLE_PLACES", "Google Places"),
                            ("MANUAL_ENTRY", "Manual Entry"),
                            ("FIELD_AGENT", "Field Agent"),
                        ],
                        db_index=True,
                        default="MANUAL_ENTRY",
                        max_length=20,
                    ),
                ),
                (
                    "tags",
                    models.ManyToManyField(
                        blank=True,
                        related_name="vendors",
                        to="tags.tag",
                    ),
                ),
                ("is_deleted", models.BooleanField(db_index=True, default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Vendor",
                "verbose_name_plural": "Vendors",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="vendor",
            index=models.Index(fields=["qc_status", "is_deleted"], name="vendor_qc_deleted_idx"),
        ),
        migrations.AddIndex(
            model_name="vendor",
            index=models.Index(fields=["area", "is_deleted"], name="vendor_area_deleted_idx"),
        ),
        migrations.AddIndex(
            model_name="vendor",
            index=models.Index(fields=["data_source"], name="vendor_data_source_idx"),
        ),

        # GiST spatial index on gps_point via RunSQL — NOT models.Index (R1)
        migrations.RunSQL(
            sql="CREATE INDEX IF NOT EXISTS vendor_gps_point_gist ON vendors_vendor USING GiST (gps_point);",
            reverse_sql="DROP INDEX IF EXISTS vendor_gps_point_gist;",
        ),
    ]
