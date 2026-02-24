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

    Uses ``REMOTE_ADDR`` as the authoritative source when behind a trusted
    reverse proxy (nginx). If ``NUM_PROXIES`` is set in Django settings
    (default 1), the rightmost non-proxy IP in ``X-Forwarded-For`` is used,
    which cannot be spoofed by the client.

    Taking the *leftmost* XFF entry is insecure because clients can inject
    arbitrary values there. The *rightmost* entry is appended by the trusted
    proxy and is reliable.

    Args:
        request: The incoming Django HTTP request.

    Returns:
        Client IP address string. Returns "unknown" if no IP can be determined.

    Example:
        >>> ip = get_client_ip(request)
        >>> isinstance(ip, str)
        True
    """
    from django.conf import settings

    num_proxies: int = getattr(settings, "NUM_PROXIES", 1)

    x_forwarded_for: str | None = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for and num_proxies > 0:
        # X-Forwarded-For: client, proxy1, ..., trusted-proxy
        # Take the entry num_proxies positions from the right — that is the
        # first IP added by the trusted proxy, not client-controlled.
        ips = [ip.strip() for ip in x_forwarded_for.split(",")]
        index = max(len(ips) - num_proxies, 0)
        ip = ips[index]
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
