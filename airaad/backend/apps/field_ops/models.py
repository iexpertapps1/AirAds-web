"""
AirAd Backend — FieldVisit and FieldPhoto Models

FieldVisit records a field agent's on-site visit to a vendor location.
FieldPhoto stores the S3 key of a photo taken during a visit — never a public URL.
Presigned URLs are generated on read via core.storage.generate_presigned_url().
gps_confirmed_point uses PostGIS PointField — GiST index via migrations.RunSQL.
"""

import uuid

from django.contrib.gis.db import models as gis_models
from django.db import models


class FieldVisit(models.Model):
    """A field agent's on-site visit to verify a vendor's location and details.

    gps_confirmed_point is the GPS coordinate confirmed by the agent on-site.
    It is nullable — the agent may not always capture a GPS point.
    GiST index is added via migrations.RunSQL.

    Attributes:
        id: UUID primary key.
        vendor: FK to Vendor being visited.
        agent: FK to AdminUser (FIELD_AGENT role) conducting the visit.
        visited_at: Datetime of the visit.
        visit_notes: Free-text notes from the agent.
        gps_confirmed_point: GPS point confirmed on-site (nullable PointField).
        created_at: Auto-set on creation.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.PROTECT,
        related_name="field_visits",
    )
    agent = models.ForeignKey(
        "accounts.AdminUser",
        on_delete=models.PROTECT,
        related_name="field_visits",
    )
    visited_at = models.DateTimeField()
    visit_notes = models.TextField(blank=True)
    gps_confirmed_point = gis_models.PointField(
        srid=4326,
        null=True,
        blank=True,
        help_text="GPS point confirmed on-site. GiST index added via RunSQL migration.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Field Visit"
        verbose_name_plural = "Field Visits"
        ordering = ["-visited_at"]
        indexes = [
            models.Index(fields=["vendor", "visited_at"], name="fieldvisit_vendor_date_idx"),
            models.Index(fields=["agent", "visited_at"], name="fieldvisit_agent_date_idx"),
        ]

    def __str__(self) -> str:
        return f"FieldVisit {self.id} — {self.vendor_id} by {self.agent_id}"


class FieldPhoto(models.Model):
    """A photo taken during a field visit, stored in S3.

    s3_key stores the S3 object key ONLY — never a public URL.
    Presigned URLs are generated on read via core.storage.generate_presigned_url().

    Attributes:
        id: UUID primary key.
        field_visit: FK to FieldVisit this photo belongs to.
        s3_key: S3 object key string. NEVER a public URL.
        caption: Optional caption for the photo.
        is_active: Soft-disable flag (does not delete from S3).
        uploaded_at: Auto-set on creation.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    field_visit = models.ForeignKey(
        FieldVisit,
        on_delete=models.PROTECT,
        related_name="photos",
    )
    s3_key = models.CharField(
        max_length=500,
        help_text="S3 object key ONLY — never a public URL. Generate presigned URL on read.",
    )
    caption = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Field Photo"
        verbose_name_plural = "Field Photos"
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["field_visit", "is_active"], name="fieldphoto_visit_active_idx"),
        ]

    def __str__(self) -> str:
        return f"FieldPhoto {self.id} — visit {self.field_visit_id}"
