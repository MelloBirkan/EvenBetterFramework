---
name: evenbetter-ios-analyze
description: iOS SwiftUI Apple HIG, UX, UI, and accessibility analyzer. Use when run from or given a SwiftUI iOS project directory and asked to audit typography, color and theming, components, layout and interaction, navigation and flow, or accessibility; defaults to the current working directory when no project path is provided, dispatches one read-only Claude Code sub-agent per iOS domain (or sequential passes when sub-agents are unavailable), uses the bundled corpus first and falls back to Ref/Exa for primary-source documentation when the corpus is uncertain, generates analyzer-owned ai_fix_prompt and fix_options for every finding, populates the EvenBetter iOS HIG html_report_data block, and stores numbered reports in the project's .evenbetter folder.
---

# evenbetter-ios-analyze

## Overview

First pass of the EvenBetter iOS audit loop. Read SwiftUI source files without modifying them, dispatch one specialized read-only sub-agent per iOS domain, produce HIG-grounded violations with both an `ai_fix_prompt` and a structured `fix_options` menu, populate `html_report_data` for the browser template, and write the numbered report to `projectPath/.evenbetter/analyze-{N}.json`. After a successful run, do not echo the JSON body in chat — reply with the brief summary defined in `references/output-contract.md` and prompt the user to run `/evenbetter-validate`.

Do not edit, delete, format, generate, or execute source/project files inside `projectPath`. The only permitted writes inside `projectPath` are creating `.evenbetter/` if needed, auto-migrating a legacy `.evenbetter/analyze.json` into numbered history, writing the final report JSON to `.evenbetter/analyze-{N}.json`, updating `.evenbetter/manifest.json`, and creating a transient `.evenbetter/tmp/run-{N}/` working directory for per-domain sub-agent JSON shards that must be removed before the run ends.

## Inputs

- `projectPath` (optional): Filesystem path to a SwiftUI iOS project. Default to the host's current working directory when omitted or `.`.
- `mode` (optional): `full` or `budget`. Default to `full`.

Resolve `projectPath` to an absolute path before use. If the user supplies a relative path, resolve it against the host's current working directory. Do not ask for a full path solely because `projectPath` is omitted or relative.

## Required References

Load these files only when their phase runs:

- `references/workflow.md`: Coordinator workflow, domain dispatch, aggregation, scoring, executive summary style, and compaction-safe invariants.
- `references/schema.md`: Violation object schema for `full` and `budget` modes, including `fix_options`.
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

Run all six iOS SwiftUI domains. When the host environment supports independent sub-agents, such as Claude Code's `Agent` tool or Codex sub-agents, spawn one specialized read-only sub-agent per domain and run them concurrently in a single message — this is the default execution path under Claude Code. When sub-agents are unavailable, run the same six domain passes sequentially in the main agent.

Sub-agent briefs must stay slim so six parallel agents do not blow the orchestrator's context. The orchestrator never inlines source file contents, the corpus, the schema, or `index.json` into the brief; it only passes filesystem paths the sub-agent reads on demand. The orchestrator never asks the sub-agent to return its JSON array inline; the sub-agent writes its array to a per-domain shard file and returns only a one-line status.

In Claude Code specifically, dispatch each domain via `Agent` with `subagent_type: "general-purpose"` and pass it exactly:

1. The resolved absolute `projectPath`.
2. `mode` (`full` or `budget`).
3. `candidateFiles`: the list of relative Swift file *paths* in the inventory (no file contents, no line-indexed text).
4. `corpusPath`: absolute path to the matching domain corpus file (the sub-agent reads it once with its own `Read` tool).
5. `schemaPath`: absolute path to `references/schema.md`.
6. `outputPath`: absolute path to `projectPath/.evenbetter/tmp/run-{N}/{domain}.json` where the sub-agent must write its JSON array.

The sub-agent reads its corpus, opens only the candidate files it needs (using `Grep` to skip files with no domain-relevant tokens), produces violations against H2 corpus clauses only, writes the JSON array to `outputPath` with its `Write` tool, and returns a single line such as `Wrote 12 typography findings to <outputPath>.` It must not echo the JSON array back to the orchestrator. Use parallel `Agent` calls in one message when sub-agents are available.

| Domain | Corpus path |
|---|---|
| `typography` | `../../corpus/ios/typography.md` |
| `color-theming` | `../../corpus/ios/color-theming.md` |
| `components-patterns` | `../../corpus/ios/components-patterns.md` |
| `layout-interaction` | `../../corpus/ios/layout-interaction.md` |
| `navigation-flow` | `../../corpus/ios/navigation-flow.md` |
| `accessibility` | `../../corpus/ios/accessibility.md` |

Each domain worker is read-only. Workers must use only H2 corpus clauses from their assigned file, set `rule_id` to the matching clause ID, emit findings only inside their own `domain`, and never modify source/project files, `.evenbetter` files, cache files, or notes.

Each finding must include both an `ai_fix_prompt` (for autonomous fix workflows) and a `fix_options` array of 1-4 concrete remediation alternatives (for the user-facing `/evenbetter-fix` flow). One option must be `recommended: true` and must mirror the violation's top-level `fix_description`/`fix_code`/`ai_fix_prompt`. Provide alternatives whenever multiple legitimate paths satisfy the same rule (e.g., for an undersized tap target: enlarge frame, wrap content in a `Button`, promote to a Tab Bar item).

## Documentation Lookup Fallbacks

Prefer the bundled corpus. When a corpus clause is genuinely ambiguous for a real-world Swift snippet, the analyzer (or any domain worker) may consult primary-source Apple documentation through the host AI agent's native tools — `WebSearch` and `WebFetch` in Claude Code, equivalent native lookups in other hosts. Do not rely on third-party MCP search servers.

Only use these tools to confirm a finding or correct a `guideline_reference.url`. They must not generate violations that lack a corresponding corpus clause: the analyzer's `rule_id` always maps to `../../corpus/index.json`. If documentation research uncovers a real issue without a matching corpus clause, drop the finding rather than emit an unsupported `rule_id`.

## Aggregation

After all six domain sub-agents return their one-line status messages:

0. Read each `projectPath/.evenbetter/tmp/run-{N}/{domain}.json` shard from disk, parse it as JSON, and treat it as the domain's violation array. If a shard is missing or unparseable, treat that domain as returning zero findings and continue.
1. Validate every violation against `references/schema.md`, including non-empty `ai_fix_prompt` and a well-formed `fix_options` array with exactly one `recommended: true` entry.
2. Reject findings whose `ai_fix_prompt` or recommended `fix_options` entry is missing, generic, or not grounded in the cited source file, rule, severity, and intended remediation.
3. Add stable `id` and default `state` fields to every violation.
4. Load `.evenbetter/manifest.json` when present and carry forward the latest prior state for matching violation IDs.
5. Group violations by `file_path`.
6. Compute per-file scores and project-wide `overall_score`, `ui_score`, `ux_score`, and `a11y_score`.
7. Compute `domain_summaries`.
8. Produce a 3-5 sentence non-technical `executive_summary`.
9. Populate `html_report_data` for the EvenBetter iOS HIG HTML template, including project metadata, severity dashboard counts, and scan context.
10. Store exactly that JSON object at `projectPath/.evenbetter/analyze-{N}.json`, creating `.evenbetter/` if needed.
11. Update `.evenbetter/manifest.json` with run `N`, latest analyzer path, validation status, and state summary.
12. Remove the transient `projectPath/.evenbetter/tmp/run-{N}/` directory (and `tmp/` if empty) once `analyze-{N}.json` and the manifest have been written. Failure to clean up is not fatal, but the directory must not persist into the validator handoff.
13. Reply with the concise human-readable summary defined in `references/output-contract.md`. Do not include the analyzer report JSON body in the chat response.

Budget mode uses the same final envelope but slimmer violation objects (no `why_fix`, `fix_code`, `auto_fixable`, and no per-option `code`).

## Output Rules

- For successful analysis runs, write results to `.evenbetter/analyze-{N}.json` and `.evenbetter/manifest.json`; do not echo the analyzer JSON body in chat.
- Reply with this concise summary shape:

```text
Analysis complete.
- Wrote: .evenbetter/analyze-{N}.json
- Findings: <total> total (<error> error, <warning> warning, <info> info)

Next: use /evenbetter-validate to confirm the findings and generate the HTML report.
```

- Compute `<total>` from `total_violations`, `<error>` from `critical_count` or summed `domain_summaries[].error_count`, and `<warning>` / `<info>` from summed `domain_summaries`.
- Use relative paths from `projectPath` for `file_path`.
- Use 1-based `line_number` values.
- Preserve the schema enums exactly.
- Generate stable violation IDs from `rule_id`, relative `file_path`, line or symbol anchor, and normalized summary text.
- Include `run` metadata and violation `state` objects exactly as defined in `references/output-contract.md` and `references/schema.md`.
- Include `html_report_data` exactly as defined in `references/output-contract.md`; it provides the EvenBetter iOS HIG report dashboard and scan-context data, while issue cards are derived from violations.
- Include both a specific `ai_fix_prompt` and a structured `fix_options` array in every violation. Validators may judge their accuracy; only the analyzer creates them.
- Never modify source or project files inside `projectPath`.
- The only permitted project writes are numbered analyzer reports, `manifest.json`, and documented legacy report migration inside `projectPath/.evenbetter/`.
- End the chat summary by prompting the user to run `/evenbetter-validate`; validation corrects the analyzer JSON in place and generates the browser report.
