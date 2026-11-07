# Audit and VoiceOver map

Contents: Reading the map, Audit types, VoiceOver walk checks, Manual clauses, Keeping the map current.

## Reading the map

Each row ties one corpus clause to one runtime check. `1-plan` uses it to pick each finding's audit types, walk checks and configurations. `4-record` uses it to turn results into verdicts.

- **Configurations** are the ones a test needs to show the problem. `standard` is light mode at the default text size, `ax5` is the largest accessibility text size, `dark` is dark mode, `increaseContrast` is the Increase Contrast setting, and `rtl` is a right-to-left layout.
- **Refutes** says whether a clean result counts as evidence that the finding is wrong. `yes` means the check measures what the clause asks for. `no` means the check can catch the problem but can also miss it, so a clean result leaves the finding `inconclusive`.
- A finding is testable when its `clause_id` or any of its `related_clause_ids` has a row in the first two tables.

Apple's pages for `XCUIAccessibilityAuditType` list the type names without describing what each one checks. The rows below are EvenBetter's reading of those names and of the WWDC23 session "Perform accessibility audits for your app". The `.action` and `.parentChild` rows are the least certain: compare them with the issues of the first real run and correct the map if they disagree.

## Audit types

The audit runs every type on each screen (`.all`), and a test fails only on the types its findings map to. Other issues are logged as leads.

| Audit type | Clause | Configurations | Refutes |
| --- | --- | --- | --- |
| `.contrast` | CLR-A11Y-001 | standard, dark, increaseContrast | yes |
| `.contrast` | CLR-UI-002 | dark | no |
| `.contrast` | CLR-UI-003 | dark, increaseContrast | no |
| `.dynamicType` | TYPO-UI-001 | ax5 | no |
| `.dynamicType` | TYPO-UI-002 | ax5 | no |
| `.dynamicType` | TYPO-A11Y-001 | ax5 | no |
| `.dynamicType` | TYPO-A11Y-003 | ax5 | no |
| `.dynamicType` | TYPO-A11Y-004 | ax5 | no |
| `.textClipped` | TYPO-A11Y-002 | ax5, rtl | no |
| `.textClipped` | TYPO-A11Y-003 | ax5 | no |
| `.textClipped` | TYPO-UX-001 | ax5, rtl | no |
| `.hitRegion` | LAY-A11Y-001 | standard | no |
| `.hitRegion` | LAY-UI-001 | standard | no |
| `.sufficientElementDescription` | A11Y-UI-001 | standard | yes |
| `.elementDetection` | A11Y-UI-001 | standard | no |
| `.elementDetection` | COMP-A11Y-001 | standard | no |
| `.trait` | A11Y-A11Y-001 | standard | no |
| `.trait` | COMP-A11Y-002 | standard | no |
| `.action` | COMP-UI-001 | standard | no |
| `.parentChild` | A11Y-UI-003 | standard | no |

Why two rows refute:

- Apple's WWDC23 session says the UI test audit checks the screen "just as the Inspector does", and CLR-A11Y-001 cites the WCAG AA values Accessibility Inspector applies (4.5:1, and 3:1 for large or bold text). A `.contrast` audit that raises no issue on the finding's element, in each planned configuration, is therefore evidence against the finding.
- A clean `.sufficientElementDescription` audit means the element has a description the audit accepts, which is what A11Y-UI-001 asks for. The walk's `spoken` check is the stronger proof, because it hears the label.

Why the others do not:

- Apple does not publish the size limit behind `.hitRegion`, so a clean hit-region audit does not prove a control meets 28x28 or 44x44 points.
- `.dynamicType` reports text that does not scale. It does not measure point sizes, so it cannot clear a 9 pt label or a text style choice.
- `.textClipped` only sees text that is clipped on screen in that configuration.
- `.contrast` checks text against its background, so a clean dark-mode run does not clear a hard-coded colour or a missing asset variant in every state.

## VoiceOver walk checks

The walk needs Xcode 27 and an iOS 27 simulator. It runs in the `standard` configuration with English as the app language, because the checks read VoiceOver's spoken words. "Complete" means the walk reached the end of the screen, as `2-write` explains.

| Check | Clause | Refutes |
| --- | --- | --- |
| `button`: the element's utterance includes the trait word "button" | A11Y-A11Y-001, COMP-A11Y-002 | yes |
| `silent` with decorative image names | A11Y-UI-002 | yes, when the walk is complete |
| `silent` with the asset name of an image inside a control | A11Y-UI-001 | no |
| `silent` with labels that only the screen behind a custom overlay shows | NAV-A11Y-003 | yes, when the walk is complete |
| `oneStop`: related texts are spoken as one utterance | A11Y-UI-003 | yes |
| `value`: a stateful control speaks its value | A11Y-A11Y-002 | yes |
| `dismissControl`: a Cancel, Close or Done button is spoken | NAV-A11Y-002 | yes, when the walk is complete |
| `noRepeatedTrait`: the label does not repeat the trait VoiceOver adds | A11Y-UI-004 | no |
| `spoken`: an expected label is spoken | A11Y-UI-001 | yes, when the walk is complete |

`spoken` is mainly a regression check: plan it for an `applied` finding whose fix added a label, or for a label that already exists in code.

## Manual clauses

These clauses have no runtime check here. Their findings get `not_testable`.

| Clause | Why it stays manual |
| --- | --- |
| A11Y-A11Y-003, NAV-A11Y-001 | The walk navigates with VoiceOver off, so it cannot watch focus move after a screen change. |
| A11Y-A11Y-004 | Voice Control names are not exposed to UI tests. |
| A11Y-A11Y-005 | Gesture alternatives need a person to judge the onscreen route. |
| A11Y-A11Y-006, A11Y-A11Y-007 | Chart descriptions and announcements need listening with VoiceOver in context. |
| A11Y-A11Y-008 | Localizability is a source and string-catalog check. |
| A11Y-A11Y-009 | Caption and audio description selection needs real media playback. |
| A11Y-UX-001 | XCUIAutomation has no documented switch for Reduce Motion. |
| A11Y-UX-002 | Whether an action is obvious is a judgment call. |
| CLR-A11Y-002, CLR-UX-001, CLR-UI-001 | Colour meaning and semantic colour use are source and design checks. |
| CLR-A11Y-003 | XCUIAutomation has no documented switch for Smart Invert. |
| COMP-UI-002, COMP-UI-003, NAV-UI-001 | API choices that the running app does not reveal. |
| COMP-UX-001, COMP-UX-002, LAY-UX-001 | Destructive roles and confirmations need a judgment of consequence. |
| HAPT-UX-001, HAPT-UX-002, HAPT-UX-003, HAPT-UX-004, LAY-UX-002, LAY-UX-009 | The simulator plays no haptics a test can observe. |
| LAY-A11Y-002, LAY-UI-002 | Safe-area problems show in screenshots, not in audit issues. Ask for one when it matters. |
| LAY-UI-003, LAY-UI-004 | Loading and empty states need app state the tests do not set up. |
| NAV-UI-002, NAV-UI-003, NAV-UX-001, NAV-UX-002 | Navigation structure is a source and design check. |
| TYPO-A11Y-005 | The Large Content Viewer appears on a long press with large text, which the audit does not report. |
| TYPO-A11Y-006 | Web view text controls need the web content. |
| TYPO-UI-003, TYPO-UX-002 | Type hierarchy and line spacing are design checks. |

## Keeping the map current

A clause that appears in no table here, for example one added to `../../corpus/index.json` after this map, is treated as manual until a row is added. When adding a row, cite only clause IDs that exist in the index, and give the configurations and the Refutes value with a reason.
