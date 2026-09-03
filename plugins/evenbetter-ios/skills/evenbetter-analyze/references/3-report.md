# 3 Report

## Role

Render the verified findings into the interactive HTML template at `.evenbetter/<project-name>/evenbetter-analyze-report.html`.

## Process

1. Resolve `<project-name>`. Reuse an existing `.evenbetter/<name>/` folder when one exists. Otherwise derive the name from the project root in kebab-case.
2. Make sure `.evenbetter/<project-name>/` exists. Create it with `mkdir -p` if needed.
3. Read `references/report-template.html` once. Treat it as a string with a single placeholder, `__EVENBETTER_REPORT_DATA__`, that must be replaced with a JavaScript object literal containing the audit data.
4. Build the data object using the schema in this file. Make sure every issue is fully populated — the template will not render finds that have missing fields.
5. Serialize the data object to JSON. Use the same JSON shape that the template's `reportApp()` function expects: a single object containing `project_name`, `project_path`, `framework`, `wcag_level`, `scan_date`, `workflow`, `summary`, `issues`, and `scan_context`.
6. Replace `__EVENBETTER_REPORT_DATA__` in the template with the serialized JSON. Do not add quoting around it — the placeholder sits inside a JavaScript expression and the JSON literal is itself valid JavaScript.
7. Write the populated template to `.evenbetter/<project-name>/evenbetter-analyze-report.html`. Overwrite any prior report.
8. After writing, return the absolute path to the user as a copyable line, optionally formatted as a `file://` URL. Keep any accompanying message short — the deliverable is the file, not the chat output.

## Top-level data shape

```json
{
  "project_name": "string, human-readable project name",
  "project_path": "string, absolute project root",
  "framework": "string, e.g., \"SwiftUI\" or \"SwiftUI + UIKit\"",
  "wcag_level": "string, e.g., \"AA\" — the conformance target the report claims",
  "scan_date": "string, \"YYYY-MM-DD HH:MM:SS\" in local time",
  "workflow": {
    "state": "analyzed",
    "validated_at": "",
    "validation": { "kept": 0, "adjusted": 0, "removed": 0 },
    "repaired_at": "",
    "repair": { "applied": 0, "deferred": 0, "skipped": 0, "failed": 0 }
  },
  "summary": {
    "total": 0,
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0
  },
  "issues": [ /* finding objects, schema below */ ],
  "scan_context": {
    "frameworks": ["SwiftUI"],
    "framework_versions": { "SwiftUI": "5.0" },
    "design_systems": [],
    "component_patterns": [],
    "custom_utilities": [],
    "scan_duration": 0.0,
    "files_scanned": 0,
    "confidence": 0.0
  }
}
```

`scan_context` is optional in spirit but the template renders cleanly when it is present, so always include it. Use empty arrays and `0` values for unknowns instead of `null`. Set `confidence` to a value between 0 and 1 representing how strongly the audit ran (1.0 = full repo scan with all corpus domains; 0.5 = partial scope or missing source files).

## Finding object schema

```json
{
  "id": "string, stable per audit, e.g., \"EB-001\"",
  "title": "string, short imperative phrasing of the issue",
  "description": "string, 1-3 sentences of user-impact context",
  "severity": "critical | high | medium | low",
  "wcag_criteria": "string, WCAG 2.2 SC ID or \"\"",
  "wcag_level": "A | AA | AAA | \"\"",
  "hig_reference_url": "string, canonical Apple HIG or Apple Developer URL — required",
  "file_path": "string, project-relative path",
  "line_number": 0,
  "code_snippet": "string, raw Swift source",
  "minimal_fix": "string, smallest mechanical patch",
  "recommended_fix": "string, system-native best-practice fix",
  "ai_fix_prompt": "string, paste-ready prompt for an AI coding agent",
  "language": "swift",
  "repair": {
    "status": "pending",
    "path": "",
    "owner": "",
    "applied_at": "",
    "changed_files": [],
    "note": ""
  }
}
```

Every field is required. The HTML template binds directly to these keys via Alpine `x-text` and `:href` directives, so missing fields render as empty strings or break the issue card layout.

The nested `repair` object is the per-finding remediation ledger. `evenbetter-analyze` never fills it in — it always writes the `pending` shape above and leaves every string empty. Only `evenbetter-repair` may set `status` to `applied`, `deferred`, `skipped`, or `failed`, and only `evenbetter-repair` writes `path`, `owner`, `applied_at`, `changed_files`, or `note`.

## Workflow state

The `workflow` block records where the report sits in the four-state EvenBetter interaction model: planning, analysis, validation, repair. It is the handoff contract between `evenbetter-analyze`, `evenbetter-validate`, and `evenbetter-repair`.

`evenbetter-analyze` always writes the freshly-scanned shape:

- `state` is `analyzed`. Never write `validated` or `repaired` from this skill, even when re-scanning a project whose previous report carried one of those states — a new scan invalidates any prior validation.
- `validated_at`, `repaired_at`, and every tally counter stay empty or `0`.

`evenbetter-validate` promotes the report to `validated` and stamps `validated_at`. `evenbetter-repair` refuses any report whose `state` is still `analyzed`, and refuses a report whose `validated_at` is older than `scan_date` — that combination means analyze re-ran after the last validation and the findings are unvalidated again.

Overwriting a previously validated or repaired report is expected and correct. The report is the latest snapshot, not history, so a re-scan resets the workflow state along with the findings.

## Severity tally

Compute `summary.total` and the four per-severity counts after verification. Counts must match the `issues` array exactly — the severity filter chips in the report calculate filtered subsets from this number.

## Validation before write

Before writing the file, sanity-check the data object:

- `summary.total === issues.length`.
- Each `severity` is one of `critical`, `high`, `medium`, `low`.
- Each `hig_reference_url` is a non-empty string starting with `https://developer.apple.com/`.
- Each `id` is unique within `issues`.
- Every `code_snippet`, `minimal_fix`, and `recommended_fix` is non-empty.
- `workflow.state` is `analyzed`, `workflow.validated_at` and `workflow.repaired_at` are empty strings, and every tally counter is `0`.
- Every issue carries a `repair` object with `status: "pending"`, empty `path`, `owner`, `applied_at`, and `note`, and an empty `changed_files` array.

If any check fails, fix the data and re-validate before writing. Do not emit a partial report.

## After writing

Show the user one of the following, then stop:

- A `file://` link to `.evenbetter/<project-name>/evenbetter-analyze-report.html` so they can click to open it.
- The relative path inside the workspace if `file://` is not appropriate for the host environment.

Do not summarize the findings inline. The user opens the report to read them. If the audit produced zero findings, say so in one sentence and still write the report — the template renders an "All clear" state from an empty `issues` array.
