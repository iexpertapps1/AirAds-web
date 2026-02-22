"""
AirAd Backend — QA URL Configuration
Mounted at: /api/v1/qa/
Full implementation in TASK-020 (SESSION A-S5).
"""

from django.urls import path

from .views import QADashboardView

urlpatterns = [
    path("dashboard/", QADashboardView.as_view(), name="qa-dashboard"),
]
