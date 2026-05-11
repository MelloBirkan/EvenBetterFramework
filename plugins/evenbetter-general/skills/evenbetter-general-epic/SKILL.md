---
name: evenbetter-general-epic
description: Platform-agnostic product-first epic workflow for larger scoped work. Use when the user wants to clarify an epic, write an epic brief, design core flows, validate product requirements, create a technical plan, validate architecture, break specs into tickets, execute tickets, validate implementation, revise requirements, or check cross-spec consistency without a platform-specific design system such as Apple HIG or Material Design 3. Trigger on general epic workflow, epic brief, core flows, PRD validation, tech plan, architecture validation, ticket breakdown, implementation validation, revise requirements, cross-artifact validation, or former epic slash-command stage requests.
---

# evenbetter-general-epic

## Operating model

Use this skill as a staged, question-driven product and engineering workflow for platform-agnostic work. The goal is shared understanding before artifacts, with product decisions flowing into technical decisions. Optimize for exhaustive clarification: do not infer anything you could ask, and do not draft from a one-sentence prompt.

- Ask interview questions until the problem, audience, user journeys, technical approach, data model, integration boundaries, failure handling, and validation decisions are genuinely clear. Before ticket breakdown, expect roughly 3-10 questions per phase on average across `0-trigger-workflow`, `1-epic-brief`, `2-core-flows`, `3-prd-validation`, `4-tech-plan`, and `5-architecture-validation`. The cumulative pre-ticket interview can and should exceed 10 questions when complexity warrants it.
- Do not treat 10 as a total cap. When the request is large or ambiguous (new product, multi-area epic, ambiguous audience, novel domain), 20-40 cumulative questions across rounds is normal. Stop asking only when each artifact section can be drafted from explicit decisions rather than assumptions.
- Treat `0-trigger-workflow`, `1-epic-brief`, and `2-core-flows` as discovery-heavy. Do not draft `epic-brief.md` or `core-flows.md` from a vague prompt; ask enough closed questions to make the intended audience, scope boundaries, primary flows, edge cases, success criteria, dependencies, and constraints explicit.
- In `2-core-flows`, ask flow-by-flow questions before writing `core-flows.md`. Every primary flow needs a decided entry point, step sequence, primary action, feedback/state model, completion destination, cancellation/back behavior, failure/recovery path, and notable edge cases.
- Prefer concrete multiple-choice options with a recommended default when one is defensible. Use open-text follow-ups only when the answer space cannot reasonably be enumerated (for example, naming an external system, citing a regulatory requirement, or pasting an existing schema).
- If the user chooses "Other," convert their answer into a concrete assumption and immediately continue with another closed question if any uncertainty remains.
- Use early questions in each phase to close gaps and assumptions. Use later rounds to cover edge cases, failure states, auth/permissions, offline/degraded behavior, data conflicts, destructive actions, scaling concerns, and any decisions the user has not explicitly confirmed.
- Prefer returning to the relevant earlier phase over carrying an unresolved assumption forward. Do not proceed to ticket breakdown while a high-impact product, flow, data, integration, failure-mode, or architecture decision is still implicit.
- Surface your key assumptions explicitly before drafting any section and ask the user to confirm or correct each one.
- Ground recommendations in the actual codebase before planning or reviewing implementation.
- Keep artifacts in `.evenbetter/<epic-name>/`, reusing an existing EvenBetter epic folder when the target is clear.
- Treat the Epic Brief, Core Flows, and Tech Plan as source specs; tickets derive from those specs.
- Load only the reference for the current stage plus `question-patterns.md` when option banks would help close gaps faster.

Former slash-command names in the references are aliases. Interpret `/epic:4-tech-plan` as "use `$evenbetter-general-epic` with stage `4-tech-plan`."

## Question tooling

For all interviews, clarification rounds, refinement choices, and user decisions, use the best available user-question mechanism:

- Claude Code: use `AskUserQuestion` with 2-4 mutually exclusive options per question. Up to 4 questions per round.
- Codex Plan mode: use `request_user_input` when it is available. Ask 1-3 short questions per round, give 2-3 mutually exclusive choices per question, put the recommended choice first when there is one, and rely on the client-added "Other" option.
- Codex Default mode or any environment without a structured question tool: ask concise plain-text questions and wait for the user. Do not simulate a tool call.
- Cursor or other agents with an ask-question tool: use the native structured question tool with mutually exclusive options.

Keep each round focused. Multiple clarification rounds per phase are expected. Use the first questions in a phase to close gaps and assumptions, then use later rounds to cover edge cases, failure states, integration risks, data conflicts, security/permissions, and cross-spec consistency. Prefer returning to the relevant earlier phase over carrying unresolved assumptions forward.

## Tool equivalents

The reference files were converted from Claude Code commands and may mention Claude tool names. Apply these equivalents in Codex:

| Claude command instruction | Codex equivalent |
| --- | --- |
| `AskUserQuestion` | `request_user_input` when available, otherwise concise plain-text questions |
| `Glob`, `Grep`, `Read` | `rg --files`, `rg`, and shell file reads such as `sed` or `nl` |
| `Bash` | `exec_command` |
| `TaskCreate`, `TaskUpdate` | `update_plan` |
| `Agent` | `spawn_agent` only when current instructions allow delegation and the user has explicitly permitted agent work; otherwise do the work locally |
| `ref_search_documentation`, `ref_read_url` | use the available Ref MCP tools if present; otherwise use official docs or web search when current instructions require current or source-backed information |
| `web_search_exa`, `tavily_search` | use the available web-search mechanism, preferring primary sources for technical claims |

If current system or developer instructions conflict with a converted reference, follow the current higher-priority instruction.

## Stage selection

Infer the stage from the user request. If the user gives no stage and there is no active `.evenbetter` epic, start with `0-trigger-workflow`. If there are multiple epic folders and the correct one is unclear, ask the user which one to use.

| Stage | Reference | Use when |
| --- | --- | --- |
| `0-trigger-workflow` | `references/0-trigger-workflow.md` | Turn an initial request into clarified requirements and create the `.evenbetter/<epic-name>/` folder. |
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
- Store core flows at `.evenbetter/<epic-name>/core-flows.md`.
- Store the tech plan at `.evenbetter/<epic-name>/tech-plan.md`.
- Store tickets at `.evenbetter/<epic-name>/tickets/TICKET-NNN.md`.
- Update existing artifacts surgically. Preserve decisions that still hold.
- When a stage says to ask for confirmation or alignment, do that before writing or revising artifacts.

## Research rules

Ground technical recommendations in the actual codebase before proposing architecture. Use current, primary documentation when API behavior, library constraints, platform rules, or framework guidance might matter.

When documentation research is needed, prefer official docs through Ref MCP if available. If using web search, compare dates and source authority, and cite sources when reporting externally.

## Anti-patterns

Do not:

- Draft any source spec (`epic-brief.md`, `core-flows.md`, `tech-plan.md`) before the relevant phase questions are answered.
- Skip clarification rounds for efficiency. Treat questions as investments in correctness; treat inference as a cost.
- Ask "anything else?" or broad discovery questions. Convert open uncertainty into concrete closed questions.
- Stop at one round of answers when the user's request is large, ambiguous, or new-domain. Multiple rounds per phase are normal.
- Carry uncommunicated assumptions forward. Either ask, or record the assumption in-spec with a confidence note so the user can correct it.
