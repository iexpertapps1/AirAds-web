# AirAd Frontend — Admin Portal Page Tasks
## Groups F2–F11: Authentication + All 10 Admin Pages
### Phase A — Internal Data Collection Portal

> **Parent Index:** [`TASKS_INDEX.md`](./TASKS_INDEX.md)
> **Prerequisites:** All of `TASKS_FOUNDATION.md` (F0) + `TASKS_DLS_COMPONENTS.md` (F1) complete
> **Last Updated:** 2026-02-22

---

## Priority Summary

| Group | Feature | Priority | Effort |
|---|---|---|---|
| F2 | Authentication (Login + Logout) | P0 | S |
| F3 | Platform Health Dashboard | P1 | L |
| F4 | Geographic Management | P1 | L |
| F5 | Tag Management | P1 | M |
| F6 | Vendor List + Detail | P1 | XL |
| F7 | Import Management | P1 | M |
| F8 | Field Operations | P2 | M |
| F9 | QA Dashboard | P2 | M |
| F10 | Audit Log | P2 | S |
| F11 | User Management | P2 | S |

---

## GROUP F2 — AUTHENTICATION

### TASK-F2-01 · Login Page
**Priority:** P0 | **Effort:** S
**File:** `src/features/auth/components/LoginPage.tsx` | **Route:** `/login` (public)

**API:** `POST /api/v1/auth/login/`
- Request: `{ email: string, password: string }` — JSON body
- Response 200: `{ success: true, data: { tokens: { access, refresh }, user: { id, email, role } } }`
- Response 400/401: `{ success: false, message: string }`

**Form (React Hook Form + Zod):**
- `email`: required + valid email format
- `password`: required, min 1 char

**Post-Login Flow:** store tokens → `authStore.login()` → prefetch profile → navigate to `?redirect` or `/`

**UI Rules:**
- Centered 480px card, AirAd logo, DM Sans font
- Email + Password inputs (password show/hide toggle with `Eye`/`EyeOff`)
- Primary "Sign In" button (full width)
- **No "Forgot Password"** — endpoint does not exist
- **No "Sign Up"** — internal portal only
- Error: display exact API `message` field below form (never generic)

**Acceptance Criteria:**
- [ ] Successful login stores tokens in-memory, redirects to `/` or `?redirect` URL
- [ ] Invalid credentials shows exact API error message
- [ ] Form submits on Enter key from either field
- [ ] Loading state disables button + shows spinner
- [ ] Already-authenticated users visiting `/login` redirected to `/`

---

### TASK-F2-02 · Logout Flow
**Priority:** P0 | **Effort:** XS
**Trigger:** "Sign Out" in TopBar user dropdown

**Flow:**
1. `POST /api/v1/auth/logout/` with `{ refresh: authStore.refreshToken }`
2. `authStore.logout()` — clears all state (regardless of API result)
3. `queryClient.clear()` — removes all cached data
4. Navigate to `/login`
5. Toast: "You have been signed out."

**Acceptance Criteria:**
- [ ] Refresh token blacklisted via API call
- [ ] Auth state + query cache cleared even if API call fails
- [ ] Redirected to `/login` after logout

---

## GROUP F3 — PLATFORM HEALTH DASHBOARD

### TASK-F3-01 · Platform Health Dashboard
**Priority:** P1 | **Effort:** L
**File:** `src/features/dashboard/components/PlatformHealthPage.tsx` | **Route:** `/`

**API Calls:**
- `GET /api/v1/analytics/kpis/` — `staleTime: 5min`, `refetchInterval: 60_000`
- `GET /api/v1/audit/?page_size=10` — recent activity (SUPER_ADMIN, ANALYST only)
- `GET /api/v1/health/` — system status (public, no auth)

**Page Sections (all show skeleton cards/rows during load):**

1. **Hero KPI Row** — 6 metric cards with sparklines (Recharts `LineChart`): total_vendors, QC pending, QC needs_review, imports this week, field visits this week, active drift flags. Restricted to SUPER_ADMIN + ANALYST — show "Access restricted" placeholder for other roles.

2. **Vendor QC Status Donut** — Recharts `PieChart`. Segments: PENDING/APPROVED/REJECTED/NEEDS_REVIEW/FLAGGED. Click segment → navigate to `/vendors?qc_status={status}`.

3. **Import Activity Chart** — Recharts `BarChart`. Period picker: 7d/14d/30d (URL param `?period=7d`).

4. **Recent Activity Feed** — `GET /api/v1/audit/?page_size=10`. Clickable rows → `/system/audit`. Hidden for roles without audit access.

5. **System Health** — `GET /api/v1/health/`. `"healthy"` → green badge, `"degraded"` → amber badge.

**Acceptance Criteria:**
- [ ] All sections show skeleton placeholders during load
- [ ] Auto-refresh every 60s without user interaction
- [ ] Donut segment click navigates to filtered vendor list
- [ ] Period picker persists in URL
- [ ] Non-SUPER_ADMIN/ANALYST roles see "Access restricted" for KPI cards (not a blank page)

---

## GROUP F4 — GEOGRAPHIC MANAGEMENT

### TASK-F4-01 · Geographic Management Page
**Priority:** P1 | **Effort:** L
**File:** `src/features/geo/components/GeoPage.tsx` | **Route:** `/geo`

**API Calls:**
- `GET /api/v1/geo/countries/` + `POST` (SUPER_ADMIN, CITY_MANAGER)
- `GET /api/v1/geo/cities/` + `GET /api/v1/geo/cities/{id}/` + `POST` + `PATCH` (SUPER_ADMIN, CITY_MANAGER)
- `GET /api/v1/geo/areas/` + `POST` (SUPER_ADMIN, CITY_MANAGER)
- `GET /api/v1/geo/landmarks/` + `POST` (SUPER_ADMIN, CITY_MANAGER)

**Layout:** Two-panel — 320px left tree + flex-grow right detail

**Left Panel:** Collapsible tree Country → City → Area → Landmark. Click node → loads detail in right panel.

**Right Panel:**
- Country: name, code (read-only after creation), city count
- City: editable name + aliases (tag-input chips), Launch Readiness checklist, "Launch City" button (enabled only when all criteria pass), alias count < 3 → warning badge, Leaflet map preview
- Area: name, parent city
- Landmark: name, parent area, GPS (`GPSInput`)

**Create Forms (Drawer):**
- Country: `name` (required), `code` (required, exactly 2 chars — `z.string().length(2)`)
- City: `name` (required), `country` (Select), slug shown read-only
- Area: `name` (required), `city` (Select)
- Landmark: `name` (required), `area` (Select), GPS (`GPSInput`)

**RBAC:** SUPER_ADMIN, CITY_MANAGER see create/edit buttons. All other roles read-only.

**Acceptance Criteria:**
- [ ] Geo tree shows skeleton rows during fetch
- [ ] "Launch City" button disabled until all readiness criteria pass
- [ ] Country `code` validates exactly 2 characters (Zod)
- [ ] Create/edit buttons hidden via `RoleGate` for non-write roles
- [ ] After mutation, tree and detail refresh automatically

---

## GROUP F5 — TAG MANAGEMENT

### TASK-F5-01 · Tag Management Page
**Priority:** P1 | **Effort:** M
**File:** `src/features/tags/components/TagsPage.tsx` | **Route:** `/tags`

**API Calls:**
- `GET /api/v1/tags/` + `POST` (SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY)
- `GET /api/v1/tags/{id}/` + `PATCH` (SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY)
- `DELETE /api/v1/tags/{id}/` (SUPER_ADMIN, CITY_MANAGER) — 204 on success

**⚠️ API Business Rules (enforce in UI):**
- `tag_type = SYSTEM` → read-only for all roles — no create/edit/delete controls
- Slug → read-only after creation (API rejects changes)
- `tag_type = SYSTEM` excluded from create form's type Select

**Table Columns:** Name, Slug (monospace), Tag Type (Badge), Display Order, Is Active (Toggle), Usage Count, Actions

**Tag Type Badge Colors:** CATEGORY→info, INTENT→success, PROMOTION→warning, TIME→neutral, SYSTEM→neutral+lock

**Create/Edit Drawer:**
- Fields: `name` (required), `tag_type` (Select, excludes SYSTEM), `display_order` (number), `is_active` (Toggle)
- Live preview: shows badge as it will appear on vendor cards
- Slug: auto-generated, shown read-only, cannot be edited

**Bulk Actions:** Activate/Deactivate selected — sequential PATCH calls (no bulk endpoint). Progress toast.

**System Tags Section:** Read-only section at bottom, lock icon in Actions column.

**Acceptance Criteria:**
- [ ] SYSTEM tags show lock icon, no edit/delete controls for all roles
- [ ] Slug field read-only in edit drawer
- [ ] SYSTEM type excluded from create form
- [ ] Bulk actions show progress toast during sequential updates
- [ ] Delete requires confirmation modal before DELETE call

---

## GROUP F6 — VENDOR MANAGEMENT

### TASK-F6-01 · Vendor List Page
**Priority:** P1 | **Effort:** L
**File:** `src/features/vendors/components/VendorListPage.tsx` | **Route:** `/vendors`

**API Calls:**
- `GET /api/v1/vendors/?area_id=&city_id=&data_source=&qc_status=&page=&page_size=`
- `PATCH /api/v1/vendors/{id}/qc-status/` — quick approve/reject
- `DELETE /api/v1/vendors/{id}/` — soft-delete (SUPER_ADMIN, CITY_MANAGER)
- `GET /api/v1/geo/cities/` + `GET /api/v1/geo/areas/` — filter dropdowns

**URL State:** All filters in search params. `/vendors?qc_status=PENDING&city_id=uuid&page=1`

**Table Columns:** Logo (avatar), Business Name (→ `/vendors/{id}`), City+Area, QC Status (Badge), Data Source (Badge), GPS (mini-map thumbnail), Phone (masked), Created (relative), Actions

**Filters:** search (debounced 300ms), qc_status (multi-select), data_source, city, area (cascades from city), date range

**Quick Approve/Reject:** Inline buttons → `PATCH /qc-status/`. Optimistic update with rollback on error.

**Bulk Actions:** Bulk Approve, Bulk Flag — sequential PATCH calls, confirmation modal, progress toast.

**RBAC:**
- Quick Approve/Reject: SUPER_ADMIN, CITY_MANAGER, QA_REVIEWER
- Delete: SUPER_ADMIN, CITY_MANAGER
- Create Vendor: SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY

**Acceptance Criteria:**
- [ ] All filters persist in URL — back/forward restores state
- [ ] Area filter cascades from city (clears when city changes)
- [ ] Quick Approve/Reject optimistic update with rollback
- [ ] Phone numbers masked in table
- [ ] Delete requires confirmation modal
- [ ] Skeleton rows shown during load and filter changes

---

### TASK-F6-02 · Vendor Detail Page (6 Tabs)
**Priority:** P1 | **Effort:** XL
**File:** `src/features/vendors/components/VendorDetailPage.tsx` | **Route:** `/vendors/:id`

**API Calls:**
- `GET /api/v1/vendors/{id}/` — vendor detail
- `PATCH /api/v1/vendors/{id}/` — update (SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY)
- `PATCH /api/v1/vendors/{id}/qc-status/` — QC actions (SUPER_ADMIN, CITY_MANAGER, QA_REVIEWER)
- `GET /api/v1/field-ops/?vendor_id={id}` — visit history (Tab 3)
- `GET /api/v1/field-ops/{visit_id}/photos/` — photos (Tab 2)
- `GET /api/v1/tags/` — available tags (Tab 4)

**URL State:** Active tab in URL: `/vendors/{id}?tab=overview`

**Tab 1 — Overview:** Business info + Leaflet map + QC widget + Approve/Reject/Flag buttons (role-gated)
- Reject action: requires `qc_notes` textarea in confirmation Modal before PATCH

**Tab 2 — Field Photos:** Masonry grid, presigned URLs, lightbox, soft-delete. Upload: `POST /photos/upload/` → use `presigned_url` for S3 PUT. `s3_key` NOT in response — never display it.

**Tab 3 — Visit History:** Timeline of field visits. GPS drift alert if distance > 20m (amber badge). Click visit → Drawer with `GPSSplitMap`.

**Tab 4 — Tags:** Table with source label. Add/Remove controls (SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY). SYSTEM tags: lock icon, no remove.

**Tab 5 — Analytics:** Read-only stats from vendor detail response. Only show fields that exist in API response.

**Tab 6 — Internal Notes:** `qc_notes` field. Editable for SUPER_ADMIN + QA_REVIEWER only. **Hidden entirely** for all other roles.

**Acceptance Criteria:**
- [ ] Active tab persists in URL
- [ ] Approve/Reject/Flag only visible to SUPER_ADMIN, CITY_MANAGER, QA_REVIEWER
- [ ] Reject requires `qc_notes` before submitting
- [ ] Photo upload uses presigned URL — `s3_key` never exposed
- [ ] GPS drift > 20m shows amber warning
- [ ] Tab 6 hidden entirely for non-SUPER_ADMIN/QA_REVIEWER
- [ ] Soft-delete redirects to `/vendors` after confirmation

---

## GROUP F7 — IMPORT MANAGEMENT

### TASK-F7-01 · Import Management Page
**Priority:** P1 | **Effort:** M
**File:** `src/features/imports/components/ImportsPage.tsx` | **Route:** `/imports`

**API Calls:**
- `GET /api/v1/imports/` — batch list
- `POST /api/v1/imports/` — upload CSV (`multipart/form-data`, key=`file`)
- `GET /api/v1/imports/{id}/` — batch detail

**RBAC:** SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY only

**Table Columns:** File Name, Status (ImportStatusBadge), Uploaded By, Created At, Vendors Created, Vendors Failed, Actions

**Auto-refresh:** `refetchInterval: (data) => hasActiveJobs(data) ? 10_000 : false` — stops when all DONE/FAILED

**CSV Upload Flow:**
1. Drag-and-drop zone (`.csv` only)
2. PapaParse preview: first 5 rows, missing required columns highlighted red
3. "Upload" → `POST /api/v1/imports/` with `FormData` (key=`file`)
4. Response: `{ data: { id, status: "QUEUED", file_key } }` — `file_key` is S3 key, NOT a URL

**Batch Detail (Drawer):**
- Progress bar (vendors_created + vendors_failed / total_rows)
- Error log table from `data.error_log[]`: row number, field, error message
- "Download Error Log" — client-side CSV export via PapaParse

**Acceptance Criteria:**
- [ ] Auto-refresh stops when all jobs are DONE/FAILED
- [ ] CSV preview shows first 5 rows, missing columns highlighted red
- [ ] Upload accepts `.csv` only
- [ ] `file_key` never displayed as a URL
- [ ] Error log table shows row-level errors

---

## GROUP F8 — FIELD OPERATIONS

### TASK-F8-01 · Field Operations Page
**Priority:** P2 | **Effort:** M
**File:** `src/features/field-ops/components/FieldOpsPage.tsx` | **Route:** `/field-ops`

**API Calls:**
- `GET /api/v1/field-ops/` — visits list (FIELD_AGENT: own only — API enforced, not client-filtered)
- `POST /api/v1/field-ops/` — create visit (SUPER_ADMIN, CITY_MANAGER, FIELD_AGENT)
- `GET /api/v1/field-ops/{id}/` — visit detail
- `GET /api/v1/field-ops/{id}/photos/` — photos
- `POST /api/v1/field-ops/{id}/photos/upload/` — upload photo (SUPER_ADMIN, FIELD_AGENT)

**⚠️ FIELD_AGENT scope:** API enforces own-visits-only. Do NOT add client-side filtering. Do NOT show agent filter to FIELD_AGENT.

**Table Columns:** Vendor Name (→ `/vendors/{id}`), Agent, Visit Date, GPS Confirmed (✓/✗), Photos Count, Drift Alert (amber if >20m), Actions

**Visit Detail Drawer:** Vendor info + notes + `GPSSplitMap` (vendor GPS vs confirmed GPS) + distance delta + photos grid + photo upload

**Agent Overview Table** (SUPER_ADMIN, CITY_MANAGER only): Agent name, total visits, avg photos, drift count. Click → filter by agent.

**Acceptance Criteria:**
- [ ] FIELD_AGENT sees only own visits (API enforced — verified by checking response, not client filter)
- [ ] Agent filter hidden for FIELD_AGENT
- [ ] Split map shows vendor vs confirmed GPS with distance delta
- [ ] Drift alert shown when distance > 20m
- [ ] Photo upload uses presigned URL flow

---

## GROUP F9 — QA DASHBOARD

### TASK-F9-01 · QA Dashboard Page
**Priority:** P2 | **Effort:** M
**File:** `src/features/qa/components/QAPage.tsx` | **Route:** `/qa`

**API Calls:**
- `GET /api/v1/qa/dashboard/` → `{ data: { vendors: Vendor[] } }` — all NEEDS_REVIEW
- `PATCH /api/v1/vendors/{id}/qc-status/` — approve/reject

**RBAC:** SUPER_ADMIN, CITY_MANAGER, QA_REVIEWER

**Page Sections:**

**1. NEEDS_REVIEW Queue Table:**
- Columns: Vendor Name, City, Area, Data Source, Days Waiting (from `created_at`), Actions
- Approve → `PATCH /qc-status/` with `{ qc_status: 'APPROVED' }`
- Reject → Modal with `qc_notes` textarea → PATCH with `{ qc_status: 'REJECTED', qc_notes }`
- Bulk Approve: select multiple → confirmation modal → sequential PATCH calls

**2. GPS Drift Flags Section:**
- Vendors where field visit GPS differs from vendor GPS by > 20m
- Source: cross-reference vendor GPS with field visit `gps_confirmed_point`
- Bulk resolve: mark drift as acknowledged
- "Run GPS Drift Scan Now" button — SUPER_ADMIN only — with loading state + success toast

**3. Duplicate Flags Section:**
- Vendors flagged as potential duplicates
- Compare Modal: side-by-side vendor details
- Merge Wizard (Drawer): select canonical record → confirm data to keep → submit

**Acceptance Criteria:**
- [ ] NEEDS_REVIEW queue shows all vendors from `/api/v1/qa/dashboard/`
- [ ] Reject requires `qc_notes` before submitting
- [ ] "Run GPS Drift Scan Now" only visible to SUPER_ADMIN
- [ ] Merge wizard requires explicit canonical record selection before submit
- [ ] After approve/reject, item removed from queue (optimistic update)

---

## GROUP F10 — AUDIT LOG

### TASK-F10-01 · Audit Log Page
**Priority:** P2 | **Effort:** S
**File:** `src/features/audit/components/AuditLogPage.tsx` | **Route:** `/system/audit`

**API Calls:**
- `GET /api/v1/audit/?action=&actor_label=&target_type=&page=&page_size=`
- Response: paginated, `{ count, data: AuditEntry[] }`
- **POST → 405** — immutable, no write operations

**RBAC:** SUPER_ADMIN, ANALYST only (route guarded + nav item hidden for others)

**Table Columns (44px row height — dense):** Timestamp, Action (code), Actor (email), Target Type, Target ID, Request ID, IP Address, Expand (chevron)

**Row Expansion (inline, not modal):**
- Click row → expands inline to show before/after JSON diff
- `react-diff-viewer-continued` component for side-by-side diff
- Collapse on second click

**Filters (URL params):**
- `action` (text input)
- `actor_label` (email search)
- `target_type` (Select)
- Date range

**Export CSV Button:**
- Max 10,000 records
- Client-side: fetch all pages up to limit, PapaParse unparse to CSV
- Loading state during export

**Rules:**
- No edit or delete controls anywhere — immutable log
- `POST /api/v1/audit/` returns 405 — do not attempt any write operations

**Acceptance Criteria:**
- [ ] Route inaccessible to all roles except SUPER_ADMIN and ANALYST
- [ ] Row expansion shows before/after JSON diff inline (not in modal)
- [ ] No create/edit/delete buttons anywhere on this page
- [ ] Export CSV limited to 10,000 records with loading state
- [ ] All filters persist in URL

---

## GROUP F11 — USER MANAGEMENT

### TASK-F11-01 · User Management Page
**Priority:** P2 | **Effort:** S
**File:** `src/features/system/components/UsersPage.tsx` | **Route:** `/system/users`

**API Calls:**
- `GET /api/v1/auth/users/` — user list (inferred from POST endpoint; list likely exists)
- `POST /api/v1/auth/users/` — create user (SUPER_ADMIN only)
- Response: `{ data: { id: UUID, role: Role } }`

**RBAC:** SUPER_ADMIN only (route guarded + nav item hidden for all other roles)

**Table Columns:** Full Name, Email, Role (Badge), Last Login, Failed Attempts, Account Status (Locked with time remaining)

**Create User Drawer:**
- Fields: `full_name` (required), `email` (required, valid email), `role` (Select — all 7 roles)
- Auto-generated password: shown once in a copyable field after creation (from API response)
- Password field: monospace font, copy-to-clipboard button with `Copy` icon
- After copy: button changes to `Check` icon + "Copied!" for 2s

**Edit User Drawer:**
- Editable fields: `full_name`, `role`, `is_active` (Toggle)
- Email: read-only after creation
- Password: not editable here

**Unlock Account:**
- "Unlock" button visible when account is locked
- Confirmation Modal: "Are you sure you want to unlock {email}?"
- Action: `PATCH /api/v1/accounts/{id}/unlock/` (endpoint referenced in `02_FRONTEND_PLAN.md`)

**Acceptance Criteria:**
- [ ] Route inaccessible to all roles except SUPER_ADMIN
- [ ] Auto-generated password shown once in copyable field after user creation
- [ ] Copy button shows "Copied!" confirmation for 2s
- [ ] Edit drawer only allows `full_name`, `role`, `is_active` changes
- [ ] Unlock confirmation modal required before PATCH call
- [ ] Role Select includes all 7 valid roles

---

## Global Acceptance Criteria (applies to ALL pages above)

- [ ] Zero TypeScript errors (`tsc --noEmit` passes)
- [ ] Zero hardcoded hex/px values — CSS custom properties only
- [ ] All async states handled: loading (skeleton), error (toast + inline message), success
- [ ] All interactive elements keyboard accessible with visible focus ring
- [ ] `aria-*` attributes correct on all tables, forms, modals, drawers
- [ ] `prefers-reduced-motion` respected on all animations
- [ ] No `style={}` props anywhere
- [ ] No `any` type anywhere
- [ ] Role-based UI rendering verified for all 7 roles
- [ ] Responsive at 1280px, 1024px, 768px viewports
- [ ] All mutations show success/error toast
- [ ] All filters persist in URL search params
