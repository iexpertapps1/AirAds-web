"""AirAd — Subscriptions app configuration."""

from django.apps import AppConfig


class SubscriptionsConfig(AppConfig):
    """Configuration for the subscriptions application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.subscriptions"
    verbose_name = "Subscriptions"
