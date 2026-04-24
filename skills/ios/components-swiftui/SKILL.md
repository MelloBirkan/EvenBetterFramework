---
description: "UI component usage rules for SwiftUI projects following Apple Human Interface Guidelines"
---

# Component Usage Rules — SwiftUI (Apple HIG)

## COMP-UI-001: Use `Button` Instead of `.onTapGesture`

- **What to check:** Interactive elements should use `Button` rather than applying `.onTapGesture` to `Text` or `Image` views.
- **Why it matters:** `Button` provides built-in accessibility traits, highlight states, and keyboard support. `.onTapGesture` creates invisible touch targets that VoiceOver cannot identify as interactive.
- **Correct code example:**
  ```swift
  Button(action: { doSomething() }) {
      Label("Action", systemImage: "star")
  }
  ```

## COMP-UI-002: Use `NavigationStack` Instead of `NavigationView`

- **What to check:** Navigation containers should use `NavigationStack` (iOS 16+) rather than the deprecated `NavigationView`.
- **Why it matters:** `NavigationStack` provides type-safe navigation paths, better state management, and is the HIG-recommended approach. `NavigationView` is deprecated and has known layout issues.
- **Correct code example:**
  ```swift
  NavigationStack {
      List(items) { item in
          NavigationLink(value: item) {
              Text(item.name)
          }
      }
      .navigationDestination(for: Item.self) { item in
          DetailView(item: item)
      }
  }
  ```

## COMP-UI-003: Use `.confirmationDialog` Instead of `.actionSheet`

- **What to check:** Action sheets should use `.confirmationDialog` (iOS 15+) rather than the deprecated `.actionSheet` modifier.
- **Why it matters:** `.confirmationDialog` is the modern replacement that adapts correctly across platforms and device sizes. `.actionSheet` is deprecated.
- **Correct code example:**
  ```swift
  .confirmationDialog("Choose an action", isPresented: $showDialog) {
      Button("Option A") { /* ... */ }
      Button("Option B") { /* ... */ }
      Button("Cancel", role: .cancel) { }
  }
  ```

## COMP-UX-001: Use `role: .destructive` for Destructive Actions

- **What to check:** Buttons that perform destructive actions (delete, remove, discard) should use `role: .destructive` to visually indicate danger.
- **Why it matters:** The destructive role applies red styling automatically and signals to VoiceOver that the action is irreversible, following HIG guidance for destructive actions.
- **Correct code example:**
  ```swift
  Button("Delete", role: .destructive) {
      deleteItem()
  }
  ```

## COMP-UX-002: Use `.alert` for Confirmations

- **What to check:** Destructive or irreversible actions should present an `.alert` confirmation before proceeding.
- **Why it matters:** HIG requires confirmation for destructive actions to prevent accidental data loss. Skipping confirmation creates a poor user experience.
- **Correct code example:**
  ```swift
  .alert("Delete Item?", isPresented: $showAlert) {
      Button("Delete", role: .destructive) { deleteItem() }
      Button("Cancel", role: .cancel) { }
  } message: {
      Text("This action cannot be undone.")
  }
  ```

## COMP-A11Y-001: Prefer System Components

- **What to check:** Use system-provided components (e.g., `DatePicker`, `ColorPicker`, `PhotosPicker`, `ShareLink`) rather than building custom equivalents.
- **Why it matters:** System components follow HIG automatically, include built-in accessibility, adapt to platform conventions, and receive OS-level improvements.
- **Correct code example:**
  ```swift
  DatePicker("Select Date", selection: $date, displayedComponents: .date)
  ```

## COMP-A11Y-002: Add `.accessibilityAddTraits(.isButton)` to Custom Buttons

- **What to check:** Custom interactive views that act as buttons but are not `Button` instances should have `.accessibilityAddTraits(.isButton)`.
- **Why it matters:** Without the button trait, VoiceOver will not announce the element as interactive, leaving users unaware they can tap it.
- **Correct code example:**
  ```swift
  Text("Custom Action")
      .onTapGesture { doSomething() }
      .accessibilityAddTraits(.isButton)
      .accessibilityLabel("Perform custom action")
  ```
