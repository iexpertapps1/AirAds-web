"""
AirAd Backend — Governance Serializers

Read/write serializers for all governance models.
No business logic — all delegated to services.py (R4).
"""

from rest_framework import serializers

from .models import (
    AppealStatus,
    Blacklist,
    BlacklistType,
    ConsentCategory,
    ConsentRecord,
    EnforcementAction,
    FraudScore,
    FraudSignal,
    VendorSuspension,
    VendorToSAcceptance,
)

# ---------------------------------------------------------------------------
# Fraud Score
# ---------------------------------------------------------------------------


class FraudScoreSerializer(serializers.ModelSerializer):
    needs_manual_review = serializers.BooleanField(read_only=True)
    should_auto_suspend = serializers.BooleanField(read_only=True)

    class Meta:
        model = FraudScore
        fields = [
            "id",
            "vendor",
            "actor_email",
            "score",
            "is_auto_suspended",
            "signals",
            "needs_manual_review",
            "should_auto_suspend",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class AddFraudSignalSerializer(serializers.Serializer):
    signal = serializers.ChoiceField(choices=FraudSignal.choices)
    vendor_id = serializers.UUIDField(required=False, allow_null=True)
    actor_email = serializers.EmailField(required=False, allow_blank=True, default="")
    reason = serializers.CharField(required=False, allow_blank=True, default="")


# ---------------------------------------------------------------------------
# Blacklist
# ---------------------------------------------------------------------------


class BlacklistSerializer(serializers.ModelSerializer):
    added_by_email = serializers.CharField(
        source="added_by.email", read_only=True, default=""
    )

    class Meta:
        model = Blacklist
        fields = [
            "id",
            "blacklist_type",
            "value",
            "reason",
            "added_by",
            "added_by_email",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "added_by",
            "added_by_email",
            "created_at",
            "updated_at",
        ]


class CreateBlacklistSerializer(serializers.Serializer):
    blacklist_type = serializers.ChoiceField(choices=BlacklistType.choices)
    value = serializers.CharField(max_length=500)
    reason = serializers.CharField()


class LiftBlacklistSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True, default="")


# ---------------------------------------------------------------------------
# Vendor Suspension
# ---------------------------------------------------------------------------


class VendorSuspensionSerializer(serializers.ModelSerializer):
    issued_by_email = serializers.CharField(
        source="issued_by.email", read_only=True, default=""
    )
    appeal_reviewed_by_email = serializers.CharField(
        source="appeal_reviewed_by.email", read_only=True, default=""
    )

    class Meta:
        model = VendorSuspension
        fields = [
            "id",
            "vendor",
            "action",
            "reason",
            "policy_reference",
            "issued_by",
            "issued_by_email",
            "suspension_ends_at",
            "appeal_status",
            "appeal_notes",
            "appeal_reviewed_by",
            "appeal_reviewed_by_email",
            "appeal_reviewed_at",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "issued_by",
            "issued_by_email",
            "appeal_reviewed_by",
            "appeal_reviewed_by_email",
            "appeal_reviewed_at",
            "created_at",
            "updated_at",
        ]


class IssueEnforcementSerializer(serializers.Serializer):
    vendor_id = serializers.UUIDField()
    action = serializers.ChoiceField(choices=EnforcementAction.choices)
    reason = serializers.CharField()
    policy_reference = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    suspension_days = serializers.IntegerField(
        required=False, default=7, min_value=1, max_value=365
    )


class ProcessAppealSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(
        choices=[AppealStatus.APPROVED, AppealStatus.REJECTED]
    )
    notes = serializers.CharField(required=False, allow_blank=True, default="")


# ---------------------------------------------------------------------------
# Vendor ToS Acceptance
# ---------------------------------------------------------------------------


class VendorToSAcceptanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorToSAcceptance
        fields = [
            "id",
            "vendor",
            "tos_version",
            "accepted_by_email",
            "ip_address",
            "accepted_at",
        ]
        read_only_fields = fields


class RecordToSAcceptanceSerializer(serializers.Serializer):
    vendor_id = serializers.UUIDField()
    accepted_by_email = serializers.EmailField()
    tos_version = serializers.CharField(required=False, default="1.0", max_length=20)


# ---------------------------------------------------------------------------
# Consent Record
# ---------------------------------------------------------------------------


class ConsentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentRecord
        fields = ["id", "user", "category", "granted", "ip_address", "created_at"]
        read_only_fields = fields


class UpdateConsentSerializer(serializers.Serializer):
    category = serializers.ChoiceField(choices=ConsentCategory.choices)
    granted = serializers.BooleanField()
