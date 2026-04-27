# iOS SwiftUI Accessibility Analysis

Analyze only the `accessibility` domain. Never edit, write, delete, format, generate, or execute source/project files inside `projectPath`; read files only. Report storage is handled by the top-level analyzer.

## Inputs

- `projectPath`: Absolute path to the SwiftUI iOS project.
- `mode`: `full` or `budget`.
- `files`: SwiftUI `.swift` file inventory with relative paths, line-indexed text, and metrics.

If this domain reference is used standalone without a file inventory, perform read-only discovery: skip `node_modules`, `.build`, `.git`, `Pods`, `DerivedData`, `.swiftpm`, `build`, and `.xcodeproj` internals; collect `.swift` files; require at least one `import SwiftUI`.

## Finding Discipline

- Return concrete line-numbered findings only.
- Use `domain: "accessibility"` on every violation.
- Use relative `file_path` values from `projectPath`.
- Use the first offending line when a pattern spans multiple lines.
- Prefer actionable findings tied to a specific element, not general accessibility advice.
- In `budget` mode, omit `why_fix`, `fix_code`, and `auto_fixable`.

## Rule Table

### A11Y-UI-001 - Label meaningful images and icon buttons

- severity: `error`
- dimension: `ui`
- check: Flag `Image(systemName:)`, image-only `Button`, toolbar icon controls, or custom icon controls that lack a visible text label and lack `.accessibilityLabel(...)`.
- why: VoiceOver users need a meaningful name for non-text controls and images.
- correct code:

```swift
Button(action: close) {
    Image(systemName: "xmark")
}
.accessibilityLabel("Close")
```

- guideline_reference: `{ "label": "Apple Developer: accessibilityLabel", "url": "https://developer.apple.com/documentation/swiftui/view/accessibilitylabel(_:)" }`

### A11Y-UI-002 - Hide decorative imagery

- severity: `warning`
- dimension: `ui`
- check: Flag decorative `Image`, shape, divider, background, or icon-only ornament that lacks `.accessibilityHidden(true)` and would add noise to the accessibility tree.
- why: Decorative elements should not distract assistive technology users from meaningful content.
- correct code:

```swift
Image("backgroundPattern")
    .accessibilityHidden(true)
```

- guideline_reference: `{ "label": "Apple Developer: accessibilityHidden", "url": "https://developer.apple.com/documentation/swiftui/view/accessibilityhidden(_:)" }`

### A11Y-UI-003 - Combine related child elements

- severity: `warning`
- dimension: `ui`
- check: Flag rows, cards, or summary groups made from several `Text` and `Image` elements that should be announced as one logical element but omit `.accessibilityElement(children: .combine)`.
- why: Combining related children reduces repetitive navigation and gives users a coherent announcement.
- correct code:

```swift
HStack {
    Text(account.name)
    Text(account.balance)
}
.accessibilityElement(children: .combine)
```

- guideline_reference: `{ "label": "Apple Developer: accessibilityElement children combine", "url": "https://developer.apple.com/documentation/swiftui/accessibilitychildbehavior/combine" }`

### A11Y-UX-001 - Respect Reduce Motion

- severity: `warning`
- dimension: `ux`
- check: Flag significant animations, looping motion, parallax, matched-geometry transitions, or gesture-triggered movement that does not check `accessibilityReduceMotion` or provide a reduced-motion alternative.
- why: Motion-sensitive users can be harmed or disoriented by unnecessary animation.
- correct code:

```swift
@Environment(\.accessibilityReduceMotion) private var reduceMotion

withAnimation(reduceMotion ? nil : .spring()) {
    isExpanded.toggle()
}
```

- guideline_reference: `{ "label": "Apple Developer: accessibilityReduceMotion", "url": "https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion" }`

### A11Y-UX-002 - Add hints for non-obvious actions

- severity: `info`
- dimension: `ux`
- check: Flag custom gestures, ambiguous icon buttons, swipe-only controls, or unusual interactions that lack `.accessibilityHint(...)`.
- why: Hints explain what will happen when the result is not obvious from the label alone.
- correct code:

```swift
Button("Archive") {
    archive()
}
.accessibilityHint("Moves the message out of the inbox")
```

- guideline_reference: `{ "label": "Apple Developer: accessibilityHint", "url": "https://developer.apple.com/documentation/swiftui/view/accessibilityhint(_:)" }`

### A11Y-A11Y-001 - Add button traits to custom interactives

- severity: `error`
- dimension: `accessibility`
- check: Flag views with `.onTapGesture`, custom gesture recognizers, or manual hit testing that activate actions but omit `.accessibilityAddTraits(.isButton)`.
- why: Assistive technologies need the correct role to communicate that the element is actionable.
- correct code:

```swift
Text("Retry")
    .padding()
    .onTapGesture { retry() }
    .accessibilityAddTraits(.isButton)
```

- guideline_reference: `{ "label": "Apple Developer: accessibilityAddTraits", "url": "https://developer.apple.com/documentation/swiftui/view/accessibilityaddtraits(_:)" }`

### A11Y-A11Y-002 - Provide accessibilityValue for stateful controls

- severity: `warning`
- dimension: `accessibility`
- check: Flag custom sliders, progress indicators, rating controls, selection controls, counters, or stateful custom controls without `.accessibilityValue(...)`.
- why: The label names the control, while the value communicates its current state.
- correct code:

```swift
RatingView(value: rating)
    .accessibilityLabel("Rating")
    .accessibilityValue("\(rating) of 5")
```

- guideline_reference: `{ "label": "Apple Developer: accessibilityValue", "url": "https://developer.apple.com/documentation/swiftui/view/accessibilityvalue(_:)" }`

### A11Y-A11Y-003 - Notify assistive technology of screen changes

- severity: `warning`
- dimension: `accessibility`
- check: Flag custom routers, page replacements, onboarding step changes, or large content swaps that do not post screen-change or layout-change accessibility notifications.
- why: Assistive apps need explicit notification when the screen or layout changes outside normal system navigation.
- correct code:

```swift
AccessibilityNotification.ScreenChanged().post()
```

- guideline_reference: `{ "label": "Apple Developer: AccessibilityNotification", "url": "https://developer.apple.com/documentation/Accessibility/AccessibilityNotification" }`

## Operation

Given a list of `.swift` files, return a JSON array of violation objects matching the shared schema. Output only the JSON array, with no Markdown fences and no explanatory prose.
