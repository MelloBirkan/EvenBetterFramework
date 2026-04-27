# 2 Plan Validation

## Role

Stress-test `ios-ux-plan.md` before ticketing or implementation.

## Process

1. Read `.evenbetter/<feature-name>/ios-ux-plan.md`.
2. Inspect the current codebase for feasibility: existing navigation, shared components, themes, forms, custom controls, and minimum iOS version.
3. Read `official-sources.md` and consult Apple sources for any non-obvious HIG or accessibility claim.
4. Validate the plan against the checklist below.
5. Present findings by severity and ask closed disposition questions for unresolved tradeoffs. Ask additional multiple-choice questions when validation exposes hidden assumptions, edge cases, or missing review evidence; this phase can reasonably add 3-10 questions when the plan is complex.
6. Update `ios-ux-plan.md` only after alignment.

## Validation Checklist

- User flow has a clear entry, primary task, completion state, and failure state.
- Screen structure preserves information hierarchy and native iOS conventions.
- Dynamic Type behavior is explicit for large accessibility sizes.
- VoiceOver labels, grouping, reading order, and custom actions are addressed where needed.
- Touch targets, gesture alternatives, keyboard, Voice Control, and Switch Control are not ignored.
- Color and typography choices use semantic/system behavior or explain the exception.
- SwiftUI implementation direction matches local app patterns.
- Screenshot or simulator validation needs are recorded.

## Output

Either confirm the plan is ready for ticketing or revise the plan with a short "Validation Updates" section. Do not create implementation tickets in this stage.
