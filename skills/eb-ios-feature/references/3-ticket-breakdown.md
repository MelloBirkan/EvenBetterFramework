# 3 Ticket Breakdown

## Role

Convert `ios-ux-plan.md` into story-sized UX implementation tickets.

## Process

1. Read `.evenbetter/<feature-name>/ios-ux-plan.md`.
2. Inspect current code if needed to identify integration points and likely files.
3. Create `.evenbetter/<feature-name>/tickets/` if needed.
4. Write `UX-TICKET-NNN.md` files in dependency order.

## Ticket Template

```markdown
# UX-TICKET-NNN: <Title>

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

## Ticket Rules

- Keep tickets small enough to implement and validate independently.
- Put shared component or design-system changes before screen-level tickets.
- Include screenshot validation tickets when visual evidence is required.
- Include accessibility acceptance criteria in every ticket that touches UI.
- Do not create generic polish tickets without a concrete outcome.
