# 1 Load

## Role

Locate the existing EvenBetter audit report and extract the `reportData` object so stage `2-validate` has a structured findings list to re-check.

## Process

1. Resolve the project root. Default to the current working directory.
2. Find the report. Look in this order and stop at the first hit:
   - A path the user supplied explicitly.
   - `.evenbetter/<project-name>/evenbetter-analyze-report.html` derived from the project folder in kebab-case.
   - The single `evenbetter-analyze-report.html` under `.evenbetter/*/` if exactly one exists.
3. If multiple `.evenbetter/*/evenbetter-analyze-report.html` files exist and the user did not specify one, ask a closed question listing the candidates and their last-modified times. Do not guess.
4. If no report exists, stop and tell the user to run `evenbetter-analyze` first. Validation has nothing to validate.
5. Read the HTML file as text. Do not parse the markup — the only payload that matters lives inside the `<script>` block at the bottom of the document.
6. Extract the `reportData` JS literal:
   - Anchor on the exact prefix `const reportData = ` (note the single space on each side of `=`).
   - Walk forward from the first `{` after the prefix using a brace counter that respects string literals (`"` and `'`) and escaped characters. Stop when the counter returns to `0`. The character immediately after must be `;`.
   - The substring from the opening `{` through the matching `}` is the report payload, inclusive.
7. Parse the payload as JSON. The template guarantees the literal is JSON-compatible; if parsing fails, the report has been hand-edited and validation must stop with a clear error message that names the file and the failing offset.
8. Hold the parsed object in memory under the variable name `report`. Hold the original HTML text under `html`. Both are needed by stage `3-update`.
9. Capture two anchors for the rewrite:
   - `prefix_index` — the byte offset where the literal `{` begins (immediately after `const reportData = `).
   - `suffix_index` — the byte offset of the matching `}`, exclusive. The character at `suffix_index` must be `;`.

## Validation before continuing

After loading, sanity-check the `report` object so stage `2-validate` operates on a well-formed input:

- `report.issues` is an array. Empty is allowed; the report may legitimately have zero findings.
- Each issue has `id`, `clause_id`, `title`, `description`, `severity`, `hig_reference_url`, `file_path`, `line_number`, `code_snippet`, `minimal_fix`, `recommended_fix`, `ai_fix_prompt`, `language`.
- `report.summary` exists and contains `total`, `critical`, `high`, `medium`, `low`.
- `report.workflow` exists and contains `state`, `validated_at`, `validation`, `repaired_at`, and `repair`.
- `report.project_path` resolves to a directory on disk. If it does not, fall back to the current working directory and record that the report was generated against a different root — relative `file_path` values still resolve against `report.project_path` first, then against the current root.

If a check fails, do not silently repair the report. Stop and report the missing fields to the user. The fix belongs in `evenbetter-analyze`, not here.

The `workflow` and per-issue `repair` blocks are the one exception: they postdate the original report schema, so a report generated before the four-state contract legitimately lacks them. Backfill them in memory rather than failing:

- Missing `report.workflow` becomes `{"state": "analyzed", "validated_at": "", "validation": {"kept": 0, "adjusted": 0, "removed": 0}, "repaired_at": "", "repair": {"applied": 0, "deferred": 0, "skipped": 0, "failed": 0}}`.
- A missing per-issue `repair` becomes `{"status": "pending", "path": "", "owner": "", "applied_at": "", "changed_files": [], "note": ""}`.

Backfilling is what makes an older report repairable: stage `3-update` writes the block out, and `evenbetter-repair`'s gate then passes. Do not backfill a `validated` state — the backfilled state is always `analyzed`, and this run is what earns the promotion.

## Output of this stage

Stage `1-load` produces three artifacts in memory:

- `report` — parsed JS object literal containing `project_name`, `project_path`, `framework`, `wcag_level`, `scan_date`, `workflow`, `summary`, `issues`, and `scan_context`, with `workflow` and every issue's `repair` block backfilled if the report predates them.
- `html` — full original HTML text, byte-for-byte.
- `(prefix_index, suffix_index)` — the slice that bounds the JS literal inside `html`. These are the only positions stage `3-update` is allowed to mutate.
