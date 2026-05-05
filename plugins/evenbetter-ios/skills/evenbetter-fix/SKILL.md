---
name: evenbetter-fix
description: Per-issue interactive remediator for EvenBetter iOS analyzer findings in the current or supplied project directory. Use when asked to fix issues from analyze-{N}.json, apply fixes after evenbetter-validate has corrected analyzer JSON, walk through findings with the user, or coordinate remediation batches for an analyzed project with .evenbetter/manifest.json history. The skill scopes severity once, then asks per-issue which problem to address and which fix_options option to apply (with skip/defer/reject as alternatives) using Claude Code AskUserQuestion or Codex request_user_input, dispatches sub-agents per file group to apply only the user-selected options, never invents new fix prompts, and updates analyzer state and manifest after each fix. Defaults to the current working directory when no project path is provided.
---

# evenbetter-fix

## Overview

Coordinate the fix step of the EvenBetter loop. Read numbered findings from `.evenbetter/analyze-{N}.json`, scope once, then walk the user through findings one at a time using closed-ended choices grounded in the analyzer's `fix_options`. The user picks which issues to address and exactly how to address each one (e.g., for a small tap target: enlarge frame, wrap content in a `Button`, promote to a Tab Bar item, or skip). Sub-agents apply only the user-approved option per file group.

This skill never invents new `ai_fix_prompt` or `fix_options`; both come from the analyzer report and pass through unchanged.

## Inputs

- `projectPath` (optional): Filesystem path to the analyzed project. Default to the host's current working directory when omitted or `.`.
- Optional user intent from the prompt: severity scope, domain or file filters, batch size, remediation preference, request to use raw analyzer findings.

Resolve `projectPath` to an absolute path before use. If the user supplies a relative path, resolve it against the host's current working directory. Do not ask for a full path solely because `projectPath` is omitted or relative.

## Report Source Precedence

Load reports from `projectPath/.evenbetter/` in this order:

1. `manifest.json` as the source of truth for numbered report history.
2. Newest validated analyzer report `analyze-{N}.json` (manifest run has `validated: true`).
3. Newest unvalidated analyzer report only when validation has not run yet, or when the user explicitly asks for unvalidated scope.
4. Older analyzer runs listed in the manifest for unresolved items still `open` or `deferred`.
5. Legacy `analyze.json` only when no manifest exists; perform the documented auto-migration to `analyze-1.json` and initialize `manifest.json` before continuing.

Default to `state.status = "open"` findings. Include `deferred` only when the user explicitly opts in. Skip `fixed`, `rejected`, and `duplicate_of`.

Before writing any state update, reread `manifest.json` from disk. Only one analyzer/validator/fixer run writes `.evenbetter/` at a time.

## Step 1 — Build The Working Set

Build work items keyed by violation `id` across all manifest runs:

- Keep the latest occurrence of each ID as the display/source context.
- Preserve the originating analyzer run path so the mutable `state` can be written back there.
- Skip `fixed`, `rejected`, `duplicate_of`. Include `deferred` only when explicitly opted in.

Each work item must carry: `work_item_id` (== violation `id`), `source_report` path, `originating_run`, `rule_id`, `severity`, `domain`, `dimension`, `file_path`, `line_number`, `summary`, `fix_description`, optional `fix_code`, `ai_fix_prompt`, `fix_options`, `guideline_reference`, and current `state`.

Reject path traversal: resolve source files as `projectPath / file_path` and ensure they stay inside `projectPath`; resolve report paths inside `.evenbetter/` only.

## Step 2 — One-Shot Scoping

Ask scoping questions in a single turn using a question tool:

- **Claude Code:** `AskUserQuestion` with up to 4 questions per call, 2-4 options each. The "Other" choice is added automatically.
- **Codex Plan mode:** `request_user_input` when available with the same shape (1-3 questions, 2-3 choices each).
- **Otherwise:** plain-text closed questions; do not simulate an unavailable tool.

Cover these decisions only when not already clear from the prompt. Pick at most 3-4 questions:

| Question | Header | Default options |
|---|---|---|
| "Severity scope?" | `Severity` | `Errors only` (Recommended) / `Errors + warnings` / `Everything` / `Pick by file` |
| "Prioritization?" | `Order` | `Accessibility first` (Recommended) / `Severity first` / `Files w/ most findings` / `Source order` |
| "Include deferred findings?" | `Deferred` | `No` (Recommended) / `Yes` / `Review-only, no edits` |
| "Default for ambiguous fixes?" | `Default` | `Apply recommended` (Recommended) / `Ask me each time` / `Skip ambiguous` |

Do not ask open-ended questions. The user always retains "Other" via the question tool's built-in escape hatch.

## Step 3 — Per-Issue Remediation Selection

For every selected work item, in remediation order, ask one closed question. This is the central loop the user expects: every code change is preceded by an explicit choice.

Order remediation by:

1. Severity (`error` > `warning` > `info`).
2. User impact (accessibility and interaction blockers before visual cleanup).
3. Validation state (validated runs before unvalidated).
4. Files with the highest concentration of findings.
5. Source order by file path and line number.

For each work item:

1. Compose the question text:

   ```text
   How do you want to fix [<rule_id>] <file_path>:<line_number> — <summary>?
   ```

2. Compose option list from the work item's `fix_options`:
   - The first option is the analyzer's `recommended: true` entry, labeled `<label> (Recommended)`.
   - Then the next 1-2 alternatives from `fix_options` in their original order.
   - Always include a final `Skip / defer / reject` option that triggers a follow-up question (skip, defer, reject — with reason).

   Caps:
   - `AskUserQuestion` allows 2-4 options. With one always-present `Skip / defer / reject`, present at most 3 `fix_options` entries. If `fix_options` has 4 entries, drop the option whose `kind` ranks lowest (`accessibility-only` > `minimal` > `structural` > `alternative-component` > `defer-to-user`) or split into two consecutive questions.
   - If `fix_options` is empty (legacy report), present `Apply analyzer recommendation`, `Skip`, `Defer`, `Reject` and rely on `ai_fix_prompt` for the recommended path.

3. Use the option's `description` as the AskUserQuestion option `description`. When the host supports preview content, pass each option's `code` (full mode) as `preview` so the user can compare snippets side-by-side.

4. Record the user's choice on the work item:
   - `selected_option_id`
   - `selected_option_kind`
   - `apply_decision` ∈ `apply | skip | defer | reject`
   - For `defer` / `reject`, prompt for a one-line reason.

The user always sees the same options that appear in the EvenBetter HTML report's per-issue remediation menu, so they can review the report first and then drive the fix loop with consistent labels.

## Step 4 — Plan And Group

After all per-issue choices are collected:

- Drop work items where `apply_decision` is `skip`, `defer`, or `reject`. Persist `defer` and `reject` decisions immediately in the originating analyzer report (see Step 6).
- Group remaining `apply` work items by `file_path`. Same file is always one group.
- Keep groups that touch shared symbols, navigation roots, theme tokens, build settings, package files, schemas, generated files, or public APIs sequential; disjoint leaf files may run in parallel.
- When unsure if two groups conflict, make them sequential.

Present a brief execution plan to the user when the run includes more than one group or any parallelism. The plan lists per group: file, work item IDs, chosen option labels.

## Step 5 — Execute With Sub-Agents

Always spawn sub-agents to apply source edits. The fixer never edits Swift files directly.

- **Claude Code:** dispatch `Agent` calls (subagent_type `general-purpose`) — one per independent group, multiple in a single message for parallel groups.
- **Codex:** dispatch sub-agents with the equivalent isolation.
- If the environment cannot spawn sub-agents, stop before editing and report that this fixer requires sub-agent execution.

Each worker receives only:

- file ownership (a single `file_path`)
- the selected work items for that file with the user's selected option ID and label
- the analyzer's `ai_fix_prompt` for the recommended option, or the option-specific `ai_fix_prompt` from `fix_options[]` when present
- the analyzer's `fix_description` and `fix_code` when in full mode
- acceptance criteria taken verbatim from the analyzer's prompt
- a reminder that they are not alone in the codebase, must not revert other workers' edits, and must adapt to existing changes

Workers must list changed files and addressed work item IDs in their reply. They must not generate new fix prompts; if the option is unclear, they return the work item with a "needs-user-clarification" status and the orchestrator pauses to ask.

## Step 6 — Persist State

After each work item resolution:

- `apply` succeeded: set `state.status = "fixed"`, `state.decidedIn = currentRun`, `state.decidedBy = "fix-skill"`, `state.reason = null` unless a concise note is useful, `state.duplicateOf = null`. Optionally record `state.applied_option_id` to remember which option was applied (extension field, ignored by older readers).
- `skip`: leave `state.status = "open"` unchanged.
- `defer`: `state.status = "deferred"`, `state.decidedIn = currentRun`, `state.decidedBy = "user"`, `state.reason`.
- `reject`: `state.status = "rejected"`, `state.decidedIn = currentRun`, `state.decidedBy = "user"`, `state.reason`.

After every state mutation:

1. Reread `manifest.json`.
2. Recompute the affected run's `summary` from its analyzer report.
3. Update the run's `status` to `fixed` (no remaining `open` or `deferred` for that run), `partially_fixed` (some remain), or preserve `validated`/`pending_validation` when no fix decision was made.
4. Update `analyze-{N}.json` `run.status` to match where applicable.
5. Preserve `latest.analyze`, `latest.validate`, `latest.html_report`, `currentRun`, and unrelated runs.

Only mutate violation `state` blocks in analyzer reports. Do not change rule metadata, source excerpts, scoring summaries, `ai_fix_prompt`, `fix_options`, or validator results.

## Step 7 — Verify

After each group, inspect the diff for scope creep and run the most relevant available verification. For SwiftUI/iOS fixes:

- Prefer the project's normal build or test command when discoverable.
- Otherwise, perform static checks (does the file still parse? do the cited symbols still exist?) and explain the verification gap.
- When the change touched accessibility, suggest re-running `XCUIApplication.performAccessibilityAudit()` as a follow-up; do not run it on the user's behalf without permission.

Never claim a finding is fixed unless the source change is complete and verification was attempted or the gap is explicitly stated.

## Step 8 — Final Summary

At the end, summarize:

- Report source used and scope selected.
- Work items fixed, with the option label chosen for each.
- Work items skipped / deferred / rejected with reasons.
- Files changed.
- Analyzer report state files and manifest entries updated.
- Verification commands run and results.
- Remaining findings or recommended next batch.

## Edge Cases

- **`fix_options` missing or empty.** Legacy analyzer output. Present `Apply analyzer recommendation` (using `ai_fix_prompt`), `Skip`, `Defer`, `Reject`.
- **`ai_fix_prompt` missing or generic.** Do not synthesize one. Ask the user whether to skip, reject, defer, or rerun analysis/validation so the analyzer can provide a corrected prompt.
- **Source no longer matches the cited snippet.** Mark the work item as needing re-analysis and ask the user before editing.
- **Sub-agent reports needs-user-clarification.** Pause, ask one closed question, then resume.
- **No question tool available.** Use plain-text closed questions; do not silently fall back to "apply recommended" without asking.

## Compaction-Safe Invariants

- `projectPath` defaults to the invocation working directory.
- `manifest.json` is the source of truth for runs.
- Default working set is `state.status = "open"` from the newest validated analyzer run.
- Per-issue Q&A is mandatory — never apply a fix without a recorded user decision.
- Options come from analyzer `fix_options`; the fixer does not invent them.
- Source edits go through sub-agents; if sub-agents are unavailable, stop and report.
- Only mutate violation `state` in analyzer reports; never change rule metadata or analyzer prompts.
- Re-read manifest before every write.
