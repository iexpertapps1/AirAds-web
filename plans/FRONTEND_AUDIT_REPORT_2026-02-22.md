# AirAd Frontend — Senior PM Execution Audit Report

**Auditor:** Senior Product Manager | **Date:** 2026-02-22 | **Mode:** Strict Frontend Execution Audit  
**Source of Truth:** `IMPLEMENTATION_PROMPT.md`, `TASKS_FOUNDATION.md`, `TASKS_DLS_COMPONENTS.md`, `TASKS_ADMIN_PAGES.md`, `TASKS_INDEX.md`

---

## 1. Traceability Matrix (Summary by Group)

### F0 — Foundation (88% complete)
| Status | Item |
|---|---|
| ✅ | Vite+React18+TS5 scaffold, all prod deps pinned |
| ✅ | Axios + JWT interceptor, concurrent 401 queue, `data.access` correct |
| ✅ | authStore in-memory only, `subscribeWithSelector`+`immer` |
| ✅ | uiStore: sidebar, toasts, `crypto.randomUUID()`, timer cancellation |
| ✅ | QueryClient config, `queryKeys.ts` all 10 domains |
| ✅ | Router: 11 routes lazy-loaded, `ProtectedRoute`, `PublicOnlyRoute`, `RoleGate`, skip link |
| ⚠️ | `tsconfig.json`: `noUncheckedIndexedAccess` + `exactOptionalPropertyTypes` unverified |
| ⚠️ | DevDeps use `^` ranges (spec: all pinned) |
| ⚠️ | `ThemeProvider` uses `data-theme` attribute — no dark-mode token overrides defined |
| ⚠️ | Husky in devDeps but no `.husky/` directory confirmed |

### F1 — DLS Components (70% complete)
| Status | Item |
|---|---|
| ✅ | Button, Badge (QCStatus/Import/Role), Input/Textarea/Select/Checkbox/Toggle |
| ✅ | EmptyState, SkeletonTable, Table (sortable/paginated/selectable/sticky) |
| ✅ | AdminLayout, FiltersBar, GPSInput (GeoJSON↔Leaflet swap correct) |
| ⚠️ | Modal: `closeOnBackdrop` prop missing; size uses `sm/md/lg` not spec's `confirm/form/detail` |
| ⚠️ | Drawer: focus trap incomplete — only first button focused; Tab cycling not enforced |
| ⚠️ | Sidebar: RBAC mismatches (see §3-M08); QC Queue badge missing; collapsed tooltip missing |
| ⚠️ | TopBar: no `POST /api/v1/auth/logout/`; no breadcrumb; no notification bell; no dropdown |
| ⚠️ | PageHeader: breadcrumb uses `<a href>` not `<Link>` — full page reload |
| ⚠️ | GPSMap: basic map only — `GPSSplitMap` and `ChoroplethMap` not implemented |
| ❌ | ToastProvider: not rendered via React Portal — inside main tree (spec: `document.body`) |

### F2 — Authentication (60% complete)
| Status | Item |
|---|---|
| ✅ | Login page: form, Zod, exact API error, `?redirect` param, `PublicOnlyRoute` |
| ❌ | Profile not prefetched after login (`queryClient.prefetchQuery` never called) |
| ❌ | Logout never calls `POST /api/v1/auth/logout/` — refresh token never blacklisted |

### F3 — Platform Health Dashboard (20% complete)
| Status | Item |
|---|---|
| ✅ | `GET /api/v1/analytics/kpis/` fetched, MetricCard + BarChart rendered |
| ❌ | `refetchInterval: 60_000` missing |
| ❌ | `GET /api/v1/health/` not called |
| ❌ | `GET /api/v1/audit/?page_size=10` (recent activity) not called |
| ❌ | KPI cards not restricted to SUPER_ADMIN + ANALYST |
| ❌ | Donut chart (QC status breakdown) not implemented |
| ❌ | Donut segment click → `/vendors?qc_status=` not implemented |
| ❌ | Period picker (7d/14d/30d) in URL not implemented |
| ❌ | System health badge not implemented |

### F4 — Geographic Management (45% complete)
| Status | Item |
|---|---|
| ✅ | Two-panel layout, collapsible tree, RBAC on create buttons, query invalidation |
| ✅ | Country code `z.string().length(2)` |
| ❌ | Right panel: shows only type+ID — no editable fields, no Launch City, no aliases, no map |
| ❌ | City PATCH (edit) not implemented |
| ❌ | Aliases tag-input chip component not implemented |

### F5 — Tag Management (78% complete)
| Status | Item |
|---|---|
| ✅ | Tag list, SYSTEM lock, slug read-only, SYSTEM excluded from create type, delete modal |
| ❌ | Bulk activate/deactivate: `selectedIds` tracked but no bulk action UI or sequential PATCH |

### F6 — Vendor Management (38% complete)
| Status | Item |
|---|---|
| ✅ | Vendor list: pagination, URL filters, optimistic approve/reject, phone masked |
| ✅ | Vendor detail: 6 tabs with URL persistence, Tab 6 role-gated |
| ✅ | Tab 1 Overview: business info, reject requires `qc_notes` |
| ❌ | Create Vendor: button has no `onClick` — no drawer, no mutation |
| ❌ | City/area cascade filter not implemented |
| ❌ | Bulk Approve/Flag: `selectedIds` tracked but no handler |
| ❌ | Tab 1: no Leaflet map of vendor location |
| ❌ | Tab 2 Field Photos: placeholder only |
| ❌ | Tab 3 Visit History: placeholder only |
| ❌ | Tab 4 Tags: placeholder only |
| ❌ | Tab 5 Analytics: placeholder only |
| ❌ | Tab 6 Notes: textarea renders but no PATCH save mutation |
| ❌ | Soft-delete on detail page: no delete button |

### F7 — Import Management (80% complete)
| Status | Item |
|---|---|
| ✅ | Import list, auto-refresh (stops when all DONE/FAILED), CSV drag-drop, PapaParse preview |
| ✅ | Missing columns highlighted red, batch detail drawer, progress bar, error log, CSV download |
| ❌ | Batch detail never fetches `GET /api/v1/imports/{id}/` — uses stale list data |
| ❌ | No `RoleGate` on page — all roles can access |

### F8 — Field Operations (35% complete)
| Status | Item |
|---|---|
| ✅ | Field visits table, drift badge (>20m), visit detail drawer (text) |
| ⚠️ | Agent filter shown to QA_REVIEWER — spec: SUPER_ADMIN + CITY_MANAGER only |
| ❌ | `GPSSplitMap` in visit detail: component doesn't exist |
| ❌ | Photo upload (presigned URL), create visit, agent overview table: not implemented |

### F9 — QA Dashboard (45% complete)
| Status | Item |
|---|---|
| ✅ | NEEDS_REVIEW queue, approve/reject (optimistic), bulk approve, reject requires `qc_notes` |
| ⚠️ | "Run GPS Drift Scan" calls `POST /api/v1/qa/drift-scan/` — **invented endpoint, not in Postman collection** |
| ❌ | GPS Drift Flags section: not implemented |
| ❌ | Duplicate Flags section + Merge Wizard: not implemented |

### F10 — Audit Log (88% complete)
| Status | Item |
|---|---|
| ✅ | Table, URL filters, inline diff (`react-diff-viewer-continued`), CSV export, no write ops |
| ❌ | No route-level RBAC guard — any authenticated user can access `/system/audit` |

### F11 — User Management (90% complete)
| Status | Item |
|---|---|
| ✅ | User list, create drawer, auto-generated password shown once, copy button, edit drawer, unlock modal |
| ❌ | No route-level RBAC guard — any authenticated user can access `/system/users` |

---

## 2. API Integration Verification

| Endpoint | Method | Status | Issue |
|---|---|---|---|
| `/api/v1/auth/login/` | POST | ✅ | |
| `/api/v1/auth/logout/` | POST | ❌ | Never called |
| `/api/v1/auth/refresh/` | POST | ✅ | `data.access` correct |
| `/api/v1/auth/profile/` | GET | ❌ | Never prefetched |
| `/api/v1/auth/users/` | GET/POST | ✅ | |
| `/api/v1/auth/users/{id}/` | PATCH | ✅ | |
| `/api/v1/accounts/{id}/unlock/` | PATCH | ✅ | |
| `/api/v1/analytics/kpis/` | GET | ✅ | Missing `refetchInterval` |
| `/api/v1/health/` | GET | ❌ | Not called |
| `/api/v1/geo/countries/` | GET/POST | ✅ | |
| `/api/v1/geo/cities/` | GET/POST | ✅ | PATCH missing |
| `/api/v1/geo/cities/{id}/` | GET/PATCH | ❌ | Not implemented |
| `/api/v1/geo/areas/` | GET/POST | ✅ | |
| `/api/v1/geo/landmarks/` | GET/POST | ✅ | |
| `/api/v1/tags/` | GET/POST | ✅ | |
| `/api/v1/tags/{id}/` | GET/PATCH/DELETE | ✅ | |
| `/api/v1/vendors/` | GET | ✅ | |
| `/api/v1/vendors/` | POST | ❌ | Button exists, no mutation |
| `/api/v1/vendors/{id}/` | GET/PATCH | ✅ | |
| `/api/v1/vendors/{id}/` | DELETE | ✅ | List page only; missing on detail |
| `/api/v1/vendors/{id}/qc-status/` | PATCH | ✅ | |
| `/api/v1/imports/` | GET/POST | ✅ | multipart/form-data correct |
| `/api/v1/imports/{id}/` | GET | ❌ | Drawer uses stale list data |
| `/api/v1/field-ops/` | GET | ✅ | |
| `/api/v1/field-ops/` | POST | ❌ | Not implemented |
| `/api/v1/field-ops/{id}/photos/upload/` | POST | ❌ | Not implemented |
| `/api/v1/qa/dashboard/` | GET | ✅ | |
| `/api/v1/qa/drift-scan/` | POST | ❌ | **Invented — not in Postman collection** |
| `/api/v1/audit/` | GET | ✅ | |

---

## 3. Gap Analysis

### 🔴 CRITICAL (7 — blocks production)

| ID | Gap | File | Risk |
|---|---|---|---|
| C-01 | Logout never calls `POST /api/v1/auth/logout/` | `TopBar.tsx` | Security: refresh tokens never blacklisted |
| C-02 | Route-level RBAC not enforced on 5 restricted pages | `router.tsx` | Any authenticated user bypasses access control |
| C-03 | Vendor Detail Tabs 2–5 are static placeholders | `VendorDetailPage.tsx` | 4 of 6 tabs non-functional |
| C-04 | `GPSSplitMap` component does not exist | DLS | GPS comparison workflow impossible |
| C-05 | Create Vendor flow not implemented | `VendorListPage.tsx` | Primary data entry broken |
| C-06 | `POST /api/v1/qa/drift-scan/` is an invented endpoint | `QAPage.tsx` | Will 404; violates "No undocumented endpoints" |
| C-07 | `ToastProvider` not in React Portal | `Toast.tsx` | z-index failures in production |

### 🟠 MAJOR (10 — significant feature deficiency)

| ID | Gap | File |
|---|---|---|
| M-01 | Dashboard: 6 of 9 sections missing | `PlatformHealthPage.tsx` |
| M-02 | Geo right panel shows only type+ID — no editable detail | `GeoPage.tsx` |
| M-03 | Tags bulk activate/deactivate not implemented | `TagsPage.tsx` |
| M-04 | Vendor list missing city/area cascade filter | `VendorListPage.tsx` |
| M-05 | Vendor list bulk Approve/Flag not implemented | `VendorListPage.tsx` |
| M-06 | QA: GPS Drift Flags + Duplicate Flags + Merge Wizard missing | `QAPage.tsx` |
| M-07 | Field Ops: photo upload, create visit, agent overview missing | `FieldOpsPage.tsx` |
| M-08 | Sidebar RBAC mismatches (Dashboard, Audit Log, Field Ops nav items) | `Sidebar.tsx` |
| M-09 | Import batch detail never fetches live `GET /api/v1/imports/{id}/` | `ImportsPage.tsx` |
| M-10 | Vendor Tab 6 notes textarea has no save mutation | `VendorDetailPage.tsx` |

### 🟡 MINOR (8 — polish / compliance)

| ID | Gap | File |
|---|---|---|
| m-01 | `tsconfig.json` missing `noUncheckedIndexedAccess` + `exactOptionalPropertyTypes` | `tsconfig.json` |
| m-02 | DevDeps use `^` ranges (spec: all pinned) | `package.json` |
| m-03 | `GPSMap.tsx` uses `style={{ height }}` — violates "No `style={}` props" | `GPSMap.tsx` |
| m-04 | `ImportsPage.tsx` progress bar uses `style={{ width }}` — same violation | `ImportsPage.tsx` |
| m-05 | Drawer focus trap incomplete — Tab cycling not enforced | `Drawer.tsx` |
| m-06 | TopBar missing breadcrumb, notification bell, user dropdown | `TopBar.tsx` |
| m-07 | PageHeader breadcrumb uses `<a href>` not `<Link>` | `PageHeader.tsx` |
| m-08 | Sidebar QC Queue badge + collapsed tooltip not implemented | `Sidebar.tsx` |

---

## 4. Production Readiness Score

| Group | Weight | Completion | Weighted |
|---|---|---|---|
| F0 Foundation | 15% | 88% | 13.2 |
| F1 DLS Components | 15% | 70% | 10.5 |
| F2 Auth | 10% | 60% | 6.0 |
| F3 Dashboard | 8% | 20% | 1.6 |
| F4 Geo | 8% | 45% | 3.6 |
| F5 Tags | 7% | 78% | 5.5 |
| F6 Vendors | 15% | 38% | 5.7 |
| F7 Imports | 7% | 80% | 5.6 |
| F8 Field Ops | 5% | 35% | 1.8 |
| F9 QA | 5% | 45% | 2.3 |
| F10 Audit | 5% | 88% | 4.4 |
| F11 Users | 5% | 90% | 4.5 |
| **TOTAL** | **100%** | | **64.7 / 100** |

---

## 5. Risk Assessment

| Risk | Severity | Description |
|---|---|---|
| Refresh token never blacklisted on logout | 🔴 Critical | Stolen tokens remain valid indefinitely after logout |
| RBAC bypass via direct URL | 🔴 Critical | No route-level guards on 5 restricted pages |
| Invented API endpoint | 🔴 Critical | `/qa/drift-scan/` will 404 in production |
| 4 vendor detail tabs are placeholders | 🔴 Critical | Core portal workflow non-functional |
| `GPSSplitMap` missing | 🟠 High | GPS verification broken across Field Ops + Vendor detail |
| Dashboard auto-refresh missing | 🟠 High | Stale KPI data on landing page |
| `ToastProvider` not in Portal | 🟠 High | z-index failures when modals/drawers open |
| `style={}` prop violations | 🟡 Medium | Violates absolute constraint; may fail ESLint in CI |
| Sidebar RBAC mismatches | 🟡 Medium | Wrong nav items shown to wrong roles |

---

## 6. Required Fix Actions (Priority Order)

### Immediate — Before Any Testing
1. **[C-01]** Add `POST /api/v1/auth/logout/` call in `TopBar.tsx` before clearing auth state
2. **[C-02]** Add route-level `RoleGate` in `router.tsx` for `/imports`, `/field-ops`, `/qa`, `/system/audit`, `/system/users`
3. **[C-06]** Remove `POST /api/v1/qa/drift-scan/` — find correct endpoint in Postman collection or remove button
4. **[C-07]** Wrap `ToastProvider` in `ReactDOM.createPortal(toasts, document.body)`

### Sprint 1 — Core Feature Completion
5. **[C-03]** Implement Vendor Detail Tabs 2–5 (Photos, Visits, Tags, Analytics)
6. **[C-04]** Build `GPSSplitMap` component (two Leaflet instances side-by-side)
7. **[C-05]** Implement Create Vendor drawer with `POST /api/v1/vendors/`
8. **[M-01]** Complete Dashboard: `PieChart` donut, `GET /api/v1/health/`, audit feed, `refetchInterval`, `RoleGate`, period picker
9. **[M-02]** Implement Geo right panel: editable fields, Launch City button, aliases chip input, Leaflet map
10. **[M-06]** Add QA GPS Drift Flags + Duplicate Flags + Merge Wizard

### Sprint 2 — Polish & Compliance
11. **[M-03/M-05]** Implement bulk actions for Tags and Vendors (sequential PATCH)
12. **[M-04]** Add city/area cascade filter to Vendor list
13. **[M-07]** Add Field Ops: create visit, photo upload (presigned URL), agent overview
14. **[M-08]** Fix Sidebar RBAC: Dashboard → all roles; Audit Log → SUPER_ADMIN + ANALYST only
15. **[M-09]** Fetch `GET /api/v1/imports/{id}/` in batch detail drawer
16. **[M-10]** Add save mutation for Vendor Tab 6 notes
17. **[m-03/m-04]** Replace `style={}` props in `GPSMap` and `ImportsPage` with CSS modules
18. **[m-05]** Implement full focus trap in `Drawer`
19. **[m-07]** Replace `<a href>` with `<Link>` in `PageHeader` breadcrumbs
20. **[F2-01]** Add `queryClient.prefetchQuery(queryKeys.auth.profile())` after login

---

## 7. Final Go / No-Go Recommendation

### 🔴 NO-GO — Phase A is NOT production-ready

**Overall Score: 64.7 / 100** (threshold: 95)

**Blockers:**
- 7 critical gaps including a security vulnerability (refresh token never blacklisted) and route-level RBAC bypass
- 4 of 6 vendor detail tabs are static placeholder text
- Platform Health Dashboard (the landing page) is ~20% complete
- `GPSSplitMap` — required by Field Ops and Vendor detail — does not exist
- 2 absolute constraint violations: `style={}` props; invented API endpoint

**What IS production-quality:**
- F0 Foundation: Axios/JWT interceptor, stores, router, query keys — excellent
- F7 Import Management: upload flow, preview, auto-refresh, error log — solid
- F10 Audit Log: table, inline diff, CSV export — complete
- F11 User Management: full CRUD, password reveal, unlock — complete
- F5 Tag Management: core flow complete; only bulk actions missing

**Estimated effort to reach Go:** ~3–4 sprint weeks focused on Vendor Detail tabs, Dashboard completion, GPS components, RBAC hardening, and Field Ops/QA sections.
