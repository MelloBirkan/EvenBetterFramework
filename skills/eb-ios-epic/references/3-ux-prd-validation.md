# 3 UX PRD Validation

## Role

Validate the UX brief and screen flows before technical planning.

## Process

1. Read `ios-ux-brief.md` and `screen-flows.md`.
2. Read `official-sources.md` and consult Apple sources for any non-obvious HIG/accessibility claim.
3. Validate requirements against the checklist below.
4. Present findings by severity and ask closed disposition questions for unresolved tradeoffs. Ask additional multiple-choice questions when validation exposes hidden assumptions, edge cases, or missing review evidence; this phase can reasonably add 3-10 questions when the epic is complex.
5. Update specs only after alignment.

## Validation Checklist

- Audience, jobs, and product success are clear.
- Screen inventory matches the requested epic scope.
- Entry points, exits, cancellation, and recovery are clear for every main flow.
- Navigation model is coherent and platform-native.
- Dynamic Type and VoiceOver implications are explicit across screens.
- Gesture alternatives, destructive actions, errors, empty states, and loading states are covered.
- iPad/adaptive scope is defined or explicitly deferred.
- Screenshots or simulator validation needs are recorded.

## Output

Either confirm the specs are ready for `4-ios-hig-tech-plan` or revise source specs with a short "Validation Updates" section. Do not create tickets in this stage. The workflow must still pass through `5-architecture-validation` before `6-ticket-breakdown`.
