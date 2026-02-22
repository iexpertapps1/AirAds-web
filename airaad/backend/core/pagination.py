"""
AirAd Backend — Standard Pagination

PAGE_SIZE=25, max_page_size=100. Applied globally via REST_FRAMEWORK settings.
"""

import logging

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class StandardResultsPagination(PageNumberPagination):
    """Standard page-number pagination for all AirAd API endpoints.

    Default page size is 25 results. Clients may request up to 100 results
    per page using the ``page_size`` query parameter.

    Example:
        GET /api/v1/vendors/?page=2&page_size=50
    """

    page_size: int = 25
    page_size_query_param: str = "page_size"
    max_page_size: int = 100
    page_query_param: str = "page"

    def get_paginated_response(self, data: list) -> Response:
        """Return paginated response wrapped in the standard AirAd envelope.

        Args:
            data: Serialized page of results.

        Returns:
            Response with success, count, next, previous, and results fields.
        """
        return Response(
            {
                "success": True,
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "data": data,
            }
        )

    def get_paginated_response_schema(self, schema: dict) -> dict:
        """Return OpenAPI schema for the paginated response envelope.

        Args:
            schema: The schema of the items array.

        Returns:
            OpenAPI schema dict describing the paginated envelope.
        """
        return {
            "type": "object",
            "required": ["success", "count", "data"],
            "properties": {
                "success": {"type": "boolean", "example": True},
                "count": {"type": "integer", "example": 100},
                "next": {"type": "string", "nullable": True, "format": "uri"},
                "previous": {"type": "string", "nullable": True, "format": "uri"},
                "data": schema,
            },
        }
