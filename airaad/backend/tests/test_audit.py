"""
Tests for apps/audit — AuditLog immutability and log_action().
"""

import pytest


@pytest.mark.django_db
class TestAuditLogImmutability:
    """Tests for AuditLog immutable semantics."""

    def test_log_action_creates_record(self, super_admin_user, vendor):
        """log_action() creates an AuditLog record."""
        from apps.audit.models import AuditLog
        from apps.audit.utils import log_action

        before_count = AuditLog.objects.count()
        log_action(
            action="TEST_ACTION",
            actor=super_admin_user,
            target_obj=vendor,
            request=None,
            before={"field": "old"},
            after={"field": "new"},
        )
        assert AuditLog.objects.count() == before_count + 1

    def test_log_action_stores_actor_label(self, super_admin_user, vendor):
        """log_action() stores actor email as actor_label snapshot."""
        from apps.audit.models import AuditLog
        from apps.audit.utils import log_action

        log_action(
            action="TEST_ACTOR_LABEL",
            actor=super_admin_user,
            target_obj=vendor,
            request=None,
            before={},
            after={},
        )
        entry = AuditLog.objects.filter(action="TEST_ACTOR_LABEL").first()
        assert entry is not None
        assert entry.actor_label == "superadmin@test.airaad.com"

    def test_log_action_stores_target_type(self, super_admin_user, vendor):
        """log_action() stores the target model class name."""
        from apps.audit.models import AuditLog
        from apps.audit.utils import log_action

        log_action(
            action="TEST_TARGET_TYPE",
            actor=super_admin_user,
            target_obj=vendor,
            request=None,
            before={},
            after={},
        )
        entry = AuditLog.objects.filter(action="TEST_TARGET_TYPE").first()
        assert entry.target_type == "Vendor"

    def test_audit_log_save_blocks_update(self, super_admin_user, vendor):
        """Saving an existing AuditLog record raises NotImplementedError."""
        from apps.audit.models import AuditLog
        from apps.audit.utils import log_action

        log_action(
            action="TEST_IMMUTABLE",
            actor=super_admin_user,
            target_obj=vendor,
            request=None,
            before={},
            after={},
        )
        entry = AuditLog.objects.filter(action="TEST_IMMUTABLE").first()
        entry.action = "MUTATED"

        with pytest.raises(NotImplementedError):
            entry.save()

    def test_audit_log_delete_raises(self, super_admin_user, vendor):
        """Calling delete() on AuditLog raises NotImplementedError."""
        from apps.audit.models import AuditLog
        from apps.audit.utils import log_action

        log_action(
            action="TEST_DELETE_GUARD",
            actor=super_admin_user,
            target_obj=vendor,
            request=None,
            before={},
            after={},
        )
        entry = AuditLog.objects.filter(action="TEST_DELETE_GUARD").first()

        with pytest.raises(NotImplementedError):
            entry.delete()

    def test_audit_log_manager_update_raises(self):
        """ImmutableAuditLogManager.update() raises NotImplementedError."""
        from apps.audit.models import AuditLog

        with pytest.raises(NotImplementedError):
            AuditLog.objects.update(action="MUTATED")

    def test_log_action_with_none_actor(self, vendor):
        """log_action() with actor=None (Celery context) stores null FK."""
        from apps.audit.models import AuditLog
        from apps.audit.utils import log_action

        log_action(
            action="CELERY_ACTION",
            actor=None,
            target_obj=vendor,
            request=None,
            before={},
            after={"source": "celery"},
        )
        entry = AuditLog.objects.filter(action="CELERY_ACTION").first()
        assert entry is not None
        assert entry.actor is None
        assert entry.actor_label == ""
