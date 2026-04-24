# iOS SwiftUI Layout And Interaction Analysis

Analyze only the `layout-interaction` domain. Never edit, write, delete, format, generate, or execute files inside `projectPath`; reads only.

## Inputs

- `projectPath`: Absolute path to the SwiftUI iOS project.
- `mode`: `full` or `budget`.
- `files`: SwiftUI `.swift` file inventory with relative paths, line-indexed text, and metrics.

If this domain reference is used standalone without a file inventory, perform read-only discovery: skip `node_modules`, `.build`, `.git`, `Pods`, `DerivedData`, `.swiftpm`, `build`, and `.xcodeproj` internals; collect `.swift` files; require at least one `import SwiftUI`.

## Finding Discipline

- Return concrete line-numbered findings only.
- Use `domain: "layout-interaction"` on every violation.
- Use relative `file_path` values from `projectPath`.
- Use the first offending line when a pattern spans multiple lines.
- Treat layout rules as findings only when the code strongly indicates visible UI risk.
- In `budget` mode, omit `why_fix`, `fix_code`, and `auto_fixable`.

## Rule Table

### LAY-UI-001 - Provide 44x44 point tap targets

- severity: `error`
- dimension: `ui`
- check: Flag interactive views with `.frame(width:)`, `.frame(height:)`, icon-only buttons, or gesture targets whose visible or content shape area is under 44x44 points.
- why: Apple recommends comfortable hit targets so touch interactions are reliable.
- correct code:

```swift
Button(action: refresh) {
    Image(systemName: "arrow.clockwise")
        .frame(width: 44, height: 44)
}
```

- guideline_reference: `{ "label": "Apple HIG: Accessibility", "url": "https://developer.apple.com/design/human-interface-guidelines/accessibility" }`

### LAY-UI-002 - Respect safe areas

- severity: `warning`
- dimension: `ui`
- check: Flag broad `.ignoresSafeArea()` usage on interactive content, text, toolbars, forms, or scrollable primary content without compensating safe-area insets.
- why: Content that ignores safe areas can collide with device edges, sensors, system gestures, and bars.
- correct code:

```swift
ScrollView {
    content
}
.safeAreaInset(edge: .bottom) {
    checkoutBar
}
```

- guideline_reference: `{ "label": "Apple HIG: Layout", "url": "https://developer.apple.com/design/human-interface-guidelines/layout" }`

### LAY-UI-003 - Use ProgressView for loading states

- severity: `warning`
- dimension: `ui`
- check: Flag loading booleans that show only blank space, disabled content, text like "Loading...", or custom spinners when `ProgressView` would communicate activity.
- why: Native progress indicators make waiting states recognizable and accessible.
- correct code:

```swift
if isLoading {
    ProgressView("Loading")
}
```

- guideline_reference: `{ "label": "Apple Developer: ProgressView", "url": "https://developer.apple.com/documentation/swiftui/progressview" }`

### LAY-UI-004 - Provide useful empty states

- severity: `info`
- dimension: `ui`
- check: Flag list, grid, or search result views that render nothing when their data collection is empty and no placeholder, guidance, or recovery action is present.
- why: Empty states should orient users and explain what can happen next.
- correct code:

```swift
if items.isEmpty {
    ContentUnavailableView("No Items", systemImage: "tray")
} else {
    List(items) { item in
        ItemRow(item: item)
    }
}
```

- guideline_reference: `{ "label": "Apple HIG: Layout", "url": "https://developer.apple.com/design/human-interface-guidelines/layout" }`

### LAY-UX-001 - Confirm destructive choices

- severity: `error`
- dimension: `ux`
- check: Flag destructive actions that are triggered from regular buttons, swipe actions, menus, or gesture handlers without `.confirmationDialog`, `.alert`, undo, or an equivalent confirmation mechanism.
- why: Destructive actions need clear confirmation or recovery to prevent accidental loss.
- correct code:

```swift
.confirmationDialog("Delete this item?", isPresented: $confirmDelete) {
    Button("Delete", role: .destructive) { deleteItem() }
    Button("Cancel", role: .cancel) {}
}
```

- guideline_reference: `{ "label": "Apple HIG: Action Sheets", "url": "https://developer.apple.com/design/human-interface-guidelines/action-sheets" }`

### LAY-UX-002 - Use sensoryFeedback for meaningful state changes

- severity: `info`
- dimension: `ux`
- check: Flag important success, selection, completion, or error transitions in highly interactive flows where no haptic or sensory feedback is provided and the project targets platforms supporting `.sensoryFeedback`.
- why: Subtle feedback can reinforce important state changes without requiring visual attention.
- correct code:

```swift
.sensoryFeedback(.success, trigger: didSave)
```

- guideline_reference: `{ "label": "Apple Developer: sensoryFeedback", "url": "https://developer.apple.com/documentation/swiftui/view/sensoryfeedback(_:trigger:)" }`

### LAY-A11Y-001 - Enforce 44x44 accessibility hit areas

- severity: `error`
- dimension: `accessibility`
- check: Flag accessibility elements with gesture or button behavior whose tappable area is less than 44x44 points, even if the visible icon appears adequate.
- why: Small targets are difficult for users with motor disabilities and conflict with accessible target-size guidance.
- correct code:

```swift
Image(systemName: "xmark")
    .frame(width: 44, height: 44)
    .contentShape(Rectangle())
    .accessibilityLabel("Close")
```

- guideline_reference: `{ "label": "WCAG 2.2: Target Size Minimum", "url": "https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html" }`

### LAY-A11Y-002 - Keep accessible content inside safe areas

- severity: `warning`
- dimension: `accessibility`
- check: Flag focusable controls or essential text placed under unsafe edges, overlays, home indicator areas, or system bars.
- why: Users who rely on VoiceOver, Switch Control, or larger text need content to remain reachable and unobscured.
- correct code:

```swift
VStack {
    formContent
}
.safeAreaPadding()
```

- guideline_reference: `{ "label": "Apple HIG: Layout", "url": "https://developer.apple.com/design/human-interface-guidelines/layout" }`

## Operation

Given a list of `.swift` files, return a JSON array of violation objects matching the shared schema. Output only the JSON array, with no Markdown fences and no explanatory prose.
