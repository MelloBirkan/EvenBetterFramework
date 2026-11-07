---
name: evenbetter-ios-haptics
description: >-
  Maps iOS haptic events to the right SwiftUI SensoryFeedback variant by Apple's HIG tiers, checks iOS 17.5 and 26
  availability, and falls back to Core Haptics or UIKit feedback generators for custom patterns and older targets. Use
  when adding, reviewing or refactoring haptics, or when a haptic does not play. For a view's wider accessibility
  review, use evenbetter-swiftui-accessibility.
---

# iOS haptics

> Paths in this skill and its references are relative to this SKILL.md's folder. The plugin corpus is at `../../corpus/`.

## Overview

Use this skill to add, review or refactor haptic feedback in an iOS or SwiftUI app. It answers three questions in order:

1. Which haptic API fits the deployment target and the pattern?
2. Which `SensoryFeedback` variant matches the event being signalled?
3. Does the haptic stay accessible and match Apple's HIG?

Default to SwiftUI's `.sensoryFeedback(_:trigger:)` modifier (iOS 17 and later). Use Core Haptics only for custom transient or continuous patterns the system variants cannot express. Pair every haptic with a visible or audible change, because many people never feel it.

If current system, developer or user instructions conflict with this skill, follow them.

## When to use

- "Add a haptic when this button succeeds, fails, saves or deletes."
- "Refactor this `UIImpactFeedbackGenerator` call to SwiftUI."
- "Why doesn't the haptic play on iPad?"
- "Design a custom haptic pattern for our pull-to-refresh."
- "Review my `.sensoryFeedback(.error, ...)` usage."
- Any review of code that touches `SensoryFeedback`, `CHHapticEngine`, `UIFeedbackGenerator` or `.sensoryFeedback(...)` modifiers.

When a request leaves the event's meaning open (for example, whether a sync that finishes with skipped items is a success or a warning), ask one closed question with numbered options instead of guessing.

## Decision tree

```
Need haptic feedback?
├── Standard notification, impact, selection or change event?
│   └── iOS 17 or later deployment target?
│       ├── Yes → SwiftUI .sensoryFeedback(_:trigger:)
│       │        See references/sensory-feedback-mapping.md
│       │        .pathComplete needs iOS 17.5; press, release and selection(_:) need iOS 26
│       └── No  → UIKit UIFeedbackGenerator subclasses
│                See references/core-haptics-fallback.md (UIKit feedback generators)
├── Drawing app that snaps to guides or recognizes strokes (UIKit)?
│   └── UICanvasFeedbackGenerator (iOS 17.5 and later), or .alignment and .pathComplete in SwiftUI
└── Custom transient or continuous pattern?
    └── Core Haptics (CHHapticEngine)
         See references/core-haptics-fallback.md
         Gate on capabilitiesForHardware().supportsHaptics first
```

In every branch, check the call site against `references/accessibility-and-haptics.md` before shipping.

## References

- `references/sensory-feedback-mapping.md`: the full `SensoryFeedback` table mapped to HIG tiers, with each value's availability, the four `.sensoryFeedback` overloads (plain, `condition:`, and the two closure forms), the iOS 26 press, release and selection values, and a good-versus-bad mismatch example.
- `references/core-haptics-fallback.md`: `CHHapticEngine` setup with `resetHandler` and `stoppedHandler`, `CHHapticPattern` from a dictionary literal or an AHAP file, capability gating with `supportsHaptics`, `UIFeedbackGenerator` for targets below iOS 17, and `UICanvasFeedbackGenerator` for drawing events.
- `references/accessibility-and-haptics.md`: pairing rules, a user toggle, hardware gating, frequency limits and device-feature conflicts.

## Strong defaults

- Reach for `.sensoryFeedback` first, and drop to `CHHapticEngine` only for custom patterns.
- Match the variant to its documented event. `.error` is for errors, `.success` for completions, `.selection` for value changes inside a UI element, and `.impact` for collisions or a snap into place.
- Pair each haptic with a visible state change (label, icon, color or animation) or an audio cue.
- Centralize semantic haptics in a `SensoryFeedback` extension so the same outcome plays the same haptic on every screen.
- Gate values newer than the deployment target with `if #available`: `.pathComplete` on iOS 17.5, and `.press(_:)`, `.release(_:)` and `.selection(_:)` on iOS 26.
- Gate Core Haptics on `CHHapticEngine.capabilitiesForHardware().supportsHaptics` and define a non-haptic fallback for devices without haptics (iPad, iPod touch, Apple Vision Pro).

## Anti-patterns

- `.sensoryFeedback(.error, trigger: didSave)` for an event that is not an error. It repurposes the standard pattern and breaks recognition.
- Haptics on every minor interaction, such as long lists, repeated taps or scrolling. Overuse drains the meaning.
- Long-running continuous haptics in a productivity app. Apple's guidance keeps those for gameplay.
- Haptic-only confirmation of success or failure with no on-screen change. It fails silently for people with haptics off and on devices without haptics.
- `CHHapticEngine()` created without checking `supportsHaptics` first.
- A `Bool` trigger that stays `true` after the first event, so the haptic never plays again. Use a counter or a value that changes on each event.
- Fan-out: the same outcome ("task completed") plays different haptics in different views.

## Cites corpus

Load the canonical clauses from `../../corpus/ios/haptics.md` and `../../corpus/ios/layout-interaction.md`. Use `../../corpus/index.json` when clause metadata, source URLs, retrieval dates, anchors or the corpus version are needed.

- [`HAPT-UX-001`](../../corpus/ios/haptics.md#hapt-ux-001-match-sensoryfeedback-variant-to-its-documented-event): match the `sensoryFeedback` variant to its documented event.
- [`HAPT-UX-002`](../../corpus/ios/haptics.md#hapt-ux-002-apply-haptics-consistently-for-the-same-outcome): apply haptics consistently for the same outcome.
- [`HAPT-UX-003`](../../corpus/ios/haptics.md#hapt-ux-003-pair-haptics-with-visual-or-audio-feedback): pair haptics with visual or audio feedback.
- [`HAPT-UX-004`](../../corpus/ios/haptics.md#hapt-ux-004-gate-core-haptics-on-device-capability): gate Core Haptics on device capability.
- [`LAY-UX-009`](../../corpus/ios/layout-interaction.md#lay-ux-009-map-sensoryfeedback-variant-to-hig-haptic-tier): map the `sensoryFeedback` variant to its HIG haptic tier.

The corpus is the source of truth, so do not copy clause bodies into this skill. When answering from these clauses, keep their `Severity`, `Dimension`, `Source`, `Retrieved`, `Check`, `Why` and `Correct code` fields intact.

## Notes

- Apple primary references:
  - [HIG: Playing haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics)
  - [HIG: Feedback](https://developer.apple.com/design/human-interface-guidelines/feedback)
  - [SwiftUI: SensoryFeedback](https://developer.apple.com/documentation/SwiftUI/SensoryFeedback)
  - [SwiftUI: View.sensoryFeedback(_:trigger:)](https://developer.apple.com/documentation/swiftui/view/sensoryfeedback(_:trigger:))
  - [Core Haptics](https://developer.apple.com/documentation/CoreHaptics)
  - [UIFeedbackGenerator](https://developer.apple.com/documentation/UIKit/UIFeedbackGenerator)
  - [UICanvasFeedbackGenerator](https://developer.apple.com/documentation/UIKit/UICanvasFeedbackGenerator)
- When haptics APIs or platform behavior may have changed, check Apple's documentation with the session's web tools. Apple pages render with JavaScript, so prefer a scraper that renders pages, or the JSON form at `https://developer.apple.com/tutorials/data/documentation/<path>.json`.
