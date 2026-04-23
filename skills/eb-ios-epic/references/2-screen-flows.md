# 2 Screen Flows

## Role

Design multi-screen user journeys and interaction flows at the product level.

## Process

1. Read `.evenbetter/<epic-name>/ios-ux-brief.md`.
2. Explore current app flows and navigation if the project already exists.
3. Read `question-patterns.md` and use multiple-choice questions for flow decisions. Ask roughly 3-10 questions in this phase when needed to close cross-screen assumptions, edge cases, and unspoken flow expectations.
4. Think through entry, each action, visible feedback, navigation, completion, cancellation, and recovery for each flow.
5. Write `.evenbetter/<epic-name>/screen-flows.md`.

## Flow Template

```markdown
# Screen Flows: <Epic Name>

## Flow: <Name>
- Purpose:
- Entry point:
- Screens involved:
- Steps:
- Completion:
- Failure or cancellation:
- Accessibility notes:
- Screenshots needed for later review:
```

## Flow Design Rules

- Keep flows product-level. Do not include code or file paths.
- Use native iOS presentation language: tab, stack, sheet, alert, toolbar, split view, or modal only when the choice matters.
- Make primary and destructive actions explicit.
- Record how VoiceOver users understand screen changes and completion.
- Record where Dynamic Type can force layout changes across screens.

## Next Step

Route through validation before ticketing. Recommend `3-ux-prd-validation` when flows are complex or high-risk; otherwise proceed to `4-ios-hig-tech-plan`. After the technical plan, run `5-architecture-validation` before `6-ticket-breakdown`. Do not recommend ticket breakdown directly from screen flows.
