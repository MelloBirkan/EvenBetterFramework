---
corpus_version: development
domain: haptics
platform: ios
last_reviewed: 2026-05-06
---

# iOS SwiftUI Haptics Corpus

Canonical EvenBetter iOS corpus clauses for this conformance domain. Each H2 heading is a stable clause ID used by analyzer, validator, fixer, and benchmark outputs.

## HAPT-UX-001 - Match sensoryFeedback variant to its documented event

**Severity:** warning
**Dimension:** ux
**Platform:** ios
**Source:** [Apple HIG: Playing haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics)
**Retrieved:** 2026-05-06

**Check.** Flag `.sensoryFeedback(.error, ...)`, `.sensoryFeedback(.success, ...)`, `.sensoryFeedback(.warning, ...)`, or any other `SensoryFeedback` variant played for an event whose semantics do not match the documented meaning. Examples: `.error` triggered when a save succeeds, `.success` triggered when a request fails, `.selection` triggered for a non-selection state change, `.impact` triggered without an accompanying visual collision or snap.

**Why.** Apple guidance: use system-provided haptic patterns according to their documented meanings. People recognize standard haptics because the system plays them consistently on interactions with standard controls; repurposing a pattern for an unrelated outcome breaks that learned association and confuses users.

**Correct code.**

```swift
Text(saveStatus)
    .sensoryFeedback(.success, trigger: didSave)
    .sensoryFeedback(.error, trigger: saveFailed)
```

## HAPT-UX-002 - Apply haptics consistently for the same outcome

**Severity:** info
**Dimension:** ux
**Platform:** ios
**Source:** [Apple HIG: Playing haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics#Best-practices)
**Retrieved:** 2026-05-06

**Check.** Flag the same logical outcome fired with different haptic variants in different views or flows (for example, "task completed" plays `.success` in one screen, `.impact` in another, and `.selection` elsewhere).

**Why.** Apple guidance: build a clear, causal relationship between each haptic and the action that causes it so people learn to associate certain haptic patterns with certain experiences. Inconsistent mapping defeats that recognition and feels gratuitous.

**Correct code.**

```swift
extension SensoryFeedback {
    static let taskCompleted: SensoryFeedback = .success
    static let taskFailed: SensoryFeedback = .error
}

Text(status)
    .sensoryFeedback(.taskCompleted, trigger: didFinish)
```

## HAPT-UX-003 - Pair haptics with visual or audio feedback

**Severity:** error
**Dimension:** ux
**Platform:** ios
**Source:** [Apple HIG: Feedback](https://developer.apple.com/design/human-interface-guidelines/feedback)
**Retrieved:** 2026-05-06

**Check.** Flag state changes that fire `.sensoryFeedback` or `CHHapticEngine` playback without a visible UI confirmation (banner, alert, label update, animated state change, color/icon change) and without an audio cue. Especially flag success, warning, and error notifications that have no on-screen counterpart.

**Why.** Haptics may be muted, off, imperceptible to the user, or unsupported on the device (iPad, iPod touch, Apple Vision Pro). When haptics are the only feedback channel, those users miss the outcome entirely. The HIG requires that all feedback be accessible by reaching users through more than one sense.

**Correct code.**

```swift
HStack {
    Image(systemName: didSave ? "checkmark.circle.fill" : "circle")
    Text(didSave ? "Saved" : "Saving…")
}
.sensoryFeedback(.success, trigger: didSave)
```

## HAPT-UX-004 - Gate Core Haptics on device capability

**Severity:** warning
**Dimension:** ux
**Platform:** ios
**Source:** [Apple Developer: Preparing your app to play haptics](https://developer.apple.com/documentation/corehaptics/preparing-your-app-to-play-haptics)
**Retrieved:** 2026-05-06

**Check.** Flag `CHHapticEngine()` initialization, `try engine.start()`, or `try engine.makePlayer(with:)` paths that do not first inspect `CHHapticEngine.capabilitiesForHardware().supportsHaptics` and do not provide a non-haptic fallback when the capability is `false`.

**Why.** iPad, iPod touch, and Apple Vision Pro do not support Core Haptics. Initializing or starting an engine on those devices silently delivers no feedback. Apple guidance is to check `supportsHaptics` first and adjust to provide an alternative type of feedback (for example, stronger audio, multimedia, or visual feedback) when haptics are unavailable.

**Correct code.**

```swift
let capability = CHHapticEngine.capabilitiesForHardware()
guard capability.supportsHaptics else {
    showVisualConfirmation()
    return
}

let engine = try CHHapticEngine()
try engine.start()
```
