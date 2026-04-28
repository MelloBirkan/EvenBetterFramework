# Validator Workflow

This workflow validates `severity: "error"` findings from a numbered EvenBetter iOS analyzer report. Treat `error` as the high-severity class.

EvenBetter assumes serial execution. Before writing any validation report or manifest update, reread `projectPath/.evenbetter/manifest.json` from disk.

## 1. Normalize Inputs

1. Require `projectPath`.
2. Confirm `projectPath` is absolute.
3. Set `confidence_threshold` to `0.7` when omitted.
4. Accept only numeric thresholds from `0.0` to `1.0`; otherwise return a JSON error object with an `error` key and stop.
5. Accept optional `run` as a positive integer analyzer run number.
6. Accept optional `revalidate` as a boolean; default to `false`.

## 2. Load Manifest And Select Run

Read:

```text
projectPath/.evenbetter/manifest.json
```

If no manifest exists but `projectPath/.evenbetter/analyze.json` exists, perform the legacy migration documented in the analyzer output contract, initialize run 1, and continue with run 1. If neither a manifest nor a legacy analyzer report exists, emit a JSON error object and stop.

Select the run to validate:

1. If `run` is provided, select that manifest run.
2. If `run` is omitted, select the newest manifest run with `validated: false` or missing `validate`.
3. If every run is already validated and no explicit `run` was provided, emit a JSON error object explaining that there is no unvalidated analyzer run.
4. If the selected run already has a paired validation report and `revalidate` is false, emit a JSON error object and stop.
5. If `revalidate` is true, replace `evenbetter-validate-{N}.json` for the selected run.

The selected analyzer report must be:

```text
projectPath/.evenbetter/analyze-{N}.json
```

where `N` equals the manifest run number.

## 3. Load Analyzer Report

Read `projectPath/.evenbetter/analyze-{N}.json`.

If the file is missing, malformed, or does not contain `files[]`, emit a JSON error object and stop. Do not read legacy `eb-analyze.json`.

Extract every violation under `files[].violations[]` where:

- `severity` is `error`
- `state.status` is not `fixed`
- `state.status` is not `rejected`
- `state.status` is not `duplicate_of`

Preserve the original `id`, `state`, `file_path`, `line_number`, `rule_id`, `domain`, `guideline_reference`, and all other original fields in the validation result. Deferred findings remain eligible for validation because deferral is a fix-scoping decision, not evidence invalidation.

## 4. Prepare Evidence

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

## 5. Verify The Guideline URL

Promote this deterministic rule to code: use the bundled script rather than model judgment for URL reachability.

For each finding with a resolved clause:

1. Read `violation.guideline_reference.url`.
2. Run `scripts/verify_url.py <url>`.
3. Record the script JSON as `url_verification`.
4. If the script exits nonzero or `ok` is not `true`, classify the finding as `dropped` with `drop_reason: "url_unreachable"`.

The URL must resolve with HTTP 200 and must belong to `developer.apple.com`, `www.w3.org`, or `w3.org`.

## 6. Independent Judgment

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

Do not set violation `state.status` based on `kept`, `downgraded`, or `dropped`. Validation decisions live in the validation report; fix/reject/defer decisions live in analyzer violation state.

## 7. Aggregate Results

Load `references/output-contract.md` and produce exactly that envelope.

Compute:

- `validates`: `analyze-{N}.json`
- `analyzer_run`: `N`
- `input_report`: absolute path to `analyze-{N}.json`
- `createdAt`: current UTC ISO-8601 timestamp with `Z`
- `total_high_input`: number of input `error` violations with actionable state
- `kept_count`, `downgraded_count`, `dropped_count`
- `retention_rate`: `kept_count / total_high_input`, or `0.0` when there are no high-severity inputs
- `mean_confidence`: mean validator confidence across all processed findings, or `0.0` for no findings
- `time_per_finding_ms`: elapsed validation time divided by processed findings, or `0.0` for no findings

Round rates and mean confidence to four decimal places. Round time to one decimal place.

## 8. Store And Update Manifest

Create `projectPath/.evenbetter/` if needed and write:

```text
projectPath/.evenbetter/evenbetter-validate-{N}.json
```

This validation file, `manifest.json`, and the paired analyzer report's `run.status` are the only permitted writes inside `projectPath`.

After the validation file is written:

1. Reread `manifest.json`.
2. Update the matching run entry with `validate: "evenbetter-validate-{N}.json"` and `validated: true`.
3. Set the run entry `status` to `validated` unless it is already `fixed` or `partially_fixed`.
4. Set `latest.validate` to `evenbetter-validate-{N}.json` when this is the newest validation report by `createdAt`; this is always true for the default latest-unvalidated run.
5. Recompute the run entry `summary` from violation `state.status` values in `analyze-{N}.json`.
6. Update `analyze-{N}.json` `run.status` to `validated` unless it is already `fixed` or `partially_fixed`.

Emit the validation report object on stdout when running headless.

## 9. Compaction-Safe Invariants

If context is compacted, preserve these facts:

- report history is indexed by `.evenbetter/manifest.json`
- default target is the newest unvalidated analyzer run
- explicit `run` requires a matching `analyze-{N}.json`
- revalidating an already validated run requires `revalidate: true`
- output report path is `.evenbetter/evenbetter-validate-{N}.json`
- validation report includes `validates: "analyze-{N}.json"` and `analyzer_run: N`
- only actionable `severity: "error"` findings are validated
- canonical threshold is `0.7`
- kept findings require verified URL, resolved clause, coherent reasoning, and confidence at or above threshold
- every dropped finding requires a machine-readable `drop_reason`
- validation does not mutate user fix/reject/defer decisions in violation `state`
- source/project files are read-only except for validation report, manifest, and paired analyzer `run.status`
