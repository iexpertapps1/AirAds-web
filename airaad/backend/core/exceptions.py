"""
AirAd Backend — Custom Exception Handler

Wraps all DRF exceptions into a consistent JSON envelope:
    {
        "success": false,
        "data": null,
        "message": "Human-readable summary",
        "errors": { ... }
    }

Never swallows unhandled exceptions — only wraps DRF-handled ones.
"""

import logging
from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(
    exc: Exception, context: dict[str, Any]
) -> Response | None:
    """Wrap DRF exceptions into the standard AirAd response envelope.

    Calls DRF's default exception_handler first. If DRF handles the exception,
    the response is re-wrapped into the standard envelope. If DRF does not
    handle it (returns None), this function also returns None — Django's
    500 handler takes over.

    Args:
        exc: The exception that was raised.
        context: DRF context dict containing the view and request.

    Returns:
        Wrapped Response if DRF handled the exception, None otherwise.

    Example response (400):
        {
            "success": false,
            "data": null,
            "message": "Validation failed",
            "errors": {"email": ["This field is required."]}
        }
    """
    response = exception_handler(exc, context)

    if response is None:
        # Unhandled exception — let Django's 500 handler deal with it
        logger.exception(
            "Unhandled exception in view",
            extra={
                "exception_type": type(exc).__name__,
                "view": context.get("view"),
            },
        )
        return None

    errors: dict[str, Any] = {}
    message: str = "An error occurred"

    if isinstance(response.data, dict):
        # DRF validation errors: {"field": ["msg"]} or {"detail": "msg"}
        if "detail" in response.data:
            message = str(response.data["detail"])
            errors = {}
        else:
            message = _extract_message(response.data)
            errors = response.data
    elif isinstance(response.data, list):
        message = str(response.data[0]) if response.data else "An error occurred"
        errors = {"non_field_errors": response.data}
    else:
        message = str(response.data)

    response.data = {
        "success": False,
        "data": None,
        "message": message,
        "errors": errors,
    }

    return response


def _extract_message(data: dict[str, Any]) -> str:
    """Extract a human-readable summary from a DRF validation error dict.

    Args:
        data: DRF validation error dictionary.

    Returns:
        First error message found, or a generic fallback.
    """
    for field, errors in data.items():
        if isinstance(errors, list) and errors:
            first = errors[0]
            return f"{field}: {first}" if field != "non_field_errors" else str(first)
        if isinstance(errors, str):
            return f"{field}: {errors}"
    return "Validation failed"


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK,
) -> Response:
    """Build a standard success response envelope.

    Convenience helper for views that need to return a consistent
    success envelope without going through a serializer.

    Args:
        data: Serialized payload to include in the response.
        message: Human-readable success message.
        status_code: HTTP status code (default 200).

    Returns:
        DRF Response with the standard success envelope.
    """
    return Response(
        {
            "success": True,
            "data": data,
            "message": message,
            "errors": {},
        },
        status=status_code,
    )
