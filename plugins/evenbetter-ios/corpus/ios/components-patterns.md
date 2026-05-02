---
corpus_version: development
domain: components-patterns
platform: ios
last_reviewed: 2026-05-02
---

# iOS SwiftUI Components And Patterns Corpus

Canonical EvenBetter iOS corpus clauses for this conformance domain. Each H2 heading is a stable clause ID used by analyzer, validator, fixer, and benchmark outputs.

## COMP-UI-001 - Prefer Button over onTapGesture for actions

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple Developer: Button](https://developer.apple.com/documentation/swiftui/button)
**Retrieved:** 2026-05-02

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
**Retrieved:** 2026-05-02

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
**Retrieved:** 2026-05-02

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
**Retrieved:** 2026-05-02

**Check.** Flag `Button` actions named or implemented as delete, remove, reset, discard, revoke, erase, or sign out when they omit `role: .destructive`.

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
**Retrieved:** 2026-05-02

**Check.** Flag immediate destructive or irreversible actions without a nearby `.alert` confirmation or equivalent confirmation flow.

**Why.** Confirmations reduce accidental data loss and make destructive choices explicit.

**Correct code.**

```swift
.alert("Delete item?", isPresented: $showDeleteAlert) {
    Button("Delete", role: .destructive) { deleteItem() }
    Button("Cancel", role: .cancel) {}
}
```

## COMP-A11Y-001 - Prefer system controls over custom recreations

**Severity:** warning
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple HIG: Components](https://developer.apple.com/design/human-interface-guidelines/components)
**Retrieved:** 2026-05-02

**Check.** Flag custom toggles, sliders, steppers, segmented controls, tab controls, or pickers built from shapes and gestures when a native SwiftUI control would provide equivalent behavior.

**Why.** System controls inherit platform accessibility, focus, VoiceOver, localization, and interaction behavior.

**Correct code.**

```swift
Toggle("Notifications", isOn: $notificationsEnabled)
```

## COMP-A11Y-002 - Add button traits to custom buttons

**Severity:** error
**Dimension:** accessibility
**Platform:** ios
**Source:** [Apple Developer: accessibilityAddTraits](https://developer.apple.com/documentation/swiftui/view/accessibilityaddtraits(_:))
**Retrieved:** 2026-05-02

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
