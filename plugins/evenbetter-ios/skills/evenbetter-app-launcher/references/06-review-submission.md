# Phase 6 — App Review & Submission

## Table of Contents
1. Apple's Review Process
2. Review Timelines
3. Review Statuses
4. Common Rejection Reasons
5. How to Fix Rejections
6. Best Practices for Faster Approval
7. Expedited Reviews
8. After Approval

---

## 1. Apple's Review Process

Every app and every update goes through Apple's review. Apple checks that your app:
- Functions correctly
- Matches its App Store listing
- Follows App Store Review Guidelines
- Handles permissions and user data properly
- Does not crash or block core flows

This applies to: first-time submissions, version updates, and subscription/pricing changes requiring a new build.

### Apple's Key Review Areas

**Safety:** Apps must protect user data, handle it securely, encrypt data, obtain consent. Apps with user-generated content must have reporting and blocking mechanisms.

**Performance:** Apps must be complete and fully functional — no beta, demo, trial, or test versions. Must use Apple's public APIs only.

**Business:** Apps using in-app purchases, subscriptions, or monetization must comply with Apple's payment rules. Must comply with local laws.

**Design:** Intuitive, user-friendly interface following Apple's design standards. No spam or copycat apps.

**Legal:** Respect third-party IP rights. Provide clear information about data collection and usage.

**Privacy:** Provide a privacy policy. Obtain explicit consent before collecting personal data. Handle data securely.

## 2. Review Timelines

| Submission Type | Expected Timeline |
|---|---|
| First-time app | 24–72 hours |
| App updates | 12–48 hours |
| Metadata-only changes | Few hours, sometimes same-day |

Most apps are reviewed within **1–2 days**.

## 3. Review Statuses in App Store Connect

- **Prepare for Submission** — Build and metadata setup
- **Waiting for Review** — App is in Apple's queue
- **In Review** — App is actively being reviewed
- **Pending Developer Release** — Approved, waiting for manual release
- **Ready for Sale** — App is live
- **Rejected** — Changes are required

## 4. Common Rejection Reasons

### Top 3 Rejection Reasons

#### 1. Permission Problems (Info.plist / app.json)
When your app asks for device permissions (camera, photos, location) but doesn't clearly explain WHY. The description must be specific and thorough.

**Fix:** Navigate to Info.plist, find each permission key (NSCameraUsageDescription, etc.), and write a clear, specific explanation.

#### 2. Subscription / Paywall Issues
- Missing privacy policy, terms & conditions, or EULA links on the paywall
- Missing policy links in App Store description
- Not disclosing paywall existence in App Store description
- Hard paywall without disclosure

**Fix:** Add all policy links to both the paywall screen AND the App Store description. If using a hard paywall, explicitly mention it in the description.

#### 3. iPad Screenshot Issues
- Submitting stretched iPhone screenshots as iPad screenshots
- Apple will reject stretched/resized iPhone screenshots immediately

**Fix:** Use Xcode's iPad Simulator (12.9-inch) to capture real iPad screenshots at 2048 × 2732 px.

### Other Common Reasons Reviews Take Longer
- Missing or unclear permission descriptions
- App crashes or blank screens
- Login required without test credentials
- iPad support enabled but not properly handled
- Features shown in screenshots but not working
- App hangs on loading or requires unavailable backend

## 5. How to Fix Rejections

Rejections are **common and expected**, especially on first submissions.

### Process:
1. Read the rejection message carefully
2. Fix **only** what Apple mentions
3. Upload a new build or update metadata
4. Resubmit

Most apps are approved after **one follow-up submission**.

## 6. Best Practices for Faster Approval

- Test on a real device
- Make sure all buttons and flows work
- Avoid placeholder text or broken screens
- Add clear permission explanations
- If login required: provide demo credentials in App Review notes
- Ensure app works on both iPhone and iPad if both are enabled
- Don't include beta features or test data
- Make sure screenshots accurately represent the app

## 7. Expedited Reviews

Apple allows developers to request an expedited review in limited situations.

### When It's Appropriate
- Critical bug fixes affecting users
- Security or data issues
- Time-sensitive launches or events
- App blocked due to a major issue

### How to Request
1. Go to App Store Connect
2. Select your app
3. Open the submitted version
4. Click "Request Expedited Review"
5. Provide a clear, specific explanation

### What to Say
✅ "This build fixes a critical crash affecting all users."
✅ "This update resolves a blocking login issue."
✅ "This app supports a time-sensitive event."
❌ "We want it faster." (too vague)

### Timing
- If approved: review often happens within **24 hours**, sometimes same-day
- If denied: app remains in normal review queue

## 8. After Approval

Once approved, you can:
- **Release immediately** — goes live within a few hours
- **Schedule a release** — choose a specific date and time
- **Phased rollout** — gradually release to increasing percentage of users

Most apps appear on the App Store within a few hours after release.
