"""
AirAd — tests/test_governance_models.py

Regression tests for governance models and services:
  - New AdminRole values (spec §2.1)
  - FraudScore model + add_fraud_signal service (spec §6.2)
  - Blacklist model + add/lift services (spec §6.3)
  - VendorSuspension + enforcement ladder + appeal (spec §8.2)
  - VendorToSAcceptance + record_tos_acceptance (spec §8.3)
  - ConsentRecord + record_consent / get_current_consent (spec §8.1)
"""
from __future__ import annotations

import uuid
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.accounts.models import AdminRole, AdminUser
from apps.governance.models import (
    AppealStatus,
    BlacklistType,
    ConsentCategory,
    ConsentRecord,
    EnforcementAction,
    FRAUD_SCORE_AUTO_SUSPEND_THRESHOLD,
    FRAUD_SCORE_MANUAL_REVIEW_THRESHOLD,
    FraudScore,
    FraudSignal,
    VendorSuspension,
    VendorToSAcceptance,
)
from apps.governance.services import (
    add_fraud_signal,
    add_to_blacklist,
    file_appeal,
    get_current_consent,
    get_fraud_score,
    is_blacklisted,
    issue_enforcement_action,
    lift_blacklist_entry,
    process_appeal,
    record_consent,
    record_tos_acceptance,
)
from tests.factories import AdminUserFactory


# ---------------------------------------------------------------------------
# §2.1 — New AdminRole values
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestNewAdminRoles:
    def test_all_11_roles_present(self):
        assert len(AdminRole.values) == 11

    def test_operations_manager_value(self):
        assert AdminRole.OPERATIONS_MANAGER == "OPERATIONS_MANAGER"

    def test_content_moderator_value(self):
        assert AdminRole.CONTENT_MODERATOR == "CONTENT_MODERATOR"

    def test_data_quality_analyst_value(self):
        assert AdminRole.DATA_QUALITY_ANALYST == "DATA_QUALITY_ANALYST"

    def test_analytics_observer_value(self):
        assert AdminRole.ANALYTICS_OBSERVER == "ANALYTICS_OBSERVER"

    def test_operations_manager_persists_to_db(self):
        user = AdminUserFactory(role=AdminRole.OPERATIONS_MANAGER)
        assert AdminUser.objects.filter(id=user.id, role="OPERATIONS_MANAGER").exists()

    def test_data_quality_analyst_persists_to_db(self):
        user = AdminUserFactory(role=AdminRole.DATA_QUALITY_ANALYST)
        assert AdminUser.objects.filter(id=user.id, role="DATA_QUALITY_ANALYST").exists()

    def test_analytics_observer_persists_to_db(self):
        user = AdminUserFactory(role=AdminRole.ANALYTICS_OBSERVER)
        assert AdminUser.objects.filter(id=user.id, role="ANALYTICS_OBSERVER").exists()

    def test_content_moderator_persists_to_db(self):
        user = AdminUserFactory(role=AdminRole.CONTENT_MODERATOR)
        assert AdminUser.objects.filter(id=user.id, role="CONTENT_MODERATOR").exists()


# ---------------------------------------------------------------------------
# §6.2 — Fraud Score
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestFraudScoreModel:
    def test_needs_manual_review_at_threshold(self, vendor):
        fs = FraudScore.objects.create(vendor=vendor, score=FRAUD_SCORE_MANUAL_REVIEW_THRESHOLD)
        assert fs.needs_manual_review is True
        assert fs.should_auto_suspend is False

    def test_should_auto_suspend_at_threshold(self, vendor):
        fs = FraudScore.objects.create(vendor=vendor, score=FRAUD_SCORE_AUTO_SUSPEND_THRESHOLD)
        assert fs.should_auto_suspend is True
        assert fs.needs_manual_review is False

    def test_normal_score_no_flags(self, vendor):
        fs = FraudScore.objects.create(vendor=vendor, score=1)
        assert fs.needs_manual_review is False
        assert fs.should_auto_suspend is False

    def test_gps_anomaly_adds_2(self, vendor, super_admin_user):
        fs = add_fraud_signal(
            signal=FraudSignal.GPS_ANOMALY, actor=super_admin_user,
            request=None, vendor_id=str(vendor.id), reason="Water body",
        )
        assert fs.score == 2
        assert fs.signals[0]["signal"] == FraudSignal.GPS_ANOMALY
        assert fs.signals[0]["score_delta"] == 2
        assert "ts" in fs.signals[0]

    def test_blacklisted_phone_adds_3(self, vendor, super_admin_user):
        fs = add_fraud_signal(signal=FraudSignal.BLACKLISTED_PHONE, actor=super_admin_user, request=None, vendor_id=str(vendor.id))
        assert fs.score == 3

    def test_user_report_adds_1(self, vendor, super_admin_user):
        fs = add_fraud_signal(signal=FraudSignal.USER_REPORT, actor=super_admin_user, request=None, vendor_id=str(vendor.id))
        assert fs.score == 1

    def test_multi_claim_adds_1(self, vendor, super_admin_user):
        fs = add_fraud_signal(signal=FraudSignal.MULTI_CLAIM_SAME_DEVICE, actor=super_admin_user, request=None, vendor_id=str(vendor.id))
        assert fs.score == 1

    def test_excessive_promotions_adds_1(self, vendor, super_admin_user):
        fs = add_fraud_signal(signal=FraudSignal.EXCESSIVE_PROMOTIONS, actor=super_admin_user, request=None, vendor_id=str(vendor.id))
        assert fs.score == 1

    def test_duplicate_claim_adds_2(self, vendor, super_admin_user):
        fs = add_fraud_signal(signal=FraudSignal.DUPLICATE_CLAIM, actor=super_admin_user, request=None, vendor_id=str(vendor.id))
        assert fs.score == 2

    def test_auto_suspend_triggered_at_threshold(self, vendor, super_admin_user):
        add_fraud_signal(signal=FraudSignal.BLACKLISTED_PHONE, actor=super_admin_user, request=None, vendor_id=str(vendor.id))
        add_fraud_signal(signal=FraudSignal.GPS_ANOMALY, actor=super_admin_user, request=None, vendor_id=str(vendor.id))
        fs = add_fraud_signal(signal=FraudSignal.DUPLICATE_CLAIM, actor=super_admin_user, request=None, vendor_id=str(vendor.id))
        assert fs.is_auto_suspended is True
        assert fs.score >= FRAUD_SCORE_AUTO_SUSPEND_THRESHOLD

    def test_auto_suspend_flags_vendor_qc(self, vendor, super_admin_user):
        from apps.vendors.models import QCStatus
        add_fraud_signal(signal=FraudSignal.BLACKLISTED_PHONE, actor=super_admin_user, request=None, vendor_id=str(vendor.id))
        add_fraud_signal(signal=FraudSignal.GPS_ANOMALY, actor=super_admin_user, request=None, vendor_id=str(vendor.id))
        add_fraud_signal(signal=FraudSignal.DUPLICATE_CLAIM, actor=super_admin_user, request=None, vendor_id=str(vendor.id))
        vendor.refresh_from_db()
        assert vendor.qc_status == QCStatus.FLAGGED

    def test_invalid_signal_raises(self, super_admin_user):
        with pytest.raises(ValueError, match="Invalid fraud signal"):
            add_fraud_signal(signal="FAKE_SIGNAL", actor=super_admin_user, request=None)

    def test_get_fraud_score_none_for_unknown(self):
        assert get_fraud_score(str(uuid.uuid4())) is None

    def test_get_fraud_score_returns_existing(self, vendor, super_admin_user):
        add_fraud_signal(signal=FraudSignal.USER_REPORT, actor=super_admin_user, request=None, vendor_id=str(vendor.id))
        fs = get_fraud_score(str(vendor.id))
        assert fs is not None and fs.score == 1

    def test_multiple_signals_accumulate(self, vendor, super_admin_user):
        add_fraud_signal(signal=FraudSignal.USER_REPORT, actor=super_admin_user, request=None, vendor_id=str(vendor.id))
        add_fraud_signal(signal=FraudSignal.EXCESSIVE_PROMOTIONS, actor=super_admin_user, request=None, vendor_id=str(vendor.id))
        fs = get_fraud_score(str(vendor.id))
        assert fs.score == 2 and len(fs.signals) == 2


# ---------------------------------------------------------------------------
# §6.3 — Blacklist
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestBlacklist:
    def test_add_phone(self, super_admin_user):
        e = add_to_blacklist(blacklist_type=BlacklistType.PHONE_NUMBER, value="+923001234567", reason="Fraud", actor=super_admin_user, request=None)
        assert e.is_active is True and e.blacklist_type == BlacklistType.PHONE_NUMBER

    def test_add_device_id(self, super_admin_user):
        e = add_to_blacklist(blacklist_type=BlacklistType.DEVICE_ID, value="dev-xyz", reason="Suspicious", actor=super_admin_user, request=None)
        assert e.blacklist_type == BlacklistType.DEVICE_ID

    def test_add_gps_coordinate(self, super_admin_user):
        e = add_to_blacklist(blacklist_type=BlacklistType.GPS_COORDINATE, value="24.8,67.0", reason="Water", actor=super_admin_user, request=None)
        assert e.blacklist_type == BlacklistType.GPS_COORDINATE

    def test_is_blacklisted_true(self, super_admin_user):
        add_to_blacklist(blacklist_type=BlacklistType.PHONE_NUMBER, value="+923009999999", reason="Test", actor=super_admin_user, request=None)
        assert is_blacklisted(BlacklistType.PHONE_NUMBER, "+923009999999") is True

    def test_is_blacklisted_false_for_unknown(self):
        assert is_blacklisted(BlacklistType.PHONE_NUMBER, "+923001111111") is False

    def test_lift_sets_inactive(self, super_admin_user):
        e = add_to_blacklist(blacklist_type=BlacklistType.DEVICE_ID, value="dev-abc", reason="Test", actor=super_admin_user, request=None)
        lifted = lift_blacklist_entry(str(e.id), actor=super_admin_user, request=None)
        assert lifted.is_active is False

    def test_is_blacklisted_false_after_lift(self, super_admin_user):
        e = add_to_blacklist(blacklist_type=BlacklistType.DEVICE_ID, value="dev-lift", reason="Test", actor=super_admin_user, request=None)
        lift_blacklist_entry(str(e.id), actor=super_admin_user, request=None)
        assert is_blacklisted(BlacklistType.DEVICE_ID, "dev-lift") is False

    def test_lift_already_inactive_raises(self, super_admin_user):
        e = add_to_blacklist(blacklist_type=BlacklistType.GPS_COORDINATE, value="24.8,67.1", reason="Test", actor=super_admin_user, request=None)
        lift_blacklist_entry(str(e.id), actor=super_admin_user, request=None)
        with pytest.raises(ValueError, match="already inactive"):
            lift_blacklist_entry(str(e.id), actor=super_admin_user, request=None)

    def test_lift_nonexistent_raises(self, super_admin_user):
        with pytest.raises(ValueError, match="not found"):
            lift_blacklist_entry(str(uuid.uuid4()), actor=super_admin_user, request=None)

    def test_empty_reason_raises(self, super_admin_user):
        with pytest.raises(ValueError, match="Reason is required"):
            add_to_blacklist(blacklist_type=BlacklistType.PHONE_NUMBER, value="+923001234568", reason="", actor=super_admin_user, request=None)

    def test_invalid_type_raises(self, super_admin_user):
        with pytest.raises(ValueError, match="Invalid blacklist_type"):
            add_to_blacklist(blacklist_type="FAKE", value="test", reason="Test", actor=super_admin_user, request=None)

    def test_reactivate_lifted_entry(self, super_admin_user):
        phone = f"+9230088{uuid.uuid4().hex[:5]}"
        e = add_to_blacklist(blacklist_type=BlacklistType.PHONE_NUMBER, value=phone, reason="First", actor=super_admin_user, request=None)
        lift_blacklist_entry(str(e.id), actor=super_admin_user, request=None)
        r = add_to_blacklist(blacklist_type=BlacklistType.PHONE_NUMBER, value=phone, reason="Second", actor=super_admin_user, request=None)
        assert r.is_active is True


# ---------------------------------------------------------------------------
# §8.2 — Vendor Suspension
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestVendorSuspension:
    def test_issue_warning(self, vendor, super_admin_user):
        s = issue_enforcement_action(vendor_id=str(vendor.id), action=EnforcementAction.WARNING, reason="First", actor=super_admin_user, request=None)
        assert s.action == EnforcementAction.WARNING and s.is_active is True and s.suspension_ends_at is None

    def test_issue_content_removal_with_policy_ref(self, vendor, super_admin_user):
        s = issue_enforcement_action(vendor_id=str(vendor.id), action=EnforcementAction.CONTENT_REMOVAL, reason="Fake promo", actor=super_admin_user, request=None, policy_reference="§4.3")
        assert s.policy_reference == "§4.3"

    def test_temporary_suspension_sets_end_date(self, vendor, super_admin_user):
        s = issue_enforcement_action(vendor_id=str(vendor.id), action=EnforcementAction.TEMPORARY_SUSPENSION, reason="Repeat", actor=super_admin_user, request=None, suspension_days=7)
        assert s.suspension_ends_at is not None
        assert 6 <= (s.suspension_ends_at - timezone.now()).days <= 7

    def test_permanent_ban_flags_vendor_qc(self, vendor, super_admin_user):
        from apps.vendors.models import QCStatus
        issue_enforcement_action(vendor_id=str(vendor.id), action=EnforcementAction.PERMANENT_BAN, reason="Fraud", actor=super_admin_user, request=None)
        vendor.refresh_from_db()
        assert vendor.qc_status == QCStatus.FLAGGED

    def test_invalid_action_raises(self, vendor, super_admin_user):
        with pytest.raises(ValueError, match="Invalid enforcement action"):
            issue_enforcement_action(vendor_id=str(vendor.id), action="FAKE", reason="Test", actor=super_admin_user, request=None)

    def test_empty_reason_raises(self, vendor, super_admin_user):
        with pytest.raises(ValueError, match="Reason is required"):
            issue_enforcement_action(vendor_id=str(vendor.id), action=EnforcementAction.WARNING, reason="", actor=super_admin_user, request=None)

    def test_unknown_vendor_raises(self, super_admin_user):
        with pytest.raises(ValueError, match="not found"):
            issue_enforcement_action(vendor_id=str(uuid.uuid4()), action=EnforcementAction.WARNING, reason="Test", actor=super_admin_user, request=None)

    def test_file_appeal_sets_pending(self, vendor, super_admin_user):
        s = issue_enforcement_action(vendor_id=str(vendor.id), action=EnforcementAction.WARNING, reason="Test", actor=super_admin_user, request=None)
        updated = file_appeal(str(s.id), actor=super_admin_user, request=None)
        assert updated.appeal_status == AppealStatus.PENDING

    def test_file_appeal_twice_raises(self, vendor, super_admin_user):
        s = issue_enforcement_action(vendor_id=str(vendor.id), action=EnforcementAction.WARNING, reason="Test", actor=super_admin_user, request=None)
        file_appeal(str(s.id), actor=super_admin_user, request=None)
        with pytest.raises(ValueError, match="already been filed"):
            file_appeal(str(s.id), actor=super_admin_user, request=None)

    def test_file_appeal_expired_window_raises(self, vendor, super_admin_user):
        s = issue_enforcement_action(vendor_id=str(vendor.id), action=EnforcementAction.WARNING, reason="Test", actor=super_admin_user, request=None)
        VendorSuspension.objects.filter(id=s.id).update(created_at=timezone.now() - timedelta(days=8))
        s.refresh_from_db()
        with pytest.raises(ValueError, match="Appeal window has expired"):
            file_appeal(str(s.id), actor=super_admin_user, request=None)

    def test_file_appeal_nonexistent_raises(self, super_admin_user):
        with pytest.raises(ValueError, match="not found"):
            file_appeal(str(uuid.uuid4()), actor=super_admin_user, request=None)

    def test_process_appeal_approved_lifts(self, vendor, super_admin_user):
        s = issue_enforcement_action(vendor_id=str(vendor.id), action=EnforcementAction.TEMPORARY_SUSPENSION, reason="Test", actor=super_admin_user, request=None)
        file_appeal(str(s.id), actor=super_admin_user, request=None)
        result = process_appeal(str(s.id), decision=AppealStatus.APPROVED, reviewer=super_admin_user, request=None, notes="Proof provided")
        assert result.appeal_status == AppealStatus.APPROVED and result.is_active is False

    def test_process_appeal_approved_restores_vendor_qc(self, vendor, super_admin_user):
        from apps.vendors.models import QCStatus
        s = issue_enforcement_action(vendor_id=str(vendor.id), action=EnforcementAction.TEMPORARY_SUSPENSION, reason="Test", actor=super_admin_user, request=None)
        file_appeal(str(s.id), actor=super_admin_user, request=None)
        process_appeal(str(s.id), decision=AppealStatus.APPROVED, reviewer=super_admin_user, request=None)
        vendor.refresh_from_db()
        assert vendor.qc_status == QCStatus.PENDING

    def test_process_appeal_rejected_keeps_active(self, vendor, super_admin_user):
        s = issue_enforcement_action(vendor_id=str(vendor.id), action=EnforcementAction.WARNING, reason="Test", actor=super_admin_user, request=None)
        file_appeal(str(s.id), actor=super_admin_user, request=None)
        result = process_appeal(str(s.id), decision=AppealStatus.REJECTED, reviewer=super_admin_user, request=None)
        assert result.appeal_status == AppealStatus.REJECTED and result.is_active is True

    def test_process_appeal_no_pending_raises(self, vendor, super_admin_user):
        s = issue_enforcement_action(vendor_id=str(vendor.id), action=EnforcementAction.WARNING, reason="Test", actor=super_admin_user, request=None)
        with pytest.raises(ValueError, match="No pending appeal"):
            process_appeal(str(s.id), decision=AppealStatus.APPROVED, reviewer=super_admin_user, request=None)

    def test_process_appeal_invalid_decision_raises(self, vendor, super_admin_user):
        s = issue_enforcement_action(vendor_id=str(vendor.id), action=EnforcementAction.WARNING, reason="Test", actor=super_admin_user, request=None)
        file_appeal(str(s.id), actor=super_admin_user, request=None)
        with pytest.raises(ValueError, match="Decision must be"):
            process_appeal(str(s.id), decision="MAYBE", reviewer=super_admin_user, request=None)

    def test_process_appeal_nonexistent_raises(self, super_admin_user):
        with pytest.raises(ValueError, match="not found"):
            process_appeal(str(uuid.uuid4()), decision=AppealStatus.APPROVED, reviewer=super_admin_user, request=None)


# ---------------------------------------------------------------------------
# §8.3 — Vendor ToS Acceptance
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestVendorToSAcceptance:
    def test_record_acceptance(self, vendor, super_admin_user):
        a = record_tos_acceptance(vendor_id=str(vendor.id), accepted_by_email="v@test.com", actor=super_admin_user, request=None, tos_version="1.0")
        assert a.vendor_id == vendor.id and a.tos_version == "1.0" and a.accepted_by_email == "v@test.com"

    def test_unknown_vendor_raises(self, super_admin_user):
        with pytest.raises(ValueError, match="not found"):
            record_tos_acceptance(vendor_id=str(uuid.uuid4()), accepted_by_email="v@test.com", actor=super_admin_user, request=None)

    def test_multiple_acceptances_allowed(self, vendor, super_admin_user):
        record_tos_acceptance(vendor_id=str(vendor.id), accepted_by_email="a@test.com", actor=super_admin_user, request=None, tos_version="1.0")
        record_tos_acceptance(vendor_id=str(vendor.id), accepted_by_email="b@test.com", actor=super_admin_user, request=None, tos_version="1.1")
        assert VendorToSAcceptance.objects.filter(vendor=vendor).count() == 2

    def test_default_tos_version_is_1_0(self, vendor, super_admin_user):
        a = record_tos_acceptance(vendor_id=str(vendor.id), accepted_by_email="v@test.com", actor=super_admin_user, request=None)
        assert a.tos_version == "1.0"


# ---------------------------------------------------------------------------
# §8.1 — Consent Management
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestConsentRecord:
    def test_opt_in(self, super_admin_user):
        r = record_consent(user_id=str(super_admin_user.id), category=ConsentCategory.GPS_TRACKING, granted=True, actor=super_admin_user, request=None)
        assert r.granted is True and r.category == ConsentCategory.GPS_TRACKING

    def test_opt_out(self, super_admin_user):
        r = record_consent(user_id=str(super_admin_user.id), category=ConsentCategory.BEHAVIORAL_ANALYTICS, granted=False, actor=super_admin_user, request=None)
        assert r.granted is False

    def test_marketing_notifications_category(self, super_admin_user):
        r = record_consent(user_id=str(super_admin_user.id), category=ConsentCategory.MARKETING_NOTIFICATIONS, granted=True, actor=super_admin_user, request=None)
        assert r.category == ConsentCategory.MARKETING_NOTIFICATIONS

    def test_get_current_returns_latest(self, super_admin_user):
        record_consent(user_id=str(super_admin_user.id), category=ConsentCategory.GPS_TRACKING, granted=True, actor=super_admin_user, request=None)
        record_consent(user_id=str(super_admin_user.id), category=ConsentCategory.GPS_TRACKING, granted=False, actor=super_admin_user, request=None)
        assert get_current_consent(str(super_admin_user.id))[ConsentCategory.GPS_TRACKING] is False

    def test_get_current_multiple_categories(self, super_admin_user):
        record_consent(user_id=str(super_admin_user.id), category=ConsentCategory.GPS_TRACKING, granted=True, actor=super_admin_user, request=None)
        record_consent(user_id=str(super_admin_user.id), category=ConsentCategory.MARKETING_NOTIFICATIONS, granted=False, actor=super_admin_user, request=None)
        consent = get_current_consent(str(super_admin_user.id))
        assert consent[ConsentCategory.GPS_TRACKING] is True
        assert consent[ConsentCategory.MARKETING_NOTIFICATIONS] is False

    def test_get_current_empty_dict_for_new_user(self, super_admin_user):
        assert get_current_consent(str(super_admin_user.id)) == {}

    def test_invalid_category_raises(self, super_admin_user):
        with pytest.raises(ValueError, match="Invalid consent category"):
            record_consent(user_id=str(super_admin_user.id), category="FAKE", granted=True, actor=super_admin_user, request=None)

    def test_unknown_user_raises(self, super_admin_user):
        with pytest.raises(ValueError, match="not found"):
            record_consent(user_id=str(uuid.uuid4()), category=ConsentCategory.GPS_TRACKING, granted=True, actor=super_admin_user, request=None)

    def test_immutable_new_record_per_change(self, super_admin_user):
        record_consent(user_id=str(super_admin_user.id), category=ConsentCategory.GPS_TRACKING, granted=True, actor=super_admin_user, request=None)
        record_consent(user_id=str(super_admin_user.id), category=ConsentCategory.GPS_TRACKING, granted=False, actor=super_admin_user, request=None)
        assert ConsentRecord.objects.filter(user=super_admin_user, category=ConsentCategory.GPS_TRACKING).count() == 2
