---
corpus_version: development
domain: color-theming
platform: ios
last_reviewed: 2026-11-07
---

# iOS SwiftUI Color And Theming Corpus

Canonical EvenBetter iOS corpus clauses for this conformance domain. Each H2 heading is a stable clause ID used by the analyze, validate and repair skills and by benchmark outputs.

## CLR-UI-001 - Prefer semantic system colors

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple HIG: Color](https://developer.apple.com/design/human-interface-guidelines/color)
**Retrieved:** 2026-11-07

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
**Retrieved:** 2026-11-07

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
**Retrieved:** 2026-11-07

**Check.** Flag named brand/background colors used broadly in SwiftUI when the project contains asset catalogs but the referenced color asset appears to lack Any/Dark variants or equivalent appearance support. Also flag custom color assets that have no High Contrast variant.

**Why.** Apple asks for every custom color to have light and dark variants, plus an increased contrast option for each. Apps that ship in a single appearance still need both light and dark colors, because Liquid Glass adapts to them.

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
**Retrieved:** 2026-11-07

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
**Retrieved:** 2026-11-07
**Standards note:** WCAG 2.2 SC 1.4.3 Contrast (Minimum), Level AA.

**Check.** Flag visible text color/background pairs that are likely too low contrast for comfortable reading across system appearances and accessibility settings. Accessibility Inspector applies WCAG AA values: 4.5:1 for text up to 17 pt, and 3:1 for text of 18 pt or larger and for bold text. Common examples include light gray text on white, secondary opacity text on tinted backgrounds, or low-alpha foregrounds over materials.

**Why.** Insufficient contrast prevents many users from reading text reliably. Apple asks apps to check contrast in both light and dark appearances, and, when the default colors fall short of these minimums, to at least offer a higher-contrast color scheme when Increase Contrast is on.

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
**Retrieved:** 2026-11-07

**Check.** Flag paired red/green or blue/orange success/failure, gain/loss, online/offline, or yes/no states without text labels, symbols, or shape differences.

**Why.** Apple names red-green and blue-orange as pairings that people who are color blind find hard to tell apart, and asks for shapes or icons in addition to color.

**Correct code.**

```swift
Label("Available", systemImage: "checkmark.circle.fill")
    .foregroundStyle(.green)
```

## CLR-A11Y-003 - Keep photos and video from inverting under Smart Invert

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple App Store Connect Help: Dark Interface evaluation criteria](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/dark-interface-evaluation-criteria/)
**Retrieved:** 2026-11-07

**Check.** Flag photos, user or remote images (`AsyncImage`, `Image(uiImage:)`), video views (`VideoPlayer`, `AVPlayerLayer` wrappers), camera previews and map snapshots that lack `.accessibilityIgnoresInvertColors()`. Symbols, icons and interface chrome should keep following Smart Invert.

**Why.** Some people with light sensitivity keep the screen dark with Smart Invert. Apple's Dark Interface criteria treat it as a last resort for a dark interface, and say that media colors must not appear inverted when it is on. A photo with inverted colors looks like a negative. `accessibilityIgnoresInvertColors(_:)` (iOS 14+) exempts a view from Smart Invert.

**Correct code.**

```swift
AsyncImage(url: photo.url) { image in
    image
        .resizable()
        .scaledToFill()
} placeholder: {
    ProgressView()
}
.accessibilityIgnoresInvertColors()
```
