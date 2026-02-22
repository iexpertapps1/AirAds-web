# TASK_FIX_M01 — Fix N+1 Query in `weekly_gps_drift_scan`
**Severity:** 🟠 MAJOR — N+1 queries cause exponential DB load at scale
**Session:** A-S8 | **Effort:** 20 min | **File:** `apps/qa/tasks.py`

---

## PROBLEM

`weekly_gps_drift_scan` fetches a list of vendor IDs, then calls `Vendor.objects.get(id=vendor_id)` inside the loop — one DB query per vendor. With 10,000 vendors this is 10,000 queries per batch tick.

**Current broken pattern:**
```python
vendor_ids = Vendor.objects.filter(is_deleted=False).values_list("id", flat=True)
for vendor_id in vendor_ids[offset:offset + batch_size]:
    vendor = Vendor.objects.get(id=vendor_id)  # N+1 query!
    latest_visit = FieldVisit.objects.filter(
        vendor_id=vendor_id, gps_confirmed_point__isnull=False
    ).latest("created_at")
```

---

## FIX

Replace the two-step ID-then-fetch pattern with a single queryset slice using `select_related`. Materialize with `list()` before iteration to avoid queryset re-evaluation inside the loop.

**In `weekly_gps_drift_scan`:**

```python
# BEFORE — N+1
vendor_ids = Vendor.objects.filter(is_deleted=False).values_list("id", flat=True)
for vendor_id in vendor_ids[offset:offset + batch_size]:
    vendor = Vendor.objects.get(id=vendor_id)

# AFTER — single query per batch
vendors = list(
    Vendor.objects.filter(is_deleted=False)
    .select_related("city", "area")
    .order_by("id")[offset:offset + batch_size]
)
for vendor in vendors:
    ...
```

**In the inner `FieldVisit` query** — replace `.latest()` (raises `DoesNotExist`) with `.first()` on an ordered queryset:

```python
# BEFORE — raises DoesNotExist if no visits
latest_visit = FieldVisit.objects.filter(
    vendor_id=vendor.id, gps_confirmed_point__isnull=False
).latest("created_at")

# AFTER — returns None safely
latest_visit = (
    FieldVisit.objects
    .filter(vendor=vendor, gps_confirmed_point__isnull=False)
    .order_by("-created_at")
    .first()
)
if latest_visit is None:
    continue
```

**Apply the same fix to `daily_duplicate_scan`** if it has the same pattern:

```python
# BEFORE
vendor_ids = Vendor.objects.exclude(qc_status=QCStatus.NEEDS_REVIEW)...values_list("id", flat=True)
for vendor_id in vendor_ids[offset:offset + batch_size]:
    vendor = Vendor.objects.get(id=vendor_id)

# AFTER
vendors = list(
    Vendor.objects.filter(is_deleted=False)
    .exclude(qc_status=QCStatus.NEEDS_REVIEW)
    .select_related("city", "area")
    .order_by("id")[offset:offset + batch_size]
)
for vendor in vendors:
    ...
```

---

## COMPLETE CORRECTED TASK BODIES

Read the current `apps/qa/tasks.py` first, then apply these targeted edits:

1. In `weekly_gps_drift_scan`: replace the `vendor_ids` + inner `get()` pattern with the `list(queryset[offset:offset+batch_size])` pattern
2. In `weekly_gps_drift_scan`: replace `FieldVisit.objects.filter(...).latest(...)` with `.order_by("-created_at").first()` + `if latest_visit is None: continue`
3. In `daily_duplicate_scan`: apply the same queryset fix if the same N+1 pattern exists

---

## CONSTRAINTS

- **Do NOT change** the batch size (500), the `offset` loop logic, or the `flag_gps_drift()` / `run_duplicate_scan_for_vendor()` call signatures
- **Do NOT use** `iterator()` on the sliced queryset — `list()` is sufficient and avoids cursor issues with PostGIS
- **`select_related("city", "area")`** — only add relations that are actually accessed inside the loop body
- **`order_by("id")`** is required on the sliced queryset — without it, pagination is non-deterministic
- **`FieldVisit.objects.filter(...).first()`** returns `None` — always add `if latest_visit is None: continue` guard

---

## VERIFICATION

```bash
cd airaad/backend

# Confirm the N+1 pattern is gone
grep -n "objects.get(id=vendor_id)" apps/qa/tasks.py
# Expected: no output (pattern removed)

grep -n "select_related" apps/qa/tasks.py
# Expected: at least 1 match in weekly_gps_drift_scan

# Run the QA task tests
pytest tests/test_celery_tasks.py::TestWeeklyGpsDriftScan -v
pytest tests/test_celery_tasks.py::TestDailyDuplicateScan -v
```

---

## PYTHON EXPERT RULES APPLIED

- **Correctness:** `.first()` instead of `.latest()` — no `DoesNotExist` exception risk
- **Performance:** Single queryset per batch replaces N individual `get()` calls
- **Type Safety:** `vendors: list[Vendor]` — explicit type after `list()` materialization
- **Style:** `order_by("id")` makes pagination deterministic and testable
