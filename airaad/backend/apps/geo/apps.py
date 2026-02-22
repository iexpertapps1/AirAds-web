"""AirAd — Geo app configuration."""

from django.apps import AppConfig


class GeoConfig(AppConfig):
    """Configuration for the geo application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.geo"
    verbose_name = "Geo"
