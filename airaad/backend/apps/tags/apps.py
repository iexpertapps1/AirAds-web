"""AirAd — Tags app configuration."""

from django.apps import AppConfig


class TagsConfig(AppConfig):
    """Configuration for the tags application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.tags"
    verbose_name = "Tags"
