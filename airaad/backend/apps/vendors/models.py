"""
AirAd Backend — Vendor Model (R2, R6)

phone_number_encrypted: BinaryField — AES-256-GCM encrypted at rest (R2).
is_deleted: Soft delete only — delete() overridden, never super().delete() (R6).
Default manager filters is_deleted=False automatically.
gps_point: PointField — GiST index via migrations.RunSQL (NOT models.Index).
business_hours: JSONField — validated via BusinessHoursSchema in vendors/services.py.
qc_reviewed_by: FK to AdminUser — NOT a raw UUID field.
"""

import uuid

from django.contrib.gis.db import models as gis_models
from django.db import models


class QCStatus(models.TextChoices):
    """Quality control review status for a vendor record."""

    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    NEEDS_REVIEW = "NEEDS_REVIEW", "Needs Review"


class DataSource(models.TextChoices):
    """Origin of the vendor record."""

    CSV_IMPORT = "CSV_IMPORT", "CSV Import"
    GOOGLE_PLACES = "GOOGLE_PLACES", "Google Places"
    MANUAL_ENTRY = "MANUAL_ENTRY", "Manual Entry"
    FIELD_AGENT = "FIELD_AGENT", "Field Agent"


class ActiveVendorManager(models.Manager):
    """Default manager — automatically filters out soft-deleted vendors.

    Any queryset from Vendor.objects will exclude is_deleted=True records.
    Use Vendor.all_objects for unfiltered access (admin/QA use only).
    """

    def get_queryset(self) -> models.QuerySet:
        """Return only non-deleted vendors.

        Returns:
            QuerySet filtered to is_deleted=False.
        """
        return super().get_queryset().filter(is_deleted=False)


class Vendor(models.Model):
    """A vendor (business) in the AirAd platform.

    Core data collection model for Phase A. Extended with owner, subscription,
    and media fields in Phase B via a new migration.

    Phone numbers are stored AES-256-GCM encrypted in phone_number_encrypted
    (BinaryField). Plaintext is never stored. Encrypt/decrypt happens in
    vendors/services.py — never in serializers or views.

    Soft delete: delete() sets is_deleted=True and calls save(). Records are
    never hard-deleted. Default manager (objects) filters is_deleted=False.
    Use all_objects for unfiltered access.

    gps_point uses a PostGIS PointField. GiST index is added via
    migrations.RunSQL — not models.Index.

    business_hours is a JSONField validated against BusinessHoursSchema
    on every write in vendors/services.py.

    Attributes:
        id: UUID primary key.
        business_name: Trading name of the business.
        slug: URL-safe identifier — unique.
        description: Optional long-form description.
        gps_point: PostGIS PointField (SRID=4326). GiST index via RunSQL.
        address_text: Human-readable address string.
        city: FK to geo.City.
        area: FK to geo.Area.
        landmark: FK to geo.Landmark (nullable).
        phone_number_encrypted: AES-256-GCM encrypted phone (BinaryField, R2).
        business_hours: JSONField validated by BusinessHoursSchema.
        qc_status: QCStatus TextChoices.
        qc_reviewed_by: FK to AdminUser (nullable) — NOT a raw UUID.
        qc_reviewed_at: Datetime of last QC review.
        qc_notes: Reviewer notes.
        data_source: DataSource TextChoices.
        tags: M2M to tags.Tag.
        is_deleted: Soft delete flag (R6). Default manager filters this out.
        created_at: Auto-set on creation.
        updated_at: Auto-updated on every save.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=280, unique=True, db_index=True)
    description = models.TextField(blank=True)

    # GPS — PostGIS PointField. GiST index via migrations.RunSQL (NOT models.Index).
    gps_point = gis_models.PointField(
        srid=4326,
        help_text="GPS location. GiST index added via RunSQL migration.",
    )
    address_text = models.CharField(max_length=500, blank=True)

    # Geo hierarchy
    city = models.ForeignKey(
        "geo.City",
        on_delete=models.PROTECT,
        related_name="vendors",
    )
    area = models.ForeignKey(
        "geo.Area",
        on_delete=models.PROTECT,
        related_name="vendors",
    )
    landmark = models.ForeignKey(
        "geo.Landmark",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="vendors",
    )

    # Phone — AES-256-GCM encrypted BinaryField (R2). NEVER plaintext.
    phone_number_encrypted = models.BinaryField(
        blank=True,
        help_text="AES-256-GCM encrypted phone number. Encrypt/decrypt in services.py only.",
    )

    # Business hours — validated via BusinessHoursSchema on every write in services.py
    business_hours = models.JSONField(
        default=dict,  # callable — NEVER default={}
        blank=True,
        help_text="7-day hours dict. Validated by BusinessHoursSchema in services.py.",
    )

    # QC workflow
    qc_status = models.CharField(
        max_length=20,
        choices=QCStatus.choices,
        default=QCStatus.PENDING,
        db_index=True,
    )
    qc_reviewed_by = models.ForeignKey(
        "accounts.AdminUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="qc_reviewed_vendors",
        help_text="FK to AdminUser — NOT a raw UUID field.",
    )
    qc_reviewed_at = models.DateTimeField(null=True, blank=True)
    qc_notes = models.TextField(blank=True)

    # Data provenance
    data_source = models.CharField(
        max_length=20,
        choices=DataSource.choices,
        default=DataSource.MANUAL_ENTRY,
        db_index=True,
    )

    # Tags M2M
    tags = models.ManyToManyField(
        "tags.Tag",
        blank=True,
        related_name="vendors",
    )

    # Soft delete (R6) — default manager filters this out automatically
    is_deleted = models.BooleanField(default=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Default manager — filters is_deleted=False automatically (R6)
    objects = ActiveVendorManager()

    # Unfiltered manager — for admin/QA/migration use only
    all_objects = models.Manager()

    class Meta:
        verbose_name = "Vendor"
        verbose_name_plural = "Vendors"
        ordering = ["-created_at"]
        indexes = [
            # Composite indexes per plan spec
            models.Index(fields=["qc_status", "is_deleted"], name="vendor_qc_deleted_idx"),
            models.Index(fields=["area", "is_deleted"], name="vendor_area_deleted_idx"),
            models.Index(fields=["data_source"], name="vendor_data_source_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.business_name} ({self.qc_status})"

    def delete(self, using: str | None = None, keep_parents: bool = False) -> tuple:
        """Soft delete — sets is_deleted=True and saves. Never hard-deletes (R6).

        Args:
            using: Database alias (ignored — soft delete only).
            keep_parents: Ignored — soft delete only.

        Returns:
            Tuple of (1, {"vendors.Vendor": 1}) to mimic Django's delete() return.
        """
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at"])
        return 1, {f"{self._meta.app_label}.{self._meta.object_name}": 1}
