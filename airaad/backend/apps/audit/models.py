"""
AirAd Backend — AuditLog Model (R5)

AuditLog is IMMUTABLE — records are written once and never modified.
The custom manager raises NotImplementedError on update() to enforce this.
log_action() is called explicitly from services.py only — never via signals.
Every POST/PATCH/DELETE in the system must produce an AuditLog entry.
"""

import uuid

from django.db import models


class ImmutableAuditLogManager(models.Manager):
    """Custom manager that prevents any mutation of AuditLog records.

    AuditLog entries are write-once. Calling update() on this manager
    raises NotImplementedError to enforce immutability at the ORM level.
    """

    def update(self, **kwargs: object) -> int:
        """Prevent bulk updates on AuditLog.

        Raises:
            NotImplementedError: Always — AuditLog records are immutable.
        """
        raise NotImplementedError(
            "AuditLog records are immutable and cannot be updated. "
            "Create a new entry instead."
        )

    def get_queryset(self) -> models.QuerySet:
        """Return the default queryset ordered by creation time descending.

        Returns:
            QuerySet ordered by -created_at.
        """
        return super().get_queryset().order_by("-created_at")


class AuditLog(models.Model):
    """Immutable audit trail for all mutations in the AirAd system.

    Every POST, PATCH, and DELETE operation must produce one AuditLog entry.
    Records are written once and never modified or deleted.

    Attributes:
        id: UUID primary key.
        action: Short action identifier (e.g. "VENDOR_CREATED", "AUTH_LOGIN_SUCCESS").
        actor: FK to the AdminUser who performed the action. Nullable — set to
            NULL if the actor is later deleted (SET_NULL). actor_label preserves
            the email snapshot for forensic purposes.
        actor_label: Email snapshot of the actor at the time of the action.
            Preserved even if the actor account is deleted.
        target_type: String identifier of the affected model (e.g. "Vendor").
        target_id: UUID of the affected record. Nullable for system-level events.
        before_state: JSON snapshot of the record before the mutation.
        after_state: JSON snapshot of the record after the mutation.
        request_id: UUID from RequestIDMiddleware for distributed tracing.
        ip_address: Client IP address extracted by get_client_ip().
        created_at: Timestamp of the audit event. Indexed for range queries.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,  # callable — NOT uuid.uuid4()
        editable=False,
    )
    action = models.CharField(max_length=100, db_index=True)

    # Actor — nullable FK so records survive account deletion
    actor = models.ForeignKey(
        "accounts.AdminUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    actor_label = models.CharField(
        max_length=255,
        blank=True,
        help_text="Email snapshot of the actor at the time of the event.",
    )

    # Target
    target_type = models.CharField(max_length=100, blank=True)
    target_id = models.UUIDField(null=True, blank=True)

    # State snapshots
    before_state = models.JSONField(default=dict, blank=True)
    after_state = models.JSONField(default=dict, blank=True)

    # Tracing
    request_id = models.CharField(max_length=36, blank=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # Timestamp — indexed for time-range queries
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = ImmutableAuditLogManager()

    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        # Prevent Django from adding default ordering that conflicts with manager
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["target_type", "target_id"], name="audit_target_idx"),
            models.Index(
                fields=["actor", "created_at"], name="audit_actor_created_idx"
            ),
        ]
        # Enforce immutability at DB level — no update permission
        default_permissions = ("add", "view")

    def __str__(self) -> str:
        return f"[{self.created_at}] {self.action} by {self.actor_label or 'system'}"

    def save(self, *args: object, **kwargs: object) -> None:
        """Allow creation only. Prevent updates to existing records.

        Raises:
            NotImplementedError: If attempting to update an existing record.
        """
        if self.pk and AuditLog.objects.filter(pk=self.pk).exists():
            raise NotImplementedError(
                "AuditLog records are immutable and cannot be updated."
            )
        super().save(*args, **kwargs)

    def delete(self, *args: object, **kwargs: object) -> tuple:
        """Prevent deletion of audit log records.

        Raises:
            NotImplementedError: Always — AuditLog records must never be deleted.
        """
        raise NotImplementedError(
            "AuditLog records are immutable and cannot be deleted."
        )
