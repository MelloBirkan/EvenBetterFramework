# 6 Ticket Breakdown

## Role

Convert the iOS UX brief, screen flows, and HIG technical plan into story-sized UX implementation tickets.

## Process

1. Read `ios-ux-brief.md`, `screen-flows.md`, and `ios-hig-tech-plan.md`.
2. Inspect current code if needed to identify integration points and likely files.
3. Confirm `0-trigger-workflow`, `1-ios-ux-brief`, `2-screen-flows`, `3-ux-prd-validation`, `4-ios-hig-tech-plan`, and `5-architecture-validation` have closed material gaps and uncommunicated assumptions. If not, return to the relevant phase and ask more multiple-choice questions.
4. Create `.evenbetter/<epic-name>/tickets/` if needed.
5. Write `UX-TICKET-NNN.md` files in dependency order.

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
- Cross-screen state:

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

- Put navigation, routing, theming, and shared accessibility foundations before screen-level tickets.
- Keep tickets independently reviewable.
- Include screenshot validation tickets for representative default, large text, dark mode, error, empty, and completion states when needed.
- Include accessibility acceptance criteria in every ticket that touches UI.
- Avoid tickets that merely say "polish"; name the specific HIG or accessibility outcome.
