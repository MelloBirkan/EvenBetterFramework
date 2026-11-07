# EvenBetter iOS Corpus

This directory is the canonical source for the iOS guideline corpus shipped inside the `evenbetter-ios` plugin. Keep the corpus plugin-local so installed marketplace skills can read it after Claude Code or Codex copies `plugins/evenbetter-ios`.

The corpus is markdown-first. Each domain file under `ios/` contains stable H2 clause IDs used by the analyze, validate and repair skills and by benchmark outputs. Do not maintain duplicate rule bodies inside skill `references/`; skills should load these corpus files directly.

## Files

- `ios/typography.md`
- `ios/color-theming.md`
- `ios/components-patterns.md`
- `ios/layout-interaction.md`
- `ios/navigation-flow.md`
- `ios/accessibility.md`
- `ios/haptics.md`
- `index.json`, the maintained derived index of corpus clauses
- `SCHEMA.md`, the file and clause format

## Workflow

1. Edit the relevant markdown file under `ios/`.
2. Keep the clause ID stable unless the rule meaning changes incompatibly.
3. Update `index.json` when clause metadata changes.
4. Run the corpus consistency checks documented in the repository `AGENTS.md`.

`index.json` is derived from the markdown corpus and must stay synchronized with it.

## Re-reviewing against Apple's guidance

Apple lists HIG changes by date at https://developer.apple.com/design/whats-new/, and each HIG page ends with its own change log. To re-review the corpus:

1. Compare the dates on the what's-new page with each file's `last_reviewed` date, and note the cited pages that changed since then.
   App Store Connect Help pages, such as the Accessibility Nutrition Labels evaluation criteria, have no change log, so reread every one the corpus cites.
2. Read each clause's source page. Apple's pages need JavaScript, so a plain fetch can return an empty shell. Use a scraper that renders pages, or Apple's JSON form: `https://developer.apple.com/tutorials/data/design/human-interface-guidelines/<page>.json` for HIG pages and `https://developer.apple.com/tutorials/data/documentation/<path>.json` for API documentation.
3. Confirm that the page still states the rule the clause encodes. If Apple moved the guidance, point **Source** at the page that states it now. Change Check, Why, Correct code, or Severity only when the source changed or the clause is wrong.
4. Set **Retrieved** on every clause you checked and `last_reviewed` on every file you changed, then update `index.json` to match.
5. Run the corpus checks in the repository `AGENTS.md` and `python3 scripts/check-skills.py` from the repository root.

The last full review was on 2026-11-07, after the HIG revisions of 2026-06-08 and 2026-09-09.
