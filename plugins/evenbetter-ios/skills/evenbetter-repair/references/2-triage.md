# 2 Triage

## Role

Split the queue into findings this skill may repair on its own and findings that belong to a human, then choose the remediation path for the repairable ones. Triage decides *who* acts and *which fix*; stage `3-apply` performs the edits.

## Why this stage exists

The audit report already contains two remediations and an AI prompt per finding. What it cannot do is tell the difference between "add the missing accessibility label" and "decide what this button should be called". The first is a conformance change with one correct answer, grounded in a corpus clause. The second is a product decision that happens to surface as a conformance finding. Applying both classes automatically is how an audit tool starts rewriting a product's voice.

Triage draws that line explicitly, so the technical work runs unattended and the judgement calls reach the person who owns them.

## The R2 boundary

A finding is a **human decision** when closing it would change any of the following. Defer it.

| Class | Examples |
| --- | --- |
| Product copy | Button titles, labels a user reads aloud, empty-state text, error wording, any string that has to *say* something new rather than restate what is on screen. |
| Navigation and IA | Where a screen sits, whether a flow becomes a sheet or a push, tab structure, back-button semantics, what a deep link resolves to. |
| Product behaviour | Whether an action gets a confirmation step, whether an operation becomes undoable, what a destructive action actually destroys, what a control does. |
| Visual design | Brand colours, the choice of a semantic colour when several fit, spacing and layout beyond the minimum the clause requires, icon selection, typography scale. |
| Scope beyond the finding | The fix requires touching a second file that is not itself a finding, changing a shared component used elsewhere, or adding a new type. |

A finding is **agent-repairable** when the remediation is a mechanical conformance change with a single correct shape:

| Class | Examples |
| --- | --- |
| Accessibility plumbing | Adding `.accessibilityLabel` that restates existing visible text verbatim, adding a missing trait, grouping an already-labelled composite with `.accessibilityElement(children: .combine)`, marking a genuinely decorative image hidden. |
| API modernization | `NavigationView` to `NavigationStack`, `actionSheet` to `confirmationDialog`, a deprecated modifier to its documented replacement. |
| Semantic substitution | A hard-coded colour to the equivalent semantic system colour named by the clause, a fixed font size to a Dynamic Type text style. |
| Interaction correctness | `onTapGesture` on a control that should be a `Button`, a hit target grown to the documented minimum, a missing `.disabled` state on an inert control. |
| Structural conformance | Any change whose target shape is written out in the clause's **Correct code** block and whose identifiers all already exist in the snippet's scope. |

When a finding sits on the boundary — the fix is mechanical but the *value* is editorial, such as an accessibility label for an icon-only button — it is a human decision about the string and an agent repair about the modifier. Ask the closed question, then apply. If the question cannot be asked, defer.

## Process

1. For each finding in the queue, in queue order:
   - Load its cached corpus clause. Read the **Check**, **Why**, and **Correct code** blocks.
   - Re-read the source at `file_path` around `line_number`, about 20 lines either side. Confirm the `code_snippet` is still there and the **Check** condition still holds.
     - If the violation is already gone, the outcome is `skipped` with `note` of `already satisfied in source`. Do not edit. Do not treat this as an error — validation ran earlier and the source may have moved since.
     - If the snippet moved by a few lines, record the new `line_number` for stage `3-apply` and continue.
     - If the file is gone entirely, the outcome is `skipped` with `note` naming the missing file.
   - Classify against the R2 boundary above.
2. For a **human-decision** finding, try to convert it into a closed question before deferring:
   - Draw 2-4 concrete candidate answers from the surrounding code — existing strings in the same view, the sibling controls' naming pattern, the semantic colours already used in the file.
   - State the user impact in one sentence lifted from the clause's **Why** block, so the human is deciding on impact rather than on syntax.
   - Ask with the environment's structured-question tool. An answer converts the finding to agent-repairable with the chosen value; declining, or having no question tool available, leaves it `deferred`.
   - Batch the questions. Ask once per finding, but gather the run's questions and ask them together where the tool allows rather than interrupting after every edit.
3. For an **agent-repairable** finding, choose the path:
   - Default to `recommended_fix`.
   - Choose `minimal_fix` when the recommended path would restructure a view the finding does not own, touch a file outside the audited scope, or exceed a smallest-safe-change scope the user asked for.
   - When both fixes are identical — validation sets them equal for structural violations — apply the shared text and record the path as `recommended`.
   - If the chosen fix references an identifier that does not exist in the snippet's scope, do not substitute one. The outcome is `failed` with the missing symbol in `note`.
4. Record the triage decision for every finding before any edit is made. Stage `3-apply` should not be re-deciding classification mid-edit.

## Triage record

Hold one record per finding:

```json
{
  "id": "EB-004",
  "route": "apply | defer | skip | fail",
  "path": "minimal | recommended | \"\"",
  "fix_text": "the exact remediation to apply, after any human-supplied value is substituted",
  "line_number": 0,
  "reason": "one short imperative sentence",
  "question_asked": false
}
```

`reason` is what reaches the user and the report's `note` field, so write it for a developer reading the report a week later: `deferred — button title is product copy, three candidates offered`, not `needs input`.

## Stage exit criteria

Move to stage `3-apply` only when:

- Every queued finding has exactly one route.
- Every `apply` route has a non-empty `fix_text` and a `path` of `minimal` or `recommended`.
- Every `defer` route has a `reason` that names the class from the R2 boundary table.
- No route was chosen by guessing at a product decision. If you cannot tell whether a change is editorial, it is editorial — defer it.
