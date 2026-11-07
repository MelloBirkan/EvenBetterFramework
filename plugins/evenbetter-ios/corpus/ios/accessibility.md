---
corpus_version: development
domain: accessibility
platform: ios
last_reviewed: 2026-11-07
---

# iOS SwiftUI Accessibility Corpus

Canonical EvenBetter iOS corpus clauses for this conformance domain. Each H2 heading is a stable clause ID used by the analyze, validate and repair skills and by benchmark outputs.

## A11Y-UI-001 - Label meaningful images and icon buttons

**Severity:** error
**Dimension:** ui
**Platform:** ios
**Source:** [Apple Developer: accessibilityLabel](https://developer.apple.com/documentation/swiftui/view/accessibilitylabel(_:))
**Retrieved:** 2026-11-07

**Check.** Flag `Image(systemName:)`, image-only `Button`, toolbar icon controls, or custom icon controls that lack a visible text label and lack `.accessibilityLabel(...)`.

**Why.** VoiceOver users need a meaningful name for non-text controls and images.

**Correct code.**

```swift
Button(action: close) {
    Image(systemName: "xmark")
}
.accessibilityLabel("Close")
```

## A11Y-UI-002 - Hide decorative imagery

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple Developer: accessibilityHidden](https://developer.apple.com/documentation/swiftui/view/accessibilityhidden(_:))
**Retrieved:** 2026-11-07

**Check.** Flag decorative `Image`, shape, divider, background, or icon-only ornament that lacks `.accessibilityHidden(true)` and would add noise to the accessibility tree.

**Why.** Decorative elements should not distract assistive technology users from meaningful content.

**Correct code.**

```swift
Image("backgroundPattern")
    .accessibilityHidden(true)
```

## A11Y-UI-003 - Combine related child elements

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple Developer: accessibilityElement children combine](https://developer.apple.com/documentation/swiftui/accessibilitychildbehavior/combine)
**Retrieved:** 2026-11-07

**Check.** Flag rows, cards, or summary groups made from several `Text` and `Image` elements that should be announced as one logical element but omit `.accessibilityElement(children: .combine)`.

**Why.** Combining related children reduces repetitive navigation and gives users a coherent announcement.

**Correct code.**

```swift
HStack {
    Text(account.name)
    Text(account.balance)
}
.accessibilityElement(children: .combine)
```

## A11Y-UI-004 - Keep control types and states out of labels

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple App Store Connect Help: VoiceOver evaluation criteria](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/voiceover-evaluation-criteria/)
**Retrieved:** 2026-11-07

**Check.** Flag `.accessibilityLabel(...)` text that names the element's own type or state, such as "Play button", "Remember me checkbox", "Settings tab" or "Favorite, selected". Words like "button", "checkbox", "toggle", "tab", "link", "selected", "checked" and "unchecked" are the usual signs. Also flag labels that switch wording with state ("Favorite" and "Favorited") instead of adding the `.isSelected` trait or an `.accessibilityValue(...)`. A label that changes because the action changes, such as Play and Pause, is fine.

**Why.** VoiceOver speaks the type from the element's traits and the state from its traits or value. A label that repeats them is heard twice, as in "Unsubscribe checkbox, checkbox", and a state written into the label is wrong as soon as the state changes. Apple's VoiceOver criteria for Accessibility Nutrition Labels ask for labels without control types or states, and the `accessibilityLabel` documentation gives "Play button" as the label not to use.

**Correct code.**

```swift
Button(action: toggleFavorite) {
    Image(systemName: isFavorite ? "star.fill" : "star")
}
.accessibilityLabel("Favorite")
.accessibilityAddTraits(isFavorite ? .isSelected : [])
```

## A11Y-UX-001 - Respect Reduce Motion

**Severity:** warning
**Dimension:** ux
**Platform:** ios
**Source:** [Apple Developer: accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
**Retrieved:** 2026-11-07

**Check.** Flag significant animations, looping motion, parallax, matched-geometry transitions, or gesture-triggered movement that does not check `accessibilityReduceMotion` or provide a reduced-motion alternative.

**Why.** Motion-sensitive users can be harmed or disoriented by unnecessary animation.

**Correct code.**

```swift
@Environment(\.accessibilityReduceMotion) private var reduceMotion

withAnimation(reduceMotion ? nil : .spring()) {
    isExpanded.toggle()
}
```

## A11Y-UX-002 - Add hints for non-obvious actions

**Severity:** info
**Dimension:** ux
**Platform:** ios
**Source:** [Apple Developer: accessibilityHint](https://developer.apple.com/documentation/swiftui/view/accessibilityhint(_:))
**Retrieved:** 2026-11-07

**Check.** Flag custom gestures, ambiguous icon buttons, swipe-only controls, or unusual interactions that lack `.accessibilityHint(...)`.

**Why.** Hints explain what will happen when the result is not obvious from the label alone.

**Correct code.**

```swift
Button("Archive") {
    archive()
}
.accessibilityHint("Moves the message out of the inbox")
```

## A11Y-A11Y-001 - Add button traits to custom interactives

**Severity:** error
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple Developer: accessibilityAddTraits](https://developer.apple.com/documentation/swiftui/view/accessibilityaddtraits(_:))
**Retrieved:** 2026-11-07

**Check.** Flag views with `.onTapGesture`, custom gesture recognizers, or manual hit testing that activate actions but omit `.accessibilityAddTraits(.isButton)`.

**Why.** Assistive technologies need the correct role to communicate that the element is actionable.

**Correct code.**

```swift
Text("Retry")
    .padding()
    .onTapGesture { retry() }
    .accessibilityAddTraits(.isButton)
```

## A11Y-A11Y-002 - Provide accessibilityValue for stateful controls

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple Developer: accessibilityValue](https://developer.apple.com/documentation/swiftui/view/accessibilityvalue(_:))
**Retrieved:** 2026-11-07

**Check.** Flag custom sliders, progress indicators, rating controls, selection controls, counters, or stateful custom controls without `.accessibilityValue(...)`.

**Why.** The label names the control, while the value communicates its current state.

**Correct code.**

```swift
RatingView(value: rating)
    .accessibilityLabel("Rating")
    .accessibilityValue("\(rating) of 5")
```

## A11Y-A11Y-003 - Notify assistive technology of screen changes

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple Developer: AccessibilityNotification](https://developer.apple.com/documentation/accessibility/accessibilitynotification)
**Retrieved:** 2026-11-07

**Check.** Flag custom routers, page replacements, onboarding step changes, or large content swaps that do not post screen-change or layout-change accessibility notifications.

**Why.** Assistive apps need explicit notification when the screen or layout changes outside normal system navigation.

**Correct code.**

```swift
AccessibilityNotification.ScreenChanged().post()
```

## A11Y-A11Y-004 - Match Voice Control names to visible text

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple App Store Connect Help: Voice Control evaluation criteria](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/voice-control-evaluation-criteria/)
**Retrieved:** 2026-11-07
**Standards note:** WCAG 2.2 SC 2.5.3 Label in Name, Level A.

**Check.** Flag controls that show text but carry an `.accessibilityLabel(...)` with different words, for example a button that reads "End call" labelled "Leave call", unless `.accessibilityInputLabels(...)` lists the visible text first. Also flag icon-only buttons whose label is a long phrase people are unlikely to say in full, such as "Compose a new message" on a pencil icon, when they have no shorter input labels.

**Why.** Voice Control users act on a control by saying its name, usually the words they can see. When the accessibility name differs from the visible text, "Tap End call" does nothing and the person has to say "Show names" to find out why, which Apple's Voice Control criteria call out. `accessibilityInputLabels(_:)` (iOS 14+) adds the names Voice Control and Full Keyboard Access accept, in descending order of importance, and leaves the VoiceOver label as it is.

**Correct code.**

```swift
// Visible text and spoken name match, so no label override is needed.
Button("End call", action: endCall)

// An icon-only control gets the short names people are likely to say.
Button(action: compose) {
    Image(systemName: "square.and.pencil")
}
.accessibilityLabel("New message")
.accessibilityInputLabels(["New message", "Compose"])
```

## A11Y-A11Y-005 - Offer alternatives to gesture-only actions

**Severity:** error
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility#Mobility)
**Retrieved:** 2026-11-07
**Standards note:** WCAG 2.2 SC 2.5.1 Pointer Gestures, Level A, and SC 2.5.7 Dragging Movements, Level AA.

**Check.** Flag actions that only a gesture can trigger: `.onLongPressGesture`, `DragGesture`, `MagnifyGesture`, `RotateGesture`, a swipe built from a drag, a double tap or a multi-finger gesture. Report them when the view has no `.accessibilityAction(named:_:)` or `.accessibilityActions`, no `.contextMenu` with the same action, and no visible control that does the same thing. Also flag list rows whose `.swipeActions` or `.onDelete` actions have no onscreen route, such as an `EditButton` or a button on the detail screen.

**Why.** People with limited dexterity, and people who use VoiceOver, Voice Control or Switch Control, may not be able to drag, hold or use several fingers. Apple's HIG asks that core functionality work through more than one kind of physical interaction, with an onscreen way to get the same result, such as a button as well as a swipe to dismiss. The Voice Control criteria ask that controls revealed by a swipe or long press stay reachable, for example through a custom action, and the VoiceOver criteria suggest a custom action for long presses and context menus.

**Correct code.**

```swift
CardView(card: card)
    .gesture(
        DragGesture(minimumDistance: 30).onEnded { value in
            if value.translation.width < -80 { archive(card) }
        }
    )
    .accessibilityAction(named: "Archive") { archive(card) }

// The swipe stays as a shortcut. The button is the route everyone can use.
Button("Archive", systemImage: "archivebox") { archive(card) }
```

## A11Y-A11Y-006 - Make charts accessible to VoiceOver

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple App Store Connect Help: VoiceOver evaluation criteria](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/voiceover-evaluation-criteria/)
**Retrieved:** 2026-11-07
**Standards note:** WCAG 2.2 SC 1.1.1 Non-text Content, Level A.

**Check.** Flag charts drawn with `Path`, `Canvas`, stacks of shapes, or shown as an `Image`, that have no `.accessibilityChartDescriptor(_:)`, no `.accessibilityRepresentation(representation:)` and no label or nearby text that says what the data shows. In Swift Charts, flag marks whose values need a unit, a date format or other context to make sense when spoken and that set neither `.accessibilityLabel(...)` nor `.accessibilityValue(...)`. Also flag charts hidden with `.accessibilityHidden(true)` that have no text alternative.

**Why.** A VoiceOver user cannot see the shape of a chart, only what the app exposes. Apple's VoiceOver criteria ask that charts carry accessibility information through a chart API or, at minimum, a reasonably complete text alternative. Swift Charts marks accept `accessibilityLabel` and `accessibilityValue` (iOS 16+). For custom charts, `accessibilityChartDescriptor(_:)` (iOS 15+) supplies the data that VoiceOver needs to build an Audio Graph.

**Correct code.**

```swift
import Charts
import SwiftUI

struct DaySteps: Identifiable {
    let id = UUID()
    let date: Date
    let steps: Int
}

struct StepsChart: View {
    let days: [DaySteps]

    var body: some View {
        Chart(days) { day in
            BarMark(
                x: .value("Day", day.date, unit: .day),
                y: .value("Steps", day.steps)
            )
            .accessibilityLabel(day.date.formatted(.dateTime.weekday(.wide)))
            .accessibilityValue("\(day.steps) steps")
        }
    }
}
```

## A11Y-A11Y-007 - Announce temporary status messages

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple App Store Connect Help: VoiceOver evaluation criteria](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/voiceover-evaluation-criteria/)
**Retrieved:** 2026-11-07
**Standards note:** WCAG 2.2 SC 4.1.3 Status Messages, Level AA.

**Check.** Flag custom toasts, snackbars, banners and inline status text ("Saved", "Copied", "Upload failed") that appear through a state change without taking focus and post no `AccessibilityNotification.Announcement(...)` when they appear. System `.alert` and `.confirmationDialog` presentations are out of scope.

**Why.** A banner that slides in and fades out never reaches a VoiceOver user unless the app announces it. Apple's VoiceOver criteria ask that temporary status banners and important in-app alerts reach VoiceOver users in a timely but non-disruptive way, often with an `AccessibilityNotification`. `AccessibilityNotification.Announcement` needs iOS 17 or later.

**Correct code.**

```swift
@State private var toast: String?

func didSaveDraft() {
    let message = String(localized: "Draft saved")
    toast = message
    AccessibilityNotification.Announcement(message).post()
}
```

## A11Y-A11Y-008 - Keep accessibility text localizable

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple Developer: LocalizedStringKey](https://developer.apple.com/documentation/swiftui/localizedstringkey)
**Retrieved:** 2026-11-07

**Check.** In apps that ship more than one language (a String Catalog or `.lproj` folders for several locales), flag `.accessibilityLabel`, `.accessibilityHint`, `.accessibilityValue`, `.accessibilityInputLabels` and `.accessibilityAction(named:)` calls that receive a `String` variable or constant holding fixed text, such as `let closeLabel = "Close"` or a `String` built by interpolation. User content and values that come from a formatter are fine as plain strings.

**Why.** SwiftUI looks up a translation when it receives a string literal, which it turns into a `LocalizedStringKey`. Apple's `LocalizedStringKey` documentation says that passing a `String` variable to the matching `StringProtocol` overload avoids localization. The spoken label then stays in the development language for VoiceOver and Voice Control users in every other locale, even when the visible text is translated. Xcode also leaves a plain `let closeLabel = "Close"` out of the String Catalog, because Apple's Xcode localization guide says Swift code outside SwiftUI's views has to use `String(localized:)` for a string to be localizable.

**Correct code.**

```swift
// A literal becomes a LocalizedStringKey, so SwiftUI looks up the translation.
Button(action: removeItem) {
    Image(systemName: "trash")
}
.accessibilityLabel("Remove from cart")

// Text built in code: localize it before passing it on as a String.
let hint = String(localized: "Removes \(item.name) from your cart")
CartRow(item: item)
    .accessibilityHint(hint)
```

## A11Y-A11Y-009 - Keep automatic caption and audio description selection

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple Developer: appliesMediaSelectionCriteriaAutomatically](https://developer.apple.com/documentation/avfoundation/avplayer/appliesmediaselectioncriteriaautomatically)
**Retrieved:** 2026-11-07
**Standards note:** WCAG 2.2 SC 1.2.2 Captions (Prerecorded), Level A, and SC 1.2.5 Audio Description (Prerecorded), Level AA.

**Check.** Flag `appliesMediaSelectionCriteriaAutomatically = false` on an `AVPlayer`, `select(nil, in:)` on a legible or audible `AVMediaSelectionGroup`, and code that picks a subtitle or audio option when an item loads without reading the user's settings. List video in common tasks that plays outside AVFoundation, such as web embeds, GIF or image-sequence clips and third-party players, for a manual captions check, because a static scan cannot tell whether it follows the system settings.

**Why.** By default, `AVPlayer` applies media selection criteria based on the system accessibility preferences, so captions and audio descriptions come on when the person has turned them on in Settings. Apple's Captions and Audio Descriptions criteria ask apps to enable both by default when they detect those settings. Turning automatic selection off, or forcing a track on load, undoes that. People can also set how captions look in Accessibility settings, and the Captions criteria name braille displays as one place captions go. Captions burned into the picture ignore those settings and never reach a braille display, so ship a caption track as well.

**Correct code.**

```swift
import AVKit
import SwiftUI

struct TrailerView: View {
    let url: URL
    @State private var player: AVPlayer?

    var body: some View {
        VideoPlayer(player: player)
            .task { player = AVPlayer(url: url) }
    }
}
```
