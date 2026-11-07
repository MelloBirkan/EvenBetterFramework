# 2 Validate

Contents: Role, Before the checks, The checks, Repair re-check, Runtime verdicts, Decision recording, Rules for fixes, Stage exit criteria.

## Role

Re-check every finding in the loaded report against the current source code, the EvenBetter iOS corpus and Apple's documentation. Decide `keep`, `adjust` or `remove` for each one, and produce the corrected findings that stage `3-update` writes back.

The code can change between the scan and the review. Analyze can misjudge a severity or write a fix that does not compile, and Apple pages move. This stage catches those problems before evenbetter-repair acts on them. It does not look for new problems; discovery belongs to evenbetter-analyze.

## Before the checks

1. Read `../../corpus/index.json` once. Map each `clause_id` to its `domain`, `severity`, `source_url`, `file_path` and `retrieved`. The index `file_path` values are relative to the plugin root, so `corpus/ios/accessibility.md` is `../../corpus/ios/accessibility.md` from the SKILL.md folder.
2. Group the findings by every clause they carry, primary and related. Load a domain file the first time one of its clauses comes up and cache each parsed clause: its `Severity`, `Source` and `Retrieved` lines, the **Check**, the **Why** and the **Correct code** block.
3. Fetch each distinct index `source_url` once, with a scraper that renders JavaScript or Apple's JSON form described in SKILL.md, and reuse the result for every finding that cites it. If no fetch tool works, rely on the corpus and remember to say so in the status line.
4. Keep the to-do list from stage 1 at hand. Every line on it has to be resolved by the end of this stage, either by a change or by removing the finding.
5. Note each finding's `runtime.status` and `checked_at`, and its `repair.applied_at`. Runtime verdicts come from evenbetter-accessibility-tests, and Runtime verdicts below says how the source check and the repair re-check use them.

## The checks

Run checks 1 and 2 on every finding first, so the merge check compares findings in their current state. Then run checks 3 to 8 on each finding that is left.

The checks add up. Each one works on the finding as the earlier checks left it and records the fields it changed; any recorded change makes the decision `adjust`. A check that decides `remove` ends the checks for that finding.

1. **Clause check.**
   - Drop any `related_clause_ids` entry that is not in the index. If the primary `clause_id` is not in the index, the source check picks a new primary from the related clauses. When there are none, remove the finding with the reason `clause not in corpus`.
   - Set `hig_reference_url` to the index `source_url` of the primary clause whenever the two differ. The description may cite a more specific Apple page; this field never does.
   - When a clause's `retrieved` date is later than the report's `scan_date`, the corpus changed after the scan. Judge the finding by the current clause body, not by what the report recorded.
2. **Source check.** Open `file_path` and read about 20 lines above and below `line_number`.
   - Find the snippet. If the construct moved, update `line_number`, and update `code_snippet` when its lines changed but it is the same construct. If the recorded snippet is elided or trimmed (it contains `// ...` or `…`, or skips lines), capture it again verbatim and contiguous, as the Snippet capture rules in `../evenbetter-analyze/references/1-scan.md` describe. A new snippet means the fix check has to rewrite both fixes.
   - Decide, for each clause on the finding, whether it still holds in context. Read its **Check** for intent: it describes the common form of the violation, so a control built as `Image` plus `.onTapGesture` counts as a button for button clauses. Look for parent modifiers, `if` and `#if` branches, `accessibility*` modifiers further up the chain, and siblings that already satisfy the clause.
   - A view that nothing references is dead code: remove the finding. A view that is unreachable only because of another finding in the report still counts.
   - No clause holds: remove the finding, with the reason (false positive, fixed since the scan, satisfied by a parent, decorative only).
   - A `refuted` runtime verdict is one input to this check, never a reason to remove the finding on its own. Weigh it with the code and record a `Runtime:` note, as Runtime verdicts below describes. A finding whose `runtime.status` is `confirmed` with a `checked_at` later than its `repair.applied_at` is not removed here either, whatever its `repair.status`, because the running app still shows the problem. An empty `repair.applied_at` counts as earlier than any `checked_at`. The repair re-check below marks an `applied` one `failed`; any other one keeps its `repair` block unchanged.
   - The primary clause no longer holds but a related one does: make the related clause the primary, choosing as the merge rule in `../evenbetter-analyze/references/2-verify.md` does (the clause whose **Correct code** the fix most resembles, then the higher corpus severity, then index order). Drop the clauses that no longer hold, and set `hig_reference_url` for the new primary.
   - You may add a clause in two cases only. The first is the twin of a clause already on the finding, from the twin table in `../evenbetter-analyze/references/2-verify.md`, when its Check holds too. The second is an exclusive pair from the table after it, when the code falls on the other side of the pair's split. `LAY-A11Y-001` covers a hit area under 28x28 pt and `LAY-UI-001` one from 28x28 pt up to 44x44 pt. `TYPO-A11Y-004` covers a Dynamic Type cap on primary content and `TYPO-A11Y-005` one on a small repeated control such as a tab bar. Swap the clause on the finding for the other one and set `hig_reference_url` for it. The new clause can change the severity, the fixes and the WCAG fields, which the later checks settle; if its `source_url` was not fetched in step 3, fetch it now for the reference check. Never move a finding to any other clause that was not on it.
3. **Merge check.** Compare the finding with the other surviving findings in the same file whose lines overlap it. Merge two findings only when they sit on the same construct and one of these holds: they share a clause, they split a twin pair, or one edit closes both. The construct is the view expression a snippet centres on, with its own modifiers: one `Button`, one `Image`, one `TextField`. Two controls in the same `HStack` or `toolbar` are two constructs, so findings on them stay separate even when their lines overlap or one commit could fix both. The exception is two constructs that start on the same line and share a clause or a twin pair: give them one finding, because the report checker treats `file_path` plus `line_number` as one site. Two such constructs on opposite sides of an exclusive pair also get one finding, with only the stricter clause (`LAY-A11Y-001` or `TYPO-A11Y-004`) and fixes that bring both constructs up to it. This is the grouping rule evenbetter-analyze uses, and keeping to it makes repeated validations of one report give the same findings.
   - Keep the finding with the lower `id` and remove the other with the reason `merged into EB-00N`.
   - Move the removed finding's clauses into the survivor's `related_clause_ids`, with no clause listed twice and the primary never repeated. Re-pick the primary by the merge rule if the edit now centres on another clause.
   - Widen the survivor's `code_snippet` when the two snippets cover different lines, so it is one contiguous, verbatim block that covers both.
   - The survivor keeps its own `repair` and `runtime` blocks. The removed finding's ledger and runtime verdict leave with it.
   - Different edits on the same construct stay separate findings. Converting a tappable trash `Image` to `Button(role: .destructive)` is one finding; adding a confirmation before the delete needs new state and an alert, so it is a second one.
4. **Reference check.** Use the page fetched for each clause on the finding. A page passes when it states the rule the clause encodes or, for an API reference page, when it documents the API the fix relies on; the clause's **Why** carries the rule, so a terse API page is not a failure. A page fails only when it is gone or now contradicts the clause.
   - A failing clause leaves the finding. If it was the primary, pick a new one as in the source check. If no clause is left, remove the finding with the reason `no Apple source supports it`. This applies to `error` clauses too: they are dropped with a note, never downgraded.
   - Add one note per failing clause to `scan_context.notes`: `Corpus drift: [clause ID], [URL], [what changed].`
   - Keep `hig_reference_url` equal to the index `source_url` even when the page moved. The corpus owns that URL, and the drift note tells its maintainers to update it.
   - When no source could be fetched, skip this check and rely on the corpus.
5. **Severity check.** Apply the Severity mapping table in SKILL.md to every clause on the finding and keep the highest result. An `error` clause always gives `critical`, an `info` clause always gives `low`, and a `warning` finding is `high` by default, `medium` when the violation depends on runtime context the code does not show, and `critical` when the context makes it an accessibility blocker or a destructive risk. A `warning` finding never becomes `low`.
6. **Fix check.** Read `minimal_fix` and `recommended_fix` against the current `code_snippet`, the surrounding code and the **Correct code** of every clause on the finding. Rewrite a fix that fails any of these:
   - It is a complete replacement for `code_snippet`: every line written out with the snippet's indentation, and no `// ...`, `…` or "rest unchanged" comments.
   - It compiles in context, using only identifiers the surrounding code declares plus system APIs.
   - It closes every clause on the finding, primary and related.
   - `minimal_fix` is the smallest change that does that. `recommended_fix` follows the primary clause's **Correct code** or another approach its Check or title allows (`NAV-UI-001` accepts `NavigationStack` or `NavigationSplitView`). Treat **Correct code** as the pattern to follow, not as the only valid text.
   - A fix that also needs lines elsewhere is split into parts. The first part replaces `code_snippet`. Each later part starts with a `// File: [project-relative path]` line and a second comment line saying where it goes, for example `// Add to struct AddPlantView, after the existing properties:`. A fix with parts starts with a `// File:` line. When the whole edit belongs in a different file, keep `file_path` as it is: the first part repeats `code_snippet` unchanged, and the description says where the change goes.
   - When the violation is structural and only one fix is reasonable, both fixes are the same and the description says they match on purpose.
   - It follows the Rules for fixes below.
7. **WCAG check.** `wcag_criteria` holds at most one WCAG 2.2 success criterion and `wcag_level` that criterion's own level, or both are empty. Check numbers and levels on `https://www.w3.org/TR/WCAG22/` using the anchors in `../evenbetter-analyze/references/official-sources.md`, not on the Quick Reference, whose filters need JavaScript. The mapping table in `../evenbetter-analyze/references/2-verify.md` gives the usual criterion per problem.
   - The criterion's level must not be above the report's `wcag_level` target.
   - Target size is 2.5.8 Target Size (Minimum), level AA: 24 by 24 CSS pixels, with one iOS point counted as one CSS pixel. Use 2.5.5 Target Size (Enhanced) only when the report targets AAA. Apple's 44x44 pt guideline is stricter, so a 28x28 pt control can break the Apple clause and still meet 2.5.8; then leave both fields empty.
   - 4.1.1 Parsing is obsolete in WCAG 2.2; clear it.
8. **Text and prompt check.**
   - `title` is a short imperative in user-facing language. `description` says in 1-3 sentences what goes wrong for users and names, in plain words, what each related clause adds. Update both when the clauses on the finding changed.
   - Rewrite `ai_fix_prompt` when `recommended_fix`, `line_number`, `code_snippet` or the clause list changed, when the repository moved (stage 1), or when the prompt breaks any rule in Writing the AI fix prompt in `../evenbetter-analyze/references/2-verify.md`. The prompt leads with the absolute path and line range of every file the fix touches, gives the clause IDs and the user impact in one sentence, includes the original snippet and the recommended replacement fenced with `swift` (every part, with its `// File:` line), and ends with a one-line acceptance check. Its prose stays under about 120 words; the code blocks do not count.

## Repair re-check

A finding whose `repair.status` is `applied` was edited by evenbetter-repair since the last pass. Check its runtime verdict first, then the source:

- The running app still shows the problem: `runtime.status` is `confirmed` and `runtime.checked_at` is later than the finding's own `repair.applied_at` (both are `YYYY-MM-DD HH:MM:SS`, so the strings compare as times). Use the finding's stamp, not `workflow.repaired_at`: repair can run twice before the next validation, and a test run between the two would otherwise look older than the repair it checked. The test ran after this finding's repair and reproduced the problem, so the repair did not hold, even if the source now looks right. Mark it `failed` as in the next bullet, with a `note` that quotes `runtime.evidence` and names the test, for example `Still confirmed at runtime after the repair: hitRegion issue in standard on 'Delete' (EBAccessibilityAuditTests/test_PlantDetail_standard).` Keep the finding even when the source check found no clause that still holds.
- The violation is still in the source: the repair did not close it. Set `repair.status` to `failed` and replace `repair.note` with one sentence naming what still matches the clause's **Check**. Leave `repair.path`, `repair.owner`, `repair.applied_at` and `repair.changed_files` as they are, so the next repair run can see what was tried. The finding counts as `adjust`. If the repair changed the code around it, also update `line_number`, `code_snippet` and the fixes to the current code.
- The violation is gone and the finding is removed: the repair worked. Nothing more to record; the finding leaves the report.

A `confirmed` verdict from before the finding's `repair.applied_at` describes the code before the repair, so it does not count here, and the source check decides.

Findings with any other status are checked like the rest and keep their `repair` block untouched. Never set `repair.status` to `applied`, `deferred` or `skipped`, and never clear a `repair` block; only evenbetter-repair writes those.

## Runtime verdicts

Each finding's `runtime` block records what evenbetter-accessibility-tests saw in the running app. Validation reads it and never writes it: carry the block through unchanged, including on findings this stage adjusts or marks `failed`.

- `confirmed`: the running app reproduced the problem, which supports keeping the finding. For an `applied` finding, the repair re-check above says when it means `failed`.
- `refuted`: every planned test ran clean, and the audit map accepts a clean result as evidence against the finding's clauses. It never removes a finding on its own, because the audit sees only what was on screen in the configurations that ran. Weigh it in the source check with the code, the `configs` it lists and its `evidence`, then decide as usual and add one note for `scan_context.notes`:
  - Kept or adjusted: `Runtime: EB-005 was refuted at runtime on [checked_at], but the source still [what still matches the Check], so it stays.`
  - Removed: `Runtime: EB-005 was refuted at runtime on [checked_at]; the source check removed it as [reason].`
  - Skip the note when `scan_context.notes` already has a `Runtime:` note for the same finding and `checked_at`.
- `inconclusive`, `not_testable` and `untested` change nothing. Decide from the source.

## Decision recording

Record, for every finding:

- `decision`: `keep`, `adjust` or `remove`.
- `finding`: the updated finding object, for `keep` and `adjust`, in the same schema and key order as the input.
- `reasons`: one short line for each check that changed something, or for `remove` the reason, such as `fixed since the scan`, `false positive: the parent Button already provides the label`, `merged into EB-004`, `clause not in corpus` or `no Apple source supports it`.
- Any `Corpus drift:` or `Runtime:` note for `scan_context.notes`.

On `keep`, nothing changes. On `adjust`, only the fields a check changed. `id` and `file_path` never change, and the surviving findings keep their order and their ids; do not renumber after removals. The report's filters and links key on `id`.

## Rules for fixes

These are the same hard rules evenbetter-analyze applies in `../evenbetter-analyze/references/2-verify.md`:

- An accessibility label contains the visible text verbatim, possibly with context added, so WCAG 2.5.3 Label in Name holds.
- Wording that users see, such as a VoiceOver label or a button title, follows the visible UI, for example `"Delete \(plant.name)"` next to a plant's name.
- Never hide an interactive element with `accessibilityHidden(true)`.
- No `Color(red:green:blue:)` or hex literals in a recommended fix; use a semantic asset colour or a system colour.
- Fixed `.black` or `.white` text is allowed only on a fill that does not follow the system background, such as a tinted button fill or an image, with the reason in the description. On adaptive backgrounds use `.primary`, `.secondary` or another semantic style, because `CLR-UI-002` flags fixed black and white there.

## Stage exit criteria

Move to stage `3-update` only when:

- Every loaded finding has exactly one decision, and every line on the stage 1 to-do list is resolved.
- Every surviving finding's `clause_id` and `related_clause_ids` exist in the index, no clause is listed twice on one finding, no twin pair is split across findings, and neither exclusive pair (`LAY-A11Y-001` with `LAY-UI-001`, `TYPO-A11Y-004` with `TYPO-A11Y-005`) sits on one construct.
- Every `hig_reference_url` equals the index `source_url` of its `clause_id`.
- Every severity fits the SKILL.md table for the finding's clauses.
- Both fixes are complete replacements that close every clause on the finding, with every part of a multi-part fix labelled `// File:`, and every `ai_fix_prompt` names `file_path` and each `// File:` path.
- The WCAG fields are both set or both empty, with a level no higher than the report's target.
- No finding still has `repair.status` set to `applied`; each one was removed or marked `failed`. No finding with a `confirmed` verdict later than its `repair.applied_at` was removed by the source check, and each `applied` one among the survivors was marked `failed`.
- No finding was removed only because it was `refuted` at runtime, and every `refuted` finding has its `Runtime:` note.
- Every surviving finding carries a `repair` block and its loaded `runtime` block (or the `untested` backfill) unchanged, and the ids are the loaded ids, in the loaded order.

Stage 3 runs the report checker with `--state validated` on the result, so anything missed here stops the write. If every decision is `keep`, the pass is clean and stage 3 writes only the workflow stamp and any new `Runtime:` notes.
