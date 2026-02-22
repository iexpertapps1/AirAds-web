"""AirAd — Imports app configuration."""

from django.apps import AppConfig


class ImportsConfig(AppConfig):
    """Configuration for the imports application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.imports"
    verbose_name = "Imports"
