---
name: evenbetter-analyze
description: Full-repo Swift and SwiftUI audit for Apple Human Interface Guidelines and accessibility violations. Scans the codebase against the EvenBetter iOS corpus, verifies each finding against official Apple documentation and WCAG 2.2, and writes an interactive branded HTML report to `.evenbetter/<project>/evenbetter-analyze-report.html` with file/line evidence, two remediation paths, and AI fix prompts. Use this skill whenever the user asks to analyze, audit, scan, lint, review, check, or evaluate an iOS, Swift, or SwiftUI project for HIG conformance, accessibility issues, VoiceOver problems, Dynamic Type problems, color contrast, hit-target sizing, navigation, or WCAG concerns, even when they do not say the word "report" — they almost always want the HTML deliverable.
---

# evenbetter-analyze

## Operating model

Use this skill as a three-stage automated audit for a Swift/SwiftUI repository. The output is a self-contained interactive HTML report that lists Apple HIG and accessibility findings with file/line evidence, two remediation paths per issue (minimal and recommended), and an AI fix prompt that can be pasted into Claude Code, Cursor, or Copilot.

- The audit is corpus-first: walk the EvenBetter iOS corpus (`../../corpus/index.json` and `../../corpus/ios/*.md`) before reaching for web search.
- Every reported issue must link to at least one official Apple HIG or Apple Developer Documentation URL. Findings that cannot be verified are dropped.
- The report is the deliverable. Do not summarize findings inline beyond a one-paragraph status update with the path to the generated HTML.
- Keep artifacts in `.evenbetter/<project-name>/`. Reuse an existing folder when one is already there.
- Load only the reference for the current stage plus `official-sources.md` when documentation lookup is needed.

Former slash-command names may be aliases. Interpret `/evenbetter-analyze:1-scan` as "use `evenbetter-analyze` with stage `1-scan`."

## Workflow position

Analysis is the second of four EvenBetter interaction states: planning, analysis, validation, repair. This skill owns analysis only. It discovers findings and writes them into the report; it never edits application source code.

- `evenbetter-validate` runs next. It re-checks every finding and stamps `workflow.state = "validated"` into the same report.
- `evenbetter-repair` runs last. It applies remediations, and it refuses any report this skill produced until validation has stamped it.

Because a fresh scan invalidates prior review, this skill always writes `workflow.state = "analyzed"` and clears the validation and repair stamps, even when overwriting a report that was previously validated or repaired. See `references/3-report.md` for the block's shape.

## Question tooling

Most analyses need no questions. Ask only when the audit scope is genuinely ambiguous. When asking is necessary (multiple Swift targets, monorepo layout, conflicting feature folders), use the best available structured-question tool with mutually exclusive options:

- Claude Code: `AskUserQuestion` with 2-4 options.
- Codex Plan mode: `request_user_input` when available.
- Cursor or other agents with an ask-question tool: the native structured tool.
- Environments without structured questions: one closed question with numbered options.

Never ask open-ended questions during an audit. Default to scanning the entire repository when no scope is specified.

## Tool equivalents

The reference files mention Claude-style tool names. Apply these equivalents in Codex:

| Claude command instruction | Codex equivalent |
| --- | --- |
| `AskUserQuestion` | `request_user_input` in Plan mode when available, otherwise a concise closed question |
| `Glob`, `Grep`, `Read` | `rg --files`, `rg`, and shell file reads such as `sed` or `nl` |
| `Bash` | `exec_command` |
| `WebSearch`, `WebFetch` | available web-search tooling, or official Apple documentation lookup |
| `TaskCreate`, `TaskUpdate` | `update_plan` |
| `ref_search_documentation`, `ref_read_url` | available official-doc tooling, otherwise direct fetch of Apple documentation URLs |

If current system or developer instructions conflict with a converted reference, follow the higher-priority instruction.

## Stage selection

Run the stages in order for a fresh audit. Skip ahead only when prior-stage artifacts already exist and remain valid.

| Stage | Reference | Use when |
| --- | --- | --- |
| `1-scan` | `references/1-scan.md` | Walk Swift sources, match each file against corpus clauses, and produce a draft findings list with file/line evidence. |
| `2-verify` | `references/2-verify.md` | Confirm each finding against Apple HIG or Apple Developer Documentation, attach the canonical URL, and discard false positives. |
| `3-report` | `references/3-report.md` | Render the verified findings into the HTML template at `.evenbetter/<project>/evenbetter-analyze-report.html`. |

## Severity mapping

The corpus uses three severity levels. Map them to the report's four-tier model when assembling the issue list:

| Corpus `severity` | Report severity | Use |
| --- | --- | --- |
| `error` | `critical` | User harm, accessibility blocker, destructive risk, high-confidence violation. |
| `warning` (a11y/ux blocker) | `high` | Meaningful user impact and high confidence the rule applies. |
| `warning` (lower confidence) | `medium` | Conformance concern with broader uncertainty or context-dependent impact. |
| `info` | `low` | Polish, consistency, or non-blocking quality improvement. |

When a `warning` clause is firmly grounded in the source (e.g., explicit accessibility notification or destructive confirmation), choose `high`. When the static signal is weaker (e.g., possible custom-component reasoning), choose `medium`.

## Artifact rules

- Create `.evenbetter/` if it does not exist.
- Derive `<project-name>` from the repository folder name in kebab-case. If the workspace already contains `.evenbetter/<existing-name>/`, reuse that folder.
- Write the report to `.evenbetter/<project-name>/evenbetter-analyze-report.html`. Overwrite existing reports — the file is the latest snapshot, not history.
- Reset the workflow state on every write: `workflow.state` is `analyzed`, the validation and repair stamps are cleared, and every finding's `repair.status` is `pending`. A re-scan never inherits a previous run's validation.
- Do not create supporting Markdown summaries unless the user asks. The HTML is the source of truth.
- After writing the report, surface the absolute file path to the user as a clickable `file://` link or a copyable path; keep the rest of the response short.

## Research rules

Read `references/official-sources.md` before making any HIG, WCAG, or SwiftUI claim that ends up in the report. Always prefer Apple HIG and Apple Developer Documentation. Use WCAG 2.2 only as a cross-reference, never as the primary citation. Cite one canonical URL per finding in `hig_reference_url`. If the agent cannot find an Apple URL for a finding, drop the finding rather than invent one.

## iOS skill integration

- Use `evenbetter-swiftui-accessibility` clause loading when accessibility findings need detailed clause bodies.
- Use `evenbetter-swiftui-ui-patterns` references for SwiftUI navigation, sheets, forms, controls, theming, and Dynamic Type background context.
- Use `evenbetter-swiftui-view-refactor` heuristics when remediation needs structural decomposition rather than a single modifier change.
- Use `evenbetter-swiftui-liquid-glass` only when iOS 26+ Liquid Glass APIs are involved in the finding.
- Use `evenbetter-ios-debugger-agent` to capture simulator screenshots when a visual rule (contrast, layout, large Dynamic Type) needs runtime evidence.
- Hand off to `evenbetter-validate`, then `evenbetter-repair`, rather than editing source code from this skill. The `ai_fix_prompt` field stays in the report as a manual escape hatch; `evenbetter-repair` is the guided path.
