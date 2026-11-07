---
name: evenbetter-general-epic
description: >-
  Runs a staged, product-first workflow for large work on any stack: clarifying questions, an epic brief, HTML core flows and a tech plan, each validated, then tickets, execution and review. Use when the user wants to plan or build a new product area or a change that spans several flows or teams. For one scoped feature use evenbetter-general-feature; for iOS use evenbetter-ios-epic.
---

# evenbetter-general-epic

Paths in this skill and its references are relative to this SKILL.md's folder.

## Operating model

Use this skill as a staged, question-driven product and engineering workflow for platform-agnostic work. The goal is shared understanding before artifacts, with product decisions flowing into technical decisions. Optimize for exhaustive clarification: do not infer anything you could ask, and do not draft from a one-sentence prompt.

- Ask interview questions until the problem, audience, user journeys, technical approach, data model, integration boundaries, failure handling, and validation decisions are genuinely clear. Before ticket breakdown, expect roughly 3-10 questions per phase on average across `0-trigger-workflow`, `1-epic-brief`, `2-core-flows`, `3-prd-validation`, `4-tech-plan`, and `5-architecture-validation`. The cumulative pre-ticket interview can and should exceed 10 questions when complexity warrants it.
- Do not treat 10 as a total cap. When the request is large or ambiguous (new product, multi-area epic, ambiguous audience, novel domain), 20-40 cumulative questions across rounds is normal. Stop asking only when each artifact section can be drafted from explicit decisions rather than assumptions.
- Treat `0-trigger-workflow`, `1-epic-brief`, and `2-core-flows` as discovery-heavy. Do not draft `epic-brief.md` or `core-flows.html` from a vague prompt; ask enough closed questions to make the intended audience, scope boundaries, primary flows, edge cases, success criteria, dependencies, and constraints explicit.
- In `2-core-flows`, ask flow-by-flow questions before writing `core-flows.html`. Every primary flow needs a decided entry point, step sequence, primary action, feedback/state model, completion destination, cancellation/back behavior, failure/recovery path, and notable edge cases. The flows artifact is a self-contained HTML file with inline CSS that includes a visual preview of each flow alongside the prose; previews are visual only and do not need to be interactive.
- Prefer concrete multiple-choice options with a recommended default when one is defensible. Use open-text follow-ups only when the answer space cannot reasonably be enumerated (for example, naming an external system, citing a regulatory requirement, or pasting an existing schema).
- If the user chooses "Other," convert their answer into a concrete assumption and immediately continue with another closed question if any uncertainty remains.
- Use early questions in each phase to close gaps and assumptions. Use later rounds to cover edge cases, failure states, auth/permissions, offline/degraded behavior, data conflicts, destructive actions, scaling concerns, and any decisions the user has not explicitly confirmed.
- Prefer returning to the relevant earlier phase over carrying an unresolved assumption forward. Do not proceed to ticket breakdown while a high-impact product, flow, data, integration, failure-mode, or architecture decision is still implicit.
- Surface your key assumptions explicitly before drafting any section and ask the user to confirm or correct each one.
- Ground recommendations in the actual codebase before planning or reviewing implementation.
- Keep artifacts in `.evenbetter/<epic-name>/`, reusing an existing EvenBetter epic folder when the target is clear.
- Treat the Epic Brief, Core Flows, and Tech Plan as source specs; tickets derive from those specs.
- Load only the reference for the current stage, plus `references/question-patterns.md` when its option banks would close gaps faster.

A stage name given as the argument (for example `4-tech-plan`) selects that stage.

The `3-prd-validation` and `5-architecture-validation` stages review specs before any code is written. They are not the evenbetter-validate skill, which checks an evenbetter-analyze audit report for an iOS project.

## Question tooling

Ask with the host's structured question tool when it has one:

- Claude Code: `AskUserQuestion`, with 2-4 mutually exclusive options per question and up to 4 questions per round.
- Codex in Plan mode: `request_user_input`, with 1-3 short questions of 2-3 options each, the recommended option first and marked "(Recommended)". The client adds "Other". Plan mode is read-only, so present results in a `<proposed_plan>` block and ask the user to switch to Default mode before writing `.evenbetter/` files or editing code.
- Codex in Default mode: ask one concise closed question with numbered options in plain text, then wait. Use `request_user_input` instead if the session offers it.
- Other agents: use their structured question tool, or ask one closed question with numbered options.
- When nobody can answer, because the user said they will not be around or asked you to go ahead without questions, or because the run is one-shot and non-interactive (such as `claude -p`, `codex exec`, CI or a scheduled task), do not end the turn on a clarifying question. Take the recommended option, say which one you took, and record it as an assumption in the artifact or the final reply. Never assume an approval the user has not given, such as accepting a plan or starting to edit code: finish the current stage and end with what waits on the person. Any exception this skill names elsewhere still applies.

Keep each round focused. Multiple clarification rounds per phase are expected. Ask only the current round's questions. Leave later topics for their own round, with options, instead of listing them as open questions at the end. Use the first questions in a phase to close gaps and assumptions, then use later rounds to cover edge cases, failure states, integration risks, data conflicts, security/permissions, and cross-spec consistency. Prefer returning to the relevant earlier phase over carrying unresolved assumptions forward.

## Tool equivalents

The references use Claude Code tool names. In Codex, use these equivalents, and do not simulate a tool the session does not have:

| Claude Code | Codex |
| --- | --- |
| `AskUserQuestion` | `request_user_input` (Plan mode, or Default mode when enabled); otherwise a closed plain-text question |
| `Glob`, `Grep`, `Read` | `rg --files`, `rg`, and shell reads such as `sed -n` or `nl` through `exec_command` |
| `Edit`, `Write` | `apply_patch` (Default mode only) |
| `Bash` | `exec_command` |
| `TaskCreate`, `TaskUpdate` | `update_plan` (Default mode only; in Plan mode keep the steps in `<proposed_plan>`) |
| `WebSearch`, `WebFetch` | `web_search`, or a configured MCP search or fetch tool such as Firecrawl, Tavily or Exa; `curl` through `exec_command` where network access is allowed |
| `ref_search_documentation`, `ref_read_url` | any documentation MCP the session has; otherwise official documentation through the web tools above |
| `Agent` | `spawn_agent`, then `wait_agent` |

A stage that says to delegate is itself the request to delegate. Codex agents share one working directory, so run tickets in parallel only when their files do not overlap.

If current system, developer or user instructions conflict with this skill, follow them.

## Stage selection

Infer the stage from the user request. If the user gives no stage and there is no active `.evenbetter` epic, start with `0-trigger-workflow`, which opens with a scope check that can hand the request to evenbetter-general-feature or evenbetter-ios-epic. If there are multiple epic folders and the correct one is unclear, ask the user which one to use.

| Stage | Reference | Use when |
| --- | --- | --- |
| `0-trigger-workflow` | `references/0-trigger-workflow.md` | Check the request's size, turn it into clarified requirements, and create the `.evenbetter/<epic-name>/` folder. |
| `1-epic-brief` | `references/1-epic-brief.md` | Define the problem, affected users, context, and scope. |
| `2-core-flows` | `references/2-core-flows.md` | Design product-level user journeys and interaction flows. |
| `3-prd-validation` | `references/3-prd-validation.md` | Validate requirements clarity and completeness before technical planning. |
| `4-tech-plan` | `references/4-tech-plan.md` | Create the technical architecture grounded in product specs and codebase reality. |
| `5-architecture-validation` | `references/5-architecture-validation.md` | Stress-test technical decisions before ticketing. |
| `6-ticket-breakdown` | `references/6-ticket-breakdown.md` | Convert specs into story-sized implementation tickets. |
| `7-execute` | `references/7-execute.md` | Execute tickets in dependency order and validate each batch. |
| `8-implementation-validation` | `references/8-implementation-validation.md` | Review implementation against specs and tickets. |
| `9-revise-requirements` | `references/9-revise-requirements.md` | Propagate changed requirements through specs and tickets. |
| `10-cross-artifact-validation` | `references/10-cross-artifact-validation.md` | Check consistency across specs and tickets. |

## Artifact rules

- Create `.evenbetter/` if it does not exist.
- Derive `<epic-name>` as short, descriptive kebab-case.
- Store the epic brief at `.evenbetter/<epic-name>/epic-brief.md`.
- Store core flows at `.evenbetter/<epic-name>/core-flows.html`. The file is self-contained HTML with inline CSS; each flow includes a non-interactive visual preview of every meaningful step.
- Store the tech plan at `.evenbetter/<epic-name>/tech-plan.md`.
- Store tickets at `.evenbetter/<epic-name>/tickets/TICKET-NNN.md`.
- Update existing artifacts surgically. Preserve decisions that still hold.
- When a stage says to ask for confirmation or alignment, do that before writing or revising artifacts.
- Write artifacts only when the session can edit files. In Codex Plan mode, show the draft in a `<proposed_plan>` block and ask the user to switch to Default mode to save it.

## Research rules

Ground technical recommendations in the actual codebase before proposing architecture. Use current, primary documentation when API behavior, library constraints, platform rules, or framework guidance might matter.

For documentation, prefer official sources, read through a documentation MCP server such as Ref when the session has one. If you use web search, compare dates and source authority, and cite sources when reporting externally.

## Anti-patterns

Do not:

- Draft any source spec (`epic-brief.md`, `core-flows.html`, `tech-plan.md`) before the relevant phase questions are answered.
- Skip clarification rounds for efficiency. Treat questions as investments in correctness; treat inference as a cost.
- Ask "anything else?" or broad discovery questions. Convert open uncertainty into concrete closed questions.
- Stop at one round of answers when the user's request is large, ambiguous, or new-domain. Multiple rounds per phase are normal.
- Carry uncommunicated assumptions forward. Either ask, or record the assumption in-spec with a confidence note so the user can correct it.
