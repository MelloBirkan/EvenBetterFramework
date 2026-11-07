# Phase 6: App Review and submission

## Table of contents
1. Apple's review process
2. Review timelines
3. Review statuses
4. Common rejection reasons
5. How to fix rejections
6. Best practices for faster approval
7. Expedited reviews
8. After approval

The Apple facts in this file were checked on 2026-11-07 against the pages linked next to them.

---

## 1. Apple's review process

Every app and every update goes through App Review. Apple checks that the app:
- Works correctly
- Matches its App Store listing
- Follows the [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- Handles permissions and user data properly
- Does not crash or block core flows

This applies to first submissions, version updates, and pricing or subscription changes that need a new build.

### Apple's key review areas

**Safety:** protect user data, handle it securely and get consent. Apps with user-generated content need reporting and blocking.

**Performance:** the app is complete and fully functional. Demos, betas and trial versions belong in TestFlight, not on the App Store. Use public APIs only.

**Business:** in-app purchases, subscriptions and other monetization follow Apple's payment rules and local law.

**Design:** an intuitive interface that follows Apple's design standards. No spam or copycat apps.

**Legal:** respect third-party IP and say clearly what data the app collects and how it is used.

**Privacy:** provide a privacy policy and get explicit consent before collecting personal data.

## 2. Review timelines

Apple's own figure ([App Review](https://developer.apple.com/distribute/app-review/)): "App Review works around the clock, typically reviewing at least 50% of submissions in less than 24 hours and 90% in less than 48 hours."

Apple publishes no separate figures for first submissions, updates or metadata-only changes. Plan release dates with at least two days of review time, plus a resubmission cycle for a first launch.

## 3. Review statuses in App Store Connect

From Apple's [app and submission statuses](https://developer.apple.com/help/app-store-connect/reference/app-information/app-and-submission-statuses) reference, the ones you will see most:

- **Prepare for Submission:** the version exists but its information is still being prepared
- **Waiting for Review:** Apple has the submission and has not started reviewing it
- **In Review:** App Review is reviewing the app
- **Pending Developer Release:** approved, waiting for you to release it
- **Processing for Distribution:** being processed, ready within 24 hours
- **Ready for Distribution:** approved and available (formerly "Ready for Sale")
- **Rejected:** the app was not accepted
- **Metadata Rejected:** App Review did not accept the metadata
- **Developer Rejected:** you removed the version from review

## 4. Common rejection reasons

Apple says that on average more than 40% of unresolved issues relate to guideline 2.1, App Completeness, which covers crashes, placeholder content, incomplete information and more ([App Review](https://developer.apple.com/distribute/app-review/)). Check those first.

These three come up often for first-time indie submissions:

#### 1. Permission problems (Info.plist, or app.json in Expo projects)
The app asks for camera, photos, location or another permission without saying specifically why.

**Fix:** open Info.plist, find each purpose string (`NSCameraUsageDescription` and so on) and write a clear, specific explanation of what the access is for.

#### 2. Subscription and paywall issues
- Privacy policy, terms of use or EULA links missing from the paywall
- Policy links missing from the App Store description
- In-app purchases or a hard paywall not disclosed in the description and screenshots (guideline 2.3.2)

**Fix:** add the policy links to the paywall and to the App Store description, and say plainly in the description which features need a purchase.

#### 3. iPad screenshot issues
iPhone screenshots stretched or resized to pass as iPad screenshots get rejected (guideline 2.3.3).

**Fix:** capture real iPad screenshots in a 13-inch iPad simulator, at 2064 x 2752 or 2048 x 2732 px.

### Other causes of rejections and delays
- App crashes or blank screens
- Login required without a demo account or demo mode
- iPad support enabled but the iPad layout not handled
- Features shown in screenshots that do not work
- The app hangs on loading or needs a backend App Review cannot reach
- A custom "rate us" prompt instead of the system review prompt (guideline 5.6.1)

## 5. How to fix rejections

Rejections are common, especially on a first submission.

### Process
1. Read the rejection message and the guideline it cites.
2. Fix what Apple mentions, and nothing unrelated in the same build.
3. Upload a new build or update the metadata.
4. Reply in App Store Connect if something needs explaining, then resubmit.

Most apps get approved after one follow-up submission.

## 6. Best practices for faster approval

- Test on a real device.
- Make sure every button and flow works.
- Remove placeholder text and broken screens.
- Write clear permission purpose strings.
- If the app needs a login, put a demo account or demo mode in the App Review notes.
- If iPad is enabled, make the app work properly on iPad.
- Leave out beta features and test data.
- Make the screenshots match the app.

## 7. Expedited reviews

Apple reviews some submissions faster when there are extenuating circumstances ([Request an expedited review](https://developer.apple.com/help/app-review/after-submitting-for-review/request-expedited-review)).

### When it is appropriate
- A critical bug fix
- A release timed to an event the app is directly associated with

Apple asks that expedite requests be kept for matters of genuine urgency.

### How to request
1. Submit the app for review in App Store Connect first. Only submissions already sent to App Review can be expedited.
2. Put the reason in the Notes field: the bug you are fixing, or the event, its date and how the app relates to it.
3. Open Apple's [Request an Expedited App Review](https://developer.apple.com/contact/app-store/?topic=expedite) form, select the app and platform, and submit.
4. App Review evaluates the request and expedites it as availability and demand allow.

For an event, schedule the release in App Store Connect ahead of time when you can.

### What to say
- Good: "This build fixes a crash on launch affecting all users of version 2.3."
- Good: "This update resolves a login failure that blocks every account."
- Good: "This app is the official companion for [event] on [date]."
- Too vague: "We want it faster."

If the request is not granted, the submission stays in the normal queue.

## 8. After approval

Choose the release option on the version page ([release options](https://developer.apple.com/help/app-store-connect/manage-your-apps-availability/select-an-app-store-version-release-option)):
- **Manually release this version:** you press release when ready.
- **Automatically release this version:** it goes out as soon as it is approved.
- **Automatically release after App Review, no earlier than a date and time:** a scheduled launch.
- **Phased release (updates only):** rolls an update out to automatic-update users over 7 days. See `references/08-post-launch.md`.

After a manual release, Apple says it may take up to 24 hours for the version to appear on the App Store.
