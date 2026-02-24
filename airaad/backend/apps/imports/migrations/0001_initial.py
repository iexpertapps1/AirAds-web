"""
AirAd — imports initial migration
Creates ImportBatch with S3 key, status, error_log (default=list, capped in services).
"""

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ImportBatch",
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
                    "file_key",
                    models.CharField(
                        help_text="S3 object key ONLY — never a public URL.",
                        max_length=500,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("QUEUED", "Queued"),
                            ("PROCESSING", "Processing"),
                            ("DONE", "Done"),
                            ("FAILED", "Failed"),
                        ],
                        db_index=True,
                        default="QUEUED",
                        max_length=20,
                    ),
                ),
                ("total_rows", models.PositiveIntegerField(default=0)),
                ("processed_rows", models.PositiveIntegerField(default=0)),
                ("error_count", models.PositiveIntegerField(default=0)),
                (
                    "error_log",
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text="Per-row error list. Capped at 1000 entries by append_error_log() in services.py.",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="import_batches",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Import Batch",
                "verbose_name_plural": "Import Batches",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="importbatch",
            index=models.Index(
                fields=["status", "created_by"],
                name="import_status_creator_idx",
            ),
        ),
    ]
