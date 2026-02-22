# **AirAd Phase-1**
# **End User Functional Document**

**Version: 1.0**  
**Date: February 2026**  
**Status: Approved for Phase-1 Execution**

---

## **Executive Summary**

This document defines the complete end-user experience, functionality, and workflows for AirAd Phase-1. It serves as the authoritative reference for understanding user discovery patterns, interaction models, personalization strategies, and engagement metrics.

AirAd's user experience is built around the core question:  
**"What can I get right now, near me, with value?"**

The platform delivers instant, location-aware discovery through three primary interaction modes:
1. **AR-First Exploration** (camera-based, spatial discovery)
2. **Voice-Driven Search** (natural language queries)
3. **Tag-Based Browsing** (category and intent filtering)

**Critical Design Principle:** Minimize friction, maximize speed to decision.

---

## **1. Purpose & Scope**

### **1.1 Document Purpose**

This document establishes:
- Complete user journey mapping (discovery → engagement → conversion)
- AR interaction models and visual design requirements
- Voice search workflow and query handling
- Tag-based filtering and exploration patterns
- Personalization and recommendation logic
- Notification strategies and engagement triggers
- User analytics and behavioral tracking

### **1.2 Scope Boundaries**

**Included in Phase-1:**
- AR vendor discovery and navigation
- Voice and text search
- Tag-based exploration
- Reel viewing (vendor-created short videos)
- Promotion engagement (discounts, happy hours)
- Turn-by-turn navigation
- Basic user preferences

**Explicitly Excluded:**
- Social networking features (no friend connections, sharing, commenting)
- User-generated content (no reviews, ratings, photos)
- In-app payments or transactions
- Loyalty programs or reward points
- Chat or direct messaging with vendors

---

## **2. User Personas & Target Audience**

### **2.1 Primary User Personas**

**Persona 1: The Hungry Professional**
- **Age:** 25-40
- **Context:** Office lunch break, limited time
- **Behavior:** Uses voice search, wants quick decisions
- **Primary Query:** "Cheap lunch near me under 300 rupees"
- **Pain Point:** Too many options, needs instant filtering

**Persona 2: The Weekend Explorer**
- **Age:** 18-35
- **Context:** Leisure time, exploring new areas
- **Behavior:** Uses AR to discover interesting spots nearby
- **Primary Query:** "What's around here?"
- **Pain Point:** Doesn't know what's available in unfamiliar areas

**Persona 3: The Bargain Hunter**
- **Age:** 20-50
- **Context:** Price-conscious, seeks value
- **Behavior:** Filters by discount tags, watches promotional reels
- **Primary Query:** "Any discounts nearby?"
- **Pain Point:** Misses time-limited deals, wants real-time alerts

**Persona 4: The Late-Night Snacker**
- **Age:** 18-30
- **Context:** Late evening, limited open options
- **Behavior:** Filters by "Open Now" and "Late Night" tags
- **Primary Query:** "What's open now for food?"
- **Pain Point:** Most places closed, wants instant availability info

---

## **3. User Journey Mapping**

### **3.1 Discovery Journey (AR-First)**

**Step 1: App Launch**
- User opens AirAd app
- GPS permission requested (required for core functionality)
- Camera permission requested (required for AR)
- Location detected automatically

**Step 2: AR View Activation**
- User taps "AR Discover" (primary CTA on home screen)
- Camera activates with real-world overlay
- System loads nearby vendors within 500m radius

**Step 3: Vendor Visualization**
- AR markers appear in 3D space, oriented to real-world positions
- Distance shown dynamically (e.g., "120m", "250m")
- Active promotions displayed as badges ("20% OFF", "Happy Hour")
- Subscription badges visible (Verified, Premium, Elite)

**Step 4: Marker Interaction**
- User taps AR marker
- Quick info card expands:
  - Vendor name
  - Category (Pizza, Cafe, BBQ)
  - Distance
  - Active promotion (if any)
  - Rating/engagement indicator (aggregated taps, not user reviews)

**Step 5: Decision & Action**
- User taps "Get Directions" → Launches navigation
- User taps "View Details" → Opens vendor profile with reels, menu, hours
- User taps "Call" → Direct phone call (if vendor provided number)

**Step 6: Navigation & Arrival**
- Turn-by-turn navigation via Google Maps integration
- Optional: "Arrived?" confirmation button (for analytics)

**Success Metrics:**
- AR load time: <2 seconds
- Marker tap rate: 30% minimum
- Navigation click-through: 15% minimum

### **3.2 Discovery Journey (Voice-Driven)**

**Step 1: Voice Activation**
- User taps microphone icon (always visible)
- Voice prompt: "What are you looking for?"

**Step 2: Query Capture**
- User speaks naturally: "Cheap pizza near me"
- System captures audio, converts to text
- Displays transcription for confirmation

**Step 3: Intent Classification**
- NLP extracts entities:
  - "Cheap" → Intent: BudgetUnder300
  - "Pizza" → Category: Pizza
  - "Near me" → GPS proximity filter

**Step 4: Results Generation**
- System ranks vendors by relevance score
- Filters by GPS distance (<500m default)
- Voice bot responds:
  - "I found 3 places: Pizza Hub 120m away with 20% off, Mario's Pizza 250m, and Fast Slice 400m. Would you like directions to Pizza Hub?"

**Step 5: User Action**
- User confirms verbally ("Yes") or taps result card
- Navigation launches immediately

**Success Metrics:**
- Intent classification accuracy: 85% minimum
- Voice query completion rate: 70%
- Navigation activation from voice: 25% minimum

### **3.3 Discovery Journey (Tag-Based Browsing)**

**Step 1: Tag Navigation**
- User taps "Browse" (secondary tab)
- Sees curated tag groups:
  - **Popular:** Food, Cafe, Pizza, BBQ
  - **Deals:** Discounts Live, Happy Hour, Free Delivery
  - **Timing:** Open Now, Breakfast, Lunch, Late Night
  - **Lifestyle:** Healthy, Family-Friendly, Budget-Friendly

**Step 2: Tag Selection**
- User taps "Cheap" intent tag
- System filters vendors with BudgetUnder300 or BudgetUnder500 tags
- Results displayed as list or map view

**Step 3: Refinement**
- User can stack tags: "Cheap" + "Pizza" + "Open Now"
- System applies AND logic (all tags must match)

**Step 4: Vendor Selection**
- User taps vendor card
- Opens profile with reels, promotions, details

**Success Metrics:**
- Tag usage rate: 40% of sessions
- Multi-tag filtering: 20% of tag sessions
- Conversion from tag browsing: 10%

---

## **4. AR Interaction Design Requirements**

### **4.1 AR Marker Visual Hierarchy**

**Marker Components (Priority Order):**

1. **Distance Indicator** (Most Prominent)
   - Large, readable font (min 18pt)
   - Updates in real-time (1-second refresh)
   - Color: White text on semi-transparent dark background

2. **Vendor Name**
   - Bold, sans-serif font
   - Max 20 characters (truncate with "...")
   - Color: White

3. **Active Promotion Badge**
   - Bright accent color (red/yellow for urgency)
   - Animated pulse effect (subtle, not distracting)
   - Text: "20% OFF" or "Happy Hour"

4. **Subscription Badge** (Corner Icon)
   - Small icon:
     - Gold: Star ⭐
     - Diamond: Gem 💎
     - Platinum: Crown 👑
   - Semi-transparent, does not dominate visual

5. **Category Icon** (Small, Bottom Corner)
   - Pizza slice 🍕, Coffee ☕, etc.
   - Helps quick visual identification

**Design Rules:**
- Markers must be readable in bright sunlight (high contrast)
- Minimum touch target: 44×44 pixels (accessibility)
- Avoid visual clutter: max 5 information elements per marker
- Subscription badges should NOT overshadow content (subtle, not dominant)

### **4.2 AR Clustering Behavior**

**When to Cluster:**
- 3+ vendors within 50m radius
- Inside landmarks (malls, markets)

**Cluster Visual:**
- Single marker with count badge: "5 vendors"
- Tap to expand → Shows list of vendors inside cluster
- User selects specific vendor → Individual marker highlights

**Multi-Floor Landmarks:**
- Floor-based sub-clustering
- Visual indicator: "3 vendors on Floor 2"

### **4.3 AR Performance Requirements**

| **Metric**                  | **Target**          |
|-----------------------------|---------------------|
| Initial AR load time        | <2 seconds          |
| Marker render time          | <500ms              |
| Real-time distance refresh  | 1-second intervals  |
| Frame rate (AR smoothness)  | 30 FPS minimum      |
| Battery drain per 10 min    | <5%                 |

### **4.4 Fallback for Non-AR Devices**

**Map View Fallback:**
- Detects AR capability on app launch
- If unavailable (old device, missing sensors), defaults to map view
- Same data, different visualization:
  - Google Maps-style pins replace AR markers
  - List view option available
  - All filtering and promotions remain functional

---

## **5. Voice Search Functionality**

### **5.1 Supported Query Types**

**Query Category 1: Food Discovery**
- Examples:
  - "Cheap pizza near me"
  - "Best burgers under 500 rupees"
  - "Healthy lunch options"
- System Action: Filter by category + intent + GPS

**Query Category 2: Availability**
- Examples:
  - "What's open now?"
  - "Late night food near me"
  - "Breakfast places open early"
- System Action: Filter by time tags + business hours

**Query Category 3: Promotions**
- Examples:
  - "Any discounts nearby?"
  - "Happy hour deals"
  - "Free delivery options"
- System Action: Filter by promotion tags

**Query Category 4: Navigation**
- Examples:
  - "Take me to Pizza Hub"
  - "Show directions to the nearest cafe"
- System Action: Launch navigation immediately

**Query Category 5: Vendor Details**
- Examples:
  - "Does Pizza Hub deliver?"
  - "What are the prices at Mario's Pizza?"
- System Action: Query vendor voice bot (Diamond/Platinum vendors)

### **5.2 Voice Response Templates**

**Template 1: Multiple Results**
- "I found [count] places: [Vendor 1] [distance]m away with [promotion], [Vendor 2] [distance]m, and [Vendor 3] [distance]m. Would you like directions to [top result]?"

**Template 2: Single Result**
- "[Vendor name] is [distance]m away and currently offering [promotion]. Shall I navigate you there?"

**Template 3: No Results**
- "I didn't find any [category] places nearby right now. Try widening your search or exploring a different area."

**Template 4: Clarification Needed**
- "Did you mean [option 1] or [option 2]?" (e.g., "pizza delivery" vs "pizza restaurant")

### **5.3 Voice Interaction Flow**

1. **User Activates Voice**
   - Taps mic icon or says wake word (future feature)
   - Visual feedback: pulsing microphone animation

2. **User Speaks Query**
   - Audio captured, sent to NLP service
   - Transcription displayed in real-time

3. **System Processes**
   - Intent classification (food discovery, availability, etc.)
   - Entity extraction (category, price range, location)
   - Query executed against database

4. **Voice Response Delivered**
   - Text-to-speech (TTS) reads results
   - Simultaneously displays result cards visually

5. **User Confirmation**
   - User can confirm verbally ("Yes") or tap result
   - Navigation launches or vendor profile opens

**Error Handling:**
- If voice unclear: "I didn't catch that. Could you repeat?"
- If no GPS: "I need your location to find nearby places. Please enable GPS."

---

## **6. Reel Viewing Experience**

### **6.1 Reel Discovery Modes**

**Mode 1: Nearby Reels Feed**
- User swipes to "Reels" tab
- System shows reels from vendors within 1km
- Ranked by:
  - Distance (closer = higher priority)
  - Recency (newer reels prioritized)
  - Engagement (views, completion rate)
  - Promotions (active discounts boost ranking)

**Mode 2: Vendor Profile Reels**
- User taps vendor in AR or search results
- Views all active reels from that vendor
- Max 6 reels per vendor (Diamond tier limit)

**Mode 3: Promotion-Triggered Reels**
- User searches for discounts
- System surfaces reels tagged with active promotions
- Sorted by discount value (highest first)

### **6.2 Reel Player Specifications**

| **Feature**              | **Specification**                     |
|--------------------------|---------------------------------------|
| Reel duration            | 9 or 11 seconds (fixed lengths)       |
| Autoplay                 | Yes (muted by default)                |
| Sound activation         | Tap to unmute                         |
| Vertical scroll          | Swipe up for next reel                |
| Pause/resume             | Tap screen                            |
| Vendor CTA               | "Get Directions" button overlaid      |
| Skip                     | Swipe right                           |

### **6.3 Reel Engagement Metrics**

**Tracked Events:**
- Reel Impression (appeared in feed)
- Reel View (played for >2 seconds)
- Completion Rate (watched to end)
- CTA Tap (clicked "Get Directions" or "View Offer")
- Share (future feature, excluded Phase-1)

**Vendor Analytics:**
- Gold+: Can see total views and completion rate
- Diamond+: Can see hourly breakdown and traffic sources

---

## **7. Personalization & Recommendations**

### **7.1 Personalization Strategy**

**Approach: Implicit Behavioral Learning (No Explicit Profiles)**
- AirAd does NOT ask users to fill out preference forms
- Learns from behavior:
  - Categories frequently searched
  - Price ranges selected
  - Time-of-day patterns
  - Geographic areas visited

**Privacy-First:**
- Personalization data stored locally on device
- Aggregated anonymously for vendor analytics
- User can reset preferences anytime

### **7.2 Recommendation Logic**

**Scenario 1: User Opens App at 12:30 PM**
- System detects "lunch time"
- Prioritizes vendors with "Lunch" time tag
- Suggests: "Looking for lunch? Here are nearby options."

**Scenario 2: User Frequently Searches "Cheap"**
- System learns budget preference
- Automatically filters results to BudgetUnder300 by default
- User can override with voice or tags

**Scenario 3: User Visits Same Area Weekly**
- System detects pattern
- Suggests new vendors in that area: "New pizza place opened in F-10."

**Scenario 4: User Engages with Discount Reels**
- System prioritizes promotional content in feed
- Increases frequency of "Deals" tab suggestions

### **7.3 Notification Strategy**

**Push Notification Types:**

**Type 1: Proximity-Based Promotions**
- Trigger: User GPS enters area with active happy hour
- Message: "Pizza Hub is 200m away with 20% off right now!"
- Frequency: Max 2/day to avoid spam

**Type 2: Time-Sensitive Deals**
- Trigger: Vendor launches flash deal
- Message: "Flash Deal: 30% off at Mario's Pizza for the next hour!"
- Condition: User must have visited area in past 7 days

**Type 3: New Vendor Alert**
- Trigger: New vendor claims business in user's frequent areas
- Message: "New cafe opened near you: Brew Masters in F-10"
- Frequency: Max 1/week

**Type 4: Re-Engagement**
- Trigger: User inactive for 7 days
- Message: "5 new deals available near you. Check them out!"
- Frequency: Once per inactivity period

**Opt-Out:** Users can disable notifications by type (promotions, new vendors, etc.)

---

## **8. User Preferences & Settings**

### **8.1 Preference Categories**

**Discovery Preferences:**
- Default search radius (500m, 1km, 2km)
- Preferred categories (auto-suggest in voice search)
- Price range preference (budget, mid-range, premium)

**Notification Preferences:**
- Enable/disable proximity alerts
- Enable/disable flash deal notifications
- Enable/disable new vendor alerts

**Privacy Preferences:**
- Share location data (required for core functionality, but can limit background tracking)
- Behavioral analytics opt-out
- Data deletion request

**Accessibility:**
- Text size (small, medium, large)
- High contrast mode (for AR readability in sunlight)
- Voice-only mode (minimal visual UI)

### **8.2 Account Management**

**Phase-1 Account Model: Minimal (No Mandatory Signup)**
- Users can browse anonymously
- Optional account creation for:
  - Saving favorite vendors (future feature)
  - Personalization sync across devices

**Account Data:**
- Phone number (optional, for account recovery)
- Email (optional)
- GPS history (stored locally, anonymized for analytics)

---

## **9. User Analytics & Behavioral Tracking**

### **9.1 Event Tracking Taxonomy**

**Session Events:**
- App Open (timestamp, GPS)
- AR View Activated
- Voice Search Activated
- Tag Browse Initiated

**Discovery Events:**
- Vendor Marker Viewed (AR or map)
- Vendor Marker Tapped
- Reel Viewed
- Promotion Badge Clicked

**Conversion Events:**
- Navigation Clicked
- Phone Call Initiated
- Vendor Profile Viewed

**Engagement Events:**
- Reel Completion
- Voice Query Made
- Tag Filter Applied

### **9.2 User Segmentation**

**Segment 1: Frequent Users**
- Definition: 4+ sessions/week
- Behavior: High AR usage, voice search power users
- Value: Core audience, high engagement

**Segment 2: Deal Seekers**
- Definition: 70%+ interactions with promotion tags
- Behavior: Price-sensitive, time-limited deal hunters
- Value: Drives vendor promotion adoption

**Segment 3: Explorers**
- Definition: High geographic variance, new area discovery
- Behavior: AR-heavy, low repeat vendor visits
- Value: Discovery advocates, word-of-mouth potential

**Segment 4: Ghost Users**
- Definition: Installed but <1 session/month
- Behavior: Low engagement, possibly churned
- Value: Re-engagement targets

### **9.3 Success Metrics & KPIs**

| **Metric**                     | **Phase-1 Target**  |
|--------------------------------|---------------------|
| Daily Active Users (DAU)       | 10,000 (Month 3)    |
| AR Session Rate                | 60% of opens        |
| Voice Query Rate               | 25% of sessions     |
| Navigation Click-Through       | 15% of discoveries  |
| Average Session Duration       | 3-5 minutes         |
| Retention (Day 7)              | 40%                 |
| Retention (Day 30)             | 25%                 |

---

## **10. User Safety & Privacy**

### **10.1 Data Collection Transparency**

**What We Collect:**
- GPS location (real-time, for discovery)
- Voice query transcriptions (for NLP improvement)
- Behavioral events (AR taps, reel views, navigation clicks)

**What We DON'T Collect:**
- Camera feed or photos (AR processed locally)
- Personal identifiable information (unless user creates account)
- Financial data (no payments in Phase-1)

**User Control:**
- Transparent privacy policy (plain language, no legalese)
- One-tap data deletion
- Export personal data as JSON

### **10.2 AR Safety Features**

**Walking Mode Warning:**
- Detects when user is moving while AR is active
- Displays overlay: "Pay attention to your surroundings while walking."
- Auto-dimming of AR markers to reduce distraction

**GPS Accuracy Alerts:**
- If GPS signal weak: "Location accuracy low. Results may be inaccurate."
- Prevents navigation launch if GPS error >50m

---

## **11. Usability & Accessibility**

### **11.1 Accessibility Compliance**

**Visual Accessibility:**
- Minimum text size: 14pt (adjustable in settings)
- Color contrast ratio: 4.5:1 (WCAG AA standard)
- AR markers readable in bright sunlight (high contrast backgrounds)

**Motor Accessibility:**
- Minimum touch target: 44×44 pixels
- Voice-only mode for users with limited mobility

**Cognitive Accessibility:**
- Simple, jargon-free language
- Clear visual hierarchy (primary actions prominent)
- Minimal cognitive load (one primary action per screen)

### **11.2 Onboarding Flow**

**Step 1: Welcome Screen**
- Value proposition: "Discover what's nearby, right now."
- Skip button (no forced tutorial)

**Step 2: Permission Requests**
- GPS: "We need your location to show nearby places."
- Camera: "We use your camera for AR discovery."
- Notifications: "Get alerts about nearby deals." (optional)

**Step 3: Feature Tour (Optional)**
- 3-screen carousel:
  - Screen 1: AR Discovery
  - Screen 2: Voice Search
  - Screen 3: Deals & Promotions
- "Skip" button on every screen

**Step 4: Discovery Launch**
- Immediate AR activation after permissions granted
- No signup required

**Onboarding Success Metrics:**
- Permission grant rate (GPS): 90% minimum
- Permission grant rate (Camera): 80% minimum
- Tutorial skip rate: <30% (indicates clear value prop)

---

## **12. Conclusion & Next Steps**

This document establishes the complete end-user functional architecture for AirAd Phase-1. Successful user adoption depends on:

1. **Instant Value Delivery:** Users must find relevant vendors within 10 seconds of app open.
2. **Minimal Friction:** No signups, no profiles, no unnecessary steps.
3. **Clarity Over Complexity:** AR, voice, and tags should feel intuitive, not overwhelming.
4. **Privacy Respect:** Users must trust that their data is protected and controlled.

The user experience is the platform's face. Without satisfied, engaged users, vendors have no audience.

**— End of Document —**
