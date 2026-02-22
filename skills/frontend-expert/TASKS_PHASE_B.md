# AirAd Frontend — Phase B Task Breakdown
## Vendor Dashboard: Profile · Discounts · Analytics · Voice Bot · Subscription
### Phase B — Public Platform (after Phase A sign-off)

> **Parent Index:** [`TASKS_INDEX.md`](./TASKS_INDEX.md)
> **Prerequisites:** Phase A complete + Phase B backend APIs live
> **Priority:** All tasks P3 (Phase B only — do not start until Phase A is signed off)
> **Last Updated:** 2026-02-22

---

## Phase B Architecture Notes

### New Layout
- `VendorLayout.tsx` — separate from `AdminLayout`
- Vendor sidebar: My Business (Profile, Media) → Discounts → Performance → Voice Bot → Subscription
- Route prefix: `/vendor/`
- Auth: same JWT flow as Phase A — vendor users have a different role (Phase B backend defines this)

### Subscription Tier Gating
Phase B features are gated by subscription tier. The frontend must:
- Read the vendor's current plan from the subscription API response
- Use a `TierGate` component (similar to `RoleGate`) to show/hide/blur features
- **Never hard-code tier logic in page components** — always use `TierGate`

```typescript
interface TierGateProps {
  requiredTier: 'Silver' | 'Gold' | 'Diamond' | 'Platinum';
  fallback?: React.ReactNode; // blurred overlay with upgrade prompt
  children: React.ReactNode;
}
```

### Phase B API Endpoints
Phase B backend APIs are stubs in Phase A. The following endpoints are expected but **not yet implemented**. Do NOT build Phase B pages until these endpoints are confirmed live:
- `/api/v1/vendor/profile/` — vendor profile CRUD
- `/api/v1/vendor/discounts/` — discount management
- `/api/v1/vendor/analytics/` — vendor analytics
- `/api/v1/vendor/voice-bot/` — voice bot config
- `/api/v1/vendor/subscription/` — subscription management

---

## GROUP B1 — VENDOR ONBOARDING WIZARD

### TASK-B1-01 · Vendor Onboarding Wizard
**Priority:** P3 | **Effort:** L
**File:** `src/features/vendor-dashboard/components/OnboardingWizard.tsx`
**Trigger:** First login after claim approval (flag in vendor profile response)

**Structure:** Full-page overlay, 6 steps, progress bar at top, skippable optional steps

**Step 1 — Confirm Business Details:**
- Pre-filled from vendor profile API response
- Vendor reviews + edits: `business_name`, `description`, `phone`, `website`
- Form validation (Zod): `business_name` required, `phone` format

**Step 2 — Add Location:**
- `GPSInput` component with Leaflet map + drag-pin
- "Use my current location" button (browser Geolocation API)
- Submits GPS as GeoJSON Point: `{ type: "Point", coordinates: [lng, lat] }`

**Step 3 — Upload Logo and Cover Photo:**
- Logo: square crop, max 2MB, JPEG/PNG
- Cover: 16:9 crop, max 5MB, JPEG/PNG
- Upload via presigned URL flow (same pattern as field photos)

**Step 4 — Add First Video (optional):**
- Skippable — "Skip for now" link
- Encouragement copy: "Businesses with videos get 3× more views"
- Video URL input (YouTube/Vimeo embed) or direct upload

**Step 5 — Review Your Package:**
- Shows current plan (Silver by default)
- Feature checklist for Silver
- Gold upgrade prompt card (never forced — "Learn More" link only)
- No payment flow in this step

**Step 6 — Go Live Confirmation:**
- Summary card: business name, location, plan
- "Go Live" primary button
- Confetti animation on click (respects `prefers-reduced-motion`)
- Marks onboarding complete in vendor profile

**Acceptance Criteria:**
- [ ] Progress bar shows correct step (1/6, 2/6, etc.)
- [ ] Optional steps (4) have visible "Skip" link
- [ ] GPS step uses `GPSInput` component with correct GeoJSON coordinate order
- [ ] Wizard only shown on first login (flag from profile API)
- [ ] "Go Live" confetti respects `prefers-reduced-motion`
- [ ] Completing wizard marks onboarding as done — never shown again

---

## GROUP B2 — VENDOR PROFILE

### TASK-B2-01 · Vendor Profile Edit Page
**Priority:** P3 | **Effort:** M
**File:** `src/features/vendor-dashboard/components/VendorProfilePage.tsx`
**Route:** `/vendor/profile/`

**API Calls:**
- `GET /api/v1/vendor/profile/` — load profile
- `PATCH /api/v1/vendor/profile/` — save changes

**Sections:**

**Business Info:**
- `business_name` (required), `description` (Textarea, character count display, max 500 chars), `phone`, `website`
- Character count: "247 / 500" shown below textarea, turns red at 480+

**Business Hours:**
- Visual weekly grid: 7 rows (Mon–Sun) × time slots
- Click cells to set open/close time per day
- "Same as yesterday" convenience button per row
- Toggle: "Closed" for a day

**Service Options:**
- Toggle cards: Delivery (with description field) + Pickup (with description field)
- Toggle uses DLS `Toggle` component

**Location:**
- Leaflet map embed (read-only view of current GPS)
- "Request Location Update" button → opens Modal explaining it goes to admin review
- Does NOT directly update GPS — creates a review request

**Profile Completeness Widget (persistent sidebar):**
- Percentage progress bar
- List of incomplete items with direct links to the relevant section
- Updates in real-time as user fills in fields

**Acceptance Criteria:**
- [ ] Character count shown for description, turns red at 480+
- [ ] Business hours grid allows per-day open/close time setting
- [ ] "Same as yesterday" copies previous day's hours
- [ ] "Request Location Update" opens informational modal — does NOT directly update GPS
- [ ] Profile completeness widget updates as fields are filled
- [ ] All changes require explicit "Save" — no auto-save

---

## GROUP B3 — DISCOUNT MANAGER

### TASK-B3-01 · Discount Manager Page
**Priority:** P3 | **Effort:** L
**File:** `src/features/vendor-dashboard/components/DiscountManagerPage.tsx`
**Route:** `/vendor/discounts/`

**API Calls:**
- `GET /api/v1/vendor/discounts/` — discount list
- `POST /api/v1/vendor/discounts/` — create discount
- `PATCH /api/v1/vendor/discounts/{id}/` — update
- `DELETE /api/v1/vendor/discounts/{id}/` — delete

**Calendar View (default):**
- Colored blocks per discount: Active=solid `--color-babu`, Scheduled=dashed `--color-arches`, Expired=`--color-grey-300`
- Click block → opens edit Drawer
- Toggle button: "Calendar" / "List" view (persists in URL `?view=calendar`)

**List View:**
- Table columns: Title, Type, Schedule, Views While Active, Status badge, Actions

**Create/Edit Drawer — 4 Steps:**

**Step 1 — Type Selection:**
- Large visual cards with emoji icons for each discount type
- Types (from backend tag system): PERCENTAGE_OFF, FIXED_AMOUNT, BUY_X_GET_Y, HAPPY_HOUR, etc.
- Single selection, highlighted on click

**Step 2 — Details:**
- Conditional fields based on type:
  - PERCENTAGE_OFF: slider (0–100%) + live badge preview
  - FIXED_AMOUNT: currency input
  - BUY_X_GET_Y: quantity inputs
  - HAPPY_HOUR: time range inputs
- Live badge preview: shows how discount badge will appear on vendor card

**Step 3 — Scheduling:**
- Start datetime + End datetime inputs
- Recurring: day-selector chips (Mon/Tue/Wed/Thu/Fri/Sat/Sun)
- "Active now" toggle (overrides scheduling)

**Step 4 — Confirm:**
- Summary card: type, value, schedule
- Preview of vendor card with discount badge
- "Create Discount" primary button

**Subscription Limit Display:**
- "Happy Hours used today: 1/3" — from subscription API
- Silver plan: "Upgrade to Gold for unlimited Happy Hours" prompt (never forced)

**Acceptance Criteria:**
- [ ] Calendar view shows colored blocks per discount status
- [ ] Toggle between calendar and list view persists in URL
- [ ] Create drawer has 4 steps with progress indicator
- [ ] Conditional fields shown based on discount type selection
- [ ] Live badge preview updates as user changes discount value
- [ ] Subscription limit shown for Happy Hour type
- [ ] Delete requires confirmation modal

---

## GROUP B4 — VENDOR ANALYTICS

### TASK-B4-01 · Vendor Analytics Page
**Priority:** P3 | **Effort:** L
**File:** `src/features/vendor-dashboard/components/VendorAnalyticsPage.tsx`
**Route:** `/vendor/analytics/`

**API Calls:**
- `GET /api/v1/vendor/analytics/` — analytics data (tier-gated response)

**Sections by Subscription Tier:**

**All Tiers — Overview:**
- Hero metric: "Your business was viewed X times this week"
- 3 metric cards with period comparison (this week vs last week): Views, Search Appearances, Direction Requests
- Bar chart: daily views over last 14 days (Recharts `BarChart`)

**All Tiers — Video Performance Table:**
- Thumbnail, title, view count, trend indicator (up/down arrow + %)

**Diamond + Platinum — Time-of-Day Heatmap:**
- 7×24 grid (days × hours)
- Cell color intensity = view count
- Silver + Gold: blurred overlay with "Upgrade to Diamond to unlock" message
- `TierGate` component with blurred fallback

**Gold+ — Discount Performance:**
- Views during active discount window vs same timeslot without discount
- Bar chart comparison (Recharts)
- Silver: `TierGate` with upgrade prompt

**Platinum — Smart Recommendations:**
- 3 insight cards: "Your busiest time is Friday 6–8pm. Create a Happy Hour discount."
- Each card has pre-filled "Create Discount" CTA button
- Silver/Gold/Diamond: `TierGate` with upgrade prompt

**All Tiers — Report Export:**
- "Export PDF" + "Export CSV" buttons
- PDF: browser `window.print()` with print-optimized CSS
- CSV: client-side PapaParse unparse

**Acceptance Criteria:**
- [ ] All tiers see Overview + Video Performance
- [ ] Time-of-Day Heatmap blurred for Silver + Gold (not hidden — blurred with upgrade prompt)
- [ ] Discount Performance blurred for Silver
- [ ] Smart Recommendations blurred for Silver/Gold/Diamond
- [ ] `TierGate` component used for all tier-gated sections — no inline tier logic
- [ ] Export buttons work for all tiers

---

## GROUP B5 — VOICE BOT SETUP

### TASK-B5-01 · Voice Bot Setup Page
**Priority:** P3 | **Effort:** M
**File:** `src/features/vendor-dashboard/components/VoiceBotPage.tsx`
**Route:** `/vendor/voice-bot/`

**API Calls:**
- `GET /api/v1/vendor/voice-bot/` — config
- `PATCH /api/v1/vendor/voice-bot/` — save config
- `POST /api/v1/vendor/voice-bot/test/` — test query

**Tier Gate:** Silver+ only. Bronze/Free: locked icon + upgrade prompt + demo audio player.

**Layout:** Split panel — left config (60%) + right live test (40%)

**Left Panel — Configuration:**
- Menu Items: dynamic list (add/remove/reorder) — each item: name + price + description
- Delivery Info: delivery radius, minimum order, delivery fee
- Hours Summary: read-only display (from business hours in profile)
- Custom Q&A Pairs: dynamic list — question + answer pairs

**Completeness Score:**
- "Your voice bot is X% configured"
- Progress bar + list of missing items
- Updates in real-time as user fills in fields

**Right Panel — Live Test:**
- Microphone button → browser `MediaRecorder` API → speech-to-text
- Text input fallback (for non-microphone environments)
- Submit → `POST /api/v1/vendor/voice-bot/test/` with `{ query: string }`
- Response: text answer + browser TTS (`window.speechSynthesis.speak()`)
- Last 5 test query history (in-memory, not persisted)

**Acceptance Criteria:**
- [ ] Silver+ tier gate: locked icon + upgrade prompt + demo audio for lower tiers
- [ ] Menu items support add/remove/reorder
- [ ] Microphone button uses browser `MediaRecorder` API
- [ ] Text input fallback available when microphone not available
- [ ] Browser TTS reads out the voice bot response
- [ ] Last 5 test queries shown in history
- [ ] Completeness score updates in real-time

---

## GROUP B6 — SUBSCRIPTION MANAGEMENT

### TASK-B6-01 · Subscription Management Page
**Priority:** P3 | **Effort:** L
**File:** `src/features/vendor-dashboard/components/SubscriptionPage.tsx`
**Route:** `/vendor/subscription/`

**API Calls:**
- `GET /api/v1/vendor/subscription/` — current plan + billing history
- `POST /api/v1/vendor/subscription/upgrade/` — initiate upgrade
- `POST /api/v1/vendor/subscription/cancel/` — cancel/downgrade

**Current Plan Card:**
- Plan name + badge (Silver/Gold/Diamond/Platinum)
- Expiry date
- Feature checklist (what's included in current plan)
- Usage progress bars: "Happy Hours used today: 1/3", "Videos uploaded: 2/5"

**Upgrade Comparison Table:**
- 4 plans as columns (Silver, Gold, Diamond, Platinum)
- Current plan highlighted with `--color-rausch` border
- Features as rows with ✓/✗ per plan
- "Upgrade" button per column (disabled for current plan + lower plans)

**Payment Flow — 3 Steps (in Modal):**

**Step 1 — Plan Summary:**
- Selected plan name, price, billing period
- Feature diff: "You'll gain access to: [list]"

**Step 2 — Payment Method:**
- Payment options: JazzCash, Easypaisa, Card (debit/credit)
- Each option: large visual card with logo
- Card option: card number, expiry, CVV inputs (masked)
- No actual payment processing in frontend — submits to backend payment endpoint

**Step 3 — Confirmation:**
- Success state: confetti animation + "Welcome to {Plan}!" heading
- Plan badge updated immediately (optimistic)
- Confetti respects `prefers-reduced-motion`

**Billing History Table:**
- Columns: Date, Plan, Amount, Payment Method, Status (Badge), Invoice (download link)
- Invoice download: link from API response (presigned URL or PDF endpoint)

**Cancellation Flow:**
- "Manage Subscription" → "Cancel Subscription" link
- Drawer: explains downgrade at next renewal (not immediate)
- Confirmation: user must type their `business_name` exactly to confirm
- Submit → `POST /api/v1/vendor/subscription/cancel/`

**Acceptance Criteria:**
- [ ] Current plan highlighted in comparison table
- [ ] Payment flow is 3 steps with progress indicator
- [ ] Confetti on successful upgrade (respects `prefers-reduced-motion`)
- [ ] Cancellation requires typing exact business name to confirm
- [ ] Cancellation is downgrade at next renewal — not immediate
- [ ] Billing history shows all past invoices with download links
- [ ] Usage progress bars reflect actual limits from subscription API

---

## Phase B Global Acceptance Criteria

- [ ] `VendorLayout` is completely separate from `AdminLayout` — no shared layout components
- [ ] `TierGate` component used for ALL tier-gated features — no inline tier logic in pages
- [ ] All Phase B routes prefixed with `/vendor/`
- [ ] Onboarding wizard shown only on first login (never again after completion)
- [ ] All Phase B pages comply with same DLS rules as Phase A (no exceptions)
- [ ] All Phase B API calls use same Axios instance + JWT interceptor from Phase A
- [ ] Phase B routes added to `router.tsx` with `ProtectedRoute` guard
- [ ] Phase B feature gating is always blurred overlay (not hidden) — user can see what they're missing

---

## Phase B Implementation Order

```
B1-01  Vendor Onboarding Wizard    ← first login experience
B2-01  Vendor Profile Edit         ← core data
B3-01  Discount Manager            ← primary vendor value
B4-01  Vendor Analytics            ← engagement + retention
B5-01  Voice Bot Setup             ← Silver+ differentiator
B6-01  Subscription Management     ← monetization
```
