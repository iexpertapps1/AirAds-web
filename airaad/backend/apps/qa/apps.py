"""AirAd — QA app configuration."""

from django.apps import AppConfig


class QAConfig(AppConfig):
    """Configuration for the qa application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.qa"
    verbose_name = "QA"
