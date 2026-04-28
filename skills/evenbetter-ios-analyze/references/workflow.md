# Coordinator Workflow

This workflow coordinates a source-safe design-guidelines compliance analysis for iOS SwiftUI projects. Never edit, delete, format, generate, or execute source/project files inside `projectPath`; read source files only. The only permitted write inside `projectPath` is the final JSON report at `.evenbetter/analyze.json`.

## 1. Normalize Inputs

1. Require `projectPath`.
2. Confirm `projectPath` is absolute.
3. Set `mode` to `full` when omitted.
4. Accept only `full` or `budget`; otherwise return a JSON error object with an `error` key and stop.

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

## 4. Run The Six Domains

Run all six domains against the same inventory:

| Domain | Domain reference |
|---|---|
| `typography` | `references/typography.md` |
| `color-theming` | `references/color-theming.md` |
| `components-patterns` | `references/components-patterns.md` |
| `layout-interaction` | `references/layout-interaction.md` |
| `navigation-flow` | `references/navigation-flow.md` |
| `accessibility` | `references/accessibility.md` |

If the host environment supports independent worker contexts, these analyses may run concurrently because they are read-only and independent. Otherwise run them sequentially in the table order.

Use this generic prompt shape for each domain context:

```text
Analyze the provided iOS SwiftUI file inventory for the <domain> domain only.
Inputs:
- projectPath: <absolute path>
- mode: <full|budget>
- files: <relative path, line-indexed content, and metrics>

Follow <domain reference>. Return only a JSON array of violation objects matching the shared schema for the active mode. Do not modify source/project files. Do not include findings outside <domain>.
```

## 5. Validate Domain Results

For each domain JSON array:

1. Parse as JSON.
2. Reject or correct non-array wrapper text.
3. Validate each object against `references/schema.md`.
4. Require `domain` to match the domain context.
5. Require `severity` to be `error`, `warning`, or `info`.
6. Require `dimension` to be `ui`, `ux`, or `accessibility`.
7. Require `file_path` to be in the file inventory.
8. Require `line_number` to be a positive 1-based integer.
9. In `budget` mode, remove `why_fix`, `fix_code`, and `auto_fixable` if present.
10. In `full` mode, discard findings that cannot provide all required full-mode fields.

## 6. Aggregate Violations

1. Concatenate the six arrays.
2. Sort violations by `file_path`, then `line_number`, then `rule_id`.
3. Group by `file_path`.
4. Include one `files[]` entry for every analyzed SwiftUI source file. Use an empty `violations` array for clean files.
5. Compute `total_files` from the inventory.
6. Compute `total_violations` from the concatenated array.
7. Compute `critical_count` as the count of violations where `severity` is `error`.

## 7. Domain Summaries

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

## 8. Scoring Heuristics

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

## 9. Executive Summary Style

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

## 10. Store And Output

Load `references/output-contract.md` and emit one JSON object matching it exactly. Use:

- `project_path`: the input `projectPath`
- `platform`: `swiftui`
- `guidelines`: `Apple Human Interface Guidelines`

Before emitting the JSON object, create `projectPath/.evenbetter/` if it does not exist and write the same JSON object to:

```text
projectPath/.evenbetter/analyze.json
```

This report file is the only permitted write inside `projectPath`. Overwrite the file on each new analysis so it always represents the latest `evenbetter-ios-analyze` result.

After storing the file, output JSON only, with no Markdown fences, commentary, or extra keys. The emitted JSON and stored JSON must be identical.

## 11. Optional Validator Handoff

If `skills/evenbetter-validate/SKILL.md` exists in the workspace and the user or host requests validation, invoke `$evenbetter-validate` as a separate skill against the same `projectPath` after `.evenbetter/analyze.json` is written. Keep the validation output separate at `.evenbetter/evenbetter-validate.json`; do not merge validator results into the analyzer JSON envelope.

For JSON-only analyzer runs, do not append validator commentary to stdout. The analyzer output must remain the exact `analyze.json` object.

## 12. Compaction-Safe Invariants

If context is compacted, preserve these facts exactly:

- `projectPath`
- `mode`
- skip-directory list
- ordered SwiftUI file inventory
- six domain names and reference paths
- schema field sets for `full` and `budget`
- domain, severity, and dimension enums
- aggregation and scoring contract
- source-safe discipline and the `.evenbetter/analyze.json` report write
- final output envelope keys
