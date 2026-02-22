# AirAd Frontend — Audit Report Part 1 of 2
**Sections:** Traceability Matrix · API Mapping · Issues List (Critical + Major + Minor)
**Date:** 2026-02-22 | **Auditor:** Senior PM — Strict Code-Only Execution Verification Mode
**Scope:** Phase A Admin Portal (React 18 + TypeScript 5 + Vite)
**Method:** Direct source-code reading only. No test runs, no prior reports assumed.

> See **Part 2** for RBAC verification, auth flow, error handling, verdict, and fix priority.

---

## Section 1 — Task-to-Code Traceability Matrix

| Task | Requirement | File | Status |
|------|-------------|------|--------|
| F0-01 | Vite + React 18 + TS5 scaffold | `vite.config.ts`, `package.json` | ✅ |
| F0-02 | DLS tokens CSS first import + ThemeProvider | `main.tsx`, `ThemeProvider.tsx` | ✅ |
| F0-03 | Axios client + JWT interceptor (concurrent 401 queue) | `lib/axios.ts` | ✅ |
| F0-04 | Zustand auth store (subscribeWithSelector + immer, in-memory tokens) | `authStore.ts` | ✅ |
| F0-05 | Zustand UI store (toasts, sidebar, theme) | `uiStore.ts` | ⚠️ M-01 |
| F0-06 | TanStack QueryClient + all query key factories | `queryClient.ts`, `queryKeys.ts` | ✅ |
| F0-07 | Router v6 + ProtectedRoute + RequireRole + skip link | `router.tsx` | ✅ |
| F1-01 | Button (variants, sizes, loading, icon, aria-busy) | `Button.tsx` | ✅ |
| F1-02 | Badge + QCStatusBadge + ImportStatusBadge + RoleBadge | `Badge.tsx` | ✅ |
| F1-03 | Input / Select / Textarea / Checkbox / Toggle | all present | ✅ |
| F1-04 | EmptyState | `EmptyState.tsx` | ✅ |
| F1-05 | SkeletonTable | `SkeletonTable.tsx` | ⚠️ m-01 |
| F1-06 | Table (skeleton on load, selectable, pagination, sort) | `Table.tsx` | ⚠️ M-02, m-05 |
| F1-07 | Modal (native `<dialog>`, ESC, aria-labelledby) | `Modal.tsx` | ✅ |
| F1-08 | Drawer (focus trap, Tab/Shift+Tab cycling, ESC) | `Drawer.tsx` | ✅ |
| F1-09 | Toast + ToastProvider (createPortal to document.body) | `Toast.tsx` | ✅ |
| F1-10 | Sidebar (RBAC nav, pill-right active, collapse) | `Sidebar.tsx` | ✅ |
| F1-11 | TopBar (async logout, best-effort POST) | `TopBar.tsx` | ✅ |
| F1-12 | AdminLayout (Sidebar + TopBar + `#main-content`) | `AdminLayout.tsx` | ✅ |
| F1-13 | PageHeader (breadcrumbs with `<Link>`, actions slot) | `PageHeader.tsx` | ✅ |
| F1-14 | FiltersBar | `FiltersBar.tsx` | ✅ |
| F1-15 | GPSInput (GeoJSON↔Leaflet swap, geolocation, drag) | `GPSInput.tsx` | ✅ |
| F1-16 | GPSMap (lazy Leaflet, coord swap, draggable) | `GPSMap.tsx` | ⚠️ m-02 |
| F2-01 | Login page (RHF+Zod, exact API error, redirect, profile prefetch) | `LoginPage.tsx` | ⚠️ C-02 |
| F2-02 | Logout flow (POST then clear, best-effort) | `TopBar.tsx` | ✅ |
| F3 | Platform Health Dashboard (KPIs, charts, 60s poll, health endpoint, alerts) | `PlatformHealthPage.tsx` | ⚠️ C-01, M-03, m-03 |
| F4 | Geographic Management (tree, edit forms, GPSMap, delete confirm, RBAC) | `GeoPage.tsx` | ✅ |
| F5 | Tag Management (SYSTEM lock, slug read-only, bulk toggle, delete confirm) | `TagsPage.tsx` | ✅ |
| F6-01 | Vendor List (URL filters, optimistic QC, phone mask, bulk, create drawer) | `VendorListPage.tsx` | ⚠️ M-04, M-05 |
| F6-02 | Vendor Detail (6 tabs, URL tab, reject modal, notes RBAC, delete) | `VendorDetailPage.tsx` | ⚠️ M-06 |
| F7 | Import Management (multipart, PapaParse preview, 5s poll, error export) | `ImportsPage.tsx` | ⚠️ m-04 |
| F8 | Field Operations (drift badge, visit drawer, GPS split map, photo upload) | `FieldOpsPage.tsx` | ⚠️ C-03, M-07 |
| F9 | QA Dashboard (NEEDS_REVIEW queue, reject modal, optimistic, bulk, drift scan) | `QAPage.tsx` | ⚠️ M-08, M-09 |
| F10 | Audit Log (URL filters, inline diff, CSV export ≤10k) | `AuditLogPage.tsx` | ⚠️ m-06 |
| F11 | User Management (create+temp password, edit, unlock confirm) | `UsersPage.tsx` | ⚠️ C-04 |

**Legend:** ✅ Fully implemented · ⚠️ Partial/violation (see issue ID) · ❌ Missing

---

## Section 2 — API-to-UI Mapping Table

| Endpoint | Method | Component | Payload Correct | Response Handled | Status |
|----------|--------|-----------|-----------------|-----------------|--------|
| `/api/v1/auth/login/` | POST | `LoginPage` | ✅ `{email,password}` | ✅ `data.data.tokens/user` | ✅ |
| `/api/v1/auth/logout/` | POST | `TopBar` | ✅ no body | ✅ best-effort | ✅ |
| `/api/v1/auth/refresh/` | POST | `axios.ts` | ✅ `{refresh}` | ✅ `data.access` (no wrapper) | ✅ |
| `/api/v1/auth/profile/` | GET | — | — | ❌ never called | ❌ C-02 |
| `/api/v1/auth/users/` | GET | `UsersPage` | ✅ | ✅ `r.data.data` | ✅ |
| `/api/v1/auth/users/` | POST | `UsersPage` | ✅ `{full_name,email,role}` | ✅ `resp.data.temp_password` | ✅ |
| `/api/v1/auth/users/{id}/` | PATCH | `UsersPage` | ✅ `{full_name,role,is_active}` | ✅ | ✅ |
| `/api/v1/accounts/{id}/unlock/` | PATCH | `UsersPage` | ✅ | ✅ | ⚠️ C-04 |
| `/api/v1/analytics/kpis/` | GET | `PlatformHealthPage` | ✅ | ✅ `r.data.data` | ✅ |
| `/api/v1/health/` | GET | — | — | ❌ never called | ❌ C-01 |
| `/api/v1/audit/` | GET | `AuditLogPage`, `PlatformHealthPage` | ✅ | ✅ | ✅ |
| `/api/v1/geo/countries/` | GET/POST/PATCH/DELETE | `GeoPage` | ✅ | ✅ | ✅ |
| `/api/v1/geo/cities/` | GET/POST/PATCH/DELETE | `GeoPage` | ✅ | ✅ | ✅ |
| `/api/v1/geo/areas/` | GET/POST/PATCH/DELETE | `GeoPage` | ✅ | ✅ | ✅ |
| `/api/v1/geo/landmarks/` | GET/POST/PATCH/DELETE | `GeoPage` | ✅ | ✅ | ✅ |
| `/api/v1/tags/` | GET/POST | `TagsPage`, `VendorDetailPage` | ✅ | ✅ | ✅ |
| `/api/v1/tags/{id}/` | PATCH/DELETE | `TagsPage` | ✅ | ✅ | ✅ |
| `/api/v1/vendors/` | GET | `VendorListPage` | ✅ paginated | ✅ `r.data` | ✅ |
| `/api/v1/vendors/` | POST | `VendorListPage` | ✅ `{...fields,data_source:'MANUAL'}` | ✅ | ✅ |
| `/api/v1/vendors/{id}/` | GET | `VendorDetailPage` | ✅ | ✅ `r.data.data` | ✅ |
| `/api/v1/vendors/{id}/` | PATCH | `VendorDetailPage` (notes) | ✅ `{qc_notes}` | ✅ | ✅ |
| `/api/v1/vendors/{id}/` | DELETE | `VendorListPage` | ✅ | ✅ | ✅ |
| `/api/v1/vendors/{id}/qc-status/` | PATCH | `VendorListPage`, `VendorDetailPage`, `QAPage` | ✅ `{qc_status,qc_notes?}` | ✅ optimistic | ✅ |
| `/api/v1/vendors/{id}/photos/` | GET | `VendorDetailPage` | ✅ | ✅ | ✅ |
| `/api/v1/vendors/{id}/photos/{pid}/` | DELETE | `VendorDetailPage` | ✅ | ✅ | ✅ |
| `/api/v1/vendors/{id}/visits/` | GET | `VendorDetailPage` | ✅ | ✅ | ✅ |
| `/api/v1/vendors/{id}/tags/` | GET/POST | `VendorDetailPage` | ✅ `{tag_id}` | ✅ | ✅ |
| `/api/v1/vendors/{id}/tags/{vtid}/` | DELETE | `VendorDetailPage` | ✅ | ✅ | ✅ |
| `/api/v1/vendors/{id}/analytics/` | GET | `VendorDetailPage` | ✅ | ✅ | ✅ |
| `/api/v1/imports/` | GET | `ImportsPage` | ✅ | ✅ `r.data.data` | ✅ |
| `/api/v1/imports/` | POST | `ImportsPage` | ✅ `multipart/form-data` key=`file` | ✅ | ✅ |
| `/api/v1/imports/{id}/` | GET | `ImportsPage` (drawer 5s poll) | ✅ | ✅ | ✅ |
| `/api/v1/field-ops/` | GET | `FieldOpsPage` | ✅ paginated | ✅ `r.data` | ✅ |
| `/api/v1/field-ops/{id}/photos/upload/` | POST | — | — | ❌ never implemented | ❌ C-03 |
| `/api/v1/qa/dashboard/` | GET | `QAPage` | ✅ | ✅ `r.data.data.vendors` | ✅ |

**Summary:** 30/35 endpoints correctly integrated. 3 endpoints never called (health, profile, field-ops photo upload). 1 endpoint URL unverified (unlock). 1 endpoint correctly removed (invented drift-scan).

---

## Section 3 — Missing / Partial Implementation List

### 🔴 CRITICAL (4 issues)

---

**C-01 — `GET /api/v1/health/` never called**

- **Spec (F3):** Dashboard must call `GET /api/v1/health/` alongside KPIs to display system health status.
- **Code:** `PlatformHealthPage.tsx` only fetches `/api/v1/analytics/kpis/`. `queryKeys.health.status()` exists in `queryKeys.ts` but is never used in any component.
- **Impact:** System health status (uptime, service checks) is invisible to operators. A backend service could be down with no UI indication.
- **Fix:** Add `useQuery({ queryKey: queryKeys.health.status(), queryFn: () => apiClient.get('/api/v1/health/') })` and render a status indicator card in the dashboard.

---

**C-02 — `GET /api/v1/auth/profile/` prefetch missing after login**

- **Spec (F2-01):** "Prefetch `GET /api/v1/auth/profile/` via `queryClient.prefetchQuery`" after successful login.
- **Code (`LoginPage.tsx` `onSuccess`):** Calls `login(data.data.tokens, data.data.user)` then navigates. No `prefetchQuery` call exists anywhere in the file.
- **Impact:** Profile data never pre-warmed. Components depending on the full profile show a loading state on first render after login.
- **Fix:** Add `await queryClient.prefetchQuery({ queryKey: queryKeys.auth.profile(), queryFn: () => apiClient.get('/api/v1/auth/profile/') })` in `onSuccess` before `navigate()`.

---

**C-03 — Field Ops photo upload entirely absent**

- **Spec (F8):** "Photo upload: presigned URL flow — `POST /api/v1/field-ops/{id}/photos/upload/` → use `presigned_url` for S3 PUT."
- **Code:** `FieldOpsPage.tsx` has zero upload functionality. The visit detail drawer shows only text metadata (agent, date, GPS confirmed boolean, drift meters, notes).
- **Impact:** Field agents cannot upload photos through the UI. Core field operations workflow is broken.
- **Fix:** Implement presigned URL upload flow in the visit detail drawer: POST to get presigned URL → PUT file to S3 → invalidate visit query.

---

**C-04 — `UsersPage` calls wrong unlock endpoint namespace**

- **Spec (F11):** Unlock user account via the auth/users resource.
- **Code (`UsersPage.tsx` line ~112):** `apiClient.patch('/api/v1/accounts/${id}/unlock/')` — uses `/api/v1/accounts/` namespace, inconsistent with all other user endpoints at `/api/v1/auth/users/`.
- **Impact:** If the backend unlock endpoint lives at `/api/v1/auth/users/{id}/unlock/`, every unlock call 404s. Account unlock is completely non-functional.
- **Fix:** Verify the correct URL in `airaad_collection.json` and align. If `/api/v1/accounts/{id}/unlock/` is correct per the Postman collection, this is a false positive.

---

### 🟠 MAJOR (9 issues)

---

**M-01 — `uiStore` writes theme to `localStorage` (constraint violation + broken read-back)**

- **Code (`uiStore.ts` line 40):** `localStorage.setItem('airaad-theme', theme)` — theme is written to localStorage but never read back on store initialization. Store always starts with `'light'`, making the write pointless.
- **Constraint:** "No `localStorage` or `sessionStorage`" (applies to all state, not just tokens per spirit of the rule).
- **Impact:** Theme preference is not persisted across sessions (read-back missing), and the write violates the constraint.
- **Fix:** Either remove the write entirely, or add a proper read-back on store init: `theme: (localStorage.getItem('airaad-theme') as Theme) ?? 'light'`.

---

**M-02 — `Table` page-size selector `onChange` does not update page size**

- **Code (`Table.tsx` lines 221–223):**
  ```tsx
  onChange={() => {
    pagination.onPageChange(1);
  }}
  ```
  The `select` element's `onChange` fires but only resets to page 1 — it never reads `e.target.value` to change the actual page size.
- **Impact:** Page size control is non-functional. Users see the dropdown but selecting a different option has no effect on the data set size returned from the API.
- **Fix:** Add `onPageSizeChange` callback to `PaginationProps`, wire `onChange={(e) => pagination.onPageSizeChange(Number(e.target.value))}`, and update all pages that use `Table` with pagination.

---

**M-03 — `PlatformHealthPage` KPI cards not gated by `RoleGate`**

- **Spec (F3):** "KPI cards restricted to SUPER_ADMIN + ANALYST — use `RoleGate`, show 'Access restricted' placeholder for other roles."
- **Code:** All KPI cards, charts, alerts, and activity feed render for all authenticated roles with no `RoleGate` wrapping.
- **Impact:** RBAC violation. `FIELD_AGENT` and `SUPPORT` users see sensitive operational metrics they should not have access to.
- **Fix:** Wrap KPI section in `<RoleGate allowedRoles={['SUPER_ADMIN', 'ANALYST']} fallback={<p className={styles.restricted}>Access restricted</p>}>`.

---

**M-04 — `VendorListPage` city/area cascade filter not implemented**

- **Spec (F6-01):** "Area filter cascades from city (clear area when city changes)."
- **Code:** Only `qc_status` and `data_source` filters exist. No city filter, no area filter, no cascade logic. `queryKeys.ts` `VendorFilters` interface has `area_id` and `city_id` fields — confirming these were planned but never built.
- **Impact:** City managers cannot filter vendors by their territory. Core city manager workflow gap.
- **Fix:** Add city `Select` (populated from `GET /api/v1/geo/cities/`) → area `Select` (populated based on selected city from `GET /api/v1/geo/areas/?city_id=X`) to `FiltersBar`, wired to URL params `city_id`/`area_id`.

---

**M-05 — `VendorListPage` quick Reject fires without `qc_notes` modal**

- **Spec (F6-02):** "Reject action: requires `qc_notes` textarea in Modal before PATCH."
- **Code (`VendorListPage.tsx` line ~248):** Reject button calls `qcMutation.mutate({ id: v.id, status: 'REJECTED' })` directly — no modal, no notes field.
- **Impact:** Vendors can be rejected without a reason, violating the QC workflow contract. Inconsistent with `VendorDetailPage` and `QAPage` which both require notes.
- **Fix:** Add a reject modal to `VendorListPage` (same pattern as `VendorDetailPage`) that requires `qc_notes` before submitting.

---

**M-06 — `VendorDetailPage` has no delete button or soft-delete flow**

- **Spec (F6-02):** "Soft-delete: confirmation modal → DELETE → redirect to `/vendors`."
- **Code:** No delete button, no delete confirmation modal, no DELETE mutation in `VendorDetailPage.tsx`. Delete only exists in `VendorListPage`.
- **Impact:** Admins must navigate back to the list to delete a vendor they are currently viewing. Spec non-compliance.
- **Fix:** Add delete button (SUPER_ADMIN + CITY_MANAGER only via `RoleGate`) with confirmation modal and `navigate('/vendors')` on success.

---

**M-07 — `FieldOpsPage` visit detail drawer has no GPS split map**

- **Spec (F8):** "Visit detail: `GPSSplitMap` component (vendor GPS vs confirmed GPS)."
- **Code:** Visit drawer renders a `<dl>` with text fields only. No map is rendered at all.
- **Impact:** GPS drift cannot be visually verified by city managers — they see only a drift number, not a map comparison showing where the vendor is vs where the agent confirmed.
- **Fix:** Implement split-map view (two `GPSMap` instances side-by-side) in the visit detail drawer, using vendor GPS from the vendor record and confirmed GPS from the visit record.

---

**M-08 — `QAPage` "Run GPS Drift Scan Now" button missing**

- **Spec (F9):** "'Run GPS Drift Scan Now': SUPER_ADMIN only, loading state + success toast."
- **Code:** No such button exists in `QAPage.tsx`.
- **Note:** If no valid drift-scan endpoint exists in `airaad_collection.json`, this must be formally descoped. As written, the spec requires it.
- **Fix:** Verify endpoint in Postman collection; if valid, implement SUPER_ADMIN-only button with `useMutation`, loading state, and success toast.

---

**M-09 — `QAPage` GPS Drift Flags + Duplicate Flags + Merge Wizard absent**

- **Spec (F9):** "Merge wizard: user must explicitly select canonical record before submit."
- **Code:** No merge wizard, no duplicate flag UI, no GPS drift flag UI in `QAPage.tsx`. The page only shows the NEEDS_REVIEW queue.
- **Impact:** QA reviewers cannot resolve duplicate vendors or GPS drift flags through the UI. Significant QA workflow gap.
- **Fix:** Implement per spec — requires backend endpoints to be confirmed in Postman collection first.

---

### 🟡 MINOR (8 issues)

---

**m-01 — `SkeletonTable` uses `style={{}}` (constraint violation)**

- **Code (`SkeletonTable.tsx` lines 27, 41):** `style={{ width: COLUMN_WIDTHS[i % COLUMN_WIDTHS.length] } as React.CSSProperties}` — dynamic widths applied via inline style.
- **Constraint:** "No `style={}` props. CSS custom properties or CSS modules only. Zero exceptions."
- **Fix:** Use CSS custom property: `style={{ '--skeleton-width': COLUMN_WIDTHS[...] } as React.CSSProperties}` and reference `var(--skeleton-width)` in the CSS module `.cell` rule.

---

**m-02 — `GPSMap` uses `style={{}}` for dynamic height (constraint violation)**

- **Code (`GPSMap.tsx` line 110):** `style={{ height } as React.CSSProperties}` — the `height` prop is applied via inline style.
- **Fix:** Use CSS custom property: `style={{ '--map-height': height } as React.CSSProperties}` and `.map { height: var(--map-height, 240px); }` in the CSS module.

---

**m-03 — Recharts `contentStyle`/`wrapperStyle` are inline objects (constraint violation)**

- **Code:** Multiple `<Tooltip contentStyle={{ background: 'var(--color-white)', ... }} />` and `<Legend wrapperStyle={{ fontSize: 11 }} />` across `PlatformHealthPage.tsx` (5 instances) and `VendorDetailPage.tsx` (2 instances).
- **Note:** These are third-party Recharts API props — the library does not accept CSS class names for these slots. This is an unavoidable constraint of the Recharts API, not a developer error.
- **Fix:** Accept as a known Recharts limitation and document the exception, or replace Recharts with a library that accepts CSS class names for tooltip/legend styling.

---

**m-04 — `ImportsPage` progress bar uses `style={{}}` (constraint violation)**

- **Code (`ImportsPage.tsx` line 328):** `style={{ width: '${pct}%' } as React.CSSProperties}` on the progress fill div.
- **Fix:** Use CSS custom property: `style={{ '--progress': '${pct}%' } as React.CSSProperties}` and `.progressFill { width: var(--progress, 0%); }`.

---

**m-05 — `Table` pagination renders max 7 page buttons (truncation bug)**

- **Code (`Table.tsx` line ~240):** `Array.from({ length: Math.min(totalPages, 7) }, ...)` — only pages 1–7 are rendered as buttons. Pages 8+ are inaccessible via page buttons (only prev/next arrows work).
- **Fix:** Implement ellipsis pagination (1 … 4 5 6 … 50) or add a page number input field.

---

**m-06 — `vite.config.ts` missing ESLint checker option**

- **Spec (F0-01):** `checker({ typescript: true, eslint: { lintCommand: 'eslint ./src' } })`
- **Code (`vite.config.ts`):** `checker({ typescript: true })` — the `eslint` option is absent. ESLint violations will not surface during `vite dev` hot-reload.
- **Fix:** Add `eslint: { lintCommand: 'eslint ./src' }` to the checker config.

---

**m-07 — `devDependencies` use `^` version ranges (constraint violation)**

- **Spec (F0-01):** "Install all dependencies (pinned, no `^` or `~`)."
- **Code (`package.json`):** All devDependencies use `^` ranges (`"eslint": "^9.39.1"`, `"vite": "^7.3.1"`, etc.). Production `dependencies` are correctly pinned.
- **Impact:** Dev builds are not reproducible — `npm install` on a new machine could pull different minor/patch versions of ESLint, Vite, or TypeScript plugins.
- **Fix:** Pin all devDependencies to exact versions (remove `^`).

---

**m-08 — `Table.tsx` column width applied via `style={{}}` (constraint violation)**

- **Code (`Table.tsx` line ~144):** `style={col.width ? ({ width: col.width } as React.CSSProperties) : undefined}` on `<th>`.
- **Fix:** Use CSS custom property `--col-width` and reference via `var(--col-width)` in the CSS module, or use a `data-width` attribute with CSS `attr()`.

---

## Section 4 — Absolute Constraint Violations Summary

| Constraint | Status | Evidence |
|------------|--------|----------|
| No `any` type | ✅ Clean | Grep: zero results in `src/` |
| No `console.log` | ✅ Clean | Grep: zero results; `logger` utility used correctly |
| No `style={}` props | ❌ **11 violations** | `SkeletonTable`(2), `GPSMap`(1), `ImportsPage`(1), `Table`(1), `PlatformHealthPage`(5), `VendorDetailPage`(2) — Recharts slots are API-forced |
| No hardcoded hex values | ✅ Clean | All colors use `var(--color-*)` tokens |
| No other component libraries | ✅ Clean | Only AirAd DLS used |
| No server state in Zustand | ✅ Clean | TanStack Query owns all server data |
| No logic in JSX | ✅ Clean | Logic extracted to hooks/utils |
| No string literal query keys | ✅ Clean | All keys in `queryKeys.ts` |
| No spinners for content areas | ✅ Clean | `SkeletonTable` used everywhere |
| No barrel file abuse | ✅ Clean | Direct imports throughout |
| Tokens in-memory only | ⚠️ Partial | Theme (non-sensitive) written to `localStorage`; never read back — write is pointless |
| No undocumented endpoints | ⚠️ Unverified | `/api/v1/accounts/{id}/unlock/` differs from all other auth endpoints |
| Pinned dependencies | ❌ Violated | All devDependencies use `^` ranges |
| ESLint checker in Vite | ❌ Violated | `eslint` option absent from `vite-plugin-checker` config |

---

## Section 5 — Issue Count by Severity

| Severity | Count | Issue IDs |
|----------|-------|-----------|
| 🔴 Critical | 4 | C-01, C-02, C-03, C-04 |
| 🟠 Major | 9 | M-01 through M-09 |
| 🟡 Minor | 8 | m-01 through m-08 |
| **Total** | **21** | |

---

*Continue to Part 2 for RBAC verification, authentication flow, error handling, production readiness verdict, and recommended fix priority.*
