# 4 Execute

## Role

Implement or guide UX tickets while preserving the iOS UX/accessibility contract.

## Process

1. Read `ios-ux-plan.md` and the selected `UX-TICKET-NNN.md` files.
2. Inspect affected SwiftUI/iOS code and nearby local patterns.
3. Use the iOS skills listed in `SKILL.md` when the ticket touches their domain.
4. Implement tickets in dependency order, yourself or through subagents as described under Delegation.
5. After each batch, verify buildability where feasible and check the ticket acceptance criteria.
6. Update ticket status only when implementation and validation evidence support it. When a ticket fully passes its acceptance criteria, edit its `UX-TICKET-NNN.md` file and flip the `## Status` checkbox from `- [ ] Completed` to `- [x] Completed`. Leave the box unchecked for tickets with open issues, drift, or pending fixup work, so the open/closed state of the ticket folder stays trustworthy.

## Delegation

This stage delegates independent tickets to subagents. That instruction is itself the request to delegate, so it needs no separate approval. A feature batch often holds one or two tickets, and then there is nothing to delegate.

- Delegate when the current batch has two or more tickets whose dependencies are met and whose likely files do not overlap. Implement a single ticket, or tickets that touch the same files, yourself.
- Give a subagent its own git worktree only when that worktree starts from the current work. In Claude Code, `isolation: "worktree"` on the `Agent` call branches from the repository's default branch unless the `worktree.baseRef` setting is `"head"`, and a worktree holds only committed files, so it can miss tickets finished earlier in this stage. In that case, skip worktrees. After a worktree batch, review and merge each worktree's changes before the next batch.
- Without worktrees, subagents share one working directory, as Codex agents always do. Run in parallel only tickets with disjoint files, and let the parent build once per batch, because two builds of the same project in the same location fail on a locked build database.
- Give each subagent absolute paths to the ticket and to `ios-ux-plan.md` in the main checkout (a worktree may lack an untracked `.evenbetter/` folder), the guardrails below, and the iOS skills that apply.
- Subagents do not ask the user questions. A subagent that hits a blocker, such as an open UX or accessibility decision, an acceptance criterion it cannot meet, or a build failure it cannot fix, stops and returns the blocker to the parent. The parent asks the user a closed question, then passes the answer back or takes the ticket over.
- Each subagent returns the files it changed, the validation it ran, and any acceptance criteria still unmet. Subagents leave the `## Status` checkboxes alone; the parent flips them after checking that evidence.

## Execution Guardrails

- Prefer standard SwiftUI controls and modifiers over custom interaction code.
- Keep views small, state ownership explicit, and side effects out of `body`.
- Use semantic colors, system text styles, and native accessibility behavior by default.
- Add accessibility modifiers only where standard controls or labels do not provide enough context.
- Preserve visible alternatives for gesture-driven actions.
- Change plan decisions only through `6-revise-requirements`, so the plan and the code stay in step.

## Validation During Execution

- If the Xcode MCP server is connected (this plugin registers `xcrun mcpbridge` as the `xcode` server), use it to build the project and, where it offers them, to render previews and read build issues. Otherwise build with `xcodebuild` through the shell.
- Build or run targeted checks when available.
- Add previews or simulator screenshots when the ticket requires visual validation. For simulator runs, screenshots and runtime behavior, use evenbetter-ios-debugger-agent, which tries the Xcode MCP server first, then MobileBuildMCP, then `xcodebuild` and `xcrun simctl`.
- When a ticket's acceptance criteria need runtime accessibility evidence, use evenbetter-accessibility-tests. It checks an evenbetter-analyze report's findings in the running app and marks each one confirmed or refuted, so run evenbetter-analyze once the code is in place. It writes no test for a screen without findings. When a criterion asks for a clean audit on such a screen, for example at the largest text size, write a UI test in the project's UI test target that calls `performAccessibilityAudit(for:_:)` (iOS 17 or later).
- For visual uncertainty, ask for specific screenshots instead of guessing.
