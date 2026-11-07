---
name: evenbetter-ios-feature
description: >-
  Plans and reviews one iOS screen or small feature in closed-question stages: UX plan, plan validation, tickets, execution and implementation review. Use when adding or reworking a single SwiftUI screen, setting its Dynamic Type and VoiceOver contract, or checking a built screen against its plan and screenshots. For multi-screen flows or a new app use evenbetter-ios-epic.
---

# evenbetter-ios-feature

Paths in this skill and its references are relative to this SKILL.md's folder. The plugin corpus is at `../../corpus/`.

## Operating model

Use this skill as a staged, question-driven iOS UX workflow for feature-scale work: one screen, one view, or a narrow change to an existing screen. Optimize for accessible, platform-native, HIG-aligned SwiftUI features before implementation and during review.

- Check the request's size first. `references/0-trigger-workflow.md` opens with a scope check that offers evenbetter-ios-epic when the work spans several screens or a new app.
- Ask multiple-choice questions until the feature's user goal, interaction model, accessibility contract, and review scope are clear. Before ticket breakdown, expect roughly 3-10 questions per phase on average, across several rounds when complexity warrants it; the cumulative pre-ticket interview can exceed 10 questions.
- Ask closed questions with concrete options, and mark a recommended default when one is defensible. Open-ended questions hand the design work back to the user.
- Ground UX and technical recommendations in the current codebase before planning or reviewing implementation.
- Keep artifacts in `.evenbetter/<feature-name>/`, reusing an existing EvenBetter feature folder when the target is clear.
- Treat `ios-ux-plan.md` as the UX source of truth. Tickets derive from the plan.
- Load only the reference for the current stage, plus `references/official-sources.md`, `references/question-patterns.md`, or `references/review-checklist.md` when needed.

A stage name given as the argument (for example `1-ux-plan`) selects that stage.

## Question tooling

Ask with the host's structured question tool when it has one:

- Claude Code: `AskUserQuestion`, with 2-4 mutually exclusive options per question.
- Codex in Plan mode: `request_user_input`, with 1-3 short questions of 2-3 options each, the recommended option first and marked "(Recommended)". The client adds "Other". Plan mode is read-only, so present results in a `<proposed_plan>` block and ask the user to switch to Default mode before writing `.evenbetter/` files or editing code.
- Codex in Default mode: ask one concise closed question with numbered options in plain text, then wait. Use `request_user_input` instead if the session offers it.
- Other agents: use their structured question tool, or ask one closed question with numbered options.
- When nobody can answer, because the user said they will not be around or asked you to go ahead without questions, or because the run is one-shot and non-interactive (such as `claude -p`, `codex exec`, CI or a scheduled task), do not end the turn on a clarifying question. Take the recommended option, say which one you took, and record it as an assumption in the artifact or the final reply. Never assume an approval the user has not given, such as accepting a plan or starting to edit code: finish the current stage and end with what waits on the person. Any exception this skill names elsewhere still applies.

Keep each round focused, and expect several rounds. Ask only the current round's questions. Leave later topics for their own round, with options, instead of listing them as open questions at the end. Use the first questions in a phase to close gaps and assumptions, then use later rounds for edge cases, failure states, accessibility risks, and platform tradeoffs. Stay out of ticket breakdown while a high-impact UX, accessibility, navigation, review-evidence, or platform-conformance decision is unresolved, because tickets would then encode a guess.

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

Infer the stage from the user request. If the user gives no stage and there is no active `.evenbetter` feature, start with `0-trigger-workflow`. If several feature folders could apply, ask the user to choose from concrete folder options.

| Stage | Reference | Use when |
| --- | --- | --- |
| `0-trigger-workflow` | `references/0-trigger-workflow.md` | Check the request's size, turn it into clarified UX/accessibility requirements, and create or select the feature folder. |
| `1-ux-plan` | `references/1-ux-plan.md` | Create `.evenbetter/<feature-name>/ios-ux-plan.md`. |
| `2-plan-validation` | `references/2-plan-validation.md` | Stress-test the UX plan for HIG, accessibility, and iOS feasibility before ticketing. |
| `3-ticket-breakdown` | `references/3-ticket-breakdown.md` | Convert the UX plan into story-sized UX implementation tickets. |
| `4-execute` | `references/4-execute.md` | Execute or guide tickets in dependency order while preserving the UX/accessibility contract. |
| `5-ux-implementation-review` | `references/5-ux-implementation-review.md` | Review implementation using plan, screenshots, code, and Apple guidance. |
| `6-revise-requirements` | `references/6-revise-requirements.md` | Propagate changed UX/accessibility requirements through plan and tickets. |
| `7-cross-artifact-validation` | `references/7-cross-artifact-validation.md` | Check consistency among the feature plan, UX tickets, review notes, and implementation. |

The validation stages here check this skill's own plan and tickets. They are not the evenbetter-validate skill, which checks evenbetter-analyze audit reports.

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

- Use `evenbetter-swiftui-ui-patterns` for SwiftUI layout, navigation, sheets, forms, controls, theming, Dynamic Type, and component patterns.
- Use `evenbetter-swiftui-view-refactor` when review or execution needs smaller views, MV-first structure, state cleanup, or accessibility modifiers.
- Use `evenbetter-swiftui-accessibility` when a plan, ticket, or review needs the corpus accessibility clauses for VoiceOver, Dynamic Type, contrast, or hit targets.
- Use `evenbetter-ios-haptics` when the feature adds or reviews haptic feedback, such as `.sensoryFeedback` for success, error, or selection events.
- Use `evenbetter-swiftui-liquid-glass` when iOS 26+ Liquid Glass APIs or HIG Liquid Glass guidance affect the feature.
- Use `evenbetter-ios-debugger-agent` for simulator screenshots, the UI hierarchy, logs and runtime behavior. It works through the Xcode MCP server if that is connected, then MobileBuildMCP if the user has installed it, then `xcodebuild` and `xcrun simctl`.
- Use `evenbetter-accessibility-tests` for runtime accessibility evidence. It runs Apple's accessibility audit in UI tests, at large text sizes and in dark mode, and on Xcode 27 it also walks each screen with VoiceOver. It tests the findings of an evenbetter-analyze report, and only the screens that have them, so run evenbetter-analyze on the built code first.
- Use `evenbetter-ios-app-intents` when feature actions should appear in Siri, Shortcuts, Spotlight, widgets, controls, or other system surfaces.
- Use `evenbetter-swiftui-performance-audit` only when UX issues involve sluggish scrolling, heavy views, hangs, or render-performance regressions.

## Research rules

Read `references/official-sources.md` before making HIG, accessibility, or SwiftUI API claims that matter to the plan or review. Prefer official Apple sources. If browsing or documentation search is used, compare source authority and dates, and cite official links when reporting externally.

Apple's pages render with JavaScript, so a plain fetch can return an empty "requires JavaScript" shell. Prefer a scraper MCP that renders pages (Firecrawl, Tavily extract, Exa fetch), or Apple's JSON form: `https://developer.apple.com/tutorials/data/documentation/<path>.json` for API docs and `https://developer.apple.com/tutorials/data/design/human-interface-guidelines/<page>.json` for HIG pages.

For review stages, default to plan + visual + code review. If screenshots are missing and visual evidence matters, ask for specific screenshots by state, such as default, large Dynamic Type, dark mode, error, empty, destructive confirmation, loading, or post-action success.
