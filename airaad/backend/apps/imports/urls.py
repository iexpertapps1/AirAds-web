"""
AirAd Backend — Imports URL Configuration
Mounted at: /api/v1/imports/
Full implementation in TASK-020 (SESSION A-S5).
"""

from django.urls import path

from .views import ImportBatchDetailView, ImportBatchListCreateView
from .views_geo_hierarchy import (
    AreasByCityView,
    AreaWithCentroidView,
    CategoryTagsListView,
    CitiesByCountryView,
    CountriesListView,
)
from .views_google_places import GooglePlacesImportView
from .views_google_places_enhanced import EnhancedGooglePlacesImportView

urlpatterns = [
    # Import batches
    path("", ImportBatchListCreateView.as_view(), name="import-batch-list"),
    path("<uuid:pk>/", ImportBatchDetailView.as_view(), name="import-batch-detail"),
    # Google Places imports
    path(
        "google-places/", GooglePlacesImportView.as_view(), name="google-places-import"
    ),
    path(
        "google-places/enhanced/",
        EnhancedGooglePlacesImportView.as_view(),
        name="enhanced-google-places-import",
    ),
    # Geo hierarchy for dropdowns
    path("geo/countries/", CountriesListView.as_view(), name="countries-list"),
    path(
        "geo/countries/<uuid:country_id>/cities/",
        CitiesByCountryView.as_view(),
        name="cities-by-country",
    ),
    path(
        "geo/cities/<uuid:city_id>/areas/",
        AreasByCityView.as_view(),
        name="areas-by-city",
    ),
    path(
        "geo/areas/<uuid:area_id>/", AreaWithCentroidView.as_view(), name="area-detail"
    ),
    # Categories
    path("tags/categories/", CategoryTagsListView.as_view(), name="category-tags-list"),
]
