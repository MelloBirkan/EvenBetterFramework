# Validator Workflow

Validate every actionable finding from a numbered EvenBetter iOS analyzer report, correct the analyzer JSON in place, and generate an issue-focused HTML report. Validation answers whether each analyzer finding is actually an issue; it does not report per-item validation status.

EvenBetter assumes serial execution. Before writing analyzer or manifest updates, reread `projectPath/.evenbetter/manifest.json` from disk.

## 1. Normalize Inputs

1. If `projectPath` is omitted or `.`, set it to the host's current working directory for this skill invocation.
2. If `projectPath` is relative, resolve it against the host's current working directory.
3. Canonicalize `projectPath` to an absolute path before reading, writing, reporting, or passing it to validator contexts.
4. Set `confidence_threshold` to `0.7` when omitted.
5. Accept only numeric thresholds from `0.0` to `1.0`; otherwise return a JSON error object with an `error` key and stop.
6. Accept optional `run` as a positive integer analyzer run number.
7. Accept optional `revalidate` as a boolean; default to `false`.

## 2. Load Manifest And Select Run

Read:

```text
projectPath/.evenbetter/manifest.json
```

If no manifest exists but `projectPath/.evenbetter/analyze.json` exists, perform the legacy migration documented in the analyzer output contract, initialize run 1, and continue with run 1. If neither a manifest nor a legacy analyzer report exists, emit a JSON error object and stop.

Select the run to validate:

1. If `run` is provided, select that manifest run.
2. If `run` is omitted, select the newest manifest run with `validated: false`.
3. If every run is already validated and no explicit `run` was provided, emit a JSON error object explaining that there is no unvalidated analyzer run.
4. If the selected run already has `validated: true` and `revalidate` is false, emit a JSON error object and stop.
5. If `revalidate` is true, validate the selected run again and overwrite the derived HTML report only.

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

Deferred findings remain eligible for validation because deferral is a fix-scoping decision, not evidence invalidation.

## 3.5 Plan Execution And Keep The Turn Alive

Before any long-running evidence pass, decide and state the actual execution mode. Do not send a future-tense status message and then stop. The following message is prohibited as a terminal response:

```text
Validator is now performing second-pass evidence checks... This will take a moment...
```

A progress message is only valid if the agent continues working in the same turn immediately after it.

Use this liveness contract:

1. Count actionable findings and group them by domain and, when useful, file.
2. If host-native sub-agents are available, spawn the validator sub-agents immediately and state the concrete dispatched units, for example `typography`, `color-theming`, `accessibility batch 1`, and `accessibility batch 2`.
3. If sub-agents are unavailable, state the fallback once and continue sequentially in domain/batch chunks.
4. For sequential validation, use batches of no more than 10 findings. For sub-agent validation, split very large domains into batches that keep related findings together by file and rule.
5. After each completed sequential batch or returned sub-agent batch, report concise progress: validated count out of total, rejected count, severity corrections, guideline corrections, and remaining count.
6. Do not provide the final validation summary until `analyze-{N}.json`, `manifest.json`, and `.evenbetter/evenbetter-validate-{N}.html` have actually been written.
7. If a blocker prevents continuing, return a concrete error or blocker with the file/run involved. Do not leave the user with a vague "running" status.

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
9. Attach index metadata to the working evidence: `clause_id`, `source_url`, `retrieved`, and `corpus_version`.
10. If the index entry or markdown clause cannot be found, reject the analyzer violation with `state.reason = "Corpus clause for <rule_id> could not be resolved."`

## 5. Dispatch Specialized Validator Contexts

Group prepared findings by analyzer `domain`: `typography`, `color-theming`, `components-patterns`, `layout-interaction`, `navigation-flow`, and `accessibility`.

If the host environment supports independent sub-agents or worker contexts, such as Claude Code subagents or Codex sub-agents, spawn specialized validator sub-agents by domain when practical. For very large domains, split into batches that keep related findings together by file and rule. Each validator sub-agent is an expert for its assigned Apple HIG, SwiftUI, and accessibility domain. The orchestrator must explicitly state which sub-agents or batches were dispatched before waiting for them.

Pass each validator sub-agent only:

- the assigned original violation objects
- source excerpts and adjacent source context needed to interpret them
- resolved corpus clauses and index metadata
- URL verification results
- analyzer-provided `ai_fix_prompt`, `fix_description`, and `fix_code` when present
- optional primary-source web evidence when needed

Validator sub-agents return proposed actions only: keep as issue, correct severity, correct guideline reference, or reject as non-issue with concise reasoning. They must not write source files, `.evenbetter` files, cache files, or notes. The validator orchestrator reviews their outputs and is the only actor that mutates `analyze-{N}.json`, updates `manifest.json`, or generates HTML.

If sub-agents are unavailable or not permitted, perform the same domain-specialized validation sequentially in the main agent from the prepared artifacts, using the batch/progress rules from section 3.5.

## 6. Verify Or Correct The Guideline URL

Promote this deterministic rule to code: use the bundled script rather than model judgment for URL reachability.

For each finding with a resolved clause:

1. Read `violation.guideline_reference.url`.
2. Run `scripts/verify_url.py <url>`.
3. If the script exits with `ok: true`, keep the URL unless the evidence shows it points to the wrong source.
4. If the script fails or the URL is wrong, use the corpus index `source_url` or native web/documentation lookup to find the correct primary source.
5. Verify the corrected URL with `scripts/verify_url.py`.
6. If no valid source URL can be verified, reject the analyzer violation with `state.reason = "No reachable primary guideline URL could be verified."`

The URL must resolve with HTTP 200 and belong to `developer.apple.com`. Prefer Apple Human Interface Guidelines pages when available; Apple Developer documentation pages are valid for SwiftUI API-specific clauses.

## 7. Optional Web Evidence

Use the host AI agent's native web search, web fetch, or documentation lookup tools when the local corpus clause and verified guideline URL leave uncertainty about whether the issue is real, severity is correct, or the fix prompt is accurate.

Rules:

- Prefer primary sources on `developer.apple.com`: Apple Human Interface Guidelines or official SwiftUI framework documentation.
- Do not require extra web-discovered evidence for every finding; the existing verified guideline URL and corpus source may be enough.
- Use web results to correct analyzer fields or reject unsupported findings, not to add validation metadata.
- If native web tools are unavailable, continue from local evidence and the deterministic URL verifier.

## 8. Independent Judgment And Corrections

Judge from fresh evidence, not from the original auditor's confidence. Use only:

- the original violation object
- the source excerpt
- the resolved corpus clause
- the verified or corrected guideline URL
- directly adjacent source context needed to interpret the excerpt
- the analyzer-provided `ai_fix_prompt`, `fix_description`, and `fix_code` when present
- optional primary-source web evidence when needed

When isolated sub-agent contexts are available and permitted, use the specialized validator sub-agent outputs from the dispatch step as independent evidence proposals. Otherwise perform a deliberate second-pass re-evaluation after reloading those artifacts.

For each finding, choose one action:

- **Keep as issue**: evidence supports the violation, severity is correct, guideline URL is valid, and `ai_fix_prompt` is accurate.
- **Correct severity**: evidence supports the violation, but `severity` should be `error`, `warning`, or `info`; update the analyzer violation in place.
- **Correct guideline reference**: evidence supports the violation, but the label or URL is wrong; update `guideline_reference` in place.
- **Reject as non-issue**: evidence does not support the finding, confidence is below threshold, the clause or URL cannot be resolved, the claim conflicts with source, or `ai_fix_prompt` is missing/inaccurate.

Reject by mutating only the existing state block:

```json
{
  "status": "rejected",
  "decidedIn": N,
  "decidedBy": "validator",
  "reason": "Concise evidence-based reason.",
  "duplicateOf": null
}
```

Do not create, revise, or backfill `ai_fix_prompt`; that field belongs to the analyzer report. Do not add validator decision fields to analyzer violations.

## 9. Recompute Analyzer Aggregates

Load `references/output-contract.md` and update the selected analyzer report accordingly.

Recompute visible issue counts from violations whose `state.status` is `open` or `deferred`:

- `total_violations`
- `critical_count`
- domain summary counts
- file scores
- project scores

Refresh `executive_summary` if corrections materially changed the issue set. Preserve old reports and do not rewrite unrelated analyzer runs.

Recompute or repair the top-level `html_report_data` object so the adapted EvenBetter iOS HIG template has all required fields:

- `brand`, `report_title`, `standard_label`, `project_name`, `project_path`, `framework`, `hig_standard`, and `scan_date`
- `summary.total`, `summary.critical`, `summary.high`, `summary.medium`, and `summary.low`
- `scan_context.frameworks`, `framework_versions`, `design_systems`, `component_patterns`, `scan_duration`, `files_scanned`, `confidence`, and `custom_utilities`

Use current visible issues for summary counts. Map `error -> critical`, `warning -> high`, `info -> medium`, and write `low: 0` unless a lower-priority severity exists in the analyzer contract. Do not add `html_report_data.issues`; the HTML issue list is derived from `files[].violations[]`.

## 10. Store Analyzer And Update Manifest

Before writing, reread `manifest.json`.

Write the corrected analyzer report back to:

```text
projectPath/.evenbetter/analyze-{N}.json
```

Then update `projectPath/.evenbetter/manifest.json`:

1. Update the matching run entry with `validated: true`.
2. Set the run entry `status` to `validated` unless it is already `fixed` or `partially_fixed`.
3. Add or update the run entry `html_report` with the generated HTML report path.
4. Recompute the run entry `summary` from violation `state.status` values in `analyze-{N}.json`.
5. Preserve any existing `validate` fields for legacy compatibility, but do not set them to a new validation JSON file.
6. Preserve `latest.analyze`, `latest.validate`, `currentRun`, and unrelated run entries.
7. Set `latest.html_report` to the generated HTML path when the manifest has a `latest` object.
8. Update `analyze-{N}.json` `run.status` to `validated` unless it is already `fixed` or `partially_fixed`.

## 11. Generate HTML Report

After analyzer and manifest updates complete, generate the browser report:

```text
projectPath/.evenbetter/evenbetter-validate-{N}.html
```

Run the bundled generator with:

```text
scripts/generate_html_report.py --analyze projectPath/.evenbetter/analyze-{N}.json --manifest projectPath/.evenbetter/manifest.json --output projectPath/.evenbetter/evenbetter-validate-{N}.html
```

The HTML report is a derived view of current issues using the EvenBetter iOS HIG adaptation of the supplied template. It must include only analyzer findings with `state.status = "open"` or `state.status = "deferred"`, render issue-level HIG/evidence links from `guideline_reference.url`, use `html_report_data` for dashboard and scan-context fields, and avoid validation-status language.

When regenerating HTML for older projects that still have `.evenbetter/evenbetter-validate-{N}.json`, pass that file through the generator's optional `--validation` argument if needed. The visual report must still remain issue-focused: include kept and severity-adjusted legacy findings as issue cards, populate their analyzer `ai_fix_prompt` values from `original_violation`, include legacy supporting evidence links, and exclude dropped findings.

In interactive chat, keep the response concise:

```text
Validation complete.
- Updated: .evenbetter/analyze-{N}.json
- HTML report: .evenbetter/evenbetter-validate-{N}.html
- Current issues: <total> total (<error> error, <warning> warning, <info> info)
- Corrections: <severity> severity, <links> guideline links, <rejected> rejected

Open the HTML report in a browser by holding Command and clicking the left mouse button on the path. To apply corrections, use $evenbetter-fix.
```

## 12. Compaction-Safe Invariants

If context is compacted, preserve these facts:

- report history is indexed by `.evenbetter/manifest.json`
- `projectPath` defaults to the invocation working directory when omitted
- default target is the newest unvalidated analyzer run
- spawn specialized validator sub-agents by domain or domain-sized batches when the host supports sub-agents; otherwise perform the same validation sequentially
- never end after a "validation is running" progress message; continue to sub-agent dispatch, sequential batches, written outputs, or a concrete blocker
- large sequential validations use batches of no more than 10 findings with progress after each batch
- explicit `run` requires a matching `analyze-{N}.json`
- revalidating an already validated run requires `revalidate: true`
- validation does not create `.evenbetter/evenbetter-validate-{N}.json`
- HTML report path is `.evenbetter/evenbetter-validate-{N}.html`
- HTML generation can read old validation JSON only as compatibility input, never as a new output artifact
- every actionable finding is validated, regardless of severity
- canonical threshold is `0.7`
- real issues remain analyzer violations
- wrong severities and guideline references are corrected in analyzer JSON
- missing or stale `html_report_data` is corrected in analyzer JSON before HTML generation
- non-issues are rejected through `state.status = "rejected"` with `decidedBy = "validator"`
- validation does not create or change analyzer `ai_fix_prompt` values
- source/project files are read-only except for analyzer report, manifest, and HTML report writes inside `.evenbetter/`
