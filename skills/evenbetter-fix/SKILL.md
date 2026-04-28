---
name: evenbetter-fix
description: Workflow skill that scopes and orchestrates agent-driven remediation from numbered EvenBetter findings. Use when asked to fix issues from analyze-{N}.json, orchestrate fixes from evenbetter-validate-{N}.json, resolve findings with agents, fix only severe issues first, generate fallback fix prompts, or coordinate remediation batches for an analyzed project with .evenbetter/manifest.json history.
---

# evenbetter-fix

## Overview

Coordinate the fix step of the EvenBetter loop after analysis and validation. Read numbered findings from the target project's `.evenbetter` reports, merge unresolved work across analyzer runs, ask a short scoping round before editing, plan deterministic remediation groups, and then execute fixes locally, with sub-agents, or as static prompts depending on user choice and environment support.

## Inputs

- `projectPath` (required): Absolute filesystem path to the analyzed project.
- Optional user intent from the prompt: severity scope, domain or file filters, execution mode, batch size, or request to use raw analyzer findings.

If `projectPath` is missing or not absolute, ask for the absolute path and stop until it is provided.

## Report Source Precedence

Load reports from `projectPath/.evenbetter/` in this order:

1. `manifest.json` as the source of truth for numbered report history.
2. The newest paired validation report, `evenbetter-validate-{N}.json`, for the latest validated actionable run.
3. The newest analyzer report, `analyze-{N}.json`, for raw latest findings and warning/info scopes.
4. Older analyzer runs listed in the manifest for unresolved items that remain open or deferred.
5. Legacy `evenbetter-validate.json`, `validate.json`, or `analyze.json` only when no manifest exists; if legacy `analyze.json` exists, perform the documented auto-migration to `analyze-1.json` and initialize `manifest.json` before continuing.

Treat validation output as the preferred evidence source for high-severity findings. From validator reports, act by default only on `kept` and `downgraded` findings. Never act on `dropped` findings unless the user explicitly requests raw analyzer findings or dropped-item review.

Use raw `analyze-{N}.json` for warning and info scopes when validation output only covers high-severity findings.

Before writing any state update, reread `manifest.json` from disk. EvenBetter assumes serial execution: only one analyzer, validator, or fixer run writes `.evenbetter/` at a time.

## Build The Merged Working Set

Build work items by violation `id` across all manifest runs:

- For each violation ID, keep the latest occurrence as the display/source context.
- Preserve the originating analyzer run and report path where the selected violation state must be written.
- If the latest known `state.status` is `fixed`, `rejected`, or `duplicate_of`, skip it.
- If the latest known `state.status` is `deferred`, include it only when the user explicitly opts into deferred work.
- If the latest known `state.status` is `open`, include it.
- If a validation report exists for a run, attach validator `decision`, `confidence`, `reasoning`, and `downgraded_severity` to matching violation IDs from `kept` and `downgraded`.
- Do not act on validator `dropped` findings by default, even if the analyzer violation is still open.

When two reports disagree, newest analyzer state wins for state, and newest validation report wins for validator evidence. Per-run analyzer files remain the source of truth for the mutable `state` block.

## Scoping Before Fixes

Do not start remediation before a short closed-ended scoping step. If a question tool is available, use it. In Codex Plan mode, use `request_user_input`; otherwise ask concise plain-text questions and wait. Do not simulate an unavailable tool call.

Ask only what materially changes the run. Cover these decisions unless already clear from the user request:

- Severity scope:
  - Most serious only, usually `error` and validator `kept`.
  - Serious and medium, usually `error` plus `warning`.
  - Everything, including `info`.
  - Selected domain or file set.
- Prioritization:
  - Accessibility and user-impacting issues first.
  - Severity first.
  - Files with the highest concentration of findings first.
- Deferred findings:
  - Exclude deferred findings, which is the default.
  - Include deferred findings in this run.
  - Review deferred findings only, without editing.
- Execution mode:
  - Agent batches when current instructions allow sub-agents and the user has selected or authorized them.
  - Sequential local remediation.
  - Static prompts only for manual execution or debugging.

Each closed-ended question must offer 3 or 4 concrete options with one marked as recommended when there is a safe default. Avoid open-ended questions unless the required decision cannot be represented as structured choices.

## Normalize Findings

Convert each selected finding into a traceable work item before grouping:

- `source_report`: absolute path to the report used.
- `source_kind`: `manifest`, `evenbetter-validate`, `validate`, or `analyze`.
- `source_analyze_report`: absolute path to the originating `analyze-{N}.json`.
- `source_validate_report`: absolute path to the paired `evenbetter-validate-{N}.json` when available.
- `originating_run`: analyzer run number where the mutable state must be written.
- `work_item_id`: the stable violation `id`; use `<rule_id>:<file_path>:<line_number>` only for legacy reports without IDs.
- `state`: the current violation state object.
- `rule_id`, `severity`, `domain`, `dimension`, `file_path`, and `line_number`.
- `summary`, `why_fix`, `fix_description`, `fix_code`, `ai_fix_prompt`, and `auto_fixable` when available.
- `guideline_reference` and corpus clause/source details when available.
- Validator `decision`, `confidence`, `reasoning`, and `downgraded_severity` when available.

For validator reports, the original analyzer violation usually lives under `original_violation`; preserve the validator wrapper and the original violation so the final summary can trace both.

Reject path traversal. Resolve source files as `projectPath / file_path` and ensure the result stays inside `projectPath`. Resolve report paths as `projectPath/.evenbetter / filename` and ensure they stay inside `.evenbetter/`.

## Plan Remediation Order

Sort selected work items by:

1. Severity, with `error` before `warning` before `info`.
2. User impact, with accessibility and interaction blockers before visual cleanup.
3. Validator confidence, higher first when available.
4. Concentration of findings in the same file.
5. Source order by file path and line number.

Group work items for edit safety:

- Same `file_path` always belongs to one group.
- Findings that touch shared components, navigation roots, theme tokens, build settings, package files, schemas, generated files, or public APIs must be sequential unless independence is obvious.
- Disjoint leaf files with no shared symbols, imports, or generated outputs may run in parallel.
- If uncertain whether two groups conflict, make them sequential.

Present a brief execution plan before edits when the plan includes more than one group or any parallelism.

## Execute Fixes

Use the existing codebase patterns. Do not rewrite unrelated code, reformat entire files, or revert user changes. Keep each change tied to one or more work items.

When sub-agents are permitted and selected:

- Spawn one worker per independent group, not per finding.
- Give each worker exclusive file ownership for its group.
- Tell workers they are not alone in the codebase, must not revert edits by others, and must adjust to existing changes.
- Include only the relevant work items, source report path, file ownership, acceptance criteria, and verification expectations.
- Require workers to list changed files and work item IDs addressed.

When sub-agents are unavailable or not permitted, process the planned groups sequentially in priority order using the same group boundaries.

When static prompt mode is selected, generate one prompt per group or file. Each prompt must include the selected work items, source file paths, traceability IDs, and acceptance criteria. Do not edit source files in static prompt mode.

After each completed fix attempt, update the originating analyzer report's violation state:

- `state.status`: `fixed`
- `state.decidedIn`: current manifest `currentRun`
- `state.decidedBy`: `fix-skill`
- `state.reason`: null unless a concise fix note is useful
- `state.duplicateOf`: null

Then update the matching manifest run summary. Set report/run status to `fixed` when no `open` or `deferred` items remain for that run; otherwise set it to `partially_fixed`.

Never claim a work item is fixed before the source change is complete and verification was attempted or the verification gap is explicitly stated.

## Ambiguous Remediation

Proceed without interruption when the finding is clear, low risk, source context still matches, and the fix follows local code patterns.

Pause for a closed-ended resolution decision when any of these are true:

- `auto_fixable` is false or missing and the fix changes behavior.
- The cited snippet or line no longer matches source.
- Validator confidence is low or the finding was downgraded.
- Multiple plausible fixes affect product behavior, compatibility, accessibility semantics, navigation, data persistence, public APIs, or visual direction.
- The fix would suppress the finding instead of remediating it.

Use 3 or 4 concrete options and mark one recommended choice. Recommended defaults should favor standards-compliant, user-impacting fixes over suppression. Acceptable options include:

- Apply the strict standards-compliant fix (recommended).
- Apply a compatibility-oriented fix.
- Reject the finding as not applicable and record the reason.
- Defer this item and record the reason.

Persist the selected option immediately in the originating analyzer report when it is a decision rather than a source fix:

- Reject: `state.status = "rejected"`, `state.decidedIn = currentRun`, `state.decidedBy = "user"`, `state.reason = <user reason>`.
- Defer: `state.status = "deferred"`, `state.decidedIn = currentRun`, `state.decidedBy = "user"`, `state.reason = <user reason>`.

Record the selected option in the final summary with the originating work item ID.

## State Persistence

Only mutate violation `state` blocks in analyzer reports. Do not rewrite older analyzer report content except for the specific `state` object of the affected violation. Do not change rule metadata, source excerpts, scoring, summaries, or validator result arrays.

After every state mutation:

1. Reread `manifest.json`.
2. Recompute the affected run's `summary` counts from its analyzer report.
3. Update the affected run's `status` to `fixed`, `partially_fixed`, or preserve `validated`/`pending_validation` when no fix decision was made.
4. Update the analyzer report `run.status` to match the manifest run status when applicable.
5. Preserve `latest.analyze`, `latest.validate`, `currentRun`, and unrelated run entries.

Project memory may mirror these decisions for convenience, but the in-repo manifest and analyzer report state are the only authoritative records.

## Progress And Verification

Track group status deterministically. In Codex, use `update_plan` when available for multi-group runs. Keep status labels aligned to the actual workflow: pending, in progress, blocked for user decision, fixed, skipped, or failed verification.

After each group, inspect the diff for scope creep and run the most relevant available verification. For SwiftUI/iOS fixes, prefer the project's normal build or test command when discoverable; otherwise perform static checks and explain any verification gap.

At the end, summarize:

- Report source used and scope selected.
- Work item IDs fixed, skipped, or converted to prompts.
- Work item IDs rejected or deferred with reasons.
- Files changed.
- User decisions made for ambiguous remediation.
- Analyzer report state files and manifest entries updated.
- Verification commands run and results.
- Remaining findings or recommended next batch.

Never claim a finding is fixed unless the source change is complete and verification was attempted or the verification gap is explicitly stated.
