---
corpus_version: development
domain: components-patterns
platform: ios
last_reviewed: 2026-11-07
---

# iOS SwiftUI Components And Patterns Corpus

Canonical EvenBetter iOS corpus clauses for this conformance domain. Each H2 heading is a stable clause ID used by the analyze, validate and repair skills and by benchmark outputs.

## COMP-UI-001 - Prefer Button over onTapGesture for actions

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple Developer: Button](https://developer.apple.com/documentation/swiftui/button)
**Retrieved:** 2026-11-07

**Check.** Flag tappable `Text`, `Image`, `HStack`, `VStack`, `ZStack`, or custom rows using `.onTapGesture` for primary actions where `Button` would provide native behavior.

**Why.** `Button` provides platform styling, input behavior, accessibility traits, and activation semantics.

**Correct code.**

```swift
Button {
    save()
} label: {
    Label("Save", systemImage: "checkmark")
}
```

## COMP-UI-002 - Use NavigationStack instead of NavigationView

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple Developer: Migrating to New Navigation Types](https://developer.apple.com/documentation/swiftui/migrating-to-new-navigation-types)
**Retrieved:** 2026-11-07

**Check.** Flag `NavigationView` in iOS SwiftUI code that can target modern navigation APIs.

**Why.** Apple recommends migrating to value-based `NavigationStack` and `NavigationSplitView` APIs for predictable modern navigation.

**Correct code.**

```swift
NavigationStack {
    SettingsView()
        .navigationTitle("Settings")
}
```

## COMP-UI-003 - Use confirmationDialog instead of actionSheet

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple HIG: Action Sheets](https://developer.apple.com/design/human-interface-guidelines/action-sheets)
**Retrieved:** 2026-11-07

**Check.** Flag `.actionSheet` usage.

**Why.** `confirmationDialog` is the modern SwiftUI API for presenting action choices in a platform-adaptive way.

**Correct code.**

```swift
.confirmationDialog("Choose an option", isPresented: $showOptions) {
    Button("Archive") { archive() }
    Button("Cancel", role: .cancel) {}
}
```

## COMP-UX-001 - Mark destructive buttons with role destructive

**Severity:** error
**Dimension:** ux
**Platform:** ios
**Source:** [Apple HIG: Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons)
**Retrieved:** 2026-11-07

**Check.** Flag `Button` actions named or implemented as delete, remove, reset, discard, revoke, erase, or sign out when they omit `role: .destructive`. Do not flag the confirming button of an alert that follows a destructive action the person chose on purpose, such as the Delete button in a "Delete this item?" alert raised by their own Delete tap: HIG Alerts reserves the destructive style for destructive actions people didn't deliberately choose. Buttons in confirmation dialogs and action sheets stay in scope.

**Why.** Destructive roles help the system present risk clearly and support safer user decisions.

**Correct code.**

```swift
Button("Delete Account", role: .destructive) {
    deleteAccount()
}
```

## COMP-UX-002 - Use alerts for high-consequence confirmations

**Severity:** warning
**Dimension:** ux
**Platform:** ios
**Source:** [Apple HIG: Alerts](https://developer.apple.com/design/human-interface-guidelines/alerts)
**Retrieved:** 2026-11-07

**Check.** Flag uncommon destructive actions that people can't undo, such as deleting an account, erasing all data, or permanently removing shared content, when they run immediately without an `.alert` confirmation or equivalent confirmation flow. Do not flag common destructive actions that people can undo, such as deleting a message or file that goes to a recoverable trash.

**Why.** Apple's alert guidance asks for an alert when people take an uncommon destructive action they can't undo, in case they started it by accident, and advises against alerts for common, undoable actions even when they are destructive. An alert that confirms a destructive action includes a Cancel button so people have a clear, safe way out.

**Correct code.**

```swift
.alert("Delete Account?", isPresented: $showDeleteAlert) {
    Button("Delete") { deleteAccount() }
    Button("Cancel", role: .cancel) {}
} message: {
    Text("Your data is removed permanently. You can't undo this.")
}
```

## COMP-A11Y-001 - Prefer system controls over custom recreations

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple Developer: Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
**Retrieved:** 2026-11-07

**Check.** Flag custom toggles, sliders, steppers, segmented controls, tab controls, or pickers built from shapes and gestures when a native SwiftUI control would provide equivalent behavior.

**Why.** SwiftUI introspects common elements such as lists, text fields, sliders, and buttons and gives them accessibility labels and values by default. A control rebuilt from shapes and gestures loses that support, along with platform focus, localization, and interaction behavior. When a custom look is required, give the native control a custom style (a custom `ToggleStyle` keeps the accessibility of `Toggle`), or use `accessibilityRepresentation(representation:)`.

**Correct code.**

```swift
Toggle("Notifications", isOn: $notificationsEnabled)
```

## COMP-A11Y-002 - Add button traits to custom buttons

**Severity:** error
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple Developer: accessibilityAddTraits](https://developer.apple.com/documentation/swiftui/view/accessibilityaddtraits(_:))
**Retrieved:** 2026-11-07

**Check.** Flag custom interactive views that use gestures or custom hit testing as buttons but omit `.accessibilityAddTraits(.isButton)`.

**Why.** VoiceOver users need the correct role to understand that an element activates an action.

**Correct code.**

```swift
HStack {
    Image(systemName: "star")
    Text("Favorite")
}
.onTapGesture { favorite() }
.accessibilityElement(children: .combine)
.accessibilityAddTraits(.isButton)
```
