# Validator Workflow

Validate is a fast second pass: a deterministic verification pass over `analyze-{N}.json`, escalation only for ambiguous findings, in-place corrections, and an issue-focused HTML report. It is not a re-run of the analyzer.

EvenBetter assumes serial execution. Before writing analyzer or manifest updates, reread `projectPath/.evenbetter/manifest.json` from disk.

## 1. Normalize Inputs

1. If `projectPath` is omitted or `.`, set it to the host's current working directory for this skill invocation.
2. If `projectPath` is relative, resolve it against the host's current working directory.
3. Canonicalize `projectPath` to an absolute path.
4. Default `confidence_threshold` to `0.7`. Accept `0.0`-`1.0`; otherwise emit a JSON error and stop.
5. Accept optional `run` as a positive integer.
6. Accept optional `revalidate` boolean; default `false`.

## 2. Select The Run

Read `projectPath/.evenbetter/manifest.json`.

- If `run` is provided, select that manifest run; require `revalidate: true` if it is already `validated`.
- Otherwise, select the newest run with `validated: false`. If every run is already validated, emit a JSON error and stop.
- If no manifest exists but legacy `.evenbetter/analyze.json` exists, perform the documented migration to `analyze-1.json` + `manifest.json`, then continue with run 1. If neither exists, emit a JSON error.

Read `projectPath/.evenbetter/analyze-{N}.json`. Reject malformed reports. If only `violations[]` exists at the top level, normalize to `files[].violations[]` in memory; the canonical write-back shape is `files[].violations[]`.

Collect every actionable violation: `state.status` not in `fixed`, `rejected`, or `duplicate_of`. Deferred findings remain eligible.

## 3. Fast Verification Pass

Run these deterministic checks per finding. They are cheap, parallel-safe, and need no model judgment.

| Step | Pass | Fail handling |
|---|---|---|
| Source line | `line_number` exists, file readable | reject with `state.reason = "Source line out of range or file unreadable."` |
| Code drift | `code_snippet` still appears within ±5 lines of `line_number` | flag `uncertain: source-drift` |
| Corpus clause | `rule_id` in `../../corpus/index.json` and the H2 clause exists in the linked corpus markdown | reject with `state.reason = "Corpus clause for <rule_id> could not be resolved."` |
| URL | `scripts/verify_url.py <violation.guideline_reference.url>` exits `ok: true` | swap with corpus `source_url` and re-verify; if still failing, flag `uncertain: url-broken` |
| Severity sanity | `severity` matches corpus clause severity | mark `severity-correction` |
| Fix prompt sanity | `ai_fix_prompt` is non-empty, mentions the rule, references the cited line/symbol | reject with `state.reason = "ai_fix_prompt missing or generic."` |
| Fix options sanity | `fix_options` is a 1-4 entry array with exactly one `recommended: true`, distinct labels, valid `kind` values | reject with `state.reason = "fix_options missing or malformed."` |

Bucket each finding into one of: `confirmed`, `severity-correction`, `link-correction`, `rejected`, `uncertain`.

State the bucket counts before continuing — for example: `Fast pass: 38 confirmed, 4 severity-correction, 2 link-correction, 1 rejected, 6 uncertain → escalating uncertain bucket.`

## 4. Escalate Only Uncertain Findings

If the `uncertain` bucket is empty, skip this section.

When the host supports sub-agents (Claude Code's `Agent` tool, Codex sub-agents):

- Split the `uncertain` bucket into batches of ≤10 findings, grouped by file when practical.
- Dispatch one sub-agent per batch in a single message so they run in parallel.
- Pass each sub-agent the violation objects, source excerpts (line ±5), resolved corpus clauses, and URL verification results. Allow it to call the host's native `WebSearch`/`WebFetch` to find primary-source `developer.apple.com` evidence.
- Each sub-agent returns `keep` / `correct severity` / `correct guideline_reference` / `reject` per finding plus a one-sentence justification.

When sub-agents are unavailable:

- Re-evaluate the bucket inline in the main agent, in batches of ≤10.
- After each batch, emit a short progress update: `validated 10/30 (kept 7, corrected 2, rejected 1)`.

Do not end the turn on a future-tense status message. Continue until corrections are applied, manifest is updated, and HTML is generated, or until a concrete blocker is reported.

Do not invent new findings, `rule_id`, `ai_fix_prompt`, or `fix_options` from web research. The analyzer is the only skill that creates those.

## 5. Apply Corrections

Mutate `analyze-{N}.json` per `references/output-contract.md`:

- `severity-correction`: update `severity`.
- `link-correction`: update `guideline_reference.url` (and `label` when needed).
- `rejected`: set `state.status = "rejected"`, `state.decidedIn = N`, `state.decidedBy = "validator"`, `state.reason`, `state.duplicateOf = null`. Do not delete.
- Confirmed findings remain unchanged.

Recompute on the corrected report:

- `total_violations`, `critical_count`
- `domain_summaries[].violation_count` and severity counts
- `files[].score`, `ui_score`, `ux_score`, `a11y_score`
- project `overall_score`, `ui_score`, `ux_score`, `a11y_score`
- `executive_summary` only when corrections materially changed posture
- `html_report_data` (especially `summary` and `scan_context.files_scanned`)

Set `analyze-{N}.json` `run.status = "validated"` unless it is already `fixed` or `partially_fixed`.

## 6. Update Manifest

Reread `manifest.json`. Update the matching run entry:

- `validated: true`
- `status: "validated"` unless already `fixed` or `partially_fixed`
- `html_report: "evenbetter-validate-{N}.html"` or `.evenbetter/evenbetter-validate-{N}.html` (match the manifest's existing path style)
- `summary` recomputed from violation `state.status` values

Update `latest.html_report` to the generated HTML when the manifest has a `latest` object. Preserve `latest.analyze`, `latest.validate` (legacy), `currentRun`, and unrelated run entries.

## 7. Generate HTML

Run:

```text
scripts/generate_html_report.py --analyze projectPath/.evenbetter/analyze-{N}.json --manifest projectPath/.evenbetter/manifest.json --output projectPath/.evenbetter/evenbetter-validate-{N}.html
```

The HTML must render only current issues (`state.status` is `open` or `deferred`), pull dashboard/scan-context from `html_report_data`, surface each finding's `fix_options` for the end user, and avoid validation-status UI (no kept/dropped/severity-adjusted blocks). Issue cards include `id`, `summary`, `severity`, `rule_id`, `dimension`, `file_path`, `line_number`, `code_snippet`, `fix_description`, optional `fix_code`, `ai_fix_prompt`, `fix_options`, and `guideline_reference`.

Legacy `.evenbetter/evenbetter-validate-{N}.json` files may still exist for older projects; the generator's `--validation` argument accepts them as input. Do not write a new validation JSON.

## 8. Chat Summary

```text
Validation complete.
- Updated: .evenbetter/analyze-{N}.json
- HTML report: .evenbetter/evenbetter-validate-{N}.html
- Current issues: <total> total (<error> error, <warning> warning, <info> info)
- Corrections: <severity> severity, <links> guideline links, <rejected> rejected

Open the HTML report in a browser by holding Command and clicking the left mouse button on the path. To apply corrections, use $evenbetter-fix.
```

When invoked by automation, keep stdout concise and do not emit a validation report JSON object.

## 9. Compaction-Safe Invariants

- Report history is indexed by `.evenbetter/manifest.json`.
- `projectPath` defaults to the invocation working directory when omitted.
- Default target is the newest unvalidated analyzer run.
- The fast pass is deterministic; only the `uncertain` bucket escalates to sub-agents or web research.
- Web research uses host-native tools only (`WebSearch`/`WebFetch` in Claude Code).
- Validation never creates new `rule_id`, `ai_fix_prompt`, or `fix_options`.
- Validation does not write `.evenbetter/evenbetter-validate-{N}.json`.
- HTML path is `.evenbetter/evenbetter-validate-{N}.html`.
- Wrong severities and guideline references are corrected in analyzer JSON.
- Non-issues are rejected through `state.status = "rejected"` with `decidedBy = "validator"`.
- Source/project files are read-only except for analyzer report, manifest, and HTML report writes inside `.evenbetter/`.
