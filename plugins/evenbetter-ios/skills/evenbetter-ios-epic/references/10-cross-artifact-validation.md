# 10 Cross-Artifact Validation

## Role

Check consistency between the iOS UX brief, screen flows, HIG technical plan, UX tickets, review notes, and implementation.

## Process

1. Read all epic UX artifacts in `.evenbetter/<epic-name>/`.
2. Inspect implementation only where needed to verify a contradiction or missing requirement.
3. Check that each brief/flow/technical-plan requirement has ticket coverage or an explicit deferral.
4. Check that each ticket traces back to a source spec requirement.
5. Check that review findings are resolved, ticketed, or explicitly accepted.
6. Present discrepancies by severity and ask closed disposition questions when needed.

## Consistency Checks

- Same epic name, scope, audience, platform scope, and top-level navigation across artifacts.
- Same screen inventory across brief, flows, plan, and tickets.
- Same Dynamic Type, VoiceOver, gesture, state, and adaptivity requirements across specs and tickets.
- Navigation and modal policy are consistent across specs, tickets, and code.
- No ticket implements a UX behavior that source specs explicitly exclude.
- Review findings are not silently dropped.

## Output

Return a concise validation report. Update artifacts only after user alignment when the fix changes requirements, source specs, or ticket scope.
