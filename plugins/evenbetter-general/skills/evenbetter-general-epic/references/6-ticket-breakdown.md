# 6 ticket-breakdown

> Converted from a former Claude Code command. Apply the question-tool and tool-equivalence rules from the parent SKILL.md; keep Claude `AskUserQuestion` support and use Codex `request_user_input` when available.

## Tools

- Use Claude Code `AskUserQuestion` or Codex `request_user_input` when available to present refinement options and gather feedback on the ticket breakdown. In Claude, present 2-4 distinct options per question ("Other" is added automatically) and ask up to 4 questions per round. In Codex, follow the parent SKILL.md limits.
- Use `Read` to review spec files (Epic Brief, Core Flows, Tech Plan).

## Artifacts

All artifacts live in `.evenbetter/<epic-folder>/`. Scan `.evenbetter/` to find the epic folder. If multiple exist, use Claude `AskUserQuestion` or Codex `request_user_input` when available to ask which epic to work on. Read specs from `.evenbetter/<epic-folder>/` and write tickets to `.evenbetter/<epic-folder>/tickets/TICKET-NNN.md`.

## Processing User Request

1. Infer the area to prioritize for tickets from the arguments.
2. Review specs (Epic Brief, Core Flows, Tech Plan) and identify natural work units.
3. Apply best judgment to create ticket breakdown:

Consider:

    - How to group work (by component, by flow, by layer)
    - What dependencies exist between pieces of work
    - What order makes sense for implementation

    Prefer coarse groupings:

    - Group by component or layer, not by individual function
    - Group by flow, not by step
    - Each ticket should be story-sized-meaningful work, not a single function

    Anti-pattern: Do NOT over-breakdown. The minimal least set of tickets is better than multiple small ones.

1. Draft tickets using best judgment:

For each ticket:

    - **Status**: Always start the ticket file with a `## Status` section containing an unchecked `- [ ] Completed` checkbox. The `7-execute` stage flips it to `- [x] Completed` only after the ticket is implemented and validated.
    - **Title**: Action-oriented
    - **Scope**: What's included, what's explicitly out
    - **Spec references**: Link to relevant Epic Brief, Core Flows, Tech Plan sections
    - **Dependencies**: What must be completed first (if any)

Ticket file skeleton:

```markdown
# TICKET-NNN: <Title>

## Status
- [ ] Completed

## Scope
...
```

1. Present the proposed ticket breakdown to the user.

Use a mermaid diagram to visualize ticket dependencies for quick reference.

1. After presenting, offer refinement options (whatever are applicable and make sense):
    - Change ticket granularity (combine related work or split for parallel work/ clarity)
    - Reorganize dependencies or implementation order
    - Different grouping approach (by component, by flow, etc.)
1. Iterate based on feedback until the breakdown is right.
2. Once finalized, write each ticket as an individual file to `.evenbetter/<epic-folder>/tickets/TICKET-NNN.md`.

## Next Step

Present the following options to the user:
1. `$evenbetter-general-epic 7-execute` — begin implementation of the tickets (required next step)
2. `$evenbetter-general-epic 10-cross-artifact-validation` — validate consistency across all specs and tickets before executing (optional intermediate step)

