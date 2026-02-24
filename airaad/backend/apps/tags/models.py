"""
AirAd Backend — Tag Model

6 tag types via TextChoices. SYSTEM tags cannot be created/edited/deleted
via API — enforced in tags/services.py, not at model level.
slug is immutable after creation — enforced in tags/services.py.
"""

import uuid

from django.db import models


class TagType(models.TextChoices):
    """Six tag type categories for the AirAd taxonomy."""

    LOCATION = "LOCATION", "Location"
    CATEGORY = "CATEGORY", "Category"
    INTENT = "INTENT", "Intent"
    PROMOTION = "PROMOTION", "Promotion"
    TIME = "TIME", "Time"
    SYSTEM = "SYSTEM", "System"


class Tag(models.Model):
    """A taxonomy tag that can be assigned to vendors.

    SYSTEM tags are auto-managed by TagAutoAssigner (Phase B) and cannot
    be created, edited, or deleted via the public API. This constraint is
    enforced in tags/services.py — not at the model level.

    slug is immutable after creation — enforced in tags/services.py.

    Attributes:
        id: UUID primary key.
        name: Human-readable tag name.
        slug: URL-safe identifier — immutable after creation.
        tag_type: One of 6 TagType values.
        display_label: UI display string (may differ from name).
        display_order: Integer for ordering in UI.
        icon_name: Icon identifier string for frontend rendering.
        is_active: Whether this tag is active.
        created_at: Auto-set on creation.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, db_index=True)
    tag_type = models.CharField(
        max_length=20,
        choices=TagType.choices,
        db_index=True,
    )
    display_label = models.CharField(max_length=150, blank=True)
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    icon_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Optional expiry datetime for PROMOTION tags (spec §4.3). "
        "Null means the tag never auto-expires. "
        "expire_promotion_tags Celery task deactivates tags past this datetime.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["tag_type", "display_order", "name"]
        indexes = [
            models.Index(
                fields=["tag_type", "is_active"], name="tags_tag_type_active_idx"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} [{self.tag_type}]"

    @property
    def is_system(self) -> bool:
        """Return True if this tag is a SYSTEM tag.

        Returns:
            True if tag_type is SYSTEM, False otherwise.
        """
        return self.tag_type == TagType.SYSTEM
