# Phase 5: App Store preparation

## Table of contents
1. App Store Connect setup
2. Store requirements (2026)
3. App icon
4. Screenshots
5. App description and keywords
6. Metadata and Info.plist
7. Policies and support URL
8. Pre-submission checklist

The Apple facts in this file were checked on 2026-11-07 against the pages linked next to them. Apple changes these often, so re-check the page before quoting a size, date or fee as current.

---

## 1. App Store Connect setup

### Two key platforms
- **Apple Developer website (Certificates, Identifiers & Profiles):** certificates, app IDs, provisioning profiles.
- **App Store Connect:** listings, analytics, financials, submissions.

### Account setup
- Enroll in the Apple Developer Program. Membership costs USD 99 a year ([developer.apple.com/programs](https://developer.apple.com/programs/)).
- Understand the App Store Connect roles, such as Admin, App Manager, Developer and Marketing.
- In Apps, add a new app (platform, name, primary language, bundle ID, SKU). Then fill in App Information: category, the age rating questionnaire and the privacy policy URL.
- Set up pricing and availability.

## 2. Store requirements (2026)

These block an upload, a submission or a storefront when they are missing.

| Requirement | Since | What to do | Source |
| --- | --- | --- | --- |
| Build with Xcode 26 or later, using the iOS 26 SDK or later | 2026-04-28 | Archive with a current Xcode. Xcode 26 and Xcode 27 support deployment targets from iOS 15. | [Upcoming requirements](https://developer.apple.com/news/upcoming-requirements/), [Xcode system requirements](https://developer.apple.com/xcode/system-requirements) |
| iOS and iPadOS apps must target iOS 13 or later | 2026-09-09 | Apple's rule says iOS 13, but the Xcode versions that can upload today start at iOS 15, so set the minimum deployment target to iOS 15 or higher. | [Upcoming requirements](https://developer.apple.com/news/upcoming-requirements/), [Xcode system requirements](https://developer.apple.com/xcode/system-requirements) |
| Age ratings are 4+, 9+, 13+, 16+ and 18+ | 2026-01-31 | Answer the updated age rating questions in App Information. Apple said apps without answers by that date would hit an interruption when submitting updates. Devices on OS versions before 26 still show the older 4+, 9+, 12+ and 17+ ratings. | [Upcoming requirements](https://developer.apple.com/news/upcoming-requirements/), [Age ratings](https://developer.apple.com/help/app-store-connect/reference/app-information/age-ratings-values-and-definitions) |
| App Privacy details | in force | Describe your data handling in App Store Connect, including the practices of third-party SDKs you ship. | [Manage app privacy](https://developer.apple.com/help/app-store-connect/manage-app-information/manage-app-privacy) |
| Privacy manifest with approved reasons for the listed APIs | 2024-05-01 | Add `PrivacyInfo.xcprivacy` and declare an approved reason for each required-reason API your code or its SDKs use. | [Upcoming requirements](https://developer.apple.com/news/upcoming-requirements/) |
| EU trader status (Digital Services Act) | 2025-02-17 | Provide trader status in App Store Connect, or the app is removed from the EU App Store. | [Upcoming requirements](https://developer.apple.com/news/upcoming-requirements/) |
| iPhone Duo screenshots | April 2027 | Required for any app using the iOS 27.1 SDK or later. See section 4. | [Screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications/) |

### Accessibility Nutrition Labels

The product page can show which accessibility features the app supports: VoiceOver, Voice Control, Larger Text, Dark Interface, Differentiate Without Color Alone, Sufficient Contrast, Reduced Motion, Captions and Audio Descriptions. The labels are voluntary today, and Apple says they will become required ([overview](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/overview-of-accessibility-nutrition-labels/)).

Claim only what people can do in all of the app's common tasks with the feature on. You answer separately for each device in App Store Connect, under App Accessibility in the app's sidebar, and you can add an optional accessibility URL that links to a page on your website. The evenbetter-accessibility-nutrition-labels skill lists the common tasks, checks each feature against EvenBetter findings, runtime results and checks on a device, and drafts the answers for you to enter. Run evenbetter-analyze and evenbetter-validate first, so it has confirmed findings to work from.

## 3. App icon

### Design principles
- The icon is the first thing people see, so it matters.
- Make it appealing and relevant to what the app does.
- Make it stand out among other icons.
- Avoid text; it is hard to read at small sizes.

### Technical requirements
- Provide either a single 1024 x 1024 px square image or a layered Icon Composer file. Layers give the most control over how Liquid Glass and the dark, clear and tinted appearances render ([HIG: App icons](https://developer.apple.com/design/human-interface-guidelines/app-icons)).
- Provide square, unmasked artwork. The system applies the rounded corners.
- A flattened PNG icon must have no transparency.

## 4. Screenshots

### Why screenshots matter
Screenshots are one of the biggest drivers of installs. Most people decide from the first few.

### Required sizes

From Apple's [screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications/):

- 1-10 screenshots per device size, in `.jpeg`, `.jpg` or `.png`, with no alpha channel or transparency.
- **iPhone, 6.9-inch class** (Apple's "iPhone with Dynamic Island (large display)" set): **1320 x 2868**, **1290 x 2796** or 1260 x 2736 px portrait. App Store Connect scales this set down for smaller iPhones.
- Apple's page lists the medium Dynamic Island set (1206 x 2622 or 1179 x 2556 px) as the required iPhone size, while its scaling notes let the larger set stand in, so the page contradicts itself. Upload the 6.9-inch set, check the version page in App Store Connect for a missing-size warning, and add a medium set if it asks.
- **iPad, 13-inch class:** **2064 x 2752** or **2048 x 2732** px portrait. Required if the app runs on iPad.
- **iPhone Duo:** outer display 1398 x 2034 px, inner display 2007 x 2853 px (or the landscape equivalents). Starting in April 2027, these are required for any app using the iOS 27.1 SDK or later.

### Use real iPad screenshots
Capture iPad screenshots on an iPad or the iPad simulator. App Review rejects iPhone screenshots that were stretched or resized to look like iPad ones (guideline 2.3.3), because they misrepresent the app.

### Screenshot strategy
1. Screenshot 1: the core value proposition
2. Screenshots 2-3: the main features
3. Screenshots 4-5: differentiation, results or use cases
4. Keep the text short and readable on small screens.
5. Use as many of the 10 slots as you have strong screens for.

### How to capture screenshots

**iPhone:**
1. Open the Simulator from Xcode.
2. Choose a current Pro Max device (6.9-inch class).
3. Capture in portrait with Cmd+S.

**iPad:**
1. Open an iPad simulator from Xcode.
2. Choose a 13-inch iPad Pro or iPad Air.
3. Capture in portrait.

### Design tools
- **Canva:** search "App Store Screenshot" and pick an iPhone or iPad template, then export at one of the sizes above.
- **Screenshots Pro:** device frames, consistent layouts, batch export.
- **Figma:** full design control.
- **iOS Simulator:** best for raw captures.

### Export guidelines
- Format: PNG or JPEG, flattened, no transparency.
- No visible compression artifacts.
- Keep text within safe margins.
- Use high contrast and readable fonts.

### Common mistakes
- Wrong dimensions
- Missing iPad screenshots when the app runs on iPad
- Text too small to read
- Overcrowded designs
- Stretched iPhone screenshots used for iPad

## 5. App description and keywords

### Writing a compelling description
- Highlight unique features and benefits.
- Be specific about what the app does.
- Lead with the strongest selling point.
- If the app sells in-app purchases or subscriptions, say so clearly in the description, screenshots and previews (guideline 2.3.2).

### Keywords
- Think about the terms potential users would search for.
- Use App Store Optimization (ASO) tools such as AppTweak.
- Include relevant, specific keywords.
- Example for WeatherWiz: Weather, Storm Tracker, Radar, Forecast, Rain Alert

### Tips for screenshot text overlay
Overlay short text on screenshots to describe features:
- "Real-time storm alerts"
- "Track your daily progress"
- Keep it concise and action-oriented.

## 6. Metadata and Info.plist

### App Store Connect metadata
Limits from Apple's [app information](https://developer.apple.com/help/app-store-connect/reference/app-information/app-information) and [platform version information](https://developer.apple.com/help/app-store-connect/reference/app-information/platform-version-information) pages:

| Field | Limit | Required |
| --- | --- | --- |
| App name | 2-30 characters | Yes |
| Subtitle | 30 characters | No |
| Description | 4,000 characters | Yes |
| Keywords | 100 bytes | Yes |
| Promotional text | 170 characters | No |
| Support URL | | Yes |
| Privacy policy URL | | Yes, for iOS apps |
| Marketing URL | | No |
| Copyright | | Yes |
| What's New | 4,000 characters | From the second version on |

Category, age rating and screenshots are required too.

### Info.plist key settings
- CFBundleName: the app's name
- CFBundleShortVersionString: version number (for example "1.0")
- CFBundleVersion: build number (for example "1")
- Permission purpose strings: each one says specifically why the app needs that access.

### Permission description best practices

**Specific (accepted):**
```
NSCameraUsageDescription: "This app needs camera access to scan food items and track your calorie intake in real-time"
NSPhotoLibraryUsageDescription: "Access to your photo library allows you to upload progress photos for your fitness timeline"
```

**Too vague (rejected):**
```
NSCameraUsageDescription: "Camera access"
NSPhotoLibraryUsageDescription: "Photo access needed"
```

## 7. Policies and support URL

### Required policies
1. **Privacy policy.** Every iOS app needs one: a URL in App Store Connect and an easy-to-find link inside the app (guideline 5.1.1(i)). Generators such as Termly, PrivacyPolicies.com and Iubenda can write and host one.
2. **Terms & conditions.** The same tools generate them, usually bundled with the privacy policy.
3. **EULA.** Apple's standard EULA applies unless you add your own in App Store Connect.

### Where to link policies
- In the App Store description
- In the app's Settings screen
- On the paywall screen, if there is one. A subscription paywall without terms-of-use and privacy links is a common rejection.

### Support URL
- Required for every submission.
- A simple contact page is enough: Google Sites, Termly or any website builder.
- It must load and show contact information.

## 8. Pre-submission checklist

### Store requirements
- [ ] Built with Xcode 26 or later on the iOS 26 SDK or later
- [ ] Minimum deployment target is iOS 15 or later (Apple's rule is iOS 13; current Xcode starts at iOS 15)
- [ ] Age rating questionnaire answered (4+/9+/13+/16+/18+)
- [ ] App Privacy details completed, including third-party SDKs
- [ ] Privacy manifest declares approved reasons for every required-reason API
- [ ] EU trader status provided, if the app is distributed in the EU
- [ ] Accessibility Nutrition Labels, if used, claim only features you verified

### Testing
- [ ] Spend at least an hour testing the app deliberately
- [ ] Test all buttons and flows
- [ ] Test on both iPhone and iPad, if the app runs on iPad
- [ ] No crashes or blank screens
- [ ] All placeholder text removed
- [ ] Tested on a real device when possible

### App Store assets
- [ ] App icon meets Apple's specifications
- [ ] iPhone screenshots in the 6.9-inch class, for example 1320 x 2868 or 1290 x 2796 px
- [ ] iPad screenshots in the 13-inch class, 2064 x 2752 or 2048 x 2732 px, captured on iPad (not stretched)
- [ ] 1-10 screenshots per size that show the app as it really works

### Policies and legal
- [ ] Privacy policy created, hosted and entered in App Store Connect
- [ ] Terms & conditions created and hosted
- [ ] EULA chosen (Apple standard or custom)
- [ ] Policies linked in the App Store description
- [ ] Policies linked inside the app (Settings and paywall)

### Pricing transparency
- [ ] In-app purchases and any paywall disclosed in the description and screenshots
- [ ] Subscription pricing clearly shown

### Permissions
- [ ] Every purpose string says specifically why the access is needed
- [ ] No unused permissions requested

### Configuration
- [ ] Bundle identifier is unique and correct
- [ ] Version and build numbers are set correctly
- [ ] Signing is configured
- [ ] Support URL loads and shows contact information

### If login is required
- [ ] Demo account or demo mode described in the App Review notes
