# AirAd — Airbnb Design Language System (DLS)
**Version:** 1.0 · **Date:** February 2026 · **Status:** Approved for Phase-1 Execution

> All UI in the AirAd Data Collection Portal **must** comply with sections A1–A14. No exceptions.

---

## A1 — Design Principles

| Principle | Definition | Portal Application |
|-----------|-----------|-------------------|
| **Unified** | Consistent experience across all surfaces | Same component library, token system, and interaction patterns across all 10 portal pages |
| **Universal** | Accessible and inclusive by default | WCAG 2.1 AA minimum, keyboard nav, screen reader labels on all tables and forms |
| **Iconic** | Simple, bold, purposeful — no decoration for decoration's sake | Use whitespace, clear hierarchy, purposeful color — no gratuitous gradients or shadows |
| **Conversational** | Design feels human — warm, clear, direct | Form labels as plain-language questions, error messages with helpful guidance, not codes |

---

## A2 — Color System

Apply as CSS custom properties. **Never hardcode hex values in components.**

```css
:root {
  /* Core Brand */
  --color-rausch:        #FF5A5F;  /* Primary CTAs, alerts — max 1 per view */
  --color-babu:          #00A699;  /* Success states, approvals, verified badges */
  --color-arches:        #FC642D;  /* Warnings, pending states */
  --color-hof:           #484848;  /* Primary text */
  --color-foggy:         #767676;  /* Secondary text, meta info */

  /* Extended Neutrals */
  --color-white:         #FFFFFF;
  --color-grey-100:      #F7F7F7;  /* Page backgrounds */
  --color-grey-200:      #EBEBEB;  /* Card borders, dividers */
  --color-grey-300:      #DDDDDD;  /* Input borders (default) */
  --color-grey-400:      #B0B0B0;  /* Placeholder text */
  --color-grey-500:      #767676;  /* Secondary text */
  --color-grey-700:      #484848;  /* Primary text */
  --color-grey-900:      #222222;  /* Headings */

  /* Semantic Colors */
  --color-success:       #008A05;
  --color-success-light: #E8F5E9;
  --color-warning:       #C45300;
  --color-warning-light: #FFF3E0;
  --color-error:         #C13515;
  --color-error-light:   #FFEBEE;
  --color-info:          #0077C8;
  --color-info-light:    #E3F2FD;

  /* AirAd AR Accent — data viz only, use sparingly */
  --color-airaad-accent: #00D4FF;
}
```

**Color usage rules:**
- `--color-rausch` → Primary action buttons only. Maximum **1 per view**.
- `--color-babu` → Success/completion states (GPS Validated badges, Approved status).
- `--color-arches` → Warning states (Pending QC, Needs Review, partial import).
- **Never use color alone** to convey status — always pair with icon + label text.
- Page backgrounds: `--color-grey-100` (not white) to reduce eye strain.

---

## A3 — Typography

**Font:** Circular (approximated with DM Sans for web).

```css
--font-family-base: 'Circular', 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-family-mono: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
```

| Token | Size | Weight | Line Height | Usage |
|-------|------|--------|-------------|-------|
| `--text-display` | 32px | 700 | 1.25 | Page hero titles (Dashboard H1) |
| `--text-heading-xl` | 26px | 600 | 1.3 | Section headings |
| `--text-heading-lg` | 22px | 600 | 1.35 | Card titles, modal headers |
| `--text-heading-md` | 18px | 600 | 1.4 | Subsection titles |
| `--text-heading-sm` | 16px | 600 | 1.4 | Table column headers |
| `--text-body-lg` | 16px | 400 | 1.6 | Primary body text |
| `--text-body-md` | 14px | 400 | 1.6 | Default UI text, table rows |
| `--text-body-sm` | 12px | 400 | 1.5 | Meta text, timestamps, captions |
| `--text-label` | 13px | 500 | 1.4 | Form labels, badge text |
| `--text-caption` | 11px | 400 | 1.4 | Footnotes, tooltips (min size) |

**Rules:**
- Minimum font size: **11px**
- Body text minimum contrast: **4.5:1** against background (WCAG AA)
- Never use more than **3 font weights** in a single view
- Use **sentence case** everywhere — not Title Case

---

## A4 — Spacing System (8px Base Grid)

All spacing must follow multiples of 8px. **Never use arbitrary pixel values.**

```css
:root {
  --space-1:  4px;   /* Tight: icon-to-label gaps */
  --space-2:  8px;   /* XS: inline element spacing */
  --space-3:  12px;  /* SM: tight component padding */
  --space-4:  16px;  /* MD: default component padding */
  --space-5:  20px;
  --space-6:  24px;  /* LG: card padding, section gaps */
  --space-8:  32px;  /* XL: between major sections */
  --space-10: 40px;  /* 2XL: page-level breathing room */
  --space-12: 48px;  /* 3XL: hero sections */
  --space-16: 64px;  /* 4XL: full-bleed separations */
}
```

**Grid system:**
- Sidebar width: `240px` (fixed)
- Content area max-width: `1280px` (centered)
- Page padding: `32px` horizontal, `40px` vertical top
- Card grid gap: `24px` minimum
- Table row height: `56px`
- Topbar height: `64px`

---

## A5 — Component Library

### A5.1 Buttons

```tsx
<Button variant="primary">   // bg: --color-rausch — ONE per view maximum
<Button variant="secondary"> // bg: white, border: 1px --color-grey-300
<Button variant="ghost">     // bg: transparent, hover: --color-grey-100
<Button variant="danger">    // bg: --color-error — destructive actions only
```

**Rules:**
- Border radius: `8px` (Airbnb signature)
- Min height: `48px` (primary), `40px` (secondary/ghost)
- Padding: `12px 24px` (primary), `10px 20px` (secondary)
- Loading state: spinner replaces label (never disable without feedback)
- Focus state: `2px solid --color-rausch` outline, `2px offset`
- Button labels: verb + noun — `"Import CSV"`, `"Approve vendor"`, `"View details"` — never `"OK"` or `"Submit"`

### A5.2 Form Inputs

```css
.dls-input {
  height: 48px;                          /* Prevents iOS zoom on focus */
  border: 1px solid var(--color-grey-300);
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 16px;
  transition: border-color 150ms ease;
}

.dls-input:hover  { border-color: var(--color-grey-700); }
.dls-input:focus  { border-color: var(--color-grey-900);
                    box-shadow: 0 0 0 2px rgba(72,72,72,0.2); }
.dls-input.error  { border-color: var(--color-error); }
.dls-input.valid  { border-color: var(--color-success); }
```

**Rules:**
- Validate on **blur**, not on every keystroke
- Error messages appear **below** the input in `--color-error`
- Required fields: asterisk (*) in label + `aria-describedby` for screen readers
- Never use placeholder-only labels (accessibility failure)

### A5.3 Cards

```css
.dls-card {
  background: var(--color-white);
  border: 1px solid var(--color-grey-200);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08);
}
```

**Rules:**
- No colored card backgrounds (white only)
- Status/KPI cards: left border `4px solid` in semantic color
- Avoid nesting cards inside cards (max 1 level)

### A5.4 Data Tables

```
Header row:   background --color-grey-100, font --text-heading-sm, border-bottom 2px
Data rows:    height 56px, padding 12px 16px, border-bottom 1px --color-grey-200
Hover:        background --color-grey-100
Selected:     background rgba(255,90,95,0.04), left border 3px --color-rausch
```

**Rules:**
- Always show row count: `"Showing 1–25 of 4,218 vendors"`
- Pagination: 25 rows default (options: 10 / 25 / 50 / 100)
- Sticky header on all tables with more than 10 rows
- Loading state: **skeleton rows** (not spinner) — same height as real rows
- Empty state: illustration + explanation + action CTA (never blank)

### A5.5 Status Badges / Chips

```tsx
<Badge variant="success">Approved</Badge>   // bg: success-light, text: success
<Badge variant="warning">Pending</Badge>    // bg: warning-light, text: warning
<Badge variant="error">Rejected</Badge>     // bg: error-light, text: error
<Badge variant="info">Processing</Badge>    // bg: info-light, text: info
<Badge variant="neutral">Unclaimed</Badge>  // bg: grey-100, text: foggy
```

**Rules:**
- Border radius: `100px` (pill shape)
- Padding: `4px 10px`
- Font: `--text-label` (13px, weight 500)
- Always include icon/dot prefix — **never text alone**

### A5.6 Modals / Drawers

- Overlay: `rgba(0,0,0,0.5)` + `backdrop-filter: blur(4px)`
- Modal container: white, `border-radius: 16px`, `padding: 32px`
- Max-width: `480px` (confirmations), `640px` (forms)
- Slide-in Drawer: `width: 640px`, from right
- Close: X button + ESC key + backdrop click
- Always **trap focus** inside modal
- Action buttons: right-aligned, primary button is **rightmost**

### A5.7 Sidebar Navigation

```
Width: 240px fixed
Nav item height: 44px
Nav item border-radius: 0 100px 100px 0  (pill-right)
Nav item margin-right: 16px

States:
  default → text: --color-foggy
  hover   → background: --color-grey-100, text: --color-grey-900
  active  → background: rgba(255,90,95,0.08), text: --color-rausch, weight: 600

Section labels: 11px, 700, uppercase, letter-spacing: 1px, color: --color-grey-400
```

### A5.8 Empty States

Every list/table must have an empty state:

```
[Simple line-art illustration]
     Heading: Clear, plain language
  Subheading: Why it's empty + what to do
      Button: Primary action to fill the empty state
```

Examples:
- Vendors table empty → `"No vendors yet — start by importing data"` + `[Import CSV]`
- QA queue empty → `"You're all caught up! No vendors pending GPS validation"`

---

## A6 — Iconography

**Library:** `lucide-react` exclusively.

**Rules:**
- Size: `16px` (inline), `20px` (nav), `24px` (standalone), `32px` (empty states)
- Stroke width: `1.5` (Airbnb signature — not bold 2.0)
- Stroke only — **never filled icons**
- Always pair icons with visible text labels in navigation

---

## A7 — Motion & Animation

```css
--duration-instant:  100ms;  /* Hover state changes */
--duration-fast:     150ms;  /* Button presses, badge changes */
--duration-normal:   250ms;  /* Modal open, drawer slide */
--duration-slow:     350ms;  /* Page transitions */
--ease-standard:     cubic-bezier(0.4, 0, 0.2, 1);
--ease-enter:        cubic-bezier(0.0, 0.0, 0.2, 1);
--ease-exit:         cubic-bezier(0.4, 0.0, 1, 1);
```

**Rules:**
- `prefers-reduced-motion: reduce` → disable ALL animations
- Skeleton loaders: `1.5s` shimmer, `linear`, infinite
- Page entry: `fadeUp` — `opacity 0→1` + `translateY(8px→0)`, `250ms`
- Drawer slide: `350ms ease-standard` from right
- Toast: slide from bottom-right, auto-dismiss `4s`
- **No bouncing, spinning, or looping animations** in production UI

---

## A8 — Layout System

```
┌────────────────────────────────────────────────────────┐
│  TOPBAR  [Breadcrumb]     [Search]   [Notif] [Avatar]  │ height: 64px
├──────────┬─────────────────────────────────────────────┤
│          │                                              │
│ SIDEBAR  │  PAGE CONTENT AREA                          │
│ 240px    │  max-width: 1280px, padding: 40px 32px      │
│ fixed    │                                              │
│          │  ┌──────────────────────────────────────┐   │
│          │  │ PAGE HEADER (title + actions)         │   │ height: 80px
│          │  ├──────────────────────────────────────┤   │
│          │  │ FILTERS BAR                           │   │ height: 56px
│          │  ├──────────────────────────────────────┤   │
│          │  │ MAIN CONTENT (table / cards / map)    │   │
│          │  └──────────────────────────────────────┘   │
└──────────┴─────────────────────────────────────────────┘
```

**Page Header pattern:**
```tsx
<PageHeader
  title="Vendor management"       // --text-display, sentence case
  subtitle="4,218 vendors total"  // --text-body-lg, --color-foggy
  actions={<Button variant="primary">Import CSV</Button>}
/>
```

**Filters Bar pattern:**
```tsx
<FiltersBar>
  <SearchInput placeholder="Search vendors..." />
  <Select label="City" />
  <Select label="QC Status" />
  <Select label="Data source" />
  <Button variant="ghost">Clear filters</Button>
  <span>Showing 4,218 results</span>
</FiltersBar>
```

---

## A9 — Form Design

- Single-column for fewer than 8 fields; two-column grid for longer forms
- Most important / required fields first
- Submit button: right-aligned on desktop, full-width on mobile
- Validation on **blur** only

---

## A10 — Data Visualization (Recharts)

**Chart color sequence:**
1. `--color-rausch` (#FF5A5F)
2. `--color-babu` (#00A699)
3. `--color-arches` (#FC642D)
4. `--color-info` (#0077C8)
5. `--color-grey-400` (#B0B0B0)

**Rules:**
- Grid lines: `--color-grey-200`, `1px`, dashed
- No 3D charts ever
- No pie charts for more than 5 segments (use bar chart instead)
- Area charts: fill opacity `0.08`

**Required charts for portal:**

| Page | Chart Type | Data |
|------|-----------|------|
| Dashboard | KPI Stat Cards (4-up) | Vendors, GPS %, Tag %, Coverage |
| Dashboard | Choropleth Map | Vendor density per area |
| Analytics | Line Chart | Vendor acquisition over time |
| Analytics | Horizontal Bar | Coverage per area vs. 500 target |
| Import Center | Progress Bar | Real-time batch import |
| QA Center | Progress Bar | Tag accuracy vs. 95% target |

---

## A11 — Accessibility (WCAG 2.1 AA — Mandatory)

**Contrast ratios:**
- Normal text (≤18px): **4.5:1 minimum**
- Large text / UI components: **3:1 minimum**
- `--color-foggy` (#767676) on white = 4.48:1 ✓ passes AA
- `--color-rausch` (#FF5A5F) on white = 3.04:1 — **large text and icons only**

**Keyboard navigation:**
- All interactive elements reachable via Tab
- Logical focus order (top-left to bottom-right)
- Visible focus ring: `2px solid --color-rausch` on ALL elements
- First focusable element: skip-to-content link
- Modal focus trap (Tab cycles within open modal)
- ESC closes modals and drawers

**Screen readers:**
- Data tables: `<th scope="col/row">`, `<caption>`, `aria-sort`
- Status badges: `aria-label="Status: Approved"` (not just color)
- Form errors: `aria-describedby` linking input to error message
- Dynamic content: `aria-live="polite"` for toasts and status updates
- Icons paired with text: `aria-hidden="true"` on the icon

**Touch targets:**
- Minimum **44×44px** for all interactive elements
- 8px minimum spacing between adjacent touch targets

---

## A12 — Responsive Behavior

| Breakpoint | Behavior |
|-----------|---------|
| `1280px+` | Full sidebar + 3-column KPI grid |
| `1024px` | Full sidebar + 2-column KPI grid |
| `768px` | Sidebar collapses to icon rail |
| `375px` | Hamburger menu, single column |

Tables at <1024px: horizontal scroll, sticky first column, reduce row padding to `--space-3`.

---

## A13 — Loading & Empty States

**Skeleton screens (preferred over spinners):**
```tsx
<TableSkeleton rows={10} columns={7} />   // Shimmer bars matching real layout
<StatCardSkeleton />                       // 4 cards, shimmer
<MapSkeleton />                            // Grey rectangle, same aspect ratio
```

**Loading priority (perceived performance):**
1. Page chrome renders immediately (sidebar, header)
2. Skeleton appears for content areas
3. Critical data loads first (KPI numbers)
4. Secondary data loads progressively

**Toast notifications:**
```tsx
toast.success("Vendor approved")           // green, auto-dismiss 4s
toast.error("GPS validation failed")       // red, 6s, manual dismiss
toast.warning("Duplicate detected")        // orange, 6s, with action
toast.info("Import batch queued")          // blue, auto-dismiss 4s
```

Position: bottom-right. Stack up to 3 visible (FIFO). Slide up from bottom, fade on dismiss.

---

## A14 — Writing Style

**Rules:**
- **Sentence case** for everything (not Title Case)
- Address the user directly: `"Your import completed"` not `"Import completed"`
- Be specific in errors — no error codes
- Confirmation messages: past tense `"Vendor approved"` not `"Vendor has been approved"`
- Button labels: verb + noun — never `"OK"` or `"Submit"`

| ✕ Don't | ✓ Do |
|---------|------|
| `"Error 422: Unprocessable Entity"` | `"GPS accuracy must be 10m or less"` |
| `"Operation completed successfully"` | `"Vendor approved"` |
| `"No records found"` | `"No vendors match your filters"` |
| `"Are you sure? This cannot be undone"` | `"Remove this vendor? This will archive their data."` |
| `"Submit"` / `"OK"` | `"Save vendor"` / `"Approve"` / `"Import CSV"` |

---

## AirAd — AR Visibility Scoring Formula

```
Final AR Score =
  (Intent Match      × 0.30) +
  (Distance Weight   × 0.25) +
  (Active Promotion  × 0.15) +
  (Engagement Score  × 0.15) +
  (Subscription Mult × 0.15)
```

**Subscription multipliers:**

| Tier | Price | Multiplier |
|------|-------|-----------|
| Silver | Free | 1.0× |
| Gold | PKR 3,000/mo | 1.2× |
| Diamond | PKR 7,000/mo | 1.5× |
| Platinum | PKR 15,000/mo | 2.0× |

> Paid tier cannot override distance relevance by more than 30%.

---

## AirAd — 5-Layer Tag System

| Layer | Type | Set By | Examples |
|-------|------|--------|---------|
| **Layer 1** | Category — *What the vendor IS* | Vendor (max 3) | Food, Pizza, Cafe, BBQ, Salon |
| **Layer 2** | Intent — *Why users search* | Vendor | Cheap, BudgetUnder300, Halal, Quick |
| **Layer 3** | Promotion — *Time-bound campaigns* | Auto-generated | DiscountLive, HappyHour, FlashDeal |
| **Layer 4** | Time Context — *Clock-based* | Auto-generated | OpenNow, Lunch, Dinner, LateNightOpen |
| **Layer 5** | System — *Invisible to users* | Platform only | ClaimedVendor, ARPriority, HighEngagement |

---

## Portal Pages

| Page | Route | Primary Role |
|------|-------|-------------|
| Dashboard | `/` | Platform health, KPIs, alerts, coverage map |
| Vendor Management | `/vendors` | Full data table, bulk actions, filters |
| Vendor Detail | `/vendors/:id` | GPS map, tags, photos, QC decision |
| Geographic Management | `/geo` | Country / City / Area / Landmark CRUD |
| Tag Management | `/tags` | All 5 layers, usage counts, add/deprecate |
| Import Center | `/import` | CSV drag-drop, Google Places, batch history |
| Field Operations | `/field` | Assignment map, visit log, photo review |
| QA Center | `/qa` | GPS queue, duplicates, tag audit, drift |
| Analytics | `/analytics` | KPI charts, trends, source breakdown |
| Admin & Audit | `/admin` | User management, audit log (SUPER_ADMIN) |

---

## Phase-1 KPI Targets

| Metric | Target |
|--------|--------|
| Vendors per launch area | 500+ minimum |
| GPS accuracy ≤10m | 95% of listings |
| Tag accuracy | 95% minimum |
| Voice bot intent accuracy | 85% minimum |
| AR marker render time | <2 seconds |
| Vendor claim rate (Month 1) | 15% minimum |
| Platform uptime | 99.5% |
| API response time (p95) | <200ms |

---

*AirAd Phase-1 — DLS Reference v1.0 · Authority: Airbnb Design Language System A1–A14*
