# SwiftUI `.sensoryFeedback` variant mapping

Reference for `evenbetter-ios-haptics`. Maps every `SensoryFeedback` static and overload to the HIG haptic tier it belongs to, plus three modifier shapes and a misuse example.

Cites: `HAPT-UX-001`, `HAPT-UX-002`, `LAY-UX-009`.

## Platform availability

`.sensoryFeedback` requires iOS 17, iPadOS 17, Mac Catalyst 17, macOS 14, tvOS 17, visionOS 26, watchOS 10. For earlier targets, see [`core-haptics-fallback.md`](core-haptics-fallback.md) (UIKit fallback section).

## HIG haptic tiers

Apple groups iPhone haptics into three tiers in [Playing haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics):

- **Notification** — outcomes of significant tasks (success / warning / error).
- **Impact** — physical metaphor; collisions and snap-into-place.
- **Selection** — value-of-a-UI-element changes.

`SwiftUI.SensoryFeedback` exposes additional change/activity variants beyond the three classic tiers.

## Variant → tier table

### Notification tier

| Variant | Use for | HIG meaning |
| --- | --- | --- |
| `.success` | Task completed (save, send, deposit, unlock) | "A task or action has completed." |
| `.warning` | Task produced a non-blocking caveat | "A task or action has produced a warning of some kind." |
| `.error` | Task failed; recovery needed | "An error has occurred." |

### Impact tier

| Variant | Use for | Notes |
| --- | --- | --- |
| `.impact` | Generic physical impact / snap | Default impact; complements a visual collision or layout change. |
| `.impact(weight:intensity:)` | Tunable weight/intensity impact | `weight`: `.light`, `.medium`, `.heavy`. `intensity`: `0.0…1.0`. |
| `.impact(flexibility:intensity:)` | Soft/rigid material metaphor | `flexibility`: `.soft`, `.solid`, `.rigid`. `intensity`: `0.0…1.0`. |

### Selection tier

| Variant | Use for | Notes |
| --- | --- | --- |
| `.selection` | UI element value is changing (segmented control, picker tick, slider tick) | Not for navigation completion or task outcomes. |

### Change / activity tier

These extend the three classic tiers; use them for the specific transitions they describe rather than substituting them for `.success` or `.selection`.

| Variant | Use for |
| --- | --- |
| `.start` | An activity started. |
| `.stop` | An activity stopped. |
| `.alignment` | Dragged item aligns to a guide. |
| `.increase` | Important value crossed a threshold upward. |
| `.decrease` | Important value crossed a threshold downward. |
| `.levelChange` | Movement between discrete pressure levels. |
| `.pathComplete` | Drawn path completed or recognized. |

### Press / release composition

`.press(_:)`, `.release(_:)`, and `.selection(_:)` accept `PressFeedback`, `ReleaseFeedback`, and `SelectionFeedback` builders for elements that need separate feedback on touch-down vs touch-up. Reach for these only when a control has distinct press and release moments worth distinguishing.

## Modifier shapes

`.sensoryFeedback` ships three overloads. Pick the one that matches your trigger logic.

### 1. Plain — fire on every change

```swift
ContentView()
    .sensoryFeedback(.selection, trigger: showAccessory)
```

Plays whenever `trigger` changes. `trigger` must be `Equatable`.

### 2. With `condition:` — fire only on certain transitions

```swift
ContentView(phase: $phase)
    .sensoryFeedback(.selection, trigger: phase) { old, new in
        old == .inactive || new == .expanded
    }
```

Plays only when the closure returns `true`. The closure receives the old and new values.

### 3. Closure-returning — choose the variant per transition

```swift
ContentView(isExpanded: $isExpanded)
    .sensoryFeedback(trigger: isExpanded) {
        isExpanded ? .impact : nil
    }
```

Returns the `SensoryFeedback?` to play (or `nil` to suppress). Use when the haptic depends on the new state.

## Mismatch flag (the LAY-UX-009 / HAPT-UX-001 case)

The acceptance criterion: `.sensoryFeedback(.error)` triggered for a non-error event must be flagged.

### Bad — variant does not match event semantics

```swift
struct SaveButton: View {
    @State private var didSave = false

    var body: some View {
        Button("Save") { didSave = true }
            .sensoryFeedback(.error, trigger: didSave) // wrong: didSave is a success signal
    }
}
```

The user feels the system "error" pattern after a successful save. Standard pattern recognition is broken.

### Good — variant matches the event

```swift
struct SaveButton: View {
    @State private var didSave = false
    @State private var saveFailed = false

    var body: some View {
        Button("Save") { performSave() }
            .sensoryFeedback(.success, trigger: didSave)
            .sensoryFeedback(.error, trigger: saveFailed)
    }
}
```

`.success` plays when `didSave` flips; `.error` plays only when `saveFailed` flips.

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

Every call site uses `.taskCompleted`, never `.success` directly. If the team later decides task completion should be `.impact(flexibility: .soft, intensity: 1)`, change one line.

## Quick checklist for review

- [ ] Variant matches HIG tier for the event (Notification / Impact / Selection / Change).
- [ ] Trigger value cleanly transitions only when the event happens (not on every render).
- [ ] No `.error` / `.success` / `.warning` reused for non-notification events.
- [ ] Same outcome maps to the same variant across the codebase.
- [ ] Paired with a visible UI change — see [`accessibility-and-haptics.md`](accessibility-and-haptics.md).
