# 2 Validate

## Role

Re-check every finding in the loaded `report.issues` array against the live source code, the EvenBetter iOS corpus, and Apple HIG / Apple Developer Documentation. Decide for each finding whether to `keep`, `adjust`, or `remove`, and produce the corrected finding objects that stage `3-update` will write back.

## Why this stage exists

Audits drift. Source files get refactored between scan and review. The original analyze pass may have promoted a `warning` it should have left as `medium`, paired a real violation with a `recommended_fix` that does not actually compile, or attached a stale Apple URL after a documentation reshuffle. Validation is the layer that catches these errors before users start opening tickets against fixes that look authoritative but are wrong.

## Process

1. Pre-load corpus context once per run:
   - Read `../../corpus/index.json`. Build a map keyed by `clause_id` containing `domain`, `dimension`, `severity`, `source_url`, `source_label`, `file_path`, `anchor`, and `retrieved`.
   - Group findings by `clause_id`. For each unique `clause_id`, lazy-load the matching `../../corpus/ios/<domain>.md` and extract the H2 section: the metadata block (`Severity`, `Dimension`, `Platform`, `Source`, `Retrieved`), the **Check.** paragraph, the **Why.** paragraph, and the **Correct code.** Swift block. Cache the parsed clause body and reuse it across every finding that cites the same clause.
   - If a finding's `clause_id` is absent from `index.json`, mark the finding `remove` immediately with reason `clause not in corpus`. Do not try to rebind it.
2. For every finding, run the five checks in order. The first failing check decides the action:

   - **Clause check.** Look the finding's `clause_id` up in the cached corpus map. The clause body's `Severity`, `Source`, and **Check.** description are the contract for the rest of the validation. If the corpus index `source_url` differs from the finding's `hig_reference_url`, set `hig_reference_url` to the corpus value (the corpus index is authoritative) and mark the finding `adjust`.
   - **Source check.** Read the captured `file_path` around `line_number` (about 20 lines above and 20 below). Confirm the captured `code_snippet` still appears in the file and still satisfies the clause's **Check.** description in context. If the offending pattern is gone, decoratively-only, already wrapped by a parent modifier that satisfies the clause, or otherwise no longer matches the **Check** condition, the action is `remove`. If the violation moved by a few lines, update `line_number` and `code_snippet` to the new location and continue with `adjust`.
   - **Reference check.** Confirm `hig_reference_url` resolves and the page still states the rule the clause's **Check.** description encodes. If the URL is dead, replace it with the current canonical Apple HIG or Apple Developer Documentation URL and propose the same value as the corpus index `source_url` — flag corpus drift in the validation log when the corpus URL is also stale. If no canonical Apple replacement exists, the action is `remove`.
   - **Severity check.** Start from the corpus clause's `Severity` field, then apply the four-tier mapping documented in `evenbetter-analyze/SKILL.md`:
     - `error` → `critical` — user harm, accessibility blocker, destructive risk, high-confidence violation.
     - `warning` (strong static evidence and direct user impact) → `high`.
     - `warning` (broader uncertainty or context-dependent impact) → `medium`.
     - `info` → `low` — polish, consistency, non-blocking quality improvement.
     A `warning`-derived finding can be promoted to `critical` only when the surrounding context turns the violation into an accessibility blocker (for example, an unlabeled `Image(systemName:)` inside a destructive `Button`). If the recorded `severity` does not match the corpus-grounded mapping, update `severity` and mark the finding `adjust`.
   - **Fix check.** Read the candidate `minimal_fix` and `recommended_fix` against the captured snippet and the clause's **Correct code.** block. Both fixes must be valid Swift in context, both must reference identifiers from the snippet, and both must actually close the violation defined by **Check.**:
     - `minimal_fix` — smallest mechanical patch (one added modifier, a single argument change, a renamed identifier). If it does not fully close the violation expressed in **Check.**, rewrite it.
     - `recommended_fix` — system-native, Apple-blessed approach. The structure should align with the clause's **Correct code.** Swift block (`Button` instead of `onTapGesture`, `NavigationStack` instead of `NavigationView`, `confirmationDialog` instead of `actionSheet`, semantic system colors, lifted accessibility on the parent group, etc.). If the existing one is style-equivalent to the minimal fix or diverges from the **Correct code.** pattern, rewrite it.
     If either fix changed, also rewrite `ai_fix_prompt` so it stays consistent with the new recommended fix.

3. Repair re-check. A finding whose `repair.status` is `applied` was edited by `evenbetter-repair` since the last pass, and the source check above is the verdict on that edit:
   - The finding failed the source check and is being removed — the repair worked. Nothing extra to record; the finding leaves the report.
   - The finding survived the source check — the repair did not close the violation. Set `repair.status` to `failed`, leave `repair.path`, `repair.owner`, and `repair.changed_files` as they are so the next run can see what was tried, replace `repair.note` with one sentence naming what still matches the clause's **Check**, and mark the finding `adjust`.
   Never set `repair.status` to `applied`, `deferred`, or `skipped` from this skill, and never clear a `repair` block. Validation reads the ledger and may only flip an unsuccessful `applied` to `failed`; everything else in it belongs to `evenbetter-repair`.
4. WCAG cross-reference. When the clause maps to a WCAG 2.2 Success Criterion (commonly 1.1.1 Non-text Content, 1.3.1 Info and Relationships, 1.4.3 Contrast, 1.4.10 Reflow, 1.4.11 Non-text Contrast, 2.1.1 Keyboard, 2.4.3 Focus Order, 2.5.3 Label in Name, 2.5.5 Target Size, 4.1.2 Name/Role/Value), confirm `wcag_criteria` and `wcag_level` against `https://www.w3.org/WAI/WCAG22/quickref/`. WCAG is a cross-reference, never the primary citation. If the criterion no longer applies, clear the field; if it does and the recorded value is wrong, update it. Either change is an `adjust`.
5. Re-write `ai_fix_prompt` whenever `recommended_fix`, `file_path`, `line_number`, or `code_snippet` changed. The prompt must:
   - Lead with the absolute file path and the line range to edit.
   - State the corpus clause ID and the user-impact reason (lifted from the clause's **Why.** block) in one sentence.
   - Include the original snippet and the recommended replacement, both fenced with `swift`.
   - End with a one-line acceptance check the agent can run mentally.
   - Stay under ~200 words.
6. Stop validating once you have re-checked every finding. Do not invent new findings — discovery is `evenbetter-analyze`'s job.

## Decision recording

For every finding, record the decision and the post-validation finding object in memory:

```json
{
  "decision": "keep | adjust | remove",
  "issue": { /* updated finding object, identical schema as input, only present when decision is keep or adjust */ },
  "reasons": ["short, imperative reason strings, one per check that fired"]
}
```

Keep `id`, `clause_id`, `file_path`, `code_snippet`, and `line_number` stable on `keep`. On `adjust`, change only the fields that failed a check. On `remove`, drop the finding from the surviving list entirely. Carry each surviving finding's `repair` block through unchanged, except for the one `applied` → `failed` flip described above.

## Hard rules for editing fixes

- Both fixes must compile against the snippet's identifiers. Do not introduce variables that the surrounding code does not declare.
- If only one solution is reasonable (the violation is structural, e.g., replacing `NavigationView` with `NavigationStack`), set `minimal_fix` equal to `recommended_fix` and add one sentence to `description` clarifying that they intentionally match.
- Never use `accessibilityLabel("…")` strings that paraphrase visible text in a way that breaks WCAG 2.5.3 Label in Name. The accessible label must contain the visible text verbatim, possibly with extra context appended.
- Never recommend `accessibilityHidden(true)` for any element a user can interact with.
- Never recommend hard-coded `Color(red:green:blue:)` or hex literals as a `recommended_fix`. Always lift to a semantic asset color or a system color.

## Stage exit criteria

Move to stage `3-update` only when:

- Every input finding has exactly one decision: `keep`, `adjust`, or `remove`.
- Every surviving finding's `clause_id` is present in `../../corpus/index.json`.
- Every surviving finding still has a non-empty `hig_reference_url` that begins with `https://developer.apple.com/`, and that URL matches the corpus index `source_url` for the same `clause_id` unless the corpus itself is stale.
- Every surviving finding's `severity` is one of `critical`, `high`, `medium`, `low` and is consistent with the corpus-grounded mapping for its clause.
- Every surviving finding's `recommended_fix` is structurally aligned with the clause's **Correct code.** block.
- IDs remain stable. Do not renumber survivors. The report's UI keys off `id` for deep links and severity filters.
- Every surviving finding still carries a `repair` block, backfilled by stage `1-load` when the report predates it.
- If every decision is `keep`, mark the validation pass clean. Stage `3-update` will write only the workflow stamp and emit the "OK" status.
