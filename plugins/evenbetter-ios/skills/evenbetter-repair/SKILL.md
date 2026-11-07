---
name: evenbetter-repair
description: >-
  Applies the fixes from a validated EvenBetter audit report to the project's Swift code, most severe first, and records each outcome in the report. Product, copy and design choices go back to the user as closed questions. Use when asked to repair, fix or apply an EvenBetter report's findings, such as "fix the criticals". To re-check findings without editing code, use evenbetter-validate.
---

# evenbetter-repair

> Paths in this skill and its references are relative to this SKILL.md's folder. The plugin corpus is at `../../corpus/`.

Paths inside the user's project, such as a finding's `file_path` and the `.evenbetter/` folder, resolve against the project root.

## Operating model

This skill is the fourth EvenBetter interaction state and the third pass over the audit report. It turns a validated report into source edits. The report stays the single source of truth: repair reads its findings, edits the project's Swift files, and writes each finding's outcome back into the same HTML file.

- Repair needs a validated report: `workflow.state` of `validated` or `repaired`, with a `workflow.validated_at` no earlier than `scan_date`. Stage `1-load` refuses anything else, because unvalidated findings have not been re-checked against the live source.
- Repair is grounded in the corpus. It applies `minimal_fix` or `recommended_fix` and checks the result against the Check and Correct code blocks of the finding's `clause_id` and of every ID in its `related_clause_ids`. The `ai_fix_prompt` is for people who paste it into another agent; this skill does not follow it.
- Repair does not make product decisions. A fix that changes user-facing copy, navigation, product behaviour or visual design goes to the user as a closed question, or is deferred with a written handoff. Technical conformance changes are applied.
- Repair does not discover or re-judge findings. It never adds a finding, re-scans, changes a severity or writes a finding's `runtime` block. Discovery belongs to evenbetter-analyze, corrections to evenbetter-validate, and runtime verdicts to evenbetter-accessibility-tests.
- Every finding ends a completed run with an outcome (`applied`, `deferred`, `skipped` or `failed`) in its `repair` object. Only a run that stopped early leaves findings `pending`.

A stage name given as the argument (for example `3-apply`) selects that stage. Stages `1-load` and `2-triage` still run first, because the gate and the triage records come from them.

## Workflow position

The four EvenBetter interaction states are planning, analysis, validation and repair. Each is a separate invocation against the same artifact:

| State | Skill | Reads | Writes |
| --- | --- | --- | --- |
| Planning | evenbetter-ios-feature, evenbetter-ios-epic | Product intent | Tickets and plans |
| Analysis | evenbetter-analyze | Swift sources, corpus | The report, `workflow.state = "analyzed"` |
| Validation | evenbetter-validate | The report, sources, corpus | The report, `workflow.state = "validated"` |
| Repair | evenbetter-repair | The report, sources, corpus | Swift sources, plus `workflow.state = "repaired"` |

Repair is the only state that edits application source, so it is the only one gated on another state's stamp. Running evenbetter-validate after a repair closes the loop: it removes findings whose violation is gone, and flips any `applied` finding that still matches its clause to `failed`, so the next repair run picks it up. Running evenbetter-accessibility-tests with `recheck` between the two adds runtime evidence: validation also flips an `applied` finding that the tests confirmed in the running app after the repair.

## Stage selection

Run the stages in order. If stage `1-load` refuses, the run stops there and no source file is touched.

| Stage | Reference | Use when |
| --- | --- | --- |
| `1-load` | `references/1-load.md` | Locate the report, enforce the validation gate, check its structure, and build the queue of edit sites. |
| `2-triage` | `references/2-triage.md` | Split the queue into agent-repairable and human-decision findings, combine findings that share a construct, and choose the fix path. |
| `3-apply` | `references/3-apply.md` | Edit the Swift sources and verify each edit against its corpus clauses. |
| `4-status` | `references/4-status.md` | Write every outcome back into the report, stamp `workflow`, and give the handoff summary. |

## Report helper

The plugin ships `../../scripts/evenbetter_report.py` (Python 3, standard library only). Resolve that path against this SKILL.md's folder to an absolute path, written `[script]` below, because commands run from the project root:

- `python3 [script] extract REPORT.html` prints the embedded report data as JSON.
- `python3 [script] check REPORT.html|DATA.json [--state analyzed|validated|repaired]` checks the report contract and exits 1 with one line per problem. Without `--state` it checks the report's own state.
- `python3 [script] update DATA.json REPORT.html --state STATE` checks the data, then replaces only the embedded data in the existing report. Every other byte of the file stays as it was.

The helper's `render` command belongs to evenbetter-analyze: it moves the existing report into `history/` and writes a fresh page, so repair does not use it. Use the helper whenever `python3` runs. Without it, stages `1-load` and `4-status` describe the by-hand extract, check and splice.

## Decision model

Every finding ends in exactly one outcome, recorded in `repair.status`:

| Outcome | Trigger | `repair.owner` |
| --- | --- | --- |
| `applied` | A technical conformance change was made and verified against the clause Checks. This includes a finding closed by an edit made for another finding at the same site. | `agent` |
| `deferred` | The fix is a product, copy, navigation or visual-design choice, or the user declined to pick an option. The source is unchanged for it, or only the mechanical part of a combined edit landed, as its `note` says. | `human` |
| `skipped` | Out of the scope the user asked for, the violation is already absent from the current source, or its file is gone. | `agent` |
| `failed` | The edit was attempted and could not be completed or verified: an ambiguous site, a violation that stayed, or a build break that was reverted. | `agent` |

A deferral is a good result. The user gets the finding, the candidate fixes and a closed question with a recommended answer, which is more than the report alone gives them.

## Path selection

- `recommended_fix` is the default. It is the system-native shape and follows the clause's Correct code.
- Use `minimal_fix` when the recommended fix crosses the human-decision boundary in `references/2-triage.md` and the minimal one does not (new copy, a confirmation step, a changed animation or look), when it would restructure a view the finding does not own, or when the user asked for the smallest change. Say why in `repair.note`.
- When both fixes are identical, apply the shared text and record `recommended`.
- When both cross the boundary, ask, or defer.

Record the chosen path in `repair.path`. It stays empty for deferred and skipped findings.

## Source-edit rules

- Edit only files inside the project root (`report.project_path`, or the current root when stage `1-load` falls back to it), and only the files a fix names: the finding's `file_path`, plus any file a `// File: [path]` line in the fix names.
- Findings that target the same construct get one combined edit, recorded on each finding it closes with the same `changed_files`.
- Re-read the file before every edit. An applied fix, from this run or an earlier one, is never undone by a later edit.
- Reference only symbols the project or the SDK already declares. Declaring a read-only system environment value in the view, such as `@Environment(\.accessibilityReduceMotion)`, `\.dynamicTypeSize` or `\.colorScheme`, or a private `@State` that only the fix uses, is part of a fix.
- Do not delete, comment out, disable, `#if`-guard or hide the offending code to make a finding go away. Removing a control does not repair it.
- An accessibility label contains the visible text verbatim ([WCAG 2.2 2.5.3 Label in Name](https://www.w3.org/TR/WCAG22/#label-in-name)), and nothing a user can interact with gets `.accessibilityHidden(true)`.
- Colour fixes use semantic colours (`.primary`, `.secondary`, or UIColor-backed ones such as `Color(uiColor: .systemBackground)`). A fix value of `Color(red:green:blue:)` or a hex literal trips CLR-UI-001, and `.black` or `.white` for text or surfaces on a system or adaptive background trips CLR-UI-002, so neither is applied. Fixed `.black` or `.white` text on a fill that does not follow the system background, such as a tinted button, is a design question that `references/2-triage.md` turns into a closed question.
- Keep the file's indentation, brace style and modifier layout. Do not reformat, re-sort imports, rename unrelated symbols or fix unrelated warnings.

## Artifact rules

- The audit artifact is `.evenbetter/[project]/evenbetter-analyze-report.html`, edited in place. Leave `.evenbetter/[project]/history/` alone, and create no sibling JSON, Markdown or patch files in the project. The helper's temporary DATA.json goes outside the project and the plugin folder and is deleted after `update`.
- Do not delete findings or recompute `summary`. Removing fixed findings is evenbetter-validate's job on the next pass.
- Source edits land first, then the report. If the report write fails after source edits landed, say so plainly: the code is ahead of the ledger.
- Give the absolute report path as a `file://` link or copyable path, plus a one-line tally such as `Repaired 14: 9 applied, 3 deferred, 1 skipped, 1 failed`.

## Corpus rules

- Read `../../corpus/index.json` once per run. Its `file_path` values are relative to the plugin root, so `corpus/ios/accessibility.md` is `../../corpus/ios/accessibility.md` from here. Load each domain file the first time a queued clause needs it, and cache the parsed clauses.
- The Correct code block is the shape a repair converges on. The Check is the acceptance test, for the primary clause and every related clause. The Why block is the sentence to quote when deferring, because it states the user impact.
- Read Checks for intent: a control built from `Image` plus `.onTapGesture` counts as a button for button clauses.

## iOS skill integration

- Use evenbetter-swiftui-view-refactor when a `recommended_fix` is a structural decomposition, and keep the extraction inside the finding's file.
- Use evenbetter-swiftui-accessibility clause bodies when an accessibility repair needs the full clause text to choose between labels, traits and grouping.
- Use evenbetter-swiftui-ui-patterns references for the SwiftUI shape of navigation, sheets, forms, controls, theming and Dynamic Type repairs.
- Use evenbetter-swiftui-liquid-glass only when the repair touches iOS 26+ Liquid Glass APIs.
- Runtime confirmation of applied repairs comes from evenbetter-accessibility-tests, run with `recheck` after this skill and before evenbetter-validate. It re-runs the tests that carry an applied finding.
- Use evenbetter-ios-debugger-agent for a simulator screenshot of a state those tests do not cover, such as a layout at a large text size. It builds and runs the app through Xcode's MCP server first and falls back to MobileBuildMCP.
- Use evenbetter-design when a deferred finding turns into a design decision the user wants help with, then return here once it is made.

## Question tooling

Repair asks more often than analyze or validate, because deferring a product decision is a normal outcome. Ask when a fix changes what the user sees or how the app behaves, and when the report path or the repair scope is unclear.

Ask with the host's structured question tool when it has one:

- Claude Code: `AskUserQuestion`, with 2-4 mutually exclusive options per question.
- Codex in Plan mode: `request_user_input`, with 1-3 short questions of 2-3 options each, the recommended option first and marked "(Recommended)". The client adds "Other". Plan mode is read-only, so present results in a `<proposed_plan>` block and ask the user to switch to Default mode before writing `.evenbetter/` files or editing code.
- Codex in Default mode: ask one concise closed question with numbered options in plain text, then wait. Use `request_user_input` instead if the session offers it.
- Other agents: use their structured question tool, or ask one closed question with numbered options.
- When nobody can answer, because the user said they will not be around or asked you to go ahead without questions, or because the run is one-shot and non-interactive (such as `claude -p`, `codex exec`, CI or a scheduled task), do not end the turn on a clarifying question. Take the recommended option, say which one you took, and record it as an assumption in the artifact or the final reply. Never assume an approval the user has not given, such as accepting a plan or starting to edit code: finish the current stage and end with what waits on the person. Any exception this skill names elsewhere still applies.

Because Plan mode cannot write, repair runs only `1-load` and `2-triage` there.

Offer concrete candidates drawn from the code and mark one as recommended. For a label, recommend the visible text; for an icon-only control, the name the code gives the action or the usual meaning of the SF Symbol (`trash` is "Delete", `plus` is "Add", `xmark` is "Close"). When nobody can answer, record the finding as `deferred` with the candidates and the recommended one in `note`, and move on. This is the exception to taking the recommended option, because a guessed label or colour would ship as if the person had chosen it.

## Tool equivalents

The references use Claude Code tool names. In Codex, use these equivalents, and do not simulate a tool the session does not have:

| Claude Code | Codex |
| --- | --- |
| `AskUserQuestion` | `request_user_input` (Plan mode, or Default mode when enabled); otherwise a closed plain-text question |
| `Glob`, `Grep`, `Read` | `rg --files`, `rg`, and shell reads such as `sed -n` or `nl` through `exec_command` |
| `Read` on an image or screenshot | `view_image` |
| `Edit`, `Write` | `apply_patch` (Default mode only) |
| `Bash` | `exec_command` |
| `TaskCreate`, `TaskUpdate` | `update_plan` (Default mode only; in Plan mode keep the steps in `<proposed_plan>`) |
| `WebSearch`, `WebFetch` | `web_search`, or a configured MCP search or fetch tool such as Firecrawl, Tavily or Exa; `curl` through `exec_command` where network access is allowed |

If current system, developer or user instructions conflict with this skill, follow them.
