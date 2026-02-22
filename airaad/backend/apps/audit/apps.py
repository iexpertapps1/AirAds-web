"""AirAd — Audit app configuration."""

from django.apps import AppConfig


class AuditConfig(AppConfig):
    """Configuration for the audit application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.audit"
    verbose_name = "Audit"
