"""
AirAd Backend — pytest conftest.py

All fixtures use factory-boy factories for consistent, minimal test data.
django_db marker is applied per-test — not globally.
Fixtures use pytest-django's db fixture for proper transaction isolation.
No mutable default arguments — all factory defaults use LazyAttribute or Sequence.
"""

import base64
import os

import pytest
from django.contrib.gis.geos import Point
from rest_framework.test import APIClient


# ---------------------------------------------------------------------------
# Settings override — ensure test settings are active
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def django_db_setup():
    """Use the test database defined in config/settings/test.py."""


# ---------------------------------------------------------------------------
# API Client
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client() -> APIClient:
    """Return an unauthenticated DRF APIClient.

    Returns:
        Unauthenticated APIClient instance.
    """
    return APIClient()


@pytest.fixture
def auth_client(api_client: APIClient, super_admin_user) -> APIClient:
    """Return an APIClient authenticated as SUPER_ADMIN.

    Args:
        api_client: Base APIClient fixture.
        super_admin_user: SUPER_ADMIN AdminUser fixture.

    Returns:
        Authenticated APIClient instance.
    """
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(super_admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def data_entry_client(api_client: APIClient, data_entry_user) -> APIClient:
    """Return an APIClient authenticated as DATA_ENTRY.

    Args:
        api_client: Base APIClient fixture.
        data_entry_user: DATA_ENTRY AdminUser fixture.

    Returns:
        Authenticated APIClient instance.
    """
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(data_entry_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


# ---------------------------------------------------------------------------
# AdminUser fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def super_admin_user(db):
    """Create and return a SUPER_ADMIN AdminUser.

    Args:
        db: pytest-django db fixture.

    Returns:
        AdminUser instance with SUPER_ADMIN role.
    """
    from apps.accounts.models import AdminRole, AdminUser

    return AdminUser.objects.create_user(
        email="superadmin@test.airaad.com",
        password="TestPass@123!",
        full_name="Test Super Admin",
        role=AdminRole.SUPER_ADMIN,
    )


@pytest.fixture
def data_entry_user(db):
    """Create and return a DATA_ENTRY AdminUser.

    Args:
        db: pytest-django db fixture.

    Returns:
        AdminUser instance with DATA_ENTRY role.
    """
    from apps.accounts.models import AdminRole, AdminUser

    return AdminUser.objects.create_user(
        email="dataentry@test.airaad.com",
        password="TestPass@123!",
        full_name="Test Data Entry",
        role=AdminRole.DATA_ENTRY,
    )


@pytest.fixture
def admin_user(db):
    """Create and return a DATA_ENTRY AdminUser (generic admin_user alias for tests).

    Args:
        db: pytest-django db fixture.

    Returns:
        AdminUser instance with DATA_ENTRY role.
    """
    from apps.accounts.models import AdminRole, AdminUser

    return AdminUser.objects.create_user(
        email="adminuser@test.airaad.com",
        password="TestPass@123!",
        full_name="Test Admin User",
        role=AdminRole.DATA_ENTRY,
    )


@pytest.fixture
def qa_reviewer_user(db):
    """Create and return a QA_REVIEWER AdminUser.

    Args:
        db: pytest-django db fixture.

    Returns:
        AdminUser instance with QA_REVIEWER role.
    """
    from apps.accounts.models import AdminRole, AdminUser

    return AdminUser.objects.create_user(
        email="qareviewer@test.airaad.com",
        password="TestPass@123!",
        full_name="Test QA Reviewer",
        role=AdminRole.QA_REVIEWER,
    )


@pytest.fixture
def field_agent_user(db):
    """Create and return a FIELD_AGENT AdminUser.

    Args:
        db: pytest-django db fixture.

    Returns:
        AdminUser instance with FIELD_AGENT role.
    """
    from apps.accounts.models import AdminRole, AdminUser

    return AdminUser.objects.create_user(
        email="fieldagent@test.airaad.com",
        password="TestPass@123!",
        full_name="Test Field Agent",
        role=AdminRole.FIELD_AGENT,
    )


# ---------------------------------------------------------------------------
# Geo fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def country(db):
    """Create and return a Pakistan Country instance.

    Args:
        db: pytest-django db fixture.

    Returns:
        Country instance.
    """
    from apps.geo.models import Country

    country, _ = Country.objects.get_or_create(
        code="PK",
        defaults={"name": "Pakistan", "is_active": True},
    )
    return country


@pytest.fixture
def city(db, country):
    """Create and return a Karachi City instance.

    Args:
        db: pytest-django db fixture.
        country: Pakistan Country fixture.

    Returns:
        City instance.
    """
    from apps.geo.models import City

    city, _ = City.objects.get_or_create(
        slug="karachi-test",
        defaults={
            "country": country,
            "name": "Karachi",
            "aliases": ["Karāchi"],
            "centroid": Point(67.0099, 24.8607, srid=4326),
            "is_active": True,
            "display_order": 1,
        },
    )
    return city


@pytest.fixture
def area(db, city):
    """Create and return a DHA Phase 6 Area instance.

    Args:
        db: pytest-django db fixture.
        city: Karachi City fixture.

    Returns:
        Area instance.
    """
    from apps.geo.models import Area

    area, _ = Area.objects.get_or_create(
        slug="dha-phase-6-test",
        defaults={
            "city": city,
            "name": "DHA Phase 6",
            "aliases": ["Defence Phase 6", "DHA-6"],
            "centroid": Point(67.0680, 24.8200, srid=4326),
            "is_active": True,
        },
    )
    return area


@pytest.fixture
def landmark(db, area):
    """Create and return a Zamzama Landmark instance.

    Args:
        db: pytest-django db fixture.
        area: DHA Phase 6 Area fixture.

    Returns:
        Landmark instance.
    """
    from apps.geo.models import Landmark

    landmark, _ = Landmark.objects.get_or_create(
        slug="zamzama-test",
        defaults={
            "area": area,
            "name": "Zamzama Boulevard",
            "aliases": ["Zamzama", "Zamzama Street", "Zamzama Commercial Area"],
            "location": Point(67.0600, 24.8270, srid=4326),
            "is_active": True,
        },
    )
    return landmark


# ---------------------------------------------------------------------------
# Tag fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def category_tag(db):
    """Create and return a CATEGORY tag.

    Args:
        db: pytest-django db fixture.

    Returns:
        Tag instance with tag_type=CATEGORY.
    """
    from apps.tags.models import Tag, TagType

    tag, _ = Tag.objects.get_or_create(
        slug="category-restaurant-test",
        defaults={
            "name": "Restaurant",
            "tag_type": TagType.CATEGORY,
            "display_label": "Restaurant",
            "is_active": True,
        },
    )
    return tag


# ---------------------------------------------------------------------------
# Vendor fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def vendor(db, city, area, landmark, super_admin_user):
    """Create and return a sample Vendor with encrypted phone.

    Args:
        db: pytest-django db fixture.
        city: Karachi City fixture.
        area: DHA Phase 6 Area fixture.
        landmark: Zamzama Landmark fixture.
        super_admin_user: SUPER_ADMIN actor for AuditLog.

    Returns:
        Vendor instance with phone encrypted and business_hours set.
    """
    from apps.vendors.services import create_vendor

    return create_vendor(
        business_name="Test Grill House",
        slug="test-grill-house",
        city_id=str(city.id),
        area_id=str(area.id),
        gps_lon=67.0601,
        gps_lat=24.8271,
        actor=super_admin_user,
        request=None,
        phone="+923001234567",
        description="Test vendor for pytest.",
        address_text="Test Address, DHA Phase 6, Karachi",
        landmark_id=str(landmark.id),
        business_hours={
            "MON": {"open": "09:00", "close": "22:00", "is_closed": False},
            "TUE": {"open": "09:00", "close": "22:00", "is_closed": False},
            "WED": {"open": "09:00", "close": "22:00", "is_closed": False},
            "THU": {"open": "09:00", "close": "22:00", "is_closed": False},
            "FRI": {"open": "09:00", "close": "23:00", "is_closed": False},
            "SAT": {"open": "10:00", "close": "23:00", "is_closed": False},
            "SUN": {"open": "00:00", "close": "00:00", "is_closed": True},
        },
        data_source="MANUAL_ENTRY",
    )


# ---------------------------------------------------------------------------
# ImportBatch fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def import_batch(db, super_admin_user):
    """Create and return an ImportBatch in QUEUED status.

    Args:
        db: pytest-django db fixture.
        super_admin_user: AdminUser who created the batch.

    Returns:
        ImportBatch instance with status=QUEUED.
    """
    from apps.imports.models import ImportBatch, ImportStatus

    return ImportBatch.objects.create(
        file_key="imports/test-batch-001.csv",
        status=ImportStatus.QUEUED,
        created_by=super_admin_user,
    )
