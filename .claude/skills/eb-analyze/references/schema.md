# Violation Schema

Each violation object has these fields in `full` mode:

| Field | Type | Allowed values / shape |
|---|---|---|
| `rule_id` | string | e.g. `TYPO-UI-001` |
| `severity` | string | `error` \| `warning` \| `info` |
| `dimension` | string | `ui` \| `ux` \| `accessibility` |
| `domain` | string | `typography` \| `color-theming` \| `components-patterns` \| `navigation-flow` \| `layout-interaction` \| `accessibility` |
| `file_path` | string | path relative to `projectPath` |
| `line_number` | integer | 1-based line number of the offending code |
| `code_snippet` | string | the offending code |
| `summary` | string | one-sentence description |
| `why_fix` | string | why this matters (user impact, HIG/WCAG rationale) |
| `guideline_reference` | object | `{ "label": string, "url": string }` - URL must resolve to a real HIG / developer.apple.com / WCAG page |
| `fix_description` | string | recommended remediation in prose |
| `fix_code` | string | corrected code snippet |
| `ai_fix_prompt` | string | self-contained prompt another AI could follow to apply the fix |
| `auto_fixable` | boolean | whether the fix can be applied deterministically |

Budget mode drops `why_fix`, `fix_code`, and `auto_fixable`; keeps `fix_description` and `ai_fix_prompt`.

## Full Mode Object

```json
{
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
  "auto_fixable": true
}
```

## Budget Mode Object

```json
{
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
  "ai_fix_prompt": "Self-contained prompt for another AI to apply the fix."
}
```

## Validation Rules

- No extra fields.
- No omitted fields for the active mode.
- Enum values must match exactly.
- `rule_id` must follow `<PREFIX><DIMENSION>-<NNN>`, where `<DIMENSION>` is `UI`, `UX`, or `A11Y`.
- `line_number` must be a positive 1-based integer.
- `code_snippet` must be the offending code, not a paraphrase.
- `guideline_reference.url` must be a verified Apple HIG, developer.apple.com, or WCAG URL.
