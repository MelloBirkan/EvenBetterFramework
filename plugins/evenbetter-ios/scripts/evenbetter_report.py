#!/usr/bin/env python3
"""Read, write and check EvenBetter analyze reports. Python 3 standard library only.

Usage:
  python3 evenbetter_report.py extract REPORT.html
  python3 evenbetter_report.py render DATA.json REPORT.html [--state STATE] [--no-archive]
  python3 evenbetter_report.py update DATA.json REPORT.html [--state STATE]
  python3 evenbetter_report.py check REPORT.html|DATA.json [--state STATE]

  STATE is analyzed, validated or repaired.

extract  Print the report data embedded in REPORT.html as JSON on stdout.
render   Check DATA.json, inject it into the evenbetter-analyze report template
         and write REPORT.html. An existing REPORT.html is first copied to
         history/evenbetter-analyze-report-YYYYMMDD-HHMMSS.html next to it,
         named after its scan_date, then replaced. --no-archive skips the copy.
         A fresh scan has no runtime verdicts, so every runtime block must be
         the empty untested block.
update   Check DATA.json and replace only the embedded data in an existing
         REPORT.html. Every other byte of the file stays as it was.
check    Validate the report contract and workflow state. Prints one line per
         problem and exits 1, or prints one OK line and exits 0. Without
         --state, the report's own workflow.state is checked.

A finding with no runtime block comes from a report written before runtime
checks existed. check accepts it with a warning on stderr, and render and update
add the untested block right after repair before they check the data.

Options:
  --corpus PATH    corpus index.json (default: ../corpus/index.json from this script)
  --template PATH  report template for render
                   (default: ../skills/evenbetter-analyze/references/report-template.html)

The embedded data is JSON with "</" written as "<\\/", "<!--" as "\\u003c!--", and
U+2028 and U+2029 as escapes, so it cannot end or confuse the script tag.

Exit status: 0 success, 1 contract problems, 2 usage or file errors.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_CORPUS = HERE.parent / "corpus" / "index.json"
DEFAULT_TEMPLATE = HERE.parent / "skills" / "evenbetter-analyze" / "references" / "report-template.html"

ANCHOR = "const reportData = "
PLACEHOLDER = "__EVENBETTER_REPORT_DATA__"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
STATES = ("analyzed", "validated", "repaired")
SEVERITIES = ("critical", "high", "medium", "low")
# Report severities allowed for the highest corpus severity among a finding's clauses.
SEVERITY_BAND = {
    "error": {"critical"},
    "warning": {"critical", "high", "medium"},
    "info": {"low"},
}
CORPUS_RANK = {"info": 0, "warning": 1, "error": 2}
LEVEL_RANK = {"A": 1, "AA": 2, "AAA": 3}
REPAIR_STATUSES = ("pending", "applied", "deferred", "skipped", "failed")
# Runtime verdicts. Only evenbetter-accessibility-tests writes a status other than untested.
RUNTIME_STATUSES = ("untested", "confirmed", "refuted", "inconclusive", "not_testable")
RUNTIME_CONFIGS = ("standard", "ax5", "dark", "increaseContrast", "rtl")
TEST_NAME_RE = re.compile(r"^[^\s/]+/test[^\s/]*$")
APPLE_PREFIX = "https://developer.apple.com/"
ID_RE = re.compile(r"^EB-\d{3,}$")
CLAUSE_RE = re.compile(r"^[A-Z0-9]+-(?:UI|UX|A11Y)-\d{3}$")
FILE_HEADER_RE = re.compile(r"^\s*//\s*File:\s*(.+?)\s*$")
ELISION_RE = re.compile(r"//\s*(?:\.\.\.|…)|/\*\s*(?:\.\.\.|…)|^\s*(?:\.\.\.|…)\s*$", re.M)

# Clause pairs whose Checks describe the same violation, or one a narrower case of the
# other. They belong in one finding. Keep in step with the twin table in
# skills/evenbetter-analyze/references/2-verify.md.
TWINS = [
    {"A11Y-A11Y-001", "COMP-A11Y-002"},
    {"LAY-UX-001", "COMP-UX-002"},
    {"COMP-UI-002", "NAV-UI-001"},
    {"A11Y-A11Y-003", "NAV-A11Y-001"},
    {"HAPT-UX-001", "LAY-UX-009"},
]

# Clause pairs whose Checks exclude each other: one construct gets at most one of them.
# Each pair carries the hint the error message gives. The table in
# skills/evenbetter-analyze/references/2-verify.md explains each split.
# Target size splits at 28x28 pt: under it is LAY-A11Y-001, from it up to 44x44 pt is LAY-UI-001.
# A Dynamic Type cap splits by what it applies to: primary content is TYPO-A11Y-004, a small
# repeated control such as a tab bar is TYPO-A11Y-005.
EXCLUSIVE = [
    ({"LAY-A11Y-001", "LAY-UI-001"}, "keep the one that matches the measured hit area"),
    ({"TYPO-A11Y-004", "TYPO-A11Y-005"},
     "a cap on primary content is TYPO-A11Y-004, a cap on a small repeated control is TYPO-A11Y-005"),
]

# WCAG 2.2 success criteria and levels (https://www.w3.org/TR/WCAG22/, checked 2026-11-07).
# 4.1.1 Parsing is obsolete and removed in WCAG 2.2.
WCAG22 = {
    "1.1.1": "A", "1.2.1": "A", "1.2.2": "A", "1.2.3": "A", "1.2.4": "AA", "1.2.5": "AA",
    "1.2.6": "AAA", "1.2.7": "AAA", "1.2.8": "AAA", "1.2.9": "AAA",
    "1.3.1": "A", "1.3.2": "A", "1.3.3": "A", "1.3.4": "AA", "1.3.5": "AA", "1.3.6": "AAA",
    "1.4.1": "A", "1.4.2": "A", "1.4.3": "AA", "1.4.4": "AA", "1.4.5": "AA", "1.4.6": "AAA",
    "1.4.7": "AAA", "1.4.8": "AAA", "1.4.9": "AAA", "1.4.10": "AA", "1.4.11": "AA",
    "1.4.12": "AA", "1.4.13": "AA",
    "2.1.1": "A", "2.1.2": "A", "2.1.3": "AAA", "2.1.4": "A",
    "2.2.1": "A", "2.2.2": "A", "2.2.3": "AAA", "2.2.4": "AAA", "2.2.5": "AAA", "2.2.6": "AAA",
    "2.3.1": "A", "2.3.2": "AAA", "2.3.3": "AAA",
    "2.4.1": "A", "2.4.2": "A", "2.4.3": "A", "2.4.4": "A", "2.4.5": "AA", "2.4.6": "AA",
    "2.4.7": "AA", "2.4.8": "AAA", "2.4.9": "AAA", "2.4.10": "AAA", "2.4.11": "AA",
    "2.4.12": "AAA", "2.4.13": "AAA",
    "2.5.1": "A", "2.5.2": "A", "2.5.3": "A", "2.5.4": "A", "2.5.5": "AAA", "2.5.6": "AAA",
    "2.5.7": "AA", "2.5.8": "AA",
    "3.1.1": "A", "3.1.2": "AA", "3.1.3": "AAA", "3.1.4": "AAA", "3.1.5": "AAA", "3.1.6": "AAA",
    "3.2.1": "A", "3.2.2": "A", "3.2.3": "AA", "3.2.4": "AA", "3.2.5": "AAA", "3.2.6": "A",
    "3.3.1": "A", "3.3.2": "A", "3.3.3": "AA", "3.3.4": "AA", "3.3.5": "AAA", "3.3.6": "AAA",
    "3.3.7": "A", "3.3.8": "AA", "3.3.9": "AAA",
    "4.1.2": "A", "4.1.3": "AA",
}

TOP_LEVEL_KEYS = ("project_name", "project_path", "framework", "wcag_level", "scan_date",
                  "workflow", "summary", "issues", "scan_context")
ISSUE_TEXT_KEYS = ("id", "clause_id", "title", "description", "severity", "hig_reference_url",
                   "file_path", "code_snippet", "minimal_fix", "recommended_fix",
                   "ai_fix_prompt", "language")
ISSUE_KEYS = ISSUE_TEXT_KEYS + ("related_clause_ids", "wcag_criteria", "wcag_level",
                                "line_number", "repair")
REPAIR_KEYS = ("status", "path", "owner", "applied_at", "changed_files", "note")
RUNTIME_KEYS = ("status", "checked_at", "configs", "tests", "evidence", "result_bundle")


def runtime_default() -> dict:
    return {"status": "untested", "checked_at": "", "configs": [], "tests": [],
            "evidence": "", "result_bundle": ""}


class UsageError(Exception):
    pass


# ---------------------------------------------------------------- embedding

def serialize(data: dict) -> str:
    """JSON for the script tag, with the sequences that could break it escaped."""
    text = json.dumps(data, indent=2, ensure_ascii=False)
    return (text.replace("</", "<\\/")
                .replace("<!--", "\\u003c!--")
                .replace("\u2028", "\\u2028")
                .replace("\u2029", "\\u2029"))


def locate(html: str) -> tuple[int, int, dict]:
    """Return (start, end, data) for the embedded literal; html[end] is the ';'."""
    count = html.count(ANCHOR)
    if count != 1:
        raise ValueError(f"expected one '{ANCHOR.strip()}' anchor, found {count}")
    start = html.index(ANCHOR) + len(ANCHOR)
    if html.startswith(PLACEHOLDER, start):
        raise ValueError("the template placeholder was never replaced; render the report first")
    try:
        data, end = json.JSONDecoder().raw_decode(html, start)
    except json.JSONDecodeError as e:
        raise ValueError(f"embedded report data is not valid JSON at offset {e.pos}: {e.msg}")
    if end >= len(html) or html[end] != ";":
        raise ValueError(f"the embedded data must be followed directly by ';' (offset {end})")
    if not isinstance(data, dict):
        raise ValueError("embedded report data is not a JSON object")
    return start, end, data


def raw_literal_problems(literal: str) -> list[str]:
    problems = []
    if "</" in literal:
        problems.append("embedded data contains an unescaped '</', which can end the script tag early (write '<\\/')")
    if "<!--" in literal:
        problems.append("embedded data contains an unescaped '<!--', which changes how the script tag is parsed (write '\\u003c!--')")
    if "\u2028" in literal or "\u2029" in literal:
        problems.append("embedded data contains a raw U+2028 or U+2029 (write \\u2028 or \\u2029)")
    return problems


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        raise UsageError(f"cannot read {path}: {e.strerror}")


def load_input(path: Path) -> tuple[dict, list[str]]:
    """Load DATA.json or REPORT.html. Returns (data, problems with the embedding)."""
    text = read_text(path)
    if text.lstrip().startswith("{"):
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise UsageError(f"{path} is not valid JSON (line {e.lineno}, column {e.colno}): {e.msg}")
        if not isinstance(data, dict):
            raise UsageError(f"{path} does not hold a JSON object")
        return data, []
    try:
        start, end, data = locate(text)
    except ValueError as e:
        raise UsageError(f"{path}: {e}")
    return data, raw_literal_problems(text[start:end])


def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".evenbetter-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# ---------------------------------------------------------------- checking

def load_corpus(path: Path) -> dict:
    try:
        entries = json.loads(path.read_text(encoding="utf-8"))
    except OSError as e:
        raise UsageError(f"cannot read corpus index {path}: {e.strerror}")
    except json.JSONDecodeError as e:
        raise UsageError(f"corpus index {path} is not valid JSON: {e.msg}")
    return {e["clause_id"]: e for e in entries if isinstance(e, dict) and "clause_id" in e}


def parse_time(value) -> datetime | None:
    # Zero-padded only: the skills compare stamps as strings, which works only in this exact form.
    if not isinstance(value, str) or not TIME_RE.match(value):
        return None
    try:
        return datetime.strptime(value, TIME_FORMAT)
    except ValueError:
        return None


def is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def fix_parts(text: str) -> list[str]:
    return [m.group(1) for line in text.splitlines() if (m := FILE_HEADER_RE.match(line))]


def check_issue(issue, index: int, corpus: dict, report_level: str, problems: list[str]) -> None:
    where = f"issues[{index}]"
    if not isinstance(issue, dict):
        problems.append(f"{where}: not an object")
        return
    if isinstance(issue.get("id"), str) and issue["id"]:
        where = issue["id"]
    p = problems.append

    missing = [k for k in ISSUE_KEYS if k not in issue]
    if missing:
        p(f"{where}: missing {', '.join(missing)}")
    for key in ISSUE_TEXT_KEYS:
        if key in issue and (not isinstance(issue[key], str) or not issue[key].strip()):
            p(f"{where} {key}: must be a non-empty string")

    fid = issue.get("id")
    if isinstance(fid, str) and fid and not ID_RE.match(fid):
        p(f"{where} id: use the EB-001 form")

    severity = issue.get("severity")
    if "severity" in issue and severity not in SEVERITIES:
        p(f"{where} severity: {severity!r} is not one of {', '.join(SEVERITIES)}")

    if "line_number" in issue and (not is_int(issue["line_number"]) or issue["line_number"] < 1):
        p(f"{where} line_number: must be an integer of 1 or more")

    # Clauses, URL and severity band.
    clause = issue.get("clause_id")
    related = issue.get("related_clause_ids")
    clauses = []
    if isinstance(clause, str) and clause:
        if clause not in corpus:
            p(f"{where} clause_id: {clause} is not in corpus/index.json")
        else:
            clauses.append(clause)
    if "related_clause_ids" in issue:
        if not isinstance(related, list) or not all(isinstance(r, str) for r in related):
            p(f"{where} related_clause_ids: must be an array of clause ID strings")
        else:
            if len(set(related)) != len(related):
                p(f"{where} related_clause_ids: lists a clause twice")
            for r in related:
                if r == clause:
                    p(f"{where} related_clause_ids: repeats the primary clause {r}")
                elif r not in corpus:
                    p(f"{where} related_clause_ids: {r} is not in corpus/index.json")
                else:
                    clauses.append(r)
    for pair, hint in EXCLUSIVE:
        if pair <= set(clauses):
            p(f"{where}: {' and '.join(sorted(pair))} exclude each other; {hint}")
    url = issue.get("hig_reference_url")
    if isinstance(url, str) and url:
        if not url.startswith(APPLE_PREFIX):
            p(f"{where} hig_reference_url: must start with {APPLE_PREFIX}")
        if isinstance(clause, str) and clause in corpus and url != corpus[clause].get("source_url"):
            p(f"{where} hig_reference_url: must equal the index source_url of {clause} "
              f"({corpus[clause].get('source_url')}), found {url}")
    if clauses and severity in SEVERITIES:
        top = max((corpus[c].get("severity", "info") for c in clauses),
                  key=lambda s: CORPUS_RANK.get(s, 0))
        allowed = SEVERITY_BAND.get(top, set(SEVERITIES))
        if severity not in allowed:
            p(f"{where} severity: {severity} does not fit corpus severity {top} "
              f"(allowed: {', '.join(s for s in SEVERITIES if s in allowed)})")

    # WCAG cross-reference.
    crit = issue.get("wcag_criteria")
    level = issue.get("wcag_level")
    if "wcag_criteria" in issue and not isinstance(crit, str):
        p(f"{where} wcag_criteria: must be a string")
    elif "wcag_level" in issue and level not in ("", "A", "AA", "AAA"):
        p(f"{where} wcag_level: must be A, AA, AAA or empty")
    elif isinstance(crit, str):
        crit = crit.strip()
        if bool(crit) != bool(level):
            p(f"{where} wcag_level: set wcag_criteria and wcag_level together, or leave both empty")
        elif crit:
            if crit == "4.1.1":
                p(f"{where} wcag_criteria: 4.1.1 Parsing is obsolete and removed in WCAG 2.2")
            elif crit not in WCAG22:
                p(f"{where} wcag_criteria: {crit!r} is not one WCAG 2.2 success criterion number")
            else:
                if level != WCAG22[crit]:
                    p(f"{where} wcag_level: {crit} is level {WCAG22[crit]}, not {level}")
                if report_level in LEVEL_RANK and LEVEL_RANK[WCAG22[crit]] > LEVEL_RANK[report_level]:
                    hint = " (use 2.5.8 Target Size (Minimum) for AA)" if crit == "2.5.5" else ""
                    p(f"{where} wcag_criteria: {crit} is level {WCAG22[crit]}, above the report's "
                      f"target {report_level}{hint}")

    # Code and fixes.
    for key in ("code_snippet", "minimal_fix", "recommended_fix"):
        text = issue.get(key)
        if not isinstance(text, str):
            continue
        if ELISION_RE.search(text):
            p(f"{where} {key}: contains an elision such as '// ...'; write the complete code")
        if key == "code_snippet":
            continue
        parts = fix_parts(text)
        if parts:
            first = next((line for line in text.splitlines() if line.strip()), "")
            if not FILE_HEADER_RE.match(first):
                p(f"{where} {key}: a multi-part fix must start with a '// File: path' line")
            for part in parts:
                if part.startswith("/"):
                    p(f"{where} {key}: '// File: {part}' must be a project-relative path")
    prompt = issue.get("ai_fix_prompt")
    if isinstance(prompt, str) and prompt:
        named = set()
        if isinstance(issue.get("file_path"), str) and issue["file_path"]:
            named.add(issue["file_path"])
        for key in ("minimal_fix", "recommended_fix"):
            if isinstance(issue.get(key), str):
                named.update(fix_parts(issue[key]))
        for path in sorted(named):
            if path not in prompt:
                p(f"{where} ai_fix_prompt: does not name {path}")

    # Repair ledger.
    repair = issue.get("repair")
    if "repair" in issue:
        if not isinstance(repair, dict):
            p(f"{where} repair: must be an object")
        else:
            gone = [k for k in REPAIR_KEYS if k not in repair]
            if gone:
                p(f"{where} repair: missing {', '.join(gone)}")
            status = repair.get("status")
            if status not in REPAIR_STATUSES:
                p(f"{where} repair.status: {status!r} is not one of {', '.join(REPAIR_STATUSES)}")
            if repair.get("path", "") not in ("", "minimal", "recommended"):
                p(f"{where} repair.path: must be minimal, recommended or empty")
            if repair.get("owner", "") not in ("", "agent", "human"):
                p(f"{where} repair.owner: must be agent, human or empty")
            for key in ("applied_at", "note"):
                if key in repair and not isinstance(repair[key], str):
                    p(f"{where} repair.{key}: must be a string")
            applied_at = repair.get("applied_at", "")
            if isinstance(applied_at, str) and applied_at and not parse_time(applied_at):
                p(f"{where} repair.applied_at: use YYYY-MM-DD HH:MM:SS")
            files = repair.get("changed_files")
            if "changed_files" in repair and (not isinstance(files, list) or
                                              not all(isinstance(f, str) for f in files)):
                p(f"{where} repair.changed_files: must be an array of strings")
            if status == "applied":
                if not applied_at:
                    p(f"{where} repair: an applied finding needs applied_at")
                if not files:
                    p(f"{where} repair: an applied finding needs at least one changed_files entry")
            if status in ("deferred", "failed") and not repair.get("note"):
                p(f"{where} repair: a {status} finding needs a note")

    # Runtime verdict. A missing block is a pre-runtime report; cmd_check warns about it.
    if "runtime" in issue:
        check_runtime(issue["runtime"], where, problems)


def check_runtime(runtime, where: str, problems: list[str]) -> None:
    p = problems.append
    if not isinstance(runtime, dict):
        p(f"{where} runtime: must be an object")
        return
    gone = [k for k in RUNTIME_KEYS if k not in runtime]
    if gone:
        p(f"{where} runtime: missing {', '.join(gone)}")
    extra = [k for k in runtime if k not in RUNTIME_KEYS]
    if extra:
        p(f"{where} runtime: unknown key {', '.join(extra)} (keys are {', '.join(RUNTIME_KEYS)})")
    status = runtime.get("status")
    if status not in RUNTIME_STATUSES:
        p(f"{where} runtime.status: {status!r} is not one of {', '.join(RUNTIME_STATUSES)}")
        status = None
    for key in ("checked_at", "evidence", "result_bundle"):
        if key in runtime and not isinstance(runtime[key], str):
            p(f"{where} runtime.{key}: must be a string")
    lists = {}
    for key in ("configs", "tests"):
        value = runtime.get(key)
        if key not in runtime:
            continue
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            p(f"{where} runtime.{key}: must be an array of strings")
            continue
        lists[key] = value
        if len(set(value)) != len(value):
            p(f"{where} runtime.{key}: lists an entry twice")
    for config in lists.get("configs", []):
        if config not in RUNTIME_CONFIGS:
            p(f"{where} runtime.configs: {config!r} is not one of {', '.join(RUNTIME_CONFIGS)}")
    for test in lists.get("tests", []):
        if not TEST_NAME_RE.match(test):
            p(f"{where} runtime.tests: {test!r} is not a Class/test name such as "
              f"EBAccessibilityAuditTests/test_PlantList_AX5")
    checked_at = runtime.get("checked_at")
    bundle = runtime.get("result_bundle")
    evidence = runtime.get("evidence")
    if isinstance(bundle, str) and bundle:
        parts = bundle.replace("\\", "/").rstrip("/").split("/")
        if bundle.startswith(("/", "~")) or re.match(r"^[A-Za-z]:", bundle):
            p(f"{where} runtime.result_bundle: must be a project-relative path")
        elif ".." in parts:
            p(f"{where} runtime.result_bundle: must not contain '..'")
        elif not parts[-1].endswith(".xcresult"):
            p(f"{where} runtime.result_bundle: must name an .xcresult bundle")
    if status is None:
        return
    if status == "untested":
        if checked_at:
            p(f"{where} runtime.checked_at: an untested finding keeps it empty")
        if lists.get("configs") or lists.get("tests") or bundle:
            p(f"{where} runtime: an untested finding keeps configs, tests and result_bundle empty")
        return
    if isinstance(checked_at, str) and not parse_time(checked_at):
        p(f"{where} runtime.checked_at: a {status} verdict needs the run start as YYYY-MM-DD HH:MM:SS")
    if isinstance(evidence, str) and not evidence.strip():
        p(f"{where} runtime.evidence: a {status} verdict needs one sentence of evidence")
    if status == "not_testable":
        if lists.get("configs") or lists.get("tests") or bundle:
            p(f"{where} runtime: a not_testable finding keeps configs, tests and result_bundle empty")
        return
    if "configs" in lists and not lists["configs"]:
        p(f"{where} runtime.configs: a {status} verdict names the configurations that ran")
    if "tests" in lists and not lists["tests"]:
        p(f"{where} runtime.tests: a {status} verdict names the tests that ran")


def missing_runtime(data: dict) -> list[str]:
    """IDs (or positions) of findings with no runtime block."""
    issues = data.get("issues")
    if not isinstance(issues, list):
        return []
    return [str(x.get("id") or f"issues[{i}]") for i, x in enumerate(issues)
            if isinstance(x, dict) and "runtime" not in x]


def backfill_runtime(data: dict) -> list[str]:
    """Add the untested runtime block right after repair where it is missing. Returns the IDs."""
    filled = missing_runtime(data)
    if not filled:
        return filled
    issues = data["issues"]
    for i, issue in enumerate(issues):
        if not isinstance(issue, dict) or "runtime" in issue:
            continue
        items = list(issue.items())
        at = next((n + 1 for n, (key, _) in enumerate(items) if key == "repair"), len(items))
        items.insert(at, ("runtime", runtime_default()))
        issues[i] = dict(items)
    return filled


def fresh_scan_problems(data: dict) -> list[str]:
    """render writes a new scan, so every finding carries the empty untested block."""
    problems = []
    issues = data.get("issues")
    for i, issue in enumerate(issues if isinstance(issues, list) else []):
        runtime = issue.get("runtime") if isinstance(issue, dict) else None
        if isinstance(runtime, dict) and runtime != runtime_default():
            where = issue.get("id") or f"issues[{i}]"
            problems.append(f"{where} runtime: a fresh scan writes the empty untested block; verdicts "
                            f"come from evenbetter-accessibility-tests after the scan")
    return problems


def check_report(data: dict, corpus: dict, want_state: str | None) -> list[str]:
    problems: list[str] = []
    p = problems.append

    missing = [k for k in TOP_LEVEL_KEYS if k not in data]
    if missing:
        p(f"report: missing {', '.join(missing)}")
    for key in ("project_name", "framework"):
        if key in data and (not isinstance(data[key], str) or not data[key].strip()):
            p(f"report {key}: must be a non-empty string")
    if "project_path" in data and (not isinstance(data["project_path"], str) or
                                   not os.path.isabs(data["project_path"])):
        p("report project_path: must be an absolute path")
    report_level = data.get("wcag_level")
    if "wcag_level" in data and report_level not in LEVEL_RANK:
        p("report wcag_level: must be A, AA or AAA")
    scan_date = parse_time(data.get("scan_date"))
    if "scan_date" in data and scan_date is None:
        p("report scan_date: use YYYY-MM-DD HH:MM:SS")

    issues = data.get("issues")
    if "issues" in data and not isinstance(issues, list):
        p("report issues: must be an array")
        issues = []
    issues = issues if isinstance(issues, list) else []
    seen_ids = set()
    for i, issue in enumerate(issues):
        check_issue(issue, i, corpus, report_level, problems)
        fid = issue.get("id") if isinstance(issue, dict) else None
        if isinstance(fid, str) and fid:
            if fid in seen_ids:
                p(f"{fid}: id is used by more than one finding")
            seen_ids.add(fid)

    # One finding per construct: the same clause or a twin pair twice on one site.
    sites: dict[tuple, list[tuple[str, set]]] = {}
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        key = (issue.get("file_path"), issue.get("line_number"))
        cs = set()
        if isinstance(issue.get("clause_id"), str):
            cs.add(issue["clause_id"])
        if isinstance(issue.get("related_clause_ids"), list):
            cs.update(r for r in issue["related_clause_ids"] if isinstance(r, str))
        for other_id, other in sites.get(key, []):
            shared = cs & other
            twins = [sorted(t) for t in TWINS if t & cs and t & other]
            clash = [(sorted(t), hint) for t, hint in EXCLUSIVE
                     if (t & cs) and (t & other) and (t & cs) != (t & other)]
            if shared:
                p(f"{issue.get('id')}: {', '.join(sorted(shared))} also appears in {other_id} at "
                  f"{key[0]}:{key[1]}; one construct gets one finding")
            elif twins:
                pair = " and ".join("/".join(t) for t in twins)
                p(f"{issue.get('id')} and {other_id}: twin clauses {pair} on the same construct "
                  f"({key[0]}:{key[1]}) belong in one finding")
            for t, hint in clash:
                p(f"{issue.get('id')} and {other_id}: {'/'.join(t)} exclude each other on the same "
                  f"construct ({key[0]}:{key[1]}); {hint}")
        sites.setdefault(key, []).append((issue.get("id"), cs))

    # Summary tallies.
    summary = data.get("summary")
    if "summary" in data:
        if not isinstance(summary, dict):
            p("summary: must be an object")
        else:
            counts = {s: sum(1 for x in issues if isinstance(x, dict) and x.get("severity") == s)
                      for s in SEVERITIES}
            expected = {"total": len(issues), **counts}
            for key, value in expected.items():
                if not is_int(summary.get(key)):
                    p(f"summary.{key}: must be an integer")
                elif summary[key] != value:
                    p(f"summary.{key}: is {summary[key]} but the issues array gives {value}")

    # Scan context.
    ctx = data.get("scan_context")
    if "scan_context" in data:
        if not isinstance(ctx, dict):
            p("scan_context: must be an object")
        else:
            for key in ("frameworks", "design_systems", "component_patterns", "custom_utilities"):
                if not isinstance(ctx.get(key), list) or not all(isinstance(v, str) for v in ctx[key]):
                    p(f"scan_context.{key}: must be an array of strings")
            fv = ctx.get("framework_versions")
            if not isinstance(fv, dict) or not all(isinstance(v, str) for v in fv.values()):
                p("scan_context.framework_versions: must map names to version strings")
            if not is_number(ctx.get("scan_duration")) or ctx["scan_duration"] < 0:
                p("scan_context.scan_duration: must be a number of seconds")
            if not is_int(ctx.get("files_scanned")) or ctx["files_scanned"] < 0:
                p("scan_context.files_scanned: must be a whole number")
            conf = ctx.get("confidence")
            if not is_number(conf) or not 0 <= conf <= 1:
                p("scan_context.confidence: must be a number from 0 to 1")
            if "notes" in ctx and (not isinstance(ctx["notes"], list) or
                                   not all(isinstance(v, str) for v in ctx["notes"])):
                p("scan_context.notes: must be an array of strings")

    check_workflow(data, issues, scan_date, want_state, problems)
    return problems


def check_workflow(data, issues, scan_date, want_state, problems) -> None:
    p = problems.append
    wf = data.get("workflow")
    if "workflow" not in data:
        return
    if not isinstance(wf, dict):
        p("workflow: must be an object")
        return
    state = wf.get("state")
    if state not in STATES:
        p(f"workflow.state: {state!r} is not one of {', '.join(STATES)}")
        return
    if want_state and state != want_state:
        p(f"workflow.state: is {state}, expected {want_state}")
    tallies = {"validation": ("kept", "adjusted", "removed"),
               "repair": ("applied", "deferred", "skipped", "failed")}
    for block, keys in tallies.items():
        value = wf.get(block)
        if not isinstance(value, dict):
            p(f"workflow.{block}: must be an object with {', '.join(keys)}")
            continue
        for k in keys:
            if not is_int(value.get(k)) or value[k] < 0:
                p(f"workflow.{block}.{k}: must be a whole number")
    stamps = {}
    for key in ("validated_at", "repaired_at"):
        value = wf.get(key)
        if not isinstance(value, str):
            p(f"workflow.{key}: must be a string")
            stamps[key] = None
        elif value and not parse_time(value):
            p(f"workflow.{key}: use YYYY-MM-DD HH:MM:SS or leave it empty")
            stamps[key] = None
        else:
            stamps[key] = parse_time(value) if value else None
    validation = wf.get("validation") if isinstance(wf.get("validation"), dict) else {}
    repair = wf.get("repair") if isinstance(wf.get("repair"), dict) else {}
    statuses = [x.get("repair", {}).get("status") for x in issues
                if isinstance(x, dict) and isinstance(x.get("repair"), dict)]
    status_count = {s: statuses.count(s) for s in REPAIR_STATUSES}

    if state == "analyzed":
        if wf.get("validated_at") or wf.get("repaired_at"):
            p("workflow: an analyzed report has empty validated_at and repaired_at")
        if any(validation.get(k) for k in tallies["validation"]) or \
                any(repair.get(k) for k in tallies["repair"]):
            p("workflow: an analyzed report has every validation and repair tally at 0")
        for x in issues:
            r = x.get("repair") if isinstance(x, dict) else None
            if isinstance(r, dict) and (r.get("status") != "pending" or r.get("path") or r.get("owner")
                                        or r.get("applied_at") or r.get("changed_files") or r.get("note")):
                p(f"{x.get('id')} repair: an analyzed report has every ledger pending and empty")
        return

    validated_at = stamps.get("validated_at")
    if not wf.get("validated_at"):
        p(f"workflow.validated_at: a {state} report needs a validation stamp")
    elif validated_at and scan_date and validated_at < scan_date:
        p("workflow.validated_at: is earlier than scan_date, so the findings are unvalidated")
    kept, adjusted = validation.get("kept"), validation.get("adjusted")
    if is_int(kept) and is_int(adjusted) and kept + adjusted != len(issues):
        p(f"workflow.validation: kept + adjusted is {kept + adjusted} but there are {len(issues)} findings")

    if state == "validated":
        applied = [x.get("id") for x in issues if isinstance(x, dict)
                   and isinstance(x.get("repair"), dict) and x["repair"].get("status") == "applied"]
        if applied:
            p(f"workflow: a validated report has no applied repairs left (validation removes them or "
              f"marks them failed): {', '.join(map(str, applied))}")
        return

    # repaired
    repaired_at = stamps.get("repaired_at")
    if not wf.get("repaired_at"):
        p("workflow.repaired_at: a repaired report needs a repair stamp")
    elif repaired_at and validated_at and repaired_at < validated_at:
        p("workflow.repaired_at: is earlier than validated_at")
    for k in tallies["repair"]:
        if is_int(repair.get(k)) and repair[k] != status_count[k]:
            p(f"workflow.repair.{k}: is {repair[k]} but {status_count[k]} findings have status {k}")
    if status_count["applied"] == 0:
        p("workflow: a repaired report has at least one applied finding")


# ---------------------------------------------------------------- commands

def archive_existing(report: Path) -> Path | None:
    if not report.exists():
        return None
    stamp = None
    try:
        _, _, old = locate(report.read_text(encoding="utf-8"))
        when = parse_time(old.get("scan_date"))
        if when:
            stamp = when.strftime("%Y%m%d-%H%M%S")
    except (OSError, ValueError, UnicodeDecodeError):
        pass
    if stamp is None:
        stamp = datetime.fromtimestamp(report.stat().st_mtime).strftime("%Y%m%d-%H%M%S")
    history = report.parent / "history"
    history.mkdir(parents=True, exist_ok=True)
    target = history / f"evenbetter-analyze-report-{stamp}.html"
    n = 2
    while target.exists():
        target = history / f"evenbetter-analyze-report-{stamp}-{n}.html"
        n += 1
    # Copy, not move: the current report stays in place until the new one replaces it atomically.
    shutil.copy2(report, target)
    return target


def report_problems(problems: list[str]) -> int:
    for line in problems:
        print(line)
    print(f"{len(problems)} problem{'s' if len(problems) != 1 else ''} found", file=sys.stderr)
    return 1


def cmd_extract(args) -> int:
    data, problems = load_input(Path(args.pos[0]))
    for line in problems:
        print(f"warning: {line}", file=sys.stderr)
    json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def warn_missing_runtime(ids: list[str]) -> None:
    if not ids:
        return
    shown = ", ".join(ids[:5]) + (f" and {len(ids) - 5} more" if len(ids) > 5 else "")
    print(f"warning: {len(ids)} finding{'s' if len(ids) != 1 else ''} without a runtime block "
          f"({shown}), from a report written before runtime checks; render and update add the "
          f"untested block", file=sys.stderr)


def note_backfill(ids: list[str]) -> None:
    if ids:
        print(f"added the untested runtime block to {len(ids)} finding{'s' if len(ids) != 1 else ''}")


def cmd_check(args) -> int:
    data, problems = load_input(Path(args.pos[0]))
    problems += check_report(data, load_corpus(args.corpus), args.state)
    warn_missing_runtime(missing_runtime(data))
    if problems:
        return report_problems(problems)
    issues = data.get("issues", [])
    print(f"OK: {len(issues)} finding{'s' if len(issues) != 1 else ''}, "
          f"state {data['workflow']['state']}")
    return 0


def load_data_json(path: Path) -> dict:
    text = read_text(path)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise UsageError(f"{path} is not valid JSON (line {e.lineno}, column {e.colno}): {e.msg}")
    if not isinstance(data, dict):
        raise UsageError(f"{path} does not hold a JSON object")
    return data


def cmd_render(args) -> int:
    data = load_data_json(Path(args.pos[0]))
    filled = backfill_runtime(data)
    problems = check_report(data, load_corpus(args.corpus), args.state) + fresh_scan_problems(data)
    if problems:
        print("not written: the data has problems", file=sys.stderr)
        return report_problems(problems)
    template = read_text(args.template)
    if template.count(PLACEHOLDER) != 1 or template.count(ANCHOR) != 1:
        raise UsageError(f"{args.template} must hold one '{ANCHOR}{PLACEHOLDER};' line")
    html = template.replace(PLACEHOLDER, serialize(data), 1)
    _, _, roundtrip = locate(html)
    if roundtrip != data:
        raise UsageError("the rendered data does not read back unchanged; nothing was written")
    report = Path(args.pos[1])
    moved = None if args.no_archive else archive_existing(report)
    write_atomic(report, html)
    if moved:
        print(f"archived {moved}")
    note_backfill(filled)
    print(f"wrote {report.resolve()}")
    return 0


def cmd_update(args) -> int:
    data = load_data_json(Path(args.pos[0]))
    filled = backfill_runtime(data)
    problems = check_report(data, load_corpus(args.corpus), args.state)
    if problems:
        print("not written: the data has problems", file=sys.stderr)
        return report_problems(problems)
    report = Path(args.pos[1])
    html = read_text(report)
    try:
        start, end, _ = locate(html)
    except ValueError as e:
        raise UsageError(f"{report}: {e}")
    new_html = html[:start] + serialize(data) + html[end:]
    _, _, roundtrip = locate(new_html)
    if roundtrip != data:
        raise UsageError("the spliced data does not read back unchanged; nothing was written")
    write_atomic(report, new_html)
    note_backfill(filled)
    print(f"updated {report.resolve()}")
    return 0


class Args:
    def __init__(self, argv: list[str]):
        if not argv:
            raise UsageError(None)
        self.command = argv[0]
        self.state = None
        self.no_archive = False
        self.corpus = DEFAULT_CORPUS
        self.template = DEFAULT_TEMPLATE
        self.pos: list[str] = []
        rest = iter(argv[1:])
        for arg in rest:
            if arg in ("--state", "--corpus", "--template"):
                value = next(rest, None)
                if value is None:
                    raise UsageError(f"{arg} needs a value")
                if arg == "--state":
                    if value not in STATES:
                        raise UsageError(f"--state must be one of {', '.join(STATES)}")
                    self.state = value
                elif arg == "--corpus":
                    self.corpus = Path(value)
                else:
                    self.template = Path(value)
            elif arg == "--no-archive":
                self.no_archive = True
            elif arg.startswith("--"):
                raise UsageError(f"unknown option {arg}")
            else:
                self.pos.append(arg)
        need = {"extract": 1, "check": 1, "render": 2, "update": 2}
        if self.command not in need:
            raise UsageError(f"unknown command {self.command!r}")
        if len(self.pos) != need[self.command]:
            raise UsageError(f"{self.command} takes {need[self.command]} path argument"
                             f"{'s' if need[self.command] > 1 else ''}")


def main(argv: list[str]) -> int:
    if argv and argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    try:
        args = Args(argv)
        return {"extract": cmd_extract, "check": cmd_check,
                "render": cmd_render, "update": cmd_update}[args.command](args)
    except UsageError as e:
        if e.args and e.args[0]:
            print(f"error: {e.args[0]}", file=sys.stderr)
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
