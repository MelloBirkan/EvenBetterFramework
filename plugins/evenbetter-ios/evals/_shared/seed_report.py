#!/usr/bin/env python3
"""Seed .evenbetter/plant-care/evenbetter-analyze-report.html in an eval workspace.

Usage: python3 seed_report.py analyzed|validated WORKSPACE

The findings come from plantcare-findings.json next to this file: the 25 findings
of a validated PlantCare audit. The analyzed seed adds two planted false positives
(EB-031 and EB-032, both on correct code in AddPlantView.swift) that
evenbetter-validate should remove. The report is rendered and checked with the
plugin's own scripts/evenbetter_report.py, so a seed that no longer meets the
current report contract fails the scaffold instead of reaching the agent.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent.parent
HELPER = PLUGIN / "scripts" / "evenbetter_report.py"
INDEX = PLUGIN / "corpus" / "index.json"
SEVERITIES = ("critical", "high", "medium", "low")


def source_url(clause):
    for entry in json.loads(INDEX.read_text(encoding="utf-8")):
        if entry.get("clause_id") == clause:
            return entry["source_url"]
    sys.exit(f"seed: {clause} is not in {INDEX}")


def finding(fid, clause, severity, line, snippet, title, description, minimal, recommended):
    path = "PlantCare/Views/AddPlantView.swift"
    return {
        "id": fid,
        "clause_id": clause,
        "related_clause_ids": [],
        "title": title,
        "description": description,
        "severity": severity,
        "wcag_criteria": "1.1.1",
        "wcag_level": "A",
        "hig_reference_url": source_url(clause),
        "file_path": path,
        "line_number": line,
        "code_snippet": snippet,
        "minimal_fix": minimal,
        "recommended_fix": recommended,
        "ai_fix_prompt": (f"Edit {{{{PROJECT_PATH}}}}/{path} line {line} ({fid}).\n"
                          f"Clause {clause}: {title}. {description}\n\n"
                          f"Original:\n```swift\n{snippet}\n```\n\n"
                          f"Replace with:\n```swift\n{recommended}\n```"),
        "language": "swift",
        "repair": {"status": "pending", "path": "", "owner": "", "applied_at": "",
                   "changed_files": [], "note": ""},
    }


def planted_false_positives():
    return [
        finding("EB-031", "A11Y-UI-001", "critical", 17,
                '                Image(systemName: "checkmark")',
                "Label the save checkmark for VoiceOver",
                "The save control in AddPlantView shows only a checkmark symbol with no "
                "accessibilityLabel, so VoiceOver reads a generic symbol name.",
                'Image(systemName: "checkmark")\n    .accessibilityLabel("Save plant")',
                'Label("Save plant", systemImage: "checkmark")\n    .labelStyle(.iconOnly)'),
        finding("EB-032", "A11Y-UI-002", "medium", 21,
                '            Image("divider-flourish")',
                "Hide the divider flourish from VoiceOver",
                "The divider flourish in AddPlantView is decorative but VoiceOver still "
                "focuses it and reads its asset name.",
                'Image("divider-flourish")\n    .accessibilityHidden(true)',
                'Image(decorative: "divider-flourish")'),
    ]


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("analyzed", "validated"):
        sys.exit(__doc__)
    state, workspace = sys.argv[1], os.path.abspath(sys.argv[2])
    data = json.loads((HERE / "plantcare-findings.json").read_text(encoding="utf-8"))

    if state == "analyzed":
        data["issues"] += planted_false_positives()
        data["workflow"] = {"state": "analyzed", "validated_at": "",
                            "validation": {"kept": 0, "adjusted": 0, "removed": 0},
                            "repaired_at": "",
                            "repair": {"applied": 0, "deferred": 0, "skipped": 0, "failed": 0}}

    # A seed is a fresh scan as far as runtime goes: render adds the untested block.
    for issue in data["issues"]:
        issue.pop("runtime", None)
    issues = data["issues"]
    data["summary"] = {"total": len(issues),
                       **{s: sum(1 for i in issues if i["severity"] == s) for s in SEVERITIES}}

    text = json.dumps(data, indent=2, ensure_ascii=False).replace("{{PROJECT_PATH}}", workspace)
    report = Path(workspace) / ".evenbetter" / "plant-care" / "evenbetter-analyze-report.html"
    with tempfile.TemporaryDirectory() as tmp:
        data_path = Path(tmp) / "data.json"
        data_path.write_text(text, encoding="utf-8")
        for args in (["render", str(data_path), str(report), "--no-archive"],
                     ["check", str(report), "--state", state]):
            run = subprocess.run([sys.executable, str(HELPER), *args],
                                 capture_output=True, text=True)
            if run.returncode != 0:
                sys.exit(f"seed: evenbetter_report.py {args[0]} failed\n{run.stdout}{run.stderr}")
    print(f"seeded {report} ({state}, {len(issues)} findings)")


if __name__ == "__main__":
    main()
