---
corpus_version: development
domain: navigation-flow
platform: ios
last_reviewed: 2026-11-07
---

# iOS SwiftUI Navigation And Flow Corpus

Canonical EvenBetter iOS corpus clauses for this conformance domain. Each H2 heading is a stable clause ID used by the analyze, validate and repair skills and by benchmark outputs.

## NAV-UI-001 - Choose NavigationStack or NavigationSplitView intentionally

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple Developer: NavigationSplitView](https://developer.apple.com/documentation/swiftui/navigationsplitview)
**Retrieved:** 2026-11-07

**Check.** Flag root iOS navigation that uses a single `NavigationStack` for an iPad-style sidebar/detail information architecture where `NavigationSplitView` would better match the content structure; also flag deprecated `NavigationView`.

**Why.** Modern SwiftUI navigation APIs provide better platform adaptation for stack and split-view flows.

**Correct code.**

```swift
NavigationSplitView {
    Sidebar()
} detail: {
    DetailView()
}
```

## NAV-UI-002 - Provide navigation titles

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple Developer: navigationTitle](https://developer.apple.com/documentation/swiftui/view/navigationtitle(_:))
**Retrieved:** 2026-11-07

**Check.** Flag top-level destinations inside `NavigationStack` or `NavigationSplitView` that omit `.navigationTitle(...)`.

**Why.** Navigation titles orient users and help clarify where they are in the app.

**Correct code.**

```swift
NavigationStack {
    ProfileView()
        .navigationTitle("Profile")
}
```

## NAV-UI-003 - Preserve the standard back button

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple HIG: Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars#Navigation)
**Retrieved:** 2026-11-07

**Check.** Flag `.navigationBarBackButtonHidden(true)` without a clearly equivalent custom back or close control. Also flag custom back controls that look or behave differently from the system one, such as a text label that says "Back" in place of the standard chevron.

**Why.** People know that the standard Back button retraces their steps through a hierarchy. Apple's toolbar guidance asks for the standard Back and Close buttons, and for any custom version to look the same, behave as people expect, and be used consistently. Removing the system back affordance can make navigation unpredictable and harder to recover from.

**Correct code.**

```swift
DetailView()
    .navigationTitle("Details")
```

## NAV-UX-001 - Present creation flows as sheets when appropriate

**Severity:** info
**Dimension:** ux
**Platform:** ios
**Source:** [Apple HIG: Sheets](https://developer.apple.com/design/human-interface-guidelines/sheets)
**Retrieved:** 2026-11-07

**Check.** Flag short-lived create, add, compose, edit, or filter flows pushed deeply onto a navigation stack when `.sheet` would better express a focused modal task.

**Why.** Modal presentation helps separate temporary creation tasks from hierarchical browsing.

**Correct code.**

```swift
.sheet(isPresented: $isComposing) {
    ComposeView()
}
```

## NAV-UX-002 - Avoid excessive navigation depth

**Severity:** warning
**Dimension:** ux
**Platform:** ios
**Source:** [Apple HIG: Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles#Simplicity)
**Retrieved:** 2026-11-07

**Check.** Flag flows with more than three sequential push levels, nested `NavigationLink` chains, or route enums that imply deep drill-down without shortcuts or regrouping.

**Why.** Apple's design principles ask for an interface that is logically organized and straightforward to navigate, with a consistent structure that helps people understand where they are and what comes next. Deep drill-down makes location harder to track and important tasks harder to return to. Apple sets no push-level limit: the three-level threshold is an EvenBetter heuristic, and the usual fixes are regrouping into tabs or a sidebar, or a navigation path the app can reset to its root.

**Correct code.**

```swift
NavigationStack(path: $path) {
    Overview()
        .navigationDestination(for: Route.self) { route in
            route.destination
        }
}
```

## NAV-A11Y-001 - Announce major screen changes

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple Developer: AccessibilityNotification](https://developer.apple.com/documentation/accessibility/accessibilitynotification)
**Retrieved:** 2026-11-07

**Check.** Flag custom navigation, manual page swaps, onboarding steps, or wizard screens that replace most visible content without posting an accessibility screen-change notification or moving accessibility focus.

**Why.** Assistive technologies need notification when a new screen or major layout appears.

**Correct code.**

```swift
.onAppear {
    AccessibilityNotification.ScreenChanged().post()
}
```

## NAV-A11Y-002 - Provide modal dismissal affordances

**Severity:** error
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple HIG: Sheets](https://developer.apple.com/design/human-interface-guidelines/sheets)
**Retrieved:** 2026-11-07

**Check.** Flag `.sheet`, `.fullScreenCover`, or modal-like overlays without a visible Cancel, Close, Done, or equivalent dismiss action when dismissal is not otherwise obvious. Also flag sheets whose only way out is a Done button: Apple asks for Done to be paired with Cancel, or with Back in a multistep sheet.

**Why.** Modal flows need an accessible way to exit, especially for users who do not discover the swipe-to-dismiss gesture. In Apple's sheet guidance, Cancel (or Close) dismisses without saving and Done dismisses after the task is complete. A sheet that offers only Done implies that finishing the task is the only way out.

**Correct code.**

```swift
.toolbar {
    ToolbarItem(placement: .cancellationAction) {
        Button("Cancel") { dismiss() }
    }
    ToolbarItem(placement: .confirmationAction) {
        Button("Done") {
            save()
            dismiss()
        }
    }
}
```

## NAV-A11Y-003 - Keep VoiceOver inside custom modal overlays

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple App Store Connect Help: VoiceOver evaluation criteria](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/voiceover-evaluation-criteria/)
**Retrieved:** 2026-11-07
**Standards note:** WCAG 2.2 SC 2.4.3 Focus Order, Level A.

**Check.** Flag custom dialogs, pop-ups, bottom panels and full-screen overlays built with a `ZStack`, `.overlay` or a conditional view instead of `.sheet`, `.fullScreenCover`, `.alert`, `.confirmationDialog` or `.popover`, when the overlay lacks `.accessibilityAddTraits(.isModal)` or has no `.accessibilityAction(.escape)` that dismisses it.

**Why.** While a custom overlay is up, VoiceOver can still move to the screen behind it unless the overlay is marked modal. Apple's VoiceOver criteria ask that inactive content behind a modal view stay out of reach, and that people can dismiss the modal with the escape action. With the `.isModal` trait, assistive technologies ignore sibling elements that are not modal while the overlay is visible.

**Correct code.**

```swift
ZStack {
    content
    if isShowingPicker {
        ColorPickerPanel(selection: $color, onDone: { isShowingPicker = false })
            .accessibilityAddTraits(.isModal)
            .accessibilityAction(.escape) { isShowingPicker = false }
    }
}
```
