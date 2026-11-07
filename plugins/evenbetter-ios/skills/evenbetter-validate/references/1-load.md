# 1 Load

Contents: Role, Process, Reading the data by hand, Required fields, Backfilling older reports, Output of this stage.

## Role

Find the existing EvenBetter report, extract its embedded data, and list the contract problems it already has, so stage `2-validate` has a findings list and a to-do list to work through.

## Process

1. Resolve the project root. Default to the current working directory.
2. Find the report. Look in this order and stop at the first hit:
   - A path the user gave.
   - `.evenbetter/[project]/evenbetter-analyze-report.html`, where `[project]` is the kebab-case name of the project folder.
   - The only `evenbetter-analyze-report.html` directly under `.evenbetter/*/`, if there is exactly one.

   Files under `.evenbetter/[project]/history/` are archived reports that evenbetter-analyze moved aside. Never load or edit them.
3. If several reports match and the user did not name one, ask one closed question that lists each candidate with its folder and `scan_date`, the newest `scan_date` first as the recommended option. Do not guess.
4. If there is no report, stop and tell the user to run the evenbetter-analyze skill first.
5. Extract the data. With `python3`, run `python3 [script] extract [report]` and save its output to a temporary file outside the project, for example one made with `mktemp`. `[script]` is `../../scripts/evenbetter_report.py`, resolved against the SKILL.md folder. Exit status 2 means the file cannot be read as a report (no anchor, an unreplaced template placeholder, or data that is not valid JSON): stop and pass its message to the user. Without `python3`, follow Reading the data by hand below.
6. List the contract problems with `python3 [script] check [report]`. Without `--state`, it checks the report against its own `workflow.state`. Each output line names a finding `id` and a field, for example a missing `related_clause_ids`, a level AAA criterion in an AA report, a snippet with `// ...` in it, or two twin clauses split across findings. Keep these lines as the to-do list for stage 2. A `warning:` line about findings without a runtime block is not a to-do: the backfill below handles it. Without `python3`, run the Pre-write checks in `../evenbetter-analyze/references/3-report.md` by hand and note every failure the same way, except the last two, which hold only for a fresh scan. In their place, check the `workflow` block against the report's own `workflow.state`, as the helper does: for `analyzed`, empty stamps, every tally 0 and every `repair` pending and empty; for `validated`, `validated_at` set, `kept + adjusted` equal to the number of findings and no `applied` finding; for `repaired`, `repaired_at` set and not earlier than `validated_at`, each repair tally equal to its ledger count and at least one `applied` finding. Check each `runtime` block for its shape only. A recorded repair outcome or runtime verdict is not a to-do.
7. Check the project root. Each `file_path` is relative to `project_path`. If `project_path` is not a directory on this machine but the files resolve under the current root, the repository moved: use the current root, and tell stage 2 to set `project_path` to it and to rewrite the absolute paths in every `ai_fix_prompt`. If the files resolve under neither root, stop and ask the user to run validation from the project root.

## Reading the data by hand

Only when `python3` is not available:

1. Read the report as text. Do not parse the markup; the data sits in the `<script>` block near the end of the file.
2. Find the line that contains `const reportData = `. It appears exactly once. The data starts at the `{` right after it.
3. Walk forward from that `{`, counting `{` and `}` that sit outside strings. JSON strings are always in double quotes, so a `'` never starts a string, and inside a string a backslash skips the character after it. Stop when the count returns to 0. The next character must be `;`.
4. Parse the text from the opening `{` through the matching `}` as JSON. The sequences `<\/`, `\u003c!--`, `\u2028` and `\u2029` are ordinary JSON escapes for `</`, `<!--` and the two line-separator characters, so a JSON parser reads them with no special handling. If parsing fails, the file was edited by hand: stop and name the file and the position where parsing failed.
5. Keep the whole HTML text and the start and end positions of the data. Stage 3 replaces exactly that range when it writes by hand.

## Required fields

Stop and ask the user to run evenbetter-analyze again when the data is not an object, `issues` is not an array, or any finding lacks `id`, `clause_id`, `file_path`, `line_number` or `code_snippet`. Without those fields a finding cannot be found in the code or tied to a clause, and validation never invents a clause for a finding.

Everything else that is missing or wrong is a to-do for stage 2, not a reason to stop. An empty `issues` array is valid; the pass still runs and stamps the report.

## Backfilling older reports

Reports written before the current contract can lack some blocks. Fill them in memory, then carry on:

- A missing `workflow` becomes `{"state": "analyzed", "validated_at": "", "validation": {"kept": 0, "adjusted": 0, "removed": 0}, "repaired_at": "", "repair": {"applied": 0, "deferred": 0, "skipped": 0, "failed": 0}}`.
- A missing finding `repair` becomes `{"status": "pending", "path": "", "owner": "", "applied_at": "", "changed_files": [], "note": ""}`.
- A missing `related_clause_ids` becomes `[]`.
- A missing finding `runtime` becomes `{"status": "untested", "checked_at": "", "configs": [], "tests": [], "evidence": "", "result_bundle": ""}`, placed right after `repair`. The helper's `update` adds the same block on its own when it is missing.

A backfill alone does not count as an adjustment. Stage 3 writes the backfilled blocks out, which is what lets evenbetter-repair accept an older report. Never backfill a `validated` state; the backfilled state is always `analyzed`, and this pass is what promotes it.

## Output of this stage

Held in memory for the next stages:

- The report data, with any backfills applied.
- The to-do list from the check.
- The absolute path of the report, and the project root the file paths resolve against.
- When working by hand, the original HTML text and the start and end positions of the data.
