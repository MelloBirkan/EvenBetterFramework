# 9 Revise Requirements

## Role

Propagate changed UX/accessibility requirements through the epic specs, tickets, and review notes.

## Process

1. Identify the source of the change: user decision, implementation discovery, screenshot review, Apple guidance, or technical constraint.
2. Read `ios-ux-brief.md`, `screen-flows.html`, `ios-hig-tech-plan.md`, relevant `UX-TICKET-NNN.md` files, and `ios-ux-review.md` if present.
3. Ask multiple-choice questions only for decisions that materially change user experience, accessibility, navigation, scope, or implementation order.
4. Update artifacts surgically.
5. Summarize what changed and which tickets now need implementation or review.

## Revision Rules

- Preserve previous decisions that still hold.
- Add a dated "Revision Notes" section when a change reverses or materially alters a prior decision.
- Update tickets derived from changed specs.
- If an accepted deviation remains, document why and where it should be revisited.
- If a source spec changes, check downstream tickets for stale assumptions.
