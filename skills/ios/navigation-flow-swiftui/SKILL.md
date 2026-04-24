---
description: "Navigation and flow analysis rules for SwiftUI projects following Apple Human Interface Guidelines"
---

# Navigation & Flow Rules — SwiftUI (Apple HIG)

## NAV-UI-001: Use `NavigationStack` vs `NavigationSplitView` Appropriately

- **What to check:** Use `NavigationStack` for linear drill-down flows and `NavigationSplitView` for sidebar-based or multi-column layouts on iPad/Mac.
- **Why it matters:** HIG distinguishes between hierarchical (stack) and flat (split) navigation patterns. Using the wrong container produces awkward layouts, especially on larger screens.
- **Correct code example:**
  ```swift
  // iPhone: linear flow
  NavigationStack { /* ... */ }

  // iPad/Mac: sidebar + detail
  NavigationSplitView {
      SidebarView()
  } detail: {
      DetailView()
  }
  ```

## NAV-UI-002: Always Set `.navigationTitle`

- **What to check:** Every view pushed onto a `NavigationStack` should set `.navigationTitle()` to provide context to the user.
- **Why it matters:** HIG requires clear titles so users always know where they are in the app's hierarchy. Missing titles disorient users and break VoiceOver navigation announcements.
- **Correct code example:**
  ```swift
  struct DetailView: View {
      var body: some View {
          ScrollView { /* ... */ }
              .navigationTitle("Item Details")
      }
  }
  ```

## NAV-UI-003: Preserve the Back Button

- **What to check:** Do not hide or replace the system back button with `.navigationBarBackButtonHidden(true)` without providing an equivalent accessible alternative.
- **Why it matters:** The system back button is universally understood and supports swipe-to-go-back gestures. Hiding it without replacement breaks navigation expectations and accessibility.
- **Correct code example:**
  ```swift
  // If custom back is needed, provide accessibility:
  .toolbar {
      ToolbarItem(placement: .navigationBarLeading) {
          Button(action: { dismiss() }) {
              Label("Back", systemImage: "chevron.left")
          }
      }
  }
  ```

## NAV-UX-002: Limit Navigation Depth to 3 Levels

- **What to check:** Navigation stacks should not exceed 3 levels of depth. Deeply nested views indicate a flat navigation pattern may be more appropriate.
- **Why it matters:** HIG recommends shallow hierarchies for discoverability. Deep stacks make it hard for users to maintain their mental model of where they are.
- **Correct code example:**
  ```swift
  // Level 1: List → Level 2: Detail → Level 3: Sub-detail (maximum)
  NavigationStack {
      ListView()
          .navigationDestination(for: Item.self) { item in
              DetailView(item: item)
          }
  }
  ```

## NAV-UX-001: Use `.sheet` for Creation Flows

- **What to check:** Content creation flows (new item, compose, edit) should use `.sheet` modals rather than pushing onto the navigation stack.
- **Why it matters:** HIG specifies that modal sheets indicate a separate task context. Pushing creation flows onto the stack conflates navigation with task modality.
- **Correct code example:**
  ```swift
  .sheet(isPresented: $showCreate) {
      NavigationStack {
          CreateItemView()
              .toolbar {
                  ToolbarItem(placement: .cancellationAction) {
                      Button("Cancel") { showCreate = false }
                  }
              }
      }
  }
  ```

## NAV-A11Y-001: VoiceOver Focus Management

- **What to check:** After navigation transitions, VoiceOver focus should move to the new content. Use `UIAccessibility.post(notification: .screenChanged, argument: nil)` or `AccessibilityFocusState` to manage focus.
- **Why it matters:** Without focus management, VoiceOver users may be stranded on the previous screen's elements after a transition, unable to discover new content.
- **Correct code example:**
  ```swift
  @AccessibilityFocusState var isTitleFocused: Bool

  var body: some View {
      Text("New Screen Title")
          .accessibilityFocused($isTitleFocused)
          .onAppear { isTitleFocused = true }
  }
  ```

## NAV-A11Y-002: Modal Dismiss Button

- **What to check:** Every modal sheet must include a visible and accessible dismiss button (e.g., "Done", "Cancel", or "Close").
- **Why it matters:** Users relying on assistive technology may not be able to use swipe-to-dismiss gestures. A visible button ensures all users can exit the modal.
- **Correct code example:**
  ```swift
  .sheet(isPresented: $showSheet) {
      NavigationStack {
          ContentView()
              .toolbar {
                  ToolbarItem(placement: .confirmationAction) {
                      Button("Done") { showSheet = false }
                  }
              }
      }
  }
  ```
