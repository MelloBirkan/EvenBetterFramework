# SwiftUI `.sensoryFeedback` variant mapping

Reference for `evenbetter-ios-haptics`. Maps every `SensoryFeedback` value to the HIG haptic tier it belongs to, with each value's availability, the four modifier overloads and a misuse example.

Cites: `HAPT-UX-001`, `HAPT-UX-002`, `LAY-UX-009`.

Contents:

- Platform availability
- HIG haptic tiers
- Variant to tier table
- Modifier shapes
- Mismatch flag (the LAY-UX-009 and HAPT-UX-001 case)
- Centralizing semantics (the HAPT-UX-002 case)
- Quick checklist for review

## Platform availability

The `SensoryFeedback` type and the `.sensoryFeedback` modifiers need iOS 17, iPadOS 17, Mac Catalyst 17, macOS 14, tvOS 17, visionOS 26 or watchOS 10. Two groups of values arrived later:

- `.pathComplete`: iOS 17.5, iPadOS 17.5, Mac Catalyst 17.5, macOS 14.5, watchOS 10.5.
- `.press(_:)`, `.release(_:)` and `.selection(_:)`, with their `PressFeedback`, `ReleaseFeedback` and `SelectionFeedback` values: iOS 26 and the matching 26 releases.

Gate those with `if #available` when the deployment target is lower. For targets below iOS 17, see the UIKit fallback section of `references/core-haptics-fallback.md`.

## HIG haptic tiers

Apple groups iPhone haptics into three tiers in [Playing haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics):

- Notification: the outcome of a significant task (success, warning, error).
- Impact: a physical metaphor, such as a collision or a snap into place.
- Selection: the value of a UI element is changing.

`SwiftUI.SensoryFeedback` adds change and activity values beyond the three classic tiers.

## Variant to tier table

### Notification tier

| Variant | Use for | HIG meaning |
| --- | --- | --- |
| `.success` | Task completed (save, send, deposit, unlock) | "A task or action has completed." |
| `.warning` | Task produced a non-blocking caveat | "A task or action has produced a warning of some kind." |
| `.error` | Task failed; recovery needed | "An error has occurred." |

### Impact tier

| Variant | Use for | Notes |
| --- | --- | --- |
| `.impact` | Generic physical impact or snap | Default impact; complements a visual collision or layout change. |
| `.impact(weight:intensity:)` | Tunable weight and intensity | `weight`: `.light`, `.medium`, `.heavy`. `intensity`: `0.0...1.0`. |
| `.impact(flexibility:intensity:)` | Soft or rigid material metaphor | `flexibility`: `.soft`, `.solid`, `.rigid`. `intensity`: `0.0...1.0`. |

### Selection tier

| Variant | Use for | Notes |
| --- | --- | --- |
| `.selection` | A UI element's value is changing (segmented control, picker tick, slider tick) | Not for navigation completion or task outcomes. |

### Change and activity values

These extend the three classic tiers. Use them for the transition each one describes, not as stand-ins for `.success` or `.selection`.

| Variant | Use for | Availability |
| --- | --- | --- |
| `.start` | An activity started. | iOS 17 |
| `.stop` | An activity stopped. | iOS 17 |
| `.alignment` | A dragged item aligns to a guide. | iOS 17 |
| `.increase` | An important value crossed a threshold upward. | iOS 17 |
| `.decrease` | An important value crossed a threshold downward. | iOS 17 |
| `.levelChange` | Movement between discrete pressure levels. | iOS 17 |
| `.pathComplete` | A drawn path completed or was recognized. | iOS 17.5 |

### Control press, release and value feedback (iOS 26)

These values match the feedback the system plays for its own controls. Use them in custom controls that should feel like the system ones, and only when the control has distinct touch-down, touch-up or value moments.

| Value | Members | Plays when |
| --- | --- | --- |
| `.press(_:)` with `PressFeedback` | `.button`, `.buttonIconOnly`, `.slider`, `.tab`, `.toggle` | The element is pressed (touch down). |
| `.release(_:)` with `ReleaseFeedback` | `.slider` | The element is released (touch up). |
| `.selection(_:)` with `SelectionFeedback` | `.minimum`, `.maximum`, `.on`, `.off` | The element's value changes, for example a slider reaching its end or a toggle switching. |

```swift
if #available(iOS 26, *) {
    CustomToggle(isOn: $isOn)
        .sensoryFeedback(trigger: isOn) { _, newValue in
            .selection(newValue ? .on : .off)
        }
} else {
    CustomToggle(isOn: $isOn)
        .sensoryFeedback(.selection, trigger: isOn)
}
```

## Modifier shapes

`.sensoryFeedback` has four overloads, all iOS 17. Pick the one that matches your trigger logic. `trigger` must be `Equatable` in each.

### 1. Plain: play on every change

```swift
ContentView()
    .sensoryFeedback(.selection, trigger: showAccessory)
```

Plays whenever `trigger` changes.

### 2. With `condition:`: play only on certain transitions

```swift
ContentView(phase: $phase)
    .sensoryFeedback(.selection, trigger: phase) { old, new in
        old == .inactive || new == .expanded
    }
```

Plays only when the closure returns `true`. The closure receives the old and new values.

### 3. Closure with no arguments: choose the variant from current state

```swift
ContentView(isExpanded: $isExpanded)
    .sensoryFeedback(trigger: isExpanded) {
        isExpanded ? .impact : nil
    }
```

Returns the `SensoryFeedback?` to play, or `nil` to play nothing.

### 4. Closure with old and new values: choose the variant per transition

```swift
ContentView(phase: $phase)
    .sensoryFeedback(trigger: phase) { old, new in
        switch (old, new) {
        case (.inactive, _): return .success
        case (_, .expanded): return .impact
        default: return nil
        }
    }
```

Use it when the haptic depends on where the value came from as well as where it went.

## Mismatch flag (the LAY-UX-009 and HAPT-UX-001 case)

The acceptance criterion: `.sensoryFeedback(.error)` triggered for a non-error event must be flagged.

### Bad: variant does not match event semantics

```swift
struct SaveButton: View {
    @State private var didSave = false

    var body: some View {
        Button("Save") { didSave = true }
            .sensoryFeedback(.error, trigger: didSave) // wrong: didSave is a success signal
    }
}
```

The user feels the system error pattern after a successful save, so the pattern they have learned stops meaning anything.

### Good: variant matches the event

```swift
struct SaveButton: View {
    @State private var saveCount = 0
    @State private var failureCount = 0

    var body: some View {
        Button("Save") {
            if performSave() {
                saveCount += 1
            } else {
                failureCount += 1
            }
        }
        .sensoryFeedback(.success, trigger: saveCount)
        .sensoryFeedback(.error, trigger: failureCount)
    }
}
```

`.success` plays on every successful save and `.error` only on a failure. Counters change on each event, whereas a `Bool` that stays `true` after the first save would never trigger again.

## Centralizing semantics (the HAPT-UX-002 case)

Define an `extension` so the same outcome plays the same haptic across every screen.

```swift
extension SensoryFeedback {
    static let taskCompleted: SensoryFeedback = .success
    static let taskFailed: SensoryFeedback = .error
    static let toggleFlipped: SensoryFeedback = .selection
    static let cardSnappedIntoPlace: SensoryFeedback = .impact(weight: .medium, intensity: 1)
}
```

Every call site uses `.taskCompleted` instead of `.success` directly. If the team later decides task completion should be `.impact(flexibility: .soft, intensity: 1)`, one line changes.

## Quick checklist for review

- [ ] The variant matches the HIG tier for the event (Notification, Impact, Selection or a change value).
- [ ] The trigger value changes only when the event happens, not on every render.
- [ ] No `.error`, `.success` or `.warning` reused for events that are not task outcomes.
- [ ] The same outcome maps to the same variant across the codebase.
- [ ] iOS 17.5 and iOS 26 values are gated when the deployment target is lower.
- [ ] Each haptic is paired with a visible UI change. See `references/accessibility-and-haptics.md`.
