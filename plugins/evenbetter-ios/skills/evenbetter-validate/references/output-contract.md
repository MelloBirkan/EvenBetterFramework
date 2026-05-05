# Output Contract

Write the final validation report to `projectPath/.evenbetter/evenbetter-validate-{N}.json`, where `N` matches the analyzer run being validated, and emit the same JSON object when running headless:

```json
{
  "project_path": "/abs/path",
  "input_report": "/abs/path/.evenbetter/analyze-3.json",
  "validates": "analyze-3.json",
  "analyzer_run": 3,
  "html_report": ".evenbetter/evenbetter-validate-3.html",
  "createdAt": "2026-04-28T12:40:00Z",
  "confidence_threshold": 0.7,
  "total_validated_input": 0,
  "kept_count": 0,
  "severity_adjusted_count": 0,
  "dropped_count": 0,
  "retention_rate": 0.0,
  "mean_confidence": 0.0,
  "time_per_finding_ms": 0.0,
  "kept": [],
  "severity_adjusted": [],
  "dropped": []
}
```

## Run Pairing

| Field | Type | Description |
|---|---|---|
| `input_report` | string | Absolute path to `.evenbetter/analyze-{N}.json`. |
| `validates` | string | Analyzer report filename, e.g. `analyze-3.json`. |
| `analyzer_run` | integer | Analyzer run number `N`; must match both report filenames. |
| `html_report` | string | Relative path to the generated browser report, e.g. `.evenbetter/evenbetter-validate-3.html`. |
| `createdAt` | string | UTC ISO-8601 timestamp with `Z`. |

The validator must update `.evenbetter/manifest.json` after a successful write so the matching `runs[]` entry has:

- `validate: "evenbetter-validate-{N}.json"`
- `validated: true`
- `status: "validated"` unless the run was already marked `fixed` or `partially_fixed`
- `summary` recomputed from the paired analyzer report's violation states
- `latest.validate: "evenbetter-validate-{N}.json"` when this is the newest validation report by `createdAt`

It may also update `analyze-{N}.json` `run.status` to `validated`. It must not rewrite analyzer violation objects except for preserving existing state when the file is touched for the run status update. It must not create, revise, or backfill analyzer `ai_fix_prompt` values.

After the JSON report and manifest updates succeed, the validator must generate the derived HTML report at `projectPath/.evenbetter/evenbetter-validate-{N}.html`. The HTML report is populated from the paired analyzer report plus this validation report; it is not the source of truth for decisions.

## Result Object

Each item in `kept`, `severity_adjusted`, or `dropped` must include:

| Field | Type | Description |
|---|---|---|
| `decision` | string | `kept`, `severity_adjusted`, or `dropped`. |
| `confidence` | number | Validator confidence from `0.0` to `1.0`. |
| `reasoning` | string | Concise evidence-based explanation. |
| `original_violation` | object | The complete original analyzer violation, including `id` and `state`. |
| `source_context` | object | `{ "file_path": string, "line_start": integer, "line_end": integer, "excerpt": string }`. |
| `corpus_clause` | object | `{ "clause_id": string, "reference_file": string, "heading": string, "text": string, "source_url": string, "retrieved": string, "corpus_version": string }`. |
| `url_verification` | object | JSON emitted by `scripts/verify_url.py`. |
| `severity_assessment` | object | `{ "original": "error" \| "warning" \| "info", "correct": "error" \| "warning" \| "info", "reasoning": string }`. |
| `fix_prompt_assessment` | object | `{ "accurate": boolean, "reasoning": string }`; evaluates the analyzer-provided `ai_fix_prompt` without replacing it. |
| `supporting_links` | array | Optional evidence links used by validation, each shaped as `{ "label": string, "url": string, "source": "guideline" \| "corpus" \| "web", "reason": string }`. May be empty. |

Items in `severity_adjusted` must also include:

| Field | Type | Description |
|---|---|---|
| `corrected_severity` | string | Correct severity, one of `error`, `warning`, or `info`. |

Items in `dropped` must also include:

| Field | Type | Allowed values |
|---|---|---|
| `drop_reason` | string | `low_confidence`, `url_unreachable`, `clause_not_found`, `reasoning_incoherent`, `not_a_violation`, `fix_prompt_missing`, or `fix_prompt_inaccurate`. |

## Kept Invariants

Every item in `kept` must satisfy:

- `confidence >= confidence_threshold`
- `url_verification.ok == true`
- `url_verification.status_code == 200`
- `corpus_clause.text` is non-empty
- `reasoning` explains why the source excerpt violates the cited rule
- `severity_assessment.original == severity_assessment.correct`
- `fix_prompt_assessment.accurate == true`
- every `supporting_links[].url` is a working, relevant evidence link when present

Every item in `severity_adjusted` must satisfy the same evidence and prompt requirements as `kept`, but `severity_assessment.correct` differs from the analyzer's original severity.

## Aggregate Fields

| Field | Type | Description |
|---|---|---|
| `project_path` | string | Absolute `projectPath` received as input. |
| `html_report` | string | Relative path to `.evenbetter/evenbetter-validate-{N}.html`. |
| `confidence_threshold` | number | Threshold used for retained decisions. |
| `total_validated_input` | integer | Count of input violations whose state is actionable for validation. |
| `kept_count` | integer | Number of retained findings whose original severity and fix prompt are accurate. |
| `severity_adjusted_count` | integer | Number of real findings whose severity needed correction. |
| `dropped_count` | integer | Number of inputs removed from the validated set. |
| `retention_rate` | number | `(kept_count + severity_adjusted_count) / total_validated_input`, rounded to four decimals. |
| `mean_confidence` | number | Mean confidence across processed findings, rounded to four decimals. |
| `time_per_finding_ms` | number | Mean validation time per processed finding, rounded to one decimal. |

## Backwards Compatibility

If no `manifest.json` exists but `.evenbetter/analyze.json` exists, perform the analyzer legacy migration first: write `analyze-1.json`, add missing `run`, `id`, and `state` fields when possible, initialize `manifest.json`, and validate run 1. Do not treat `.evenbetter/analyze.json` as the latest report once the manifest exists.

## HTML Report

Generate `projectPath/.evenbetter/evenbetter-validate-{N}.html` with `scripts/generate_html_report.py` after the validation JSON is written. The generator must:

- Read `analyze-{N}.json`, `evenbetter-validate-{N}.json`, and `manifest.json` when present.
- Flatten all analyzer `files[].violations[]` into the HTML `issues[]` view.
- Join validation decisions by matching each validation result's `original_violation.id` to analyzer violation `id`.
- Derive template-only fields such as `title`, `description`, `recommended_fix`, `language`, and `scan_context` without adding them to the analyzer JSON.
- Render issue-level evidence links from validation `supporting_links`, analyzer `guideline_reference.url`, and validation `corpus_clause.source_url` when present.
- Show analyzer findings as `not_validated` only when they were excluded by state or when the validation report predates the all-actionable validation contract.

## JSON-Only Rule

When invoked headless, output only the validation report object. Do not wrap it in Markdown fences, add commentary, or include partial diagnostic output. The manifest and HTML report are written as side effects and are not included in stdout beyond the `html_report` path field.
