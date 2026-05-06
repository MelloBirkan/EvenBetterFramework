---
name: evenbetter-ios-haptics
description: Map .sensoryFeedback to event semantics per Apple HIG (success/error/impact tiers); CoreHaptics fallback for custom patterns.
---

# iOS Haptics

## Overview

Use this skill when a user wants to add, review, or refactor haptic feedback in an iOS / SwiftUI app. The skill answers three questions in order:

1. Which haptic API should I reach for?
2. Which `SensoryFeedback` variant matches the event I'm signalling?
3. How do I keep haptics accessible and HIG-aligned?

Default to SwiftUI's `.sensoryFeedback(_:trigger:)` modifier (iOS 17+). Use Core Haptics only for custom transient or continuous patterns the system tier can't express. Never make haptics the sole feedback channel.

## When to use

- "Add a haptic when this button succeeds / fails / saves / deletes"
- "Refactor this `UIImpactFeedbackGenerator` call to SwiftUI"
- "Why doesn't the haptic fire on iPad?"
- "Design a custom haptic pattern for our pull-to-refresh"
- "Review my `.sensoryFeedback(.error, ...)` usage"
- Any review of code touching `SensoryFeedback`, `CHHapticEngine`, `UIFeedbackGenerator`, or `.sensoryFeedback(...)` modifiers.

## Decision tree

```
Need haptic feedback?
├── Standard Notification / Impact / Selection event?
│   └── iOS 17+ deployment target?
│       ├── Yes → SwiftUI `.sensoryFeedback(_:trigger:)`
│       │        See references/sensory-feedback-mapping.md
│       └── No  → UIKit UIFeedbackGenerator
│                See references/core-haptics-fallback.md (UIKit fallback section)
└── Custom transient or continuous pattern?
    └── Core Haptics (CHHapticEngine)
         See references/core-haptics-fallback.md
         Always gate on capabilitiesForHardware().supportsHaptics
```

In all branches, validate against `references/accessibility-and-haptics.md` before shipping.

## References

- `references/sensory-feedback-mapping.md` — full `SensoryFeedback` variant table mapped to HIG tiers (Notification, Impact, Selection, Change), the three `.sensoryFeedback(_:trigger:)` overload shapes (plain, `condition:`, closure-returning), and a good-vs-bad mismatch example.
- `references/core-haptics-fallback.md` — `CHHapticEngine` setup with `resetHandler` and `stoppedHandler`, `CHHapticPattern` from dictionary literal or AHAP file, capability gating via `supportsHaptics`, and `UIFeedbackGenerator` for pre-iOS 17 / UIKit-bridged code.
- `references/accessibility-and-haptics.md` — pairing requirements, user-controllable toggle, hardware gating, frequency limits, and the rule that haptics must never be the only feedback channel.

## Strong defaults

- Reach for `.sensoryFeedback` first; only drop to `CHHapticEngine` for truly custom patterns.
- Match the variant to the documented event semantics. `.error` is for errors, `.success` for completions, `.selection` for value changes inside a UI element, `.impact` for collisions or snap-into-place.
- Always pair a haptic with a visible state change (label, icon, color, animation) or audio cue.
- Centralize semantic-named haptics in a `SensoryFeedback` extension so the same outcome plays the same haptic across every screen.
- Gate Core Haptics on `CHHapticEngine.capabilitiesForHardware().supportsHaptics` and define a non-haptic fallback for unsupported devices (iPad, iPod touch, Apple Vision Pro).

## Anti-patterns

- `.sensoryFeedback(.error, trigger: didSave)` for non-error events — repurposes the standard pattern and breaks user recognition.
- Firing haptics on every minor interaction (long lists, repeated taps, scroll) — overuse drains the meaning.
- Long-running continuous haptics in a productivity app — Apple guidance limits these to gameplay.
- Haptic-only confirmation of success or failure with no on-screen change — silently fails for muted, low-perception, or unsupported users.
- `CHHapticEngine()` without first checking `supportsHaptics`.
- Fan-out: same outcome ("task completed") plays different haptics in different views.

## Cites corpus

Load canonical clauses from `../../corpus/ios/haptics.md` and `../../corpus/ios/layout-interaction.md`. Use `../../corpus/index.json` when clause metadata, source URLs, retrieval dates, anchors, or corpus version are needed.

- `HAPT-UX-001` — Match `sensoryFeedback` variant to its documented event.
- `HAPT-UX-002` — Apply haptics consistently for the same outcome.
- `HAPT-UX-003` — Pair haptics with visual or audio feedback.
- `HAPT-UX-004` — Gate Core Haptics on device capability.
- `LAY-UX-009` — Map `sensoryFeedback` variant to HIG haptic tier.

Do not duplicate clause bodies in this skill; the corpus is the source of truth. Preserve `Severity`, `Dimension`, `Source`, `Retrieved`, `Check`, `Why`, and `Correct code` fields when answering from these clauses.

## Notes

- Apple primary references:
  - [HIG: Playing haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics)
  - [HIG: Feedback](https://developer.apple.com/design/human-interface-guidelines/feedback)
  - [SwiftUI: SensoryFeedback](https://developer.apple.com/documentation/SwiftUI/SensoryFeedback)
  - [SwiftUI: View.sensoryFeedback(_:trigger:)](https://developer.apple.com/documentation/swiftui/view/sensoryfeedback(_:trigger:))
  - [Core Haptics](https://developer.apple.com/documentation/CoreHaptics)
  - [UIFeedbackGenerator](https://developer.apple.com/documentation/UIKit/UIFeedbackGenerator)
- Use web search to consult current Apple Developer documentation when haptics APIs or platform behavior may have changed.
