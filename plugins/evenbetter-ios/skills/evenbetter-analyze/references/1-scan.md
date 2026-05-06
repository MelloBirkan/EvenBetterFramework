# 1 Scan

## Role

Walk the Swift sources of the target repository and produce a draft findings list grounded in the EvenBetter iOS corpus.

## Process

1. Resolve the project root. Default to the current working directory. If `.evenbetter/<name>/` already exists for this project, reuse `<name>`; otherwise derive `<name>` from the project folder in kebab-case.
2. Detect Swift sources. Use `Glob`/`rg --files` to gather files matching `**/*.swift`. Skip directories that are clearly not the user's source: `.build/`, `Pods/`, `Carthage/`, `DerivedData/`, `.swiftpm/`, `Package.resolved`, generated `*.generated.swift`, snapshot-test reference data, and any path containing `/Tests/` Vendor or `/Vendor/`.
3. Detect the SwiftUI surface area. Quickly grep for `import SwiftUI`, `@main`, `WindowGroup`, `App {`, and target file count to record `framework`, `files_scanned`, `frameworks`, and `framework_versions` for the report's `scan_context`.
4. Load corpus metadata. Read `../../corpus/index.json` once to enumerate clause IDs, severities, source URLs, and domain file paths. Treat the index as the authoritative list of detection targets.
5. For each domain that has clauses present in the index, lazy-load the matching `../../corpus/ios/<domain>.md` file the first time a clause from that domain triggers. Do not pre-read every domain.
6. Match each clause's **Check** description against the source. Use targeted `rg` searches per clause family (see Detection Patterns below) instead of monolithic regex sweeps. When a candidate match is found, read the surrounding lines (about 5 above and 10 below) so the snippet captures the relevant SwiftUI declaration, modifier chain, or closure body.
7. Record each candidate finding in memory as a structured object using the schema in `3-report.md`. Do not write to disk yet — verification is a separate stage.
8. Track scan statistics: total Swift files scanned, scan duration, frameworks detected, and any custom utilities or design systems referenced by name (`Color.appBackground`, `Theme.spacing`, custom `ViewModifier` types) for the report's `scan_context`.

## Detection Patterns

Use these starting `rg` patterns to locate candidate code. Adjust per clause; the goal is high recall — verification removes false positives.

| Domain | Pattern hint |
| --- | --- |
| `A11Y-UI-001` | `Image\(systemName:`, `Image\("[^"]+"\)`, image-only `Button` literals without trailing `accessibilityLabel` within ~3 lines |
| `A11Y-UI-002` | Decorative `Image`, `Divider`, `Rectangle()` backgrounds without `accessibilityHidden(true)` |
| `A11Y-UI-003` | `HStack`/`VStack` containing two or more `Text` siblings without `accessibilityElement(children: .combine)` |
| `A11Y-UX-001` | `withAnimation`, `matchedGeometryEffect`, looping `Animation`, `phaseAnimator` without an `accessibilityReduceMotion` guard |
| `A11Y-UX-002` | `onTapGesture`, custom gestures, swipe actions without `accessibilityHint` |
| `A11Y-A11Y-001` | `onTapGesture` or `gesture(...)` without `accessibilityAddTraits(.isButton)` |
| `A11Y-A11Y-002` | Custom slider, progress, rating, or stepper-like views without `accessibilityValue` |
| `A11Y-A11Y-003` | Manual screen routing or onboarding step changes without `AccessibilityNotification.ScreenChanged().post()` |
| `CLR-A11Y-001`/`CLR-A11Y-002`/`CLR-UX-001` | Hard-coded `Color(red:green:blue:)`, hex literals, status text relying solely on red/green |
| `CLR-UI-001`/`CLR-UI-002`/`CLR-UI-003` | `Color.black`, `Color.white`, custom palettes without dark-mode asset variants |
| `COMP-A11Y-001`/`COMP-A11Y-002` | Custom shapes used as buttons without `accessibilityAddTraits(.isButton)` |
| `COMP-UI-001` | `onTapGesture` used for actions where `Button` would suffice |
| `COMP-UI-002` | `NavigationView` instead of `NavigationStack` |
| `COMP-UI-003` | `actionSheet(...)` instead of `confirmationDialog` |
| `COMP-UX-001`/`COMP-UX-002`/`LAY-UX-001` | Destructive `Button` without `role: .destructive`, missing alert/confirmation for destructive paths |
| `LAY-A11Y-001`/`LAY-UI-001` | `frame(width:` / `frame(height:` smaller than 44 around tappable controls |
| `LAY-A11Y-002`/`LAY-UI-002` | `ignoresSafeArea` on interactive content, layouts that push content under navigation/tab bars |
| `LAY-UI-003`/`LAY-UI-004` | Loading via `if isLoading` without `ProgressView`, empty states with bare strings |
| `LAY-UX-002` | State changes without `sensoryFeedback` for high-impact transitions |
| `NAV-A11Y-001`/`NAV-A11Y-002` | Custom modal flows without `cancellationAction` toolbar item or screen-change notification |
| `NAV-UI-001`/`NAV-UI-002`/`NAV-UI-003` | Missing `navigationTitle`, hidden back buttons, ad-hoc replacements for `NavigationStack`/`NavigationSplitView` |
| `NAV-UX-001`/`NAV-UX-002` | Creation flows pushed into the stack instead of presented as sheets, deep `NavigationLink` chains |
| `TYPO-A11Y-001` | `font(.system(size: <11))`, `font(.custom(name, size: <11))` |
| `TYPO-A11Y-002`/`TYPO-A11Y-003` | `Text(...).frame(height:` constants, `minimumScaleFactor` on Dynamic Type body styles |
| `TYPO-UI-001`/`TYPO-UI-002`/`TYPO-UI-003` | Numeric `Font.system(size:)` instead of `.title2`/`.headline`, `Font.custom` without `relativeTo`, weight-only hierarchy |
| `TYPO-UX-001`/`TYPO-UX-002` | `lineLimit(1)` on important content, `.lineSpacing` overrides on body text |

When a clause's **Check** mentions multiple structural cues, capture the dominant cue first and let stage `2-verify` decide whether the surrounding context fits.

## Snippet capture

Extract a minimal, faithful code snippet for each finding:

- Start at the line where the candidate violation begins (e.g., the modifier chain root view or the offending modifier).
- Include up to 12 lines, ending at the closing brace or end of the modifier chain.
- Preserve original indentation. Do not trim, normalize, or annotate the snippet.
- If the candidate spans more than 12 lines, take the first 6 and the last 6 with an unobtrusive `// …` separator only when the omitted middle is non-essential to the violation.

## Output of this stage

The result of stage 1 is an in-memory list of draft findings, ready for stage 2. Each draft finding holds:

- `clause_id` — corpus clause ID, kept for traceability through verification.
- `file_path` — path relative to the project root.
- `line_number` — first offending line.
- `code_snippet` — raw code as captured.
- `language` — always `swift` for this skill.
- Initial `severity`, `title`, `description` copied from the corpus clause's metadata. Verification may refine the severity using the mapping in `SKILL.md`.

Do not skip stage `2-verify`. Static matches almost always include false positives — for example, a custom view that already provides accessibility through a parent modifier, a `Color.black` used only for a print preview, or a `frame(height: 32)` on a non-interactive label.
