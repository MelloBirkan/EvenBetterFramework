---
name: evenbetter-ios-analyze
description: iOS SwiftUI design-guidelines compliance analyzer for Apple Human Interface Guidelines and WCAG 2.2. Use when given an absolute path to a SwiftUI iOS project and asked to audit typography, color and theming, components, layout and interaction, navigation and flow, or accessibility; reads source files without modifying them and stores the JSON report in the project's .evenbetter folder.
---

# evenbetter-ios-analyze

## Overview

Analyze an iOS SwiftUI project for Apple Human Interface Guidelines and WCAG 2.2 compliance. The analyzer reads source files without modifying them, then stores each final JSON report at `projectPath/.evenbetter/analyze-{N}.json` and updates `projectPath/.evenbetter/manifest.json`.

Do not edit, delete, format, generate, or execute source/project files inside `projectPath`. The only permitted writes inside `projectPath` are creating `.evenbetter/` if needed, auto-migrating a legacy `.evenbetter/analyze.json` into numbered history, writing the final report JSON to `.evenbetter/analyze-{N}.json`, and updating `.evenbetter/manifest.json`.

## Inputs

- `projectPath` (required): Absolute filesystem path to a SwiftUI iOS project.
- `mode` (optional): `full` or `budget`. Default to `full`.

If `projectPath` is missing or not absolute, return a JSON error object with an `error` key and stop.

## Required References

Load these files only when their phase runs:

- `references/workflow.md`: Full coordinator workflow, domain dispatch, aggregation, scoring, executive summary style, and compaction-safe invariants.
- `references/schema.md`: Violation object schema for `full` and `budget` modes.
- `references/output-contract.md`: Final JSON report envelope and field definitions.
- Domain rule modules: `references/typography.md`, `references/color-theming.md`, `references/components-patterns.md`, `references/layout-interaction.md`, `references/navigation-flow.md`, and `references/accessibility.md`.

## Platform Detection

Recursively walk `projectPath` using read-only filesystem access. Skip `node_modules`, `.build`, `.git`, `Pods`, `DerivedData`, `.swiftpm`, `build`, and `.xcodeproj` internals. Collect `.swift` files and confirm at least one contains `import SwiftUI`.

If no SwiftUI source is detected, emit exactly:

```json
{"error":"not a SwiftUI project"}
```

Then stop.

## Domain Analysis

Run all six iOS SwiftUI domains. If the host environment supports independent worker contexts, the domains may run concurrently. Otherwise run them sequentially. Each domain module is self-contained and must output only a JSON array of violation objects.

- `typography`: load `references/typography.md`
- `color-theming`: load `references/color-theming.md`
- `components-patterns`: load `references/components-patterns.md`
- `layout-interaction`: load `references/layout-interaction.md`
- `navigation-flow`: load `references/navigation-flow.md`
- `accessibility`: load `references/accessibility.md`

Pass each domain the normalized `projectPath`, `mode`, and the discovered SwiftUI file list with relative paths and line-indexed contents. The domain must not inspect unrelated platforms or emit findings outside its own `domain` value.

## Aggregation

After all six domain arrays return:

1. Validate every violation against `references/schema.md`.
2. Add stable `id` and default `state` fields to every violation.
3. Load `.evenbetter/manifest.json` when present and carry forward the latest prior state for matching violation IDs.
4. Group violations by `file_path`.
5. Compute per-file scores and project-wide `overall_score`, `ui_score`, and `a11y_score`.
6. Compute `domain_summaries`.
7. Produce a 3-5 sentence non-technical `executive_summary`.
8. Store exactly that JSON object at `projectPath/.evenbetter/analyze-{N}.json`, creating `.evenbetter/` if needed.
9. Update `.evenbetter/manifest.json` with run `N`, latest analyzer path, validation status, and state summary.
10. Emit exactly the same analyzer report JSON object matching `references/output-contract.md`.

Budget mode uses the same final envelope but slimmer violation objects.

## Output Rules

- Output JSON only, with no Markdown fences and no explanatory prose.
- Use relative paths from `projectPath` for `file_path`.
- Use 1-based `line_number` values.
- Preserve the schema enums exactly.
- Generate stable violation IDs from `rule_id`, relative `file_path`, line or symbol anchor, and normalized summary text.
- Include `run` metadata and violation `state` objects exactly as defined in `references/output-contract.md` and `references/schema.md`.
- Never modify source or project files inside `projectPath`.
- The only permitted project writes are numbered analyzer reports, `manifest.json`, and documented legacy report migration inside `projectPath/.evenbetter/`.
