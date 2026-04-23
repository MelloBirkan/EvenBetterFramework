# 4 iOS HIG Tech Plan

## Role

Create the technical plan that turns the iOS UX brief and screen flows into a SwiftUI implementation architecture aligned with Apple HIG and accessibility requirements.

## Process

1. Read `ios-ux-brief.md` and `screen-flows.md`.
2. Inspect the codebase for app entry points, navigation, environment dependencies, theming, shared components, and minimum OS.
3. Use `$swiftui-ui-patterns` references for app wiring, TabView, NavigationStack, sheets, split views, forms, controls, theming, async state, and previews.
4. Use `official-sources.md` for Apple documentation links.
5. Ask multiple-choice questions for unresolved architecture or UX implementation tradeoffs. Ask roughly 3-10 questions in this phase when needed to close state, navigation, accessibility, adaptivity, and review-evidence assumptions.
6. Write `.evenbetter/<epic-name>/ios-hig-tech-plan.md`.

## Plan Template

```markdown
# iOS HIG Technical Plan: <Epic Name>

## Summary
<Short implementation direction grounded in the UX specs and codebase.>

## Navigation and Presentation
- Top-level structure:
- Routes and sheet ownership:
- Completion/cancellation behavior:
- iPad/adaptive behavior:

## Screen Architecture
- Screens and responsibilities:
- Shared components:
- State ownership and dependencies:

## Accessibility Architecture
- Dynamic Type:
- VoiceOver labels, grouping, headings, and custom actions:
- Gesture alternatives and input methods:
- Color/contrast and motion:

## Implementation Sequence
- Foundation:
- Screen delivery order:
- Review/screenshot checkpoints:

## Sources
- Apple links and local iOS skills used.
```

## Technical Defaults

- Prefer one `NavigationStack` per tab when tabs need independent history.
- Prefer `sheet(item:)` and enum-driven modal routing when multiple sheets exist.
- Prefer shared semantic theme tokens over raw colors.
- Prefer previews and simulator screenshots for representative states.
- Use App Intents only for user-valued system actions, not every screen.

## Next Step

Recommend `5-architecture-validation`. Do not route from the technical plan directly to `6-ticket-breakdown`; architecture validation is required before ticketing.
