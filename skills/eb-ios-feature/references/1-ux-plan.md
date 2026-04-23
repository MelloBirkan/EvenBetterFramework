# 1 UX Plan

## Role

Create an HIG-aware, accessibility-first UX plan for a small iOS feature or single SwiftUI screen.

## Process

1. Read the gathered requirements and inspect the current codebase for nearby SwiftUI patterns, navigation, styling, and shared components.
2. Read `official-sources.md` and `question-patterns.md`.
3. Use `$swiftui-ui-patterns` references as needed for navigation, sheets, forms, controls, theming, Dynamic Type, async state, or previews.
4. Ask multiple-choice questions for unresolved UX decisions before drafting.
5. Write `.evenbetter/<feature-name>/ios-ux-plan.md`.

## Plan Template

Use only sections relevant to the feature.

```markdown
# iOS UX Plan: <Feature Name>

## Summary
<3-6 sentences describing the user goal, target screen, and expected outcome.>

## User Flow
- Entry:
- Primary action:
- Completion:
- Failure or cancellation:

## Screen Structure
- Primary content:
- Secondary content:
- Navigation and presentation:
- Empty/loading/error states:

## HIG and Accessibility Contract
- Dynamic Type:
- VoiceOver labels, grouping, and reading order:
- Touch targets and gesture alternatives:
- Color, contrast, and semantic styling:
- Motion and feedback:

## SwiftUI Implementation Direction
- Preferred native components:
- State and navigation ownership:
- Local iOS skills to use:
- Screenshot or simulator validation needed:

## Sources
- Apple HIG/source links relevant to this plan.
```

## Planning Defaults

- Prefer native SwiftUI controls and platform navigation over custom controls.
- Prefer system text styles, semantic colors, and scalable layouts.
- Ensure every important gesture has a visible alternative.
- Keep destructive actions visually distinct and confirmed or undoable.
- Preserve primary content and actions at large accessibility text sizes.

## Next Step

Offer `3-ticket-breakdown` as the usual next step, or `2-plan-validation` when the feature has complex navigation, custom gestures, high accessibility risk, or uncertain HIG tradeoffs.
