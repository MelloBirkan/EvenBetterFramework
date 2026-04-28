---
name: evenbetter-fix
description: Workflow skill that scopes and orchestrates agent-driven remediation from EvenBetter findings. Use when asked to fix issues from analyze.json, orchestrate fixes from validate.json or evenbetter-validate.json, resolve findings with agents, fix only severe issues first, generate fallback fix prompts, or coordinate remediation batches for an analyzed project.
---

# evenbetter-fix

## Overview

Coordinate the fix step of the EvenBetter loop after analysis and validation. Read findings from the target project's `.evenbetter` reports, ask a short scoping round before editing, plan deterministic remediation groups, and then execute fixes locally, with sub-agents, or as static prompts depending on user choice and environment support.

## Inputs

- `projectPath` (required): Absolute filesystem path to the analyzed project.
- Optional user intent from the prompt: severity scope, domain or file filters, execution mode, batch size, or request to use raw analyzer findings.

If `projectPath` is missing or not absolute, ask for the absolute path and stop until it is provided.

## Report Source Precedence

Load reports from `projectPath/.evenbetter/` in this order:

1. `validate.json` when present.
2. `evenbetter-validate.json` when present. This is the current EvenBetter validator contract.
3. `analyze.json` when validation output is absent, malformed, unsuitable for the selected scope, or the user explicitly asks for raw findings.

Treat validation output as the preferred execution source. From validator reports, act by default only on `kept` and `downgraded` findings. Never act on `dropped` findings unless the user explicitly requests raw analyzer findings or dropped-item review.

Use raw `analyze.json` for warning and info scopes when validation output only covers high-severity findings.

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
- Execution mode:
  - Agent batches when current instructions allow sub-agents and the user has selected or authorized them.
  - Sequential local remediation.
  - Static prompts only for manual execution or debugging.

Each closed-ended question must offer 3 or 4 concrete options with one marked as recommended when there is a safe default. Avoid open-ended questions unless the required decision cannot be represented as structured choices.

## Normalize Findings

Convert each selected finding into a traceable work item before grouping:

- `source_report`: absolute path to the report used.
- `source_kind`: `validate`, `evenbetter-validate`, or `analyze`.
- `work_item_id`: stable short ID, preferably `<rule_id>:<file_path>:<line_number>`.
- `rule_id`, `severity`, `domain`, `dimension`, `file_path`, and `line_number`.
- `summary`, `why_fix`, `fix_description`, `fix_code`, `ai_fix_prompt`, and `auto_fixable` when available.
- `guideline_reference` and corpus clause/source details when available.
- Validator `decision`, `confidence`, `reasoning`, and `downgraded_severity` when available.

For validator reports, the original analyzer violation usually lives under `original_violation`; preserve the validator wrapper and the original violation so the final summary can trace both.

Reject path traversal. Resolve source files as `projectPath / file_path` and ensure the result stays inside `projectPath`.

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
- Keep behavior and suppress or document the finding.
- Skip this item for now.

Record the selected option in the final summary with the originating work item ID.

## Progress And Verification

Track group status deterministically. In Codex, use `update_plan` when available for multi-group runs. Keep status labels aligned to the actual workflow: pending, in progress, blocked for user decision, fixed, skipped, or failed verification.

After each group, inspect the diff for scope creep and run the most relevant available verification. For SwiftUI/iOS fixes, prefer the project's normal build or test command when discoverable; otherwise perform static checks and explain any verification gap.

At the end, summarize:

- Report source used and scope selected.
- Work item IDs fixed, skipped, or converted to prompts.
- Files changed.
- User decisions made for ambiguous remediation.
- Verification commands run and results.
- Remaining findings or recommended next batch.

Never claim a finding is fixed unless the source change is complete and verification was attempted or the verification gap is explicitly stated.
