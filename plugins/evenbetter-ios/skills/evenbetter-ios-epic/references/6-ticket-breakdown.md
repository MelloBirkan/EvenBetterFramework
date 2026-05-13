# 6 Ticket Breakdown

## Role

Convert the iOS UX brief, screen flows, and HIG technical plan into story-sized UX implementation tickets.

## Process

1. Read `ios-ux-brief.md`, `screen-flows.html`, and `ios-hig-tech-plan.md`.
2. Inspect current code if needed to identify integration points and likely files.
3. Confirm `0-trigger-workflow`, `1-ios-ux-brief`, `2-screen-flows`, `3-ux-prd-validation`, `4-ios-hig-tech-plan`, and `5-architecture-validation` have closed material gaps and uncommunicated assumptions. If not, return to the relevant phase and ask more multiple-choice questions.
4. Before creating tickets, verify each planned ticket can trace to a specific brief requirement, flow step, accessibility requirement, and technical-plan decision.
5. Create `.evenbetter/<epic-name>/tickets/` if needed.
6. Write `UX-TICKET-NNN.md` files in dependency order.

## Ticket Readiness Gate

Return to the relevant question stage before ticketing if any ticket would need to decide:

- Which screens or surfaces are included.
- Whether a destination is pushed, tab-rooted, sheet-based, popover-based, full-screen, split-view, or externally entered.
- What happens after completion, cancellation, failed submission, permission denial, offline mode, or destructive action.
- What Dynamic Type, VoiceOver, gesture/input, contrast, or motion behavior is required.
- What screenshot, simulator, preview, or code-review evidence proves acceptance.

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

Every ticket file must start with the `## Status` section above and an unchecked `- [ ] Completed` checkbox. The `7-execute` stage flips it to `- [x] Completed` only after the ticket is implemented and its acceptance criteria pass, so anyone scanning `tickets/` can see at a glance which tickets are still open.

## Ticket Rules

- Put navigation, routing, theming, and shared accessibility foundations before screen-level tickets.
- Keep tickets independently reviewable.
- Include screenshot validation tickets for representative default, large text, dark mode, error, empty, and completion states when needed.
- Include accessibility acceptance criteria in every ticket that touches UI.
- Avoid tickets that merely say "polish"; name the specific HIG or accessibility outcome.
- Do not hide flow-discovery work inside implementation tickets. Send unresolved decisions back to the brief, flow, validation, or technical-plan stage.
