---
name: evenbetter-repair
description: Applies the remediations recorded in a validated EvenBetter audit report. Walks the findings in `.evenbetter/<project>/evenbetter-analyze-report.html` in severity order, edits the Swift and SwiftUI source for the technical ones using the report's `minimal_fix` or `recommended_fix`, and hands product, copy, navigation, and visual-design choices back to the human instead of guessing. Refuses to run against a report that `evenbetter-validate` has not stamped, so unvalidated findings never reach the codebase. Writes the outcome of every finding back into the same report so validation can be re-run afterwards. Use this skill whenever the user asks to repair, fix, remediate, resolve, action, apply, or clear the findings, issues, or violations from an EvenBetter analyze report, an `evenbetter-analyze-report.html`, or an accessibility/HIG audit — including phrasings like "fix the criticals", "apply the recommended fixes", or "work through the report".
---

# evenbetter-repair

## Operating model

This skill is the fourth EvenBetter interaction state and the third pass over the audit report. It turns a reviewed audit into source changes. The report stays the single source of truth: repair reads its findings, edits the project's Swift files, and writes the outcome of each finding back into the same HTML file.

- Repair is gated. The report must carry `workflow.state` of `validated` or `repaired`, and a `workflow.validated_at` stamp no older than `scan_date`. A report straight out of `evenbetter-analyze` is refused — its findings have not been re-checked against the live source, and applying them would push unverified edits into the codebase.
- Repair is corpus-grounded, not prompt-grounded. The report's `ai_fix_prompt` is a convenience for humans pasting into another agent. This skill applies `minimal_fix` or `recommended_fix` and checks the result against the clause's **Check** and **Correct code** blocks in `../../corpus/ios/<domain>.md`.
- Repair does not decide product questions. A finding whose remediation changes user-facing copy, navigation structure, product behaviour, or visual design is deferred to the human with a closed question or a written handoff. Technical conformance changes are applied.
- Repair does not discover findings. It never adds an issue to the report, never re-scans, and never adjusts a severity. Discovery belongs to `evenbetter-analyze`; correction of the findings themselves belongs to `evenbetter-validate`.
- Every finding ends the run with a recorded outcome — `applied`, `deferred`, `skipped`, or `failed` — written into its `repair` object. Nothing is left `pending` after a completed run.

Former slash-command names may be aliases. Interpret `/evenbetter-repair:3-apply` as "use `evenbetter-repair` with stage `3-apply`."

## Workflow position

The four EvenBetter interaction states are planning, analysis, validation, and repair. They are separate invocations against the same artifact:

| State | Skill | Reads | Writes |
| --- | --- | --- | --- |
| Planning | `evenbetter-ios-feature`, `evenbetter-ios-epic` | Product intent | Tickets and plans |
| Analysis | `evenbetter-analyze` | Swift sources, corpus | The report, `workflow.state = "analyzed"` |
| Validation | `evenbetter-validate` | The report, sources, corpus | The report, `workflow.state = "validated"` |
| Repair | `evenbetter-repair` | The report, sources, corpus | **Swift sources**, plus `workflow.state = "repaired"` |

Repair is the only state that edits application source code. That is why it is the only state with a precondition on another state's output.

After repair, re-running `evenbetter-validate` closes the loop: findings whose violation is genuinely gone are removed from the report, and any finding still matching its clause despite an `applied` repair is flipped to `failed` so the next repair run picks it up again.

## Question tooling

Repair asks more questions than analyze or validate, because deferring a product decision is a first-class outcome rather than a failure. Ask when a remediation changes what the user sees or how the app behaves, and when the report path or repair scope is ambiguous. Use the best available structured-question tool with mutually exclusive options:

- Claude Code: `AskUserQuestion` with 2-4 options.
- Codex Plan mode: `request_user_input` when available.
- Cursor or other agents with an ask-question tool: the native structured tool.
- Environments without structured questions: one closed question with numbered options.

Keep questions closed and multiple-choice. Never ask an open-ended "what would you like the label to say?" — offer concrete candidate strings drawn from the surrounding code and let the human pick or override. When no question tool is available at all, do not guess: record the finding as `deferred` with the options in its `note` and move on.

## Tool equivalents

The reference files mention Claude-style tool names. Apply these equivalents in Codex:

| Claude command instruction | Codex equivalent |
| --- | --- |
| `AskUserQuestion` | `request_user_input` in Plan mode when available, otherwise a concise closed question |
| `Glob`, `Grep`, `Read` | `rg --files`, `rg`, and shell file reads such as `sed` or `nl` |
| `Edit`, `Write` | `apply_patch` |
| `Bash` | `exec_command` |
| `WebSearch`, `WebFetch` | available web-search tooling, or official Apple documentation lookup |
| `TaskCreate`, `TaskUpdate` | `update_plan` |
| `ref_search_documentation`, `ref_read_url` | available official-doc tooling, otherwise direct fetch of Apple documentation URLs |

If current system or developer instructions conflict with a converted reference, follow the higher-priority instruction.

## Stage selection

Run the stages in order. Stage `1-load` is the gate — if it refuses, the run stops there and no source file is touched.

| Stage | Reference | Use when |
| --- | --- | --- |
| `1-load` | `references/1-load.md` | Locate the report, enforce the validation gate, and build the severity-ordered repair queue. |
| `2-triage` | `references/2-triage.md` | Split the queue into agent-repairable and human-decision findings, and choose the minimal or recommended path for each. |
| `3-apply` | `references/3-apply.md` | Edit the Swift sources for agent-repairable findings and verify each edit against its corpus clause. |
| `4-status` | `references/4-status.md` | Write every outcome back into the report, stamp `workflow`, and emit the handoff summary. |

## Repair gate

Stage `1-load` refuses the run in each of these cases. Refusal is a one-line message naming the cause and the command that fixes it — never a partial repair.

| Condition | Message |
| --- | --- |
| No report found under `.evenbetter/*/` | Run `evenbetter-analyze` first. There is nothing to repair. |
| `workflow` block missing entirely | The report predates the workflow contract. Run `evenbetter-validate` to stamp it. |
| `workflow.state` is `analyzed` | The report has not been validated. Run `evenbetter-validate` first. |
| `workflow.validated_at` is empty | Same as above — the stamp is the proof, not the state string alone. |
| `workflow.validated_at` is earlier than `scan_date` | Analyze re-ran after the last validation. Re-run `evenbetter-validate`. |
| `issues` is empty | Nothing to repair. Report the clean state and stop. |

Never "repair anyway" on user insistence by bypassing the gate. If the user wants to proceed, the correct move is to run `evenbetter-validate` for them — one extra invocation — and then repair.

## Decision model

Every finding ends in exactly one of four outcomes, recorded in its `repair.status`:

| Outcome | Trigger | `repair.owner` |
| --- | --- | --- |
| `applied` | A technical conformance change. The edit was made and verified against the clause's **Check**. | `agent` |
| `deferred` | The remediation is a product, copy, navigation, or visual-design choice, or the human declined to pick an option. The finding is unchanged in source. | `human` |
| `skipped` | Out of the scope the user asked for, or the violation is already absent from the current source. | `agent` |
| `failed` | The edit was attempted and could not be completed or verified — ambiguous target, the change did not close the violation, or the build broke and was reverted. | `agent` |

`deferred` is a success, not a shortfall. It is the guided handoff the report alone does not give: the human gets the finding, the two candidate fixes, and a closed question, instead of a prompt string they have to interpret.

## Path selection

Each finding carries two remediations. Choose one per finding:

- **`recommended_fix` is the default.** It is the system-native, Apple-blessed shape and it is structurally aligned with the clause's **Correct code** block.
- **`minimal_fix` when the recommended path exceeds the finding's blast radius.** Use it when the recommended fix would restructure a view the finding does not own, when it would touch a file outside the audited scope, or when the user asked for the smallest safe change.
- **Neither, when both are equivalent.** Validation sets them equal for structural violations. Apply the shared text and record `path` as `recommended`.

Record the chosen path in `repair.path`. When a finding is deferred or skipped, `repair.path` stays empty.

## Source-edit rules

- Edit only files inside `report.project_path`. Never edit the report's own directory as if it were source, and never edit a file the finding does not name.
- One finding, one edit site. If closing a violation requires touching a second file, and that file is not itself the subject of another finding, the outcome is `deferred` with the second file named in `note`.
- Preserve surrounding formatting: indentation width, brace style, and trailing commas as the file already uses them. A repair diff should read like the file's author wrote it.
- Never introduce identifiers the surrounding scope does not declare. If the recommended fix references a symbol that does not exist yet, the outcome is `failed` with the missing symbol in `note`.
- Never disable, delete, or comment out the offending code to make the finding go away. Removing a control is not a repair for an unlabeled control.
- Never apply `accessibilityHidden(true)` to anything a user can interact with, and never write an accessibility label that drops the visible text — the label must contain the visible string verbatim, per WCAG 2.5.3 Label in Name.
- Never hard-code `Color(red:green:blue:)` or a hex literal. Lift to a semantic asset colour or a system colour, as the clause's **Correct code** block does.
- Do not reformat, re-sort imports, or fix unrelated warnings in a file you happen to be editing. Repair diffs stay scoped to the findings.

## Artifact rules

- Only ever read and write `.evenbetter/<project-name>/evenbetter-analyze-report.html` as the audit artifact. Do not create sibling JSON, Markdown, or patch files, and do not create a second `.evenbetter/` folder.
- Preserve the `<script>` block surrounding `const reportData = …;`. Replace only the literal between `const reportData = ` and the next `};`, exactly as `evenbetter-validate` does.
- Do not delete findings. Repair records outcomes; removing a finding that is genuinely fixed is `evenbetter-validate`'s job on the next pass. `summary` counts therefore stay untouched.
- Write source edits and the report update in that order. If the report write fails after source edits landed, say so explicitly — the code is ahead of the ledger and the user needs to know.
- Surface the absolute report path as a `file://` link or copyable path, plus a one-line tally such as `Repaired 14: 9 applied, 3 deferred, 1 skipped, 1 failed`.

## Corpus rules

Treat `../../corpus/index.json` and `../../corpus/ios/*.md` as the authoritative rule layer. The corpus paths are identical to `evenbetter-analyze` and `evenbetter-validate` because repair runs from the same skill root:

- Read `../../corpus/index.json` once per run and group the queue by `clause_id`. Lazy-load `../../corpus/ios/<domain>.md` the first time a finding from that domain is repaired, and cache the parsed clause.
- The clause's **Correct code** block is the shape a repair should converge on. The clause's **Check** description is the acceptance test — after the edit, the **Check** condition must no longer hold at that site.
- The clause's **Why** block is the sentence to quote when deferring a finding to a human. It states the user impact, which is what a product owner needs in order to decide.
- A finding whose `clause_id` is missing from `../../corpus/index.json` is `skipped`, not repaired. The clause was removed or renamed, so there is no acceptance test. Note that re-running `evenbetter-validate` will drop the finding.

## iOS skill integration

- Use `evenbetter-swiftui-view-refactor` when a `recommended_fix` is a structural decomposition rather than a single modifier change, and keep the resulting extraction inside the finding's file.
- Use `evenbetter-swiftui-accessibility` clause bodies when an accessibility repair needs the full clause text to choose between labels, traits, and grouping.
- Use `evenbetter-swiftui-ui-patterns` references for the canonical SwiftUI shape of navigation, sheets, forms, controls, theming, and Dynamic Type repairs.
- Use `evenbetter-swiftui-liquid-glass` only when the repair touches iOS 26+ Liquid Glass APIs.
- Use `evenbetter-ios-debugger-agent` to capture a simulator screenshot when a visual repair (contrast, layout, large Dynamic Type) needs runtime confirmation that the fix landed.
- Use `evenbetter-design` when a deferred finding turns into a design decision the user wants help making, and return here once the decision is made.
