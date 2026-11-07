# Phase 8: Post-launch and growth

## Table of contents
1. Managing app versions
2. Updating your app
3. Phased releases
4. App Store Connect analytics
5. User feedback and reviews
6. Continuous improvement loop

---

## 1. Managing app versions

### Semantic versioning
Apps use semantic versioning to communicate the scale of changes:

- **Major Version (1.0 → 2.0):** Significant updates, large features, potential functionality changes
- **Minor Version (1.0 → 1.1):** Smaller updates, minor features, bug fixes
- **Patch (1.0.0 → 1.0.1):** Even smaller fixes, specific bug addresses

### Communicate changes through version notes
For every update, inform users what's new. This helps users understand the value of updating and ensures transparency.

**Example version notes:**
- 1.0: Initial release
- 1.1: Added dark mode, fixed note sync bugs
- 2.0: Introduced collaborative sharing, redesigned UI

## 2. Updating your app

### Process for releasing a new version
1. **Increment version number** based on scale of changes
2. **Prepare the build** using Xcode archive
3. **Submit for review** via App Store Connect with updated version notes
4. **Wait for approval.** Apple says App Review typically reviews at least 50% of submissions in less than 24 hours and 90% in less than 48 hours ([App Review](https://developer.apple.com/distribute/app-review/)).

Always factor review time into your release schedule.

## 3. Phased releases

Releasing to all users simultaneously is risky. Phased releases mitigate this.

### How phased releases work
From Apple's [phased release](https://developer.apple.com/help/app-store-connect/update-your-app/release-a-version-update-in-phases) page (checked 2026-11-07):
- The update rolls out over 7 days to a random sample of users with automatic updates on: 1%, 2%, 5%, 10%, 20%, 50%, then 100%.
- Anyone can still download the new version manually from the App Store at any time, so it is a brake, not a gate.
- You can pause the rollout for up to 30 days, with no limit on the number of pauses.
- It gives you time to watch crash reports and reviews before most users have the update.

### Steps
1. On the version page, choose to release the update in phases before you submit.
2. Watch crashes, reviews and analytics as the rollout grows.
3. If problems show up, pause the release, fix them in a new build, then release that build.

**Tip:** Be prepared to act fast during phased releases. Swift action prevents small problems from escalating.

## 4. App Store Connect analytics

### Key metrics dashboard

**Downloads:** total downloads of the app, a measure of overall reach.

**Revenue:** Total earnings from in-app purchases, subscriptions, or app purchases.

**Engagement:** How often users interact with your app. Are they frequent users or one-time users?

**User Demographics & Device Usage:** Who your users are and what devices they use. Guides design and development decisions.

### Using analytics for decisions
- Spike in downloads after marketing campaign → that strategy works, invest more
- Decline in engagement → possible bug or design flaw in recent update
- Significant user base from non-English country → consider localizing
- Most users on older devices → optimize app accordingly

## 5. User feedback and reviews

### Monitoring reviews
- Check reviews regularly and look for patterns
- Multiple users reporting same issue = priority fix
- Use negative feedback as a roadmap for improvement

### Responding to reviews
Respond to positive and negative reviews alike:

**Positive review response:**
> "Thanks for the feedback! We're glad you're enjoying [feature]. Stay tuned for more updates!"

**Negative review response:**
> "We're sorry for the inconvenience. We're aware of this issue and are working on a fix. Please stay tuned for the next update."

### Encouraging positive reviews
- Ask with the system review prompt: SwiftUI's `RequestReviewAction` (`@Environment(\.requestReview)`, iOS 16 and later) or StoreKit's equivalent in UIKit. Apple disallows custom review prompts (guideline 5.6.1).
- The system decides whether to show it. For someone who hasn't rated the app on that device, it appears at most three times in 365 days ([RequestReviewAction](https://developer.apple.com/documentation/storekit/requestreviewaction)), so do not call it from a button that promises a prompt.
- Time the request after a positive moment, such as completing a goal, and after the person has used the app for a while.
- For a "Rate this app" row in settings, link to the App Store page instead of calling the prompt.
- Do not offer rewards for ratings or reviews.

## 6. Continuous improvement loop

### The post-launch cycle
1. **Monitor** analytics and reviews
2. **Identify** patterns, bugs, and opportunities
3. **Prioritize** fixes and features based on user impact
4. **Build** the update
5. **Test** thoroughly
6. **Submit** for review
7. **Release** (consider phased rollout)
8. **Repeat**

### Key principles
- User feedback is your most valuable data source
- Fix critical bugs immediately
- Add features that users actually request
- Keep app compatible with latest iOS versions and devices
- New iOS releases may require app updates
- Marketing is ongoing, so keep the influencer partnerships going
- Track ROI on every marketing dollar spent

### Helpful resources
- Paywall design: apphud.com/blog (high-converting subscription paywalls)
- App Store Optimization: apptweak.com (ASO guides)
- Onboarding examples: userpilot.com/blog (onboarding UX examples)
- Cal AI onboarding reference: screensdesign.com/showcase/cal-ai-calorie-tracker
