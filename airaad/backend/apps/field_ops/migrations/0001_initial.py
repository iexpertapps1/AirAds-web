"""
AirAd — field_ops initial migration
Creates FieldVisit and FieldPhoto.
gps_confirmed_point GiST index added via RunSQL — NOT models.Index.
FieldPhoto.s3_key stores S3 key only — never a public URL.
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
        ("vendors", "0001_initial"),
    ]

    operations = [
        # -----------------------------------------------------------------------
        # FieldVisit
        # -----------------------------------------------------------------------
        migrations.CreateModel(
            name="FieldVisit",
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
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="field_visits",
                        to="vendors.vendor",
                    ),
                ),
                (
                    "agent",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="field_visits",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("visited_at", models.DateTimeField()),
                ("visit_notes", models.TextField(blank=True)),
                (
                    "gps_confirmed_point",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True,
                        help_text="GPS point confirmed on-site. GiST index added via RunSQL migration.",
                        null=True,
                        srid=4326,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Field Visit",
                "verbose_name_plural": "Field Visits",
                "ordering": ["-visited_at"],
            },
        ),
        migrations.AddIndex(
            model_name="fieldvisit",
            index=models.Index(
                fields=["vendor", "visited_at"], name="fieldvisit_vendor_date_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="fieldvisit",
            index=models.Index(
                fields=["agent", "visited_at"], name="fieldvisit_agent_date_idx"
            ),
        ),
        # -----------------------------------------------------------------------
        # FieldPhoto
        # -----------------------------------------------------------------------
        migrations.CreateModel(
            name="FieldPhoto",
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
                    "field_visit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="photos",
                        to="field_ops.fieldvisit",
                    ),
                ),
                (
                    "s3_key",
                    models.CharField(
                        help_text="S3 object key ONLY — never a public URL. Generate presigned URL on read.",
                        max_length=500,
                    ),
                ),
                ("caption", models.CharField(blank=True, max_length=500)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Field Photo",
                "verbose_name_plural": "Field Photos",
                "ordering": ["-uploaded_at"],
            },
        ),
        migrations.AddIndex(
            model_name="fieldphoto",
            index=models.Index(
                fields=["field_visit", "is_active"],
                name="fieldphoto_visit_active_idx",
            ),
        ),
        # -----------------------------------------------------------------------
        # GiST spatial index on gps_confirmed_point via RunSQL — NOT models.Index
        # -----------------------------------------------------------------------
        migrations.RunSQL(
            sql="CREATE INDEX IF NOT EXISTS fieldvisit_gps_gist ON field_ops_fieldvisit USING GiST (gps_confirmed_point);",
            reverse_sql="DROP INDEX IF EXISTS fieldvisit_gps_gist;",
        ),
    ]
