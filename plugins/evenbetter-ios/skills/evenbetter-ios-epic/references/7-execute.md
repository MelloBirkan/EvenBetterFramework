# 7 Execute

## Role

Implement or guide UX tickets while preserving the epic's iOS UX/accessibility architecture.

## Process

1. Read the source specs and the selected `UX-TICKET-NNN.md` files.
2. Inspect affected SwiftUI/iOS code and nearby local patterns.
3. Use the iOS skills listed in `SKILL.md` when the ticket touches their domain.
4. Implement foundation tickets before screen-level tickets, yourself or through subagents as described under Delegation.
5. After each batch, verify buildability where feasible and check ticket acceptance criteria.
6. Update ticket status only when implementation and validation evidence support it. When a ticket fully passes its acceptance criteria, edit its `UX-TICKET-NNN.md` file and flip the `## Status` checkbox from `- [ ] Completed` to `- [x] Completed`. Leave the box unchecked for tickets with open issues, drift, or pending fixup work, so the open/closed state of the ticket folder stays trustworthy.

## Delegation

This stage delegates independent tickets to subagents. That instruction is itself the request to delegate, so it needs no separate approval.

- Build the foundation tickets (navigation, routing, theme, shared accessibility helpers) in the main session first, because screen tickets depend on them. Delegate screen-level tickets once their dependencies are met and their likely files do not overlap. Implement tickets that touch the same files yourself, one after another.
- Give a subagent its own git worktree only when that worktree starts from the current work. In Claude Code, `isolation: "worktree"` on the `Agent` call branches from the repository's default branch unless the `worktree.baseRef` setting is `"head"`, and a worktree holds only committed files, so it can miss the foundation tickets and earlier batches. In that case, skip worktrees. After a worktree batch, review and merge each worktree's changes before the next batch.
- Without worktrees, subagents share one working directory, as Codex agents always do. Run in parallel only tickets with disjoint files, and let the parent build once per batch, because two builds of the same project in the same location fail on a locked build database.
- Give each subagent absolute paths in the main checkout to the ticket, `ios-ux-brief.md`, `screen-flows.html`, and `ios-hig-tech-plan.md` (a worktree may lack an untracked `.evenbetter/` folder), the guardrails below, and the iOS skills that apply.
- Subagents do not ask the user questions. A subagent that hits a blocker, such as an open UX, navigation, or accessibility decision, an acceptance criterion it cannot meet, or a build failure it cannot fix, stops and returns the blocker to the parent. The parent asks the user a closed question, then passes the answer back or takes the ticket over.
- Each subagent returns the files it changed, the validation it ran, and any acceptance criteria still unmet. Subagents leave the `## Status` checkboxes alone; the parent flips them after checking that evidence.

## Execution Guardrails

- Preserve the agreed navigation model and modal policy.
- Prefer native SwiftUI controls and platform components.
- Keep shared routing, sheet mapping, theme, and accessibility helpers centralized when the plan calls for it.
- Keep views small, state ownership explicit, and side effects out of `body`.
- Use semantic colors, system text styles, and native accessibility behavior by default.
- Preserve visible alternatives for gesture-driven actions.
- Change source specs only through `9-revise-requirements`, so the specs and the code stay in step.

## Validation During Execution

- If the Xcode MCP server is connected (this plugin registers `xcrun mcpbridge` as the `xcode` server), use it to build the project and, where it offers them, to render previews and read build issues. Otherwise build with `xcodebuild` through the shell.
- Build or run targeted checks when available.
- Add previews or simulator screenshots when tickets require visual validation. For simulator runs, screenshots and runtime behavior, use evenbetter-ios-debugger-agent, which tries the Xcode MCP server first, then MobileBuildMCP, then `xcodebuild` and `xcrun simctl`.
- When tickets' acceptance criteria need runtime accessibility evidence, use evenbetter-accessibility-tests. It checks an evenbetter-analyze report's findings in the running app and marks each one confirmed or refuted, so run evenbetter-analyze once the code is in place. It writes no test for a screen without findings. When a criterion asks for a clean audit on such a screen, for example at the largest text size, write a UI test in the project's UI test target that calls `performAccessibilityAudit(for:_:)` (iOS 17 or later).
- For visual uncertainty, ask for specific screenshots instead of guessing.
