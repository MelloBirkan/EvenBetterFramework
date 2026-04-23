# 5 Architecture Validation

## Role

Stress-test the HIG technical plan before ticketing or implementation.

## Process

1. Read `ios-ux-brief.md`, `screen-flows.md`, and `ios-hig-tech-plan.md`.
2. Inspect codebase constraints that could invalidate the plan.
3. Use relevant local iOS skills for navigation, view structure, Liquid Glass, App Intents, or performance concerns.
4. Validate the plan against the checklist below.
5. Present findings by severity and ask closed disposition questions for unresolved tradeoffs. Ask additional multiple-choice questions when validation exposes hidden assumptions, edge cases, or architectural gaps; this phase can reasonably add 3-10 questions before ticketing.
6. Update `ios-hig-tech-plan.md` only after alignment.

## Validation Checklist

- Navigation architecture supports every source flow without inconsistent back/close behavior.
- State ownership is explicit for shared app state, route state, sheets, and async loading.
- Screen decomposition avoids likely giant views or duplicated routing switches.
- Dynamic Type and VoiceOver requirements have concrete implementation surfaces.
- Custom gestures, custom controls, or custom layouts have accessibility alternatives.
- iPad/adaptive behavior is feasible with the selected SwiftUI structure.
- Screenshot and simulator checkpoints exist for high-risk screens.
- Implementation sequence avoids building visual screens before shared navigation/accessibility foundations.

## Output

Either confirm the plan is ready for `6-ticket-breakdown` or revise the plan with a short "Architecture Validation Updates" section. Proceed to ticket breakdown only after the cumulative pre-ticket questions have closed all material gaps and uncommunicated assumptions.
