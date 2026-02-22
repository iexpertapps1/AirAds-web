# AirAd Frontend — Foundation Tasks
## Group F0: Project Bootstrap · Stores · HTTP Client · Router
### All tasks are P0 — nothing else can start until this group is complete

> **Parent Index:** [`TASKS_INDEX.md`](./TASKS_INDEX.md)
> **Last Updated:** 2026-02-22

---

## Dependency Order

```
F0-01 (Vite scaffold)
  └── F0-02 (DLS tokens CSS)
  └── F0-04 (authStore)
  └── F0-05 (uiStore)
  └── F0-06 (QueryClient + queryKeys)
        └── F0-03 (Axios + JWT interceptor)  ← needs authStore + uiStore
              └── F0-07 (Router + guards)    ← needs authStore
```

---

## TASK-F0-01 · Vite + React 18 + TypeScript 5 Project Bootstrap

**Priority:** P0 | **Effort:** S | **Blocks:** everything

**Problem:** No frontend project exists. Zero features can be built without the scaffold.

**User Story:** As a developer, I need a runnable, fully-configured project scaffold so I can build features without fighting tooling.

**Deliverables:**

1. `frontend/` — Vite project using `react-ts` template
2. `tsconfig.json`:
   - `strict: true`
   - `noUncheckedIndexedAccess: true`
   - `exactOptionalPropertyTypes: true`
   - Path alias: `"@/*": ["src/*"]`
3. `vite.config.ts`:
   - Path alias `@/` → `src/`
   - `vite-plugin-checker` for TypeScript + ESLint (surfaces errors in dev server)
   - Separate `resolve`, `plugins`, `build` sections (no monolithic config)
4. `.env.example`:
   ```
   VITE_API_BASE_URL=http://localhost:8000
   ```
5. `src/main.tsx` — startup env validation:
   ```typescript
   if (!import.meta.env.VITE_API_BASE_URL) {
     throw new Error('[AirAd] VITE_API_BASE_URL is not set. Check your .env file.');
   }
   ```
6. ESLint config:
   - `@typescript-eslint/no-explicit-any` → error
   - Custom rule: no `style={}` props
   - Custom rule: no hardcoded hex/rgb color values in JSX/CSS-in-JS
   - `no-console` → error
7. Prettier config: single quotes, trailing commas, 100 char line width
8. Husky pre-commit hook: runs `eslint` + `tsc --noEmit`
9. `package.json` dependencies (pinned versions):
   - `react@18`, `react-dom@18`, `typescript@5`
   - `react-router-dom@6`
   - `zustand@4` (with `immer` + `subscribeWithSelector` middleware)
   - `@tanstack/react-query@5`
   - `axios`
   - `react-hook-form`, `zod`, `@hookform/resolvers`
   - `recharts`
   - `leaflet`, `react-leaflet`, `@types/leaflet`
   - `lucide-react`
   - `papaparse`, `@types/papaparse`
   - `react-diff-viewer-continued`

**Dependencies:** None

**Acceptance Criteria:**
- [ ] `npm run dev` starts without errors on a clean clone
- [ ] `npm run build` produces zero TypeScript errors
- [ ] Missing `VITE_API_BASE_URL` throws a descriptive error at startup — not a silent undefined
- [ ] `tsc --noEmit` passes with `strict: true`
- [ ] ESLint pre-commit hook blocks commits containing `any` type or `style={}` props
- [ ] All dependencies are pinned (no `^` or `~` ranges in `package.json`)

---

## TASK-F0-02 · DLS Tokens CSS + ThemeProvider

**Priority:** P0 | **Effort:** XS | **Blocks:** all DLS components

**Problem:** Without design tokens as CSS custom properties, every component will hardcode values — a DLS violation that is grounds for immediate PR rejection per `expert-rules.md`.

**User Story:** As a developer, I need all design tokens defined as CSS custom properties in one file so I never write a raw color or spacing value.

**Deliverables:**

1. `src/theme/dls-tokens.css` — complete token set:

```css
:root {
  /* Brand Colors */
  --color-rausch: #FF5A5F;
  --color-babu: #00A699;
  --color-arches: #FC642D;
  --color-hof: #484848;
  --color-foggy: #767676;
  --color-white: #FFFFFF;

  /* Greys */
  --color-grey-50: #F7F7F7;
  --color-grey-100: #F0F0F0;
  --color-grey-200: #EBEBEB;
  --color-grey-300: #DDDDDD;
  --color-grey-400: #AAAAAA;

  /* Semantic */
  --color-success-text: #008A05;
  --color-success-bg: #E8F5E9;
  --color-warning-text: #C45300;
  --color-warning-bg: #FFF3E0;
  --color-error-text: #C13515;
  --color-error-bg: #FFEBEE;
  --color-info-text: #0077C8;
  --color-info-bg: #E3F2FD;

  /* Typography */
  --font-family: 'Circular', 'DM Sans', -apple-system, sans-serif;
  --text-display: 700 32px/1.25 var(--font-family);
  --text-heading-1: 700 24px/1.3 var(--font-family);
  --text-heading-2: 600 20px/1.4 var(--font-family);
  --text-heading-3: 600 16px/1.5 var(--font-family);
  --text-body: 400 14px/1.5 var(--font-family);
  --text-body-strong: 500 14px/1.5 var(--font-family);
  --text-caption: 400 12px/1.4 var(--font-family);
  --text-label: 500 13px/1.4 var(--font-family);
  --text-micro: 400 11px/1.3 var(--font-family);

  /* Spacing (8px grid) */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;

  /* Layout */
  --sidebar-width: 240px;
  --topbar-height: 64px;
  --content-max-width: 1280px;
  --table-row-height: 56px;
  --card-padding: var(--space-6);

  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-pill: 100px;
  --radius-nav-item: 0 100px 100px 0;

  /* Motion */
  --duration-instant: 100ms;
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 350ms;
  --ease-standard: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-enter: cubic-bezier(0, 0, 0.2, 1);
  --ease-exit: cubic-bezier(0.4, 0, 1, 1);

  /* Shadows */
  --shadow-card: 0 1px 2px rgba(0, 0, 0, 0.08);
  --shadow-modal: 0 8px 32px rgba(0, 0, 0, 0.16);
  --shadow-dropdown: 0 4px 16px rgba(0, 0, 0, 0.12);
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

2. `src/theme/ThemeProvider.tsx`:
   - Light theme default (portal uses `--color-grey-100` page bg)
   - Theme preference persisted to `localStorage` via Zustand `uiStore`
   - Sets CSS class on `<html>` element — no re-renders on theme switch
   - Single instance at root level — never inside individual components

3. `src/main.tsx` — `dls-tokens.css` is the **first** import, before React, before anything else

**Dependencies:** TASK-F0-01

**Acceptance Criteria:**
- [ ] `dls-tokens.css` is the first import in `main.tsx` — verified by file inspection
- [ ] `prefers-reduced-motion` block present — tested via Chrome DevTools "Emulate CSS media feature"
- [ ] Zero hardcoded hex values exist anywhere in the codebase (ESLint rule catches violations)
- [ ] `ThemeProvider` is the only place theme is set — components only consume tokens
- [ ] Theme switch is instant with zero React re-renders (CSS variable swap only)

---

## TASK-F0-03 · Axios Client + JWT Interceptor

**Priority:** P0 | **Effort:** S | **Blocks:** all API calls

**Problem:** Every API call needs auth headers and automatic token refresh. Without a centralized client, each feature would re-implement auth logic — creating drift and security holes.

**User Story:** As a developer, I need a single Axios instance that handles JWT auth transparently so feature code never touches token management.

**Deliverables:** `src/lib/axios.ts`

```typescript
// Pseudocode — implement fully typed with no `any`
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor: attach access token
apiClient.interceptors.request.use((config) => {
  const token = authStore.getState().accessToken;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Response interceptor: handle 401
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      // Queue concurrent 401s — only one refresh call at a time
      try {
        const { data } = await axios.post(
          `${import.meta.env.VITE_API_BASE_URL}/api/v1/auth/refresh/`,
          { refresh: authStore.getState().refreshToken }
        );
        // Response shape: { access: string } — SimpleJWT, NO data wrapper
        authStore.getState().setAccessToken(data.access);
        original.headers.Authorization = `Bearer ${data.access}`;
        return apiClient(original);
      } catch {
        authStore.getState().logout();
        window.location.href = '/login';
      }
    }
    // Show error toast for all non-401 errors
    const message = error.response?.data?.message ?? 'Something went wrong. Please try again.';
    uiStore.getState().addToast({ type: 'error', message });
    return Promise.reject(error);
  }
);
```

**Critical API Contract Notes:**
- Refresh endpoint: `POST /api/v1/auth/refresh/` → `{ access: string }` — **no `data` wrapper** (SimpleJWT standard)
- All other endpoints: `{ success: boolean, data: T }` wrapper
- Login endpoint: `{ data: { tokens: { access, refresh }, user: { id, email, role } } }`

**Concurrent 401 Queue Pattern:**
- Use a `isRefreshing` flag + `failedQueue` array
- While refreshing, queue all incoming 401 requests
- On refresh success: replay all queued requests with new token
- On refresh failure: reject all queued requests + logout

**Dependencies:** TASK-F0-04 (authStore), TASK-F0-05 (uiStore)

**Acceptance Criteria:**
- [ ] All requests include `Authorization: Bearer {token}` header
- [ ] A burst of concurrent 401s triggers exactly one refresh call (queue mechanism)
- [ ] After successful refresh, all queued requests are replayed with the new token
- [ ] After failed refresh, user is redirected to `/login` and auth state is cleared
- [ ] Refresh response correctly reads `data.access` (not `data.data.access`)
- [ ] Error toast shown for all non-401 API errors with the `message` from response body

---

## TASK-F0-04 · Zustand Auth Store

**Priority:** P0 | **Effort:** XS | **Blocks:** F0-03, F0-07, all protected pages

**Problem:** Auth state (user, role, tokens) must be globally accessible without prop drilling.

**User Story:** As a developer, I need a typed auth store so any component can read the current user's role and tokens without prop drilling.

**Deliverables:** `src/features/auth/store/authStore.ts`

```typescript
type Role = 'SUPER_ADMIN' | 'CITY_MANAGER' | 'DATA_ENTRY' | 'QA_REVIEWER'
           | 'FIELD_AGENT' | 'ANALYST' | 'SUPPORT';

interface User {
  id: string;
  email: string;
  role: Role;
  full_name?: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  // Actions
  login: (tokens: { access: string; refresh: string }, user: User) => void;
  logout: () => void;
  setAccessToken: (token: string) => void;
}
```

- `subscribeWithSelector` middleware for fine-grained reactivity
- `immer` middleware for safe state updates
- Tokens stored **in-memory only** — never `localStorage`, never `sessionStorage`
- `role` is always derived from `user.role` — never stored as a separate field

**`usePermission` hook** (`src/shared/hooks/usePermission.ts`):
```typescript
export function usePermission(allowedRoles: Role[]): boolean {
  return useAuthStore((s) => s.user !== null && allowedRoles.includes(s.user.role));
}
```

**Dependencies:** TASK-F0-01

**Acceptance Criteria:**
- [ ] Tokens are NOT in localStorage or sessionStorage — verified via DevTools Application tab
- [ ] `logout()` sets `user`, `accessToken`, `refreshToken` all to `null`
- [ ] `Role` is a discriminated string union — TypeScript rejects invalid role strings
- [ ] `usePermission(['SUPER_ADMIN'])` returns `false` for a DATA_ENTRY user

---

## TASK-F0-05 · Zustand UI Store

**Priority:** P0 | **Effort:** XS | **Blocks:** F0-03 (toast), all pages

**Deliverables:** `src/shared/store/uiStore.ts`

```typescript
interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number; // ms, default 4000
}

interface UIState {
  sidebarCollapsed: boolean;
  toasts: Toast[];
  toggleSidebar: () => void;
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}
```

- `addToast` generates a unique `id` (e.g., `crypto.randomUUID()`) and schedules `removeToast` via `setTimeout`
- `immer` middleware for safe array mutations

**`useToast` hook** (`src/shared/hooks/useToast.ts`):
```typescript
export function useToast() {
  const addToast = useUIStore((s) => s.addToast);
  return {
    success: (message: string) => addToast({ type: 'success', message }),
    error: (message: string) => addToast({ type: 'error', message }),
    warning: (message: string) => addToast({ type: 'warning', message }),
    info: (message: string) => addToast({ type: 'info', message }),
  };
}
```

**Dependencies:** TASK-F0-01

**Acceptance Criteria:**
- [ ] Multiple toasts stack simultaneously without replacing each other
- [ ] Toast auto-dismisses after 4s (default) — timer starts on `addToast`
- [ ] `removeToast` cancels the auto-dismiss timer to prevent double-removal
- [ ] `sidebarCollapsed` persists across route changes (in-memory, not page refresh)

---

## TASK-F0-06 · TanStack Query Client + Query Keys

**Priority:** P0 | **Effort:** XS | **Blocks:** all data-fetching hooks

**Problem:** Without centralized query key factories, developers will scatter string literals across the codebase, making cache invalidation fragile and untraceable.

**Deliverables:**

1. `src/lib/queryClient.ts`:
```typescript
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,      // 5 minutes
      gcTime: 10 * 60 * 1000,         // 10 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      onError: () => {
        // Global mutation error handled by Axios interceptor toast
      },
    },
  },
});
```

2. `src/queryKeys.ts` — ALL key factories, typed as `as const`:
```typescript
export const queryKeys = {
  auth: {
    profile: () => ['auth', 'profile'] as const,
  },
  analytics: {
    kpis: () => ['analytics', 'kpis'] as const,
  },
  geo: {
    countries: () => ['geo', 'countries'] as const,
    cities: (filters?: CityFilters) => ['geo', 'cities', filters] as const,
    city: (id: string) => ['geo', 'city', id] as const,
    areas: (filters?: AreaFilters) => ['geo', 'areas', filters] as const,
    landmarks: (filters?: LandmarkFilters) => ['geo', 'landmarks', filters] as const,
  },
  tags: {
    list: (filters?: TagFilters) => ['tags', 'list', filters] as const,
    detail: (id: string) => ['tags', 'detail', id] as const,
  },
  vendors: {
    list: (filters?: VendorFilters) => ['vendors', 'list', filters] as const,
    detail: (id: string) => ['vendors', 'detail', id] as const,
  },
  imports: {
    list: () => ['imports', 'list'] as const,
    detail: (id: string) => ['imports', 'detail', id] as const,
  },
  fieldOps: {
    list: (filters?: FieldOpsFilters) => ['fieldOps', 'list', filters] as const,
    detail: (id: string) => ['fieldOps', 'detail', id] as const,
    photos: (visitId: string) => ['fieldOps', 'photos', visitId] as const,
  },
  qa: {
    dashboard: () => ['qa', 'dashboard'] as const,
  },
  audit: {
    list: (filters?: AuditFilters) => ['audit', 'list', filters] as const,
  },
  system: {
    users: () => ['system', 'users'] as const,
  },
};
```

**Dependencies:** TASK-F0-01

**Acceptance Criteria:**
- [ ] Zero string literal query keys exist outside `queryKeys.ts` — ESLint rule enforces this
- [ ] All key factories return `as const` tuples (TypeScript infers literal types)
- [ ] `QueryClient` instantiated once and provided via `QueryClientProvider` at root in `main.tsx`
- [ ] `ReactQueryDevtools` included in dev mode only (`import.meta.env.DEV`)

---

## TASK-F0-07 · React Router v6 + Route Guards

**Priority:** P0 | **Effort:** S | **Blocks:** all pages

**Problem:** Without route guards, unauthenticated users can access protected pages and unauthorized roles can access admin-only routes.

**Deliverables:** `src/router.tsx`

**Route Structure (all page components lazy-loaded via `React.lazy`):**
```
/login                → LoginPage          (public — redirect to / if already authed)
/                     → PlatformHealthPage (protected — all roles)
/geo                  → GeoPage            (protected — all roles)
/tags                 → TagsPage           (protected — all roles)
/vendors              → VendorListPage     (protected — all roles)
/vendors/:id          → VendorDetailPage   (protected — all roles)
/imports              → ImportsPage        (protected — SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY)
/field-ops            → FieldOpsPage       (protected — SUPER_ADMIN, CITY_MANAGER, FIELD_AGENT)
/qa                   → QAPage             (protected — SUPER_ADMIN, CITY_MANAGER, QA_REVIEWER)
/system/audit         → AuditLogPage       (protected — SUPER_ADMIN, ANALYST)
/system/users         → UsersPage          (protected — SUPER_ADMIN only)
*                     → NotFoundPage       (public)
```

**`ProtectedRoute` component:**
- If `authStore.accessToken` is null → redirect to `/login?redirect={currentPath}`
- After login, redirect to `?redirect` param or `/`

**`RoleGate` component:**
```typescript
interface RoleGateProps {
  allowedRoles: Role[];
  fallback?: React.ReactNode; // default: null
  children: React.ReactNode;
}
```
- Renders `fallback` (or null) if current user's role is not in `allowedRoles`
- Used both for route-level protection and for hiding UI elements (buttons, nav items)

**Skip link (accessibility):**
```html
<a href="#main-content" className="skip-link">Skip to main content</a>
```
- First focusable element in DOM
- Visible only on keyboard focus (CSS: `position: absolute; top: -40px; &:focus { top: 0 }`)

**`Suspense` fallback:** `SkeletonTable` (not a spinner) while lazy chunk loads

**Dependencies:** TASK-F0-04 (authStore)

**Acceptance Criteria:**
- [ ] Unauthenticated access to any protected route redirects to `/login?redirect={path}`
- [ ] After login, user is redirected to the originally requested URL (via `?redirect` param)
- [ ] `/system/users` is inaccessible to all roles except SUPER_ADMIN — both nav hidden and route guarded
- [ ] All page components are lazy-loaded — verified by network tab showing separate JS chunks
- [ ] Skip link is the first focusable element and becomes visible on keyboard focus
- [ ] `Suspense` fallback uses `SkeletonTable`, not a spinner

---

## Global Types (`src/features/*/types/index.ts`)

Each feature owns its types. Shared primitive types live in `src/shared/types/`:

```typescript
// src/shared/types/api.ts
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  data: T[];
}

// src/shared/types/geo.ts
export interface GeoJSONPoint {
  type: 'Point';
  coordinates: [lng: number, lat: number]; // GeoJSON order: [lng, lat]
}

// IMPORTANT: Leaflet uses [lat, lng] — always swap when passing to Leaflet
// leafletLatLng = [point.coordinates[1], point.coordinates[0]]
```

**GeoJSON Coordinate Order Warning:**
The backend returns `gps_point: { type: "Point", coordinates: [lng, lat] }` — standard GeoJSON.
Leaflet expects `[lat, lng]`. **Always swap** when converting between the two. This is a known footgun — document it in the `GPSInput` component.
