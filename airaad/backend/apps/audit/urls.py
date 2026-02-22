"""
AirAd Backend — Audit URL Configuration
Mounted at: /api/v1/audit/
"""

from django.urls import path

from .views import AuditLogListView

urlpatterns = [
    path("", AuditLogListView.as_view(), name="audit-log-list"),
]
