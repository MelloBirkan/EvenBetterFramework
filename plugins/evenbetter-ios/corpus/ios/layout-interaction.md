---
corpus_version: development
domain: layout-interaction
platform: ios
last_reviewed: 2026-11-07
---

# iOS SwiftUI Layout And Interaction Corpus

Canonical EvenBetter iOS corpus clauses for this conformance domain. Each H2 heading is a stable clause ID used by the analyze, validate and repair skills and by benchmark outputs.

## LAY-UI-001 - Provide 44x44 point tap targets

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility#Mobility)
**Retrieved:** 2026-11-07
**Standards note:** The WCAG cross-reference for target size is SC 2.5.8 Target Size (Minimum), Level AA (see LAY-A11Y-001). The 44 by 44 size matches SC 2.5.5 Target Size (Enhanced), which is Level AAA only.

**Check.** Flag interactive views with `.frame(width:)`, `.frame(height:)`, icon-only buttons, or gesture targets whose visible or content shape area is under 44x44 points but at least 28x28 points. Below 28x28 points, report LAY-A11Y-001 instead. Leave standard controls alone unless the code shrinks them, for example with a fixed frame or `.controlSize(.mini)`.

**Why.** Apple's accessibility guidance lists 44x44 pt as the default control size on iOS and iPadOS, and HIG Buttons says that as a general rule a button needs a hit region of at least 44x44 pt. A smaller target can still meet Apple's 28x28 pt minimum, but it is harder to hit reliably, so this is a conformance warning rather than a blocker.

**Correct code.**

```swift
Button(action: refresh) {
    Image(systemName: "arrow.clockwise")
        .frame(width: 44, height: 44)
        .contentShape(Rectangle())
}
.accessibilityLabel("Refresh")
```

## LAY-UI-002 - Respect safe areas

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple HIG: Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
**Retrieved:** 2026-11-07

**Check.** Flag broad `.ignoresSafeArea()` usage on interactive content, text, toolbars, forms, or scrollable primary content without compensating safe-area insets. Do not flag background images, colors, or materials: Apple's layout guidance asks for full-screen background content to extend under sidebars, toolbars, and tab bars.

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
**Retrieved:** 2026-11-07

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
**Source:** [Apple HIG: Writing](https://developer.apple.com/design/human-interface-guidelines/writing#Best-practices)
**Retrieved:** 2026-11-07

**Check.** Flag list, grid, or search result views that render nothing, or only a bare string, when their data collection is empty: no explanation of why the area is empty and no next step such as an add, retry, or clear-search action where one exists.

**Why.** Apple's writing guidance says an empty screen can be daunting when the next step isn't obvious, so tell people what they can do and give them a button or link when possible. Empty states are usually temporary, so keep crucial information out of them. The Tab bars guidance adds that an empty section should explain why its content is unavailable.

**Correct code.**

```swift
if items.isEmpty {
    ContentUnavailableView {
        Label("No Items", systemImage: "tray")
    } description: {
        Text("Items you add appear here.")
    } actions: {
        Button("Add Item") { addItem() }
    }
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
**Retrieved:** 2026-11-07

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
**Retrieved:** 2026-11-07

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
**Retrieved:** 2026-11-07

**Check.** Flag `.sensoryFeedback` calls whose variant is not aligned with the tier for the event being signalled:

- Notification tier (`.success`, `.warning`, `.error`) for the outcome of a task or action.
- Impact tier (`.impact`, `.impact(weight:intensity:)`, `.impact(flexibility:intensity:)`) for a physical metaphor that complements a visual experience, such as a view snapping into place or two objects colliding.
- Selection tier (`.selection`) while the value of a UI element changes, not for outcomes.
- Change tier (`.increase`, `.decrease`, `.levelChange`, `.alignment`, `.pathComplete`, `.start`, `.stop`) for activity transitions and value-threshold crossings. This tier is an EvenBetter grouping, not an iOS HIG category. Use each variant for the meaning its `SensoryFeedback` documentation gives, for example `.increase` when an important value rises above a significant threshold.

**Why.** The iOS HIG defines three haptic categories with documented meanings: notification for the outcome of a task or action, impact as a physical metaphor that complements a visual experience, and selection while a value is changing. Mixing tiers (using `.impact` for a save success, or `.success` for a slider tick) breaks the learned association between pattern and outcome.

**Correct code.**

```swift
view
    .sensoryFeedback(.success, trigger: didSave)         // notification tier
    .sensoryFeedback(.impact, trigger: collisionCount)   // impact tier
    .sensoryFeedback(.selection, trigger: selectedTab)   // selection tier
```

## LAY-A11Y-001 - Meet the 28x28 point minimum hit area

**Severity:** error
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility#Mobility)
**Retrieved:** 2026-11-07
**Standards note:** WCAG 2.2 SC 2.5.8 Target Size (Minimum), Level AA: targets of at least 24 by 24 CSS pixels, or enough spacing around smaller ones. SC 2.5.5 Target Size (Enhanced), 44 by 44 CSS pixels, is Level AAA.

**Check.** Flag accessibility elements with gesture or button behavior whose tappable area is under 28x28 points, the minimum control size Apple lists for iOS and iPadOS, even if the visible icon appears adequate. Targets from 28x28 points up to the 44x44 point default belong to LAY-UI-001.

**Why.** Controls that are too small are hard for many people to select, especially people with limited dexterity or mobility. Apple's accessibility guidance sets 28x28 pt as the minimum control size on iOS and iPadOS, and says spacing between controls matters as much as size: about 12 pt of padding around elements with a bezel and about 24 pt around elements without one.

**Correct code.**

```swift
Button(action: close) {
    Image(systemName: "xmark")
        .frame(width: 44, height: 44)
        .contentShape(Rectangle())
}
.accessibilityLabel("Close")
```

## LAY-A11Y-002 - Keep accessible content inside safe areas

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple HIG: Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
**Retrieved:** 2026-11-07

**Check.** Flag focusable controls or essential text placed under unsafe edges, overlays, home indicator areas, or system bars.

**Why.** Users who rely on VoiceOver, Switch Control, or larger text need content to remain reachable and unobscured.

**Correct code.**

```swift
VStack {
    formContent
}
.safeAreaPadding()
```
