"""
AirAd Backend — Development Settings
Local DB, DEBUG=True, relaxed security, verbose logging.
"""

from .base import *  # noqa: F401, F403
from .base import env

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = ["*"]

# ---------------------------------------------------------------------------
# Database — local PostgreSQL+PostGIS (psycopg2-binary acceptable in dev)
# ENGINE inherited from base.py (postgis), CONN_MAX_AGE=60 inherited
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        **env.db(
            "DATABASE_URL", default="postgis://airaad:airaad@localhost:5432/airaad_db"
        ),
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "CONN_MAX_AGE": 60,
    }
}

# ---------------------------------------------------------------------------
# CORS — allow all origins in development
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True

# ---------------------------------------------------------------------------
# Django Extensions
# ---------------------------------------------------------------------------
INSTALLED_APPS = INSTALLED_APPS + ["django_extensions"]  # noqa: F405

# ---------------------------------------------------------------------------
# Email — console backend in development
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ---------------------------------------------------------------------------
# Logging — verbose in development
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "core": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
