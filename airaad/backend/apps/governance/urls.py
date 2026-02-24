"""
AirAd Backend — Governance URL Configuration
"""

from django.urls import path

from .views import (
    BlacklistLiftView,
    BlacklistListCreateView,
    ConsentView,
    FraudScoreDetailView,
    FraudScoreListView,
    FraudSignalCreateView,
    VendorSuspensionAppealReviewView,
    VendorSuspensionAppealView,
    VendorSuspensionListCreateView,
    VendorToSAcceptanceView,
    VendorToSHistoryView,
)

urlpatterns = [
    # Fraud Score
    path("fraud-scores/", FraudScoreListView.as_view(), name="fraud-score-list"),
    path(
        "fraud-scores/signals/",
        FraudSignalCreateView.as_view(),
        name="fraud-signal-create",
    ),
    path(
        "fraud-scores/<str:vendor_pk>/",
        FraudScoreDetailView.as_view(),
        name="fraud-score-detail",
    ),
    # Blacklist
    path("blacklist/", BlacklistListCreateView.as_view(), name="blacklist-list-create"),
    path(
        "blacklist/<str:pk>/lift/", BlacklistLiftView.as_view(), name="blacklist-lift"
    ),
    # Vendor Suspension
    path(
        "suspensions/",
        VendorSuspensionListCreateView.as_view(),
        name="suspension-list-create",
    ),
    path(
        "suspensions/<str:pk>/appeal/",
        VendorSuspensionAppealView.as_view(),
        name="suspension-appeal",
    ),
    path(
        "suspensions/<str:pk>/appeal/review/",
        VendorSuspensionAppealReviewView.as_view(),
        name="suspension-appeal-review",
    ),
    # Vendor ToS Acceptance
    path("tos/accept/", VendorToSAcceptanceView.as_view(), name="tos-accept"),
    path("tos/<str:vendor_pk>/", VendorToSHistoryView.as_view(), name="tos-history"),
    # Consent
    path("consent/", ConsentView.as_view(), name="consent"),
]
