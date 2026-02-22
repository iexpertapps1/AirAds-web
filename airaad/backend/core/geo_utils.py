"""
AirAd Backend — PostGIS Geospatial Utilities (R1)

ALL distance calculations use ST_Distance(geography=True).
ALL proximity queries use ST_DWithin.
NEVER use degree × constant approximations — non-negotiable rule R1.
"""

import logging
from typing import TYPE_CHECKING

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import QuerySet

if TYPE_CHECKING:
    from apps.vendors.models import Vendor

logger = logging.getLogger(__name__)


def calculate_drift_distance(point_a: Point, point_b: Point) -> float:
    """Calculate the geodesic distance in metres between two GPS points.

    Uses PostGIS ST_Distance with geography=True for accurate metre-based
    distance on the WGS-84 ellipsoid. Never uses degree × constant
    approximations (R1).

    Args:
        point_a: First GPS point (longitude, latitude, SRID=4326).
        point_b: Second GPS point (longitude, latitude, SRID=4326).

    Returns:
        Distance in metres as a float.

    Raises:
        ValueError: If either point is None or has an invalid SRID.

    Example:
        >>> from django.contrib.gis.geos import Point
        >>> a = Point(67.0011, 24.8607, srid=4326)  # Karachi
        >>> b = Point(67.0100, 24.8700, srid=4326)
        >>> distance = calculate_drift_distance(a, b)
        >>> isinstance(distance, float)
        True
    """
    if point_a is None or point_b is None:
        raise ValueError("Both points must be non-None GPS Point objects")

    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT ST_Distance(%s::geography, %s::geography)",
            [point_a.ewkt, point_b.ewkt],
        )
        row = cursor.fetchone()

    return float(row[0])


def find_nearby_vendors(center: Point, radius_meters: float) -> "QuerySet[Vendor]":
    """Return vendors within radius_meters of center using ST_DWithin.

    Filters using PostGIS ST_DWithin on the geography type for accurate
    metre-based proximity. Always filters is_deleted=False (R6).
    Results are annotated with distance and ordered nearest-first.

    Args:
        center: GPS point to search from (longitude, latitude, SRID=4326).
        radius_meters: Search radius in metres.

    Returns:
        QuerySet of Vendor objects within the radius, ordered by distance,
        annotated with a `distance` attribute (Distance object).

    Raises:
        ValueError: If center is None or radius_meters is not positive.

    Example:
        >>> from django.contrib.gis.geos import Point
        >>> center = Point(67.0011, 24.8607, srid=4326)
        >>> qs = find_nearby_vendors(center, 500)
    """
    if center is None:
        raise ValueError("center point must not be None")
    if radius_meters <= 0:
        raise ValueError(f"radius_meters must be positive, got {radius_meters}")

    from apps.vendors.models import Vendor

    return (
        Vendor.objects.filter(
            is_deleted=False,
            gps_point__dwithin=(center, D(m=radius_meters)),
        )
        .annotate(distance=Distance("gps_point", center, spherical=True))
        .order_by("distance")
    )
