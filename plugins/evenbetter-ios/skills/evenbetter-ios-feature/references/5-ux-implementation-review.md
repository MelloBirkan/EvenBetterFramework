# 5 UX Implementation Review

## Role

Review the implemented or existing feature surface against `ios-ux-plan.md`, available UX tickets, screenshots, code, Apple HIG, accessibility guidance, and SwiftUI best practices. This stage can run before ticket breakdown when the feature already exists or screenshots/code are available.

## Process

1. Read `.evenbetter/<feature-name>/ios-ux-plan.md` and relevant `UX-TICKET-NNN.md` files when they exist.
2. Read `references/review-checklist.md` and `references/official-sources.md`.
3. Inspect changed code with `git diff` or the files named by the user/tickets.
4. Review screenshots when available. If screenshots are missing and visual evidence matters, ask for specific states from `references/question-patterns.md`. When nobody can answer, do not wait for them: capture the states with evenbetter-ios-debugger-agent when a simulator is available, otherwise review the code alone and list the missing states under Screenshot and Test Gaps.
5. Use `evenbetter-swiftui-view-refactor`, `evenbetter-swiftui-ui-patterns`, `evenbetter-swiftui-accessibility`, `evenbetter-ios-haptics`, `evenbetter-swiftui-liquid-glass`, or `evenbetter-swiftui-performance-audit` when their domain is relevant. For simulator screenshots of the built screen and its runtime behavior, use `evenbetter-ios-debugger-agent`, which works through the Xcode MCP server first when it is connected. For runtime accessibility evidence, run `evenbetter-accessibility-tests` on an evenbetter-analyze report of the built code, and cite its confirmed and refuted verdicts in the review.
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
