# 0 Trigger Workflow

## Role

Clarify an app-scale or epic-scale iOS UX request and create or select the EvenBetter epic folder. This stage gathers requirements only; it does not write source specs yet.

## Process

1. Internalize the user's request and identify whether it is a new app, multi-screen feature, redesign, or full UX review.
2. Inspect the repo enough to discover likely iOS app structure, SwiftUI entry points, navigation architecture, and existing `.evenbetter/` folders.
3. If an existing `.evenbetter/<epic-name>/` folder clearly matches, reuse it. If multiple folders match, ask the user to choose from concrete options.
4. Ask roughly 3-10 multiple-choice questions in this phase, across one or more rounds depending on complexity, until the app/epic goal, audience, screen set, navigation model, accessibility baseline, and review/build scope are clear.
5. Create `.evenbetter/<epic-name>/` only after the epic name and scope are clear.
6. Summarize the agreed requirements and recommend `1-ios-ux-brief` next.

## Questions To Resolve

- Product shape: new app, multi-screen feature, redesign, or review.
- Audience and primary jobs.
- Screen inventory and top-level navigation.
- Platform scope: iPhone-only, iPhone+iPad, or adaptive universal app.
- Accessibility baseline: Dynamic Type, VoiceOver, keyboard/Switch Control/Voice Control, motion, and color/contrast.
- Visual evidence: whether screenshots are needed now, later during review, or not at all.
- Edge cases: empty, loading, error, destructive, permission, offline, cancellation, recovery, and cross-screen post-action states.

## Acceptance Criteria

- The request is converted into precise iOS UX/accessibility requirements.
- The correct `.evenbetter/<epic-name>/` folder exists or is selected.
- No brief, flow, technical plan, tickets, or review artifact is written in this stage.
