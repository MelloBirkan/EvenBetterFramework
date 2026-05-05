# Output Contract

Validate writes corrections into the selected analyzer report. It does not create a separate validation JSON artifact.

## Written Files

For analyzer run `N`, update:

```text
projectPath/.evenbetter/analyze-{N}.json
projectPath/.evenbetter/manifest.json
projectPath/.evenbetter/evenbetter-validate-{N}.html
```

The HTML path intentionally keeps the historical filename for compatibility, but the page content is an issue report, not a validation-status report.

Legacy compatibility: older skill versions wrote `.evenbetter/evenbetter-validate-{N}.json` files with `kept`, `severity_adjusted`, and `dropped` decision buckets. New validator runs must not create those JSON files, but the HTML generator may accept one as `--validation` input, or as the `--analyze` input when it can resolve the paired analyzer report, so existing validated issue data can still populate the browser report.

## Analyzer JSON Corrections

Use `analyze-{N}.json` as the source of truth. For every actionable finding:

- Keep real issues in `files[].violations[]`.
- Correct `severity` in place when evidence shows the analyzer chose the wrong severity.
- Correct `guideline_reference` in place when the issue is real but the URL or label points to the wrong Apple HIG or Apple Developer source.
- Correct `html_report_data` in place when analyzer dashboard or scan-context fields are missing, stale, or inconsistent with the selected analyzer report.
- Leave `ai_fix_prompt` unchanged when accurate.
- Reject unsupported findings by mutating only the existing `state` object:

```json
{
  "status": "rejected",
  "decidedIn": 3,
  "decidedBy": "validator",
  "reason": "Source evidence does not support this as a HIG violation.",
  "duplicateOf": null
}
```

Reject instead of keeping when:

- source evidence does not support the finding
- confidence is below `confidence_threshold`
- the corpus clause cannot be resolved
- no valid primary-source guideline URL can be verified or corrected
- the finding is internally inconsistent with the source excerpt
- `ai_fix_prompt` is missing, vague, or inaccurate

Do not delete rejected findings from analyzer JSON. Do not add validation result wrappers, decision buckets, confidence fields, or validation status fields to individual violations.

## Recomputed Analyzer Fields

After corrections, recompute analyzer aggregate fields from non-rejected, non-fixed, non-duplicate current issues unless a field explicitly summarizes all historical violations:

- `total_violations`
- `critical_count`
- `domain_summaries[].violation_count`
- `domain_summaries[].error_count`
- `domain_summaries[].warning_count`
- `domain_summaries[].info_count`
- `files[].score`
- `files[].ui_score`
- `files[].ux_score`
- `files[].a11y_score`
- project `overall_score`, `ui_score`, `ux_score`, and `a11y_score`
- `executive_summary` when rejected or corrected findings materially change the user-facing compliance posture
- `html_report_data.summary`
- `html_report_data.scan_context.files_scanned`
- `html_report_data.project_name`, `project_path`, `framework`, `hig_standard`, and `scan_date` when missing or inconsistent with the analyzer run

Do not rewrite code snippets, fix descriptions, fix code, summaries, or `ai_fix_prompt` unless the analyzer field is directly wrong and the correction is explicitly permitted above.

## Analyzer HTML Template Data

Validate must verify the selected analyzer report includes `html_report_data` for the adapted EvenBetter iOS HIG HTML template. If missing or stale, add or correct only this top-level object; do not duplicate the issue list inside it.

Required `html_report_data` fields:

- `brand: "EvenBetter"`
- `report_title: "EvenBetter iOS HIG Report"`
- `standard_label: "Apple Human Interface Guidelines"`
- `project_name`
- `project_path`
- `framework`
- `hig_standard`
- `scan_date`
- `summary.total`
- `summary.critical`
- `summary.high`
- `summary.medium`
- `summary.low`
- `scan_context.frameworks`
- `scan_context.framework_versions`
- `scan_context.design_systems`
- `scan_context.component_patterns`
- `scan_context.scan_duration`
- `scan_context.files_scanned`
- `scan_context.confidence`
- `scan_context.custom_utilities`

Issue-card fields remain sourced from analyzer violations: canonical `files[].violations[]`, or top-level `violations[]` only when reading older flat analyzer reports. Required issue-card fields are `id`, `summary`, `severity`, `rule_id`, `dimension`, `file_path`, `line_number`, `code_snippet`, `fix_description`, optional `fix_code`, `ai_fix_prompt`, and `guideline_reference`.

## Manifest

Update the matching manifest run entry:

- `validated: true`
- `status: "validated"` unless it is already `fixed` or `partially_fixed`
- `html_report: "evenbetter-validate-{N}.html"` or `.evenbetter/evenbetter-validate-{N}.html`, matching the manifest's existing path style
- `summary` recomputed from violation `state.status` values in the corrected analyzer report

Update `latest.html_report` to the generated HTML report when the manifest has a `latest` object. Preserve `latest.analyze`, `latest.validate`, `currentRun`, legacy per-run `validate` fields, and unrelated run entries. New validation runs must not set per-run `validate` to a new JSON file because no validation JSON is written.

Update `analyze-{N}.json` `run.status` to `validated` unless it is already `fixed` or `partially_fixed`.

## HTML Report

Generate `projectPath/.evenbetter/evenbetter-validate-{N}.html` with `scripts/generate_html_report.py` after analyzer and manifest updates succeed. The generator must:

- Read `analyze-{N}.json` and optional `manifest.json`.
- Populate issues from canonical `files[].violations[]`; if `files[]` is missing and top-level `violations[]` exists, group flat violations by `file_path` and render those as issue cards.
- Render only current issues: `state.status = "open"` or `state.status = "deferred"`.
- Exclude `fixed`, `rejected`, and `duplicate_of` findings.
- Populate the Current Code panel from `code_snippet` when present. If older analyzer output used another source-code field name, or if the snippet is missing, use available source-context excerpts or read the cited source file from `project_path` and `file_path` at the reported line range.
- Tolerate legacy per-finding visible states or validation decisions such as `validated`, `kept`, and `severity_adjusted` when regenerating HTML from older reports.
- When a legacy validation report is supplied, include the validator-kept and severity-adjusted issue cards, exclude dropped findings, and source issue details and `ai_fix_prompt` from each result's `original_violation` when the paired analyzer report cannot be loaded.
- Use `html_report_data` for the EvenBetter iOS HIG dashboard and scan context, correcting it before generation when needed.
- Derive issue-card display fields such as title, description, recommended fix, language, HIG criteria, and HIG area from analyzer violations.
- Render inline HIG/evidence links per issue from `guideline_reference.url`, legacy validation `supporting_links`, and validation `corpus_clause.source_url` when present.
- Keep the supplied visual standard adapted to EvenBetter and iOS HIG: summary dashboard, severity filtering, search, AI prompt copying, code/fix comparison, and the same compact inline evidence style.
- Avoid validation-status UI: no `kept`, `dropped`, `severity_adjusted`, `not_validated`, confidence, retention, or validation decision blocks.

Run the generator with:

```text
scripts/generate_html_report.py --analyze projectPath/.evenbetter/analyze-{N}.json --manifest projectPath/.evenbetter/manifest.json --output projectPath/.evenbetter/evenbetter-validate-{N}.html
```

For legacy report regeneration only, the generator also accepts:

```text
scripts/generate_html_report.py --analyze projectPath/.evenbetter/analyze-{N}.json --validation projectPath/.evenbetter/evenbetter-validate-{N}.json --manifest projectPath/.evenbetter/manifest.json --output projectPath/.evenbetter/evenbetter-validate-{N}.html
```

## Chat Summary

In interactive chat, respond with a concise summary:

```text
Validation complete.
- Updated: .evenbetter/analyze-{N}.json
- HTML report: .evenbetter/evenbetter-validate-{N}.html
- Current issues: <total> total (<error> error, <warning> warning, <info> info)
- Corrections: <severity> severity, <links> guideline links, <rejected> rejected

Open the HTML report in a browser by holding Command and clicking the left mouse button on the path. To apply corrections, use $evenbetter-fix.
```

When invoked by automation, keep stdout concise and do not emit a validation report JSON object.
