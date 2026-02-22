# AirAd — Frontend Build Plan
## React 18 + TypeScript 5 — Admin Portal (Phase A) + Vendor Dashboard (Phase B)
### Airbnb Design Language System (DLS) — Non-Negotiable

---

## 0. ANALYSIS SUMMARY

Two surfaces sharing one codebase:
- **Phase A**: Internal Data Collection Portal — 7 admin roles, vendor data management
- **Phase B**: Vendor Dashboard — discount management, analytics, voice bot, subscriptions

**Non-negotiable DLS rules:**
- CSS custom properties only — never hardcode hex values in components
- `--color-rausch` (#FF5A5F) for primary CTAs only — max 1 per view
- `--color-babu` (#00A699) for success/approved states
- `--color-arches` (#FC642D) for warnings/pending states
- 8px base spacing grid — no arbitrary pixel values
- DM Sans typography only
- WCAG 2.1 AA — 4.5:1 body text, 3:1 large text
- All tables: empty state + skeleton loading — NEVER spinners for content areas
- All interactive elements: keyboard navigable with visible focus ring
- `prefers-reduced-motion`: disable ALL animations
- Sidebar nav: `border-radius: 0 100px 100px 0` (pill-right)
- No icon-only buttons without `aria-label`
- lucide-react ONLY for icons, stroke-width: 1.5, never filled

---

## 1. TECH STACK

| Tool | Purpose |
|---|---|
| Vite + React 18 + TypeScript 5 | Framework |
| React Router v6 | Routing |
| Zustand | Global auth + UI state |
| TanStack Query v5 | API data fetching + caching |
| Axios | HTTP client with JWT interceptor |
| React Hook Form + Zod | Forms + validation |
| Recharts | Charts (line, bar, donut) |
| Leaflet + react-leaflet | Maps + GPS components |
| lucide-react | Icons (stroke-width: 1.5 only) |
| PapaParse | Client-side CSV preview |
| react-diff-viewer | Audit log before/after diff |

---

## 2. PROJECT STRUCTURE

```
frontend/
├── src/
│   ├── styles/
│   │   └── dls-tokens.css          # ALL CSS custom properties — imported FIRST in main.tsx
│   ├── components/dls/             # Built BEFORE any pages
│   │   ├── Button.tsx
│   │   ├── Badge.tsx
│   │   ├── Table.tsx               # Sortable, paginated, EmptyState + SkeletonRows
│   │   ├── Input.tsx / Textarea.tsx / Select.tsx / Checkbox.tsx / Toggle.tsx
│   │   ├── Modal.tsx               # Focus trap, ESC close, backdrop close
│   │   ├── Drawer.tsx              # 640px right-side
│   │   ├── Toast.tsx + ToastProvider.tsx
│   │   ├── Sidebar.tsx             # Pill-right nav, role-based visibility
│   │   ├── TopBar.tsx / PageHeader.tsx / FiltersBar.tsx
│   │   ├── EmptyState.tsx / SkeletonTable.tsx
│   │   └── GPSInput.tsx            # lat/lng + Leaflet mini-map preview
│   ├── layouts/
│   │   ├── AdminLayout.tsx
│   │   └── VendorLayout.tsx        # Phase B
│   ├── pages/
│   │   ├── auth/LoginPage.tsx
│   │   ├── dashboard/PlatformHealthPage.tsx
│   │   ├── geo/                    # Countries, Cities, Areas, Landmarks
│   │   ├── tags/TagsPage.tsx
│   │   ├── vendors/                # List, Detail, QC Queue
│   │   ├── imports/                # List, Detail
│   │   ├── field-ops/              # Visits, Agents
│   │   ├── qa/                     # GPS Drift, Duplicates
│   │   ├── audit/AuditLogPage.tsx
│   │   ├── system/UsersPage.tsx
│   │   └── vendor-dashboard/       # Phase B: Profile, Discounts, Analytics, VoiceBot, Subscription
│   ├── store/
│   │   ├── authStore.ts            # user, token, role
│   │   └── uiStore.ts              # sidebar, toast queue
│   ├── api/
│   │   ├── client.ts               # Axios instance + JWT interceptor
│   │   └── [auth, geo, tags, vendors, imports, fieldOps, qa, analytics, audit].ts
│   ├── hooks/
│   │   └── [useAuth, useToast, useDebounce].ts
│   ├── types/index.ts
│   └── main.tsx                    # Imports dls-tokens.css FIRST
```

---

## 3. DLS DESIGN TOKENS (`dls-tokens.css`)

```css
:root {
  --color-rausch: #FF5A5F;    --color-babu: #00A699;
  --color-arches: #FC642D;    --color-hof: #484848;
  --color-foggy: #767676;     --color-white: #FFFFFF;
  --color-grey-50: #F7F7F7;   --color-grey-100: #F0F0F0;
  --color-grey-200: #EBEBEB;  --color-grey-300: #DDDDDD;
  --color-grey-400: #AAAAAA;

  --color-success-text: #008A05; --color-success-bg: #E8F5E9;
  --color-warning-text: #C45300; --color-warning-bg: #FFF3E0;
  --color-error-text: #C13515;   --color-error-bg: #FFEBEE;
  --color-info-text: #0077C8;    --color-info-bg: #E3F2FD;

  --font-family: 'Circular', 'DM Sans', -apple-system, sans-serif;

  --space-1:4px; --space-2:8px; --space-3:12px; --space-4:16px;
  --space-5:20px; --space-6:24px; --space-8:32px; --space-10:40px;
  --space-12:48px; --space-16:64px;

  --duration-fast: 150ms; --duration-normal: 250ms;
  --ease-standard: cubic-bezier(0.4, 0, 0.2, 1);

  --sidebar-width: 240px; --topbar-height: 64px;
  --content-max-width: 1280px;
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 4. DLS COMPONENT SPECS

### Button
- Variants: Primary (rausch), Secondary (outlined), Destructive (error red), Ghost
- Heights: 40px / 32px compact / 48px large
- States: default, hover (8% darker), active (12% darker), disabled (40% opacity), loading (spinner)
- Max 1 Primary button per view

### Badge
- Variants: Success (babu), Warning (arches), Error (red), Info (blue), Neutral (grey)
- Height: 24px, border-radius: 12px, 12px/500 font
- Always include icon alongside color

### Table
- Header: 14px/600, `--color-grey-50` bg, 1px bottom border
- Row: 56px height, hover `--color-grey-50`, 1px bottom border
- Sortable: sort indicator on hover, `aria-sort` attribute
- Checkbox column: 48px for bulk selection
- MUST include: `EmptyState` + `SkeletonRows` — NEVER spinners
- Pagination: 25 items default

### Input / Select / Textarea
- Height: 40px, border-radius: 8px, border: 1px solid `--color-grey-300`
- Focus ring: 2px solid `--color-rausch`, offset 2px
- Error state: red border + message below with icon
- Label: 13px/500, `--color-hof`, above input

### Modal
- Overlay: `rgba(0,0,0,0.5)` backdrop-blur 4px
- Border-radius: 16px, padding: 32px
- Widths: 480px (confirm), 640px (forms), 80vw (detail)
- Focus trap, ESC + backdrop close, `aria-modal`, `role="dialog"`

### Drawer
- Width: 640px from right, same overlay as Modal
- Focus trap, ESC + backdrop close

### Sidebar
- 240px fixed, white bg, 1px right border `--color-grey-200`
- Nav item: 44px height, `border-radius: 0 100px 100px 0`
- Active: `bg rgba(255,90,95,0.08)`, text `--color-rausch`, weight 600
- Section labels: 11px uppercase, letter-spacing 1px
- Role-based visibility from Zustand auth store

### Toast
- Position: top-right, auto-dismiss 4s
- Variants: success/error/warning/info with icon
- Stack multiple toasts

### EmptyState
- Line-art illustration + heading + subheading (why empty + what to do) + primary CTA button

---

## 5. AXIOS INTERCEPTOR (`api/client.ts`)

```typescript
// - Attach Authorization: Bearer {token} to all requests
// - On 401: attempt token refresh → on success retry original request
//           → on refresh failure: clear auth store, redirect to /login
// - On any API error: show Toast with { message } from response
```

---

## 6. BUILD SEQUENCE (Steps 32–39)

### Step 32 — DLS Tokens CSS
Create `src/styles/dls-tokens.css` with all custom properties. Import FIRST in `main.tsx`.

### Step 33 — All DLS Base Components
Build all 16 components in `components/dls/` before any pages. Each with:
- Full TypeScript props interface
- Keyboard navigation (Tab, Enter, Escape, Space)
- Appropriate `aria-*` attributes
- No hardcoded hex values

### Step 34 — Layout Components
- `AdminLayout.tsx`: Sidebar (240px fixed) + TopBar (64px) + content area (max-width 1280px, padding 40px 32px)
- `TopBar.tsx`: Breadcrumb, search, notification bell, user avatar + role badge
- `Sidebar.tsx`: Role-based nav, pill-right active state, section labels
- `PageHeader.tsx`: Title + subtitle + primary CTA slot (h: 80px)
- `FiltersBar.tsx`: Search input + dropdowns + result count (h: 56px)

### Step 35 — Shared Components
- `EmptyState.tsx`: Props: illustration, heading, subheading, ctaLabel, onCta
- `SkeletonTable.tsx`: Animated skeleton rows matching Table column widths
- `ToastProvider.tsx`: Context + `useToast()` hook

### Step 36 — Zustand Stores + API Clients
- `authStore.ts`: user, accessToken, role, login(), logout(), refreshToken()
- `uiStore.ts`: sidebarCollapsed, toasts, addToast(), removeToast()
- All API modules with TanStack Query hooks

### Step 37 — All 10 Admin Portal Pages

#### `/` — Platform Health Dashboard (default home)
- Hero metrics row: 6 cards with sparklines, auto-refresh 60s
- Data collection metrics: 4 cards (QC pending, import rate, drift flags, field visits)
- Discount activity timeline (Recharts line chart, last 24h by hour)
- Vendor QC status donut chart (Recharts) — click segment → filter vendors
- City coverage map (Leaflet choropleth) — green/amber/red circles
- Import activity chart (Recharts, 7d/14d/30d picker)
- Search terms ranked list (top 20, last 7 days)
- System alerts section (HIGH/MED/LOW severity, direct action links)
- Recent activity feed (last 10 AuditLog entries, clickable)
- TanStack Query 5min staleTime, skeleton loading on all areas

#### `/geo/` — Geographic Management
- Left panel (320px): collapsible tree Country → City → Area → Landmark
- Right panel: inline editing, aliases array editor (tag-input style)
- City table with Launch Readiness indicator (checklist from API)
- "Launch City" button only enabled when all criteria pass
- Alias count < 3: warning badge
- Leaflet map preview for centroid + bounding box
- Role gate: DATA_MANAGER + SUPER_ADMIN write; all roles read

#### `/tags/` — Tag Management
- Dense table: Name, Slug, Tag Type (colored badge), Display Order, Is Active, Usage Count
- Filters: tag_type, is_active, search. Sort: display_order/name/usage_count
- Create/Edit in right Drawer with live preview of how tag appears on vendor cards
- Tag Usage modal: which vendors use it, assignment method, sparkline trend
- Bulk activate/deactivate with progress toast
- System Tags section: read-only, no create/edit/delete controls
- Role gate: CONTENT_MODERATOR (CATEGORY+INTENT), DATA_MANAGER+SUPER_ADMIN (all)

#### `/vendors/` — Vendor List + QC Queue
- Dense table: Logo, Business Name, City, Area, QC Status (badge), Data Source (badge), GPS (mini-map), Phone (masked), Created
- Filters: qc_status (multi-select), data_source, city, area (cascades), date range, search
- Inline: Quick Approve, Quick Reject, Open Detail. Bulk: Bulk Approve, Bulk Flag
- QC Queue sidebar item: count badge, shows PENDING + NEEDS_REVIEW only
- Claim Review Queue: vendor name, claimer phone/email, days waiting
- Location Change Review: side-by-side split map (old vs new GPS)

#### `/vendors/:id/` — Vendor Detail (full page, 6 tabs)
- Tab 1 Overview: business info + Leaflet map + QC widget + Approve/Reject/Flag buttons
- Tab 2 Field Photos: masonry grid, presigned URLs, lightbox, soft delete
- Tab 3 Visit History: timeline, GPS drift alert if >20m
- Tab 4 Tags: table with source label, Add/Remove controls
- Tab 5 Analytics: read-only stats summary
- Tab 6 Internal Notes (SUPER_ADMIN + QC_REVIEWER): qc_notes, timestamped

#### `/imports/` — Import Management
- Table with status badges: QUEUED (grey), PROCESSING (blue animated), DONE (green), FAILED (red)
- Auto-refresh every 10s for active jobs (TanStack Query refetchInterval)
- Drag-and-drop CSV upload, PapaParse preview (first 5 rows), missing columns in red
- Upload flow: CSV → S3 presigned URL → POST /api/v1/imports/ → job detail
- Job detail: progress bar, error log table, Retry button if FAILED
- Role gate: IMPORT_OPERATOR, DATA_MANAGER, SUPER_ADMIN

#### `/field-ops/` — Field Operations
- Visit table: Vendor Name, Agent, Visit Date, GPS Confirmed, Photos Count, Drift Alert
- FIELD_AGENT: only own visits (API enforced, not just frontend)
- Visit detail Drawer: vendor info, visit notes, side-by-side Leaflet maps (vendor vs confirmed GPS)
- Distance delta label, amber warning if >20m
- Photos grid with lightbox, presigned S3 upload
- Agent overview table with click-to-filter

#### `/qa/` — QA Dashboard
- GPS Drift Flags table: Vendor, City, Old GPS, New GPS, Distance Delta, Status
- Bulk resolve, "Run GPS Drift Scan Now" (SUPER_ADMIN only) with loading state + toast
- Duplicate Flags table: Vendor A, Vendor B, Similarity %, Distance, Status
- Compare modal: side-by-side vendor details
- Merge wizard: select canonical record, confirm data to keep

#### `/system/audit/` — Audit Log (SUPER_ADMIN only)
- Dense table (44px rows): Timestamp, Action, Actor, Target Type, Target ID, Request ID, IP
- Row expansion inline (not modal): before/after JSON diff (react-diff-viewer)
- Export CSV button (max 10,000 records)
- No edit or delete controls — immutable

#### `/system/users/` — User Management (SUPER_ADMIN only)
- Table: Full Name, Email, Role (badge), Last Login, Failed Attempts, Account Status (Locked with time remaining)
- Create User Drawer: auto-generated password shown once in copyable field
- Edit User Drawer: name, role, is_active only
- Unlock Account: confirmation modal → PATCH /api/v1/accounts/{id}/unlock/

### Step 38 — GPS Map Components
- `GPSInput.tsx`: lat/lng inputs + draggable Leaflet marker
- Leaflet choropleth for Platform Health Dashboard
- Split map for Location Change Review

### Step 39 — README
- Prerequisites, key generation commands, local dev setup, production deployment

---

## 7. PHASE B — VENDOR DASHBOARD PAGES

Vendor sidebar: My Business (Profile, Media) → Discounts → Performance → Voice Bot → Subscription

### Vendor Onboarding Wizard (first login after claim approval)
Full-page overlay, 6 steps, progress bar, skippable optional steps:
1. Confirm Business Details (pre-filled, vendor reviews + edits)
2. Add Location (Leaflet map with drag-pin)
3. Upload Logo and Cover Photo
4. Add First Video (optional — "3x more views" encouragement)
5. Review Your Package (Silver features + Gold upgrade prompt, never forced)
6. Go Live confirmation

### Vendor Profile Edit (`/vendor/profile/`)
- Business info: name, description (character count), phone, website
- Business Hours: visual weekly grid — click cells to set open/close per day. "Same as yesterday" convenience.
- Service Options: toggle cards for delivery + pickup with description fields
- Location: map embed + "Request Location Update" button (goes to admin review)
- Profile Completeness Widget: persistent sidebar widget, % progress bar, incomplete items list

### Discount Manager (`/vendor/discounts/`)
- Calendar view: colored blocks (Active=solid babu, Scheduled=dashed, Expired=grey). Toggle to list view.
- Create/Edit Drawer (4 steps):
  1. Type Selection: large visual cards with emoji icons
  2. Details: conditional fields, live badge preview, slider for % value
  3. Scheduling: datetime inputs + recurring day-selector chips
  4. Confirm: summary card + preview
- Discount Performance Table: Title, Type, Schedule, Views While Active, Status badge
- Subscription limit display: "Happy Hours used today: 1/3" or upgrade prompt for Silver

### Analytics (`/vendor/analytics/`)
- Overview (all tiers): hero metric "viewed X times this week", 3 metric cards with period comparison
- Bar chart: daily views over last 14 days
- Video Performance Table: thumbnail, title, view count, trend indicator
- Time-of-Day Heatmap (Diamond + Platinum): 7×24 grid. Silver+Gold: blurred overlay with upgrade message.
- Discount Performance (Gold+): views during active window vs same timeslot without discount
- Smart Recommendations (Platinum): 3 insight cards with pre-filled discount creation CTA
- Report Export (all tiers): PDF + CSV

### Voice Bot Setup (`/vendor/voice-bot/`)
- Feature gate: Silver → locked icon + upgrade prompt with demo audio
- Split panel: left = configuration, right = live test area
- Left: Menu Items (dynamic list), Delivery Info, Hours Summary (read-only), Custom Q&A Pairs
- Right: microphone button → speech → voice-query API → text response + browser TTS
- Last 5 test query history
- Completeness Score: "Your voice bot is X% configured"

### Subscription Management (`/vendor/subscription/`)
- Current Plan Card: plan name + badge, expiry, feature checklist, usage progress bars
- Upgrade Comparison Table: 4 plans as columns, current highlighted, features as rows
- Payment Flow (3 steps): Plan Summary → Payment Method (JazzCash/Easypaisa/Card) → Confirmation (confetti)
- Billing History Table: Date, Plan, Amount, Method, Status, Invoice download
- Cancellation Flow: "Manage Subscription" → downgrade at next renewal, confirm by typing business name

---

## 8. QUALITY GATE CHECKLIST

- [ ] All pages comply with DLS Prompts 2.1 and 2.2
- [ ] WCAG AA contrast (4.5:1 body text, 3:1 large text)
- [ ] All interactive elements keyboard accessible with visible focus ring
- [ ] All tables: empty state + skeleton loading (never spinners)
- [ ] All async mutations: toast notification
- [ ] No hardcoded hex colors anywhere — CSS custom properties only
- [ ] No icon-only buttons without `aria-label`
- [ ] `prefers-reduced-motion` respected
- [ ] Sidebar nav: pill-right pattern (`border-radius: 0 100px 100px 0`)
- [ ] `--color-rausch` primary button: max 1 per view
- [ ] Axios interceptor: 401 → refresh → retry → on failure redirect to /login
- [ ] TanStack Query: skeleton loading on initial load, staleTime configured
- [ ] Role-based nav: items hidden based on user role
- [ ] FIELD_AGENT sees only own visits (API enforced, verified in frontend too)
- [ ] All forms: real-time validation with plain-language error messages
- [ ] Skip-to-main-content link as first focusable element
- [ ] Screen reader labels on all tables (role, aria-sort, aria-label)
