# Repository Guidelines

## Project Shape

EvenBetter is a curated-skills framework and plugin marketplace, not a single app or runtime. This repository distributes skill packages for Claude Code and Codex from one GitHub-hosted marketplace.

The installable plugin skill sources of truth are:

- `plugins/evenbetter-ios/skills/`
- `plugins/evenbetter-general/skills/`

Do not maintain parallel copies of installable plugin skills under root `skills/`. If a skill ships to users, edit it under the matching plugin in `plugins/*/skills/`.

## Marketplace Metadata

Marketplace files:

- Claude Code marketplace: `.claude-plugin/marketplace.json`
- Codex marketplace: `.agents/plugins/marketplace.json`
- Claude Code iOS plugin manifest: `plugins/evenbetter-ios/.claude-plugin/plugin.json`
- Codex iOS plugin manifest: `plugins/evenbetter-ios/.codex-plugin/plugin.json`
- Claude Code general plugin manifest: `plugins/evenbetter-general/.claude-plugin/plugin.json`
- Codex general plugin manifest: `plugins/evenbetter-general/.codex-plugin/plugin.json`
- MCP servers for the iOS plugin: `plugins/evenbetter-ios/.mcp.json`, one file with an `mcpServers` map that both hosts read

Keep marketplace entries pointed at `./plugins/evenbetter-ios` and `./plugins/evenbetter-general`.

Only `plugin.json` belongs inside `.claude-plugin/` and `.codex-plugin/`. Plugin components such as `skills/`, `agents/`, scripts, commands, hooks, MCP servers, or assets belong at the plugin root or inside the relevant skill package.

During active Claude Code development, keep explicit `version` fields omitted unless the repository adopts a formal release/versioning process.

## Skill Authoring Rules

Each skill should have:

- `SKILL.md` with YAML frontmatter containing `name` and `description`
- optional `references/` for progressive disclosure
- optional `agents/openai.yaml` when the skill needs agent configuration
- optional `scripts/` for deterministic helpers

Frontmatter and text rules that keep a skill working in both hosts:

- Frontmatter uses only `name`, `description` and, when needed, `license`, `compatibility` and `metadata`. No `version`, `model` or `effort`, and no skill names a model.
- `description` is third person: what the skill does, then "Use when ..." with concrete triggers, 250-500 characters (1,024 is the hard limit), no `<` or `>`. When two skills sit close together, end with one routing clause that names the neighbour.
- Never write `$` followed by a digit in a `SKILL.md` body (Claude Code substitutes it); write `USD 9.99`, or keep price tables in `references/`.
- State each rule once, in sentence case, with its reason. No all-caps emphasis such as CRITICAL or MUST.
- Paths in a skill are relative to its `SKILL.md` folder; the iOS corpus is `../../corpus/` from there. Never tell an agent to write inside the installed plugin folder: artifacts go to the user's project under `.evenbetter/`.
- Refer to other skills by plain name and to MCP tools by server and tool name, not by one host's syntax.
- When a skill is adapted from another project, keep its notice in `THIRD_PARTY_NOTICES.md` (root and plugin copy) and any license file it needs.

Prefer router-style `SKILL.md` files plus focused `references/*` files over one large monolithic skill. Load and edit only the relevant stage/reference when making scoped changes.

Keep skills agent-generic. Avoid hard-coding one host's invocation syntax, project instruction files, or MCP-specific assumptions unless the target platform explicitly requires it. When converted Claude Code references mention `AskUserQuestion`, preserve that support and add Codex equivalents where relevant.

For Codex:

- In Plan mode, use `request_user_input` when available. Plan mode is read-only, so a skill presents its plan in a `<proposed_plan>` block and asks the user to switch to Default mode before it writes `.evenbetter/` files or edits code.
- In Default mode, ask concise plain-text questions and wait.
- `update_plan` and `apply_patch` work only in Default mode.
- Do not simulate unavailable tools.
- Workflow skills carry "Question tooling" and "Tool equivalents" sections that share most of their wording. When you change a shared bullet or table row, change it in every skill that has it, word for word. Each skill keeps its own lines: what its Plan-mode bullet says it writes, a per-round limit, the table rows it adds or leaves out, the sources its `ref_search_documentation` row falls back to (official documentation, official Apple pages or official pages), and the paragraphs before or after the bullets and the table, such as when it asks, which exceptions it makes, how to fetch Apple pages and when to delegate.

For iOS UX/HIG workflow skills, questions should be closed and multiple-choice by default. Avoid open-ended questions, ask for screenshots or simulator evidence when reviewing UI states, and keep feature-scale and epic-scale flows separate.

## Validation Commands

Always run these checks after marketplace, skill, or corpus edits:

```bash
jq . .claude-plugin/marketplace.json \
  .agents/plugins/marketplace.json \
  plugins/evenbetter-ios/corpus/index.json \
  plugins/evenbetter-ios/.claude-plugin/plugin.json \
  plugins/evenbetter-ios/.codex-plugin/plugin.json \
  plugins/evenbetter-general/.claude-plugin/plugin.json \
  plugins/evenbetter-general/.codex-plugin/plugin.json \
  plugins/evenbetter-ios/.mcp.json
```

```bash
python3 scripts/check-skills.py
```

`scripts/check-skills.py` (needs PyYAML) covers what the host validators skip: frontmatter keys and limits (name matches the folder, description of 1,024 characters or fewer with no `<` or `>`), `$` followed by a digit in a `SKILL.md` body (Claude Code replaces it with an argument), broken relative paths and links, `agents/openai.yaml` fields, plugin manifests and paths, and the corpus and `index.json` sync described below. Errors fail the run. Clear the warnings for any file you touch, or say why you kept one.

```bash
for t in . plugins/evenbetter-ios plugins/evenbetter-general; do
  claude plugin validate "$t"
done
```

Run `claude plugin validate` on each plugin folder as well as the root: the root run does not open the plugins' skills. Leave out `--strict` while `version` stays omitted, because the missing version is its only warning. `.github/workflows/validate.yml` runs all of these checks plus a Codex install in a throwaway `CODEX_HOME` on every pull request.

```bash
for skill in plugins/evenbetter-ios/skills/* plugins/evenbetter-general/skills/*; do
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
rg -o "[A-Z0-9]+-(UI|UX|A11Y)-[0-9]{3}" plugins/evenbetter-ios/skills plugins/evenbetter-general/skills \
  | sed -E "s/^.*:([A-Z0-9]+-(UI|UX|A11Y)-[0-9]{3})$/\1/" \
  | sort -u > /tmp/evenbetter-skill-ids.txt

comm -23 /tmp/evenbetter-skill-ids.txt /tmp/evenbetter-index-ids.txt
```

The `comm -23` output must be empty. Also inspect each changed corpus clause and matching `index.json` entry to confirm `severity`, `dimension`, `platform`, `source_url`, `retrieved`, and `file_path` stayed synchronized.

```bash
git diff --check
```

Use `rg`/`rg --files` for repo inspection. Do not add `.DS_Store`, `.codex/`, or `.claude/`; they are local metadata and should stay ignored.

## Evals

Each plugin has a `claude plugin eval` suite under `plugins/*/evals/`. Routing cases check which skill a plain request reaches. Behaviour cases run a skill on a fixture (PlantCare, a small SwiftUI app, for iOS; a small Express API for general) and grade the files it leaves behind. Each `evals/README.md` lists the cases and explains the graders. See [Claude Code's plugin evals guide](https://code.claude.com/docs/en/plugin-evals) for the case format.

Run the suite after you change a skill's description, its stages or the report contract. The runs spend tokens, so CI does not run them.

```bash
cd plugins/evenbetter-ios
export CLAUDE_CONFIG_DIR="$(mktemp -d)"
claude auth login   # once: a new config folder can start signed out; skip when ANTHROPIC_API_KEY is set
export TMPDIR=/srv/eb-eval-tmp   # Linux: an existing folder outside /tmp and HOME
claude plugin eval . --tag routing --ablation none --runs 1 \
  --no-publish --trust-plugin --max-cost-usd 3
claude plugin eval . --tag behaviour --ablation none --runs 1 \
  --scaffold --allow-tools Bash Write Edit \
  --no-publish --trust-plugin --max-cost-usd 10
```

- Always pass `--no-publish`. By default the runner publishes the HTML report to the claude.ai account that is signed in.
- Use a throwaway `CLAUDE_CONFIG_DIR`, so a run never touches your own Claude Code settings or plugins. Test skills this way, not by installing the plugins into a personal account. Claude Code keeps its sign-in with the config, so the new folder can start signed out: sign in there once, or export `ANTHROPIC_API_KEY`.
- Behaviour cases that grant Bash need the sandbox backend, which on Linux is `bubblewrap` and `socat`. The eval sandbox makes `/tmp` read-only and hides HOME, so `TMPDIR` has to point outside both.
- Set `--max-cost-usd` on every run. Results land in `evals/results/`, which is gitignored.
