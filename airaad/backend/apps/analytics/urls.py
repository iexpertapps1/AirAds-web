"""
AirAd Backend — Analytics URL Configuration
Mounted at: /api/v1/analytics/
Full implementation in TASK-020 (SESSION A-S5).
"""

from django.urls import path

from .views import PlatformKPIView

urlpatterns = [
    path("kpis/", PlatformKPIView.as_view(), name="analytics-kpis"),
]
