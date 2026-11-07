#!/usr/bin/env python3
"""Offline checks for the EvenBetter marketplace, plugins, skills and corpus.

Run from the repository root:

    python3 scripts/check-skills.py            # errors fail, warnings are printed
    python3 scripts/check-skills.py --strict   # warnings fail too

Needs Python 3.9+ and PyYAML (`pip install pyyaml`).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("check-skills: PyYAML is required (pip install pyyaml)")

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ["evenbetter-ios", "evenbetter-general"]
CORPUS = ROOT / "plugins/evenbetter-ios/corpus"

# Portable frontmatter subset (Agent Skills spec). Host-specific keys are refused
# because the same SKILL.md ships to Claude Code and Codex.
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata"}
REFUSED_KEYS = {"version", "model", "effort"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CLAUSE_RE = re.compile(r"\b[A-Z0-9]+-(?:UI|UX|A11Y)-[0-9]{3}\b")
# Claude Code replaces $N with the Nth argument (regex /\$(\d+)(?!\w)/ in 2.1.319).
DOLLAR_DIGIT_RE = re.compile(r"\$\d+(?!\w)")
EMPHASIS_RE = re.compile(r"\b(CRITICAL|IMPORTANT|MUST|NEVER|ALWAYS|DO NOT|MUST NOT)\b")
HOST_SYNTAX_RE = re.compile(r"mcp__[A-Za-z]|/evenbetter-(?:ios|general):|\$evenbetter-")
SKILL_PATH_RE = re.compile(r"`((?:references|scripts|assets|agents)/[A-Za-z0-9_./-]+|\.\./\.\./(?:corpus|scripts)/[A-Za-z0-9_./-]+)`")
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
DESC_TOTAL_BUDGET = 8000

errors: list[str] = []
warnings: list[str] = []


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def err(p: Path | str, msg: str) -> None:
    errors.append(f"ERROR {p if isinstance(p, str) else rel(p)}: {msg}")


def warn(p: Path | str, msg: str) -> None:
    warnings.append(f"WARN  {p if isinstance(p, str) else rel(p)}: {msg}")


def load_json(p: Path):
    try:
        return json.loads(p.read_text())
    except Exception as e:  # noqa: BLE001
        err(p, f"invalid JSON ({e})")
        return None


def split_frontmatter(text: str):
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 4 :].lstrip("\n")


def strip_code(text: str) -> str:
    """Drop fenced code blocks so examples are not checked as prose."""
    return re.sub(r"```.*?```", "", text, flags=re.S)


def check_manifests() -> None:
    cm = load_json(ROOT / ".claude-plugin/marketplace.json")
    xm = load_json(ROOT / ".agents/plugins/marketplace.json")
    for mp, path in ((cm, ".claude-plugin/marketplace.json"), (xm, ".agents/plugins/marketplace.json")):
        if not mp:
            continue
        for entry in mp.get("plugins", []):
            src = entry.get("source")
            src = src.get("path") if isinstance(src, dict) else src
            if not isinstance(src, str) or not (ROOT / src).is_dir():
                err(path, f"plugin {entry.get('name')} source does not resolve: {src}")
            elif Path(src).name != entry.get("name"):
                err(path, f"plugin {entry.get('name')} points at {src}")
    for plugin in PLUGINS:
        base = ROOT / "plugins" / plugin
        if (base / ".mcp.json").exists():
            mcp = load_json(base / ".mcp.json")
            if mcp is not None and not isinstance(mcp.get("mcpServers"), dict):
                err(base / ".mcp.json", "expected an mcpServers map")
        for host in (".claude-plugin", ".codex-plugin"):
            d = base / host
            extra = [p.name for p in d.iterdir() if p.name != "plugin.json"] if d.is_dir() else []
            if extra:
                err(d, f"only plugin.json belongs here, found {extra}")
            m = load_json(d / "plugin.json")
            if not m:
                continue
            if m.get("name") != plugin:
                err(d / "plugin.json", f"name is {m.get('name')!r}, expected {plugin!r}")
            if "version" in m:
                warn(d / "plugin.json", "version is set; AGENTS.md keeps it omitted during development")
            for key in ("icon", "mcpServers"):
                v = m.get(key)
                if isinstance(v, str) and v.startswith("./") and not (base / v).exists():
                    err(d / "plugin.json", f"{key} path {v} does not exist")
            iface = m.get("interface") or {}
            for key in ("composerIcon", "logo"):
                v = iface.get(key)
                if isinstance(v, str) and not (base / v).exists():
                    err(d / "plugin.json", f"interface.{key} path {v} does not exist")
            sd = iface.get("shortDescription")
            if isinstance(sd, str) and len(sd) > 30:
                warn(d / "plugin.json", f"interface.shortDescription is {len(sd)} chars (30 max for directory listings)")
        if not (base / "README.md").is_file():
            warn(base, "no README.md in the plugin folder")
        for p in base.rglob("*"):
            if p.is_symlink():
                err(p, "symlinks do not survive plugin installs")
            if p.name in {".DS_Store", "Thumbs.db", "desktop.ini"}:
                err(p, "local metadata file")


def check_links(skill_dir: Path, md: Path, text: str) -> None:
    prose = strip_code(text)
    for m in SKILL_PATH_RE.finditer(prose):
        target = m.group(1).split("#")[0].rstrip(".,")
        if any(ch in target for ch in "*[]"):
            continue
        if not (skill_dir / target).exists():
            err(md, f"path `{target}` does not exist (paths resolve from the skill folder)")
    for m in MD_LINK_RE.finditer(prose):
        target = m.group(1)
        if re.match(r"^(https?:|mailto:|#|file:)", target):
            continue
        target = target.split("#")[0]
        if not target:
            continue
        if not ((md.parent / target).exists() or (skill_dir / target).exists()):
            err(md, f"link target {target} does not exist")


def check_openai_yaml(skill_dir: Path, name: str) -> None:
    p = skill_dir / "agents/openai.yaml"
    if not p.is_file():
        warn(skill_dir, "no agents/openai.yaml (Codex UI metadata)")
        return
    try:
        data = yaml.safe_load(p.read_text()) or {}
    except yaml.YAMLError as e:
        err(p, f"invalid YAML ({e})")
        return
    iface = data.get("interface") or {}
    dn = iface.get("display_name", "")
    sd = iface.get("short_description", "")
    dp = iface.get("default_prompt", "")
    if not dn or len(dn) > 64:
        err(p, "interface.display_name must be 1-64 chars")
    if not (25 <= len(sd) <= 64):
        err(p, f"interface.short_description is {len(sd)} chars (25-64)")
    if not dp:
        warn(p, "interface.default_prompt is missing")
    elif f"${name}" not in dp:
        err(p, f"interface.default_prompt should mention ${name}")
    for field, value in (("short_description", sd), ("default_prompt", dp)):
        if "<" in value or ">" in value:
            err(p, f"interface.{field} contains angle brackets")
        if "—" in value:
            warn(p, f"interface.{field} contains an em dash")


def check_skill(skill_dir: Path) -> int:
    md = skill_dir / "SKILL.md"
    if not md.is_file():
        err(skill_dir, "missing SKILL.md")
        return 0
    text = md.read_text()
    fm_text, body = split_frontmatter(text)
    if fm_text is None:
        err(md, "missing YAML frontmatter")
        return 0
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as e:
        err(md, f"invalid frontmatter ({e})")
        return 0
    name = fm.get("name")
    if name != skill_dir.name:
        err(md, f"name {name!r} does not match folder {skill_dir.name!r}")
    if not isinstance(name, str) or not NAME_RE.match(name or "") or len(name) > 64:
        err(md, "name must be lowercase letters, digits and single hyphens, 64 chars max")
    for key in fm:
        if key in REFUSED_KEYS:
            err(md, f"frontmatter key {key!r} is not portable; leave it out")
        elif key not in ALLOWED_KEYS:
            warn(md, f"frontmatter key {key!r} is outside the portable subset")
    desc = fm.get("description")
    dlen = 0
    if not isinstance(desc, str) or not desc.strip():
        err(md, "description must be a non-empty string")
    else:
        dlen = len(desc)
        if dlen > 1024:
            err(md, f"description is {dlen} chars (1024 max; Codex truncates and claude.ai rejects longer)")
        elif dlen < 250 or dlen > 500:
            warn(md, f"description is {dlen} chars (aim for 250-500)")
        if "<" in desc or ">" in desc:
            err(md, "description contains < or > (write [project], not <project>)")
        if not re.search(r"\buse\b.{0,20}\bwhen\b", desc, re.I):
            warn(md, "description has no 'Use when' trigger sentence")
    comp = fm.get("compatibility")
    if comp is not None and (not isinstance(comp, str) or len(comp) > 500):
        err(md, "compatibility must be a string of 500 chars or fewer")
    meta = fm.get("metadata")
    if meta is not None and (not isinstance(meta, dict) or not all(isinstance(v, str) for v in meta.values())):
        err(md, "metadata must map strings to strings")

    lines = body.count("\n") + 1
    if lines > 500:
        warn(md, f"SKILL.md body is {lines} lines (keep under 500; move detail to references/)")
    if DOLLAR_DIGIT_RE.search(body):
        err(md, "SKILL.md contains $ followed by a digit, which Claude Code replaces with arguments (write USD 1)")
    prose = strip_code(body)
    caps = EMPHASIS_RE.findall(prose)
    if caps:
        warn(md, f"all-caps emphasis {sorted(set(caps))}; state the rule plainly with its reason")
    if HOST_SYNTAX_RE.search(prose):
        warn(md, "host-specific syntax (mcp__ ids, /plugin:skill or $skill); name skills and tools neutrally")
    check_links(skill_dir, md, body)

    for ref in sorted(skill_dir.rglob("*.md")):
        if ref == md:
            continue
        rtext = ref.read_text()
        check_links(skill_dir, ref, rtext)
        if ref.parent.name == "references" and rtext.count("\n") > 100:
            head = "\n".join(rtext.splitlines()[:25]).lower()
            if "contents" not in head:
                warn(ref, "reference over 100 lines without a contents list near the top")
        rcaps = EMPHASIS_RE.findall(strip_code(rtext))
        if len(rcaps) >= 3:
            warn(ref, f"all-caps emphasis x{len(rcaps)} {sorted(set(rcaps))}")
    check_openai_yaml(skill_dir, skill_dir.name)
    return dlen


def check_corpus() -> None:
    index = load_json(CORPUS / "index.json")
    if index is None:
        return
    md_ids = set()
    for f in sorted((CORPUS / "ios").glob("*.md")):
        for m in re.finditer(r"^## ([A-Z0-9]+-(?:UI|UX|A11Y)-[0-9]{3})\b", f.read_text(), re.M):
            if m.group(1) in md_ids:
                err(f, f"duplicate clause {m.group(1)}")
            md_ids.add(m.group(1))
    idx_ids = {e.get("clause_id") for e in index}
    for cid in sorted(md_ids - idx_ids):
        err(CORPUS / "index.json", f"{cid} is in the corpus but not in index.json")
    for cid in sorted(idx_ids - md_ids):
        err(CORPUS / "index.json", f"{cid} is in index.json but not in the corpus")
    required = ("clause_id", "severity", "dimension", "platform", "source_url", "retrieved", "file_path")
    for e in index:
        missing = [k for k in required if not e.get(k)]
        if missing:
            err(CORPUS / "index.json", f"{e.get('clause_id')} lacks {missing}")
            continue
        fp = CORPUS.parent / e["file_path"]  # file_path is relative to the plugin root
        if not fp.is_file():
            err(CORPUS / "index.json", f"{e['clause_id']} file_path {e['file_path']} does not exist")
            continue
        section = re.search(rf"^## {re.escape(e['clause_id'])}\b(.*?)(?=^## |\Z)", fp.read_text(), re.S | re.M)
        if not section:
            err(fp, f"{e['clause_id']} heading not found")
            continue
        s = section.group(1)
        for label, key in (("Severity", "severity"), ("Dimension", "dimension"), ("Platform", "platform"), ("Retrieved", "retrieved")):
            m = re.search(rf"\*\*{label}:\*\*\s*(\S+)", s)
            if m and m.group(1) != str(e[key]):
                err(fp, f"{e['clause_id']} {label} is {m.group(1)} but index.json says {e[key]}")
        m = re.search(r"^\*\*Source:\*\*\s*\[[^\]]*\]\((https?://.+)\)\s*$", s, re.M)
        if m and m.group(1) != e["source_url"]:
            err(fp, f"{e['clause_id']} source URL differs from index.json")
    cited = set()
    for plugin in PLUGINS:
        for f in (ROOT / "plugins" / plugin / "skills").rglob("*"):
            if f.is_file() and f.suffix in {".md", ".html", ".yaml", ".json"}:
                cited |= set(CLAUSE_RE.findall(f.read_text(errors="ignore")))
    for cid in sorted(cited - idx_ids):
        err("plugins/*/skills", f"cites {cid}, which is not in corpus/index.json")


def main() -> int:
    strict = "--strict" in sys.argv
    check_manifests()
    total = 0
    for plugin in PLUGINS:
        for skill_dir in sorted((ROOT / "plugins" / plugin / "skills").iterdir()):
            if skill_dir.is_dir():
                total += check_skill(skill_dir)
    if total > DESC_TOTAL_BUDGET:
        warn("plugins", f"skill descriptions total {total} chars; Claude Code's listing budget is {DESC_TOTAL_BUDGET} chars at 200K context, and Codex falls back to the same when the window is unknown")
    check_corpus()
    for line in errors + warnings:
        print(line)
    print(f"check-skills: {len(errors)} errors, {len(warnings)} warnings, {total} description chars")
    return 1 if errors or (strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
