"""
AirAd — tests/test_governance_tasks.py

Regression tests for governance Celery tasks and API RBAC:
  - expire_temporary_suspensions task (spec §8.2)
  - purge_deleted_user_data task (spec §8.1)
  - purge_old_analytics_events task (spec §8.1)
  - deprecate_unused_tags task (spec §5.1)
  - Governance API endpoints RBAC enforcement
"""
from __future__ import annotations

import uuid
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import AdminRole, AdminUser
from apps.governance.models import EnforcementAction, VendorSuspension
from tests.factories import AdminUserFactory, VendorFactory


def make_auth_client(api_client, role: str):
    user = AdminUserFactory(role=role)
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return api_client, user


# ---------------------------------------------------------------------------
# Celery Tasks
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestExpireTemporarySuspensions:
    def test_lifts_expired_suspension(self, vendor, super_admin_user):
        from apps.governance.tasks import expire_temporary_suspensions
        s = VendorSuspension.objects.create(
            vendor=vendor, action=EnforcementAction.TEMPORARY_SUSPENSION,
            reason="Test", issued_by=super_admin_user,
            suspension_ends_at=timezone.now() - timedelta(hours=1),
            is_active=True,
        )
        expire_temporary_suspensions.apply()
        s.refresh_from_db()
        assert s.is_active is False

    def test_keeps_future_suspension_active(self, vendor, super_admin_user):
        from apps.governance.tasks import expire_temporary_suspensions
        s = VendorSuspension.objects.create(
            vendor=vendor, action=EnforcementAction.TEMPORARY_SUSPENSION,
            reason="Test", issued_by=super_admin_user,
            suspension_ends_at=timezone.now() + timedelta(days=5),
            is_active=True,
        )
        expire_temporary_suspensions.apply()
        s.refresh_from_db()
        assert s.is_active is True

    def test_ignores_non_temporary_suspensions(self, vendor, super_admin_user):
        from apps.governance.tasks import expire_temporary_suspensions
        s = VendorSuspension.objects.create(
            vendor=vendor, action=EnforcementAction.WARNING,
            reason="Test", issued_by=super_admin_user,
            suspension_ends_at=timezone.now() - timedelta(hours=1),
            is_active=True,
        )
        expire_temporary_suspensions.apply()
        s.refresh_from_db()
        assert s.is_active is True

    def test_ignores_already_inactive(self, vendor, super_admin_user):
        from apps.governance.tasks import expire_temporary_suspensions
        s = VendorSuspension.objects.create(
            vendor=vendor, action=EnforcementAction.TEMPORARY_SUSPENSION,
            reason="Test", issued_by=super_admin_user,
            suspension_ends_at=timezone.now() - timedelta(hours=1),
            is_active=False,
        )
        expire_temporary_suspensions.apply()
        s.refresh_from_db()
        assert s.is_active is False

    def test_lifts_multiple_expired(self, super_admin_user):
        from apps.governance.tasks import expire_temporary_suspensions
        vendors = [VendorFactory() for _ in range(3)]
        suspensions = [
            VendorSuspension.objects.create(
                vendor=v, action=EnforcementAction.TEMPORARY_SUSPENSION,
                reason="Test", issued_by=super_admin_user,
                suspension_ends_at=timezone.now() - timedelta(hours=1),
                is_active=True,
            )
            for v in vendors
        ]
        expire_temporary_suspensions.apply()
        for s in suspensions:
            s.refresh_from_db()
            assert s.is_active is False


@pytest.mark.django_db
class TestPurgeDeletedUserData:
    def test_removes_old_anonymised_account(self):
        from apps.governance.tasks import purge_deleted_user_data
        old_user = AdminUser.objects.create_user(
            email=f"deleted-{uuid.uuid4().hex}@purged.airaad.internal",
            password=None, full_name="Deleted",
            role=AdminRole.DATA_ENTRY, is_active=False,
        )
        AdminUser.objects.filter(id=old_user.id).update(
            updated_at=timezone.now() - timedelta(days=31)
        )
        purge_deleted_user_data.apply()
        assert not AdminUser.objects.filter(id=old_user.id).exists()

    def test_keeps_recently_deleted_account(self):
        from apps.governance.tasks import purge_deleted_user_data
        recent = AdminUser.objects.create_user(
            email=f"deleted-{uuid.uuid4().hex}@purged.airaad.internal",
            password=None, full_name="Deleted",
            role=AdminRole.DATA_ENTRY, is_active=False,
        )
        purge_deleted_user_data.apply()
        assert AdminUser.objects.filter(id=recent.id).exists()

    def test_does_not_purge_active_users(self):
        from apps.governance.tasks import purge_deleted_user_data
        active = AdminUserFactory(role=AdminRole.DATA_ENTRY)
        purge_deleted_user_data.apply()
        assert AdminUser.objects.filter(id=active.id).exists()

    def test_does_not_purge_non_anonymised_inactive(self):
        from apps.governance.tasks import purge_deleted_user_data
        user = AdminUserFactory(role=AdminRole.DATA_ENTRY)
        AdminUser.objects.filter(id=user.id).update(
            is_active=False,
            updated_at=timezone.now() - timedelta(days=31),
        )
        purge_deleted_user_data.apply()
        assert AdminUser.objects.filter(id=user.id).exists()


@pytest.mark.django_db
class TestPurgeOldAnalyticsEvents:
    def test_deletes_events_older_than_90_days(self):
        from apps.analytics.models import AnalyticsEvent, EventType
        from apps.governance.tasks import purge_old_analytics_events
        ev = AnalyticsEvent.objects.create(event_type=EventType.VENDOR_VIEW)
        AnalyticsEvent.objects.filter(id=ev.id).update(
            created_at=timezone.now() - timedelta(days=91)
        )
        purge_old_analytics_events.apply()
        assert not AnalyticsEvent.objects.filter(id=ev.id).exists()

    def test_keeps_events_within_90_days(self):
        from apps.analytics.models import AnalyticsEvent, EventType
        from apps.governance.tasks import purge_old_analytics_events
        ev = AnalyticsEvent.objects.create(event_type=EventType.VENDOR_VIEW)
        purge_old_analytics_events.apply()
        assert AnalyticsEvent.objects.filter(id=ev.id).exists()

    def test_keeps_events_exactly_at_89_days(self):
        from apps.analytics.models import AnalyticsEvent, EventType
        from apps.governance.tasks import purge_old_analytics_events
        ev = AnalyticsEvent.objects.create(event_type=EventType.VENDOR_VIEW)
        AnalyticsEvent.objects.filter(id=ev.id).update(
            created_at=timezone.now() - timedelta(days=89)
        )
        purge_old_analytics_events.apply()
        assert AnalyticsEvent.objects.filter(id=ev.id).exists()

    def test_deletes_multiple_old_events(self):
        from apps.analytics.models import AnalyticsEvent, EventType
        from apps.governance.tasks import purge_old_analytics_events
        ids = []
        for _ in range(3):
            ev = AnalyticsEvent.objects.create(event_type=EventType.VENDOR_VIEW)
            AnalyticsEvent.objects.filter(id=ev.id).update(
                created_at=timezone.now() - timedelta(days=91)
            )
            ids.append(ev.id)
        purge_old_analytics_events.apply()
        assert AnalyticsEvent.objects.filter(id__in=ids).count() == 0


@pytest.mark.django_db
class TestDeprecateUnusedTags:
    def test_deactivates_zero_usage_category_tag(self):
        from apps.governance.tasks import deprecate_unused_tags
        from apps.tags.models import Tag, TagType
        tag = Tag.objects.create(
            name="Unused Cat", slug=f"unused-cat-{uuid.uuid4().hex[:6]}",
            tag_type=TagType.CATEGORY, is_active=True,
        )
        VendorFactory()
        deprecate_unused_tags.apply()
        tag.refresh_from_db()
        assert tag.is_active is False

    def test_deactivates_zero_usage_intent_tag(self):
        from apps.governance.tasks import deprecate_unused_tags
        from apps.tags.models import Tag, TagType
        tag = Tag.objects.create(
            name="Unused Intent", slug=f"unused-intent-{uuid.uuid4().hex[:6]}",
            tag_type=TagType.INTENT, is_active=True,
        )
        VendorFactory()
        deprecate_unused_tags.apply()
        tag.refresh_from_db()
        assert tag.is_active is False

    def test_skips_system_tags(self):
        from apps.governance.tasks import deprecate_unused_tags
        from apps.tags.models import Tag, TagType
        tag = Tag.objects.create(
            name="SysTag", slug=f"sys-{uuid.uuid4().hex[:6]}",
            tag_type=TagType.SYSTEM, is_active=True,
        )
        VendorFactory()
        deprecate_unused_tags.apply()
        tag.refresh_from_db()
        assert tag.is_active is True

    def test_skips_promotion_tags(self):
        from apps.governance.tasks import deprecate_unused_tags
        from apps.tags.models import Tag, TagType
        tag = Tag.objects.create(
            name="PromoTag", slug=f"promo-{uuid.uuid4().hex[:6]}",
            tag_type=TagType.PROMOTION, is_active=True,
        )
        VendorFactory()
        deprecate_unused_tags.apply()
        tag.refresh_from_db()
        assert tag.is_active is True

    def test_skips_time_tags(self):
        from apps.governance.tasks import deprecate_unused_tags
        from apps.tags.models import Tag, TagType
        tag = Tag.objects.create(
            name="TimeTag", slug=f"time-{uuid.uuid4().hex[:6]}",
            tag_type=TagType.TIME, is_active=True,
        )
        VendorFactory()
        deprecate_unused_tags.apply()
        tag.refresh_from_db()
        assert tag.is_active is True

    def test_no_vendors_skips_gracefully(self):
        from apps.governance.tasks import deprecate_unused_tags
        from apps.tags.models import Tag, TagType
        from apps.vendors.models import Vendor
        Vendor.objects.all().delete()
        tag = Tag.objects.create(
            name="Unused2", slug=f"unused2-{uuid.uuid4().hex[:6]}",
            tag_type=TagType.CATEGORY, is_active=True,
        )
        deprecate_unused_tags.apply()
        tag.refresh_from_db()
        assert tag.is_active is True

    def test_keeps_tag_assigned_to_vendor(self):
        from apps.governance.tasks import deprecate_unused_tags
        from apps.tags.models import Tag, TagType
        tag = Tag.objects.create(
            name="Used Tag", slug=f"used-{uuid.uuid4().hex[:6]}",
            tag_type=TagType.CATEGORY, is_active=True,
        )
        vendor = VendorFactory()
        vendor.tags.add(tag)
        deprecate_unused_tags.apply()
        tag.refresh_from_db()
        assert tag.is_active is True


# ---------------------------------------------------------------------------
# Governance API Endpoints — RBAC
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestGovernanceAPIRBAC:
    """All governance endpoints require SUPER_ADMIN or OPERATIONS_MANAGER."""

    # Fraud score endpoints
    def test_fraud_score_list_forbidden_for_data_entry(self, api_client):
        client, _ = make_auth_client(api_client, AdminRole.DATA_ENTRY)
        assert client.get("/api/v1/governance/fraud-scores/").status_code == status.HTTP_403_FORBIDDEN

    def test_fraud_score_list_forbidden_for_analyst(self, api_client):
        client, _ = make_auth_client(api_client, AdminRole.ANALYST)
        assert client.get("/api/v1/governance/fraud-scores/").status_code == status.HTTP_403_FORBIDDEN

    def test_fraud_score_list_allowed_for_super_admin(self, api_client):
        client, _ = make_auth_client(api_client, AdminRole.SUPER_ADMIN)
        assert client.get("/api/v1/governance/fraud-scores/").status_code == status.HTTP_200_OK

    def test_fraud_score_list_allowed_for_operations_manager(self, api_client):
        client, _ = make_auth_client(api_client, AdminRole.OPERATIONS_MANAGER)
        assert client.get("/api/v1/governance/fraud-scores/").status_code == status.HTTP_200_OK

    def test_fraud_score_list_unauthenticated_returns_401(self, api_client):
        api_client.credentials()
        assert api_client.get("/api/v1/governance/fraud-scores/").status_code == status.HTTP_401_UNAUTHORIZED

    # Blacklist endpoints
    def test_blacklist_list_forbidden_for_qa_reviewer(self, api_client):
        client, _ = make_auth_client(api_client, AdminRole.QA_REVIEWER)
        assert client.get("/api/v1/governance/blacklist/").status_code == status.HTTP_403_FORBIDDEN

    def test_blacklist_list_allowed_for_super_admin(self, api_client):
        client, _ = make_auth_client(api_client, AdminRole.SUPER_ADMIN)
        assert client.get("/api/v1/governance/blacklist/").status_code == status.HTTP_200_OK

    def test_blacklist_list_allowed_for_operations_manager(self, api_client):
        client, _ = make_auth_client(api_client, AdminRole.OPERATIONS_MANAGER)
        assert client.get("/api/v1/governance/blacklist/").status_code == status.HTTP_200_OK

    def test_blacklist_create_forbidden_for_field_agent(self, api_client):
        client, _ = make_auth_client(api_client, AdminRole.FIELD_AGENT)
        payload = {"blacklist_type": "PHONE_NUMBER", "value": "+923001234567", "reason": "Test"}
        assert client.post("/api/v1/governance/blacklist/", payload, format="json").status_code == status.HTTP_403_FORBIDDEN

    def test_blacklist_create_allowed_for_super_admin(self, api_client):
        client, _ = make_auth_client(api_client, AdminRole.SUPER_ADMIN)
        payload = {"blacklist_type": "PHONE_NUMBER", "value": f"+9230099{uuid.uuid4().int % 100000:05d}", "reason": "Test"}
        assert client.post("/api/v1/governance/blacklist/", payload, format="json").status_code == status.HTTP_201_CREATED

    # Suspension endpoints
    def test_suspension_list_forbidden_for_support(self, api_client):
        client, _ = make_auth_client(api_client, AdminRole.SUPPORT)
        assert client.get("/api/v1/governance/suspensions/").status_code == status.HTTP_403_FORBIDDEN

    def test_suspension_list_allowed_for_operations_manager(self, api_client):
        client, _ = make_auth_client(api_client, AdminRole.OPERATIONS_MANAGER)
        assert client.get("/api/v1/governance/suspensions/").status_code == status.HTTP_200_OK

    def test_suspension_create_allowed_for_super_admin(self, api_client, vendor):
        client, _ = make_auth_client(api_client, AdminRole.SUPER_ADMIN)
        payload = {"vendor_id": str(vendor.id), "action": "WARNING", "reason": "Test violation"}
        assert client.post("/api/v1/governance/suspensions/", payload, format="json").status_code == status.HTTP_201_CREATED

    def test_suspension_create_forbidden_for_city_manager(self, api_client, vendor):
        client, _ = make_auth_client(api_client, AdminRole.CITY_MANAGER)
        payload = {"vendor_id": str(vendor.id), "action": "WARNING", "reason": "Test"}
        assert client.post("/api/v1/governance/suspensions/", payload, format="json").status_code == status.HTTP_403_FORBIDDEN

    # ToS endpoints
    def test_tos_accept_allowed_for_any_authenticated(self, api_client, vendor):
        client, _ = make_auth_client(api_client, AdminRole.DATA_ENTRY)
        payload = {"vendor_id": str(vendor.id), "accepted_by_email": "v@test.com", "tos_version": "1.0"}
        assert client.post("/api/v1/governance/tos/accept/", payload, format="json").status_code == status.HTTP_201_CREATED

    def test_tos_history_forbidden_for_data_entry(self, api_client, vendor):
        client, _ = make_auth_client(api_client, AdminRole.DATA_ENTRY)
        assert client.get(f"/api/v1/governance/tos/{vendor.id}/").status_code == status.HTTP_403_FORBIDDEN

    def test_tos_history_allowed_for_operations_manager(self, api_client, vendor):
        client, _ = make_auth_client(api_client, AdminRole.OPERATIONS_MANAGER)
        assert client.get(f"/api/v1/governance/tos/{vendor.id}/").status_code == status.HTTP_200_OK

    # Consent endpoints
    def test_consent_get_allowed_for_any_authenticated(self, api_client):
        client, _ = make_auth_client(api_client, AdminRole.FIELD_AGENT)
        assert client.get("/api/v1/governance/consent/").status_code == status.HTTP_200_OK

    def test_consent_post_allowed_for_any_authenticated(self, api_client):
        client, _ = make_auth_client(api_client, AdminRole.SUPPORT)
        payload = {"category": "GPS_TRACKING", "granted": True}
        assert client.post("/api/v1/governance/consent/", payload, format="json").status_code == status.HTTP_201_CREATED

    def test_consent_unauthenticated_returns_401(self, api_client):
        api_client.credentials()
        assert api_client.get("/api/v1/governance/consent/").status_code == status.HTTP_401_UNAUTHORIZED

    # Appeal endpoint (any authenticated)
    def test_appeal_file_allowed_for_any_authenticated(self, api_client, vendor):
        from apps.governance.services import issue_enforcement_action
        ops_user = AdminUserFactory(role=AdminRole.OPERATIONS_MANAGER)
        suspension = issue_enforcement_action(
            vendor_id=str(vendor.id), action=EnforcementAction.WARNING,
            reason="Test", actor=ops_user, request=None,
        )
        client, _ = make_auth_client(api_client, AdminRole.SUPPORT)
        assert client.post(f"/api/v1/governance/suspensions/{suspension.id}/appeal/").status_code == status.HTTP_200_OK

    def test_appeal_review_forbidden_for_support(self, api_client, vendor):
        from apps.governance.services import file_appeal, issue_enforcement_action
        ops_user = AdminUserFactory(role=AdminRole.OPERATIONS_MANAGER)
        suspension = issue_enforcement_action(
            vendor_id=str(vendor.id), action=EnforcementAction.WARNING,
            reason="Test", actor=ops_user, request=None,
        )
        file_appeal(str(suspension.id), actor=ops_user, request=None)
        client, _ = make_auth_client(api_client, AdminRole.SUPPORT)
        payload = {"decision": "APPROVED", "notes": "OK"}
        assert client.post(f"/api/v1/governance/suspensions/{suspension.id}/appeal/review/", payload, format="json").status_code == status.HTTP_403_FORBIDDEN

    def test_appeal_review_allowed_for_operations_manager(self, api_client, vendor):
        from apps.governance.services import file_appeal, issue_enforcement_action
        ops_user = AdminUserFactory(role=AdminRole.OPERATIONS_MANAGER)
        suspension = issue_enforcement_action(
            vendor_id=str(vendor.id), action=EnforcementAction.WARNING,
            reason="Test", actor=ops_user, request=None,
        )
        file_appeal(str(suspension.id), actor=ops_user, request=None)
        client, _ = make_auth_client(api_client, AdminRole.OPERATIONS_MANAGER)
        payload = {"decision": "REJECTED", "notes": "Not valid"}
        assert client.post(f"/api/v1/governance/suspensions/{suspension.id}/appeal/review/", payload, format="json").status_code == status.HTTP_200_OK


# ---------------------------------------------------------------------------
# §2.2 — Updated RBAC matrix for existing endpoints
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestUpdatedRBACMatrix:
    """Verify the updated permission sets for existing endpoints per spec §2.2."""

    def test_operations_manager_can_access_audit_log(self, api_client):
        client, _ = make_auth_client(api_client, AdminRole.OPERATIONS_MANAGER)
        assert client.get("/api/v1/audit/").status_code == status.HTTP_200_OK

    def test_content_moderator_cannot_access_audit_log(self, api_client):
        client, _ = make_auth_client(api_client, AdminRole.CONTENT_MODERATOR)
        assert client.get("/api/v1/audit/").status_code == status.HTTP_403_FORBIDDEN

    def test_analytics_observer_can_access_kpis(self, api_client):
        client, _ = make_auth_client(api_client, AdminRole.ANALYTICS_OBSERVER)
        assert client.get("/api/v1/analytics/kpis/").status_code == status.HTTP_200_OK

    def test_data_quality_analyst_can_access_kpis(self, api_client):
        client, _ = make_auth_client(api_client, AdminRole.DATA_QUALITY_ANALYST)
        assert client.get("/api/v1/analytics/kpis/").status_code == status.HTTP_200_OK

    def test_content_moderator_cannot_access_kpis(self, api_client):
        client, _ = make_auth_client(api_client, AdminRole.CONTENT_MODERATOR)
        assert client.get("/api/v1/analytics/kpis/").status_code == status.HTTP_403_FORBIDDEN

    def test_data_quality_analyst_can_create_tag(self, api_client):
        client, _ = make_auth_client(api_client, AdminRole.DATA_QUALITY_ANALYST)
        payload = {"name": f"DQA Tag {uuid.uuid4().hex[:6]}", "slug": f"dqa-{uuid.uuid4().hex[:6]}", "tag_type": "CATEGORY", "display_label": "DQA", "is_active": True}
        resp = client.post("/api/v1/tags/", payload, format="json")
        assert resp.status_code in (status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST)

    def test_analytics_observer_cannot_create_tag(self, api_client):
        client, _ = make_auth_client(api_client, AdminRole.ANALYTICS_OBSERVER)
        payload = {"name": "Observer Tag", "slug": f"obs-{uuid.uuid4().hex[:6]}", "tag_type": "CATEGORY", "display_label": "Obs", "is_active": True}
        assert client.post("/api/v1/tags/", payload, format="json").status_code == status.HTTP_403_FORBIDDEN

    def test_operations_manager_can_delete_vendor(self, api_client, vendor):
        client, _ = make_auth_client(api_client, AdminRole.OPERATIONS_MANAGER)
        assert client.delete(f"/api/v1/vendors/{vendor.id}/").status_code == status.HTTP_204_NO_CONTENT

    def test_data_entry_cannot_delete_vendor(self, api_client, vendor):
        client, _ = make_auth_client(api_client, AdminRole.DATA_ENTRY)
        assert client.delete(f"/api/v1/vendors/{vendor.id}/").status_code == status.HTTP_403_FORBIDDEN

    def test_field_agent_cannot_delete_vendor(self, api_client, vendor):
        client, _ = make_auth_client(api_client, AdminRole.FIELD_AGENT)
        assert client.delete(f"/api/v1/vendors/{vendor.id}/").status_code == status.HTTP_403_FORBIDDEN
