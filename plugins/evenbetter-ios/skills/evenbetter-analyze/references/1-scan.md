# 1 Scan

Contents: Role, Process, Detection patterns, Snippet capture, Output of this stage.

## Role

Walk the Swift sources of the target repository and produce a draft findings list grounded in the EvenBetter iOS corpus. Paths here are relative to the skill's SKILL.md folder, so the corpus is `../../corpus/`.

## Process

1. Resolve the project root. Default to the current working directory. Resolve `[project]` and `project_name` as the Artifact rules in SKILL.md describe: `[project]` is the kebab-case folder under `.evenbetter/`, and `project_name` is the app's human-readable name.
2. Find the Swift sources with `Glob` or `rg --files -g '*.swift'`. Skip code that is not the user's: `.build/`, `Pods/`, `Carthage/`, `DerivedData/`, `.swiftpm/`, generated `*.generated.swift` files, snapshot-test reference data, and any path containing `/Tests/` or `/Vendor/`.
3. Record the scan context:
   - `framework` is a top-level report field, for example `SwiftUI` or `SwiftUI + UIKit`. It does not go inside `scan_context`.
   - `scan_context.frameworks` lists the UI and data frameworks in use (`SwiftUI`, `UIKit`, `Observation`, `SwiftData`).
   - `scan_context.framework_versions` maps each framework to a short string. Take the deployment target from the `.xcodeproj` or `Package.swift`, for example `iOS 17.0 deployment target`. When the repository has neither, write the minimum implied by the APIs it uses and mark it, for example `iOS 17+ (inferred)`.
   - `scan_context.files_scanned`, `scan_duration`, and any design systems, component patterns and custom utilities referenced by name (`Color.appBackground`, `Theme.spacing`, custom `ViewModifier` types).
4. Read `../../corpus/index.json` once. It lists every clause ID with its severity, `source_url` and `file_path`. The `file_path` values are relative to the plugin root (`corpus/ios/accessibility.md`), so from the skill folder the file is `../../corpus/ios/accessibility.md`. Treat the index as the complete list of detection targets.
5. Load a domain file the first time one of its clauses triggers, and cache it. Do not pre-read every domain.
6. Match each clause's **Check** against the source with targeted `rg` searches (see Detection patterns). Read each Check for its intent: it describes the common form of the violation, not the only one. A control built as `Image` plus `.onTapGesture` is a button for button-specific clauses, and a deprecated `NavigationView` root counts for clauses written about `NavigationStack` roots. When a candidate matches, read about 5 lines above and 10 below so the snippet captures the declaration, modifier chain or closure involved.
7. Several clauses often fire on one construct. For each candidate, record every clause that fires on it; stage `2-verify` decides which ones share a fix and merges them.
8. Only corpus clauses become drafts. When you notice a real problem that no clause covers (for example a `NavigationLink(value:)` with no matching `navigationDestination`), keep a one-line note for stage 2. It ends up in the description of a related finding or in `scan_context.notes`.
9. Keep the drafts in memory. Stage 1 writes nothing to disk.

## Detection patterns

Starting `rg` patterns per clause. Adjust per project; aim for high recall, because stage 2 removes false positives. The index stays the authority on which clauses exist.

| Clauses | Pattern hint |
| --- | --- |
| `A11Y-UI-001` | `Image\(systemName:`, `Image\("[^"]+"\)`, image-only `Button` labels and toolbar icons without `accessibilityLabel` within about 3 lines |
| `A11Y-UI-002` | Decorative `Image`, `Divider`, `Rectangle()` backgrounds without `accessibilityHidden(true)` |
| `A11Y-UI-003` | `HStack`/`VStack` holding two or more `Text` siblings without `accessibilityElement(children: .combine)` |
| `A11Y-UI-004` | `.accessibilityLabel("…")` literals that contain the whole word button, checkbox, toggle, tab, link, selected, checked or unchecked (any case); ternary labels whose branches name a state, such as Favorite and Favorited. Skip ternaries that swap actions, such as Play and Pause |
| `A11Y-UX-001` | `withAnimation`, `matchedGeometryEffect`, `repeatForever`, `phaseAnimator`, `symbolEffect` without an `accessibilityReduceMotion` guard |
| `A11Y-UX-002` | `onTapGesture`, custom gestures and swipe actions whose result is not obvious, without `accessibilityHint` |
| `A11Y-A11Y-001`, `COMP-A11Y-002` | `onTapGesture` or `gesture(...)` that triggers an action without `accessibilityAddTraits(.isButton)` |
| `A11Y-A11Y-002` | Custom slider, progress, rating or stepper-like views without `accessibilityValue` |
| `A11Y-A11Y-003`, `NAV-A11Y-001` | Manual screen routing, page swaps or onboarding steps without `AccessibilityNotification.ScreenChanged` |
| `A11Y-A11Y-004` | `Button("X")`, or a `Label` or `Text` inside a control, followed by `.accessibilityLabel("Y")` where Y does not begin with the words of X and no `.accessibilityInputLabels` contains X; icon-only buttons whose label has 4 or more words and no input labels |
| `A11Y-A11Y-005` | `onLongPressGesture`, `DragGesture`, `MagnifyGesture`, `RotateGesture` and `onTapGesture(count: 2)` on a view with no `accessibilityAction(named:)` or `accessibilityActions`, no `contextMenu` and no visible button for the same action. `.swipeActions` and `.onDelete` rows with no `EditButton` or button on the detail screen are lower-confidence matches: Apple's `swipeActions` page does not say whether VoiceOver exposes them, so say in the description that the finding rests on the HIG's request for an onscreen alternative |
| `A11Y-A11Y-006` | `Chart {` marks whose values need a unit or a date and set no mark-level `accessibilityLabel` or `accessibilityValue`; `Canvas` or `Path` charts and chart images with no `accessibilityChartDescriptor`, no `accessibilityRepresentation` and no text alternative; charts with `accessibilityHidden(true)` and no text alternative |
| `A11Y-A11Y-007` | State or views named toast, snackbar, banner or statusMessage, shown on a state change, in files with no `AccessibilityNotification.Announcement`. Skip `.alert` and `.confirmationDialog` |
| `A11Y-A11Y-008` | Only when the project has a String Catalog (`*.xcstrings`) or several `.lproj` folders: `accessibilityLabel`, `accessibilityHint`, `accessibilityValue`, `accessibilityInputLabels` or `accessibilityAction(named:)` called with a non-literal argument. Trace it to a fixed `let x = "…"` or an interpolated `String`; formatter output and user content are fine |
| `A11Y-A11Y-009` | `appliesMediaSelectionCriteriaAutomatically = false`, `.select(nil, in:`, `setMediaSelectionCriteria`, and subtitle or audio options picked when an item loads. Web embeds, GIF or image-sequence video and third-party players go into a `Manual check:` note in `scan_context.notes` |
| `CLR-A11Y-001`, `CLR-A11Y-002`, `CLR-UX-001` | `Color(red:green:blue:)`, hex literals, fixed `.black`/`.white` text on coloured fills, status shown only in red or green |
| `CLR-A11Y-003` | `AsyncImage`, `Image(uiImage:)`, photo assets, `VideoPlayer(`, `AVPlayerLayer`, `AVCaptureVideoPreviewLayer` and `MKMapSnapshotter` output with no `accessibilityIgnoresInvertColors`. Skip `Image(systemName:)` |
| `CLR-UI-001`, `CLR-UI-002`, `CLR-UI-003` | `Color.black`, `Color.white`, custom palettes without dark-mode asset variants |
| `COMP-A11Y-001` | Custom recreations of system controls (toggles, pickers, steppers) built from shapes and gestures |
| `COMP-UI-001` | `.onTapGesture` on `Text`, `Image`, stacks or rows for primary actions where `Button` fits |
| `COMP-UI-002`, `NAV-UI-001` | `NavigationView`; a single `NavigationStack` for a sidebar and detail layout |
| `COMP-UI-003` | `actionSheet(` instead of `confirmationDialog` |
| `COMP-UX-001` | Delete, remove, reset, discard or sign-out actions, in a `Button` or a tap gesture, without `role: .destructive` |
| `COMP-UX-002`, `LAY-UX-001` | Destructive or irreversible actions that run immediately, with no `.alert`, `.confirmationDialog` or undo |
| `HAPT-UX-001`, `LAY-UX-009` | `.sensoryFeedback(` whose variant does not match the event, for example `.error` on a successful save |
| `HAPT-UX-002` | The same outcome played with different feedback in different places |
| `HAPT-UX-003` | `.sensoryFeedback` or `CHHapticEngine` playback with no visible or audible change for the same event |
| `HAPT-UX-004` | `CHHapticEngine` used without checking `capabilitiesForHardware().supportsHaptics` |
| `LAY-A11Y-001`, `LAY-UI-001` | `.frame(width:` or `.frame(height:` under 44 on tappable controls, icon-only buttons without `contentShape`. A hit area under 28x28 pt is `LAY-A11Y-001`; 28x28 pt up to 44x44 pt is `LAY-UI-001` |
| `LAY-A11Y-002`, `LAY-UI-002` | `ignoresSafeArea` on interactive content, content pushed under navigation or tab bars |
| `LAY-UI-003`, `LAY-UI-004` | `if isLoading` without `ProgressView`; lists, grids or search results that show nothing, or a bare string, when empty |
| `LAY-UX-002` | High-impact state changes with no `sensoryFeedback` |
| `NAV-A11Y-002` | `.sheet` or `.fullScreenCover` content with no visible Cancel, Close or Done control, or with Done alone |
| `NAV-A11Y-003` | Custom Dialog, Popup, Overlay or Panel views, and `ZStack` or `.overlay` blocks gated on `isShowing` or `isPresented`, with no `.accessibilityAddTraits(.isModal)` or no `.accessibilityAction(.escape)` |
| `NAV-UI-002`, `NAV-UI-003` | Top-level destinations without `navigationTitle`; `navigationBarBackButtonHidden(true)` or a custom back control that differs from the system one |
| `NAV-UX-001`, `NAV-UX-002` | Creation flows pushed onto the stack instead of presented as sheets; deep `NavigationLink` chains |
| `TYPO-A11Y-001` | `.font(.system(size:` or `.font(.custom(` with a size under 11 |
| `TYPO-A11Y-002`, `TYPO-A11Y-003` | `Text(...)` with a fixed `.frame(height:`; `minimumScaleFactor` on body text |
| `TYPO-A11Y-004` | `.dynamicTypeSize(` with an upper bound below `.accessibility3`, or a fixed value, on an app or scene root, a navigation container, a `ScrollView` or `List`, or body text. A cap on a small repeated control such as a tab bar or a badge is `TYPO-A11Y-005` instead |
| `TYPO-A11Y-005` | Custom TabBar, BottomBar, Toolbar or FloatingButton views that cap `dynamicTypeSize`, use a fixed `.font(.system(size:))` or fix their icon frames, and have no `accessibilityShowsLargeContentViewer`. The viewer on body text or list rows does not answer `TYPO-A11Y-004` |
| `TYPO-A11Y-006` | `WKWebView`, `WebView(` or `WebPage(` on reading screens with no `pageZoom`, no text-size CSS injection, no in-app text-size control and no hand-off through `SFSafariViewController` or `openURL` |
| `TYPO-UI-001`, `TYPO-UI-002`, `TYPO-UI-003` | Numeric `Font.system(size:)` instead of text styles; `Font.custom` without `relativeTo:` on titles, headlines, captions or footnotes, or `Font.custom(_:fixedSize:)` on text that should follow Dynamic Type; hierarchy carried by weight alone |
| `TYPO-UX-001`, `TYPO-UX-002` | `lineLimit(1)` on important content; `.leading(.tight)` on text that can wrap to three or more lines, or long custom-font passages with no `.lineSpacing` (`.lineSpacing(0)` is the default, so leave it) |

When a clause's Check names several cues, capture the dominant cue first and let stage `2-verify` judge the context.

## Snippet capture

`code_snippet` is the exact source the fixes will replace, so capture it carefully:

- Start at the line where the construct begins (the root view of the modifier chain, or the offending modifier) and end at its closing brace or the end of the chain.
- Copy the lines verbatim and contiguously, with their original indentation. Do not trim, annotate or elide anything; a `// ...` marker can never match the file again.
- Aim for 15 lines or fewer. A construct that needs more may take up to about 30 lines. If it is longer still, capture the contiguous block the fix actually changes.
- Record `line_number` as the first line of the snippet.

## Output of this stage

An in-memory list of draft findings for stage 2. Each draft holds:

- `clause_ids`: every corpus clause that fired on the construct. Stage 2 picks the primary one and the related ones.
- `file_path` (relative to the project root), `line_number`, `code_snippet`, and `language` (always `swift`).
- The corpus title, Check and severity for each clause, for stage 2 to refine.
- Any note about a problem outside the corpus, as described in step 8.

Do not skip stage `2-verify`. Static matches include false positives, for example a custom view whose parent already provides accessibility, a `Color.black` used only in a print preview, or a `frame(height: 32)` on a label nobody taps.
