# TASK_FIX_C01 — Create Phase B Stub Task Files
**Severity:** 🔴 CRITICAL — Celery Beat crashes on startup without these files
**Session:** A-S8 | **Effort:** 30 min | **Blocks:** Everything (Beat must start before any task runs)

---

## PROBLEM

`celery_app.py` registers 3 Beat schedules pointing to task paths that do not exist:

```python
# celery_app.py — these 3 task paths have no corresponding .py files:
"apps.vendors.tasks.discount_scheduler"
"apps.subscriptions.tasks.subscription_expiry_check"
"apps.tags.tasks.hourly_tag_assignment"
```

Celery Beat raises `celery.exceptions.NotRegistered` on startup. The entire scheduled task system is broken.

---

## FILES TO CREATE

### 1. `apps/vendors/tasks.py`

```python
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
```

### 2. `apps/subscriptions/tasks.py`

```python
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
```

### 3. `apps/tags/tasks.py`

```python
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
```

---

## CONSTRAINTS

- Task `name=` strings must **exactly** match what `celery_app.py` registers — do not change them
- `bind=True` is required on all tasks — Beat tasks always use `self`
- Return type is `None` — these stubs do nothing
- Do NOT add any model imports or DB queries — pure stubs only
- `from __future__ import annotations` must be the first import

---

## VERIFICATION

```bash
# Start Celery worker — must show no NotRegistered errors
cd airaad/backend
celery -A celery_app worker --loglevel=info --without-gossip --without-mingle -Q celery 2>&1 | head -40

# Confirm all 3 tasks are registered
celery -A celery_app inspect registered 2>&1 | grep -E "(discount_scheduler|subscription_expiry_check|hourly_tag_assignment)"
# Expected output — all 3 lines present:
# apps.vendors.tasks.discount_scheduler
# apps.subscriptions.tasks.subscription_expiry_check
# apps.tags.tasks.hourly_tag_assignment
```

---

## PYTHON EXPERT RULES APPLIED

- **Correctness:** Exact `name=` string match prevents `NotRegistered`
- **Type Safety:** `-> None` return type on all stubs
- **Style:** Google-style docstring explaining Phase B deferral
- **Performance:** No-op body — zero overhead on Beat tick
