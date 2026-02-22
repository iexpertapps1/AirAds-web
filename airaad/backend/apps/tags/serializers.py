"""
AirAd Backend — Tags Serializers

No business logic — validation only. SYSTEM tag enforcement in tags/services.py.
read_only_fields explicitly declared.
"""

import logging

from rest_framework import serializers

from .models import Tag, TagType

logger = logging.getLogger(__name__)


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model. Read path only — writes go through services."""

    class Meta:
        model = Tag
        fields = [
            "id", "name", "slug", "tag_type",
            "display_label", "display_order", "icon_name",
            "is_active", "created_at",
        ]
        read_only_fields = ["id", "slug", "created_at"]


class CreateTagSerializer(serializers.Serializer):
    """Serializer for creating a Tag. Delegates to tags/services.py."""

    name = serializers.CharField(max_length=100)
    slug = serializers.SlugField(max_length=120)
    tag_type = serializers.ChoiceField(
        choices=[t.value for t in TagType],
        help_text="SYSTEM type is rejected by the API.",
    )
    display_label = serializers.CharField(max_length=150, required=False, default="")
    display_order = serializers.IntegerField(required=False, default=0)
    icon_name = serializers.CharField(max_length=100, required=False, default="")


class UpdateTagSerializer(serializers.Serializer):
    """Serializer for updating a Tag. slug and SYSTEM type changes are rejected in services."""

    name = serializers.CharField(max_length=100, required=False)
    display_label = serializers.CharField(max_length=150, required=False)
    display_order = serializers.IntegerField(required=False)
    icon_name = serializers.CharField(max_length=100, required=False)
    is_active = serializers.BooleanField(required=False)
