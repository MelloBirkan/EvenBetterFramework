# 0 Trigger Workflow

## Role

Clarify an app-scale or epic-scale iOS UX request and create or select the EvenBetter epic folder. This stage gathers requirements only; it does not write source specs yet.

## Process

1. Internalize the user's request and identify whether it is a new app, multi-screen feature, redesign, or full UX review.
2. Inspect the repo enough to discover likely iOS app structure, SwiftUI entry points, navigation architecture, and existing `.evenbetter/` folders.
3. Read `question-patterns.md`, especially `0 Trigger Workflow`.
4. If an existing `.evenbetter/<epic-name>/` folder clearly matches, reuse it. If multiple folders match, ask the user to choose from concrete options.
5. Ask roughly 3-10 multiple-choice questions in this phase, across one or more rounds depending on complexity, until the app/epic goal, audience, screen set, navigation model, accessibility baseline, and review/build scope are clear.
6. Use later rounds to cover edge cases and unspoken assumptions. Do not create the epic folder from only a one-sentence app idea unless the scope is already explicit.
7. Create `.evenbetter/<epic-name>/` only after the epic name and scope are clear.
8. Summarize the agreed requirements and recommend `1-ios-ux-brief` next.

## Question Rounds

Use the option sets in `question-patterns.md`. Keep each round to 1-3 closed questions.

1. Shape and audience:
   - Product shape, epic scale, primary user journey, and first-release audience.
   - Existing app, greenfield app, redesign, or review scope.
2. Screen and navigation assumptions:
   - Initial screen inventory, top-level navigation, main entry point, and whether external entry points matter.
   - Platform scope for iPhone, iPad, and adaptive behavior.
3. Accessibility and evidence baseline:
   - Dynamic Type, VoiceOver, gesture/input alternatives, contrast/motion, and screenshot/simulator evidence.
   - Whether visual evidence is needed now, later during review, or not for a greenfield plan.
4. Edge-case pass:
   - Empty, loading, error, destructive, permission, offline, cancellation, recovery, auth, and cross-screen post-action states.
   - Ask this round whenever the request includes data creation, submission, account state, permissions, sync, deletion, or external entry points.

## Acceptance Criteria

- The request is converted into precise iOS UX/accessibility requirements.
- The correct `.evenbetter/<epic-name>/` folder exists or is selected.
- The next brief stage has enough context to draft audience, scope, platform assumptions, accessibility baseline, and initial flow inventory.
- No brief, flow, technical plan, tickets, or review artifact is written in this stage.
