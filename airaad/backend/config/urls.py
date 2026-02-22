"""
AirAd Backend — Root URL Configuration
All 12 API prefixes registered here.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Django admin (internal use only)
    path("django-admin/", admin.site.urls),

    # -------------------------------------------------------------------------
    # API v1 — all routes
    # -------------------------------------------------------------------------
    path("api/v1/auth/",       include("apps.accounts.urls")),
    path("api/v1/geo/",        include("apps.geo.urls")),
    path("api/v1/tags/",       include("apps.tags.urls")),
    path("api/v1/vendors/",    include("apps.vendors.urls")),
    path("api/v1/imports/",    include("apps.imports.urls")),
    path("api/v1/field-ops/",  include("apps.field_ops.urls")),
    path("api/v1/qa/",         include("apps.qa.urls")),
    path("api/v1/analytics/",  include("apps.analytics.urls")),
    path("api/v1/audit/",      include("apps.audit.urls")),
    path("api/v1/health/",     include("apps.health.urls")),

    # -------------------------------------------------------------------------
    # OpenAPI schema + Swagger UI
    # -------------------------------------------------------------------------
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
