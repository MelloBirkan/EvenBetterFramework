# Phase 4: Monetization and onboarding

## Table of contents
1. Pricing strategy
2. Onboarding flow design
3. Paywall strategy
4. Free trials
5. Legal requirements (privacy, T&C, EULA)
6. Purchase handling: StoreKit or RevenueCat

---

## 1. Pricing strategy

The simplest way to monetize: make the app pay-to-access with a paywall after onboarding.

### A common starting point
- **$9.99/month** or **$59.99/year**
- Attach a **3-day free trial to the yearly plan only**
- This nudges users toward the annual plan, which brings in more cash up front

These are a starting point, not a rule. Check what competitors charge, and remember Apple's commission: 30% on most sales, 15% for App Store Small Business Program members, and 15% on subscriptions after a subscriber's first paid year ([subscriptions](https://developer.apple.com/app-store/subscriptions/), [Small Business Program](https://developer.apple.com/app-store/small-business-program/), checked 2026-11-07).

### Pricing rules of thumb
- If competitors exist → copy their pricing
- If your app is unique → use intuition, then test and iterate
- Experiment with pricing; there is no perfect formula

## 2. Onboarding flow design

Onboarding is everything that happens before the paywall. It should:
- Educate the user about the app
- Tailor the experience to them personally
- Build desire and justification for why they need it

### Recommended onboarding format

#### Step 1: Educate the user
Show quick 3-5 second visuals demonstrating each major feature. People won't pay if they don't know what the app does.

#### Step 2: Personalize the experience
- Ask for their name and use it throughout onboarding
- Ask questions that lead them to the problem your app solves
- Example (Cal AI): "Have you tried other weight loss apps in the past?" → If yes: "Here's why we're different."

#### Step 3: Use sunk-cost psychology
Draw out personalization just enough that the user feels invested, but not so long that they get bored and leave. The more time they spend setting up, the more compelled they are to pay at the paywall.

#### Step 4: Tie their goals to the app
- Ask for their objective related to your solution
- Show a visual roadmap: their journey without your app compared with their journey with it
- Creates internal logic: "This app accelerates my progress"

#### Step 5: Lock the final deliverable behind the paywall
For apps that analyze data/media: the user uploads content during onboarding → sees "Profile complete" → hits the paywall. They have already invested time and emotion, so they are primed to convert.

### Study other apps
Spend 1-2 hours downloading successful apps in your space and studying their monetization experience. Notice where you feel compelled to buy, and why. Reference apps: Cal AI, Quittr, UMax.

## 3. Paywall strategy

### Hard paywall vs. soft paywall
- **Hard paywall:** every feature locked behind payment. Disclose it in the App Store description and screenshots (guideline 2.3.2).
- **Soft paywall:** Some features free, premium features locked. More user-friendly but lower conversion.

### Paywall requirements (Apple)
- Link the privacy policy and the terms of use (EULA) on the paywall.
- Say clearly what the user gets for the price, and show the price and billing period (guideline 3.1.2).
- Unlock digital features and content with In-App Purchase (guideline 3.1.1).
- Links to other ways to pay depend on the storefront. On the US storefront, apps may include buttons, external links or other calls to action for other purchase methods. In some other regions, apps can apply for a StoreKit External Purchase Link Entitlement. Everywhere else, the app and its metadata may not point customers to purchase methods other than In-App Purchase ([guidelines 3.1.1 and 3.1.1(a)](https://developer.apple.com/app-store/review/guidelines/), checked 2026-11-07).

### Paywall design tips
- Show both monthly and yearly pricing
- Highlight the savings on yearly plan
- Include a "Restore Purchases" button
- Make the value proposition crystal clear
- Show what the user gets vs. what they're missing

## 4. Free trials

### How to add a free trial (App Store Connect)
**Prerequisites:** subscriptions configured in App Store Connect, and purchase handling in the app (StoreKit directly or a service such as RevenueCat).

1. Open the subscriptions tab in your app's distribution section
2. Click on the subscription you want to add a trial to
3. Click the plus button to add a new offer
4. Select "Introductory Offer"
5. Set the duration (e.g., 3 days, 7 days)
6. Click next and confirm

New offers can take a while to show up in the app. Test the trial in the sandbox, or with a StoreKit configuration file in Xcode, before submitting.

### Best practice
- Attach free trial to yearly plan only (encourages annual commitment)
- 3-day trial is the most common for consumer apps
- 7-day trial for apps requiring more time to demonstrate value

## 5. Legal requirements

### End user license agreement (EULA)
- You do not need to write your own.
- **Apple's Standard EULA** applies by default on the App Store.
- Write a custom EULA only if you have specific legal requirements, and add it in App Store Connect.

### Privacy policy (required for every iOS app)
- Enter its URL in App Store Connect and link it inside the app (guideline 5.1.1(i)), whatever data you collect.
- Describe your data handling in the App Privacy section of App Store Connect too.
- Generate using: **Termly** (recommended), PrivacyPolicies.com, or Iubenda
- These tools let you answer questions, auto-generate a policy, and host it as a URL

### Terms and conditions
- Define how users can use your app and limit your liability
- Generate with same tools as Privacy Policy (Termly, PrivacyPolicies.com)
- Most tools bundle Terms + Privacy Policy together

### Where to place these policies
- Add all policies to your **App Store description**
- Link to the policies from the app's **Settings** screen
- Link to the policies on the **paywall** screen
- Missing links in the listing or in the app are a common rejection reason

## 6. Purchase handling: StoreKit or RevenueCat

Purchases need code in the app. Two common routes:

- **StoreKit 2 directly.** Apple's framework loads products, runs purchases, verifies transactions and reports subscription status. SwiftUI's StoreKit views (`SubscriptionStoreView`, `ProductView`, iOS 17 and later) can draw a basic paywall.
- **RevenueCat.** A third-party service on top of StoreKit that handles transaction validation, subscription status, paywall experiments and a revenue dashboard.

Either way, finish it before adding free trials or paywall logic: a trial cannot be tested until purchases work.
