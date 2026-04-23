# 4 Execute

## Role

Implement or guide UX tickets while preserving the iOS UX/accessibility contract.

## Process

1. Read `ios-ux-plan.md` and selected `UX-TICKET-NNN.md` files.
2. Inspect affected SwiftUI/iOS code and nearby local patterns.
3. Use the local iOS skills listed in the parent `SKILL.md` when the ticket touches their domain.
4. Implement tickets in dependency order.
5. After each batch, verify buildability where feasible and check the ticket acceptance criteria.
6. Update ticket status only when implementation and validation evidence support it.

## Execution Guardrails

- Prefer standard SwiftUI controls and modifiers over custom interaction code.
- Keep views small, state ownership explicit, and side effects out of `body`.
- Use semantic colors, system text styles, and native accessibility behavior by default.
- Add accessibility modifiers only where standard controls or labels do not provide enough context.
- Preserve visible alternatives for gesture-driven actions.
- Do not regress plan decisions without updating the plan through `6-revise-requirements`.

## Validation During Execution

- Build or run targeted checks when available.
- Add previews or simulator screenshots when the ticket requires visual validation.
- For visual uncertainty, ask for specific screenshots instead of guessing.
