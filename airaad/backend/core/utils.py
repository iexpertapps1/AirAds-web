"""
AirAd Backend — General Utilities

get_client_ip: Extracts real client IP from X-Forwarded-For or REMOTE_ADDR.
vendor_has_feature: Stub returning False — Phase B implements full feature gating.
"""

import logging
from typing import TYPE_CHECKING

from django.http import HttpRequest

if TYPE_CHECKING:
    from apps.vendors.models import Vendor

logger = logging.getLogger(__name__)


def get_client_ip(request: HttpRequest) -> str:
    """Extract the real client IP address from the request.

    Checks the ``X-Forwarded-For`` header first (set by nginx reverse proxy),
    then falls back to ``REMOTE_ADDR``. Takes the first (leftmost) IP from
    ``X-Forwarded-For`` which is the original client address.

    Args:
        request: The incoming Django HTTP request.

    Returns:
        Client IP address string. Returns "unknown" if no IP can be determined.

    Example:
        >>> ip = get_client_ip(request)
        >>> isinstance(ip, str)
        True
    """
    x_forwarded_for: str | None = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # X-Forwarded-For: client, proxy1, proxy2 — take the leftmost
        ip = x_forwarded_for.split(",")[0].strip()
        return ip if ip else "unknown"

    return request.META.get("REMOTE_ADDR", "unknown")


def vendor_has_feature(vendor: "Vendor", feature: str) -> bool:
    """Check whether a vendor's subscription tier includes a given feature.

    This is the ONLY subscription feature gate in the entire codebase.
    No ``if vendor.subscription_level ==`` checks are permitted anywhere else.

    Phase A stub — always returns False. Phase B (TASK-B08) implements
    the full feature matrix based on SubscriptionPackage.

    Feature names (Phase B):
        - ``HAPPY_HOUR``
        - ``VOICE_BOT``
        - ``SPONSORED_WINDOW``
        - ``TIME_HEATMAP``
        - ``PREDICTIVE_RECOMMENDATIONS``
        - ``EXTRA_REELS``

    Args:
        vendor: The Vendor instance to check.
        feature: Feature name string (case-sensitive).

    Returns:
        False in Phase A. Phase B returns True if the vendor's subscription
        tier includes the requested feature.

    Example:
        >>> vendor_has_feature(vendor, "HAPPY_HOUR")
        False
    """
    return False
