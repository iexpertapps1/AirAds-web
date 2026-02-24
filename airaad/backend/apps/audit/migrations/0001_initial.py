"""
AirAd — audit initial migration
Creates AuditLog with UUID PK, composite indexes, immutable semantics.
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
            name="AuditLog",
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
                ("action", models.CharField(db_index=True, max_length=100)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="audit_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "actor_label",
                    models.CharField(
                        blank=True,
                        help_text="Email snapshot of the actor at the time of the event.",
                        max_length=255,
                    ),
                ),
                ("target_type", models.CharField(blank=True, max_length=100)),
                ("target_id", models.UUIDField(blank=True, null=True)),
                ("before_state", models.JSONField(blank=True, default=dict)),
                ("after_state", models.JSONField(blank=True, default=dict)),
                (
                    "request_id",
                    models.CharField(blank=True, db_index=True, max_length=36),
                ),
                (
                    "ip_address",
                    models.GenericIPAddressField(blank=True, null=True),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, db_index=True),
                ),
            ],
            options={
                "verbose_name": "Audit Log",
                "verbose_name_plural": "Audit Logs",
                "ordering": ["-created_at"],
                "default_permissions": ("add", "view"),
            },
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(
                fields=["target_type", "target_id"],
                name="audit_target_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(
                fields=["actor", "created_at"],
                name="audit_actor_created_idx",
            ),
        ),
    ]
