"""
AirAd Backend — Governance Models (spec §6, §8)

Five models covering Phase-A governance gaps:

  FraudScore      — per-vendor fraud signal accumulation (spec §6.2)
  Blacklist       — phone/device/GPS blacklist management (spec §6.3)
  VendorSuspension — enforcement ladder: warn/suspend/ban (spec §8.2)
  VendorToSAcceptance — vendor terms-of-service acceptance audit trail (spec §8.3)
  ConsentRecord   — GDPR consent capture per user (spec §8.1)

All models use UUID PKs. All mutations must call log_action() from services.py.
"""

import uuid

from django.db import models

# ---------------------------------------------------------------------------
# §6.2 — Fraud Score
# ---------------------------------------------------------------------------


class FraudSignal(models.TextChoices):
    """Fraud signal types with their score contributions (spec §6.2)."""

    MULTI_CLAIM_SAME_DEVICE = (
        "MULTI_CLAIM_SAME_DEVICE",
        "Multiple claims from same device/IP (+1)",
    )
    BLACKLISTED_PHONE = "BLACKLISTED_PHONE", "Blacklisted phone number (+3)"
    GPS_ANOMALY = "GPS_ANOMALY", "GPS anomaly — water/outside city (+2)"
    EXCESSIVE_PROMOTIONS = (
        "EXCESSIVE_PROMOTIONS",
        "Excessive promotion creation >10/day (+1)",
    )
    DUPLICATE_CLAIM = "DUPLICATE_CLAIM", "Duplicate claim attempt (+2)"
    USER_REPORT = "USER_REPORT", "User report received (+1)"


FRAUD_SIGNAL_SCORES: dict[str, int] = {
    FraudSignal.MULTI_CLAIM_SAME_DEVICE: 1,
    FraudSignal.BLACKLISTED_PHONE: 3,
    FraudSignal.GPS_ANOMALY: 2,
    FraudSignal.EXCESSIVE_PROMOTIONS: 1,
    FraudSignal.DUPLICATE_CLAIM: 2,
    FraudSignal.USER_REPORT: 1,
}

FRAUD_SCORE_MANUAL_REVIEW_THRESHOLD = 3
FRAUD_SCORE_AUTO_SUSPEND_THRESHOLD = 6


class FraudScore(models.Model):
    """Accumulated fraud score for a vendor or user account (spec §6.2).

    Score is incremented by add_signal() in governance/services.py.
    Thresholds:
      0–2  → Normal, no action
      3–5  → Flagged for manual review
      6+   → Auto-suspend, requires Ops Manager approval to reactivate

    Attributes:
        id: UUID primary key.
        vendor: FK to Vendor (nullable — score can apply to a user account too).
        actor_email: Email of the user/vendor being scored (denormalised for display).
        score: Current accumulated fraud score.
        is_auto_suspended: True if score crossed the auto-suspend threshold.
        signals: JSON list of signal events applied to this score.
        created_at: When the score record was first created.
        updated_at: Last time the score was updated.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    vendor = models.OneToOneField(
        "vendors.Vendor",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="fraud_score",
        help_text="Vendor this score belongs to. Null for user-level scores.",
    )
    actor_email = models.EmailField(
        blank=True,
        db_index=True,
        help_text="Denormalised email of the entity being scored.",
    )
    score = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Accumulated fraud score. Thresholds: 3+ manual review, 6+ auto-suspend.",
    )
    is_auto_suspended = models.BooleanField(
        default=False,
        db_index=True,
        help_text="True if score crossed AUTO_SUSPEND_THRESHOLD (6+).",
    )
    signals = models.JSONField(
        default=list,
        blank=True,
        help_text="Ordered list of signal events: [{signal, score_delta, reason, ts}].",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fraud Score"
        verbose_name_plural = "Fraud Scores"
        ordering = ["-score", "-updated_at"]
        indexes = [
            models.Index(fields=["score", "is_auto_suspended"], name="fraud_score_idx"),
        ]

    def __str__(self) -> str:
        return f"FraudScore({self.actor_email or self.vendor_id}, score={self.score})"

    @property
    def needs_manual_review(self) -> bool:
        """True if score is in the manual-review band (3–5)."""
        return (
            FRAUD_SCORE_MANUAL_REVIEW_THRESHOLD
            <= self.score
            < FRAUD_SCORE_AUTO_SUSPEND_THRESHOLD
        )

    @property
    def should_auto_suspend(self) -> bool:
        """True if score has reached or exceeded the auto-suspend threshold (6+)."""
        return self.score >= FRAUD_SCORE_AUTO_SUSPEND_THRESHOLD


# ---------------------------------------------------------------------------
# §6.3 — Blacklist
# ---------------------------------------------------------------------------


class BlacklistType(models.TextChoices):
    """Types of entities that can be blacklisted (spec §6.3)."""

    PHONE_NUMBER = "PHONE_NUMBER", "Phone Number"
    DEVICE_ID = "DEVICE_ID", "Device ID"
    GPS_COORDINATE = "GPS_COORDINATE", "GPS Coordinate"


class Blacklist(models.Model):
    """Blacklisted entity — phone number, device ID, or GPS coordinate (spec §6.3).

    Blacklist entries require Ops Manager approval (enforced in services.py).
    Documented reason is mandatory for audit trail.

    Attributes:
        id: UUID primary key.
        blacklist_type: One of BlacklistType values.
        value: The blacklisted value (phone number, device ID, or "lat,lon" string).
        reason: Mandatory reason for blacklisting (audit trail).
        added_by: FK to AdminUser who added this entry.
        is_active: False = entry has been lifted (appeal approved).
        created_at: When the entry was added.
        updated_at: Last modification time.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    blacklist_type = models.CharField(
        max_length=20,
        choices=BlacklistType.choices,
        db_index=True,
    )
    value = models.CharField(
        max_length=500,
        db_index=True,
        help_text="Blacklisted value: phone number, device ID, or 'lat,lon' string.",
    )
    reason = models.TextField(
        help_text="Mandatory reason for blacklisting (audit trail per spec §6.3).",
    )
    added_by = models.ForeignKey(
        "accounts.AdminUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="blacklist_entries_added",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="False = entry has been lifted via appeal process.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Blacklist Entry"
        verbose_name_plural = "Blacklist Entries"
        ordering = ["-created_at"]
        unique_together = [("blacklist_type", "value")]
        indexes = [
            models.Index(
                fields=["blacklist_type", "is_active"], name="blacklist_type_active_idx"
            ),
        ]

    def __str__(self) -> str:
        return (
            f"Blacklist[{self.blacklist_type}] {self.value} (active={self.is_active})"
        )


# ---------------------------------------------------------------------------
# §8.2 — Vendor Suspension (Enforcement Ladder)
# ---------------------------------------------------------------------------


class EnforcementAction(models.TextChoices):
    """Enforcement ladder actions per spec §8.2."""

    WARNING = "WARNING", "Warning"
    CONTENT_REMOVAL = "CONTENT_REMOVAL", "Content Removal"
    TEMPORARY_SUSPENSION = "TEMPORARY_SUSPENSION", "Temporary Suspension (7 days)"
    PERMANENT_BAN = "PERMANENT_BAN", "Permanent Ban"


class AppealStatus(models.TextChoices):
    """Appeal status for a suspension record."""

    NONE = "NONE", "No Appeal Filed"
    PENDING = "PENDING", "Appeal Pending"
    APPROVED = "APPROVED", "Appeal Approved — Restored"
    REJECTED = "REJECTED", "Appeal Rejected"


class VendorSuspension(models.Model):
    """Enforcement action applied to a vendor (spec §8.2).

    Implements the 4-step enforcement ladder:
      1. WARNING — first offense, minor violation
      2. CONTENT_REMOVAL — reel/promotion deleted
      3. TEMPORARY_SUSPENSION — 7 days, repeat offenses
      4. PERMANENT_BAN — severe violations, fraud

    Vendors may appeal within 7 days. Ops Manager reviews appeals.
    All actions are audit-logged via log_action() in services.py.

    Attributes:
        id: UUID primary key.
        vendor: FK to the suspended Vendor.
        action: EnforcementAction value.
        reason: Mandatory reason for the action.
        policy_reference: Optional policy clause reference.
        issued_by: FK to AdminUser who issued the action.
        suspension_ends_at: For TEMPORARY_SUSPENSION — when it expires. Null otherwise.
        appeal_status: Current appeal status.
        appeal_notes: Notes from the appeal review.
        appeal_reviewed_by: FK to AdminUser who reviewed the appeal.
        appeal_reviewed_at: When the appeal was reviewed.
        is_active: False = action has been lifted (appeal approved or expired).
        created_at: When the action was issued.
        updated_at: Last modification time.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.CASCADE,
        related_name="suspensions",
    )
    action = models.CharField(
        max_length=25,
        choices=EnforcementAction.choices,
        db_index=True,
    )
    reason = models.TextField(
        help_text="Mandatory reason for the enforcement action (shown to vendor).",
    )
    policy_reference = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional policy clause reference, e.g. 'Section 4.3 — Fake Promotions'.",
    )
    issued_by = models.ForeignKey(
        "accounts.AdminUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="suspensions_issued",
    )
    suspension_ends_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="For TEMPORARY_SUSPENSION only — when the suspension expires.",
    )

    # Appeal workflow
    appeal_status = models.CharField(
        max_length=10,
        choices=AppealStatus.choices,
        default=AppealStatus.NONE,
        db_index=True,
    )
    appeal_notes = models.TextField(
        blank=True,
        help_text="Notes from the appeal review (Ops Manager).",
    )
    appeal_reviewed_by = models.ForeignKey(
        "accounts.AdminUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="appeals_reviewed",
    )
    appeal_reviewed_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="False = action lifted (appeal approved or temporary suspension expired).",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vendor Suspension"
        verbose_name_plural = "Vendor Suspensions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["vendor", "is_active"], name="suspension_vendor_active_idx"
            ),
            models.Index(
                fields=["action", "is_active"], name="suspension_action_active_idx"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.action} on {self.vendor_id} (active={self.is_active})"


# ---------------------------------------------------------------------------
# §8.3 — Vendor Terms of Service Acceptance
# ---------------------------------------------------------------------------


class VendorToSAcceptance(models.Model):
    """Audit trail of vendor terms-of-service acceptance (spec §8.3).

    Required before claim approval. Digital acceptance stored with:
    - Vendor reference
    - ToS version accepted
    - IP address at time of acceptance
    - Timestamp

    Attributes:
        id: UUID primary key.
        vendor: FK to Vendor.
        tos_version: Version string of the ToS accepted (e.g. "1.0").
        accepted_by_email: Email of the person who accepted (denormalised).
        ip_address: IP address at time of acceptance.
        accepted_at: Timestamp of acceptance.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.CASCADE,
        related_name="tos_acceptances",
    )
    tos_version = models.CharField(
        max_length=20,
        default="1.0",
        help_text="Version of the Terms of Service accepted.",
    )
    accepted_by_email = models.EmailField(
        help_text="Email of the person who accepted the ToS (denormalised for audit).",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address at time of acceptance.",
    )
    accepted_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Vendor ToS Acceptance"
        verbose_name_plural = "Vendor ToS Acceptances"
        ordering = ["-accepted_at"]
        indexes = [
            models.Index(
                fields=["vendor", "tos_version"], name="tos_vendor_version_idx"
            ),
        ]

    def __str__(self) -> str:
        return f"ToS v{self.tos_version} accepted by {self.accepted_by_email}"


# ---------------------------------------------------------------------------
# §8.1 — Consent Record (GDPR)
# ---------------------------------------------------------------------------


class ConsentCategory(models.TextChoices):
    """GDPR consent categories per spec §8.1."""

    GPS_TRACKING = "GPS_TRACKING", "GPS Tracking (required for AR)"
    BEHAVIORAL_ANALYTICS = "BEHAVIORAL_ANALYTICS", "Behavioral Analytics (optional)"
    MARKETING_NOTIFICATIONS = (
        "MARKETING_NOTIFICATIONS",
        "Marketing Notifications (optional)",
    )


class ConsentRecord(models.Model):
    """GDPR consent record for an admin user (spec §8.1).

    Captures explicit opt-in/opt-out per consent category.
    Granular controls: each category is stored as a separate record.
    Immutable — new record created on each consent change (audit trail).

    Attributes:
        id: UUID primary key.
        user: FK to AdminUser.
        category: ConsentCategory value.
        granted: True = opted in, False = opted out.
        ip_address: IP address at time of consent action.
        created_at: Timestamp of this consent event.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        "accounts.AdminUser",
        on_delete=models.CASCADE,
        related_name="consent_records",
    )
    category = models.CharField(
        max_length=30,
        choices=ConsentCategory.choices,
        db_index=True,
    )
    granted = models.BooleanField(
        help_text="True = opted in, False = opted out.",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address at time of consent action.",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Consent Record"
        verbose_name_plural = "Consent Records"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["user", "category", "created_at"], name="consent_user_cat_idx"
            ),
        ]

    def __str__(self) -> str:
        status = "granted" if self.granted else "revoked"
        return f"Consent[{self.category}] {status} by user {self.user_id}"
