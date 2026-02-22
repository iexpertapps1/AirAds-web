"""
AirAd Backend — Geo URL Configuration
Mounted at: /api/v1/geo/
"""

from django.urls import path

from .views import (
    AreaListCreateView,
    CityDetailView,
    CityListCreateView,
    CountryListCreateView,
    LandmarkListCreateView,
)

urlpatterns = [
    path("countries/", CountryListCreateView.as_view(), name="geo-country-list"),
    path("cities/", CityListCreateView.as_view(), name="geo-city-list"),
    path("cities/<uuid:pk>/", CityDetailView.as_view(), name="geo-city-detail"),
    path("areas/", AreaListCreateView.as_view(), name="geo-area-list"),
    path("landmarks/", LandmarkListCreateView.as_view(), name="geo-landmark-list"),
]
