# 1 iOS UX Brief

## Role

Create the product-level UX brief for a multi-screen iOS epic or app.

## Process

1. Read gathered requirements and inspect the current codebase or project structure.
2. Read `official-sources.md` and `question-patterns.md`.
3. Ask roughly 3-10 multiple-choice questions in this phase, across one or more rounds before drafting when complexity warrants it. Use early questions to close gaps and assumptions; use later questions to cover edge cases, cross-screen consistency, failure states, accessibility risks, and screenshot/simulator evidence.
4. Write `.evenbetter/<epic-name>/ios-ux-brief.md`.

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

## Next Step

Recommend `2-screen-flows` after the brief is aligned.
