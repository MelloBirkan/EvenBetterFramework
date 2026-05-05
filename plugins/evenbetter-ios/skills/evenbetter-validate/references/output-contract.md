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

## Analyzer JSON Corrections

Use `analyze-{N}.json` as the source of truth. For every actionable finding:

- Keep real issues in `files[].violations[]`.
- Correct `severity` in place when evidence shows the analyzer chose the wrong severity.
- Correct `guideline_reference` in place when the issue is real but the URL or label points to the wrong HIG, developer.apple.com, or WCAG source.
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

Do not rewrite code snippets, fix descriptions, fix code, summaries, or `ai_fix_prompt` unless the analyzer field is directly wrong and the correction is explicitly permitted above.

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
- Render only current issues: `state.status = "open"` or `state.status = "deferred"`.
- Exclude `fixed`, `rejected`, and `duplicate_of` findings.
- Derive template-only fields such as display title, description, recommended fix, language, and scan context without adding them to analyzer JSON.
- Render an inline HIG/evidence link per issue from `guideline_reference.url` when present.
- Keep the previous visual standard: summary dashboard, severity filtering, search, AI prompt copying, code/fix comparison, and the same compact inline evidence style.
- Avoid validation-status UI: no `kept`, `dropped`, `severity_adjusted`, `not_validated`, confidence, retention, or validation decision blocks.

Run the generator with:

```text
scripts/generate_html_report.py --analyze projectPath/.evenbetter/analyze-{N}.json --manifest projectPath/.evenbetter/manifest.json --output projectPath/.evenbetter/evenbetter-validate-{N}.html
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
