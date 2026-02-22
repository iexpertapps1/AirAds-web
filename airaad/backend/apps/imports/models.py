"""
AirAd Backend — ImportBatch Model

file_key stores the S3 object key ONLY — never a public URL.
error_log is a JSONField with default=list (callable). The 1000-entry cap
is enforced in imports/services.py via append_error_log() — not at model level.
CSV content is NEVER passed over the Celery broker — only batch_id (R8).
"""

import uuid

from django.db import models


class ImportStatus(models.TextChoices):
    """Processing status for a CSV import batch."""

    QUEUED = "QUEUED", "Queued"
    PROCESSING = "PROCESSING", "Processing"
    DONE = "DONE", "Done"
    FAILED = "FAILED", "Failed"


class ImportBatch(models.Model):
    """A single CSV import job uploaded by an admin user.

    The CSV file is stored in S3. file_key holds the S3 object key — never
    a public URL. The Celery task reads the file from S3 using the key.

    error_log accumulates per-row validation errors. The 1000-entry cap is
    enforced in imports/services.py — not here. Exceeding the cap is silently
    truncated by append_error_log().

    Attributes:
        id: UUID primary key.
        file_key: S3 object key string (e.g. "imports/2024/01/abc123").
            NEVER a public URL.
        status: ImportStatus TextChoices.
        total_rows: Total number of data rows in the CSV.
        processed_rows: Number of rows processed so far.
        error_count: Number of rows that produced errors.
        error_log: List of error dicts (JSONField, default=list, capped at 1000).
        created_by: FK to AdminUser who uploaded the file.
        created_at: Auto-set on creation.
        updated_at: Auto-updated on every save.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_key = models.CharField(
        max_length=500,
        help_text="S3 object key ONLY — never a public URL.",
    )
    status = models.CharField(
        max_length=20,
        choices=ImportStatus.choices,
        default=ImportStatus.QUEUED,
        db_index=True,
    )
    total_rows = models.PositiveIntegerField(default=0)
    processed_rows = models.PositiveIntegerField(default=0)
    error_count = models.PositiveIntegerField(default=0)
    error_log = models.JSONField(
        default=list,  # callable — NEVER default=[]
        blank=True,
        help_text="Per-row error list. Capped at 1000 entries by append_error_log() in services.py.",
    )
    created_by = models.ForeignKey(
        "accounts.AdminUser",
        on_delete=models.PROTECT,
        related_name="import_batches",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Import Batch"
        verbose_name_plural = "Import Batches"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_by"], name="import_status_creator_idx"),
        ]

    def __str__(self) -> str:
        return f"ImportBatch {self.id} [{self.status}] by {self.created_by_id}"
