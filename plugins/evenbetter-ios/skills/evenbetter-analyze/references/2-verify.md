# 2 Verify

## Role

Confirm each draft finding from stage `1-scan` against an authoritative source so the report only ships claims you can defend. Discard everything you cannot verify.

## Why this stage exists

Static pattern matching against the corpus is recall-heavy on purpose. Many draft findings fall apart on closer reading: a Swift expression that looks like a tap gesture turns out to be a private extension; a bare `Image` is decoratively scoped under a parent that already sets `accessibilityHidden(true)`; a `frame(width: 32)` belongs to an icon inside a tappable parent that meets the 44pt requirement on its own bounds. Verification is what separates an audit from a noise-generator.

## Process

1. Group draft findings by `clause_id` so you fetch each Apple URL once per audit. Read the canonical source on the first encounter and reuse it across findings that cite the same clause.
2. For every finding, do these checks before keeping it:
   - **Source check.** Resolve the corpus `source_url` for the clause via `WebFetch` (or `ref_read_url`). Skim the page for the exact rule the clause encodes. If the source no longer states the rule, drop the finding and flag the corpus drift in the audit log.
   - **Context check.** Re-read the source file around the captured snippet (about 20 lines above and 20 below). Confirm the violation actually applies in this context: parent modifiers, surrounding `if`/`#if` branches, `accessibility*` modifiers further up the chain, or sibling elements that already satisfy the clause.
   - **WCAG cross-reference.** When the clause maps to a WCAG 2.2 Success Criterion (commonly 1.1.1 Non-text Content, 1.3.1 Info and Relationships, 1.4.3 Contrast, 1.4.10 Reflow, 1.4.11 Non-text Contrast, 2.1.1 Keyboard, 2.4.3 Focus Order, 2.5.3 Label in Name, 2.5.5 Target Size, 4.1.2 Name/Role/Value), capture the criterion ID and conformance level from `https://www.w3.org/WAI/WCAG22/quickref/`. WCAG is a cross-reference, never the primary citation.
   - **Severity refinement.** Apply the mapping in `SKILL.md`. A `warning` clause with strong static evidence and direct user impact promotes to `high`; the same clause with broader uncertainty stays at `medium`.
3. Build the verified finding using the schema below. Discard anything missing a confirmed Apple HIG or Apple Developer Documentation URL — the report's `hig_reference_url` field is mandatory.
4. Stop verifying once you reach roughly 30 high-quality findings unless the user asked for an exhaustive audit. Severity-rank the survivors and trim the tail of `low` findings before stage 3. Quality beats volume — a 12-issue report that is 100% verified is more useful than a 50-issue report with skim quality.

## Verified finding schema

Every entry that survives verification must populate every field. Stage `3-report` will refuse to render a finding with missing fields.

```json
{
  "id": "string, stable per audit (e.g., \"EB-001\", \"EB-002\")",
  "clause_id": "string, original corpus ID, kept for traceability",
  "title": "string, short imperative title rewritten in user-facing language",
  "description": "string, 1-3 sentences explaining the user impact in concrete terms",
  "severity": "critical | high | medium | low",
  "wcag_criteria": "string, e.g., \"2.5.5\" or \"\" if not applicable",
  "wcag_level": "A | AA | AAA | \"\"",
  "hig_reference_url": "string, canonical Apple HIG or Apple Developer URL",
  "file_path": "string, project-relative path",
  "line_number": "integer, first offending line",
  "code_snippet": "string, exact code captured in stage 1",
  "minimal_fix": "string, the smallest correct change that closes the violation",
  "recommended_fix": "string, the best-practice fix that future-proofs the code",
  "ai_fix_prompt": "string, paste-ready prompt for an AI coding agent",
  "language": "swift"
}
```

## Writing the two fixes

The dual-fix model is the headline remediation feature of this skill. Treat the two columns as different tools, not duplicates.

- **Minimal fix.** The smallest mechanical change that resolves the violation. One added modifier, a single argument change, a renamed identifier. The reader should be able to apply it without restructuring anything around it. Prefer to keep the original code lines intact and add only what is missing.
- **Recommended fix.** The change you would request in code review: the system-native or Apple-blessed approach. Replace `onTapGesture` with `Button`, replace `NavigationView` with `NavigationStack`, lift accessibility into the parent group, switch to semantic system colors, swap `actionSheet` for `confirmationDialog`. The recommended fix often touches more lines and may rename or move elements; that is fine.

Both fixes must be valid Swift that compiles in context. Both must reference the same identifiers found in the captured snippet. If only one solution is reasonable (for example, there is no minimal patch — the violation is structural), set the minimal fix to the same content as the recommended fix and explain in the description that they intentionally match.

## Writing the AI fix prompt

The `ai_fix_prompt` is what the user pastes into Claude Code, Cursor, or Copilot to apply the recommended fix automatically. Make it self-contained:

- Lead with the absolute file path and the line range to edit.
- State the corpus clause ID and the user-impact reason in one sentence.
- Include the original code block and the recommended replacement, both fenced with `swift`.
- End with a one-line acceptance check the agent can run mentally (e.g., "the `Button` retains its `Image(systemName:)` and gains `.accessibilityLabel(\"Close\")`").

Keep prompts under ~200 words. They are designed to be skimmed and pasted, not read.

## Stage exit criteria

Move to stage `3-report` only when:

- Every surviving finding has a non-empty `hig_reference_url`.
- Severities are consistent with the SKILL.md mapping.
- Both fixes compile against the snippet's identifiers.
- IDs are stable and sequential within the audit (`EB-001`, `EB-002`, …).
