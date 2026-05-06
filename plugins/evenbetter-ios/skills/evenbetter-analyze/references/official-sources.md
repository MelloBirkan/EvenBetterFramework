# Official Sources

Use this file when verifying findings or rewriting clause titles, descriptions, and fixes for the report. Prefer Apple HIG and Apple Developer Documentation. Use WCAG only as a cross-reference, never as the primary citation.

## Core Apple HIG

- Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines/
- Accessibility: https://developer.apple.com/design/human-interface-guidelines/accessibility
- Typography and Dynamic Type: https://developer.apple.com/design/human-interface-guidelines/typography
- Layout: https://developer.apple.com/design/human-interface-guidelines/layout
- Color: https://developer.apple.com/design/human-interface-guidelines/color
- Materials: https://developer.apple.com/design/human-interface-guidelines/materials
- Gestures: https://developer.apple.com/design/human-interface-guidelines/gestures
- Buttons: https://developer.apple.com/design/human-interface-guidelines/buttons
- Action Sheets: https://developer.apple.com/design/human-interface-guidelines/action-sheets
- Alerts: https://developer.apple.com/design/human-interface-guidelines/alerts
- Sheets: https://developer.apple.com/design/human-interface-guidelines/sheets
- Tab Bars: https://developer.apple.com/design/human-interface-guidelines/tab-bars
- Toolbars: https://developer.apple.com/design/human-interface-guidelines/toolbars
- Navigation and Search: https://developer.apple.com/design/human-interface-guidelines/navigation-and-search
- Text Fields: https://developer.apple.com/design/human-interface-guidelines/text-fields
- Search Fields: https://developer.apple.com/design/human-interface-guidelines/search-fields
- VoiceOver: https://developer.apple.com/design/human-interface-guidelines/voiceover
- Icons and SF Symbols: https://developer.apple.com/design/human-interface-guidelines/icons

## Apple Developer Documentation

- SwiftUI accessibility modifiers: https://developer.apple.com/documentation/swiftui/view-accessibility
- SwiftUI accessibility fundamentals: https://developer.apple.com/documentation/swiftui/accessibility-fundamentals
- Enhancing SwiftUI accessibility: https://developer.apple.com/documentation/accessibility/enhancing-the-accessibility-of-your-swiftui-app
- Performing accessibility testing: https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app
- Accessibility Inspector: https://developer.apple.com/documentation/accessibility/accessibility-inspector
- Dynamic Type size: https://developer.apple.com/documentation/swiftui/dynamictypesize
- AccessibilityNotification: https://developer.apple.com/documentation/Accessibility/AccessibilityNotification
- accessibilityLabel: https://developer.apple.com/documentation/swiftui/view/accessibilitylabel(_:)
- accessibilityHidden: https://developer.apple.com/documentation/swiftui/view/accessibilityhidden(_:)
- accessibilityHint: https://developer.apple.com/documentation/swiftui/view/accessibilityhint(_:)
- accessibilityValue: https://developer.apple.com/documentation/swiftui/view/accessibilityvalue(_:)
- accessibilityAddTraits: https://developer.apple.com/documentation/swiftui/view/accessibilityaddtraits(_:)
- accessibilityElement children combine: https://developer.apple.com/documentation/swiftui/accessibilitychildbehavior/combine
- accessibilityReduceMotion: https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion
- NavigationStack migration: https://developer.apple.com/documentation/swiftui/migrating-to-new-navigation-types
- ProgressView: https://developer.apple.com/documentation/swiftui/progressview
- sensoryFeedback: https://developer.apple.com/documentation/swiftui/view/sensoryfeedback(_:trigger:)
- SwiftUI Color: https://developer.apple.com/documentation/swiftui/color

## WCAG 2.2 cross-references

Use these only to populate `wcag_criteria` and `wcag_level` on a finding. Never cite them as `hig_reference_url`.

- WCAG 2.2 Quick Reference: https://www.w3.org/WAI/WCAG22/quickref/
- 1.1.1 Non-text Content (A): https://www.w3.org/WAI/WCAG22/Understanding/non-text-content
- 1.3.1 Info and Relationships (A): https://www.w3.org/WAI/WCAG22/Understanding/info-and-relationships
- 1.4.3 Contrast (Minimum) (AA): https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum
- 1.4.10 Reflow (AA): https://www.w3.org/WAI/WCAG22/Understanding/reflow
- 1.4.11 Non-text Contrast (AA): https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast
- 2.1.1 Keyboard (A): https://www.w3.org/WAI/WCAG22/Understanding/keyboard
- 2.4.3 Focus Order (A): https://www.w3.org/WAI/WCAG22/Understanding/focus-order
- 2.5.3 Label in Name (A): https://www.w3.org/WAI/WCAG22/Understanding/label-in-name
- 2.5.5 Target Size (Enhanced) (AAA): https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced
- 2.5.8 Target Size (Minimum) (AA): https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum
- 4.1.2 Name, Role, Value (A): https://www.w3.org/WAI/WCAG22/Understanding/name-role-value

## Working rules

- Verify each finding's primary citation with `WebFetch` (or `ref_read_url`) before including it. Apple URLs change shape; cache the response per audit.
- Use one canonical Apple URL per finding in `hig_reference_url`. If a clause has both an HIG page and a Developer Documentation page, choose the one that most directly states the rule the finding violates.
- For accessibility findings, prefer the Apple Developer accessibility modifier reference over the HIG page when the violation is mechanical (e.g., missing `accessibilityLabel`).
- For HIG-style design findings (color, layout, target size, navigation), prefer the HIG page.
- Treat the corpus as the starting set of clauses, not the limit. If the agent identifies a verifiable Apple HIG violation that has no corpus clause, include it with a synthesized title and description, citing the official Apple URL directly.
- Do not paste large excerpts of HIG or Developer Documentation into the report. Summarize in your own words and link out.
