---
name: swiftui-accessibility
description: "Accessibility analysis rules for SwiftUI projects following Apple Human Interface Guidelines and WCAG"
---

# Accessibility Rules — SwiftUI (Apple HIG & WCAG)

## A11Y-UI-001: Add `.accessibilityLabel` to Images and Icon Buttons

- **What to check:** All `Image` views and icon-only `Button` instances must have an `.accessibilityLabel()` that describes their purpose.
- **Why it matters:** Without labels, VoiceOver announces images as "image" and icon buttons as "button", giving users no information about what they represent or do.
- **Correct code example:**
  ```swift
  Button(action: { share() }) {
      Image(systemName: "square.and.arrow.up")
  }
  .accessibilityLabel("Share")
  ```

## A11Y-UI-002: Use `.accessibilityHidden(true)` for Decorative Elements

- **What to check:** Decorative images, dividers, and visual-only elements should be hidden from VoiceOver using `.accessibilityHidden(true)`.
- **Why it matters:** Decorative elements clutter VoiceOver navigation and slow down users who rely on assistive technology. Hiding them streamlines the experience.
- **Correct code example:**
  ```swift
  Image("decorative-background")
      .accessibilityHidden(true)
  ```

## A11Y-UI-003: Use `.accessibilityElement(children: .combine)`

- **What to check:** Groups of related elements (e.g., a label + value pair, an icon + text) should use `.accessibilityElement(children: .combine)` to be announced as a single unit.
- **Why it matters:** Without combining, VoiceOver announces each child separately, fragmenting the context and making it harder for users to understand related information.
- **Correct code example:**
  ```swift
  HStack {
      Image(systemName: "star.fill")
      Text("4.5 out of 5")
  }
  .accessibilityElement(children: .combine)
  ```

## A11Y-UX-001: Support Reduce Motion

- **What to check:** Animations should respect the user's "Reduce Motion" setting. Use `@Environment(\.accessibilityReduceMotion)` to conditionally disable or simplify animations.
- **Why it matters:** Motion-sensitive users experience discomfort or nausea from animations. HIG and WCAG require respecting this preference.
- **Correct code example:**
  ```swift
  @Environment(\.accessibilityReduceMotion) var reduceMotion

  var body: some View {
      ContentView()
          .animation(reduceMotion ? nil : .easeInOut, value: isExpanded)
  }
  ```

## A11Y-UX-002: Add `.accessibilityHint()` for Non-Obvious Actions

- **What to check:** Interactive elements whose action is not immediately clear from the label should include `.accessibilityHint()` to describe what will happen.
- **Why it matters:** Hints provide VoiceOver users with additional context about what an action does before they activate it, reducing uncertainty.
- **Correct code example:**
  ```swift
  Button("Order") { placeOrder() }
      .accessibilityLabel("Order")
      .accessibilityHint("Places your order and proceeds to payment")
  ```

## A11Y-A11Y-001: Add `.accessibilityAddTraits(.isButton)` to Custom Interactives

- **What to check:** Custom interactive views (views with `.onTapGesture` that are not `Button`) must add `.accessibilityAddTraits(.isButton)`.
- **Why it matters:** Without the button trait, VoiceOver does not announce the element as interactive, leaving users unaware they can tap it.
- **Correct code example:**
  ```swift
  Text("Tap me")
      .onTapGesture { doSomething() }
      .accessibilityAddTraits(.isButton)
      .accessibilityLabel("Perform action")
  ```

## A11Y-A11Y-002: Use `.accessibilityValue()` for Stateful Controls

- **What to check:** Controls that have a current state (sliders, steppers, toggles, progress indicators) should use `.accessibilityValue()` to announce their current value.
- **Why it matters:** Without an accessibility value, VoiceOver users cannot determine the current state of a control without visual inspection.
- **Correct code example:**
  ```swift
  Slider(value: $volume, in: 0...100)
      .accessibilityValue("\(Int(volume)) percent")
  ```

## A11Y-A11Y-003: Post Screen Change Notifications

- **What to check:** When significant screen content changes (e.g., after loading, after a navigation event, after an error appears), post `UIAccessibility.Notification.screenChanged` to move VoiceOver focus.
- **Why it matters:** Without screen change notifications, VoiceOver focus may remain on stale or removed elements, stranding users.
- **Correct code example:**
  ```swift
  func onContentLoaded() {
      UIAccessibility.post(notification: .screenChanged, argument: nil)
  }
  ```
