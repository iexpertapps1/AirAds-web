# AirAd Frontend — Audit Report Part 2 of 2
**Sections:** RBAC Verification · Auth Flow · Error Handling · Verdict · Fix Priority
**Date:** 2026-02-22 | **Auditor:** Senior PM — Strict Code-Only Execution Verification Mode
**Scope:** Phase A Admin Portal (React 18 + TypeScript 5 + Vite)
**Method:** Direct source-code reading only. No test runs, no prior reports assumed.

> See **Part 1** for Traceability Matrix, API Mapping, and full Issues list (C-01 through m-08).

---

## Section 6 — RBAC Verification

### 6.1 Route-Level Guards

| Route | Spec Roles | Router `RequireRole`? | Sidebar Hides Link? | Verdict |
|-------|-----------|----------------------|--------------------|---------| 
| `/` (Dashboard) | All roles | ProtectedRoute only | All 7 roles shown | ✅ |
| `/geo` | SA, CM, DE | ❌ No RequireRole | ✅ SA, CM, DE only | ⚠️ **Gap** |
| `/tags` | SA, CM, DE | ❌ No RequireRole | ✅ SA, CM, DE only | ⚠️ **Gap** |
| `/vendors` | SA, CM, DE, QA, SUP | ❌ No RequireRole | ✅ correct roles | ⚠️ **Gap** |
| `/vendors/:id` | SA, CM, DE, QA, SUP | ❌ No RequireRole | (via /vendors link) | ⚠️ **Gap** |
| `/imports` | SA, CM, DE | ✅ RequireRole | ✅ SA, CM, DE only | ✅ |
| `/field-ops` | SA, CM, FA | ✅ RequireRole | ✅ SA, CM, FA only | ✅ |
| `/qa` | SA, CM, QA | ✅ RequireRole | ✅ SA, CM, QA only | ✅ |
| `/system/audit` | SA, AN | ✅ RequireRole | ✅ SA, AN only | ✅ |
| `/system/users` | SA only | ✅ RequireRole | ✅ SA only | ✅ |

**RBAC Gap — Routes `/geo`, `/tags`, `/vendors`, `/vendors/:id` unguarded at router level.**

A `FIELD_AGENT` or `ANALYST` who knows the URL can navigate directly to these pages — the Sidebar hides the links but URL-based access is unrestricted. For an internal admin portal this is a **Major** security gap. Fix: add `RequireRole` guards in `router.tsx` for these four routes, matching the roles already defined in the Sidebar config.

### 6.2 In-Page RBAC (Action-Level)

| Page | Action | Guard | Correct? |
|------|--------|-------|----------|
| GeoPage | Create/Edit/Delete | `RoleGate` (SA, CM, DE) | ✅ |
| TagsPage | Create/Edit/Delete/Bulk | `RoleGate` (SA, CM, DE) | ✅ |
| VendorListPage | Approve/Reject/Bulk | `RoleGate` (SA, CM, QA) | ✅ |
| VendorListPage | Create Vendor | `RoleGate` (SA, CM, DE) | ✅ |
| VendorDetailPage | QC Status actions | `RoleGate` (SA, CM, QA) | ✅ |
| VendorDetailPage | Internal Notes tab | `RoleGate` (SA, CM) | ✅ |
| PlatformHealthPage | KPI cards / charts | ❌ No `RoleGate` | ❌ **M-03** |
| QAPage | Bulk approve | `RoleGate` (SA, CM, QA) | ✅ |
| UsersPage | All actions | API-enforced (SA only) | ✅ |
| FieldOpsPage | Agent filter | `RoleGate` (SA, CM) | ✅ |

---

## Section 7 — Authentication & Token Flow Verification

| Check | File | Result |
|-------|------|--------|
| Access token stored in Zustand (in-memory) only | `authStore.ts` | ✅ No localStorage/sessionStorage for tokens |
| Refresh token stored in Zustand (in-memory) only | `authStore.ts` | ✅ Confirmed |
| Concurrent 401s trigger exactly one refresh call | `lib/axios.ts` | ✅ `isRefreshing` flag + `failedQueue` pattern correctly implemented |
| Refresh reads `data.access` (not `data.data.access`) | `lib/axios.ts` | ✅ `const newToken = data.access` — no wrapper |
| On refresh failure: logout + clear query cache + redirect `/login` | `lib/axios.ts` | ✅ `queryClient.clear()` + `window.location.href = '/login'` |
| Non-401 errors trigger toast notification | `lib/axios.ts` | ✅ `addToast` called in response interceptor |
| Login stores tokens in `authStore` (not localStorage) | `LoginPage.tsx` | ✅ `authStore.login(tokens, user)` |
| Logout clears `user` + `accessToken` + `refreshToken` | `authStore.ts` | ✅ All three nulled in `logout` action |
| Post-login redirect to `?redirect` param | `LoginPage.tsx` | ✅ `decodeURIComponent(redirect)` used correctly |
| `dls-tokens.css` is first import in `main.tsx` | `main.tsx` | ✅ Line 1 |
| `VITE_API_BASE_URL` validated at startup | `main.tsx` | ✅ Throws if missing |
| Profile prefetch after login | `LoginPage.tsx` | ❌ **Missing — see C-02** |

**Token flow is correctly implemented end-to-end with one gap: profile prefetch (C-02).**

---

## Section 8 — Error Handling & Loading State Verification

| Page | Loading State | Error State | Empty State | Verdict |
|------|--------------|-------------|-------------|---------|
| PlatformHealthPage | ✅ `SkeletonTable` | ✅ Axios interceptor toast | ✅ Sections hidden | ✅ |
| GeoPage | ✅ `SkeletonTable` | ✅ Toast | ✅ Empty detail panel | ✅ |
| TagsPage | ✅ `Table` → `SkeletonTable` | ✅ Toast | ✅ `EmptyState` | ✅ |
| VendorListPage | ✅ `Table` → `SkeletonTable` | ✅ Toast | ✅ `EmptyState` | ✅ |
| VendorDetailPage | ✅ `SkeletonTable` per tab | ✅ "Not found" fallback | ✅ Per-tab `EmptyState` | ✅ |
| ImportsPage | ✅ `Table` → `SkeletonTable` | ✅ Toast | ✅ `EmptyState` | ✅ |
| FieldOpsPage | ✅ `Table` → `SkeletonTable` | ✅ Toast | ✅ `EmptyState` | ✅ |
| QAPage | ✅ `Table` → `SkeletonTable` | ✅ Toast | ✅ "Queue is clear" | ✅ |
| AuditLogPage | ✅ `Table` → `SkeletonTable` | ✅ Toast | ✅ `EmptyState` | ✅ |
| UsersPage | ✅ `Table` → `SkeletonTable` | ✅ Toast | ✅ `EmptyState` | ✅ |

**No spinners used for content areas — `SkeletonTable` used consistently throughout. Error handling is global via Axios interceptor with per-mutation rollback where optimistic updates are used.**

### Optimistic Update Rollback Coverage

| Page | Action | Optimistic? | Rollback on Error? |
|------|--------|-------------|-------------------|
| VendorListPage | QC status (approve/reject) | ✅ | ✅ `onError` restores previous data |
| VendorDetailPage | QC status | ✅ | ✅ `onError` restores previous data |
| QAPage | Individual approve/reject | ✅ | ✅ `onError` restores previous data |
| QAPage | Bulk approve | ❌ (uses `invalidateQueries`) | N/A — full refetch |
| TagsPage | Bulk activate/deactivate | ❌ (sequential PATCH + refetch) | N/A — full refetch |
| VendorListPage | Bulk approve/flag | ❌ (sequential PATCH + refetch) | N/A — full refetch |

---

## Section 9 — Production Readiness Verdict

### **VERDICT: ❌ NO-GO**

---

### What blocks production:

**4 Critical issues must be resolved before any production deployment:**

| # | Issue | Why Blocking |
|---|-------|-------------|
| C-01 | `GET /api/v1/health/` never called | Operators have no system health visibility. Silent backend failures. |
| C-02 | Profile prefetch missing post-login | Spec non-compliance. Profile-dependent components show loading flash. |
| C-03 | Field Ops photo upload entirely absent | Core field agent workflow is broken. `POST /api/v1/field-ops/{id}/photos/upload/` never called. |
| C-04 | Unlock endpoint URL unverified | `/api/v1/accounts/{id}/unlock/` vs `/api/v1/auth/users/{id}/unlock/` — may be 404ing in production. |

**5 Major issues that significantly degrade the product:**

| # | Issue | Why Significant |
|---|-------|----------------|
| M-02 | Table page-size selector broken | Non-functional UI control — users see a dropdown that does nothing. |
| M-03 | KPI dashboard visible to all roles | RBAC violation — FIELD_AGENT sees sensitive operational metrics. |
| M-04 | No city/area filter on Vendor List | Core city manager workflow missing — cannot filter vendors by territory. |
| M-05 | Vendor reject on list page fires without QC notes | QC workflow contract violated — vendors rejected without reason. |
| RBAC Gap | `/geo`, `/tags`, `/vendors` routes unguarded | URL-based access bypasses all role restrictions for these pages. |

---

### What IS production-ready:

| Area | Status |
|------|--------|
| JWT token flow (in-memory, concurrent 401 handling, refresh, logout) | ✅ |
| All DLS components (Button, Badge, Modal, Drawer, Toast, Table, Sidebar, GPSMap, GPSInput) | ✅ |
| Geographic Management (full CRUD + GPS coordinate handling) | ✅ |
| Tag Management (full CRUD + bulk toggle + SYSTEM lock) | ✅ |
| Import Management (upload, PapaParse preview, 5s poll, error export) | ✅ |
| Audit Log (URL filters, inline diff with react-diff-viewer, CSV export) | ✅ |
| User Management (create + temp password, edit, unlock) | ✅ (pending C-04 URL verification) |
| QA Dashboard (NEEDS_REVIEW queue, approve, reject with notes, bulk approve) | ✅ (minus drift scan + merge wizard) |
| TypeScript strictness (strict, noUncheckedIndexedAccess, exactOptionalPropertyTypes) | ✅ |
| Zero `any` types, zero `console.log` calls | ✅ |
| Accessibility (skip link, aria-live toasts, focus trap in Drawer, aria-sort in Table) | ✅ |

---

## Section 10 — Recommended Fix Priority

| Priority | Issue | Effort | Owner |
|----------|-------|--------|-------|
| **P0 — Ship Blocker** | C-04: Verify unlock URL against `airaad_collection.json` | XS (5 min) | Dev |
| **P0 — Ship Blocker** | C-02: Add profile prefetch in `LoginPage.tsx` `onSuccess` | XS (15 min) | Dev |
| **P0 — Ship Blocker** | C-01: Add `GET /api/v1/health/` query + status card in `PlatformHealthPage` | S (1 hr) | Dev |
| **P0 — Ship Blocker** | RBAC Gap: Add `RequireRole` to `/geo`, `/tags`, `/vendors`, `/vendors/:id` in `router.tsx` | S (30 min) | Dev |
| **P0 — Ship Blocker** | M-03: Wrap KPI section in `RoleGate` in `PlatformHealthPage` | S (30 min) | Dev |
| **P0 — Ship Blocker** | M-05: Add reject modal with `qc_notes` to `VendorListPage` | M (2 hr) | Dev |
| **P1 — High** | M-02: Fix `Table` page-size selector + add `onPageSizeChange` prop | M (2 hr) | Dev |
| **P1 — High** | M-04: Add city/area cascade filter to `VendorListPage` | L (4 hr) | Dev |
| **P1 — High** | M-06: Add delete button + modal to `VendorDetailPage` | S (1 hr) | Dev |
| **P2 — Medium** | C-03: Field Ops photo upload (presigned URL flow) | XL (1 day) | Dev |
| **P2 — Medium** | M-07: GPS split map in `FieldOpsPage` visit drawer | M (3 hr) | Dev |
| **P2 — Medium** | M-01: Fix `uiStore` theme localStorage (remove write or add read-back) | XS (15 min) | Dev |
| **P3 — Low** | M-08/M-09: QA drift scan + merge wizard (verify endpoints first) | XL (2 days) | Dev |
| **P3 — Low** | m-01/m-02/m-04/m-08: Replace `style={{}}` with CSS custom properties | S (2 hr) | Dev |
| **P3 — Low** | m-05: Ellipsis pagination in `Table` | M (2 hr) | Dev |
| **P3 — Low** | m-06: Add ESLint checker to `vite.config.ts` | XS (5 min) | Dev |
| **P3 — Low** | m-07: Pin all devDependencies in `package.json` | XS (10 min) | Dev |
| **Deferred** | m-03: Recharts `contentStyle`/`wrapperStyle` (API-forced, document exception) | — | PM decision |

---

## Appendix — Files Audited

| File | Lines Read | Key Finding |
|------|-----------|-------------|
| `src/main.tsx` | 1–34 | ✅ dls-tokens.css first, VITE_API_BASE_URL validated |
| `src/lib/axios.ts` | 1–109 | ✅ JWT interceptor, concurrent 401 queue, refresh reads `data.access` |
| `src/lib/queryClient.ts` | 1–18 | ✅ staleTime, gcTime, retry, refetchOnWindowFocus |
| `src/queryKeys.ts` | 1–98 | ✅ All factories present, `as const` |
| `src/features/auth/store/authStore.ts` | 1–61 | ✅ In-memory tokens, subscribeWithSelector + immer |
| `src/shared/store/uiStore.ts` | 1–73 | ⚠️ M-01: localStorage write without read-back |
| `src/router.tsx` | 1–118 | ⚠️ 4 routes missing RequireRole |
| `src/shared/hooks/usePermission.ts` | 1–7 | ✅ |
| `src/shared/hooks/useToast.ts` | 1–12 | ✅ |
| `src/shared/hooks/useDebounce.ts` | 1–15 | ✅ |
| `src/shared/components/dls/Button.tsx` | 1–56 | ✅ |
| `src/shared/components/dls/Badge.tsx` | 1–57 | ✅ |
| `src/shared/components/dls/Toast.tsx` | 1–56 | ✅ createPortal to document.body |
| `src/shared/components/dls/ToastProvider.tsx` | 1–2 | ✅ re-export |
| `src/shared/components/dls/Sidebar.tsx` | 1–141 | ✅ RBAC nav, pill-right active |
| `src/shared/components/dls/Modal.tsx` | 1–88 | ✅ native dialog, ESC, aria-labelledby |
| `src/shared/components/dls/Drawer.tsx` | 1–133 | ✅ Full focus trap, Tab/Shift+Tab cycling |
| `src/shared/components/dls/TopBar.tsx` | 1–58 | ✅ Best-effort logout POST |
| `src/shared/components/dls/GPSMap.tsx` | 1–116 | ⚠️ m-02: style={{height}} |
| `src/shared/components/dls/GPSInput.tsx` | 1–156 | ✅ GeoJSON↔Leaflet swap |
| `src/shared/components/dls/Table.tsx` | 1–268 | ⚠️ M-02: page-size broken; m-05: 7-page truncation; m-08: style={{}} |
| `src/shared/components/dls/SkeletonTable.tsx` | 1–50 | ⚠️ m-01: style={{}} |
| `src/shared/components/dls/PageHeader.tsx` | 1–42 | ✅ |
| `src/shared/components/dls/AdminLayout.tsx` | 1–23 | ✅ #main-content, tabIndex=-1 |
| `src/theme/ThemeProvider.tsx` | 1–13 | ✅ data-theme on documentElement |
| `src/shared/types/geo.ts` | 1–11 | ✅ GeoJSON [lng,lat] comment |
| `src/shared/utils/logger.ts` | 1–21 | ✅ Dev-only info/warn, always-on error |
| `src/features/auth/components/LoginPage.tsx` | 1–144 | ⚠️ C-02: no profile prefetch |
| `src/features/dashboard/components/PlatformHealthPage.tsx` | 1–313 | ⚠️ C-01: no health endpoint; M-03: no RoleGate |
| `src/features/geo/components/GeoPage.tsx` | 1–676 | ✅ |
| `src/features/tags/components/TagsPage.tsx` | 1–408 | ✅ |
| `src/features/vendors/components/VendorListPage.tsx` | 1–471 | ⚠️ M-04, M-05 |
| `src/features/vendors/components/VendorDetailPage.tsx` | 1–749 | ⚠️ M-06 |
| `src/features/imports/components/ImportsPage.tsx` | 1–376 | ⚠️ m-04: style={{}} progress bar |
| `src/features/field-ops/components/FieldOpsPage.tsx` | 1–222 | ⚠️ C-03, M-07 |
| `src/features/qa/components/QAPage.tsx` | 1–259 | ⚠️ M-08, M-09 |
| `src/features/audit/components/AuditLogPage.tsx` | 1–305 | ✅ |
| `src/features/system/components/UsersPage.tsx` | 1–389 | ⚠️ C-04: unlock URL unverified |
| `package.json` | 1–53 | ⚠️ m-07: devDeps use ^ ranges |
| `tsconfig.app.json` | 1–35 | ✅ strict + noUncheckedIndexedAccess + exactOptionalPropertyTypes |
| `vite.config.ts` | 1–19 | ⚠️ m-06: ESLint checker missing |
