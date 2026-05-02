---
corpus_version: development
domain: typography
platform: ios
last_reviewed: 2026-05-02
---

# iOS SwiftUI Typography Corpus

Canonical EvenBetter iOS corpus clauses for this conformance domain. Each H2 heading is a stable clause ID used by analyzer, validator, fixer, and benchmark outputs.

## TYPO-UI-001 - Prefer system text styles

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple HIG: Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
**Retrieved:** 2026-05-02

**Check.** Flag `Text` or label typography using fixed `.font(.system(size: ...))` for semantic content where a system text style such as `.title`, `.headline`, `.body`, `.caption`, or `.footnote` would preserve platform hierarchy.

**Why.** Apple typography guidance emphasizes legible hierarchy and platform text styles that adapt to context.

**Correct code.**

```swift
Text("Account")
    .font(.title2)
```

## TYPO-UI-002 - Use Font.custom relativeTo

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple Developer: Scaling Fonts Automatically](https://developer.apple.com/documentation/uikit/scaling-fonts-automatically#user-interface)
**Retrieved:** 2026-05-02

**Check.** Flag `Font.custom(_:size:)` or `.font(.custom(..., size: ...))` that lacks `relativeTo:` for user-facing text.

**Why.** Custom fonts need a text-style relationship to scale consistently with Dynamic Type.

**Correct code.**

```swift
Text("Balance")
    .font(.custom("BrandSans", size: 22, relativeTo: .title2))
```

## TYPO-UI-003 - Keep weight hierarchy meaningful

**Severity:** info
**Dimension:** ui
**Platform:** ios
**Source:** [Apple HIG: Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
**Retrieved:** 2026-05-02

**Check.** Flag dense view sections where many sibling `Text` views all use `.bold()`, `.fontWeight(.bold)`, `.fontWeight(.heavy)`, or `.fontWeight(.black)` without a clear semantic hierarchy.

**Why.** Overusing heavy weights weakens visual hierarchy and makes scanning harder.

**Correct code.**

```swift
VStack(alignment: .leading) {
    Text("Plan")
        .font(.headline)
    Text("Renews May 12")
        .font(.subheadline)
        .foregroundStyle(.secondary)
}
```

## TYPO-UX-001 - Avoid truncating important text

**Severity:** warning
**Dimension:** ux
**Platform:** ios
**Source:** [Apple Developer: Text Input and Output](https://developer.apple.com/documentation/swiftui/text-input-and-output)
**Retrieved:** 2026-05-02

**Check.** Flag `.lineLimit(1)` or restrictive `.lineLimit(...)` on user-generated, localized, instructional, title, error, or accessibility-relevant text without an evident expansion path.

**Why.** Fixed line limits can hide important content, especially with localization and larger text sizes.

**Correct code.**

```swift
Text(message)
    .font(.body)
    .fixedSize(horizontal: false, vertical: true)
```

## TYPO-UX-002 - Use line spacing intentionally

**Severity:** info
**Dimension:** ux
**Platform:** ios
**Source:** [Apple Developer: lineSpacing](https://developer.apple.com/documentation/swiftui/view/linespacing(_:))
**Retrieved:** 2026-05-02

**Check.** Flag body-length text blocks with `.lineSpacing(0)` or very large line spacing that harms readability; also flag long paragraphs with no explicit readable spacing when custom fonts are used.

**Why.** Comfortable line spacing improves comprehension in longer text and helps custom type feel native.

**Correct code.**

```swift
Text(articleSummary)
    .font(.body)
    .lineSpacing(4)
```

## TYPO-A11Y-001 - Do not render text below 11pt

**Severity:** error
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple HIG: Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
**Retrieved:** 2026-05-02

**Check.** Flag `.font(.system(size: n))`, `.custom(... size: n ...)`, or equivalent text sizing below 11 points for visible user-facing text.

**Why.** Very small text is difficult to read and conflicts with accessible legibility expectations.

**Correct code.**

```swift
Text("Updated now")
    .font(.caption)
```

## TYPO-A11Y-002 - Avoid fixed-height frames on Text

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple Developer: dynamicTypeSize](https://developer.apple.com/documentation/swiftui/view/dynamictypesize(_:))
**Retrieved:** 2026-05-02

**Check.** Flag `Text` with `.frame(height:)`, tight `.frame(maxHeight:)`, or parent containers that clip text at larger Dynamic Type sizes.

**Why.** Fixed vertical space can truncate text when users increase text size.

**Correct code.**

```swift
Text(settingsDescription)
    .font(.body)
    .fixedSize(horizontal: false, vertical: true)
```

## TYPO-A11Y-003 - Avoid hiding Dynamic Type with minimumScaleFactor

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple Developer: minimumScaleFactor](https://developer.apple.com/documentation/swiftui/view/minimumscalefactor(_:))
**Retrieved:** 2026-05-02

**Check.** Flag `.minimumScaleFactor(...)` below `0.8` on meaningful text, especially when combined with `.lineLimit(1)` or fixed frames.

**Why.** Shrinking text to fit can override the user's text-size preference and reduce readability.

**Correct code.**

```swift
Text(total)
    .font(.headline)
    .lineLimit(2)
```
