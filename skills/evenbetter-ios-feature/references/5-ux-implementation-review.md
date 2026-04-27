# 5 UX Implementation Review

## Role

Review the implemented or existing feature surface against `ios-ux-plan.md`, available UX tickets, screenshots, code, Apple HIG, accessibility guidance, and SwiftUI best practices. This stage can run before ticket breakdown when the feature already exists or screenshots/code are available.

## Process

1. Read `.evenbetter/<feature-name>/ios-ux-plan.md` and relevant `UX-TICKET-NNN.md` files when they exist.
2. Read `review-checklist.md` and `official-sources.md`.
3. Inspect changed code with `git diff` or the files named by the user/tickets.
4. Review screenshots when available. If screenshots are missing and visual evidence matters, ask for specific states from `question-patterns.md`.
5. Use `$swiftui-view-refactor`, `$swiftui-ui-patterns`, `$swiftui-liquid-glass`, `$ios-debugger-agent`, or `$swiftui-performance-audit` when their domain is relevant.
6. Write `.evenbetter/<feature-name>/ios-ux-review.md` for formal reviews.
7. Ask closed disposition questions for findings that need product or timing decisions. When review exposes hidden assumptions or missing states before ticketing, ask enough additional multiple-choice questions to close them; 3-10 questions in this phase is normal for complex screens.

## Review Output

Lead with findings ordered by severity.

```markdown
# iOS UX Review: <Feature Name>

## Findings
- [Severity] <Issue title> - <specific evidence, affected state/file/screenshot, source/spec reference, recommended fix.>

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

- Cite specific code locations, screenshots, or plan sections.
- Distinguish HIG guidance from API requirements.
- Do not flag a standard SwiftUI component for missing labels unless evidence shows the default is insufficient.
- Do not rely on color contrast claims without enough evidence; request a screenshot or note the gap.
