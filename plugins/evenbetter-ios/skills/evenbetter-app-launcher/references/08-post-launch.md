# Phase 8 — Post-Launch & Growth

## Table of Contents
1. Managing App Versions
2. Updating Your App
3. Phased Releases
4. App Store Connect Analytics
5. User Feedback & Reviews
6. Continuous Improvement Loop

---

## 1. Managing App Versions

### Semantic Versioning
Apps use semantic versioning to communicate the scale of changes:

- **Major Version (1.0 → 2.0):** Significant updates, large features, potential functionality changes
- **Minor Version (1.0 → 1.1):** Smaller updates, minor features, bug fixes
- **Patch (1.0.0 → 1.0.1):** Even smaller fixes, specific bug addresses

### Communicate Changes Through Version Notes
For every update, inform users what's new. This helps users understand the value of updating and ensures transparency.

**Example version notes:**
- 1.0: Initial release
- 1.1: Added dark mode, fixed note sync bugs
- 2.0: Introduced collaborative sharing, redesigned UI

## 2. Updating Your App

### Process for Releasing a New Version
1. **Increment version number** based on scale of changes
2. **Prepare the build** using Xcode archive
3. **Submit for review** via App Store Connect with updated version notes
4. **Wait for approval** (updates typically 12–48 hours)

Always factor review time into your release schedule.

## 3. Phased Releases

Releasing to all users simultaneously is risky. Phased releases mitigate this.

### How Phased Releases Work
- Release update to a subset of users, increasing over time
- Gives time to monitor feedback and catch unforeseen issues
- Typically completes over one week

### Steps
1. When submitting, choose "Phased Release" option
2. Monitor feedback as rollout increases
3. If problems arise: pause the release, fix, then resume

**Tip:** Be prepared to act fast during phased releases. Swift action prevents small problems from escalating.

## 4. App Store Connect Analytics

### Key Metrics Dashboard

**Downloads:** Total times your app has been downloaded — measures overall reach.

**Revenue:** Total earnings from in-app purchases, subscriptions, or app purchases.

**Engagement:** How often users interact with your app. Are they frequent users or one-time users?

**User Demographics & Device Usage:** Who your users are and what devices they use. Guides design and development decisions.

### Using Analytics for Decisions
- Spike in downloads after marketing campaign → that strategy works, invest more
- Decline in engagement → possible bug or design flaw in recent update
- Significant user base from non-English country → consider localizing
- Most users on older devices → optimize app accordingly

## 5. User Feedback & Reviews

### Monitoring Reviews
- Check reviews regularly — look for patterns
- Multiple users reporting same issue = priority fix
- Use negative feedback as a roadmap for improvement

### Responding to Reviews
Respond to BOTH positive and negative reviews:

**Positive review response:**
> "Thanks for the feedback! We're glad you're enjoying [feature]. Stay tuned for more updates!"

**Negative review response:**
> "We're sorry for the inconvenience. We're aware of this issue and are working on a fix. Please stay tuned for the next update."

### Encouraging Positive Reviews
- Add an in-app prompt asking users to rate after they've used the app for a while
- Send push notifications (with consent) thanking them and asking for a review
- Time the prompt after a positive interaction (e.g., completing a goal)

## 6. Continuous Improvement Loop

### The Post-Launch Cycle
1. **Monitor** analytics and reviews
2. **Identify** patterns, bugs, and opportunities
3. **Prioritize** fixes and features based on user impact
4. **Build** the update
5. **Test** thoroughly
6. **Submit** for review
7. **Release** (consider phased rollout)
8. **Repeat**

### Key Principles
- User feedback is your most valuable data source
- Fix critical bugs immediately
- Add features that users actually request
- Keep app compatible with latest iOS versions and devices
- New iOS releases may require app updates
- Marketing is ongoing — continue influencer partnerships
- Track ROI on every marketing dollar spent

### Helpful Resources
- Paywall design: apphud.com/blog (high-converting subscription paywalls)
- App Store Optimization: apptweak.com (ASO guides)
- Onboarding examples: userpilot.com/blog (onboarding UX examples)
- Cal AI onboarding reference: screensdesign.com/showcase/cal-ai-calorie-tracker
