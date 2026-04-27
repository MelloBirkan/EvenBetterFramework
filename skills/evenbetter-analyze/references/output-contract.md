# Output Contract

Create `projectPath/.evenbetter/` if needed, write the final report JSON to `projectPath/.evenbetter/eb-analyze.json`, then emit the same single JSON object on stdout in `full` mode:

```json
{
  "project_path": "/abs/path",
  "platform": "swiftui",
  "guidelines": "Apple Human Interface Guidelines",
  "total_files": 0,
  "total_violations": 0,
  "critical_count": 0,
  "files": [
    {
      "file_path": "relative/path.swift",
      "violations": [ /* violation objects */ ],
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

`critical_count` = number of violations with `severity = "error"`. Budget mode uses the same envelope; per-violation shape is the slimmer one from the schema.

## Field Descriptions

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

## JSON-Only Rule

The final response must contain only the JSON object. Do not wrap it in Markdown fences, add commentary, or include partial diagnostic output. The stored file at `.evenbetter/eb-analyze.json` and the emitted JSON must be identical.
