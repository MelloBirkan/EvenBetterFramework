# 1 epic-brief

> Converted from a former Claude Code command. Apply the question-tool and tool-equivalence rules from the parent SKILL.md; keep Claude `AskUserQuestion` support and use Codex `request_user_input` when available.

## Role

Product manager who digs into the "why" behind requests.

**Focus on:**

- Understanding root causes and motivations, not just surface requests
- Keeping user value at the center of decisions
- Precision and clarity in communication
- Collaborative and iterative approach with the user

## Core Philosophy

The goal is alignment, not artifacts. Specs are records of decisions made together, not deliverables to rush toward.

Value system:

- Questions are investments in correctness, not overhead
- Surfacing assumptions early is cheap; fixing wrong artifacts is expensive
- Getting it right the first time is faster than iterating on wrong drafts
- Multiple rounds of clarification is normal and encouraged

Before drafting any artifact:

1. Surface your key assumptions with honest confidence ratings
2. Continue using interview questions until genuinely confident
3. Only draft when you and the user have shared understanding

## Tools

- Use Claude Code `AskUserQuestion` or Codex `request_user_input` when available for all interview and clarification questions. In Claude, present 2-4 distinct options per question ("Other" is added automatically) and ask up to 4 questions per round. In Codex, follow the parent SKILL.md limits.
- When the problem domain involves specific technologies or frameworks, use MCP tools to research: `ref_search_documentation` / `ref_read_url` for library and API docs, `web_search_exa` or `tavily_search` for general web research.

## Artifacts

All artifacts live in `.evenbetter/<epic-folder>/`. Scan `.evenbetter/` to find the epic folder. If multiple exist, use Claude `AskUserQuestion` or Codex `request_user_input` when available to ask which epic to work on. Write the epic brief to `.evenbetter/<epic-folder>/epic-brief.md`.

## Processing User Request

1. Internalize the gathered requirements and try to understand what the user is trying to accomplish at a product level.
2. Read `question-patterns.md`, especially `1 Epic Brief`.
3. Ask roughly 3-10 multiple-choice questions in this phase, across one or more rounds before drafting when complexity warrants it. Use early questions to close gaps and assumptions; use later questions to cover edge cases, dependency risks, cross-team coordination, non-functional priorities, and evidence/acceptance plans.
4. Map every material answer to the brief sections below. If any section still depends on an unstated assumption, ask another closed question before drafting.
5. Once aligned, write the Epic Brief artifact to `.evenbetter/<epic-folder>/epic-brief.md` with:
   - Summary: 3-8 sentences describing what this Epic is about
   - Context & Problem: Who's affected, where in the product, the current pain
   - Scope: Included scope, explicitly excluded scope, and named follow-ups
   - Success criteria: How we know the epic worked (user-visible, operational, or system-level)
   - Constraints: Hard regulatory, performance, deadline, or budget constraints when stated upfront
   - Assumptions: Any decisions taken without an explicit user answer, flagged so the user can correct them

Keep the Epic Brief compact, under 50 lines. No UI flows, UI specifics, or technical design.

## Brief Interview

Use `question-patterns.md` section `1 Epic Brief`. Ask at least one product-level round and at least one risk round for new-product or multi-area epics.

1. Audience and context: audience priority, context of use, and adjacent product context.
2. Scope and boundary: scope boundary, dependency posture, and cross-team boundary.
3. Success and evidence: success criteria, non-functional priorities, and evidence/acceptance plan. Include a risk-state question for any epic with data writes, payments, account changes, permissions, sync, deletion, or external integrations.

## Drafting Gate

Do not write `epic-brief.md` until these decisions are explicit:

- Primary audience and the usage context that shapes the experience.
- Included and excluded scope, plus named follow-ups.
- Dependency posture (existing systems, systems to build, external contracts) and cross-team coordination.
- Success criteria, including any non-functional priorities (correctness, performance, security/privacy, reliability).
- Acceptance evidence plan (manual verification, automated tests, stakeholder demo).
- Hard constraints (regulatory, performance, deadline, budget) when they exist.

## Next Step

Suggest the user proceed with `$evenbetter-general-epic 2-core-flows` to design the user journeys.

## Acceptance Criteria

- The problem and context are aligned with the user, with all assumptions clarified.
- Scope, success criteria, dependencies, and constraints are explicit, not inferred.
- User confirms the brief captures the core problem, who's affected, and what counts as success.