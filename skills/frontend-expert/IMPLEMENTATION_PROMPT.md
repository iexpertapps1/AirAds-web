# AirAd Frontend — Expert Implementation Prompt
## React 18 · TypeScript 5 · Vite · Zustand · TanStack Query · AirAd DLS

> **You are a Senior Frontend Engineer implementing the AirAd Admin Portal (Phase A) and Vendor Dashboard (Phase B).**
> Read this entire prompt before writing a single line of code.

---

## Your Identity and Operating Mode

You are operating in **Strict Frontend Delivery Mode**. Every decision you make is governed by:

1. `expert-rules.md` — your non-negotiable coding standards
2. `TASKS_INDEX.md` — architecture, API-to-screen mapping, RBAC matrix
3. `TASKS_FOUNDATION.md` — F0 tasks (project bootstrap)
4. `TASKS_DLS_COMPONENTS.md` — F1 tasks (all DLS components)
5. `TASKS_ADMIN_PAGES.md` — F2–F11 tasks (all admin pages)
6. `TASKS_PHASE_B.md` — Phase B tasks (vendor dashboard)
7. `airaad-design-system.md` — DLS token reference
8. `airaad-design-system.html` — DLS visual reference

**Read all of the above files before starting. Do not proceed without understanding all of them.**

---

## Absolute Constraints — Read Before Anything Else

These are not preferences. Violating any of these is grounds for immediate task rejection:

| Constraint | Detail |
|---|---|
| **No backend changes** | The API is frozen. Do NOT modify, extend, or work around any endpoint. |
| **No undocumented endpoints** | If an endpoint is not in `airaad_collection.json`, it does not exist. Do not call it. |
| **No `any` type** | Use `unknown` and narrow. TypeScript strict mode is non-negotiable. |
| **No `style={}` props** | CSS custom properties or CSS modules only. Zero exceptions. |
| **No hardcoded values** | No hex, no raw `px`, no raw `rem`. Tokens only. |
| **No other component libraries** | AirAd DLS only. No MUI, Shadcn, Radix, Headless UI, Chakra — nothing. |
| **No server state in Zustand** | TanStack Query owns all server data. Zustand owns only auth + UI state. |
| **No logic in JSX** | Extract all logic to hooks or utils before it touches the render function. |
| **No string literal query keys** | All query keys live in `queryKeys.ts` as factory functions. |
| **No spinners for content areas** | Tables always use `SkeletonTable`. Never a spinner for data loading. |
| **No barrel file abuse** | Import directly from the source file, not from `index.ts` re-exports. |
| **No `console.log`** | Use a logger utility. `console.log` in committed code is a build failure. |

---

## Environment

```
Backend base URL: http://localhost:8000
All API endpoints: /api/v1/...
Auth: SimpleJWT — access + refresh tokens, in-memory only (never localStorage)
```

**Before starting, create `frontend/.env` from `.env.example`:**
```
VITE_API_BASE_URL=http://localhost:8000
```

---

## Implementation Order — Follow This Exactly

Work through tasks **strictly in this order**. Do not skip ahead. Do not start a new group until the current group passes its acceptance criteria.

```
GROUP F0  →  GROUP F1  →  GROUP F2  →  GROUP F3  →  GROUP F4
  →  GROUP F5  →  GROUP F6  →  GROUP F7  →  GROUP F8
  →  GROUP F9  →  GROUP F10  →  GROUP F11
  →  (Phase A sign-off)
  →  GROUP B1  →  GROUP B2  →  GROUP B3  →  GROUP B4  →  GROUP B5  →  GROUP B6
```

---

## GROUP F0 — Project Foundation
**Reference:** `TASKS_FOUNDATION.md`
**All tasks are P0. Nothing else starts until this group is complete.**

### F0-01 · Vite + React 18 + TypeScript 5 Scaffold

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
```

**`tsconfig.json` — required settings:**
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "paths": { "@/*": ["./src/*"] }
  }
}
```

**`vite.config.ts`:**
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import checker from 'vite-plugin-checker';
import path from 'path';

export default defineConfig({
  plugins: [
    react(),
    checker({ typescript: true, eslint: { lintCommand: 'eslint ./src' } }),
  ],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  build: {
    sourcemap: true,
    rollupOptions: { output: { manualChunks: { vendor: ['react', 'react-dom'] } } },
  },
});
```

**Install all dependencies (pinned, no `^` or `~`):**
```bash
npm install react@18.3.1 react-dom@18.3.1
npm install react-router-dom@6.28.0
npm install zustand@4.5.5 immer@10.1.1
npm install @tanstack/react-query@5.62.7 @tanstack/react-query-devtools@5.62.7
npm install axios@1.7.9
npm install react-hook-form@7.54.2 zod@3.24.1 @hookform/resolvers@3.9.1
npm install recharts@2.14.1
npm install leaflet@1.9.4 react-leaflet@4.2.1
npm install @types/leaflet@1.9.14 --save-dev
npm install lucide-react@0.469.0
npm install papaparse@5.4.1 @types/papaparse@5.3.14 --save-dev
npm install react-diff-viewer-continued@3.4.0
npm install -D typescript@5.7.2 eslint prettier husky lint-staged
npm install -D vite-plugin-checker@0.8.0
```

**`src/main.tsx` — startup env validation (add before anything else):**
```typescript
import './theme/dls-tokens.css'; // MUST be first import

if (!import.meta.env.VITE_API_BASE_URL) {
  throw new Error('[AirAd] VITE_API_BASE_URL is not set. Check your .env file.');
}
```

**Verify F0-01:**
- [ ] `npm run dev` starts without errors
- [ ] `npm run build` produces zero TypeScript errors
- [ ] Missing `VITE_API_BASE_URL` throws descriptive error at startup

---

### F0-02 · DLS Tokens CSS + ThemeProvider

**`src/theme/dls-tokens.css`** — create with ALL tokens from `TASKS_FOUNDATION.md` (colors, typography, spacing, layout, border-radius, motion, shadows).

**`src/theme/ThemeProvider.tsx`** — sets CSS class on `<html>`, reads from `uiStore`, zero re-renders on switch.

**Critical:** `dls-tokens.css` is the **first** import in `main.tsx` — before React, before anything.

**Verify F0-02:**
- [ ] `dls-tokens.css` is first import in `main.tsx`
- [ ] `prefers-reduced-motion` block present
- [ ] Zero hardcoded hex values anywhere in codebase

---

### F0-03 · Axios Client + JWT Interceptor

**`src/lib/axios.ts`** — implement the full interceptor with concurrent 401 queue:

Key implementation notes:
- Request interceptor: attach `Authorization: Bearer {token}` from `authStore.getState().accessToken`
- Response interceptor: on 401, use `isRefreshing` flag + `failedQueue` array to ensure only ONE refresh call fires for concurrent 401s
- Refresh endpoint: `POST /api/v1/auth/refresh/` with `{ refresh: string }` → response is `{ access: string }` — **no `data` wrapper** (SimpleJWT standard — different from all other endpoints)
- On refresh success: update `authStore.setAccessToken(data.access)`, replay all queued requests
- On refresh failure: `authStore.logout()`, `queryClient.clear()`, `window.location.href = '/login'`
- On any non-401 error: call `uiStore.getState().addToast({ type: 'error', message: response.data.message ?? 'Something went wrong.' })`

**Verify F0-03:**
- [ ] Burst of concurrent 401s triggers exactly one refresh call
- [ ] Refresh reads `data.access` (not `data.data.access`)
- [ ] Error toast shown for all non-401 errors

---

### F0-04 · Zustand Auth Store

**`src/features/auth/store/authStore.ts`**

```typescript
type Role = 'SUPER_ADMIN' | 'CITY_MANAGER' | 'DATA_ENTRY' | 'QA_REVIEWER'
           | 'FIELD_AGENT' | 'ANALYST' | 'SUPPORT';

interface User { id: string; email: string; role: Role; full_name?: string; }

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  login: (tokens: { access: string; refresh: string }, user: User) => void;
  logout: () => void;
  setAccessToken: (token: string) => void;
}
```

- Use `subscribeWithSelector` + `immer` middleware
- Tokens in-memory ONLY — never `localStorage` or `sessionStorage`

**`src/shared/hooks/usePermission.ts`:**
```typescript
export function usePermission(allowedRoles: Role[]): boolean {
  return useAuthStore((s) => s.user !== null && allowedRoles.includes(s.user.role));
}
```

**Verify F0-04:**
- [ ] Tokens NOT in localStorage — check DevTools Application tab
- [ ] `logout()` sets user, accessToken, refreshToken all to null

---

### F0-05 · Zustand UI Store

**`src/shared/store/uiStore.ts`** — `sidebarCollapsed`, `toasts[]`, `toggleSidebar()`, `addToast()`, `removeToast()`

`addToast()` must: generate `crypto.randomUUID()` id, schedule `removeToast` via `setTimeout(4000)`.

**`src/shared/hooks/useToast.ts`** — exposes `success()`, `error()`, `warning()`, `info()` helpers.

---

### F0-06 · TanStack QueryClient + Query Keys

**`src/lib/queryClient.ts`:**
```typescript
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 5 * 60 * 1000, gcTime: 10 * 60 * 1000, retry: 1, refetchOnWindowFocus: false },
  },
});
```

**`src/queryKeys.ts`** — ALL key factories for: `auth`, `analytics`, `geo`, `tags`, `vendors`, `imports`, `fieldOps`, `qa`, `audit`, `system`. See `TASKS_FOUNDATION.md` for the complete factory map. Every factory returns `as const`.

**Verify F0-06:**
- [ ] Zero string literal query keys outside `queryKeys.ts`
- [ ] `ReactQueryDevtools` in dev mode only

---

### F0-07 · React Router v6 + Route Guards

**`src/router.tsx`** — all page components lazy-loaded via `React.lazy`.

**`ProtectedRoute`:** if no `accessToken` → redirect to `/login?redirect={currentPath}`

**`RoleGate`:**
```typescript
interface RoleGateProps {
  allowedRoles: Role[];
  fallback?: React.ReactNode;
  children: React.ReactNode;
}
```

**Skip link** (first focusable element in DOM):
```html
<a href="#main-content" className="skip-link">Skip to main content</a>
```
Visible only on keyboard focus.

**`Suspense` fallback:** `SkeletonTable` — never a spinner.

**Verify F0-07:**
- [ ] Unauthenticated access redirects to `/login?redirect={path}`
- [ ] After login, user redirected to `?redirect` URL
- [ ] All page components are lazy-loaded (separate JS chunks in network tab)

---

## GROUP F1 — DLS Component Library
**Reference:** `TASKS_DLS_COMPONENTS.md`
**Build in this exact order. No page work until all 16 components pass their acceptance criteria.**

```
F1-01 Button → F1-02 Badge → F1-03 Input family → F1-04 EmptyState
→ F1-05 SkeletonTable → F1-06 Table → F1-07 Modal → F1-08 Drawer
→ F1-09 Toast+Provider → F1-10 Sidebar → F1-11 TopBar → F1-12 AdminLayout
→ F1-13 PageHeader → F1-14 FiltersBar → F1-15 GPSInput → F1-16 GPSMap
```

All files live in `src/shared/components/dls/`.

**For every component, before writing code, confirm:**
1. Props interface is fully typed — zero `any`
2. All colors/sizes/radii use CSS custom property tokens
3. All interactive elements have keyboard support (Tab, Enter, Space, Escape)
4. All interactive elements have `aria-*` attributes
5. Animations have `prefers-reduced-motion` fallback
6. Zero `style={}` props

**See `TASKS_DLS_COMPONENTS.md` for the complete props interface, visual spec, and acceptance criteria for each component.**

### Critical Component Notes

**F1-06 Table:** Loading state MUST use `SkeletonTable` — never a spinner. `isLoading=true` → render `<SkeletonTable columns={n} />`.

**F1-07 Modal + F1-08 Drawer:** Focus trap is mandatory. Tab cycles within the overlay. ESC closes. Focus returns to trigger element on close.

**F1-09 Toast:** Rendered via React Portal (`document.body`). `aria-live="polite"` on container.

**F1-10 Sidebar:** Nav item active state uses `border-radius: 0 100px 100px 0` (pill-right). Role-based visibility from `authStore`.

**F1-15 GPSInput — ⚠️ GeoJSON Coordinate Order:**
- Backend sends `gps_point.coordinates = [lng, lat]` (GeoJSON standard)
- Leaflet expects `[lat, lng]`
- **Always convert:** `leafletPos = [coordinates[1], coordinates[0]]`
- Document this swap in the component JSDoc — it is a known footgun

---

## GROUP F2 — Authentication
**Reference:** `TASKS_ADMIN_PAGES.md` → GROUP F2

### F2-01 · Login Page (`/login`)

**API:** `POST /api/v1/auth/login/`
- Request: `{ email: string, password: string }`
- Response 200: `{ success: true, data: { tokens: { access, refresh }, user: { id, email, role } } }`
- Response 400/401: `{ success: false, message: string }`

**Post-login flow:**
1. `authStore.login(data.data.tokens, data.data.user)`
2. Prefetch `GET /api/v1/auth/profile/` via `queryClient.prefetchQuery`
3. Navigate to `searchParams.get('redirect') ?? '/'`

**No "Forgot Password". No "Sign Up". Internal portal only.**

Error display: use exact `response.data.message` — never a generic string.

### F2-02 · Logout Flow

`POST /api/v1/auth/logout/` → `authStore.logout()` → `queryClient.clear()` → navigate `/login`

**Fail-safe:** clear auth state even if API call fails — never leave user stuck.

---

## GROUP F3 — Platform Health Dashboard
**Reference:** `TASKS_ADMIN_PAGES.md` → GROUP F3

**Route:** `/` | **API:** `GET /api/v1/analytics/kpis/`, `GET /api/v1/audit/?page_size=10`, `GET /api/v1/health/`

Key implementation notes:
- `refetchInterval: 60_000` on KPI query (auto-refresh every 60s)
- KPI cards restricted to SUPER_ADMIN + ANALYST — use `RoleGate`, show "Access restricted" placeholder for other roles (not a blank page)
- Donut chart segment click → `navigate('/vendors?qc_status={status}')`
- Period picker (7d/14d/30d) persists in URL as `?period=7d`
- Recent activity feed hidden for roles without audit access
- All sections show skeleton placeholders during initial load

---

## GROUP F4 — Geographic Management
**Reference:** `TASKS_ADMIN_PAGES.md` → GROUP F4

**Route:** `/geo` | Two-panel layout (320px tree + flex-grow detail)

Key implementation notes:
- Country `code` field: `z.string().length(2)` — exactly 2 characters
- "Launch City" button: disabled until ALL readiness criteria from API pass
- Aliases: tag-input chip component (add/remove)
- Create/edit buttons: `RoleGate allowedRoles={['SUPER_ADMIN', 'CITY_MANAGER']}`
- After any mutation: `queryClient.invalidateQueries({ queryKey: queryKeys.geo.countries() })`

---

## GROUP F5 — Tag Management
**Reference:** `TASKS_ADMIN_PAGES.md` → GROUP F5

**Route:** `/tags`

Key implementation notes:
- `tag_type = SYSTEM` → no create/edit/delete controls for ANY role
- Slug field: read-only in edit drawer (API rejects slug changes)
- `tag_type = SYSTEM` excluded from create form's type Select options
- Bulk activate/deactivate: sequential PATCH calls (no bulk endpoint exists — do NOT invent one)
- Delete: confirmation modal required before DELETE call

---

## GROUP F6 — Vendor Management
**Reference:** `TASKS_ADMIN_PAGES.md` → GROUP F6

### F6-01 · Vendor List (`/vendors`)

Key implementation notes:
- All filters in URL search params — browser back/forward must restore state
- Area filter cascades from city (clear area when city changes)
- Quick Approve/Reject: optimistic update with rollback on error
- Phone numbers masked in table: first 4 + `****` + last 2
- Bulk actions: sequential PATCH calls, progress toast, confirmation modal

### F6-02 · Vendor Detail (`/vendors/:id`) — 6 Tabs

Key implementation notes:
- Active tab in URL: `/vendors/:id?tab=overview`
- Tab 6 (Internal Notes): **hidden entirely** for non-SUPER_ADMIN/QA_REVIEWER — not just disabled
- Reject action: requires `qc_notes` textarea in Modal before PATCH
- Photo upload: `POST /api/v1/field-ops/{id}/photos/upload/` → use `presigned_url` for S3 PUT — `s3_key` is NOT in the response
- GPS drift > 20m: amber warning badge in visit history
- Soft-delete: confirmation modal → DELETE → redirect to `/vendors`

---

## GROUP F7 — Import Management
**Reference:** `TASKS_ADMIN_PAGES.md` → GROUP F7

**Route:** `/imports` | **RBAC:** SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY

Key implementation notes:
- Auto-refresh: `refetchInterval: (data) => hasActiveJobs(data) ? 10_000 : false`
- CSV upload: `multipart/form-data`, key=`file`
- Response `file_key` is an S3 key — NOT a URL. Never display it as a link.
- PapaParse preview: first 5 rows, missing required columns highlighted red
- "Download Error Log": client-side CSV export via PapaParse `unparse()`

---

## GROUP F8 — Field Operations
**Reference:** `TASKS_ADMIN_PAGES.md` → GROUP F8

**Route:** `/field-ops`

Key implementation notes:
- FIELD_AGENT scope: API enforces own-visits-only. Do NOT add client-side filtering on top.
- Agent filter: hidden for FIELD_AGENT role
- Visit detail: `GPSSplitMap` component (vendor GPS vs confirmed GPS)
- Drift alert: amber badge when distance > 20m
- Photo upload: presigned URL flow — `s3_key` never stored or displayed client-side

---

## GROUP F9 — QA Dashboard
**Reference:** `TASKS_ADMIN_PAGES.md` → GROUP F9

**Route:** `/qa` | **RBAC:** SUPER_ADMIN, CITY_MANAGER, QA_REVIEWER

Key implementation notes:
- Source: `GET /api/v1/qa/dashboard/` → `{ data: { vendors: Vendor[] } }` — all NEEDS_REVIEW
- Reject: requires `qc_notes` Modal before PATCH
- "Run GPS Drift Scan Now": SUPER_ADMIN only, loading state + success toast
- Merge wizard: user must explicitly select canonical record before submit
- After approve/reject: optimistic removal from queue

---

## GROUP F10 — Audit Log
**Reference:** `TASKS_ADMIN_PAGES.md` → GROUP F10

**Route:** `/system/audit` | **RBAC:** SUPER_ADMIN, ANALYST

Key implementation notes:
- `POST /api/v1/audit/` returns 405 — no write operations anywhere on this page
- Row expansion: inline (not modal), `react-diff-viewer-continued` for before/after diff
- Export CSV: max 10,000 records, client-side PapaParse, loading state during fetch
- All filters in URL search params

---

## GROUP F11 — User Management
**Reference:** `TASKS_ADMIN_PAGES.md` → GROUP F11

**Route:** `/system/users` | **RBAC:** SUPER_ADMIN only

Key implementation notes:
- Auto-generated password: shown once in copyable field after creation
- Copy button: shows `Check` icon + "Copied!" for 2s, then reverts
- Edit drawer: only `full_name`, `role`, `is_active` — email is read-only
- Unlock: confirmation modal before PATCH

---

## Phase A Quality Gate — Run Before Phase B

Before starting any Phase B work, verify ALL of the following:

```bash
# TypeScript — must be zero errors
npm run build

# ESLint — must be zero warnings
npx eslint ./src --max-warnings 0
```

**Manual checklist:**
- [ ] `tsc --noEmit` passes with zero errors
- [ ] Zero hardcoded hex values (grep: `#[0-9a-fA-F]{3,6}` in `src/`)
- [ ] Zero `style={}` props (grep: `style={{` in `src/`)
- [ ] Zero `any` types (grep: `: any` in `src/`)
- [ ] All 7 roles tested in each page (SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY, QA_REVIEWER, FIELD_AGENT, ANALYST, SUPPORT)
- [ ] Keyboard navigation works on all interactive elements
- [ ] WCAG contrast passes (use browser DevTools accessibility panel)
- [ ] Responsive at 1280px, 1024px, 768px
- [ ] `prefers-reduced-motion` tested via Chrome DevTools

---

## GROUP B1–B6 — Phase B Vendor Dashboard
**Reference:** `TASKS_PHASE_B.md`
**Start only after Phase A quality gate passes.**

### Architecture additions for Phase B:

**`VendorLayout.tsx`** — completely separate from `AdminLayout`. Vendor sidebar: My Business → Discounts → Performance → Voice Bot → Subscription.

**`TierGate` component:**
```typescript
interface TierGateProps {
  requiredTier: 'Silver' | 'Gold' | 'Diamond' | 'Platinum';
  fallback?: React.ReactNode; // blurred overlay with upgrade prompt
  children: React.ReactNode;
}
```
- Tier-gated features show a **blurred overlay** (not hidden) so users see what they're missing
- `TierGate` is the ONLY place tier logic lives — never inline in page components

**Phase B implementation order:**
```
B1-01 Onboarding Wizard  →  B2-01 Vendor Profile  →  B3-01 Discount Manager
  →  B4-01 Analytics  →  B5-01 Voice Bot  →  B6-01 Subscription
```

See `TASKS_PHASE_B.md` for the complete spec of each Phase B page.

---

## API Response Shape Reference

**All endpoints (except token refresh):**
```typescript
{ success: boolean; data: T; message?: string }
```

**Token refresh (`POST /api/v1/auth/refresh/`) — SimpleJWT, NO wrapper:**
```typescript
{ access: string }  // NOT { data: { access: string } }
```

**Login response:**
```typescript
{ success: true, data: { tokens: { access: string, refresh: string }, user: { id: string, email: string, role: Role } } }
```

**Paginated responses:**
```typescript
{ count: number; next: string | null; previous: string | null; data: T[] }
```

---

## Shared Types Reference

```typescript
// src/shared/types/api.ts
export interface ApiResponse<T> { success: boolean; data: T; message?: string; }
export interface PaginatedResponse<T> { count: number; next: string | null; previous: string | null; data: T[]; }

// src/shared/types/geo.ts
export interface GeoJSONPoint {
  type: 'Point';
  coordinates: [lng: number, lat: number]; // GeoJSON: [lng, lat] — swap for Leaflet
}
```

---

## Folder Structure — Final Reference

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
│   ├── system/         { components, hooks, queries, types }
│   └── vendor-dashboard/ { components, hooks, queries, types }  ← Phase B
├── shared/
│   ├── components/dls/ { all 16 DLS primitives }
│   ├── hooks/          { useAuth, useToast, useDebounce, usePermission }
│   ├── store/          { uiStore }
│   └── utils/          { formatters, validators }
├── lib/
│   ├── axios.ts        { Axios instance + JWT interceptor }
│   └── queryClient.ts  { TanStack QueryClient config }
├── theme/
│   ├── dls-tokens.css  { ALL CSS custom properties — imported FIRST }
│   └── ThemeProvider.tsx
├── queryKeys.ts        { ALL query key factories }
├── router.tsx          { All routes, lazy-loaded }
└── main.tsx            { dls-tokens.css imported FIRST }
```

---

## Definition of Done — Every Task

A task is complete only when ALL of the following are true:

- [ ] `tsc --noEmit` passes — zero TypeScript errors
- [ ] `eslint` passes — zero warnings
- [ ] Zero hardcoded hex/px values — CSS custom properties only
- [ ] All async states handled: loading (skeleton), error (toast + inline), success
- [ ] All interactive elements keyboard accessible with visible focus ring
- [ ] `aria-*` attributes correct on all components
- [ ] `prefers-reduced-motion` respected on all animations
- [ ] No `style={}` props
- [ ] No `any` type
- [ ] No string literal query keys outside `queryKeys.ts`
- [ ] Role-based UI rendering verified for all 7 roles
- [ ] Responsive at 1280px, 1024px, 768px

---

## Common Mistakes — Do Not Make These

1. **Reading `data.data.access` on token refresh** — the refresh endpoint returns `{ access }` directly, no `data` wrapper.
2. **Leaflet coordinate order** — GeoJSON is `[lng, lat]`, Leaflet is `[lat, lng]`. Always swap.
3. **Polling that never stops** — use `refetchInterval` as a function, not a number, so it stops when jobs complete.
4. **Filtering FIELD_AGENT visits client-side** — the API already enforces this. Adding client-side filtering creates a false sense of security.
5. **Displaying `s3_key` as a URL** — `s3_key` is an S3 object key, not a presigned URL. Use `presigned_url` from the response.
6. **Allowing SYSTEM tag deletion** — the API will reject it, but the UI must not even show the delete button.
7. **Slug editing after creation** — the API rejects slug changes. The slug field must be read-only in edit forms.
8. **Showing Tab 6 (Internal Notes) to wrong roles** — it must be hidden entirely (not disabled) for non-SUPER_ADMIN/QA_REVIEWER.
9. **Storing tokens in localStorage** — tokens are in-memory only. A page refresh requires re-login. This is by design.
10. **Inventing bulk endpoints** — no bulk update endpoint exists. Bulk actions are sequential individual PATCH calls.
