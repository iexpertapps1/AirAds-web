"""
AirAd — apps/tags/tasks.py

Phase B placeholder tasks registered in celery_app.py Beat schedule.
Full implementation deferred to Phase B (TASK-B07).
"""
from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="apps.tags.tasks.hourly_tag_assignment")
def hourly_tag_assignment(self) -> None:
    """Auto-assign tags to vendors based on business profile signals.

    Registered in celery_app.py Beat schedule (every 1 hour).
    Full implementation deferred to Phase B — TASK-B07.
    """
    logger.debug("hourly_tag_assignment: Phase B stub — no-op.")
