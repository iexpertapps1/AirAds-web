"""
AirAd Backend — AuditLog Utility

log_action() is the single entry point for writing AuditLog records.
Called explicitly from services.py only — never via signals (R5).
Every POST/PATCH/DELETE in the system must call this function.
"""

import logging
from typing import Any

from django.db import models
from django.http import HttpRequest

logger = logging.getLogger(__name__)


def log_action(
    action: str,
    actor: "Any | None",
    target_obj: models.Model | None,
    request: HttpRequest | None,
    before: dict[str, Any],
    after: dict[str, Any],
) -> "Any":
    """Write an immutable AuditLog entry for a mutation event.

    Must be called from services.py for every POST, PATCH, and DELETE
    operation. Never called via signals — always explicit (R5).

    Args:
        action: Short action identifier string, e.g. "VENDOR_CREATED",
            "AUTH_LOGIN_SUCCESS", "QC_STATUS_UPDATED". Use SCREAMING_SNAKE_CASE.
        actor: The AdminUser (or Customer/Vendor in Phase B) performing the
            action. Pass None for system-initiated events (e.g. Celery tasks).
        target_obj: The Django model instance being acted upon. Pass None
            for events with no specific target (e.g. bulk operations).
        request: The HTTP request object. Used to extract request_id and
            ip_address. Pass None for Celery task contexts.
        before: Dict snapshot of the record state before the mutation.
            Pass {} for creation events.
        after: Dict snapshot of the record state after the mutation.
            Pass {} for deletion events.

    Returns:
        The created AuditLog instance.

    Raises:
        Exception: Re-raises any unexpected DB error after logging it.
            Never silently swallows errors — audit failures are critical.

    Example:
        >>> log_action(
        ...     action="VENDOR_CREATED",
        ...     actor=request.user,
        ...     target_obj=vendor,
        ...     request=request,
        ...     before={},
        ...     after={"business_name": vendor.business_name},
        ... )
    """
    from core.utils import get_client_ip

    from .models import AuditLog

    # Extract actor metadata
    actor_label: str = ""
    if actor is not None:
        actor_label = getattr(actor, "email", str(actor))

    # Extract target metadata
    target_type: str = ""
    target_id = None
    if target_obj is not None:
        target_type = target_obj.__class__.__name__
        pk = getattr(target_obj, "pk", None)
        if pk is not None:
            try:
                import uuid

                target_id = uuid.UUID(str(pk))
            except (ValueError, AttributeError):
                target_id = None

    # Extract request tracing fields
    request_id: str = ""
    ip_address: str | None = None
    if request is not None:
        request_id = getattr(request, "request_id", "")
        ip_address = get_client_ip(request)

    try:
        audit_log = AuditLog(
            action=action,
            actor=actor if _is_admin_user(actor) else None,
            actor_label=actor_label,
            target_type=target_type,
            target_id=target_id,
            before_state=before,
            after_state=after,
            request_id=request_id,
            ip_address=ip_address,
        )
        audit_log.save()
        return audit_log
    except Exception as e:
        logger.error(
            "CRITICAL: Failed to write AuditLog entry",
            extra={
                "action": action,
                "actor_label": actor_label,
                "target_type": target_type,
                "error": str(e),
            },
        )
        raise


def _is_admin_user(actor: Any) -> bool:
    """Check if actor is an AdminUser instance (avoids circular import).

    Args:
        actor: The actor object to check.

    Returns:
        True if actor is an AdminUser, False otherwise.
    """
    if actor is None:
        return False
    return actor.__class__.__name__ == "AdminUser"
