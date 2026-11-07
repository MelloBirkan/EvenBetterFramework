# Accessibility and haptics

Reference for `evenbetter-ios-haptics`. Haptics become an accessibility risk when they are the only feedback channel. This file sets the rules every haptic call site should meet before it ships.

Cites: `HAPT-UX-003`, `HAPT-UX-004`.

Contents:

- Why this matters
- Rule 1: haptics are never the only feedback channel (HAPT-UX-003)
- Rule 2: provide a user toggle
- Rule 3: gate Core Haptics on capability (HAPT-UX-004)
- Rule 4: don't overuse
- Rule 5: respect device features
- Rule 6: match haptic intensity to visual intensity
- Quick review checklist

## Why this matters

A haptic may never reach the person because it is:

- Turned off in Settings, under Sounds & Haptics or under Accessibility > Touch > Vibration.
- Hard to feel for some people, such as those with reduced tactile sensitivity.
- Unsupported by the device. iPad, iPod touch and Apple Vision Pro have no Taptic Engine for app haptics.
- Stopped by the system, for example when the audio session is interrupted or the app is suspended. Core Haptics reports both as engine stop reasons.

[HIG: Feedback](https://developer.apple.com/design/human-interface-guidelines/feedback) puts it this way: "When you use multiple ways to provide feedback, you reach more people and give them the opportunity to receive the feedback in ways that work for them."

## Rule 1: haptics are never the only feedback channel (HAPT-UX-003)

Pair every haptic with at least one of:

- A visible UI change: label text, an icon, color, an animation, a banner, a sheet or an alert.
- An audio cue: a system sound, custom audio, or audio synchronized through an AHAP file.

### Bad: silent success

```swift
Button("Save") { performSave() }
    .sensoryFeedback(.success, trigger: didSave)
```

Someone with haptics off sees no change and feels nothing.

### Good: paired confirmation

```swift
HStack {
    Image(systemName: didSave ? "checkmark.circle.fill" : "circle")
        .foregroundStyle(didSave ? .green : .secondary)
    Text(didSave ? "Saved" : "Save")
}
.sensoryFeedback(.success, trigger: didSave)
```

The outcome is now perceptible whether haptics are on or off, and to VoiceOver and low-vision users.

## Rule 2: provide a user toggle

Apple's [Playing haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics) guidance: "Make haptics optional. Let people turn off or mute haptics, and make sure people can still enjoy your app or game without them."

Expose a toggle in the app's settings:

```swift
@AppStorage("hapticsEnabled") private var hapticsEnabled = true

var body: some View {
    ContentView()
        .sensoryFeedback(trigger: didSave) {
            hapticsEnabled ? .success : nil
        }
}
```

The closure overload of `.sensoryFeedback` returns `nil` when the person has opted out, so no haptic plays even though the trigger changed.

## Rule 3: gate Core Haptics on capability (HAPT-UX-004)

Details are in `references/core-haptics-fallback.md`. In short:

```swift
guard CHHapticEngine.capabilitiesForHardware().supportsHaptics else {
    showVisualConfirmation()
    return
}
```

People on unsupported devices still get the feedback through another channel.

## Rule 4: don't overuse

Apple's guidance: "Sometimes a haptic can feel just right when it happens occasionally, but become tiresome when it plays frequently."

- Don't play haptics on every list-row tap, scroll event or character typed.
- Don't repeat the same haptic in a tight loop, for example during a continuous drag.
- Keep long-running continuous haptics for gameplay, not productivity flows.

If you find yourself debouncing haptics, the interaction probably doesn't warrant one.

## Rule 5: respect device features

Apple's guidance: "Be aware that playing haptics might impact other user experiences. By design, haptics produce enough physical force for people to feel the vibration. Ensure that haptic vibrations don't disrupt experiences involving device features like the camera, gyroscope, or microphone."

Suppress haptics during:

- Active camera capture.
- Audio recording, while the microphone is in use.
- Gameplay driven by the gyroscope or accelerometer, where vibration could disturb motion input.

## Rule 6: match haptic intensity to visual intensity

A small label nudge pairs with a light impact, not a heavy one. A confetti burst can pair with a heavier impact. Keep the haptic and the animation in the same energy range so they feel like one event.

## Quick review checklist

- [ ] Every haptic is paired with a visible UI change or an audio cue (HAPT-UX-003).
- [ ] People can turn off haptics in the app's settings.
- [ ] Core Haptics is gated on `supportsHaptics` (HAPT-UX-004).
- [ ] No haptic plays on routine, frequent interactions.
- [ ] Haptics don't play while the camera, microphone or motion sensors are in use.
- [ ] Haptic intensity matches the visual energy of the accompanying animation.
- [ ] The same outcome plays the same haptic everywhere (HAPT-UX-002).
