# Corpus Schema

The EvenBetter iOS corpus is a version-controlled markdown corpus. It gives skills a stable, traceable rule layer without requiring a YAML database or a separate repository.

## File Frontmatter

Every domain file starts with:

```yaml
---
corpus_version: development
domain: typography
platform: ios
last_reviewed: 2026-05-02
---
```

Use `corpus_version: development` during active development. Formal releases may replace this with a release version or tag once the repository adopts a release process. Until then, cite the commit SHA for reproducibility.

## Clause Format

Each clause is one H2 section:

````markdown
## TYPO-UI-001 - Prefer system text styles

**Severity:** warning
**Dimension:** ui
**Platform:** ios
**Source:** [Apple HIG: Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
**Retrieved:** 2026-05-02

**Check.** Flag the static condition to detect.

**Why.** Explain the user impact or guideline rationale.

**Correct code.**

```swift
Text("Account").font(.title2)
```
````

Optional:

```markdown
**WCAG:** WCAG 2.2 - Target Size Minimum
```

## Taxonomy

Clause IDs use:

```text
<DOMAIN>-<DIMENSION>-<NNN>
```

Domains:

- `TYPO`: typography
- `CLR`: color and theming
- `COMP`: components and patterns
- `LAY`: layout and interaction
- `NAV`: navigation and flow
- `A11Y`: accessibility

Dimensions:

- `UI`: platform visual or component convention
- `UX`: user-flow, interaction, or decision-safety issue
- `A11Y`: accessibility or assistive-technology issue

Keep IDs stable. If a rule is renamed but its detection meaning remains the same, keep the ID. Create a new ID when the rule's meaning changes enough that old analyzer outputs should not be treated as the same clause.

## Severity

- `error`: likely user harm, accessibility blocker, destructive action risk, or a high-confidence issue the validator should recheck.
- `warning`: actionable conformance issue with meaningful user impact but lower severity or broader static uncertainty.
- `info`: quality or polish issue that improves consistency but is not blocking.

## Contribution Rules

- Add clauses to exactly one domain file.
- Use one source URL per clause and record the retrieval date.
- Prefer Apple HIG, Apple Developer, or W3C WCAG sources.
- Keep examples short and SwiftUI-specific.
- Update `index.json` whenever clause metadata changes.
- Run the corpus consistency checks documented in the repository `AGENTS.md` before committing.

Conceptually, the taxonomy supports traceability from mobile usability criteria and accessibility standards into concrete SwiftUI checks, including the kind of design-heuristic structure discussed by Hoehle and Venkatesh and mobile accessibility mappings such as WCAG2Mobile.
