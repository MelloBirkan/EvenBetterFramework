---
name: evenbetter-ios-epic
description: >-
  Plans and reviews multi-screen iOS work, such as a complex flow or a whole new app, in closed-question stages: UX brief, HTML screen flows, HIG tech plan, tickets, execution and review. Use when designing navigation across several screens, planning an app from scratch, or reviewing a built multi-screen flow against its specs. For one screen or a small change use evenbetter-ios-feature.
---

# evenbetter-ios-epic

Paths in this skill and its references are relative to this SKILL.md's folder. The plugin corpus is at `../../corpus/`.

## Operating model

Use this skill as a staged, question-driven iOS UX workflow for epic-scale work: several screens, a new navigation structure, or a new app. Optimize for coherent multi-screen user journeys, accessible interaction architecture, platform-native navigation, and traceability from Apple guidance to tickets and review findings.

- Check the request's size first. `references/0-trigger-workflow.md` opens with a scope check that offers evenbetter-ios-feature when the work is one screen or a small change.
- Ask multiple-choice questions until the app or epic's audience, screen set, navigation model, accessibility strategy, and review scope are clear. Before ticket breakdown, expect roughly 3-10 questions per phase on average, across several rounds when complexity warrants it; the cumulative pre-ticket interview can exceed 10 questions.
- Treat the brief and core-flow stages as discovery-heavy. Draft `ios-ux-brief.md` and `screen-flows.html` only after enough closed questions have made the intended users, included screens, primary flows, edge cases, and review evidence explicit; a vague prompt produces specs that tickets cannot trace to.
- In `2-screen-flows`, ask flow-by-flow questions before writing `screen-flows.html`. Every primary flow needs a decided entry point, screen sequence, presentation style, completion state, cancellation or back behavior, failure/recovery path, accessibility implications, and screenshot needs. `references/2-screen-flows.md` describes the HTML previews and the SwiftUI mapping block that follows each one.
- Ask closed questions with concrete options, and mark a recommended default when one is defensible. Open-ended questions hand the design work back to the user.
- Ground UX and technical recommendations in the current codebase before planning or reviewing implementation.
- Keep artifacts in `.evenbetter/<epic-name>/`, reusing an existing EvenBetter epic folder when the target is clear.
- Treat `ios-ux-brief.md`, `screen-flows.html`, and `ios-hig-tech-plan.md` as source specs. Tickets derive from those specs.
- Load only the reference for the current stage, plus `references/official-sources.md`, `references/question-patterns.md`, or `references/review-checklist.md` when needed.

A stage name given as the argument (for example `2-screen-flows`) selects that stage.

## Question tooling

Ask with the host's structured question tool when it has one:

- Claude Code: `AskUserQuestion`, with 2-4 mutually exclusive options per question.
- Codex in Plan mode: `request_user_input`, with 1-3 short questions of 2-3 options each, the recommended option first and marked "(Recommended)". The client adds "Other". Plan mode is read-only, so present results in a `<proposed_plan>` block and ask the user to switch to Default mode before writing `.evenbetter/` files or editing code.
- Codex in Default mode: ask one concise closed question with numbered options in plain text, then wait. Use `request_user_input` instead if the session offers it.
- Other agents: use their structured question tool, or ask one closed question with numbered options.
- When nobody can answer, because the user said they will not be around or asked you to go ahead without questions, or because the run is one-shot and non-interactive (such as `claude -p`, `codex exec`, CI or a scheduled task), do not end the turn on a clarifying question. Take the recommended option, say which one you took, and record it as an assumption in the artifact or the final reply. Never assume an approval the user has not given, such as accepting a plan or starting to edit code: finish the current stage and end with what waits on the person. Any exception this skill names elsewhere still applies.

Keep each round focused, and expect several rounds. Ask only the current round's questions. Leave later topics for their own round, with options, instead of listing them as open questions at the end. Use the first questions in a phase to close gaps and assumptions, then use later rounds for edge cases, failure states, accessibility risks, and platform tradeoffs. Prefer returning to the relevant earlier phase over carrying unresolved assumptions forward. Stay out of ticket breakdown while a high-impact UX, accessibility, navigation, review-evidence, platform-conformance, or architecture decision is unresolved, because tickets would then encode a guess.

## Tool equivalents

The references use Claude Code tool names. In Codex, use these equivalents, and do not simulate a tool the session does not have:

| Claude Code | Codex |
| --- | --- |
| `AskUserQuestion` | `request_user_input` (Plan mode, or Default mode when enabled); otherwise a closed plain-text question |
| `Glob`, `Grep`, `Read` | `rg --files`, `rg`, and shell reads such as `sed -n` or `nl` through `exec_command` |
| `Read` on an image or screenshot | `view_image` |
| `Edit`, `Write` | `apply_patch` (Default mode only) |
| `Bash` | `exec_command` |
| `TaskCreate`, `TaskUpdate` | `update_plan` (Default mode only; in Plan mode keep the steps in `<proposed_plan>`) |
| `WebSearch`, `WebFetch` | `web_search`, or a configured MCP search or fetch tool such as Firecrawl, Tavily or Exa; `curl` through `exec_command` where network access is allowed |
| `Agent` | `spawn_agent`, then `wait_agent` |
| `ref_search_documentation`, `ref_read_url` | any documentation MCP the session has; otherwise official Apple pages through the web tools above |

A stage that says to delegate is itself the request to delegate. Codex agents share one working directory, so run tickets in parallel only when their files do not overlap.

If current system, developer or user instructions conflict with this skill, follow them.

## Stage selection

Infer the stage from the user request. If the user gives no stage and there is no active `.evenbetter` epic, start with `0-trigger-workflow`. If several epic folders could apply, ask the user to choose from concrete folder options.

| Stage | Reference | Use when |
| --- | --- | --- |
| `0-trigger-workflow` | `references/0-trigger-workflow.md` | Check the request's size, turn it into clarified iOS UX/accessibility requirements, and create or select the epic folder. |
| `1-ios-ux-brief` | `references/1-ios-ux-brief.md` | Create `.evenbetter/<epic-name>/ios-ux-brief.md`. |
| `2-screen-flows` | `references/2-screen-flows.md` | Design multi-screen user journeys and interaction flows. |
| `3-ux-prd-validation` | `references/3-ux-prd-validation.md` | Validate requirements clarity and HIG/accessibility completeness before technical planning. |
| `4-ios-hig-tech-plan` | `references/4-ios-hig-tech-plan.md` | Create `.evenbetter/<epic-name>/ios-hig-tech-plan.md` grounded in product specs and codebase reality. |
| `5-architecture-validation` | `references/5-architecture-validation.md` | Stress-test navigation, state, accessibility, and architecture decisions before ticketing. |
| `6-ticket-breakdown` | `references/6-ticket-breakdown.md` | Convert the specs into story-sized UX implementation tickets. |
| `7-execute` | `references/7-execute.md` | Execute or guide tickets in dependency order while preserving the UX/accessibility contract. |
| `8-ux-implementation-review` | `references/8-ux-implementation-review.md` | Review implementation using specs, screenshots, code, and Apple guidance. |
| `9-revise-requirements` | `references/9-revise-requirements.md` | Propagate changed UX/accessibility requirements through specs and tickets. |
| `10-cross-artifact-validation` | `references/10-cross-artifact-validation.md` | Check consistency among the epic specs, UX tickets, review notes, and implementation. |

The validation stages here check this skill's own specs and tickets. They are not the evenbetter-validate skill, which checks evenbetter-analyze audit reports.

## Artifact rules

- Create `.evenbetter/` if it does not exist.
- Derive `<epic-name>` as short, descriptive kebab-case.
- Prefer reusing an existing `.evenbetter/<epic-name>/` folder when the epic clearly matches.
- Store the UX brief at `.evenbetter/<epic-name>/ios-ux-brief.md`.
- Store screen flows at `.evenbetter/<epic-name>/screen-flows.html`. The file is self-contained HTML with inline CSS; each step has a non-interactive iOS-approximating visual preview followed by an inline SwiftUI mapping block.
- Store the HIG technical plan at `.evenbetter/<epic-name>/ios-hig-tech-plan.md`.
- Store UX review output at `.evenbetter/<epic-name>/ios-ux-review.md`.
- Store tickets at `.evenbetter/<epic-name>/tickets/UX-TICKET-NNN.md`.
- Update existing artifacts surgically. Preserve decisions that still hold.
- When a stage says to ask for confirmation or alignment, do that before writing or revising artifacts.

## iOS skill integration

- Use `evenbetter-swiftui-ui-patterns` for SwiftUI layout, navigation, sheets, forms, controls, theming, Dynamic Type, and component patterns.
- Use `evenbetter-swiftui-view-refactor` when review or execution needs smaller views, MV-first structure, state cleanup, or accessibility modifiers.
- Use `evenbetter-swiftui-accessibility` when a spec, ticket, or review needs the corpus accessibility clauses for VoiceOver, Dynamic Type, contrast, or hit targets.
- Use `evenbetter-ios-haptics` when flows add or review haptic feedback, such as `.sensoryFeedback` for completion, error, or selection events, and to keep haptics consistent across screens.
- Use `evenbetter-swiftui-liquid-glass` when iOS 26+ Liquid Glass APIs or HIG Liquid Glass guidance affect the epic.
- Use `evenbetter-ios-debugger-agent` for simulator screenshots, the UI hierarchy, logs and runtime behavior. It works through the Xcode MCP server if that is connected, then MobileBuildMCP if the user has installed it, then `xcodebuild` and `xcrun simctl`.
- Use `evenbetter-accessibility-tests` for runtime accessibility evidence. It runs Apple's accessibility audit in UI tests, at large text sizes and in dark mode, and on Xcode 27 it also walks each screen with VoiceOver. It tests the findings of an evenbetter-analyze report, and only the screens that have them, so run evenbetter-analyze on the built code first.
- Use `evenbetter-ios-app-intents` when app actions should appear in Siri, Shortcuts, Spotlight, widgets, controls, or other system surfaces.
- Use `evenbetter-swiftui-performance-audit` only when UX issues involve sluggish scrolling, heavy views, hangs, or render-performance regressions.

## Research rules

Read `references/official-sources.md` before making HIG, accessibility, or SwiftUI API claims that matter to the plan or review. Prefer official Apple sources. If browsing or documentation search is used, compare source authority and dates, and cite official links when reporting externally.

Apple's pages render with JavaScript, so a plain fetch can return an empty "requires JavaScript" shell. Prefer a scraper MCP that renders pages (Firecrawl, Tavily extract, Exa fetch), or Apple's JSON form: `https://developer.apple.com/tutorials/data/documentation/<path>.json` for API docs and `https://developer.apple.com/tutorials/data/design/human-interface-guidelines/<page>.json` for HIG pages.

For review stages, default to plan + visual + code review. If screenshots are missing and visual evidence matters, ask for specific screenshots by state, such as default, large Dynamic Type, dark mode, error, empty, destructive confirmation, loading, or post-action success.
