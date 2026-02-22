"""
AirAd Backend — Health Check URLs
GET /api/v1/health/ — unauthenticated, implemented in TASK-023 (A-S6).
"""

from django.urls import path

from .views import HealthCheckView

urlpatterns = [
    path("", HealthCheckView.as_view(), name="health-check"),
]
