---
name: evenbetter-analyze
description: >-
  Audits a Swift or SwiftUI repository against the EvenBetter corpus of Apple HIG and accessibility clauses, checks
  each finding on Apple's docs, and writes an HTML report with evidence and fixes. Use when asked to analyze, audit,
  scan or review an iOS app for HIG conformance, VoiceOver, Dynamic Type, contrast, tap targets or WCAG. To re-check
  an existing report, use evenbetter-validate.
---

# evenbetter-analyze

> Paths in this skill and its references are relative to this SKILL.md's folder. The plugin corpus is at `../../corpus/`.

## Operating model

This skill runs a three-stage audit of a Swift or SwiftUI repository. The deliverable is a self-contained HTML report: Apple HIG and accessibility findings with file and line evidence, a minimal and a recommended fix for each, and an AI fix prompt the user can paste into an AI coding agent such as Claude Code or Codex.

- The audit is corpus-first. Walk the EvenBetter iOS corpus (`../../corpus/index.json` and `../../corpus/ios/*.md`) before searching the web.
- Every finding cites a corpus clause and links to that clause's Apple HIG or Apple Developer Documentation page. A candidate that cannot be verified is dropped.
- The report is the deliverable. Do not summarize findings in chat beyond a short status line and the path to the HTML.
- Load only the reference for the current stage, plus `references/official-sources.md` when looking up documentation.

A stage name given as the argument (for example `1-scan`) selects that stage.

## Workflow position

Analysis is the second of four EvenBetter interaction states: planning, analysis, validation, repair. This skill discovers findings and writes them into the report. It never edits application source code.

- evenbetter-validate runs next. It re-checks every finding and stamps `workflow.state = "validated"` into the same report.
- evenbetter-repair runs last. It refuses a report from this skill until validation has stamped it.
- evenbetter-accessibility-tests can run after validation or repair. It runs Apple's accessibility audit on the screens behind the findings, in the running app, and writes only each finding's `runtime` block.

A fresh scan invalidates any earlier review, so this skill always writes `workflow.state = "analyzed"` with the validation and repair stamps cleared. The previous report is kept in `history/` first (see Artifact rules). `references/3-report.md` has the block's shape.

## Question tooling

Most analyses need no questions. Ask only when the audit scope is ambiguous: several app targets, a monorepo, or conflicting feature folders. Otherwise scan the whole repository without asking. Questions are closed, with mutually exclusive options and the recommended option first.

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

Run the stages in order in one session. Stages 1 and 2 keep their results in memory and write nothing, so starting at `2-verify` or `3-report` only works when the earlier stages already ran in this session; otherwise start at `1-scan`.

| Stage | Reference | Use when |
| --- | --- | --- |
| `1-scan` | `references/1-scan.md` | Walk Swift sources, match them against corpus clauses, and draft findings with file and line evidence. |
| `2-verify` | `references/2-verify.md` | Confirm each draft on its Apple page, merge findings that share a construct and a fix, write both fixes and the prompt, and drop false positives. |
| `3-report` | `references/3-report.md` | Build the report data and render it into `references/report-template.html` at `.evenbetter/[project]/evenbetter-analyze-report.html`. |

## Finding rules

These hold for every finding. `references/2-verify.md` has the detail and `references/3-report.md` the schema.

- One finding per construct and fix. When several clauses fire on the same element and one edit closes them all, emit one finding: `clause_id` is the clause the edit centres on, the others go in `related_clause_ids`, and severity is the highest any of them maps to. Different constructs, or fixes that differ, stay separate.
- `hig_reference_url` equals the `source_url` of `clause_id` in `../../corpus/index.json`. A more specific Apple page can be cited in the description text.
- Only corpus clauses become findings. A real problem with no clause goes into the description of a finding whose fix also closes it, or into `scan_context.notes`.
- `code_snippet` is verbatim, contiguous source with no elisions. `minimal_fix` and `recommended_fix` are complete, compilable replacements for those lines, also with no elisions. A fix that touches another file, or another place in the same file, is split into parts that each start with `// File: [project-relative path]`, and `ai_fix_prompt` names every file it touches.
- WCAG is a cross-reference only. Cite WCAG 2.2 criteria from `https://www.w3.org/TR/WCAG22/`. For target size in an AA report use 2.5.8 Target Size (Minimum); 2.5.5 is AAA.

## Severity mapping

The corpus has three severity levels and the report has four. Use this table in every stage; evenbetter-validate and the report checker apply the same one.

| Corpus `severity` | Report severity | When |
| --- | --- | --- |
| `error` | `critical` | Always. If the Apple source no longer supports the rule, the finding fails verification and is dropped with a note, not downgraded. |
| `warning` | `high` | Default: the code shows the violation directly and users meet it in normal use. |
| `warning` | `medium` | The violation depends on runtime context the code does not show, such as a custom component's behaviour or where a view is presented. |
| `warning` | `critical` | The context makes it an accessibility blocker or a destructive risk, for example an unlabeled control that deletes data. |
| `info` | `low` | Always. |

A merged finding takes the highest severity that any of its clauses maps to.

## Evidence without a simulator

Simulator screenshots, from evenbetter-ios-debugger-agent or from the user, are the preferred evidence for visual rules: contrast, layout, and large Dynamic Type sizes. When none is available, as on Linux, in CI, or without a booted simulator, run a static audit:

- Keep a visual finding when the code gives the values it depends on. Compute contrast from the colours in code, using Apple's documented values for system colours, and say in the description that the ratio is computed from colour values, not measured on a device.
- Drop a visual finding when the code does not give enough to judge it, and mention it in `scan_context.notes`.
- Severity still follows the mapping above. Record the static audit in `scan_context.notes` and lower `scan_context.confidence` as `references/3-report.md` describes.

## Artifact rules

- Artifacts live in the user's project under `.evenbetter/`. Never write inside this skill or the plugin folder.
- `[project]` is the folder under `.evenbetter/` that already holds `evenbetter-analyze-report.html`. When there is none, it is the repository root folder name in kebab-case. Other EvenBetter skills keep feature folders under `.evenbetter/` too, so do not reuse a folder just because it exists.
- `project_name` in the report is the app's human-readable name (the `@main` App type without its `App` suffix, the Xcode project, or the Swift package), which can differ from `[project]`.
- Write the report to `.evenbetter/[project]/evenbetter-analyze-report.html`. Before overwriting an existing report, move it to `.evenbetter/[project]/history/evenbetter-analyze-report-[YYYYMMDD-HHMMSS].html`, named after its `scan_date`, so validated decisions and repair notes are not lost. The report helper does this for you.
- Every write resets the workflow: `workflow.state` is `analyzed`, the validation and repair stamps are cleared, every finding's `repair.status` is `pending`, and every finding's `runtime.status` is `untested`.
- Do not create Markdown summaries or other files unless the user asks. The HTML report is the source of truth; audit notes go in `scan_context.notes`.
- After writing, give the user the absolute path as a `file://` link or a copyable path, and keep the rest of the reply short.

## Report helper

`../../scripts/evenbetter_report.py` (Python 3 standard library only) renders, reads and checks reports, so analyze, validate and repair enforce the same contract. Resolve its path against this SKILL.md's folder. When `python3` is available, use it:

- `python3 [script] render DATA.json REPORT.html --state analyzed` checks the data, moves an existing report to `history/`, and writes the report with the data safely escaped.
- `python3 [script] check REPORT.html --state analyzed` re-checks a written report.
- `python3 [script] extract REPORT.html` prints the embedded data as JSON.

Without `python3`, follow the by-hand procedure in `references/3-report.md`.

## Research rules

Read `references/official-sources.md` before making any HIG, WCAG or SwiftUI claim that ends up in the report. Prefer Apple HIG and Apple Developer Documentation, and use WCAG 2.2 only as a cross-reference. If a finding has no Apple source that supports it, drop it rather than invent a URL.

## iOS skill integration

- Use evenbetter-swiftui-accessibility clause loading when an accessibility finding needs the full clause body.
- Use evenbetter-swiftui-ui-patterns references for background on SwiftUI navigation, sheets, forms, controls, theming and Dynamic Type.
- Use evenbetter-swiftui-view-refactor heuristics when a fix needs structural decomposition rather than a single modifier change.
- Use evenbetter-swiftui-liquid-glass only when a finding involves iOS 26 or later Liquid Glass APIs.
- Use evenbetter-ios-debugger-agent to build and run the app and capture a simulator screenshot of a state when a visual rule needs one during the scan. It works through Xcode's MCP server first and falls back to MobileBuildMCP.
- Runtime accessibility evidence for the findings comes later, from evenbetter-accessibility-tests (see Workflow position). This skill does not run it.
- Hand off to evenbetter-validate, then evenbetter-repair, rather than editing source code. The `ai_fix_prompt` field stays in the report as a manual option; evenbetter-repair is the guided path.
