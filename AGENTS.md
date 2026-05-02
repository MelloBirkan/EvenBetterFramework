# Repository Guidelines

## Project Shape

EvenBetter is a curated-skills framework and plugin marketplace, not a single app or runtime. This repository distributes skill packages for Claude Code and Codex from one GitHub-hosted marketplace.

The installable iOS plugin source of truth is:

- `plugins/evenbetter-ios/skills/`

The root `skills/` directory contains repo-local platform-agnostic workflow skills:

- `skills/evenbetter-general-feature/`
- `skills/evenbetter-general-epic/`

Do not maintain a parallel copy of installable iOS plugin skills under root `skills/`. If an iOS skill ships to users, edit it under `plugins/evenbetter-ios/skills/`.

## Marketplace Metadata

Marketplace files:

- Claude Code marketplace: `.claude-plugin/marketplace.json`
- Codex marketplace: `.agents/plugins/marketplace.json`
- Claude Code plugin manifest: `plugins/evenbetter-ios/.claude-plugin/plugin.json`
- Codex plugin manifest: `plugins/evenbetter-ios/.codex-plugin/plugin.json`

Keep marketplace entries pointed at `./plugins/evenbetter-ios`.

Only `plugin.json` belongs inside `.claude-plugin/` and `.codex-plugin/`. Plugin components such as `skills/`, `agents/`, scripts, commands, hooks, MCP servers, or assets belong at the plugin root or inside the relevant skill package.

During active Claude Code development, keep explicit `version` fields omitted unless the repository adopts a formal release/versioning process.

## Skill Authoring Rules

Each skill should have:

- `SKILL.md` with YAML frontmatter containing `name` and `description`
- optional `references/` for progressive disclosure
- optional `agents/openai.yaml` when the skill needs agent configuration
- optional `scripts/` for deterministic helpers

Prefer router-style `SKILL.md` files plus focused `references/*` files over one large monolithic skill. Load and edit only the relevant stage/reference when making scoped changes.

Keep skills agent-generic. Avoid hard-coding one host's invocation syntax, project instruction files, or MCP-specific assumptions unless the target platform explicitly requires it. When converted Claude Code references mention `AskUserQuestion`, preserve that support and add Codex equivalents where relevant.

For Codex:

- In Plan mode, use `request_user_input` when available.
- In Default mode, ask concise plain-text questions and wait.
- Do not simulate unavailable tools.

For iOS UX/HIG workflow skills, questions should be closed and multiple-choice by default. Avoid open-ended questions, ask for screenshots or simulator evidence when reviewing UI states, and keep feature-scale and epic-scale flows separate.

## Analyzer, Validator, and Fixer Contract

The current EvenBetter report contract is manifest-first:

- `.evenbetter/manifest.json` is the source of truth for report history.
- Analyzer reports are numbered as `.evenbetter/analyze-{N}.json`.
- Validator reports are numbered as `.evenbetter/evenbetter-validate-{N}.json`.
- Legacy singleton files such as `.evenbetter/analyze.json`, `.evenbetter/eb-analyze.json`, `.evenbetter/validate.json`, and `.evenbetter/evenbetter-validate.json` are compatibility or migration cases only.

Analyzer behavior:

- Read project source files without modifying them.
- Only write numbered analyzer reports, documented legacy migrations, and `manifest.json` inside the analyzed project's `.evenbetter/` directory.
- Preserve stable violation IDs and carry forward prior mutable state when matching violations recur.

Validator behavior:

- Select runs from `manifest.json` by default.
- Validate the newest unvalidated run unless an explicit run is requested.
- Write the matching `evenbetter-validate-{N}.json` report and update manifest run pairing.
- Validate high-severity findings separately from analyzer output; do not merge validator results into analyzer JSON.

Fixer behavior:

- Do a short closed-ended scoping step before remediation.
- Use precedence: manifest, newest validation report, newest analyzer report, then older unresolved manifest runs.
- Skip `fixed` and `rejected` findings. Include `deferred` only when explicitly requested.
- Reread `manifest.json` before writing state updates. EvenBetter assumes serial writes to `.evenbetter/`.

## Validation Commands

Always run these checks after marketplace, skill, or corpus edits:

```bash
jq . .claude-plugin/marketplace.json \
  .agents/plugins/marketplace.json \
  plugins/evenbetter-ios/corpus/index.json \
  plugins/evenbetter-ios/.claude-plugin/plugin.json \
  plugins/evenbetter-ios/.codex-plugin/plugin.json
```

```bash
for skill in skills/* plugins/evenbetter-ios/skills/*; do
  [ -d "$skill" ] || continue
  name="$(basename "$skill")"
  rg -n "^name: $name$" "$skill/SKILL.md" >/dev/null || echo "name mismatch: $skill"
done
```

For corpus or skill changes, always verify the maintained derived index manually:

```bash
rg -o "^## [A-Z0-9]+-(UI|UX|A11Y)-[0-9]{3}" plugins/evenbetter-ios/corpus/ios/*.md \
  | sed -E "s/^.*## ([A-Z0-9]+-(UI|UX|A11Y)-[0-9]{3})$/\1/" \
  | sort > /tmp/evenbetter-corpus-ids.txt

jq -r ".[].clause_id" plugins/evenbetter-ios/corpus/index.json \
  | sort > /tmp/evenbetter-index-ids.txt

diff -u /tmp/evenbetter-corpus-ids.txt /tmp/evenbetter-index-ids.txt
```

Then check every skill-cited clause ID exists in `plugins/evenbetter-ios/corpus/index.json`:

```bash
rg -o "[A-Z0-9]+-(UI|UX|A11Y)-[0-9]{3}" skills plugins/evenbetter-ios/skills \
  | sed -E "s/^.*:([A-Z0-9]+-(UI|UX|A11Y)-[0-9]{3})$/\1/" \
  | sort -u > /tmp/evenbetter-skill-ids.txt

comm -23 /tmp/evenbetter-skill-ids.txt /tmp/evenbetter-index-ids.txt
```

The `comm -23` output must be empty. Also inspect each changed corpus clause and matching `index.json` entry to confirm `severity`, `dimension`, `platform`, `source_url`, `retrieved`, and `file_path` stayed synchronized.

```bash
git diff --check
```

Use `rg`/`rg --files` for repo inspection. Do not add `.DS_Store`, `.codex/`, or `.claude/`; they are local metadata and should stay ignored.
