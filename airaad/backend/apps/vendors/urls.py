"""
AirAd Backend — Vendors URL Configuration
Mounted at: /api/v1/vendors/
Full implementation in TASK-020 (SESSION A-S5).
"""

from django.urls import path

from .views import (
    VendorAnalyticsView,
    VendorDetailView,
    VendorListCreateView,
    VendorPhotosView,
    VendorQCStatusView,
    VendorTagDetailView,
    VendorTagsView,
    VendorVisitsView,
)

urlpatterns = [
    path("", VendorListCreateView.as_view(), name="vendor-list"),
    path("<uuid:pk>/", VendorDetailView.as_view(), name="vendor-detail"),
    path("<uuid:pk>/qc-status/", VendorQCStatusView.as_view(), name="vendor-qc-status"),
    path("<uuid:vendor_pk>/photos/", VendorPhotosView.as_view(), name="vendor-photos"),
    path("<uuid:vendor_pk>/visits/", VendorVisitsView.as_view(), name="vendor-visits"),
    path("<uuid:vendor_pk>/tags/", VendorTagsView.as_view(), name="vendor-tags"),
    path(
        "<uuid:vendor_pk>/tags/<uuid:tag_pk>/",
        VendorTagDetailView.as_view(),
        name="vendor-tag-detail",
    ),
    path(
        "<uuid:vendor_pk>/analytics/",
        VendorAnalyticsView.as_view(),
        name="vendor-analytics",
    ),
]
