# 3 Apply

## Role

Make the source edits for every finding routed to `apply`, and verify each one against its corpus clause before moving to the next. This is the only EvenBetter stage that writes application code.

## Process

1. Walk the queue in the order stage `1-load` built: severity descending, grouped by file, and within a file by descending line number. Bottom-up within a file means an applied edit never shifts the line numbers of the findings still queued behind it.
2. For each file, read the whole file once before the first edit in it. Editing from a 40-line window loses the context that decides whether a fix is correct — the enclosing view, the existing modifiers, the file's formatting conventions.
3. For each `apply` finding in that file:
   - Locate the exact edit site by matching `code_snippet` in the file, not by trusting `line_number` alone. If the snippet appears more than once in the file, disambiguate with the surrounding lines the report captured. If it still cannot be pinned to one site, the outcome is `failed` with `note` of `ambiguous edit site — snippet matches N locations`.
   - Apply the triage record's `fix_text`, adapted to the file's formatting: the file's indentation width, its brace and modifier-chain style, its trailing-comma habit. A repair diff should read like the file's author wrote it.
   - Keep the edit minimal. Change the lines the violation lives on. Do not reformat neighbours, re-sort imports, rename unrelated symbols, or clear unrelated warnings in a file you happen to have open.
4. Verify the edit immediately, before starting the next one. See **Verification** below.
5. Record the outcome and the changed file path in the triage record, then move on.

## Verification

Every applied edit gets all four checks. The first failure decides the outcome.

1. **Clause check.** Re-read the edited region and evaluate the clause's **Check** condition against it. The condition must no longer hold. An edit that changes the code without closing the violation is `failed`, not `applied`.
2. **Shape check.** Compare the result with the clause's **Correct code** block. A `recommended` repair should be structurally the same shape; a `minimal` repair need only close the violation. If a `recommended` repair drifted into a different shape, either bring it back to the clause's shape or record the path as `minimal`.
3. **Scope check.** Confirm the edit touched only the finding's own file and only within the finding's construct. If the change leaked into a sibling view or a shared component, revert it and record `failed` with `note` naming what it would have touched.
4. **Compile check, where a build is available.** Prefer the project's own build command. Run it once per file after that file's findings are all applied, not once per finding — a SwiftUI build is too slow to run per edit.
   - If the build succeeds, the file's findings stay `applied`.
   - If the build fails and the failure is attributable to one edit, revert that edit, mark it `failed` with the compiler message's first line in `note`, and re-run the build.
   - If the build fails and the cause cannot be attributed, revert every edit made to that file in this run and mark them all `failed` with a shared `note`. A half-repaired file is worse than an unrepaired one.
   - If no build command is available, say so once in the final summary rather than per finding. The edits stay `applied` on the strength of checks 1-3.

Never delete, comment out, disable, or `#if`-guard code to make a check pass. Removing the offending control is not a repair.

## Repair-specific rules by class

- **Accessibility labels.** The label must contain the visible text verbatim, with extra context appended rather than substituted, per WCAG 2.5.3 Label in Name. `Label("Delete", systemImage: "trash")` becomes an accessible name containing `Delete`, never a paraphrase like `Remove item`.
- **Decorative images.** `.accessibilityHidden(true)` is correct only for imagery carrying no information and no interaction. If the element is inside a tappable region, or is the only content of a control, it is never hidden — it is labelled.
- **Grouping.** When a composite is already fully labelled by its children, prefer `.accessibilityElement(children: .combine)` on the container over adding a synthetic parent label that duplicates the children's text.
- **Colour substitutions.** Replace a literal with the semantic system colour the clause names. When the clause names a role rather than a specific colour, and more than one system colour fits, that is a design decision — it should already have been deferred in triage.
- **Structural migrations.** `NavigationView` to `NavigationStack`, `actionSheet` to `confirmationDialog`, and similar replacements change call-site shape. Migrate the whole construct including its modifiers, not just the type name, and confirm the enclosing view still compiles against the new container's requirements.
- **Hit targets.** Grow the target with the documented minimum from the clause, applied via `.frame(minWidth:minHeight:)` or `.contentShape` as the **Correct code** block shows. Do not scale the visual content to reach the number.
- **View decomposition.** When a `recommended_fix` is a structural extraction, use `evenbetter-swiftui-view-refactor` heuristics and keep the extracted view in the same file. An extraction that wants its own file is beyond a repair's blast radius — defer it.

## Interruption and partial runs

A repair run may stop early — a build hangs, the user interrupts, a question goes unanswered. That is expected and safe, because the queue is ordered by severity and applied bottom-up per file.

- Findings already applied and verified stay applied. Do not roll back completed work because a later finding failed.
- Findings not reached keep their previous status. They are `pending` for the next run.
- Always proceed to stage `4-status` even after an interruption, so the report records what actually happened. A run that edits source and never writes the ledger leaves the code ahead of the report.

## Output of this stage

For every finding routed to `apply`, an updated triage record carrying:

- `route` resolved to `applied` or `failed`.
- `changed_files` — the project-relative paths actually written, usually one.
- `note` — empty on success; on failure, the check that failed and its evidence in one sentence.
- `applied_at` — current local time as `YYYY-MM-DD HH:MM:SS`, set only on success.
