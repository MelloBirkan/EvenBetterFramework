# 0 trigger_workflow

> Converted from a former Claude Code command. Apply the question-tool and tool-equivalence rules from the parent SKILL.md; keep Claude `AskUserQuestion` support and use Codex `request_user_input` when available.

## Collaboration Philosophy

The philosophy and goal of this workflow is alignment, coming to a set of decisions made together, not deliverables to rush toward.

Value system:

- Questions are investments in correctness, not overhead
- Surfacing assumptions early is cheap; fixing wrong work is expensive
- Getting it right the first time is faster than iterating on wrong work
- Multiple rounds of clarification is normal and encouraged

Before proceeding to the next step:

1. Surface your key assumptions with genuine honesty
2. Continue asking questions until genuinely confident
3. Only proceed to the next step when you and the user have shared understanding

## Multi-Round Clarification

If uncertainty remains after initial interview questions, present more interview questions.

- Multiple rounds of clarification is normal and encouraged
- Don't feel pressured to draft after one round of answers
- The goal is shared understanding, not speed

## Tools

- Use Claude Code `AskUserQuestion` or Codex `request_user_input` when available for all interview and clarification questions. In Claude, present 2-4 distinct options per question ("Other" is added automatically) and ask up to 4 questions per round. In Codex, follow the parent SKILL.md limits.
- When the user's request involves specific technologies, frameworks, or domains you need more context on, use MCP tools to research: `ref_search_documentation` / `ref_read_url` for library and API docs, `web_search_exa` or `tavily_search` for general web research.

## User Request

The user's current request or stage arguments

## Processing User Request

1. Internalize the user's request above and identify whether it is a new product, multi-area epic, redesign, refactor, or investigation.
2. Inspect the repo enough to discover likely architecture, primary entry points, and existing `.evenbetter/` folders.
3. Read `question-patterns.md`, especially `0 Trigger Workflow`.
4. If an existing `.evenbetter/<epic-name>/` folder clearly matches, reuse it. If multiple folders match, ask the user to choose from concrete options.
5. Ask roughly 3-10 multiple-choice questions in this phase, across one or more rounds depending on complexity, until the product shape, audience, primary goal, initial scope, success measure, dependency posture, and constraint posture are clear.
6. Use later rounds to cover edge cases and unspoken assumptions (failure handling, auth/permissions, offline/degraded mode, destructive actions). Do not create the epic folder from only a one-sentence prompt unless the scope is already explicit.
7. Create `.evenbetter/<epic-name>/` only after the epic name and scope are clear.
8. Summarize the agreed requirements concisely and recommend `1-epic-brief` next.

Note: This step is for REQUIREMENT GATHERING and EPIC FOLDER CREATION only. No spec artifacts are created here.

## Question Rounds

Use the option banks in `question-patterns.md`. Keep each round to 1-4 closed questions (Claude) or 1-3 (Codex).

1. Problem shape and audience: product shape, epic scale, primary user audience, and primary user goal.
2. Scope and success: initial scope inventory, success measure, and constraint posture (technical, regulatory, performance, deadline).
3. Edge-case pass: failure handling posture, auth/permissions, offline/degraded mode, destructive actions, and integration boundary. Ask this round whenever the request involves data creation, submission, account state, permissions, sync, deletion, payments, integrations, or background processing.

## Next Step

Suggest the user proceed with `$evenbetter-general-epic 1-epic-brief` to define the problem and scope.

## Acceptance Criteria

- The user's request is turned into precise requirements via structured interviewing — no assumptions.
- The correct `.evenbetter/<epic-name>/` folder exists or is selected.
- The user is satisfied with the requirements.
- No epic brief, core flows, tech plan, tickets, or review artifact is written in this stage.

## Principles

- User intent first: Workflow guides but user directs.
- Questions are investments in correctness, not overhead. Treat inference as a cost; ask whenever a closed question would resolve the ambiguity.