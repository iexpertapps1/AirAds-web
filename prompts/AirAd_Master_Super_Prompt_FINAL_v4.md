# AirAd — Master Super Prompt for Windsurf IDE
### Complete Build Instructions: Django Backend · React Web Portal · Flutter Mobile App
### UNIFIED EDITION — v1 (Full Platform) + v2 (Post-Audit, All 30 Gaps Resolved)
> **How to Use This Document:** Each section below is a **standalone prompt block**. Copy the entire block into Windsurf's prompt input when working on that specific module. Do NOT send all sections at once. Work module by module, section by section. Windsurf is intelligent — these prompts describe intent and architecture, not code syntax.
>
> **Build Sequence:** Start with Phase A (Data Collection Portal) to seed the platform database, then move to Phase B (Full Platform: Vendor APIs + React Portal + Flutter App).

---

## 📋 TABLE OF CONTENTS

### PHASE A — DATA COLLECTION PORTAL (Build First)
*(Internal admin tool to seed and verify vendor data before public launch)*

1. [Project Foundation & Global Rules — Phase A](#1-project-foundation--global-rules--phase-a)
   - 1.1 Project Identity & Phase A Context
   - 1.2 Absolute Prohibitions & Authority Documents
2. [★ Airbnb Design Language System — Non-Negotiable Frontend Standards](#2-airbnb-design-language-system)
   - 2.1 DLS Principles, Color System & Typography
   - 2.2 DLS Components & Interaction Patterns
3. [Django Backend — Data Collection Portal Layer](#3-django-backend--data-collection-portal)
   - 3.1 Project Setup & Architecture (Portal)
   - 3.2 Django Models — Complete ORM Schema
   - 3.3 Core Utilities (Encryption · Geo · Middleware · Pagination)
   - 3.4 Authentication, RBAC & Account Lockout (7 Admin Roles)
   - 3.5 Geographic Hierarchy APIs
   - 3.6 Tag System APIs
   - 3.7 Vendor Management & QC APIs
   - 3.8 Import & CSV Processing Engine
   - 3.9 Field Operations APIs
   - 3.10 QA, GPS Drift & Duplicate Detection
   - 3.11 Analytics & KPI Reporting (Portal)
   - 3.12 Audit Trail System
   - 3.13 Health Check & OpenAPI
4. [React Admin Portal — Internal Data Collection Dashboard](#4-react-admin-portal)
   - 4.1 Design System Setup & DLS Token File
   - 4.2 Geographic Management Section
   - 4.3 Tag & Category Management Section
   - 4.4 Vendor Oversight & QC Queue
   - 4.5 Import Management Section
   - 4.6 Field Operations Section
   - 4.7 QA Dashboard
   - 4.8 Platform Health Dashboard
   - 4.9 Audit Log Viewer
   - 4.10 User & Role Management
5. [Infrastructure & DevOps](#5-infrastructure--devops)
   - 5.1 Docker & Docker Compose
   - 5.2 CI/CD Pipeline (GitHub Actions)
   - 5.3 Environment Configuration
   - 5.4 Seed Data Management Command
6. [Test Suite — Portal](#6-test-suite--portal)
   - 6.1 Unit Tests — Business Rules R1–R10
   - 6.2 RBAC Integration Tests
   - 6.3 Security & Lockout Tests
   - 6.4 Celery Task Tests
7. [Quality Gate & Execution Order — Phase A](#7-quality-gate--execution-order--phase-a)
8. [Phase-2 Exclusion List (Portal Build)](#8-phase-2-exclusion-list-portal-build)

---

### PHASE B — FULL PLATFORM (Build After Phase A)
*(Public-facing: Discovery APIs + Vendor Dashboard + Flutter App)*

9.  [Project Foundation & Global Rules — Phase B](#9-project-foundation--global-rules--phase-b)
10. [Django Backend — Full Platform APIs](#10-django-backend--full-platform-apis)
    - 10.1 Additional Models (Discount, Analytics Event, Voice Bot Config, Subscription)
    - 10.2 Authentication — Customer & Vendor (OTP + Email)
    - 10.3 Vendor Module APIs (Public + Vendor-Authenticated)
    - 10.4 Discovery & Search APIs (Geospatial + Ranking Engine)
    - 10.5 Discount & Promotion Engine (Auto-activation via Celery)
    - 10.6 Tag Discovery & Auto-Assignment APIs
    - 10.7 Admin Management APIs (Geographic + Vendor + Claims)
    - 10.8 Analytics & Reporting APIs (Vendor + Admin)
    - 10.9 Subscription & Package System
11. [React Web Portal — Vendor Dashboard](#11-react-web-portal--vendor-dashboard)
    - 11.1 Vendor Onboarding Wizard & Profile Setup
    - 11.2 Discount & Promotion Manager
    - 11.3 Analytics & Reports
    - 11.4 Voice Bot Setup
    - 11.5 Subscription Management
12. [Flutter Mobile App — Customer & Vendor Facing](#12-flutter-mobile-app)
    - 12.1 App Architecture & Setup
    - 12.2 Onboarding & Authentication
    - 12.3 Home / Discovery Screen
    - 12.4 Augmented Reality (AR) Camera View
    - 12.5 Map View
    - 12.6 Tag-Based Browsing
    - 12.7 Voice Search & Voice Bot
    - 12.8 Vendor Profile Screen
    - 12.9 Navigation & Turn-by-Turn Directions
    - 12.10 Vendor App — Claim & Setup Flow
    - 12.11 Vendor App — Discount Management
    - 12.12 Reel / Video Upload System
13. [Windsurf Session Execution Guide](#13-windsurf-session-execution-guide)
14. [Final Notes for Windsurf](#14-final-notes-for-windsurf)

---
---

# PHASE A — DATA COLLECTION PORTAL

---

# 1. PROJECT FOUNDATION & GLOBAL RULES — PHASE A

> **Send this section FIRST before any Phase A module. It sets the context for the internal data collection portal build.**

---

## PROMPT 1.1 — Project Identity & Phase A Context

```
You are building AirAd — a hyperlocal vendor discovery platform connecting nearby customers
with small vendors, street stalls, kiosks, and local shops in real time.

The core philosophy is "Nearby + Now" — the app always answers:
"What can I get RIGHT NOW, NEAR ME, with good value?"

PHASE A — WHAT YOU ARE BUILDING NOW:
The AirAd DATA COLLECTION PORTAL — an internal admin web application used by AirAd operations
staff to seed, verify, and manage the vendor database BEFORE the public platform launches.
This is NOT customer-facing, NOT vendor-facing.

The portal is built on two surfaces:
1. Django 5.x + DRF 3.15 (Python 3.12) — backend API and data layer
2. React 18 + TypeScript 5 — internal admin portal (desktop-first)

The portal's purpose: "Collect accurate, verified, geospatially precise vendor data at scale."
Every feature must serve data quality, operational efficiency, and admin governance.

Portal users (7 roles):
- SUPER_ADMIN: Full access, platform-wide controls, user management
- DATA_MANAGER: Import, edit, and verify vendor data
- QC_REVIEWER: Review GPS data, approve/reject vendors
- FIELD_AGENT: Submit field visit reports and photos
- CONTENT_MODERATOR: Manage tags and categories
- ANALYTICS_VIEWER: Read-only analytics access
- IMPORT_OPERATOR: Trigger and manage CSV import jobs

Phase A does NOT include: customer-facing features, vendor login, subscription management,
payment processing, Flutter app, AR, voice bot, or any public-facing discovery.

Global technical rules:
- All APIs: RESTful with consistent JSON envelope { success, data, message, errors }
- All timestamps: stored in UTC, displayed in local timezone
- All distances: calculated server-side via PostGIS (never manual lat/lng math)
- All phone numbers: encrypted at rest using AES-256-GCM
- All media/photos: go to S3-compatible storage — never the application server
- All business logic: lives in services.py — never in views.py
- Multi-city support: no hardcoded city or country references anywhere
```

---

## PROMPT 1.2 — Absolute Prohibitions & Authority Documents

```
AUTHORITY DOCUMENTS — Referenced for traceability only:
- [DOC-1]: AirAd_Data_Collection_and_Seed_Data.docx       → placed in /requirements/
- [DOC-2]: AirAd_Vendor_Functional_Document.md            → placed in /requirements/
- [DOC-3]: AirAd_End_User_Functional_Document.md          → placed in /requirements/
- [DOC-4]: AirAd_Admin_Operations_and_Governance_Document.md → placed in /requirements/
- [AUDIT]: AirAd_SDLC_Compliance_Audit_Report.md          → placed in /requirements/

CRITICAL INSTRUCTION FOR WINDSURF:
This Master Prompt IS the complete, self-contained specification.
If any referenced document above is not present in the current project context,
treat this Master Prompt as the SOLE source of truth.
NEVER infer, assume, or hallucinate content from document filenames or section references.
When a section says "reference [DOC-1] §3" — the actual required content is already
written inline in this prompt. No external document reading is required to proceed.

This consolidated Master Prompt supersedes all prior versions on any point of conflict.
All 30 audit gaps (G01–G30) from [AUDIT] are resolved in this document.

ABSOLUTE PROHIBITIONS — Violating any of these terminates the build:
- No TODO, pass, raise NotImplementedError, or stub code in any production code path
- No placeholder strings in any generated file (.env.example uses generation instructions)
- No npm run dev in any Docker or production context
- No source code volume mounts in production Docker Compose
- No raw UUID stored where a ForeignKey relationship is required
- No GPS drift calculation using degree × constant — use PostGIS ST_Distance exclusively
- No CSV file content passed as a string over the Celery broker — pass batch_id only
- No __call__ method on DRF permission classes — use the for_roles() class factory exclusively
- No separate JWT_REFRESH_SECRET_KEY — SimpleJWT uses one secret
- No psycopg2-binary in production requirements — use compiled psycopg2
- No django-guardian — custom RolePermission class factory is the sole RBAC mechanism
- No business logic in views — all domain logic lives in services.py per app
- No hardcoded hex colors in React components — CSS custom properties only
```

---
---

# 2. AIRBNB DESIGN LANGUAGE SYSTEM

> **Priority: CRITICAL. Send this section before ANY frontend module prompt. Every UI component MUST comply.**

---

## PROMPT 2.1 — DLS Principles, Color System & Typography

```
All frontend work (both Phase A portal and Phase B vendor dashboard) must follow the
Airbnb Design Language System (DLS).

DESIGN PRINCIPLES (Non-Negotiable):
- Unified: Same component library, tokens, and interaction patterns across all pages
- Universal: WCAG 2.1 AA minimum, keyboard navigation, screen reader labels everywhere
- Iconic: Whitespace, clear hierarchy, purposeful color — no gratuitous gradients or shadows
- Conversational: Form labels as plain-language questions, helpful error messages (never error codes)

COLOR SYSTEM — Apply as CSS custom properties in :root. NEVER hardcode hex values in components:

--color-rausch:    #FF5A5F   /* PRIMARY brand — ONLY for primary action buttons, max 1 per view */
--color-babu:      #00A699   /* SUCCESS — approved states, verified badges, success toasts */
--color-arches:    #FC642D   /* WARNING — pending review, attention needed */
--color-hof:       #484848   /* PRIMARY TEXT */
--color-foggy:     #767676   /* SECONDARY TEXT */
--color-white:     #FFFFFF   /* Card/surface background */
--color-grey-50:   #F7F7F7   /* PAGE BACKGROUND — never pure white for admin sessions */
--color-grey-200:  #EBEBEB   /* Card borders, dividers */
--color-grey-300:  #DDDDDD   /* Input borders default */
--color-grey-400:  #AAAAAA   /* Disabled elements */

Semantic colors (paired text + background):
--color-success-text:  #008A05;   --color-success-bg: #E8F5E9
--color-warning-text:  #C45300;   --color-warning-bg: #FFF3E0
--color-error-text:    #C13515;   --color-error-bg:   #FFEBEE
--color-info-text:     #0077C8;   --color-info-bg:    #E3F2FD

TYPOGRAPHY — Import DM Sans (Circular fallback):
Font stack: 'Circular', 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif
- Page hero titles:     32px / 700 weight / 1.25 line-height
- Section headings:     26px / 600 weight
- Card titles, modals:  22px / 600 weight
- Subsection titles:    18px / 600 weight
- Table column headers: 16px / 600 weight
- Primary body text:    16px / 400 weight / 1.60 line-height
- Table rows, UI text:  14px / 400 weight
- Meta, timestamps:     12px / 400 weight
- Form labels, badges:  13px / 500 weight
- Minimum font size:    11px

SPACING — 8px base grid ONLY. Never use arbitrary pixel values:
Allowed: 4px, 8px, 12px, 16px, 20px, 24px, 32px, 40px, 48px, 64px

LAYOUT STRUCTURE:
┌─────────────────────────────────────────────────────────────────┐
│  TOPBAR [Breadcrumb]              [Search]  [Notif]  [Avatar]   │  h: 64px
├──────────┬──────────────────────────────────────────────────────┤
│          │                                                       │
│ SIDEBAR  │  PAGE CONTENT AREA                                   │
│ 240px    │  max-width: 1280px · padding: 40px 32px              │
│ fixed    │  ┌────────────────────────────────────────────────┐  │
│          │  │ PAGE HEADER (title + subtitle + primary CTA)   │  │ h: 80px
│          │  ├────────────────────────────────────────────────┤  │
│          │  │ FILTERS BAR (search + dropdowns + count)       │  │ h: 56px
│          │  ├────────────────────────────────────────────────┤  │
│          │  │ MAIN CONTENT (table / cards / map / charts)    │  │
│          │  └────────────────────────────────────────────────┘  │
└──────────┴──────────────────────────────────────────────────────┘
Sidebar: 240px fixed, white bg, 1px right border --color-grey-200
```

---

## PROMPT 2.2 — DLS Components & Interaction Patterns

```
COMPONENT LIBRARY — Build these shared components BEFORE any page:

BUTTON:
- Primary (--color-rausch), Secondary (outlined), Destructive (error red), Ghost (text only)
- Never use red for anything other than primary action
- States: default, hover (8% darker), active (12% darker), disabled (40% opacity), loading (spinner)
- Height: 40px standard, 32px compact, 48px large

BADGE/STATUS CHIP:
- Success (Babu teal), Warning (Arches orange), Error (red), Info (blue), Neutral (grey)
- Always include an icon alongside color — never convey meaning through color alone
- Height: 24px, border-radius: 12px, font: 12px/500

TABLE:
- Header: 14px/600, --color-grey-50 background, 1px bottom border
- Row: 56px height, hover: --color-grey-50 background, 1px bottom border
- Sortable columns with sort indicator on hover
- Checkbox column: 48px for bulk selection
- Must include: empty state and skeleton loading (NEVER spinners for content areas)
- Pagination: 25 items default (matches backend StandardResultsPagination)

FORM COMPONENTS:
- Input height: 40px, border-radius: 8px, border: 1px solid --color-grey-300
- Focus ring: 2px solid --color-rausch, offset 2px
- Error state: red border + error message below with icon
- Label: above input, 13px/500, --color-hof
- Helper text: 12px, --color-foggy, below input
- Validation: plain-language errors, never error codes

MODAL/DRAWER:
- Overlay: rgba(0,0,0,0.5) backdrop-blur 4px
- Modal border-radius: 16px, padding: 32px
- Widths: 480px (confirmation), 640px (forms), 80vw (detail panels)
- Drawer: 640px from right
- Always trap focus inside (accessibility). Close via X button + ESC + backdrop

SIDEBAR NAVIGATION:
- Nav item height: 44px
- Border-radius: 0 100px 100px 0 (pill-right — Airbnb signature pattern)
- Default: text --color-foggy
- Hover: bg --color-grey-100
- Active: bg rgba(255,90,95,0.08), text --color-rausch, font-weight 600
- Section labels: 11px uppercase, letter-spacing 1px

EMPTY STATES — EVERY list/table MUST implement:
  [Line-art illustration, neutral colors]
  Heading: Clear, plain language
  Subheading: Why it's empty + what to do next
  Button: Primary CTA

TOAST NOTIFICATIONS: Top-right corner, auto-dismiss 4s, variants: success/error/warning/info.

ICONOGRAPHY: lucide-react ONLY. Stroke width: 1.5 (Airbnb signature). Never filled.
Sizes: 16px inline, 20px nav, 24px standalone, 32px empty states.

MOTION:
--duration-fast: 150ms; --duration-normal: 250ms;
--ease-standard: cubic-bezier(0.4, 0, 0.2, 1);
prefers-reduced-motion: reduce → disable ALL animations.

ACCESSIBILITY:
- WCAG AA contrast (4.5:1 body text, 3:1 large text)
- All interactive elements keyboard navigable (Tab, Enter, Escape, Space)
- Visible focus ring on all focusable elements
- aria-label on all icon-only buttons
- Screen reader labels on all tables (role, aria-sort, aria-label)
- Skip-to-main-content link as first focusable element
- Color-blind safe: never convey meaning through color alone
```

---
---

# 3. DJANGO BACKEND — DATA COLLECTION PORTAL

---

## PROMPT 3.1 — Project Setup & Architecture (Portal)

```
Set up the Django backend for the AirAd Data Collection Portal.

TECH STACK:
- Python 3.12 · Django 5.x · Django REST Framework 3.15
- PostgreSQL 16 + PostGIS (mandatory for all location queries)
- Redis (Celery broker + result backend)
- Celery 5.x + Celery Beat (scheduled tasks)
- SimpleJWT · drf-spectacular · django-storages + boto3 · django-environ
- factory_boy + pytest-django (testing)

PROJECT STRUCTURE:
airaad/
├── backend/
│   ├── config/
│   │   ├── settings/ (base.py, production.py, development.py, test.py)
│   │   ├── urls.py
│   │   └── asgi.py
│   ├── celery_app.py           # Celery config + task failure signal handler
│   ├── apps/
│   │   ├── accounts/           # AdminUser model, 7 roles, JWT auth, account lockout
│   │   ├── geo/                # Country, City, Area, Landmark models
│   │   ├── vendors/            # Vendor model + QC workflow
│   │   ├── tags/               # Tag taxonomy
│   │   ├── imports/            # CSV import engine, ImportBatch model
│   │   ├── field_ops/          # FieldVisit, FieldPhoto models
│   │   ├── qa/                 # GPS drift detection, duplicate scanning
│   │   ├── analytics/          # Platform KPI endpoints
│   │   └── audit/              # AuditLog model + middleware
│   └── core/
│       ├── encryption.py       # AES-256-GCM (phone numbers)
│       ├── geo_utils.py        # PostGIS ST_Distance (NO degree×constant)
│       ├── middleware.py       # RequestIDMiddleware (FIRST in MIDDLEWARE)
│       ├── pagination.py       # StandardResultsPagination (25 default)
│       ├── exceptions.py       # custom_exception_handler + normalised format
│       ├── storage.py          # S3 presigned URL helpers
│       ├── schemas.py          # BusinessHoursSchema (Pydantic)
│       └── utils.py            # get_client_ip, etc.
├── frontend/ (React portal)
├── docker-compose.yml
├── docker-compose.dev.yml
└── README.md

CRITICAL SETTINGS (base.py):
- ENGINE: django.contrib.gis.db.backends.postgis (GeoDjango required)
- CONN_MAX_AGE: 60 (connection pooling)
- CELERY_BEAT_SCHEDULE registered in code via setup_periodic_tasks() in celery_app.py
- SIMPLE_JWT: ACCESS_TOKEN_LIFETIME=15min, REFRESH_TOKEN_LIFETIME=7days, ROTATE_REFRESH_TOKENS=True
- RequestIDMiddleware must be FIRST middleware after SecurityMiddleware
- EXCEPTION_HANDLER: core.exceptions.custom_exception_handler
```

---

## PROMPT 3.2 — Django Models — Complete ORM Schema

```
Create all database models for the AirAd Data Collection Portal.

ACCOUNTS (apps/accounts/models.py):
AdminUser extends AbstractBaseUser. Fields: id (UUID PK), email (unique), full_name,
role (choices: SUPER_ADMIN, DATA_MANAGER, QC_REVIEWER, FIELD_AGENT, CONTENT_MODERATOR,
ANALYTICS_VIEWER, IMPORT_OPERATOR), is_active, failed_login_count (int default 0),
locked_until (datetime nullable), last_login_ip, created_at, updated_at.

GEOGRAPHIC (apps/geo/models.py):
- Country: id (UUID PK), name, code (ISO-2), is_active, created_at
- City: id (UUID PK), country (FK), name, slug, aliases (JSONField array), centroid (PointField),
  bounding_box (PolygonField nullable), is_active, display_order, created_at
- Area: id (UUID PK), city (FK), parent_area (FK self nullable), name, slug, aliases (JSONField),
  centroid (PointField nullable), is_active, created_at
- Landmark: id (UUID PK), area (FK), name, slug, aliases (JSONField), location (PointField),
  is_active, created_at
- ALL PointField columns: add GiST spatial index via migration RunSQL (NOT models.Index)

VENDOR (apps/vendors/models.py):
id (UUID PK), business_name, slug, description,
gps_point (PointField, GiST index via RunSQL migration),
address_text, city (FK), area (FK), landmark (FK nullable),
phone_number_encrypted (BinaryField — AES-256-GCM via core/encryption.py),
qc_status (choices: PENDING, APPROVED, REJECTED, NEEDS_REVIEW),
qc_reviewed_by (FK AdminUser nullable — NOT raw UUID), qc_reviewed_at, qc_notes,
data_source (choices: CSV_IMPORT, GOOGLE_PLACES, MANUAL_ENTRY, FIELD_AGENT),
is_deleted (boolean default False, db_index=True),
created_at (auto_now_add), updated_at (auto_now)
Indexes: (qc_status, is_deleted), (area, is_deleted), (data_source)

IMPORT BATCH (apps/imports/models.py):
id (UUID PK), file_key (S3 key — NEVER file content), status (QUEUED/PROCESSING/DONE/FAILED),
total_rows, processed_rows, error_count, error_log (JSONField, capped at 1000 entries),
created_by (FK AdminUser), created_at, updated_at

FIELD VISIT (apps/field_ops/models.py):
id (UUID PK), vendor (FK), agent (FK AdminUser), visited_at (datetime),
visit_notes (text), gps_confirmed_point (PointField nullable), created_at

FIELD PHOTO (apps/field_ops/models.py):
id (UUID PK), field_visit (FK), s3_key (CharField), caption, is_active (default True), uploaded_at
Presigned URLs generated on read — NEVER stored as public URLs.

AUDIT LOG (apps/audit/models.py):
id (UUID PK), action (CharField indexed), actor (FK AdminUser nullable SET_NULL),
actor_label (CharField — snapshot at action time), target_type (CharField),
target_id (UUID nullable), before_state (JSONField nullable), after_state (JSONField nullable),
request_id (CharField), ip_address (GenericIPAddressField nullable),
created_at (auto_now_add, indexed)
Indexes: (target_type, target_id), (actor, created_at)
IMMUTABLE — no updates, no deletes, ever.

BUSINESS HOURS:
Stored as JSONField on Vendor. Validated on write via Pydantic BusinessHoursSchema in core/schemas.py.
Schema: { "monday": {"open": "09:00", "close": "22:00", "closed": false}, ... }
```

---

## PROMPT 3.3 — Core Utilities

```
Build all shared core utilities in the core/ directory.

core/encryption.py — AES-256-GCM:
- encrypt(plaintext: str) -> bytes  |  decrypt(ciphertext: bytes) -> str
- Uses ENCRYPTION_KEY from env (32-byte base64-encoded)
- Empty string → empty bytes (no error). Randomised IV = different ciphertexts each time.

core/geo_utils.py — PostGIS only:
- calculate_drift_distance(point_a, point_b) -> float (metres)
  Uses ST_Distance with geography=True — NEVER degree × constant approximation
- find_nearby_vendors(center, radius_metres) -> QuerySet

core/middleware.py — RequestIDMiddleware:
- Generates UUID request ID per request, attaches as X-Request-ID response header
- Stores on request object for AuditLog. MUST be FIRST in MIDDLEWARE.

core/pagination.py — StandardResultsPagination:
- PAGE_SIZE = 25, max_page_size = 100

core/exceptions.py — custom_exception_handler:
- Wraps ALL DRF exceptions: { success: false, data: null, message, errors }

core/schemas.py — Pydantic:
- BusinessHoursSchema validates 7-day business hours JSON on write

core/storage.py — S3 helpers:
- generate_presigned_url(s3_key, expiry_seconds=3600) -> str
- upload_file_to_s3(file_obj, key_prefix) -> str (returns S3 key only)

All utilities must have unit tests in tests/unit/test_core.py.
```

---

## PROMPT 3.4 — Authentication, RBAC & Account Lockout

```
Build the complete authentication system with RBAC for all 7 admin roles.

RBAC PATTERN — for_roles() class factory (NO django-guardian, NO __call__ method):

class RolePermission(BasePermission):
    allowed_roles: tuple[AdminRole, ...]

    @classmethod
    def for_roles(cls, *roles):
        return type('DynamicRolePermission', (cls,), {'allowed_roles': roles})

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.role in self.allowed_roles)

Usage: permission_classes = [RolePermission.for_roles(AdminRole.SUPER_ADMIN, AdminRole.DATA_MANAGER)]

ROLE PERMISSION MATRIX (from [DOC-4] §2.2):
- SUPER_ADMIN: all endpoints
- DATA_MANAGER: vendors CRUD, imports, geo, tags
- QC_REVIEWER: vendor QC review, field ops read, GPS audit
- FIELD_AGENT: field visits CRUD, own photos only
- CONTENT_MODERATOR: tags CRUD, vendor tags
- ANALYTICS_VIEWER: analytics read-only
- IMPORT_OPERATOR: imports CRUD, import job triggers

ACCOUNT LOCKOUT [AUDIT G02]:
- Failed login: increment failed_login_count
- After 5 failures: set locked_until = now() + 30 minutes → return HTTP 429
- Successful login: reset failed_login_count = 0 and locked_until = None

JWT FLOW:
- POST /api/v1/auth/login/ — validates, checks lockout, returns access + refresh
- POST /api/v1/auth/refresh/ — rotates token, blacklists old
- POST /api/v1/auth/logout/ — blacklists refresh token
- Custom serializer adds role, full_name, email to claims. No separate JWT_REFRESH_SECRET_KEY.
All auth endpoints create AuditLog entries.
```

---

## PROMPT 3.5 — Geographic Hierarchy APIs

```
Build all APIs for the geographic data layer.

ENDPOINTS:
GET/POST  /api/v1/geo/countries/              — list + create (SUPER_ADMIN, DATA_MANAGER)
GET/PATCH /api/v1/geo/cities/?country={id}    — list with filter, update
POST      /api/v1/geo/cities/                 — create
GET/POST  /api/v1/geo/areas/?city={id}        — hierarchical list + create
GET/POST  /api/v1/geo/landmarks/?area={id}    — list + create
GET       /api/v1/geo/tree/?city={id}         — full nested tree: city→areas→landmarks

Also build city launch-readiness endpoint:
GET /api/v1/geo/cities/{id}/launch-readiness/ — checklist: areas created, vendors seeded (≥500),
  tags configured, vendors QC-approved (≥80%). Returns { ready: bool, checks: [...] }

BUSINESS RULES:
- Aliases field: JSON array, each alias non-empty string
- Slug: auto-generated from name on create, immutable after
- Landmark with < 3 aliases: flag in API response (voice search accuracy)
- GiST spatial index on all PointField columns via RunSQL migrations
- All mutations create AuditLog entries
- Roles: SUPER_ADMIN, DATA_MANAGER for writes; all roles for reads
```

---

## PROMPT 3.6 — Tag System APIs

```
Build the tag taxonomy system.

TAG TYPES: LOCATION, CATEGORY, INTENT, PROMOTION, TIME, SYSTEM
SYSTEM tags are auto-assigned by platform — admins cannot create/edit/delete them.

ENDPOINTS:
GET/POST   /api/v1/tags/                         — list (all) + create
GET/PATCH  /api/v1/tags/{id}/                    — detail + update
DELETE     /api/v1/tags/{id}/                    — soft delete (is_active=False only)
POST       /api/v1/vendors/{id}/tags/            — assign tag
DELETE     /api/v1/vendors/{id}/tags/{tag_id}/  — remove tag
GET        /api/v1/vendors/{id}/tags/            — list vendor's tags with assignment source

BUSINESS RULES:
- SYSTEM tags: cannot be created, edited, or deleted via API
- Tag slug: auto-generated from name, immutable
- Deleting tag: only marks is_active=False — vendor assignments preserved for audit
- CONTENT_MODERATOR: CATEGORY + INTENT tags only
- SUPER_ADMIN + DATA_MANAGER: all tag types
- All mutations create AuditLog entries
```

---

## PROMPT 3.7 — Vendor Management & QC APIs

```
Build the complete vendor management API layer.

CRUD ENDPOINTS:
GET    /api/v1/vendors/              — list (filters: qc_status, data_source, city, area, search)
POST   /api/v1/vendors/              — create (DATA_MANAGER, SUPER_ADMIN)
GET    /api/v1/vendors/{id}/         — detail (all roles read)
PATCH  /api/v1/vendors/{id}/         — update
DELETE /api/v1/vendors/{id}/         — soft delete (sets is_deleted=True — NEVER hard delete)

QC WORKFLOW:
POST /api/v1/vendors/{id}/approve/  — QC_REVIEWER, DATA_MANAGER, SUPER_ADMIN
POST /api/v1/vendors/{id}/reject/   — requires qc_notes in body
POST /api/v1/vendors/{id}/flag/     — sets qc_status=NEEDS_REVIEW

RELATED ENDPOINTS:
GET  /api/v1/vendors/{id}/audit-trail/   — AuditLog entries for this vendor
GET  /api/v1/vendors/{id}/photos/        — field photos (presigned S3 URLs)
GET  /api/v1/vendors/{id}/field-visits/  — field visit history

BUSINESS RULES:
- Phone number: decrypt on read, encrypt on write via core/encryption.py
- GPS: stored as PostGIS PointField — NOT separate lat/lng floats
- Soft delete: sets is_deleted=True, recorded in AuditLog with before/after snapshot
- is_deleted=True excluded from all list queries by default
- qc_reviewed_by must be FK to AdminUser — NOT raw UUID
- business_hours validated via BusinessHoursSchema on every write
- All POST/PATCH/DELETE create AuditLog with before_state + after_state snapshots
```

---

## PROMPT 3.8 — Import & CSV Processing Engine

```
Build the CSV import system for bulk vendor data ingestion.

IMPORT BATCH FLOW:
1. Admin uploads CSV to S3 directly (presigned URL from API)
2. POST /api/v1/imports/ with { file_key: "imports/batch_xyz.csv" }
3. API creates ImportBatch (status=QUEUED), triggers Celery task with batch_id ONLY
4. Celery task reads CSV from S3 streaming — NEVER from broker payload
5. Processes row by row, logs errors per-row, never stops on single-row error
6. error_log capped at 1000 entries
7. Updates ImportBatch.status = DONE or FAILED on completion

ENDPOINTS:
POST /api/v1/imports/presigned-url/    — generate S3 upload URL for CSV
POST /api/v1/imports/                  — create ImportBatch, trigger Celery
GET  /api/v1/imports/                  — list all jobs with status
GET  /api/v1/imports/{id}/             — detail with progress + error_log
POST /api/v1/imports/{id}/retry/       — re-trigger failed batch (idempotency guard)

CELERY TASK (apps/imports/tasks.py):
- Idempotency: check ImportBatch.status != PROCESSING before starting
- Per-row validation: GPS accuracy, business name, all required fields present
- On row error: append to error_log, increment error_count, continue processing
- On success: create Vendor record with data_source=CSV_IMPORT

CSV EXPECTED COLUMNS:
business_name, address_text, latitude, longitude, phone_number,
city_slug, area_slug, category_tag_slug, description, website_url

Roles: IMPORT_OPERATOR, DATA_MANAGER, SUPER_ADMIN
```

---

## PROMPT 3.9 — Field Operations APIs

```
Build the field operations module for on-ground data verification.

ENDPOINTS:
GET/POST    /api/v1/field-ops/visits/                     — list + create
GET/PATCH   /api/v1/field-ops/visits/{id}/                — detail + update
POST        /api/v1/field-ops/visits/{id}/photos/         — get presigned S3 upload URL
GET         /api/v1/field-ops/visits/{id}/photos/         — list photos (presigned URLs, 1hr)
DELETE      /api/v1/field-ops/visits/{id}/photos/{id}/    — soft delete photo

BUSINESS RULES:
- FIELD_AGENT: can only access own visits — enforce at QuerySet level in services.py
- Photos: stored as S3 key only — presigned URL generated fresh on every read
- GPS drift: if confirmed_point differs from vendor.gps_point by >20m via PostGIS ST_Distance,
  automatically flag vendor for QC review (set qc_status=NEEDS_REVIEW)
- Photo deletion: soft delete (is_active=False) — never hard delete from S3
- All mutations create AuditLog entries
```

---

## PROMPT 3.10 — QA, GPS Drift & Duplicate Detection

```
Build the QA automation module.

GPS DRIFT DETECTION ([DOC-1] §8.2):
- Business Rule R10: vendors where GPS moved >20m from baseline are flagged
- ALWAYS use PostGIS: ST_Distance(point::geography, new_point::geography) > 20
- NEVER use degree × constant approximation
- Weekly Celery Beat task: apps.qa.tasks.weekly_gps_drift_scan
  Schedule: Sunday 02:00 UTC (registered in code via setup_periodic_tasks())
  Sets qc_status=NEEDS_REVIEW, creates AuditLog per flagged vendor

DUPLICATE DETECTION ([DOC-1] §8.1):
- Business Rule R7: vendors with ≥85% name similarity within 50m radius are flagged
- Daily Celery Beat task: apps.qa.tasks.daily_duplicate_scan
  Schedule: daily 03:00 UTC
  Uses PostGIS ST_DWithin for radius + difflib.SequenceMatcher for name similarity
  Caps scan at 100 comparisons per vendor (prevents O(n²) explosion)

ENDPOINTS:
GET  /api/v1/qa/drift-flags/                  — list GPS drift flags
POST /api/v1/qa/drift-flags/{id}/resolve/     — mark resolved
GET  /api/v1/qa/duplicate-flags/              — list duplicate flags
POST /api/v1/qa/duplicate-flags/{id}/merge/   — merge duplicates (DATA_MANAGER, SUPER_ADMIN)
POST /api/v1/qa/drift-scan/trigger/           — manual trigger (SUPER_ADMIN only)

Celery tasks: retry logic (max 3 retries, exponential backoff), structured logging.
task_failure signal handler registered in celery_app.py.
```

---

## PROMPT 3.11 — Analytics & KPI Reporting (Portal)

```
Build analytics endpoints for platform health monitoring.

ENDPOINTS (all require ANALYTICS_VIEWER role or higher):
GET /api/v1/analytics/overview/           — total vendors by qc_status, imports stats, tags count
GET /api/v1/analytics/vendors/by-city/   — vendors per city with QC breakdown (choropleth data)
GET /api/v1/analytics/vendors/by-qc-status/  — counts and percentages by status
GET /api/v1/analytics/imports/trend/?days=30 — daily import counts + success rates
GET /api/v1/analytics/field-ops/activity/?days=7  — field visits per agent per day
GET /api/v1/analytics/qa/drift-flags/trend/   — GPS flags raised and resolved per week

BUSINESS RULES:
- All read-only — no mutations
- Results cached in Redis for 5 minutes
- Counts exclude is_deleted=True vendors
- Date ranges default to last 30 days, max 365 via ?days= param
```

---

## PROMPT 3.12 — Audit Trail System

```
Build the complete audit trail system.

AUDIT MIDDLEWARE (apps/audit/middleware.py):
- Runs after every POST, PUT, PATCH, DELETE request
- Guards against AnonymousUser and system/Celery calls
- Attaches request_id from RequestIDMiddleware

AUDIT UTILITIES (apps/audit/utils.py):
- log_action(action, actor, target_obj, request, before=None, after=None)
- Called explicitly from services.py — not only from middleware

ENDPOINTS:
GET /api/v1/audit/logs/                         — list (SUPER_ADMIN only), filters: actor, action,
                                                  target_type, date_range, request_id
GET /api/v1/audit/logs/{target_type}/{id}/      — all entries for a specific object
POST /api/v1/audit/logs/export/                 — CSV export (max 10,000 records)

BUSINESS RULES:
- AuditLog entries are IMMUTABLE — no updates, no deletes, ever
- Every POST, PATCH, DELETE MUST create an AuditLog entry
- System/Celery changes: actor=None, actor_label='SYSTEM_CELERY'
- before_state + after_state stored as JSON snapshots (not FKs)
```

---

## PROMPT 3.13 — Health Check & OpenAPI

```
Build health check endpoint and OpenAPI documentation.

HEALTH CHECK [AUDIT G01]:
GET /api/v1/health/ — UNAUTHENTICATED endpoint (for Docker health checks + load balancers)
- Checks: database connectivity + Redis ping
- HTTP 200: { status: "healthy", db: "ok", cache: "ok" }
- HTTP 503: { status: "degraded", db: "error", cache: "ok" }

OPENAPI:
- GET /api/v1/schema/  — raw OpenAPI JSON (drf-spectacular)
- GET /api/v1/docs/    — Swagger UI
- GET /api/v1/redoc/   — ReDoc UI
- All views decorated with @extend_schema (summary, tags, auth requirements)

URL STRUCTURE (config/urls.py):
/api/v1/auth/       /api/v1/geo/        /api/v1/tags/
/api/v1/vendors/    /api/v1/imports/    /api/v1/field-ops/
/api/v1/qa/         /api/v1/analytics/  /api/v1/audit/
/api/v1/health/     /api/v1/schema/     /api/v1/docs/
```

---
---

# 4. REACT ADMIN PORTAL

> **Desktop-first internal tool. All pages must comply with DLS A1–A14. Build DLS components FIRST (Prompt 4.1), then pages.**

---

## PROMPT 4.1 — Design System Setup & DLS Token File

```
Set up the React portal project and create all DLS foundation files.

PROJECT SETUP:
Vite + React 18 + TypeScript 5. React Router v6. Zustand (global state). TanStack Query
(API data fetching + caching). Axios with JWT interceptor (auto-attach token, handle 401 refresh).

Create frontend/src/styles/dls-tokens.css with ALL CSS custom properties from Prompt 2.1.
Import this file FIRST in main.tsx. Never hardcode hex values in any component.

Create frontend/src/components/dls/ with these shared components BEFORE any pages:
Button.tsx · Badge.tsx · Table.tsx (sortable, paginated, EmptyState + SkeletonRows)
Input.tsx · Textarea.tsx · Select.tsx · Checkbox.tsx · Toggle.tsx
Modal.tsx (focus trap, ESC close) · Drawer.tsx (640px right-side)
Toast.tsx + ToastProvider.tsx
Sidebar.tsx (pill-right nav, role-based visibility) · TopBar.tsx · PageHeader.tsx · FiltersBar.tsx
EmptyState.tsx · SkeletonTable.tsx · GPSInput.tsx (lat/lng + Leaflet mini-map preview)

Axios interceptor:
- Attach Authorization: Bearer {token} to all requests
- On 401: attempt token refresh; on refresh failure: redirect to /login
- On any API error: show Toast with error message from { message } field

All components: keyboard navigation (Tab, Enter, Escape, Space) + appropriate aria-* attributes.
```

---

## PROMPT 4.2 — Geographic Management Section

```
Build the Geographic Management section.

NAVIGATION: Sidebar → "Data Management" → "Geography" (sub-items: Countries, Cities, Areas, Landmarks)

CITY TREE VIEW (Main):
Left panel (320px): Collapsible tree: Country → City → Area → Landmark.
Click any node → loads detail + edit form in right panel.
Right panel: inline editing (click to edit), shows: name, slug (read-only after create),
aliases array editor (tag-input style), active toggle, display order.

CITY MANAGEMENT:
Columns: Name, Country, Areas Count, Landmarks Count, Aliases Count, Is Active, Actions.
Create/Edit in right-side Drawer. Map preview: Leaflet showing centroid + bounding box.
Launch Readiness indicator: calls /api/v1/geo/cities/{id}/launch-readiness/ and displays
as a checklist. "Launch City" button only enabled when all criteria pass.
Alias count < 3: show warning badge.

AREA MANAGEMENT:
Tree view within city. Drawer for create/edit.
Parent Area selector (self-referential). Alias warning if < 3.

LANDMARK MANAGEMENT:
List per area. Each: name, alias count, GPS pin on Leaflet mini-map.
Alias count < 3: warning badge "Low Alias Count — Add More for Voice Accuracy".

All forms: real-time validation. AuditLog created on every save.
Role gate: DATA_MANAGER + SUPER_ADMIN write; all roles read.
```

---

## PROMPT 4.3 — Tag & Category Management Section

```
Build the Tag Management section.

NAVIGATION: Sidebar → "Data Management" → "Tags"

MAIN TAG LIST:
Dense table. Columns: Name, Slug, Tag Type (colored badge), Display Order, Is Active, Usage Count, Actions.
Filters: tag_type dropdown, is_active toggle, search. Sorting: display_order (default), name, usage_count.
Inline actions: Toggle Active, Edit, View Usage.

CREATE/EDIT TAG FORM (right Drawer):
Fields: name (auto-generates slug), tag_type selector (colored chips), display_label, display_order,
icon_name (lucide-react picker), is_active toggle. Live preview: how tag appears on vendor cards.

TAG USAGE DETAIL (click Usage Count):
Modal: which vendors use this tag, assignment method (SYSTEM/ADMIN/AUTO), sparkline trend over 30 days.

BULK OPERATIONS:
Multi-select → bulk activate/deactivate. Runs as background job with progress toast.

SYSTEM TAGS SECTION:
Separate section at bottom (read-only). Each: effect description + current usage count.
No create/edit/delete controls for SYSTEM tags.

Role gate: CONTENT_MODERATOR (CATEGORY + INTENT only), DATA_MANAGER + SUPER_ADMIN (all types).
```

---

## PROMPT 4.4 — Vendor Oversight & QC Queue

```
Build the Vendor Management section — the most-used section of the portal.

NAVIGATION: Sidebar → "Vendors" (top-level)

VENDOR LIST:
Dense table. Columns: Logo (32px), Business Name, City, Area, QC Status (colored badge),
Data Source (badge), GPS (pin icon — click opens mini-map), Phone (masked), Created, Actions.
Filters: qc_status (multi-select), data_source, city, area (cascades), date range, text search.
Sorting: created_at desc (default), business_name, qc_status.
Inline actions: Quick Approve, Quick Reject, Open Detail. Bulk: Bulk Approve, Bulk Flag.

VENDOR DETAIL PAGE (full page — NOT a modal):
Tabs:

Tab 1 — Overview: business info left / Leaflet map + QC widget right. Approve/Reject/Flag buttons.
Tab 2 — Field Photos: masonry grid, presigned S3 URLs, lightbox, admin delete (soft).
Tab 3 — Visit History: timeline of FieldVisit records, GPS drift alert if confirmed >20m from vendor.
Tab 4 — Tags: table of assigned tags with source label. Add/Remove tag controls.
Tab 5 — Analytics: read-only vendor stats summary.
Tab 6 — Internal Notes (SUPER_ADMIN + QC_REVIEWER): qc_notes, timestamped, never visible to vendor.

QC REVIEW QUEUE:
Separate view (Sidebar → "QC Queue"): shows only PENDING + NEEDS_REVIEW, sorted by created_at asc.
Count badge on sidebar nav item. One-click Approve + Reject with required notes field.

CLAIM REVIEW QUEUE:
Shows all pending vendor claims. Columns: vendor name, claimer phone/email, days waiting.
Approve/reject with required reason note.

LOCATION CHANGE REVIEW:
Side-by-side split map: old GPS vs new GPS. Approve or reject.

All mutations show toast + create AuditLog.
```

---

## PROMPT 4.5 — Import Management Section

```
Build the CSV Import Management section.

NAVIGATION: Sidebar → "Imports"

IMPORT JOB LIST:
Table. Columns: Batch ID (truncated UUID), File Name, Status (badge), Total Rows, Processed,
Errors, Created By, Created At, Actions.
Status badges: QUEUED (grey), PROCESSING (blue animated), DONE (green), FAILED (red).
Auto-refresh every 10s for QUEUED/PROCESSING jobs (React Query refetchInterval).

CREATE NEW IMPORT:
Drag-and-drop CSV upload. Client validates: CSV format, < 50MB.
Column mapping preview: PapaParse first 5 rows client-side, highlight missing required columns in red.
Flow: Upload CSV → S3 presigned URL → POST /api/v1/imports/ → navigate to job detail.

IMPORT JOB DETAIL:
Progress bar: processed_rows / total_rows. Error log table: row number, field, error, raw row.
"Retry" button if status=FAILED.

Role gate: IMPORT_OPERATOR, DATA_MANAGER, SUPER_ADMIN.
```

---

## PROMPT 4.6 — Field Operations Section

```
Build the Field Operations management section.

NAVIGATION: Sidebar → "Field Ops" → sub-items: Visits, Agents

VISIT LIST:
Table. Columns: Vendor Name (linked), Agent Name, Visit Date, GPS Confirmed (checkmark/dash),
Photos Count, GPS Drift Alert (warning icon if confirmed GPS differs >20m), Actions.
Filters: agent, vendor, date range, has_drift_alert.
FIELD_AGENT role: only own visits shown (API enforced, not just frontend).

VISIT DETAIL (right-side Drawer):
Vendor info card. Visit notes. GPS section: vendor pin + confirmed pin on Leaflet map side-by-side.
Distance delta displayed. If >20m: amber warning "GPS Drift Detected — Vendor flagged for QC."
Photos grid: thumbnail + lightbox. Upload button triggers presigned S3 upload.

AGENT OVERVIEW:
Table: Name, Email, Total Visits, Visits This Week, Last Active, Status.
Click agent → filter visit list to that agent.

Role gate: FIELD_AGENT (own), QC_REVIEWER (read all), DATA_MANAGER/SUPER_ADMIN (full).
```

---

## PROMPT 4.7 — QA Dashboard

```
Build the QA monitoring and action dashboard.

NAVIGATION: Sidebar → "QA" → sub-items: GPS Drift Flags, Duplicate Flags

GPS DRIFT FLAGS:
Table. Columns: Vendor Name, City, Old GPS, New GPS, Distance Delta (metres), Flagged At,
Status (OPEN/RESOLVED), Actions.
Filter: status, city, date range. Bulk: Mark Selected as Resolved.
"Resolve" button: confirms GPS change is legitimate, sets RESOLVED, updates AuditLog.
"Run GPS Drift Scan Now" (SUPER_ADMIN only) → POST /api/v1/qa/drift-scan/trigger/
→ loading state → success toast with count of flags created.

DUPLICATE FLAGS:
Table. Columns: Vendor A (name + city), Vendor B (name + city), Similarity %, Distance (m),
Flagged At, Status, Actions.
"Compare" → side-by-side comparison modal with both vendor details.
"Mark as Not Duplicate" → resolves without merge.
"Merge" → merge wizard: select canonical record, confirm data to keep (DATA_MANAGER, SUPER_ADMIN).
```

---

## PROMPT 4.8 — Platform Health Dashboard

```
Build the Platform Health Dashboard as the default home page (/) after login.
This is the first screen admins see — it must load fast and communicate platform status clearly.

HERO METRICS ROW (top):
Six large metric cards with number, label, and sparkline trend (vs yesterday):
Total Active Vendors · Total Active Discounts Right Now · Discovery Searches Today ·
Voice Queries Today · New Vendor Claims (last 7 days) · Vendors Pending Verification.
Auto-refresh every 60 seconds. Show "Last updated X seconds ago" per card.

DATA COLLECTION PORTAL METRICS (second row):
Four focused metric cards:
- Vendors Pending QC (count + "Review Queue" link)
- Import Success Rate this week (percentage)
- GPS Drift Flags Open (count + "View" link)
- Field Visits this week (count)
Semantic color per card: green (healthy), amber (attention), red (critical threshold).

DISCOUNT ACTIVITY TIMELINE:
Line chart (Recharts): discount activations (green) + deactivations (grey) over last 24h by hour.
Reference line = average activity level. Helps verify Celery scheduler is running correctly.

VENDOR QC STATUS DONUT CHART (Recharts):
APPROVED (Babu teal) / PENDING (grey) / REJECTED (red) / NEEDS_REVIEW (Arches orange).
Click a segment → filters vendor list to that status.

CITY COVERAGE MAP (Leaflet + react-leaflet):
Choropleth showing vendors per city. Color intensity: light to --color-rausch based on vendor count.
Portal mode: color-coded circles per city: green ≥100 vendors, amber 50–99, red <50.
Hover tooltip: city name + vendor count + active discount count + searches today.

IMPORT ACTIVITY CHART (Recharts):
Line chart: daily import jobs over last 30 days, success vs error. Time range picker: 7d/14d/30d.

SEARCH TERMS CLOUD:
Top 20 most-searched terms in last 7 days (word cloud or ranked list).

SYSTEM ALERTS SECTION (bottom):
Automated alerts: corrupted location data, areas with zero vendors, Celery task failures,
expired subscriptions, pending claims >48 hours. Severity (HIGH/MED/LOW with semantic colors),
description, affected entity, direct action link.

RECENT ACTIVITY FEED:
Last 10 AuditLog entries. Shows: action, actor, target, time-ago. Clickable → opens object detail.

All data: /api/v1/analytics/ endpoints. React Query 5min staleTime. Skeleton loading on all areas.
```

---

## PROMPT 4.9 — Audit Log Viewer

```
Build the Audit Log viewer section (SUPER_ADMIN only).

NAVIGATION: Sidebar → "System" → "Audit Log" (visible to SUPER_ADMIN only)

MAIN VIEW:
Dense table (44px row height — read-only, high volume).
Columns: Timestamp, Action (code + human label), Actor, Target Type, Target ID (linked), Request ID, IP.
Filters: actor (search), action (searchable dropdown), target_type, date range.
Sorting: created_at desc (default). No bulk actions — logs are immutable.

ROW EXPANSION:
Click row → expands inline (not modal) showing:
  - Before State JSON + After State JSON (syntax-highlighted diff viewer — use react-diff-viewer)
  - Full Request ID

EXPORT:
"Export CSV" → POST /api/v1/audit/logs/export/ → download link. Max 10,000 records.

Reminder: No edit or delete controls anywhere. AuditLog entries are immutable.
```

---

## PROMPT 4.10 — User & Role Management

```
Build the User Management section (SUPER_ADMIN only).

NAVIGATION: Sidebar → "System" → "Users"

USER LIST:
Table. Columns: Full Name, Email, Role (colored badge), Last Login, Failed Attempts,
Account Status (Active / Locked with time remaining), Created, Actions.
Filters: role, is_active, is_locked.
Inline: Edit Role, Deactivate, Unlock Account.

CREATE USER (right Drawer):
Fields: full_name, email, role (single select with permission summary tooltip per role),
is_active toggle. Password: auto-generated, shown once in copyable field. Must change on first login.

EDIT USER (right Drawer): Change full_name, role, is_active. Cannot change email/password here.

ACCOUNT UNLOCK:
"Unlock Account" → confirmation modal → PATCH /api/v1/accounts/{id}/unlock/.

All mutations create AuditLog entries. Role gate: SUPER_ADMIN only.
```

---
---

# 5. INFRASTRUCTURE & DEVOPS

---

## PROMPT 5.1 — Docker & Docker Compose

```
Build the complete Docker setup.

BACKEND DOCKERFILE (multi-stage):
Stage 1 (builder): python:3.12-slim, install build deps, compile psycopg2 (NOT psycopg2-binary).
Stage 2 (production): python:3.12-slim + GDAL system package.
  CRITICAL: GDAL version must match PostGIS image GDAL version exactly.
  CMD: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4

FRONTEND DOCKERFILE (multi-stage):
Stage 1 (builder): node:20-alpine, npm ci, npm run build.
Stage 2 (production): nginx:alpine, serve /builder/dist.
  NEVER use npm run dev in production stage.

docker-compose.yml (PRODUCTION):
Services: postgres (PostGIS image), redis, backend, celery-worker, celery-beat, frontend (nginx), nginx
- NO source code volume mounts in production
- celery-beat: deploy.replicas: 1 (exactly one — prevents duplicate tasks)
- backend: depends_on postgres (with health check condition) + redis

docker-compose.dev.yml (DEVELOPMENT override):
- Source code volume mounts for hot reload
- Backend CMD: python manage.py runserver 0.0.0.0:8000
- Frontend CMD: npm run dev

.dockerignore: present for both backend + frontend.
Health checks: postgres uses pg_isready, redis uses redis-cli ping.
```

---

## PROMPT 5.2 — CI/CD Pipeline (GitHub Actions)

```
Build the complete GitHub Actions CI pipeline (.github/workflows/ci.yml).
Trigger: push to main/develop, PR to main.

JOBS (parallel where possible):
1. backend-lint: ruff check + black --check + isort --check
2. backend-migration-check: python manage.py migrate --check
3. backend-test (depends on 1+2):
   Services: postgres:16-postgis, redis:7
   Env: test settings, test DB, dummy AWS vars
   Run: pytest --cov-fail-under=80
   ALL external API calls (S3, Google Places) must be mocked (moto / unittest.mock)
4. security-scan: bandit -r apps core -ll + safety check -r requirements/production.txt
5. frontend-lint: npm run lint + npm run type-check + npm run format:check
6. frontend-build (depends on 5): npm run build (must succeed without warnings)

Pipeline passes ONLY when ALL jobs pass.
```

---

## PROMPT 5.3 — Environment Configuration

```
Create .env.example with ZERO literal placeholder values — only generation instructions.

# AirAd Environment Configuration
# Generate: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY=GENERATE_WITH_DJANGO_MANAGEMENT_COMMAND_SEE_README

DJANGO_SETTINGS_MODULE=config.settings.production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DEBUG=False

DB_NAME=airaad
DB_USER=airaad_user
DB_PASSWORD=CHANGE_IN_PRODUCTION_USE_STRONG_RANDOM_VALUE
DB_HOST=postgres
DB_PORT=5432

REDIS_URL=redis://redis:6379/0
REDIS_RESULT_URL=redis://redis:6379/1

# Generate: python -c "import os,base64; print(base64.b64encode(os.urandom(32)).decode())"
ENCRYPTION_KEY=GENERATE_WITH_SCRIPT_IN_README_32_BYTES_BASE64_ENCODED

AWS_ACCESS_KEY_ID=GET_FROM_AWS_IAM_CONSOLE
AWS_SECRET_ACCESS_KEY=GET_FROM_AWS_IAM_CONSOLE
AWS_STORAGE_BUCKET_NAME=airaad-media-production
AWS_S3_REGION_NAME=ap-south-1

VITE_API_BASE_URL=https://api.yourdomain.com
```

---

## PROMPT 5.4 — Seed Data Management Command

```
Build: python manage.py seed_data

MUST be idempotent (safe to run multiple times — uses update_or_create).

SEED DATA:
1. Countries: Pakistan (PK) and expansion markets
2. Cities: All major Pakistani cities with GPS centroids + bounding boxes
3. Areas: Key areas per city (reference [DOC-1])
4. Landmarks: Key landmarks per area with minimum 3 aliases each (voice search)
5. Tags (all types from [DOC-1] §3):
   CATEGORY: Food, Shopping, Services, Health, etc.
   INTENT: Cheap, Fast, Nearby, etc.
   PROMOTION: Discount, Flash Deal, Happy Hour, etc.
   TIME: Open Now, Breakfast, Lunch, Dinner, etc.
   SYSTEM: Platform-assigned, cannot be created via API
6. Subscription packages (SILVER, GOLD, DIAMOND, PLATINUM) with features + pricing

BEHAVIOR:
- update_or_create for all records
- Prints progress: "Loading cities... [10/25 done]"
- Prints summary: "Seeded: 3 countries, 25 cities, 180 areas, 420 landmarks, 47 tags, 4 packages"
- Exit code 0 on success, 1 on error with descriptive message
```

---
---

# 6. TEST SUITE — PORTAL

---

## PROMPT 6.1 — Unit Tests — Business Rules R1–R10

```
Build unit tests for all 10 business rules. Define factory_boy factories for ALL models first.

tests/factories.py:
AdminUserFactory · CityFactory · AreaFactory · LandmarkFactory
VendorFactory (with qc_status, gps_point kwargs)
ImportBatchFactory · FieldVisitFactory · TagFactory

BUSINESS RULES:

R1 — Only SUPER_ADMIN creates users:
  TestCreateUserRBAC: test_super_admin_201 · test_data_manager_403 · test_field_agent_403

R2 — Account lockout after 5 failed logins:
  TestAccountLockout: test_lockout_after_five · test_returns_429 · test_clears_after_duration · test_reset_on_success

R3 — GPS as PostGIS PointField:
  TestVendorGPSStorage: test_is_postgis_point_type · test_uses_st_distance (assert no degree math)

R4 — GPS drift >20m triggers QC flag:
  TestGPSDriftDetection: test_flagged_on_21m · test_no_flag_on_19m · test_uses_postgis_not_approximation

R5 — Phone numbers encrypted at rest:
  TestPhoneEncryption: test_stored_encrypted · test_decrypted_on_read · test_round_trip

R6 — Soft delete only:
  TestSoftDelete: test_sets_is_deleted_true · test_excluded_from_list · test_still_in_db

R7 — Duplicate detection ≥85% similarity within 50m:
  TestDuplicateDetection: test_flagged_within · test_outside_50m_not_flagged · test_different_name_not_flagged · test_capped_100_comparisons

R8 — All mutations create AuditLog:
  TestAuditLogCreation: test_vendor_create · test_vendor_approve · test_soft_delete · test_includes_before_after_state

R9 — CSV import idempotency:
  TestCSVImport: test_idempotency_guard · test_per_row_error_continues · test_error_log_capped_1000 · test_only_batch_id_passed

R10 — GPS drift Celery task:
  TestGPSDriftTask (CELERY_TASK_ALWAYS_EAGER=True):
  test_flags_on_20m · test_no_flag_within · test_creates_audit_log · test_uses_postgis
```

---

## PROMPT 6.2 — RBAC Integration Tests

```
Build RBAC integration tests for every restricted endpoint.
FILE: tests/integration/test_rbac.py

Use @pytest.mark.parametrize with (role, expected_status) tuples.
Cover minimum:
- GET /api/v1/vendors/               — all roles 200
- POST /api/v1/vendors/              — DATA_MANAGER/SUPER_ADMIN 201; others 403
- POST /api/v1/vendors/{id}/approve/ — QC_REVIEWER/DATA_MANAGER/SUPER_ADMIN 200; others 403
- POST /api/v1/imports/              — IMPORT_OPERATOR/DATA_MANAGER/SUPER_ADMIN 201; others 403
- GET /api/v1/analytics/overview/    — ANALYTICS_VIEWER+ 200; no auth 401
- GET /api/v1/audit/logs/            — SUPER_ADMIN 200; all others 403
- POST /api/v1/accounts/             — SUPER_ADMIN 201; all others 403
- POST /api/v1/qa/drift-scan/trigger/ — SUPER_ADMIN 200; all others 403

No test may rely on real external APIs. Mock all S3 and external service calls.
```

---

## PROMPT 6.3 — Security & Lockout Tests

```
FILE: tests/unit/test_security.py

TestAccountLockout:
  test_lockout_after_five_failed_attempts
  test_lockout_clears_after_duration (use freezegun)
  test_successful_login_resets_counter
  test_locked_account_returns_429_with_retry_after_header

TestEncryption:
  test_encrypt_decrypt_round_trip
  test_empty_string_returns_empty_bytes
  test_different_plaintexts_produce_different_ciphertexts
  test_tampered_ciphertext_raises_decryption_error

TestJWTAuth:
  test_expired_access_token_returns_401
  test_refresh_rotates_token
  test_blacklisted_refresh_token_rejected
  test_token_claims_include_role_and_full_name

TestHealthCheck:
  test_returns_200_when_healthy
  test_returns_503_when_db_down (mock DB OperationalError)
  test_is_unauthenticated (no JWT required)
```

---

## PROMPT 6.4 — Celery Task Tests

```
FILE: tests/unit/test_tasks.py (CELERY_TASK_ALWAYS_EAGER=True in test settings)

TestCSVImportTask:
  test_idempotency_skips_already_processing
  test_idempotency_skips_completed
  test_per_row_error_appends_without_stopping
  test_error_log_truncated_at_1000
  test_successful_rows_create_vendor_records
  test_status_done_on_completion
  test_status_failed_on_exception

TestGPSDriftScanTask:
  test_flagged_on_20m_deviation
  test_no_flag_within_20m
  test_uses_st_distance_not_manual_math
  test_creates_audit_log_per_flagged_vendor
  test_creates_audit_log_with_system_actor

TestDuplicateScanTask:
  test_flagged_at_85_percent_within_50m
  test_respects_100_comparison_cap

All: mock S3 with moto. Mock SMTP/notification calls.
```

---
---

# 7. QUALITY GATE & EXECUTION ORDER — PHASE A

---

## PROMPT 7.1 — Quality Gate Checklist

```
Before submitting any module as complete, verify ALL items:

BACKEND:
- [ ] Every model: UUID PK, created_at, updated_at where appropriate
- [ ] Every mutating view creates an AuditLog entry
- [ ] All 10 business rules (R1–R10) enforced and tested
- [ ] RolePermission.for_roles() on every view — no __call__ method
- [ ] GPS: PostGIS PointField — never separate lat/lng floats
- [ ] Phone numbers: AES-256-GCM encrypted at rest
- [ ] No TODO, pass, or stub in any production path
- [ ] Health check returns 503 on DB or cache failure
- [ ] CONN_MAX_AGE=60 in database config
- [ ] GiST spatial indexes via migrations.RunSQL for all PointField columns
- [ ] psycopg2 (compiled) in requirements/production.txt — NOT psycopg2-binary
- [ ] error_log in ImportBatch capped at 1000 entries
- [ ] Business hours validated via BusinessHoursSchema on write
- [ ] Celery periodic schedules in code via setup_periodic_tasks()
- [ ] task_failure signal handler registered in celery_app.py
- [ ] RequestIDMiddleware is FIRST middleware
- [ ] All 7 AdminRole values in enum match RBAC matrix exactly
- [ ] OpenAPI schema accessible at /api/v1/schema/

FRONTEND:
- [ ] All pages comply with DLS Prompts 2.1 and 2.2
- [ ] WCAG AA contrast (4.5:1 body text, 3:1 large text)
- [ ] All interactive elements keyboard accessible with visible focus ring
- [ ] All tables: empty state + skeleton loading (never spinners)
- [ ] All async mutations: toast notification
- [ ] No hardcoded hex colors anywhere — CSS custom properties only
- [ ] No icon-only buttons without aria-label
- [ ] prefers-reduced-motion respected
- [ ] Sidebar nav: pill-right pattern (border-radius: 0 100px 100px 0)
- [ ] --color-rausch primary button: max 1 per view

TESTS:
- [ ] All 10 business rules: dedicated test classes
- [ ] RBAC: forbidden 403, permitted 200/201
- [ ] Celery tasks: CELERY_TASK_ALWAYS_EAGER=True
- [ ] Account lockout tested (5 attempts → 429)
- [ ] AES-256-GCM round-trip tested
- [ ] Coverage ≥ 80% enforced by --cov-fail-under=80
- [ ] No tests use real S3, Google Places, or external APIs
- [ ] factory_boy factories for all models

DOCKER & CI:
- [ ] docker-compose up brings full stack in one command
- [ ] Frontend: multi-stage Dockerfile, no npm run dev in production
- [ ] No source volume mounts in production Compose
- [ ] Nginx reverse proxy — backend not directly port-exposed
- [ ] .dockerignore for backend and frontend
- [ ] CI: lint → migration check → test ≥80% → security scan → build
- [ ] celery-beat: replicas: 1 in Compose deploy config
- [ ] .env.example: zero literal placeholder values
```

---

## PROMPT 7.2 — Execution Build Order (39 Steps)

```
Follow this order STRICTLY. Do NOT skip or reorder.
Do NOT proceed to Step N+1 if Quality Gate for Step N has any unchecked item.

Step 1:  .env.example + README setup instructions
Step 2:  docker-compose.yml + docker-compose.dev.yml
Step 3:  backend/Dockerfile + frontend/Dockerfile
Step 4:  nginx/nginx.conf
Step 5:  requirements/*.txt (base, production, development, test)
Step 6:  config/settings/ (base, production, development, test)
Step 7:  config/urls.py
Step 8:  celery_app.py (routing + task failure signal handler)
Step 9:  core/ utilities (encryption, geo_utils, middleware, pagination, exceptions, storage, schemas, utils)
Step 10: apps/accounts/models.py + migrations (7 roles, lockout fields)
Step 11: apps/accounts/permissions.py (for_roles class factory)
Step 12: apps/accounts/views.py + serializers + urls (login with lockout)
Step 13: apps/audit/models.py + middleware + utils
Step 14: apps/geo/models.py + migrations (GiST index RunSQL)
Step 15: apps/tags/models.py + migrations
Step 16: apps/vendors/models.py + migrations (FK refs, updated_at)
Step 17: apps/imports/models.py + apps/field_ops/models.py + migrations
Step 18: All services.py with business logic
Step 19: All DRF serializers for every app
Step 20: All DRF views + ViewSets + urls
Step 21: apps/imports/parsers.py + tasks.py (idempotent, S3-based)
Step 22: apps/qa/tasks.py (PostGIS drift, periodic schedules)
Step 23: Health check view at /api/v1/health/
Step 24: core/schemas.py (BusinessHoursSchema)
Step 25: Management command: seed_data
Step 26: OpenAPI schema at /api/v1/schema/
Step 27: pytest.ini + tests/factories.py
Step 28: All unit tests (R1–R10 + lockout + encryption)
Step 29: All RBAC integration tests
Step 30: All Celery task tests
Step 31: .github/workflows/ci.yml
Step 32: frontend/src/styles/dls-tokens.css
Step 33: All DLS base components (components/dls/)
Step 34: Layout components (Sidebar, TopBar, PageHeader, FiltersBar)
Step 35: Shared components (EmptyState, SkeletonTable, ToastProvider)
Step 36: Zustand store slices + Axios API clients
Step 37: All 10 admin portal pages (Prompts 4.2–4.10)
Step 38: GPS map components (GPSInput, Leaflet choropleth)
Step 39: README.md with complete setup, key generation, and run instructions

SESSION-BASED EXECUTION RULES:
- Execute ONLY the steps specified in your current session prompt.
- Confirm each step completion before proceeding to the next step.
- Stop at the session boundary — do not continue to the next session's steps unprompted.
- After completing each step, output: "✓ Step N complete — [one-line summary of what was built]"
- Self-check against Quality Gate (Prompt 7.1) before marking any step complete.
- If a step cannot be completed due to a dependency or blocker, STOP and report the issue
  clearly before proceeding. Do not skip steps silently.

HOW TO USE THE 39-STEP ORDER:
Copy only the steps for your current session into Windsurf along with Prompts 1.1, 1.2,
and the relevant module prompts. Never send all 39 steps in a single session.
Recommended session groupings are provided in the README execution guide.
```

---
---

# 8. PHASE-2 EXCLUSION LIST (PORTAL BUILD)

```
In the Phase A portal build, do NOT implement, stub, or create placeholder routes for:

| Feature                              | Source Reference              |
|--------------------------------------|-------------------------------|
| Customer-facing discovery API        | [DOC-3] — all                 |
| Vendor login / vendor dashboard      | [DOC-2] — all                 |
| Flutter mobile app                   | Phase B only                  |
| AR spatial features                  | [DOC-3] §4                    |
| Voice bot / voice search             | [DOC-3] §5                    |
| Subscription / payment management    | [DOC-2] §10                   |
| Advanced AI-based fraud detection    | [DOC-4] §1.2                  |
| Automated sentiment analysis         | [DOC-4] §1.2                  |
| Review and rating systems            | [DOC-1] §1.2                  |
| Payment processing / POS integration | [DOC-1] §1.2                  |
| Inventory management systems         | [DOC-2] §1.2                  |
| LimitedStock proof validation        | [DOC-2] §9.2                  |
| Social networking / friend features  | [DOC-3] §1.2                  |
| Multi-location franchisee dashboards | [DOC-2] §1.2                  |
| Loyalty programs and gamification    | [DOC-1] §1.2                  |
| Advanced music copyright detection   | [DOC-4] §4.2                  |
```

---
---
---

# PHASE B — FULL PLATFORM

---

# 9. PROJECT FOUNDATION & GLOBAL RULES — PHASE B

> **Send this section before any Phase B module. It extends Phase A with the full public platform.**

---

## PROMPT 9.1 — Phase B Context & Additional Global Rules

```
Phase A is complete — the data collection portal is built and the vendor database is seeded.

CRITICAL — PHASE B IS AN EXTENSION, NOT A NEW PROJECT:
Do NOT create a new Django project. Do NOT create a new React project.
Phase B extends the existing Phase A codebase:
- Add new Django apps (discounts, analytics, voice_bot, subscriptions) to the EXISTING project
- Extend existing models (Vendor, accounts) with new fields via new migrations
- Add new React pages/routes to the EXISTING portal for Vendor Dashboard
- All Phase A models, migrations, services, tests, and infrastructure remain intact and unchanged
- New Celery tasks register alongside existing Phase A tasks in celery_app.py
- New URL patterns append to the existing config/urls.py

PHASE B — WHAT YOU ARE BUILDING NOW:
Extend the AirAd backend with full public-facing APIs, build the Vendor Dashboard in the
React portal, and build the Flutter mobile app for customers and vendors.

The full platform surfaces are:
1. Django REST API — now extended with Discovery, Discounts, Voice Bot, Subscriptions
2. React Web Portal — now extended with Vendor Dashboard (Profile, Discounts, Analytics, Voice Bot, Subscription)
3. Flutter Mobile App — Customer discovery (AR, Map, Voice) + Vendor mobile tools

ADDITIONAL USER TYPES (Phase B):
- CUSTOMER: discovers vendors, navigates, uses voice search, AR view
- VENDOR (registered): manages listing, discounts, reels, voice bot

ADDITIONAL GLOBAL RULES:
- Vendor visibility is NEVER blocked for free (Silver) tier — paid tiers only improve placement
- Ranking algorithm weights: Relevance 30% + Distance 25% + Active Offer 15% + Popularity 15% + Subscription 15%
- All discount activations/deactivations are AUTOMATIC via Celery — never require manual vendor action
- vendor_has_feature(vendor, feature_name) is the ONLY subscription gate mechanism — no scattered if-else
- Customer phone OTP via Twilio (abstracted behind service class, provider-swappable)
- Flutter app: Provider/Riverpod for state, Go Router for navigation, Dio as HTTP client
```

---
---

# 10. DJANGO BACKEND — FULL PLATFORM APIS

---

## PROMPT 10.1 — Additional Models (Full Platform)

```
Extend the Django backend with additional models required for the public platform.

DISCOUNT MODEL (apps/vendors/models.py — extend):
vendor (FK), title, discount_type (choices: PERCENTAGE, FIXED_AMOUNT, BUY_ONE_GET_ONE,
FREE_DELIVERY, FLASH_DEAL, ITEM_SPECIFIC), value (decimal), applies_to (ALL_ITEMS/SPECIFIC_ITEMS),
item_description (text nullable), start_time (datetime), end_time (datetime),
is_recurring (boolean), recurrence_days (JSONField array of day numbers),
is_active (computed property — True only when current time is between start and end),
min_order_value (decimal nullable), created_at.

ANALYTICS EVENT MODEL (apps/analytics/models.py — extend):
event_type (choices: VIEW, TAP, DIRECTION_REQUEST, VOICE_QUERY, VIDEO_VIEW, DISCOUNT_VIEW),
vendor (FK nullable), user (FK nullable), session_id, latitude, longitude, device_type,
search_query (text nullable), timestamp.
CRITICAL: This table will be high-volume — partition by month.

VOICE BOT CONFIG MODEL (apps/vendors/models.py — extend):
One-to-one with Vendor. Fields: menu_items (JSONField array: {name, price, availability}),
opening_hours_summary (text, auto-generated from business_hours),
delivery_info (text), discount_summary (auto-updated when discounts change),
custom_qa_pairs (JSONField array of {question, answer} objects).

SUBSCRIPTION PACKAGE MODEL:
Reference data. Fields: level (SILVER/GOLD/DIAMOND/PLATINUM), price_monthly,
max_videos, daily_happy_hours_allowed, has_voice_bot, has_sponsored_windows,
has_predictive_reports, visibility_boost_weight (decimal, used in ranking), description.
Seeded via management command (not migration).

EXTEND VENDOR MODEL (for public platform):
Add to existing Vendor model: owner (FK to Customer/Vendor User nullable),
is_claimed (boolean default False), claimed_at (datetime nullable),
logo (ImageField → S3), cover_photo (ImageField → S3),
offers_delivery (boolean), offers_pickup (boolean),
is_verified (boolean), subscription_level (SILVER/GOLD/DIAMOND/PLATINUM default SILVER),
subscription_valid_until (datetime nullable),
total_views (integer counter), total_profile_taps (integer counter),
location_pending_review (boolean default False).
```

---

## PROMPT 10.2 — Authentication — Customer & Vendor (OTP + Email)

```
Extend authentication to support CUSTOMER and VENDOR users.

CUSTOMER AUTH:
- Registration via phone number + OTP (SMS via Twilio — abstract behind service class)
- Optional email. Phone = primary identity.
- POST /api/v1/auth/customer/send-otp/    — send OTP to phone number
- POST /api/v1/auth/customer/verify-otp/  — verify OTP, create/login user, return JWT
- POST /api/v1/auth/customer/profile/     — update name, email, preferred_language, device_token

VENDOR AUTH:
- Requires phone + email. Phone OTP first, then email verification.
- PENDING_CLAIM state until admin approves claim.
- POST /api/v1/auth/vendor/send-otp/
- POST /api/v1/auth/vendor/verify-otp/
- POST /api/v1/auth/vendor/verify-email/
- GET  /api/v1/auth/vendor/me/            — vendor profile + subscription status

CUSTOMER MODEL ADDITIONS:
last_location (PointField nullable — for customers who allow location sharing),
preferred_language, device_token (for push notifications).

JWT:
Single JWT for all user types. Token payload includes: user_type (CUSTOMER/VENDOR/ADMIN), role.
Separate token serializers for each user type.
```

---

## PROMPT 10.3 — Vendor Module APIs (Public + Vendor-Authenticated)

```
Build all vendor-facing and public vendor APIs.

PUBLIC ENDPOINTS (no auth required):
GET /api/v1/vendors/{slug}/          — public vendor profile (exclude encrypted phone, internal notes)
GET /api/v1/vendors/{slug}/reels/    — active reels ordered by upload_order
GET /api/v1/vendors/{slug}/discounts/active/ — currently active discounts only
GET /api/v1/vendors/{slug}/tags/     — CATEGORY, INTENT, PROMOTION tags only (never SYSTEM)

VENDOR-AUTHENTICATED (IsVendorOwner):
POST  /api/v1/vendors/{slug}/claim/           — claim unclaimed listing
PATCH /api/v1/vendors/{id}/                   — update profile (name, description, logo, cover,
                                                business_hours, phone, website, delivery, pickup)
                                                NEVER allows updating location or subscription here
POST  /api/v1/vendors/{id}/update-location/  — separate endpoint (triggers location_pending_review flag)
POST  /api/v1/vendors/{id}/reels/            — upload reel (enforce video limit by subscription)
PATCH /api/v1/vendors/{id}/reels/{reel_id}/ — update title or reorder
DELETE/api/v1/vendors/{id}/reels/{reel_id}/ — soft delete (is_active=False)

VIDEO LIMIT ENFORCEMENT: Silver=1, Gold=3, Diamond=6, Platinum=unlimited.
Return 403 with upgrade prompt if limit reached.

Analytics events logged ASYNCHRONOUSLY via Celery (never block request cycle):
- Profile views → VIEW event
- Profile taps → TAP event
- Direction requests → DIRECTION_REQUEST event
```

---

## PROMPT 10.4 — Discovery & Search APIs

```
Build the discovery and search engine — the most performance-critical part of the backend.

MAIN SEARCH:
GET /api/v1/discovery/search/?lat={lat}&lng={lng}&radius={m}&q={text}&tags={slugs}

ALGORITHM (build as separate RankingService class — independently testable as pure function):
1. PostGIS ST_DWithin filter FIRST — only rank vendors within requested radius
2. Score each vendor:
   - Text match (30%): PostgreSQL full-text search + trigram similarity on name, category, description
   - Distance score (25%): inverse of distance, normalized within result set
   - Active offer score (15%): binary — discount currently active = full score, else 0
   - Popularity score (15%): total_views + total_profile_taps from LAST 30 DAYS (not all-time)
   - Subscription score (15%): SILVER=0.0, GOLD=0.3, DIAMOND=0.6, PLATINUM=1.0
3. Sort by composite score descending

GET /api/v1/discovery/nearby/?lat={lat}&lng={lng}&radius={m} — simple nearby, no scoring

TAG FILTER API:
GET /api/v1/tags/discovery/?tag_types=CATEGORY,INTENT,PROMOTION,TIME
- TIME tags: computed dynamically based on current time (e.g., "Breakfast" only 6–11 AM)
- PROMOTION tags: only include tags currently active for ≥1 vendor
- Includes "count" field per tag (how many vendors carry it)

VOICE SEARCH:
POST /api/v1/discovery/voice-search/
- Accepts: transcribed_text, latitude, longitude
- Rule-based NLP parser (no ML in Phase 1): "cheap pizza" → {category: pizza, intent: cheap}
- Calls same ranking logic as main search
- Logs full transcribed text to analytics table

VENDOR VOICE BOT QUERY:
POST /api/v1/vendors/{slug}/voice-query/
- Accepts: question (transcribed text)
- Rule-based matching against VoiceBotConfig (menu_items, hours, custom_qa_pairs)
- Returns: { answer_text, confidence: "high"|"medium"|"low" }
- Only available for GOLD+ vendors (vendor_has_feature check)
```

---

## PROMPT 10.5 — Discount & Promotion Engine

```
Build the fully automated discount system.

DISCOUNT CRUD (Vendor auth, IsVendorOwner):
POST   /api/v1/vendors/{id}/discounts/               — create (validate daily happy_hours_allowed)
GET    /api/v1/vendors/{id}/discounts/               — list all (past, current, scheduled)
PATCH  /api/v1/vendors/{id}/discounts/{discount_id}/ — edit (only if discount not yet started)
DELETE /api/v1/vendors/{id}/discounts/{discount_id}/ — cancel future discount (not active ones)

PUBLIC:
GET /api/v1/vendors/{slug}/discounts/active/ — currently active discounts

HAPPY HOUR LIMITS (vendor_has_feature):
Silver: NO happy hour discounts (basic listing discounts only)
Gold: 1 per day, Diamond: 3 per day, Platinum: unlimited

AUTO-ACTIVATION CELERY TASKS:
- discount_scheduler: Runs every minute. Checks start_time/end_time fields.
  Activates discounts that should start, deactivates those that have ended.
  For recurring discounts: checks recurrence_days against current day.
- Subscription expiry: Runs nightly at midnight UTC. Queries all vendors where
  subscription_valid_until < now() and subscription_level != SILVER.
  Sets subscription_level = SILVER. Sends notification. Sends reminders at 7d and 1d before expiry.

TAGAUTO-ASSIGNER (TagAutoAssigner service class):
1. Discount activates → auto-assign PROMOTION tag (Discount Live, Happy Hour, Flash Deal)
2. Discount deactivates → remove that PROMOTION tag
3. Current time window → assign TIME tags globally (Breakfast 6–11 AM, etc.)
4. First 10 views this week → assign SYSTEM tag "New Vendor Boost"
5. Top 10% profile_taps in area this week → assign SYSTEM tag "High Engagement"
```

---

## PROMPT 10.6 — Tag Discovery & Auto-Assignment APIs

```
Build the complete tag management layer for the public platform.

AUTO-ASSIGNMENT SERVICE (TagAutoAssigner):
Build as a background service called from Celery tasks:
1. On discount activate → auto-assign appropriate PROMOTION tag
2. On discount deactivate → remove PROMOTION tag
3. On hourly cron → assign/remove TIME tags based on current time globally
4. On vendor reaching 10 views this week → assign SYSTEM:NewVendorBoost
5. On vendor reaching top 10% taps in area → assign SYSTEM:HighEngagement

VENDOR TAG APIs (Public):
GET /api/v1/vendors/{slug}/tags/ — CATEGORY, INTENT, PROMOTION only. NEVER expose SYSTEM tags publicly.

TAG DISCOVERY (Public):
GET /api/v1/tags/browse/ — grouped tags for discovery UI:
- Category group: Food, Cafe, Bakery, Pizza, Pharmacy, etc.
- Intent group: Cheap, Quick, Healthy, Family Friendly, Student Friendly
- Time group: only tags relevant to current time of day
- Promotion group: only promotion tags currently active for ≥1 vendor
Each tag includes "count" field (vendors currently carrying it).

ADMIN TAG APIs:
POST   /api/v1/admin/tags/              — create
PATCH  /api/v1/admin/tags/{id}/         — edit
DELETE /api/v1/admin/tags/{id}/         — soft delete (is_active=False, never hard delete if in use)
POST   /api/v1/admin/tags/bulk-assign/  — assign multiple tags to multiple vendors (pre-seeding tool)
```

---

## PROMPT 10.7 — Admin Management APIs

```
Build admin-only management APIs for the full platform.

GEOGRAPHIC APIs:
POST /api/v1/admin/geo/countries/ · POST /api/v1/admin/geo/cities/
POST /api/v1/admin/geo/areas/ (supports parent_area for nested sub-areas)
POST /api/v1/admin/geo/landmarks/ (aliases array — critical for voice search accuracy)
GET  /api/v1/admin/geo/hierarchy/ — full geographic tree as nested JSON

VENDOR MANAGEMENT:
GET   /api/v1/admin/vendors/                   — paginated with all filters
GET   /api/v1/admin/vendors/{id}/              — full detail including reels, discounts, tags
PATCH /api/v1/admin/vendors/{id}/verify/       — set is_verified=True with optional note
PATCH /api/v1/admin/vendors/{id}/suspend/      — suspend vendor (hidden from discovery)
POST  /api/v1/admin/vendors/{id}/approve-claim/— approve vendor claim request
POST  /api/v1/admin/vendors/{id}/reject-claim/ — reject claim with required reason
POST  /api/v1/admin/vendors/{id}/approve-location/ — approve location change request
POST  /api/v1/admin/vendors/{id}/reject-location/  — reject location change

CITY LAUNCH:
POST /api/v1/admin/geo/cities/{id}/launch/ — only enabled when launch-readiness all green
```

---

## PROMPT 10.8 — Analytics & Reporting APIs (Vendor + Admin)

```
Build all analytics endpoints for vendor dashboard and admin platform analytics.

VENDOR ANALYTICS (Vendor auth, IsVendorOwner):
GET /api/v1/vendors/{id}/analytics/summary/
  Returns last 7d and last 30d: total views, taps, direction requests, tap-through rate,
  most popular hour, most popular day.

GET /api/v1/vendors/{id}/analytics/reels/
  Per-reel: view count, trend (increasing/decreasing/stable, last 7d).

GET /api/v1/vendors/{id}/analytics/discounts/
  Per-discount: views during active window vs inactive same timeslot.

GET /api/v1/vendors/{id}/analytics/time-heatmap/
  7×24 matrix (days × hours) with view counts.
  DIAMOND + PLATINUM only — return 403 for lower tiers (vendor_has_feature check).

GET /api/v1/vendors/{id}/analytics/recommendations/
  PLATINUM only. Rule-based: find top 3 peak hours with no active discount.
  Suggest running a discount during those windows.

ADMIN PLATFORM ANALYTICS:
GET /api/v1/admin/analytics/platform-overview/
  Daily active searches, voice query volume, total events by type, new vendors registered.

GET /api/v1/admin/analytics/area-heatmap/{city_id}/
  Discovery request density by area within a city (for vendor recruitment prioritization).

GET /api/v1/admin/analytics/search-terms/
  Top 50 most searched text queries (voice search intent analysis).

EVENT INGESTION RULE:
NEVER block an API request to record analytics.
Always dispatch analytics Celery task → return API response immediately.
Analytics accuracy is important, latency is more important.
```

---

## PROMPT 10.9 — Subscription & Package System

```
Build the subscription system and vendor_has_feature utility.

PACKAGE SEEDING:
Management command seeds SILVER, GOLD, DIAMOND, PLATINUM with features + pricing.
Data in DB served via API — NOT hardcoded in application logic.

GET /api/v1/subscriptions/packages/ — Public. Lists all packages with features. Used by Flutter + React.

VENDOR SUBSCRIPTION (Vendor auth):
GET  /api/v1/vendors/{id}/subscription/ — current level, expiry, unlocked features, upgrade options
POST /api/v1/vendors/{id}/subscription/upgrade/ — abstract payment interface (JazzCash/Easypaisa/Stripe)
POST /api/v1/vendors/{id}/subscription/cancel/ — cancel auto-renewal (stays active until expiry)

FEATURE GATING UTILITY (central — no scattered if-else):
vendor_has_feature(vendor, feature_name) -> bool
Feature names: HAPPY_HOUR, VOICE_BOT, SPONSORED_WINDOW, TIME_HEATMAP, PREDICTIVE_RECOMMENDATIONS, EXTRA_REELS
All API endpoints with premium features MUST use this function.
Subscription logic changes only need to be updated in one place.

AUTOMATION:
Celery nightly task (midnight UTC):
- Downgrade expired subscriptions to SILVER
- Send reminder notifications at 7 days and 1 day before expiry
```

---
---

# 11. REACT WEB PORTAL — VENDOR DASHBOARD

> **Extends the React portal from Phase A. Vendors access a different sidebar/navigation than admins.**

---

## PROMPT 11.1 — Vendor Onboarding Wizard & Profile Setup

```
Build the Vendor Dashboard and onboarding wizard.

VENDOR ONBOARDING WIZARD (first login after claim approval — full page overlay, NOT modal):
Step 1: Confirm Business Details (name, description, hours) — pre-filled, vendor reviews + edits.
Step 2: Add Location — Leaflet map with drag-pin for precise placement.
Step 3: Upload Logo and Cover Photo.
Step 4: Add First Video (optional — "Listings with videos get 3x more views" progress bar encouragement).
Step 5: Review Your Package — Silver features + what Gold unlocks. Upgrade prompt, never forced.
Step 6: Go Live confirmation.

Progress bar at top. Skippable optional steps. Completed steps show green checkmark.

PROFILE EDIT PAGE (sidebar → Profile):
Business Information: name, description (character count), phone, website.
Business Hours: visual weekly grid — click cells to set open/close per day.
  "Same as yesterday" convenience. Mark specific days as closed.
Service Options: toggle cards for "We offer delivery" + "We offer pickup" with description fields.
Location: map embed with current pin + "Request Location Update" button (goes to admin review).

PROFILE COMPLETENESS WIDGET:
Persistent sidebar widget showing profile completeness % with progress bar.
Lists incomplete items and their point values. Motivates action.
```

---

## PROMPT 11.2 — Discount & Promotion Manager

```
Build the Discount Manager section of the Vendor Dashboard.

MAIN VIEW — Calendar:
Calendar view showing all discounts as colored blocks. Active = solid Babu teal.
Scheduled = dashed border, lighter color. Expired = grey. Toggle to list view.

CREATE/EDIT FLOW — Right-side Drawer:
Step 1 — Type Selection: Large visual cards for each discount type with emoji icons.
Step 2 — Details: Fields conditional on type. Live badge preview showing how it appears to customers.
  Slider/stepper for % value. For BOGO: item selection.
Step 3 — Scheduling: datetime inputs + recurring day-selector (day chips).
  Show tier limits with upgrade prompt (not hard block) for Silver trying to create Happy Hour.
Step 4 — Confirm: summary card + preview. CTA to save.

DISCOUNT PERFORMANCE TABLE:
Columns: Title, Type, Schedule, Views While Active, Status (badge: Active/Scheduled/Expired/Cancelled).

SUBSCRIPTION LIMIT DISPLAY:
Top of discounts tab: "Happy Hours used today: 1/3" (Gold/Diamond).
Silver: "Happy Hours available from Gold plan" with upgrade link.
```

---

## PROMPT 11.3 — Analytics & Reports

```
Build the Analytics section of the Vendor Dashboard.

OVERVIEW (All tiers):
Hero metric: "Your listing was viewed X times this week" — large, clear typography.
Three metric cards: Views (7d), Profile Taps (7d), Direction Requests (7d).
Each: comparison vs previous period with semantic color indicator (↑ teal, ↓ red, flat grey).
Bar chart: daily views over last 14 days.

VIDEO PERFORMANCE TABLE (All tiers):
Columns: thumbnail, title, view count, trend indicator. Sorted by view count desc.

TIME-OF-DAY HEATMAP (Diamond + Platinum):
7×24 grid — color-coded view count intensity per day/hour.
Silver + Gold: blurred/locked overlay with upgrade message.

DISCOUNT PERFORMANCE (Gold+):
Per-discount: views during active window vs same timeslot without discount. Side-by-side bar chart.

SMART RECOMMENDATIONS (Platinum):
3 insight cards: "Your peak hour is Thursday 1–2 PM but you have no discount then."
CTA: "Create Discount for This Window" — pre-fills discount creation form with that timeslot.

REPORT EXPORT (All tiers): server-side PDF + CSV export.
```

---

## PROMPT 11.4 — Voice Bot Setup

```
Build the Voice Bot Setup section (Gold, Diamond, Platinum vendors only).

FEATURE GATE: Silver vendors see locked icon in sidebar → upgrade prompt with demo audio.

LAYOUT: Split panel — left = configuration form, right = live test area.

LEFT PANEL — Configuration:
Section 1 — Menu Items: dynamic list. Each: name, price, availability toggle.
  Recommend adding ≥5 items for well-configured bot.
  Tier limits: Gold 10 custom pairs, Diamond 20, Platinum unlimited.
Section 2 — Delivery Information: toggle + delivery area, min order, delivery time estimate.
Section 3 — Hours Summary: auto-generated from business_hours (read-only), link to update.
Section 4 — Custom Q&A Pairs: {question, answer} list. Common examples provided.

RIGHT PANEL — Test the Bot:
Microphone button → captures speech → sends to voice-query API → displays text response.
Also plays response via browser text-to-speech.
Shows last 5 test query history.

COMPLETENESS SCORE:
Top of page: "Your voice bot is X% configured."
Missing items listed. 100% = higher confidence responses + better voice search ranking.
```

---

## PROMPT 11.5 — Subscription Management

```
Build the Subscription Management section of the Vendor Dashboard.

CURRENT PLAN CARD:
Plan name + badge, expiry date ("Free — No Expiry" for Silver),
checklist of unlocked features, progress bar: videos used vs allowed, happy hours used today vs allowed.

UPGRADE COMPARISON TABLE:
All 4 plans as columns. Current plan highlighted. Rows = features:
Listing visibility · Videos allowed · Happy Hours/day · Voice Bot · Sponsored Windows ·
Time Heatmap · Predictive Recommendations · Reports level · Price.
Checkmarks (green) = included. X (grey) = not included.
Upgrade CTA only on better-tier columns. Never show downgrade button here.

PAYMENT FLOW (on "Upgrade to Gold" click):
Step 1 — Plan Summary: what's included, price, pro-rated credit for mid-cycle upgrades.
Step 2 — Payment Method: JazzCash, Easypaisa, Card. Secure form.
Step 3 — Confirmation: new plan badge, expiry date, newly unlocked features. Confetti animation.

BILLING HISTORY TABLE:
Date, Plan, Amount, Payment Method, Status (Paid/Failed/Refunded), Invoice download link.

CANCELLATION FLOW:
"Manage Subscription" → downgrade to Silver at next renewal.
Clear message: "You keep [current] features until [expiry date]. After that, you revert to Silver."
Confirm by typing business name.
```

---
---

# 12. FLUTTER MOBILE APP

---

## PROMPT 12.1 — App Architecture & Setup

```
Set up the Flutter mobile app for AirAd. One codebase for both Customer and Vendor users.

TECH STACK: Flutter 3.x, Dart (null-safety). Riverpod (state management).
Go Router (navigation with deep link support). Dio (HTTP client with JWT interceptor).

FOLDER STRUCTURE: Feature-based (each feature folder has its own models, providers, screens, widgets).
Core folder for shared utilities, theme, API client.

THEMING (ThemeData):
Primary: #FF5A5F (Rausch) · Secondary: #00A699 (Babu) · Warning: #FC642D (Arches)
Background: #F7F7F7 · Surface: #FFFFFF · Text primary: #484848 · Text secondary: #767676
Typography: DM Sans (Google Fonts package)
DARK MODE from day one (used outdoors):
  Dark bg: #121212 · Dark surface: #1E1E1E · Brand colors at higher saturation

PERMISSIONS SERVICE:
Handles Location (required for discovery), Microphone (voice search), Camera (AR).
Shows human-readable rationale screen BEFORE system permission dialog.
Fallbacks: location denied → city-level manual selection; mic denied → hide voice search;
camera denied → hide AR, show map as default.

OFFLINE BEHAVIOR:
connectivity_plus to detect network state. Persistent "You're offline — showing cached results" banner.
Cache last successful discovery results for user's location. Never crash or show error screens offline.
```

---

## PROMPT 12.2 — Onboarding & Authentication

```
Build the onboarding and authentication flow.

SPLASH SCREEN:
AirAd logo centered, white background, 2 seconds. Check auth state: valid JWT → discovery screen.
No JWT → onboarding.

ONBOARDING (first-time only, 3 swipeable screens):
Screen 1: "Discover what's around you right now" — AR camera concept illustration.
Screen 2: "Real deals from real nearby shops" — vendor cards with discount badges illustration.
Screen 3: "Talk to find it, walk to get it" — voice search + navigation illustration.
"Skip" top-right on all screens. "Get Started" CTA on last screen.

AUTHENTICATION:
Phone number entry with country code selector (pre-selected by device locale). "Continue" → OTP.

OTP SCREEN:
6 individual digit boxes. Auto-advance on digit entry. Auto-submit when all 6 filled.
60-second countdown for resend. Loading indicator on verify.
Success routing: CUSTOMER → discovery screen. VENDOR (incomplete profile) → vendor setup wizard.
```

---

## PROMPT 12.3 — Home / Discovery Screen

```
Build the Home / Discovery Screen — the core customer experience.

BOTTOM NAVIGATION (Customer mode):
Discover (home) · Map · Tags · Saved · Profile
(Vendor mode): My Business · Discounts · Performance · Profile

DISCOVER TAB LAYOUT:
Top: Search bar (text + microphone icon). Below: horizontal scrollable quick-filter chips
(preset intents: "Cheap", "Open Now", "Nearby"). AR camera button top-right.

VENDOR CARD:
Cover photo (16:9 aspect ratio). Vendor logo (overlapping bottom-left, 40px circle).
Vendor name, category, distance, open/close status chip.
Active discount badge (Rausch red, prominent) if currently running.
Subscription badge (Verified, Premium, Elite) top-right of card.
Video reel preview strip below main card (3 thumbnail squares) if vendor has reels.
Voice bot microphone icon on logo for vendors with voice bot configured.

VENDOR CARD INTERACTIONS:
Tap → Vendor Profile Screen. Long press → quick action bottom sheet: Get Directions, Call, Share.
Swipe right → save to Favorites (heart animation feedback).

INFINITE SCROLL + PAGINATION:
Load 20 vendors at a time. Seamless scroll (never "Load More" button).
Skeleton loader cards at bottom during loading. Pull to refresh with current location.
```

---

## PROMPT 12.4 — Augmented Reality (AR) Camera View

```
Build the AR Camera View — AirAd's signature feature.

ENTRY: AR camera icon button top-right of Discover screen. Full-screen experience.

AR VIEW BEHAVIOR:
Camera + compass/heading sensor + GPS → render floating vendor "bubbles" overlaid on camera feed.
Each bubble: vendor name (bold), distance (e.g., "80m"), discount badge if active (Rausch red).
Bubble size varies slightly by distance — closer = slightly larger (depth perception).
As user rotates phone: bubbles move accordingly. Vendor to north only appears when pointing north.

BUBBLE LIMIT: Show max 5–8 vendor bubbles at once (closest + highest-ranked).
"X more nearby" indicator at bottom prompts list view exploration.

AR INTERACTION:
Tap bubble → Vendor Profile Screen.
List button at bottom → slides up bottom sheet with full vendor list (switch between AR + list without leaving camera).

DEVICE FALLBACK:
No compass/heading sensors or inadequate GPU → automatically switch to flat map view.
One-time message: "AR view is not available on this device. Showing map view instead."

CLOSE BUTTON: X button top-left exits to Discover tab.

PRIVACY: Camera feed processed locally only. No recording or storage of AR sessions.
```

---

## PROMPT 12.5 — Map View

```
Build the Map View tab.

FULL-SCREEN MAP: Google Maps Flutter plugin (or Mapbox). User location as pulsing blue dot.
All nearby vendors as custom map pins.

VENDOR PIN TYPES:
Default pin: Rausch red circle with vendor category icon.
Active discount: larger pin with pulsing animation + discount badge.
Premium/Diamond: gold-outlined pin.
Tap pin → vendor summary card slides up from bottom (mini card: logo, name, distance, discount badge).
Tap card → full Vendor Profile Screen.

RADIUS INDICATOR: Translucent circle showing the current search radius.

MAP CONTROLS: My Location button (bottom-right). Radius selector: 200m / 500m / 1km / 2km.
Filter button (top-right): opens same tag filter sheet as Tags tab.

CLUSTER BEHAVIOR:
Dense areas: cluster pins into count circles. Tap cluster → zoom in to reveal individual pins.

VENDOR LIST TOGGLE:
Bottom of map: a handle that slides up a half-screen vendor list sorted by distance.
This list updates as the map is panned.
```

---

## PROMPT 12.6 — Tag-Based Browsing

```
Build the Tag-Based Browsing tab.

TAG BROWSER SHEET (bottom sheet from Tags tab):
Section 1 — What's happening now? (PROMOTION + TIME tags):
  "Happy Hour Active" "Flash Deal" "Breakfast Spots" etc. as colored chips.
  Orange background on active deal tags.
Section 2 — What do you want? (INTENT tags):
  "Cheap" "Quick" "Healthy" "Family Friendly" "Student Friendly" "Romantic" "Late Night"
  as chips with emoji icons.
Section 3 — What are you looking for? (CATEGORY tags):
  Grid of category cards with icon + name: Food, Pizza, Bakery, Cafe, Pharmacy, Clothing, etc.
Section 4 — Near a specific place? (LOCATION tags for current city):
  Area names and landmark names as flat list. Tap → filter to that area.

MULTI-TAG SELECTION:
Multiple tags combinable. Selected tags appear as chips in persistent filter bar at top.
Each chip has X to deselect. "Clear All" link.

LIVE RESULTS UPDATE:
As tags are selected, discovery screen behind sheet updates in real time.
Floating bubble: "14 vendors match your filters". Close sheet → see filtered results immediately.
```

---

## PROMPT 12.7 — Voice Search & Voice Bot

```
Build the complete voice experience.

VOICE SEARCH (Discovery):
Triggered by microphone icon on Discover screen. Full-screen overlay: centered animated waveform.
Brief prompt: "Say what you're looking for — like 'cheap pizza' or 'open pharmacy nearby'."

After speech: transcribed on-device (speech_to_text Flutter plugin) → show transcription on screen
→ send to POST /api/v1/discovery/voice-search/ → animate overlay down → show discovery results
filtered by interpreted query. Active filter chips show interpreted tags (e.g., "category: pizza, intent: cheap").

Not understood or no vendors: "I couldn't find that nearby. Try 'cheap food' or 'open cafe'."

VENDOR VOICE BOT (Vendor Profile Screen — Gold+ vendors only):
"Ask a question" microphone button. Opens compact voice overlay for that vendor.
After speech: transcribe → POST /api/v1/vendors/{slug}/voice-query/ → show text response in
chat-bubble style (one question, one answer — not a full chat UI) → play response via device TTS.
Show last 3 questions + answers as user continues. "Close" button dismisses.

VOICE BOT INDICATOR ON VENDOR CARD:
Small microphone icon badge on vendor logo for vendors with voice bot configured.
```

---

## PROMPT 12.8 — Vendor Profile Screen

```
Build the Vendor Profile Screen.

STICKY HEADER:
Cover photo (full-width, 220px). Overlaid at bottom: vendor name (bold 22px), open/closed status chip,
distance, subscription badge. Back arrow top-left. Share icon top-right.
Scrolling: vendor logo (64px circle) slides over cover photo, with action row: "Navigate", "Call",
"Ask Bot" (if voice bot available). Rating placeholder: show NOTHING (Phase 1, no ratings — no empty stars).

VIDEO REEL SECTION:
Horizontally scrollable row of 9:16 aspect ratio reel cards. Tap → full-screen video player.
Reels auto-play (silently) when scrolled into view, pause when scrolled out.

ABOUT SECTION: description, address, website link.

HOURS SECTION: compact weekly view. Highlight today's row. Show open/closed based on current time.

ACTIVE DISCOUNTS SECTION:
Active discounts: prominent cards with countdown timer ("Ends in 1h 23m").
Scheduled future discounts: lighter upcoming cards.

LOCATION MAP SECTION:
Small non-interactive map preview with vendor pin + surrounding streets.
"Get Directions" button → opens native navigation (Google Maps or Apple Maps via url_launcher).

SERVICE OPTIONS: "Delivery Available" chip + "Pickup Available" chip. Always show at least one.
```

---

## PROMPT 12.9 — Navigation & Turn-by-Turn Directions

```
Build the in-app navigation experience.
NOTE: AirAd is NOT a full navigation app. Walking-distance directions only. No multi-city routing.

TRIGGER: "Navigate" button on Vendor Profile Screen.

NAVIGATION SCREEN:
Shows a map with the route drawn in Rausch red from the user's current location to the vendor.
Route is walking directions only (max distance where walking makes sense — 2km threshold).
For distances > 2km: show external navigation option instead.

STEP-BY-STEP PANEL:
Bottom sheet showing the current step in large readable text: "Turn right on Jinnah Avenue."
Distance to next turn. Step counter: "Step 2 of 7."
Arrow indicator pointing in the correct direction using compass heading.

ARRIVAL DETECTION:
When within 30m of destination, show "You've arrived!" screen.
Optional "I'm Here" confirmation button (for analytics).

EXTERNAL NAVIGATION FALLBACK:
For complex routes or user preference: "Open in Google Maps" / "Open in Apple Maps" button
via url_launcher with the vendor's GPS coordinates.

GPS TRACKING during navigation: continuous location updates every 2 seconds.
Recalculate route if user deviates by more than 50m.
```

---

## PROMPT 12.10 — Vendor App — Claim & Setup Flow

```
Build the vendor claiming and setup flow within the Flutter app.

VENDOR MODE ACTIVATION:
After "I have a business" selection during role selection, app switches to vendor mode.
Bottom nav changes to: My Business, Discounts, Performance, Profile.

FIND MY BUSINESS SCREEN:
Search bar at top. As vendor types: matching unclaimed listings from DB as a list.
Each result: name, address, "Claimed" or "Unclaimed" badge.
"Register New Business" button at bottom if business not found → submit details for admin review.

CLAIM CONFIRMATION SCREEN:
"Is this your business?" with listing details. "Yes, This Is My Business" CTA + "Not My Business" link.
On confirm: claim request submitted.

PENDING CLAIM STATE:
"Claim Submitted" screen with estimated review time. Pending status bar until admin approves.
Push notifications on claim approval or rejection.

MOBILE VENDOR PROFILE EDIT (after approval — simplified vs web portal):
Focus on: photos (logo + cover), hours (mobile-optimized picker), delivery/pickup toggles.
Complex operations → directed to web portal with a link.
```

---

## PROMPT 12.11 — Vendor App — Discount Management

```
Build the mobile discount management screens.

DISCOUNTS TAB (Vendor bottom nav):
Three sections:
1. Active Right Now: if active discount exists, large live card with green pulsing indicator,
   details, countdown, "Stop Early" button.
2. Upcoming: scheduled discounts with start time countdown.
3. Past: recent discount history with views received during window.

QUICK CREATE DISCOUNT (FAB — floating action button):
Simplified mobile creation bottom sheet:
Type selector: large emoji buttons for each type (easy to tap on mobile).
Duration selector: "Next 30 min", "Next 1 hour", "Next 2 hours", "Custom time".
Value input: large number field.
Start Now toggle: ON = start immediately; OFF = schedule future start.
Save = create immediately. Active section updates in real time.

SUBSCRIPTION LIMIT DISPLAY:
Top of tab: "Happy Hours used today: 1/3" (Diamond).
Silver: "Happy Hours available from Gold plan" with upgrade link.
```

---

## PROMPT 12.12 — Reel / Video Upload System

```
Build the video reel upload system for vendors in Flutter.

REEL MANAGEMENT SCREEN (My Business → Media):
Vertical list of uploaded reels (not a grid — needs title + action space per reel).
Each reel: thumbnail, title, view count, upload date, drag handle for reordering.
Delete button (with confirmation) + edit title button per reel.
Upload limit progress: "1 of 1 used" (Silver) or "3 of 6 uploaded" (Diamond).
Silver at limit: upload button disabled, shows "Upgrade to Gold for 3 videos."

VIDEO UPLOAD FLOW:
"Add Video" → bottom sheet: "Record Now" (opens camera) or "Choose from Gallery"
(image_picker / camera Flutter plugins).

TRIM EDITOR:
Horizontal scrubber with start + end drag handles. Live preview of selected clip.
AirAd maximum: 15 seconds per reel. Minimum: 9 seconds.

UPLOAD CONFIRMATION:
Thumbnail preview (auto-captured from first frame). Title input field. "Upload" button.

UPLOAD PROGRESS:
Chunked upload in background. Persistent progress bar at top during upload.
Upload continues if user navigates away. Notification on completion.

After upload: reel appears immediately in list. "Processing" badge while backend optimizes.
Visible to customers ONLY after processing completes.
```

---
---

# 13. WINDSURF SESSION EXECUTION GUIDE

> **How to run each session. Copy this guide to your README.**

---

## Session Template (Copy-Paste for Every Windsurf Session)

```
=== AIRAD WINDSURF SESSION START ===

[PASTE Prompt 1.1 — Project Identity]
[PASTE Prompt 1.2 — Absolute Prohibitions]
[PASTE Section 14 Final Notes — relevant phase only]

CURRENT SESSION GOAL: Execute Steps [X] through [Y].
PREVIOUSLY COMPLETED: Steps [list]

RULES FOR THIS SESSION:
- Execute steps [X] to [Y] only. Stop after Step [Y].
- Confirm each step: "✓ Step N complete — [one-line summary]"
- If blocked, report and stop. Never skip steps silently.
- Self-check Quality Gate (Prompt 7.1) before marking any step complete.

=== BEGIN STEP [X] ===
```

---

## Phase A Backend — Session Groups

| Session | Steps | Prompts          | Goal                                   |
|---------|-------|------------------|----------------------------------------|
| A-S1    | 1–4   | 1.1, 1.2, 5.1, 5.3 | Docker + Nginx + env               |
| A-S2    | 5–9   | 1.1, 1.2, 3.1, 5.2 | Requirements + Settings + Celery + Core |
| A-S3    | 10–13 | 1.1, 1.2, 3.2, 3.4 | Accounts + Permissions + Auth + Audit |
| A-S4    | 14–17 | 1.1, 1.2, 3.2    | Geo + Tags + Vendors + Imports models  |
| A-S5    | 18–20 | 1.1, 1.2, 3.5–3.9 | All services.py + Serializers + Views |
| A-S6    | 21–23 | 1.1, 1.2, 3.8, 3.10, 3.13 | Import/QA tasks + Health check |
| A-S7    | 24–26 | 1.1, 1.2, 3.3, 5.4, 3.13 | Schemas + Seed + OpenAPI     |
| A-S8    | 27–31 | 1.1, 1.2, 6.1–6.4, 5.2 | All tests + CI pipeline          |

**Gate after A-S8:** `docker-compose up` → `pytest --cov-fail-under=80` → all green → start React.

## Phase A React — Session Groups

| Session | Steps | Prompts             | Goal                               |
|---------|-------|---------------------|------------------------------------|
| A-S9    | 32–33 | 1.1, 1.2, 2.1, 2.2, 4.1 | DLS tokens + base components  |
| A-S10   | 34–35 | 1.1, 1.2, 2.1, 2.2, 4.1 | Layout + shared components    |
| A-S11   | 36–37 | 1.1, 1.2, 4.2–4.6  | Zustand + API clients + Pages 1–5 |
| A-S12   | 38–39 | 1.1, 1.2, 4.7–4.10 | Pages 6–10 + GPS maps + README    |

**Gate after A-S12:** Full Phase A demo working → QA checklist → start Phase B.

## Phase B — Session Groups

| Session | Prompts          | Goal                                        |
|---------|------------------|---------------------------------------------|
| B-S1    | 9.1, 10.1, 10.2  | New models + Customer/Vendor auth           |
| B-S2    | 9.1, 10.3, 10.4  | Vendor APIs + Discovery/Search engine       |
| B-S3    | 9.1, 10.5, 10.6  | Discount engine + Tag auto-assignment       |
| B-S4    | 9.1, 10.7–10.9   | Admin APIs + Analytics + Subscriptions      |
| B-S5    | 9.1, 11.1–11.5   | React Vendor Dashboard (all 5 sections)     |
| B-S6    | 9.1, 12.1–12.6   | Flutter: setup + Auth + Discovery + AR      |
| B-S7    | 9.1, 12.7–12.12  | Flutter: Voice + Vendor screens + Video     |

---

# 14. FINAL NOTES FOR WINDSURF

```
Before starting ANY Windsurf session, always paste Prompts 1.1 + 1.2 + the relevant
constraints below from this section. These apply across BOTH Phase A and Phase B.
See Section 13 (Session Execution Guide) for exact copy-paste session templates.

═══════════════════════════════════════════════════════════════
PHASE A — DATA COLLECTION PORTAL CONSTRAINTS
═══════════════════════════════════════════════════════════════

1. Phase A builds an INTERNAL admin tool — NOT customer-facing, NOT vendor-facing.
   The Phase A portal has NO Flutter app, NO Discovery API, NO subscriptions, NO payments, NO voice bot.

2. All 30 audit gaps (G01–G30) from AirAd_SDLC_Compliance_Audit_Report.md are resolved in this prompt.
   Do NOT revert to patterns from the v1 prompt.

3. The for_roles() class factory is the ONLY RBAC mechanism.
   No django-guardian. No __call__ on permission classes.

4. PostGIS ST_Distance is the ONLY GPS calculation method.
   No degree × constant math ANYWHERE in the codebase.

5. psycopg2 (compiled) in production. NEVER psycopg2-binary.
   GDAL version in Dockerfile must match PostGIS image version exactly.

6. All business logic lives in services.py — NEVER in views.py or serializers.py.

7. Every POST, PATCH, DELETE MUST create an AuditLog entry.
   System/Celery actions use actor=None + actor_label='SYSTEM_CELERY'.
   AuditLog entries are IMMUTABLE — no updates, no deletes ever.

8. Test coverage must be ≥80% enforced by --cov-fail-under=80.
   No test may rely on real external services (mock S3, Google Places, SMTP).

9. celery-beat must always run with replicas: 1 in Docker Compose — never more than one instance.

10. The React portal follows Airbnb DLS strictly:
    Rausch (#FF5A5F) for primary CTAs only (max 1 per view),
    Babu (#00A699) for success/approved states,
    Arches (#FC642D) for warnings/pending states,
    #F7F7F7 page backgrounds, 8px spacing grid, DM Sans typography.
    NEVER hardcode hex values — CSS custom properties only.

═══════════════════════════════════════════════════════════════
PHASE B — FULL PLATFORM ADDITIONAL CONSTRAINTS
═══════════════════════════════════════════════════════════════

11. AirAd is a "Nearby + Now" discovery platform. Phase 1 has NO reviews, ratings,
    chat, social features, or delivery logistics.

12. Free Silver vendors are ALWAYS visible — paid tiers improve ranking, not existence.

13. The ranking algorithm is always:
    Relevance 30% + Distance 25% + Active Offer 15% + Popularity 15% + Subscription 15%.

14. All discount activations/deactivations are AUTOMATIC via Celery — never require manual vendor action.

15. vendor_has_feature() is the ONLY subscription gate — no scattered if-else checks throughout codebase.
    Feature names: HAPPY_HOUR, VOICE_BOT, SPONSORED_WINDOW, TIME_HEATMAP, PREDICTIVE_RECOMMENDATIONS, EXTRA_REELS.

16. The Flutter app handles customer discovery + vendor mobile tasks.
    The React portal handles admin governance + vendor complex configuration.

17. All APIs follow consistent envelope: { success, data, message, errors }

18. All media uploads go to S3-compatible storage — never the application server.
    Photos: stored as s3_key only — presigned URL generated fresh on every read.
    CSV imports: read from S3 in Celery task — NEVER pass file content over broker.

19. AR camera feed is processed LOCALLY only — never uploaded to servers. No recording or storage of AR sessions.

20. Voice search: rule-based NLP parser only (no ML in Phase 1).
    Voice bot: rule-based matching against VoiceBotConfig (no ML in Phase 1).
```

---
*AirAd Master Super Prompt — Unified Edition v4.0 FINAL (Phase A + Phase B)*
*Prepared for Windsurf IDE*
*Phase A: Django 5.x + React 18 + TypeScript 5 (Internal Data Collection Portal)*
*Phase B: Django 5.x + React 18 + Flutter 3.x (Full Public Platform)*
*POST-AUDIT: All 30 compliance gaps resolved. All 7 technical debt risks addressed.*
*v4.0 Changes: Authority Documents disclaimer added · Autonomous execution removed ·*
*Phase B Django extension note added · Session Execution Guide (Section 13) added.*
*Authority: AirAd Specification Documents v1.0 · Compliance Audit v1.0 · Airbnb DLS*
*Status: Production-Ready for Windsurf Session-Based Build Mode*
