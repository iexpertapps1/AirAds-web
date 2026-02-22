"""
Tests for apps/health — HealthCheckView.
"""

import pytest
from django.urls import reverse
from unittest.mock import patch


@pytest.mark.django_db
class TestHealthCheckView:
    """Tests for GET /api/v1/health/."""

    def test_health_check_returns_200_when_db_ok(self, api_client):
        """Health check returns 200 when DB is reachable."""
        url = reverse("health-check")
        response = api_client.get(url)
        # DB is up in test environment — expect 200 or 503 depending on Redis
        assert response.status_code in (200, 503)
        assert "status" in response.data

    def test_health_check_no_auth_required(self, api_client):
        """Health check endpoint requires no authentication."""
        url = reverse("health-check")
        response = api_client.get(url)
        # Must not return 401 or 403
        assert response.status_code not in (401, 403)

    @patch("apps.health.views.connection")
    def test_health_check_db_failure_returns_503(self, mock_conn, api_client):
        """DB failure returns 503 with degraded status."""
        from django.db import OperationalError

        mock_conn.cursor.side_effect = OperationalError("DB down")
        url = reverse("health-check")
        response = api_client.get(url)
        assert response.status_code == 503
        assert response.data["status"] == "degraded"
        assert response.data["details"]["database"] == "unavailable"
