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
| `fix_options` | array | 1-4 concrete remediation alternatives the fixer can present to the user (see Fix Options). |
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

## Fix Options

`fix_options` is the structured menu of remediation alternatives the Fix skill presents to the user before editing. The recommended option must mirror the same intent as the violation's top-level `fix_description`, `fix_code`, and `ai_fix_prompt`; alternatives offer different but legitimate ways to satisfy the same Apple HIG, SwiftUI, or accessibility outcome.

Each entry in `fix_options[]`:

| Field | Type | Allowed values / shape |
|---|---|---|
| `id` | string | Stable kebab-case option ID, unique within the violation. Examples: `enlarge-frame`, `wrap-in-button`, `move-to-toolbar`. |
| `label` | string | Short user-facing label (≤ 60 chars), suitable as an `AskUserQuestion` choice. |
| `description` | string | One-sentence explanation of what changes in the source and why it satisfies the rule. |
| `kind` | string | `minimal` \| `structural` \| `alternative-component` \| `accessibility-only` \| `defer-to-user`. |
| `recommended` | boolean | Exactly one option per violation has `recommended: true`. |
| `code` | string | Optional corrected snippet in full mode; omit in budget mode. |
| `ai_fix_prompt` | string | Optional, option-specific fix prompt. When omitted, the Fix skill reuses the violation's top-level `ai_fix_prompt` for the recommended option. |

Rules:

- Provide 1 entry when only one reasonable remediation exists. Provide 2-4 entries when multiple legitimate paths exist (e.g., enlarge tap target vs. wrap content in a `Button` vs. promote to a Tab Bar item).
- Mark exactly one entry `recommended: true` and place the same content in the violation's `fix_description`, `fix_code`, and `ai_fix_prompt`.
- Keep options mutually distinct — do not list two near-identical entries.
- Do not invent options that violate the cited rule. Each option must end with the file in compliance with `rule_id`.
- The Fix skill may add `defer-to-user` style choices ("skip", "defer", "reject") at runtime; analyzers must not include those in `fix_options`.

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
  "fix_options": [
    {
      "id": "use-dynamic-type",
      "label": "Use Dynamic Type token (.title)",
      "description": "Replace the fixed point size with the .title text style so the label scales with user settings.",
      "kind": "minimal",
      "recommended": true,
      "code": "Text(\"Title\").font(.title)"
    },
    {
      "id": "custom-scaled-font",
      "label": "Adopt @ScaledMetric for custom size",
      "description": "Keep the visual weight but make the size respect Dynamic Type via @ScaledMetric.",
      "kind": "structural",
      "recommended": false,
      "code": "@ScaledMetric var titleSize: CGFloat = 28\nText(\"Title\").font(.system(size: titleSize))"
    }
  ],
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
  "fix_options": [
    {
      "id": "use-dynamic-type",
      "label": "Use Dynamic Type token (.title)",
      "description": "Replace the fixed point size with the .title text style so the label scales with user settings.",
      "kind": "minimal",
      "recommended": true
    }
  ],
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
- `fix_options` must contain 1-4 entries; one option must be `recommended: true`; option `id` values must be unique within the violation; `kind` must use one of the allowed values; in budget mode, omit each option's `code` field.
- `fix_options[].label` and `fix_options[].description` must be filled, distinct between options, and aligned with the cited rule.
- `state.status = "duplicate_of"` requires `state.duplicateOf`; every other status requires `state.duplicateOf = null`.
