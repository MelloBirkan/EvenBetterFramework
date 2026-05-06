# Accessibility and haptics

Reference for `evenbetter-ios-haptics`. Haptics are an accessibility risk when treated as the only feedback channel. This file defines the rules every haptic call site must satisfy before shipping.

Cites: `HAPT-UX-003`, `HAPT-UX-004`.

## Why this matters

A haptic vibration may be:

- Muted by the user in Settings → Sounds & Haptics, or via Silent Mode.
- Disabled per-app for accessibility or comfort.
- Imperceptible to a user with motor or sensory disabilities.
- Unsupported by the device — iPad, iPod touch, and Apple Vision Pro do not have a Taptic Engine.
- Suppressed by the system (Low Power Mode, audio interruption, app suspension).

Per [HIG: Feedback](https://developer.apple.com/design/human-interface-guidelines/feedback): "When you use multiple ways to provide feedback, you reach more people and give them the opportunity to receive the feedback in ways that work for them."

## Rule 1 — Haptics must never be the only feedback channel (HAPT-UX-003)

Every haptic must be paired with at least one of:

- Visible UI change (label text, icon, color, animation, banner, sheet, or alert).
- Audio cue (system sound, custom audio, or AHAP-synced audio).

### Bad — silent success

```swift
Button("Save") { performSave() }
    .sensoryFeedback(.success, trigger: didSave)
```

A muted user sees no change and feels nothing.

### Good — paired confirmation

```swift
HStack {
    Image(systemName: didSave ? "checkmark.circle.fill" : "circle")
        .foregroundStyle(didSave ? .green : .secondary)
    Text(didSave ? "Saved" : "Save")
}
.sensoryFeedback(.success, trigger: didSave)
```

Now every user — haptic-on, haptic-off, VoiceOver, low vision — can perceive the outcome.

## Rule 2 — Provide a user toggle

Apple guidance: "Make haptics optional. Let people turn off or mute haptics, and make sure people can still enjoy your app or game without them."

Expose a Settings toggle:

```swift
@AppStorage("hapticsEnabled") private var hapticsEnabled = true

var body: some View {
    ContentView()
        .sensoryFeedback(trigger: didSave) {
            hapticsEnabled ? .success : nil
        }
}
```

The closure-returning `.sensoryFeedback` overload returns `nil` when the user has opted out, so no haptic plays even though the trigger changed.

## Rule 3 — Gate Core Haptics on capability (HAPT-UX-004)

Detailed in [`core-haptics-fallback.md`](core-haptics-fallback.md). Summary:

```swift
guard CHHapticEngine.capabilitiesForHardware().supportsHaptics else {
    showVisualConfirmation()
    return
}
```

Unsupported devices must still receive feedback through another channel.

## Rule 4 — Don't overuse

Apple guidance: "Sometimes a haptic can feel just right when it happens occasionally, but become tiresome when it plays frequently."

- Don't fire haptics on every list-row tap, scroll event, or character input.
- Don't repeat the same haptic in a tight loop (e.g., during continuous drag).
- Long-running continuous haptics belong in gameplay, not productivity flows.

If you find yourself debouncing haptics, the underlying interaction probably doesn't warrant one.

## Rule 5 — Respect device features

Apple guidance: "Be aware that playing haptics might impact other user experiences. By design, haptics produce enough physical force for people to feel the vibration. Ensure that haptic vibrations don't disrupt experiences involving device features like the camera, gyroscope, or microphone."

Suppress haptics during:

- Active camera capture.
- Audio recording (microphone in use).
- Gyroscope/accelerometer-driven gameplay where vibration could foul motion input.

## Rule 6 — Match haptic intensity to visual intensity

A small label nudge should pair with a light impact, not a heavy one. A confetti burst can pair with a heavier impact. Keep the haptic and the animation in the same energy range so the experience feels coherent rather than glitchy.

## Quick review checklist

- [ ] Every haptic is paired with a visible UI change or audio cue (HAPT-UX-003).
- [ ] User can disable haptics in app settings.
- [ ] Core Haptics gated on `supportsHaptics` (HAPT-UX-004).
- [ ] No haptic fires on routine, frequent interactions.
- [ ] Haptics don't fire while the camera, microphone, or motion sensors are active.
- [ ] Haptic intensity matches the visual energy of the accompanying animation.
- [ ] Same outcome plays the same haptic everywhere (HAPT-UX-002).
