# Coordinator Workflow

This workflow coordinates a source-safe Apple HIG and iOS accessibility analysis for SwiftUI projects. Never edit, delete, format, generate, or execute source/project files inside `projectPath`; read source files only. The only permitted writes inside `projectPath` are numbered analyzer reports, `manifest.json`, and documented legacy report migration inside `.evenbetter/`.

EvenBetter assumes serial execution. Before writing any report or manifest update, reread `projectPath/.evenbetter/manifest.json` from disk.

## 1. Normalize Inputs

1. If `projectPath` is omitted or `.`, set it to the host's current working directory for this skill invocation.
2. If `projectPath` is relative, resolve it against the host's current working directory.
3. Canonicalize `projectPath` to an absolute path before reading, writing, reporting, or passing it to domain workers.
4. Set `mode` to `full` when omitted.
5. Accept only `full` or `budget`; otherwise return a JSON error object with an `error` key and stop.

## 2. Detect SwiftUI

Walk `projectPath` recursively with read-only filesystem access.

Skip directories named:

- `node_modules`
- `.build`
- `.git`
- `Pods`
- `DerivedData`
- `.swiftpm`
- `build`

Also skip `.xcodeproj` internals.

Collect files ending in `.swift`. For each candidate, read text and keep it only if the file is part of the source inventory. Confirm at least one collected Swift file contains `import SwiftUI`.

If no SwiftUI source is detected, emit exactly:

```json
{"error":"not a SwiftUI project"}
```

Then stop.

## 3. Build The File Inventory

Create a stable in-memory inventory:

- `projectPath`
- `mode`
- ordered list of Swift source files
- each file's relative path
- each file's full text
- line-indexed text for 1-based line numbers
- basic file metrics, including Swift line count

Preserve this inventory through any context compaction. Do not re-walk with different skip rules later in the same analysis.

## 4. Prepare Report History

Create `projectPath/.evenbetter/` if needed, then determine the next analyzer run number.

1. If `manifest.json` exists, parse it and treat it as the source of truth for known runs.
2. If `manifest.json` is missing but `analyze-*.json` exists, scan the numbered reports, infer `currentRun` from the highest number, and write a manifest before continuing.
3. If `manifest.json` is missing and legacy `analyze.json` exists, auto-migrate it:
   - Treat it as run 1.
   - Write the same report to `analyze-1.json`.
   - Add missing `run`, violation `id`, and violation `state` fields when possible.
   - Initialize `manifest.json` with run 1.
   - Use run 2 for the new analysis.
4. If no history exists, use run 1.

For the new run, set:

- `run.number`: the selected run number `N`.
- `run.createdAt`: current UTC ISO-8601 timestamp with `Z`.
- `run.previousRun`: previous manifest `currentRun`, or null.
- `run.supersedes`: the previous analyzer filename when one exists; otherwise an empty array.
- `run.status`: `pending_validation`.

Keep old reports indefinitely. Do not delete or overwrite `analyze-{N}.json`, `evenbetter-validate-{N}.json`, or legacy `analyze.json`.

## 5. Run The Six Domain Specialists

Run all six domains against the same inventory:

| Domain | Domain reference |
|---|---|
| `typography` | `../../corpus/ios/typography.md` |
| `color-theming` | `../../corpus/ios/color-theming.md` |
| `components-patterns` | `../../corpus/ios/components-patterns.md` |
| `layout-interaction` | `../../corpus/ios/layout-interaction.md` |
| `navigation-flow` | `../../corpus/ios/navigation-flow.md` |
| `accessibility` | `../../corpus/ios/accessibility.md` |

If the host environment supports independent sub-agents or worker contexts, such as Claude Code subagents or Codex sub-agents, spawn one specialized read-only domain sub-agent for each row in the table and run them concurrently when practical. Each sub-agent is an expert for its own Apple HIG, SwiftUI, and accessibility domain. If sub-agents are unavailable or not permitted, run the same six domain passes sequentially in the table order.

Only the analyzer orchestrator may write files. Domain sub-agents must read the supplied inventory and references, return a JSON array, and not write source files, `.evenbetter` files, cache files, or notes.

Use this generic prompt shape for each domain context:

```text
You are the <domain> specialist for an EvenBetter iOS SwiftUI Apple HIG and accessibility analysis.

Analyze the provided iOS SwiftUI file inventory for the <domain> domain only.
Inputs:
- projectPath: <absolute path>
- mode: <full|budget>
- files: <relative path, line-indexed content, and metrics>

Follow <domain corpus reference>. Use only H2 corpus clauses from that domain file as rules, and set each violation `rule_id` to the matching clause ID. Return only a JSON array of violation objects matching the shared schema for the active mode except for analyzer-added id and state. Create `ai_fix_prompt` directly in each violation as a self-contained prompt that identifies the finding, cites the relevant file/line/rule, explains the intended remediation, and gives clear acceptance criteria for a later fixer agent. Do not modify source/project files. Do not include findings outside <domain>.
```

## 6. Validate And Enrich Domain Results

For each domain JSON array:

1. Parse as JSON.
2. Reject or correct non-array wrapper text.
3. Validate each object against `references/schema.md`, allowing `id` and `state` to be added by the analyzer after domain output.
4. Require `domain` to match the domain context.
5. Require `rule_id` to match a `clause_id` in `../../corpus/index.json`.
6. Require `severity` to be `error`, `warning`, or `info`.
7. Require `dimension` to be `ui`, `ux`, or `accessibility`.
8. Require `file_path` to be in the file inventory.
9. Require `line_number` to be a positive 1-based integer.
10. Require `ai_fix_prompt` to be present, specific, and grounded in `rule_id`, `file_path`, `line_number`, `summary`, and `fix_description`.
11. Reject findings whose prompt asks for broad redesign, unrelated refactoring, validation work, or future prompt generation instead of a concrete fix.
12. In `budget` mode, remove `why_fix`, `fix_code`, and `auto_fixable` if present.
13. In `full` mode, discard findings that cannot provide all required full-mode fields.
14. Generate `id` for each remaining violation using `references/schema.md`.
15. Add default `state` for each new violation.
16. For a matching violation ID found in previous analyzer reports, copy the latest prior `state` into the new violation so fixed, rejected, and deferred decisions persist across runs.
17. If the analyzer can confidently identify a duplicate of an earlier violation with a different ID, set `state.status` to `duplicate_of` and `state.duplicateOf` to the earlier ID.

When copying prior state, latest run wins. Never overwrite a prior report's `violations[]` content during analysis; only the fixer may mutate prior violation `state` after a user decision or completed fix.

## 7. Aggregate Violations

1. Concatenate the six arrays.
2. Sort violations by `file_path`, then `line_number`, then `rule_id`.
3. Group by `file_path`.
4. Include one `files[]` entry for every analyzed SwiftUI source file. Use an empty `violations` array for clean files.
5. Compute `total_files` from the inventory.
6. Compute `total_violations` from the concatenated array.
7. Compute `critical_count` as the count of violations where `severity` is `error`.

## 8. Domain Summaries

Emit exactly six `domain_summaries[]` entries in this order:

1. `typography`
2. `color-theming`
3. `components-patterns`
4. `layout-interaction`
5. `navigation-flow`
6. `accessibility`

For each domain, count:

- `violation_count`
- `error_count`
- `warning_count`
- `info_count`

Use zeros for domains with no findings.

## 9. Scoring Heuristics

All scores are integers from 0 to 100. A clean file scores 100. A file with many severe findings can score near 0.

Severity weights:

- `error`: 12 points
- `warning`: 6 points
- `info`: 2 points

For each file and dimension:

1. Sum severity weights for violations in that dimension.
2. Adjust lightly for file size: use the full weight for files up to 160 Swift lines, reduce penalty by up to 40 percent for larger files, and never increase penalty above the base weight.
3. Score = `100 - adjusted penalty`, clamped to `0...100`.

For each file:

- `ui_score`: dimension score for `ui`
- `ux_score`: dimension score for `ux`
- `a11y_score`: dimension score for `accessibility`
- `score`: rounded average of `ui_score`, `ux_score`, and `a11y_score`

For project-wide scores:

1. Weight each file by Swift line count, with a minimum weight of 20 lines so tiny files do not disappear.
2. Compute weighted averages for `ui_score`, `ux_score`, `a11y_score`, and `overall_score`.
3. Round to the nearest integer.

When evidence suggests a severe accessibility blocker affects a central shared component, keep the score holistic: allow the project accessibility score to drop more than raw counts alone would imply.

## 10. Executive Summary Style

Write 3-5 sentences for a non-technical stakeholder.

Include:

- overall compliance posture
- the most affected domains
- whether accessibility risk is low, moderate, or high
- one practical remediation theme

Avoid:

- code snippets
- rule IDs
- jargon-heavy implementation details
- vague claims unsupported by the findings

## 11. Store Report And Manifest

Load `references/output-contract.md` and produce one analyzer report object matching it exactly. Use:

- `run`: metadata from the prepared report history
- `project_path`: the resolved absolute `projectPath`
- `platform`: `swiftui`
- `guidelines`: `Apple Human Interface Guidelines`
- `html_report_data`: dashboard and scan-context data for the EvenBetter iOS HIG browser template

Populate `html_report_data` from the same source facts rather than inventing a second issue model:

- `brand`: `EvenBetter`
- `report_title`: `EvenBetter iOS HIG Report`
- `standard_label` and `hig_standard`: `Apple Human Interface Guidelines`
- `project_name`: project directory name unless a stronger app name is known from project metadata
- `project_path`: same value as top-level `project_path`
- `framework`: `SwiftUI`
- `scan_date`: same value as `run.createdAt`
- `summary.total`: same value as `total_violations`
- `summary.critical`: count of `severity = "error"`
- `summary.high`: count of `severity = "warning"`
- `summary.medium`: count of `severity = "info"`
- `summary.low`: `0` unless the contract later adds a lower-priority severity
- `scan_context.frameworks`: at least `["SwiftUI"]`
- `scan_context.design_systems`: at least `["Apple Human Interface Guidelines"]`
- `scan_context.component_patterns`: detected SwiftUI patterns or the analyzed domain names
- `scan_context.files_scanned`: same value as `total_files`
- `scan_context.framework_versions`, `scan_context.scan_duration`, `scan_context.confidence`, and `scan_context.custom_utilities`: fill when known, otherwise use the null/empty defaults from the output contract

Before writing the JSON object, reread `projectPath/.evenbetter/manifest.json` and write the analyzer report to:

```text
projectPath/.evenbetter/analyze-{N}.json
```

Then update `projectPath/.evenbetter/manifest.json`:

- `version`: `1`
- `currentRun`: `N`
- `latest.analyze`: `analyze-{N}.json`
- `latest.validate`: preserve legacy validation report paths for compatibility, or null when no legacy validation report exists
- `latest.html_report`: preserve the newest generated HTML report path when present, or null when no HTML report exists
- `runs[]`: add or replace the entry for run `N`
- `runs[].validate`: preserve legacy compatibility only; new validation runs do not write validation JSON
- `runs[].html_report`: null until the validator generates `.evenbetter/evenbetter-validate-{N}.html`
- `runs[].validated`: false until validation succeeds
- `runs[].status`: `pending_validation`
- `runs[].summary`: counts of violation `state.status` values in `analyze-{N}.json`

The stored analyzer JSON remains the complete machine-readable artifact. The chat response must not include that JSON body.

Reply with this concise summary only:

```text
Analysis complete.
- Wrote: .evenbetter/analyze-{N}.json
- Findings: <total> total (<error> error, <warning> warning, <info> info)

Next: use $evenbetter-validate to confirm the findings and generate the HTML report.
```

Compute `<total>` from `total_violations`, `<error>` from `critical_count` or summed `domain_summaries[].error_count`, and `<warning>` / `<info>` from summed `domain_summaries`.

## 12. Optional Validator Handoff

If `skills/evenbetter-validate/SKILL.md` exists in the workspace and the user or host requests validation, invoke `evenbetter-validate` as a separate skill against the same `projectPath` after `.evenbetter/analyze-{N}.json` and `.evenbetter/manifest.json` are written. Validation corrects the analyzer JSON in place, marks the run as validated in `manifest.json`, and generates `.evenbetter/evenbetter-validate-{N}.html`; it does not write `.evenbetter/evenbetter-validate-{N}.json`.

For analyzer runs that also request validation, keep the analyzer summary separate from validator output. The analyzer summary should still prompt the user to run `$evenbetter-validate` unless validation was already requested and completed in the same interaction.

## 13. Compaction-Safe Invariants

If context is compacted, preserve these facts exactly:

- `projectPath`
- `projectPath` defaults to the invocation working directory when omitted
- `mode`
- skip-directory list
- ordered SwiftUI file inventory
- `.evenbetter/manifest.json` is the source of truth for report history
- analyzer reports are numbered as `.evenbetter/analyze-{N}.json`
- legacy `.evenbetter/analyze.json` is auto-migrated only when no manifest exists
- six domain names and corpus paths
- spawn specialized read-only domain sub-agents for the six domains when the host supports sub-agents; otherwise run the same passes sequentially
- schema field sets for `full` and `budget`
- analyzer creates all `ai_fix_prompt` values directly in the JSON report
- analyzer creates `html_report_data` for the EvenBetter iOS HIG HTML template, while current issue cards still come from `files[].violations[]`
- domain, severity, dimension, state, and run status enums
- stable violation ID inputs and SHA-256 prefix rule
- aggregation and scoring contract
- source-safe discipline and the numbered report plus manifest writes
- final output envelope keys
- successful analysis prompts the user to run `$evenbetter-validate`
