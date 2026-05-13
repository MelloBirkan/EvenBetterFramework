# 3 UX PRD Validation

## Role

Validate the UX brief and screen flows before technical planning.

## Process

1. Read `ios-ux-brief.md` and `screen-flows.html`.
2. Read `official-sources.md` and consult Apple sources for any non-obvious HIG/accessibility claim.
3. Validate requirements against the checklist below.
4. Present findings by severity and ask closed disposition questions for unresolved tradeoffs. Ask additional multiple-choice questions when validation exposes hidden assumptions, edge cases, or missing review evidence; this phase can reasonably add 3-10 questions when the epic is complex.
5. If the gap belongs to audience, scope, platform, or accessibility baseline, return to `1-ios-ux-brief`. If the gap belongs to entry, screen sequence, presentation, completion, cancellation, recovery, or screenshots, return to `2-screen-flows`.
6. Update specs only after alignment.

## Validation Checklist

- Audience, jobs, and product success are clear.
- Screen inventory matches the requested epic scope.
- Entry points, exits, cancellation, and recovery are clear for every main flow.
- Each primary flow has an owning root or entry surface, presentation style, completion destination, and post-action state update.
- Navigation model is coherent and platform-native.
- Dynamic Type and VoiceOver implications are explicit across screens.
- Gesture alternatives, destructive actions, errors, empty states, and loading states are covered.
- Auth, permissions, offline/degraded behavior, and external entry points are covered or explicitly out of scope.
- iPad/adaptive scope is defined or explicitly deferred.
- Screenshots or simulator validation needs are recorded.

## Output

Either confirm the specs are ready for `4-ios-hig-tech-plan` or revise source specs with a short "Validation Updates" section. Do not create tickets in this stage. The workflow must still pass through `5-architecture-validation` before `6-ticket-breakdown`. Do not mark the PRD ready while any primary flow is missing entry, steps, completion, failure/cancellation, accessibility notes, or review evidence.
