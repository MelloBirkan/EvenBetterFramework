---
name: eb-analyze-ios-navigation-flow
description: Read-only navigation and flow compliance analysis for iOS SwiftUI projects against Apple Human Interface Guidelines and SwiftUI navigation APIs.
---

# iOS SwiftUI Navigation And Flow Analysis

Analyze only the `navigation-flow` domain. Never edit, write, delete, format, generate, or execute files inside `projectPath`; reads only.

## Inputs

- `projectPath`: Absolute path to the SwiftUI iOS project.
- `mode`: `full` or `budget`.
- `files`: SwiftUI `.swift` file inventory with relative paths, line-indexed text, and metrics.

If this sub-skill is run standalone without a file inventory, perform read-only discovery: skip `node_modules`, `.build`, `.git`, `Pods`, `DerivedData`, `.swiftpm`, `build`, and `.xcodeproj` internals; collect `.swift` files; require at least one `import SwiftUI`.

## Finding Discipline

- Return concrete line-numbered findings only.
- Use `domain: "navigation-flow"` on every violation.
- Use relative `file_path` values from `projectPath`.
- Use the first offending line when a pattern spans multiple lines.
- Navigation depth and flow findings should be based on visible code structure, route enums, or repeated nested navigation calls, not speculation.
- In `budget` mode, omit `why_fix`, `fix_code`, and `auto_fixable`.

## Rule Table

### NAV-UI-001 - Choose NavigationStack or NavigationSplitView intentionally

- severity: `warning`
- dimension: `ui`
- check: Flag root iOS navigation that uses a single `NavigationStack` for an iPad-style sidebar/detail information architecture where `NavigationSplitView` would better match the content structure; also flag deprecated `NavigationView`.
- why: Modern SwiftUI navigation APIs provide better platform adaptation for stack and split-view flows.
- correct code:

```swift
NavigationSplitView {
    Sidebar()
} detail: {
    DetailView()
}
```

- guideline_reference: `{ "label": "Apple Developer: NavigationSplitView", "url": "https://developer.apple.com/documentation/swiftui/navigationsplitview#this-page-requires-javascript" }`

### NAV-UI-002 - Provide navigation titles

- severity: `warning`
- dimension: `ui`
- check: Flag top-level destinations inside `NavigationStack` or `NavigationSplitView` that omit `.navigationTitle(...)`.
- why: Navigation titles orient users and help clarify where they are in the app.
- correct code:

```swift
NavigationStack {
    ProfileView()
        .navigationTitle("Profile")
}
```

- guideline_reference: `{ "label": "Apple Developer: navigationTitle", "url": "https://developer.apple.com/documentation/swiftui/view/navigationtitle(_:)" }`

### NAV-UI-003 - Preserve the standard back button

- severity: `warning`
- dimension: `ui`
- check: Flag `.navigationBarBackButtonHidden(true)` without a clearly equivalent custom back or close control.
- why: Removing the system back affordance can make navigation unpredictable and harder to recover from.
- correct code:

```swift
DetailView()
    .navigationTitle("Details")
```

- guideline_reference: `{ "label": "Apple HIG: Navigation and Search", "url": "https://developer.apple.com/design/human-interface-guidelines/navigation-and-search" }`

### NAV-UX-001 - Present creation flows as sheets when appropriate

- severity: `info`
- dimension: `ux`
- check: Flag short-lived create, add, compose, edit, or filter flows pushed deeply onto a navigation stack when `.sheet` would better express a focused modal task.
- why: Modal presentation helps separate temporary creation tasks from hierarchical browsing.
- correct code:

```swift
.sheet(isPresented: $isComposing) {
    ComposeView()
}
```

- guideline_reference: `{ "label": "Apple HIG: Sheets", "url": "https://developer.apple.com/design/human-interface-guidelines/sheets" }`

### NAV-UX-002 - Avoid excessive navigation depth

- severity: `warning`
- dimension: `ux`
- check: Flag flows with more than three sequential push levels, nested `NavigationLink` chains, or route enums that imply deep drill-down without shortcuts or regrouping.
- why: Excessive depth makes it harder to understand location and return to important tasks.
- correct code:

```swift
NavigationStack(path: $path) {
    Overview()
        .navigationDestination(for: Route.self) { route in
            route.destination
        }
}
```

- guideline_reference: `{ "label": "Apple HIG: Navigation and Search", "url": "https://developer.apple.com/design/human-interface-guidelines/navigation-and-search" }`

### NAV-A11Y-001 - Announce major screen changes

- severity: `warning`
- dimension: `accessibility`
- check: Flag custom navigation, manual page swaps, onboarding steps, or wizard screens that replace most visible content without posting an accessibility screen-change notification or moving accessibility focus.
- why: Assistive technologies need notification when a new screen or major layout appears.
- correct code:

```swift
.onAppear {
    AccessibilityNotification.ScreenChanged().post()
}
```

- guideline_reference: `{ "label": "Apple Developer: AccessibilityNotification", "url": "https://developer.apple.com/documentation/Accessibility/AccessibilityNotification" }`

### NAV-A11Y-002 - Provide modal dismissal affordances

- severity: `error`
- dimension: `accessibility`
- check: Flag `.sheet`, `.fullScreenCover`, or modal-like overlays without a visible Cancel, Close, Done, or equivalent dismiss action when dismissal is not otherwise obvious.
- why: Modal flows need an accessible way to exit, especially for users who do not discover gestures.
- correct code:

```swift
.toolbar {
    ToolbarItem(placement: .cancellationAction) {
        Button("Cancel") { dismiss() }
    }
}
```

- guideline_reference: `{ "label": "Apple Developer: cancellationAction", "url": "https://developer.apple.com/documentation/swiftui/toolbaritemplacement/cancellationaction" }`

## Operation

Given a list of `.swift` files, return a JSON array of violation objects matching the shared schema. Output only the JSON array, with no Markdown fences and no explanatory prose.
