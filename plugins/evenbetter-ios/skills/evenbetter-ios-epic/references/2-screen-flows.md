# 2 Screen Flows

## Role

Design multi-screen user journeys and interaction flows at the product level.

## Process

1. Read `.evenbetter/<epic-name>/ios-ux-brief.md`.
2. Explore current app flows and navigation if the project already exists.
3. Read `question-patterns.md`, especially `2 Screen Flows`, and use multiple-choice questions for flow decisions. Ask roughly 3-10 questions in this phase when needed to close cross-screen assumptions, edge cases, and unspoken flow expectations. For app-scale work, expect multiple rounds and exceed 10 total questions when the flow map is still ambiguous.
4. Run the core-flow interview below before drafting. Ask flow-by-flow questions for every primary flow; do not rely on a single generic navigation question.
5. Think through entry, each action, visible feedback, navigation, completion, cancellation, and recovery for each flow.
6. Write `.evenbetter/<epic-name>/screen-flows.md`.

## Core-Flow Interview

Use closed questions from `question-patterns.md`. Keep each round to 1-3 questions, then continue with another round when answers expose new gaps.

### Round 1: Flow Inventory

Clarify:

- The set of primary, secondary, and deferred flows.
- The top-level navigation model and owning root screen for each flow.
- Whether each flow starts in-app, from onboarding/auth/permissions, or from external system surfaces.
- Whether iPad/adaptive behavior changes the flow structure.

### Round 2: Per-Flow Decisions

Repeat this round for each primary flow. Do not write the flow until every item is decided or intentionally deferred:

- Entry state: existing data, empty/first-use, signed-out, permission-blocked, offline, or deep-linked.
- Screen sequence: root, list/detail, task, confirmation, completion, and any optional branch screens.
- Presentation style: push, tab, sheet, popover, split view, alert, full-screen cover, or external entry.
- Primary and destructive actions: visible placement, disabled/loading behavior, confirmation, and undo/recovery.
- Completion: return target, success feedback, next suggested action, and cross-screen state update.
- Cancellation/back behavior: standard back, dismiss, confirmation, draft preservation, or blocked dismissal.
- Failure/recovery: inline retry, preserved input, error screen, permission education, offline queue, or central error surface.

### Round 3: Cross-Flow Edge Cases

Ask this round before drafting when more than one screen or more than one user state exists:

- State restoration, per-tab history, draft persistence, and post-completion reset behavior.
- Authentication, permissions, empty/loading/error states, destructive actions, offline/degraded mode, and data conflicts.
- Dynamic Type reflow, VoiceOver headings/grouping/announcements, custom actions, gesture alternatives, keyboard/Switch Control/Voice Control implications.
- Screenshot or simulator evidence for default, large text, dark mode, error, empty, modal, destructive, and completion states.

## Drafting Gate

Do not write `screen-flows.md` until every primary flow has:

- Purpose and owning root or entry point.
- Screens involved and presentation style for each meaningful step.
- Primary action, visible feedback, and loading/disabled behavior.
- Completion destination and cross-screen state update.
- Failure, cancellation, back/dismiss, and recovery behavior.
- Accessibility notes for Dynamic Type and VoiceOver.
- Screenshots or simulator states needed for later review, or an explicit code-only rationale.

## Flow Template

```markdown
# Screen Flows: <Epic Name>

## Flow: <Name>
- Purpose:
- Entry point:
- Owning root or surface:
- Screens involved:
- Steps:
- Presentation and navigation:
- Primary and destructive actions:
- Completion:
- Failure or cancellation:
- Edge states:
- Accessibility notes:
- Screenshots needed for later review:
```

## Flow Design Rules

- Keep flows product-level. Do not include code or file paths.
- Use native iOS presentation language: tab, stack, sheet, alert, toolbar, split view, or modal only when the choice matters.
- Make primary and destructive actions explicit.
- Record how VoiceOver users understand screen changes and completion.
- Record where Dynamic Type can force layout changes across screens.
- Record how back, dismiss, cancel, and resume behave when data may be lost.
- Record how external entry points, permissions, auth state, and offline state affect the journey.

## Next Step

Route through validation before ticketing. Recommend `3-ux-prd-validation` when flows are complex or high-risk; otherwise proceed to `4-ios-hig-tech-plan`. After the technical plan, run `5-architecture-validation` before `6-ticket-breakdown`. Do not recommend ticket breakdown directly from screen flows.
