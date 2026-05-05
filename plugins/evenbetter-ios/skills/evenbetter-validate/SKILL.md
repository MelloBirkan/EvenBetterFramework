---
name: evenbetter-validate
description: Fast second-pass validator for numbered EvenBetter iOS analyzer reports. Use to verify .evenbetter/analyze-{N}.json findings in the current or supplied project directory, run a deterministic verification pass (URL reachability, corpus clause resolution, source line existence, ai_fix_prompt and fix_options sanity), escalate only the small set of ambiguous findings to a re-evaluation sub-agent or host-native web research, correct severity, guideline references, and html_report_data directly in the analyzer JSON, reject unsupported findings via state, update .evenbetter/manifest.json, and generate .evenbetter/evenbetter-validate-{N}.html. Defaults to the current working directory when no project path is provided.
---

# evenbetter-validate

## Overview

Confirm or correct an analyzer report so the user can trust the issues that go into the HTML report and into `$evenbetter-fix`. This skill is intentionally lean: it does *not* re-run the six-domain analysis. It runs a single deterministic verification pass over `analyze-{N}.json`, escalates only findings flagged ambiguous, applies corrections in place, and renders the HTML report from the corrected analyzer JSON.

The analyzer is the source of truth for findings, `ai_fix_prompt`, `fix_options`, and the top-level `html_report_data`. Validate may correct `severity`, `guideline_reference`, and `html_report_data`, and may reject unsupported findings through the existing violation `state` object. It must not invent new fix prompts, options, or rules.

## Inputs

- `projectPath` (optional): Filesystem path to the analyzed SwiftUI project. Default to the host's current working directory when omitted or `.`.
- `confidence_threshold` (optional): Float from `0.0` to `1.0`. Default to `0.7`.
- `run` (optional): Analyzer run number to validate. Default is the latest unvalidated analyzer run in `.evenbetter/manifest.json`.
- `revalidate` (optional): Boolean. Default `false`; when `true`, allow validating a run whose manifest entry already has `validated: true`.

Resolve `projectPath` to an absolute path before use. If the user supplies a relative path, resolve it against the host's current working directory. Do not ask for a full path solely because `projectPath` is omitted or relative.

## Source Safety

Do not edit, delete, format, generate, or execute source/project files inside `projectPath`. The only permitted writes inside `projectPath` are creating `.evenbetter/` if needed, updating the selected `.evenbetter/analyze-{N}.json`, writing the derived browser report to `.evenbetter/evenbetter-validate-{N}.html`, and updating `.evenbetter/manifest.json`.

## Required References

Load only what the current phase needs:

- `references/workflow.md`: Fast-pass loop, escalation rules, analyzer JSON correction rules, and compaction-safe invariants.
- `references/output-contract.md`: Analyzer JSON mutation and HTML output contract.
- `references/architecture.md`: Analyzer-to-validator-to-fixer flow.
- `scripts/verify_url.py`: Deterministic URL verifier for Apple guideline and developer documentation sources.
- `scripts/generate_html_report.py`: Deterministic HTML issue report generator.

## Run Selection

Read `projectPath/.evenbetter/manifest.json` and select the analyzer run to validate. Default to the newest run with `validated: false`. If `run` is provided, validate that run; if it already has `validated: true`, require `revalidate: true`. Then read `projectPath/.evenbetter/analyze-{N}.json` and collect every violation whose `state.status` is not `fixed`, `rejected`, or `duplicate_of`. Deferred findings remain eligible — deferral is a fix-scoping decision, not evidence invalidation.

Compatibility: if `analyze-{N}.json` has top-level `violations[]` and no `files[]`, normalize them in memory by grouping by `file_path`. When rewriting, prefer the canonical `files[].violations[]` shape; the HTML generator accepts both.

## Fast Verification Pass

For every actionable finding, run the following deterministic checks. They are cheap and require no model judgment:

1. **Source line check.** Resolve `source_path = projectPath / violation.file_path`. Reject path traversal. Read the file. Ensure `line_number` is a positive 1-based integer within file bounds.
2. **Code-context check.** Capture the snippet at `line_number ± 5` lines. Compare to `violation.code_snippet`: if the snippet has changed materially (e.g., the cited symbol no longer appears nearby), flag the finding `uncertain: source-drift`.
3. **Corpus clause check.** Resolve `rule_id` against `../../corpus/index.json`. Read the corresponding H2 section in the indexed corpus markdown file. If the clause cannot be found, reject with `state.reason = "Corpus clause for <rule_id> could not be resolved."`.
4. **URL check.** Run `scripts/verify_url.py <violation.guideline_reference.url>`. On success, keep the URL. On failure, replace with `corpus index entry source_url` and re-verify; if that also fails, flag `uncertain: url-broken`.
5. **Fix-prompt sanity.** Confirm `ai_fix_prompt` is non-empty, mentions the rule, and is grounded in the source line. Confirm `fix_options` is a 1-4 entry array with exactly one `recommended: true` entry, distinct labels, and aligned with the violation's `fix_description`. If either is missing or obviously generic, reject with a clear `state.reason`.
6. **Severity sanity.** Compare the finding's `severity` against the corpus clause's documented severity. If they differ, mark for severity correction (do not reject).

Bucket each finding into one of: `confirmed`, `severity-correction`, `link-correction`, `rejected`, or `uncertain`. The first three buckets need no further work; only `uncertain` findings escalate.

## Escalation For Uncertain Findings Only

Do not dispatch per-domain validator sub-agents by default. Only the `uncertain` bucket requires escalation:

- **Claude Code with sub-agents available.** Spawn one `Agent` call (subagent_type `general-purpose`) per ≤10 uncertain findings, in parallel where possible. Pass each sub-agent the violation objects, the source excerpts, the resolved corpus clauses, and the URL verification results. The sub-agent decides keep / correct severity / correct guideline_reference / reject. The orchestrator alone applies the decisions.
- **Codex sub-agents available.** Equivalent dispatch in batches of ≤10.
- **No sub-agents.** Re-evaluate the uncertain bucket inline in the main agent, in batches of ≤10 findings with a short progress update after each batch.

For findings the sub-agent or main agent cannot resolve from local evidence alone, use the host AI agent's native web research tools (Claude Code's `WebSearch` and `WebFetch`; equivalent native lookups in other hosts) to find a primary source on `developer.apple.com`. Use those results only to confirm or correct existing analyzer fields. Do not introduce new findings, new `rule_id` values, new `ai_fix_prompt` values, or new `fix_options` from web research; that is the analyzer's job.

State the actual execution mode before starting (`fast pass only — N confirmed, N corrected, N rejected, N uncertain → escalating to <route>`). Do not end the turn after a future-tense status message; continue until `analyze-{N}.json`, `manifest.json`, and the HTML report are written.

## Apply Corrections

Mutate `analyze-{N}.json` in place using the rules in `references/output-contract.md`:

- Keep confirmed findings with `state.status` unchanged.
- Update `severity` for severity-correction findings.
- Update `guideline_reference` for link-correction findings.
- For rejections, set `state.status = "rejected"`, `state.decidedIn = N`, `state.decidedBy = "validator"`, `state.reason = <evidence>`, `state.duplicateOf = null`. Do not delete rejected findings.
- Recompute aggregate counts, file scores, project scores, executive summary (only when materially changed), and `html_report_data`.
- Set `analyze-{N}.json` `run.status = "validated"` unless it is already `fixed` or `partially_fixed`.

Update `.evenbetter/manifest.json`: `validated: true`, `status: "validated"` (preserve `fixed`/`partially_fixed`), `html_report: ".evenbetter/evenbetter-validate-{N}.html"`, recomputed `summary`. Preserve `latest.analyze`, `latest.validate` (legacy), `currentRun`, and unrelated runs. Update `latest.html_report` to the generated HTML.

## Generate HTML

Run the bundled generator:

```text
scripts/generate_html_report.py --analyze projectPath/.evenbetter/analyze-{N}.json --manifest projectPath/.evenbetter/manifest.json --output projectPath/.evenbetter/evenbetter-validate-{N}.html
```

The HTML report is the primary artifact for the end user. It must render only current issues (`state.status` is `open` or `deferred`), pull dashboard/scan-context from `html_report_data`, and surface each finding's `fix_options` so users see the same remediation alternatives `$evenbetter-fix` will offer.

Do not write `.evenbetter/evenbetter-validate-{N}.json`. Older projects may still have such files — the generator's `--validation` argument can accept them as legacy input.

## Chat Summary

After a successful run, reply with:

```text
Validation complete.
- Updated: .evenbetter/analyze-{N}.json
- HTML report: .evenbetter/evenbetter-validate-{N}.html
- Current issues: <total> total (<error> error, <warning> warning, <info> info)
- Corrections: <severity> severity, <links> guideline links, <rejected> rejected

Open the HTML report in a browser by holding Command and clicking the left mouse button on the path. To apply corrections, use $evenbetter-fix.
```

Load `references/workflow.md` next.
