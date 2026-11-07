# 2 Verify

Contents: Role, Process, Merging findings, Writing the two fixes, Writing the AI fix prompt, WCAG cross-references, How many findings to keep, Stage exit criteria.

## Role

Confirm each draft from stage `1-scan` against its Apple source and its code context, merge drafts that share a construct and a fix, and write the fixes and prompt for each surviving finding. Drop anything you cannot defend.

Static matching is recall-heavy on purpose, and many drafts fall apart on a closer read: a call that looks like a tap gesture is a private helper, a bare `Image` sits under a parent that already sets `accessibilityHidden(true)`, a `frame(width: 32)` icon lives inside a tappable parent that is 44 points wide. This stage is what turns matches into an audit.

## Process

1. Group the drafts by clause so each Apple page is fetched once per audit. Fetch each clause's `source_url` from `../../corpus/index.json` with `WebFetch`, `ref_read_url`, or a scraper MCP such as Firecrawl, Tavily or Exa. Apple pages need JavaScript, so a plain fetch may return an empty shell; the JSON form in SKILL.md works without it. If no fetch tool works at all, rely on the corpus (its clauses were checked on their `retrieved` date), add a `scan_context.notes` line saying the Apple sources were not re-fetched, and lower `scan_context.confidence` by 0.1.
2. For every draft, run these checks:
   - **Source check.** The page passes when it states the rule the clause encodes, or, for an API reference page, when it documents the API the clause's fix relies on. Many index URLs are API pages that describe a modifier rather than the rule; the clause's **Why** carries the rule, so do not drop a finding just because the API page is terse. The source fails only when the page is gone or now contradicts the clause. Then drop the drafts for that clause and add a corpus-drift note to `scan_context.notes` naming the clause ID, the URL and what changed.
   - **Context check.** Re-read about 20 lines above and below the snippet. Confirm the violation applies here: look for parent modifiers, `if` or `#if` branches, `accessibility*` modifiers further up the chain, and siblings that already satisfy the clause. Read the clause's **Check** for its intent, as stage 1 does. A view that the app cannot reach only because of another finding in this report still counts; say so in the description. A view nothing references at all is dead code, so drop its drafts.
   - **Merge.** Apply the rules in Merging findings below.
   - **Severity.** Apply the table in SKILL.md to every clause on the finding and keep the highest result.
   - **WCAG.** Pick at most one criterion, as WCAG cross-references describes.
3. Write `minimal_fix`, `recommended_fix` and `ai_fix_prompt` for each finding, as the sections below describe, then the user-facing `title` and `description`. The description says what goes wrong for users, in 1-3 sentences. It may cite a more specific Apple page than `hig_reference_url` in its text; `hig_reference_url` itself always equals the primary clause's index `source_url`.
4. Order and number the findings as How many findings to keep describes.

## Merging findings

Emit one finding per construct and fix. The construct is the view expression a snippet centres on, with its own modifiers: one `Button`, one `Image`, one `TextField`. Two controls in the same `HStack` or `toolbar` are two constructs, so their findings stay separate even when their lines overlap or one commit could fix both. The exception is two constructs that start on the same line and share a clause or a twin pair: give them one finding, because the report checker treats `file_path` plus `line_number` as one site. Two such constructs on opposite sides of an exclusive pair (the second table below) also get one finding: it carries only the stricter clause (`LAY-A11Y-001` or `TYPO-A11Y-004`), its fixes bring both constructs up to that clause's bar, and its description names both. When several clauses fire on the same construct and one edit closes all of them, they form one finding:

- `clause_id` is the clause the edit centres on, meaning the clause whose **Correct code** the fix most resembles. Break ties by the higher corpus severity, then by the order of the clauses in `index.json`.
- `related_clause_ids` lists the other clauses the same edit closes. It is an empty array when there are none.
- `severity` is the highest that any of the clauses maps to.
- The fixes must close every listed clause, and the description names what each related clause adds in plain words.

Different constructs stay separate findings, and so do different fixes on the same construct. For example, a tappable `Image(systemName: "trash")` with `.onTapGesture`, a 28x28 frame and no label becomes one finding: converting it to `Button(role: .destructive)` with a label and a 44x44 content shape closes `COMP-UI-001`, `A11Y-A11Y-001`, `COMP-A11Y-002`, `A11Y-UI-001`, `LAY-UI-001` and `COMP-UX-001` together. Asking for confirmation before the delete (`LAY-UX-001`, and `COMP-UX-002` when the delete cannot be undone) needs new state and an alert, which is a different edit, so it is a second finding on the same construct.

These clause pairs describe the same violation, or one is a narrower case of the other. When one fires, read the other clause's **Check** and, if it holds too, put both on the same finding. The report checker rejects them as separate findings on the same line.

| Clauses | Shared fix |
| --- | --- |
| `A11Y-A11Y-001`, `COMP-A11Y-002` | Button trait on a custom tappable view |
| `LAY-UX-001`, `COMP-UX-002` | Confirmation or undo before a destructive action (`COMP-UX-002` only for uncommon actions that cannot be undone) |
| `COMP-UI-002`, `NAV-UI-001` | `NavigationView` replaced by `NavigationStack` or `NavigationSplitView` |
| `A11Y-A11Y-003`, `NAV-A11Y-001` | Screen-change notification after a custom page swap |
| `HAPT-UX-001`, `LAY-UX-009` | Haptic variant that matches the event |

When the twins' **Correct code** examples differ (`LAY-UX-001` shows `confirmationDialog`, `COMP-UX-002` shows `.alert`), follow the primary clause's example; either one satisfies both Checks.

Some pairs are the opposite case: their Checks split one problem between them, so a construct gets at most one of the two. The report checker rejects both on one construct.

| Clauses | Split |
| --- | --- |
| `LAY-A11Y-001`, `LAY-UI-001` | Target size, at 28x28 points. A tappable area under 28x28 pt is `LAY-A11Y-001` (error); one from 28x28 pt up to the 44x44 pt default is `LAY-UI-001` (warning). Measure the hit area the code produces, including any `contentShape` or padding. |
| `TYPO-A11Y-004`, `TYPO-A11Y-005` | A Dynamic Type cap, by what it applies to. A cap below `.accessibility3` on an app or scene root, a navigation container, a `ScrollView`, a `List` or body text is `TYPO-A11Y-004` (error). A small repeated control that stays small on purpose, such as a custom tab bar or a badge, is `TYPO-A11Y-005` (warning), fixed with the Large Content Viewer. The viewer never fixes `TYPO-A11Y-004`. |

## Writing the two fixes

The two fixes are different tools, not duplicates:

- **Minimal fix**: the smallest change that closes every clause on the finding. Keep the original lines where you can and add only what is missing.
- **Recommended fix**: the change you would ask for in code review, following the primary clause's **Correct code** or another approach its Check or title allows (`NAV-UI-001` accepts `NavigationStack` or `NavigationSplitView`). Typical moves: `Button` instead of `.onTapGesture`, `NavigationStack` instead of `NavigationView`, `confirmationDialog` instead of `actionSheet`, semantic system colours, accessibility lifted to the parent group.

Both fixes are complete, compilable replacements for the lines in `code_snippet`:

- Write out every line of the replacement, keeping the snippet's indentation. Never write `// ...`, `…`, or "rest unchanged" comments; the person or agent applying the fix replaces the snippet with exactly this text.
- Use only identifiers the surrounding code declares, plus system APIs.
- When the fix also needs lines elsewhere (a new `@State` or `@Environment` property in the same type, or a change in another file), split it into parts. Each part starts with a `// File: [project-relative path]` line. The first part replaces `code_snippet`; each later part has a second comment line saying where it goes, for example `// Add to struct AddPlantView, after the existing properties:`. When the main edit belongs in another file than the evidence (a sheet presented in `PlantListView` whose dismiss button belongs in `AddPlantView`), anchor the finding on the file that changes and mention the other in the description.
- If only one fix is reasonable because the violation is structural, make both fixes the same and say in the description that they match on purpose.
- Wording that users see (a VoiceOver label, a button title) follows the visible UI, for example `"Delete \(plant.name)"` next to a plant's name. evenbetter-repair decides whether a person has to confirm it.

Hard rules for fixes:

- An accessibility label contains the visible text verbatim, possibly with context added, so WCAG 2.5.3 Label in Name holds.
- Never hide an interactive element with `accessibilityHidden(true)`.
- No `Color(red:green:blue:)` or hex literals in a recommended fix; use a semantic asset colour or a system colour.
- Fixed `.black` or `.white` text is allowed only on a fill that does not follow the system background (a tinted button fill, an image), with the reason in the description. On adaptive backgrounds use `.primary`, `.secondary` or another semantic style, because `CLR-UI-002` flags fixed black and white there.

## Writing the AI fix prompt

`ai_fix_prompt` is what the user pastes into an AI coding agent such as Claude Code or Codex to apply the recommended fix. Make it self-contained:

- Lead with the absolute path and line range of every file the fix touches.
- State the clause ID, any related clause IDs, and the user impact in one sentence.
- Include the original snippet and the recommended replacement, both fenced with `swift`. For a multi-part fix, include every part with its `// File:` line.
- End with a one-line acceptance check, for example "the trash control is a `Button` with `role: .destructive`, a label, and a 44x44 pt content shape".

Keep the prose under about 120 words. The code blocks do not count toward that.

## WCAG cross-references

`wcag_criteria` holds one WCAG 2.2 success criterion number and `wcag_level` its level, or both are empty. The criterion's level must not be above the report's `wcag_level` target. Common mappings:

| Problem | Criterion |
| --- | --- |
| Image with no text alternative | 1.1.1 Non-text Content (A) |
| Prerecorded video with no captions | 1.2.2 Captions (Prerecorded) (A) |
| Prerecorded video with no audio description | 1.2.5 Audio Description (Prerecorded) (AA) |
| Control with no name or role (no label, no button trait) | 4.1.2 Name, Role, Value (A) |
| Related elements read separately | 1.3.1 Info and Relationships (A) |
| Colour is the only signal | 1.4.1 Use of Color (A) |
| Low text contrast | 1.4.3 Contrast (Minimum) (AA) |
| Low icon or control contrast | 1.4.11 Non-text Contrast (AA) |
| Fixed font sizes, text that does not scale | 1.4.4 Resize Text (AA) |
| Looping or auto-playing motion with no way to stop it | 2.2.2 Pause, Stop, Hide (A) |
| Screen with no title | 2.4.2 Page Titled (A) |
| VoiceOver focus leaves a custom modal for the content behind it | 2.4.3 Focus Order (A) |
| Swipe-only dismissal or other path-based gesture with no single-tap alternative | 2.5.1 Pointer Gestures (A) |
| Visible label missing from the accessible name | 2.5.3 Label in Name (A) |
| Drag-only action with no single-pointer alternative | 2.5.7 Dragging Movements (AA) |
| Tap target under 24 by 24 points, with no spacing around it | 2.5.8 Target Size (Minimum) (AA) |
| Delete with no confirmation or undo | 3.3.4 Error Prevention (Legal, Financial, Data) (AA) |
| Status change not announced | 4.1.3 Status Messages (AA) |

2.5.5 Target Size (Enhanced) and 2.3.3 Animation from Interactions are AAA; use them only when the report targets AAA. Check levels and wording on `https://www.w3.org/TR/WCAG22/`, not the Quick Reference, whose filters need JavaScript. `references/official-sources.md` lists the anchors. 2.5.8 asks for 24 by 24 CSS pixels, and for this comparison one iOS point counts as one CSS pixel. Apple's 44x44 pt guideline is stricter, so a 28x28 pt control can break the Apple clause and still meet 2.5.8; in that case leave the WCAG fields empty.

## How many findings to keep

Keep every verified finding; merging already removes the duplicates. Order the findings by severity (critical first), then by file path, then by line number, and number them `EB-001` upward in that order.

If the user asked for a limited audit (for example "the top 10"), keep the limit and add a `scan_context.notes` line saying how many verified findings were left out and at which severities. Never drop verified findings silently.

## Stage exit criteria

Move to stage `3-report` only when:

- Every finding has a primary `clause_id`, a `related_clause_ids` array, and a `hig_reference_url` equal to that clause's index `source_url`.
- No two findings share a construct and a fix, no twin pair is split across findings, and the two clauses of an exclusive pair (`LAY-A11Y-001` and `LAY-UI-001`, `TYPO-A11Y-004` and `TYPO-A11Y-005`) never sit on the same construct.
- Every severity follows the SKILL.md table for the finding's clauses.
- Both fixes are complete replacements with no elisions, and every multi-part fix labels each part with `// File:`.
- The findings are ordered and numbered `EB-001`, `EB-002`, and so on.
