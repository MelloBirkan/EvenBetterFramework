# 2 Triage

Contents: Role, Why this stage exists, The R2 boundary, Process, Edit sites, Triage record, Stage exit criteria.

## Role

Split the queue into findings this skill may repair on its own and findings that belong to a person, combine the findings that share an edit site, and choose the fix for each site. Triage decides who acts and which fix. Stage `3-apply` makes the edits.

## Why this stage exists

The audit report already contains two fixes and an AI prompt per finding. It cannot tell "add the missing button trait" apart from "decide what this button should be called". The first is a conformance change with one correct answer, grounded in a corpus clause. The second is a product decision that happens to surface as a conformance finding. An audit tool that applies both automatically ends up rewriting a product's voice.

Triage draws that line explicitly, so the technical work runs unattended and the judgement calls reach the person who owns them.

## The R2 boundary

Classify the fix you would apply, not only the finding. A finding can be agent-repairable through its `minimal_fix` while its `recommended_fix` adds new copy.

A fix is a human decision when it would change any of the following. Ask, or defer.

| Class | Examples |
| --- | --- |
| Product copy | Button titles, accessibility labels a user hears, empty-state text, error wording: any string that says something new rather than restating what is on screen. |
| Navigation and IA | Where a screen sits, whether a flow becomes a sheet or a push, tab structure, back-button behaviour, what a deep link opens. |
| Product behaviour | Whether an action gets a confirmation step, whether it becomes undoable, what a destructive action destroys, what a control does, an animation replaced rather than switched off. |
| Visual design | Brand colours, a semantic colour role when several fit, any colour for text on a fixed or brand fill, spacing and layout beyond the clause's minimum, icon choice, a change to the type hierarchy. |
| Scope beyond the finding | A second file the fix does not name with a `// File:` line, a shared component used elsewhere, or a new type. |

A fix is agent-repairable when it is a mechanical conformance change with one correct shape:

| Class | Examples |
| --- | --- |
| Accessibility plumbing | A label that restates the visible text verbatim, a missing trait, `.accessibilityElement(children: .combine)` on an already-labelled composite, hiding a decorative image. |
| API modernization | `NavigationView` to `NavigationStack`, `actionSheet` to `confirmationDialog`, a deprecated modifier to its documented replacement. |
| Semantic substitution | `.black` or `.white` text on a system background to `.primary`, as CLR-UI-002's Correct code shows; a literal colour to the semantic colour the clause names; a fixed font size to a text style. |
| Interaction correctness | A view with `.onTapGesture` to a `Button`, a hit target grown to the clause's minimum, a missing `.disabled` state, a Reduce Motion guard that switches an animation off. |
| Structural conformance | A change whose target shape the clause's Correct code writes out, whose project symbols all exist, and whose new declarations are limited to system environment values or private state the fix alone uses. |

Some values look like copy but are not new. The system's standard title for a standard role that the clause's Correct code shows, such as `Button("Cancel")` in the `.cancellationAction` slot (NAV-A11Y-002), restates a platform convention. Treat it as mechanical. When the fix also wraps the sheet's content in a `NavigationStack` to host that toolbar, the wrapper is part of the same change. It does not move the screen anywhere, so it is not a navigation decision.

A fix can be mechanical in shape while its value is editorial, such as an accessibility label for an icon-only button. The string is a human decision and the modifier is an agent repair: ask the closed question, then apply. If the question cannot be asked and answered in this session, defer.

## Process

1. For each finding, in queue order:
   - Read its cached clauses: the primary `clause_id` and every ID in `related_clause_ids`.
   - Re-read the source at `file_path` around `line_number`, about 20 lines either side, and confirm the construct is still there and at least one of its clause Checks still holds, read for intent.
     - If the violation is gone, the outcome is `skipped` with note `already satisfied in source`. This is not an error: the source may have moved since validation. The exception is a finding whose `runtime.status` is `confirmed` with a `checked_at` later than its `repair.applied_at`: the running app still shows the problem, so clean-looking source is not proof. An empty `repair.applied_at` counts as earlier than any `checked_at`. Plan a fix from `runtime.evidence` when it says what is still wrong; otherwise the outcome is `failed` with that evidence in `note`.
     - If `code_snippet` no longer matches because an earlier repair run or the user rewrote the construct, but a Check still holds, plan the fix against the current code and say in `reason` that the site changed.
     - If the snippet moved a few lines, record the new `line_number` for stage `3-apply`.
     - If the file is gone, the outcome is `skipped` with a note naming the missing file.
   - Classify each of its two fixes against the R2 boundary.
2. Choose the path for an agent-repairable finding:
   - Default to `recommended_fix`.
   - Use `minimal_fix` when the recommended fix crosses the R2 boundary and the minimal one does not, when the recommended fix would restructure a view the finding does not own, or when the user asked for the smallest change. Put the reason in `reason`, for example `minimal path: the recommended fix adds the new title "Watered"`.
   - When both fixes are identical, record `recommended`.
   - A fix value of `Color(red:green:blue:)` or a hex literal trips CLR-UI-001, and `.black` or `.white` for text or surfaces on a system or adaptive background trips CLR-UI-002. Take the other fix if it uses a semantic colour; otherwise treat the colour as a visual-design question. Fixed `.black` or `.white` text on a tinted or brand fill is allowed, as evenbetter-validate allows it, but only as an answer the person chose.
   - If the chosen fix calls a project symbol (a type, function, property, asset or string key) that the project does not declare, do not invent one. Try the other fix; if it has the same gap, the outcome is `failed` with the missing symbol in `note`. Declaring a read-only system environment value in the view (`@Environment(\.accessibilityReduceMotion)`, `\.dynamicTypeSize`, `\.colorScheme`, `\.colorSchemeContrast`, `\.accessibilityDifferentiateWithoutColor`) or a private `@State` or `@AccessibilityFocusState` property that only the fix uses is part of the fix, not a missing symbol.
3. Turn a human-decision finding into a closed question before deferring it:
   - Draw 2-4 concrete candidates from the surrounding code: visible strings in the same view, the naming pattern of sibling controls, the action's function name, the semantic colours the file already uses, and the two fixes themselves.
   - Mark one candidate as recommended. For a label, that is the visible text; for an icon-only control, the name the code gives the action (`deletePlant()` gives "Delete") or the usual meaning of the SF Symbol (`trash` is "Delete", `plus` is "Add", `xmark` is "Close"). For a colour on a fixed fill, it is the option that meets the report's contrast target in light and dark appearance. For behaviour or navigation, it is the option the clause's Correct code shows.
   - State the user impact in one sentence taken from the clause's Why block, so the person decides on impact rather than on syntax.
   - Gather the run's questions and ask them together where the tool allows, one question per finding or per site.
   - An answer turns the finding into an agent-repairable one with the chosen value. A declined question, or a run where nobody can answer (see Question tooling in SKILL.md), leaves it `deferred` with the candidates and the recommended one in `note`.
4. Build the edit sites' combined plans (below).
5. Record the triage decision for every finding before any edit is made, so stage `3-apply` does not re-decide classification mid-edit.

## Edit sites

Stage `1-load` grouped findings that target the same construct into sites. Plan one combined edit per site, because separate passes over one construct make later edits undo or duplicate earlier ones:

1. Start from the chosen fix that the edit centres on: the agent-repairable fix that restructures the construct, such as a `Button` conversion rather than a trait shim. When no fix in the site restructures it, or several do, take the highest-severity one.
2. Fold in what each other agent-repairable finding in the site needs, such as a trait, a label, a frame or a role, unless the combined shape already satisfies its clause Check. Leave out a shim that the combined shape makes redundant: `.accessibilityAddTraits(.isButton)` is not needed once the view is a `Button`, which satisfies A11Y-A11Y-001 and COMP-A11Y-002 on its own.
3. Keep every change that an already `applied` finding made at the site.
4. If part of the combined edit crosses the R2 boundary, split it. The mechanical part is applied; the rest goes through a question or is deferred, and the findings that need it stay `deferred`. When one finding's fix has both parts, say in its `reason` which part lands and which waits, for example `deferred: the 44x44 frame lands with the site edit; the label is product copy`.
5. Route every finding the combined edit closes to `apply` with the same `site`, and put the ID of the finding whose fix text the edit starts from in `base` on each of them.

## Triage record

Hold one record per finding:

```json
{
  "id": "EB-004",
  "site": "S3",
  "route": "apply | defer | skip | fail",
  "path": "minimal | recommended | \"\"",
  "base": "EB-002",
  "fix_text": "the exact code to apply at the site, after any value the user chose is substituted",
  "line_number": 0,
  "reason": "one short sentence",
  "question_asked": false
}
```

`base` is the finding whose fix text the site's combined edit starts from. It equals `id` for that finding, and is empty for findings that are not applied. Every finding the combined edit closes carries the same `fix_text`, the site's combined code, and the same `path`, the path of the base fix.

`reason` reaches the user and the report's `note`, so write it for a developer reading the report a week later: `deferred: the button label is product copy; offered "Delete" (recommended), "Delete plant", "Remove"`, not `needs input`.

## Stage exit criteria

Move to stage `3-apply` only when:

- Every queued finding has exactly one route.
- Every `apply` route has a `site`, a `base`, a non-empty `fix_text` and a `path` of `minimal` or `recommended`.
- Every `defer` route has a `reason` that names the class from the R2 boundary table and, when a question was possible, the candidates with one marked recommended.
- No route was chosen by guessing at a product decision. If you cannot tell whether a change is editorial, treat it as editorial and ask or defer.
