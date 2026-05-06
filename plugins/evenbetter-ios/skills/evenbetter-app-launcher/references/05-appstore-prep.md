# Phase 5 — App Store Preparation

## Table of Contents
1. App Store Connect Setup
2. App Icon
3. Screenshots
4. App Description & Keywords
5. Metadata & Info.plist
6. Policies & Support URL
7. Pre-Submission Checklist

---

## 1. App Store Connect Setup

### Two Key Platforms
- **Apple Developer Portal:** Manage certificates, app IDs, provisioning profiles
- **App Store Connect:** Manage listings, analytics, financials, submissions

### Account Setup
- Understand roles: Admin, Developer, Marketing
- In "My Apps," add a new app with: name, primary language, category, age rating
- Set up pricing and availability

## 2. App Icon

### Design Principles
- First impression matters — it's the face of your app
- Must be visually appealing and relevant to your app's function
- Should stand out among other icons
- Follow Apple's icon specifications for dimensions and format

### Technical Requirements
- Single icon file in Assets.xcassets
- High resolution, no transparency
- No rounded corners (iOS applies them automatically)
- Avoid text in the icon (hard to read at small sizes)

## 3. Screenshots

### Why Screenshots Matter
Screenshots are one of the biggest drivers of installs. Most users decide to download based on the first few screenshots.

### Required Sizes

**iPhone (Portrait):**
- **1290 × 2796 px** (6.7-inch display) — RECOMMENDED
- Aspect ratio: 9:16
- This size covers iPhone 14/15/16 Pro Max and all smaller phones

**iPad (Portrait):**
- **2048 × 2732 px** (12.9-inch iPad)
- Aspect ratio: 4:3
- Required if your app supports iPad

### ⚠️ CRITICAL: NEVER stretch iPhone screenshots for iPad
This is an instant rejection. iPad screenshots must be real iPad screenshots captured from an iPad simulator or device.

### Screenshot Strategy
1. Screenshot 1: Core value proposition
2. Screenshots 2–3: Main features
3. Screenshots 4–5: Differentiation, results, or use cases
4. Keep text minimal and readable on small screens
5. Need 3–10 screenshots total

### How to Capture Screenshots

**iPhone:**
1. Open iOS Simulator in Xcode
2. Choose a 6.7-inch Pro Max device
3. Capture in portrait mode (Cmd+S in Simulator)

**iPad:**
1. Open iPad Simulator in Xcode
2. Choose 12.9-inch iPad
3. Capture in portrait mode

### Design Tools
- **Canva (Recommended):** Search "App Store Screenshot," choose iPhone (9:16) or iPad (4:3) template
- **Screenshots Pro:** Device frames, consistent layouts, batch export
- **Figma:** Full design control
- **iOS Simulator:** Best for raw captures

### Export Guidelines
- Format: PNG
- No compression
- Keep text within safe margins
- High contrast and readable fonts

### Common Mistakes
- Wrong dimensions or aspect ratio
- Missing iPad screenshots when iPad is supported
- Text too small to read
- Overcrowded designs
- Stretched iPhone screenshots for iPad

## 4. App Description & Keywords

### Writing a Compelling Description
- Highlight unique features and benefits
- Be specific about what the app does
- Lead with the most compelling selling point
- If you have a paywall: MUST disclose this in the description

### Keywords
- Think about terms potential users would search
- Use App Store Optimization (ASO) tools like AppTweak
- Include relevant, specific keywords
- Example for WeatherWiz: Weather, Storm Tracker, Radar, Forecast, Rain Alert

### Tips for Screenshots Text Overlay
Consider adding overlay text on screenshots to describe features:
- "Real-time storm alerts"
- "Track your daily progress"
- Keep it concise and action-oriented

## 5. Metadata & Info.plist

### Required Metadata in App Store Connect
- App name
- Subtitle
- Category and subcategory
- Keywords (up to 100 characters)
- Description
- Promotional text
- Support URL
- Marketing URL (optional)

### Info.plist Critical Settings
- CFBundleName: Your app's name
- CFBundleShortVersionString: Version number (e.g., "1.0")
- CFBundleVersion: Build number (e.g., "1")
- **Permission descriptions: Must clearly explain WHY each permission is needed**

### Permission Description Best Practices

✅ **GOOD (will be accepted):**
```
NSCameraUsageDescription: "This app needs camera access to scan food items and track your calorie intake in real-time"
NSPhotoLibraryUsageDescription: "Access to your photo library allows you to upload progress photos for your fitness timeline"
```

❌ **BAD (will be rejected):**
```
NSCameraUsageDescription: "Camera access"
NSPhotoLibraryUsageDescription: "Photo access needed"
```

## 6. Policies & Support URL

### Required Policies
1. **Privacy Policy** — Generate with Termly (recommended)
2. **Terms & Conditions** — Generate with same tool
3. **EULA** — Use Apple's Standard EULA

### Where to Link Policies
- In the App Store description
- In the app's Settings screen
- On the Paywall screen (if applicable)

### Support URL
- Required for App Store submission
- Create a simple contact page using: Google Sites, Termly, or any website builder
- Must be a working URL with contact information

## 7. Pre-Submission Checklist

### Testing
- [ ] Test app thoroughly for at least 1 hour
- [ ] Test all buttons and flows
- [ ] Test on both iPhone and iPad (if supported)
- [ ] Ensure no crashes or blank screens
- [ ] Verify all placeholder text is removed
- [ ] Test on real device when possible

### App Store Assets
- [ ] App icon meets Apple's specifications
- [ ] iPhone screenshots: 1290 × 2796 px (PNG)
- [ ] iPad screenshots: 2048 × 2732 px (real iPad screenshots, not stretched!)
- [ ] 3–10 screenshots that accurately showcase functionality

### Policies & Legal
- [ ] Privacy policy created and hosted
- [ ] Terms & conditions created and hosted
- [ ] EULA selected (Apple Standard or custom)
- [ ] All policies linked in App Store description
- [ ] All policies linked inside the app (Settings + Paywall)

### Pricing Transparency
- [ ] If paywall exists, disclosed in App Store description
- [ ] Subscription pricing clearly shown

### Permissions
- [ ] All permission descriptions clearly explain WHY they're needed
- [ ] No unused permissions requested

### Configuration
- [ ] Bundle identifier is unique and correct
- [ ] Version and build numbers are set correctly
- [ ] Signing certificates are configured
- [ ] Support URL is working and accessible

### If Login Required
- [ ] Provide demo/test credentials in App Review notes
