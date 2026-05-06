---
corpus_version: development
domain: layout-interaction
platform: ios
last_reviewed: 2026-05-05
---

# iOS SwiftUI Layout And Interaction Corpus

Canonical EvenBetter iOS corpus clauses for this conformance domain. Each H2 heading is a stable clause ID used by analyzer, validator, fixer, and benchmark outputs.

## LAY-UI-001 - Provide 44x44 point tap targets

**Severity:** error
**Dimension:** ui
**Platform:** ios
**Source:** [Apple HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
**Retrieved:** 2026-05-02

**Check.** Flag interactive views with `.frame(width:)`, `.frame(height:)`, icon-only buttons, or gesture targets whose visible or content shape area is under 44x44 points.

**Why.** Apple recommends comfortable hit targets so touch interactions are reliable.

**Correct code.**

```swift
Button(action: refresh) {
    Image(systemName: "arrow.clockwise")
        .frame(width: 44, height: 44)
}
```

## LAY-UI-002 - Respect safe areas

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple HIG: Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
**Retrieved:** 2026-05-02

**Check.** Flag broad `.ignoresSafeArea()` usage on interactive content, text, toolbars, forms, or scrollable primary content without compensating safe-area insets.

**Why.** Content that ignores safe areas can collide with device edges, sensors, system gestures, and bars.

**Correct code.**

```swift
ScrollView {
    content
}
.safeAreaInset(edge: .bottom) {
    checkoutBar
}
```

## LAY-UI-003 - Use ProgressView for loading states

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple Developer: ProgressView](https://developer.apple.com/documentation/swiftui/progressview)
**Retrieved:** 2026-05-02

**Check.** Flag loading booleans that show only blank space, disabled content, text like "Loading...", or custom spinners when `ProgressView` would communicate activity.

**Why.** Native progress indicators make waiting states recognizable and accessible.

**Correct code.**

```swift
if isLoading {
    ProgressView("Loading")
}
```

## LAY-UI-004 - Provide useful empty states

**Severity:** info
**Dimension:** ui
**Platform:** ios
**Source:** [Apple HIG: Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
**Retrieved:** 2026-05-02

**Check.** Flag list, grid, or search result views that render nothing when their data collection is empty and no placeholder, guidance, or recovery action is present.

**Why.** Empty states should orient users and explain what can happen next.

**Correct code.**

```swift
if items.isEmpty {
    ContentUnavailableView("No Items", systemImage: "tray")
} else {
    List(items) { item in
        ItemRow(item: item)
    }
}
```

## LAY-UX-001 - Confirm destructive choices

**Severity:** error
**Dimension:** ux
**Platform:** ios
**Source:** [Apple HIG: Action Sheets](https://developer.apple.com/design/human-interface-guidelines/action-sheets)
**Retrieved:** 2026-05-02

**Check.** Flag destructive actions that are triggered from regular buttons, swipe actions, menus, or gesture handlers without `.confirmationDialog`, `.alert`, undo, or an equivalent confirmation mechanism.

**Why.** Destructive actions need clear confirmation or recovery to prevent accidental loss.

**Correct code.**

```swift
.confirmationDialog("Delete this item?", isPresented: $confirmDelete) {
    Button("Delete", role: .destructive) { deleteItem() }
    Button("Cancel", role: .cancel) {}
}
```

## LAY-UX-002 - Use sensoryFeedback for meaningful state changes

**Severity:** info
**Dimension:** ux
**Platform:** ios
**Source:** [Apple Developer: sensoryFeedback](https://developer.apple.com/documentation/swiftui/view/sensoryfeedback(_:trigger:))
**Retrieved:** 2026-05-02

**Check.** Flag important success, selection, completion, or error transitions in highly interactive flows where no haptic or sensory feedback is provided and the project targets platforms supporting `.sensoryFeedback`.

**Why.** Subtle feedback can reinforce important state changes without requiring visual attention.

**Correct code.**

```swift
.sensoryFeedback(.success, trigger: didSave)
```

## LAY-UX-009 - Map sensoryFeedback variant to HIG haptic tier

**Severity:** info
**Dimension:** ux
**Platform:** ios
**Source:** [Apple HIG: Playing haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics)
**Retrieved:** 2026-05-06

**Check.** Flag `.sensoryFeedback` calls whose variant is not aligned with the HIG-defined tier for the event being signalled:

- Notification tier (`.success`, `.warning`, `.error`) for outcomes of significant tasks or actions.
- Impact tier (`.impact`, `.impact(weight:intensity:)`, `.impact(flexibility:intensity:)`) for collisions, snap-into-place metaphors, and physical impacts complementing visual motion.
- Selection tier (`.selection`) for changes to a UI element's value, not for notification outcomes.
- Change tier (`.increase`, `.decrease`, `.levelChange`, `.alignment`, `.pathComplete`, `.start`, `.stop`) for activity transitions and value-threshold crossings.

**Why.** Apple groups haptics into Notification, Impact, and Selection categories with documented meanings. Mixing tiers (using `.impact` for a save success, or `.success` for a slider tick) breaks the learned association between pattern and outcome and degrades recognizability.

**Correct code.**

```swift
view
    .sensoryFeedback(.success, trigger: didSave)         // notification tier
    .sensoryFeedback(.impact, trigger: collisionCount)   // impact tier
    .sensoryFeedback(.selection, trigger: selectedTab)   // selection tier
```

## LAY-A11Y-001 - Enforce 44x44 accessibility hit areas

**Severity:** error
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
**Retrieved:** 2026-05-05

**Check.** Flag accessibility elements with gesture or button behavior whose tappable area is less than 44x44 points, even if the visible icon appears adequate.

**Why.** Small targets are difficult for users with motor disabilities and conflict with iOS accessibility guidance for comfortable touch interaction.

**Correct code.**

```swift
Image(systemName: "xmark")
    .frame(width: 44, height: 44)
    .contentShape(Rectangle())
    .accessibilityLabel("Close")
```

## LAY-A11Y-002 - Keep accessible content inside safe areas

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple HIG: Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
**Retrieved:** 2026-05-02

**Check.** Flag focusable controls or essential text placed under unsafe edges, overlays, home indicator areas, or system bars.

**Why.** Users who rely on VoiceOver, Switch Control, or larger text need content to remain reachable and unobscured.

**Correct code.**

```swift
VStack {
    formContent
}
.safeAreaPadding()
```
