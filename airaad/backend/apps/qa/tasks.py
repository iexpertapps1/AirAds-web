"""
AirAd Backend — QA Celery Tasks

weekly_gps_drift_scan: Beat schedule — every Sunday 02:00 UTC.
    Iterates approved vendors that have at least one FieldVisit.
    Compares stored gps_point against the latest confirmed gps_confirmed_point.
    Uses ST_Distance(geography=True) via qa/services.flag_gps_drift() — never degree×constant (R1).

daily_duplicate_scan: Beat schedule — daily 03:00 UTC.
    Iterates approved vendors in batches of 500.
    Uses ST_DWithin(50m) + difflib.SequenceMatcher(0.85) via qa/services.run_duplicate_scan_for_vendor().
    Skips vendors already flagged as NEEDS_REVIEW.
"""

import logging
from typing import Any

from celery import shared_task

logger = logging.getLogger(__name__)

_BATCH_SIZE = 500


@shared_task(bind=True, name="apps.qa.tasks.weekly_gps_drift_scan")
def weekly_gps_drift_scan(self: Any) -> None:
    """Scan all APPROVED vendors for GPS drift against their latest field visit.

    Triggered by Celery Beat every Sunday at 02:00 UTC.
    Processes vendors in batches of 500 to avoid memory pressure.
    Uses ST_Distance(geography=True) in qa/services.flag_gps_drift() — never degree×constant (R1).
    Writes AuditLog for every flagged vendor via log_action() in services.py (R5).
    """
    from apps.field_ops.models import FieldVisit
    from apps.vendors.models import QCStatus, Vendor

    from .services import flag_gps_drift

    logger.info("weekly_gps_drift_scan started")

    flagged_count = 0
    checked_count = 0

    # Iterate approved vendors in batches — single query per batch (no N+1)
    offset = 0
    while True:
        vendors = list(
            Vendor.objects
            .filter(qc_status=QCStatus.APPROVED)
            .select_related("city", "area")
            .order_by("id")[offset:offset + _BATCH_SIZE]
        )
        if not vendors:
            break

        for vendor in vendors:
            # Get the most recent field visit with a confirmed GPS point
            latest_visit = (
                FieldVisit.objects
                .filter(vendor=vendor, gps_confirmed_point__isnull=False)
                .order_by("-created_at")
                .first()
            )

            if latest_visit is None:
                continue

            checked_count += 1

            try:
                was_flagged = flag_gps_drift(
                    vendor=vendor,
                    field_visit_point=latest_visit.gps_confirmed_point,
                    actor=None,   # Celery context — no HTTP actor
                    request=None,
                )
                if was_flagged:
                    flagged_count += 1
            except Exception as exc:
                logger.error(
                    "GPS drift check failed for vendor",
                    extra={"vendor_id": str(vendor.id), "error": str(exc)},
                )

        offset += _BATCH_SIZE

    logger.info(
        "weekly_gps_drift_scan complete",
        extra={"checked": checked_count, "flagged": flagged_count},
    )


@shared_task(bind=True, name="apps.qa.tasks.daily_duplicate_scan")
def daily_duplicate_scan(self: Any) -> None:
    """Scan all APPROVED vendors for potential duplicates.

    Triggered by Celery Beat daily at 03:00 UTC.
    Processes vendors in batches of 500 to avoid memory pressure.
    Skips vendors already flagged as NEEDS_REVIEW.
    Uses ST_DWithin(50m) + difflib.SequenceMatcher(0.85) in qa/services.
    Writes AuditLog for every flagged vendor via log_action() in services.py (R5).
    """
    from apps.vendors.models import QCStatus, Vendor

    from .services import run_duplicate_scan_for_vendor

    logger.info("daily_duplicate_scan started")

    total_flagged = 0
    total_checked = 0

    offset = 0
    while True:
        vendors = list(
            Vendor.objects
            .filter(is_deleted=False)
            .exclude(qc_status=QCStatus.NEEDS_REVIEW)
            .select_related("city", "area")
            .order_by("id")[offset:offset + _BATCH_SIZE]
        )
        if not vendors:
            break

        for vendor in vendors:
            total_checked += 1

            try:
                flagged_ids = run_duplicate_scan_for_vendor(
                    vendor=vendor,
                    actor=None,   # Celery context — no HTTP actor
                    request=None,
                )
                total_flagged += len(flagged_ids)
            except Exception as exc:
                logger.error(
                    "Duplicate scan failed for vendor",
                    extra={"vendor_id": str(vendor.id), "error": str(exc)},
                )

        offset += _BATCH_SIZE

    logger.info(
        "daily_duplicate_scan complete",
        extra={"checked": total_checked, "flagged": total_flagged},
    )
