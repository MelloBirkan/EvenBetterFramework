# 3 Report

Contents: Role, Process, Top-level data shape, Finding object schema, Scan context, Workflow state, Pre-write checks, Writing the report by hand, After writing.

## Role

Turn the verified findings into the report data object and render it into `references/report-template.html` at `.evenbetter/[project]/evenbetter-analyze-report.html`.

## Process

1. Resolve `[project]` and `project_name` as the Artifact rules in SKILL.md describe.
2. Build the data object with the schemas below. Fill every field of every finding.
3. With `python3` available, use the report helper at `../../scripts/evenbetter_report.py` (resolve it against the SKILL.md folder):
   - Write the data object as JSON to a temporary file outside the project, for example one made with `mktemp`.
   - Run `python3 [script] render [data file] [project root]/.evenbetter/[project]/evenbetter-analyze-report.html --state analyzed`. It checks the data, creates the folder, moves an existing report to `history/evenbetter-analyze-report-[YYYYMMDD-HHMMSS].html` (named after that report's `scan_date`), and writes the new one with the data safely escaped.
   - If it prints problems, it wrote nothing. Fix the data and run it again. Then delete the temporary file.
4. Without `python3`, follow Writing the report by hand below, then run the Pre-write checks yourself before writing.
5. Finish with After writing.

## Top-level data shape

```json
{
  "project_name": "string, the app's human-readable name, e.g. \"PlantCare\"",
  "project_path": "string, absolute project root",
  "framework": "string, e.g. \"SwiftUI\" or \"SwiftUI + UIKit\"",
  "wcag_level": "string, the conformance target the report claims: \"A\", \"AA\" or \"AAA\" (default \"AA\")",
  "scan_date": "string, \"YYYY-MM-DD HH:MM:SS\" in local time",
  "workflow": {
    "state": "analyzed",
    "validated_at": "",
    "validation": { "kept": 0, "adjusted": 0, "removed": 0 },
    "repaired_at": "",
    "repair": { "applied": 0, "deferred": 0, "skipped": 0, "failed": 0 }
  },
  "summary": { "total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0 },
  "issues": [],
  "scan_context": {
    "frameworks": ["SwiftUI"],
    "framework_versions": { "SwiftUI": "iOS 17.0 deployment target" },
    "design_systems": [],
    "component_patterns": [],
    "custom_utilities": [],
    "scan_duration": 0.0,
    "files_scanned": 0,
    "confidence": 1.0,
    "notes": []
  }
}
```

`summary` counts must match the `issues` array exactly; the severity filter chips in the report depend on them.

## Finding object schema

Keep the keys in this order.

```json
{
  "id": "string, \"EB-001\", \"EB-002\", ... in report order",
  "clause_id": "string, the primary corpus clause, e.g. \"COMP-UI-001\"",
  "related_clause_ids": ["other clause IDs the same edit closes; [] when none"],
  "title": "string, short imperative title in user-facing language",
  "description": "string, 1-3 sentences on what goes wrong for users",
  "severity": "critical | high | medium | low",
  "wcag_criteria": "string, one WCAG 2.2 criterion such as \"2.5.8\", or \"\"",
  "wcag_level": "A | AA | AAA | \"\" (the criterion's own level)",
  "hig_reference_url": "string, the index.json source_url of clause_id",
  "file_path": "string, project-relative path of the file the fix changes",
  "line_number": 1,
  "code_snippet": "string, verbatim contiguous source lines, no elisions",
  "minimal_fix": "string, complete replacement for code_snippet",
  "recommended_fix": "string, complete replacement for code_snippet",
  "ai_fix_prompt": "string, paste-ready prompt naming every file it touches",
  "language": "swift",
  "repair": {
    "status": "pending",
    "path": "",
    "owner": "",
    "applied_at": "",
    "changed_files": [],
    "note": ""
  },
  "runtime": {
    "status": "untested",
    "checked_at": "",
    "configs": [],
    "tests": [],
    "evidence": "",
    "result_bundle": ""
  }
}
```

Every field is required. The template binds directly to these keys, so a missing field renders as an empty string or breaks the card. The card shows `clause_id` and each of `related_clause_ids` as badges.

The nested `repair` object is the per-finding remediation ledger. This skill always writes the `pending` shape above with every string empty. Only evenbetter-repair sets `status` to `applied`, `deferred` or `skipped`, and only it writes `path`, `owner`, `applied_at` and `changed_files`. evenbetter-repair and evenbetter-validate can both set `failed` and write `note`; validate does it only when an `applied` finding's repair did not hold.

The nested `runtime` object, right after `repair`, holds the result of a check on the running app. This skill always writes the `untested` shape above, because a new scan has not been tested yet. Only evenbetter-accessibility-tests writes another status (`confirmed`, `refuted`, `inconclusive` or `not_testable`) and fills `checked_at`, `configs`, `tests`, `evidence` and `result_bundle`. The card shows a badge for those statuses and nothing for `untested`. The helper's `render` refuses any `runtime` block that differs from that empty `untested` shape.

## Scan context

Use empty arrays and `0` for unknowns, never `null`. `framework_versions` values are short strings; mark versions inferred from API use, for example `"iOS 17+ (inferred)"`.

`notes` is the audit log, shown in the report's Scan Context panel. Add one short sentence per item, starting with its kind:

- `Static audit: ...` when visual findings rest on computed values because no simulator or screenshots were available.
- `Corpus drift: ...` for a clause whose Apple source no longer supports it (clause ID, URL, what changed).
- `Outside the corpus: ...` for a real problem no clause covers and no finding's fix closes.
- `Left out: ...` when the user limited the audit and verified findings were not included.
- `Manual check: ...` when a clause's Check asks a person to look at something a static scan cannot judge, such as captions on web-embedded video for `A11Y-A11Y-009`.
- `Sources not re-fetched: ...` when no fetch tool worked.

`confidence` says how strongly the audit ran, from 0 to 1:

- 1.0: the whole repository was scanned, and every visual finding has runtime evidence (or there are no visual findings).
- 0.8: the whole repository was scanned, but visual findings rest on computed values.
- 0.5 or lower: only part of the repository was in scope or readable. Say which part in `notes`.
- Subtract 0.1 more when the Apple sources could not be fetched.

## Workflow state

The `workflow` block records where the report sits in the four-state EvenBetter model: planning, analysis, validation, repair. It is the handoff contract between evenbetter-analyze, evenbetter-validate and evenbetter-repair.

This skill always writes the freshly scanned shape shown above: `state` is `analyzed`, both stamps are empty, and every tally is `0`. That holds even when the previous report was validated or repaired, because a new scan invalidates the earlier review. The previous report is kept in `history/`, so its decisions, repair notes and runtime verdicts are still there to read.

evenbetter-validate promotes the report to `validated` and stamps `validated_at`. evenbetter-repair refuses a report whose `state` is still `analyzed`, or whose `validated_at` is older than `scan_date`.

## Pre-write checks

The helper's `render` with `--state analyzed` runs all of these for you, except that it does not check where `runtime` sits among a finding's keys. `check` runs all but the last two: it checks the `workflow` block against the report's own state, and it accepts runtime verdicts, because a report that has been through validate, repair or evenbetter-accessibility-tests carries them. When writing by hand, confirm each one before writing:

- Every top-level key is present; `scan_date` uses `YYYY-MM-DD HH:MM:SS`; `project_path` is absolute; `wcag_level` is `A`, `AA` or `AAA`.
- `summary.total` equals `issues.length`, and each severity count matches the array.
- Each `id` is unique and has the `EB-001` form.
- Each `clause_id` and every entry of `related_clause_ids` exists in `../../corpus/index.json`, and no clause is listed twice on one finding.
- Each `hig_reference_url` starts with `https://developer.apple.com/` and equals the index `source_url` of its `clause_id`.
- Each `severity` is `critical`, `high`, `medium` or `low` and fits the SKILL.md table for the finding's clauses.
- `wcag_criteria` and `wcag_level` are both set or both empty; the level is the criterion's own level and not above the report's target.
- `code_snippet`, `minimal_fix` and `recommended_fix` are non-empty and contain no `// ...` or `…` elisions. A fix with `// File:` parts starts with one, and its paths are project-relative.
- `ai_fix_prompt` names `file_path` and every `// File:` path.
- No two findings at the same file and line share a clause or split a twin pair from `references/2-verify.md`, and no construct carries both clauses of an exclusive pair from that file (`LAY-A11Y-001` and `LAY-UI-001`, `TYPO-A11Y-004` and `TYPO-A11Y-005`).
- `workflow.state` is `analyzed`, both stamps are empty strings, every tally is `0`, and every finding's `repair` has `status: "pending"`, empty strings and an empty `changed_files` array.
- Every finding's `runtime` comes right after `repair` and is the `untested` shape: `status: "untested"`, empty `checked_at`, `evidence` and `result_bundle`, and empty `configs` and `tests` arrays.

If any check fails, fix the data before writing. Do not write a partial report.

## Writing the report by hand

Only when `python3` is not available:

1. If `.evenbetter/[project]/evenbetter-analyze-report.html` exists, read its `"scan_date"` value and move the file to `.evenbetter/[project]/history/evenbetter-analyze-report-[YYYYMMDD-HHMMSS].html` using that date (create `history/` first; add `-2` if the name is taken).
2. Read `references/report-template.html` as text. It holds one placeholder, `__EVENBETTER_REPORT_DATA__`, inside the line `const reportData = __EVENBETTER_REPORT_DATA__;`.
3. Serialize the data object as JSON with 2-space indentation, keeping the finding keys in schema order, so each `runtime` block sits right after `repair`. Then escape the sequences that could break the `<script>` element: replace every `</` with `<\/`, every `<!--` with `\u003c!--`, and the characters U+2028 and U+2029 with `\u2028` and `\u2029`. All of these are still valid JSON.
4. Replace the placeholder with the escaped JSON, without adding quotes; the JSON literal is valid JavaScript. Keep the `;` that follows it.
5. Write the result to `.evenbetter/[project]/evenbetter-analyze-report.html`, creating the folder with `mkdir -p` if needed.

## After writing

Give the user the absolute path as a `file://` link (or the workspace-relative path if `file://` does not suit the host), one line with the finding count by severity, and this next step: "Next, run the evenbetter-validate skill." Then stop.

Do not summarize the findings in chat; the user opens the report to read them. If the audit found nothing, say so in one sentence and still write the report: the template shows an "All clear" state for an empty `issues` array.
