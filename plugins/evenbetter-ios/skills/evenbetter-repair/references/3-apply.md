# 3 Apply

Contents: Role, Process, Verification, Repair rules by class, Interruption and partial runs, Output of this stage.

## Role

Make the source edits for every site routed to `apply`, and verify each edit against its corpus clauses before moving to the next. This is the only EvenBetter stage that writes application code. The source-edit rules in SKILL.md apply to every edit here.

## Process

1. Walk the sites in the order stage `1-load` built.
2. Re-read the file from disk before every edit: the whole file before the first edit in it, and at least the enclosing view before each later one. Earlier edits in this run, an earlier repair run or the user may have changed it, and editing from a stale copy is how a later fix undoes an earlier one.
3. Locate the site by matching `code_snippet` in the current file, not by trusting `line_number` alone.
   - If the snippet matches more than once, disambiguate with `line_number` and the surrounding lines. If it still cannot be pinned to one place, the outcome is `failed` with note `ambiguous edit site: snippet matches N locations`.
   - If the snippet matches nowhere because an earlier edit rewrote the construct, find the construct by intent (the same control in the same view). When its clause Checks no longer hold, the earlier edit already closed the finding: record `applied` with that edit's `changed_files` and a note naming the finding it was made for, or `skipped` with `already satisfied in source` when the edit came from an earlier run or the user, unless the finding has a `confirmed` runtime verdict later than its `repair.applied_at`, which stage `2-triage` already planned for. When a Check still holds, apply only what this site still needs on top of the current code.
4. Apply the site's `fix_text`:
   - Fixes replace the lines of `code_snippet` whole. Replace exactly those lines.
   - A fix whose parts start with `// File: [path]` lines touches each named file. Apply each part to its own file, at the site the part and the finding's `ai_fix_prompt` describe, and leave the `// File:` lines out of the source. Comment lines that only say where code goes (`// Add to PlantDetailView: ...`) are directions too: follow them and leave them out.
   - Match the file's indentation width, brace and modifier-chain style and trailing-comma habit, so the diff reads as if the file's author wrote it.
   - Change only the lines the violation lives on, plus any property declaration the fix adds to the same view, placed with the view's other properties.
5. Keep every earlier fix. If the fix text carries an older version of lines that an applied edit already changed, for example a `.frame(width: 28, height: 28)` that a hit-target fix grew to 44 by 44, keep the applied lines and add only what this site needs.
6. Verify the edit immediately (below), before starting the next site.
7. Record the outcome and the changed files on every finding of the site, then move on.

## Verification

Every applied edit gets these checks. The first failure decides the outcome.

1. Clause check. Re-read the edited region and evaluate the Check of the primary clause and of every related clause, for every finding the edit claims to close, reading each Check for intent. None may still hold. An edit that changes the code without closing a violation is `failed` for that finding, not `applied`.
2. No new violation. The edited lines must not trip a corpus clause they did not trip before. A construct the repair creates follows the clauses for that construct: a new `Button` whose action deletes gets `role: .destructive` (COMP-UX-001) unless it is the confirming button of an alert raised by the person's own Delete tap, a control keeps any accessibility label it had, and a hit area never shrinks below 44 by 44 points (LAY-UI-001). Make the change within the edit when the clause names it; otherwise revert and record `failed` with the clause in `note`.
3. Shape check. Compare the result with each clause's Correct code block. An equivalent form passes: dropping `.foregroundColor(.black)` so the text takes its default primary style matches `.foregroundStyle(.primary)`. Do not add code only to mirror the Correct code literally. If a `recommended` repair drifted into another shape, bring it back to the clause's shape or record the path as `minimal`.
4. Scope check. Confirm the edit touched only the files the fix names and only the site's construct, plus the declarations the fix adds to the same view. If it leaked into a sibling view or a shared component, revert it and record `failed` with a note naming what it would have touched.
5. Compile check, where a build is available. Prefer the project's own build command, and run it once per file after that file's sites are all applied, because a SwiftUI build is too slow to run per edit.
   - If the build succeeds, the file's findings stay `applied`.
   - If it fails and the failure points to one edit, revert that edit, mark its findings `failed` with the compiler message's first line in `note`, and build again.
   - If it fails and the cause cannot be pinned to one edit, revert every edit this run made to that file and mark those findings `failed` with a shared `note`. A half-repaired file is worse than an unrepaired one.
   - If no build command is available, say so once in the final summary rather than per finding. The edits stay `applied` on the strength of checks 1-4.

## Repair rules by class

- Accessibility labels. The label contains the visible text verbatim, with any extra context appended, per [WCAG 2.2 2.5.3 Label in Name](https://www.w3.org/TR/WCAG22/#label-in-name). `Label("Delete", systemImage: "trash")` keeps an accessible name containing `Delete`, never a paraphrase like `Remove item`. A label for an icon-only control comes from the question in stage `2-triage`.
- Decorative images. `.accessibilityHidden(true)` fits only imagery with no information and no interaction. An image inside a tappable region, or the only content of a control, is labelled rather than hidden.
- Grouping. When a composite is already labelled by its children, prefer `.accessibilityElement(children: .combine)` on the container over a parent label that repeats their text.
- Buttons. Converting a tappable view to a `Button` keeps its look: add `.buttonStyle(.plain)` unless the fix sets a style, because the plain style leaves the label undecorated while idle and the default style tints it. A `Button` whose action deletes carries `role: .destructive` (COMP-UX-001). The one exception is the confirming button of an alert that follows a destructive action the person chose on purpose; buttons in confirmation dialogs and action sheets keep the role. The `Button` supplies the button trait, so no `.accessibilityAddTraits(.isButton)` shim is needed.
- Colours. `.black` or `.white` text on a system background becomes `.primary`, as CLR-UI-002's Correct code shows, or `.secondary` when the text is already styled as secondary. Surfaces take UIColor-backed semantic colours such as `Color(uiColor: .systemBackground)`. When several roles fit, or the text sits on a fixed or brand fill, the colour is a design decision that stage `2-triage` turns into a question.
- Typography. Replace a fixed size with the text style the chosen fix names. When it names none, use the style whose default size at the Large setting is nearest: `.largeTitle` 34 pt, `.title` 28, `.title2` 22, `.title3` 20, `.headline` 17 semibold, `.body` 17, `.callout` 16, `.subheadline` 15, `.footnote` 13, `.caption` 12, `.caption2` 11. A size under 11 points takes `.caption2`. At 17 points, semibold or bold text takes `.headline` and other text `.body`. When a size sits halfway between two styles, take the larger one, so the text does not shrink. Choosing a style that changes the hierarchy is a design decision.
- Environment values. Declare the value the fix reads in the view, for example `@Environment(\.accessibilityReduceMotion) private var reduceMotion`, then switch the motion off with it, as A11Y-UX-001's Correct code does (`withAnimation(reduceMotion ? nil : .spring())`). Replacing the animation with a different one is a behaviour change.
- Structural migrations. `NavigationView` to `NavigationStack`, `actionSheet` to `confirmationDialog`, and similar replacements change the call site's shape. Migrate the whole construct with its modifiers, and confirm the enclosing view still compiles against the new container.
- Hit targets. Grow the target to the clause's minimum with `.frame(minWidth:minHeight:)` or `.frame(width:height:)` plus `.contentShape(Rectangle())`, as the Correct code block shows. Do not scale the visible content to reach the number.
- View decomposition. When a `recommended_fix` is a structural extraction, use the evenbetter-swiftui-view-refactor heuristics and keep the extracted view in the same file. An extraction that wants its own file is beyond a repair, so defer it.

When an applied edit makes code reachable or visible for the first time, for example a new `.navigationDestination` that opens a screen whose findings are still deferred, record that for the handoff in stage `4-status`.

## Interruption and partial runs

A run can stop early: a build hangs, the user interrupts, a question goes unanswered. That is safe, because the queue runs most severe first and every edit is verified before the next.

- Findings already applied and verified stay applied. Do not roll back completed work because a later site failed.
- Findings not reached keep their previous status, so they are `pending` for the next run.
- Always continue to stage `4-status`, even after an interruption, so the report records what happened. A run that edits source and never writes the ledger leaves the code ahead of the report.

## Output of this stage

For every finding routed to `apply`, an updated triage record carrying:

- `route` resolved to `applied` or `failed`.
- `changed_files`: the project-relative paths written for the site, usually one. Every finding a combined edit closes gets the same list.
- `note`: empty for a plain applied edit. Otherwise one sentence, such as `closed by the combined edit for EB-019 (Button conversion)`, `minimal path: the recommended fix adds the new title "Watered"`, or, on failure, the check that failed and its evidence.
- `applied_at`: the current local time as `YYYY-MM-DD HH:MM:SS`, set only on success and shared by every finding of the site.
- `exposes`: the IDs of deferred or failed findings the edit made reachable or visible, if any.
