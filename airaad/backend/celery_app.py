"""
AirAd Backend — Celery Application
All Beat schedules registered in code via setup_periodic_tasks() — never in DB (R10).
task_failure signal handler uses structured logging — never print().
"""

import logging
import os
from typing import Any

from celery import Celery
from celery.signals import task_failure
from django.conf import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Celery app instance
# ---------------------------------------------------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

app = Celery("airaad")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


# ---------------------------------------------------------------------------
# Beat schedules — all registered in code, never stored in DB (R10)
# Registered after all apps are finalized to ensure task names are resolvable.
# ---------------------------------------------------------------------------
@app.on_after_finalize.connect
def setup_periodic_tasks(sender: Celery, **kwargs: Any) -> None:
    """Register all Celery Beat periodic schedules in code.

    All 5 schedules are defined here. Beat replicas must be exactly 1 (R10).
    Phase B tasks (discount_scheduler, subscription_expiry_check,
    hourly_tag_assignment) are registered now so Beat is aware of them
    when Phase B task bodies are implemented.

    Args:
        sender: The Celery app instance.
        **kwargs: Additional signal keyword arguments.
    """
    from celery.schedules import crontab

    # Phase A — GPS drift scan: every Sunday at 02:00 UTC
    sender.add_periodic_task(
        crontab(hour=2, minute=0, day_of_week="sunday"),
        app.signature("apps.qa.tasks.weekly_gps_drift_scan"),
        name="weekly_gps_drift_scan",
    )

    # Phase A — Duplicate vendor scan: daily at 03:00 UTC
    sender.add_periodic_task(
        crontab(hour=3, minute=0),
        app.signature("apps.qa.tasks.daily_duplicate_scan"),
        name="daily_duplicate_scan",
    )

    # Phase B — Discount scheduler: every 1 minute
    sender.add_periodic_task(
        60.0,
        app.signature("apps.vendors.tasks.discount_scheduler"),
        name="discount_scheduler",
    )

    # Phase B — Subscription expiry check: daily at midnight UTC
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        app.signature("apps.subscriptions.tasks.subscription_expiry_check"),
        name="subscription_expiry_check",
    )

    # Phase B — Hourly tag auto-assignment: every 1 hour
    sender.add_periodic_task(
        crontab(minute=0),
        app.signature("apps.tags.tasks.hourly_tag_assignment"),
        name="hourly_tag_assignment",
    )


# ---------------------------------------------------------------------------
# task_failure signal — structured logging, never print()
# ---------------------------------------------------------------------------
@task_failure.connect
def on_task_failure(
    sender: Any,
    task_id: str,
    exception: Exception,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    traceback: Any,
    einfo: Any,
    **signal_kwargs: Any,
) -> None:
    """Handle Celery task failure with structured logging.

    Logs task name, task_id, and exception message. Never raises — signal
    handlers must not propagate exceptions back to the worker.

    Args:
        sender: The task class that failed.
        task_id: Unique ID of the failed task execution.
        exception: The exception instance that caused the failure.
        args: Positional arguments the task was called with.
        kwargs: Keyword arguments the task was called with.
        traceback: Traceback object.
        einfo: ExceptionInfo object from billiard.
        **signal_kwargs: Additional signal keyword arguments.
    """
    logger.error(
        "Task failed",
        extra={
            "task": sender.name,
            "task_id": task_id,
            "exception": str(exception),
            "exception_type": type(exception).__name__,
        },
    )
