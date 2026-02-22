"""
AirAd Backend — Audit Serializers

Read-only serializer for AuditLog. No write operations permitted.
"""

from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """Read-only serializer for AuditLog entries.

    All fields are read-only — AuditLog records are immutable (R5).
    """

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "action",
            "actor",
            "actor_label",
            "target_type",
            "target_id",
            "before_state",
            "after_state",
            "request_id",
            "ip_address",
            "created_at",
        ]
        read_only_fields = fields
