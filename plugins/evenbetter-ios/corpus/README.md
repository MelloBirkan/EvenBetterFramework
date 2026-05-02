# EvenBetter iOS Corpus

This directory is the canonical source for the iOS guideline corpus shipped inside the `evenbetter-ios` plugin. Keep the corpus plugin-local so installed marketplace skills can read it after Claude Code or Codex copies `plugins/evenbetter-ios`.

The corpus is markdown-first. Each domain file under `ios/` contains stable H2 clause IDs used by analyzer, validator, fixer, and benchmark outputs. Do not maintain duplicate rule bodies inside skill `references/`; skills should load these corpus files directly.

## Files

- `ios/typography.md`
- `ios/color-theming.md`
- `ios/components-patterns.md`
- `ios/layout-interaction.md`
- `ios/navigation-flow.md`
- `ios/accessibility.md`
- `index.json`, the maintained derived index of corpus clauses

## Workflow

1. Edit the relevant markdown file under `ios/`.
2. Keep the clause ID stable unless the rule meaning changes incompatibly.
3. Update `index.json` when clause metadata changes.
4. Run the corpus consistency checks documented in the repository `AGENTS.md`.

`index.json` is derived from the markdown corpus and must stay synchronized with it.
