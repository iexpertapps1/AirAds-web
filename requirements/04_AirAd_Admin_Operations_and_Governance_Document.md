# **AirAd Phase-1**
# **Admin Operations & Governance Document**

**Version: 1.0**  
**Date: February 2026**  
**Status: Approved for Phase-1 Execution**

---

## **Executive Summary**

This document defines the complete administrative operations, governance frameworks, and system control mechanisms for AirAd Phase-1. It serves as the authoritative reference for platform administrators, operations teams, and compliance officers responsible for maintaining platform integrity, vendor quality, and user safety.

AirAd's operational success depends on scalable governance that balances:
- **Automation** (to minimize manual overhead)
- **Human oversight** (for quality and safety)
- **Vendor enablement** (avoiding excessive gatekeeping)
- **User protection** (preventing fraud and spam)

**Core Administrative Responsibilities:**
1. Vendor verification and claim approval
2. Content moderation (reels, promotions, profiles)
3. Tag system management and quality control
4. Fraud detection and prevention
5. Analytics and reporting
6. Compliance and legal oversight

---

## **1. Purpose & Scope**

### **1.1 Document Purpose**

This document establishes:
- Admin role definitions and access controls
- Vendor verification and claim approval workflows
- Content moderation standards and enforcement procedures
- Tag taxonomy management and validation rules
- Fraud detection mechanisms and response protocols
- Analytics dashboard specifications for operations monitoring
- Compliance frameworks (GDPR, local regulations, platform policies)
- Escalation workflows for edge cases and disputes

### **1.2 Scope Boundaries**

**Included in Phase-1:**
- Manual vendor verification (supplementing automated OTP)
- Content moderation workflows (flagged reels, inappropriate content)
- Tag accuracy audits and corrections
- Basic fraud detection (duplicate claims, fake promotions)
- Operational analytics (platform health, vendor activity, user engagement)
- Compliance monitoring (privacy, data protection)

**Explicitly Excluded:**
- Advanced AI-based fraud detection (Phase-2)
- Automated sentiment analysis for vendor reviews (N/A, no reviews in Phase-1)
- Legal dispute resolution (handled by legal team, not operations)
- Financial transaction monitoring (no payments in Phase-1)

---

## **2. Admin Roles & Access Control**

### **2.1 Role Hierarchy**

| **Role**                  | **Responsibilities**                                           | **System Access**                        |
|---------------------------|----------------------------------------------------------------|------------------------------------------|
| **Super Admin**           | Full platform control, role management, system configuration   | All systems, all data                    |
| **Operations Manager**    | Vendor verification oversight, escalation handling             | Vendor dashboard, moderation queue       |
| **Content Moderator**     | Reel review, promotion validation, profile screening           | Moderation dashboard, vendor profiles    |
| **Data Quality Analyst**  | Tag accuracy audits, GPS validation, data cleanup              | Data management tools, tag taxonomy      |
| **Support Agent**         | Vendor onboarding assistance, user support tickets             | Read-only vendor profiles, support CRM   |
| **Analytics Observer**    | Platform health monitoring, reporting (no write access)        | Analytics dashboards (read-only)         |

### **2.2 Access Control Matrix**

| **System Component**           | **Super Admin** | **Ops Manager** | **Moderator** | **Data Analyst** | **Support** | **Analytics** |
|--------------------------------|-----------------|-----------------|---------------|------------------|-------------|---------------|
| Vendor Verification Queue      | ✅              | ✅              | ❌            | ❌               | Read-only   | ❌            |
| Content Moderation Dashboard   | ✅              | ✅              | ✅            | ❌               | ❌          | ❌            |
| Tag Taxonomy Editor            | ✅              | ❌              | ❌            | ✅               | ❌          | ❌            |
| User Data Access               | ✅              | ❌              | ❌            | ❌               | Limited     | Anonymized    |
| Vendor Suspension Actions      | ✅              | ✅              | ❌            | ❌               | ❌          | ❌            |
| Analytics Dashboards           | ✅              | ✅              | Read-only     | ✅               | Read-only   | ✅            |
| System Configuration           | ✅              | ❌              | ❌            | ❌               | ❌          | ❌            |

### **2.3 Audit Logging**

**All Admin Actions Logged:**
- Timestamp
- Admin user ID
- Action type (approve, reject, suspend, edit)
- Target entity (vendor ID, reel ID, user ID)
- IP address
- Reason/notes (required for enforcement actions)

**Log Retention:**
- Active logs: 1 year
- Archived logs: 5 years (compliance requirement)

---

## **3. Vendor Verification & Claim Approval**

### **3.1 Automated Verification (Primary Path)**

**Criteria for Auto-Approval:**
1. OTP sent to phone number on file (from Google Places or field data)
2. OTP successfully verified
3. GPS proximity check: User claiming within 100m of business location
4. No fraud flags (duplicate claims, blacklisted numbers)

**Approval Time:**
- Instant (within 2 seconds of OTP verification)

**Success Rate Target:**
- 70% of claims auto-approved

### **3.2 Manual Verification Workflow**

**Triggers for Manual Review:**
- No phone number on file (OTP not possible)
- GPS proximity check fails (user >100m from business)
- Multiple claim attempts for same business
- Business in high-fraud risk category (determined by operations team)

**Manual Verification Steps:**

**Step 1: Claim Submitted**
- Vendor uploads:
  - Storefront photo (with visible business name)
  - Business license or tax registration (optional but accelerates approval)
  - Additional contact information (email, alternate phone)

**Step 2: Admin Review Queue**
- Claim appears in Operations Manager dashboard
- Assigned to Content Moderator for review

**Step 3: Verification Checks**
- Cross-reference storefront photo with Google Street View
- Verify business name matches GPS location
- Check for duplicate claims (same name, similar GPS)
- Validate business license if provided

**Step 4: Decision**
- **Approve:** Vendor account activated, receives confirmation notification
- **Reject:** Vendor notified with reason (e.g., "Business name does not match location. Please submit correct documentation.")
- **Request More Info:** Vendor receives request for additional evidence

**Approval Time:**
- Target: <24 hours for manual reviews
- Priority: <6 hours for high-engagement vendors (flagged by system)

**Success Rate Target:**
- 85% approval rate for manual reviews (15% rejected or require re-submission)

### **3.3 Duplicate Claim Handling**

**Scenario:** Two vendors claim the same business.

**Resolution Workflow:**
1. **System Detection:** Flags duplicate based on:
   - Identical GPS coordinates (within 10m)
   - Similar business name (fuzzy matching)
2. **Admin Investigation:**
   - Review both claimants' evidence
   - Cross-check with external sources (Google, government records)
3. **Decision Criteria:**
   - **First Claimant with Valid Proof:** Approved
   - **Second Claimant Legitimate (e.g., new ownership):** First claim invalidated, second approved
   - **Both Fraudulent:** Both rejected, business remains unclaimed
4. **Communication:**
   - Approved claimant: "Congratulations, your claim was verified."
   - Rejected claimant: "Another verified owner claimed this business. If you believe this is an error, contact support."

---

## **4. Content Moderation**

### **4.1 Moderation Principles**

**Balance:**
- **Permissive:** Allow creative freedom, avoid over-policing
- **Protective:** Prevent harmful, misleading, or illegal content

**Core Standards:**
- No false advertising (misleading pricing, fake discounts)
- No offensive content (hate speech, violence, explicit material)
- No copyright violations (unlicensed music, stolen visuals)
- No competitor defamation (negative attacks on other vendors)

### **4.2 Reel Moderation Workflow**

**Automated Pre-Screening (Phase-1 Basic):**
- Duplicate reel detection (same vendor uploads identical reel twice)
- Explicit content detection (basic image analysis for nudity, violence)
- Audio analysis for copyrighted music (limited Phase-1, expanded Phase-2)

**Flagged Reels Queue:**
- Reels flagged by automated system appear in moderation dashboard
- User reports also trigger manual review

**Manual Review Process:**

**Step 1: Moderator Views Reel**
- Watches full reel (9-11 seconds)
- Checks against violation categories

**Step 2: Decision**
- **Approve:** Reel goes live (if previously pending)
- **Reject with Warning:** Reel removed, vendor notified of violation, no penalty
- **Reject with Strike:** Reel removed, vendor receives policy strike (3 strikes = suspension)
- **Immediate Suspension:** Severe violation (illegal content, graphic violence)

**Step 3: Vendor Notification**
- Approved: No notification (reel already live)
- Rejected: "Your reel was removed for [reason]. Please review our content policy."
- Suspended: "Your account is suspended for [reason]. You may appeal within 7 days."

**Moderation SLA:**
- Flagged reels reviewed within: 6 hours
- User-reported reels reviewed within: 12 hours

**Moderator Calibration:**
- Weekly calibration sessions to ensure consistency
- Random sample audits by Operations Manager (10% of decisions)

### **4.3 Promotion & Discount Validation**

**Automated Validation:**
- Discount percentage: Maximum 90% (prevents "99% off" spam)
- Time window: Minimum 1 hour, maximum 24 hours
- Expiry enforcement: System auto-expires after end time

**Manual Review Triggers:**
- Discount >75% (potential spam)
- Vendor creates >10 promotions/day (abuse flag)
- User reports "discount not honored"

**Enforcement Actions:**
- **First Offense:** Warning, promotion removed
- **Second Offense:** 7-day promotion creation ban
- **Third Offense:** Account suspension, escalation to Ops Manager

### **4.4 User-Generated Reports**

**Report Categories:**
- Inappropriate content (reel contains offensive material)
- False advertising (discount not honored, wrong prices)
- Spam (excessive promotions, irrelevant content)
- Safety concern (vendor location unsafe, misleading directions)

**Report Handling:**
1. **User Submits Report:** Selects category, adds optional notes
2. **Report Queued:** Appears in moderation dashboard
3. **Admin Review:** Moderator investigates claim
4. **Action Taken:**
   - Valid Report: Content removed, vendor warned/suspended
   - Invalid Report: No action, reporter notified if requested
   - Abuse (user spamming reports): Reporter account flagged

**Transparency:**
- Reporter receives status update: "We reviewed your report and took appropriate action. Thank you for keeping AirAd safe."

---

## **5. Tag System Management**

### **5.1 Tag Taxonomy Governance**

**Master Tag List:**
- **Layer 1 (Category):** 50 predefined tags (Food, Pizza, Cafe, etc.)
- **Layer 2 (Intent):** 30 tags (Cheap, BudgetUnder300, Premium, etc.)
- **Layer 3 (Promotion):** 10 auto-generated tags (DiscountLive, HappyHour, etc.)
- **Layer 4 (Time):** 8 auto-generated tags (Breakfast, Lunch, OpenNow, etc.)
- **Layer 5 (System):** 6 invisible tags (ClaimedVendor, ARPriority, etc.)

**Tag Addition Process:**
- **Proposal:** Data Quality Analyst identifies need (e.g., new food trend like "Cloud Kitchen")
- **Validation:** Analyze demand (user search queries, vendor requests)
- **Approval:** Super Admin adds tag to taxonomy
- **Deployment:** Tag available immediately for vendor selection

**Tag Deprecation:**
- **Trigger:** Tag usage <1% of vendors for 3 consecutive months
- **Action:** Tag removed from vendor selection UI, existing assignments retained for historical data

### **5.2 Tag Accuracy Audits**

**Monthly Audit Process:**

**Step 1: Random Sampling**
- Select 5% of claimed vendor profiles
- Stratified by category (equal representation)

**Step 2: Manual Verification**
- Data Analyst reviews:
  - Category tags match business type
  - Intent tags align with pricing/offerings
  - No misuse (e.g., "Pizza" tag on a clothing shop)

**Step 3: Correction**
- Incorrect tags removed
- Vendor notified: "We updated your tags for accuracy. This helps users find you better."

**Step 4: Pattern Detection**
- If same vendor has repeated errors: Flag for manual onboarding assistance
- If systemic issue (e.g., 20% of "Cafe" vendors also tagged "Pharmacy"): Investigate data source quality

**Audit Targets:**
- Tag accuracy: 95% minimum
- Correction time: <48 hours after detection

### **5.3 Geo-Tag & Location Validation**

**GPS Drift Detection:**
- **Automated Check:** Weekly scan for vendors with GPS coordinates shifted >20m from original
- **Trigger Causes:**
  - Vendor edited location incorrectly
  - GPS sensor error during claim
  - Fraudulent location spoofing

**Validation Workflow:**
1. **System Flags Drift:** Vendor appears in GPS validation queue
2. **Admin Review:**
   - Cross-check with Google Maps
   - Review storefront photo
   - Contact vendor if discrepancy unclear
3. **Correction:**
   - Update GPS to accurate coordinates
   - Vendor notified: "We corrected your location for better discovery."

**Landmark Clustering Review:**
- Quarterly audit of multi-vendor landmarks (malls, markets)
- Ensure vendors correctly assigned to landmark
- Verify floor numbers for multi-level buildings

---

## **6. Fraud Detection & Prevention**

### **6.1 Fraud Categories**

**Fraud Type 1: Duplicate Vendor Claims**
- **Scenario:** User claims multiple businesses they don't own (to inflate presence)
- **Detection:** Same phone number used for >3 claims
- **Action:** Manual review, reject fraudulent claims, ban user

**Fraud Type 2: Fake Promotions**
- **Scenario:** Vendor creates fake discounts to attract users, doesn't honor them
- **Detection:** User reports "discount not honored" + pattern of similar reports
- **Action:** Remove promotions, suspend vendor, refund/apologize to users (no payments in Phase-1, but note for future)

**Fraud Type 3: Location Spoofing**
- **Scenario:** Vendor claims business in high-traffic area but actually located elsewhere
- **Detection:** GPS verification + user reports "business not here"
- **Action:** Correct location or suspend account if intentional fraud

**Fraud Type 4: Review/Rating Manipulation** (Future, not Phase-1)
- **Placeholder for Phase-2:** Fake reviews, paid rating boosts

### **6.2 Fraud Detection Mechanisms**

**Automated Signals:**
- Multiple claims from same device/IP (fraud score +1)
- Phone number blacklisted (previous fraud history) (fraud score +3)
- GPS anomalies (coordinates in water, outside city boundaries) (fraud score +2)
- Excessive promotion creation (>10/day) (fraud score +1)

**Fraud Score Thresholds:**
- **0-2:** Normal, no action
- **3-5:** Flagged for manual review
- **6+:** Auto-suspend, requires Ops Manager approval to reactivate

**Manual Investigation:**
- Ops Manager reviews flagged accounts
- Gathers evidence:
  - Claim history
  - User reports
  - GPS logs
  - External verification (Google, government records)

**Enforcement:**
- **Confirmed Fraud:** Permanent ban, all associated accounts/numbers blacklisted
- **Suspected Fraud:** Temporary suspension pending investigation
- **False Positive:** Restore account, apologize, compensate if harmed

### **6.3 Blacklist Management**

**Blacklist Types:**
- **Phone Numbers:** Fraudulent claimants
- **Device IDs:** Repeat offenders
- **GPS Coordinates:** Known fraud locations (e.g., fake businesses)

**Blacklist Addition:**
- Requires Ops Manager approval
- Documented reason (audit trail)

**Blacklist Removal:**
- **Appeal Process:** User submits appeal with evidence
- **Review:** Ops Manager evaluates
- **Outcome:** Restore or uphold ban

---

## **7. Analytics & Operational Dashboards**

### **7.1 Platform Health Dashboard**

**Key Metrics:**

| **Metric**                     | **Definition**                                  | **Target**         |
|--------------------------------|-------------------------------------------------|--------------------|
| Total Vendors (Claimed)        | Active, verified vendor accounts                | 500+ per launch area |
| Daily Active Vendors           | Vendors who logged in today                     | 60%                |
| Total Users                    | Active user accounts                            | 10,000 (Month 3)   |
| Daily Active Users (DAU)       | Users who opened app today                      | 3,000 (Month 3)    |
| AR Session Rate                | % of app opens that activated AR                | 60%                |
| Voice Query Rate               | % of sessions with voice search                 | 25%                |
| Average Session Duration       | Time spent per user session                     | 3-5 minutes        |
| Crash Rate                     | % of sessions ending in crash                   | <1%                |

**Alert Thresholds:**
- DAU drops >20% day-over-day → Operations alert
- Crash rate >2% → Engineering escalation
- AR session rate <50% → UX team investigation

### **7.2 Vendor Activity Dashboard**

**Metrics:**

| **Metric**                     | **Purpose**                                     |
|--------------------------------|-------------------------------------------------|
| New Claims (Daily/Weekly)      | Track vendor acquisition rate                   |
| Claim Approval Rate            | Monitor verification efficiency                 |
| Active Promotions              | Measure vendor engagement                       |
| Reel Upload Rate               | Track content creation                          |
| Subscription Distribution      | Silver/Gold/Diamond/Platinum breakdown          |

**Trends to Monitor:**
- Declining claim rate → Marketing/outreach needed
- Low reel upload → Onboarding tutorial improvements
- High churn (downgrades) → Product/pricing issues

### **7.3 Content Moderation Dashboard**

**Queue Metrics:**

| **Queue**                      | **Target SLA**     |
|--------------------------------|--------------------|
| Pending Vendor Verifications   | <24 hours          |
| Flagged Reels                  | <6 hours           |
| User Reports                   | <12 hours          |

**Moderator Performance:**
- Average review time per item
- Decision accuracy (random audits by Ops Manager)
- Queue backlog (should never exceed 100 items)

### **7.4 User Behavior Dashboard**

**Engagement Metrics:**

| **Metric**                     | **Insight**                                     |
|--------------------------------|-------------------------------------------------|
| Top Search Queries (Voice)     | Identify popular demand (e.g., "cheap pizza")   |
| Most-Used Tags                 | Validate tag taxonomy relevance                 |
| Geographic Hotspots            | Identify high-traffic areas for expansion       |
| Reel Completion Rate           | Measure content quality                         |

**Churn Analysis:**
- Day 1 retention: % of users who return next day
- Day 7 retention: % of users active after 1 week
- Churn reasons (exit surveys, optional)

---

## **8. Compliance & Legal Governance**

### **8.1 GDPR Compliance Framework**

**Data Subject Rights:**

| **Right**                      | **Implementation**                              | **SLA**            |
|--------------------------------|-------------------------------------------------|--------------------|
| Right to Access                | User requests data export → JSON file provided  | 7 days             |
| Right to Deletion              | User requests account deletion → all data purged | 30 days            |
| Right to Rectification         | User corrects profile data via app settings     | Immediate          |
| Right to Data Portability      | Export in machine-readable format (JSON)        | 7 days             |
| Right to Object                | Opt-out of behavioral analytics                 | Immediate          |

**Data Minimization:**
- Only collect data necessary for core functionality
- No speculative data collection (e.g., future features)

**Consent Management:**
- Explicit opt-in for:
  - GPS tracking (required for AR)
  - Behavioral analytics (optional)
  - Marketing notifications (optional)
- Granular controls (e.g., disable only marketing, keep analytics)

**Data Retention:**
- Active user data: Retained while account active
- Deleted user data: Purged after 30 days (anonymized aggregates retained)
- Vendor data: Retained while business claimed (anonymized after account closure)

### **8.2 Platform Policies & Enforcement**

**Prohibited Activities:**
- Fraudulent claims or impersonation
- Misleading or false advertising
- Offensive or illegal content
- Harassment of users or vendors
- Spam or excessive promotions

**Enforcement Ladder:**
1. **Warning:** First offense, minor violation
2. **Content Removal:** Reel/promotion deleted
3. **Temporary Suspension:** 7 days, repeat offenses
4. **Permanent Ban:** Severe violations, fraud

**Appeal Process:**
- Suspended/banned users can appeal within 7 days
- Ops Manager reviews evidence
- Decision final (no further appeals)

### **8.3 Vendor Agreement & Terms of Service**

**Key Clauses:**
- Vendor affirms ownership or authorization to represent business
- Vendor agrees to honor promotions advertised on platform
- Platform reserves right to suspend/terminate for policy violations
- Vendor grants platform license to display content (reels, photos)

**Acceptance:**
- Required before claim approval
- Digital signature (tap "I Agree")
- Stored audit trail

---

## **9. Escalation & Dispute Resolution**

### **9.1 Escalation Matrix**

| **Issue Type**                 | **First Line**        | **Escalation Level 1** | **Escalation Level 2** |
|--------------------------------|-----------------------|------------------------|------------------------|
| Vendor Claim Dispute           | Support Agent         | Operations Manager     | Super Admin            |
| Content Moderation Appeal      | Content Moderator     | Operations Manager     | Legal Team             |
| Fraud Investigation            | Data Analyst          | Operations Manager     | Super Admin + Legal    |
| User Privacy Complaint         | Support Agent         | Compliance Officer     | Legal Team             |
| Technical Platform Issue       | Support Agent         | Engineering Team       | CTO                    |

### **9.2 Response Time SLAs**

| **Priority**                   | **Definition**                              | **Response Time**  |
|--------------------------------|---------------------------------------------|--------------------|
| **Critical**                   | Platform outage, data breach                | 1 hour             |
| **High**                       | Fraud, severe policy violation              | 4 hours            |
| **Medium**                     | Vendor dispute, content appeal              | 24 hours           |
| **Low**                        | General inquiry, feature request            | 48 hours           |

### **9.3 Dispute Resolution Workflow**

**Step 1: Ticket Creation**
- User/vendor submits dispute via support form
- Categorized by issue type
- Assigned to appropriate team

**Step 2: Initial Investigation**
- Support Agent or Moderator reviews evidence
- Gathers context (logs, screenshots, user reports)

**Step 3: Resolution Attempt**
- Mediates between parties (if vendor vs. user dispute)
- Proposes solution based on policy

**Step 4: Escalation (if unresolved)**
- Escalated to Ops Manager
- Additional evidence gathered
- Final decision documented

**Step 5: Communication**
- All parties notified of outcome
- Explanation provided (policy reference)

---

## **10. Operational Workflows & Runbooks**

### **10.1 Daily Operations Checklist**

**Morning (9:00 AM):**
- Review platform health dashboard (check for anomalies)
- Check moderation queue backlog (<100 items)
- Scan fraud alerts (any high-priority flags overnight)

**Midday (1:00 PM):**
- Process pending vendor verifications (target <50 in queue)
- Review user reports (prioritize "safety concern" reports)
- Monitor crash rate (escalate if >2%)

**Evening (6:00 PM):**
- Generate daily activity report (DAU, new vendors, active promotions)
- Flag any trends (declining engagement, spike in reports)
- Prepare summary for Ops Manager

### **10.2 Incident Response Runbook**

**Incident Type: Platform Outage**
1. Identify scope (full outage vs. feature-specific)
2. Notify engineering team immediately
3. Post status update on vendor dashboard: "We're aware of an issue and working to resolve it."
4. Escalate to CTO if >1 hour downtime
5. Post-mortem: Root cause analysis, prevention plan

**Incident Type: Data Breach**
1. Isolate affected systems immediately
2. Notify Super Admin + Legal Team
3. Assess scope (what data exposed, how many users)
4. Notify affected users within 72 hours (GDPR requirement)
5. Implement fixes, conduct security audit

**Incident Type: Viral Negative Feedback (Social Media Crisis)**
1. Assess validity (legitimate issue vs. troll campaign)
2. Draft public response (transparent, empathetic)
3. Implement fix if systemic issue
4. Monitor sentiment, engage directly with critics

---

## **11. Success Metrics & KPIs**

### **11.1 Operational Efficiency**

| **Metric**                     | **Target**         |
|--------------------------------|--------------------|
| Vendor Verification Time       | <24 hours (manual) |
| Moderation Queue Backlog       | <100 items         |
| Fraud Detection Rate           | 90% catch rate     |
| Tag Accuracy                   | 95%                |
| User Report Response Time      | <12 hours          |

### **11.2 Platform Health**

| **Metric**                     | **Target**         |
|--------------------------------|--------------------|
| Uptime                         | 99.5%              |
| Crash Rate                     | <1%                |
| API Response Time              | <200ms (p95)       |

### **11.3 Compliance**

| **Metric**                     | **Target**         |
|--------------------------------|--------------------|
| Data Deletion Requests         | 100% fulfilled <30 days |
| GDPR Compliance Audits         | Pass quarterly audits |
| Policy Violation Enforcement   | <2% vendor ban rate |

---

## **12. Conclusion & Next Steps**

This document establishes the complete administrative and governance architecture for AirAd Phase-1. Successful platform operations depend on:

1. **Scalable Automation:** 70%+ automated verification reduces manual overhead.
2. **Quality Oversight:** Human review for edge cases ensures safety and accuracy.
3. **Transparent Governance:** Clear policies and enforcement build vendor/user trust.
4. **Data-Driven Operations:** Analytics dashboards guide proactive interventions.

The administrative layer is the platform's backbone. Without effective governance, quality degrades, fraud proliferates, and trust collapses.

**— End of Document —**
