"""
AirAd — apps/analytics/tasks.py

Fire-and-forget analytics recording tasks.
API responses never wait for these writes — failures are logged, never propagated.
"""
from __future__ import annotations

import logging
from typing import Any

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="apps.analytics.tasks.record_vendor_view_task",
    ignore_result=True,
)
def record_vendor_view_task(
    self,
    vendor_id: str,
    actor_id: str | None,
    metadata: dict[str, Any],
) -> None:
    """Persist a vendor view analytics event asynchronously.

    Dispatched by record_vendor_view() in services.py via .delay().
    Failures are logged but never propagated to the caller.

    Args:
        vendor_id: UUID string of the viewed Vendor.
        actor_id: UUID string of the viewing AdminUser, or None for anonymous.
        metadata: Additional context dict (ip_address, user_agent, request_id).
    """
    try:
        logger.info(
            "analytics.vendor_view",
            extra={
                "vendor_id": vendor_id,
                "actor_id": actor_id,
                **metadata,
            },
        )
    except Exception as exc:
        logger.error(
            "record_vendor_view_task failed: %s",
            exc,
            exc_info=True,
            extra={"vendor_id": vendor_id},
        )
