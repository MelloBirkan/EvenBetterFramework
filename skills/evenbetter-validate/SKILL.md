---
name: evenbetter-validate
description: Read-only validator for EvenBetter iOS analyzer reports. Use to validate audit results, check evenbetter-analyze findings for hallucination, verify high-severity violations, recompute confidence, verify guideline URLs, and write .evenbetter/evenbetter-validate.json from .evenbetter/analyze.json.
---

# evenbetter-validate

## Overview

Validate high-severity EvenBetter iOS analyzer findings with a second-pass evidence check. Treat this as the validator half of the orchestrator-workers-with-validators pattern: analyzer workers propose findings, then this skill rechecks source evidence and corpus support before keeping a high-severity violation.

## Inputs

- `projectPath` (required): Absolute path to the analyzed SwiftUI project.
- `confidence_threshold` (optional): Float from `0.0` to `1.0`. Default to `0.7`.

If `projectPath` is missing or not absolute, return a JSON error object with an `error` key and stop.

## Source Safety

Do not edit, delete, format, generate, or execute source/project files inside `projectPath`. The only permitted write inside `projectPath` is creating `.evenbetter/` if needed and writing the final validation report to `.evenbetter/evenbetter-validate.json`.

## Required References

Load only what the current phase needs:

- `references/workflow.md`: Validation loop, evidence checks, confidence decisions, and compaction-safe invariants.
- `references/output-contract.md`: Stable JSON envelope and finding result fields.
- `references/architecture.md`: Orchestrator-worker-with-validators decomposition and citation note.
- `scripts/verify_url.py`: Deterministic URL verifier for Apple and W3C sources.

## Validation Scope

Read `projectPath/.evenbetter/analyze.json`. Validate only violations where `severity` is `error`; this is the current analyzer's high-severity class.

For each high-severity finding:

1. Re-read the cited Swift file and nearby lines.
2. Re-load the analyzer rule clause that matches `rule_id`.
3. Verify `guideline_reference.url` with `scripts/verify_url.py`.
4. Independently judge whether the cited code violates the rule.
5. Emit `confidence`, `reasoning`, and `decision`.

When the host supports isolated subagents, run the judgment in a fresh validator context that receives only the finding, source excerpt, corpus clause, and URL result. If isolated subagents are unavailable or not permitted, still perform an explicit independent re-evaluation from those artifacts and do not reuse the original auditor's reasoning as evidence.

## Output Rules

- Write one JSON object to `projectPath/.evenbetter/evenbetter-validate.json`.
- Emit the same JSON object on stdout when running headless.
- Use `kept`, `downgraded`, and `dropped` arrays exactly as defined in `references/output-contract.md`.
- Keep only findings with `confidence >= confidence_threshold`, valid source evidence, resolved corpus clause, coherent reasoning, and a verified source URL.
- Include `drop_reason` for every dropped finding.
- Do not wrap JSON in Markdown fences or add prose to JSON-only outputs.

Load `references/workflow.md` next.
