# 1 Load

## Role

Locate the EvenBetter audit report, prove it has been validated, and build the severity-ordered queue that stage `2-triage` works from. This stage is the gate: no source file is opened for writing until it passes.

## Process

1. Resolve the project root. Default to the current working directory.
2. Find the report. Look in this order and stop at the first hit:
   - A path the user supplied explicitly.
   - `.evenbetter/<project-name>/evenbetter-analyze-report.html` derived from the project folder in kebab-case.
   - The single `evenbetter-analyze-report.html` under `.evenbetter/*/` if exactly one exists.
3. If multiple `.evenbetter/*/evenbetter-analyze-report.html` files exist and the user did not specify one, ask a closed question listing the candidates with their last-modified times and their `workflow.state`. Do not guess.
4. If no report exists, stop. Tell the user to run `evenbetter-analyze` first.
5. Read the HTML file as text and extract the `reportData` JS literal using the same anchors `evenbetter-validate` uses:
   - Anchor on the exact prefix `const reportData = ` (single space on each side of `=`).
   - Walk forward from the first `{` after the prefix with a brace counter that respects string literals (`"` and `'`) and escaped characters. Stop when the counter returns to `0`. The character immediately after must be `;`.
   - The substring from the opening `{` through the matching `}` is the payload, inclusive.
6. Parse the payload as JSON into `report`. Hold the original HTML text as `html`, and record `prefix_index` (offset of the opening `{`) and `suffix_index` (offset of the matching `}`, inclusive). Stage `4-status` mutates only that slice.
7. Run the repair gate below. Stop on the first failure.
8. Build the queue.

## Repair gate

Check in this order and stop at the first failure. Each failure is a single line naming the cause and the fix, followed by the report path. Never continue into stage `2-triage` after a failure, and never offer to bypass the gate.

| # | Condition | Response |
| --- | --- | --- |
| 1 | `report.workflow` is absent | `Refused — this report predates the workflow contract. Run evenbetter-validate to stamp it, then repair.` |
| 2 | `report.workflow.state` is `analyzed` | `Refused — this report has not been validated. Run evenbetter-validate first.` |
| 3 | `report.workflow.validated_at` is empty or missing | `Refused — no validation stamp on this report. Run evenbetter-validate first.` |
| 4 | `report.workflow.validated_at` parses earlier than `report.scan_date` | `Refused — evenbetter-analyze re-ran after the last validation. Re-run evenbetter-validate first.` |
| 5 | `report.issues` is empty | `Nothing to repair — the report has zero findings.` Not an error; exit cleanly. |

Timestamps are `YYYY-MM-DD HH:MM:SS` local time, so a lexicographic string comparison is a correct chronological comparison. If either timestamp does not match that shape, treat it as a failure of check 4 rather than attempting a lenient parse.

`report.workflow.state` of `repaired` passes the gate. A previous repair run does not block a new one — findings left `deferred`, `failed`, or `pending` are exactly what a second run is for.

## Structural checks

After the gate passes, sanity-check `report` so the later stages operate on well-formed input:

- `report.issues` is an array and every issue has `id`, `clause_id`, `title`, `description`, `severity`, `hig_reference_url`, `file_path`, `line_number`, `code_snippet`, `minimal_fix`, `recommended_fix`, `ai_fix_prompt`, and `language`.
- Every `severity` is one of `critical`, `high`, `medium`, `low`.
- `report.project_path` resolves to a directory on disk. If it does not, fall back to the current working directory and record that the report was generated against a different root — `file_path` values resolve against `report.project_path` first, then against the current root.
- Backfill a missing per-issue `repair` object in memory with the `pending` shape (`status: "pending"`, empty `path`, `owner`, `applied_at`, `note`, empty `changed_files`). A report validated before the ledger existed is repairable; it just starts with every finding pending.

If a structural check fails, stop and name the failing issue `id` and field. Do not repair a malformed report — the repair belongs in `evenbetter-analyze`.

## Building the queue

1. Filter to the findings this run should consider:
   - Default: every finding whose `repair.status` is `pending` or `failed`.
   - A finding already `applied` is not re-applied. Report it in the tally as already done.
   - A finding already `deferred` is re-offered only when the user asked for it, or when they are answering its question in this turn. Otherwise leave it deferred and do not re-ask — repeating the same question every run is how a guided handoff becomes noise.
   - Honour any scope the user gave: severities (`fix the criticals`), file globs, clause IDs, or issue IDs. Findings outside the scope end the run as `skipped` with `note` recording the scope, not as `pending`.
2. Order by severity: `critical`, then `high`, then `medium`, then `low`. The most harmful violations get repaired first, so a run that is interrupted has still done the most valuable work.
3. Within a severity, group by `file_path`. Editing one file's findings together keeps the diff coherent and lets stage `3-apply` re-read the file once.
4. Within a file, order by descending `line_number`. Applying edits from the bottom of the file upward means an earlier edit never shifts the line numbers of the findings still queued behind it.
5. Load the corpus once: read `../../corpus/index.json` and build a map keyed by `clause_id`. Lazy-load `../../corpus/ios/<domain>.md` per domain in the queue and cache each parsed clause — its **Check**, **Why**, and **Correct code** blocks are used by every later stage.

## Output of this stage

Stage `1-load` produces four artifacts in memory:

- `report` — the parsed report object.
- `html` and `(prefix_index, suffix_index)` — the original text and the only slice stage `4-status` may mutate.
- `queue` — the ordered findings this run will act on, each carrying its cached corpus clause.
- `out_of_scope` — findings excluded by user scope, to be recorded as `skipped` by stage `4-status`.
