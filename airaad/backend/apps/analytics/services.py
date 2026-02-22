"""
AirAd Backend — Analytics Service Layer (R4)

Analytics recording is fire-and-forget via Celery — API response never waits.
Phase A: stub KPI aggregations. Phase B: full AnalyticsEvent model + partitioning.
Every mutation calls log_action() (R5).
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


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


def get_platform_kpis() -> dict[str, Any]:
    """Return basic platform KPI counts for the admin dashboard.

    Phase A: simple DB counts. Phase B: aggregated AnalyticsEvent queries.

    Returns:
        Dict with vendor_count, approved_vendors, pending_vendors,
        import_batch_count keys.
    """
    from apps.imports.models import ImportBatch
    from apps.vendors.models import QCStatus, Vendor

    return {
        "vendor_count": Vendor.objects.count(),
        "approved_vendors": Vendor.objects.filter(qc_status=QCStatus.APPROVED).count(),
        "pending_vendors": Vendor.objects.filter(qc_status=QCStatus.PENDING).count(),
        "import_batch_count": ImportBatch.objects.count(),
    }
