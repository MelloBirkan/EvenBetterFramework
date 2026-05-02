---
corpus_version: development
domain: navigation-flow
platform: ios
last_reviewed: 2026-05-02
---

# iOS SwiftUI Navigation And Flow Corpus

Canonical EvenBetter iOS corpus clauses for this conformance domain. Each H2 heading is a stable clause ID used by analyzer, validator, fixer, and benchmark outputs.

## NAV-UI-001 - Choose NavigationStack or NavigationSplitView intentionally

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple Developer: NavigationSplitView](https://developer.apple.com/documentation/swiftui/navigationsplitview#this-page-requires-javascript)
**Retrieved:** 2026-05-02

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
**Retrieved:** 2026-05-02

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
**Source:** [Apple HIG: Navigation and Search](https://developer.apple.com/design/human-interface-guidelines/navigation-and-search)
**Retrieved:** 2026-05-02

**Check.** Flag `.navigationBarBackButtonHidden(true)` without a clearly equivalent custom back or close control.

**Why.** Removing the system back affordance can make navigation unpredictable and harder to recover from.

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
**Retrieved:** 2026-05-02

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
**Source:** [Apple HIG: Navigation and Search](https://developer.apple.com/design/human-interface-guidelines/navigation-and-search)
**Retrieved:** 2026-05-02

**Check.** Flag flows with more than three sequential push levels, nested `NavigationLink` chains, or route enums that imply deep drill-down without shortcuts or regrouping.

**Why.** Excessive depth makes it harder to understand location and return to important tasks.

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
**Source:** [Apple Developer: AccessibilityNotification](https://developer.apple.com/documentation/Accessibility/AccessibilityNotification)
**Retrieved:** 2026-05-02

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
**Source:** [Apple Developer: cancellationAction](https://developer.apple.com/documentation/swiftui/toolbaritemplacement/cancellationaction)
**Retrieved:** 2026-05-02

**Check.** Flag `.sheet`, `.fullScreenCover`, or modal-like overlays without a visible Cancel, Close, Done, or equivalent dismiss action when dismissal is not otherwise obvious.

**Why.** Modal flows need an accessible way to exit, especially for users who do not discover gestures.

**Correct code.**

```swift
.toolbar {
    ToolbarItem(placement: .cancellationAction) {
        Button("Cancel") { dismiss() }
    }
}
```
