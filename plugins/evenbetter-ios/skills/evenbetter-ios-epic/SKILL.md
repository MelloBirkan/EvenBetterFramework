---
name: evenbetter-ios-epic
description: iOS UX and Apple HIG workflow for large epics, multi-screen SwiftUI flows, app-from-scratch planning, navigation architecture, accessibility strategy, Dynamic Type, VoiceOver, screenshot-informed review, and full UX implementation validation. Use when the user wants to design or audit a multi-screen iOS experience, plan an app, validate HIG conformance, create UX tickets, or review implementation against an EvenBetter epic.
---

# evenbetter-ios-epic

## Operating model

Use this skill as a staged, question-driven iOS UX workflow for epic-scale work. Optimize for coherent multi-screen user journeys, accessible interaction architecture, platform-native navigation, and traceability from Apple guidance to tickets and review findings.

- Ask multiple-choice questions until the app or epic's audience, screen set, navigation model, accessibility strategy, and review scope are genuinely clear. Before ticket breakdown, expect roughly 3-10 questions per phase on average, across multiple rounds when complexity warrants it; the cumulative pre-ticket interview can exceed 10 questions.
- Never ask open-ended questions. Use concrete options with a recommended default when one is defensible.
- Ground UX and technical recommendations in the current codebase before planning or reviewing implementation.
- Keep artifacts in `.evenbetter/<epic-name>/`, reusing an existing EvenBetter epic folder when the target is clear.
- Treat `ios-ux-brief.md`, `screen-flows.md`, and `ios-hig-tech-plan.md` as source specs. Tickets derive from those specs.
- Load only the reference for the current stage plus `official-sources.md`, `question-patterns.md`, or `review-checklist.md` when needed.

Former slash-command names may be aliases. Interpret `/ios-epic:2-screen-flows` as "use `evenbetter-ios-epic` with stage `2-screen-flows`."

## Question tooling

For all interviews, clarification rounds, tradeoffs, and review disposition decisions, use the best available user-question mechanism:

- Claude Code: use `AskUserQuestion` with 2-4 mutually exclusive options per question.
- Codex Plan mode: use `request_user_input` when available. Ask 1-3 short questions, give 2-3 mutually exclusive choices per question, put the recommended choice first when there is one, and rely on the client-added "Other" option.
- Cursor or other agents with an ask-question tool: use the native structured question tool with mutually exclusive options.
- Environments without structured question tooling: ask one concise closed question at a time and present numbered options only when current system instructions permit textual options.

Keep each round focused. Multiple clarification rounds are expected. Use the first questions in a phase to close gaps and assumptions, then use later rounds to cover edge cases, failure states, accessibility risks, and platform tradeoffs. Do not proceed to ticket breakdown while a high-impact UX, accessibility, navigation, review-evidence, platform-conformance, or architecture decision is unresolved.

## Tool equivalents

The reference files may mention Claude-style tool names. Apply these equivalents in Codex:

| Claude command instruction | Codex equivalent |
| --- | --- |
| `AskUserQuestion` | `request_user_input` in Plan mode when available, otherwise a concise closed question |
| `Glob`, `Grep`, `Read` | `rg --files`, `rg`, and shell file reads such as `sed` or `nl` |
| `Bash` | `exec_command` |
| `TaskCreate`, `TaskUpdate` | `update_plan` |
| `Agent` | `spawn_agent` only when current instructions allow delegation and the user has explicitly permitted agent work |
| `ref_search_documentation`, `ref_read_url` | use available official-doc tooling if present, otherwise official Apple documentation or web search |

If current system or developer instructions conflict with a converted reference, follow the current higher-priority instruction.

## Stage selection

Infer the stage from the user request. If the user gives no stage and there is no active `.evenbetter` epic, start with `0-trigger-workflow`. If multiple epic folders could apply, ask the user to choose from concrete folder options.

| Stage | Reference | Use when |
| --- | --- | --- |
| `0-trigger-workflow` | `references/0-trigger-workflow.md` | Turn an initial app or epic request into clarified iOS UX/accessibility requirements and create or select the epic folder. |
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

## Artifact rules

- Create `.evenbetter/` if it does not exist.
- Derive `<epic-name>` as short, descriptive kebab-case.
- Prefer reusing an existing `.evenbetter/<epic-name>/` folder when the epic clearly matches.
- Store the UX brief at `.evenbetter/<epic-name>/ios-ux-brief.md`.
- Store screen flows at `.evenbetter/<epic-name>/screen-flows.md`.
- Store the HIG technical plan at `.evenbetter/<epic-name>/ios-hig-tech-plan.md`.
- Store UX review output at `.evenbetter/<epic-name>/ios-ux-review.md`.
- Store tickets at `.evenbetter/<epic-name>/tickets/UX-TICKET-NNN.md`.
- Update existing artifacts surgically. Preserve decisions that still hold.
- When a stage says to ask for confirmation or alignment, do that before writing or revising artifacts.

## iOS skill integration

- Use `swiftui-ui-patterns` for SwiftUI layout, navigation, sheets, forms, controls, theming, Dynamic Type, and component patterns.
- Use `swiftui-view-refactor` when review or execution needs smaller views, MV-first structure, state cleanup, or accessibility modifiers.
- Use `swiftui-liquid-glass` when iOS 26+ Liquid Glass APIs or HIG Liquid Glass guidance affect the epic.
- Use `ios-debugger-agent` when simulator screenshots, UI hierarchy, runtime behavior, or accessibility inspection are needed and supported.
- Use `ios-app-intents` when app actions should appear in Siri, Shortcuts, Spotlight, widgets, controls, or other system surfaces.
- Use `swiftui-performance-audit` only when UX issues involve sluggish scrolling, heavy views, hangs, or render-performance regressions.

## Research rules

Read `references/official-sources.md` before making HIG, accessibility, or SwiftUI API claims that matter to the plan or review. Prefer official Apple sources. If browsing or documentation search is used, compare source authority and dates, and cite official links when reporting externally.

For review stages, default to plan + visual + code review. If screenshots are missing and visual evidence matters, ask for specific screenshots by state, such as default, large Dynamic Type, dark mode, error, empty, destructive confirmation, loading, or post-action success.
