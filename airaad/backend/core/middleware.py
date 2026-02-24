"""
AirAd Backend — Request ID Middleware

Assigns a unique UUID4 per request for distributed tracing.
Must be the FIRST middleware in settings.MIDDLEWARE (index 0).

Uses uuid.uuid4() — never uuid.uuid1() (uuid1 leaks MAC address — privacy risk).
"""

import logging
import uuid
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


class RequestIDMiddleware:
    """Assign a unique UUID4 request ID to every incoming HTTP request.

    Attaches the ID to:
    - ``request.request_id`` — available to all downstream middleware and views
    - ``X-Request-ID`` response header — returned to the client for tracing

    If the client sends an ``X-Request-ID`` header, it is ignored and a fresh
    server-generated UUID is always used to prevent ID spoofing.

    Must be placed at index 0 in ``settings.MIDDLEWARE``.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialise the middleware.

        Args:
            get_response: The next middleware or view callable in the chain.
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request, attach a request ID, and add it to the response.

        Args:
            request: The incoming HTTP request.

        Returns:
            The HTTP response with ``X-Request-ID`` header set.
        """
        request_id: str = str(uuid.uuid4())  # uuid4 — never uuid1 (privacy)
        request.request_id = request_id  # type: ignore[attr-defined]

        response: HttpResponse = self.get_response(request)
        response["X-Request-ID"] = request_id
        return response
