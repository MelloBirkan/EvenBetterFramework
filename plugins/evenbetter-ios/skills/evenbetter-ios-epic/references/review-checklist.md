# Review Checklist

Use this checklist for `8-ux-implementation-review` and whenever a user asks for a multi-screen iOS UX, HIG, accessibility, or screenshot review. Default to plan + visual + code review.

## Evidence

- Read `.evenbetter/<epic-name>/ios-ux-brief.md`, `screen-flows.md`, `ios-hig-tech-plan.md`, and relevant `UX-TICKET-NNN.md` files.
- Inspect changed SwiftUI/iOS code with `git diff`, paths from tickets, or user-provided files.
- Review screenshots when available. If missing, request only the states needed to resolve visual uncertainty.
- Consult `official-sources.md` for current Apple links and relevant local iOS skills.

## Severity

- Blocker: core flow is inaccessible, impossible, data-loss-prone, or conflicts with an agreed source spec.
- High: likely HIG/accessibility regression affecting many users, multiple screens, or assistive technology users.
- Medium: meaningful UX gap with a clear fix, but the core flow still works.
- Low: polish, consistency, or documentation issue.
- Validated: explicitly confirm important planned behavior that works.

## Cross-Screen UX Review

- Flow coherence: entry, orientation, task progression, completion, and cancellation are clear.
- Navigation: tabs, sidebars, stacks, sheets, and deep links match platform expectations and do not fight each other.
- Information architecture: primary objects and actions stay consistent across screens.
- State strategy: loading, empty, error, permission, offline, success, and destructive states are covered.
- Adaptivity: iPhone, iPad, rotation, keyboard, safe areas, Dynamic Island, and large text sizes are handled.
- Consistency: titles, toolbar placement, primary/destructive actions, icons, and terminology are stable across screens.

## Accessibility Review

- Dynamic Type strategy applies across all text-heavy screens and reflows at accessibility sizes.
- VoiceOver labels, grouping, headings, rotor opportunities, values, hints, and custom actions are planned and implemented where needed.
- Touch targets have at least a 44x44 pt hit region on iOS unless a standard component guarantees it.
- Important gestures have visible alternatives.
- Color, contrast, and status indicators do not rely on color alone.
- Keyboard, Switch Control, Voice Control, pointer, and focus behavior are not blocked by custom UI.
- Motion-heavy transitions respect Reduce Motion or have a calmer fallback.

## Code and Architecture Review

- Prefer SwiftUI-native app architecture: TabView, NavigationStack, NavigationSplitView, sheets, and environment injection where appropriate.
- Preserve per-tab navigation history when the app uses tabs.
- Centralize shared route and sheet mapping when the flow spans multiple screens.
- Keep feature screens decomposed; use `evenbetter-swiftui-view-refactor` for large views or unstable state.
- Use `evenbetter-swiftui-ui-patterns` for app wiring, navigation, sheets, forms, controls, theming, async state, and previews.
- Gate iOS 26+ Liquid Glass with availability and use `evenbetter-swiftui-liquid-glass` for review.
- Use `evenbetter-ios-app-intents` when system surfaces are in scope.

## Output

Write `.evenbetter/<epic-name>/ios-ux-review.md` when the stage is a formal review. Lead with findings ordered by severity, include file/screenshot/spec references, cite Apple sources for HIG claims, and finish with validated behavior plus any screenshot or test gaps.
