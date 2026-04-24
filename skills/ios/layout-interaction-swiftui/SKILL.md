---
description: "Layout and interaction analysis rules for SwiftUI projects following Apple Human Interface Guidelines"
---

# Layout & Interaction Rules — SwiftUI (Apple HIG)

## LAY-UI-001: 44x44pt Minimum Tap Targets

- **What to check:** All interactive elements (buttons, toggles, links, custom tap areas) must have a minimum tap target size of 44x44 points.
- **Why it matters:** HIG specifies 44x44pt as the minimum comfortable touch target. Smaller targets cause user frustration and accidental taps, especially for users with motor impairments.
- **Correct code example:**
  ```swift
  Button(action: { doSomething() }) {
      Image(systemName: "star")
          .frame(minWidth: 44, minHeight: 44)
  }
  ```

## LAY-UI-002: Respect Safe Areas

- **What to check:** Content should not extend behind the notch, home indicator, or status bar unless intentionally (e.g., background images). Verify that `.ignoresSafeArea()` is not used on text or interactive content.
- **Why it matters:** Content behind safe areas is obscured or unreachable. HIG requires that all interactive and readable content remains within safe area insets.
- **Correct code example:**
  ```swift
  VStack {
      Text("Content within safe area")
      Button("Action") { /* ... */ }
  }
  // Background images may ignore safe area:
  .background(
      Image("bg").ignoresSafeArea()
  )
  ```

## LAY-UI-003: Use `ProgressView` for Loading States

- **What to check:** Loading states should use the system `ProgressView` component (spinning or linear) rather than custom loading indicators.
- **Why it matters:** System progress indicators are recognized by users, support accessibility announcements, and adapt to the platform appearance automatically.
- **Correct code example:**
  ```swift
  if isLoading {
      ProgressView("Loading...")
  } else {
      ContentView()
  }
  ```

## LAY-UI-004: Provide Empty States

- **What to check:** Lists and collections should display a meaningful empty state view when there is no data, rather than showing a blank screen.
- **Why it matters:** Empty states guide users on what to do next and confirm the app is working. A blank screen is confusing and feels like a bug.
- **Correct code example:**
  ```swift
  if items.isEmpty {
      ContentUnavailableView(
          "No Items",
          systemImage: "tray",
          description: Text("Add your first item to get started.")
      )
  } else {
      List(items) { item in ItemRow(item: item) }
  }
  ```

## LAY-UX-001: Use `.confirmationDialog` for Destructive Actions

- **What to check:** Destructive actions triggered from list items or contextual menus should present a `.confirmationDialog` before executing.
- **Why it matters:** HIG requires confirmation for destructive actions to prevent accidental data loss, especially in swipe-to-delete and long-press contexts.
- **Correct code example:**
  ```swift
  .confirmationDialog("Delete this item?", isPresented: $showConfirm) {
      Button("Delete", role: .destructive) { deleteItem() }
      Button("Cancel", role: .cancel) { }
  }
  ```

## LAY-UX-002: Use `.sensoryFeedback()`

- **What to check:** Significant interactions (successful actions, errors, selections) should use `.sensoryFeedback()` to provide haptic feedback.
- **Why it matters:** Haptic feedback confirms actions and creates a more responsive, tactile user experience. HIG recommends haptics for meaningful interactions.
- **Correct code example:**
  ```swift
  Button("Save") { save() }
      .sensoryFeedback(.success, trigger: didSave)
  ```

## LAY-A11Y-001: 44x44pt Accessibility Enforcement

- **What to check:** Verify that all interactive elements meet the 44x44pt minimum even when content is smaller (e.g., small icon buttons). Use `.contentShape(Rectangle())` or padding to expand the tap area.
- **Why it matters:** Users with motor impairments need adequately sized touch targets. This is both a HIG and WCAG 2.5.5 requirement.
- **Correct code example:**
  ```swift
  Button(action: { toggle() }) {
      Image(systemName: "xmark")
          .font(.caption)
  }
  .frame(minWidth: 44, minHeight: 44)
  .contentShape(Rectangle())
  ```

## LAY-A11Y-002: Place Content Within Safe Areas

- **What to check:** Interactive and readable content must remain within safe area insets. Only decorative backgrounds should use `.ignoresSafeArea()`.
- **Why it matters:** Content placed behind safe areas (notch, home indicator) is obscured and unreachable for assistive technology users.
- **Correct code example:**
  ```swift
  ZStack {
      Color.blue.ignoresSafeArea() // decorative only
      VStack {
          Text("Safe content")
          Button("Tap me") { /* ... */ }
      }
  }
  ```
