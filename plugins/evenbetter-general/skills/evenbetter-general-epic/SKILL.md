---
name: evenbetter-general-epic
description: Platform-agnostic product-first epic workflow for larger scoped work. Use when the user wants to clarify an epic, write an epic brief, design core flows, validate product requirements, create a technical plan, validate architecture, break specs into tickets, execute tickets, validate implementation, revise requirements, or check cross-spec consistency without a platform-specific design system such as Apple HIG or Material Design 3. Trigger on general epic workflow, epic brief, core flows, PRD validation, tech plan, architecture validation, ticket breakdown, implementation validation, revise requirements, cross-artifact validation, or former epic slash-command stage requests.
---

# evenbetter-general-epic

## Operating model

Use this skill as a staged, question-driven product and engineering workflow for platform-agnostic work. The goal is shared understanding before artifacts, with product decisions flowing into technical decisions.

- Ask questions until the problem, user journeys, technical approach, or validation decision is genuinely clear.
- Surface assumptions explicitly before committing them to artifacts.
- Keep artifacts in `.evenbetter/<epic-name>/`.
- Treat the Epic Brief, Core Flows, and Tech Plan as source specs; tickets derive from those specs.
- Load only the reference for the current stage, then follow that stage precisely.

Former slash-command names in the references are aliases. Interpret `/epic:4-tech-plan` as "use `$evenbetter-general-epic` with stage `4-tech-plan`."

## Question tooling

For all interviews, clarification rounds, refinement choices, and user decisions, use the best available user-question mechanism:

- Claude Code: keep using `AskUserQuestion`.
- Codex Plan mode: use `request_user_input` when it is available. Ask 1-3 short questions, give 2-3 mutually exclusive choices per question, put the recommended choice first when there is one, and rely on the client-added "Other" option.
- Codex Default mode or any environment without a structured question tool: ask concise plain-text questions and wait for the user. Do not simulate a tool call.

Keep each round focused. Claude references allow up to 4 questions per round; Codex `request_user_input` supports up to 3. Multiple clarification rounds are expected.

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
