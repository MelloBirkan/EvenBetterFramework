# 4 Status

## Role

Write the outcome of every finding back into `.evenbetter/<project-name>/evenbetter-analyze-report.html`, stamp the workflow block, and give the user the handoff: what changed, what is waiting on them, and what to run next.

This stage always runs, including after an interrupted or entirely deferred run. The report is the ledger; source edits that never reach it leave the code ahead of the record.

## Process

1. Collect the outcome for every finding in `report.issues`, not only the ones in the queue:
   - Queued findings take their resolved route from stages `2-triage` and `3-apply`.
   - `out_of_scope` findings from stage `1-load` become `skipped`, with `note` recording the scope the user set.
   - Findings already `applied` or `deferred` from a previous run keep their existing `repair` object untouched. Do not restamp `applied_at` on work this run did not do.
2. Update each finding's `repair` object in place:

   ```json
   {
     "status": "applied | deferred | skipped | failed | pending",
     "path": "minimal | recommended | \"\"",
     "owner": "agent | human | \"\"",
     "applied_at": "YYYY-MM-DD HH:MM:SS or \"\"",
     "changed_files": ["Sources/Feature/CartView.swift"],
     "note": "one sentence"
   }
   ```

   - `applied` sets `path`, `owner: "agent"`, `applied_at`, and `changed_files`.
   - `deferred` sets `owner: "human"`, leaves `path` and `applied_at` empty, and puts the decision the human owes in `note` — the class from the R2 boundary table plus the candidates that were offered.
   - `skipped` sets `owner: "agent"` and puts the reason in `note`: out of scope, already satisfied, missing file, or clause no longer in the corpus.
   - `failed` sets `owner: "agent"`, leaves `applied_at` empty, and puts the failing check and its evidence in `note`.
   - `pending` survives only for findings a stopped run never reached.
3. Leave everything else in the finding untouched. Repair never edits `id`, `clause_id`, `title`, `description`, `severity`, `hig_reference_url`, `code_snippet`, `minimal_fix`, `recommended_fix`, `ai_fix_prompt`, or `language`. If an applied edit moved the code, `line_number` may be updated to the new site; nothing else moves.
4. Do not remove findings and do not recompute `summary`. A finding whose repair landed is still a finding until `evenbetter-validate` re-checks the source and drops it. Keeping the counts stable is what makes the next validation run a meaningful diff.
5. Stamp the workflow block:

   ```json
   "workflow": {
     "state": "repaired",
     "validated_at": "<unchanged>",
     "validation": "<unchanged>",
     "repaired_at": "YYYY-MM-DD HH:MM:SS",
     "repair": { "applied": 9, "deferred": 3, "skipped": 1, "failed": 1 }
   }
   ```

   - `state` becomes `repaired` when at least one finding was applied. A run that only deferred or skipped leaves `state` as `validated` — nothing was repaired, so nothing should claim to be.
   - `validated_at` and the `validation` tally are carried through untouched. Repair never restamps validation, and never fabricates one.
   - `repaired_at` is the current local time, set only when `state` becomes `repaired`.
   - The `repair` tally counts the whole `issues` array by status, so it stays true across runs rather than describing only this invocation.
6. Serialize and splice exactly as `evenbetter-validate` stage `3-update` does:
   - Deterministic JSON with the schema's key order, mirroring the previous literal's formatting so the diff stays minimal.
   - Replace the substring from `prefix_index` through `suffix_index` inclusive. The character immediately after must remain `;`.
   - No other byte of the HTML changes. Markup, styles, Alpine bindings, and CDN references stay byte-identical.
7. Sanity-check before writing:
   - Every `repair.status` is one of `applied`, `deferred`, `skipped`, `failed`, `pending`.
   - Every `applied` finding has a non-empty `applied_at` and at least one entry in `changed_files`.
   - Every `deferred` and `failed` finding has a non-empty `note`.
   - `summary.total === issues.length` and the per-severity counts are unchanged from the loaded report.
   - `workflow.validated_at` is unchanged from the loaded report.

   If a check fails, do not write. Name the failing finding `id` and field, and say plainly that the source edits already landed while the ledger did not.
8. Write the modified HTML to the same absolute path stage `1-load` read from. Overwrite in place; no backup or sibling file.

## The handoff

The point of this stage is the handoff that the report alone does not provide. Emit, in this order:

1. One tally line:

   ```
   Repaired 14: 9 applied, 3 deferred, 1 skipped, 1 failed
   ```

   For a run that changed nothing: `Nothing applied — 3 deferred, 1 skipped`.

2. The report path as a `file://` link or copyable path.

3. The deferred findings, one line each, because these are the only items that need a human and they will otherwise be lost in the HTML:

   ```
   Waiting on you:
   - EB-004 CartView.swift:52 — button title is product copy. Offered: "Delete item", "Remove from cart", "Delete".
   - EB-011 RootTabs.swift:18 — moving Settings out of the tab bar is a navigation decision.
   ```

4. The failed findings, one line each, with the check that failed.

5. One next-step line naming the actual next invocation:
   - Anything applied: `Re-run evenbetter-validate to confirm the repairs closed their findings.`
   - Only deferrals left: `Answer the questions above, then re-run evenbetter-repair.`
   - Nothing left in any state but `applied` and `skipped`: `Re-run evenbetter-validate — the report should come back clean.`

Do not print the applied diffs inline. The source control diff is the record for those; the chat summary is for what the human still owns.

## Re-validation contract

Repair deliberately leaves the findings in place. The loop closes on the next `evenbetter-validate` run:

- A finding whose violation is genuinely gone fails validation's source check and is removed from the report.
- A finding still matching its clause despite `repair.status` of `applied` is flipped to `failed` by validation, with a note that the repair did not close it. The next repair run picks it up again, because its queue includes `failed`.
- `deferred` and `skipped` findings survive validation untouched unless the source itself changed.

That is why repair must not delete findings or recompute `summary`: doing so would erase the evidence the next validation pass needs.

## Recovery

If serialization or the splice fails after source edits landed:

- Do not write a partially-modified report. Discard the in-memory HTML mutation.
- Say explicitly that the source edits are on disk and the report was not updated, list the applied finding IDs and their changed files, and name the failing step.
- Leave the original report untouched on disk. Re-running repair after the report is fixed will re-detect the already-satisfied findings as `skipped`, so nothing is applied twice.
