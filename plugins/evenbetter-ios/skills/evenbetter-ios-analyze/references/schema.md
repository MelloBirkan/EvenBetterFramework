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
| `guideline_reference` | object | `{ "label": string, "url": string }` - URL must resolve to a real Apple HIG or Apple Developer page |
| `fix_description` | string | recommended remediation in prose |
| `ai_fix_prompt` | string | analyzer-generated, self-contained prompt another AI could follow to apply the fix |
| `state` | object | Decision state for this violation. |

Full mode also requires:

| Field | Type | Allowed values / shape |
|---|---|---|
| `why_fix` | string | why this matters to iOS users and how it relates to Apple HIG, SwiftUI, or accessibility rationale |
| `fix_code` | string | corrected code snippet |
| `auto_fixable` | boolean | whether the fix can be applied deterministically |

Budget mode drops `why_fix`, `fix_code`, and `auto_fixable`; keeps all shared fields.

## Fix Prompt Ownership

The analyzer is responsible for creating `ai_fix_prompt` directly in each violation JSON object. Validator and fixer skills must not invent replacement prompts.

Each `ai_fix_prompt` must:

- Identify the exact finding by `id` when available, `rule_id`, `file_path`, and `line_number`.
- State the concrete source problem and the expected standards-compliant outcome.
- Reference the analyzer's `fix_description` and, in full mode, the intended `fix_code` direction without requiring blind copy-paste.
- Include acceptance criteria specific enough for a fixer agent to know when the issue is remediated.
- Stay scoped to the cited issue and avoid unrelated refactors, formatting churn, or broad redesign.

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

Only analyzer, validator, and fixer skills may mutate `state`. Analyzer creates the default state and may carry forward the latest prior state for the same `id`. Validator may set unsupported findings to `rejected` with `decidedBy: "validator"` and may set report/run validation status, but must not override user rejection or deferral decisions. Fixer records user decisions and completed fix attempts in the originating analyzer report.

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
  "why_fix": "Why this matters to iOS users and how it relates to Apple HIG, SwiftUI, or accessibility rationale.",
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
- `rule_id` must follow `<PREFIX>-<DIMENSION>-<NNN>`, where `<DIMENSION>` is `UI`, `UX`, or `A11Y`, and must match a clause ID in `../../corpus/index.json`.
- `line_number` must be a positive 1-based integer.
- `code_snippet` must be the offending code, not a paraphrase.
- `guideline_reference.url` must be a verified Apple HIG or Apple Developer URL.
- `ai_fix_prompt` must be non-empty, grounded in the violation fields, and specific enough to execute without adding new remediation requirements.
- `state.status = "duplicate_of"` requires `state.duplicateOf`; every other status requires `state.duplicateOf = null`.
