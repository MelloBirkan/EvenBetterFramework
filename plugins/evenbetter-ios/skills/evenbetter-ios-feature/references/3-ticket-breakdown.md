# 3 Ticket Breakdown

## Role

Convert `ios-ux-plan.md` into story-sized UX implementation tickets.

## Process

1. Read `.evenbetter/<feature-name>/ios-ux-plan.md`.
2. Inspect current code if needed to identify integration points and likely files.
3. Confirm `0-trigger-workflow`, `1-ux-plan`, `2-plan-validation`, and any applicable `5-ux-implementation-review` have closed material gaps and uncommunicated assumptions. If not, return to the relevant phase and ask more multiple-choice questions.
4. Create `.evenbetter/<feature-name>/tickets/` if needed.
5. Write `UX-TICKET-NNN.md` files in dependency order.

## Ticket Template

```markdown
# UX-TICKET-NNN: <Title>

## Status
- [ ] Completed

## Goal
<One concise outcome.>

## Scope
- Included:
- Excluded:

## UX and Accessibility Requirements
- HIG behavior:
- Dynamic Type:
- VoiceOver:
- Touch targets and gestures:
- States:

## Implementation Notes
- Native SwiftUI components or local patterns to prefer:
- Related iOS skills:
- Files or areas likely affected:

## Acceptance Criteria
- <Observable behavior or reviewable code outcome.>

## Validation
- Build/test/screenshot checks required:
```

Every ticket file must start with the `## Status` section above and an unchecked `- [ ] Completed` checkbox. The `4-execute` stage flips it to `- [x] Completed` only after the ticket is implemented and its acceptance criteria pass, so anyone scanning `tickets/` can see at a glance which tickets are still open.

## Ticket Rules

- Keep tickets small enough to implement and validate independently.
- Put shared component or design-system changes before screen-level tickets.
- Include screenshot validation tickets when visual evidence is required.
- Include accessibility acceptance criteria in every ticket that touches UI.
- Do not create generic polish tickets without a concrete outcome.
