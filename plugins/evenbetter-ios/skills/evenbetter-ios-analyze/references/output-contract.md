# Output Contract

Create `projectPath/.evenbetter/` if needed, write the final analyzer report JSON to `projectPath/.evenbetter/analyze-{N}.json`, update `projectPath/.evenbetter/manifest.json`, then reply with a concise summary. Do not include the analyzer report JSON body in the chat response after a successful run.

`N` is the next sequential analyzer run number. Start at `1`, or use `max(existing analyze-*.json, manifest.currentRun) + 1` when history exists.

## Analyzer Report

```json
{
  "run": {
    "number": 3,
    "createdAt": "2026-04-28T12:34:56Z",
    "previousRun": 2,
    "supersedes": ["analyze-2.json"],
    "status": "pending_validation"
  },
  "project_path": "/abs/path",
  "platform": "swiftui",
  "guidelines": "Apple Human Interface Guidelines",
  "html_report_data": {
    "brand": "EvenBetter",
    "report_title": "EvenBetter iOS HIG Report",
    "standard_label": "Apple Human Interface Guidelines",
    "project_name": "AppName",
    "project_path": "/abs/path",
    "framework": "SwiftUI",
    "hig_standard": "Apple Human Interface Guidelines",
    "scan_date": "2026-04-28T12:34:56Z",
    "summary": {
      "total": 0,
      "critical": 0,
      "high": 0,
      "medium": 0,
      "low": 0
    },
    "scan_context": {
      "frameworks": ["SwiftUI"],
      "framework_versions": {},
      "design_systems": ["Apple Human Interface Guidelines"],
      "component_patterns": [],
      "scan_duration": null,
      "files_scanned": 0,
      "confidence": null,
      "custom_utilities": []
    }
  },
  "total_files": 0,
  "total_violations": 0,
  "critical_count": 0,
  "files": [
    {
      "file_path": "relative/path.swift",
      "violations": [],
      "score": 0,
      "ui_score": 0,
      "ux_score": 0,
      "a11y_score": 0
    }
  ],
  "domain_summaries": [
    {
      "domain": "typography",
      "violation_count": 0,
      "error_count": 0,
      "warning_count": 0,
      "info_count": 0
    }
  ],
  "overall_score": 0,
  "ui_score": 0,
  "ux_score": 0,
  "a11y_score": 0,
  "executive_summary": "..."
}
```

`critical_count` = number of violations with `severity = "error"`. `html_report_data` carries the dashboard and scan-context fields consumed by the EvenBetter iOS HIG HTML template; the issue list itself is still sourced from `files[].violations[]` so validation and fix state remain authoritative. Budget mode uses the same envelope; per-violation shape is the slimmer one from the schema. Every violation in `files[].violations[]` must include `id`, `state`, an analyzer-generated `ai_fix_prompt`, and a `fix_options` array (1-4 entries, exactly one `recommended: true`).

## Run Fields

| Field | Type | Description |
|---|---|---|
| `run.number` | integer | Current analyzer run number, matching `analyze-{N}.json`. |
| `run.createdAt` | string | UTC ISO-8601 timestamp with `Z`. |
| `run.previousRun` | integer or null | Previous analyzer run number, or null on first run. |
| `run.supersedes` | array | Prior analyzer report filenames consumed as history. Usually the immediate previous report. |
| `run.status` | string | `pending_validation`, `validated`, `fixed`, or `partially_fixed`. Analyzer writes `pending_validation`; validator and fixer may later update this field. |

`projectPath` inputs are resolved before this contract is applied. When omitted, `projectPath` is the invocation working directory; when relative, it is resolved against that directory. Store the resolved absolute path in `project_path`.

## Report Fields

| Field | Type | Description |
|---|---|---|
| `project_path` | string | Resolved absolute project path. |
| `platform` | string | Always `swiftui` for successful analysis. |
| `guidelines` | string | Always `Apple Human Interface Guidelines`. |
| `html_report_data` | object | Data required by the EvenBetter iOS HIG HTML report template. |
| `html_report_data.brand` | string | Always `EvenBetter`. |
| `html_report_data.report_title` | string | Always `EvenBetter iOS HIG Report`. |
| `html_report_data.standard_label` | string | Always `Apple Human Interface Guidelines`. |
| `html_report_data.project_name` | string | Display name derived from `project_path` unless a project name is known. |
| `html_report_data.project_path` | string | Same resolved absolute path as `project_path`. |
| `html_report_data.framework` | string | Display framework, usually `SwiftUI`. |
| `html_report_data.hig_standard` | string | Display standard, usually `Apple Human Interface Guidelines`. |
| `html_report_data.scan_date` | string | Same timestamp as `run.createdAt`. |
| `html_report_data.summary.total` | integer | Count of current analyzer findings before validation. |
| `html_report_data.summary.critical` | integer | Count mapped from `severity = "error"` for the template. |
| `html_report_data.summary.high` | integer | Count mapped from `severity = "warning"` for the template. |
| `html_report_data.summary.medium` | integer | Count mapped from `severity = "info"` for the template. |
| `html_report_data.summary.low` | integer | Reserved for future low-priority display issues; write `0` unless the analyzer adds a lower severity. |
| `html_report_data.scan_context.frameworks` | array | Framework names shown in the collapsible scan context, usually `["SwiftUI"]`. |
| `html_report_data.scan_context.framework_versions` | object | Known framework/tool versions keyed by framework name; use `{}` when unknown. |
| `html_report_data.scan_context.design_systems` | array | Design systems or standards applied, usually `["Apple Human Interface Guidelines"]`. |
| `html_report_data.scan_context.component_patterns` | array | Detected SwiftUI/iOS patterns or analyzed domain names shown in the template. |
| `html_report_data.scan_context.scan_duration` | number or null | Analysis duration in seconds when known. |
| `html_report_data.scan_context.files_scanned` | integer | Same count as `total_files`. |
| `html_report_data.scan_context.confidence` | number or null | Overall analyzer confidence only when computed; otherwise `null`. |
| `html_report_data.scan_context.custom_utilities` | array | Project-specific UI helpers detected during inventory. |
| `total_files` | integer | Number of discovered SwiftUI `.swift` files analyzed. |
| `total_violations` | integer | Total number of violation objects across all domains. |
| `critical_count` | integer | Count of violations where `severity` is `error`. |
| `files` | array | One entry per analyzed SwiftUI source file, using paths relative to `projectPath`. |
| `files[].file_path` | string | Relative Swift source path. |
| `files[].violations` | array | All violations for that file. Empty for clean files. |
| `files[].score` | integer | 0-100 holistic file score. |
| `files[].ui_score` | integer | 0-100 file score for `dimension = "ui"`. |
| `files[].ux_score` | integer | 0-100 file score for `dimension = "ux"`. |
| `files[].a11y_score` | integer | 0-100 file score for `dimension = "accessibility"`. |
| `domain_summaries` | array | One entry for each of the six domains. |
| `domain_summaries[].domain` | string | Domain enum value. |
| `domain_summaries[].violation_count` | integer | Total violations for the domain. |
| `domain_summaries[].error_count` | integer | Total `error` violations for the domain. |
| `domain_summaries[].warning_count` | integer | Total `warning` violations for the domain. |
| `domain_summaries[].info_count` | integer | Total `info` violations for the domain. |
| `overall_score` | integer | 0-100 holistic project score. |
| `ui_score` | integer | 0-100 project score for UI rules. |
| `ux_score` | integer | 0-100 project score for UX rules. |
| `a11y_score` | integer | 0-100 project score for accessibility rules. |
| `executive_summary` | string | 3-5 sentence non-technical summary of compliance posture. |

The analyzer report is the source of truth for fix prompts. Validator reports may judge whether `ai_fix_prompt` is accurate, but they must not create replacement prompts. Fixer runs must consume selected analyzer prompts as guidance and apply source edits rather than writing new prompt artifacts.

## HTML Template Field Mapping

The EvenBetter browser report is based on the supplied bold modern audit template, adapted for iOS and Apple HIG. Analyze must produce all source fields needed by that template:

- Dashboard/header fields come from `html_report_data`: `project_name`, `project_path`, `framework`, `hig_standard`, `scan_date`, `summary`, and `scan_context`.
- Issue cards come from each violation: `id`, `summary`, `severity`, `rule_id`, `dimension`, `file_path`, `line_number`, `code_snippet`, `fix_description`, optional `fix_code`, `ai_fix_prompt`, `fix_options`, and `guideline_reference`.
- The HTML generator maps violation severities for display: `error -> critical`, `warning -> high`, `info -> medium`, and reserves `low` for future lower-priority issue types.
- The HTML generator maps `rule_id` to the displayed HIG criteria, `dimension` to the displayed HIG area, `fix_options` to the per-issue remediation menu, and `guideline_reference.url` to the inline Evidence link.

Do not duplicate violations inside `html_report_data.issues`; current issues are always derived from `files[].violations[]` so validator corrections and fixer state changes remain authoritative.

## Manifest

`projectPath/.evenbetter/manifest.json` is the portable source of truth for report history and run pairing:

```json
{
  "version": 1,
  "currentRun": 3,
  "latest": {
    "analyze": "analyze-3.json",
    "validate": "evenbetter-validate-1.json",
    "html_report": "evenbetter-validate-1.html"
  },
  "runs": [
    {
      "number": 1,
      "analyze": "analyze-1.json",
      "validate": "evenbetter-validate-1.json",
      "html_report": "evenbetter-validate-1.html",
      "validated": true,
      "createdAt": "2026-04-28T12:00:00Z",
      "status": "fixed",
      "summary": {
        "open": 0,
        "fixed": 12,
        "rejected": 3,
        "deferred": 1,
        "duplicate_of": 0
      }
    },
    {
      "number": 2,
      "analyze": "analyze-2.json",
      "validate": null,
      "html_report": null,
      "validated": false,
      "createdAt": "2026-04-28T12:20:00Z",
      "status": "partially_fixed",
      "summary": {
        "open": 2,
        "fixed": 5,
        "rejected": 0,
        "deferred": 1,
        "duplicate_of": 0
      }
    },
    {
      "number": 3,
      "analyze": "analyze-3.json",
      "validate": null,
      "html_report": null,
      "validated": false,
      "createdAt": "2026-04-28T12:34:56Z",
      "status": "pending_validation",
      "summary": {
        "open": 4,
        "fixed": 0,
        "rejected": 0,
        "deferred": 0,
        "duplicate_of": 0
      }
    }
  ]
}
```

The manifest is authoritative for run numbering, latest analyzer path, validation state, generated HTML report paths, and per-run state summaries. `latest.analyze` is the newest analyzer report. `latest.validate` is legacy compatibility for older validation JSON reports; new validator runs do not create validation JSON. `latest.html_report` is the newest generated browser report, or null when no HTML report exists. Per-run `analyze-{N}.json` files remain authoritative for the violations themselves.

## Backwards Compatibility

If `.evenbetter/analyze.json` exists and no `manifest.json` exists, auto-migrate it before writing a new numbered report:

1. Treat the legacy file as analyzer run 1.
2. Write the same JSON object to `.evenbetter/analyze-1.json`.
3. Add a `run` block to `analyze-1.json` if it is missing, using `number: 1`, `previousRun: null`, `supersedes: ["analyze.json"]`, and `status: "pending_validation"`.
4. Add missing violation `id` and default `state` fields when possible.
5. Initialize `manifest.json` with run 1, then write the new analysis as `analyze-2.json`.

Keep the legacy `.evenbetter/analyze.json` file untouched after migration unless the user explicitly asks to remove it. Do not use it as the latest report after `manifest.json` exists.

## State And Concurrency

Before writing a report or manifest update, reread the current manifest from disk. EvenBetter assumes serial execution: only one analyzer, validator, or fixer run writes `.evenbetter/` at a time. Do not create a lock file in this contract.

Old reports are kept indefinitely. Pruning and archival are out of scope for this skill.

## Chat Summary Rule

The final response for a successful analyzer run must be concise and human-readable. The stored file at `.evenbetter/analyze-{N}.json` is the complete analyzer report JSON artifact; do not paste, fence, or otherwise include the JSON body in chat. The manifest is written as a side effect and is not included in the chat response.

Use this response shape:

```text
Analysis complete.
- Wrote: .evenbetter/analyze-{N}.json
- Findings: <total> total (<error> error, <warning> warning, <info> info)

Next: use $evenbetter-validate to confirm the findings and generate the HTML report.
```

Compute `<total>` from `total_violations`, `<error>` from `critical_count` or summed `domain_summaries[].error_count`, and `<warning>` / `<info>` from summed `domain_summaries`.
