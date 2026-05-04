# 1 UX Plan

## Role

Create an HIG-aware, accessibility-first UX plan for a small iOS feature or single SwiftUI screen.

## Process

1. Read the gathered requirements and inspect the current codebase for nearby SwiftUI patterns, navigation, styling, and shared components.
2. Read `official-sources.md` and `question-patterns.md`.
3. Use `evenbetter-swiftui-ui-patterns` references as needed for navigation, sheets, forms, controls, theming, Dynamic Type, async state, or previews.
4. Ask roughly 3-10 multiple-choice questions in this phase, across one or more rounds before drafting when complexity warrants it. Use early questions to close gaps and assumptions; use later questions to cover edge cases, failure states, accessibility risks, and screenshot/simulator evidence.
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

Recommend `2-plan-validation` as the next step. Do not send the workflow straight from planning to `3-ticket-breakdown`. Before ticket breakdown, the user should have answered enough phase-level questions to close gaps and uncommunicated assumptions; this can exceed 10 total questions across the pre-ticket flow. proceed to `3-ticket-breakdown` only after validation and any applicable review are complete or explicitly not applicable.
