# Phase 4 — Monetization & Onboarding

## Table of Contents
1. Pricing Strategy
2. Onboarding Flow Design
3. Paywall Strategy
4. Free Trials
5. Legal Requirements (Privacy, T&C, EULA)
6. RevenueCat Integration

---

## 1. Pricing Strategy

The simplest way to monetize: make the app pay-to-access with a paywall after onboarding.

### Recommended Pricing
- **$9.99/month** or **$59.99/year**
- Attach a **3-day free trial to the yearly plan only**
- This encourages users to choose the annual plan, increasing upfront cash flow

### Pricing Rules of Thumb
- If competitors exist → copy their pricing
- If your app is unique → use intuition, then test and iterate
- Experiment with pricing — there's no perfect formula

## 2. Onboarding Flow Design

Onboarding = everything that happens BEFORE the paywall. It should:
- Educate the user about the app
- Tailor the experience to them personally
- Build desire and justification for why they need it

### Recommended Onboarding Format

#### Step 1: Educate the User
Show quick 3–5 second visuals demonstrating each major feature. People won't pay if they don't know what the app does.

#### Step 2: Personalize the Experience
- Ask for their name and use it throughout onboarding
- Ask questions that lead them to the problem your app solves
- Example (Cal AI): "Have you tried other weight loss apps in the past?" → If yes: "Here's why we're different."

#### Step 3: Use Sunk-Cost Psychology
Draw out personalization just enough that the user feels invested — but not so much they get bored and leave. The more time they spend setting up, the more compelled they are to pay at the paywall.

#### Step 4: Tie Their Goals to the App
- Ask for their objective related to your solution
- Show a visual roadmap: their journey WITHOUT your app vs. WITH your app
- Creates internal logic: "This app accelerates my progress"

#### Step 5: Lock the Final Deliverable Behind the Paywall
For apps that analyze data/media: the user uploads content during onboarding → sees "Profile complete" → hits the paywall. They've already invested time and emotion — now they're primed to convert.

### Study Other Apps
Spend 1–2 hours downloading successful apps in your space and studying their monetization experience. Notice where you feel compelled to buy and WHY. Reference apps: Cal AI, Quittr, UMax.

## 3. Paywall Strategy

### Hard Paywall vs. Soft Paywall
- **Hard paywall:** ALL features locked behind payment. Must disclose in App Store description.
- **Soft paywall:** Some features free, premium features locked. More user-friendly but lower conversion.

### Paywall Requirements (Apple)
- Must include links to: Privacy Policy, Terms & Conditions, EULA
- Must be transparent about pricing
- Must use Apple's in-app purchase system (no external payment links)

### Paywall Design Tips
- Show both monthly and yearly pricing
- Highlight the savings on yearly plan
- Include a "Restore Purchases" button
- Make the value proposition crystal clear
- Show what the user gets vs. what they're missing

## 4. Free Trials

### How to Add a Free Trial (App Store Connect)
**Prerequisites:** RevenueCat already integrated, subscriptions configured in App Store Connect.

1. Open the subscriptions tab in your app's distribution section
2. Click on the subscription you want to add a trial to
3. Click the plus button to add a new offer
4. Select "Introductory Offer"
5. Set the duration (e.g., 3 days, 7 days)
6. Click next and confirm

The free trial should appear in your app within about 20 minutes.

### Best Practice
- Attach free trial to yearly plan only (encourages annual commitment)
- 3-day trial is the most common for consumer apps
- 7-day trial for apps requiring more time to demonstrate value

## 5. Legal Requirements

### End User License Agreement (EULA)
- You do NOT need to write your own
- Use **Apple's Standard EULA** — accepted by default on the App Store
- Only write custom EULA if you have specific legal requirements

### Privacy Policy (REQUIRED for all apps)
- Required especially if you collect: user data, analytics, payments, account info
- Generate using: **Termly** (recommended), PrivacyPolicies.com, or Iubenda
- These tools let you answer questions, auto-generate a policy, and host it as a URL

### Terms & Conditions
- Define how users can use your app and limit your liability
- Generate with same tools as Privacy Policy (Termly, PrivacyPolicies.com)
- Most tools bundle Terms + Privacy Policy together

### Where to Place These Policies
- Add all policies in your **App Store description**
- Link to policies inside the app's **Settings** screen
- Link to policies on the **Paywall** screen
- Failure to do both = App Store rejection

## 6. RevenueCat Integration

RevenueCat handles in-app purchases and subscriptions:
- Manages receipt validation
- Handles subscription status tracking
- Works with App Store Connect subscriptions
- Provides analytics dashboard for revenue

**Note:** Full RevenueCat integration guide is a separate setup process. The key is to have it configured BEFORE adding free trials or paywall functionality.
