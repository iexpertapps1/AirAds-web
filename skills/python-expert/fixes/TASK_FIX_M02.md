# TASK_FIX_M02 — Implement `record_vendor_view()` Fire-and-Forget
**Severity:** 🟠 MAJOR — Current stub blocks API response; spec requires async Celery dispatch
**Session:** A-S8 | **Effort:** 20 min
**Files:** Create `apps/analytics/tasks.py` + Update `apps/analytics/services.py`

---

## PROBLEM

`apps/analytics/services.py` `record_vendor_view()` is a stub that only logs a debug message. The spec requires fire-and-forget via Celery — the API response must **never wait** for the analytics write. The current implementation blocks the request thread.

**Current broken stub:**
```python
def record_vendor_view(vendor_id: str, ...) -> None:
    logger.debug("record_vendor_view: Phase A stub — vendor_id=%s", vendor_id)
    # Nothing else — analytics event is silently dropped
```

---

## FIX — TWO STEPS

### Step 1: Create `apps/analytics/tasks.py`

```python
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
```

### Step 2: Update `apps/analytics/services.py` — replace the stub body

Find the existing `record_vendor_view` function and replace **only its body** (keep the function signature and docstring intact, or update the docstring to reflect the Celery dispatch):

```python
def record_vendor_view(
    vendor_id: str,
    actor_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Dispatch a vendor view analytics event asynchronously via Celery.

    The API response never waits for this write. Task failure is logged
    but never propagated to the caller (fire-and-forget).

    Args:
        vendor_id: UUID string of the viewed Vendor.
        actor_id: UUID string of the actor, or None for anonymous access.
        metadata: Optional context dict (ip_address, user_agent, request_id).
    """
    from apps.analytics.tasks import record_vendor_view_task

    record_vendor_view_task.delay(
        vendor_id=vendor_id,
        actor_id=actor_id,
        metadata=metadata or {},
    )
```

---

## CONSTRAINTS

- **`ignore_result=True`** on the task — analytics results are never read back; this prevents result backend pollution
- **`from apps.analytics.tasks import record_vendor_view_task`** must be a **local import** inside the function body — prevents circular imports at module load time
- **`metadata or {}`** — never pass `None` to the task; Celery serializes kwargs and `None` dict causes JSON issues
- **Do NOT** add `bind=True` retry logic — analytics failures are acceptable; retrying analytics is not worth the overhead
- **Do NOT** import `record_vendor_view_task` at the top of `services.py` — local import only
- The `record_vendor_view_task` task name must be registered in `celery_app.py` Beat or at least discoverable via `CELERY_IMPORTS` — verify `apps.analytics` is in `INSTALLED_APPS`

---

## VERIFICATION

```bash
cd airaad/backend

# Confirm task file exists and is importable
python -c "
import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.test'
django.setup()
from apps.analytics.tasks import record_vendor_view_task
print('Task registered:', record_vendor_view_task.name)
"
# Expected: Task registered: apps.analytics.tasks.record_vendor_view_task

# Confirm services.py calls .delay()
grep -n "\.delay(" apps/analytics/services.py
# Expected: 1 match — record_vendor_view_task.delay(...)

# Confirm stub logger.debug is gone
grep -n "Phase A stub" apps/analytics/services.py
# Expected: no output

# Run analytics tests
pytest tests/ -k "analytics" -v
```

---

## PYTHON EXPERT RULES APPLIED

- **Correctness:** Local import prevents circular import; `metadata or {}` prevents `None` serialization error
- **Type Safety:** `dict[str, Any]` on `metadata`; `str | None` on `actor_id`; `-> None` return type
- **Performance:** `ignore_result=True` — no result backend write for fire-and-forget tasks
- **Style:** `from __future__ import annotations`; Google-style docstring explaining fire-and-forget contract
