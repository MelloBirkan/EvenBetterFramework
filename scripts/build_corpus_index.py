#!/usr/bin/env python3
"""Build and validate the EvenBetter iOS corpus index."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "evenbetter-ios"
CORPUS_ROOT = PLUGIN_ROOT / "corpus"
IOS_CORPUS_ROOT = CORPUS_ROOT / "ios"
INDEX_PATH = CORPUS_ROOT / "index.json"
SKILL_REFERENCE_ROOTS = (PLUGIN_ROOT / "skills", REPO_ROOT / "skills")

CLAUSE_HEADING_RE = re.compile(
    r"^## (?P<id>[A-Z0-9]+-(?:UI|UX|A11Y)-[0-9]{3}) - (?P<title>.+)$",
    re.MULTILINE,
)
CLAUSE_ID_RE = re.compile(r"\b[A-Z0-9]+-(?:UI|UX|A11Y)-[0-9]{3}\b")
FIELD_RE_TEMPLATE = r"^\*\*{field}:\*\* (?P<value>.+)$"
SOURCE_RE = re.compile(r"^\[(?P<label>[^\]]+)\]\((?P<url>.+)\)$")

REQUIRED_FRONTMATTER = ("corpus_version", "domain", "platform", "last_reviewed")
REQUIRED_FIELDS = ("Severity", "Dimension", "Platform", "Source", "Retrieved")


@dataclass(frozen=True)
class CorpusFile:
    path: Path
    frontmatter: dict[str, str]
    body: str


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def repo_relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def plugin_relative(path: Path) -> str:
    return path.relative_to(PLUGIN_ROOT).as_posix()


def parse_frontmatter(path: Path) -> CorpusFile:
    text = path.read_text()
    if not text.startswith("---\n"):
        fail(f"{repo_relative(path)} is missing YAML frontmatter")

    try:
        _, raw_frontmatter, body = text.split("---\n", 2)
    except ValueError:
        fail(f"{repo_relative(path)} has malformed YAML frontmatter")

    frontmatter: dict[str, str] = {}
    for line_number, line in enumerate(raw_frontmatter.splitlines(), start=2):
        if not line.strip():
            continue
        if ":" not in line:
            fail(f"{repo_relative(path)}:{line_number} has unsupported frontmatter line")
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"').strip("'")

    for key in REQUIRED_FRONTMATTER:
        if not frontmatter.get(key):
            fail(f"{repo_relative(path)} frontmatter missing {key}")

    if frontmatter["platform"] != "ios":
        fail(f"{repo_relative(path)} platform must be ios")

    return CorpusFile(path=path, frontmatter=frontmatter, body=body)


def get_field(block: str, field: str, path: Path, clause_id: str) -> str:
    pattern = re.compile(FIELD_RE_TEMPLATE.format(field=re.escape(field)), re.MULTILINE)
    match = pattern.search(block)
    if not match:
        fail(f"{repo_relative(path)} {clause_id} missing {field}")
    return match.group("value").strip()


def parse_source(raw_source: str, path: Path, clause_id: str) -> tuple[str, str]:
    match = SOURCE_RE.match(raw_source)
    if not match:
        fail(f"{repo_relative(path)} {clause_id} Source must be markdown link")
    return match.group("label"), match.group("url")


def slugify_anchor(heading_text: str) -> str:
    slug = heading_text.strip().lower()
    slug = re.sub(r"`([^`]+)`", r"\1", slug)
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def parse_clause_blocks(corpus_file: CorpusFile) -> list[dict[str, str]]:
    matches = list(CLAUSE_HEADING_RE.finditer(corpus_file.body))
    if not matches:
        fail(f"{repo_relative(corpus_file.path)} contains no clause headings")

    clauses: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        clause_id = match.group("id")
        title = match.group("title").strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(corpus_file.body)
        block = corpus_file.body[start:end]

        for field in REQUIRED_FIELDS:
            get_field(block, field, corpus_file.path, clause_id)

        severity = get_field(block, "Severity", corpus_file.path, clause_id)
        dimension = get_field(block, "Dimension", corpus_file.path, clause_id)
        platform = get_field(block, "Platform", corpus_file.path, clause_id)
        source_label, source_url = parse_source(
            get_field(block, "Source", corpus_file.path, clause_id),
            corpus_file.path,
            clause_id,
        )
        retrieved = get_field(block, "Retrieved", corpus_file.path, clause_id)

        if severity not in {"error", "warning", "info"}:
            fail(f"{repo_relative(corpus_file.path)} {clause_id} has invalid severity {severity}")
        if dimension not in {"ui", "ux", "accessibility"}:
            fail(f"{repo_relative(corpus_file.path)} {clause_id} has invalid dimension {dimension}")
        if platform != "ios":
            fail(f"{repo_relative(corpus_file.path)} {clause_id} platform must be ios")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", retrieved):
            fail(f"{repo_relative(corpus_file.path)} {clause_id} Retrieved must be YYYY-MM-DD")

        heading_text = f"{clause_id} - {title}"
        clauses.append(
            {
                "clause_id": clause_id,
                "title": title,
                "domain": corpus_file.frontmatter["domain"],
                "severity": severity,
                "dimension": dimension,
                "platform": platform,
                "source_label": source_label,
                "source_url": source_url,
                "retrieved": retrieved,
                "file_path": plugin_relative(corpus_file.path),
                "anchor": f"#{slugify_anchor(heading_text)}",
                "corpus_version": corpus_file.frontmatter["corpus_version"],
            }
        )

    return clauses


def build_index() -> list[dict[str, str]]:
    if not IOS_CORPUS_ROOT.is_dir():
        fail(f"missing corpus directory: {repo_relative(IOS_CORPUS_ROOT)}")

    clauses: list[dict[str, str]] = []
    seen: dict[str, str] = {}

    for path in sorted(IOS_CORPUS_ROOT.glob("*.md")):
        corpus_file = parse_frontmatter(path)
        for clause in parse_clause_blocks(corpus_file):
            clause_id = clause["clause_id"]
            if clause_id in seen:
                fail(f"duplicate clause ID {clause_id}: {seen[clause_id]} and {repo_relative(path)}")
            seen[clause_id] = repo_relative(path)
            clauses.append(clause)

    return sorted(clauses, key=lambda item: item["clause_id"])


def format_index(clauses: list[dict[str, str]]) -> str:
    return json.dumps(clauses, indent=2, sort_keys=True) + "\n"


def validate_skill_references(clauses: list[dict[str, str]]) -> None:
    known = {clause["clause_id"] for clause in clauses}
    missing: dict[str, set[str]] = {}

    for root in SKILL_REFERENCE_ROOTS:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.md")):
            text = path.read_text()
            ids = set(CLAUSE_ID_RE.findall(text))
            unknown = sorted(ids - known)
            if unknown:
                missing[repo_relative(path)] = set(unknown)

    if missing:
        lines = ["unknown clause IDs referenced by skills:"]
        for path, ids in sorted(missing.items()):
            lines.append(f"  {path}: {', '.join(sorted(ids))}")
        fail("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if corpus/index.json is stale")
    parser.add_argument(
        "--validate-skill-refs",
        action="store_true",
        help="fail when plugin skills cite clause IDs absent from the corpus index",
    )
    args = parser.parse_args()

    clauses = build_index()
    formatted = format_index(clauses)

    if args.validate_skill_refs:
        validate_skill_references(clauses)

    if args.check:
        if not INDEX_PATH.exists():
            fail(f"{repo_relative(INDEX_PATH)} does not exist")
        current = INDEX_PATH.read_text()
        if current != formatted:
            fail(f"{repo_relative(INDEX_PATH)} is out of sync; run scripts/build_corpus_index.py")
        print(f"corpus index ok: {len(clauses)} clauses")
        return 0

    INDEX_PATH.write_text(formatted)
    print(f"wrote {repo_relative(INDEX_PATH)} with {len(clauses)} clauses")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
