# AirAd Backend — Python Expert Task List: PHASE B
## Source: `plans/01_BACKEND_PLAN.md` — Section 3 (Phase B Extensions)
### Priority Order: Correctness → Type Safety → Performance → Style
### Prerequisite: Phase A quality gate fully passed (`docker-compose up` + `pytest --cov-fail-under=80` all green)

---

## Overview

Phase B extends Phase A — it is NOT a new project. New apps are added and existing models are extended via new migrations. No existing migration is modified.

**Sessions:**
| Session | Goal |
|---|---|
| B-S1 | New models + Customer/Vendor auth |
| B-S2 | Vendor APIs + Discovery/Search engine |
| B-S3 | Discount engine + Tag auto-assignment |
| B-S4 | Admin APIs + Analytics + Subscriptions |

---

## SESSION B-S1 — New Models + Customer/Vendor Auth

### TASK-B01 — New models: `Discount`, `AnalyticsEvent`, `VoiceBotConfig`, `SubscriptionPackage`
**Plan Ref:** Section 3.1 | **Priority:** CRITICAL | **Effort:** M

#### `Discount` (extend `apps/vendors/`)
- [ ] `id(UUID)`, `vendor(FK Vendor)`, `title`, `discount_type(TextChoices)`, `value(DecimalField)`, `applies_to`, `item_description`
- [ ] `start_time(DateTimeField)`, `end_time(DateTimeField)`, `is_recurring(BooleanField)`, `recurrence_days(JSONField default=list)`
- [ ] `is_active` as computed `@property` — not a DB field
- [ ] `min_order_value(DecimalField null=True)`, `created_at(auto_now_add)`

> ⚠️ `JSONField(default=list)` — callable, not `[]` (mutable default rule). `is_active` must be a `@property` — never a stored field that can go stale.

#### `AnalyticsEvent` (extend `apps/analytics/`)
- [ ] `event_type(CharField)`, `vendor(FK null=True)`, `user(FK null=True)`, `session_id(CharField)`
- [ ] `latitude(FloatField null=True)`, `longitude(FloatField null=True)`, `device_type`, `search_query`, `timestamp(DateTimeField)`
- [ ] **CRITICAL: Partitioned by month** — use `migrations.RunSQL` for partition DDL
- [ ] Partition SQL: `CREATE TABLE analytics_event_YYYY_MM PARTITION OF analytics_analyticsevent FOR VALUES FROM (...) TO (...)`

> ⚠️ High-volume table — monthly partitioning is non-negotiable. Never use `models.Index` for partition — use raw SQL migration.

#### `VoiceBotConfig` (one-to-one with `Vendor`)
- [ ] `vendor(OneToOneField Vendor)`, `menu_items(JSONField default=list)`, `opening_hours_summary(TextField)`, `delivery_info(TextField)`
- [ ] `discount_summary(TextField)` — auto-updated when active discounts change
- [ ] `custom_qa_pairs(JSONField default=list)`

#### `SubscriptionPackage`
- [ ] `level(TextChoices: SILVER/GOLD/DIAMOND/PLATINUM)`, `price_monthly(DecimalField)`, `max_videos(IntegerField)`, `daily_happy_hours_allowed(IntegerField)`
- [ ] `has_voice_bot(BooleanField)`, `has_sponsored_windows(BooleanField)`, `has_predictive_reports(BooleanField)`
- [ ] `visibility_boost_weight(FloatField)` — used in ranking formula
- [ ] Seeded via `seed_data` management command — **NOT** via migration

---

### TASK-B02 — `Vendor` model extensions (new migration)
**Plan Ref:** Section 3.1 | **Priority:** CRITICAL | **Effort:** S

- [ ] New migration only — never alter existing Phase A migration
- [ ] New fields: `owner(FK Customer null=True)`, `is_claimed(BooleanField default=False)`, `claimed_at(DateTimeField null=True)`
- [ ] `logo(ImageField → S3)`, `cover_photo(ImageField → S3)`
- [ ] `offers_delivery(BooleanField default=False)`, `offers_pickup(BooleanField default=False)`, `is_verified(BooleanField default=False)`
- [ ] `subscription_level(TextChoices: SILVER/GOLD/DIAMOND/PLATINUM, default=SILVER)`
- [ ] `subscription_valid_until(DateTimeField null=True)`
- [ ] `total_views(PositiveIntegerField default=0)`, `total_profile_taps(PositiveIntegerField default=0)`
- [ ] `location_pending_review(BooleanField default=False)`

> ⚠️ `ImageField` stores S3 key via `django-storages` — presigned URL generated on read, never stored as public URL.

---

### TASK-B03 — Customer & Vendor OTP Auth
**Plan Ref:** Section 3.2 | **Priority:** CRITICAL | **Effort:** M

**Models:**
- [ ] `Customer(AbstractBaseUser)`: `id(UUID)`, `phone_number_encrypted(BinaryField)`, `name`, `email(null=True)`, `device_token`, `is_active`, `created_at`
- [ ] `OTPRecord`: `id(UUID)`, `phone_hash(CharField)`, `otp_hash(CharField)`, `expires_at`, `is_used(BooleanField)`, `created_at`

> ⚠️ Never store OTP or phone number in plaintext. Phone: AES-256-GCM. OTP: hashed (SHA-256) before storage.

**Services (`apps/accounts/services.py` extended):**
- [ ] `send_otp(phone: str) -> OTPRecord` — Twilio abstracted as `SMSService` class (not direct API call)
- [ ] `verify_otp(phone: str, otp: str) -> Customer` — validates hash, checks expiry, marks `is_used=True`
- [ ] All OTP events → `AuditLog`

**Endpoints:**
- [ ] `POST /api/v1/auth/customer/send-otp/`
- [ ] `POST /api/v1/auth/customer/verify-otp/` → create/login, return JWT
- [ ] `POST /api/v1/auth/customer/profile/` → update name, email, device_token
- [ ] `POST /api/v1/auth/vendor/send-otp/`
- [ ] `POST /api/v1/auth/vendor/verify-otp/`
- [ ] `POST /api/v1/auth/vendor/verify-email/`
- [ ] `GET /api/v1/auth/vendor/me/`

**JWT payload must include:** `user_type(CUSTOMER/VENDOR/ADMIN)`, `role`

---

## SESSION B-S2 — Vendor APIs + Discovery/Search Engine

### TASK-B04 — `RankingService` class
**Plan Ref:** Section 3.3 | **Priority:** CRITICAL | **Effort:** L

- [ ] Pure class in `apps/discovery/services.py` — independently unit-testable, no Django view dependencies
- [ ] `rank(vendors: QuerySet, query: str, user_lat: float, user_lng: float) -> list[Vendor]`

**Ranking algorithm (in order):**
1. [ ] `ST_DWithin` filter FIRST — never score vendors outside radius
2. [ ] Score = Text match (30%) + Distance (25%) + Active offer (15%) + Popularity last 30d (15%) + Subscription (15%)
3. [ ] Subscription scores: `SILVER=0.0`, `GOLD=0.3`, `DIAMOND=0.6`, `PLATINUM=1.0`
4. [ ] Paid tier cannot override distance score by more than 30% — enforced in scoring formula

> ⚠️ `RankingService` must be a pure class — no side effects, no DB writes. All inputs typed, return type annotated. Independently testable with mock data.

**Endpoints:**
- [ ] `GET /api/v1/discovery/search/?lat&lng&radius&q&tags`
- [ ] `GET /api/v1/discovery/nearby/?lat&lng&radius`
- [ ] `GET /api/v1/tags/discovery/?tag_types=...`
- [ ] `POST /api/v1/discovery/voice-search/` — rule-based NLP, **no ML dependencies**
- [ ] `POST /api/v1/vendors/{slug}/voice-query/` — rule-based `VoiceBotConfig` matching

---

### TASK-B05 — Voice Search (rule-based NLP)
**Plan Ref:** Section 3.3 | **Priority:** HIGH | **Effort:** M

- [ ] `VoiceSearchService` in `apps/discovery/services.py`
- [ ] Rule-based parsing only — no ML, no external NLP APIs
- [ ] Extracts: intent (find/open/discount), category keywords, location keywords, time context
- [ ] Maps parsed intent to `RankingService` query parameters
- [ ] `VoiceBotConfig` matching: keyword lookup in `menu_items` and `custom_qa_pairs`
- [ ] Full type hints + Google-style docstrings

---

## SESSION B-S3 — Discount Engine + Tag Auto-Assignment

### TASK-B06 — Discount & Promotion Engine (Celery tasks)
**Plan Ref:** Section 3.4 | **Priority:** HIGH | **Effort:** M

**`discount_scheduler` (every 1 minute):**
- [ ] `@shared_task` — auto-activate discounts where `start_time <= now() < end_time`
- [ ] Auto-deactivate discounts where `end_time <= now()`
- [ ] On activate: trigger `TagAutoAssigner.assign_promotion_tag(vendor)`
- [ ] On deactivate: trigger `TagAutoAssigner.remove_promotion_tag(vendor)`
- [ ] All state changes → `AuditLog`

**`subscription_expiry_check` (daily midnight UTC):**
- [ ] Downgrade expired subscriptions → `SILVER`
- [ ] Send reminder at 7 days before expiry
- [ ] Send reminder at 1 day before expiry
- [ ] All downgrades → `AuditLog`

> ⚠️ Both tasks already registered in `celery_app.py` Beat schedule from Phase A — only implement the task body here.

---

### TASK-B07 — `TagAutoAssigner` service
**Plan Ref:** Section 3.4 | **Priority:** HIGH | **Effort:** M

- [ ] `TagAutoAssigner` class in `apps/tags/services.py`
- [ ] `assign_promotion_tag(vendor: Vendor) -> None` — assigns `PROMOTION` tag when discount activates
- [ ] `remove_promotion_tag(vendor: Vendor) -> None` — removes `PROMOTION` tag when discount deactivates
- [ ] `assign_time_tags_globally() -> None` — hourly cron: assign/remove `TIME` tags based on current time
- [ ] `check_engagement_tags(vendor: Vendor) -> None`:
  - Vendor reaches 10 views/week → assign `SYSTEM:NewVendorBoost`
  - Top 10% taps in area → assign `SYSTEM:HighEngagement`
- [ ] All tag assignments/removals → `AuditLog`
- [ ] `SYSTEM` tags assigned only by `TagAutoAssigner` — API cannot create/edit/delete them

> ⚠️ `SYSTEM` tag protection enforced in `tags/services.py` — raise `PermissionDenied` if API attempts to mutate a SYSTEM tag.

---

## SESSION B-S4 — Admin APIs + Analytics + Subscriptions

### TASK-B08 — `vendor_has_feature()` — Subscription Feature Gating
**Plan Ref:** Section 3.5 | **Priority:** CRITICAL | **Effort:** S

- [ ] Implement `vendor_has_feature(vendor: Vendor, feature: str) -> bool` in `core/utils.py` (stub was created in Phase A)
- [ ] Feature names (exact strings): `HAPPY_HOUR`, `VOICE_BOT`, `SPONSORED_WINDOW`, `TIME_HEATMAP`, `PREDICTIVE_RECOMMENDATIONS`, `EXTRA_REELS`
- [ ] Tier matrix:

| Feature | SILVER | GOLD | DIAMOND | PLATINUM |
|---|---|---|---|---|
| `EXTRA_REELS` (max videos) | 1 | 3 | 6 | unlimited |
| `HAPPY_HOUR` (per day) | 0 | 1 | 3 | unlimited |
| `VOICE_BOT` | ❌ | basic | dynamic | advanced |
| `SPONSORED_WINDOW` | ❌ | ❌ | ✅ | ✅ |
| `TIME_HEATMAP` | ❌ | ❌ | ✅ | ✅ |
| `PREDICTIVE_RECOMMENDATIONS` | ❌ | ❌ | ❌ | ✅ |

- [ ] **This is the ONLY gate mechanism** — no scattered `if vendor.subscription_level ==` anywhere in codebase
- [ ] All premium API endpoints call `vendor_has_feature()` — return 403 if `False`
- [ ] Full type hints + Google-style docstring

---

### TASK-B09 — Vendor Analytics APIs
**Plan Ref:** Section 3.6 | **Priority:** HIGH | **Effort:** M

**Permission:** `IsVendorOwner` custom permission class

- [ ] `GET /api/v1/vendors/{id}/analytics/summary/` — all tiers
- [ ] `GET /api/v1/vendors/{id}/analytics/reels/` — all tiers
- [ ] `GET /api/v1/vendors/{id}/analytics/discounts/` — all tiers
- [ ] `GET /api/v1/vendors/{id}/analytics/time-heatmap/` — Diamond+ only (`vendor_has_feature(vendor, 'TIME_HEATMAP')`)
- [ ] `GET /api/v1/vendors/{id}/analytics/recommendations/` — Platinum only, rule-based (no ML)

**Rule:** NEVER block API request to record analytics. Always dispatch Celery task → return response immediately.

> ⚠️ Analytics recording is fire-and-forget via Celery. The API response must never wait for the analytics write to complete.

---

### TASK-B10 — Admin Platform Analytics APIs
**Plan Ref:** Section 3.6 | **Priority:** HIGH | **Effort:** M

**Permission:** `RolePermission.for_roles(AdminRole.SUPER_ADMIN, AdminRole.ANALYTICS_MANAGER)` (or equivalent roles)

- [ ] `GET /api/v1/admin/analytics/platform-overview/`
- [ ] `GET /api/v1/admin/analytics/area-heatmap/{city_id}/`
- [ ] `GET /api/v1/admin/analytics/search-terms/`

All endpoints:
- [ ] Paginated via `StandardResultsPagination`
- [ ] `@extend_schema` decorated
- [ ] Zero business logic in views — delegated to `analytics/services.py`

---

### TASK-B11 — Admin Management APIs
**Plan Ref:** Section 3.7 | **Priority:** HIGH | **Effort:** M

- [ ] `POST /api/v1/admin/vendors/{id}/verify/`
- [ ] `PATCH /api/v1/admin/vendors/{id}/suspend/`
- [ ] `POST /api/v1/admin/vendors/{id}/approve-claim/`
- [ ] `POST /api/v1/admin/vendors/{id}/reject-claim/`
- [ ] `POST /api/v1/admin/vendors/{id}/approve-location/`
- [ ] `POST /api/v1/admin/vendors/{id}/reject-location/`
- [ ] `POST /api/v1/admin/geo/cities/{id}/launch/`
- [ ] `POST /api/v1/admin/tags/bulk-assign/`

All endpoints:
- [ ] `RolePermission.for_roles(...)` on every view
- [ ] All mutations → `AuditLog` entry
- [ ] All logic in `services.py` — views are thin dispatchers
- [ ] `@extend_schema` decorated

---

## Phase B Testing Requirements

### TASK-B12 — Phase B tests
**Priority:** CRITICAL | **Effort:** L

**New factories (extend `tests/factories.py`):**
- [ ] `CustomerFactory`, `DiscountFactory`, `AnalyticsEventFactory`, `VoiceBotConfigFactory`, `SubscriptionPackageFactory`

**Unit tests:**
- [ ] `TestRankingService`: scoring formula, subscription cap (paid tier cannot override distance >30%), `ST_DWithin` filter first
- [ ] `TestVendorHasFeature`: all 6 features × all 4 tiers — 24 test cases
- [ ] `TestTagAutoAssigner`: PROMOTION tag assign/remove, SYSTEM tag protection
- [ ] `TestDiscountIsActive`: computed `@property` returns correct value based on `start_time`/`end_time`
- [ ] `TestOTPFlow`: send → verify → JWT issued, expired OTP rejected, used OTP rejected
- [ ] `TestAnalyticsFireAndForget`: analytics endpoint returns 200 before Celery task completes

**Integration tests:**
- [ ] Customer OTP auth full flow (mocked Twilio)
- [ ] Vendor OTP auth full flow (mocked Twilio)
- [ ] Discovery search with ranking — parametrized by subscription tier
- [ ] Subscription expiry → downgrade → feature gate blocks access
- [ ] `vendor_has_feature` gate: 403 for insufficient tier, 200 for sufficient tier

**Celery task tests:**
- [ ] `discount_scheduler`: activates/deactivates correct discounts, assigns/removes PROMOTION tags
- [ ] `subscription_expiry_check`: downgrades expired, sends reminders at 7d and 1d
- [ ] `hourly_tag_assignment`: TIME tags assigned/removed correctly

---

## Phase B Quality Gate Checklist

Before marking Phase B complete:

- [ ] `vendor_has_feature()` is the ONLY subscription gate — no scattered `if subscription_level ==`
- [ ] `RankingService` is a pure class — independently unit-testable
- [ ] `ST_DWithin` filter applied BEFORE scoring in discovery
- [ ] Paid tier subscription score cannot override distance by more than 30%
- [ ] Voice search is rule-based — zero ML dependencies
- [ ] OTP: phone stored AES-256-GCM, OTP stored SHA-256 hashed
- [ ] Analytics recording never blocks API response — always fire-and-forget via Celery
- [ ] `AnalyticsEvent` table partitioned by month
- [ ] `SYSTEM` tags cannot be created/edited/deleted via API
- [ ] All new endpoints: `RolePermission.for_roles(...)` or `IsVendorOwner`
- [ ] All new mutations: `AuditLog` entry
- [ ] All new services: full type hints + Google-style docstrings
- [ ] No bare `except` anywhere in Phase B code
- [ ] No mutable default arguments anywhere in Phase B code
- [ ] Coverage ≥ 80% maintained after Phase B additions
- [ ] No existing Phase A migration modified — only new migrations added
- [ ] `SubscriptionPackage` seeded via management command — not migration
