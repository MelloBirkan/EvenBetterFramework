# 1 Load

Contents: Role, Process, Repair gate, Structural checks, Reports without clause IDs, Building the queue, Output of this stage.

## Role

Locate the EvenBetter audit report, prove it has been validated, check its structure, and build the queue of edit sites that stage `2-triage` works from. No source file is opened for writing until this stage passes.

Skill paths here (`../../corpus/`, `../../scripts/`) resolve against the SKILL.md folder, not this `references/` folder. Project paths resolve against the project root. `[script]` is the absolute path of `../../scripts/evenbetter_report.py`.

## Process

1. Resolve the project root: the current working directory, unless the user names another.
2. Find the report, stopping at the first hit:
   - A path the user gave.
   - `.evenbetter/[project]/evenbetter-analyze-report.html`, where `[project]` is the project folder name in kebab-case.
   - The only `evenbetter-analyze-report.html` directly under `.evenbetter/*/`.

   Files under `.evenbetter/*/history/` are snapshots that evenbetter-analyze archived before a re-scan. Never load them as the report.
3. If several candidate reports exist and the user named none, ask one closed question listing each with its last-modified time and `workflow.state`. Recommend the most recently modified report that passes the repair gate below.
4. If none exists, stop with: `Run evenbetter-analyze first. There is nothing to repair.`
5. Load the report data:
   - With `python3`: run `python3 [script] extract [absolute report path]` and parse its stdout as JSON into `report`.
   - By hand: read the HTML as text into `html`. Find the exact prefix `const reportData = ` (one space on each side of `=`), then walk forward from the first `{` after it with a brace counter that skips JSON string literals (only `"` opens and closes one; an apostrophe is ordinary text) and the character after each backslash, until the counter returns to 0. The next character must be `;`. Parse the substring from that `{` through its matching `}` as JSON into `report`, and record `prefix_index` (the `{`) and `suffix_index` (the matching `}`, inclusive). That slice is the only part of `html` stage `4-status` replaces.
6. Run the repair gate. Stop at the first failure.
7. Run the structural checks.
8. Build the queue.

## Repair gate

Check in this order and stop at the first failure. Each response is one line naming the cause and the fix, followed by the report path. A refused run never continues into stage `2-triage`.

| # | Condition | Response |
| --- | --- | --- |
| 1 | `report.workflow` is absent | `Refused: this report predates the workflow contract. Run evenbetter-validate to stamp it, then repair.` |
| 2 | `report.workflow.state` is `analyzed` | `Refused: this report has not been validated. Run evenbetter-validate first.` |
| 3 | `report.workflow.validated_at` is empty or missing | `Refused: there is no validation stamp on this report. Run evenbetter-validate first.` The stamp is the proof, not the state string. |
| 4 | `report.workflow.validated_at` is earlier than `report.scan_date` | `Refused: evenbetter-analyze re-ran after the last validation. Run evenbetter-validate again first.` |
| 5 | `report.issues` is empty | `Nothing to repair: the report has zero findings.` This is a clean exit, not an error. |

Timestamps are `YYYY-MM-DD HH:MM:SS` local time, so comparing the strings compares the times. If either timestamp has another shape, treat it as a failure of check 4 rather than parsing it loosely.

A `workflow.state` of `repaired` passes the gate. Findings left `deferred`, `failed` or `pending` by an earlier run are what a second run is for.

If the user wants to repair a report that fails the gate, offer to run evenbetter-validate for them first. That is one extra pass, and the gate then passes. Repairing past the gate would push unchecked findings into the code.

## Structural checks

With `python3`, run `python3 [script] check [absolute report path]`, which checks the contract against the report's own `workflow.state`. Exit 0 means the report is well formed. Otherwise read the messages:

- Messages only about a missing `clause_id`, `related_clause_ids` or `repair` come from a report written before those fields existed. Fill them as described below and continue. A `warning:` line about findings without a runtime block is not a failure either; the backfill below adds the block.
- Any other message stops the run before any source edit. Name the finding `id` and field from each message, and tell the user to re-run evenbetter-validate, which owns those fields. Stage `4-status` writes through the same check, so a report that fails it now could not record the repairs later, and the code would end up ahead of the ledger.

Without `python3`, check the same contract by hand and treat failures the same way:

- `report.issues` is an array, every `id` is unique, and every issue has `id`, `clause_id`, `related_clause_ids`, `title`, `description`, `severity`, `wcag_criteria`, `wcag_level`, `hig_reference_url`, `file_path`, `line_number`, `code_snippet`, `minimal_fix`, `recommended_fix`, `ai_fix_prompt` and `language`.
- Every `severity` is `critical`, `high`, `medium` or `low`, and `summary` matches the `issues` array.
- `clause_id` and every ID in `related_clause_ids` exist in `../../corpus/index.json`, and `hig_reference_url` equals the index `source_url` of `clause_id`. A clause that left the corpus after validation also lands here: re-running evenbetter-validate drops its finding.
- `code_snippet`, `minimal_fix` and `recommended_fix` hold complete code, with no `// ...` elisions, and a fix that touches several files starts each part with a `// File: [path]` line.

Then, on either path:

- If `report.project_path` is not a directory on disk, use the current project root and note in the handoff that the report was generated against another root. `file_path` values resolve against `report.project_path` first, then against the current root.
- Backfill a missing `repair` object with the pending shape: `status: "pending"`, empty `path`, `owner`, `applied_at` and `note`, and an empty `changed_files` array.
- Backfill a missing `runtime` object, right after `repair`, with the untested shape: `{"status": "untested", "checked_at": "", "configs": [], "tests": [], "evidence": "", "result_bundle": ""}`. The helper's `update` adds it too, but the by-hand splice in stage `4-status` needs it in `report`.

## Reports without clause IDs

Older reports may lack `clause_id` or `related_clause_ids`.

- A missing `related_clause_ids` becomes `[]`.
- For a missing `clause_id`, use a clause ID quoted in the finding's `title` or `description` when it exists in `../../corpus/index.json` and its index `source_url` equals `hig_reference_url`. Otherwise match `hig_reference_url` against the index `source_url` values. When several clauses share that URL, pick the one whose Check matches the code at `file_path`. Repair never edits `hig_reference_url`, so a clause whose URL differs from it would fail the final write.
- Write the derived values into the finding, so the report passes `check` again. Apart from `repair` and the `line_number` moves that stage `4-status` allows, filling these two fields is the only change repair makes to a finding. List each derived ID and its source in the handoff, for example `EB-007: clause_id COMP-UI-001 derived from hig_reference_url`.
- If no single clause fits, stop before any source edit: `Refused: EB-007 has no clause_id and none can be derived. Run evenbetter-validate first.`
- With `python3`, check the filled data once more before stage `3-apply` makes its first edit: write it to a temporary file outside the project and the plugin folder, run `python3 [script] check [temp file]`, and delete the file. A derived clause can still fail the severity check, for example. Any problem left stops the run before any source edit: name the finding and field, and tell the user to run evenbetter-validate.

## Building the queue

1. Filter the findings this run acts on:
   - By default, every finding whose `repair.status` is `pending` or `failed`.
   - A finding already `applied` is not re-applied. Count it in the tally as done, and keep its edit intact when a later edit touches the same code.
   - A finding already `deferred` is re-offered only when the user asks for it or is answering its question in this turn. Asking the same question every run turns a handoff into noise.
   - Honour any scope the user gave: severities ("fix the criticals"), file globs, clause IDs or finding IDs. Findings outside the scope end the run as `skipped` with the scope in `note`.
2. Load the corpus. Read `../../corpus/index.json` once and map it by `clause_id`. For every clause the queue cites, primary or related, load `../../` plus its index `file_path` the first time it is needed, and cache the clause's Check, Why and Correct code blocks.
3. Group the queue into edit sites. Findings belong to one site when they share a `file_path` and their `code_snippet` lines overlap or sit in the same view's modifier chain, so that one edit to that construct would serve them all. A finding on its own construct is a site of one. Include in each site the IDs of any already `applied` findings on the same lines, so later edits keep their changes.
4. Order the sites by the highest severity among their findings (`critical`, `high`, `medium`, `low`), then by `file_path`, then by descending `line_number`. The most harmful violations are repaired first, so an interrupted run has still done the most valuable work. Going bottom-up within a file keeps most queued line numbers stable, and stage `3-apply` locates each site by its snippet in any case. Inside a site, order findings by severity, then `id`.

## Output of this stage

- `report`, the parsed report object, with any derived clause IDs and backfilled `repair` and `runtime` objects.
- `html`, `prefix_index` and `suffix_index`, on the by-hand path only.
- `queue`, the ordered edit sites, each finding carrying its cached corpus clauses.
- `out_of_scope`, the findings excluded by the user's scope, which stage `4-status` records as `skipped`.
- `derived`, the list of derived clause IDs for the handoff.
