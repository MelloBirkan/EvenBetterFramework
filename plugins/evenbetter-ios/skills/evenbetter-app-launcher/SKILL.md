---
name: evenbetter-app-launcher
description: >-
  Guides a chosen iOS app through Xcode setup, pricing, paywalls and trials, screenshots and metadata, App Review and rejections, marketing, updates and analytics. Use when the user asks how to price, submit, get approved, market or update an iOS app, why it was rejected, or what comes next after launch. To check whether an idea has a market, use evenbetter-app-opportunity-research.
---

# evenbetter-app-launcher: from idea to revenue

Paths in this skill and its references are relative to this SKILL.md's folder.

A playbook for planning, building, submitting, marketing and growing an iOS app on the App Store, in eight phases. Each phase has a reference file with the detail.

If current system, developer or user instructions conflict with this skill, follow them.

## How to use this skill

1. Work out which phase the user is in from their question. If it is unclear, ask one closed question listing the 2-4 likely phases: `AskUserQuestion` in Claude Code, `request_user_input` in Codex when the session offers it, otherwise numbered options in plain text.
2. Read the matching file in `references/` before answering.
3. Combine phases when the user needs the whole picture, for example "am I ready to launch?" spans phases 5 and 6.
4. Apple changes store rules often. The dated facts in the references were checked on 2026-11-07 against the Apple pages they cite. Before you present a deadline, size or fee as current, re-check that page with the session's web tools if it has them, and say when you could not.

## Routing to other EvenBetter skills

- Market evidence for an idea (competitors, revenue, demand): the evenbetter-app-opportunity-research skill.
- UX and Apple HIG planning for one screen: evenbetter-ios-feature. For several screens or a whole app: evenbetter-ios-epic.
- An accessibility and HIG audit of existing Swift code: evenbetter-analyze, then evenbetter-validate and evenbetter-repair.

---

## Phase overview

### Phase 1: Ideation and validation

**Read when:** the user is brainstorming, asking whether an idea is good, or asking about market fit.
**Reference:** `references/01-ideation.md`

- Solve a problem you experience yourself (a Y Combinator principle).
- Target pain that is frequent and intense.
- Avoid "tarpit ideas" such as social networks for a niche or "Uber for X".
- Make the product remarkable (the Purple Cow principle).
- Build for a niche first, then expand.
- Create a "gotcha moment": one feature compelling enough to stop the scroll.
- Validate fast: build a minimal version, share it with target users, and watch what they do rather than what they say.

### Phase 2: Planning and design

**Read when:** the user needs wireframes, storyboards, requirements, a vision or milestones.
**Reference:** `references/02-planning-design.md`

- Start with the vision: why are we building this?
- Define the target audience and their pain points.
- Make low-fidelity wireframes first, then high-fidelity ones.
- Follow Apple's Human Interface Guidelines from day one; route detailed HIG work to evenbetter-ios-feature or evenbetter-ios-epic.
- Turn wireframes into development requirements and milestones.

### Phase 3: Development and Xcode setup

**Read when:** the user asks about project structure, Xcode configuration, signing or code organization.
**Reference:** `references/03-development.md`

- Set a reverse-DNS bundle identifier (com.yourname.appname).
- Configure the deployment target, device families, orientations and signing. App Store uploads must be built with Xcode 26 or later on the iOS 26 SDK. Apple's minimum target is iOS 13, but Xcode 26 and 27 start at iOS 15, so iOS 15 is the practical floor.
- Use semantic versioning (major.minor.patch).
- Organize the project in clear folders and use Git from the start.
- Build core features first, then iterate and refactor.

### Phase 4: Monetization and onboarding

**Read when:** the user asks about pricing, paywalls, onboarding, free trials, subscriptions or RevenueCat.
**Reference:** `references/04-monetization.md`

- A common starting point: USD 9.99 a month or USD 59.99 a year, with a 3-day free trial on the yearly plan only.
- Onboarding flow: educate, personalize, build investment, tie the user's goals to the app, then show the paywall.
- Show the paywall after onboarding, not before.
- Study successful apps in the category (for example Cal AI or Quittr) for onboarding patterns.
- Free trials are introductory offers on a subscription in App Store Connect.
- Set up subscriptions in App Store Connect and purchase handling in the app, with StoreKit directly or a service such as RevenueCat, before adding trials.
- Unlock digital features and content with In-App Purchase (App Review Guideline 3.1.1). Links to other purchase methods depend on the storefront; the reference has the current rules.

### Phase 5: App Store preparation

**Read when:** the user needs screenshots, metadata, an icon, policies, store requirements or the submission checklist.
**Reference:** `references/05-appstore-prep.md`

- Screenshots: 1-10 per device size, JPEG or PNG, no transparency. For iPhone, use the 6.9-inch class (1320 x 2868 or 1290 x 2796 portrait). Apple's page names the medium Dynamic Island set as required; the reference says when to add it. For iPad, use the 13-inch class (2064 x 2752 or 2048 x 2732 portrait), required if the app runs on iPad. From April 2027, apps using the iOS 27.1 SDK or later also need iPhone Duo screenshots.
- Capture iPad screenshots on an iPad or iPad simulator. Stretched iPhone screenshots get the submission rejected under guideline 2.3.3.
- Current store requirements: Xcode 26 and the iOS 26 SDK, a deployment target of iOS 13 or later (iOS 15 in practice), the 4+/9+/13+/16+/18+ age ratings, App Privacy details and a privacy manifest. Accessibility Nutrition Labels are voluntary for now, and Apple says they will become required. The reference has the dates and sources.
- To decide which Accessibility Nutrition Labels the app can claim on each device and draft the answers, run the evenbetter-accessibility-nutrition-labels skill.
- Every iOS app needs a privacy policy URL in App Store Connect and a link inside the app. Use Apple's standard EULA unless you need your own terms.
- Link the privacy policy and terms of use on the paywall and in settings, and add them to the description.
- If the app sells in-app purchases, say so in the description and screenshots (guideline 2.3.2).
- Every app needs a working support URL with contact details.
- Write purpose strings in Info.plist that say specifically why the app needs each permission.
- Test every flow on a real device before submitting.

### Phase 6: App Review and submission

**Read when:** the user asks about the review process, rejections, approval tips or expedited review.
**Reference:** `references/06-review-submission.md`

- Apple says App Review typically reviews at least 50% of submissions in less than 24 hours and 90% in less than 48 hours.
- More than 40% of unresolved issues fall under guideline 2.1, App Completeness: crashes, placeholder content and missing information.
- Other common causes: vague permission strings, subscription and paywall gaps, stretched iPad screenshots.
- Rejections are normal. Most apps get approved after one follow-up.
- Give App Review a demo account or demo mode if the app needs a login.
- For a critical bug fix or an event-tied release, request expedited review through Apple's form at developer.apple.com/contact/app-store/?topic=expedite after submitting.
- After approval, release manually, automatically or on a set date. Updates can also go out as a 7-day phased release.

### Phase 7: Marketing and growth

**Read when:** the user asks about promoting the app, influencer marketing, organic content or user acquisition.
**Reference:** `references/07-marketing.md`

- Influencer marketing is the main growth lever for consumer apps.
- Find influencers through feed engineering or outreach by a virtual assistant.
- Outreach DM: "Paid promo?", one sentence on the app, a clear invitation.
- Discuss money on a call, not in DMs.
- Negotiate around USD 2-5 CPM with a minimum view guarantee.
- Make content feel like the creator's own, with the app as a tool and the creator as the hero, and still mark it as paid with the platform's label or #ad.
- Organic content tests the gotcha moment and builds a following for free.
- Meme and topic pages are cheap views, around USD 0.50-1 CPM.

### Phase 8: Post-launch and growth

**Read when:** the user asks about updates, versioning, analytics, user feedback or maintenance.
**Reference:** `references/08-post-launch.md`

- Use semantic versioning and explain each update in its release notes.
- Use phased releases for safer rollouts.
- Watch App Store Connect analytics: downloads, revenue, engagement, demographics.
- Reply to reviews, positive and negative.
- Ask for ratings only with the system review prompt, after a positive moment. Apple rejects custom review prompts (guideline 5.6.1).
- Keep iterating on user feedback and analytics.

---

## Quick decision tree

```
User asks about...
├── "Is my app idea good?" → Phase 1 (references/01-ideation.md); for market data, evenbetter-app-opportunity-research
├── "How do I design my app?" → Phase 2 (references/02-planning-design.md)
├── "How do I set up Xcode?" → Phase 3 (references/03-development.md)
├── "How do I make money?" → Phase 4 (references/04-monetization.md)
├── "What screenshots do I need?" → Phase 5 (references/05-appstore-prep.md)
├── "Why was my app rejected?" → Phase 6 (references/06-review-submission.md)
├── "How do I market my app?" → Phase 7 (references/07-marketing.md)
└── "How do I update my app?" → Phase 8 (references/08-post-launch.md)
```

## Reminders

- Check the current App Store Review Guidelines and Human Interface Guidelines before a submission; both change several times a year.
- Every submission and every update goes through App Review, so plan release dates around it.
- Test on real devices when you can, not only in the simulator.
