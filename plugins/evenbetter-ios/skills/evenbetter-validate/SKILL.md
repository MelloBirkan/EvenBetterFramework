---
name: evenbetter-validate
description: Validator for numbered EvenBetter iOS analyzer reports. Use to validate and correct .evenbetter/analyze-{N}.json findings in the current or supplied project directory, verify every actionable issue, correct severity and guideline references in place, verify the analyzer's EvenBetter iOS HIG html_report_data, reject unsupported findings in analyzer state, verify analyzer-generated ai_fix_prompt accuracy without replacing it, spawn specialized validation sub-agents when the host supports Claude Code or Codex subagents, use native web search or documentation lookup when evidence is uncertain, update .evenbetter/manifest.json, and generate .evenbetter/evenbetter-validate-{N}.html for browser review. Defaults to the current working directory when no project path is provided.
---

# evenbetter-validate

## Overview

Validate EvenBetter iOS analyzer findings with a second-pass evidence check. Treat this skill as a correction pass over `analyze-{N}.json`: confirm real issues, correct analyzer fields in place, reject findings that are not actual issues, mark the run as validated, and generate an issue-focused browser report. Do not create a separate validation JSON report.

The analyzer remains the source of truth for findings, `ai_fix_prompt` values, and the top-level `html_report_data` consumed by the EvenBetter iOS HIG browser template. The validator may correct `severity`, `guideline_reference`, and `html_report_data`, and may reject unsupported findings through the existing violation `state` object. It must not create replacement fix prompts or add per-violation validation status fields.

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

- `references/workflow.md`: Validation loop, evidence checks, analyzer JSON correction rules, and compaction-safe invariants.
- `references/output-contract.md`: Analyzer JSON mutation and HTML output contract.
- `references/architecture.md`: Analyzer-to-validator-to-fixer flow.
- `scripts/verify_url.py`: Deterministic URL verifier for Apple guideline and developer documentation sources.
- `scripts/generate_html_report.py`: Deterministic HTML issue report generator for corrected analyzer reports, with legacy validation-report compatibility.

## Validation Scope

Read `projectPath/.evenbetter/manifest.json` and select the analyzer run to validate. By default, validate the newest run whose manifest entry has `validated: false`. If `run` is provided, validate that analyzer run; if it already has `validated: true`, require `revalidate: true`.

Read `projectPath/.evenbetter/analyze-{N}.json` for the selected run. Validate every violation where `state.status` is not `fixed`, `rejected`, or `duplicate_of`. Deferred findings remain eligible because validation checks whether the issue is real, not whether the user wants to fix it now.

For each actionable finding:

1. Re-read the cited Swift file and nearby lines.
2. Resolve the corpus clause for `rule_id` through `../../corpus/index.json`, then read the matching H2 section from the indexed corpus markdown file.
3. Verify `guideline_reference.url` with `scripts/verify_url.py`.
4. When the local corpus and verified guideline URL do not fully resolve uncertainty, use the host AI agent's native web search, web fetch, or documentation lookup tools to find a primary-source confirmation link.
5. Independently judge whether the cited code violates the rule.
6. Correct `severity` in the analyzer violation when the issue is real but the analyzer severity is wrong.
7. Correct `guideline_reference` in the analyzer violation when the issue is real but the label or URL points to the wrong primary source.
8. Verify that `ai_fix_prompt` is present, scoped to this finding, and accurate for the source evidence and rule.
9. Verify that top-level `html_report_data` includes the EvenBetter iOS HIG template fields and correct it from analyzer facts when stale or missing.
10. If the finding is unsupported, too uncertain, missing a usable prompt, or has an uncorrectable guideline reference, set `state.status = "rejected"`, `state.decidedIn = N`, `state.decidedBy = "validator"`, `state.reason` to a concise evidence-based reason, and `state.duplicateOf = null`.

When the host supports isolated sub-agents, such as Claude Code subagents or Codex sub-agents, spawn specialized validator sub-agents by domain or by domain-sized batches. Each validator sub-agent receives only the relevant findings, source excerpts, corpus clauses, URL verification results, and optional primary-source links for its assigned domain. The validator orchestrator alone mutates `analyze-{N}.json`, `manifest.json`, and the HTML report. If isolated sub-agents are unavailable or not permitted, still perform an explicit independent re-evaluation from those artifacts and do not reuse the original auditor's reasoning as evidence.

## Execution Progress

Do not end the conversation after a future-tense status message such as "validation is now running" or "this will take a moment." A progress message is not a final response. After sending any progress update, continue the validation work in the same turn until the analyzer JSON, manifest, and HTML report are written, or until a concrete blocker/error is returned.

Before starting second-pass checks, state the actual execution mode:

- If sub-agents are available and spawned, name the validator sub-agents or batches, for example `typography`, `color-theming`, and `accessibility batch 1`.
- If sub-agents are unavailable, say so once and validate sequentially in explicit domain/batch chunks.

For large reports, especially 20 or more actionable findings, validate in visible chunks of no more than 10 findings per sequential batch, or domain-sized sub-agent batches when sub-agents are available. Provide short progress updates after each completed batch with counts such as `validated 20/95`, rejected findings, severity changes, and guideline corrections so far.

## Output Rules

- Do not write `.evenbetter/evenbetter-validate-{N}.json` for new validation runs.
- Update only the selected `analyze-{N}.json`, `.evenbetter/manifest.json`, and `.evenbetter/evenbetter-validate-{N}.html`.
- Keep real issues visible as analyzer violations with `state.status` unchanged unless the status was already `deferred`.
- Reject non-issues through the existing analyzer violation `state`; do not delete them from analyzer JSON.
- Do not add `kept`, `dropped`, `severity_adjusted`, `not_validated`, confidence, or validation-decision fields to analyzer violations.
- Do not create, revise, or backfill `ai_fix_prompt`. If it is missing or inaccurate, reject the finding with a clear `state.reason` so the analyzer can be rerun.
- Update `.evenbetter/manifest.json` so run `N` has `validated: true`, `status: "validated"` unless already `fixed` or `partially_fixed`, and `html_report: ".evenbetter/evenbetter-validate-{N}.html"`. Preserve `latest.validate` as legacy compatibility data and set `latest.html_report` to the generated HTML path when the `latest` object exists.
- Update `analyze-{N}.json` `run.status` to `validated` unless it is already `fixed` or `partially_fixed`.
- Generate `.evenbetter/evenbetter-validate-{N}.html` from the corrected analyzer JSON. The HTML must render current issues and their analyzer `ai_fix_prompt` values, not validation status. The generator must accept canonical `files[].violations[]` reports and flat top-level `violations[]` reports; for legacy validation JSON reports, it may read kept/severity-adjusted validation buckets only to recover the same issue-card data and evidence links.
- In interactive chat, after a successful run, provide a concise summary of current issues remaining, severities corrected, guideline references corrected, and findings rejected. Include the HTML path, tell the user they can open it in a browser by holding Command and clicking the left mouse button, and tell them to use `$evenbetter-fix` if they want to apply corrections.

Load `references/workflow.md` next.
