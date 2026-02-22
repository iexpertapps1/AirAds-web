"""
AirAd Backend — Imports URL Configuration
Mounted at: /api/v1/imports/
Full implementation in TASK-020 (SESSION A-S5).
"""

from django.urls import path

from .views import ImportBatchDetailView, ImportBatchListCreateView

urlpatterns = [
    path("", ImportBatchListCreateView.as_view(), name="import-batch-list"),
    path("<uuid:pk>/", ImportBatchDetailView.as_view(), name="import-batch-detail"),
]
