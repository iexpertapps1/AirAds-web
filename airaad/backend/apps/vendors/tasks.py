"""
AirAd — apps/vendors/tasks.py

Phase B placeholder tasks registered in celery_app.py Beat schedule.
Full implementation deferred to Phase B (TASK-B06).
"""
from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="apps.vendors.tasks.discount_scheduler")
def discount_scheduler(self) -> None:
    """Apply active discounts and promotions to eligible vendors.

    Registered in celery_app.py Beat schedule (every 1 minute).
    Full implementation deferred to Phase B — TASK-B06.
    """
    logger.debug("discount_scheduler: Phase B stub — no-op.")
