# AirAd Frontend — DLS Component Tasks
## Group F1: All 16 DLS Base Components + Layout Components
### All tasks are P0 — NO page work begins until every component in this group is complete and reviewed

> **Parent Index:** [`TASKS_INDEX.md`](./TASKS_INDEX.md)
> **Last Updated:** 2026-02-22

---

## Build Order

```
F1-01 Button          ← no deps
F1-02 Badge           ← no deps
F1-03 Input family    ← no deps
F1-04 EmptyState      ← no deps
F1-05 SkeletonTable   ← no deps
F1-06 Table           ← needs Badge, EmptyState, SkeletonTable
F1-07 Modal           ← needs Button
F1-08 Drawer          ← needs Button
F1-09 Toast + Provider← needs uiStore (F0-05)
F1-10 Sidebar         ← needs Badge, authStore (F0-04)
F1-11 TopBar          ← needs Badge, authStore, Axios (F0-03)
F1-12 AdminLayout     ← needs Sidebar, TopBar
F1-13 PageHeader      ← needs Button
F1-14 FiltersBar      ← needs Input, Select
F1-15 GPSInput        ← needs Input, Leaflet
F1-16 GPSMap          ← needs Leaflet
```

---

## DLS Enforcement Rules (apply to ALL components)

- **Zero hardcoded hex values** — CSS custom properties only
- **Zero `style={}` props** — CSS modules or CSS custom properties only
- **Zero `any` types** — use `unknown` and narrow
- **`lucide-react` only** for icons — `strokeWidth={1.5}`, never filled
- Icon sizes: `16` inline / `20` nav / `24` standalone / `32` empty states
- **No other component libraries** — no MUI, Shadcn, Radix, Headless UI
- Every interactive element: keyboard accessible (Tab, Enter, Space, Escape)
- Every interactive element: visible focus ring (`2px solid var(--color-rausch)`)
- `aria-*` attributes required on all interactive and semantic elements

---

## TASK-F1-01 · Button Component

**Priority:** P0 | **Effort:** XS
**File:** `src/shared/components/dls/Button.tsx`

**Props Interface:**
```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant: 'primary' | 'secondary' | 'destructive' | 'ghost';
  size?: 'compact' | 'default' | 'large'; // 32px / 40px / 48px
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}
```

**Visual Spec:**
- `border-radius: var(--radius-md)` (8px)
- Primary: `background: var(--color-rausch)`, white text — **max 1 per view**
- Secondary: `border: 1px solid var(--color-grey-300)`, `var(--color-hof)` text
- Destructive: `background: var(--color-error-bg)`, `var(--color-error-text)` text
- Ghost: transparent bg, `var(--color-hof)` text
- Hover: 8% darker (use `filter: brightness(0.92)`)
- Active: 12% darker (`filter: brightness(0.88)`)
- Disabled: `opacity: 0.4`, `cursor: not-allowed`
- Loading: spinner replaces content, `aria-busy="true"`, `disabled` attribute set

**Acceptance Criteria:**
- [ ] All 4 variants render with correct token-based colors
- [ ] Loading state shows spinner, disables interaction, sets `aria-busy="true"`
- [ ] Keyboard: Enter and Space trigger `onClick`
- [ ] `aria-label` required when no text children (TypeScript enforces via conditional type)
- [ ] Zero hardcoded hex values

---

## TASK-F1-02 · Badge Component

**Priority:** P0 | **Effort:** XS
**File:** `src/shared/components/dls/Badge.tsx`

**Props Interface:**
```typescript
interface BadgeProps {
  variant: 'success' | 'warning' | 'error' | 'info' | 'neutral';
  label: string;
  icon?: React.ReactNode; // lucide-react, strokeWidth 1.5, size 12
  size?: 'sm' | 'md';    // 20px / 24px height
}
```

**Visual Spec:**
- Height: 24px, `border-radius: var(--radius-pill)` (100px), 12px/500 font
- Always icon alongside color — never color alone (accessibility)
- success → `--color-babu` bg tint + `--color-success-text`
- warning → `--color-arches` bg tint + `--color-warning-text`
- error → `--color-error-bg` + `--color-error-text`
- info → `--color-info-bg` + `--color-info-text`
- neutral → `--color-grey-100` + `--color-hof`

**Standard Mappings (use these consistently across all pages):**

QC Status:
- `PENDING` → neutral + `Clock` icon
- `APPROVED` → success + `CheckCircle` icon
- `REJECTED` → error + `XCircle` icon
- `NEEDS_REVIEW` → warning + `AlertTriangle` icon
- `FLAGGED` → error + `Flag` icon

Import Status:
- `QUEUED` → neutral + `Clock` icon
- `PROCESSING` → info + `Loader` icon (animated spin, respects `prefers-reduced-motion`)
- `DONE` → success + `CheckCircle` icon
- `FAILED` → error + `XCircle` icon

**Acceptance Criteria:**
- [ ] All 5 variants use token-based colors
- [ ] Icon always present — no color-only badges
- [ ] `PROCESSING` animated icon respects `prefers-reduced-motion`
- [ ] `QCStatusBadge` and `ImportStatusBadge` convenience wrappers exported

---

## TASK-F1-03 · Form Input Components

**Priority:** P0 | **Effort:** S
**Files:** `Input.tsx`, `Textarea.tsx`, `Select.tsx`, `Checkbox.tsx`, `Toggle.tsx`

**Shared Props Pattern:**
```typescript
interface BaseInputProps {
  label: string;          // always required — no placeholder-only labels
  error?: string;
  hint?: string;
  required?: boolean;
  disabled?: boolean;
  id: string;             // always required for label association
}
```

**Visual Spec (Input, Select):**
- Height: 40px, `border-radius: var(--radius-md)` (8px)
- Border: `1px solid var(--color-grey-300)`
- Focus ring: `outline: 2px solid var(--color-rausch)`, `outline-offset: 2px`
- Error state: `border-color: var(--color-error-text)` + error message below with `AlertCircle` icon
- Label: `font: var(--text-label)` (13px/500), `color: var(--color-hof)`, above input
- Error message: `font: var(--text-caption)`, `color: var(--color-error-text)`
- `aria-describedby` links input to error message element

**Validation Timing:** on blur only — never on every keystroke

**Select:** native `<select>` styled with CSS, `options: { value: string; label: string }[]`

**Textarea:** same as Input but `resize: vertical`, min-height 80px

**Checkbox + Toggle:** 40px touch target, `color: var(--color-rausch)` when checked

**Acceptance Criteria:**
- [ ] Error message linked to input via `aria-describedby`
- [ ] Focus ring uses `--color-rausch` token
- [ ] No placeholder-only labels anywhere
- [ ] Validation fires on blur, not on every keystroke
- [ ] All inputs work with React Hook Form `register()` (forward ref)

---

## TASK-F1-04 · EmptyState Component

**Priority:** P0 | **Effort:** XS
**File:** `src/shared/components/dls/EmptyState.tsx`

**Props Interface:**
```typescript
interface EmptyStateProps {
  illustration?: React.ReactNode; // lucide-react icon at 32px
  heading: string;
  subheading: string;             // why empty + what to do
  ctaLabel?: string;
  onCta?: () => void;
  ctaDisabled?: boolean;
}
```

**Rules:**
- Never blank — always heading + subheading + CTA
- Illustration: lucide-react icon at 32px, `color: var(--color-grey-400)`
- Heading: `font: var(--text-heading-3)`, `color: var(--color-hof)`
- Subheading: `font: var(--text-body)`, `color: var(--color-foggy)`
- CTA: `Button` with `variant="primary"` (only if `ctaLabel` provided)

**Acceptance Criteria:**
- [ ] Never renders blank — always has heading + subheading
- [ ] CTA button only renders when `ctaLabel` + `onCta` are both provided
- [ ] Illustration icon is `aria-hidden="true"` (decorative)

---

## TASK-F1-05 · SkeletonTable Component

**Priority:** P0 | **Effort:** XS
**File:** `src/shared/components/dls/SkeletonTable.tsx`

**Props Interface:**
```typescript
interface SkeletonTableProps {
  rows?: number;     // default 5
  columns?: number;  // default 5
  showHeader?: boolean; // default true
}
```

**Rules:**
- Animated shimmer effect using CSS `@keyframes` (respects `prefers-reduced-motion`)
- Row height: `var(--table-row-height)` (56px)
- Skeleton cells: `background: var(--color-grey-200)`, `border-radius: var(--radius-sm)`
- Varying widths per column (60%, 40%, 80%, 30%, 50%) to look realistic
- `aria-label="Loading data"` on container, `aria-busy="true"`

**Acceptance Criteria:**
- [ ] Shimmer animation disabled when `prefers-reduced-motion` is set
- [ ] `aria-busy="true"` and `aria-label="Loading data"` present
- [ ] Row height matches actual Table row height (56px)

---

## TASK-F1-06 · Table Component (Sortable + Paginated + Selectable)

**Priority:** P0 | **Effort:** M
**File:** `src/shared/components/dls/Table.tsx`

**Props Interface:**
```typescript
interface ColumnDef<T> {
  key: string;
  header: string;
  render: (row: T) => React.ReactNode;
  sortable?: boolean;
  width?: string;
}

interface TableProps<T> {
  'aria-label': string;           // required
  columns: ColumnDef<T>[];
  data: T[];
  isLoading: boolean;
  isEmpty: boolean;
  emptyState: React.ReactNode;
  pagination?: {
    page: number;
    pageSize: number;
    total: number;
    onPageChange: (page: number) => void;
    pageSizeOptions?: number[];   // default [25, 50, 100]
  };
  sort?: {
    key: string;
    direction: 'asc' | 'desc';
    onSort: (key: string, direction: 'asc' | 'desc') => void;
  };
  selectable?: boolean;
  selectedIds?: string[];
  onSelectionChange?: (ids: string[]) => void;
  getRowId?: (row: T) => string;  // default: row.id
  stickyHeader?: boolean;         // auto-true when >10 rows
  onRowClick?: (row: T) => void;
}
```

**Visual Spec:**
- Header: `font: var(--text-body-strong)` (14px/500), `background: var(--color-grey-50)`, `border-bottom: 1px solid var(--color-grey-200)`
- Row: height `var(--table-row-height)` (56px), `border-bottom: 1px solid var(--color-grey-200)`
- Row hover: `background: var(--color-grey-50)`
- Checkbox column: 48px wide
- Sort indicator: `ChevronUp`/`ChevronDown` lucide icon, visible on hover + when active
- `aria-sort="ascending"` / `"descending"` / `"none"` on sortable headers
- Pagination: page numbers + prev/next + page size selector

**Loading/Empty Behavior:**
- `isLoading=true` → render `<SkeletonTable>` with matching column count — **never a spinner**
- `isEmpty=true` → render `emptyState` prop
- Both false → render data rows

**Bulk Selection:**
- "Select all" checkbox in header selects current page only
- `selectedIds` is controlled — parent manages selection state
- Indeterminate state when some (not all) rows selected

**Acceptance Criteria:**
- [ ] `SkeletonTable` shown when `isLoading=true` — no spinner anywhere
- [ ] `emptyState` shown when `isEmpty=true`
- [ ] `aria-sort` attribute updates correctly on sort change
- [ ] "Select all" selects current page only, not all pages
- [ ] Sticky header activates automatically when >10 rows
- [ ] `aria-label` prop is required — TypeScript enforces it
- [ ] Keyboard: Tab navigates interactive cells, Enter activates `onRowClick`

---

## TASK-F1-07 · Modal Component

**Priority:** P0 | **Effort:** S
**File:** `src/shared/components/dls/Modal.tsx`

**Props Interface:**
```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  size?: 'confirm' | 'form' | 'detail'; // 480px / 640px / 80vw
  children: React.ReactNode;
  footer?: React.ReactNode;
  closeOnBackdrop?: boolean; // default true
}
```

**Visual Spec:**
- Overlay: `background: rgba(0,0,0,0.5)`, `backdrop-filter: blur(4px)`
- Container: `border-radius: var(--radius-xl)` (16px), `padding: var(--space-8)` (32px)
- `box-shadow: var(--shadow-modal)`
- Widths: confirm=480px, form=640px, detail=80vw (max 1200px)
- Enter animation: scale 0.95→1 + fade in (`--duration-normal`)
- Exit animation: scale 1→0.95 + fade out (`--duration-fast`)

**Accessibility:**
- `role="dialog"`, `aria-modal="true"`, `aria-labelledby={titleId}`
- Focus trap: Tab cycles within modal, Shift+Tab reverses
- ESC key closes modal
- On open: focus moves to first focusable element inside modal
- On close: focus returns to the element that triggered the modal

**Acceptance Criteria:**
- [ ] Focus trapped inside modal when open
- [ ] ESC key closes modal
- [ ] Backdrop click closes modal (when `closeOnBackdrop=true`)
- [ ] `aria-modal`, `role="dialog"`, `aria-labelledby` all present
- [ ] Focus returns to trigger element on close
- [ ] Animations respect `prefers-reduced-motion`

---

## TASK-F1-08 · Drawer Component

**Priority:** P0 | **Effort:** S
**File:** `src/shared/components/dls/Drawer.tsx`

**Props Interface:**
```typescript
interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  width?: number; // default 640
  children: React.ReactNode;
  footer?: React.ReactNode;
}
```

**Visual Spec:**
- Slides in from right, width 640px (fixed)
- Same overlay as Modal (`rgba(0,0,0,0.5)` + `backdrop-filter: blur(4px)`)
- Slide animation: `translateX(100%)` → `translateX(0)` (`--duration-normal`, `--ease-enter`)
- Header: title + close button (`X` icon, `aria-label="Close drawer"`)
- Body: scrollable, `padding: var(--space-6)`
- Footer: sticky at bottom, `border-top: 1px solid var(--color-grey-200)`, `padding: var(--space-4) var(--space-6)`

**Accessibility:** Same focus trap + ESC + return-focus pattern as Modal

**Acceptance Criteria:**
- [ ] Slides in from right at 640px
- [ ] Focus trapped, ESC closes
- [ ] Slide animation disabled when `prefers-reduced-motion` is set
- [ ] Footer is sticky at bottom of drawer
- [ ] Scrollable body when content overflows

---

## TASK-F1-09 · Toast + ToastProvider

**Priority:** P0 | **Effort:** XS
**Files:** `Toast.tsx`, `ToastProvider.tsx`

**Visual Spec:**
- Position: fixed top-right, `top: var(--space-4)`, `right: var(--space-4)`
- Width: 360px max
- Stack: multiple toasts stack vertically with `var(--space-2)` gap
- Each toast: `border-radius: var(--radius-lg)`, `padding: var(--space-3) var(--space-4)`
- Left border: 4px solid semantic color
- Icon: lucide-react at 20px (`CheckCircle`, `XCircle`, `AlertTriangle`, `Info`)
- Close button: `X` icon, `aria-label="Dismiss notification"`
- Enter: slide in from right + fade (`--duration-fast`)
- Exit: fade out (`--duration-fast`)

**Accessibility:**
- Container: `aria-live="polite"`, `aria-atomic="false"`, `role="status"`
- Each toast: `role="alert"` for error type, `role="status"` for others

**`ToastProvider`:** Renders the toast stack using a React Portal (`document.body`)

**Acceptance Criteria:**
- [ ] Multiple toasts stack without overlap
- [ ] Auto-dismisses after 4s
- [ ] `aria-live="polite"` on container — screen reader announces new toasts
- [ ] Manual dismiss via close button
- [ ] Animations disabled when `prefers-reduced-motion` is set
- [ ] Rendered via React Portal (not inside main content tree)

---

## TASK-F1-10 · Sidebar Component

**Priority:** P0 | **Effort:** S
**File:** `src/shared/components/dls/Sidebar.tsx`

**Visual Spec:**
- Width: `var(--sidebar-width)` (240px), fixed position
- Background: `var(--color-white)`, `border-right: 1px solid var(--color-grey-200)`
- Nav item: height 44px, `border-radius: var(--radius-nav-item)` (`0 100px 100px 0`), pill-right
- Active state: `background: rgba(255, 90, 95, 0.08)`, text `var(--color-rausch)`, `font-weight: 600`
- Inactive: `color: var(--color-hof)`, hover `background: var(--color-grey-50)`
- Section labels: 11px uppercase, `letter-spacing: 1px`, `color: var(--color-foggy)`
- Logo area: 64px height at top

**Nav Items + Role Visibility (from RBAC matrix):**

```
SECTION: Overview
  Dashboard (/)                    → all roles
  
SECTION: Data
  Geo Management (/geo)            → all roles (write gated per RBAC)
  Tag Management (/tags)           → all roles
  Vendor List (/vendors)           → all roles
  QC Queue (/vendors?qc_status=PENDING,NEEDS_REVIEW) → all roles (count badge)
  
SECTION: Operations
  Imports (/imports)               → SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY
  Field Ops (/field-ops)           → SUPER_ADMIN, CITY_MANAGER, FIELD_AGENT
  QA (/qa)                         → SUPER_ADMIN, CITY_MANAGER, QA_REVIEWER
  
SECTION: System
  Audit Log (/system/audit)        → SUPER_ADMIN, ANALYST
  Users (/system/users)            → SUPER_ADMIN only
```

**QC Queue badge:** shows count of PENDING + NEEDS_REVIEW vendors — fetched from `analytics/kpis` response

**Collapsed state:** 64px width, icons only, tooltip on hover (from `uiStore.sidebarCollapsed`)

**Acceptance Criteria:**
- [ ] Pill-right active state (`border-radius: 0 100px 100px 0`)
- [ ] Nav items hidden based on `authStore.role` — verified for all 7 roles
- [ ] QC Queue count badge updates when vendor QC status changes (query invalidation)
- [ ] Keyboard navigable (Tab, Enter)
- [ ] No icon-only nav items without `aria-label` (tooltip serves as label)
- [ ] Collapsed state shows icons + tooltips only

---

## TASK-F1-11 · TopBar Component

**Priority:** P0 | **Effort:** S
**File:** `src/shared/components/dls/TopBar.tsx`

**API:** `GET /api/v1/auth/profile/` — called once on mount, cached by TanStack Query

**Visual Spec:**
- Height: `var(--topbar-height)` (64px), fixed at top
- Background: `var(--color-white)`, `border-bottom: 1px solid var(--color-grey-200)`
- Left: breadcrumb (derived from current route)
- Right: notification bell icon + user avatar (initials) + role badge + dropdown menu

**User Dropdown Menu:**
- User's full name + email (from `authStore.user`)
- Role badge
- "Sign Out" → triggers logout flow

**Breadcrumb:** auto-generated from route path segments, max 3 levels

**Acceptance Criteria:**
- [ ] Shows current user email + role badge from `authStore`
- [ ] Breadcrumb reflects current route path
- [ ] Dropdown opens on click, closes on ESC + outside click
- [ ] "Sign Out" calls `POST /api/v1/auth/logout/` then clears auth state

---

## TASK-F1-12 · AdminLayout Component

**Priority:** P0 | **Effort:** XS
**File:** `src/shared/components/dls/AdminLayout.tsx`

**Structure:**
```
<div class="admin-layout">
  <Sidebar />
  <div class="admin-layout__main">
    <TopBar />
    <main id="main-content" class="admin-layout__content">
      {children}
    </main>
  </div>
</div>
```

**CSS:**
- `Sidebar`: fixed left, `var(--sidebar-width)` wide
- `main`: `margin-left: var(--sidebar-width)`, `margin-top: var(--topbar-height)`
- Content: `max-width: var(--content-max-width)` (1280px), `padding: var(--space-10) var(--space-8)` (40px 32px)
- `id="main-content"` — target for skip link

**Responsive:**
- 1280px+: full layout
- 1024px: sidebar auto-collapses to icon-only mode
- 768px: sidebar hidden, hamburger menu in TopBar

**Acceptance Criteria:**
- [ ] `id="main-content"` present on `<main>` element (skip link target)
- [ ] Content max-width is 1280px
- [ ] Sidebar auto-collapses at 1024px viewport
- [ ] Layout does not break at 768px

---

## TASK-F1-13 · PageHeader Component

**Priority:** P0 | **Effort:** XS
**File:** `src/shared/components/dls/PageHeader.tsx`

**Props Interface:**
```typescript
interface PageHeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode; // primary CTA slot — max 1 Button[variant="primary"]
}
```

**Visual Spec:**
- Height: 80px, `border-bottom: 1px solid var(--color-grey-200)`
- Title: `font: var(--text-heading-1)` (24px/700), `color: var(--color-hof)`
- Subtitle: `font: var(--text-body)`, `color: var(--color-foggy)`
- Action: right-aligned

**Acceptance Criteria:**
- [ ] Title and subtitle use correct typography tokens
- [ ] Action slot is right-aligned
- [ ] Height is exactly 80px

---

## TASK-F1-14 · FiltersBar Component

**Priority:** P0 | **Effort:** XS
**File:** `src/shared/components/dls/FiltersBar.tsx`

**Props Interface:**
```typescript
interface FiltersBarProps {
  search?: {
    value: string;
    onChange: (v: string) => void;
    placeholder?: string;
  };
  filters?: React.ReactNode; // Select dropdowns
  resultCount?: number;
  actions?: React.ReactNode; // secondary actions (export, etc.)
}
```

**Visual Spec:**
- Height: 56px, `background: var(--color-white)`, `border-bottom: 1px solid var(--color-grey-200)`
- Search input: 280px wide, `Search` icon prefix
- Result count: `font: var(--text-caption)`, `color: var(--color-foggy)`

**Search debounce:** 300ms via `useDebounce` hook — do NOT fire API on every keystroke

**Acceptance Criteria:**
- [ ] Search input debounced 300ms before triggering query
- [ ] Result count updates after data loads
- [ ] All filter dropdowns use DLS `Select` component

---

## TASK-F1-15 · GPSInput Component

**Priority:** P0 | **Effort:** S
**File:** `src/shared/components/dls/GPSInput.tsx`

**Props Interface:**
```typescript
interface GPSInputProps {
  lat: number | null;
  lng: number | null;
  onChange: (lat: number, lng: number) => void;
  readonly?: boolean;
  error?: string;
}
```

**Behavior:**
- Two number inputs: Latitude (-90 to 90) + Longitude (-180 to 180)
- Leaflet mini-map preview (300px height) with draggable marker
- Dragging marker updates lat/lng inputs
- Typing in inputs moves marker
- Validation: lat must be -90 to 90, lng must be -180 to 180

**⚠️ GeoJSON Coordinate Order:**
- Backend sends `gps_point.coordinates = [lng, lat]` (GeoJSON standard)
- Leaflet expects `[lat, lng]`
- **Always convert:** `leafletPos = [coordinates[1], coordinates[0]]`
- Document this in component JSDoc

**Acceptance Criteria:**
- [ ] Dragging marker updates lat/lng inputs in real-time
- [ ] Typing valid coordinates moves marker
- [ ] Invalid lat/lng shows inline error message
- [ ] GeoJSON coordinate swap is correct (lng,lat → lat,lng for Leaflet)
- [ ] `readonly` mode shows map + marker but disables dragging and inputs

---

## TASK-F1-16 · GPSMap Components (Split Map + Choropleth)

**Priority:** P0 | **Effort:** S
**Files:** `GPSSplitMap.tsx`, `ChoroplethMap.tsx`

**GPSSplitMap** (used in Field Ops visit detail + Location Change Review):
```typescript
interface GPSSplitMapProps {
  leftLabel: string;
  leftPoint: GeoJSONPoint;
  rightLabel: string;
  rightPoint: GeoJSONPoint;
  distanceDelta?: number; // meters
}
```
- Side-by-side Leaflet maps (50% each)
- Distance delta label between maps
- Amber warning badge if `distanceDelta > 20` (meters)

**ChoroplethMap** (used in Platform Health Dashboard):
```typescript
interface ChoroplethMapProps {
  cities: Array<{
    id: string;
    name: string;
    lat: number;
    lng: number;
    vendorCount: number;
    status: 'good' | 'warning' | 'low';
  }>;
  onCityClick?: (cityId: string) => void;
}
```
- Circle markers: green (`--color-babu`) / amber (`--color-arches`) / red (`--color-error-text`)
- Click circle → `onCityClick(cityId)`

**Acceptance Criteria:**
- [ ] Split map shows two independent Leaflet instances side by side
- [ ] Distance delta > 20m shows amber warning badge
- [ ] Choropleth circles use correct token-based colors
- [ ] Both maps are keyboard accessible (Leaflet default keyboard navigation)
- [ ] GeoJSON coordinate order correctly handled in both components
