---
name: evenbetter-ios-feature
description: iOS UX and Apple HIG workflow for small features, single SwiftUI views, screen-level UX planning, accessibility contracts, Dynamic Type, VoiceOver, screenshot-informed review, and SwiftUI/iOS best-practice validation. Use when the user wants to add or review a small iOS feature, improve a screen's UX, validate Apple Human Interface Guidelines conformance, plan accessible interactions, create UX tickets, or audit implementation against an EvenBetter feature plan.
---

# evenbetter-ios-feature

## Operating model

Use this skill as a staged, question-driven iOS UX workflow for feature-scale work. Optimize for accessible, platform-native, HIG-aligned SwiftUI features before implementation and during review.

- Ask multiple-choice questions until the feature's user goal, interaction model, accessibility contract, and review scope are genuinely clear. Before ticket breakdown, expect roughly 3-10 questions per phase on average, across multiple rounds when complexity warrants it; the cumulative pre-ticket interview can exceed 10 questions.
- Never ask open-ended questions. Use concrete options with a recommended default when one is defensible.
- Ground UX and technical recommendations in the current codebase before planning or reviewing implementation.
- Keep artifacts in `.evenbetter/<feature-name>/`, reusing an existing EvenBetter feature folder when the target is clear.
- Treat `ios-ux-plan.md` as the UX source of truth. Tickets derive from the plan.
- Load only the reference for the current stage plus `official-sources.md`, `question-patterns.md`, or `review-checklist.md` when needed.

Former slash-command names may be aliases. Interpret `/ios-feature:1-ux-plan` as "use `$evenbetter-ios-feature` with stage `1-ux-plan`."

## Question tooling

For all interviews, clarification rounds, tradeoffs, and review disposition decisions, use the best available user-question mechanism:

- Claude Code: use `AskUserQuestion` with 2-4 mutually exclusive options per question.
- Codex Plan mode: use `request_user_input` when available. Ask 1-3 short questions, give 2-3 mutually exclusive choices per question, put the recommended choice first when there is one, and rely on the client-added "Other" option.
- Cursor or other agents with an ask-question tool: use the native structured question tool with mutually exclusive options.
- Environments without structured question tooling: ask one concise closed question at a time and present numbered options only when current system instructions permit textual options.

Keep each round focused. Multiple clarification rounds are expected. Use the first questions in a phase to close gaps and assumptions, then use later rounds to cover edge cases, failure states, accessibility risks, and platform tradeoffs. Do not proceed to ticket breakdown while a high-impact UX, accessibility, navigation, review-evidence, or platform-conformance decision is unresolved.

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

Infer the stage from the user request. If the user gives no stage and there is no active `.evenbetter` feature, start with `0-trigger-workflow`. If multiple feature folders could apply, ask the user to choose from concrete folder options.

| Stage | Reference | Use when |
| --- | --- | --- |
| `0-trigger-workflow` | `references/0-trigger-workflow.md` | Turn an initial iOS feature request into clarified UX/accessibility requirements and create or select the feature folder. |
| `1-ux-plan` | `references/1-ux-plan.md` | Create `.evenbetter/<feature-name>/ios-ux-plan.md`. |
| `2-plan-validation` | `references/2-plan-validation.md` | Stress-test the UX plan for HIG, accessibility, and iOS feasibility before ticketing. |
| `3-ticket-breakdown` | `references/3-ticket-breakdown.md` | Convert the UX plan into story-sized UX implementation tickets. |
| `4-execute` | `references/4-execute.md` | Execute or guide tickets in dependency order while preserving the UX/accessibility contract. |
| `5-ux-implementation-review` | `references/5-ux-implementation-review.md` | Review implementation using plan, screenshots, code, and Apple guidance. |
| `6-revise-requirements` | `references/6-revise-requirements.md` | Propagate changed UX/accessibility requirements through plan and tickets. |
| `7-cross-artifact-validation` | `references/7-cross-artifact-validation.md` | Check consistency among the feature plan, UX tickets, review notes, and implementation. |

## Artifact rules

- Create `.evenbetter/` if it does not exist.
- Derive `<feature-name>` as short, descriptive kebab-case.
- Prefer reusing an existing `.evenbetter/<feature-name>/` folder when the feature clearly matches.
- Store the UX plan at `.evenbetter/<feature-name>/ios-ux-plan.md`.
- Store UX review output at `.evenbetter/<feature-name>/ios-ux-review.md`.
- Store tickets at `.evenbetter/<feature-name>/tickets/UX-TICKET-NNN.md`.
- Update existing artifacts surgically. Preserve decisions that still hold.
- When a stage says to ask for confirmation or alignment, do that before writing or revising artifacts.

## iOS skill integration

- Use `$swiftui-ui-patterns` for SwiftUI layout, navigation, sheets, forms, controls, theming, Dynamic Type, and component patterns.
- Use `$swiftui-view-refactor` when review or execution needs smaller views, MV-first structure, state cleanup, or accessibility modifiers.
- Use `$swiftui-liquid-glass` when iOS 26+ Liquid Glass APIs or HIG Liquid Glass guidance affect the feature.
- Use `$ios-debugger-agent` when simulator screenshots, UI hierarchy, runtime behavior, or accessibility inspection are needed and supported.
- Use `$ios-app-intents` when feature actions should appear in Siri, Shortcuts, Spotlight, widgets, controls, or other system surfaces.
- Use `$swiftui-performance-audit` only when UX issues involve sluggish scrolling, heavy views, hangs, or render-performance regressions.

## Research rules

Read `references/official-sources.md` before making HIG, accessibility, or SwiftUI API claims that matter to the plan or review. Prefer official Apple sources. If browsing or documentation search is used, compare source authority and dates, and cite official links when reporting externally.

For review stages, default to plan + visual + code review. If screenshots are missing and visual evidence matters, ask for specific screenshots by state, such as default, large Dynamic Type, dark mode, error, empty, destructive confirmation, loading, or post-action success.
