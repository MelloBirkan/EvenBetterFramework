#!/usr/bin/env python3
"""Generate an interactive EvenBetter validation HTML report.

The report is a derived artifact: it does not change the analyzer or validator
JSON contracts. It flattens analyzer findings, joins validator decisions where
available, and writes one standalone HTML file for browser review.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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


def _validation_index(validation_report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
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
            original = item.get("original_violation") or {}
            violation_id = original.get("id")
            if not isinstance(violation_id, str) or not violation_id:
                continue
            by_id[violation_id] = {
                "decision": item.get("decision", fallback_decisions[bucket]),
                "confidence": item.get("confidence"),
                "reasoning": item.get("reasoning", ""),
                "corrected_severity": item.get("corrected_severity") or item.get("downgraded_severity"),
                "drop_reason": item.get("drop_reason"),
                "source_context": item.get("source_context"),
                "corpus_clause": item.get("corpus_clause"),
                "url_verification": item.get("url_verification"),
                "severity_assessment": item.get("severity_assessment"),
                "fix_prompt_assessment": item.get("fix_prompt_assessment"),
                "supporting_links": item.get("supporting_links") or [],
            }
    return by_id


def _add_supporting_link(
    links: list[dict[str, str]],
    seen: set[str],
    *,
    label: Any,
    url: Any,
    source: str,
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
            "label": str(label or normalized_url),
            "url": normalized_url,
            "source": source,
            "reason": reason,
        }
    )


def _supporting_links(
    violation: dict[str, Any],
    validation: dict[str, Any] | None,
) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    seen: set[str] = set()

    guideline = violation.get("guideline_reference") or {}
    if isinstance(guideline, dict):
        _add_supporting_link(
            links,
            seen,
            label=guideline.get("label") or "Guideline reference",
            url=guideline.get("url"),
            source="guideline",
            reason="Analyzer guideline reference verified by validation when applicable.",
        )

    if validation:
        corpus = validation.get("corpus_clause") or {}
        if isinstance(corpus, dict):
            _add_supporting_link(
                links,
                seen,
                label=corpus.get("heading") or corpus.get("clause_id") or "Corpus source",
                url=corpus.get("source_url"),
                source="corpus",
                reason="Corpus source used by the validator.",
            )

        for link in validation.get("supporting_links") or []:
            if not isinstance(link, dict):
                continue
            source = str(link.get("source") or "web")
            if source not in {"guideline", "corpus", "web"}:
                source = "web"
            _add_supporting_link(
                links,
                seen,
                label=link.get("label") or "Supporting evidence",
                url=link.get("url"),
                source=source,
                reason=str(link.get("reason") or "Additional validator evidence."),
            )

    return links


def _flatten_issues(
    analyzer_report: dict[str, Any],
    validation_report: dict[str, Any],
) -> list[dict[str, Any]]:
    validations = _validation_index(validation_report)
    issues: list[dict[str, Any]] = []

    for file_entry in analyzer_report.get("files", []) or []:
        if not isinstance(file_entry, dict):
            continue
        for violation in file_entry.get("violations", []) or []:
            if not isinstance(violation, dict):
                continue

            violation_id = str(violation.get("id", ""))
            file_path = str(violation.get("file_path") or file_entry.get("file_path") or "")
            validation = validations.get(violation_id)
            fix_code = violation.get("fix_code")
            fix_description = violation.get("fix_description", "")
            supporting_links = _supporting_links(violation, validation)

            issues.append(
                {
                    "id": violation_id,
                    "title": violation.get("summary", "Untitled finding"),
                    "description": (
                        violation.get("why_fix")
                        or (validation or {}).get("reasoning")
                        or fix_description
                        or "No additional description was provided."
                    ),
                    "severity": violation.get("severity", "info"),
                    "dimension": violation.get("dimension", ""),
                    "domain": violation.get("domain", ""),
                    "wcag_criteria": violation.get("rule_id", ""),
                    "wcag_level": violation.get("dimension", ""),
                    "guideline_reference": violation.get("guideline_reference") or {},
                    "file_path": file_path,
                    "line_number": violation.get("line_number"),
                    "code_snippet": violation.get("code_snippet", ""),
                    "recommended_fix": fix_code or fix_description,
                    "fix_description": fix_description,
                    "ai_fix_prompt": violation.get("ai_fix_prompt", ""),
                    "language": _language_for_file(file_path),
                    "state": violation.get("state") or {},
                    "supporting_links": supporting_links,
                    "validation": validation
                    or {
                        "decision": "not_validated",
                        "confidence": None,
                        "reasoning": "This finding was not included in the validation report.",
                    },
                }
            )

    return issues


def _severity_counts(issues: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"error": 0, "warning": 0, "info": 0}
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
    validation_report: dict[str, Any],
    manifest: dict[str, Any] | None,
) -> dict[str, Any]:
    issues = _flatten_issues(analyzer_report, validation_report)
    severity_counts = _severity_counts(issues)
    analyzer_run = validation_report.get("analyzer_run") or (analyzer_report.get("run") or {}).get("number")
    manifest_run = _manifest_run(manifest, analyzer_run if isinstance(analyzer_run, int) else None)
    project_path = str(analyzer_report.get("project_path") or validation_report.get("project_path") or "")
    validation_counts = {
        "kept": int(validation_report.get("kept_count") or 0),
        "severity_adjusted": int(
            validation_report.get("severity_adjusted_count")
            or validation_report.get("downgraded_count")
            or 0
        ),
        "dropped": int(validation_report.get("dropped_count") or 0),
    }
    validation_counts["not_validated"] = max(
        len(issues)
        - validation_counts["kept"]
        - validation_counts["severity_adjusted"]
        - validation_counts["dropped"],
        0,
    )

    created_at = validation_report.get("createdAt") or (analyzer_report.get("run") or {}).get("createdAt")
    if not created_at:
        created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "project_name": _project_name(project_path),
        "project_path": project_path,
        "framework": analyzer_report.get("platform", "swiftui"),
        "wcag_level": analyzer_report.get("guidelines", "Apple Human Interface Guidelines"),
        "scan_date": created_at,
        "summary": {
            "total": len(issues),
            "error": severity_counts["error"],
            "warning": severity_counts["warning"],
            "info": severity_counts["info"],
            **validation_counts,
        },
        "issues": issues,
        "scan_context": {
            "analyzer_run": analyzer_run,
            "analyzer_status": (analyzer_report.get("run") or {}).get("status"),
            "manifest_status": (manifest_run or {}).get("status"),
            "validated": (manifest_run or {}).get("validated"),
            "platform": analyzer_report.get("platform", "swiftui"),
            "guidelines": analyzer_report.get("guidelines", "Apple Human Interface Guidelines"),
            "total_files": analyzer_report.get("total_files", 0),
            "overall_score": analyzer_report.get("overall_score"),
            "ui_score": analyzer_report.get("ui_score"),
            "ux_score": analyzer_report.get("ux_score"),
            "a11y_score": analyzer_report.get("a11y_score"),
            "domain_summaries": analyzer_report.get("domain_summaries", []),
            "executive_summary": analyzer_report.get("executive_summary", ""),
            "confidence_threshold": validation_report.get("confidence_threshold"),
            "retention_rate": validation_report.get("retention_rate"),
            "mean_confidence": validation_report.get("mean_confidence"),
            "time_per_finding_ms": validation_report.get("time_per_finding_ms"),
            "validates": validation_report.get("validates"),
        },
    }


def build_html(data: dict[str, Any]) -> str:
    json_data = _safe_script_json(data)
    return f"""<!DOCTYPE html>
<html lang="en" x-data="reportApp()" x-init="initApp()" :class="{{{{ 'dark': darkMode }}}}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EvenBetter Validation Report | {{{{ data.project_name }}}}</title>

    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <script defer src="https://unpkg.com/@alpinejs/collapse"></script>
    <script defer src="https://unpkg.com/alpinejs"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css" class="dark-syntax">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-light.min.css" class="light-syntax" disabled>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

    <style>
        :root {{
            --font-display: 'Syne', sans-serif;
            --font-body: 'DM Sans', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
            --accent: #0DD3CF;
            --accent-hover: #0BEAE5;
            --accent-muted: rgba(13, 211, 207, 0.15);
            --error: #FF4757;
            --error-bg: rgba(255, 71, 87, 0.12);
            --warning: #FFA502;
            --warning-bg: rgba(255, 165, 2, 0.12);
            --info: #3B82F6;
            --info-bg: rgba(59, 130, 246, 0.12);
            --kept: #2ED573;
            --kept-bg: rgba(46, 213, 115, 0.12);
            --dropped: #A855F7;
            --dropped-bg: rgba(168, 85, 247, 0.12);
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
        }}
        .dark {{
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
        }}
        [x-cloak] {{ display: none !important; }}
        * {{ box-sizing: border-box; }}
        body {{
            font-family: var(--font-body);
            background: var(--bg-primary);
            color: var(--text-primary);
            transition: background-color 0.3s ease, color 0.3s ease;
        }}
        body::before {{
            content: '';
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 9999;
            opacity: var(--grain-opacity);
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
        }}
        .font-display {{ font-family: var(--font-display); }}
        .font-mono {{ font-family: var(--font-mono); }}
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: var(--bg-secondary); }}
        ::-webkit-scrollbar-thumb {{ background: var(--text-muted); border-radius: 4px; }}
        .glass-card {{
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border);
            transition: all 0.2s ease;
        }}
        .glass-card:hover {{ background: var(--bg-card-hover); border-color: var(--border-strong); }}
        .geo-accent {{
            position: absolute;
            width: 400px;
            height: 400px;
            border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%;
            background: linear-gradient(135deg, var(--accent) 0%, transparent 60%);
            opacity: 0.08;
            filter: blur(60px);
            pointer-events: none;
        }}
        .hljs {{ background: transparent !important; padding: 0 !important; }}
        .copy-btn {{ transition: all 0.15s ease; }}
        .copy-btn:active {{ transform: scale(0.92); }}
        .severity-border {{ position: relative; }}
        .severity-border::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            border-radius: 4px 0 0 4px;
            transition: width 0.2s ease;
        }}
        .severity-border:hover::before {{ width: 6px; }}
        .severity-error::before {{ background: var(--error); }}
        .severity-warning::before {{ background: var(--warning); }}
        .severity-info::before {{ background: var(--info); }}
        .theme-toggle {{
            position: relative;
            width: 56px;
            height: 28px;
            border-radius: 14px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-strong);
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .theme-toggle::after {{
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
        }}
        .dark .theme-toggle::after {{ transform: translateX(28px); }}
        .filter-chip {{ transition: all 0.15s ease; }}
        .filter-chip.active {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px var(--shadow);
        }}
        .prompt-row {{
            transition: all 0.15s ease;
            border-left: 3px solid transparent;
        }}
        .prompt-row:hover {{
            background: var(--bg-card-hover);
            border-left-color: var(--accent);
        }}
        .prompt-id {{ cursor: pointer; transition: color 0.15s ease; }}
        .prompt-id:hover {{ color: var(--accent-hover); text-decoration: underline; }}
        .issue-card-target {{ scroll-margin-top: 100px; }}
        .issue-card-target.highlighted {{ animation: highlight-pulse 1.5s ease-out; }}
        @keyframes highlight-pulse {{
            0% {{ box-shadow: 0 0 0 4px var(--accent); }}
            100% {{ box-shadow: 0 0 0 0 transparent; }}
        }}
    </style>
</head>
<body class="min-h-screen antialiased selection:bg-[var(--accent)] selection:text-black">
    <div class="geo-accent" style="top: -200px; right: -100px;"></div>
    <div class="geo-accent" style="bottom: -200px; left: -100px;"></div>

    <header class="fixed top-0 w-full z-50 glass-card border-b" style="border-color: var(--border);">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <div class="flex items-center gap-4">
                    <div class="flex items-center justify-center w-10 h-10 rounded-xl" style="background: linear-gradient(135deg, var(--accent) 0%, #06B6D4 100%); box-shadow: 0 4px 16px rgba(13, 211, 207, 0.3);">
                        <i data-lucide="scan-eye" class="text-black w-5 h-5"></i>
                    </div>
                    <div>
                        <h1 class="font-display font-bold text-lg tracking-tight" style="color: var(--text-primary);">
                            EVENBETTER
                            <span class="font-mono text-xs font-normal ml-2 px-2 py-0.5 rounded" style="background: var(--accent-muted); color: var(--accent);">VALIDATE</span>
                        </h1>
                        <p class="text-xs font-mono" style="color: var(--text-muted);" x-text="data.scan_date"></p>
                    </div>
                </div>
                <div class="flex items-center gap-6">
                    <div class="hidden md:flex items-center gap-6 text-sm">
                        <div class="text-right">
                            <p class="text-[10px] font-mono uppercase tracking-wider" style="color: var(--text-muted);">Project</p>
                            <p class="font-medium truncate max-w-[150px]" style="color: var(--text-primary);" x-text="data.project_name"></p>
                        </div>
                        <div class="w-px h-8" style="background: var(--border);"></div>
                        <div class="text-right">
                            <p class="text-[10px] font-mono uppercase tracking-wider" style="color: var(--text-muted);">Platform</p>
                            <p class="font-medium" style="color: var(--accent);" x-text="data.framework"></p>
                        </div>
                    </div>
                    <button @click="toggleTheme()" class="theme-toggle" :aria-label="darkMode ? 'Switch to light mode' : 'Switch to dark mode'">
                        <span class="sr-only" x-text="darkMode ? 'Dark mode' : 'Light mode'"></span>
                    </button>
                </div>
            </div>
        </div>
    </header>

    <main class="pt-24 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto relative">
        <section class="mb-8">
            <div class="glass-card rounded-2xl p-6 mb-4 relative overflow-hidden">
                <div class="absolute top-0 right-0 w-32 h-32 rounded-full blur-3xl" style="background: var(--accent); opacity: 0.1;"></div>
                <div class="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
                    <div>
                        <p class="text-xs font-mono uppercase tracking-widest mb-2" style="color: var(--text-muted);">Total Analyzer Issues</p>
                        <h2 class="font-display font-extrabold text-6xl sm:text-7xl tracking-tight" style="color: var(--text-primary);" x-text="data.summary.total"></h2>
                    </div>
                    <p class="font-mono text-sm max-w-xs" style="color: var(--text-secondary);">
                        All analyzer findings are shown. High-severity findings include validator decisions where available.
                    </p>
                </div>
            </div>
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
                <button @click="toggleFilter('error')" class="filter-chip glass-card rounded-xl p-4 text-left severity-border severity-error" :class="{{{{ 'active': filters.severity.includes('error') }}}}">
                    <div class="flex items-center justify-between mb-3">
                        <i data-lucide="alert-octagon" class="w-5 h-5" style="color: var(--error);"></i>
                        <span x-show="filters.severity.includes('error')" class="w-2 h-2 rounded-full" style="background: var(--error);"></span>
                    </div>
                    <p class="font-display font-bold text-3xl" style="color: var(--text-primary);" x-text="data.summary.error"></p>
                    <p class="text-xs font-mono uppercase tracking-wider mt-1" style="color: var(--error);">Error</p>
                </button>
                <button @click="toggleFilter('warning')" class="filter-chip glass-card rounded-xl p-4 text-left severity-border severity-warning" :class="{{{{ 'active': filters.severity.includes('warning') }}}}">
                    <div class="flex items-center justify-between mb-3">
                        <i data-lucide="alert-triangle" class="w-5 h-5" style="color: var(--warning);"></i>
                        <span x-show="filters.severity.includes('warning')" class="w-2 h-2 rounded-full" style="background: var(--warning);"></span>
                    </div>
                    <p class="font-display font-bold text-3xl" style="color: var(--text-primary);" x-text="data.summary.warning"></p>
                    <p class="text-xs font-mono uppercase tracking-wider mt-1" style="color: var(--warning);">Warning</p>
                </button>
                <button @click="toggleFilter('info')" class="filter-chip glass-card rounded-xl p-4 text-left severity-border severity-info" :class="{{{{ 'active': filters.severity.includes('info') }}}}">
                    <div class="flex items-center justify-between mb-3">
                        <i data-lucide="info" class="w-5 h-5" style="color: var(--info);"></i>
                        <span x-show="filters.severity.includes('info')" class="w-2 h-2 rounded-full" style="background: var(--info);"></span>
                    </div>
                    <p class="font-display font-bold text-3xl" style="color: var(--text-primary);" x-text="data.summary.info"></p>
                    <p class="text-xs font-mono uppercase tracking-wider mt-1" style="color: var(--info);">Info</p>
                </button>
                <div class="glass-card rounded-xl p-4 text-left">
                    <div class="flex items-center justify-between mb-3">
                        <i data-lucide="shield-check" class="w-5 h-5" style="color: var(--kept);"></i>
                    </div>
                    <p class="font-display font-bold text-3xl" style="color: var(--text-primary);" x-text="data.summary.kept"></p>
                    <p class="text-xs font-mono uppercase tracking-wider mt-1" style="color: var(--kept);">Validated Kept</p>
                </div>
            </div>
        </section>

        <section class="glass-card rounded-xl mb-6 overflow-hidden" x-data="{{{{ contextExpanded: false }}}}">
            <div @click="contextExpanded = !contextExpanded" class="w-full p-4 flex items-center justify-between cursor-pointer select-none hover:opacity-90">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 flex items-center justify-center rounded-lg" style="background: var(--accent-muted);">
                        <i data-lucide="flask-conical" class="w-4 h-4" style="color: var(--accent);"></i>
                    </div>
                    <div>
                        <h3 class="font-display font-bold text-sm" style="color: var(--text-primary);">Scan Context</h3>
                        <p class="text-xs font-mono" style="color: var(--text-muted);">Run metadata, scores, and validation statistics</p>
                    </div>
                </div>
                <button class="w-8 h-8 flex items-center justify-center rounded-lg" style="background: var(--bg-tertiary);">
                    <i data-lucide="chevron-down" class="w-4 h-4 transition-transform duration-200" :class="{{{{ 'rotate-180': contextExpanded }}}}" style="color: var(--text-muted);"></i>
                </button>
            </div>
            <div x-show="contextExpanded" x-collapse x-cloak>
                <div class="px-4 pb-4 border-t" style="border-color: var(--border);">
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-4">
                        <template x-for="item in contextCards()" :key="item.label">
                            <div class="p-3 rounded-lg" style="background: var(--bg-tertiary);">
                                <div class="flex items-center gap-2 mb-2">
                                    <i :data-lucide="item.icon" class="w-4 h-4" style="color: var(--accent);"></i>
                                    <span class="text-xs font-mono uppercase tracking-wider" style="color: var(--text-muted);" x-text="item.label"></span>
                                </div>
                                <p class="font-display font-bold text-xl" style="color: var(--text-primary);" x-text="item.value"></p>
                            </div>
                        </template>
                    </div>
                    <p class="mt-4 text-sm leading-relaxed" style="color: var(--text-secondary);" x-text="data.scan_context.executive_summary"></p>
                </div>
            </div>
        </section>

        <section class="glass-card rounded-xl p-4 mb-6 flex flex-col sm:flex-row gap-4 items-center justify-between">
            <div class="relative w-full sm:w-96">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <i data-lucide="search" class="h-4 w-4" style="color: var(--text-muted);"></i>
                </div>
                <input type="text" x-model="searchQuery" class="block w-full pl-10 pr-3 py-2.5 rounded-lg text-sm font-mono transition-all focus:outline-none focus:ring-2" style="background: var(--bg-tertiary); border: 1px solid var(--border); color: var(--text-primary); --tw-ring-color: var(--accent);" placeholder="Search files, rules, findings...">
            </div>
            <div class="flex items-center gap-3 text-sm flex-wrap justify-center sm:justify-end">
                <span class="font-mono text-xs" style="color: var(--text-muted);">Filters:</span>
                <template x-if="filters.severity.length === 0 && !searchQuery">
                    <span class="px-2 py-1 rounded text-xs font-mono" style="background: var(--bg-tertiary); color: var(--text-secondary);">All issues</span>
                </template>
                <template x-for="filter in filters.severity" :key="filter">
                    <span class="px-2 py-1 rounded text-xs font-bold uppercase tracking-wider" :style="getSeverityStyle(filter)" x-text="filter"></span>
                </template>
                <button @click="resetFilters()" x-show="filters.severity.length > 0 || searchQuery" class="flex items-center gap-1 text-xs font-mono hover:opacity-80 transition-opacity" style="color: var(--accent);">
                    <i data-lucide="x" class="w-3 h-3"></i>
                    Clear
                </button>
            </div>
        </section>

        <section class="glass-card rounded-xl mb-6 overflow-hidden" x-data="{{{{ promptsExpanded: false }}}}">
            <div class="w-full p-5 flex items-center justify-between select-none" style="background: var(--accent-muted);">
                <div @click="promptsExpanded = !promptsExpanded" class="flex items-center gap-4 cursor-pointer flex-1">
                    <div class="w-10 h-10 flex items-center justify-center rounded-xl" style="background: var(--accent); opacity: 0.9; box-shadow: 0 2px 8px rgba(13, 211, 207, 0.2);">
                        <i data-lucide="sparkles" class="w-5 h-5 text-black"></i>
                    </div>
                    <div class="text-left">
                        <h3 class="font-display font-bold text-base" style="color: var(--text-primary);">AI Agent Prompts Quick Reference</h3>
                        <p class="text-xs font-mono mt-0.5" style="color: var(--text-muted);">
                            <span x-text="issuesWithPrompts().length"></span> prompts ready to copy
                        </p>
                    </div>
                </div>
                <div class="flex items-center gap-4">
                    <button @click="copyAllPrompts()" class="copy-btn flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all hover:opacity-90 hover:translate-y-[-1px] shadow-sm" style="background: var(--accent); color: black;">
                        <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                        COPY ALL
                    </button>
                    <button @click="promptsExpanded = !promptsExpanded" class="w-9 h-9 flex items-center justify-center rounded-lg transition-colors hover:bg-black/5" style="background: var(--bg-tertiary);">
                        <i data-lucide="chevron-down" class="w-5 h-5 transition-transform duration-200" :class="{{{{ 'rotate-180': promptsExpanded }}}}" style="color: var(--text-muted);"></i>
                    </button>
                </div>
            </div>
            <div x-show="promptsExpanded" x-collapse x-cloak>
                <div class="border-t max-h-96 overflow-y-auto" style="border-color: var(--border);">
                    <template x-for="issue in issuesWithPrompts()" :key="issue.id">
                        <div class="prompt-row p-3 border-b flex items-start gap-3" style="border-color: var(--border);">
                            <button @click="scrollToIssue(issue.id)" class="prompt-id flex-shrink-0 px-2 py-0.5 rounded text-[10px] font-mono font-bold" style="background: var(--bg-tertiary); color: var(--accent);" :title="'Jump to issue ' + issue.id">
                                #<span x-text="shortId(issue.id)"></span>
                            </button>
                            <div class="flex-1 min-w-0">
                                <div class="flex items-center gap-2 mb-1">
                                    <span class="text-xs font-medium truncate" style="color: var(--text-primary);" x-text="truncate(issue.title, 56)"></span>
                                    <span class="flex-shrink-0 px-1.5 py-0.5 rounded text-[9px] font-bold uppercase" :style="getSeverityStyle(issue.severity)" x-text="issue.severity"></span>
                                </div>
                                <p class="text-xs font-mono truncate" style="color: var(--text-muted);" x-text="truncate(issue.ai_fix_prompt, 90)"></p>
                            </div>
                            <button @click="copyText(issue.ai_fix_prompt, 'Prompt copied!')" class="copy-btn flex-shrink-0 p-1.5 rounded-lg transition-colors hover:opacity-80" style="background: var(--bg-tertiary); color: var(--accent);" title="Copy prompt">
                                <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                            </button>
                        </div>
                    </template>
                </div>
            </div>
        </section>

        <section class="space-y-4">
            <div x-show="filteredIssues.length === 0" x-cloak class="text-center py-20">
                <div class="inline-flex items-center justify-center w-20 h-20 rounded-2xl mb-4" style="background: var(--bg-tertiary);">
                    <i data-lucide="search-x" class="w-10 h-10" style="color: var(--text-muted);"></i>
                </div>
                <h3 class="font-display font-bold text-xl" style="color: var(--text-primary);">No matching issues</h3>
                <p class="mt-2 max-w-sm mx-auto" style="color: var(--text-muted);">Try adjusting your search or filters.</p>
            </div>

            <template x-for="issue in filteredIssues" :key="issue.id">
                <article :id="'issue-' + issue.id" class="glass-card rounded-xl overflow-hidden severity-border transition-all duration-200 issue-card-target" :class="'severity-' + issue.severity">
                    <div class="p-5 cursor-pointer select-none" @click="issue.expanded = !issue.expanded">
                        <div class="flex items-start justify-between gap-4">
                            <div class="flex-1 min-w-0">
                                <div class="flex flex-wrap items-center gap-2 mb-2">
                                    <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold" style="background: var(--accent-muted); color: var(--accent);">#<span x-text="shortId(issue.id)"></span></span>
                                    <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider" :style="getSeverityStyle(issue.severity)">
                                        <i :data-lucide="getSeverityIcon(issue.severity)" class="w-3 h-3"></i>
                                        <span x-text="issue.severity"></span>
                                    </span>
                                    <span class="px-2 py-0.5 rounded text-[10px] font-mono uppercase tracking-wider" style="background: var(--bg-tertiary); color: var(--text-secondary);">
                                        <span x-text="issue.wcag_criteria"></span>
                                        <span class="opacity-60">(<span x-text="issue.dimension"></span>)</span>
                                    </span>
                                    <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider" :style="getDecisionStyle(issue.validation.decision)" x-text="decisionLabel(issue.validation)"></span>
                                </div>
                                <h3 class="font-display font-bold text-lg leading-tight mb-1" style="color: var(--text-primary);" x-text="issue.title"></h3>
                                <p class="flex items-center gap-1 text-xs font-mono truncate" style="color: var(--text-muted);">
                                    <i data-lucide="file-code" class="w-3 h-3 flex-shrink-0"></i>
                                    <span x-text="issue.file_path"></span>:<span x-text="issue.line_number"></span>
                                </p>
                            </div>
                            <div class="flex items-center gap-2 flex-shrink-0">
                                <button x-show="issue.ai_fix_prompt" @click.stop="copyText(issue.ai_fix_prompt, 'AI prompt copied!')" class="copy-btn p-2 rounded-lg transition-colors" style="background: var(--accent-muted); color: var(--accent);" title="Copy AI Fix Prompt">
                                    <i data-lucide="sparkles" class="w-4 h-4"></i>
                                </button>
                                <div class="w-8 h-8 flex items-center justify-center rounded-lg" style="background: var(--bg-tertiary);">
                                    <i data-lucide="chevron-down" class="w-4 h-4 transition-transform duration-200" :class="{{{{ 'rotate-180': issue.expanded }}}}" style="color: var(--text-muted);"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div x-show="issue.expanded" x-collapse x-cloak>
                        <div class="px-5 pb-5 pt-0 border-t" style="border-color: var(--border);">
                            <div class="mt-4 text-sm leading-relaxed" style="color: var(--text-secondary);">
                                <p x-text="issue.description"></p>
                            </div>
                            <div class="mt-4 p-4 rounded-lg" style="background: var(--bg-tertiary); border: 1px solid var(--border);">
                                <div class="flex items-center gap-2 mb-2">
                                    <i data-lucide="shield-check" class="w-4 h-4" style="color: var(--accent);"></i>
                                    <span class="text-xs font-mono uppercase tracking-wider" style="color: var(--accent);">Validation</span>
                                </div>
                                <p class="text-sm" style="color: var(--text-secondary);" x-text="issue.validation.reasoning"></p>
                                <p class="mt-2 text-xs font-mono" style="color: var(--text-muted);" x-show="issue.validation.confidence !== null && issue.validation.confidence !== undefined">
                                    Confidence: <span x-text="Math.round(issue.validation.confidence * 100) + '%'"></span>
                                </p>
                                <div class="mt-3" x-show="issue.supporting_links && issue.supporting_links.length">
                                    <div class="flex items-center gap-2 mb-2">
                                        <i data-lucide="link" class="w-3 h-3" style="color: var(--accent);"></i>
                                        <span class="text-xs font-mono uppercase tracking-wider" style="color: var(--text-muted);">Evidence Links</span>
                                    </div>
                                    <div class="flex flex-wrap gap-2">
                                        <template x-for="link in issue.supporting_links" :key="link.url">
                                            <a :href="link.url" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-mono transition-colors hover:opacity-80" style="background: var(--accent-muted); color: var(--accent);" :title="link.reason || link.url">
                                                <i data-lucide="external-link" class="w-3 h-3"></i>
                                                <span x-text="truncate(link.label, 44)"></span>
                                            </a>
                                        </template>
                                    </div>
                                </div>
                            </div>
                            <div class="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-4">
                                <div class="rounded-lg overflow-hidden" style="background: var(--bg-tertiary); border: 1px solid var(--error); border-opacity: 0.3;">
                                    <div class="px-3 py-2 flex items-center justify-between" style="background: var(--error-bg); border-bottom: 1px solid var(--error); border-opacity: 0.2;">
                                        <span class="flex items-center gap-2 text-xs font-mono uppercase tracking-wider" style="color: var(--error);">
                                            <i data-lucide="x-circle" class="w-3 h-3"></i>
                                            Current Code
                                        </span>
                                        <button @click="copyText(issue.code_snippet, 'Code copied!')" class="copy-btn p-1 rounded transition-colors hover:opacity-80" style="color: var(--text-muted);" title="Copy code">
                                            <i data-lucide="copy" class="w-3 h-3"></i>
                                        </button>
                                    </div>
                                    <div class="p-3 overflow-x-auto">
                                        <pre class="text-sm font-mono"><code :class="'language-' + issue.language" x-text="issue.code_snippet"></code></pre>
                                    </div>
                                </div>
                                <div class="rounded-lg overflow-hidden" style="background: var(--bg-tertiary); border: 1px solid var(--kept); border-opacity: 0.3;">
                                    <div class="px-3 py-2 flex items-center justify-between" style="background: var(--kept-bg); border-bottom: 1px solid var(--kept); border-opacity: 0.2;">
                                        <span class="flex items-center gap-2 text-xs font-mono uppercase tracking-wider" style="color: var(--kept);">
                                            <i data-lucide="check-circle" class="w-3 h-3"></i>
                                            Recommended Fix
                                        </span>
                                        <button @click="copyText(issue.recommended_fix, 'Fix copied!')" class="copy-btn p-1 rounded transition-colors hover:opacity-80" style="color: var(--text-muted);" title="Copy fix">
                                            <i data-lucide="copy" class="w-3 h-3"></i>
                                        </button>
                                    </div>
                                    <div class="p-3 overflow-x-auto">
                                        <pre class="text-sm font-mono"><code :class="'language-' + issue.language" x-text="issue.recommended_fix"></code></pre>
                                    </div>
                                </div>
                            </div>
                            <div class="mt-6" x-show="issue.ai_fix_prompt">
                                <div class="rounded-lg overflow-hidden" style="background: var(--bg-tertiary); border: 1px solid var(--accent); border-opacity: 0.3;">
                                    <div class="px-4 py-2 flex items-center justify-between" style="background: var(--accent-muted); border-bottom: 1px solid var(--accent); border-opacity: 0.2;">
                                        <span class="flex items-center gap-2 text-xs font-mono uppercase tracking-wider" style="color: var(--accent);">
                                            <i data-lucide="bot" class="w-3 h-3"></i>
                                            AI Agent Fix Prompt
                                        </span>
                                        <button @click="copyText(issue.ai_fix_prompt, 'AI prompt copied!')" class="copy-btn flex items-center gap-1 px-2 py-1 rounded text-xs font-bold transition-colors hover:opacity-80" style="color: var(--accent);">
                                            <i data-lucide="copy" class="w-3 h-3"></i>
                                            COPY
                                        </button>
                                    </div>
                                    <div class="p-4">
                                        <p class="text-sm font-mono break-words whitespace-pre-wrap" style="color: var(--text-secondary);" x-text="issue.ai_fix_prompt"></p>
                                        <p class="mt-3 text-xs flex items-center gap-1" style="color: var(--text-muted);">
                                            <i data-lucide="lightbulb" class="w-3 h-3"></i>
                                            Paste this into Cursor, Claude Code, Codex, or another coding agent.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </article>
            </template>
        </section>

        <footer class="mt-16 pt-8 border-t text-center" style="border-color: var(--border);">
            <p class="font-mono text-xs" style="color: var(--text-muted);">
                Generated by <span class="font-bold" style="color: var(--accent);">EvenBetter</span> - AI-powered iOS design validation
            </p>
        </footer>
    </main>

    <div class="fixed bottom-6 right-6 z-50" x-show="toast.visible" x-transition:enter="transition ease-out duration-200" x-transition:enter-start="opacity-0 translate-y-4" x-transition:enter-end="opacity-100 translate-y-0" x-transition:leave="transition ease-in duration-150" x-transition:leave-start="opacity-100 translate-y-0" x-transition:leave-end="opacity-0 translate-y-4" x-cloak>
        <div class="flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg" style="background: var(--bg-secondary); border: 1px solid var(--accent); box-shadow: 0 4px 24px var(--shadow);">
            <div class="w-6 h-6 rounded-full flex items-center justify-center" style="background: var(--accent-muted);">
                <i data-lucide="check" class="w-3 h-3" style="color: var(--accent);"></i>
            </div>
            <span class="font-mono text-sm" style="color: var(--text-primary);" x-text="toast.message"></span>
        </div>
    </div>

    <script>
        const reportData = {json_data};

        function reportApp() {{
            return {{
                data: reportData,
                darkMode: true,
                searchQuery: '',
                filters: {{ severity: [] }},
                toast: {{ visible: false, message: '' }},

                initApp() {{
                    const savedTheme = localStorage.getItem('evenbetter-report-theme');
                    this.darkMode = savedTheme ? savedTheme === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
                    this.data.issues = this.data.issues.map(issue => ({{ ...issue, expanded: false }}));
                    this.$nextTick(() => {{
                        this.initIcons();
                        this.initSyntaxHighlighting();
                        this.updateSyntaxTheme();
                    }});
                    this.$watch('filteredIssues', () => {{
                        this.$nextTick(() => {{
                            this.initIcons();
                            this.initSyntaxHighlighting();
                        }});
                    }});
                    this.$watch('darkMode', () => this.updateSyntaxTheme());
                }},
                initIcons() {{
                    try {{ lucide.createIcons(); }} catch (e) {{ console.error('Lucide icons error:', e); }}
                }},
                initSyntaxHighlighting() {{
                    try {{
                        document.querySelectorAll('pre code').forEach(block => {{
                            block.removeAttribute('data-highlighted');
                            block.classList.remove('hljs');
                            hljs.highlightElement(block);
                        }});
                    }} catch (e) {{ console.error('Highlight.js error:', e); }}
                }},
                updateSyntaxTheme() {{
                    const darkStyle = document.querySelector('.dark-syntax');
                    const lightStyle = document.querySelector('.light-syntax');
                    if (darkStyle && lightStyle) {{
                        darkStyle.disabled = !this.darkMode;
                        lightStyle.disabled = this.darkMode;
                    }}
                }},
                toggleTheme() {{
                    this.darkMode = !this.darkMode;
                    localStorage.setItem('evenbetter-report-theme', this.darkMode ? 'dark' : 'light');
                }},
                get filteredIssues() {{
                    return this.data.issues.filter(issue => {{
                        if (this.filters.severity.length > 0 && !this.filters.severity.includes(issue.severity)) return false;
                        if (!this.searchQuery) return true;
                        const query = this.searchQuery.toLowerCase();
                        return [
                            issue.title,
                            issue.description,
                            issue.file_path,
                            issue.wcag_criteria,
                            issue.domain,
                            issue.validation?.decision || ''
                        ].some(value => String(value || '').toLowerCase().includes(query));
                    }});
                }},
                issuesWithPrompts() {{
                    return this.data.issues.filter(issue => issue.ai_fix_prompt);
                }},
                contextCards() {{
                    const ctx = this.data.scan_context || {{}};
                    return [
                        {{ label: 'Run', value: ctx.analyzer_run || 'unknown', icon: 'hash' }},
                        {{ label: 'Files', value: ctx.total_files ?? 0, icon: 'files' }},
                        {{ label: 'Overall Score', value: ctx.overall_score ?? 'n/a', icon: 'gauge' }},
                        {{ label: 'Retention', value: ctx.retention_rate === null || ctx.retention_rate === undefined ? 'n/a' : Math.round(ctx.retention_rate * 100) + '%', icon: 'shield-check' }}
                    ];
                }},
                toggleFilter(severity) {{
                    const index = this.filters.severity.indexOf(severity);
                    if (index === -1) this.filters.severity.push(severity);
                    else this.filters.severity.splice(index, 1);
                }},
                resetFilters() {{
                    this.filters.severity = [];
                    this.searchQuery = '';
                }},
                getSeverityIcon(severity) {{
                    return {{ error: 'alert-octagon', warning: 'alert-triangle', info: 'info' }}[severity] || 'circle';
                }},
                getSeverityStyle(severity) {{
                    return {{
                        error: 'background: var(--error-bg); color: var(--error); border: 1px solid var(--error);',
                        warning: 'background: var(--warning-bg); color: var(--warning); border: 1px solid var(--warning);',
                        info: 'background: var(--info-bg); color: var(--info); border: 1px solid var(--info);'
                    }}[severity] || 'background: var(--bg-tertiary); color: var(--text-secondary);';
                }},
                getDecisionStyle(decision) {{
                    return {{
                        kept: 'background: var(--kept-bg); color: var(--kept); border: 1px solid var(--kept);',
                        severity_adjusted: 'background: var(--warning-bg); color: var(--warning); border: 1px solid var(--warning);',
                        downgraded: 'background: var(--warning-bg); color: var(--warning); border: 1px solid var(--warning);',
                        dropped: 'background: var(--dropped-bg); color: var(--dropped); border: 1px solid var(--dropped);',
                        not_validated: 'background: var(--bg-tertiary); color: var(--text-muted); border: 1px solid var(--border-strong);'
                    }}[decision] || 'background: var(--bg-tertiary); color: var(--text-secondary);';
                }},
                decisionLabel(validation) {{
                    if (!validation || validation.decision === 'not_validated') return 'not validated';
                    if (validation.decision === 'dropped' && validation.drop_reason) return 'dropped: ' + validation.drop_reason.replaceAll('_', ' ');
                    if (validation.decision === 'severity_adjusted' && validation.corrected_severity) return 'severity adjusted: ' + validation.corrected_severity;
                    return validation.decision;
                }},
                shortId(id) {{
                    return String(id || '').replace(/^v_/, '').slice(0, 8) || 'unknown';
                }},
                truncate(text, length) {{
                    const value = String(text || '');
                    return value.length > length ? value.slice(0, length) + '...' : value;
                }},
                async copyText(text, message) {{
                    try {{
                        await navigator.clipboard.writeText(text || '');
                        this.showToast(message || 'Copied to clipboard!');
                    }} catch (err) {{
                        console.error('Failed to copy:', err);
                        this.showToast('Failed to copy');
                    }}
                }},
                async copyAllPrompts() {{
                    const prompts = this.issuesWithPrompts().map(issue => `[#${{issue.id}}] ${{issue.title}}\\n${{issue.ai_fix_prompt}}`).join('\\n\\n---\\n\\n');
                    await this.copyText(prompts, `${{this.issuesWithPrompts().length}} prompts copied!`);
                }},
                scrollToIssue(issueId) {{
                    const element = document.getElementById('issue-' + issueId);
                    if (!element) return;
                    const issue = this.data.issues.find(item => item.id === issueId);
                    if (issue) issue.expanded = true;
                    element.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                    element.classList.add('highlighted');
                    setTimeout(() => element.classList.remove('highlighted'), 1500);
                }},
                showToast(message) {{
                    this.toast.message = message;
                    this.toast.visible = true;
                    setTimeout(() => {{ this.toast.visible = false; }}, 2500);
                }}
            }};
        }}
    </script>
</body>
</html>
"""


def generate_html_report(
    analyze_path: Path,
    validate_path: Path,
    output_path: Path,
    manifest_path: Path | None = None,
) -> str:
    analyzer_report = _read_json(analyze_path)
    validation_report = _read_json(validate_path)
    manifest = _read_json(manifest_path) if manifest_path and manifest_path.exists() else None
    data = build_report_data(analyzer_report, validation_report, manifest)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_html(data), encoding="utf-8")
    return str(output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an EvenBetter validation HTML report.")
    parser.add_argument("--analyze", required=True, type=Path, help="Path to .evenbetter/analyze-{N}.json")
    parser.add_argument("--validate", required=True, type=Path, help="Path to .evenbetter/evenbetter-validate-{N}.json")
    parser.add_argument("--output", required=True, type=Path, help="Path to write .evenbetter/evenbetter-validate-{N}.html")
    parser.add_argument("--manifest", type=Path, help="Optional path to .evenbetter/manifest.json")
    args = parser.parse_args()

    output = generate_html_report(args.analyze, args.validate, args.output, args.manifest)
    print(json.dumps({"html_report": output}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
