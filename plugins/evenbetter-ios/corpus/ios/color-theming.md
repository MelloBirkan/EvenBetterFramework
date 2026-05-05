---
corpus_version: development
domain: color-theming
platform: ios
last_reviewed: 2026-05-05
---

# iOS SwiftUI Color And Theming Corpus

Canonical EvenBetter iOS corpus clauses for this conformance domain. Each H2 heading is a stable clause ID used by analyzer, validator, fixer, and benchmark outputs.

## CLR-UI-001 - Prefer semantic system colors

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple HIG: Color](https://developer.apple.com/design/human-interface-guidelines/color)
**Retrieved:** 2026-05-02

**Check.** Flag literal RGB/hex color construction for standard surfaces, labels, fills, separators, or backgrounds where semantic colors would better adapt to system appearance.

**Why.** Semantic system colors adapt to light mode, dark mode, contrast settings, and platform conventions.

**Correct code.**

```swift
Text("Details")
    .foregroundStyle(.secondary)
```

## CLR-UI-002 - Avoid Color.black and Color.white for adaptive UI

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple Developer: Color](https://developer.apple.com/documentation/swiftui/color)
**Retrieved:** 2026-05-02

**Check.** Flag `Color.black`, `Color.white`, `.foregroundColor(.black)`, `.foregroundColor(.white)`, `.background(.black)`, or `.background(.white)` for primary UI text or surfaces unless explicitly part of fixed artwork.

**Why.** Absolute black and white often fail dark mode and high-contrast adaptation.

**Correct code.**

```swift
Text("Name")
    .foregroundStyle(.primary)
```

## CLR-UI-003 - Provide dark-mode asset variants

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple HIG: Color](https://developer.apple.com/design/human-interface-guidelines/color)
**Retrieved:** 2026-05-02

**Check.** Flag named brand/background colors used broadly in SwiftUI when the project contains asset catalogs but the referenced color asset appears to lack Any/Dark variants or equivalent appearance support.

**Why.** Asset colors should adapt across system appearances.

**Correct code.**

```swift
RoundedRectangle(cornerRadius: 8)
    .fill(Color("CardBackground"))
```

## CLR-UX-001 - Do not use color as the only indicator

**Severity:** warning
**Dimension:** ux
**Platform:** ios
**Source:** [Apple HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
**Retrieved:** 2026-05-05

**Check.** Flag status, selection, required fields, validation, or destructive states represented only by color changes without text, icon, shape, or accessibility value redundancy.

**Why.** iOS interfaces should not rely on color alone because users with color-vision differences, increased contrast settings, or unusual display conditions need redundant cues.

**Correct code.**

```swift
Label("Payment failed", systemImage: "exclamationmark.circle.fill")
    .foregroundStyle(.red)
```

## CLR-A11Y-001 - Maintain readable text contrast

**Severity:** error
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
**Retrieved:** 2026-05-05

**Check.** Flag visible text color/background pairs that are likely too low contrast for comfortable reading across system appearances and accessibility settings. Common examples include light gray text on white, secondary opacity text on tinted backgrounds, or low-alpha foregrounds over materials.

**Why.** Insufficient contrast prevents many users from reading text reliably.

**Correct code.**

```swift
Text("Due today")
    .foregroundStyle(.primary)
    .background(.regularMaterial)
```

## CLR-A11Y-002 - Avoid red/green as the only distinction

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
**Retrieved:** 2026-05-02

**Check.** Flag paired red/green success/failure, gain/loss, online/offline, or yes/no states without text labels, symbols, or shape differences.

**Why.** Red/green-only meaning is unreliable for users with common color-vision differences.

**Correct code.**

```swift
Label("Available", systemImage: "checkmark.circle.fill")
    .foregroundStyle(.green)
```
