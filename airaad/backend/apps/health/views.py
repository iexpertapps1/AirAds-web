"""
AirAd Backend — Health Check View
GET /api/v1/health/ — unauthenticated.
Full implementation in TASK-023 (SESSION A-S6).
DB: SELECT 1 in try/except OperationalError
Redis: ping in try/except ConnectionError
Returns 200 healthy / 503 degraded — never raises unhandled exception.
"""

import logging

import redis
from django.conf import settings
from django.db import OperationalError, connection
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """Unauthenticated health check endpoint.

    Verifies database and Redis connectivity.
    Returns HTTP 200 when all services are healthy, HTTP 503 when degraded.
    Never raises an unhandled exception.
    """

    authentication_classes: list = []
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        """Check database and Redis connectivity.

        Args:
            request: The incoming HTTP request.

        Returns:
            200 {"status": "healthy"} if all services are up.
            503 {"status": "degraded", "details": {...}} if any service is down.
        """
        details: dict[str, str] = {}
        healthy = True

        # Database check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            details["database"] = "ok"
        except OperationalError as e:
            logger.error("Health check: database unavailable", extra={"error": str(e)})
            details["database"] = "unavailable"
            healthy = False

        # Redis check
        try:
            redis_url: str = settings.REDIS_URL if hasattr(settings, "REDIS_URL") else settings.CELERY_BROKER_URL
            client = redis.from_url(redis_url, socket_connect_timeout=2)
            client.ping()
            details["redis"] = "ok"
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            logger.error("Health check: Redis unavailable", extra={"error": str(e)})
            details["redis"] = "unavailable"
            healthy = False

        if healthy:
            return Response({"status": "healthy"}, status=200)

        return Response({"status": "degraded", "details": details}, status=503)
