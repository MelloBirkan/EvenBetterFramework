---
name: evenbetter-app-launcher
description: >
  Complete playbook for planning, building, submitting, marketing, and monetizing iOS apps. Covers ideation, validation, wireframing, App Store submission, screenshots, rejections, review process, listings, descriptions, keywords, monetization, paywalls, onboarding, free trials, RevenueCat, subscriptions, privacy policies, EULA, Xcode setup, SwiftUI structure, HIG compliance, influencer marketing, organic growth, App Store Connect, versioning, updates, and analytics. Use this skill aggressively for ANY iOS app lifecycle question — from "is my app idea good" to "why was my app rejected" to "how do I market my app" to "how do I price my subscription." Trigger on mentions of App Store, iOS app, mobile app launch, app marketing, app monetization, or app review.
---

# evenbetter-app-launcher — From Idea to Revenue

A complete playbook for planning, building, submitting, marketing, and growing an iOS app on the Apple App Store. This skill covers eight phases of the app lifecycle. Each phase has a dedicated reference file with deep-dive details.

## How to Use This Skill

1. **Identify which phase the user is in** based on their question
2. **Read the relevant reference file(s)** from `references/` before responding
3. **Combine knowledge across phases** when the user needs a holistic answer

---

## Phase Overview

### Phase 1 — Ideation & Validation
**When to read:** User is brainstorming app ideas, evaluating whether an idea is good, or asking about market fit.
**Reference:** `references/01-ideation.md`

Key principles:
- Solve a problem you personally experience (YC principle)
- Target high-frequency, high-intensity pain points
- Avoid "tarpit ideas" (social networks for niche, "Uber for X")
- Apply the Purple Cow principle — your product must be remarkable
- Build for a niche first, then expand
- Create a "gotcha moment" — one feature so compelling it stops the scroll
- Validate fast: build minimal, share with target users, listen to behavior not words

### Phase 2 — Planning & Design
**When to read:** User needs help with wireframes, storyboards, requirements, vision, or Apple's HIG.
**Reference:** `references/02-planning-design.md`

Key principles:
- Start with vision: "Why are we building this?"
- Define target audience and their pain points
- Create low-fidelity wireframes first, then high-fidelity
- Follow Apple's Human Interface Guidelines (HIG) from day one
- Translate wireframes into development requirements and milestones
- Use tab bars for primary navigation, standard controls, proper typography

### Phase 3 — Development & Xcode Setup
**When to read:** User asks about project structure, Xcode configuration, scaffolding, or code organization.
**Reference:** `references/03-development.md`

Key principles:
- Set correct bundle identifier (reverse DNS: com.yourname.appname)
- Configure deployment targets, device orientations, signing certificates
- Use semantic versioning (Major.Minor.Patch)
- Organize project with clear folder structure
- Set up version control (Git/GitHub) from the start
- Implement core features first, iterate with refactoring

### Phase 4 — Monetization & Onboarding
**When to read:** User asks about pricing, paywalls, onboarding, free trials, subscriptions, or RevenueCat.
**Reference:** `references/04-monetization.md`

Key principles:
- Recommended pricing: $9.99/month or $59.99/year with 3-day free trial on yearly
- Onboarding flow: Educate → Personalize → Invest (sunk cost) → Tie goals → Paywall
- The paywall appears AFTER onboarding, not before
- Study successful apps (Cal AI, Quittr) for onboarding patterns
- Free trials configured in App Store Connect via Introductory Offers
- Requires RevenueCat integration and App Store subscriptions already set up

### Phase 5 — App Store Preparation
**When to read:** User needs help with screenshots, metadata, icons, policies, or the submission checklist.
**Reference:** `references/05-appstore-prep.md`

Key principles:
- Screenshots: iPhone 1290×2796px (9:16), iPad 2048×2732px (4:3)
- NEVER stretch iPhone screenshots for iPad — instant rejection
- Create privacy policy, terms & conditions (use Termly), and use Apple's Standard EULA
- Link policies in App Store description AND inside the app (paywall/settings)
- If paywall exists, MUST disclose in App Store description
- Create a support URL (Google Sites, Termly, or any website)
- Permission descriptions in Info.plist must clearly explain WHY each permission is needed
- Test thoroughly for at least 1 hour before submission

### Phase 6 — App Review & Submission
**When to read:** User asks about the review process, rejections, approval tips, or expedited reviews.
**Reference:** `references/06-review-submission.md`

Key principles:
- First submission: 24–72 hours; Updates: 12–48 hours
- Common rejection reasons: permission issues, subscription problems, iPad screenshots
- Rejections are NORMAL — most apps approved after one follow-up
- Provide demo credentials if login is required
- Expedited reviews available for critical bugs/time-sensitive launches
- After approval: release immediately, schedule, or phased rollout

### Phase 7 — Marketing & Growth
**When to read:** User asks about promoting their app, influencer marketing, organic content, or user acquisition.
**Reference:** `references/07-marketing.md`

Key principles:
- Influencer marketing is the primary growth lever
- Find influencers via organic feed engineering or VA outreach
- Outreach DM: "Paid promo?" + one-sentence app description + clear invitation
- NEVER give payment numbers over text — get on a phone call
- Negotiate $2–5 CPM with minimum view guarantees
- Content should feel authentic, not like an ad — "the influencer is the hero, the app is a tool"
- Organic content validates the "gotcha moment" and builds following for free
- Meme/topic pages: cost-effective for views ($0.50–$1 CPM)

### Phase 8 — Post-Launch & Growth
**When to read:** User asks about app updates, versioning, analytics, user feedback, or maintenance.
**Reference:** `references/08-post-launch.md`

Key principles:
- Use semantic versioning and communicate changes via version notes
- Use phased releases for safer rollouts
- Monitor App Store Connect Analytics: downloads, revenue, engagement, demographics
- Respond to ALL reviews (positive and negative)
- Encourage positive reviews with in-app prompts
- Continuously iterate based on user feedback and analytics data

---

## Quick Decision Tree

```
User asks about...
├── "Is my app idea good?" → Phase 1 (references/01-ideation.md)
├── "How do I design my app?" → Phase 2 (references/02-planning-design.md)
├── "How do I set up Xcode?" → Phase 3 (references/03-development.md)
├── "How do I make money?" → Phase 4 (references/04-monetization.md)
├── "What screenshots do I need?" → Phase 5 (references/05-appstore-prep.md)
├── "Why was my app rejected?" → Phase 6 (references/06-review-submission.md)
├── "How do I market my app?" → Phase 7 (references/07-marketing.md)
└── "How do I update my app?" → Phase 8 (references/08-post-launch.md)
```

## Important Reminders

- Always check Apple's latest Human Interface Guidelines and App Store Review Guidelines
- The App Store review process applies to EVERY submission and update
- Privacy policy is REQUIRED for all apps
- iPad screenshots must be real iPad screenshots, not stretched iPhone ones
- Permission descriptions must clearly explain WHY the app needs each permission
- If you have a paywall, disclose it in your App Store description
- Test on real devices whenever possible, not just simulators
