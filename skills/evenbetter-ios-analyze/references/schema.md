# Violation Schema

Every violation object carries a stable identity and a mutable state block in both `full` and `budget` modes.

## Shared Fields

| Field | Type | Allowed values / shape |
|---|---|---|
| `id` | string | Stable ID in the form `v_<sha256-prefix>`. |
| `rule_id` | string | e.g. `TYPO-UI-001` |
| `severity` | string | `error` \| `warning` \| `info` |
| `dimension` | string | `ui` \| `ux` \| `accessibility` |
| `domain` | string | `typography` \| `color-theming` \| `components-patterns` \| `navigation-flow` \| `layout-interaction` \| `accessibility` |
| `file_path` | string | path relative to `projectPath` |
| `line_number` | integer | 1-based line number of the offending code |
| `code_snippet` | string | the offending code |
| `summary` | string | one-sentence description |
| `guideline_reference` | object | `{ "label": string, "url": string }` - URL must resolve to a real HIG / developer.apple.com / WCAG page |
| `fix_description` | string | recommended remediation in prose |
| `ai_fix_prompt` | string | self-contained prompt another AI could follow to apply the fix |
| `state` | object | Decision state for this violation. |

Full mode also requires:

| Field | Type | Allowed values / shape |
|---|---|---|
| `why_fix` | string | why this matters (user impact, HIG/WCAG rationale) |
| `fix_code` | string | corrected code snippet |
| `auto_fixable` | boolean | whether the fix can be applied deterministically |

Budget mode drops `why_fix`, `fix_code`, and `auto_fixable`; keeps all shared fields.

## Stable ID

Generate `id` after normalizing the domain result and before grouping into `files[]`.

Use this hash input, joined with newline characters:

1. `rule_id`, trimmed and uppercased.
2. `file_path`, trimmed, made relative to `projectPath`, and normalized to POSIX `/` separators.
3. Anchor string: use the smallest enclosing Swift symbol name when it can be identified confidently; otherwise use `line:<line_number>`.
4. Normalized message: use `summary` when present, otherwise the domain finding message; trim, lowercase, and collapse internal whitespace to one space.

Compute SHA-256 over the UTF-8 hash input and set `id` to `v_` plus the first 24 lowercase hex characters. The same underlying finding must receive the same `id` across analyzer runs. If a later run can confidently match the same finding despite a changed generated ID, keep the new `id` and set `state.status` to `duplicate_of` with `state.duplicateOf` pointing to the earlier violation ID.

## State Object

Every violation must include:

```json
{
  "status": "open",
  "decidedIn": null,
  "decidedBy": null,
  "reason": null,
  "duplicateOf": null
}
```

| Field | Type | Allowed values / shape |
|---|---|---|
| `status` | string | `open` \| `fixed` \| `rejected` \| `deferred` \| `duplicate_of` |
| `decidedIn` | integer or null | Analyzer run number where the decision was made. |
| `decidedBy` | string or null | `user` \| `fix-skill` \| `validator` |
| `reason` | string or null | Free-text note for rejected or deferred decisions. |
| `duplicateOf` | string or null | Earlier violation ID when `status` is `duplicate_of`; otherwise null. |

Only analyzer, validator, and fixer skills may mutate `state`. Analyzer creates the default state and may carry forward the latest prior state for the same `id`. Validator may set report/run validation status but must not change user rejection or deferral decisions. Fixer records user decisions and completed fix attempts in the originating analyzer report.

## Full Mode Object

```json
{
  "id": "v_0123456789abcdef01234567",
  "rule_id": "TYPO-UI-001",
  "severity": "warning",
  "dimension": "ui",
  "domain": "typography",
  "file_path": "relative/path.swift",
  "line_number": 1,
  "code_snippet": "Text(\"Title\").font(.system(size: 28))",
  "summary": "One-sentence description of the violation.",
  "why_fix": "Why this matters to users and how it relates to HIG or WCAG.",
  "guideline_reference": {
    "label": "Apple HIG: Typography",
    "url": "https://developer.apple.com/design/human-interface-guidelines/typography"
  },
  "fix_description": "Recommended remediation in prose.",
  "fix_code": "Text(\"Title\").font(.title)",
  "ai_fix_prompt": "Self-contained prompt for another AI to apply the fix.",
  "auto_fixable": true,
  "state": {
    "status": "open",
    "decidedIn": null,
    "decidedBy": null,
    "reason": null,
    "duplicateOf": null
  }
}
```

## Budget Mode Object

```json
{
  "id": "v_0123456789abcdef01234567",
  "rule_id": "TYPO-UI-001",
  "severity": "warning",
  "dimension": "ui",
  "domain": "typography",
  "file_path": "relative/path.swift",
  "line_number": 1,
  "code_snippet": "Text(\"Title\").font(.system(size: 28))",
  "summary": "One-sentence description of the violation.",
  "guideline_reference": {
    "label": "Apple HIG: Typography",
    "url": "https://developer.apple.com/design/human-interface-guidelines/typography"
  },
  "fix_description": "Recommended remediation in prose.",
  "ai_fix_prompt": "Self-contained prompt for another AI to apply the fix.",
  "state": {
    "status": "open",
    "decidedIn": null,
    "decidedBy": null,
    "reason": null,
    "duplicateOf": null
  }
}
```

## Validation Rules

- No omitted fields for the active mode.
- No extra fields beyond the active mode object shape.
- Enum values must match exactly.
- `id` must start with `v_` and must be generated from the stable ID rule above.
- `rule_id` must follow `<PREFIX><DIMENSION>-<NNN>`, where `<DIMENSION>` is `UI`, `UX`, or `A11Y`.
- `line_number` must be a positive 1-based integer.
- `code_snippet` must be the offending code, not a paraphrase.
- `guideline_reference.url` must be a verified Apple HIG, developer.apple.com, or WCAG URL.
- `state.status = "duplicate_of"` requires `state.duplicateOf`; every other status requires `state.duplicateOf = null`.
