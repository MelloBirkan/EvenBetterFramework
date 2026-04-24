# iOS SwiftUI Components And Patterns Analysis

Analyze only the `components-patterns` domain. Never edit, write, delete, format, generate, or execute files inside `projectPath`; reads only.

## Inputs

- `projectPath`: Absolute path to the SwiftUI iOS project.
- `mode`: `full` or `budget`.
- `files`: SwiftUI `.swift` file inventory with relative paths, line-indexed text, and metrics.

If this domain reference is used standalone without a file inventory, perform read-only discovery: skip `node_modules`, `.build`, `.git`, `Pods`, `DerivedData`, `.swiftpm`, `build`, and `.xcodeproj` internals; collect `.swift` files; require at least one `import SwiftUI`.

## Finding Discipline

- Return concrete line-numbered findings only.
- Use `domain: "components-patterns"` on every violation.
- Use relative `file_path` values from `projectPath`.
- Use the first offending line when a pattern spans multiple lines.
- Do not flag custom components that wrap native controls correctly and expose equivalent accessibility semantics.
- In `budget` mode, omit `why_fix`, `fix_code`, and `auto_fixable`.

## Rule Table

### COMP-UI-001 - Prefer Button over onTapGesture for actions

- severity: `warning`
- dimension: `ui`
- check: Flag tappable `Text`, `Image`, `HStack`, `VStack`, `ZStack`, or custom rows using `.onTapGesture` for primary actions where `Button` would provide native behavior.
- why: `Button` provides platform styling, input behavior, accessibility traits, and activation semantics.
- correct code:

```swift
Button {
    save()
} label: {
    Label("Save", systemImage: "checkmark")
}
```

- guideline_reference: `{ "label": "Apple Developer: Button", "url": "https://developer.apple.com/documentation/swiftui/button" }`

### COMP-UI-002 - Use NavigationStack instead of NavigationView

- severity: `warning`
- dimension: `ui`
- check: Flag `NavigationView` in iOS SwiftUI code that can target modern navigation APIs.
- why: Apple recommends migrating to value-based `NavigationStack` and `NavigationSplitView` APIs for predictable modern navigation.
- correct code:

```swift
NavigationStack {
    SettingsView()
        .navigationTitle("Settings")
}
```

- guideline_reference: `{ "label": "Apple Developer: Migrating to New Navigation Types", "url": "https://developer.apple.com/documentation/swiftui/migrating-to-new-navigation-types" }`

### COMP-UI-003 - Use confirmationDialog instead of actionSheet

- severity: `warning`
- dimension: `ui`
- check: Flag `.actionSheet` usage.
- why: `confirmationDialog` is the modern SwiftUI API for presenting action choices in a platform-adaptive way.
- correct code:

```swift
.confirmationDialog("Choose an option", isPresented: $showOptions) {
    Button("Archive") { archive() }
    Button("Cancel", role: .cancel) {}
}
```

- guideline_reference: `{ "label": "Apple HIG: Action Sheets", "url": "https://developer.apple.com/design/human-interface-guidelines/action-sheets" }`

### COMP-UX-001 - Mark destructive buttons with role destructive

- severity: `error`
- dimension: `ux`
- check: Flag `Button` actions named or implemented as delete, remove, reset, discard, revoke, erase, or sign out when they omit `role: .destructive`.
- why: Destructive roles help the system present risk clearly and support safer user decisions.
- correct code:

```swift
Button("Delete Account", role: .destructive) {
    deleteAccount()
}
```

- guideline_reference: `{ "label": "Apple HIG: Buttons", "url": "https://developer.apple.com/design/human-interface-guidelines/buttons" }`

### COMP-UX-002 - Use alerts for high-consequence confirmations

- severity: `warning`
- dimension: `ux`
- check: Flag immediate destructive or irreversible actions without a nearby `.alert` confirmation or equivalent confirmation flow.
- why: Confirmations reduce accidental data loss and make destructive choices explicit.
- correct code:

```swift
.alert("Delete item?", isPresented: $showDeleteAlert) {
    Button("Delete", role: .destructive) { deleteItem() }
    Button("Cancel", role: .cancel) {}
}
```

- guideline_reference: `{ "label": "Apple HIG: Alerts", "url": "https://developer.apple.com/design/human-interface-guidelines/alerts" }`

### COMP-A11Y-001 - Prefer system controls over custom recreations

- severity: `warning`
- dimension: `accessibility`
- check: Flag custom toggles, sliders, steppers, segmented controls, tab controls, or pickers built from shapes and gestures when a native SwiftUI control would provide equivalent behavior.
- why: System controls inherit platform accessibility, focus, VoiceOver, localization, and interaction behavior.
- correct code:

```swift
Toggle("Notifications", isOn: $notificationsEnabled)
```

- guideline_reference: `{ "label": "Apple HIG: Components", "url": "https://developer.apple.com/design/human-interface-guidelines/components" }`

### COMP-A11Y-002 - Add button traits to custom buttons

- severity: `error`
- dimension: `accessibility`
- check: Flag custom interactive views that use gestures or custom hit testing as buttons but omit `.accessibilityAddTraits(.isButton)`.
- why: VoiceOver users need the correct role to understand that an element activates an action.
- correct code:

```swift
HStack {
    Image(systemName: "star")
    Text("Favorite")
}
.onTapGesture { favorite() }
.accessibilityElement(children: .combine)
.accessibilityAddTraits(.isButton)
```

- guideline_reference: `{ "label": "Apple Developer: accessibilityAddTraits", "url": "https://developer.apple.com/documentation/swiftui/view/accessibilityaddtraits(_:)" }`

## Operation

Given a list of `.swift` files, return a JSON array of violation objects matching the shared schema. Output only the JSON array, with no Markdown fences and no explanatory prose.
