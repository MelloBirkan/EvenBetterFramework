# 3 Update

Contents: Role, Process, Writing with the helper, Writing by hand, After writing, Recovery.

## Role

Write the decisions from stage `2-validate` back into `.evenbetter/[project]/evenbetter-analyze-report.html`, in place, and stamp the workflow block so evenbetter-repair is allowed to run. The stamp is written on every pass. The findings are rewritten only when something changed.

## Process

1. Count the decisions: `kept`, `adjusted` and `removed`. `kept + adjusted` is the number of surviving findings, and all three add up to the number of findings loaded.
2. Build the data object.
   - Clean pass (`adjusted` and `removed` are both 0): start from the loaded data, with the stage 1 backfills applied, and change nothing but the workflow stamp and any new `Runtime:` notes from stage 2, appended to `scan_context.notes`. `summary`, `scan_date` and the rest of `scan_context` stay as loaded.
   - Otherwise: drop the removed findings, and put each adjusted finding in its original position. Recompute `summary` from the surviving `issues`: `total` is their count and each severity count matches the array. Set `scan_date` to the current local time as `YYYY-MM-DD HH:MM:SS`. Append stage 2's notes to `scan_context.notes`, one sentence each, creating the array if it is missing and skipping a note that is already there.
   - Leave `project_name`, `framework`, `wcag_level` and the rest of `scan_context` as loaded. `project_path` changes only when stage 1 found that the repository moved.
   - Carry every surviving finding's `repair` block through unchanged, apart from the `applied` to `failed` changes stage 2 made.
   - Carry every surviving finding's `runtime` block through unchanged, right after `repair`. Validation reads it and never writes it; only the stage 1 backfill adds an `untested` block where one was missing.
3. Stamp the workflow block:

   ```json
   "workflow": {
     "state": "validated",
     "validated_at": "YYYY-MM-DD HH:MM:SS",
     "validation": { "kept": 0, "adjusted": 0, "removed": 0 },
     "repaired_at": "(unchanged)",
     "repair": "(unchanged)"
   }
   ```

   - `state` becomes `validated` whatever it was. A `repaired` report goes back to `validated`: its repairs stay recorded in the per-finding ledger, and the report has just been reviewed again.
   - `validated_at` is the current local time, and never earlier than `scan_date`, because evenbetter-repair refuses a stamp older than the scan. When step 2 set `scan_date`, use that same timestamp for both.
   - `validation` holds the counts from step 1.
   - `repaired_at` and `repair` keep their loaded values exactly. Validation never writes them.
4. Write the report with the helper, or by hand when `python3` is not available.
5. Finish with After writing.

## Writing with the helper

1. Write the data object as JSON to a temporary file outside the project, for example one made with `mktemp`.
2. Run `python3 [script] update [data file] [report] --state validated`, with `[script]` resolved as in stage 1. It checks the data against the full contract and the validated workflow rules, replaces only the embedded data, reads the result back to confirm it, and writes the file in one step.
3. If it prints problems, it wrote nothing. Each line names a finding and a field that stage 2 left unresolved: go back, fix the data, and run it again. Do not edit the HTML by hand to get past the check.
4. Delete the temporary file.

## Writing by hand

Only when `python3` is not available:

1. Run the Pre-write checks in `../evenbetter-analyze/references/3-report.md` on the data, with the validated rules in place of the analyzed workflow and runtime ones: `state` is `validated`, `validated_at` is set and not earlier than `scan_date`, `kept + adjusted` equals the number of findings, no finding has `repair.status` set to `applied`, `repaired_at` and `repair` match the loaded values, and every finding's `runtime` block matches the loaded one (or is the `untested` backfill). If any check fails, go back to stage 2 and do not write.
2. Serialize the data as JSON with 2-space indentation, keeping the key order of the schema in `3-report.md`. Then replace every `</` with `<\/`, every `<!--` with `\u003c!--`, and the characters U+2028 and U+2029 with `\u2028` and `\u2029`. The result is still valid JSON, and it cannot end the `<script>` element early.
3. In the HTML text from stage 1, replace the data range (from its opening `{` through its matching `}`) with the new JSON. The `;` after it stays. No other byte of the file changes: markup, styles, Alpine bindings and CDN references stay as they were.
4. Write the text back to the same path. Do not create a backup or a sibling file.
5. Read the file again: `const reportData = ` appears once, the data after it parses as JSON, and a `;` follows it.

## After writing

Give the user a short status and stop. Clean pass:

```
OK: [kept] findings validated, no changes needed
file://[absolute path of the report]
```

Report with changes:

```
Validated [findings loaded]: [kept] kept, [adjusted] adjusted, [removed] removed
file://[absolute path of the report]
```

If no Apple page could be fetched, add one line: "Apple sources were not re-fetched; the corpus was used as checked on its retrieved dates."

Do not list the adjusted or removed findings; the user opens the report to read them. If the user asked for the changes, add one line per finding in the form `- EB-004: merged EB-005 into it`.

When findings survive, end with: "Next, run the evenbetter-repair skill." The report is stamped, so repair will accept it. When any surviving finding's `runtime.status` is still `untested`, add: "To confirm findings in the running app first, run the evenbetter-accessibility-tests skill." When every finding was removed, say instead that the report is clean and there is nothing to repair. If you noticed a problem that no finding covers, say in one sentence that a fresh evenbetter-analyze run would pick it up.

## Recovery

- The helper refused the data: nothing was written. Fix the fields it named and run it again.
- The helper could not find or read back the embedded data (exit status 2): the report on disk is unchanged. Tell the user which step failed and what the message said.
- A by-hand write failed its read-back in step 5: write the original HTML text from stage 1 back to the path, so the report is exactly as it was, and tell the user which step failed and which finding was involved.
- Never leave a partly written report on disk.
