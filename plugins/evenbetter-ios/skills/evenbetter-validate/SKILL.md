---
name: evenbetter-validate
description: Validator for numbered EvenBetter iOS analyzer reports. Use to validate audit results, check evenbetter-analyze findings for hallucination, verify every actionable violation, confirm severity accuracy, verify analyzer-generated ai_fix_prompt accuracy, verify guideline URLs, use native web search or documentation lookup when extra confirmation is needed, write .evenbetter/evenbetter-validate-{N}.json from .evenbetter/analyze-{N}.json using .evenbetter/manifest.json, and generate .evenbetter/evenbetter-validate-{N}.html for browser review.
---

# evenbetter-validate

## Overview

Validate EvenBetter iOS analyzer findings with a second-pass evidence check. Treat this as the validator half of the orchestrator-workers-with-validators pattern: analyzer workers propose findings and `ai_fix_prompt` values, then this skill rechecks source evidence, corpus support, severity, URL validity, optional web evidence, and fix prompt accuracy before marking a finding as validated.

## Inputs

- `projectPath` (required): Absolute path to the analyzed SwiftUI project.
- `confidence_threshold` (optional): Float from `0.0` to `1.0`. Default to `0.7`.
- `run` (optional): Analyzer run number to validate. Default is the latest unvalidated analyzer run in `.evenbetter/manifest.json`.
- `revalidate` (optional): Boolean. Default `false`; when `true`, allow replacing `evenbetter-validate-{N}.json` for an already validated run.

If `projectPath` is missing or not absolute, return a JSON error object with an `error` key and stop.

## Source Safety

Do not edit, delete, format, generate, or execute source/project files inside `projectPath`. The only permitted writes inside `projectPath` are creating `.evenbetter/` if needed, writing the final validation report to `.evenbetter/evenbetter-validate-{N}.json`, writing the derived browser report to `.evenbetter/evenbetter-validate-{N}.html`, updating `.evenbetter/manifest.json`, and setting `run.status` in `.evenbetter/analyze-{N}.json` to `validated`.

## Required References

Load only what the current phase needs:

- `references/workflow.md`: Validation loop, evidence checks, confidence decisions, and compaction-safe invariants.
- `references/output-contract.md`: Stable JSON envelope and finding result fields.
- `references/architecture.md`: Orchestrator-worker-with-validators decomposition and citation note.
- `scripts/verify_url.py`: Deterministic URL verifier for Apple and W3C sources.
- `scripts/generate_html_report.py`: Deterministic HTML report generator for all analyzer findings plus validator decisions.

## Validation Scope

Read `projectPath/.evenbetter/manifest.json` and select the analyzer run to validate. By default, validate only the newest run whose manifest entry has `validated: false` or no paired `validate` file. If `run` is provided, validate that analyzer run; if it already has a paired validation report, require `revalidate: true`.

Read `projectPath/.evenbetter/analyze-{N}.json` for the selected run. Validate every violation where `state.status` is not `fixed`, `rejected`, or `duplicate_of`. Deferred findings remain eligible because validation checks evidence and prompt quality, not user fix scheduling.

For each actionable finding:

1. Re-read the cited Swift file and nearby lines.
2. Resolve the corpus clause for `rule_id` through `../../corpus/index.json`, then read the matching H2 section from the indexed corpus markdown file.
3. Verify `guideline_reference.url` with `scripts/verify_url.py`.
4. When the local corpus and verified guideline URL do not fully resolve uncertainty, use the host AI agent's native web search, web fetch, or documentation lookup tools to find a primary-source confirmation link.
5. Independently judge whether the cited code violates the rule.
6. Confirm whether the analyzer severity is correct; if not, record the corrected severity in the validation result.
7. Verify that `ai_fix_prompt` is present, scoped to this finding, and accurate for the source evidence and rule.
8. Emit `confidence`, `reasoning`, `decision`, prompt assessment fields, and any `supporting_links`.

When the host supports isolated subagents, run the judgment in a fresh validator context that receives only the finding, source excerpt, corpus clause, and URL result. If isolated subagents are unavailable or not permitted, still perform an explicit independent re-evaluation from those artifacts and do not reuse the original auditor's reasoning as evidence.

## Output Rules

- Write one JSON object to `projectPath/.evenbetter/evenbetter-validate-{N}.json`.
- Generate `projectPath/.evenbetter/evenbetter-validate-{N}.html` after the validation JSON and manifest updates complete.
- Emit the same JSON object on stdout when running headless.
- Use `kept`, `severity_adjusted`, and `dropped` arrays exactly as defined in `references/output-contract.md`.
- Keep only findings with `confidence >= confidence_threshold`, valid source evidence, resolved corpus clause, coherent reasoning, a verified source URL, and an accurate analyzer-generated `ai_fix_prompt`.
- Include `drop_reason` for every dropped finding.
- Include `supporting_links` when the validator used a guideline, corpus source, or native web lookup link that helps substantiate the decision. Not every finding needs an extra web-discovered link.
- Include `validates: "analyze-{N}.json"` and `analyzer_run: N`.
- Include `html_report: ".evenbetter/evenbetter-validate-{N}.html"` in the validation report object.
- Update `.evenbetter/manifest.json` so run `N` has `validate: "evenbetter-validate-{N}.json"` and `validated: true`.
- Do not wrap JSON in Markdown fences or add prose to JSON-only outputs. In interactive chat, after a successful run, provide a concise summary and include `Click here to open .evenbetter/evenbetter-validate-{N}.html`.

Load `references/workflow.md` next.
