# 3 Update

## Role

Apply the decisions from stage `2-validate` back into `.evenbetter/<project-name>/evenbetter-analyze-report.html`, and stamp the workflow block so `evenbetter-repair` is allowed to run. The findings are rewritten only when something changed; the stamp is written on every pass.

## Process

1. Compute the validation tally:
   - `kept` — count of `keep` decisions.
   - `adjusted` — count of `adjust` decisions.
   - `removed` — count of `remove` decisions.
2. Stamp the workflow block. This happens on every pass, clean or not:

   ```json
   "workflow": {
     "state": "validated",
     "validated_at": "YYYY-MM-DD HH:MM:SS",
     "validation": { "kept": 0, "adjusted": 0, "removed": 0 },
     "repaired_at": "<unchanged>",
     "repair": "<unchanged>"
   }
   ```

   - `state` becomes `validated` regardless of its previous value. A report that was `repaired` returns to `validated`: the repairs are recorded in the per-finding ledger, and the report has just been re-reviewed.
   - `validated_at` is the current local time as `YYYY-MM-DD HH:MM:SS`. It must be at or after `report.scan_date`, because `evenbetter-repair` refuses a stamp older than the scan. If step 4 bumps `scan_date`, stamp `validated_at` with the same value or later, never earlier.
   - `validation` carries this pass's tally from step 1.
   - `repaired_at` and `repair` are carried through byte-for-byte. Validation never writes them.

3. If `adjusted == 0` and `removed == 0`, the pass is clean. Build a report object whose only change is the workflow stamp — every finding, the `summary`, `scan_date`, and `scan_context` stay exactly as loaded — then run steps 6-8 to serialize, splice, and write it. Emit one line and stop:

   ```
   OK — <kept> findings validated, no changes needed
   ```

   Use the absolute path of the report on its own line beneath the OK line so the user can still click through if they want to. The stamp is the reason a clean pass still writes: without it, a report with nothing wrong could never be repaired.

4. Otherwise, build the new `report` object from the surviving findings:
   - Drop every `remove` finding from `report.issues`.
   - Replace every `adjust` finding with its updated object, in the original list position.
   - Recompute `report.summary` from scratch:
     - `summary.total === report.issues.length`.
     - `summary.critical`, `summary.high`, `summary.medium`, `summary.low` are the counts of each severity in `report.issues`.
   - Update `report.scan_date` to the current local time formatted as `YYYY-MM-DD HH:MM:SS`.
   - Leave `report.project_name`, `report.project_path`, `report.framework`, `report.wcag_level`, and `report.scan_context` unchanged. Validation does not re-detect frameworks or recompute the original scan stats.
   - Carry every surviving finding's `repair` block through unchanged, other than the `applied` → `failed` flips stage `2-validate` decided.
5. Sanity-check the new object before serialization:
   - `summary.total === issues.length`.
   - Every `severity` is one of `critical`, `high`, `medium`, `low`.
   - Every `hig_reference_url` is a non-empty string starting with `https://developer.apple.com/`.
   - Every `id` is unique within `issues`.
   - Every `code_snippet`, `minimal_fix`, and `recommended_fix` is non-empty.
   - Every `ai_fix_prompt` is non-empty and under ~1,500 characters.
   - Every finding carries a `repair` block whose `status` is one of `pending`, `applied`, `deferred`, `skipped`, `failed`.
   - `workflow.state` is `validated`, `workflow.validated_at` is non-empty and not earlier than `report.scan_date`, and `workflow.repaired_at` and `workflow.repair` match the values loaded from disk.

   If any check fails, do not write. Surface the failing finding's `id` and field to the user and stop.
6. Serialize the object to a JSON literal. The template's loader expects valid JavaScript, and JSON is valid JavaScript here, so use a deterministic JSON serialization with a stable key order matching the schema. Do not pretty-print with line breaks unless the previous report was pretty-printed; mirror the original formatting style of the slice between `prefix_index` and `suffix_index` to keep diffs minimal.
7. Splice the serialized literal into `html`:
   - Replace the substring from `prefix_index` (inclusive) through `suffix_index` (inclusive) with the new literal.
   - The character immediately after the splice must remain `;`. Do not add or remove the trailing semicolon.
   - Do not modify any other byte of `html`. Markup, styles, Alpine bindings, CDN references, and the surrounding `<script>` block must stay byte-identical.
8. Write the modified `html` to the same absolute path that stage `1-load` read from. Overwrite the existing file in place. Do not create a backup or sibling file unless the user explicitly requested one.

## After writing

Surface a short status to the user, then stop. Two formats only:

Clean pass (stamp only):

```
OK — <kept> findings validated, no changes needed
file:///<absolute-path-to-report>
```

Rewritten report:

```
Validated <total>: <kept> kept, <adjusted> adjusted, <removed> removed
file:///<absolute-path-to-report>
```

Do not summarize the adjusted or removed findings inline. The HTML is the deliverable; the user opens it to read the diff between runs. If the user explicitly asked for a list of changes, append a single bulleted list of `id — short reason` lines beneath the status.

When findings survive, add one next-step line: `Run evenbetter-repair to apply these findings.` The report is now stamped, so repair will accept it. When every finding was removed, say the report is clean instead — there is nothing to repair.

## Recovery

If serialization or splice fails after stage 2 succeeded:

- Do not write a partially-modified file. Discard the in-memory `html` mutation.
- Report the failing step (serialization, splice anchor mismatch, post-write validation) and the finding `id` involved when applicable.
- Leave the original report untouched on disk.
