"""
AirAd Backend — Field Ops URL Configuration
Mounted at: /api/v1/field-ops/
Full implementation in TASK-020 (SESSION A-S5).
"""

from django.urls import path

from .views import (
    FieldPhotoListView,
    FieldPhotoUploadView,
    FieldVisitDetailView,
    FieldVisitListCreateView,
)

urlpatterns = [
    path("", FieldVisitListCreateView.as_view(), name="fieldvisit-list"),
    path("<uuid:pk>/", FieldVisitDetailView.as_view(), name="fieldvisit-detail"),
    path("<uuid:visit_pk>/photos/", FieldPhotoListView.as_view(), name="fieldphoto-list"),
    path("<uuid:visit_pk>/photos/upload/", FieldPhotoUploadView.as_view(), name="fieldphoto-upload"),
]
