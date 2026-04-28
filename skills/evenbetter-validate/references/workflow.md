# Validator Workflow

This workflow validates `severity: "error"` findings from the EvenBetter iOS analyzer. Treat `error` as the high-severity class.

## 1. Normalize Inputs

1. Require `projectPath`.
2. Confirm `projectPath` is absolute.
3. Set `confidence_threshold` to `0.7` when omitted.
4. Accept only numeric thresholds from `0.0` to `1.0`; otherwise return a JSON error object with an `error` key and stop.

## 2. Load Analyzer Report

Read exactly:

```text
projectPath/.evenbetter/analyze.json
```

If the file is missing, malformed, or does not contain `files[]`, emit a JSON error object and stop. Do not read legacy `eb-analyze.json` unless a future compatibility contract explicitly adds that path.

Extract every violation under `files[].violations[]` where `severity` is `error`. Preserve the original `file_path`, `line_number`, `rule_id`, `domain`, `guideline_reference`, and all other original fields in the validation result.

## 3. Prepare Evidence

For each high-severity finding:

1. Resolve `source_path = projectPath / violation.file_path`.
2. Reject path traversal or files outside `projectPath`.
3. Read the source file without modifying it.
4. Capture a source excerpt using 1-based line numbers: include five lines before and five lines after `line_number`, clamped to file bounds.
5. Resolve the corpus clause from the current analyzer references:
   - `typography` -> `skills/evenbetter-ios-analyze/references/typography.md`
   - `color-theming` -> `skills/evenbetter-ios-analyze/references/color-theming.md`
   - `components-patterns` -> `skills/evenbetter-ios-analyze/references/components-patterns.md`
   - `layout-interaction` -> `skills/evenbetter-ios-analyze/references/layout-interaction.md`
   - `navigation-flow` -> `skills/evenbetter-ios-analyze/references/navigation-flow.md`
   - `accessibility` -> `skills/evenbetter-ios-analyze/references/accessibility.md`
6. In the selected reference, find the heading that starts with `### <rule_id>`. Use that heading and its bullet block until the next `###` heading as the clause.
7. If the clause cannot be found, classify the finding as `dropped` with `drop_reason: "clause_not_found"`.

## 4. Verify The Guideline URL

Promote this deterministic rule to code: use the bundled script rather than model judgment for URL reachability.

For each finding with a resolved clause:

1. Read `violation.guideline_reference.url`.
2. Run `scripts/verify_url.py <url>`.
3. Record the script JSON as `url_verification`.
4. If the script exits nonzero or `ok` is not `true`, classify the finding as `dropped` with `drop_reason: "url_unreachable"`.

The URL must resolve with HTTP 200 and must belong to `developer.apple.com`, `www.w3.org`, or `w3.org`.

## 5. Independent Judgment

Judge from fresh evidence, not from the original auditor's confidence. Use only:

- the original violation object
- the source excerpt
- the resolved corpus clause
- the URL verification result
- directly adjacent source context needed to interpret the excerpt

When isolated subagent contexts are available and permitted, pass only those artifacts to the validator context. Otherwise perform a deliberate second-pass re-evaluation after reloading those artifacts.

Return this judgment for every finding:

- `confidence`: float from `0.0` to `1.0`
- `reasoning`: one concise paragraph explaining the evidence
- `decision`: `kept`, `downgraded`, or `dropped`

Decision rules:

- `kept`: `confidence >= confidence_threshold`, source excerpt supports a high-severity violation, corpus clause is resolved, URL verified, and reasoning is coherent.
- `downgraded`: evidence supports a real guideline concern, but not high-severity; include `downgraded_severity: "warning"`.
- `dropped`: evidence does not support the finding, confidence is too low for even a warning, URL verification failed, corpus clause is missing, or reasoning is incoherent.

Use `drop_reason: "low_confidence"` when evidence is too weak and no more specific dropped reason applies. Use `drop_reason: "reasoning_incoherent"` when the original finding's claim conflicts with the source excerpt or cannot be made internally consistent.

## 6. Aggregate Results

Load `references/output-contract.md` and produce exactly that envelope.

Compute:

- `total_high_input`: number of input `error` violations
- `kept_count`, `downgraded_count`, `dropped_count`
- `retention_rate`: `kept_count / total_high_input`, or `0.0` when there are no high-severity inputs
- `mean_confidence`: mean validator confidence across all processed findings, or `0.0` for no findings
- `time_per_finding_ms`: elapsed validation time divided by processed findings, or `0.0` for no findings

Round rates and mean confidence to four decimal places. Round time to one decimal place.

## 7. Store And Output

Create `projectPath/.evenbetter/` if needed and write:

```text
projectPath/.evenbetter/evenbetter-validate.json
```

This validation file is the only permitted write inside `projectPath`. Emit the same JSON object on stdout when running headless.

## 8. Compaction-Safe Invariants

If context is compacted, preserve these facts:

- input report path is `.evenbetter/analyze.json`
- output report path is `.evenbetter/evenbetter-validate.json`
- only `severity: "error"` findings are validated
- canonical threshold is `0.7`
- kept findings require verified URL, resolved clause, coherent reasoning, and confidence at or above threshold
- every dropped finding requires a machine-readable `drop_reason`
- source/project files are read-only
