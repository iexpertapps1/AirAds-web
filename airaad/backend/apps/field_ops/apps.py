"""AirAd — Field Ops app configuration."""

from django.apps import AppConfig


class FieldOpsConfig(AppConfig):
    """Configuration for the field_ops application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.field_ops"
    verbose_name = "Field Operations"
