---
name: evenbetter-swiftui-accessibility
description: >-
  Writes and reviews the accessibility of individual SwiftUI views against EvenBetter's Apple HIG and WCAG clauses and
  cites each clause ID. Use when building or checking a view's VoiceOver labels, grouping and focus order, Dynamic
  Type, contrast, Reduce Motion or hit targets. For a whole-repo audit use evenbetter-analyze; to test the running
  app, evenbetter-accessibility-tests.
---

# SwiftUI accessibility

> Paths in this skill are relative to this SKILL.md's folder. The plugin corpus is at `../../corpus/`.

This skill covers one view or a few views at a time, while they are being written or reviewed. The rules live in the EvenBetter corpus, not here: each clause has a stable ID (such as `A11Y-UI-001`), a severity, a dimension, an Apple source with a retrieval date, a Check, a Why and a Correct code example. Load the clauses that match the view and work from them, quoting only as much of a clause as the answer needs.

If current system, developer or user instructions conflict with this skill, follow them.

## When to use another skill

- Whole repository, with an HTML report: evenbetter-analyze. Re-checking that report: evenbetter-validate. Applying its fixes: evenbetter-repair.
- Checking the running app, with Apple's accessibility audit in UI tests or a VoiceOver walk on Xcode 27: evenbetter-accessibility-tests. It records a verdict on each tested finding of the evenbetter-analyze report.
- Deciding which App Store Accessibility Nutrition Labels the app can declare: evenbetter-accessibility-nutrition-labels.
- Choosing or designing haptic patterns: evenbetter-ios-haptics. This skill only checks the haptic clauses below.
- Navigation, sheets, forms and other component structure: evenbetter-swiftui-ui-patterns.

## Load the clauses for the view's concerns

Pick the rows that apply to the view, open the listed corpus file, and read only the `## CLAUSE-ID` sections named. `../../corpus/index.json` holds each clause's severity, dimension, platform, source URL, retrieval date and anchor.

| View concern | Corpus file | Clauses |
| --- | --- | --- |
| Labels, traits and values | `../../corpus/ios/accessibility.md` | A11Y-UI-001, A11Y-UI-002, A11Y-UI-004, A11Y-A11Y-001, A11Y-A11Y-002, A11Y-A11Y-004, A11Y-A11Y-008, A11Y-UX-002 |
| Gestures, charts, status messages and media | `../../corpus/ios/accessibility.md` | A11Y-A11Y-005, A11Y-A11Y-006, A11Y-A11Y-007, A11Y-A11Y-009 |
| Custom controls and buttons | `../../corpus/ios/components-patterns.md` | COMP-A11Y-001, COMP-A11Y-002, COMP-UI-001 |
| Grouping, focus and screen changes | `../../corpus/ios/accessibility.md`, `../../corpus/ios/navigation-flow.md` | A11Y-UI-003, A11Y-A11Y-003, NAV-A11Y-001, NAV-A11Y-002, NAV-A11Y-003 |
| Dynamic Type and text | `../../corpus/ios/typography.md` | TYPO-UI-001, TYPO-UI-002, TYPO-UX-001, TYPO-A11Y-001, TYPO-A11Y-002, TYPO-A11Y-003, TYPO-A11Y-004, TYPO-A11Y-005, TYPO-A11Y-006 |
| Contrast and colour | `../../corpus/ios/color-theming.md` | CLR-A11Y-001, CLR-A11Y-002, CLR-A11Y-003, CLR-UX-001, CLR-UI-001, CLR-UI-002, CLR-UI-003 |
| Reduce Motion | `../../corpus/ios/accessibility.md` | A11Y-UX-001 |
| Hit targets and safe areas | `../../corpus/ios/layout-interaction.md` | LAY-UI-001, LAY-A11Y-001, LAY-UI-002, LAY-A11Y-002 |
| Haptics | `../../corpus/ios/haptics.md`, `../../corpus/ios/layout-interaction.md` | HAPT-UX-001, HAPT-UX-002, HAPT-UX-003, HAPT-UX-004, LAY-UX-002, LAY-UX-009 |

## Workflow

1. Read the view and note which concerns it touches: icon-only buttons, custom gestures, rows that combine several texts, fixed font sizes or frames, custom colours, animation, small controls, haptics, charts, toasts and other temporary messages, custom overlays, video, web views.
2. Find out the deployment target from the project when an API depends on it. If the project does not say, ask.
3. Load the matching clauses from the table. Apply each clause's Check to the code.
4. When writing a view, follow the clause's Correct code and prefer system controls and text styles, which carry VoiceOver, Dynamic Type and keyboard support without extra work.
5. When reviewing, report each finding in the format below, ordered by severity (error, then warning, then info).
6. Contrast, clipping at large Dynamic Type sizes and Reduce Motion behaviour depend on the rendered result. For those, ask for a screenshot or simulator evidence (for example the view at the AX5 text size, in dark mode, or with Increase Contrast on), or render previews when the session has a preview tool, before calling the finding confirmed.

## Citing clauses

- Cite clause IDs exactly as they appear in `../../corpus/index.json`, and only IDs that exist there.
- Keep the clause's Severity, Dimension, Source and Retrieved values unchanged.
- When no clause covers an issue, say so and cite the Apple page directly, marked as outside the corpus. Do not invent an ID for it.

```text
A11Y-UI-001 (error, ui) Label meaningful images and icon buttons
File: Sources/Feed/FeedRow.swift:42
Found: icon-only Button with Image(systemName: "heart") and no accessibilityLabel
Fix: add .accessibilityLabel("Like")
Source: https://developer.apple.com/documentation/swiftui/view/accessibilitylabel(_:) (retrieved 2026-11-07)
```

## APIs outside the corpus

No clause covers these yet, so cite the Apple page rather than a clause ID. Availability was checked on Apple's documentation on 2026-11-07.

- Reading order: VoiceOver follows the layout, so fix the order of views first. Where the visual order and the logical order must differ, `accessibilitySortPriority(_:)` reorders elements at the same level.
- `accessibilityLinkedGroup(id:in:)` (iOS 14+) links elements that sit apart in the hierarchy, such as an item in a list and the same item in a detail pane. Starting in iOS 27, when every element in the group is a `Text`, `TextEditor` or `TextField`, VoiceOver moves by line, word and character across them as if they were one text region (WWDC26 "Enhance the accessibility of your reading app").
- `accessibilityDirectTouch(_:options:)` (iOS 17+) passes touches straight to a control that has its own gestures, such as a drawing canvas or an instrument. `.requiresActivation` waits for a double tap before touches pass through, and `.silentOnTouch` keeps VoiceOver quiet for controls that play their own audio. Add custom actions as well, because not everyone can perform the direct gestures (WWDC26 "Refine accessibility for custom controls").
- To check a running build, a UI test can call `performAccessibilityAudit(for:_:)` (iOS 17+). On iOS 27, `XCUIVoiceOverService`, reached through `XCUIDevice`'s `voiceOverService`, moves VoiceOver from element to element and returns what it speaks.

## Apple's accessibility skills

Xcode 27 ships three Apple-built accessibility specialist skills: accessibility-voiceover-specialist, accessibility-dynamic-type-specialist and accessibility-sufficient-contrast-specialist. When they are installed, each audits one view or file and gives a pass or fail against Apple's Accessibility Nutrition Label criteria for its feature. Use them as a second check next to this skill. What EvenBetter adds is a clause ID for each finding, traced to a dated Apple source, in the same form that evenbetter-analyze, evenbetter-validate and evenbetter-repair read.

## Question tooling

Ask with the host's structured question tool when it has one:

- Claude Code: `AskUserQuestion`, with 2-4 mutually exclusive options per question.
- Codex in Plan mode: `request_user_input`, with 1-3 short questions of 2-3 options each, the recommended option first and marked "(Recommended)". The client adds "Other". Plan mode is read-only, so present results in a `<proposed_plan>` block and ask the user to switch to Default mode before editing code.
- Codex in Default mode: ask one concise closed question with numbered options in plain text, then wait. Use `request_user_input` instead if the session offers it.
- Other agents: use their structured question tool, or ask one closed question with numbered options.
- When nobody can answer, because the user said they will not be around or asked you to go ahead without questions, or because the run is one-shot and non-interactive (such as `claude -p`, `codex exec`, CI or a scheduled task), do not end the turn on a clarifying question. Take the recommended option, say which one you took, and record it as an assumption in the artifact or the final reply. Never assume an approval the user has not given, such as accepting a plan or starting to edit code: finish the current stage and end with what waits on the person. Any exception this skill names elsewhere still applies.

Keep questions closed. For example, ask for the deployment target as iOS 16 or earlier, iOS 17 to 26, or iOS 27 and later, the ranges where the APIs above change. Mark the lowest range recommended, because code that guards newer APIs with `if #available` works on any target, while assuming a newer target can ship calls the app cannot make.
