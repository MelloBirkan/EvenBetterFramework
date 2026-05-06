# Core Haptics fallback patterns

Reference for `evenbetter-ios-haptics`. Use Core Haptics when `.sensoryFeedback` and `UIFeedbackGenerator` cannot express the pattern you need (for example, custom continuous, transient + audio, or AHAP-driven sequences). Use `UIFeedbackGenerator` when the deployment target is below iOS 17 and you only need a system-tier pattern.

Cites: `HAPT-UX-004`, `HAPT-UX-003`.

## When to drop down from `.sensoryFeedback`

Reach for Core Haptics only when:

- You need a custom transient or continuous waveform the system tier cannot produce.
- You need synchronized audio + haptics (AHAP files).
- You need real-time intensity / sharpness modulation tied to physics or input.
- You're shipping a game or game-like control where long-running haptic textures matter.

Otherwise, prefer `.sensoryFeedback`.

## 1. Capability gate (HAPT-UX-004)

iPad, iPod touch, and Apple Vision Pro do not support Core Haptics. Always check first and provide a non-haptic fallback.

```swift
import CoreHaptics

final class HapticPlayer {
    private(set) var supportsHaptics: Bool = false
    private var engine: CHHapticEngine?

    init() {
        let capability = CHHapticEngine.capabilitiesForHardware()
        supportsHaptics = capability.supportsHaptics

        guard supportsHaptics else { return }
        do {
            engine = try CHHapticEngine()
        } catch {
            engine = nil
        }
    }
}
```

When `supportsHaptics` is `false`, the caller must offer a non-haptic confirmation (visual, audio, or both — see [`accessibility-and-haptics.md`](accessibility-and-haptics.md)).

## 2. Engine setup with reset and stopped handlers

Core Haptics requires reset and stopped handlers so playback survives system interruptions (incoming calls, backgrounding, idle timeout, system errors).

```swift
func configure(_ engine: CHHapticEngine) {
    engine.resetHandler = { [weak self] in
        guard let self else { return }
        do {
            try self.engine?.start()
        } catch {
            self.engine = nil
        }
    }

    engine.stoppedHandler = { reason in
        switch reason {
        case .audioSessionInterrupt: break
        case .applicationSuspended:  break
        case .idleTimeout:           break
        case .systemError:           break
        @unknown default:            break
        }
    }
}
```

Per Apple guidance: set both handlers _before_ starting the engine. Restart the engine inside the reset handler if it was running when the reset fired.

## 3. Transient pattern from a dictionary literal

Use a dictionary literal for one-shot patterns defined inline (no asset file).

```swift
import CoreHaptics

func playSingleTap(on engine: CHHapticEngine) throws {
    let dict: [CHHapticPattern.Key: Any] = [
        .pattern: [
            [
                CHHapticPattern.Key.event: [
                    CHHapticPattern.Key.eventType: CHHapticEvent.EventType.hapticTransient,
                    CHHapticPattern.Key.time: CHHapticTimeImmediate,
                    CHHapticPattern.Key.eventDuration: 1.0,
                ]
            ]
        ]
    ]

    let pattern = try CHHapticPattern(dictionary: dict)
    let player  = try engine.makePlayer(with: pattern)

    try engine.start()
    try player.start(atTime: 0)
}
```

`CHHapticPatternPlayer` is a fire-and-forget object; it's lightweight and you can discard it after `start(atTime:)`. Keep the engine retained.

## 4. AHAP file playback

For richer patterns, ship an Apple Haptic and Audio Pattern (`.ahap`) file in the bundle and play it directly.

```swift
guard let url = Bundle.main.url(forResource: "Sparkle", withExtension: "ahap") else {
    return
}

try engine.start()
try engine.playPattern(from: url)
```

Use `CHHapticAdvancedPatternPlayer` (via `engine.makeAdvancedPlayer(with:)`) when you need looping, pausing, resuming, or seeking.

## 5. Auto-shutdown and player lifecycle

Stop the engine after the last player finishes to conserve power.

```swift
engine.notifyWhenPlayersFinished { _ in
    return .stopEngine
}
```

Restart it lazily before the next playback. Do not leave the engine running between unrelated events.

## 6. Pre-iOS 17 / UIKit fallback — `UIFeedbackGenerator`

When the deployment target is below iOS 17, or when working in UIKit-bridged code, use `UIFeedbackGenerator` subclasses. They give you the same Notification / Impact / Selection tiers as `.sensoryFeedback` but require manual `prepare()` and instance retention.

| Subclass | Tier | Equivalent `.sensoryFeedback` |
| --- | --- | --- |
| `UINotificationFeedbackGenerator` | Notification | `.success`, `.warning`, `.error` |
| `UIImpactFeedbackGenerator` | Impact | `.impact`, `.impact(weight:intensity:)` |
| `UISelectionFeedbackGenerator` | Selection | `.selection` |
| `UICanvasFeedbackGenerator` | Canvas (drawing) | (no direct `.sensoryFeedback` equivalent) |

```swift
import UIKit

final class LegacyHaptics {
    private let notify = UINotificationFeedbackGenerator()
    private let impact = UIImpactFeedbackGenerator(style: .medium)
    private let select = UISelectionFeedbackGenerator()

    func prepare() {
        notify.prepare()
        impact.prepare()
        select.prepare()
    }

    func didSave()   { notify.notificationOccurred(.success) }
    func didFail()   { notify.notificationOccurred(.error) }
    func snapped()   { impact.impactOccurred() }
    func tabPicked() { select.selectionChanged() }
}
```

Notes:

- `prepare()` reduces latency by warming the haptic hardware. Call it shortly before the trigger, not in `init`.
- Do not subclass `UIFeedbackGenerator` directly; only the four concrete subclasses are supported.
- These generators are still available on iOS 17+. Prefer `.sensoryFeedback` in SwiftUI views and reserve `UIFeedbackGenerator` for UIKit code.

## 7. Composition rules

- Don't layer two haptics of the same type at the same time — they become indistinguishable.
- Long-running continuous haptics dilute meaning in productivity apps; reserve them for gameplay.
- Synchronize haptic intensity with visual motion intensity for a coherent multi-sensory experience.

## Quick checklist

- [ ] `CHHapticEngine.capabilitiesForHardware().supportsHaptics` checked before any engine work (HAPT-UX-004).
- [ ] `resetHandler` and `stoppedHandler` set before `engine.start()`.
- [ ] Engine retained for the lifetime of playback.
- [ ] Non-haptic fallback path defined for unsupported devices.
- [ ] AHAP files added to the bundle target if used.
- [ ] Custom Core Haptics is the right tool — would `.sensoryFeedback` or `UIFeedbackGenerator` already cover this event?
