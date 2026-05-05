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

## 5. Run The Three Dimension Specialists

Run all six domains, batched by dimension into three specialists:

| Dimension | Domains | Corpus files |
|---|---|---|
| `ui` | `typography`, `color-theming` | `../../corpus/ios/typography.md`, `../../corpus/ios/color-theming.md` |
| `ux` | `components-patterns`, `layout-interaction`, `navigation-flow` | `../../corpus/ios/components-patterns.md`, `../../corpus/ios/layout-interaction.md`, `../../corpus/ios/navigation-flow.md` |
| `accessibility` | `accessibility` | `../../corpus/ios/accessibility.md` |

When the host supports independent sub-agents (Claude Code's `Agent` tool, Codex sub-agents, or equivalent), dispatch one specialized read-only dimension sub-agent per row in a single message so they execute concurrently. Each sub-agent is an expert for its assigned dimension and covers every domain in that row. When sub-agents are unavailable or not permitted, run the same domain passes sequentially in the main agent in this order: `typography`, `color-theming`, `components-patterns`, `layout-interaction`, `navigation-flow`, `accessibility`.

Only the analyzer orchestrator may write `.evenbetter/analyze-{N}.json` and `.evenbetter/manifest.json`. Dimension sub-agents are read-only on project source and may write only the per-domain JSON shards listed in their brief at `.evenbetter/tmp/run-{N}/<domain>.json`. They must not write source files, other `.evenbetter` files, cache files, or notes.

### 5a. Pre-Filter Candidate Files Per Domain

Before dispatching the dimension specialists, the orchestrator narrows each domain's candidate file list with a single Grep pass over the SwiftUI inventory. This eliminates redundant work — without it, every sub-agent would re-Grep the full inventory inside its own context window — and lets the orchestrator hand each agent a minimal, domain-relevant working set.

For each domain, run an alternation Grep across the inventory using the tokens below and keep only the relative paths of files with at least one match. The result is the `candidateFiles` array passed to that domain's slot in the dimension brief. If a domain matches zero files, still pass an empty array — the sub-agent will write an empty shard and aggregation continues normally.

| Domain | Tokens (case-sensitive regex; extend as the corpus evolves) |
|---|---|
| `typography` | `\.font\(`, `Text\(`, `\.bold\(`, `\.italic\(`, `\.fontWeight\(`, `\.dynamicTypeSize\(`, `\.lineLimit\(`, `\.tracking\(`, `\.kerning\(`, `@ScaledMetric` |
| `color-theming` | `\.foregroundColor\(`, `\.foregroundStyle\(`, `\.background\(`, `\.tint\(`, `\.accentColor\(`, `Color\(`, `Color\.`, `\.preferredColorScheme\(`, `UIColor` |
| `components-patterns` | `Button\(`, `Toggle\(`, `Picker\(`, `TextField\(`, `SecureField\(`, `Slider\(`, `Stepper\(`, `Menu\(`, `Form\(`, `Section\(`, `Label\(`, `DisclosureGroup` |
| `layout-interaction` | `VStack`, `HStack`, `ZStack`, `LazyV`, `LazyH`, `ScrollView`, `GeometryReader`, `\.frame\(`, `\.padding\(`, `spacing:`, `\.gesture\(`, `\.onTapGesture`, `\.swipeActions`, `\.onLongPress` |
| `navigation-flow` | `NavigationStack`, `NavigationView`, `NavigationLink`, `TabView`, `\.sheet\(`, `\.fullScreenCover\(`, `\.popover\(`, `\.alert\(`, `\.confirmationDialog`, `\.toolbar`, `\.navigationTitle`, `\.navigationBar` |
| `accessibility` | `accessibilityLabel`, `accessibilityHint`, `accessibilityValue`, `accessibilityIdentifier`, `accessibilityElement`, `accessibilityHidden`, `accessibilityAddTraits`, `accessibilityAction`, `\.accessibilityRepresentation` |

The orchestrator does not delegate this Grep to sub-agents — running it once at the orchestrator level is what makes the dimension brief affordable.

### 5b. Sub-Agent Brief Discipline (Context Budget)

Three parallel dimension sub-agents will still overflow the orchestrator's context if their briefs inline source files, schema text, or corpus text. Keep both directions lean.

**What the orchestrator sends to each dimension sub-agent (no exceptions):**

- `projectPath` — absolute path string.
- `mode` — `full` or `budget`.
- `dimension` — `ui`, `ux`, or `accessibility`.
- `domains` — array of objects, one per domain assigned to the dimension. Each entry contains:
  - `name` — domain name (e.g. `typography`).
  - `corpusPath` — absolute path to the matching `../../corpus/ios/<domain>.md`. Sub-agent reads it once with `Read`. Do not inline the corpus.
  - `candidateFiles` — orchestrator-filtered relative paths for the domain (see §5a). Never inline file contents, never inline line-indexed text. May be an empty array.
  - `outputPath` — absolute path to `projectPath/.evenbetter/tmp/run-{N}/<domain>.json`.
- The compact schema sketch for the active mode, inlined verbatim from below. Do not pass `references/schema.md` itself.

**Compact schema sketch — full mode (inline this block in the brief):**

```text
Each violation object MUST contain exactly these keys:
- rule_id: string matching an H2 clause ID in the cited corpusPath (e.g. "TYPO-UI-001").
- severity: "error" | "warning" | "info".
- dimension: "ui" | "ux" | "accessibility".
- domain: one of the assigned domain names.
- file_path: relative path from projectPath (POSIX separators).
- line_number: positive 1-based integer.
- code_snippet: the offending source verbatim (no paraphrase).
- summary: one-sentence description.
- why_fix: HIG / SwiftUI / accessibility rationale.
- guideline_reference: { label: string, url: string }. URL must be a real Apple HIG or Apple Developer page.
- fix_description: prose remediation.
- fix_code: corrected snippet.
- ai_fix_prompt: self-contained prompt that cites rule_id, file_path, line_number, the concrete change, and acceptance criteria.
- auto_fixable: boolean.
- fix_options: array of 1-4 entries, exactly one with recommended: true. Each entry has:
    id (kebab-case, unique within the violation),
    label (<= 60 chars),
    description (one sentence),
    kind ("minimal" | "structural" | "alternative-component" | "accessibility-only" | "defer-to-user"),
    recommended (boolean),
    code (corrected snippet for that option).
Do NOT emit `id` or `state` — the orchestrator adds them.
```

**Compact schema sketch — budget mode (inline this block in the brief):**

```text
Same shape as full mode, except:
- Drop `why_fix`, `fix_code`, and `auto_fixable` from each violation.
- Drop `code` from each entry of `fix_options`.
All other keys remain required.
```

**What the sub-agent does:**

1. For each entry in `domains`, reads `corpusPath` once to learn that domain's H2 clause IDs and rules.
2. Reads only the files in that entry's `candidateFiles` — on demand, no Grep, no recursive walk.
3. Builds a JSON array of violation objects scoped to that domain only, against H2 corpus clauses only, conforming to the inline schema sketch for the active mode.
4. Writes each domain's array to its corresponding `outputPath` with `Write`. Each shard contains the JSON array and nothing else.
5. Returns exactly one line summarizing all assigned domains, e.g. `Wrote ui findings: 7 typography, 4 color-theming.` Nothing else.

**What the sub-agent must not do:**

- Echo any JSON array back in chat.
- Read corpora outside the assigned `corpusPath` set.
- Read `corpus/index.json` (the orchestrator validates `rule_id` against it during aggregation).
- Read `references/schema.md` (the orchestrator inlines the compact sketch).
- Re-Grep or re-walk the inventory; trust the orchestrator's pre-filtered `candidateFiles`.
- Read or write any file under `.evenbetter/` other than the `outputPath` set in its brief.
- Emit findings outside its assigned `dimension` and `domains`.

Use this generic prompt shape:

```text
You are the <dimension> specialist for an EvenBetter iOS SwiftUI Apple HIG and accessibility analysis.

Inputs (paths only — read on demand, do not expect inline source content):
- projectPath: <absolute path>
- mode: <full|budget>
- dimension: <ui|ux|accessibility>
- domains: [
    { name: <domain>, corpusPath: <absolute>, candidateFiles: [<relative>...], outputPath: <absolute> },
    ...
  ]

<inline the active-mode compact schema sketch from references/workflow.md §5b>

Workflow:
1. For each entry in `domains`, Read its corpusPath once to learn H2 clause IDs and rules for that domain.
2. For each entry, Read only the files in candidateFiles. Do not Grep again, do not walk the project, do not read files not listed.
3. Produce a JSON array of violation objects for that domain only. Use only H2 corpus clauses; set rule_id to the matching clause ID exactly as written in corpusPath.
4. For every violation, include a self-contained ai_fix_prompt and a 1-4 entry fix_options array (exactly one recommended: true; distinct labels and descriptions; valid kind values; content aligned with the violation's top-level fix_description/fix_code/ai_fix_prompt). Conform to the inline schema sketch above for the active mode.
5. Write each domain's JSON array to its corresponding outputPath with the Write tool. Each file must contain the JSON array and nothing else.
6. Reply with exactly one line summarizing every assigned domain, e.g. "Wrote ui findings: 7 typography, 4 color-theming." Do not echo any JSON in chat.

Constraints:
- Read-only on project source.
- The only files you write are the outputPath values listed in `domains`.
- Do not read corpus/index.json, references/schema.md, or corpora outside your assigned set.
- Trust the orchestrator's candidateFiles; do not Grep or walk the inventory yourself.
- If a corpus clause is genuinely ambiguous for a real-world snippet, consult primary-source Apple documentation via the host's native web tools (WebSearch/WebFetch in Claude Code, equivalent elsewhere). Drop a finding before inventing a rule_id that is not present in the cited corpusPath.
- Do not include findings outside the assigned dimension and domains.
```

The same disk-shard discipline applies in the sequential fallback: even when running in-line, write each domain's array to its shard file before continuing to the next domain so the orchestrator's working memory does not accumulate six full violation arrays at once.

## 6. Validate And Enrich Domain Results

For each domain, read its shard from `projectPath/.evenbetter/tmp/run-{N}/<domain>.json`. If the shard is missing, empty, or unparseable JSON, treat that domain as zero findings and continue (do not fail the whole run on a single bad shard).

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
11. Require `fix_options` to be a 1-4 entry array with exactly one `recommended: true` entry, distinct labels and descriptions, valid `kind` values, and content aligned with the violation's top-level remediation fields. In budget mode, drop each option's `code` field.
12. Reject findings whose prompt or recommended option asks for broad redesign, unrelated refactoring, validation work, or future prompt generation instead of a concrete fix.
13. In `budget` mode, remove `why_fix`, `fix_code`, and `auto_fixable` if present, and strip `code` from each entry of `fix_options`.
14. In `full` mode, discard findings that cannot provide all required full-mode fields.
15. Generate `id` for each remaining violation using `references/schema.md`.
16. Add default `state` for each new violation.
17. For a matching violation ID found in previous analyzer reports, copy the latest prior `state` into the new violation so fixed, rejected, and deferred decisions persist across runs.
18. If the analyzer can confidently identify a duplicate of an earlier violation with a different ID, set `state.status` to `duplicate_of` and `state.duplicateOf` to the earlier ID.

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

After `analyze-{N}.json` and `manifest.json` have been written, remove `projectPath/.evenbetter/tmp/run-{N}/` and remove `projectPath/.evenbetter/tmp/` if it is now empty. The transient shard directory must not survive into the validator handoff. Cleanup failure is non-fatal but should be reported in the run's chat summary as a notice.

The stored analyzer JSON remains the complete machine-readable artifact. The chat response must not include that JSON body.

Reply with this concise summary only:

```text
Analysis complete.
- Wrote: .evenbetter/analyze-{N}.json
- Findings: <total> total (<error> error, <warning> warning, <info> info)

Next: use /evenbetter-validate to confirm the findings and generate the HTML report.
```

Compute `<total>` from `total_violations`, `<error>` from `critical_count` or summed `domain_summaries[].error_count`, and `<warning>` / `<info>` from summed `domain_summaries`.

## 12. Optional Validator Handoff

If `skills/evenbetter-validate/SKILL.md` exists in the workspace and the user or host requests validation, invoke `evenbetter-validate` as a separate skill against the same `projectPath` after `.evenbetter/analyze-{N}.json` and `.evenbetter/manifest.json` are written. Validation corrects the analyzer JSON in place, marks the run as validated in `manifest.json`, and generates `.evenbetter/evenbetter-validate-{N}.html`; it does not write `.evenbetter/evenbetter-validate-{N}.json`.

For analyzer runs that also request validation, keep the analyzer summary separate from validator output. The analyzer summary should still prompt the user to run `/evenbetter-validate` unless validation was already requested and completed in the same interaction.

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
- six domain names and corpus paths grouped under three dimensions: `ui` (typography, color-theming), `ux` (components-patterns, layout-interaction, navigation-flow), `accessibility` (accessibility)
- spawn three specialized read-only dimension sub-agents (one per UI/UX/accessibility row) when the host supports sub-agents; otherwise run the six domain passes sequentially in domain table order
- the orchestrator pre-filters candidate Swift files per domain with a single Grep pass over the inventory using the §5a token table and passes each domain's filtered list in the dimension brief; sub-agents do not re-Grep or re-walk the inventory
- sub-agent briefs carry only paths (projectPath, per-domain corpusPath, per-domain candidateFiles, per-domain outputPath) plus mode and dimension — never inline source content, corpus text, `corpus/index.json`, or `references/schema.md`
- the orchestrator inlines a compact required-fields schema sketch for the active mode in the brief instead of passing `references/schema.md`
- sub-agents write one JSON array per assigned domain to `.evenbetter/tmp/run-{N}/<domain>.json` and reply with a single line summarizing all domains; the orchestrator reads shards from disk during aggregation
- the transient `.evenbetter/tmp/run-{N}/` directory is removed after the final report and manifest are written
- schema field sets for `full` and `budget`
- analyzer creates all `ai_fix_prompt` values directly in the JSON report
- analyzer creates `html_report_data` for the EvenBetter iOS HIG HTML template, while current issue cards still come from `files[].violations[]`
- domain, severity, dimension, state, and run status enums
- stable violation ID inputs and SHA-256 prefix rule
- aggregation and scoring contract
- source-safe discipline and the numbered report plus manifest writes
- final output envelope keys
- successful analysis prompts the user to run `/evenbetter-validate`
