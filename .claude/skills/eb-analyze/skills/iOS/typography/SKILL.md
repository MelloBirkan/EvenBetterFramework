---
name: eb-analyze-ios-typography
description: Read-only typography compliance analysis for iOS SwiftUI projects against Apple Human Interface Guidelines, SwiftUI text APIs, and WCAG accessibility expectations.
---

# iOS SwiftUI Typography Analysis

Analyze only the `typography` domain. Never edit, write, delete, format, generate, or execute files inside `projectPath`; reads only.

## Inputs

- `projectPath`: Absolute path to the SwiftUI iOS project.
- `mode`: `full` or `budget`.
- `files`: SwiftUI `.swift` file inventory with relative paths, line-indexed text, and metrics.

If this sub-skill is run standalone without a file inventory, perform the same read-only discovery as the top-level analyzer: skip `node_modules`, `.build`, `.git`, `Pods`, `DerivedData`, `.swiftpm`, `build`, and `.xcodeproj` internals; collect `.swift` files; require at least one `import SwiftUI`.

## Finding Discipline

- Return concrete line-numbered findings only.
- Use `domain: "typography"` on every violation.
- Use relative `file_path` values from `projectPath`.
- Use the first offending line when a pattern spans multiple lines.
- Prefer high-confidence static patterns over guesses about runtime text.
- In `budget` mode, omit `why_fix`, `fix_code`, and `auto_fixable`.

## Rule Table

### TYPO-UI-001 - Prefer system text styles

- severity: `warning`
- dimension: `ui`
- check: Flag `Text` or label typography using fixed `.font(.system(size: ...))` for semantic content where a system text style such as `.title`, `.headline`, `.body`, `.caption`, or `.footnote` would preserve platform hierarchy.
- why: Apple typography guidance emphasizes legible hierarchy and platform text styles that adapt to context.
- correct code:

```swift
Text("Account")
    .font(.title2)
```

- guideline_reference: `{ "label": "Apple HIG: Typography", "url": "https://developer.apple.com/design/human-interface-guidelines/typography" }`

### TYPO-UI-002 - Use Font.custom relativeTo

- severity: `warning`
- dimension: `ui`
- check: Flag `Font.custom(_:size:)` or `.font(.custom(..., size: ...))` that lacks `relativeTo:` for user-facing text.
- why: Custom fonts need a text-style relationship to scale consistently with Dynamic Type.
- correct code:

```swift
Text("Balance")
    .font(.custom("BrandSans", size: 22, relativeTo: .title2))
```

- guideline_reference: `{ "label": "Apple Developer: Scaling Fonts Automatically", "url": "https://developer.apple.com/documentation/uikit/scaling-fonts-automatically#user-interface" }`

### TYPO-UI-003 - Keep weight hierarchy meaningful

- severity: `info`
- dimension: `ui`
- check: Flag dense view sections where many sibling `Text` views all use `.bold()`, `.fontWeight(.bold)`, `.fontWeight(.heavy)`, or `.fontWeight(.black)` without a clear semantic hierarchy.
- why: Overusing heavy weights weakens visual hierarchy and makes scanning harder.
- correct code:

```swift
VStack(alignment: .leading) {
    Text("Plan")
        .font(.headline)
    Text("Renews May 12")
        .font(.subheadline)
        .foregroundStyle(.secondary)
}
```

- guideline_reference: `{ "label": "Apple HIG: Typography", "url": "https://developer.apple.com/design/human-interface-guidelines/typography" }`

### TYPO-UX-001 - Avoid truncating important text

- severity: `warning`
- dimension: `ux`
- check: Flag `.lineLimit(1)` or restrictive `.lineLimit(...)` on user-generated, localized, instructional, title, error, or accessibility-relevant text without an evident expansion path.
- why: Fixed line limits can hide important content, especially with localization and larger text sizes.
- correct code:

```swift
Text(message)
    .font(.body)
    .fixedSize(horizontal: false, vertical: true)
```

- guideline_reference: `{ "label": "Apple Developer: Text Input and Output", "url": "https://developer.apple.com/documentation/swiftui/text-input-and-output" }`

### TYPO-UX-002 - Use line spacing intentionally

- severity: `info`
- dimension: `ux`
- check: Flag body-length text blocks with `.lineSpacing(0)` or very large line spacing that harms readability; also flag long paragraphs with no explicit readable spacing when custom fonts are used.
- why: Comfortable line spacing improves comprehension in longer text and helps custom type feel native.
- correct code:

```swift
Text(articleSummary)
    .font(.body)
    .lineSpacing(4)
```

- guideline_reference: `{ "label": "Apple Developer: lineSpacing", "url": "https://developer.apple.com/documentation/swiftui/view/linespacing(_:)" }`

### TYPO-A11Y-001 - Do not render text below 11pt

- severity: `error`
- dimension: `accessibility`
- check: Flag `.font(.system(size: n))`, `.custom(... size: n ...)`, or equivalent text sizing below 11 points for visible user-facing text.
- why: Very small text is difficult to read and conflicts with accessible legibility expectations.
- correct code:

```swift
Text("Updated now")
    .font(.caption)
```

- guideline_reference: `{ "label": "Apple HIG: Typography", "url": "https://developer.apple.com/design/human-interface-guidelines/typography" }`

### TYPO-A11Y-002 - Avoid fixed-height frames on Text

- severity: `warning`
- dimension: `accessibility`
- check: Flag `Text` with `.frame(height:)`, tight `.frame(maxHeight:)`, or parent containers that clip text at larger Dynamic Type sizes.
- why: Fixed vertical space can truncate text when users increase text size.
- correct code:

```swift
Text(settingsDescription)
    .font(.body)
    .fixedSize(horizontal: false, vertical: true)
```

- guideline_reference: `{ "label": "Apple Developer: dynamicTypeSize", "url": "https://developer.apple.com/documentation/swiftui/view/dynamictypesize(_:)" }`

### TYPO-A11Y-003 - Avoid hiding Dynamic Type with minimumScaleFactor

- severity: `warning`
- dimension: `accessibility`
- check: Flag `.minimumScaleFactor(...)` below `0.8` on meaningful text, especially when combined with `.lineLimit(1)` or fixed frames.
- why: Shrinking text to fit can override the user's text-size preference and reduce readability.
- correct code:

```swift
Text(total)
    .font(.headline)
    .lineLimit(2)
```

- guideline_reference: `{ "label": "Apple Developer: minimumScaleFactor", "url": "https://developer.apple.com/documentation/swiftui/view/minimumscalefactor(_:)" }`

## Operation

Given a list of `.swift` files, return a JSON array of violation objects matching the shared schema. Output only the JSON array, with no Markdown fences and no explanatory prose.
