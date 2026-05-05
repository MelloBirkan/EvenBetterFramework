#!/usr/bin/env python3
"""Generate comprehensive EvenBetter iOS HIG HTML reports with a bold modern aesthetic.

The report is a derived artifact. It reads the corrected analyzer JSON, or a
legacy validation JSON when older skill output is supplied, renders current
issues, and keeps rejected, fixed, duplicate, and dropped findings out of the
browser view.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any


HIDDEN_STATES = {"fixed", "rejected", "duplicate_of", "duplicate"}
LEGACY_VISIBLE_DECISIONS = {"kept", "severity_adjusted", "downgraded"}
SEVERITY_TO_TEMPLATE = {
    "error": "critical",
    "warning": "high",
    "info": "medium",
    "critical": "critical",
    "high": "high",
    "medium": "medium",
    "low": "low",
}


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _safe_script_json(data: dict[str, Any]) -> str:
    """Serialize JSON for direct placement inside a JavaScript script tag."""
    return json.dumps(data, ensure_ascii=True, sort_keys=True).replace("</", "<\\/")


def _project_name(project_path: str) -> str:
    if not project_path:
        return "Unknown Project"
    return Path(project_path).name or project_path


def _language_for_file(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()
    return {
        ".swift": "swift",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".html": "html",
        ".css": "css",
        ".py": "python",
        ".json": "json",
    }.get(suffix, "plaintext")


def _looks_like_validation_report(report: dict[str, Any]) -> bool:
    return "files" not in report and any(
        isinstance(report.get(bucket), list)
        for bucket in ("kept", "severity_adjusted", "downgraded", "dropped")
    )


def _visible_issue(violation: dict[str, Any]) -> bool:
    state = violation.get("state") or {}
    status = state.get("status", "open") if isinstance(state, dict) else "open"
    normalized = str(status or "open").lower()
    return normalized not in HIDDEN_STATES


def _validation_decision(validation: dict[str, Any] | None) -> str:
    if not isinstance(validation, dict):
        return ""
    return str(validation.get("decision") or validation.get("_bucket") or "").lower()


def _render_from_validation(validation: dict[str, Any] | None) -> bool:
    return _validation_decision(validation) in LEGACY_VISIBLE_DECISIONS


def _skip_from_validation(validation: dict[str, Any] | None) -> bool:
    return _validation_decision(validation) in {"dropped", "rejected"}


def _template_severity(severity: Any) -> str:
    return SEVERITY_TO_TEMPLATE.get(str(severity or "").lower(), "medium")


def _source_severity(
    violation: dict[str, Any],
    validation: dict[str, Any] | None,
) -> str:
    if isinstance(validation, dict):
        assessment = validation.get("severity_assessment")
        if isinstance(assessment, dict) and assessment.get("correct"):
            return str(assessment.get("correct"))
        if validation.get("corrected_severity"):
            return str(validation.get("corrected_severity"))
        if validation.get("downgraded_severity"):
            return str(validation.get("downgraded_severity"))
    return str(violation.get("severity", "info"))


def _add_evidence_link(
    links: list[dict[str, str]],
    seen: set[str],
    *,
    label: Any,
    url: Any,
    reason: str,
) -> None:
    if not isinstance(url, str):
        return
    normalized_url = url.strip()
    if not normalized_url.startswith(("http://", "https://")) or normalized_url in seen:
        return
    seen.add(normalized_url)
    links.append(
        {
            "label": str(label or "Apple HIG"),
            "url": normalized_url,
            "reason": reason,
        }
    )


def _evidence_links(
    violation: dict[str, Any],
    validation: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    seen: set[str] = set()
    guideline = violation.get("guideline_reference") or {}
    if isinstance(guideline, dict):
        _add_evidence_link(
            links,
            seen,
            label=guideline.get("label") or "Apple HIG",
            url=guideline.get("url"),
            reason="Primary guideline reference for this issue.",
        )

    if isinstance(validation, dict):
        corpus = validation.get("corpus_clause") or {}
        if isinstance(corpus, dict):
            _add_evidence_link(
                links,
                seen,
                label=corpus.get("heading") or corpus.get("clause_id") or "Corpus source",
                url=corpus.get("source_url"),
                reason="Corpus source used while validating this issue.",
            )
        for link in validation.get("supporting_links") or []:
            if not isinstance(link, dict):
                continue
            _add_evidence_link(
                links,
                seen,
                label=link.get("label") or "Supporting evidence",
                url=link.get("url"),
                reason=str(link.get("reason") or "Additional validation evidence."),
            )
    return links


def _validation_items(validation_report: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(validation_report, dict):
        return []

    items: list[dict[str, Any]] = []
    fallback_decisions = {
        "kept": "kept",
        "severity_adjusted": "severity_adjusted",
        "downgraded": "severity_adjusted",
        "dropped": "dropped",
    }
    for bucket in ("kept", "severity_adjusted", "downgraded", "dropped"):
        for item in validation_report.get(bucket, []) or []:
            if not isinstance(item, dict):
                continue
            normalized = dict(item)
            normalized["_bucket"] = fallback_decisions[bucket]
            normalized.setdefault("decision", fallback_decisions[bucket])
            items.append(normalized)
    return items


def _validation_index(validation_report: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for item in _validation_items(validation_report):
        original = item.get("original_violation") or {}
        if not isinstance(original, dict):
            continue
        violation_id = original.get("id")
        if violation_id is None:
            continue
        normalized_id = str(violation_id)
        if normalized_id:
            by_id[normalized_id] = item
    return by_id


def _issue_id(violation: dict[str, Any], file_path: str, index: int) -> str:
    violation_id = violation.get("id")
    if violation_id is not None and str(violation_id):
        return str(violation_id)
    rule_id = str(violation.get("rule_id") or "issue")
    line_number = str(violation.get("line_number") or "unknown")
    path_slug = file_path.replace("/", "-") or "unknown-file"
    return f"{rule_id}-{path_slug}-{line_number}-{index + 1}"


def _text_from_any(value: Any) -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    return str(value)


def _first_text(*values: Any) -> str:
    for value in values:
        text = _text_from_any(value)
        if text.strip():
            return text
    return ""


def _int_from_any(value: Any) -> int | None:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _source_context_from_violation(violation: dict[str, Any]) -> dict[str, Any]:
    for key in ("source_context", "sourceContext", "source", "location"):
        value = violation.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _code_from_source_file(
    project_path: str,
    file_path: str,
    violation: dict[str, Any],
    source_context: dict[str, Any],
) -> str:
    if not project_path or not file_path:
        return ""

    project_root = Path(project_path).expanduser()
    candidate = Path(file_path).expanduser()
    if not candidate.is_absolute():
        candidate = project_root / candidate

    try:
        resolved_root = project_root.resolve()
        resolved_candidate = candidate.resolve()
        if resolved_root not in resolved_candidate.parents and resolved_candidate != resolved_root:
            return ""
        lines = resolved_candidate.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return ""

    line_start = _int_from_any(
        source_context.get("line_start")
        or source_context.get("start_line")
        or violation.get("line_start")
        or violation.get("start_line")
        or violation.get("line_number")
    )
    if line_start is None:
        return ""

    line_end = _int_from_any(
        source_context.get("line_end")
        or source_context.get("end_line")
        or violation.get("line_end")
        or violation.get("end_line")
    ) or line_start

    start_index = max(line_start - 1, 0)
    end_index = min(max(line_end, line_start), len(lines))
    if start_index >= len(lines) or start_index >= end_index:
        return ""
    return "\n".join(lines[start_index:end_index])


def _code_snippet(
    violation: dict[str, Any],
    validation: dict[str, Any] | None,
    project_path: str,
    file_path: str,
) -> str:
    violation_context = _source_context_from_violation(violation)
    validation_context = validation.get("source_context") if isinstance(validation, dict) else {}
    if not isinstance(validation_context, dict):
        validation_context = {}

    explicit = _first_text(
        violation.get("code_snippet"),
        violation.get("current_code"),
        violation.get("currentCode"),
        violation.get("current_snippet"),
        violation.get("source_code"),
        violation.get("sourceCode"),
        violation.get("source_snippet"),
        violation.get("offending_code"),
        violation.get("offendingCode"),
        violation.get("problematic_code"),
        violation.get("problematicCode"),
        violation.get("snippet"),
        violation_context.get("excerpt"),
        violation_context.get("code"),
        violation_context.get("snippet"),
        violation_context.get("text"),
        validation_context.get("excerpt"),
        validation_context.get("code"),
        validation_context.get("snippet"),
        validation_context.get("text"),
    )
    if explicit:
        return explicit

    return _code_from_source_file(project_path, file_path, violation, violation_context or validation_context)


def _issue_from_violation(
    violation: dict[str, Any],
    file_entry: dict[str, Any] | None,
    validation: dict[str, Any] | None,
    project_path: str,
    index: int,
) -> dict[str, Any]:
    file_entry = file_entry or {}
    source_context = validation.get("source_context") if isinstance(validation, dict) else {}
    if not isinstance(source_context, dict):
        source_context = {}

    file_path = str(
        violation.get("file_path")
        or file_entry.get("file_path")
        or source_context.get("file_path")
        or ""
    )
    fix_code = violation.get("fix_code")
    fix_description = str(violation.get("fix_description") or "")
    source_severity = _source_severity(violation, validation)
    code_snippet = _code_snippet(violation, validation, project_path, file_path)
    fix_options = _fix_options(violation, fix_description, fix_code)

    return {
        "id": _issue_id(violation, file_path, index),
        "title": str(violation.get("summary") or "Untitled issue"),
        "description": str(
            violation.get("why_fix")
            or (validation or {}).get("reasoning")
            or fix_description
            or "No additional description was provided."
        ),
        "severity": _template_severity(source_severity),
        "source_severity": source_severity,
        "hig_criteria": str(violation.get("rule_id") or ""),
        "hig_area": str(violation.get("dimension") or "").upper(),
        "file_path": file_path,
        "line_number": violation.get("line_number") or source_context.get("line_start") or "",
        "code_snippet": code_snippet,
        "recommended_fix": str(fix_code or fix_description),
        "fix_description": fix_description,
        "ai_fix_prompt": str(violation.get("ai_fix_prompt") or ""),
        "fix_options": fix_options,
        "language": _language_for_file(file_path),
        "dimension": str(violation.get("dimension") or ""),
        "domain": str(violation.get("domain") or ""),
        "rule_id": str(violation.get("rule_id") or ""),
        "guideline_reference": violation.get("guideline_reference") or {},
        "state": violation.get("state") or {},
        "evidence_links": _evidence_links(violation, validation),
    }


def _fix_options(
    violation: dict[str, Any],
    fix_description: str,
    fix_code: Any,
) -> list[dict[str, Any]]:
    raw = violation.get("fix_options")
    options: list[dict[str, Any]] = []

    if isinstance(raw, list):
        for entry in raw:
            if not isinstance(entry, dict):
                continue
            options.append(
                {
                    "id": str(entry.get("id") or ""),
                    "label": str(entry.get("label") or "Recommended fix"),
                    "description": str(entry.get("description") or ""),
                    "kind": str(entry.get("kind") or ""),
                    "recommended": bool(entry.get("recommended")),
                    "code": str(entry.get("code") or ""),
                    "ai_fix_prompt": str(entry.get("ai_fix_prompt") or ""),
                }
            )

    if options:
        return options

    fallback_code = str(fix_code) if isinstance(fix_code, str) else ""
    fallback_description = fix_description or "Apply the analyzer's recommended remediation."
    return [
        {
            "id": "analyzer-recommended",
            "label": "Apply analyzer recommendation",
            "description": fallback_description,
            "kind": "minimal",
            "recommended": True,
            "code": fallback_code,
            "ai_fix_prompt": str(violation.get("ai_fix_prompt") or ""),
        }
    ]


def _file_entries(analyzer_report: dict[str, Any]) -> list[dict[str, Any]]:
    files = analyzer_report.get("files")
    if isinstance(files, list) and files:
        return [file_entry for file_entry in files if isinstance(file_entry, dict)]

    violations = analyzer_report.get("violations")
    if not isinstance(violations, list):
        return []

    grouped: dict[str, list[dict[str, Any]]] = {}
    for violation in violations:
        if not isinstance(violation, dict):
            continue
        file_path = str(violation.get("file_path") or "")
        grouped.setdefault(file_path, []).append(violation)

    return [
        {"file_path": file_path, "violations": grouped_violations}
        for file_path, grouped_violations in grouped.items()
    ]


def _flatten_issues(
    analyzer_report: dict[str, Any],
    validation_report: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    validations = _validation_index(validation_report)
    matched_validation_ids: set[str] = set()
    issues: list[dict[str, Any]] = []
    project_path = str(analyzer_report.get("project_path") or (validation_report or {}).get("project_path") or "")

    for file_entry in _file_entries(analyzer_report):
        for violation in file_entry.get("violations", []) or []:
            if not isinstance(violation, dict):
                continue
            validation = validations.get(str(violation.get("id") or ""))
            if _skip_from_validation(validation):
                continue
            if not _visible_issue(violation) and not _render_from_validation(validation):
                continue

            issues.append(_issue_from_violation(violation, file_entry, validation, project_path, len(issues)))
            violation_id = str(violation.get("id") or "")
            if violation_id:
                matched_validation_ids.add(violation_id)

    for validation in _validation_items(validation_report):
        if not _render_from_validation(validation):
            continue
        original = validation.get("original_violation") or {}
        if not isinstance(original, dict):
            continue
        violation_id = str(original.get("id") or "")
        if violation_id and violation_id in matched_validation_ids:
            continue
        if not _visible_issue(original) and not _render_from_validation(validation):
            continue
        issues.append(_issue_from_violation(original, None, validation, project_path, len(issues)))

    return issues


def _severity_counts(issues: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for issue in issues:
        severity = issue.get("severity")
        if severity in counts:
            counts[severity] += 1
    return counts


def _manifest_run(manifest: dict[str, Any] | None, run_number: int | None) -> dict[str, Any] | None:
    if manifest is None or run_number is None:
        return None
    for run in manifest.get("runs", []) or []:
        if isinstance(run, dict) and run.get("number") == run_number:
            return run
    return None


def build_report_data(
    analyzer_report: dict[str, Any],
    manifest: dict[str, Any] | None,
    validation_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    issues = _flatten_issues(analyzer_report, validation_report)
    severity_counts = _severity_counts(issues)
    run = analyzer_report.get("run") or {}
    analyzer_run = run.get("number") or (validation_report or {}).get("analyzer_run")
    manifest_run = _manifest_run(manifest, analyzer_run if isinstance(analyzer_run, int) else None)
    project_path = str(analyzer_report.get("project_path") or (validation_report or {}).get("project_path") or "")
    created_at = run.get("createdAt") or (validation_report or {}).get("createdAt")
    if not created_at:
        created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    html_report_data = analyzer_report.get("html_report_data")
    if not isinstance(html_report_data, dict):
        html_report_data = {}
    html_scan_context = html_report_data.get("scan_context")
    if not isinstance(html_scan_context, dict):
        html_scan_context = {}

    platform = str(html_report_data.get("framework") or analyzer_report.get("platform") or "SwiftUI")
    guidelines = str(
        html_report_data.get("hig_standard")
        or html_report_data.get("standard_label")
        or analyzer_report.get("guidelines")
        or "Apple Human Interface Guidelines"
    )
    domain_summaries = analyzer_report.get("domain_summaries", []) or []

    return {
        "project_name": html_report_data.get("project_name") or _project_name(project_path),
        "project_path": html_report_data.get("project_path") or project_path,
        "framework": platform,
        "hig_standard": guidelines,
        "guidelines": guidelines,
        "scan_date": created_at,
        "summary": {
            "total": len(issues),
            "critical": severity_counts["critical"],
            "high": severity_counts["high"],
            "medium": severity_counts["medium"],
            "low": severity_counts["low"],
        },
        "issues": issues,
        "scan_context": {
            "analyzer_run": analyzer_run,
            "analyzer_status": run.get("status"),
            "manifest_status": (manifest_run or {}).get("status"),
            "frameworks": html_scan_context.get("frameworks", [platform]),
            "framework_versions": html_scan_context.get("framework_versions", {}),
            "design_systems": html_scan_context.get("design_systems", [guidelines]),
            "component_patterns": html_scan_context.get("component_patterns") or [
                str(item.get("domain"))
                for item in domain_summaries
                if isinstance(item, dict) and item.get("domain")
            ],
            "scan_duration": html_scan_context.get("scan_duration"),
            "files_scanned": html_scan_context.get("files_scanned", analyzer_report.get("total_files", 0)),
            "confidence": html_scan_context.get("confidence"),
            "custom_utilities": html_scan_context.get("custom_utilities", []),
            "total_files": analyzer_report.get("total_files", 0),
            "overall_score": analyzer_report.get("overall_score"),
            "ui_score": analyzer_report.get("ui_score"),
            "ux_score": analyzer_report.get("ux_score"),
            "a11y_score": analyzer_report.get("a11y_score"),
            "domain_summaries": domain_summaries,
            "executive_summary": analyzer_report.get("executive_summary", ""),
        },
    }


def build_html(data: dict[str, Any]) -> str:
    """Build the complete HTML document with bold modern aesthetic."""
    json_data = _safe_script_json(data)
    project_name = escape(str(data.get("project_name") or "Unknown Project"))

    template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EvenBetter iOS HIG Report | __REPORT_PROJECT_NAME__</title>

    <!-- Tailwind CSS v4 Browser -->
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>

    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>

    <!-- Highlight.js -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css" class="dark-syntax">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-light.min.css" class="light-syntax" disabled>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

    <!-- Google Fonts - Bold Modern Typography -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

    <style>
        /* CSS Custom Properties for Theming */
        :root {
            --font-display: 'Syne', sans-serif;
            --font-body: 'DM Sans', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;

            /* Electric Teal Accent */
            --accent: #0DD3CF;
            --accent-hover: #0BEAE5;
            --accent-muted: rgba(13, 211, 207, 0.15);

            /* Severity Colors */
            --critical: #FF4757;
            --critical-bg: rgba(255, 71, 87, 0.12);
            --high: #FFA502;
            --high-bg: rgba(255, 165, 2, 0.12);
            --medium: #3B82F6;
            --medium-bg: rgba(59, 130, 246, 0.12);
            --low: #2ED573;
            --low-bg: rgba(46, 213, 115, 0.12);
        }

        /* Light Theme - Warm Beige */
        :root {
            --bg-primary: #E8E0D4;
            --bg-secondary: #F2EBE1;
            --bg-tertiary: #DCD4C8;
            --bg-card: rgba(242, 235, 225, 0.92);
            --bg-card-hover: rgba(248, 243, 235, 0.96);
            --border: rgba(87, 65, 40, 0.15);
            --border-strong: rgba(87, 65, 40, 0.28);
            --text-primary: #1A1206;
            --text-secondary: #302618;
            --text-muted: #524738;
            --shadow: rgba(60, 45, 25, 0.15);
            --grain-opacity: 0.04;
        }

        /* Dark Theme */
        .dark {
            --bg-primary: #0C0A09;
            --bg-secondary: #1C1917;
            --bg-tertiary: #292524;
            --bg-card: rgba(28, 25, 23, 0.7);
            --bg-card-hover: rgba(41, 37, 36, 0.9);
            --border: rgba(255, 255, 255, 0.06);
            --border-strong: rgba(255, 255, 255, 0.12);
            --text-primary: #FAFAF9;
            --text-secondary: #A8A29E;
            --text-muted: #78716C;
            --shadow: rgba(0, 0, 0, 0.4);
            --grain-opacity: 0.04;
        }

        [x-cloak] { display: none !important; }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: var(--font-body);
            background: var(--bg-primary);
            color: var(--text-primary);
            transition: background-color 0.3s ease, color 0.3s ease;
        }

        .report-root {
            min-height: 100vh;
            background: var(--bg-primary);
            color: var(--text-primary);
            transition: background-color 0.3s ease, color 0.3s ease;
        }

        /* Grain Texture Overlay */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 9999;
            opacity: var(--grain-opacity);
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
        }

        /* Typography */
        .font-display { font-family: var(--font-display); }
        .font-body { font-family: var(--font-body); }
        .font-mono { font-family: var(--font-mono); }

        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-secondary);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--text-muted);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-secondary);
        }

        /* Glass Card Effect */
        .glass-card {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border);
            transition: all 0.2s ease;
        }

        .glass-card:hover {
            background: var(--bg-card-hover);
            border-color: var(--border-strong);
        }

        /* Geometric Accent Shape */
        .geo-accent {
            position: absolute;
            width: 400px;
            height: 400px;
            border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%;
            background: linear-gradient(135deg, var(--accent) 0%, transparent 60%);
            opacity: 0.08;
            filter: blur(60px);
            pointer-events: none;
        }

        /* Syntax highlighting overrides */
        .hljs {
            background: transparent !important;
            padding: 0 !important;
        }

        /* Light mode syntax colors - more vibrant */
        :root .hljs-keyword,
        :root .hljs-selector-tag,
        :root .hljs-built_in,
        :root .hljs-name,
        :root .hljs-tag {
            color: #8B2252 !important;
        }

        :root .hljs-string,
        :root .hljs-title,
        :root .hljs-section,
        :root .hljs-attribute,
        :root .hljs-literal,
        :root .hljs-template-tag,
        :root .hljs-template-variable,
        :root .hljs-type {
            color: #0B6E4F !important;
        }

        :root .hljs-number,
        :root .hljs-symbol,
        :root .hljs-bullet,
        :root .hljs-link,
        :root .hljs-meta,
        :root .hljs-selector-id,
        :root .hljs-title.function_ {
            color: #0057A8 !important;
        }

        :root .hljs-comment,
        :root .hljs-quote {
            color: #656E77 !important;
            font-style: italic;
        }

        :root .hljs-variable,
        :root .hljs-params,
        :root .hljs-property {
            color: #B84C00 !important;
        }

        /* Dark mode - restore defaults */
        .dark .hljs-keyword,
        .dark .hljs-selector-tag,
        .dark .hljs-built_in,
        .dark .hljs-name,
        .dark .hljs-tag,
        .dark .hljs-string,
        .dark .hljs-title,
        .dark .hljs-section,
        .dark .hljs-attribute,
        .dark .hljs-literal,
        .dark .hljs-template-tag,
        .dark .hljs-template-variable,
        .dark .hljs-type,
        .dark .hljs-number,
        .dark .hljs-symbol,
        .dark .hljs-bullet,
        .dark .hljs-link,
        .dark .hljs-meta,
        .dark .hljs-selector-id,
        .dark .hljs-title.function_,
        .dark .hljs-comment,
        .dark .hljs-quote,
        .dark .hljs-variable,
        .dark .hljs-params,
        .dark .hljs-property {
            color: revert !important;
            font-style: revert;
        }

        /* Copy button animation */
        .copy-btn {
            transition: all 0.15s ease;
        }

        .copy-btn:active {
            transform: scale(0.92);
        }

        .copy-btn.copied {
            color: var(--accent) !important;
        }

        /* Severity border animation */
        .severity-border {
            position: relative;
        }

        .severity-border::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            border-radius: 4px 0 0 4px;
            transition: width 0.2s ease;
        }

        .severity-border:hover::before {
            width: 6px;
        }

        .severity-critical::before { background: var(--critical); }
        .severity-high::before { background: var(--high); }
        .severity-medium::before { background: var(--medium); }
        .severity-low::before { background: var(--low); }

        /* Theme toggle */
        .theme-toggle {
            position: relative;
            width: 56px;
            height: 28px;
            border-radius: 14px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-strong);
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .theme-toggle::after {
            content: '';
            position: absolute;
            top: 2px;
            left: 2px;
            width: 22px;
            height: 22px;
            border-radius: 50%;
            background: var(--accent);
            transition: transform 0.3s ease;
            box-shadow: 0 2px 8px var(--shadow);
        }

        .dark .theme-toggle::after {
            transform: translateX(28px);
        }

        /* Filter chip active state */
        .filter-chip {
            transition: all 0.15s ease;
        }

        .filter-chip.active {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px var(--shadow);
        }

        /* AI Prompts Quick Reference Section */
        .prompt-row {
            transition: all 0.15s ease;
            border-left: 3px solid transparent;
        }

        .prompt-row:hover {
            background: var(--bg-card-hover);
            border-left-color: var(--accent);
        }

        .prompt-id {
            cursor: pointer;
            transition: color 0.15s ease;
        }

        .prompt-id:hover {
            color: var(--accent-hover);
            text-decoration: underline;
        }

        /* Scroll target highlight */
        .issue-card-target {
            scroll-margin-top: 100px;
        }

        .issue-card-target.highlighted {
            animation: highlight-pulse 1.5s ease-out;
        }

        @keyframes highlight-pulse {
            0% { box-shadow: 0 0 0 4px var(--accent); }
            100% { box-shadow: 0 0 0 0 transparent; }
        }
    </style>
</head>
<body class="min-h-screen">
    <div x-data="window.reportApp()" x-init="initApp()" :class="{ 'dark': darkMode }" class="report-root antialiased selection:bg-[var(--accent)] selection:text-black">

    <!-- Geometric Background Accents -->
    <div class="geo-accent" style="top: -200px; right: -100px;"></div>
    <div class="geo-accent" style="bottom: -200px; left: -100px; animation-delay: -2s;"></div>

    <!-- Navigation / Header -->
    <header class="fixed top-0 w-full z-50 glass-card border-b" style="border-color: var(--border);">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <!-- Logo & Title -->
                <div class="flex items-center gap-4">
                    <div class="flex items-center justify-center w-10 h-10 rounded-xl" style="background: linear-gradient(135deg, var(--accent) 0%, #06B6D4 100%); box-shadow: 0 4px 16px rgba(13, 211, 207, 0.3);">
                        <i data-lucide="scan-eye" class="text-black w-5 h-5"></i>
                    </div>
                    <div>
                        <h1 class="font-display font-bold text-lg tracking-tight" style="color: var(--text-primary);">
                            EVENBETTER
                            <span class="font-mono text-xs font-normal ml-2 px-2 py-0.5 rounded" style="background: var(--accent-muted); color: var(--accent);">iOS HIG</span>
                        </h1>
                        <p class="text-xs font-mono" style="color: var(--text-muted);" x-text="data.scan_date"></p>
                    </div>
                </div>

                <!-- Meta Info & Theme Toggle -->
                <div class="flex items-center gap-6">
                    <!-- Project Meta (Hidden on mobile) -->
                    <div class="hidden md:flex items-center gap-6 text-sm">
                        <div class="text-right">
                            <p class="text-[10px] font-mono uppercase tracking-wider" style="color: var(--text-muted);">Project</p>
                            <p class="font-medium truncate max-w-[150px]" style="color: var(--text-primary);" x-text="data.project_name"></p>
                        </div>
                        <div class="w-px h-8" style="background: var(--border);"></div>
                        <div class="text-right">
                            <p class="text-[10px] font-mono uppercase tracking-wider" style="color: var(--text-muted);">Framework</p>
                            <p class="font-medium" style="color: var(--accent);" x-text="data.framework"></p>
                        </div>
                        <div class="w-px h-8" style="background: var(--border);"></div>
                        <div class="text-right">
                            <p class="text-[10px] font-mono uppercase tracking-wider" style="color: var(--text-muted);">HIG</p>
                            <p class="font-medium" style="color: var(--text-primary);" x-text="data.hig_standard"></p>
                        </div>
                    </div>

                    <!-- Theme Toggle -->
                    <button @click="toggleTheme()" class="theme-toggle" :aria-label="darkMode ? 'Switch to light mode' : 'Switch to dark mode'">
                        <span class="sr-only" x-text="darkMode ? 'Dark mode' : 'Light mode'"></span>
                    </button>
                </div>
            </div>
        </div>
    </header>

    <main class="pt-24 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto relative">

        <!-- Summary Dashboard -->
        <section class="mb-8">
            <!-- Total Issues Hero -->
            <div class="glass-card rounded-2xl p-6 mb-4 relative overflow-hidden">
                <div class="absolute top-0 right-0 w-32 h-32 rounded-full blur-3xl" style="background: var(--accent); opacity: 0.1;"></div>
                <div class="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
                    <div>
                        <p class="text-xs font-mono uppercase tracking-widest mb-2" style="color: var(--text-muted);">Total Issues Found</p>
                        <h2 class="font-display font-extrabold text-6xl sm:text-7xl tracking-tight" style="color: var(--text-primary);" x-text="data.summary.total"></h2>
                    </div>
                    <p class="font-mono text-sm max-w-xs" style="color: var(--text-secondary);">
                        iOS HIG and accessibility issues detected in your SwiftUI codebase. Click severity cards to filter.
                    </p>
                </div>
            </div>

            <!-- Severity Breakdown -->
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
                <!-- Critical -->
                <button @click="toggleFilter('critical')"
                        class="filter-chip glass-card rounded-xl p-4 text-left severity-border severity-critical"
                        :class="{ 'active': filters.severity.includes('critical') }">
                    <div class="flex items-center justify-between mb-3">
                        <i data-lucide="alert-octagon" class="w-5 h-5" style="color: var(--critical);"></i>
                        <span x-show="filters.severity.includes('critical')" class="w-2 h-2 rounded-full" style="background: var(--critical);"></span>
                    </div>
                    <p class="font-display font-bold text-3xl" style="color: var(--text-primary);" x-text="data.summary.critical"></p>
                    <p class="text-xs font-mono uppercase tracking-wider mt-1" style="color: var(--critical);">Critical</p>
                </button>

                <!-- High -->
                <button @click="toggleFilter('high')"
                        class="filter-chip glass-card rounded-xl p-4 text-left severity-border severity-high"
                        :class="{ 'active': filters.severity.includes('high') }">
                    <div class="flex items-center justify-between mb-3">
                        <i data-lucide="alert-triangle" class="w-5 h-5" style="color: var(--high);"></i>
                        <span x-show="filters.severity.includes('high')" class="w-2 h-2 rounded-full" style="background: var(--high);"></span>
                    </div>
                    <p class="font-display font-bold text-3xl" style="color: var(--text-primary);" x-text="data.summary.high"></p>
                    <p class="text-xs font-mono uppercase tracking-wider mt-1" style="color: var(--high);">High</p>
                </button>

                <!-- Medium -->
                <button @click="toggleFilter('medium')"
                        class="filter-chip glass-card rounded-xl p-4 text-left severity-border severity-medium"
                        :class="{ 'active': filters.severity.includes('medium') }">
                    <div class="flex items-center justify-between mb-3">
                        <i data-lucide="info" class="w-5 h-5" style="color: var(--medium);"></i>
                        <span x-show="filters.severity.includes('medium')" class="w-2 h-2 rounded-full" style="background: var(--medium);"></span>
                    </div>
                    <p class="font-display font-bold text-3xl" style="color: var(--text-primary);" x-text="data.summary.medium"></p>
                    <p class="text-xs font-mono uppercase tracking-wider mt-1" style="color: var(--medium);">Medium</p>
                </button>

                <!-- Low -->
                <button @click="toggleFilter('low')"
                        class="filter-chip glass-card rounded-xl p-4 text-left severity-border severity-low"
                        :class="{ 'active': filters.severity.includes('low') }">
                    <div class="flex items-center justify-between mb-3">
                        <i data-lucide="check-circle-2" class="w-5 h-5" style="color: var(--low);"></i>
                        <span x-show="filters.severity.includes('low')" class="w-2 h-2 rounded-full" style="background: var(--low);"></span>
                    </div>
                    <p class="font-display font-bold text-3xl" style="color: var(--text-primary);" x-text="data.summary.low"></p>
                    <p class="text-xs font-mono uppercase tracking-wider mt-1" style="color: var(--low);">Low</p>
                </button>
            </div>
        </section>

        <!-- Scan Context Section (Collapsible) -->
        <section class="glass-card rounded-xl mb-6 overflow-hidden" x-show="data.scan_context">
            <!-- Header -->
            <div @click="contextExpanded = !contextExpanded"
                 class="w-full p-4 flex items-center justify-between cursor-pointer select-none hover:opacity-90">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 flex items-center justify-center rounded-lg" style="background: var(--accent-muted);">
                        <i data-lucide="flask-conical" class="w-4 h-4" style="color: var(--accent);"></i>
                    </div>
                    <div>
                        <h3 class="font-display font-bold text-sm" style="color: var(--text-primary);">Scan Context</h3>
                        <p class="text-xs font-mono" style="color: var(--text-muted);">Project analysis details</p>
                    </div>
                </div>
                <button class="w-8 h-8 flex items-center justify-center rounded-lg" style="background: var(--bg-tertiary);">
                    <i data-lucide="chevron-down" class="w-4 h-4 transition-transform duration-200"
                       :class="{ 'rotate-180': contextExpanded }"
                       style="color: var(--text-muted);"></i>
                </button>
            </div>

            <!-- Expanded Content -->
            <div x-show="contextExpanded" x-collapse x-cloak>
                <div class="px-4 pb-4 border-t" style="border-color: var(--border);">
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-4">

                        <!-- Frameworks -->
                        <div class="p-3 rounded-lg" style="background: var(--bg-tertiary);" x-show="data.scan_context?.frameworks?.length > 0">
                            <div class="flex items-center gap-2 mb-2">
                                <i data-lucide="layers" class="w-4 h-4" style="color: var(--accent);"></i>
                                <span class="text-xs font-mono uppercase tracking-wider" style="color: var(--text-muted);">Frameworks</span>
                            </div>
                            <template x-for="fw in data.scan_context?.frameworks || []" :key="fw">
                                <div class="flex items-center justify-between py-1">
                                    <span class="text-sm font-medium" style="color: var(--text-primary);" x-text="fw"></span>
                                    <span class="text-xs font-mono" style="color: var(--accent);"
                                          x-text="data.scan_context?.framework_versions?.[fw] || ''"></span>
                                </div>
                            </template>
                        </div>

                        <!-- Design Systems -->
                        <div class="p-3 rounded-lg" style="background: var(--bg-tertiary);" x-show="data.scan_context?.design_systems?.length > 0">
                            <div class="flex items-center gap-2 mb-2">
                                <i data-lucide="palette" class="w-4 h-4" style="color: var(--accent);"></i>
                                <span class="text-xs font-mono uppercase tracking-wider" style="color: var(--text-muted);">Design Systems</span>
                            </div>
                            <template x-for="ds in data.scan_context?.design_systems || []" :key="ds">
                                <p class="text-sm py-1" style="color: var(--text-primary);" x-text="ds"></p>
                            </template>
                        </div>

                        <!-- Component Patterns -->
                        <div class="p-3 rounded-lg" style="background: var(--bg-tertiary);" x-show="data.scan_context?.component_patterns?.length > 0">
                            <div class="flex items-center gap-2 mb-2">
                                <i data-lucide="puzzle" class="w-4 h-4" style="color: var(--accent);"></i>
                                <span class="text-xs font-mono uppercase tracking-wider" style="color: var(--text-muted);">Patterns</span>
                            </div>
                            <template x-for="pattern in (data.scan_context?.component_patterns || []).slice(0, 4)" :key="pattern">
                                <p class="text-sm py-1" style="color: var(--text-primary);" x-text="pattern"></p>
                            </template>
                            <p x-show="(data.scan_context?.component_patterns?.length || 0) > 4"
                               class="text-xs font-mono" style="color: var(--text-muted);"
                               x-text="'... and ' + (data.scan_context.component_patterns.length - 4) + ' more'"></p>
                        </div>

                        <!-- Scan Statistics -->
                        <div class="p-3 rounded-lg" style="background: var(--bg-tertiary);">
                            <div class="flex items-center gap-2 mb-2">
                                <i data-lucide="bar-chart-3" class="w-4 h-4" style="color: var(--accent);"></i>
                                <span class="text-xs font-mono uppercase tracking-wider" style="color: var(--text-muted);">Statistics</span>
                            </div>
                            <div class="space-y-2">
                                <div class="flex justify-between" x-show="data.scan_context?.scan_duration">
                                    <span class="text-sm" style="color: var(--text-secondary);">Duration</span>
                                    <span class="text-sm font-mono" style="color: var(--text-primary);"
                                          x-text="data.scan_context?.scan_duration?.toFixed(1) + 's'"></span>
                                </div>
                                <div class="flex justify-between" x-show="data.scan_context?.files_scanned != null">
                                    <span class="text-sm" style="color: var(--text-secondary);">Files</span>
                                    <span class="text-sm font-mono" style="color: var(--text-primary);"
                                          x-text="data.scan_context?.files_scanned"></span>
                                </div>
                                <div class="flex justify-between" x-show="data.scan_context?.confidence">
                                    <span class="text-sm" style="color: var(--text-secondary);">Confidence</span>
                                    <span class="text-sm font-mono" style="color: var(--accent);"
                                          x-text="Math.round((data.scan_context?.confidence || 0) * 100) + '%'"></span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Custom Utilities (if present) -->
                    <div class="mt-4 p-3 rounded-lg" style="background: var(--bg-tertiary);"
                         x-show="data.scan_context?.custom_utilities?.length > 0">
                        <div class="flex items-center gap-2 mb-2">
                            <i data-lucide="wrench" class="w-4 h-4" style="color: var(--accent);"></i>
                            <span class="text-xs font-mono uppercase tracking-wider" style="color: var(--text-muted);">Custom Utilities</span>
                        </div>
                        <div class="flex flex-wrap gap-2">
                            <template x-for="util in (data.scan_context?.custom_utilities || []).slice(0, 6)" :key="util">
                                <span class="px-2 py-1 rounded text-xs font-mono"
                                      style="background: var(--accent-muted); color: var(--accent);"
                                      x-text="util"></span>
                            </template>
                            <span x-show="(data.scan_context?.custom_utilities?.length || 0) > 6"
                                  class="px-2 py-1 rounded text-xs font-mono"
                                  style="background: var(--bg-secondary); color: var(--text-muted);"
                                  x-text="'+' + (data.scan_context.custom_utilities.length - 6) + ' more'"></span>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Search & Filters Bar -->
        <section class="glass-card rounded-xl p-4 mb-6 flex flex-col sm:flex-row gap-4 items-center justify-between">
            <!-- Search Input -->
            <div class="relative w-full sm:w-96">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <i data-lucide="search" class="h-4 w-4" style="color: var(--text-muted);"></i>
                </div>
                <input type="text" x-model="searchQuery"
                       class="block w-full pl-10 pr-3 py-2.5 rounded-lg text-sm font-mono transition-all focus:outline-none focus:ring-2"
                       style="background: var(--bg-tertiary); border: 1px solid var(--border); color: var(--text-primary); --tw-ring-color: var(--accent);"
                       placeholder="Search files, HIG criteria, issues...">
            </div>

            <!-- Active Filters Display -->
            <div class="flex items-center gap-3 text-sm flex-wrap justify-center sm:justify-end">
                <span class="font-mono text-xs" style="color: var(--text-muted);">Filters:</span>
                <template x-if="filters.severity.length === 0 && !searchQuery">
                    <span class="px-2 py-1 rounded text-xs font-mono" style="background: var(--bg-tertiary); color: var(--text-secondary);">All issues</span>
                </template>
                <template x-for="filter in filters.severity" :key="filter">
                    <span class="px-2 py-1 rounded text-xs font-bold uppercase tracking-wider"
                          :style="getSeverityStyle(filter)" x-text="filter"></span>
                </template>
                <button @click="resetFilters()"
                        x-show="filters.severity.length > 0 || searchQuery"
                        class="flex items-center gap-1 text-xs font-mono hover:opacity-80 transition-opacity"
                        style="color: var(--accent);">
                    <i data-lucide="x" class="w-3 h-3"></i>
                    Clear
                </button>
            </div>
        </section>

        <!-- AI Prompts Quick Reference Section -->
        <section class="glass-card rounded-xl mb-6 overflow-hidden">
            <!-- Header (Always Visible) -->
            <div class="w-full p-5 flex items-center justify-between select-none"
                 style="background: var(--accent-muted);">

                <!-- Left Side (Clickable) -->
                <div @click="promptsExpanded = !promptsExpanded" class="flex items-center gap-4 cursor-pointer flex-1">
                    <div class="w-10 h-10 flex items-center justify-center rounded-xl" style="background: var(--accent); opacity: 0.9; box-shadow: 0 2px 8px rgba(13, 211, 207, 0.2);">
                        <i data-lucide="sparkles" class="w-5 h-5 text-black"></i>
                    </div>
                    <div class="text-left">
                        <h3 class="font-display font-bold text-base" style="color: var(--text-primary);">
                            AI Prompts Quick Reference
                        </h3>
                        <p class="text-xs font-mono mt-0.5" style="color: var(--text-muted);">
                            <span x-text="data.issues.length"></span> prompts ready to copy
                        </p>
                    </div>
                </div>

                <!-- Right Side (Actions) -->
                <div class="flex items-center gap-4">
                    <button @click="copyAllPrompts()"
                            class="copy-btn flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all hover:opacity-90 hover:translate-y-[-1px] shadow-sm"
                            style="background: var(--accent); color: black;">
                        <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                        COPY ALL
                    </button>

                    <button @click="promptsExpanded = !promptsExpanded"
                            class="w-9 h-9 flex items-center justify-center rounded-lg transition-colors hover:bg-black/5"
                            style="background: var(--bg-tertiary);">
                        <i data-lucide="chevron-down" class="w-5 h-5 transition-transform duration-200"
                           :class="{ 'rotate-180': promptsExpanded }"
                           style="color: var(--text-muted);"></i>
                    </button>
                </div>
            </div>

            <!-- Expanded Content -->
            <div x-show="promptsExpanded" x-collapse x-cloak>
                <div class="border-t max-h-96 overflow-y-auto" style="border-color: var(--border);">
                    <template x-for="issue in data.issues" :key="issue.id">
                        <div class="prompt-row p-3 border-b flex items-start gap-3" style="border-color: var(--border);">
                            <!-- ID Badge -->
                            <button @click="scrollToIssue(issue.id)"
                                    class="prompt-id flex-shrink-0 px-2 py-0.5 rounded text-[10px] font-mono font-bold"
                                    style="background: var(--bg-tertiary); color: var(--accent);"
                                    :title="'Jump to issue ' + issue.id">
                                #<span x-text="issue.id"></span>
                            </button>

                            <!-- Summary & Prompt -->
                            <div class="flex-1 min-w-0">
                                <div class="flex items-center gap-2 mb-1">
                                    <span class="text-xs font-medium truncate" style="color: var(--text-primary);"
                                          x-text="issue.title.length > 50 ? issue.title.substring(0, 50) + '...' : issue.title"></span>
                                    <span class="flex-shrink-0 px-1.5 py-0.5 rounded text-[9px] font-bold uppercase"
                                          :style="getSeverityStyle(issue.severity)" x-text="issue.severity"></span>
                                </div>
                                <p class="text-xs font-mono truncate" style="color: var(--text-muted);"
                                   x-text="issue.ai_fix_prompt.length > 80 ? issue.ai_fix_prompt.substring(0, 80) + '...' : issue.ai_fix_prompt"></p>
                            </div>

                            <!-- Copy Button -->
                            <button @click="copyText(issue.ai_fix_prompt, 'Prompt copied!')"
                                    class="copy-btn flex-shrink-0 p-1.5 rounded-lg transition-colors hover:opacity-80"
                                    style="background: var(--bg-tertiary); color: var(--accent);"
                                    title="Copy prompt">
                                <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                            </button>
                        </div>
                    </template>
                </div>
            </div>
        </section>

        <!-- Issues List -->
        <section class="space-y-4">
            <!-- Empty State -->
            <div x-show="filteredIssues.length === 0" x-cloak class="text-center py-20">
                <div class="inline-flex items-center justify-center w-20 h-20 rounded-2xl mb-4" style="background: var(--bg-tertiary);">
                    <i data-lucide="search-x" class="w-10 h-10" style="color: var(--text-muted);"></i>
                </div>
                <h3 class="font-display font-bold text-xl" style="color: var(--text-primary);">No matching issues</h3>
                <p class="mt-2 max-w-sm mx-auto" style="color: var(--text-muted);">
                    Try adjusting your search or filters to find what you're looking for.
                </p>
            </div>

            <!-- Issue Cards -->
            <template x-for="(issue, index) in filteredIssues" :key="issue.id">
                <article :id="'issue-' + issue.id"
                         class="glass-card rounded-xl overflow-hidden severity-border transition-all duration-200 issue-card-target"
                         :class="'severity-' + issue.severity">

                    <!-- Card Header (Always Visible) -->
                    <div class="p-5 cursor-pointer select-none" @click="issue.expanded = !issue.expanded">
                        <div class="flex items-start justify-between gap-4">
                            <div class="flex-1 min-w-0">
                                <!-- Badges Row -->
                                <div class="flex flex-wrap items-center gap-2 mb-2">
                                    <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold"
                                          style="background: var(--accent-muted); color: var(--accent);">
                                        #<span x-text="issue.id"></span>
                                    </span>
                                    <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
                                          :style="getSeverityStyle(issue.severity)">
                                        <i :data-lucide="getSeverityIcon(issue.severity)" class="w-3 h-3"></i>
                                        <span x-text="issue.severity"></span>
                                    </span>
                                    <span class="px-2 py-0.5 rounded text-[10px] font-mono uppercase tracking-wider"
                                          style="background: var(--bg-tertiary); color: var(--text-secondary);">
                                        HIG <span x-text="issue.hig_criteria"></span>
                                        <span class="opacity-60">(<span x-text="issue.hig_area"></span>)</span>
                                    </span>
                                </div>

                                <!-- Title -->
                                <h3 class="font-display font-bold text-lg leading-tight mb-1" style="color: var(--text-primary);">
                                    <span x-text="issue.title"></span>
                                </h3>

                                <!-- File Path -->
                                <p class="flex items-center gap-1 text-xs font-mono truncate" style="color: var(--text-muted);">
                                    <i data-lucide="file-code" class="w-3 h-3 flex-shrink-0"></i>
                                    <span x-text="issue.file_path"></span>:<span x-text="issue.line_number"></span>
                                </p>
                            </div>

                            <!-- Actions -->
                            <div class="flex items-center gap-2 flex-shrink-0">
                                <!-- Quick Copy AI Prompt -->
                                <button @click.stop="copyText(issue.ai_fix_prompt, 'AI prompt copied!')"
                                        class="copy-btn p-2 rounded-lg transition-colors"
                                        style="background: var(--accent-muted); color: var(--accent);"
                                        title="Copy AI Fix Prompt">
                                    <i data-lucide="sparkles" class="w-4 h-4"></i>
                                </button>

                                <!-- Expand Toggle -->
                                <div class="w-8 h-8 flex items-center justify-center rounded-lg" style="background: var(--bg-tertiary);">
                                    <i data-lucide="chevron-down" class="w-4 h-4 transition-transform duration-200"
                                       :class="{ 'rotate-180': issue.expanded }"
                                       style="color: var(--text-muted);"></i>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Expanded Content -->
                    <div x-show="issue.expanded" x-collapse x-cloak>
                        <div class="px-5 pb-5 pt-0 border-t" style="border-color: var(--border);">

                            <!-- Description -->
                            <div class="mt-4 text-sm leading-relaxed" style="color: var(--text-secondary);">
                                <p x-text="issue.description"></p>
                                <p class="mt-3 text-xs font-mono" style="color: var(--text-muted);" x-show="issue.evidence_links && issue.evidence_links.length">
                                    Evidence:
                                    <template x-for="(link, linkIndex) in issue.evidence_links" :key="link.url">
                                        <span>
                                            <a :href="link.url" target="_blank" rel="noopener noreferrer" class="hover:underline" style="color: var(--accent);" :title="link.reason || link.url" x-text="link.label"></a><span x-show="linkIndex < issue.evidence_links.length - 1"> · </span>
                                        </span>
                                    </template>
                                </p>
                            </div>

                            <!-- Code Comparison -->
                            <div class="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-4">
                                <!-- Current Code (Problematic) -->
                                <div class="rounded-lg overflow-hidden" style="background: var(--bg-tertiary); border: 1px solid var(--critical); border-opacity: 0.3;">
                                    <div class="px-3 py-2 flex items-center justify-between" style="background: var(--critical-bg); border-bottom: 1px solid var(--critical); border-opacity: 0.2;">
                                        <span class="flex items-center gap-2 text-xs font-mono uppercase tracking-wider" style="color: var(--critical);">
                                            <i data-lucide="x-circle" class="w-3 h-3"></i>
                                            Current Code
                                        </span>
                                        <button @click="copyText(issue.code_snippet, 'Code copied!')"
                                                class="copy-btn p-1 rounded transition-colors hover:opacity-80"
                                                style="color: var(--text-muted);"
                                                title="Copy code">
                                            <i data-lucide="copy" class="w-3 h-3"></i>
                                        </button>
                                    </div>
                                    <div class="p-3 overflow-x-auto">
                                        <pre class="text-sm font-mono"><code :class="'language-' + issue.language" x-text="issue.code_snippet"></code></pre>
                                    </div>
                                </div>

                                <!-- Recommended Fix -->
                                <div class="rounded-lg overflow-hidden" style="background: var(--bg-tertiary); border: 1px solid var(--low); border-opacity: 0.3;">
                                    <div class="px-3 py-2 flex items-center justify-between" style="background: var(--low-bg); border-bottom: 1px solid var(--low); border-opacity: 0.2;">
                                        <span class="flex items-center gap-2 text-xs font-mono uppercase tracking-wider" style="color: var(--low);">
                                            <i data-lucide="check-circle" class="w-3 h-3"></i>
                                            Recommended Fix
                                        </span>
                                        <button @click="copyText(issue.recommended_fix, 'Fix copied!')"
                                                class="copy-btn p-1 rounded transition-colors hover:opacity-80"
                                                style="color: var(--text-muted);"
                                                title="Copy fix">
                                            <i data-lucide="copy" class="w-3 h-3"></i>
                                        </button>
                                    </div>
                                    <div class="p-3 overflow-x-auto">
                                        <pre class="text-sm font-mono"><code :class="'language-' + issue.language" x-text="issue.recommended_fix"></code></pre>
                                    </div>
                                </div>
                            </div>

                            <!-- Remediation Options -->
                            <div class="mt-6" x-show="issue.fix_options && issue.fix_options.length > 0">
                                <div class="rounded-lg overflow-hidden" style="background: var(--bg-tertiary); border: 1px solid var(--accent); border-opacity: 0.3;">
                                    <div class="px-4 py-2 flex items-center justify-between" style="background: var(--accent-muted); border-bottom: 1px solid var(--accent); border-opacity: 0.2;">
                                        <span class="flex items-center gap-2 text-xs font-mono uppercase tracking-wider" style="color: var(--accent);">
                                            <i data-lucide="list-checks" class="w-3 h-3"></i>
                                            Remediation Options
                                        </span>
                                        <span class="text-xs" style="color: var(--text-muted);">
                                            /evenbetter-fix will ask which one to apply
                                        </span>
                                    </div>
                                    <div class="p-4 space-y-3">
                                        <template x-for="(option, optIndex) in issue.fix_options" :key="option.id || optIndex">
                                            <div class="rounded-md p-3" :style="option.recommended ? 'background: var(--low-bg); border: 1px solid var(--low);' : 'background: var(--bg-secondary); border: 1px solid var(--border);'">
                                                <div class="flex items-center justify-between gap-2 flex-wrap">
                                                    <span class="flex items-center gap-2 text-sm font-bold" :style="option.recommended ? 'color: var(--low);' : 'color: var(--text-primary);'">
                                                        <i data-lucide="check-circle" class="w-3 h-3" x-show="option.recommended"></i>
                                                        <i data-lucide="circle" class="w-3 h-3" x-show="!option.recommended"></i>
                                                        <span x-text="option.label"></span>
                                                        <span class="text-xs px-2 py-0.5 rounded font-mono uppercase tracking-wider" style="background: var(--bg-tertiary); color: var(--text-muted);" x-text="option.kind"></span>
                                                        <span x-show="option.recommended" class="text-xs px-2 py-0.5 rounded font-mono uppercase tracking-wider" style="background: var(--low); color: var(--bg-primary);">Recommended</span>
                                                    </span>
                                                    <button x-show="option.code"
                                                            @click="copyText(option.code, 'Option code copied!')"
                                                            class="copy-btn p-1 rounded transition-colors hover:opacity-80"
                                                            style="color: var(--text-muted);"
                                                            title="Copy option code">
                                                        <i data-lucide="copy" class="w-3 h-3"></i>
                                                    </button>
                                                </div>
                                                <p class="mt-2 text-sm" style="color: var(--text-secondary);" x-text="option.description"></p>
                                                <pre class="mt-2 text-sm font-mono p-2 rounded" x-show="option.code" style="background: var(--bg-tertiary);"><code :class="'language-' + issue.language" x-text="option.code"></code></pre>
                                            </div>
                                        </template>
                                    </div>
                                </div>
                            </div>

                            <!-- AI Fix Prompt -->
                            <div class="mt-6">
                                <div class="rounded-lg overflow-hidden" style="background: var(--bg-tertiary); border: 1px solid var(--accent); border-opacity: 0.3;">
                                    <div class="px-4 py-2 flex items-center justify-between" style="background: var(--accent-muted); border-bottom: 1px solid var(--accent); border-opacity: 0.2;">
                                        <span class="flex items-center gap-2 text-xs font-mono uppercase tracking-wider" style="color: var(--accent);">
                                            <i data-lucide="bot" class="w-3 h-3"></i>
                                            AI Auto-Fix Prompt
                                        </span>
                                        <button @click="copyText(issue.ai_fix_prompt, 'AI prompt copied!')"
                                                class="copy-btn flex items-center gap-1 px-2 py-1 rounded text-xs font-bold transition-colors hover:opacity-80"
                                                style="color: var(--accent);">
                                            <i data-lucide="copy" class="w-3 h-3"></i>
                                            COPY
                                        </button>
                                    </div>
                                    <div class="p-4">
                                        <p class="text-sm font-mono break-words whitespace-pre-wrap" style="color: var(--text-secondary);" x-text="issue.ai_fix_prompt"></p>
                                        <p class="mt-3 text-xs flex items-center gap-1" style="color: var(--text-muted);">
                                            <i data-lucide="lightbulb" class="w-3 h-3"></i>
                                            Paste this into Cursor, Claude Code, or Copilot to auto-fix
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </article>
            </template>
        </section>

        <!-- Footer -->
        <footer class="mt-16 pt-8 border-t text-center" style="border-color: var(--border);">
            <p class="font-mono text-xs" style="color: var(--text-muted);">
                Generated by <span class="font-bold" style="color: var(--accent);">EvenBetter</span> — AI-Powered iOS HIG Scanner
            </p>
        </footer>
    </main>

    <!-- Toast Notification -->
    <div class="fixed bottom-6 right-6 z-50"
         x-show="toast.visible"
         x-transition:enter="transition ease-out duration-200"
         x-transition:enter-start="opacity-0 translate-y-4"
         x-transition:enter-end="opacity-100 translate-y-0"
         x-transition:leave="transition ease-in duration-150"
         x-transition:leave-start="opacity-100 translate-y-0"
         x-transition:leave-end="opacity-0 translate-y-4"
         x-cloak>
        <div class="flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg"
             style="background: var(--bg-secondary); border: 1px solid var(--accent); box-shadow: 0 4px 24px var(--shadow);">
            <div class="w-6 h-6 rounded-full flex items-center justify-center" style="background: var(--accent-muted);">
                <i data-lucide="check" class="w-3 h-3" style="color: var(--accent);"></i>
            </div>
            <span class="font-mono text-sm" style="color: var(--text-primary);" x-text="toast.message"></span>
        </div>
    </div>

    </div>

    <script>
        // Inject report data from Python
        const reportData = __REPORT_DATA__;
        window.reportData = reportData;

        window.reportApp = function reportApp() {
            return {
                data: reportData,
                darkMode: true,
                searchQuery: '',
                filters: {
                    severity: []
                },
                contextExpanded: false,
                promptsExpanded: false,
                toast: {
                    visible: false,
                    message: ''
                },

                initApp() {
                    // Load theme preference from localStorage
                    const savedTheme = localStorage.getItem('evenbetter-ios-hig-theme');
                    if (savedTheme) {
                        this.darkMode = savedTheme === 'dark';
                    } else {
                        // Default to system preference
                        this.darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
                    }

                    // Initialize issues with expanded state
                    this.data.issues = this.data.issues.map(issue => ({
                        ...issue,
                        expanded: false
                    }));

                    // Initialize UI components after Alpine renders
                    this.$nextTick(() => {
                        this.initIcons();
                        this.initSyntaxHighlighting();
                        this.updateSyntaxTheme();
                    });

                    // Watch for changes to re-render icons
                    this.$watch('filteredIssues', () => {
                        this.$nextTick(() => {
                            this.initIcons();
                            this.initSyntaxHighlighting();
                        });
                    });

                    // Watch theme changes
                    this.$watch('darkMode', () => {
                        this.updateSyntaxTheme();
                    });
                },

                initIcons() {
                    try {
                        lucide.createIcons();
                    } catch (e) {
                        console.error('Lucide icons error:', e);
                    }
                },

                initSyntaxHighlighting() {
                    try {
                        document.querySelectorAll('pre code').forEach((block) => {
                            if (!block.classList.contains('hljs')) {
                                hljs.highlightElement(block);
                            }
                        });
                    } catch (e) {
                        console.error('Highlight.js error:', e);
                    }
                },

                updateSyntaxTheme() {
                    const darkStyle = document.querySelector('.dark-syntax');
                    const lightStyle = document.querySelector('.light-syntax');
                    if (darkStyle && lightStyle) {
                        darkStyle.disabled = !this.darkMode;
                        lightStyle.disabled = this.darkMode;
                    }
                },

                toggleTheme() {
                    this.darkMode = !this.darkMode;
                    localStorage.setItem('evenbetter-ios-hig-theme', this.darkMode ? 'dark' : 'light');
                },

                get filteredIssues() {
                    return this.data.issues.filter(issue => {
                        // Filter by severity
                        if (this.filters.severity.length > 0 && !this.filters.severity.includes(issue.severity)) {
                            return false;
                        }

                        // Filter by search query
                        if (this.searchQuery) {
                            const query = this.searchQuery.toLowerCase();
                            return (
                                issue.title.toLowerCase().includes(query) ||
                                issue.description.toLowerCase().includes(query) ||
                                issue.file_path.toLowerCase().includes(query) ||
                                issue.hig_criteria.includes(query)
                            );
                        }

                        return true;
                    });
                },

                toggleFilter(severity) {
                    const index = this.filters.severity.indexOf(severity);
                    if (index === -1) {
                        this.filters.severity.push(severity);
                    } else {
                        this.filters.severity.splice(index, 1);
                    }
                },

                resetFilters() {
                    this.filters.severity = [];
                    this.searchQuery = '';
                },

                getSeverityIcon(severity) {
                    const icons = {
                        critical: 'alert-octagon',
                        high: 'alert-triangle',
                        medium: 'info',
                        low: 'check-circle-2'
                    };
                    return icons[severity] || 'circle';
                },

                getSeverityStyle(severity) {
                    const styles = {
                        critical: 'background: var(--critical-bg); color: var(--critical); border: 1px solid var(--critical);',
                        high: 'background: var(--high-bg); color: var(--high); border: 1px solid var(--high);',
                        medium: 'background: var(--medium-bg); color: var(--medium); border: 1px solid var(--medium);',
                        low: 'background: var(--low-bg); color: var(--low); border: 1px solid var(--low);'
                    };
                    return styles[severity] || 'background: var(--bg-tertiary); color: var(--text-secondary);';
                },

                async copyText(text, message) {
                    try {
                        await navigator.clipboard.writeText(text);
                        this.showToast(message || 'Copied to clipboard!');
                    } catch (err) {
                        console.error('Failed to copy:', err);
                        this.showToast('Failed to copy');
                    }
                },

                async copyAllPrompts() {
                    try {
                        const allPrompts = this.data.issues.map(issue =>
                            `[#${issue.id}] ${issue.title}\\n${issue.ai_fix_prompt}`
                        ).join('\\n\\n---\\n\\n');
                        await navigator.clipboard.writeText(allPrompts);
                        this.showToast(`${this.data.issues.length} prompts copied!`);
                    } catch (err) {
                        console.error('Failed to copy all prompts:', err);
                        this.showToast('Failed to copy');
                    }
                },

                scrollToIssue(issueId) {
                    const element = document.getElementById('issue-' + issueId);
                    if (element) {
                        // Expand the issue
                        const issue = this.data.issues.find(i => i.id === issueId);
                        if (issue) {
                            issue.expanded = true;
                        }

                        // Scroll with offset for fixed header
                        element.scrollIntoView({ behavior: 'smooth', block: 'start' });

                        // Add highlight animation
                        element.classList.add('highlighted');
                        setTimeout(() => {
                            element.classList.remove('highlighted');
                        }, 1500);
                    }
                },

                showToast(message) {
                    this.toast.message = message;
                    this.toast.visible = true;
                    setTimeout(() => {
                        this.toast.visible = false;
                    }, 2500);
                }
            }
        };
    </script>

    <!-- Alpine loads after reportApp is defined so file:// reports initialize reliably. -->
    <script src="https://unpkg.com/@alpinejs/collapse"></script>
    <script src="https://unpkg.com/alpinejs"></script>
</body>
</html>
"""
    return template.replace("__REPORT_DATA__", json_data).replace("__REPORT_PROJECT_NAME__", project_name)


def generate_html_report(
    analyze_path: Path,
    output_path: Path,
    manifest_path: Path | None = None,
    validation_path: Path | None = None,
) -> str:
    analyzer_report = _read_json(analyze_path)
    validation_report = _read_json(validation_path) if validation_path and validation_path.exists() else None
    if _looks_like_validation_report(analyzer_report):
        validation_report = analyzer_report
        paired_path = validation_report.get("input_report") or validation_report.get("validates")
        if isinstance(paired_path, str) and paired_path:
            candidate = Path(paired_path)
            if not candidate.is_absolute():
                candidate = analyze_path.parent / candidate
            if candidate.exists():
                analyzer_report = _read_json(candidate)
            else:
                analyzer_report = {}
        else:
            analyzer_report = {}
    manifest = _read_json(manifest_path) if manifest_path and manifest_path.exists() else None
    data = build_report_data(analyzer_report, manifest, validation_report)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_html(data), encoding="utf-8")
    return str(output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an EvenBetter HTML issue report.")
    parser.add_argument(
        "--analyze",
        required=True,
        type=Path,
        help="Path to .evenbetter/analyze-{N}.json or a legacy evenbetter-validate-{N}.json",
    )
    parser.add_argument("--output", required=True, type=Path, help="Path to write .evenbetter/evenbetter-validate-{N}.html")
    parser.add_argument("--manifest", type=Path, help="Optional path to .evenbetter/manifest.json")
    parser.add_argument("--validation", type=Path, help="Optional legacy .evenbetter/evenbetter-validate-{N}.json")
    args = parser.parse_args()

    output = generate_html_report(args.analyze, args.output, args.manifest, args.validation)
    print(json.dumps({"html_report": output}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
