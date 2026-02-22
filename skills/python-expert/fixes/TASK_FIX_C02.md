# TASK_FIX_C02 — Create `tests/factories.py`
**Severity:** 🔴 CRITICAL — All downstream test files (C03, C04, C05) depend on this
**Session:** A-S8 | **Effort:** 45 min | **Blocks:** TASK_FIX_C03, C04, C05

---

## PROBLEM

`conftest.py` uses raw ORM `get_or_create()` calls. The spec (TASK-027) requires factory_boy factories for all 10 models. Without `factories.py`, parametrized RBAC tests and Celery task tests cannot create isolated test data.

---

## FILE TO CREATE

**`tests/factories.py`**

---

## COMPLETE IMPLEMENTATION

```python
"""
AirAd — tests/factories.py

factory_boy factories for all AirAd models.
Use these in tests instead of raw ORM calls for isolated, repeatable test data.
"""
from __future__ import annotations

import uuid

import factory
from django.contrib.gis.geos import Point, Polygon

from apps.accounts.models import AdminRole, AdminUser
from apps.audit.models import AuditLog
from apps.field_ops.models import FieldPhoto, FieldVisit
from apps.geo.models import Area, City, Country, Landmark
from apps.imports.models import ImportBatch, ImportStatus
from apps.tags.models import Tag, TagType
from apps.vendors.models import QCStatus, Vendor
from core.encryption import encrypt


class AdminUserFactory(factory.django.DjangoModelFactory):
    """Factory for AdminUser. Default role: DATA_ENTRY."""

    class Meta:
        model = AdminUser

    id = factory.LazyFunction(uuid.uuid4)
    email = factory.Sequence(lambda n: f"user{n}@test.airaad.com")
    first_name = factory.Sequence(lambda n: f"User{n}")
    last_name = "Test"
    role = AdminRole.DATA_ENTRY
    is_active = True
    is_staff = False

    @factory.post_generation
    def password(obj, create: bool, extracted: str | None, **kwargs) -> None:
        """Set password after creation. Defaults to TestPass@123!."""
        raw = extracted if extracted is not None else "TestPass@123!"
        obj.set_password(raw)
        if create:
            obj.save(update_fields=["password"])


class CountryFactory(factory.django.DjangoModelFactory):
    """Factory for Country."""

    class Meta:
        model = Country

    id = factory.LazyFunction(uuid.uuid4)
    name = "Pakistan"
    code = factory.Sequence(lambda n: f"PK{n}" if n > 0 else "PK")
    slug = factory.Sequence(lambda n: f"pakistan-{n}" if n > 0 else "pakistan")


class CityFactory(factory.django.DjangoModelFactory):
    """Factory for City."""

    class Meta:
        model = City

    id = factory.LazyFunction(uuid.uuid4)
    country = factory.SubFactory(CountryFactory)
    name = factory.Sequence(lambda n: f"City {n}")
    slug = factory.Sequence(lambda n: f"city-{n}")
    centroid = factory.LazyFunction(lambda: Point(67.0099, 24.8607, srid=4326))


class AreaFactory(factory.django.DjangoModelFactory):
    """Factory for Area."""

    class Meta:
        model = Area

    id = factory.LazyFunction(uuid.uuid4)
    city = factory.SubFactory(CityFactory)
    name = factory.Sequence(lambda n: f"Area {n}")
    slug = factory.Sequence(lambda n: f"area-{n}")
    centroid = factory.LazyFunction(lambda: Point(67.068, 24.82, srid=4326))
    boundary = factory.LazyFunction(
        lambda: Polygon(
            ((67.06, 24.81), (67.08, 24.81), (67.08, 24.83), (67.06, 24.83), (67.06, 24.81)),
            srid=4326,
        )
    )


class LandmarkFactory(factory.django.DjangoModelFactory):
    """Factory for Landmark."""

    class Meta:
        model = Landmark

    id = factory.LazyFunction(uuid.uuid4)
    area = factory.SubFactory(AreaFactory)
    name = factory.Sequence(lambda n: f"Landmark {n}")
    slug = factory.Sequence(lambda n: f"landmark-{n}")
    location = factory.LazyFunction(lambda: Point(67.06, 24.827, srid=4326))


class TagFactory(factory.django.DjangoModelFactory):
    """Factory for Tag. Default type: CATEGORY."""

    class Meta:
        model = Tag

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Tag {n}")
    slug = factory.Sequence(lambda n: f"tag-{n}")
    tag_type = TagType.CATEGORY
    is_active = True


class VendorFactory(factory.django.DjangoModelFactory):
    """Factory for Vendor with encrypted phone and valid business hours."""

    class Meta:
        model = Vendor

    id = factory.LazyFunction(uuid.uuid4)
    business_name = factory.Sequence(lambda n: f"Test Vendor {n}")
    slug = factory.Sequence(lambda n: f"test-vendor-{n}")
    city = factory.SubFactory(CityFactory)
    area = factory.SubFactory(AreaFactory)
    gps_point = factory.LazyFunction(lambda: Point(67.06, 24.82, srid=4326))
    phone_number_encrypted = factory.LazyFunction(lambda: encrypt("+923001234567"))
    qc_status = QCStatus.PENDING
    is_deleted = False
    business_hours = factory.LazyFunction(
        lambda: {
            day: {"open": "09:00", "close": "21:00", "is_closed": False}
            for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        }
    )


class ImportBatchFactory(factory.django.DjangoModelFactory):
    """Factory for ImportBatch. Default status: QUEUED."""

    class Meta:
        model = ImportBatch

    id = factory.LazyFunction(uuid.uuid4)
    created_by = factory.SubFactory(AdminUserFactory)
    file_key = factory.Sequence(lambda n: f"imports/test-batch-{n}.csv")
    status = ImportStatus.QUEUED
    total_rows = 0
    processed_rows = 0
    failed_rows = 0
    error_log = factory.LazyFunction(list)


class FieldVisitFactory(factory.django.DjangoModelFactory):
    """Factory for FieldVisit with a default GPS confirmed point."""

    class Meta:
        model = FieldVisit

    id = factory.LazyFunction(uuid.uuid4)
    vendor = factory.SubFactory(VendorFactory)
    agent = factory.SubFactory(AdminUserFactory, role=AdminRole.FIELD_AGENT)
    gps_confirmed_point = factory.LazyFunction(lambda: Point(67.06, 24.82, srid=4326))
    notes = ""


class FieldPhotoFactory(factory.django.DjangoModelFactory):
    """Factory for FieldPhoto with a unique S3 key."""

    class Meta:
        model = FieldPhoto

    id = factory.LazyFunction(uuid.uuid4)
    visit = factory.SubFactory(FieldVisitFactory)
    s3_key = factory.Sequence(lambda n: f"field-photos/test-photo-{n}.jpg")


class AuditLogFactory(factory.django.DjangoModelFactory):
    """Factory for AuditLog. Actor is None by default (Celery context)."""

    class Meta:
        model = AuditLog

    id = factory.LazyFunction(uuid.uuid4)
    actor = None
    actor_label = ""
    action = "TEST_ACTION"
    target_type = "Vendor"
    target_id = factory.LazyFunction(uuid.uuid4)
    target_label = "Test Vendor"
    before_state = factory.LazyFunction(dict)
    after_state = factory.LazyFunction(dict)
    request_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    ip_address = "127.0.0.1"
```

---

## CONSTRAINTS

- **NO mutable default arguments** — all `JSONField`-like defaults use `factory.LazyFunction(list)` or `factory.LazyFunction(dict)`
- **NO `django_get_or_create`** — factories always create fresh records for test isolation
- `VendorFactory.phone_number_encrypted` must call `encrypt()` from `core.encryption` — never store plaintext
- `VendorFactory.business_hours` must be a valid 7-day dict matching `BusinessHoursSchema`
- `AdminUserFactory.password` uses `@factory.post_generation` — never `factory.PostGenerationMethodCall` (deprecated)
- `AuditLogFactory.actor = None` — Celery tasks have no request actor
- All UUID fields use `factory.LazyFunction(uuid.uuid4)` — never `uuid.uuid4()` as a static default

---

## VERIFICATION

```bash
cd airaad/backend
python -c "
import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.test'
django.setup()
from tests.factories import (
    AdminUserFactory, VendorFactory, ImportBatchFactory,
    FieldVisitFactory, AuditLogFactory
)
print('All factories imported successfully')
"

# Run a quick factory smoke test
pytest tests/ -k "factory" -v --no-header 2>&1 | tail -5
```

---

## PYTHON EXPERT RULES APPLIED

- **Correctness:** `LazyFunction` prevents shared mutable state across test instances
- **Type Safety:** `from __future__ import annotations` + type hint on `password` post-generation
- **Performance:** `SubFactory` chains avoid redundant DB queries
- **Style:** One factory per model, alphabetically ordered imports
