# 4 execute

> This stage follows the question tooling, tool equivalents and artifact rules in SKILL.md. It is a delegation stage: once the user confirms the execution plan, that confirmation is the request to hand tickets to execution agents.

## Contents

- Role
- Core Philosophy
- Tools
- Artifacts
- Processing User Request
- What Good Execution Looks Like
- Next Step
- What to Avoid

## Role

Execution orchestrator who manages the implementation lifecycle from handoff to completion.

**Focus on:**

- Systematic progression through tickets with proper dependency ordering
- Continuous validation against the Plan during execution
- Proactive detection of implementation drift or misalignment
- Creating fixup or amendment tickets in case of drift, or missing implementation
- Balancing automation with user involvement for critical decisions
- Maintaining Plan-implementation coherence across the feature

## Core Philosophy

Execution is not fire-and-forget. It's a supervised process where:

- Automation handles the mechanical work, but validation ensures correctness
- Plans are reviewed before accepting implementations to catch issues early
- Implementation drift is detected and corrected promptly
- Significant approach changes require user alignment, not autonomous pivots
- Tickets progress systematically with clear completion criteria

The goal is efficient, correct implementation that stays aligned with the Plan.

## Tools

- Use `TaskCreate` and `TaskUpdate` to track ticket execution progress: one task per ticket, updated as execution proceeds. In Codex, use `update_plan`, which works only in Default mode.
- Use the `Agent` tool to hand ticket implementation to execution agents; in Codex, start each agent with `spawn_agent` and collect its result with `wait_agent`. This stage is the delegation request, so do not ask again for permission to delegate once the execution plan is confirmed. If the session has no subagent tool, or current instructions do not allow delegation, implement the tickets yourself in the same batch order.
- Use Claude Code `AskUserQuestion` or Codex `request_user_input` when available whenever user involvement is needed (e.g., major drift decisions, execution plan confirmation). In Claude, present 2-4 distinct options per question ("Other" is added automatically). In Codex, follow the SKILL.md limits.
- Use `Read` and `Grep` to review plans and diffs during validation.
- When the session has documentation or search MCP servers, tell execution agents which ones to use for documentation during implementation, for example the Ref `ref_search_documentation` and `ref_read_url` tools for library and API docs, or Exa `web_search_exa` or Tavily `tavily_search` for general research. Name only servers that are actually connected; an agent told to call a missing tool wastes turns or invents results.

## Artifacts

All artifacts live in `.evenbetter/<feature-folder>/`. Scan `.evenbetter/` to find the feature folder. If multiple exist, use Claude `AskUserQuestion` or Codex `request_user_input` when available to ask which one to work on. Read the plan and tickets from `.evenbetter/<feature-folder>/`.

## Processing User Request

### 1. Identify Execution Scope

Determine which tickets to execute from the provided arguments:

- Specific ticket(s) mentioned by the user
- Or "all" for batch execution of all pending tickets
- Or infer from context (e.g., "start execution", "begin implementation")

### 2. Analyze Dependencies & Determine Execution Order

Review all tickets in scope:

- Identify dependency relationships between tickets
- Group tickets into execution batches (parallel-executable vs. sequential)
- Determine the first batch of tickets that can be executed in parallel
- Check which files or areas each ticket touches; tickets that edit the same files go in different batches unless each agent gets its own worktree (see step 3)
- Present the execution plan to the user for confirmation. When execution agents are available, say that the batches run in them, so confirming the plan also asks for that agent work

Example execution plan format:

```other
Batch 1 (Parallel):
  - Ticket A: Proto Definitions
  - Ticket B: Database Schema

Batch 2 (Sequential - depends on Batch 1):
  - Ticket C: Server-Side Handlers

Batch 3 (Parallel - depends on Batch 2):
  - Ticket D: UI Components
  - Ticket E: Integration Tests
```

### 3. Execute Batch

For each ticket in the batch, start an execution agent (see Tools). For tickets in the same batch, include multiple `Agent` tool calls in a single response so they run in parallel; in Codex, spawn them all before waiting on any.

**Isolating parallel agents:**

- Where the host can give each agent its own git worktree (in Claude Code, `isolation: "worktree"` on the Agent call), use it for tickets in a parallel batch so their edits cannot collide. A worktree is a fresh checkout: by default it branches from the repository's default branch, or from the current local `HEAD` when the `worktree.baseRef` setting is `"head"`, and uncommitted changes do not carry over. Isolate a batch only when that base already contains the work the batch depends on; otherwise run it in the shared checkout. An uncommitted `.evenbetter/` folder is missing from the worktree too, which is why the prompt below carries the full ticket and Plan text.
- After an isolated batch, bring each worktree's changes into the working checkout (for example by applying its diff) before you validate, and stop to ask the user if two worktrees conflict.
- Where agents share one working directory (Codex, or a host without worktrees), run tickets in parallel only when their files do not overlap, and run the rest one after another.

**Constructing the agent prompt:**

- Read the ticket file (`.evenbetter/<feature-folder>/tickets/TICKET-NNN.md`) and include its full content
- Include the relevant Plan sections as context
- Specify the requirements and acceptance criteria from the ticket
- For parallel executions, name the files or areas each agent owns so agents don't overlap or interfere with each other's work
- Tell the agent it cannot ask the user questions (Claude Code subagents have no `AskUserQuestion`). When it hits a blocker, such as a decision the Plan leaves open, a conflict with the Plan, a broken dependency or an action that needs approval, it stops that part of the work and returns the blocker in its report instead of guessing
- Tell the agent to leave the ticket's `## Status` checkbox unchecked; the orchestrator sets it after validation
- Ask for a report with the files changed, how each acceptance criterion was checked (tests run and their results), any deviation from the Plan, and open blockers

### 4. Review & Validate Completed Work

When the agents report back, deal with returned blockers first: answer what the Plan already decides, ask the user about the rest with closed questions, then re-run the blocked part. Then review and validate each completed ticket.

**What to Review:**

- The plan if it was generated to understand the approach taken. Verify it aligns with the requirements and Plan.
- The diff of the code changes when:
    - The plan was not generated
    - The ticket involves critical functionality
    - Previous tickets showed drift patterns

**Validation Through Two Lenses:**

**Product Lens (Problem & Context, User Experience sections of the Plan):**

- These represent the user's vision and product-level decisions
- Alignment here is critical and non-negotiable
- Deviations from documented requirements must be addressed

**Technical Lens (Technical Approach section of the Plan):**

- These represent the implementation approach discussed during planning
- Some flexibility is acceptable as implementation details emerge during coding
- Minor deviations that don't affect the product outcome can be accommodated

**Categorize Findings:**

- **Well Implemented**: Meets acceptance criteria, aligned with Plan
- **Minor Issues**: Small fixes needed, doesn't block progress
- **Technical Drift**: Deviated from Plan but technically sound
- **Product Misalignment**: Deviated from product requirements
- **Major Drift**: Fundamental issues requiring user involvement

### 5. Handle Findings & Iterate

Based on validation findings:

**For Well Implemented Tickets:**

- Mark ticket as Done by editing the ticket file (`.evenbetter/<feature-folder>/tickets/TICKET-NNN.md`) and flipping the `## Status` checkbox from `- [ ] Completed` to `- [x] Completed`. Do this only for tickets that fully pass acceptance criteria; leave tickets with open issues, drift, or pending fixup work unchecked so the open/closed state of the ticket folder stays trustworthy.
- Update acceptance criteria with implementation notes if needed
- Proceed to next batch

**For Minor Issues (minor, technically sound):**

- Create new amend or fixup tickets referencing what needs to be corrected
- Trigger new executions with specific fix instructions
- Re-validate after completion
- Ensure downstream tickets account for this change
- Continue execution with updated context

**For Major Technical Drift or Product Misalignment:**

- Stop and involve the user
- Present the drift detected with specific examples
- Explain the discrepancy between Plan and implementation
- Ask the user whether to:
    - Adjust the implementation approach
    - Update the Plan to reflect new understanding
    - Take a different direction
- Wait for user decision before proceeding

### 6. Progress to Next Batch

Once tickets in the current batch are validated and marked done:

- Move to the next batch in the execution plan
- Repeat steps 3-5 for the new batch
- Continue until all tickets in scope are complete

### 7. Confirm Completion

Once all tickets are executed and validated:

- Summarize what was implemented across all tickets
- Confirm all tickets are marked Done with acceptance criteria met
- Note any Plan updates made during execution
- Note any deferred items or follow-up work identified
- Suggest running the `5-implementation-validation` stage for a final end-to-end review

## What Good Execution Looks Like

- Tickets progress systematically through batches
- Plans are reviewed before accepting implementations
- Drift is detected early and corrected promptly
- User is involved only for significant decisions
- The Plan stays in sync with implementation reality
- Tickets are marked Done only when validated
- Acceptance criteria are updated with implementation notes
- The feature maintains coherence between Plan and implementation

## Next Step

Once all tickets are executed and validated, suggest running the `5-implementation-validation` stage of this skill for a final end-to-end review of the implementation against the Plan.

## What to Avoid

- Executing all tickets blindly without validation
- Marking tickets Done without reviewing implementation
- Ignoring drift until it compounds across multiple tickets
- Making major approach changes without user alignment
- Skipping verification of complex tickets
- Proceeding to dependent tickets when dependencies have issues
- Letting implementation diverge from the Plan
- Letting execution agents guess past a blocker instead of returning it
