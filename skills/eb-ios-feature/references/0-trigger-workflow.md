# 0 Trigger Workflow

## Role

Clarify a feature-scale iOS UX request and create or select the EvenBetter feature folder. This stage gathers requirements only; it does not write the UX plan yet.

## Process

1. Internalize the user's request and identify whether it is a small iOS feature, a single SwiftUI view, a screen review, or a narrow UX improvement.
2. Inspect the repo enough to discover likely iOS app structure, SwiftUI entry points, existing `.evenbetter/` folders, and related screens.
3. If an existing `.evenbetter/<feature-name>/` folder clearly matches, reuse it. If multiple folders match, ask the user to choose from concrete options.
4. Ask roughly 3-10 multiple-choice questions in this phase, across one or more rounds depending on complexity, until the feature goal, audience, entry point, success state, accessibility baseline, and review/build scope are clear.
5. Create `.evenbetter/<feature-name>/` only after the feature name and scope are clear.
6. Summarize the agreed requirements and recommend `1-ux-plan` next.

## Questions To Resolve

- User goal: what task should the screen or feature help people complete?
- Entry point: where does the feature appear in the current app?
- Screen type: form, list/detail, modal, settings, media/content, or custom interaction.
- Accessibility baseline: Dynamic Type range, VoiceOver expectations, keyboard/Switch Control/Voice Control relevance.
- Visual evidence: whether screenshots are needed now, later during review, or not at all.
- Edge cases: empty, loading, error, destructive, permission, offline, cancellation, and post-action states.

## Acceptance Criteria

- The request is converted into precise iOS UX/accessibility requirements.
- The correct `.evenbetter/<feature-name>/` folder exists or is selected.
- No plan, tickets, or review artifact is written in this stage.
