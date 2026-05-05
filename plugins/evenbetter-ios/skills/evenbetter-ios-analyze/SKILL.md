---
name: evenbetter-ios-analyze
description: iOS SwiftUI design-guidelines compliance analyzer for Apple Human Interface Guidelines and iOS accessibility. Use when run from or given a SwiftUI iOS project directory and asked to audit typography, color and theming, components, layout and interaction, navigation and flow, or accessibility; defaults to the current working directory when no project path is provided, spawns specialized read-only domain sub-agents when the host supports Claude Code or Codex subagents, creates the EvenBetter iOS HIG HTML-template data in the analyzer JSON, creates self-contained fix prompts directly in each JSON violation, and stores the report in the project's .evenbetter folder.
---

# evenbetter-ios-analyze

## Overview

Analyze an iOS SwiftUI project for Apple Human Interface Guidelines and iOS accessibility compliance. The analyzer reads source files without modifying them, creates the first-pass violation records and their self-contained `ai_fix_prompt` values, and writes the `html_report_data` dashboard/context fields required by the EvenBetter iOS HIG browser template. It then stores each final JSON report at `projectPath/.evenbetter/analyze-{N}.json` and updates `projectPath/.evenbetter/manifest.json`. After a successful run, do not include the JSON report body in the chat response; reply only with a brief summary that names the written report path, finding counts, and prompts the user to run `$evenbetter-validate`.

Do not edit, delete, format, generate, or execute source/project files inside `projectPath`. The only permitted writes inside `projectPath` are creating `.evenbetter/` if needed, auto-migrating a legacy `.evenbetter/analyze.json` into numbered history, writing the final report JSON to `.evenbetter/analyze-{N}.json`, and updating `.evenbetter/manifest.json`.

## Inputs

- `projectPath` (optional): Filesystem path to a SwiftUI iOS project. Default to the host's current working directory when omitted or `.`.
- `mode` (optional): `full` or `budget`. Default to `full`.

Resolve `projectPath` to an absolute path before use. If the user supplies a relative path, resolve it against the host's current working directory. Do not ask for a full path solely because `projectPath` is omitted or relative.

## Required References

Load these files only when their phase runs:

- `references/workflow.md`: Full coordinator workflow, domain dispatch, aggregation, scoring, executive summary style, and compaction-safe invariants.
- `references/schema.md`: Violation object schema for `full` and `budget` modes.
- `references/output-contract.md`: Final JSON report envelope and field definitions.
- Domain corpus modules: `../../corpus/ios/typography.md`, `../../corpus/ios/color-theming.md`, `../../corpus/ios/components-patterns.md`, `../../corpus/ios/layout-interaction.md`, `../../corpus/ios/navigation-flow.md`, and `../../corpus/ios/accessibility.md`.
- Corpus index: `../../corpus/index.json` for stable clause metadata.

## Platform Detection

Recursively walk `projectPath` using read-only filesystem access. Skip `node_modules`, `.build`, `.git`, `Pods`, `DerivedData`, `.swiftpm`, `build`, and `.xcodeproj` internals. Collect `.swift` files and confirm at least one contains `import SwiftUI`.

If no SwiftUI source is detected, emit exactly:

```json
{"error":"not a SwiftUI project"}
```

Then stop.

## Domain Analysis

Run all six iOS SwiftUI domains. If the host environment supports independent sub-agents or worker contexts, such as Claude Code subagents or Codex sub-agents, spawn one specialized read-only sub-agent per domain and run them concurrently when practical. Otherwise run the same domain passes sequentially in the main agent. Each domain module is self-contained and must output only a JSON array of violation objects with analyzer-authored remediation fields, including `fix_description`, `fix_code` in full mode, and `ai_fix_prompt`. Only the analyzer orchestrator writes `.evenbetter/analyze-{N}.json` and `manifest.json`.

- `typography`: load `../../corpus/ios/typography.md`
- `color-theming`: load `../../corpus/ios/color-theming.md`
- `components-patterns`: load `../../corpus/ios/components-patterns.md`
- `layout-interaction`: load `../../corpus/ios/layout-interaction.md`
- `navigation-flow`: load `../../corpus/ios/navigation-flow.md`
- `accessibility`: load `../../corpus/ios/accessibility.md`

Pass each domain the normalized `projectPath`, `mode`, and the discovered SwiftUI file list with relative paths and line-indexed contents. The domain must use only clauses from its corpus file, emit `rule_id` values matching corpus H2 clause IDs, and must not inspect unrelated platforms or emit findings outside its own `domain` value. The domain must write each `ai_fix_prompt` as a precise, self-contained prompt that another agent can follow later without inventing scope, finding context, or acceptance criteria.

## Aggregation

After all six domain arrays return:

1. Validate every violation against `references/schema.md`, including non-empty analyzer-generated fix prompt fields.
2. Reject findings whose `ai_fix_prompt` is missing, generic, or not grounded in the cited source file, rule, severity, and intended remediation.
3. Add stable `id` and default `state` fields to every violation.
4. Load `.evenbetter/manifest.json` when present and carry forward the latest prior state for matching violation IDs.
5. Group violations by `file_path`.
6. Compute per-file scores and project-wide `overall_score`, `ui_score`, and `a11y_score`.
7. Compute `domain_summaries`.
8. Produce a 3-5 sentence non-technical `executive_summary`.
9. Populate `html_report_data` for the EvenBetter iOS HIG HTML template, including project metadata, severity dashboard counts, and scan context.
10. Store exactly that JSON object at `projectPath/.evenbetter/analyze-{N}.json`, creating `.evenbetter/` if needed.
11. Update `.evenbetter/manifest.json` with run `N`, latest analyzer path, validation status, and state summary.
12. Reply with a concise human-readable summary matching `references/output-contract.md`. Do not include the analyzer report JSON body in the chat response.

Budget mode uses the same final envelope but slimmer violation objects.

## Output Rules

- For successful analysis runs, write results to `.evenbetter/analyze-{N}.json` and `.evenbetter/manifest.json`; do not echo the analyzer JSON body in chat.
- Reply with this concise summary shape:

```text
Analysis complete.
- Wrote: .evenbetter/analyze-{N}.json
- Findings: <total> total (<error> error, <warning> warning, <info> info)

Next: use $evenbetter-validate to confirm the findings and generate the HTML report.
```

- Compute `<total>` from `total_violations`, `<error>` from `critical_count` or summed `domain_summaries[].error_count`, and `<warning>` / `<info>` from summed `domain_summaries`.
- Use relative paths from `projectPath` for `file_path`.
- Use 1-based `line_number` values.
- Preserve the schema enums exactly.
- Generate stable violation IDs from `rule_id`, relative `file_path`, line or symbol anchor, and normalized summary text.
- Include `run` metadata and violation `state` objects exactly as defined in `references/output-contract.md` and `references/schema.md`.
- Include `html_report_data` exactly as defined in `references/output-contract.md`; it provides the EvenBetter iOS HIG report dashboard and scan-context data, while issue cards are derived from violations.
- Include a specific `ai_fix_prompt` in every violation. The validator may later judge prompt accuracy, but the analyzer is the only skill that creates fix prompts.
- Never modify source or project files inside `projectPath`.
- The only permitted project writes are numbered analyzer reports, `manifest.json`, and documented legacy report migration inside `projectPath/.evenbetter/`.
- End the chat summary by prompting the user to run `$evenbetter-validate`; validation corrects the analyzer JSON in place and generates the browser report.
