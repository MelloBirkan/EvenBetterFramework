# 2-evidence

Contents: Build the matrix, Mark n/a cells, Apply the findings, Apply the runtime verdicts, Add the other notes, Run the manual checks, Output of this stage.

Read `references/feature-criteria.md` and `references/feature-clause-map.md` before this stage. The evidence rules in SKILL.md decide every cell, and this stage applies them in order.

## Build the matrix

Make one matrix per device from `0-intake`:

- Rows are the tasks from `1-common-tasks` that exist on that device.
- Columns are the features Apple offers on that device, in Apple's order: VoiceOver, Voice Control, Larger Text, Dark Interface, Differentiate Without Color Alone, Sufficient Contrast, Reduced Motion, Captions, Audio Descriptions. Leave out Voice Control on Apple TV and Apple Watch, and Larger Text on Mac.
- Every cell starts as `untested`, with an empty list of notes.

A finding or verdict reaches a device when the device builds the finding's file. Shared code reaches every device. A file that only one target builds, or code behind `#if os(...)`, reaches only that device.

## Mark n/a cells

- Media answer "No video or audio": every Captions and Audio Descriptions cell is `n/a`.
- Media answer "Audio only": every Audio Descriptions cell is `n/a`. Captions cells follow the next rule.
- Media answer "Video": a Captions or Audio Descriptions cell is `n/a` when its task plays no media. A task plays media when one of its files plays video or audio, as `1-common-tasks` noted.
- On Apple Watch, an Audio Descriptions cell is `n/a` unless the watch app plays a video program's audio track, because Apple notes that watchOS apps don't play video.

No other cell is ever `n/a`. A task with no images still needs VoiceOver, and a task with no animation still gets a Reduced Motion check, because the person confirms that nothing moves.

## Apply the findings

Take each open finding from `0-intake` in report order:

1. **Tasks.** The finding reaches a task when its `file_path` is one of the task's files.
2. **Features.** It reaches a feature when its `clause_id` or one of its `related_clause_ids` maps to that feature in `references/feature-clause-map.md`. A finding whose clauses all map to "none" adds nothing.
3. **Severity `critical` or `high`**: each cell it reaches becomes `blocked`. Record the finding as a blocker: ID, clause, severity, the label from `0-intake` (unconfirmed, repair not validated, repair did not hold) and its runtime verdict.
4. **Severity `medium` or `low`**: each cell it reaches gets a note with the ID, clause, severity and the finding's title, such as "EB-027 (A11Y-UI-002, medium): Hide the decorative leaf illustration". The manual check asks the person to watch for it.

A `blocked` cell stays blocked. Later steps only add notes to it.

## Apply the runtime verdicts

Then take each open finding's `runtime.status`:

| Status | Effect on each cell the finding reaches |
| --- | --- |
| `confirmed` | `blocked`, whatever the severity. Note "confirmed at runtime" with the configurations and the evidence. |
| `refuted` | Note "refuted at runtime" with the evidence. A refuted `critical` or `high` finding still blocks, because only evenbetter-validate removes a finding. |
| `inconclusive` | Note "inconclusive at runtime" with the evidence. |
| `not_testable` | Note "no runtime check, manual check only". |
| `untested` | Nothing. If one of the finding's clauses has a row in the Audit types or VoiceOver walk checks table of `../evenbetter-accessibility-tests/references/audit-clause-map.md`, add the finding to the "Run the evenbetter-accessibility-tests skill" next step. |

A `confirmed` verdict blocks the cells on every device that builds the file, because the code is the same.

## Add the other notes

These never change a cell's state:

- **Leads** from the tests log. A lead reaches the tasks whose screen it names (the screen is the view's name without `View`, so `PlantDetail` is `PlantDetailView.swift`). It reaches the features its "Map suggests" clauses map to.
- **Xcode accessibility specialists.** Xcode 27 ships Apple-built specialists, including accessibility ones. When the person shares their results in the conversation, a failing result on a task's file blocks the cell it reaches, labelled "unconfirmed" and cited as "Xcode specialist: [file]". A passing result is a note.
- **Code signals** from the feature's section of `references/feature-criteria.md`, found in the task's files. Each one is a note, and the log lists it under Open questions with a suggestion to run evenbetter-analyze.
- **Route gaps** from `1-common-tasks`: note "route gap: the screen may be unreachable" on every cell of the task.

## Run the manual checks

A cell passes only when a person completes the task with the feature on. For each device, and each feature in Apple's order:

- **A blocked cell in the column**: don't ask. The feature cannot be declared until the blockers are fixed, so a check now would waste a device session. Note "not asked: blocked by [IDs]" on the column's untested cells.
- **Every cell `n/a`**: nothing to ask.
- **Otherwise**: ask one question for that feature on that device.

Ask at most three questions at a time, closed, with the recommended option first. Each question names the feature and device, gives the feature's "Turn it on" and "Manual check" lines from `references/feature-criteria.md`, lists the tasks to complete, and lists the notes to watch for. For VoiceOver and Voice Control, say that a physical device is needed, because Apple says they aren't available in Simulator.

"[Feature] on [device]: with [setting] on, can you complete every task below? [tasks] Watch for: [notes]" Not tested yet (Recommended) / Completed every task with [feature] alone / Got stuck on at least one task.

- **Not tested yet**: the cells stay `untested`, and the feature goes to Pending checks. This is the recommended answer because only a real run can pass a cell, and it is the answer a session that cannot ask takes.
- **Completed every task**: each `untested` cell in the column becomes `pass`, with the note "manual check [date]". Cells already `n/a` stay `n/a`.
- **Got stuck**: ask which tasks, as a multi-select or a numbered list, and at which step. Then ask for evidence: Attach a screenshot or screen recording (Recommended) / Describe the step in words only. Read an attached screenshot to confirm what it shows. Each task named becomes `blocked`, with the note "manual check: [step]" and the evidence file or "described in words". The other cells stay `untested` with the note "not confirmed after the stuck task", because one blocked cell already decides the feature.

Answers count only for the device they name. An iPad answer needs a run on an iPad, even when the iPad build shares the iPhone code.

## Output of this stage

- One matrix per device, each cell with its state and notes.
- The blockers: finding ID, clause, severity, label, runtime verdict, and the features, tasks and devices it blocks. Manual blockers carry the task, the step and the evidence.
- The pending checks: device, feature, tasks, and how to test.
- The findings for the accessibility-tests next step.
- Code signals, for Open questions.
