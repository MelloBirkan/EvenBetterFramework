# 7 Execute

## Role

Implement or guide UX tickets while preserving the epic's iOS UX/accessibility architecture.

## Process

1. Read source specs and selected `UX-TICKET-NNN.md` files.
2. Inspect affected SwiftUI/iOS code and nearby local patterns.
3. Use the local iOS skills listed in the parent `SKILL.md` when the ticket touches their domain.
4. Implement foundation tickets before screen-level tickets.
5. After each batch, verify buildability where feasible and check ticket acceptance criteria.
6. Update ticket status only when implementation and validation evidence support it. When a ticket fully passes acceptance criteria, edit its `UX-TICKET-NNN.md` file and flip the `## Status` checkbox from `- [ ] Completed` to `- [x] Completed`. Do not check the box for tickets that still have open issues, drift, or pending fixup work — leave them unchecked so the open/closed state of the ticket folder stays trustworthy.

## Execution Guardrails

- Preserve the agreed navigation model and modal policy.
- Prefer native SwiftUI controls and platform components.
- Keep shared routing, sheet mapping, theme, and accessibility helpers centralized when the plan calls for it.
- Keep views small, state ownership explicit, and side effects out of `body`.
- Use semantic colors, system text styles, and native accessibility behavior by default.
- Preserve visible alternatives for gesture-driven actions.
- Do not regress source specs without updating them through `9-revise-requirements`.

## Validation During Execution

- Build or run targeted checks when available.
- Add previews or simulator screenshots when tickets require visual validation.
- For visual uncertainty, ask for specific screenshots instead of guessing.
