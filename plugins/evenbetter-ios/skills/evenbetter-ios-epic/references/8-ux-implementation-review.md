# 8 UX Implementation Review

## Role

Review the implemented epic against the UX brief, screen flows, HIG technical plan, UX tickets, screenshots, code, Apple HIG, accessibility guidance, and SwiftUI best practices.

## Process

1. Read `ios-ux-brief.md`, `screen-flows.md`, `ios-hig-tech-plan.md`, and relevant `UX-TICKET-NNN.md` files.
2. Read `review-checklist.md` and `official-sources.md`.
3. Inspect changed code with `git diff` or the files named by the user/tickets.
4. Review screenshots when available. If screenshots are missing and visual evidence matters, ask for specific states from `question-patterns.md`.
5. Use `/evenbetter-ios:swiftui-view-refactor`, `/evenbetter-ios:swiftui-ui-patterns`, `/evenbetter-ios:swiftui-liquid-glass`, `/evenbetter-ios:ios-debugger-agent`, `/evenbetter-ios:ios-app-intents`, or `/evenbetter-ios:swiftui-performance-audit` when their domain is relevant.
6. Write `.evenbetter/<epic-name>/ios-ux-review.md` for formal reviews.
7. Ask closed disposition questions for findings that need product or timing decisions.

## Review Output

Lead with findings ordered by severity.

```markdown
# iOS UX Review: <Epic Name>

## Findings
- [Severity] <Issue title> - <specific evidence, affected screen/state/file/screenshot, source/spec reference, recommended fix.>

## Validated
- <Important planned behavior confirmed.>

## Screenshot and Test Gaps
- <Missing visual states, simulator checks, or accessibility checks.>

## Suggested Disposition
- <Fix before merge / track follow-up / accept deviation, as applicable.>

## Sources
- <Apple links used for HIG/accessibility claims.>
```

## Finding Standards

- Cite specific code locations, screenshots, or spec sections.
- Distinguish HIG guidance from API requirements.
- Evaluate consistency across screens, not only per-screen correctness.
- Do not flag a standard SwiftUI component for missing labels unless evidence shows the default is insufficient.
- Do not rely on color contrast claims without enough evidence; request a screenshot or note the gap.
