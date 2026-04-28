# Output Contract

Write the final validation report to `projectPath/.evenbetter/evenbetter-validate.json` and emit the same JSON object when running headless:

```json
{
  "project_path": "/abs/path",
  "input_report": "/abs/path/.evenbetter/analyze.json",
  "confidence_threshold": 0.7,
  "total_high_input": 0,
  "kept_count": 0,
  "downgraded_count": 0,
  "dropped_count": 0,
  "retention_rate": 0.0,
  "mean_confidence": 0.0,
  "time_per_finding_ms": 0.0,
  "kept": [],
  "downgraded": [],
  "dropped": []
}
```

## Result Object

Each item in `kept`, `downgraded`, or `dropped` must include:

| Field | Type | Description |
|---|---|---|
| `decision` | string | `kept`, `downgraded`, or `dropped`. |
| `confidence` | number | Validator confidence from `0.0` to `1.0`. |
| `reasoning` | string | Concise evidence-based explanation. |
| `original_violation` | object | The complete original analyzer violation. |
| `source_context` | object | `{ "file_path": string, "line_start": integer, "line_end": integer, "excerpt": string }`. |
| `corpus_clause` | object | `{ "rule_id": string, "reference_file": string, "heading": string, "text": string }`. |
| `url_verification` | object | JSON emitted by `scripts/verify_url.py`. |

Items in `downgraded` must also include:

| Field | Type | Description |
|---|---|---|
| `downgraded_severity` | string | Always `warning`. |

Items in `dropped` must also include:

| Field | Type | Allowed values |
|---|---|---|
| `drop_reason` | string | `low_confidence`, `url_unreachable`, `clause_not_found`, or `reasoning_incoherent`. |

## Kept Invariants

Every item in `kept` must satisfy:

- `confidence >= confidence_threshold`
- `url_verification.ok == true`
- `url_verification.status_code == 200`
- `corpus_clause.text` is non-empty
- `reasoning` explains why the source excerpt violates the cited rule

## Aggregate Fields

| Field | Type | Description |
|---|---|---|
| `project_path` | string | Absolute `projectPath` received as input. |
| `input_report` | string | Absolute path to `.evenbetter/analyze.json`. |
| `confidence_threshold` | number | Threshold used for `kept` decisions. |
| `total_high_input` | integer | Count of input violations where `severity` is `error`. |
| `kept_count` | integer | Number of retained high-severity findings. |
| `downgraded_count` | integer | Number of high-severity inputs downgraded to warning. |
| `dropped_count` | integer | Number of high-severity inputs removed. |
| `retention_rate` | number | `kept_count / total_high_input`, rounded to four decimals. |
| `mean_confidence` | number | Mean confidence across processed findings, rounded to four decimals. |
| `time_per_finding_ms` | number | Mean validation time per processed finding, rounded to one decimal. |

## JSON-Only Rule

When invoked headless, output only the JSON object. Do not wrap it in Markdown fences, add commentary, or include partial diagnostic output.
