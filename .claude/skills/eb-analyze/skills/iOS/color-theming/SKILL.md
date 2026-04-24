---
name: eb-analyze-ios-color-theming
description: Read-only color and theming compliance analysis for iOS SwiftUI projects against Apple Human Interface Guidelines, SwiftUI color APIs, and WCAG 2.2 contrast requirements.
---

# iOS SwiftUI Color And Theming Analysis

Analyze only the `color-theming` domain. Never edit, write, delete, format, generate, or execute files inside `projectPath`; reads only.

## Inputs

- `projectPath`: Absolute path to the SwiftUI iOS project.
- `mode`: `full` or `budget`.
- `files`: SwiftUI `.swift` file inventory with relative paths, line-indexed text, and metrics.

If this sub-skill is run standalone without a file inventory, perform read-only discovery: skip `node_modules`, `.build`, `.git`, `Pods`, `DerivedData`, `.swiftpm`, `build`, and `.xcodeproj` internals; collect `.swift` files; require at least one `import SwiftUI`.

## Finding Discipline

- Return concrete line-numbered findings only.
- Use `domain: "color-theming"` on every violation.
- Use relative `file_path` values from `projectPath`.
- Use the first offending line when a pattern spans multiple lines.
- Flag contrast only when foreground/background evidence is visible in code or asset names make the risk clear.
- In `budget` mode, omit `why_fix`, `fix_code`, and `auto_fixable`.

## Rule Table

### CLR-UI-001 - Prefer semantic system colors

- severity: `warning`
- dimension: `ui`
- check: Flag literal RGB/hex color construction for standard surfaces, labels, fills, separators, or backgrounds where semantic colors would better adapt to system appearance.
- why: Semantic system colors adapt to light mode, dark mode, contrast settings, and platform conventions.
- correct code:

```swift
Text("Details")
    .foregroundStyle(.secondary)
```

- guideline_reference: `{ "label": "Apple HIG: Color", "url": "https://developer.apple.com/design/human-interface-guidelines/color" }`

### CLR-UI-002 - Avoid Color.black and Color.white for adaptive UI

- severity: `warning`
- dimension: `ui`
- check: Flag `Color.black`, `Color.white`, `.foregroundColor(.black)`, `.foregroundColor(.white)`, `.background(.black)`, or `.background(.white)` for primary UI text or surfaces unless explicitly part of fixed artwork.
- why: Absolute black and white often fail dark mode and high-contrast adaptation.
- correct code:

```swift
Text("Name")
    .foregroundStyle(.primary)
```

- guideline_reference: `{ "label": "Apple Developer: Color", "url": "https://developer.apple.com/documentation/swiftui/color" }`

### CLR-UI-003 - Provide dark-mode asset variants

- severity: `warning`
- dimension: `ui`
- check: Flag named brand/background colors used broadly in SwiftUI when the project contains asset catalogs but the referenced color asset appears to lack Any/Dark variants or equivalent appearance support.
- why: Asset colors should adapt across system appearances.
- correct code:

```swift
RoundedRectangle(cornerRadius: 8)
    .fill(Color("CardBackground"))
```

- guideline_reference: `{ "label": "Apple HIG: Color", "url": "https://developer.apple.com/design/human-interface-guidelines/color" }`

### CLR-UX-001 - Do not use color as the only indicator

- severity: `warning`
- dimension: `ux`
- check: Flag status, selection, required fields, validation, or destructive states represented only by color changes without text, icon, shape, or accessibility value redundancy.
- why: Users with color-vision differences or unusual display conditions need redundant cues.
- correct code:

```swift
Label("Payment failed", systemImage: "exclamationmark.circle.fill")
    .foregroundStyle(.red)
```

- guideline_reference: `{ "label": "WCAG 2.2: Use of Color", "url": "https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html" }`

### CLR-A11Y-001 - Meet WCAG AA text contrast

- severity: `error`
- dimension: `accessibility`
- check: Flag visible text color/background pairs that are likely below 4.5:1 for normal text or below 3:1 for large text. Common examples include light gray text on white, secondary opacity text on tinted backgrounds, or low-alpha foregrounds over materials.
- why: Insufficient contrast prevents many users from reading text reliably.
- correct code:

```swift
Text("Due today")
    .foregroundStyle(.primary)
    .background(.regularMaterial)
```

- guideline_reference: `{ "label": "WCAG 2.2: Contrast Minimum", "url": "https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html" }`

### CLR-A11Y-002 - Avoid red/green as the only distinction

- severity: `warning`
- dimension: `accessibility`
- check: Flag paired red/green success/failure, gain/loss, online/offline, or yes/no states without text labels, symbols, or shape differences.
- why: Red/green-only meaning is unreliable for users with common color-vision differences.
- correct code:

```swift
Label("Available", systemImage: "checkmark.circle.fill")
    .foregroundStyle(.green)
```

- guideline_reference: `{ "label": "Apple HIG: Accessibility", "url": "https://developer.apple.com/design/human-interface-guidelines/accessibility" }`

## Operation

Given a list of `.swift` files, return a JSON array of violation objects matching the shared schema. Output only the JSON array, with no Markdown fences and no explanatory prose.
