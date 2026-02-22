"""
AirAd Backend — Vendors URL Configuration
Mounted at: /api/v1/vendors/
Full implementation in TASK-020 (SESSION A-S5).
"""

from django.urls import path

from .views import VendorDetailView, VendorListCreateView, VendorQCStatusView

urlpatterns = [
    path("", VendorListCreateView.as_view(), name="vendor-list"),
    path("<uuid:pk>/", VendorDetailView.as_view(), name="vendor-detail"),
    path("<uuid:pk>/qc-status/", VendorQCStatusView.as_view(), name="vendor-qc-status"),
]
