"""
AirAd Backend — Production Settings
PostgreSQL + PostGIS, S3 storage, DEBUG=False, strict security.
"""

from .base import *  # noqa: F401, F403
from .base import ALLOWED_HOSTS, AWS_S3_REGION_NAME, AWS_STORAGE_BUCKET_NAME, env

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
DEBUG = False

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Railway terminates SSL at the load balancer — the container receives HTTP.
# SECURE_SSL_REDIRECT must be False to prevent redirect loops and allow
# Railway's internal health checks (which are plain HTTP) to succeed.
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)

# Trust Railway's reverse proxy X-Forwarded-Proto header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"

# ---------------------------------------------------------------------------
# ALLOWED_HOSTS — auto-detect Railway domain
# ---------------------------------------------------------------------------
# Railway injects RAILWAY_PUBLIC_DOMAIN (e.g. airaad-backend.up.railway.app)
# Auto-add it so health checks and requests work without manual configuration.
RAILWAY_PUBLIC_DOMAIN = env("RAILWAY_PUBLIC_DOMAIN", default="")
RAILWAY_PRIVATE_DOMAIN = env("RAILWAY_PRIVATE_DOMAIN", default="")
if RAILWAY_PUBLIC_DOMAIN and RAILWAY_PUBLIC_DOMAIN not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)
if RAILWAY_PRIVATE_DOMAIN and RAILWAY_PRIVATE_DOMAIN not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RAILWAY_PRIVATE_DOMAIN)

# ---------------------------------------------------------------------------
# Database — production uses DATABASE_URL from env (PostGIS engine set in base)
# ---------------------------------------------------------------------------
# Inherited from base.py — ENGINE is already postgis, CONN_MAX_AGE=60

# ---------------------------------------------------------------------------
# Static & Media — S3 via django-storages (if AWS configured)
# ---------------------------------------------------------------------------
# Only use S3 if AWS_STORAGE_BUCKET_NAME is actually configured.
# Otherwise fall back to filesystem storage (STATIC_ROOT from base.py).
# This allows the app to start without S3 during initial Railway setup.
if AWS_STORAGE_BUCKET_NAME:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "bucket_name": AWS_STORAGE_BUCKET_NAME,
                "region_name": AWS_S3_REGION_NAME,
                "default_acl": None,
                "file_overwrite": False,
                "querystring_auth": True,
            },
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
            "OPTIONS": {
                "bucket_name": AWS_STORAGE_BUCKET_NAME,
                "region_name": AWS_S3_REGION_NAME,
                "location": "static",
                "default_acl": "public-read",
                "querystring_auth": False,
            },
        },
    }
    STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/"
# else: uses STATIC_URL and STATIC_ROOT from base.py (filesystem storage)

# ---------------------------------------------------------------------------
# Logging — structured JSON in production
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": (
                '{"time": "%(asctime)s", "level": "%(levelname)s", '
                '"logger": "%(name)s", "message": "%(message)s"}'
            ),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "celery": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "core": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "security.alerts": {
            "handlers": ["console"],
            "level": "CRITICAL",
            "propagate": False,
        },
    },
}
