# AirAd — Flutter Mobile App Build Plan
## Flutter 3.x + Dart (null-safety) — Customer Discovery + Vendor Mobile Management
### Phase B Only — Built AFTER Backend + Frontend are stable

---

## 0. ANALYSIS SUMMARY

The Flutter app is a **single codebase for both Customer and Vendor users**. It is the primary customer-facing product and provides a simplified vendor management interface.

**Core customer experience:**
- AR camera view with floating vendor bubbles (signature feature)
- Voice-driven search ("cheap pizza nearby")
- Tag-based browsing
- Vendor profile with reels, discounts, navigation

**Core vendor experience (mobile):**
- Claim business + setup wizard
- Quick discount creation
- Reel upload with trim editor
- Performance overview

**Critical rules:**
- AR camera feed processed LOCALLY only — never uploaded to servers
- Voice search: rule-based NLP only (no ML in Phase 1)
- Voice bot: rule-based matching against VoiceBotConfig (no ML)
- `vendor_has_feature()` gates enforced on both backend AND app UI
- Dark mode from day one (used outdoors)
- `prefers-reduced-motion` equivalent: respect system accessibility settings
- Never crash or show error screens offline — show cached results with banner
- Camera denied → hide AR, show map as default (never force permissions)

---

## 1. TECH STACK

| Tool | Purpose |
|---|---|
| Flutter 3.x + Dart (null-safety) | Framework |
| Riverpod (flutter_riverpod) | State management |
| Go Router | Navigation + deep link support |
| Dio | HTTP client with JWT interceptor |
| flutter_secure_storage | JWT token storage (Keychain/Keystore) |
| google_maps_flutter OR flutter_map | Map view |
| ar_flutter_plugin / arcore_flutter_plugin | AR camera view |
| speech_to_text | On-device speech recognition |
| camera | Camera access for AR + video recording |
| image_picker | Gallery video selection |
| video_player | Reel playback |
| connectivity_plus | Network state detection |
| geolocator | GPS location |
| flutter_compass | Compass/heading for AR |
| url_launcher | External navigation (Google Maps / Apple Maps) |
| google_fonts | DM Sans typography |
| cached_network_image | Presigned S3 image caching |
| dio_cache_interceptor | API response caching for offline |
| flutter_local_notifications | Push notification display |
| firebase_messaging | FCM push notifications |
| permission_handler | Unified permission management |

---

## 2. PROJECT STRUCTURE (Feature-Based)

```
mobile/
├── lib/
│   ├── main.dart                    # App entry, ProviderScope, GoRouter, ThemeData
│   ├── core/
│   │   ├── api/
│   │   │   ├── api_client.dart      # Dio instance + JWT interceptor + refresh logic
│   │   │   └── api_endpoints.dart   # All endpoint constants
│   │   ├── auth/
│   │   │   ├── auth_provider.dart   # Riverpod: auth state
│   │   │   └── token_storage.dart   # flutter_secure_storage wrapper
│   │   ├── theme/
│   │   │   ├── app_theme.dart       # ThemeData light + dark
│   │   │   └── app_colors.dart      # Color constants (matches DLS)
│   │   ├── router/
│   │   │   └── app_router.dart      # GoRouter config + guards
│   │   ├── permissions/
│   │   │   └── permissions_service.dart  # Location, Mic, Camera with rationale screens
│   │   ├── connectivity/
│   │   │   └── connectivity_provider.dart  # connectivity_plus Riverpod provider
│   │   └── utils/
│   │       ├── distance_formatter.dart
│   │       └── time_formatter.dart
│   ├── features/
│   │   ├── onboarding/
│   │   │   ├── models/
│   │   │   ├── providers/
│   │   │   └── screens/
│   │   │       ├── splash_screen.dart
│   │   │       ├── onboarding_screen.dart  # 3 swipeable screens
│   │   │       └── role_selection_screen.dart
│   │   ├── auth/
│   │   │   ├── models/
│   │   │   ├── providers/
│   │   │   └── screens/
│   │   │       ├── phone_entry_screen.dart
│   │   │       └── otp_screen.dart
│   │   ├── discovery/
│   │   │   ├── models/
│   │   │   ├── providers/
│   │   │   └── screens/
│   │   │       ├── discover_screen.dart    # Main home tab
│   │   │       └── widgets/
│   │   │           ├── vendor_card.dart
│   │   │           └── filter_chips_row.dart
│   │   ├── ar/
│   │   │   ├── providers/
│   │   │   └── screens/
│   │   │       └── ar_camera_screen.dart
│   │   │           # Widgets: vendor_bubble.dart
│   │   ├── map/
│   │   │   ├── providers/
│   │   │   └── screens/
│   │   │       └── map_screen.dart
│   │   ├── tags/
│   │   │   ├── providers/
│   │   │   └── screens/
│   │   │       └── tags_browser_screen.dart
│   │   ├── voice/
│   │   │   ├── providers/
│   │   │   └── screens/
│   │   │       ├── voice_search_overlay.dart
│   │   │       └── voice_bot_overlay.dart
│   │   ├── vendor_profile/
│   │   │   ├── models/
│   │   │   ├── providers/
│   │   │   └── screens/
│   │   │       ├── vendor_profile_screen.dart
│   │   │       └── widgets/
│   │   │           ├── reel_strip.dart
│   │   │           ├── discount_card.dart
│   │   │           └── hours_section.dart
│   │   ├── navigation/
│   │   │   └── screens/
│   │   │       └── navigation_screen.dart  # Walking directions
│   │   ├── saved/
│   │   │   ├── providers/
│   │   │   └── screens/
│   │   │       └── saved_vendors_screen.dart
│   │   ├── profile/
│   │   │   └── screens/
│   │   │       └── customer_profile_screen.dart
│   │   └── vendor_app/              # Vendor mode screens
│   │       ├── claim/
│   │       │   └── screens/
│   │       │       ├── find_business_screen.dart
│   │       │       ├── claim_confirm_screen.dart
│   │       │       └── pending_claim_screen.dart
│   │       ├── business/
│   │       │   └── screens/
│   │       │       └── vendor_profile_edit_screen.dart
│   │       ├── discounts/
│   │       │   └── screens/
│   │       │       └── discount_manager_screen.dart
│   │       ├── media/
│   │       │   └── screens/
│   │       │       ├── reel_management_screen.dart
│   │       │       └── video_upload_screen.dart
│   │       └── performance/
│   │           └── screens/
│   │               └── performance_screen.dart
├── test/
│   ├── unit/
│   │   ├── ranking_service_test.dart
│   │   ├── voice_parser_test.dart
│   │   └── distance_formatter_test.dart
│   ├── widget/
│   │   ├── vendor_card_test.dart
│   │   └── otp_screen_test.dart
│   └── integration/
│       └── auth_flow_test.dart
├── pubspec.yaml
└── README.md
```

---

## 3. THEMING (`core/theme/`)

### `app_colors.dart`
```dart
class AppColors {
  // Brand (matches DLS exactly)
  static const rausch    = Color(0xFFFF5A5F);
  static const babu      = Color(0xFF00A699);
  static const arches    = Color(0xFFFC642D);
  static const hof       = Color(0xFF484848);
  static const foggy     = Color(0xFF767676);

  // Light mode
  static const background = Color(0xFFF7F7F7);
  static const surface    = Color(0xFFFFFFFF);

  // Dark mode (higher saturation for outdoor use)
  static const darkBackground = Color(0xFF121212);
  static const darkSurface    = Color(0xFF1E1E1E);
  static const darkRausch     = Color(0xFFFF6B6F);  // slightly higher saturation
  static const darkBabu       = Color(0xFF00B8AA);
}
```

### `app_theme.dart`
```dart
// Light ThemeData:
//   colorScheme.primary = AppColors.rausch
//   colorScheme.secondary = AppColors.babu
//   scaffoldBackgroundColor = AppColors.background
//   cardColor = AppColors.surface
//   textTheme: DM Sans via google_fonts

// Dark ThemeData:
//   scaffoldBackgroundColor = AppColors.darkBackground
//   cardColor = AppColors.darkSurface
//   colorScheme.primary = AppColors.darkRausch
//   Same DM Sans typography

// Both themes: respect system theme via ThemeMode.system
```

---

## 4. NAVIGATION (`core/router/app_router.dart`)

### Route Structure
```
/splash                          → SplashScreen
/onboarding                      → OnboardingScreen
/role-selection                  → RoleSelectionScreen
/auth/phone                      → PhoneEntryScreen
/auth/otp                        → OtpScreen

/discover                        → DiscoverScreen (Customer home)
/discover/ar                     → ARCameraScreen
/map                             → MapScreen
/tags                            → TagsBrowserScreen
/saved                           → SavedVendorsScreen
/profile                         → CustomerProfileScreen
/vendor/:slug                    → VendorProfileScreen
/vendor/:slug/navigate           → NavigationScreen

/vendor-app/find                 → FindBusinessScreen
/vendor-app/claim/:id            → ClaimConfirmScreen
/vendor-app/pending              → PendingClaimScreen
/vendor-app/business             → VendorProfileEditScreen
/vendor-app/discounts            → DiscountManagerScreen
/vendor-app/media                → ReelManagementScreen
/vendor-app/performance          → PerformanceScreen
```

### Route Guards
```dart
// GoRouter redirect logic:
// - No token → /splash → /onboarding or /auth/phone
// - Valid token + CUSTOMER → /discover
// - Valid token + VENDOR (incomplete profile) → /vendor-app/find
// - Valid token + VENDOR (pending claim) → /vendor-app/pending
// - Valid token + VENDOR (approved) → /vendor-app/business
```

### Bottom Navigation
```
Customer mode: Discover | Map | Tags | Saved | Profile
Vendor mode:   My Business | Discounts | Performance | Profile
```

---

## 5. API CLIENT (`core/api/api_client.dart`)

```dart
// Dio instance with:
// - BaseOptions: baseUrl from env, connectTimeout 10s, receiveTimeout 30s
// - JWT interceptor:
//     → Add Authorization: Bearer {token} to all requests
//     → On 401: attempt refresh via /api/v1/auth/customer/refresh/ or vendor refresh
//     → On refresh success: retry original request
//     → On refresh failure: clear secure storage → navigate to /auth/phone
// - dio_cache_interceptor: cache GET requests for offline fallback
//   CachePolicy: forceCache when offline, refreshForceCache when online
// - Error interceptor: parse { success, data, message, errors } envelope
```

---

## 6. PERMISSIONS SERVICE (`core/permissions/`)

```dart
// Handles: Location (required), Microphone (voice search), Camera (AR + video)
//
// Flow for each permission:
//   1. Show rationale screen BEFORE system dialog
//      - Location: "AirAd needs your location to show nearby vendors"
//      - Microphone: "Enable your mic to search by voice"
//      - Camera: "Enable camera for AR view and video upload"
//   2. Request system permission
//   3. On denial:
//      - Location denied → city-level manual selection screen
//      - Mic denied → hide voice search icon (never show error)
//      - Camera denied → hide AR button, show map as default
//
// Never crash or block the app on permission denial
```

---

## 7. OFFLINE BEHAVIOR

```dart
// connectivity_plus Riverpod provider watches network state
// When offline:
//   - Persistent amber banner at top: "You're offline — showing cached results"
//   - Serve last cached discovery results for user's location
//   - Disable all write operations (create discount, upload video, etc.)
//   - Show "Connect to internet to use this feature" for write actions
//   - Never show error screens — always show cached content
// When back online:
//   - Banner dismisses automatically
//   - TanStack-equivalent (Riverpod + Dio cache) refreshes data
```

---

## 8. FEATURE BUILD SEQUENCE (Phase B — Sessions B-S6 + B-S7)

### Session B-S6: Setup + Auth + Discovery + AR

#### Step 1 — Project Setup
- `flutter create` with null-safety
- `pubspec.yaml`: all dependencies pinned to compatible versions
- `core/` folder: api_client, auth_provider, token_storage, app_theme, app_colors, app_router
- `main.dart`: ProviderScope, GoRouter, ThemeData (light + dark), DM Sans font

#### Step 2 — Splash + Onboarding + Role Selection
**SplashScreen:**
- AirAd logo centered, white background, 2 seconds
- Check auth state: valid JWT → route to correct home; no JWT → /onboarding

**OnboardingScreen (first-time only):**
- 3 swipeable PageView screens:
  1. "Discover what's around you right now" — AR concept illustration
  2. "Real deals from real nearby shops" — vendor cards illustration
  3. "Talk to find it, walk to get it" — voice + navigation illustration
- "Skip" top-right on all screens, "Get Started" CTA on last screen
- Stored in SharedPreferences: `onboarding_complete = true` after first view

**RoleSelectionScreen:**
- Two large cards: "I'm looking for places" (Customer) + "I have a business" (Vendor)
- Tapping either → PhoneEntryScreen with role stored in provider

#### Step 3 — Authentication
**PhoneEntryScreen:**
- Country code selector (pre-selected by device locale)
- Phone number input with validation
- "Continue" → POST /api/v1/auth/{customer|vendor}/send-otp/

**OtpScreen:**
- 6 individual digit boxes (Row of TextFields, each maxLength: 1)
- Auto-advance on digit entry (FocusNode.nextFocus)
- Auto-submit when all 6 filled
- 60-second countdown for resend (Timer)
- Loading indicator on verify
- On success: CUSTOMER → /discover; VENDOR (incomplete) → /vendor-app/find

#### Step 4 — Discover Screen (Customer Home)
**Layout:**
- Search bar (text + microphone icon) at top
- Horizontal scrollable quick-filter chips: "Cheap", "Open Now", "Nearby"
- AR camera button top-right (hidden if camera permission denied)
- Infinite scroll vendor cards

**VendorCard widget:**
- Cover photo (16:9, CachedNetworkImage)
- Vendor logo (40px circle, overlapping bottom-left)
- Vendor name, category, distance, open/closed status chip
- Active discount badge (rausch red) if currently running
- Subscription badge (Verified/Premium/Elite) top-right
- Video reel preview strip (3 thumbnail squares) if vendor has reels
- Voice bot microphone icon on logo if voice bot configured
- Interactions:
  - Tap → VendorProfileScreen
  - Long press → quick action BottomSheet: Get Directions, Call, Share
  - Swipe right → save to Favorites (heart animation)

**Infinite Scroll:**
- Load 20 vendors at a time, seamless scroll (never "Load More" button)
- Skeleton loader cards at bottom during loading
- Pull to refresh with current location

#### Step 5 — AR Camera Screen
**Entry:** AR camera icon → full-screen experience

**AR View:**
- Camera feed + compass heading + GPS → render floating vendor "bubbles"
- Each bubble: vendor name (bold), distance (e.g., "80m"), discount badge if active
- Bubble size varies by distance (closer = slightly larger)
- As user rotates phone: bubbles move with compass heading
- Max 5–8 bubbles at once (closest + highest-ranked)
- "X more nearby" indicator at bottom

**Bubble Interaction:**
- Tap bubble → VendorProfileScreen
- List button at bottom → slides up BottomSheet with full vendor list

**Device Fallback:**
- No compass/heading sensors OR inadequate GPU → automatically switch to map view
- One-time SnackBar: "AR view is not available on this device. Showing map view instead."

**Privacy:** Camera feed processed locally only. No recording or storage.

**Close:** X button top-left → back to Discover tab

#### Step 6 — Map Screen
**Full-screen map** (Google Maps or flutter_map):
- User location: pulsing blue dot
- Vendor pins: custom markers

**Pin Types:**
- Default: rausch red circle with category icon
- Active discount: larger pin with pulsing animation + discount badge
- Premium/Diamond: gold-outlined pin
- Tap pin → vendor summary BottomSheet (logo, name, distance, discount badge)
- Tap card → VendorProfileScreen

**Controls:**
- Radius indicator: translucent circle
- My Location button (bottom-right)
- Radius selector: 200m / 500m / 1km / 2km
- Filter button (top-right) → same tag filter sheet as Tags tab

**Cluster Behavior:**
- Dense areas: cluster pins into count circles
- Tap cluster → zoom in to reveal individual pins

**Vendor List Toggle:**
- Handle at bottom → slides up half-screen vendor list sorted by distance
- List updates as map is panned

---

### Session B-S7: Voice + Vendor Screens + Video

#### Step 7 — Tag-Based Browsing
**Tags Tab → BottomSheet:**
- Section 1 "What's happening now?" (PROMOTION + TIME tags): colored chips, orange bg on active deal tags
- Section 2 "What do you want?" (INTENT tags): chips with emoji icons
- Section 3 "What are you looking for?" (CATEGORY tags): grid of category cards with icon + name
- Section 4 "Near a specific place?" (LOCATION tags): area + landmark names as flat list

**Multi-Tag Selection:**
- Multiple tags combinable
- Selected tags: persistent filter bar at top with X chips + "Clear All"
- Live results update as tags selected
- Floating bubble: "14 vendors match your filters"
- Close sheet → see filtered results immediately

#### Step 8 — Voice Search + Voice Bot
**Voice Search (Discovery):**
- Triggered by microphone icon on Discover screen
- Full-screen overlay: centered animated waveform (AnimatedContainer)
- Prompt: "Say what you're looking for — like 'cheap pizza' or 'open pharmacy nearby'"
- `speech_to_text` plugin: on-device transcription
- Show transcription on screen → POST /api/v1/discovery/voice-search/
- Animate overlay down → show discovery results filtered by interpreted query
- Active filter chips show interpreted tags (e.g., "category: pizza, intent: cheap")
- Not understood: "I couldn't find that nearby. Try 'cheap food' or 'open cafe'."

**Vendor Voice Bot (Gold+ vendors only):**
- "Ask a question" microphone button on VendorProfileScreen
- Opens compact voice overlay for that vendor
- Transcribe → POST /api/v1/vendors/{slug}/voice-query/
- Show text response in chat-bubble style (one Q + one A, not a full chat UI)
- Play response via Flutter TTS (flutter_tts)
- Show last 3 Q+A pairs as user continues
- "Close" button dismisses

#### Step 9 — Vendor Profile Screen
**Sticky Header:**
- Cover photo (full-width, 220px), CachedNetworkImage
- Overlaid at bottom: vendor name (bold 22px), open/closed chip, distance, subscription badge
- Back arrow top-left, Share icon top-right
- On scroll: vendor logo (64px circle) slides over cover photo
- Action row: "Navigate", "Call", "Ask Bot" (if voice bot available)
- Rating: show NOTHING (Phase 1 — no empty stars)

**Video Reel Section:**
- Horizontally scrollable row of 9:16 aspect ratio reel cards
- Tap → full-screen VideoPlayer
- Reels auto-play (silently) when scrolled into view, pause when out

**About Section:** description, address, website link (url_launcher)

**Hours Section:** compact weekly view, highlight today's row, open/closed based on current time

**Active Discounts Section:**
- Active: prominent cards with countdown timer ("Ends in 1h 23m")
- Scheduled future: lighter upcoming cards

**Location Map Section:**
- Small non-interactive map preview with vendor pin
- "Get Directions" button → native navigation via url_launcher

**Service Options:** "Delivery Available" + "Pickup Available" chips

#### Step 10 — Navigation Screen (Walking Directions)
**Trigger:** "Navigate" button on VendorProfileScreen

**Logic:**
- Distance ≤ 2km: show in-app walking navigation
- Distance > 2km: show "Open in Google Maps" / "Open in Apple Maps" via url_launcher

**Navigation Screen:**
- Map with route drawn in rausch red (user location → vendor)
- Walking directions only

**Step-by-Step Panel (BottomSheet):**
- Current step in large text: "Turn right on Jinnah Avenue"
- Distance to next turn
- Step counter: "Step 2 of 7"
- Arrow indicator using compass heading

**Arrival Detection:**
- Within 30m of destination → "You've arrived!" screen
- Optional "I'm Here" confirmation button (analytics event)

**GPS Tracking:**
- Continuous location updates every 2 seconds (geolocator)
- Recalculate route if user deviates by >50m

#### Step 11 — Vendor App: Claim + Setup Flow
**Find My Business Screen:**
- Search bar at top, matching unclaimed listings as list
- Each result: name, address, "Claimed" / "Unclaimed" badge
- "Register New Business" button at bottom → submit details for admin review

**Claim Confirmation Screen:**
- "Is this your business?" with listing details
- "Yes, This Is My Business" CTA + "Not My Business" link
- On confirm: POST claim request

**Pending Claim State:**
- "Claim Submitted" screen with estimated review time
- Pending status bar until admin approves
- Push notifications on approval or rejection (FCM)

**Mobile Vendor Profile Edit (after approval):**
- Focus: photos (logo + cover), hours (mobile-optimized picker), delivery/pickup toggles
- Complex operations → "Manage on web portal" link

#### Step 12 — Vendor App: Discount Management
**Discounts Tab:**
1. Active Right Now: large live card with green pulsing indicator, countdown, "Stop Early" button
2. Upcoming: scheduled discounts with start time countdown
3. Past: recent history with views received during window

**Quick Create Discount (FAB):**
- Simplified BottomSheet:
  - Type selector: large emoji buttons
  - Duration: "Next 30 min", "Next 1 hour", "Next 2 hours", "Custom time"
  - Value input: large number field
  - Start Now toggle: ON = immediate; OFF = schedule
- Save → active section updates in real time

**Subscription Limit Display:**
- "Happy Hours used today: 1/3" (Diamond)
- Silver: "Happy Hours available from Gold plan" with upgrade link

#### Step 13 — Reel Management + Video Upload
**Reel Management Screen:**
- Vertical list (not grid): thumbnail, title, view count, upload date, drag handle for reordering
- Delete (with confirmation) + edit title per reel
- Upload limit progress: "1 of 1 used" (Silver) or "3 of 6 uploaded" (Diamond)
- Silver at limit: upload button disabled, "Upgrade to Gold for 3 videos"

**Video Upload Flow:**
- "Add Video" → BottomSheet: "Record Now" (camera plugin) or "Choose from Gallery" (image_picker)

**Trim Editor:**
- Horizontal scrubber with start + end drag handles
- Live preview of selected clip
- Max: 15 seconds, Min: 9 seconds

**Upload Confirmation:**
- Thumbnail preview (auto-captured from first frame)
- Title input field
- "Upload" button

**Upload Progress:**
- Chunked upload in background (Dio with FormData + onSendProgress)
- Persistent progress bar at top during upload
- Upload continues if user navigates away (background isolate or service)
- Local notification on completion
- After upload: reel appears immediately with "Processing" badge
- Visible to customers ONLY after backend processing completes

---

## 9. RIVERPOD STATE MANAGEMENT PATTERNS

### Auth Provider
```dart
// StateNotifier<AuthState>
// AuthState: { user, accessToken, refreshToken, userType }
// Methods: login(phone, otp), logout(), refreshToken()
// Persisted via flutter_secure_storage
```

### Discovery Provider
```dart
// StateNotifierProvider<DiscoveryNotifier, DiscoveryState>
// DiscoveryState: { vendors, isLoading, hasMore, activeFilters, currentLocation }
// Methods: loadMore(), refresh(), applyFilters(tags), applyVoiceSearch(query)
// Caches last successful results for offline use
```

### Location Provider
```dart
// StreamProvider<Position> from geolocator
// Handles permission check before streaming
// Falls back to last known position if permission denied
```

### Connectivity Provider
```dart
// StreamProvider<ConnectivityResult> from connectivity_plus
// Used by: offline banner, API client cache policy
```

### Vendor Provider
```dart
// FutureProvider.family<VendorDetail, String>(slug)
// Cached with dio_cache_interceptor
```

---

## 10. OFFLINE STRATEGY

| Scenario | Behavior |
|---|---|
| Discovery results | Cache last successful response per location |
| Vendor profile | Cache individual vendor details |
| Tags list | Cache for 24 hours |
| Write operations (discount, upload) | Disabled with "Connect to internet" message |
| Network restored | Auto-refresh all stale providers |
| Persistent banner | Amber banner: "You're offline — showing cached results" |

---

## 11. PUSH NOTIFICATIONS (FCM)

**Notification Types:**
- Claim approved / rejected
- Subscription expiry reminder (7 days + 1 day)
- New discount activated (for saved vendors)
- Vendor near user with active discount (proximity trigger)

**Implementation:**
- `firebase_messaging` for FCM token registration
- Token sent to backend on login: PATCH /api/v1/auth/{type}/profile/ with `device_token`
- `flutter_local_notifications` for foreground display
- Deep link routing via GoRouter on notification tap

---

## 12. TESTING PLAN

### Unit Tests
- `ranking_service_test.dart`: scoring formula with known inputs
- `voice_parser_test.dart`: rule-based NLP parsing (input → expected tags)
- `distance_formatter_test.dart`: "80m", "1.2km" formatting

### Widget Tests
- `vendor_card_test.dart`: renders all states (with/without discount, with/without reel strip)
- `otp_screen_test.dart`: auto-advance, auto-submit, countdown timer

### Integration Tests
- `auth_flow_test.dart`: phone entry → OTP → home screen routing

### Manual Test Checklist
- [ ] AR view on physical device (compass + GPS)
- [ ] Voice search on physical device (speech_to_text)
- [ ] Video upload with trim editor
- [ ] Offline mode: kill network, verify cached results + banner
- [ ] Permission denial flows: location, mic, camera
- [ ] Dark mode: all screens
- [ ] Navigation: walking route + arrival detection
- [ ] Push notifications: claim approval

---

## 13. QUALITY GATE CHECKLIST

**Architecture:**
- [ ] Feature-based folder structure — no cross-feature imports except through `core/`
- [ ] All state in Riverpod providers — no setState in business logic
- [ ] All API calls through `api_client.dart` — no raw Dio usage in features
- [ ] JWT interceptor: 401 → refresh → retry → on failure clear storage + redirect

**UX & Accessibility:**
- [ ] Dark mode from day one — all screens tested in dark mode
- [ ] DM Sans typography everywhere (google_fonts)
- [ ] Brand colors match DLS exactly (AppColors constants)
- [ ] Semantic labels on all interactive elements
- [ ] Respect system accessibility settings (text scale, reduced motion)

**Permissions:**
- [ ] Rationale screen shown BEFORE system permission dialog
- [ ] Location denied → city-level manual selection (never crash)
- [ ] Mic denied → voice search icon hidden (never error)
- [ ] Camera denied → AR hidden, map shown as default

**Offline:**
- [ ] Never crash or show error screen when offline
- [ ] Cached results served with amber banner
- [ ] Write operations disabled with clear message

**AR:**
- [ ] Camera feed never uploaded to server
- [ ] No recording or storage of AR sessions
- [ ] Device fallback: no compass/GPU → map view with one-time message

**Voice:**
- [ ] On-device transcription only (speech_to_text)
- [ ] Rule-based NLP — no ML calls
- [ ] Graceful failure: "I couldn't find that nearby"

**Vendor Feature Gates:**
- [ ] `vendor_has_feature()` checked before showing premium UI
- [ ] Silver at reel limit: upload disabled with upgrade message
- [ ] Silver voice bot: locked icon + upgrade prompt
- [ ] Happy hour limits displayed accurately

**Performance:**
- [ ] Reel auto-play only when scrolled into view
- [ ] CachedNetworkImage for all remote images
- [ ] Infinite scroll: 20 vendors per page, skeleton loaders
- [ ] AR: max 5–8 bubbles at once

---

## 14. SESSION BUILD ORDER

| Session | Prompts | Goal |
|---|---|---|
| B-S6 | 12.1–12.6 | Setup + Auth + Discovery + AR + Map |
| B-S7 | 12.7–12.12 | Voice + Vendor Profile + Navigation + Vendor App + Video |

**Gate before starting Flutter:** Backend Phase B APIs stable + tested. React vendor dashboard complete.

**Gate after B-S7:** Manual test on physical device (iOS + Android). All checklist items above pass.
