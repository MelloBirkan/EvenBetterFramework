---
corpus_version: development
domain: typography
platform: ios
last_reviewed: 2026-11-07
---

# iOS SwiftUI Typography Corpus

Canonical EvenBetter iOS corpus clauses for this conformance domain. Each H2 heading is a stable clause ID used by the analyze, validate and repair skills and by benchmark outputs.

## TYPO-UI-001 - Prefer system text styles

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple HIG: Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
**Retrieved:** 2026-11-07

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
**Source:** [Apple Developer: Applying custom fonts to text](https://developer.apple.com/documentation/swiftui/applying-custom-fonts-to-text)
**Retrieved:** 2026-11-07

**Check.** Flag `Font.custom(_:size:)` or `.font(.custom(..., size: ...))` without `relativeTo:` on text whose role is not body text, such as titles, headlines, captions, and footnotes. Also flag `Font.custom(_:fixedSize:)` on user-facing text that should follow Dynamic Type.

**Why.** A custom font created with `custom(_:size:)` scales with Dynamic Type relative to the body text style. `relativeTo:` ties a title or caption to its own text style so it scales the way that style does, while `custom(_:fixedSize:)` does not scale at all.

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
**Retrieved:** 2026-11-07

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
**Source:** [Apple HIG: Typography](https://developer.apple.com/design/human-interface-guidelines/typography#Supporting-Dynamic-Type)
**Retrieved:** 2026-11-07

**Check.** Flag `.lineLimit(1)` or restrictive `.lineLimit(...)` on user-generated, localized, instructional, title, error, or accessibility-relevant text without an evident expansion path.

**Why.** Apple asks apps to keep text truncation to a minimum as font size increases, and to avoid truncating text in scrollable regions unless people can open a separate view to read the rest. Fixed line limits can hide important content, especially with localization and larger text sizes.

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
**Source:** [Apple HIG: Typography](https://developer.apple.com/design/human-interface-guidelines/typography#Using-system-fonts)
**Retrieved:** 2026-11-07

**Check.** Flag `.leading(.tight)` on text that can wrap to three or more lines, and long passages or wide text columns set in a custom font with no added `.lineSpacing`. Do not flag `.lineSpacing(0)`: it adds no space and matches the default.

**Why.** Apple's typography guidance says loose leading helps people keep their place in wide columns and long passages. Tight leading suits short text in height-constrained areas such as list rows, and Apple advises against it for three or more lines even there.

**Correct code.**

```swift
Text(articleBody)
    .font(.body.leading(.loose))

Text(articleBody)
    .font(.custom("BrandSerif", size: 17, relativeTo: .body))
    .lineSpacing(4)
```

## TYPO-A11Y-001 - Do not render text below 11pt

**Severity:** error
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple HIG: Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
**Retrieved:** 2026-11-07

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
**Source:** [Apple HIG: Layout](https://developer.apple.com/design/human-interface-guidelines/layout#Adaptability)
**Retrieved:** 2026-11-07

**Check.** Flag `Text` with `.frame(height:)`, tight `.frame(maxHeight:)`, or parent containers that clip text at larger Dynamic Type sizes.

**Why.** Apple's layout guidance says table rows and other containers may need to grow in height when people increase text size, so that text isn't cropped and doesn't overlap other content. Fixed vertical space prevents that and truncates the text.

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
**Retrieved:** 2026-11-07

**Check.** Flag `.minimumScaleFactor(...)` below `0.8` on meaningful text, especially when combined with `.lineLimit(1)` or fixed frames.

**Why.** Shrinking text to fit can override the user's text-size preference and reduce readability.

**Correct code.**

```swift
Text(total)
    .font(.headline)
    .lineLimit(2)
```

## TYPO-A11Y-004 - Do not cap primary text below AX3

**Severity:** error
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple App Store Connect Help: Larger Text evaluation criteria](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/larger-text-evaluation-criteria/)
**Retrieved:** 2026-11-07
**Standards note:** WCAG 2.2 SC 1.4.4 Resize Text, Level AA.

**Check.** Flag `.dynamicTypeSize(...)` ranges with an upper bound below `.accessibility3`, and fixed values such as `.dynamicTypeSize(.large)`, when they apply to an app or scene root, a navigation container, a `ScrollView` or `List`, or any view that holds body text. Caps on small repeated controls such as a tab bar or a badge belong to TYPO-A11Y-005 instead.

**Why.** Apple's Larger Text criteria allow the label only when people can enlarge text to at least 200 percent or the system maximum. Dynamic Type on iOS passes 200 percent at AX3 and goes over 300 percent for body text at AX5, so a cap below `.accessibility3` on primary content rules the label out. Zoom and Hover Text do not count toward it. Restack the layout at accessibility sizes instead of capping the text.

**Correct code.**

```swift
struct OrderTotal: View {
    let total: String
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize

    var body: some View {
        if dynamicTypeSize.isAccessibilitySize {
            VStack(alignment: .leading) {
                Text("Total")
                Text(total)
            }
        } else {
            HStack {
                Text("Total")
                Text(total)
            }
        }
    }
}
```

## TYPO-A11Y-005 - Show the Large Content Viewer for controls that stay small

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple Developer: accessibilityShowsLargeContentViewer()](https://developer.apple.com/documentation/swiftui/view/accessibilityshowslargecontentviewer())
**Retrieved:** 2026-11-07

**Check.** Flag custom tab bars, bottom toolbars, segmented bars, floating buttons and other controls that stay small at large text sizes, because they cap Dynamic Type with `.dynamicTypeSize(...)`, use a fixed `.font(.system(size:))` or size their icons with fixed frames, and that lack `.accessibilityShowsLargeContentViewer()` or `.accessibilityShowsLargeContentViewer { ... }`. Do not accept the viewer on body text or list rows, which should grow with Dynamic Type.

**Why.** Some controls stay small by design, like tab bar buttons that leave room for content. The Large Content Viewer shows an enlarged version of such a control to people who use large text sizes. Apple's Larger Text criteria point to it for elements like tab bars that do not grow, and the API documentation says views whose Dynamic Type size is constrained may need it. The same page warns against using it in place of Dynamic Type support. The modifier needs iOS 15 or later.

**Correct code.**

```swift
HStack {
    ForEach(tabs) { tab in
        Button {
            selection = tab
        } label: {
            Label(tab.title, systemImage: tab.symbol)
        }
        .accessibilityShowsLargeContentViewer()
    }
}
.dynamicTypeSize(...DynamicTypeSize.xxxLarge)
```

## TYPO-A11Y-006 - Offer a text size control in web views

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple App Store Connect Help: Larger Text evaluation criteria](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/larger-text-evaluation-criteria/)
**Retrieved:** 2026-11-07
**Standards note:** WCAG 2.2 SC 1.4.4 Resize Text, Level AA.

**Check.** Flag `WKWebView` (directly or inside a `UIViewRepresentable`) and SwiftUI `WebView` (iOS 26+) screens that show reading content in a common task when the app never sets `pageZoom`, injects no text-size CSS, offers no text size control and does not hand the page to Safari.

**Why.** Web pages do not always grow with Dynamic Type. Apple's Larger Text criteria ask apps that use a web view in a common task to provide a font size control or let Safari handle the page, the way Safari offers a text size per site. `WKWebView.pageZoom` (iOS 14+) scales the page content, the same as setting CSS `zoom` on all of it.

**Correct code.**

```swift
import SwiftUI
import WebKit

struct ArticleWebView: UIViewRepresentable {
    let url: URL
    let zoom: CGFloat // set from the app's text size control, for example 1.0 to 2.0

    func makeUIView(context: Context) -> WKWebView {
        let webView = WKWebView()
        webView.load(URLRequest(url: url))
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {
        webView.pageZoom = zoom
    }
}
```
