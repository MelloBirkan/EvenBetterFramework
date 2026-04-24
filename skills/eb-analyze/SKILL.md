---
name: eb-analyze
description: Read-only iOS SwiftUI design-guidelines compliance analyzer for Apple Human Interface Guidelines and WCAG 2.2. Use when given an absolute path to a SwiftUI iOS project and asked to audit typography, color and theming, components, layout and interaction, navigation and flow, or accessibility without modifying the target project.
---

# eb-analyze

## Overview

Analyze an iOS SwiftUI project for Apple Human Interface Guidelines and WCAG 2.2 compliance. The analyzer is read-only: never edit, create, delete, format, generate, or execute files inside `projectPath`; only read source files and produce one JSON report.

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
2. Group violations by `file_path`.
3. Compute per-file scores and project-wide `overall_score`, `ui_score`, `ux_score`, and `a11y_score`.
4. Compute `domain_summaries`.
5. Produce a 3-5 sentence non-technical `executive_summary`.
6. Emit exactly one JSON object matching `references/output-contract.md`.

Budget mode uses the same final envelope but slimmer violation objects.

## Output Rules

- Output JSON only, with no Markdown fences and no explanatory prose.
- Use relative paths from `projectPath` for `file_path`.
- Use 1-based `line_number` values.
- Preserve the schema enums exactly.
- Never modify or write inside `projectPath`.
