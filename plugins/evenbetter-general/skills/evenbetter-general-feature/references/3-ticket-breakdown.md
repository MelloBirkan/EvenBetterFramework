# 3 ticket-breakdown

> This stage follows the question tooling, tool equivalents and artifact rules in SKILL.md.

## Tools

- Use Claude Code `AskUserQuestion` or Codex `request_user_input` when available to present refinement options and gather feedback on the ticket breakdown. In Claude, present 2-4 distinct options per question ("Other" is added automatically) and ask up to 4 questions per round. In Codex, follow the SKILL.md limits.
- Use `Read` to review the Plan.

## Artifacts

All artifacts live in `.evenbetter/<feature-folder>/`. Scan `.evenbetter/` to find the feature folder. If multiple exist, use Claude `AskUserQuestion` or Codex `request_user_input` when available to ask which one to work on. Read the plan from `.evenbetter/<feature-folder>/plan.md` and write tickets to `.evenbetter/<feature-folder>/tickets/TICKET-NNN.md`.

## Processing User Request

1. Infer the area to prioritize for tickets from the arguments.
2. Review the Plan and identify natural work units.
3. Apply best judgment to create ticket breakdown.

   Consider:

   - How to group work (by component, by flow, by layer)
   - What dependencies exist between pieces of work
   - What order makes sense for implementation

   Prefer coarse groupings:

   - Group by component or layer, not by individual function
   - Group by flow, not by step
   - Each ticket should be story-sized, meaningful work, not a single function

   Keep the ticket set as small as the work allows. Every extra ticket adds a handoff and a dependency edge, and a pile of small tickets makes drift harder to see.

4. Draft tickets using best judgment.

   For each ticket:

   - **Status**: Always start the ticket file with a `## Status` section containing an unchecked `- [ ] Completed` checkbox. The `4-execute` stage flips it to `- [x] Completed` only after the ticket is implemented and validated.
   - **Title**: Action-oriented
   - **Scope**: What's included, what's explicitly out
   - **Spec references**: Link to relevant Plan sections
   - **Dependencies**: What must be completed first (if any)

   Ticket file skeleton:

   ```markdown
   # TICKET-NNN: <Title>

   ## Status
   - [ ] Completed

   ## Scope
   ...
   ```

5. Present the proposed ticket breakdown to the user. Use a mermaid diagram to visualize ticket dependencies for quick reference.
6. After presenting, offer the refinement options that apply:
   - Change ticket granularity (combine related work, or split for parallel work or clarity)
   - Reorganize dependencies or implementation order
   - Different grouping approach (by component, by flow, etc.)
7. Iterate based on feedback until the breakdown is right.
8. Once finalized, write each ticket as an individual file to `.evenbetter/<feature-folder>/tickets/TICKET-NNN.md`.

## Next Step

Present the following options to the user:

1. The `4-execute` stage: begin implementation of the tickets (required next step)
2. The `7-cross-artifact-validation` stage: validate consistency across the plan and tickets before executing (optional intermediate step)
