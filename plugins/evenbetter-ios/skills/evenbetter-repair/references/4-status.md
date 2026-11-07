# 4 Status

Contents: Role, Process, Writing the report, The handoff, Re-validation contract, Recovery.

## Role

Write the outcome of every finding back into `.evenbetter/[project]/evenbetter-analyze-report.html`, stamp the workflow block, and give the user the handoff: what changed, what is waiting on them, and what to run next.

This stage always runs, including after an interrupted or entirely deferred run. The report is the ledger, and source edits that never reach it leave the code ahead of the record. `[script]` is the absolute path of `../../scripts/evenbetter_report.py`, resolved against the SKILL.md folder.

## Process

1. Collect the outcome for every finding in `report.issues`, not only the queued ones:
   - Queued findings take their resolved route from stages `2-triage` and `3-apply`. Every finding a combined edit closed is `applied` with the same `changed_files` and `applied_at`.
   - `out_of_scope` findings from stage `1-load` become `skipped`, with the user's scope in `note`.
   - Findings already `applied` or `deferred` from an earlier run that this run did not queue keep their `repair` object as it was, apart from the site note in step 3. Do not restamp `applied_at` on work this run did not do.
2. Update each finding's `repair` object in place:

   ```json
   {
     "status": "applied | deferred | skipped | failed | pending",
     "path": "minimal | recommended | \"\"",
     "owner": "agent | human | \"\"",
     "applied_at": "YYYY-MM-DD HH:MM:SS or \"\"",
     "changed_files": ["Sources/Feature/CartView.swift"],
     "note": "one or two sentences"
   }
   ```

   - `applied` sets `path`, `owner: "agent"`, `applied_at` and `changed_files`. `note` stays empty for a plain edit and says why otherwise: closed by the combined edit for another finding, the minimal path because the recommended fix crosses the R2 boundary, or a derived `clause_id`.
   - `deferred` sets `owner: "human"`, leaves `path` and `applied_at` empty, and puts the decision the user owes in `note`: the class from the R2 boundary table, the candidates offered, and which one is recommended. If the mechanical part of its fix landed with a combined edit, `note` says which part.
   - `skipped` sets `owner: "agent"` and puts the reason in `note`: out of scope, already satisfied, or a missing file.
   - `failed` sets `owner: "agent"`, keeps any `applied_at` an earlier run left (empty otherwise), and puts the failing check and its evidence in `note`.
   - `pending` survives only for findings a stopped run never reached.
3. Leave every other finding field untouched. Repair never edits `id`, `title`, `description`, `severity`, `wcag_criteria`, `wcag_level`, `hig_reference_url`, `file_path`, `code_snippet`, `minimal_fix`, `recommended_fix`, `ai_fix_prompt`, `language` or `runtime`, and changes `clause_id` or `related_clause_ids` only to fill them when they were missing (stage `1-load`). Two exceptions apply to `line_number`:
   - If an applied edit moved the code, `line_number` may move to the new site.
   - If this run's edits rewrote or moved the construct of a finding that stays `deferred`, `failed` or `pending`, move its `line_number` to the construct's new place and append to `note`: `site rewritten by the EB-019 edit; code_snippet shows the code before repair.` That lets the next run find it.
4. Do not remove findings and do not recompute `summary`. A finding whose repair landed stays a finding until evenbetter-validate re-checks the source and drops it, and stable counts are what make the next validation run a meaningful diff.
5. Stamp the workflow block:

   ```json
   "workflow": {
     "state": "repaired",
     "validated_at": "[unchanged]",
     "validation": "[unchanged]",
     "repaired_at": "YYYY-MM-DD HH:MM:SS",
     "repair": { "applied": 9, "deferred": 3, "skipped": 1, "failed": 1 }
   }
   ```

   - `state` becomes `repaired`, and `repaired_at` the current local time, when this run applied at least one finding. A run that applied nothing leaves `state` and `repaired_at` as loaded, so a `validated` report stays `validated`.
   - `validated_at` and the `validation` tally are carried through untouched. Repair never restamps or invents a validation.
   - The `repair` tally counts the whole `issues` array by status, so it stays true across runs rather than describing only this invocation.

## Writing the report

With `python3`:

1. Write the updated `report` as JSON to a temporary file outside the project and the plugin folder, for example one made with `mktemp`.
2. Run `python3 [script] update [temp file] [absolute report path] --state [the new workflow.state]`. It checks the data first and writes nothing if a check fails. On success it replaces only the embedded data, with the script-tag escaping done for you, and every other byte of the report stays as it was. Do not use `render`, which archives the report into `history/` as if analyze had re-run.
3. If `update` exits 1, name the failing finding `id` and field from each message, and say plainly that the source edits already landed while the ledger did not.
4. Delete the temporary file.

By hand:

1. Sanity-check the object before serializing. These are the checks the script runs:
   - Every `repair.status` is `applied`, `deferred`, `skipped`, `failed` or `pending`.
   - Every `applied` finding has a non-empty `applied_at` and at least one entry in `changed_files`, and findings a combined edit closed share the same list.
   - Every `deferred` and `failed` finding has a non-empty `note`.
   - `summary.total` equals `issues.length`, and the per-severity counts are unchanged from the loaded report.
   - `workflow.validated_at` is unchanged, and `workflow.repair` matches the counts of `issues` by status.
   - Every `runtime` block is the loaded one, or the `untested` backfill from stage `1-load`, and sits right after `repair`.
   - A `repaired` report has at least one `applied` finding and a `repaired_at` no earlier than `validated_at`. A report that stays `validated` has no `applied` findings.

   If a check fails, do not write. Name the failing finding `id` and field, and say plainly that the source edits already landed while the ledger did not.
2. Serialize to JSON the way the helper does, so either path produces the same file: keys in the order they were loaded, two-space indentation, and non-ASCII characters kept as they are. Then write `</` as `<\/`, `<!--` as `\u003c!--`, and the characters U+2028 and U+2029 as `\u2028` and `\u2029`, so the data cannot end or confuse the script tag.
3. Replace the substring of `html` from `prefix_index` through `suffix_index`, inclusive. The character after the splice must still be `;`, and no other byte of the HTML changes.
4. Write `html` to the same absolute path stage `1-load` read from, overwriting it in place. Make no backup or sibling file.

## The handoff

The report alone does not tell the user what they still own. Give, in this order:

1. One tally line, for example `Repaired 14: 9 applied, 3 deferred, 1 skipped, 1 failed`. For a run that changed nothing: `Nothing applied: 3 deferred, 1 skipped`.
2. The report path as a `file://` link or copyable path.
3. The deferred findings, one line each, because they are the only items that need a person and they get lost in the HTML:

   ```
   Waiting on you:
   - EB-004 CartView.swift:52: the button label is product copy. Options: "Delete item" (recommended), "Remove from cart", "Delete".
   - EB-011 RootTabs.swift:18: moving Settings out of the tab bar is a navigation decision.
   ```

4. The failed findings, one line each, with the check that failed.
5. Deferred or failed findings that an applied edit made reachable or visible, for example `EB-021 now opens PlantDetailView, where the one-tap delete in EB-006 is still deferred.`
6. Any clause IDs derived in stage `1-load`, a different project root, and a missing build command, each said once.
7. One next-step line:
   - Anything applied: `Next, run evenbetter-validate to confirm the repairs closed their findings. To check them in the running app first, run evenbetter-accessibility-tests with recheck, then evenbetter-validate.`
   - Only deferrals left: `Answer the questions above, then run evenbetter-repair again.`
   - Nothing left but `applied` and `skipped`: `Next, run evenbetter-validate. The report should come back clean.`

Do not print the applied diffs inline. Source control holds those, and the chat summary is for what the user still owns.

## Re-validation contract

Repair leaves the findings in place on purpose. The loop closes on the next evenbetter-validate run:

- A finding whose violation is gone fails validation's source check and is removed from the report.
- A finding that still matches its clause despite `repair.status` of `applied` is flipped to `failed` by validation, with a note that the repair did not close it. The next repair run picks it up, because its queue includes `failed`.
- The same happens when evenbetter-accessibility-tests, run with `recheck` after this skill, confirms the problem in the running app: validation reads a `confirmed` verdict newer than the finding's `repair.applied_at` on an `applied` finding as a repair that did not hold. A `refuted` verdict is evidence for validation, never a removal on its own.
- `deferred` and `skipped` findings survive validation untouched unless the source itself changed.

Deleting findings or recomputing `summary` here would erase the evidence the next validation pass needs.

## Recovery

If serialization, `update` or the splice fails after source edits landed:

- Do not write a partially modified report. Discard the in-memory change.
- Say plainly that the source edits are on disk and the report was not updated. List the applied finding IDs and their changed files, and name the step that failed.
- Leave the original report untouched on disk. A later repair run re-detects the already satisfied findings as `skipped`, so nothing is applied twice.
