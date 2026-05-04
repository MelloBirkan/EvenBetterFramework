# 1 iOS UX Brief

## Role

Create the product-level UX brief for a multi-screen iOS epic or app.

## Process

1. Read gathered requirements and inspect the current codebase or project structure.
2. Read `official-sources.md` and `question-patterns.md`.
3. Ask roughly 3-10 multiple-choice questions in this phase, across one or more rounds before drafting when complexity warrants it. Use early questions to close gaps and assumptions; use later questions to cover edge cases, cross-screen consistency, failure states, accessibility risks, and screenshot/simulator evidence.
4. Map every material answer to the brief sections below. If any section still depends on an unstated assumption, ask another closed question before drafting.
5. Write `.evenbetter/<epic-name>/ios-ux-brief.md`.

## Brief Interview

Use `question-patterns.md` section `1 iOS UX Brief`. Ask at least one round for product-level decisions and at least one risk round for complex or app-from-scratch epics.

1. Product and audience:
   - Audience priority, context of use, primary job, and secondary users.
   - Whether the app supports short interrupted sessions, long-form work, or occasional utility entry.
2. Scope and platform:
   - Included screens, excluded screens, release boundary, dependencies, and first iPhone/iPad posture.
   - Whether external system surfaces are in scope now, deferred, or explicitly out of scope.
3. UX and accessibility baseline:
   - Information hierarchy, feedback and recovery style, Dynamic Type, VoiceOver, gesture/input alternatives, contrast, and motion.
   - Ask a stricter accessibility question when the epic has custom controls, custom gestures, dense data, media, maps, capture, scanning, or creation/submission flows.
4. Success and evidence:
   - User-visible success, accessibility success, HIG/platform success, and screenshot/simulator evidence.
   - Include a failure-state question for destructive, offline, permission, account, payment, sync, or irreversible submission flows.

## Drafting Gate

Do not write `ios-ux-brief.md` until these decisions are explicit:

- Primary audience and the usage context that shapes mobile UX.
- Included and excluded screens or product areas.
- Platform scope for iPhone, iPad, and adaptive behavior.
- Accessibility baseline for Dynamic Type and VoiceOver, plus any specialized input or motion/contrast needs.
- Success criteria for task completion, recovery, and platform fit.
- Evidence plan for screenshots, simulator review, or code-only planning.

## Brief Template

```markdown
# iOS UX Brief: <Epic Name>

## Summary
<3-8 sentences describing the app/epic goal, affected users, and intended outcome.>

## Audience and Context
- Primary users:
- Accessibility-sensitive contexts:
- Device/platform assumptions:

## Scope
- Included screens or areas:
- Excluded screens or areas:
- Dependencies:

## UX Principles
- Platform fit:
- Accessibility baseline:
- Information hierarchy:
- Feedback and recovery:

## Success Criteria
- User-visible success:
- Accessibility success:
- HIG/platform success:

## Sources
- Apple HIG/source links relevant to this brief.
```

## Brief Defaults

- Prefer platform-native navigation and standard components.
- Make accessibility a source requirement, not a review-only concern.
- Define iPad/adaptive scope explicitly, even if deferred.
- Keep visual style decisions semantic enough to survive implementation.
- Capture unknowns as exclusions or validation questions, not hidden assumptions.

## Next Step

Recommend `2-screen-flows` after the brief is aligned.
