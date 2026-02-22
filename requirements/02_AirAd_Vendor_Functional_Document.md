# **AirAd Phase-1**
# **Vendor Functional Document**

**Version: 1.0**  
**Date: February 2026**  
**Status: Approved for Phase-1 Execution**

---

## **Executive Summary**

This document defines the complete vendor-side functionality, workflows, and requirements for AirAd Phase-1. It serves as the authoritative reference for understanding vendor roles, subscription packages, feature access, campaign management, and lifecycle workflows.

AirAd's vendor platform operates on a **claim-to-own model** with progressive activation, enabling micro-vendors to start with zero friction and gradually unlock advanced capabilities through tiered subscriptions.

**Core Principles:**
- Claim-based vendor acquisition (pre-seeded listings)
- Progressive feature activation (Silver → Gold → Diamond → Platinum)
- Subscription-based AR visibility enhancement
- Real-time promotion and discount control
- Voice bot configuration for automated customer queries

---

## **1. Purpose & Scope**

### **1.1 Document Purpose**

This document establishes:
- Complete vendor account lifecycle workflows
- Subscription tier feature matrices and limits
- Campaign creation and management processes
- Analytics access levels and KPI tracking
- Vendor onboarding and activation strategies

### **1.2 Scope Boundaries**

**Included in Phase-1:**
- Business profile claiming and verification
- Subscription packages (Silver, Gold, Diamond, Platinum)
- Promotion and discount management
- Voice bot configuration
- AR visibility ranking
- Basic analytics dashboards

**Explicitly Excluded:**
- Payment processing / point-of-sale integration
- Inventory management systems
- Customer relationship management (CRM)
- Multi-location franchisee dashboards
- Third-party integrations (beyond Google Maps)

---

## **2. Vendor Roles & Definitions**

### **2.1 Vendor Types**

AirAd supports four primary vendor types without functional limitations:

| **Vendor Type**         | **Characteristics**                                          | **Primary Use Cases**                       |
|-------------------------|--------------------------------------------------------------|---------------------------------------------|
| **Food Vendors**        | Restaurants, cafes, street food, kiosks                      | Promotions, happy hours, meal deals         |
| **Retail Shops**        | Clothing, electronics, groceries, pharmacies                 | Product discounts, flash sales              |
| **Service Providers**   | Salons, gyms, clinics, repair services                       | Time-slot promotions, service discounts     |
| **Micro-Vendors**       | Street carts, breakfast points, small kiosks                 | Daily offers, location-based discovery      |

All Phase-1 features remain usable, performant, and valuable across vendor sizes.

### **2.2 Vendor Account States**

| **State**           | **Definition**                                                   | **User Visibility**         |
|---------------------|------------------------------------------------------------------|-----------------------------|
| **Unclaimed**       | System-seeded listing, no vendor control                         | Visible in AR & search      |
| **Claimed**         | Vendor has verified ownership                                    | Enhanced profile control    |
| **Suspended**       | Admin action due to policy violation                             | Hidden from discovery       |
| **Closed**          | Business permanently shut down                                   | Archived, not visible       |

---

## **3. Vendor Onboarding & Claiming Process**

### **3.1 Claim-Based Onboarding Flow**

**Step 1: Business Discovery**
- Vendor opens AirAd Creator app
- Searches for business name or uses GPS to find nearby listings
- Sees pre-seeded business profile

**Step 2: Claim Initiation**
- Taps "Claim This Business"
- System sends OTP to phone number on file (if available)
- If phone not available, manual verification via photo evidence

**Step 3: Verification**
- **Automated Verification:** OTP match + GPS proximity (within 100m of business location)
- **Manual Verification:** Upload storefront photo + business license (reviewed within 24 hours)

**Step 4: Profile Completion**
- Add business hours
- Upload logo/storefront photo (optional in claim flow)
- Select primary category tags (system pre-assigns, vendor confirms)

**Step 5: Activation**
- Vendor is automatically assigned **Silver (Free)** tier
- Profile goes live immediately after verification
- Receives onboarding tutorial (optional)

**Success Metrics:**
- Claim completion rate: 80% minimum
- Time to verification: <1 hour for automated, <24 hours for manual
- Profile activation within 2 minutes of claim completion

### **3.2 Progressive Activation Strategy**

Vendors unlock features gradually to prevent overwhelming UI and ensure value realization:

**Phase 1: Claim (Day 1)**
- Basic profile control
- Business hours editing
- Single reel upload

**Phase 2: Engagement (Week 1)**
- View basic analytics (views, taps)
- Unlock discount creation
- Add voice intro (static)

**Phase 3: Monetization (Week 2+)**
- Subscription upgrade prompts based on usage
- Access to advanced analytics
- Campaign scheduling unlocked

---

## **4. Subscription Tier Architecture**

### **4.1 Tier Overview**

| **Tier**     | **Monthly Price** | **Strategic Position**           | **Primary Value**                    |
|--------------|-------------------|----------------------------------|--------------------------------------|
| **Silver**   | Free              | Entry Presence                   | Be visible                           |
| **Gold**     | PKR 3,000         | Competitive Edge                 | Be preferred                         |
| **Diamond**  | PKR 7,000         | Growth Engine                    | Convert efficiently                  |
| **Platinum** | PKR 15,000        | Area Dominance                   | Own visibility                       |

### **4.2 Feature Matrix (Comprehensive)**

| **Feature**                      | **Silver** | **Gold**   | **Diamond** | **Platinum** |
|----------------------------------|------------|------------|-------------|--------------|
| **Basic Profile**                | ✅         | ✅         | ✅          | ✅           |
| **AR Visibility**                | Standard   | Boosted    | High Priority | Dominant Zone |
| **Active AR Reels**              | 1          | 3          | 6           | Unlimited    |
| **Business Voice Intro**         | ❌         | Basic (static) | Dynamic | Advanced + Priority |
| **Happy Hour Slots**             | ❌         | 1/day      | 3/day       | Unlimited    |
| **Free Delivery Configs**        | ❌         | 1 Config   | 3 Configs   | Unlimited    |
| **Discount Campaigns**           | Basic      | Scheduled  | Advanced    | Smart Automation |
| **Sponsored Placement**          | ❌         | Limited Time | Area Boost | Area Exclusive |
| **Analytics Dashboard**          | Basic Metrics | Standard Insights | Advanced Insights | Predictive Insights |
| **Campaign Scheduling**          | ❌         | Basic      | Advanced Controls | Smart Automation |
| **Badge & Trust Mark**           | Claimed    | Verified   | Premium     | Elite + AR Crown |
| **Voice Search Priority**        | None       | Low        | Medium      | Highest      |
| **Support Level**                | Community  | Email (48h) | Priority Email (24h) | Dedicated Account Manager |

### **4.3 AR Visibility Ranking Formula**

**Final AR Score** =  
(Intent Match × 0.30) +  
(Distance Weight × 0.25) +  
(Active Promotion × 0.15) +  
(Engagement Score × 0.15) +  
(Subscription Multiplier × 0.15)

**Subscription Multipliers:**
- Silver: 1.0x
- Gold: 1.2x
- Diamond: 1.5x
- Platinum: 2.0x

**Critical Rules:**
- Paid tier cannot override distance relevance by more than 30%
- Promotion tags (Layer 3) apply additional +0.1 boost
- ARPriority tag (Layer 5) activates for Diamond+

### **4.4 Upgrade Triggers & Psychology**

**Trigger #1: Fear of Invisibility**
- When vendors see competitors with:
  - "Verified" badge (Gold)
  - "Premium" badge (Diamond)
  - "Elite" crown in AR (Platinum)
- Result: Natural competitive pressure to upgrade

**Trigger #2: Time-Slot Monetization**
- Micro-vendors think in daily cycles:
  - "Slow hours" (3-5 PM)
  - "Evening rush" (7-9 PM)
  - "Office lunch" (12-2 PM)
- When they see Gold vendors filling slow hours via Happy Hour slots, they upgrade

**Trigger #3: Voice Automation ROI**
- Voice bot reduces manual query handling
- Diamond vendors appear in more voice search results
- Higher conversion rates justify subscription cost

**Trigger #4: Data Visibility**
- Silver sees: "Your listing had 240 views. Upgrade to see time breakdown."
- Curiosity drives upgrade to access hourly analytics

---

## **5. Campaign & Promotion Management**

### **5.1 Discount Configuration System**

**Discount Types:**

| **Type**             | **Configuration**                           | **Tier Access**  |
|----------------------|---------------------------------------------|------------------|
| **Flat Discount**    | Fixed amount off (e.g., PKR 50 off)         | All tiers        |
| **Percentage**       | % off total (e.g., 20% off)                 | All tiers        |
| **Buy 1 Get 1**      | BOGO deals                                  | Gold+            |
| **Happy Hour**       | Time-limited discount window                | Gold+            |
| **Item-Specific**    | Discount on selected products               | Diamond+         |
| **Random Flash**     | System-triggered surprise discount          | Platinum         |

**Discount Workflow:**

1. **Vendor Creates Campaign**
   - Selects discount type
   - Sets value (flat amount or percentage)
   - Defines time window (start/end time)
   - Chooses days of week
   - Sets visibility (AR badge, reel mention)

2. **System Activates**
   - Promotion tag (Layer 3) auto-applied
   - AR badge displays "20% OFF" or "Happy Hour"
   - Voice bot responses updated in real-time

3. **User Discovery**
   - AR view shows discount badge
   - Voice query: "Any discounts near me?" returns this vendor
   - Reel content surfaces in feed

4. **Campaign End**
   - Promotion tag auto-expires
   - Analytics dashboard shows:
     - Total views during campaign
     - AR marker taps
     - Navigation clicks
     - Estimated ROI

### **5.2 Happy Hour Slot Management**

**Happy Hour Definition:**  
Time-limited promotional window designed to drive foot traffic during low-demand periods.

**Tier Limits:**
- Gold: 1 Happy Hour/day
- Diamond: 3 Happy Hours/day
- Platinum: Unlimited

**Configuration Options:**
- Start time & end time (minimum 1 hour)
- Discount value (flat or percentage)
- Recurring schedule (daily, weekdays, weekends)
- Auto-activate on slow days (Platinum feature)

**Example Use Case:**
- Restaurant notices 3-5 PM is consistently slow
- Creates Happy Hour: "20% off all items, 3-5 PM, Mon-Fri"
- System activates promotion tag automatically during window
- AR users within 500m see "Happy Hour Active" badge

### **5.3 Free Delivery Campaigns**

**Configuration:**
- Delivery radius (max 5km)
- Free delivery distance (e.g., free within 2km)
- Time slots (e.g., "Free delivery 12-2 PM")
- Minimum order value (optional)

**Tier Limits:**
- Silver: Cannot configure
- Gold: 1 free delivery config
- Diamond: 3 configs (different time windows)
- Platinum: Unlimited

**Voice Bot Integration:**  
User asks: "Who delivers free near me?"  
Voice bot filters vendors with active "FreeDelivery" tag.

---

## **6. Voice Bot Configuration**

### **6.1 Voice Bot Tiers**

| **Tier**     | **Voice Bot Type**            | **Capabilities**                                    |
|--------------|-------------------------------|-----------------------------------------------------|
| **Silver**   | None                          | No voice automation                                 |
| **Gold**     | Basic (static)                | Pre-recorded intro message                          |
| **Diamond**  | Dynamic                       | Real-time query responses based on menu/pricing     |
| **Platinum** | Advanced + Priority Routing   | Personalized responses, priority in voice results   |

### **6.2 Voice Bot Configuration Workflow**

**Step 1: Vendor Access (Diamond/Platinum)**
- Opens "Voice Bot Settings" in dashboard
- Reviews current business information (auto-populated)

**Step 2: Data Verification**
- Confirms pricing accuracy
- Updates availability (in stock / out of stock items)
- Sets delivery/pickup options

**Step 3: Response Customization (Optional)**
- Adds custom intro message (e.g., "Welcome to Pizza Hub, we specialize in authentic Italian pizza")
- Configures FAQs (e.g., "Do you have vegetarian options?" → "Yes, we offer 5 vegetarian pizzas")

**Step 4: Testing**
- Vendor can test voice bot via in-app simulator
- Simulates user queries:
  - "What are your prices?"
  - "Do you deliver?"
  - "What's on sale today?"

**Step 5: Activation**
- Voice bot goes live immediately
- Reflects in user-facing voice search
- Updates in real-time when vendor changes promotions

### **6.3 Voice Bot Data Requirements**

For voice bot to function, vendor must maintain:
- **Menu/Product List:** Names, prices, availability
- **Promotions:** Active discounts, happy hours
- **Business Hours:** Current open/closed status
- **Delivery Info:** Radius, charges, free delivery zones
- **Pickup Availability:** Takeout or dine-in only

System validates data freshness:
- Menu not updated in 30 days → warning notification
- Out-of-stock items persisting >7 days → prompt to update

---

## **7. Analytics & Performance Tracking**

### **7.1 Analytics Dashboard Access Levels**

| **Metric Category**         | **Silver** | **Gold**  | **Diamond** | **Platinum** |
|-----------------------------|------------|-----------|-------------|--------------|
| **Total Views**             | ✅         | ✅        | ✅          | ✅           |
| **AR Marker Taps**          | ✅         | ✅        | ✅          | ✅           |
| **Hourly Breakdown**        | ❌         | ✅        | ✅          | ✅           |
| **Day-of-Week Analysis**    | ❌         | ✅        | ✅          | ✅           |
| **Promotion ROI**           | ❌         | Basic     | Advanced    | Advanced     |
| **Voice Query Stats**       | ❌         | ❌        | ✅          | ✅           |
| **Navigation Clicks**       | ❌         | ✅        | ✅          | ✅           |
| **Conversion Estimates**    | ❌         | ❌        | ✅          | ✅           |
| **Predictive Insights**     | ❌         | ❌        | ❌          | ✅           |
| **Competitor Benchmarking** | ❌         | ❌        | ❌          | ✅           |

### **7.2 Key Performance Indicators (KPIs)**

**Discovery Metrics:**
- **Impressions:** Number of times vendor appeared in AR view
- **View Rate:** (AR taps ÷ Impressions) × 100
- **Distance Distribution:** How far users were when they discovered vendor

**Engagement Metrics:**
- **Reel Views:** Total reel plays
- **Reel Completion Rate:** % of users who watched full reel
- **Voice Queries:** Number of voice bot interactions

**Conversion Metrics:**
- **Navigation Clicks:** Users who tapped "Get Directions"
- **Promotion Clicks:** Users who tapped active discount badge
- **Estimated Visits:** Based on navigation completion (GPS tracking to vendor location)

**Time-Based Metrics (Gold+):**
- **Peak Discovery Hours:** When most users found vendor
- **Low-Traffic Windows:** Time slots with minimal engagement
- **Happy Hour Performance:** Views/taps during promotional windows

### **7.3 Predictive Insights (Platinum Only)**

**Smart Recommendations:**
- "Your busiest hour is 7-8 PM. Consider running a Happy Hour at 5-6 PM to shift demand."
- "Users search for 'cheap lunch' most at 12:30 PM. Schedule a discount for max impact."
- "Your competitor (Pizza Corner) runs discounts every Friday. Consider matching or differentiating."

**Demand Forecasting:**
- Predict slow days based on historical patterns
- Suggest optimal discount timing
- Recommend reel posting times for maximum visibility

---

## **8. Vendor Lifecycle Management**

### **8.1 Activation Stages**

**Stage 1: Discovery (Day 0)**
- Vendor becomes aware of AirAd (marketing, word-of-mouth, competitor pressure)
- Searches for business, finds pre-seeded listing

**Stage 2: Claiming (Day 1)**
- Claims business via OTP or manual verification
- Completes basic profile setup
- Enters Silver tier (free)

**Stage 3: Engagement (Week 1)**
- Uploads first reel
- Views basic analytics
- Creates first discount campaign
- Realizes value from free tier

**Stage 4: Monetization Decision (Week 2-4)**
- Sees competitors with higher visibility
- Analytics show lost opportunities during slow hours
- Upgrade prompt appears based on usage patterns

**Stage 5: Growth (Month 2+)**
- Gold/Diamond vendors optimize campaigns
- Regular discount scheduling
- Voice bot handling customer queries
- Continuous analytics review

**Stage 6: Retention (Ongoing)**
- Platinum vendors dominate local area
- Competitors forced to upgrade to compete
- Network effects lock in high-value vendors

### **8.2 Churn Prevention Strategies**

**Trigger-Based Re-Engagement:**
- Vendor stops logging in for 7 days → Email: "Your listing had 150 views this week. See who's finding you."
- Reel not uploaded in 14 days → Push notification: "Upload a reel to stay top-of-mind."
- Subscription downgrade → Survey: "Tell us why you downgraded. Here's 20% off to re-upgrade."

**Value Demonstration:**
- Monthly email report: "Your AirAd presence drove 450 AR views and 120 navigation clicks this month."
- Competitor comparison (Platinum): "You're 30% more visible than Pizza Corner. Keep it up."

---

## **9. Compliance & Vendor Policies**

### **9.1 Content Moderation**

**Prohibited Content:**
- Misleading pricing or false discounts
- Copyrighted music/images in reels without license
- Offensive or inappropriate content
- Competitor defamation

**Violation Handling:**
- **First Offense:** Warning + content removal
- **Second Offense:** 7-day suspension
- **Third Offense:** Permanent account ban

### **9.2 Discount Authenticity**

**System Validation:**
- Discounts must be realistic (no "99% off" spam)
- Time windows must be honored (system enforces auto-expiry)
- Vendor cannot claim "limited stock" without inventory proof (future Phase-2 feature)

**User Reporting:**
- Users can report "discount not honored" → Admin review within 24 hours

---

## **10. Success Metrics & KPIs**

### **10.1 Vendor Acquisition Metrics**

| **Metric**                     | **Phase-1 Target**  |
|--------------------------------|---------------------|
| Claim rate (first month)       | 15% of listings     |
| Verification completion rate   | 80%                 |
| Time to first reel upload      | <48 hours           |

### **10.2 Engagement Metrics**

| **Metric**                     | **Phase-1 Target**  |
|--------------------------------|---------------------|
| Weekly active vendors          | 60%                 |
| Average reels per vendor/month | 4                   |
| Active discount campaigns/week | 40% of vendors      |

### **10.3 Monetization Metrics**

| **Metric**                     | **Phase-1 Target**  |
|--------------------------------|---------------------|
| Gold upgrade rate (Month 2)    | 10%                 |
| Diamond upgrade rate (Month 3) | 5%                  |
| Churn rate                     | <10%/month          |
| Average revenue per vendor     | PKR 2,500/month     |

---

## **11. Conclusion & Next Steps**

This document establishes the complete vendor-side functional architecture for AirAd Phase-1. Successful vendor enablement depends on:

1. **Frictionless Claiming:** 80% claim completion rate ensures supply-side growth.
2. **Progressive Activation:** Vendors must see value before being asked to pay.
3. **Clear Upgrade Path:** Each tier solves a specific pain point (visibility, control, automation, dominance).
4. **Data-Driven Decisions:** Analytics must demonstrate ROI, not just vanity metrics.

The vendor platform is the revenue engine. Without active, engaged vendors, discovery has no value.

**— End of Document —**
