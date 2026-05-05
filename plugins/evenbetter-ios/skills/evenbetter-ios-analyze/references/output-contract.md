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

`critical_count` = number of violations with `severity = "error"`. Budget mode uses the same envelope; per-violation shape is the slimmer one from the schema. Every violation in `files[].violations[]` must include `id`, `state`, and an analyzer-generated `ai_fix_prompt`.

## Run Fields

| Field | Type | Description |
|---|---|---|
| `run.number` | integer | Current analyzer run number, matching `analyze-{N}.json`. |
| `run.createdAt` | string | UTC ISO-8601 timestamp with `Z`. |
| `run.previousRun` | integer or null | Previous analyzer run number, or null on first run. |
| `run.supersedes` | array | Prior analyzer report filenames consumed as history. Usually the immediate previous report. |
| `run.status` | string | `pending_validation`, `validated`, `fixed`, or `partially_fixed`. Analyzer writes `pending_validation`; validator and fixer may later update this field. |

## Report Fields

| Field | Type | Description |
|---|---|---|
| `project_path` | string | Absolute path received as `projectPath`. |
| `platform` | string | Always `swiftui` for successful analysis. |
| `guidelines` | string | Always `Apple Human Interface Guidelines`. |
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

## Manifest

`projectPath/.evenbetter/manifest.json` is the portable source of truth for report history and run pairing:

```json
{
  "version": 1,
  "currentRun": 3,
  "latest": {
    "analyze": "analyze-3.json",
    "validate": "evenbetter-validate-1.json"
  },
  "runs": [
    {
      "number": 1,
      "analyze": "analyze-1.json",
      "validate": "evenbetter-validate-1.json",
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

The manifest is authoritative for run numbering, latest analyzer/validator paths, validation pairing, and per-run state summaries. `latest.analyze` is the newest analyzer report. `latest.validate` is the newest validation report across all runs, or null when no validation report exists. Per-run `analyze-{N}.json` files remain authoritative for the violations themselves.

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
```

Compute `<total>` from `total_violations`, `<error>` from `critical_count` or summed `domain_summaries[].error_count`, and `<warning>` / `<info>` from summed `domain_summaries`.
