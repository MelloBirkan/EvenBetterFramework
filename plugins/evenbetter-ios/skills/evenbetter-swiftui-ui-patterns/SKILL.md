---
name: evenbetter-swiftui-ui-patterns
description: >-
  Builds SwiftUI screens from component patterns and examples: navigation stacks, tabs, sheets, forms, lists,
  controls, search, async state and app wiring. Use when shaping navigation, state, layouts, controls or screen
  composition in a SwiftUI app. For visual direction and styling, use evenbetter-design.
---

# SwiftUI UI Patterns

> Paths in this skill and its references are relative to this SKILL.md's folder. The plugin corpus is at `../../corpus/`.

If current system, developer or user instructions conflict with this skill, follow them.

## Quick start

Choose a track based on your goal:

### Existing project

- Identify the feature or screen and the primary interaction model (list, detail, editor, settings, tabbed).
- Find a nearby example in the repo with `rg "TabView\("` or similar, then read the closest SwiftUI view.
- Apply local conventions: prefer SwiftUI-native state, keep state local when possible, and use environment injection for shared dependencies.
- Pick the matching entry in the component references below and follow its guidance.
- If the interaction reveals secondary content by dragging or scrolling the primary content away, read `references/scroll-reveal.md` before implementing gestures manually.
- Build the view with small, focused subviews and SwiftUI-native data flow.

### New project scaffolding

- Start with `references/app-wiring.md` to wire TabView + NavigationStack + sheets.
- Add a minimal `AppTab` and `RouterPath` based on the provided skeletons.
- Choose the next component reference based on the UI you need first (TabView, NavigationStack, Sheets).
- Expand the route and sheet enums as new screens are added.

## General rules to follow

- Use modern SwiftUI state (`@State`, `@Binding`, `@Observable`, `@Environment`) and avoid unnecessary view models.
- If the deployment target includes iOS 16 or earlier and cannot use the Observation API introduced in iOS 17, fall back to `ObservableObject` with `@StateObject` for root ownership, `@ObservedObject` for injected observation, and `@EnvironmentObject` only for truly shared app-level state.
- Prefer composition; keep views small and focused.
- Use async/await with `.task` and explicit loading/error states. For restart, cancellation, and debouncing guidance, read `references/async-state.md`.
- Keep shared app services in `@Environment`, but prefer explicit initializer injection for feature-local dependencies and models. For root wiring patterns, read `references/app-wiring.md`.
- Prefer the newest SwiftUI API that fits the deployment target and call out the minimum OS whenever a pattern depends on it.
- Maintain existing legacy patterns only when editing legacy files.
- Follow the project's formatter and style guide.
- Sheets: prefer `.sheet(item:)` over `.sheet(isPresented:)` when state represents a selected model. Avoid `if let` inside a sheet body. Sheets should own their actions and call `dismiss()` internally instead of forwarding `onCancel`/`onConfirm` closures.
- Scroll-driven reveals: prefer deriving a normalized progress value from scroll offset and driving the visual state from that single source of truth. Avoid parallel gesture state machines unless scroll alone cannot express the interaction.

## State ownership summary

Use the narrowest state tool that matches the ownership model:

| Scenario | Preferred pattern |
| --- | --- |
| Local UI state owned by one view | `@State` |
| Child mutates parent-owned value state | `@Binding` |
| Root-owned reference model on iOS 17+ | `@State` with an `@Observable` type |
| Child reads or mutates an injected `@Observable` model on iOS 17+ | Pass it explicitly as a stored property |
| Shared app service or configuration | `@Environment(Type.self)` |
| Legacy reference model on iOS 16 and earlier | `@StateObject` at the root, `@ObservedObject` when injected |

Choose the ownership location first, then pick the wrapper. Do not introduce a reference model when plain value state is enough.

## Cross-cutting references

- `references/navigationstack.md`: navigation ownership, per-tab history, and enum routing.
- `references/sheets.md`: centralized modal presentation and enum-driven sheets.
- `references/deeplinks.md`: URL handling and routing external links into app destinations.
- `references/app-wiring.md`: root dependency graph, environment usage, and app shell wiring.
- `references/async-state.md`: `.task`, `.task(id:)`, cancellation, debouncing, and async UI state.
- `references/previews.md`: `#Preview`, fixtures, mock environments, and isolated preview setup.
- `references/performance.md`: stable identity, observation scope, lazy containers, and render-cost guardrails.

## Component references

Read the one file that matches the component you are building:

| Component | Reference | Use when |
| --- | --- | --- |
| TabView | `references/tabview.md` | Building a tab-based app or any tabbed feature set. |
| NavigationStack | `references/navigationstack.md` | You need push navigation and programmatic routing, especially per-tab history. |
| Sheets and presentation | `references/sheets.md` | Local item-driven sheets, centralized modal routing, and sheet-owned actions. |
| Form and settings | `references/form.md` | Settings, grouped inputs, and structured data entry. |
| macOS Settings | `references/macos-settings.md` | A macOS Settings window built with SwiftUI's Settings scene. |
| Split views and columns | `references/split-views.md` | iPad and macOS multi-column layouts or custom secondary columns. |
| List and Section | `references/list.md` | Feed-style content and settings rows. |
| ScrollView and lazy stacks | `references/scrollview.md` | Custom layouts, horizontal scrollers, or grids. |
| Scroll-reveal detail surfaces | `references/scroll-reveal.md` | A detail screen reveals secondary content or actions as the user scrolls or swipes between full-screen sections. |
| Grids | `references/grids.md` | Icon pickers, media galleries, and tiled layouts. |
| Theming and Dynamic Type | `references/theming.md` | App-wide theme tokens, colors, and type scaling. |
| Controls (toggles, pickers, sliders) | `references/controls.md` | Settings controls and input selection. |
| Input toolbar (bottom anchored) | `references/input-toolbar.md` | Chat or composer screens with a sticky input bar. |
| Top bar overlays (iOS 26+ and fallback) | `references/top-bar.md` | Pinned selectors or pills above scroll content. |
| Overlay and toasts | `references/overlay.md` | Transient UI such as banners or toasts. |
| Focus handling | `references/focus.md` | Chaining fields and keyboard focus management. |
| Searchable | `references/searchable.md` | Native search UI with scopes and async results. |
| Async images and media | `references/media.md` | Remote media, previews, and media viewers. |
| Haptics | `references/haptics.md` | Tactile feedback tied to key actions. For HIG mapping of feedback types, use evenbetter-ios-haptics. |
| Matched transitions | `references/matched-transitions.md` | Smooth source-to-destination animations. |
| Deep links and URL routing | `references/deeplinks.md` | In-app navigation from URLs. |
| Title menus | `references/title-menus.md` | Filter or context menus in the navigation title. |
| Menu bar commands | `references/menu-bar.md` | Adding or customizing macOS and iPadOS menu bar commands. |
| Loading and placeholders | `references/loading-placeholders.md` | Redacted skeletons, empty states, and loading UX. |
| Lightweight clients | `references/lightweight-clients.md` | Small, closure-based API clients injected into stores. |

When no reference fits, follow the general rules above and the closest existing view in the project.

## Anti-patterns

- Giant views that mix layout, business logic, networking, routing, and formatting in one file.
- Multiple boolean flags for mutually exclusive sheets, alerts, or navigation destinations.
- Live service calls directly inside `body`-driven code paths instead of view lifecycle hooks or injected models/services.
- Reaching for `AnyView` to work around type mismatches that should be solved with better composition.
- Defaulting every shared dependency to `@EnvironmentObject` or a global router without a clear ownership reason.

## Workflow for a new SwiftUI view

1. Define the view's state, ownership location, and minimum OS assumptions before writing UI code.
2. Identify which dependencies belong in `@Environment` and which should stay as explicit initializer inputs.
3. Sketch the view hierarchy, routing model, and presentation points; extract repeated parts into subviews. For complex navigation, read `references/navigationstack.md`, `references/sheets.md`, or `references/deeplinks.md`. Build and fix compiler errors before moving on, because later steps are harder to debug on top of a broken build.
4. Implement async loading with `.task` or `.task(id:)`, plus explicit loading and error states when needed. Read `references/async-state.md` when the work depends on changing inputs or cancellation.
5. Add previews for the primary and secondary states, then add accessibility labels or identifiers when the UI is interactive. Read `references/previews.md` when the view needs fixtures or injected mock dependencies.
6. Validate with a build: confirm there are no compiler errors, check that previews render without crashing and that state changes reach the views that read them, and check that list identity and observation scope will not cause avoidable re-renders. Read `references/performance.md` if the screen is large, scroll-heavy, or frequently updated.
7. If the build fails, read the error, fix the identified issue (often a missing `@State`, an ambiguous `ViewBuilder` closure or a mismatched generic type), and rebuild before updating call sites. If a preview crashes, isolate the offending subview, confirm its state initialization is valid, and re-run the preview.

## Related skills and sources

- Apple's swiftui-specialist skill, which ships with Xcode 27, may also be installed. It covers SwiftUI API correctness and performance; use it alongside this skill when it is present.
- HIG and accessibility questions go to evenbetter-swiftui-accessibility, or straight to the corpus clauses listed in `../../corpus/index.json`.
- For visual direction (palette, type, layout identity), use evenbetter-design. For splitting an existing large view, use evenbetter-swiftui-view-refactor.
- When SwiftUI APIs, availability or platform guidance may have changed, check current Apple Developer documentation with the session's documentation or web tools. Apple's pages are rendered with JavaScript, so prefer a scraper that renders pages, or the JSON form `https://developer.apple.com/tutorials/data/documentation/<path>.json`.
