# TASK_FIX_C03 — Create `tests/test_business_rules.py`
**Severity:** 🔴 CRITICAL — Phase A Quality Gate requires one test class per business rule R1–R10
**Session:** A-S8 | **Effort:** 60 min | **Depends on:** TASK_FIX_C02 (factories.py)

---

## PROBLEM

No dedicated test classes exist for the 10 non-negotiable business rules. Spot-checks are scattered across other test files. The Phase A Quality Gate explicitly requires `TestPostGISDistanceOnly`, `TestAES256GCMEncryption`, etc. as named classes.

---

## FILE TO CREATE

**`tests/test_business_rules.py`**

---

## COMPLETE IMPLEMENTATION

```python
"""
AirAd — tests/test_business_rules.py

One test class per business rule (R1–R10).
These tests verify the architectural constraints of the AirAd backend.
"""
from __future__ import annotations

import inspect
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml
from django.contrib.gis.geos import Point
from rest_framework.test import APIRequestFactory

from apps.accounts.models import AdminRole, AdminUser
from apps.accounts.permissions import RolePermission
from apps.audit.models import AuditLog
from apps.audit.utils import log_action
from apps.imports.models import ImportBatch
from apps.imports.services import append_error_log
from apps.vendors.models import Vendor
from core.encryption import EncryptionError, decrypt, encrypt
from tests.factories import (
    AdminUserFactory,
    AuditLogFactory,
    ImportBatchFactory,
    VendorFactory,
)

BACKEND_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# R1 — ST_Distance(geography=True) ONLY
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPostGISDistanceOnly:
    """R1: All distance calculations use ST_Distance(geography=True) — never degree × constant."""

    def test_geo_utils_uses_geography_true(self) -> None:
        source = (BACKEND_ROOT / "core" / "geo_utils.py").read_text()
        assert "geography=True" in source, "geo_utils.py must use geography=True in ST_Distance"

    def test_geo_utils_never_uses_degree_constant(self) -> None:
        source = (BACKEND_ROOT / "core" / "geo_utils.py").read_text()
        assert "111" not in source, "Degree-to-metre constant (111) must not appear in geo_utils.py"
        assert "111000" not in source

    def test_qa_services_uses_geography_true(self) -> None:
        source = (BACKEND_ROOT / "apps" / "qa" / "services.py").read_text()
        assert "geography=True" in source, "qa/services.py must use geography=True in ST_Distance"

    def test_drift_distance_returns_metres_not_degrees(self, vendor, field_agent_user) -> None:
        from apps.field_ops.models import FieldVisit
        from core.geo_utils import calculate_drift_distance

        visit = FieldVisit.objects.create(
            vendor=vendor,
            agent=field_agent_user,
            gps_confirmed_point=Point(67.065, 24.825, srid=4326),
        )
        distance = calculate_drift_distance(vendor.gps_point, visit.gps_confirmed_point)
        # 0.005° longitude ≈ ~500m at Karachi latitude — must be > 1 (metres), not 0.005 (degrees)
        assert distance > 1.0, f"Expected metres (>1), got {distance} — likely returning degrees"
        assert distance < 10_000.0, f"Distance {distance}m seems unreasonably large"


# ---------------------------------------------------------------------------
# R2 — AES-256-GCM phone encryption
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAES256GCMEncryption:
    """R2: All phone numbers encrypted at rest using AES-256-GCM."""

    def test_roundtrip(self) -> None:
        plaintext = "+923001234567"
        assert decrypt(encrypt(plaintext)) == plaintext

    def test_random_iv_produces_different_ciphertext(self) -> None:
        ciphertext_a = encrypt("+923001234567")
        ciphertext_b = encrypt("+923001234567")
        assert ciphertext_a != ciphertext_b, "Each encrypt() call must use a fresh random IV"

    def test_empty_string_returns_empty_bytes(self) -> None:
        result = encrypt("")
        assert result == b"", "encrypt('') must return b'' without raising"

    def test_tampered_ciphertext_raises_encryption_error(self) -> None:
        ciphertext = encrypt("+923001234567")
        tampered = bytes([ciphertext[0] ^ 0xFF]) + ciphertext[1:]
        with pytest.raises(EncryptionError):
            decrypt(tampered)

    def test_vendor_phone_stored_as_bytes_not_plaintext(self) -> None:
        vendor = VendorFactory()
        assert isinstance(vendor.phone_number_encrypted, (bytes, memoryview))
        raw = bytes(vendor.phone_number_encrypted)
        assert b"+92" not in raw, "Phone number must not be stored in plaintext"


# ---------------------------------------------------------------------------
# R3 — RolePermission.for_roles() is the ONLY RBAC mechanism
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestForRolesRBAC:
    """R3: RolePermission.for_roles() is the sole RBAC mechanism — no manual role checks in views."""

    def test_for_roles_returns_a_class(self) -> None:
        perm_class = RolePermission.for_roles(AdminRole.SUPER_ADMIN)
        assert inspect.isclass(perm_class)

    def test_permitted_role_has_permission(self) -> None:
        perm_class = RolePermission.for_roles(AdminRole.SUPER_ADMIN)
        user = AdminUserFactory(role=AdminRole.SUPER_ADMIN)
        rf = APIRequestFactory()
        request = rf.get("/")
        request.user = user
        assert perm_class().has_permission(request, None) is True

    def test_blocked_role_denied(self) -> None:
        perm_class = RolePermission.for_roles(AdminRole.SUPER_ADMIN)
        user = AdminUserFactory(role=AdminRole.DATA_ENTRY)
        rf = APIRequestFactory()
        request = rf.get("/")
        request.user = user
        assert perm_class().has_permission(request, None) is False

    def test_unauthenticated_denied(self) -> None:
        perm_class = RolePermission.for_roles(AdminRole.SUPER_ADMIN)
        rf = APIRequestFactory()
        request = rf.get("/")
        request.user = MagicMock(is_authenticated=False)
        assert perm_class().has_permission(request, None) is False

    def test_views_do_not_check_role_manually(self) -> None:
        """No view file should contain raw `request.user.role ==` checks."""
        view_files = list(BACKEND_ROOT.glob("apps/*/views.py"))
        for view_file in view_files:
            source = view_file.read_text()
            assert "request.user.role ==" not in source, (
                f"{view_file.name} contains manual role check — use RolePermission.for_roles() instead"
            )


# ---------------------------------------------------------------------------
# R4 — All business logic in services.py
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestServicesOnlyLogic:
    """R4: Views contain no business logic — all logic delegated to services.py."""

    def test_vendor_views_contain_no_orm_calls(self) -> None:
        source = (BACKEND_ROOT / "apps" / "vendors" / "views.py").read_text()
        assert "Vendor.objects." not in source, "vendors/views.py must not call Vendor.objects directly"

    def test_accounts_views_contain_no_orm_calls(self) -> None:
        source = (BACKEND_ROOT / "apps" / "accounts" / "views.py").read_text()
        assert "AdminUser.objects." not in source

    def test_imports_views_contain_no_orm_calls(self) -> None:
        source = (BACKEND_ROOT / "apps" / "imports" / "views.py").read_text()
        assert "ImportBatch.objects.create" not in source

    def test_services_files_exist_for_all_apps(self) -> None:
        apps_with_mutations = ["accounts", "vendors", "imports", "qa", "tags", "analytics"]
        for app in apps_with_mutations:
            services_path = BACKEND_ROOT / "apps" / app / "services.py"
            assert services_path.exists(), f"apps/{app}/services.py is missing"


# ---------------------------------------------------------------------------
# R5 — AuditLog on every mutation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAuditLogImmutable:
    """R5: AuditLog is write-once — update and delete raise NotImplementedError."""

    def test_manager_update_raises(self, super_admin_user, vendor) -> None:
        log_action(actor=super_admin_user, action="TEST", target=vendor)
        with pytest.raises(NotImplementedError):
            AuditLog.objects.update(action="TAMPERED")

    def test_instance_save_raises(self, super_admin_user, vendor) -> None:
        log_action(actor=super_admin_user, action="TEST", target=vendor)
        entry = AuditLog.objects.first()
        entry.action = "TAMPERED"
        with pytest.raises(NotImplementedError):
            entry.save()

    def test_instance_delete_raises(self, super_admin_user, vendor) -> None:
        log_action(actor=super_admin_user, action="TEST", target=vendor)
        entry = AuditLog.objects.first()
        with pytest.raises(NotImplementedError):
            entry.delete()

    def test_log_action_creates_exactly_one_record(self, super_admin_user, vendor) -> None:
        before_count = AuditLog.objects.count()
        log_action(actor=super_admin_user, action="VENDOR_CREATE", target=vendor)
        assert AuditLog.objects.count() == before_count + 1


# ---------------------------------------------------------------------------
# R6 — Soft deletes only
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestSoftDeleteOnly:
    """R6: Vendor.delete() sets is_deleted=True — never removes the DB row."""

    def test_delete_sets_is_deleted_true(self, vendor) -> None:
        vendor.delete()
        vendor.refresh_from_db()
        assert vendor.is_deleted is True

    def test_record_still_exists_in_db_after_delete(self, vendor) -> None:
        vendor_id = vendor.id
        vendor.delete()
        assert Vendor.all_objects.filter(id=vendor_id).exists()

    def test_default_manager_excludes_deleted_vendor(self, vendor) -> None:
        vendor_id = vendor.id
        vendor.delete()
        assert not Vendor.objects.filter(id=vendor_id).exists()

    def test_all_objects_manager_includes_deleted_vendor(self, vendor) -> None:
        vendor_id = vendor.id
        vendor.delete()
        assert Vendor.all_objects.filter(id=vendor_id).exists()

    def test_db_row_count_unchanged_after_soft_delete(self, vendor) -> None:
        before = Vendor.all_objects.count()
        vendor.delete()
        assert Vendor.all_objects.count() == before


# ---------------------------------------------------------------------------
# R7 — psycopg2 (compiled) — never psycopg2-binary in production
# ---------------------------------------------------------------------------

class TestPsycopg2Compiled:
    """R7: production.txt must use psycopg2 (compiled from source), never psycopg2-binary."""

    def test_production_txt_has_no_binary(self) -> None:
        content = (BACKEND_ROOT / "requirements" / "production.txt").read_text()
        assert "psycopg2-binary" not in content, (
            "production.txt must NOT contain psycopg2-binary (use compiled psycopg2)"
        )

    def test_production_txt_has_psycopg2(self) -> None:
        content = (BACKEND_ROOT / "requirements" / "production.txt").read_text()
        assert "psycopg2" in content, "production.txt must contain psycopg2"


# ---------------------------------------------------------------------------
# R8 — CSV never passed over Celery broker
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCSVNeverOnBroker:
    """R8: process_import_batch receives batch_id only — CSV is always read from S3."""

    def test_task_signature_receives_batch_id_only(self) -> None:
        from apps.imports.tasks import process_import_batch

        sig = inspect.signature(process_import_batch)
        params = list(sig.parameters.keys())
        # bind=True tasks have 'self' as first param; batch_id must be second
        assert "batch_id" in params, "process_import_batch must accept batch_id parameter"
        assert "csv" not in params, "CSV content must never be a task parameter"
        assert "content" not in params

    def test_task_source_reads_from_s3_not_broker(self) -> None:
        source = (BACKEND_ROOT / "apps" / "imports" / "tasks.py").read_text()
        assert "get_object" in source or "StreamingBody" in source, (
            "Import task must read CSV from S3 via get_object/StreamingBody"
        )
        assert "apply_async" not in source.split("def process_import_batch")[0], (
            "CSV content must not be passed in apply_async call"
        )


# ---------------------------------------------------------------------------
# R9 — error_log capped at 1000 entries
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestErrorLogCap:
    """R9: ImportBatch.error_log is capped at 1000 entries by append_error_log()."""

    def test_cap_at_1000_entries(self) -> None:
        batch = ImportBatchFactory()
        for i in range(1001):
            append_error_log(batch, row_number=i, message=f"Error {i}")
        batch.refresh_from_db()
        assert len(batch.error_log) == 1000

    def test_1000_entries_does_not_raise(self) -> None:
        batch = ImportBatchFactory()
        for i in range(1000):
            append_error_log(batch, row_number=i, message=f"Error {i}")
        batch.refresh_from_db()
        assert len(batch.error_log) == 1000

    def test_error_count_field_matches_log_length(self) -> None:
        batch = ImportBatchFactory()
        for i in range(50):
            append_error_log(batch, row_number=i, message=f"Error {i}")
        batch.refresh_from_db()
        assert batch.failed_rows == len(batch.error_log)


# ---------------------------------------------------------------------------
# R10 — celery-beat deploy.replicas: 1
# ---------------------------------------------------------------------------

class TestCeleryBeatReplicas:
    """R10: celery-beat must have deploy.replicas: 1 — prevents duplicate scheduled tasks."""

    def test_celery_beat_service_exists_in_compose(self) -> None:
        compose_path = BACKEND_ROOT.parent / "docker-compose.yml"
        data = yaml.safe_load(compose_path.read_text())
        assert "celery-beat" in data.get("services", {}), (
            "docker-compose.yml must define a celery-beat service"
        )

    def test_celery_beat_replicas_is_one(self) -> None:
        compose_path = BACKEND_ROOT.parent / "docker-compose.yml"
        data = yaml.safe_load(compose_path.read_text())
        replicas = (
            data["services"]["celery-beat"]
            .get("deploy", {})
            .get("replicas")
        )
        assert replicas == 1, (
            f"celery-beat deploy.replicas must be 1, got {replicas!r} — "
            "multiple Beat instances cause duplicate task execution"
        )

    def test_beat_schedules_defined_in_code_not_db(self) -> None:
        source = (BACKEND_ROOT / "celery_app.py").read_text()
        assert "setup_periodic_tasks" in source, (
            "celery_app.py must define setup_periodic_tasks() for code-based Beat schedules"
        )
        assert "DatabaseScheduler" not in source, (
            "DatabaseScheduler must not be used — schedules must be in code only"
        )
```

---

## CONSTRAINTS

- All 10 class names must match exactly: `TestPostGISDistanceOnly`, `TestAES256GCMEncryption`, `TestForRolesRBAC`, `TestServicesOnlyLogic`, `TestAuditLogImmutable`, `TestSoftDeleteOnly`, `TestPsycopg2Compiled`, `TestCSVNeverOnBroker`, `TestErrorLogCap`, `TestCeleryBeatReplicas`
- Classes that don't need DB access must NOT have `@pytest.mark.django_db` (e.g., `TestPsycopg2Compiled`, `TestCeleryBeatReplicas`)
- `BACKEND_ROOT` must be computed from `Path(__file__).resolve().parent.parent` — never hardcoded
- `yaml` import requires `PyYAML` — already in `requirements/base.txt`
- `Vendor.all_objects` must be the unfiltered manager — verify it exists in `vendors/models.py`

---

## VERIFICATION

```bash
cd airaad/backend
pytest tests/test_business_rules.py -v --no-header

# Expected: 30+ tests, all passing
# TestPostGISDistanceOnly::test_geo_utils_uses_geography_true PASSED
# TestAES256GCMEncryption::test_roundtrip PASSED
# ...
# TestCeleryBeatReplicas::test_celery_beat_replicas_is_one PASSED
```

---

## PYTHON EXPERT RULES APPLIED

- **Correctness:** File path assertions use `Path.read_text()` — no subprocess calls
- **Type Safety:** `-> None` on all test methods; `from __future__ import annotations`
- **Style:** Section comments (`# R1`, `# R2`, etc.) for navigation; Google-style docstrings on classes
