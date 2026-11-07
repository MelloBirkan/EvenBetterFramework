# Core Haptics fallback patterns

Reference for `evenbetter-ios-haptics`. Use Core Haptics when `.sensoryFeedback` and `UIFeedbackGenerator` cannot express the pattern you need, for example a custom continuous pattern, haptics synchronized with audio, or an AHAP-driven sequence. Use `UIFeedbackGenerator` when the deployment target is below iOS 17 and you only need a system-tier pattern, or in UIKit code.

Cites: `HAPT-UX-004`, `HAPT-UX-003`.

Contents:

- When to drop down from `.sensoryFeedback`
- 1. Capability gate (HAPT-UX-004)
- 2. Engine setup with reset and stopped handlers
- 3. Transient pattern from a dictionary literal
- 4. AHAP file playback
- 5. Auto-shutdown and player lifecycle
- 6. UIKit feedback generators
- 7. Composition rules
- Quick checklist

## When to drop down from `.sensoryFeedback`

Reach for Core Haptics only when:

- You need a custom transient or continuous waveform the system tier cannot produce.
- You need synchronized audio and haptics (AHAP files).
- You need real-time intensity or sharpness changes tied to physics or input.
- You're shipping a game or game-like control where long-running haptic textures matter.

Otherwise, prefer `.sensoryFeedback`.

## 1. Capability gate (HAPT-UX-004)

iPad, iPod touch and Apple Vision Pro do not support Core Haptics. Check `supportsHaptics` before creating an engine, and provide a non-haptic fallback, because on those devices the haptic never plays.

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

When `supportsHaptics` is `false`, the caller offers a non-haptic confirmation instead: visual, audio or both. See `references/accessibility-and-haptics.md`.

## 2. Engine setup with reset and stopped handlers

Set reset and stopped handlers so playback survives system interruptions such as an audio session interruption, the app being suspended, an idle timeout or a system error.

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

Set both handlers before starting the engine. Restart the engine inside the reset handler if it was running when the reset fired.

## 3. Transient pattern from a dictionary literal

Use a dictionary literal for one-shot patterns defined inline, without an asset file.

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

A `CHHapticPatternPlayer` is lightweight, and you can discard it after `start(atTime:)`. Keep the engine retained.

## 4. AHAP file playback

For richer patterns, ship an Apple Haptic and Audio Pattern (`.ahap`) file in the bundle and play it directly.

```swift
guard let url = Bundle.main.url(forResource: "Sparkle", withExtension: "ahap") else {
    return
}

try engine.start()
try engine.playPattern(from: url)
```

Use `CHHapticAdvancedPatternPlayer` (from `engine.makeAdvancedPlayer(with:)`) when you need looping, pausing, resuming or seeking.

## 5. Auto-shutdown and player lifecycle

Stop the engine after the last player finishes to conserve power.

```swift
engine.notifyWhenPlayersFinished { _ in
    return .stopEngine
}
```

Restart it lazily before the next playback. Do not leave the engine running between unrelated events.

## 6. UIKit feedback generators

When the deployment target is below iOS 17, or in UIKit code, use the `UIFeedbackGenerator` subclasses. They cover the same Notification, Impact and Selection tiers as `.sensoryFeedback`, but you call `prepare()` yourself and keep the generator alive while it is in use.

### Below iOS 17

| Subclass | Tier | Equivalent `.sensoryFeedback` |
| --- | --- | --- |
| `UINotificationFeedbackGenerator` | Notification | `.success`, `.warning`, `.error` |
| `UIImpactFeedbackGenerator` | Impact | `.impact`, `.impact(weight:intensity:)` |
| `UISelectionFeedbackGenerator` | Selection | `.selection` |

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

### Canvas feedback (iOS 17.5 and later)

`UICanvasFeedbackGenerator` (iOS 17.5, iPadOS 17.5, Mac Catalyst 17.5) signals drawing events, such as an object snapping to a guide or ruler. With Apple Pencil Pro on a compatible iPad, it produces a tactile response. It is not a pre-iOS 17 fallback, and each of its methods has a SwiftUI equivalent:

| `UICanvasFeedbackGenerator` method | Equivalent `.sensoryFeedback` |
| --- | --- |
| `alignmentOccurred(at:)` | `.alignment` (iOS 17) |
| `pathCompleted(at:)` | `.pathComplete` (iOS 17.5) |

```swift
import UIKit

final class CanvasViewController: UIViewController {
    private var feedback: UICanvasFeedbackGenerator?

    override func viewDidLoad() {
        super.viewDidLoad()
        feedback = UICanvasFeedbackGenerator(view: view)
    }

    func itemSnappedToGuide(at point: CGPoint) {
        feedback?.alignmentOccurred(at: point)
    }

    func strokeRecognized(endingAt point: CGPoint) {
        feedback?.pathCompleted(at: point)
    }
}
```

Notes:

- `prepare()` reduces latency by warming the haptic hardware. Call it shortly before the trigger, not in `init`.
- Do not subclass `UIFeedbackGenerator` or create instances of it. Apple supports only its concrete subclasses: impact, selection, notification and canvas.
- These generators still work on iOS 17 and later. Prefer `.sensoryFeedback` in SwiftUI views and keep `UIFeedbackGenerator` for UIKit code.

## 7. Composition rules

- Don't play two haptics of the same type at the same time, because they become indistinguishable.
- Long-running continuous haptics dilute meaning in productivity apps, so keep them for gameplay.
- Match haptic intensity to the intensity of the visual motion it accompanies.

## Quick checklist

- [ ] `CHHapticEngine.capabilitiesForHardware().supportsHaptics` checked before any engine work (HAPT-UX-004).
- [ ] `resetHandler` and `stoppedHandler` set before `engine.start()`.
- [ ] Engine retained for the lifetime of playback.
- [ ] Non-haptic fallback path defined for unsupported devices.
- [ ] AHAP files added to the bundle target if used.
- [ ] Custom Core Haptics is the right tool: neither `.sensoryFeedback` nor `UIFeedbackGenerator` covers this event.
