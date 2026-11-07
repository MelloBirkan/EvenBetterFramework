---
name: evenbetter-validate
description: >-
  Re-checks an evenbetter-analyze HTML report against current source, the EvenBetter corpus and Apple's docs, then
  edits it in place: drops false positives, merges duplicates, corrects severities and fixes, and stamps it validated
  so evenbetter-repair can run. Use when asked to validate, verify or double-check an EvenBetter report. To scan for
  new issues, use evenbetter-analyze.
---

# evenbetter-validate

> Paths in this skill and its references are relative to this SKILL.md's folder. The plugin corpus is at `../../corpus/`.

## Operating model

This skill is the second pass after evenbetter-analyze. It loads the existing HTML report, re-checks every finding against the live source code, the EvenBetter iOS corpus and Apple's documentation, and writes its corrections back into the same file. The HTML stays the single source of truth; there are no separate JSON or Markdown deliverables.

- Every finding names a primary corpus clause in `clause_id` and the other clauses its fix closes in `related_clause_ids`. Each clause is an H2 block in `../../corpus/ios/[domain].md` with a **Check**, a **Why**, a **Correct code** example, and its `Severity` and `Source`. Validate against those clause bodies, not only the captured snippet.
- A Check is read for its intent: it describes the common form of the violation. A control built as `Image` plus `.onTapGesture` counts as a button for button-specific clauses.
- Fixes are reviewed for correctness, not style. They must be complete replacements for `code_snippet` that close every clause on the finding.
- The report is rewritten in place. Only the embedded data changes; the rest of the HTML stays byte-identical.
- Every pass stamps `workflow.state = "validated"` with the current `validated_at`. evenbetter-repair checks that stamp before it touches source code, so it is written even on a clean pass.

A stage name given as the argument (for example `2-validate`) selects that stage.

## Workflow position

Validation is the third of four EvenBetter interaction states: planning, analysis, validation, repair. It sits between the audit and the code changes and is the only thing that authorizes them.

- evenbetter-analyze runs before, writing `workflow.state = "analyzed"`.
- This skill promotes the report to `workflow.state = "validated"` and stamps `workflow.validated_at`.
- evenbetter-repair runs after. It refuses a report whose state is still `analyzed`, or whose `validated_at` is older than `scan_date`, so an unvalidated finding never reaches the codebase.

Validation also closes the loop. Run again after a repair pass, it removes findings whose violation is gone, and marks a finding that a repair claimed to fix but did not as `failed` so the next repair run picks it up. A finding that evenbetter-accessibility-tests confirmed in the running app after the last repair counts as not fixed. See the repair re-check in `references/2-validate.md`.

## Question tooling

Validation rarely needs questions. Ask only when the report path is ambiguous (several `.evenbetter/*/evenbetter-analyze-report.html` files for sibling sub-projects) or when the user scoped validation to a subset (severities, file globs, clause IDs) and the scope is unclear. Otherwise validate every finding in the report without asking. Questions are closed, with mutually exclusive options and the recommended option first.

Ask with the host's structured question tool when it has one:

- Claude Code: `AskUserQuestion`, with 2-4 mutually exclusive options per question.
- Codex in Plan mode: `request_user_input`, with 1-3 short questions of 2-3 options each, the recommended option first and marked "(Recommended)". The client adds "Other". Plan mode is read-only, so present results in a `<proposed_plan>` block and ask the user to switch to Default mode before writing `.evenbetter/` files or editing code.
- Codex in Default mode: ask one concise closed question with numbered options in plain text, then wait. Use `request_user_input` instead if the session offers it.
- Other agents: use their structured question tool, or ask one closed question with numbered options.
- When nobody can answer, because the user said they will not be around or asked you to go ahead without questions, or because the run is one-shot and non-interactive (such as `claude -p`, `codex exec`, CI or a scheduled task), do not end the turn on a clarifying question. Take the recommended option, say which one you took, and record it as an assumption in the artifact or the final reply. Never assume an approval the user has not given, such as accepting a plan or starting to edit code: finish the current stage and end with what waits on the person. Any exception this skill names elsewhere still applies.

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
| `ref_search_documentation`, `ref_read_url` | any documentation MCP the session has; otherwise official Apple pages through the web tools above |

Apple pages are rendered with JavaScript; a plain fetch can return a "requires JavaScript" shell. Prefer a scraper MCP that renders pages (Firecrawl, Tavily extract, Exa fetch) or Apple's JSON form: `https://developer.apple.com/tutorials/data/documentation/[path].json` for API docs and `https://developer.apple.com/tutorials/data/design/human-interface-guidelines/[page].json` for HIG pages.

If current system, developer or user instructions conflict with this skill, follow them.

## Stage selection

Run the stages in order. Stage 3 always runs, because even a clean pass has to write the workflow stamp, but it rewrites findings only when stage 2 changed something.

| Stage | Reference | Use when |
| --- | --- | --- |
| `1-load` | `references/1-load.md` | Find the report, extract its data, and list the contract problems it already has. |
| `2-validate` | `references/2-validate.md` | Re-check every finding and decide `keep`, `adjust` or `remove`. |
| `3-update` | `references/3-update.md` | Always. Stamp the workflow block and, when anything changed, write the corrected findings and summary. |

## Decision model

Every finding ends in exactly one of three decisions:

| Decision | Trigger | Effect on the report |
| --- | --- | --- |
| `keep` | Every check passes and nothing needs to change. | None. |
| `adjust` | The finding is real, but at least one field is wrong or stale: `clause_id`, `related_clause_ids`, `title`, `description`, `severity`, `wcag_criteria`, `wcag_level`, `hig_reference_url`, `minimal_fix`, `recommended_fix`, `ai_fix_prompt`, or `line_number` and `code_snippet` when the code moved or the snippet was elided. | Only the wrong fields change. `id` and `file_path` stay. |
| `remove` | No clause on the finding still holds in the source (a false positive, fixed since the scan, satisfied by a parent, decorative only), no Apple source supports any of its clauses, or it duplicates another finding and was merged into it. | The finding leaves `issues`, and `summary` is recomputed. |

The checks in `references/2-validate.md` run in order and add up. A check that adjusts a field records the change and the remaining checks still run on the updated finding. A check that decides `remove` ends the checks for that finding. When the primary clause no longer holds but a related one does, the finding is adjusted, not removed: the related clause becomes the primary.

Validation writes into the repair ledger in one case only: a finding whose `repair.status` is `applied` but whose violation is still in the source, or was confirmed at runtime after the last repair, gets `repair.status = "failed"` and a one-sentence `note`, and counts as `adjust`. Every other `repair` field is carried through untouched.

Validation never writes a finding's `runtime` block. It reads the verdict as evidence: a `refuted` verdict never removes a finding on its own, and it gets a `Runtime:` note in `scan_context.notes` whatever the decision.

## Severity mapping

Use the same table as evenbetter-analyze; the report checker applies it too.

| Corpus `severity` | Report severity | When |
| --- | --- | --- |
| `error` | `critical` | Always. If the Apple source no longer supports the rule, the finding fails verification and is dropped with a note, not downgraded. |
| `warning` | `high` | Default: the code shows the violation directly and users meet it in normal use. |
| `warning` | `medium` | The violation depends on runtime context the code does not show, such as a custom component's behaviour or where a view is presented. |
| `warning` | `critical` | The context makes it an accessibility blocker or a destructive risk, for example an unlabeled control that deletes data. |
| `info` | `low` | Always. |

A merged finding takes the highest severity that any of its clauses maps to. Moving a `warning` finding between `critical`, `high` and `medium` is an `adjust`; a `warning` finding never becomes `low`.

## Artifact rules

- Read and write only `.evenbetter/[project]/evenbetter-analyze-report.html`, in place. Do not create folders, sibling JSON exports or Markdown summaries. The `history/` folder belongs to evenbetter-analyze; leave it alone.
- Replace only the JSON literal after `const reportData = `. Markup, styles, Alpine bindings and CDN references stay byte-identical.
- Recompute `summary` from the surviving `issues` before writing.
- Bump `scan_date` to the current local time (`YYYY-MM-DD HH:MM:SS`) only when at least one finding was adjusted or removed. Leave it alone on a clean pass.
- Always write the workflow stamp: `state` becomes `validated`, `validated_at` becomes the current local time (never earlier than `scan_date`), and `validation` carries this pass's `kept`, `adjusted` and `removed` tally.
- Never write `workflow.state = "repaired"`, and never touch `workflow.repaired_at` or `workflow.repair`. Carry them through unchanged, and carry each finding's `runtime` block through unchanged too.
- Validation notes, such as corpus drift, go into `scan_context.notes` as one sentence each (`Corpus drift: ...`). Leave the rest of `scan_context` as loaded.
- After writing, give the user the absolute path as a `file://` link or a copyable path, plus the tally line from `references/3-update.md`.

## Report helper

`../../scripts/evenbetter_report.py` (Python 3 standard library only) reads, checks and updates reports with the same contract evenbetter-analyze and evenbetter-repair use. Resolve its path against this SKILL.md's folder. When `python3` is available:

- `python3 [script] extract REPORT.html` prints the embedded data as JSON.
- `python3 [script] check REPORT.html` lists every contract problem in the loaded report; stage 2 fixes them.
- `python3 [script] update DATA.json REPORT.html --state validated` checks the corrected data and replaces only the embedded data in the report. It refuses to write data with problems.

Without `python3`, follow the by-hand steps in the references.

## Corpus rules

- Read `../../corpus/index.json` once per run and group the findings by clause. The index gives `domain`, `severity`, `source_url`, `file_path` and `retrieved` for every clause. Its `file_path` values are relative to the plugin root, so `corpus/ios/accessibility.md` is `../../corpus/ios/accessibility.md` from this skill.
- Load a domain file the first time a finding from that domain needs it, and cache the parsed clauses.
- A finding's `hig_reference_url` equals the index `source_url` of its `clause_id`. When it differs, set it to the index value; analyze may cite a more specific Apple page in the description, never in this field.
- A clause ID that is missing from the index was removed or renamed since the scan. Drop it from `related_clause_ids`; if it is the primary clause, promote a related clause that still holds, or remove the finding when none does. Do not rebind a finding to a clause that was not on it; the only additions allowed are the twin and exclusive-pair cases in the source check of `references/2-validate.md`.
- When a clause's `retrieved` date is newer than the report's `scan_date`, the corpus moved after the scan, so the clause body, not the report's recorded fields, is the source of truth for that finding.

## Research rules

Read `../evenbetter-analyze/references/official-sources.md` before re-checking any HIG, WCAG or SwiftUI claim. Validation uses the same Apple-first discipline as evenbetter-analyze:

- Fetch each distinct index `source_url` once per run and reuse the result. If no fetch tool works, rely on the corpus, which was checked on its `retrieved` date, and say in the status line that sources were not re-fetched.
- Use WCAG 2.2 only as a cross-reference, from `https://www.w3.org/TR/WCAG22/`.
- Do not invent URLs. A finding that no Apple page supports is removed.

## iOS skill integration

- Use evenbetter-swiftui-accessibility clause loading when an accessibility clause body is unclear after re-reading the corpus.
- Use evenbetter-swiftui-ui-patterns references for SwiftUI navigation, sheets, forms, controls, theming and Dynamic Type when judging a fix.
- Use evenbetter-swiftui-view-refactor heuristics when a `recommended_fix` should be a structural decomposition rather than a single modifier change.
- Use evenbetter-swiftui-liquid-glass only when a finding involves iOS 26 or later Liquid Glass APIs.
- Runtime evidence for a finding comes from evenbetter-accessibility-tests, which writes the `runtime` block this skill reads. When a decision hangs on how the running app behaves and the finding is still `untested`, decide from the source as usual and suggest running that skill, then validating again.
- Use evenbetter-ios-debugger-agent for a simulator screenshot of a state the tests do not cover, such as a layout at a large text size. It builds and runs the app through Xcode's MCP server first and falls back to MobileBuildMCP.
- Do not edit application source code from this skill. Validation corrects the report; evenbetter-repair corrects the project.
