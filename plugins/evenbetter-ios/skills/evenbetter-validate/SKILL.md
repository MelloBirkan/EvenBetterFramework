---
name: evenbetter-validate
description: Validates the HTML audit report produced by evenbetter-analyze by re-reading each finding against the source code, the EvenBetter iOS corpus, and Apple HIG / Apple Developer Documentation, then auto-corrects the report in place. Confirms whether each issue is genuine, whether its severity is right, and whether `minimal_fix`, `recommended_fix`, and `ai_fix_prompt` actually resolve the violation. Removes false positives, promotes warnings that should be critical, demotes findings that are over-flagged, and rewrites incorrect fixes directly inside `.evenbetter/<project>/evenbetter-analyze-report.html`. Returns a one-line "OK" status when nothing needs to change. Use this skill whenever the user asks to validate, verify, double-check, sanity-check, audit-the-audit, fix-up, refine, or correct an EvenBetter analyze report, an `evenbetter-analyze-report.html`, or its findings, fixes, or severities.
---

# evenbetter-validate

## Operating model

This skill is the second pass after `evenbetter-analyze`. It treats the existing HTML report as authoritative input, re-checks every finding against the live source code, the EvenBetter iOS corpus, and official Apple documentation, then writes corrections back into the same HTML file. The HTML stays the single source of truth — there are no parallel JSON or Markdown deliverables.

- The audit is corpus-first. Every finding carries a `clause_id` that points to a specific H2 block in `../../corpus/ios/<domain>.md`. The clause's **Check**, **Why**, **Correct code**, `Severity`, and `Source` are the binding contract. Validate against the clause body, not just the captured snippet.
- The report is loaded by extracting the `reportData` JavaScript object literal from `.evenbetter/<project>/evenbetter-analyze-report.html`.
- Every finding is re-validated using the same corpus and Apple-first research rules as `evenbetter-analyze`. Findings whose clause no longer matches the live source, whose Apple URL no longer states the rule, or whose `clause_id` is missing from `../../corpus/index.json`, are removed.
- Fixes are reviewed for correctness, not just style. A `minimal_fix` that does not actually close the violation is rewritten. A `recommended_fix` that is not structurally aligned with the clause's **Correct code** block — the system-native Apple-blessed approach — is upgraded.
- Severity is realigned by mapping the corpus `severity` field through the four-tier model documented below. Warnings with strong evidence and direct user impact are promoted; over-flagged findings are demoted.
- The report is rewritten in place. The `summary` counts and the JS literal are regenerated. No other files are produced.
- Every pass stamps the report's `workflow` block with `state: "validated"` and the current `validated_at` time. That stamp is the precondition `evenbetter-repair` checks before it is allowed to touch source code, so it is written even on a clean pass — it is the one thing a clean pass changes.
- If no finding changes, the skill reports a single "OK — N findings validated, no changes needed" line and rewrites nothing but the workflow stamp.

Former slash-command names may be aliases. Interpret `/evenbetter-validate:2-validate` as "use `evenbetter-validate` with stage `2-validate`."

## Workflow position

Validation is the third of four EvenBetter interaction states: planning, analysis, validation, repair. It sits between the audit and the code changes, and it is the only thing that authorizes them.

- `evenbetter-analyze` runs before, writing `workflow.state = "analyzed"`.
- This skill promotes the report to `workflow.state = "validated"` and stamps `workflow.validated_at`.
- `evenbetter-repair` runs after. It refuses any report whose state is still `analyzed`, or whose `validated_at` predates `scan_date`, so an unvalidated finding can never reach the codebase.

Validation is also the loop's closing move. Running it again after a repair pass removes findings whose violation is genuinely gone, and flips any finding that a repair claimed to fix but did not into `failed` so the next repair run picks it up. See the repair re-check rule in `references/2-validate.md`.

## Question tooling

Validation should not need questions. Ask only when the report path is ambiguous (multiple `.evenbetter/<name>/` folders for sibling sub-projects) or when the user explicitly scoped validation to a subset (severities, file globs, clause IDs). When asking is necessary, use the best available structured-question tool with mutually exclusive options:

- Claude Code: `AskUserQuestion` with 2-4 options.
- Codex Plan mode: `request_user_input` when available.
- Cursor or other agents with an ask-question tool: the native structured tool.
- Environments without structured questions: one closed question with numbered options.

Never ask open-ended questions during validation. Default to validating every finding in the most recent `.evenbetter/<project>/evenbetter-analyze-report.html`.

## Tool equivalents

The reference files mention Claude-style tool names. Apply these equivalents in Codex:

| Claude command instruction | Codex equivalent |
| --- | --- |
| `AskUserQuestion` | `request_user_input` in Plan mode when available, otherwise a concise closed question |
| `Glob`, `Grep`, `Read` | `rg --files`, `rg`, and shell file reads such as `sed` or `nl` |
| `Bash` | `exec_command` |
| `WebSearch`, `WebFetch` | available web-search tooling, or official Apple documentation lookup |
| `TaskCreate`, `TaskUpdate` | `update_plan` |
| `ref_search_documentation`, `ref_read_url` | available official-doc tooling, otherwise direct fetch of Apple documentation URLs |

If current system or developer instructions conflict with a converted reference, follow the higher-priority instruction.

## Stage selection

Run the stages in order. Stage 3 always runs — even a clean pass has to write the workflow stamp — but it only rewrites findings when stage 2 produced a change.

| Stage | Reference | Use when |
| --- | --- | --- |
| `1-load` | `references/1-load.md` | Locate and parse the `reportData` object from `.evenbetter/<project>/evenbetter-analyze-report.html`. |
| `2-validate` | `references/2-validate.md` | Re-check every finding for genuineness, severity, and fix correctness, and decide `keep`, `adjust`, or `remove`. |
| `3-update` | `references/3-update.md` | Always. Stamp `workflow` in the HTML, and when any decision was `adjust` or `remove`, also rewrite the findings and recompute summary counts. |

## Decision model

Every finding ends in exactly one of three states. The state determines what the report looks like after stage 3:

| Decision | Trigger | Effect on the report |
| --- | --- | --- |
| `keep` | Source still violates the clause, severity matches the mapping, both fixes resolve the violation, AI prompt is paste-ready, Apple URL still supports the rule. | No change. Finding stays as-is. |
| `adjust` | The finding is real but at least one of severity, `minimal_fix`, `recommended_fix`, `ai_fix_prompt`, `wcag_criteria`, `wcag_level`, or `hig_reference_url` is wrong or stale. | Update only the wrong fields. Keep `id`, `clause_id`, `file_path`, `line_number`, and `code_snippet` unless the underlying line moved. |
| `remove` | Source no longer matches (false positive, fixed since scan, parent already satisfies clause, decorative-only context), or the Apple URL no longer states the rule and no replacement exists. | Drop the finding from `issues`. Recompute `summary`. |

A finding carrying `repair.status` of `applied` is the one case where validation writes into the repair ledger: if the finding survives the source check, the repair did not close the violation, so set `repair.status` to `failed` with a one-sentence `note` and count the finding as `adjust`. Every other `repair` field is carried through untouched.

Promotion (`warning` → `critical`) and demotion (`high` → `medium`, `medium` → `low`) both count as `adjust`. Use the severity mapping documented in `evenbetter-analyze/SKILL.md`:

- `critical` — user harm, accessibility blocker, destructive risk, high-confidence violation.
- `high` — meaningful user impact and high confidence the rule applies.
- `medium` — conformance concern with broader uncertainty or context-dependent impact.
- `low` — polish, consistency, or non-blocking quality improvement.

## Artifact rules

- Only ever read and write `.evenbetter/<project-name>/evenbetter-analyze-report.html`. Do not create new folders, sibling JSON exports, or Markdown summaries.
- Preserve the `<script>` block surrounding `const reportData = …;`. Replace only the literal between `const reportData = ` and the next `};`.
- Do not touch the rest of the HTML template — markup, styles, Alpine bindings, and CDN references must stay byte-identical.
- Recompute `summary.total`, `summary.critical`, `summary.high`, `summary.medium`, and `summary.low` from the surviving `issues` array before writing.
- Bump `scan_date` to the current local time in `YYYY-MM-DD HH:MM:SS` format only when at least one finding was adjusted or removed. Leave it untouched on a clean pass.
- Always write the workflow stamp: `workflow.state` becomes `validated`, `workflow.validated_at` becomes the current local time, and `workflow.validation` carries the `kept`/`adjusted`/`removed` tally. This is the sole exception to the clean-pass no-write rule, and `validated_at` must be stamped at or after `scan_date` so `evenbetter-repair`'s freshness check passes.
- Never write `workflow.state = "repaired"` and never touch `workflow.repaired_at` or `workflow.repair`. Those belong to `evenbetter-repair`; carry them through unchanged.
- After writing, surface the absolute file path to the user as a `file://` link or a copyable path, plus a short tally such as `OK — 12 kept, 3 adjusted, 2 removed`. On a clean pass, the response is a single `OK — N findings validated, no changes needed` line.

## Corpus rules

Treat `../../corpus/index.json` and `../../corpus/ios/*.md` as the authoritative rule layer. The corpus paths are identical to `evenbetter-analyze` because validate runs from the same skill root:

- Read `../../corpus/index.json` once per validation run and group findings by `clause_id`. The index gives `domain`, `dimension`, `severity`, `source_url`, `source_label`, `file_path`, `anchor`, and `retrieved` for every clause.
- Lazy-load `../../corpus/ios/<domain>.md` the first time a finding from that domain needs verification. Each clause is one H2 section keyed by clause ID and contains four binding fields: **Check** (what to detect), **Why** (user impact), **Correct code** (Swift example), and the metadata block with `Severity` and `Source`.
- The clause's **Check** description is the contract for the source-code re-read — the captured `code_snippet` must still match the **Check** condition in context. The clause's **Correct code** block is the contract for `recommended_fix` — the proposed remediation must be structurally aligned with it.
- The corpus index `source_url` is the canonical Apple URL. If a finding's `hig_reference_url` differs from the index value, replace it with the index value rather than refetching the old URL.
- If a `clause_id` on a finding is not present in `../../corpus/index.json`, the clause has been removed or renamed since the report was generated. The finding is `remove`. Do not try to rebind it to a sibling clause.
- Note any clause whose `retrieved` date in `index.json` is newer than the report's `scan_date` — it indicates the corpus moved between scan and validation, so the clause body, not the report's recorded fields, is the source of truth for that finding.

## Research rules

Read `../evenbetter-analyze/references/official-sources.md` before re-checking any HIG, WCAG, or SwiftUI claim. Validation must use the same Apple-first research discipline as `evenbetter-analyze`:

- Re-confirm each `hig_reference_url` resolves and still states the rule the corpus clause encodes. If the page moved, replace the URL with the corpus index `source_url` first; only refetch externally if the index value is also stale.
- Use WCAG 2.2 only as a cross-reference, never as the primary citation. The `wcag_criteria` and `wcag_level` fields stay aligned with the Apple-supported claim, not the other way around.
- Do not invent URLs. A finding without a verifiable Apple HIG or Apple Developer Documentation URL — and no matching `source_url` in `../../corpus/index.json` — is removed.

## iOS skill integration

- Use `evenbetter-swiftui-accessibility` clause loading when an accessibility finding's clause body is unclear after corpus re-read.
- Use `evenbetter-swiftui-ui-patterns` references for SwiftUI navigation, sheets, forms, controls, theming, and Dynamic Type background context when judging fix correctness.
- Use `evenbetter-swiftui-view-refactor` heuristics when a `recommended_fix` should be a structural decomposition rather than a single modifier change.
- Use `evenbetter-swiftui-liquid-glass` only when iOS 26+ Liquid Glass APIs are involved in the finding under review.
- Use `evenbetter-ios-debugger-agent` to capture simulator screenshots when a visual rule (contrast, layout, large Dynamic Type) needs runtime evidence to confirm or reject a finding.
- Hand off to `evenbetter-repair` once the pass is clean or the corrections are written. Do not edit application source code from this skill — validation corrects the report, repair corrects the project.
