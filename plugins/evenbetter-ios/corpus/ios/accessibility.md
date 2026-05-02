---
corpus_version: development
domain: accessibility
platform: ios
last_reviewed: 2026-05-02
---

# iOS SwiftUI Accessibility Corpus

Canonical EvenBetter iOS corpus clauses for this conformance domain. Each H2 heading is a stable clause ID used by analyzer, validator, fixer, and benchmark outputs.

## A11Y-UI-001 - Label meaningful images and icon buttons

**Severity:** error
**Dimension:** ui
**Platform:** ios
**Source:** [Apple Developer: accessibilityLabel](https://developer.apple.com/documentation/swiftui/view/accessibilitylabel(_:))
**Retrieved:** 2026-05-02

**Check.** Flag `Image(systemName:)`, image-only `Button`, toolbar icon controls, or custom icon controls that lack a visible text label and lack `.accessibilityLabel(...)`.

**Why.** VoiceOver users need a meaningful name for non-text controls and images.

**Correct code.**

```swift
Button(action: close) {
    Image(systemName: "xmark")
}
.accessibilityLabel("Close")
```

## A11Y-UI-002 - Hide decorative imagery

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple Developer: accessibilityHidden](https://developer.apple.com/documentation/swiftui/view/accessibilityhidden(_:))
**Retrieved:** 2026-05-02

**Check.** Flag decorative `Image`, shape, divider, background, or icon-only ornament that lacks `.accessibilityHidden(true)` and would add noise to the accessibility tree.

**Why.** Decorative elements should not distract assistive technology users from meaningful content.

**Correct code.**

```swift
Image("backgroundPattern")
    .accessibilityHidden(true)
```

## A11Y-UI-003 - Combine related child elements

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple Developer: accessibilityElement children combine](https://developer.apple.com/documentation/swiftui/accessibilitychildbehavior/combine)
**Retrieved:** 2026-05-02

**Check.** Flag rows, cards, or summary groups made from several `Text` and `Image` elements that should be announced as one logical element but omit `.accessibilityElement(children: .combine)`.

**Why.** Combining related children reduces repetitive navigation and gives users a coherent announcement.

**Correct code.**

```swift
HStack {
    Text(account.name)
    Text(account.balance)
}
.accessibilityElement(children: .combine)
```

## A11Y-UX-001 - Respect Reduce Motion

**Severity:** warning
**Dimension:** ux
**Platform:** ios
**Source:** [Apple Developer: accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
**Retrieved:** 2026-05-02

**Check.** Flag significant animations, looping motion, parallax, matched-geometry transitions, or gesture-triggered movement that does not check `accessibilityReduceMotion` or provide a reduced-motion alternative.

**Why.** Motion-sensitive users can be harmed or disoriented by unnecessary animation.

**Correct code.**

```swift
@Environment(\.accessibilityReduceMotion) private var reduceMotion

withAnimation(reduceMotion ? nil : .spring()) {
    isExpanded.toggle()
}
```

## A11Y-UX-002 - Add hints for non-obvious actions

**Severity:** info
**Dimension:** ux
**Platform:** ios
**Source:** [Apple Developer: accessibilityHint](https://developer.apple.com/documentation/swiftui/view/accessibilityhint(_:))
**Retrieved:** 2026-05-02

**Check.** Flag custom gestures, ambiguous icon buttons, swipe-only controls, or unusual interactions that lack `.accessibilityHint(...)`.

**Why.** Hints explain what will happen when the result is not obvious from the label alone.

**Correct code.**

```swift
Button("Archive") {
    archive()
}
.accessibilityHint("Moves the message out of the inbox")
```

## A11Y-A11Y-001 - Add button traits to custom interactives

**Severity:** error
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple Developer: accessibilityAddTraits](https://developer.apple.com/documentation/swiftui/view/accessibilityaddtraits(_:))
**Retrieved:** 2026-05-02

**Check.** Flag views with `.onTapGesture`, custom gesture recognizers, or manual hit testing that activate actions but omit `.accessibilityAddTraits(.isButton)`.

**Why.** Assistive technologies need the correct role to communicate that the element is actionable.

**Correct code.**

```swift
Text("Retry")
    .padding()
    .onTapGesture { retry() }
    .accessibilityAddTraits(.isButton)
```

## A11Y-A11Y-002 - Provide accessibilityValue for stateful controls

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple Developer: accessibilityValue](https://developer.apple.com/documentation/swiftui/view/accessibilityvalue(_:))
**Retrieved:** 2026-05-02

**Check.** Flag custom sliders, progress indicators, rating controls, selection controls, counters, or stateful custom controls without `.accessibilityValue(...)`.

**Why.** The label names the control, while the value communicates its current state.

**Correct code.**

```swift
RatingView(value: rating)
    .accessibilityLabel("Rating")
    .accessibilityValue("\(rating) of 5")
```

## A11Y-A11Y-003 - Notify assistive technology of screen changes

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple Developer: AccessibilityNotification](https://developer.apple.com/documentation/Accessibility/AccessibilityNotification)
**Retrieved:** 2026-05-02

**Check.** Flag custom routers, page replacements, onboarding step changes, or large content swaps that do not post screen-change or layout-change accessibility notifications.

**Why.** Assistive apps need explicit notification when the screen or layout changes outside normal system navigation.

**Correct code.**

```swift
AccessibilityNotification.ScreenChanged().post()
```
