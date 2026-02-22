"""AirAd — Discovery app configuration."""

from django.apps import AppConfig


class DiscoveryConfig(AppConfig):
    """Configuration for the discovery application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.discovery"
    verbose_name = "Discovery"
