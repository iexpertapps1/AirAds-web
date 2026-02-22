"""
AirAd — apps/subscriptions/tasks.py

Phase B placeholder tasks registered in celery_app.py Beat schedule.
Full implementation deferred to Phase B (TASK-B06).
"""
from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="apps.subscriptions.tasks.subscription_expiry_check")
def subscription_expiry_check(self) -> None:
    """Check and expire overdue vendor subscriptions.

    Registered in celery_app.py Beat schedule (daily midnight UTC).
    Full implementation deferred to Phase B — TASK-B06.
    """
    logger.debug("subscription_expiry_check: Phase B stub — no-op.")
