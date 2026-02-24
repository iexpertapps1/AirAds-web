"""
AirAd — governance initial migration
Creates FraudScore, Blacklist, VendorSuspension, VendorToSAcceptance, ConsentRecord.
"""

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("vendors", "0003_vendor_claimed_status_storefront_photo_key"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ----------------------------------------------------------------
        # FraudScore
        # ----------------------------------------------------------------
        migrations.CreateModel(
            name="FraudScore",
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
                ("actor_email", models.EmailField(blank=True, db_index=True)),
                (
                    "score",
                    models.PositiveIntegerField(
                        db_index=True,
                        default=0,
                        help_text="Accumulated fraud score. Thresholds: 3+ manual review, 6+ auto-suspend.",
                    ),
                ),
                (
                    "is_auto_suspended",
                    models.BooleanField(db_index=True, default=False),
                ),
                ("signals", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "vendor",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="fraud_score",
                        to="vendors.vendor",
                    ),
                ),
            ],
            options={
                "verbose_name": "Fraud Score",
                "verbose_name_plural": "Fraud Scores",
                "ordering": ["-score", "-updated_at"],
            },
        ),
        migrations.AddIndex(
            model_name="fraudscore",
            index=models.Index(
                fields=["score", "is_auto_suspended"], name="fraud_score_idx"
            ),
        ),
        # ----------------------------------------------------------------
        # Blacklist
        # ----------------------------------------------------------------
        migrations.CreateModel(
            name="Blacklist",
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
                    "blacklist_type",
                    models.CharField(
                        choices=[
                            ("PHONE_NUMBER", "Phone Number"),
                            ("DEVICE_ID", "Device ID"),
                            ("GPS_COORDINATE", "GPS Coordinate"),
                        ],
                        db_index=True,
                        max_length=20,
                    ),
                ),
                ("value", models.CharField(db_index=True, max_length=500)),
                ("reason", models.TextField()),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "added_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="blacklist_entries_added",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Blacklist Entry",
                "verbose_name_plural": "Blacklist Entries",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AlterUniqueTogether(
            name="blacklist",
            unique_together={("blacklist_type", "value")},
        ),
        migrations.AddIndex(
            model_name="blacklist",
            index=models.Index(
                fields=["blacklist_type", "is_active"], name="blacklist_type_active_idx"
            ),
        ),
        # ----------------------------------------------------------------
        # VendorSuspension
        # ----------------------------------------------------------------
        migrations.CreateModel(
            name="VendorSuspension",
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
                    "action",
                    models.CharField(
                        choices=[
                            ("WARNING", "Warning"),
                            ("CONTENT_REMOVAL", "Content Removal"),
                            ("TEMPORARY_SUSPENSION", "Temporary Suspension (7 days)"),
                            ("PERMANENT_BAN", "Permanent Ban"),
                        ],
                        db_index=True,
                        max_length=25,
                    ),
                ),
                ("reason", models.TextField()),
                ("policy_reference", models.CharField(blank=True, max_length=200)),
                (
                    "suspension_ends_at",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                (
                    "appeal_status",
                    models.CharField(
                        choices=[
                            ("NONE", "No Appeal Filed"),
                            ("PENDING", "Appeal Pending"),
                            ("APPROVED", "Appeal Approved — Restored"),
                            ("REJECTED", "Appeal Rejected"),
                        ],
                        db_index=True,
                        default="NONE",
                        max_length=10,
                    ),
                ),
                ("appeal_notes", models.TextField(blank=True)),
                ("appeal_reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="suspensions",
                        to="vendors.vendor",
                    ),
                ),
                (
                    "issued_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="suspensions_issued",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "appeal_reviewed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="appeals_reviewed",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Vendor Suspension",
                "verbose_name_plural": "Vendor Suspensions",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="vendorsuspension",
            index=models.Index(
                fields=["vendor", "is_active"], name="suspension_vendor_active_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="vendorsuspension",
            index=models.Index(
                fields=["action", "is_active"], name="suspension_action_active_idx"
            ),
        ),
        # ----------------------------------------------------------------
        # VendorToSAcceptance
        # ----------------------------------------------------------------
        migrations.CreateModel(
            name="VendorToSAcceptance",
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
                ("tos_version", models.CharField(default="1.0", max_length=20)),
                ("accepted_by_email", models.EmailField()),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("accepted_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tos_acceptances",
                        to="vendors.vendor",
                    ),
                ),
            ],
            options={
                "verbose_name": "Vendor ToS Acceptance",
                "verbose_name_plural": "Vendor ToS Acceptances",
                "ordering": ["-accepted_at"],
            },
        ),
        migrations.AddIndex(
            model_name="vendortosacceptance",
            index=models.Index(
                fields=["vendor", "tos_version"], name="tos_vendor_version_idx"
            ),
        ),
        # ----------------------------------------------------------------
        # ConsentRecord
        # ----------------------------------------------------------------
        migrations.CreateModel(
            name="ConsentRecord",
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
                    "category",
                    models.CharField(
                        choices=[
                            ("GPS_TRACKING", "GPS Tracking (required for AR)"),
                            ("BEHAVIORAL_ANALYTICS", "Behavioral Analytics (optional)"),
                            (
                                "MARKETING_NOTIFICATIONS",
                                "Marketing Notifications (optional)",
                            ),
                        ],
                        db_index=True,
                        max_length=30,
                    ),
                ),
                ("granted", models.BooleanField()),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="consent_records",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Consent Record",
                "verbose_name_plural": "Consent Records",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="consentrecord",
            index=models.Index(
                fields=["user", "category", "created_at"], name="consent_user_cat_idx"
            ),
        ),
    ]
