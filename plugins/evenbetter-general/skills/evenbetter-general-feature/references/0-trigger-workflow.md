# 0 trigger_workflow

> This stage follows the question tooling, tool equivalents and artifact rules in SKILL.md.

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

- Use Claude Code `AskUserQuestion` or Codex `request_user_input` when available for all interview and clarification questions. In Claude, present 2-4 distinct options per question ("Other" is added automatically) and ask up to 4 questions per round. In Codex, follow the SKILL.md limits.
- When the request involves technologies, frameworks or domains you need more context on, research them with the documentation and search tools the session has: the Ref `ref_search_documentation` and `ref_read_url` tools for library and API docs when the Ref server is connected, and a search tool such as Exa `web_search_exa`, Tavily `tavily_search` or the host's web search for general research.

## User Request

The user's current request or stage arguments

## Processing User Request

1. Internalize the user's request above and identify whether it is a product-facing feature, pure technical work (refactor, performance, infrastructure, bug fix), or mixed work with user-visible consequences.
2. Run the scope check below, and continue with these steps only if the request stays with this skill.
3. Inspect the repo enough to discover likely architecture, primary entry points, related code, and existing `.evenbetter/` folders.
4. Read `references/question-patterns.md`, especially `0 Trigger Workflow`.
5. If an existing `.evenbetter/<feature-name>/` folder clearly matches, reuse it. If multiple folders match, ask the user to choose from concrete options.
6. Ask roughly 3-10 multiple-choice questions in this phase, across one or more rounds depending on complexity, until the work nature, primary goal, entry point, audience, scope boundary, and existing-behavior posture are clear.
7. Use later rounds to cover edge cases and unspoken assumptions (failure handling, auth/permissions, offline/degraded mode, destructive actions). Do not create the feature folder from only a one-sentence prompt unless the scope is already explicit.
8. Create `.evenbetter/<feature-name>/` only after the feature name and scope are clear.
9. Summarize the agreed requirements concisely and recommend `1-plan` next.

This stage gathers requirements and creates the feature folder. It writes no plan, tickets or review artifacts, because those depend on decisions the later stages make with the user.

## Scope Check

Decide whether the request fits this skill before the intake rounds. A request is epic-sized when it spans several user flows or surfaces, starts a new product or product area, crosses several teams or services, or needs its own brief, flow spec and tech plan before anyone can ticket it.

When the request clearly fits, skip the question. When it looks epic-sized, ask one closed question and wait:

- Switch to the evenbetter-general-epic skill (brief, core flows, tech plan, then tickets). Mark it recommended when the epic signs are clear.
- Keep it here as one feature, with the scope narrowed to a single plan. Mark it recommended when the epic signs are not clear.

If the work is an iOS or SwiftUI screen, also offer the evenbetter-ios-feature skill, which adds Apple HIG and accessibility review. Put it in that same question, or ask it alone when size is not the issue, with the evenbetter-ios-feature skill marked recommended, because iOS work needs its HIG and accessibility review. Offer it only when the session has that skill; it ships in the evenbetter-ios plugin.

If the user picks another skill, stop this workflow without creating a folder and run that skill with the original request, carrying over the answers gathered so far.

## Question Rounds

Use the option banks in `references/question-patterns.md`. Keep each round to 1-4 closed questions (Claude) or 1-3 (Codex). A message ends with this round's questions and nothing after them. Do not list the topics of later rounds, because a bare question with no options invites an open answer; ask each one closed when its round comes.

1. Work shape and goal: work nature (product / technical / mixed), primary user goal or improvement target, entry point, and audience.
2. Scope and constraints: scope boundary, constraint posture, and existing-behavior posture (net-new, extends existing, replaces existing).
3. Edge-case pass: failure handling posture, auth/permissions, offline/degraded mode, and destructive actions. Ask this round whenever the work involves data writes, account state, permissions, sync, deletion, payments, integrations, or background processing.

## Next Step

Suggest running the `1-plan` stage of this skill next to create the plan.

## Acceptance Criteria

- The scope check confirmed the request belongs in this skill, or the user chose to switch skills.
- The user's request is turned into precise requirements via structured interviewing, with no unstated assumptions.
- The correct `.evenbetter/<feature-name>/` folder exists or is selected.
- The user is satisfied with the requirements.
- No plan, tickets, or review artifact is written in this stage.

## Principles

- User intent first: Workflow guides but user directs.
- Questions are investments in correctness, not overhead. Treat inference as a cost; ask whenever a closed question would resolve the ambiguity.
