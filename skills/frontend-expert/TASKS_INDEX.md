# AirAd Frontend — Master Task Index
## Phase A: Admin Portal + Phase B: Vendor Dashboard
### React 18 · TypeScript 5 · Vite · Zustand · TanStack Query · AirAd DLS

> **Governance:** Senior PM · Strict API Alignment · No Backend Changes
> **Source of Truth:** `airaad_collection.json` · `02_FRONTEND_PLAN.md` · `expert-rules.md` · `airaad-design-system.md`
> **Last Updated:** 2026-02-22

---

## File Map

| File | Contents | Phase |
|---|---|---|
| [`TASKS_FOUNDATION.md`](./TASKS_FOUNDATION.md) | Project bootstrap, DLS tokens, Axios+JWT, Zustand stores, TanStack Query, Router | A |
| [`TASKS_DLS_COMPONENTS.md`](./TASKS_DLS_COMPONENTS.md) | All 16 DLS base components + layout components | A |
| [`TASKS_ADMIN_PAGES.md`](./TASKS_ADMIN_PAGES.md) | Auth, Dashboard, Geo, Tags, Vendors, Imports, Field Ops, QA, Audit, Users | A |
| [`TASKS_PHASE_B.md`](./TASKS_PHASE_B.md) | Vendor Dashboard: Profile, Discounts, Analytics, Voice Bot, Subscription | B |

---

## Architecture Overview

### State Ownership (NON-NEGOTIABLE)

| State Type | Owner |
|---|---|
| Auth session (user, role, tokens) | Zustand `authStore` — in-memory only, never localStorage |
| UI state (sidebar, toasts) | Zustand `uiStore` |
| All server data | TanStack Query — never Zustand |
| Form state | React Hook Form + Zod |
| URL filters / pagination / tabs | React Router search params |

### Folder Structure

```
frontend/src/
├── features/
│   ├── auth/           { components, hooks, store, queries, types }
│   ├── dashboard/      { components, hooks, queries, types }
│   ├── geo/            { components, hooks, queries, types }
│   ├── tags/           { components, hooks, queries, types }
│   ├── vendors/        { components, hooks, queries, types }
│   ├── imports/        { components, hooks, queries, types }
│   ├── field-ops/      { components, hooks, queries, types }
│   ├── qa/             { components, hooks, queries, types }
│   ├── audit/          { components, hooks, queries, types }
│   └── system/         { components, hooks, queries, types }
├── shared/
│   ├── components/dls/ { all 16 DLS primitives }
│   ├── hooks/          { useAuth, useToast, useDebounce, usePermission }
│   └── utils/          { formatters, validators, rbac }
├── lib/
│   ├── axios.ts        { Axios instance + JWT interceptor }
│   └── queryClient.ts  { TanStack QueryClient config }
├── theme/
│   ├── dls-tokens.css  { ALL CSS custom properties — imported FIRST }
│   └── ThemeProvider.tsx
├── queryKeys.ts        { ALL query key factories — no string literals elsewhere }
├── router.tsx          { All routes, lazy-loaded }
└── main.tsx            { dls-tokens.css imported FIRST }
```

### JWT Token Flow

```
Login  → { access, refresh } → authStore (in-memory)
Every request → Authorization: Bearer {access}
On 401 → POST /api/v1/auth/refresh/ → { access }  ← SimpleJWT, no data wrapper
  Success → update authStore.accessToken, retry original request
  Failure → authStore.logout(), navigate('/login')
Logout → POST /api/v1/auth/logout/ (blacklists refresh), clear authStore
```

### RBAC Matrix

| Role | Geo Write | Tag Write | Vendor Write | QC Status | Import | Field Ops | QA | Audit | Users |
|---|---|---|---|---|---|---|---|---|---|
| SUPER_ADMIN | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| CITY_MANAGER | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| DATA_ENTRY | ❌ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| QA_REVIEWER | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| FIELD_AGENT | ❌ | ❌ | ❌ | ❌ | ❌ | own only | ❌ | ❌ | ❌ |
| ANALYST | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | read | ❌ |
| SUPPORT | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## API-to-Screen Mapping Table

| Screen | Method | Endpoint | Write Roles | Key Notes |
|---|---|---|---|---|
| Login | POST | `/api/v1/auth/login/` | all | `{ data: { tokens: { access, refresh }, user: { role, email } } }` |
| Logout | POST | `/api/v1/auth/logout/` | all | Blacklists refresh token |
| Token Refresh | POST | `/api/v1/auth/refresh/` | all | `{ access }` — no `data` wrapper (SimpleJWT) |
| Profile | GET | `/api/v1/auth/profile/` | all | `{ data: { email, role } }` |
| Create User | POST | `/api/v1/auth/users/` | SUPER_ADMIN | `{ data: { id, role } }` |
| Health | GET | `/api/v1/health/` | public | `{ status: "healthy" \| "degraded" }` |
| Platform KPIs | GET | `/api/v1/analytics/kpis/` | SUPER_ADMIN, ANALYST | `{ data: { total_vendors, ... } }` |
| List Countries | GET | `/api/v1/geo/countries/` | all read | `{ data: [] }` array |
| Create Country | POST | `/api/v1/geo/countries/` | SUPER_ADMIN, CITY_MANAGER | `code` must be exactly 2 chars |
| List Cities | GET | `/api/v1/geo/cities/` | all read | Paginated |
| Create City | POST | `/api/v1/geo/cities/` | SUPER_ADMIN, CITY_MANAGER | Response includes `slug` |
| Get City | GET | `/api/v1/geo/cities/{id}/` | all read | |
| Update City | PATCH | `/api/v1/geo/cities/{id}/` | SUPER_ADMIN, CITY_MANAGER | |
| List Areas | GET | `/api/v1/geo/areas/` | all read | |
| Create Area | POST | `/api/v1/geo/areas/` | SUPER_ADMIN, CITY_MANAGER | |
| List Landmarks | GET | `/api/v1/geo/landmarks/` | all read | |
| Create Landmark | POST | `/api/v1/geo/landmarks/` | SUPER_ADMIN, CITY_MANAGER | |
| List Tags | GET | `/api/v1/tags/` | all read | |
| Create Tag | POST | `/api/v1/tags/` | SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY | `tag_type` ≠ SYSTEM — API rejects |
| Get Tag | GET | `/api/v1/tags/{id}/` | all read | |
| Update Tag | PATCH | `/api/v1/tags/{id}/` | SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY | SYSTEM tags + slug changes rejected by API |
| Delete Tag | DELETE | `/api/v1/tags/{id}/` | SUPER_ADMIN, CITY_MANAGER | SYSTEM tags rejected; 204 on success |
| List Vendors | GET | `/api/v1/vendors/?area_id=&city_id=&data_source=&qc_status=` | all read | Paginated; `count` field; `is_deleted=false` guaranteed |
| Create Vendor | POST | `/api/v1/vendors/` | SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY | `qc_status=PENDING` on create; `gps_point` is GeoJSON Point |
| Get Vendor | GET | `/api/v1/vendors/{id}/` | all read | `is_deleted=false` guaranteed |
| Update Vendor | PATCH | `/api/v1/vendors/{id}/` | SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY | |
| Delete Vendor | DELETE | `/api/v1/vendors/{id}/` | SUPER_ADMIN, CITY_MANAGER | Soft-delete; subsequent GET returns 404 |
| Update QC Status | PATCH | `/api/v1/vendors/{id}/qc-status/` | SUPER_ADMIN, CITY_MANAGER, QA_REVIEWER | Sets `qc_reviewed_by` + `qc_reviewed_at` |
| List Imports | GET | `/api/v1/imports/` | all read | |
| Upload CSV | POST | `/api/v1/imports/` | SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY | `multipart/form-data`, key=`file`; `{ data: { status: "QUEUED", file_key } }` |
| Get Import | GET | `/api/v1/imports/{id}/` | all read | `status`: QUEUED/PROCESSING/DONE/FAILED; `error_log[]` |
| List Field Visits | GET | `/api/v1/field-ops/` | all read; FIELD_AGENT: own only | |
| Create Field Visit | POST | `/api/v1/field-ops/` | SUPER_ADMIN, CITY_MANAGER, FIELD_AGENT | `gps_confirmed_point` is GeoJSON Point |
| Get Field Visit | GET | `/api/v1/field-ops/{id}/` | all read | |
| List Visit Photos | GET | `/api/v1/field-ops/{id}/photos/` | all read | |
| Upload Visit Photo | POST | `/api/v1/field-ops/{id}/photos/upload/` | SUPER_ADMIN, FIELD_AGENT | `{ data: { presigned_url } }`; `s3_key` NOT exposed |
| QA Dashboard | GET | `/api/v1/qa/dashboard/` | SUPER_ADMIN, CITY_MANAGER, QA_REVIEWER | `{ data: { vendors: [...NEEDS_REVIEW] } }` |
| List Audit Log | GET | `/api/v1/audit/?action=&actor_label=&target_type=&page=&page_size=` | SUPER_ADMIN, ANALYST | Paginated; immutable (POST → 405) |

---

## Priority Classification

| Priority | Definition | Task Groups |
|---|---|---|
| **P0** | Blocks everything else — must ship first | Foundation (F0), DLS Components (F1), Auth (F2) |
| **P1** | Core portal functionality — ships in Phase A | Dashboard (F3), Geo (F4), Tags (F5), Vendors (F6), Imports (F7) |
| **P2** | Operational tools — ships in Phase A | Field Ops (F8), QA (F9), Audit (F10), Users (F11) |
| **P3** | Phase B only | Vendor Dashboard (all of TASKS_PHASE_B.md) |

---

## Implementation Order

```
Week 1  → F0-01 to F0-07 (Foundation)
Week 2  → F1-01 to F1-10 (DLS Components)
Week 3  → F2-01 to F2-02 (Auth) + F3-01 (Dashboard skeleton)
Week 4  → F4-01 (Geo) + F5-01 (Tags)
Week 5  → F6-01 to F6-02 (Vendor List + Detail)
Week 6  → F7-01 (Imports) + F8-01 (Field Ops)
Week 7  → F9-01 (QA) + F10-01 (Audit) + F11-01 (Users)
Week 8  → QA pass, WCAG audit, DLS compliance review
Phase B → After Phase A sign-off
```

---

## Definition of Done (Global — applies to every task)

- [ ] Zero TypeScript errors (`tsc --noEmit` passes)
- [ ] Zero hardcoded hex/px values — CSS custom properties only
- [ ] All async states handled: loading (skeleton), error (toast + inline), success
- [ ] All interactive elements keyboard accessible with visible focus ring
- [ ] `aria-*` attributes correct on all components
- [ ] `prefers-reduced-motion` respected on all animations
- [ ] No `style={}` props anywhere
- [ ] No `any` type anywhere
- [ ] No string literal query keys outside `queryKeys.ts`
- [ ] ESLint passes with zero warnings
- [ ] Role-based UI rendering verified for all 7 roles
- [ ] Responsive at 1280px, 1024px, 768px

---

## DLS Non-Negotiables (from `expert-rules.md`)

| Rule | Enforcement |
|---|---|
| No `any` type | TypeScript strict mode |
| No `style={}` props | ESLint custom rule |
| No hardcoded colors/sizes | ESLint custom rule |
| No other component libraries (MUI, Shadcn, etc.) | Code review |
| Server state never in Zustand | Code review |
| No logic inside JSX | Code review |
| No string literal query keys | ESLint + `queryKeys.ts` |
| Max 1 primary (`--color-rausch`) button per view | Code review |
| `lucide-react` only for icons, stroke-width 1.5 | Code review |
| Tables: skeleton loading only — never spinners | Code review |
