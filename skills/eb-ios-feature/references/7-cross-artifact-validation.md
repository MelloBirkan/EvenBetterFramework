# 7 Cross-Artifact Validation

## Role

Check consistency between `ios-ux-plan.md`, UX tickets, review notes, and implementation.

## Process

1. Read all feature UX artifacts in `.evenbetter/<feature-name>/`.
2. Inspect implementation only where needed to verify a contradiction or missing requirement.
3. Check that each plan requirement has ticket coverage or an explicit deferral.
4. Check that each ticket traces back to a plan requirement.
5. Check that review findings are resolved, ticketed, or explicitly accepted.
6. Present discrepancies by severity and ask closed disposition questions when needed.

## Consistency Checks

- Same feature name, scope, entry point, and target screen across artifacts.
- Same Dynamic Type, VoiceOver, gesture, and state requirements across plan and tickets.
- Same navigation and presentation model across plan, tickets, and code.
- No ticket implements a UX behavior that the plan explicitly excludes.
- Review findings are not silently dropped.

## Output

Return a concise validation report. Update artifacts only after user alignment when the fix changes requirements or ticket scope.
