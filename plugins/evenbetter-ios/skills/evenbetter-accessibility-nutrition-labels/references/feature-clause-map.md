# Feature clause map

Contents: How to use the map, Features, Clauses, Runtime checks per feature.

## How to use the map

A finding maps to a feature when its `clause_id`, or any of its `related_clause_ids`, is listed for that feature in the Clauses table. A finding can map to several features. A finding whose clauses all show "none" adds nothing to the matrix, though it stays in the report for evenbetter-repair.

The clause bodies are in `../../corpus/ios/`, and `../../corpus/index.json` lists every clause with its file. The runtime checks come from `../evenbetter-accessibility-tests/references/audit-clause-map.md`, which is the authority for audit types and configurations.

## Features

The features in Apple's order, with the App Store Connect attribute for each and the devices Apple offers it on. Apple's overview says Voice Control isn't supported on Apple TV or Apple Watch, and Larger Text isn't supported on Mac.

| Feature | Attribute | Devices | Clauses |
| --- | --- | --- | --- |
| VoiceOver | `supportsVoiceover` | all | A11Y-UI-001, A11Y-UI-002, A11Y-UI-003, A11Y-UI-004, A11Y-A11Y-001, A11Y-A11Y-002, A11Y-A11Y-003, A11Y-A11Y-005, A11Y-A11Y-006, A11Y-A11Y-007, A11Y-A11Y-008, A11Y-UX-002, COMP-A11Y-001, COMP-A11Y-002, COMP-UI-001, NAV-A11Y-001, NAV-A11Y-002, NAV-A11Y-003 |
| Voice Control | `supportsVoiceControl` | iPhone, iPad, Mac, Vision | A11Y-UI-001, A11Y-A11Y-001, A11Y-A11Y-004, A11Y-A11Y-005, A11Y-A11Y-008, COMP-A11Y-002, COMP-UI-001 |
| Larger Text | `supportsLargerText` | iPhone, iPad, Apple TV, Apple Watch, Vision | TYPO-A11Y-001, TYPO-A11Y-002, TYPO-A11Y-003, TYPO-A11Y-004, TYPO-A11Y-005, TYPO-A11Y-006, TYPO-UI-001, TYPO-UI-002, TYPO-UX-001 |
| Dark Interface | `supportsDarkInterface` | all | CLR-UI-001, CLR-UI-002, CLR-UI-003, CLR-A11Y-003 |
| Differentiate Without Color Alone | `supportsDifferentiateWithoutColorAlone` | all | CLR-A11Y-002, CLR-UX-001 |
| Sufficient Contrast | `supportsSufficientContrast` | all | CLR-A11Y-001, CLR-UI-002, CLR-UI-003 |
| Reduced Motion | `supportsReducedMotion` | all | A11Y-UX-001 |
| Captions | `supportsCaptions` | all | A11Y-A11Y-009 |
| Audio Descriptions | `supportsAudioDescriptions` | all | A11Y-A11Y-009 |

"All" means iPhone, iPad, Apple TV, Apple Watch, Mac and Vision. The attribute is spelled `supportsVoiceover`, with a lowercase o, in the App Store Connect API.

## Clauses

Every clause in `../../corpus/index.json`, with the features it bears on and why.

| Clause | Features | Why |
| --- | --- | --- |
| A11Y-A11Y-001 | VoiceOver, Voice Control | A control without the button trait is not announced as one, and Voice Control may not offer it. |
| A11Y-A11Y-002 | VoiceOver | A stateful control that speaks no value hides its state. |
| A11Y-A11Y-003 | VoiceOver | A screen change that is not announced leaves focus behind. |
| A11Y-A11Y-004 | Voice Control | People say what they see, so names must match the visible text. |
| A11Y-A11Y-005 | VoiceOver, Voice Control | A gesture-only action has no route for either. |
| A11Y-A11Y-006 | VoiceOver | Apple's VoiceOver criteria ask for accessible charts. |
| A11Y-A11Y-007 | VoiceOver | Apple's VoiceOver criteria ask for status messages to be announced. |
| A11Y-A11Y-008 | VoiceOver, Voice Control | Labels that cannot be localized are wrong in other languages. |
| A11Y-A11Y-009 | Captions, Audio Descriptions | Apple asks for captions and descriptions to follow the system settings by default. |
| A11Y-UI-001 | VoiceOver, Voice Control | An unnamed control cannot be found by ear or by name. |
| A11Y-UI-002 | VoiceOver | Decorative images that are spoken add noise. |
| A11Y-UI-003 | VoiceOver | Related text split into many stops slows navigation. |
| A11Y-UI-004 | VoiceOver | Apple's VoiceOver criteria keep control types and states out of labels. |
| A11Y-UX-001 | Reduced Motion | Motion that ignores Reduce Motion is the trigger the label covers. |
| A11Y-UX-002 | VoiceOver | A hint explains an action that the label does not. |
| CLR-A11Y-001 | Sufficient Contrast | Text below the contrast minimum fails the label directly. |
| CLR-A11Y-002 | Differentiate Without Color Alone | Red and green as the only difference is what the label rules out. |
| CLR-A11Y-003 | Dark Interface | Apple's Dark Interface criteria say media must not invert under Smart Invert. |
| CLR-UI-001 | Dark Interface | Fixed colors do not adapt to a dark appearance. |
| CLR-UI-002 | Dark Interface, Sufficient Contrast | Pure black or white breaks dark mode and can drop contrast. |
| CLR-UI-003 | Dark Interface, Sufficient Contrast | Colors without dark or increased-contrast variants miss both settings. |
| CLR-UX-001 | Differentiate Without Color Alone | Color as the only indicator is what the label rules out. |
| COMP-A11Y-001 | VoiceOver | A custom recreation of a system control often loses its accessibility. |
| COMP-A11Y-002 | VoiceOver, Voice Control | Same as A11Y-A11Y-001, for custom buttons. |
| COMP-UI-001 | VoiceOver, Voice Control | An `onTapGesture` action is not a button to assistive technology. |
| COMP-UI-002 | none | An API choice that no feature's criteria depend on. |
| COMP-UI-003 | none | An API choice that no feature's criteria depend on. |
| COMP-UX-001 | none | Destructive roles are a general usability rule. |
| COMP-UX-002 | none | Confirmations are a general usability rule. |
| HAPT-UX-001 | none | Haptics are not one of the nine features. |
| HAPT-UX-002 | none | Haptics are not one of the nine features. |
| HAPT-UX-003 | none | Haptics are not one of the nine features. |
| HAPT-UX-004 | none | Haptics are not one of the nine features. |
| LAY-A11Y-001 | none | Touch target size is not one of the nine features. |
| LAY-A11Y-002 | none | Safe areas are a layout rule. |
| LAY-UI-001 | none | Touch target size is not one of the nine features. |
| LAY-UI-002 | none | Safe areas are a layout rule. |
| LAY-UI-003 | none | Loading indicators are a general usability rule. |
| LAY-UI-004 | none | Empty states are a general usability rule. |
| LAY-UX-001 | none | Confirmations are a general usability rule. |
| LAY-UX-002 | none | Haptics are not one of the nine features. |
| LAY-UX-009 | none | Haptics are not one of the nine features. |
| NAV-A11Y-001 | VoiceOver | A major screen change that is not announced leaves focus behind. |
| NAV-A11Y-002 | VoiceOver | Apple's VoiceOver criteria ask that modals can be dismissed. |
| NAV-A11Y-003 | VoiceOver | Apple's VoiceOver criteria keep focus inside a modal. |
| NAV-UI-001 | none | A navigation API choice. |
| NAV-UI-002 | none | Titles are a general navigation rule. |
| NAV-UI-003 | none | The back button is a general navigation rule. |
| NAV-UX-001 | none | Presentation style is a design choice. |
| NAV-UX-002 | none | Navigation depth is a design choice. |
| TYPO-A11Y-001 | Larger Text | Very small fixed text cannot be read at any setting. |
| TYPO-A11Y-002 | Larger Text | Fixed-height frames clip text as it grows. |
| TYPO-A11Y-003 | Larger Text | A scale factor shrinks text back down. |
| TYPO-A11Y-004 | Larger Text | A cap below AX3 stops text short of 200 percent. |
| TYPO-A11Y-005 | Larger Text | Apple's Larger Text criteria name the Large Content Viewer for controls that stay small. |
| TYPO-A11Y-006 | Larger Text | Apple's Larger Text criteria ask web views in common tasks for a text size control. |
| TYPO-UI-001 | Larger Text | Fixed font sizes do not follow Dynamic Type. |
| TYPO-UI-002 | Larger Text | Custom fonts without `relativeTo` do not scale with the text style. |
| TYPO-UI-003 | none | Weight hierarchy is a design check. |
| TYPO-UX-001 | Larger Text | Truncated text is lost at large sizes. |
| TYPO-UX-002 | none | Line spacing is a design check. |

## Runtime checks per feature

These are the evenbetter-accessibility-tests checks whose clauses map to each feature. A verdict on the finding counts for every feature its clauses map to. To tell whether one clause has a runtime check, look it up in the Audit types and VoiceOver walk checks tables of the audit map. A clause in its Manual clauses table, or in no table, has none.

| Feature | Audit types (configurations) | VoiceOver walk checks |
| --- | --- | --- |
| VoiceOver | `.sufficientElementDescription`, `.elementDetection`, `.trait`, `.action`, `.parentChild` (standard) | `button`, `silent`, `oneStop`, `value`, `dismissControl`, `noRepeatedTrait`, `spoken` |
| Voice Control | None of its own. The `.sufficientElementDescription`, `.elementDetection`, `.trait` and `.action` results for its shared clauses count. | `button` and `spoken`, plus `silent` on an image inside a control, for its shared clauses |
| Larger Text | `.dynamicType` (ax5), `.textClipped` (ax5, rtl) | none |
| Dark Interface | `.contrast` for CLR-UI-002 and CLR-UI-003 (dark) | none |
| Differentiate Without Color Alone | none | none |
| Sufficient Contrast | `.contrast` for CLR-A11Y-001 (standard, dark, increaseContrast), CLR-UI-002 (dark) and CLR-UI-003 (dark, increaseContrast) | none |
| Reduced Motion | none | none |
| Captions | none | none |
| Audio Descriptions | none | none |

No runtime check can show that a person completes a task with a feature. A clean audit or walk is a note in the matrix, never a pass.
