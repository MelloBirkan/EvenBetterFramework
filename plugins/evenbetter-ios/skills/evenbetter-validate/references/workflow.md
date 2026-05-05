# Validator Workflow

This workflow validates every actionable finding from a numbered EvenBetter iOS analyzer report. Validation confirms whether the finding is real, whether the analyzer severity is correct, whether the analyzer-generated `ai_fix_prompt` is accurate enough for the fixer to execute, and whether useful working evidence links can be attached for review.

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

- `state.status` is not `fixed`
- `state.status` is not `rejected`
- `state.status` is not `duplicate_of`

Preserve the original `id`, `state`, `file_path`, `line_number`, `rule_id`, `domain`, `guideline_reference`, and all other original fields in the validation result. Deferred findings remain eligible for validation because deferral is a fix-scoping decision, not evidence invalidation.

## 4. Prepare Evidence

For each actionable finding:

1. Resolve `source_path = projectPath / violation.file_path`.
2. Reject path traversal or files outside `projectPath`.
3. Read the source file without modifying it.
4. Capture a source excerpt using 1-based line numbers: include five lines before and five lines after `line_number`, clamped to file bounds.
5. Read the plugin corpus index at `../../corpus/index.json`.
6. Find the index entry where `clause_id` equals `violation.rule_id`.
7. Resolve `reference_path = ../../<entry.file_path>` from this skill directory. Reject missing files or paths outside the `evenbetter-ios` plugin.
8. In the selected corpus file, find the H2 heading that starts with `## <rule_id>`. Use that heading and its clause block until the next `##` heading as the corpus clause.
9. Attach index metadata to the corpus clause: `clause_id`, `source_url`, `retrieved`, and `corpus_version`.
10. If the index entry or markdown clause cannot be found, classify the finding as `dropped` with `drop_reason: "clause_not_found"`.

## 5. Verify The Guideline URL

Promote this deterministic rule to code: use the bundled script rather than model judgment for URL reachability.

For each finding with a resolved clause:

1. Read `violation.guideline_reference.url`.
2. Run `scripts/verify_url.py <url>`.
3. Record the script JSON as `url_verification`.
4. If the script exits nonzero or `ok` is not `true`, classify the finding as `dropped` with `drop_reason: "url_unreachable"`.

The URL must resolve with HTTP 200 and must belong to `developer.apple.com`, `www.w3.org`, or `w3.org`.

## 6. Optional Web Evidence

Use the host AI agent's native web search, web fetch, or documentation lookup tools when the local corpus clause and verified guideline URL leave uncertainty about whether the issue is real, severity is correct, or the fix prompt is accurate.

Rules:

- Prefer primary sources: `developer.apple.com`, Apple Human Interface Guidelines, W3C WCAG, or official framework documentation.
- Do not require an extra web-discovered link for every finding; the existing verified guideline URL and corpus source may be enough.
- When web lookup finds a useful confirmation source, add it to `supporting_links` with a concise label and reason.
- Verify or inspect the URL enough to avoid dead, irrelevant, or unrelated links.
- If native web tools are unavailable, continue from local evidence and the deterministic URL verifier; mention the evidence limit in `reasoning` when it affects confidence.

## 7. Independent Judgment

Judge from fresh evidence, not from the original auditor's confidence. Use only:

- the original violation object
- the source excerpt
- the resolved corpus clause
- the URL verification result
- directly adjacent source context needed to interpret the excerpt
- the analyzer-provided `ai_fix_prompt`, `fix_description`, and `fix_code` when present
- optional `supporting_links` from guideline, corpus, or native web lookup evidence

When isolated subagent contexts are available and permitted, pass only those artifacts to the validator context. Otherwise perform a deliberate second-pass re-evaluation after reloading those artifacts.

Return this judgment for every finding:

- `confidence`: float from `0.0` to `1.0`
- `reasoning`: one concise paragraph explaining the evidence
- `decision`: `kept`, `severity_adjusted`, or `dropped`
- `severity_assessment`: original severity, correct severity, and concise reasoning
- `fix_prompt_assessment`: whether the analyzer-provided `ai_fix_prompt` is accurate, plus concise reasoning
- `supporting_links`: array of working evidence links used for the decision; may be empty

Decision rules:

- `kept`: `confidence >= confidence_threshold`, source excerpt supports the violation, corpus clause is resolved, URL verified, reasoning is coherent, analyzer severity is correct, and `ai_fix_prompt` is accurate.
- `severity_adjusted`: evidence supports a real guideline concern and the analyzer `ai_fix_prompt` is accurate, but the correct severity differs from the analyzer severity; include `corrected_severity`.
- `dropped`: evidence does not support the finding, confidence is too low for even an info-level concern, URL verification failed, corpus clause is missing, reasoning is incoherent, or `ai_fix_prompt` is missing or inaccurate.

Use `drop_reason: "low_confidence"` when evidence is too weak and no more specific dropped reason applies. Use `drop_reason: "reasoning_incoherent"` when the original finding's claim conflicts with the source excerpt or cannot be made internally consistent. Use `drop_reason: "fix_prompt_missing"` or `drop_reason: "fix_prompt_inaccurate"` when the issue may be real but the analyzer did not provide a usable prompt.

Do not create, revise, or backfill `ai_fix_prompt`; that field belongs to the analyzer report. Do not set violation `state.status` based on `kept`, `severity_adjusted`, or `dropped`. Validation decisions live in the validation report; fix/reject/defer decisions live in analyzer violation state.

## 8. Aggregate Results

Load `references/output-contract.md` and produce exactly that envelope.

Compute:

- `validates`: `analyze-{N}.json`
- `analyzer_run`: `N`
- `input_report`: absolute path to `analyze-{N}.json`
- `html_report`: `.evenbetter/evenbetter-validate-{N}.html`
- `createdAt`: current UTC ISO-8601 timestamp with `Z`
- `total_validated_input`: number of input violations with actionable state
- `kept_count`, `severity_adjusted_count`, `dropped_count`
- `retention_rate`: `(kept_count + severity_adjusted_count) / total_validated_input`, or `0.0` when there are no actionable inputs
- `mean_confidence`: mean validator confidence across all processed findings, or `0.0` for no findings
- `time_per_finding_ms`: elapsed validation time divided by processed findings, or `0.0` for no findings

Round rates and mean confidence to four decimal places. Round time to one decimal place.

## 9. Store And Update Manifest

Create `projectPath/.evenbetter/` if needed and write:

```text
projectPath/.evenbetter/evenbetter-validate-{N}.json
```

This validation file, the derived HTML report, `manifest.json`, and the paired analyzer report's `run.status` are the only permitted writes inside `projectPath`.

After the validation file is written:

1. Reread `manifest.json`.
2. Update the matching run entry with `validate: "evenbetter-validate-{N}.json"` and `validated: true`.
3. Set the run entry `status` to `validated` unless it is already `fixed` or `partially_fixed`.
4. Set `latest.validate` to `evenbetter-validate-{N}.json` when this is the newest validation report by `createdAt`; this is always true for the default latest-unvalidated run.
5. Recompute the run entry `summary` from violation `state.status` values in `analyze-{N}.json`.
6. Update `analyze-{N}.json` `run.status` to `validated` unless it is already `fixed` or `partially_fixed`.

## 10. Generate HTML Report

After the validation report, manifest, and paired analyzer `run.status` updates complete, generate the browser report:

```text
projectPath/.evenbetter/evenbetter-validate-{N}.html
```

Run the bundled generator with:

```text
scripts/generate_html_report.py --analyze projectPath/.evenbetter/analyze-{N}.json --validate projectPath/.evenbetter/evenbetter-validate-{N}.json --manifest projectPath/.evenbetter/manifest.json --output projectPath/.evenbetter/evenbetter-validate-{N}.html
```

The HTML report is a derived view. It must include all analyzer findings from `files[].violations[]`, annotate findings with validator decisions by matching each validation result's `original_violation.id`, and render per-issue evidence links from `supporting_links`, `guideline_reference.url`, and `corpus_clause.source_url` when present. Do not duplicate template-only fields such as `recommended_fix` or `language` into `analyze-{N}.json`; the generator derives them for display.

When running headless, emit the validation report object on stdout and no prose. The `html_report` field in that JSON points to the generated report. In interactive chat, keep the response concise and include:

```text
Validation complete.
- Wrote: .evenbetter/evenbetter-validate-{N}.json
- HTML report: .evenbetter/evenbetter-validate-{N}.html
- Retained: <kept> kept, <severity_adjusted> severity adjusted, <dropped> dropped

Click here to open .evenbetter/evenbetter-validate-{N}.html
```

## 11. Compaction-Safe Invariants

If context is compacted, preserve these facts:

- report history is indexed by `.evenbetter/manifest.json`
- default target is the newest unvalidated analyzer run
- explicit `run` requires a matching `analyze-{N}.json`
- revalidating an already validated run requires `revalidate: true`
- output report path is `.evenbetter/evenbetter-validate-{N}.json`
- HTML report path is `.evenbetter/evenbetter-validate-{N}.html`
- validation report includes `validates: "analyze-{N}.json"` and `analyzer_run: N`
- validation report includes `html_report: ".evenbetter/evenbetter-validate-{N}.html"`
- every actionable finding is validated, regardless of severity
- canonical threshold is `0.7`
- kept and severity-adjusted findings require verified URL, resolved clause, coherent reasoning, accurate fix prompt, and confidence at or above threshold
- native web lookup is used when extra confirmation is needed, and useful working links are recorded in `supporting_links`
- every dropped finding requires a machine-readable `drop_reason`
- validation does not mutate user fix/reject/defer decisions in violation `state`
- validation does not create or change analyzer `ai_fix_prompt` values
- source/project files are read-only except for validation report, manifest, and paired analyzer `run.status`
