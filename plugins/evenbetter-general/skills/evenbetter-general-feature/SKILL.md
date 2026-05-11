---
name: evenbetter-general-feature
description: Platform-agnostic feature workflow for smaller scoped work. Use when the user wants to gather feature requirements, create or revise an adaptive feature plan, break it into implementation tickets, execute tickets, validate implementation against the plan, or check plan and ticket consistency without a platform-specific design system such as Apple HIG or Material Design 3. Trigger on general feature workflow, feature planning, ticket breakdown, implementation validation, revise requirements, cross-artifact validation, or former slash-command style requests such as feature stages.
---

# evenbetter-general-feature

## Operating model

Use this skill as a staged, question-driven feature workflow for platform-agnostic product and engineering work. The goal is shared understanding before artifacts, not speed. Optimize for exhaustive clarification: do not infer anything you could ask, and do not draft from a one-sentence prompt.

- Ask interview questions until the feature's user goal, in-scope behavior, data shape, integration points, failure modes, and validation decisions are genuinely clear. Before ticket breakdown, expect roughly 3-10 questions per phase on average across `0-trigger-workflow`, `1-plan`, and `2-plan-validation`. The cumulative pre-ticket interview can and should exceed 10 questions when complexity warrants it.
- Do not treat 10 as a total cap. When the request is ambiguous (mixed product/technical work, novel integration, unfamiliar domain), 15-30 cumulative questions across rounds is normal. Stop asking only when each plan section can be drafted from explicit decisions rather than assumptions.
- Treat `0-trigger-workflow` and `1-plan` as discovery-heavy. Do not draft `plan.md` from a vague prompt; ask enough closed questions to make the user goal, in-scope behavior, key flow steps, edge cases, data changes, integration boundaries, and constraints explicit.
- For product-facing work, ask flow-by-flow questions before drafting the User Experience section: each affected flow needs a decided entry point, primary action, feedback model, completion state, cancellation/back behavior, and failure/recovery path.
- For technical work, ask architecture-by-decision questions before drafting the Technical Approach section: each defining choice needs a decided pattern, integration boundary, data shape, failure behavior, and codebase-fit justification.
- Prefer concrete multiple-choice options with a recommended default when one is defensible. Use open-text follow-ups only when the answer space cannot reasonably be enumerated (for example, naming an external system, citing a regulatory requirement, or pasting an existing schema).
- If the user chooses "Other," convert their answer into a concrete assumption and immediately continue with another closed question if any uncertainty remains.
- Use early questions in each phase to close gaps and assumptions. Use later rounds to cover edge cases, failure states, auth/permissions, offline/degraded behavior, data conflicts, destructive actions, scaling concerns, and any decisions the user has not explicitly confirmed.
- Prefer returning to `0-trigger-workflow` for missing requirements over carrying an unresolved assumption forward. Do not proceed to ticket breakdown while a high-impact product, flow, data, integration, failure-mode, or architecture decision is still implicit.
- Surface your key assumptions explicitly before drafting any plan section and ask the user to confirm or correct each one.
- Ground recommendations in the actual codebase before planning or reviewing implementation.
- Keep artifacts in `.evenbetter/<feature-name>/`, reusing an existing EvenBetter feature folder when the target is clear.
- Treat the feature plan as the source of truth and tickets as derivatives.
- Load only the reference for the current stage plus `question-patterns.md` when option banks would help close gaps faster.

Former slash-command names in the references are aliases. Interpret `/feature:1-plan` as "use `$evenbetter-general-feature` with stage `1-plan`."

## Question tooling

For all interviews, clarification rounds, refinement choices, and user decisions, use the best available user-question mechanism:

- Claude Code: use `AskUserQuestion` with 2-4 mutually exclusive options per question. Up to 4 questions per round.
- Codex Plan mode: use `request_user_input` when it is available. Ask 1-3 short questions per round, give 2-3 mutually exclusive choices per question, put the recommended choice first when there is one, and rely on the client-added "Other" option.
- Codex Default mode or any environment without a structured question tool: ask concise plain-text questions and wait for the user. Do not simulate a tool call.
- Cursor or other agents with an ask-question tool: use the native structured question tool with mutually exclusive options.

Keep each round focused. Multiple clarification rounds per phase are expected. Use the first questions in a phase to close gaps and assumptions, then use later rounds to cover edge cases, failure states, integration risks, data conflicts, security/permissions, and cross-spec consistency. Prefer returning to `0-trigger-workflow` over carrying unresolved assumptions forward.

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

Infer the stage from the user request. If the user gives no stage and there is no active `.evenbetter` feature, start with `0-trigger-workflow`. If there are multiple feature folders and the correct one is unclear, ask the user which one to use.

| Stage | Reference | Use when |
| --- | --- | --- |
| `0-trigger-workflow` | `references/0-trigger-workflow.md` | Turn an initial feature request into clarified requirements and create the `.evenbetter/<feature-name>/` folder. |
| `1-plan` | `references/1-plan.md` | Create the adaptive plan in `.evenbetter/<feature-name>/plan.md`. |
| `2-plan-validation` | `references/2-plan-validation.md` | Stress-test the plan before ticketing or implementation. |
| `3-ticket-breakdown` | `references/3-ticket-breakdown.md` | Convert the plan into story-sized tickets. |
| `4-execute` | `references/4-execute.md` | Execute tickets in dependency order and validate each batch. |
| `5-implementation-validation` | `references/5-implementation-validation.md` | Review implementation against the plan and tickets. |
| `6-revise-requirements` | `references/6-revise-requirements.md` | Propagate changed requirements through the plan and tickets. |
| `7-cross-artifact-validation` | `references/7-cross-artifact-validation.md` | Check consistency between plan sections and tickets. |

## Artifact rules

- Create `.evenbetter/` if it does not exist.
- Derive `<feature-name>` as short, descriptive kebab-case.
- Store the plan at `.evenbetter/<feature-name>/plan.md`.
- Store tickets at `.evenbetter/<feature-name>/tickets/TICKET-NNN.md`.
- Update existing artifacts surgically. Preserve decisions that still hold.
- When a stage says to ask for confirmation or alignment, do that before writing or revising artifacts.

## Research rules

Ground technical recommendations in the actual codebase before proposing architecture. Use current, primary documentation when API behavior, library constraints, platform rules, or framework guidance might matter.

When documentation research is needed, prefer official docs through Ref MCP if available. If using web search, compare dates and source authority, and cite sources when reporting externally.

## Anti-patterns

Do not:

- Draft `plan.md` before the relevant phase questions are answered.
- Skip clarification rounds for efficiency. Treat questions as investments in correctness; treat inference as a cost.
- Ask "anything else?" or broad discovery questions. Convert open uncertainty into concrete closed questions.
- Stop at one round of answers when the user's request is ambiguous, novel-domain, or mixed product/technical. Multiple rounds per phase are normal.
- Carry uncommunicated assumptions forward. Either ask, or record the assumption in-plan with a confidence note so the user can correct it.
