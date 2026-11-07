# Official Sources

Contents: How to use this list, Core Apple HIG, Apple Developer Documentation, App Store accessibility, WCAG 2.2 cross-references, Working rules.

## How to use this list

Read this file before verifying findings or rewriting clause titles, descriptions and fixes. evenbetter-validate reads it too. Every corpus clause already has its canonical Apple page as `source_url` in `../../corpus/index.json`, and that page is what a finding's `hig_reference_url` holds. The pages below give context: the surrounding guidance, newer API pages, and the WCAG criteria used as cross-references.

## Core Apple HIG

- Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines/
- HIG what's new (dated list of changed pages; check it when a clause's source seems to have moved): https://developer.apple.com/design/whats-new/
- Accessibility: https://developer.apple.com/design/human-interface-guidelines/accessibility
- Typography and Dynamic Type: https://developer.apple.com/design/human-interface-guidelines/typography
- Layout: https://developer.apple.com/design/human-interface-guidelines/layout
- Color: https://developer.apple.com/design/human-interface-guidelines/color
- Materials: https://developer.apple.com/design/human-interface-guidelines/materials
- Components: https://developer.apple.com/design/human-interface-guidelines/components
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
- Writing (including empty states): https://developer.apple.com/design/human-interface-guidelines/writing
- Feedback: https://developer.apple.com/design/human-interface-guidelines/feedback
- Playing haptics: https://developer.apple.com/design/human-interface-guidelines/playing-haptics

## Apple Developer Documentation

- SwiftUI accessibility modifiers: https://developer.apple.com/documentation/swiftui/view-accessibility
- SwiftUI accessibility fundamentals: https://developer.apple.com/documentation/swiftui/accessibility-fundamentals
- Enhancing SwiftUI accessibility: https://developer.apple.com/documentation/accessibility/enhancing-the-accessibility-of-your-swiftui-app
- Performing accessibility testing: https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app
- Accessibility Inspector: https://developer.apple.com/documentation/accessibility/accessibility-inspector
- Dynamic Type size: https://developer.apple.com/documentation/swiftui/dynamictypesize
- AccessibilityNotification: https://developer.apple.com/documentation/accessibility/accessibilitynotification
- accessibilityLabel: https://developer.apple.com/documentation/swiftui/view/accessibilitylabel(_:)
- accessibilityHidden: https://developer.apple.com/documentation/swiftui/view/accessibilityhidden(_:)
- accessibilityHint: https://developer.apple.com/documentation/swiftui/view/accessibilityhint(_:)
- accessibilityValue: https://developer.apple.com/documentation/swiftui/view/accessibilityvalue(_:)
- accessibilityAddTraits: https://developer.apple.com/documentation/swiftui/view/accessibilityaddtraits(_:)
- accessibilityElement children combine: https://developer.apple.com/documentation/swiftui/accessibilitychildbehavior/combine
- accessibilityReduceMotion: https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion
- accessibilityInputLabels: https://developer.apple.com/documentation/swiftui/view/accessibilityinputlabels(_:)
- accessibilityActions: https://developer.apple.com/documentation/swiftui/view/accessibilityactions(_:)
- AccessibilityActionKind escape: https://developer.apple.com/documentation/swiftui/accessibilityactionkind/escape
- AccessibilityTraits isModal: https://developer.apple.com/documentation/swiftui/accessibilitytraits/ismodal
- accessibilityRepresentation: https://developer.apple.com/documentation/swiftui/view/accessibilityrepresentation(representation:)
- accessibilityChartDescriptor: https://developer.apple.com/documentation/swiftui/view/accessibilitychartdescriptor(_:)
- accessibilityIgnoresInvertColors: https://developer.apple.com/documentation/swiftui/view/accessibilityignoresinvertcolors(_:)
- accessibilityShowsLargeContentViewer: https://developer.apple.com/documentation/swiftui/view/accessibilityshowslargecontentviewer()
- LocalizedStringKey: https://developer.apple.com/documentation/swiftui/localizedstringkey
- AVPlayer appliesMediaSelectionCriteriaAutomatically: https://developer.apple.com/documentation/avfoundation/avplayer/appliesmediaselectioncriteriaautomatically
- AVPlayer setMediaSelectionCriteria: https://developer.apple.com/documentation/avfoundation/avplayer/setmediaselectioncriteria(_:formediacharacteristic:)
- WKWebView pageZoom: https://developer.apple.com/documentation/webkit/wkwebview/pagezoom
- Button: https://developer.apple.com/documentation/swiftui/button
- NavigationStack migration: https://developer.apple.com/documentation/swiftui/migrating-to-new-navigation-types
- NavigationSplitView: https://developer.apple.com/documentation/swiftui/navigationsplitview
- navigationTitle: https://developer.apple.com/documentation/swiftui/view/navigationtitle(_:)
- cancellationAction: https://developer.apple.com/documentation/swiftui/toolbaritemplacement/cancellationaction
- ProgressView: https://developer.apple.com/documentation/swiftui/progressview
- sensoryFeedback: https://developer.apple.com/documentation/swiftui/view/sensoryfeedback(_:trigger:)
- Preparing your app to play haptics: https://developer.apple.com/documentation/corehaptics/preparing-your-app-to-play-haptics
- SwiftUI Color: https://developer.apple.com/documentation/swiftui/color

## App Store accessibility

- Overview of Accessibility Nutrition Labels: https://developer.apple.com/help/app-store-connect/manage-app-accessibility/overview-of-accessibility-nutrition-labels/

Each label has its own evaluation criteria page, which says what the app must support before the developer claims the label. Several clauses use one of these pages as their `source_url`.

- VoiceOver: https://developer.apple.com/help/app-store-connect/manage-app-accessibility/voiceover-evaluation-criteria/
- Voice Control: https://developer.apple.com/help/app-store-connect/manage-app-accessibility/voice-control-evaluation-criteria/
- Larger Text: https://developer.apple.com/help/app-store-connect/manage-app-accessibility/larger-text-evaluation-criteria/
- Dark Interface: https://developer.apple.com/help/app-store-connect/manage-app-accessibility/dark-interface-evaluation-criteria/
- Differentiate Without Color Alone: https://developer.apple.com/help/app-store-connect/manage-app-accessibility/differentiate-without-color-alone-evaluation-criteria/
- Sufficient Contrast: https://developer.apple.com/help/app-store-connect/manage-app-accessibility/sufficient-contrast-evaluation-criteria/
- Reduced Motion: https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria/
- Captions: https://developer.apple.com/help/app-store-connect/manage-app-accessibility/captions-evaluation-criteria/
- Audio Descriptions: https://developer.apple.com/help/app-store-connect/manage-app-accessibility/audio-descriptions-evaluation-criteria/

The labels are voluntary today, and Apple says they will become required. A finding whose clause matches a label bears on whether the app can claim it, and its description may say so.

## WCAG 2.2 cross-references

Use these only to fill `wcag_criteria` and `wcag_level`. Never put them in `hig_reference_url`.

WCAG 2.2 is the current W3C Recommendation: https://www.w3.org/TR/WCAG22/. Link and check criteria there, by anchor. The Quick Reference page filters its criteria with JavaScript, so a scraper often gets nothing from it. Each criterion also has an Understanding page at `https://www.w3.org/WAI/WCAG22/Understanding/[anchor].html` for background.

- 1.1.1 Non-text Content (A): https://www.w3.org/TR/WCAG22/#non-text-content
- 1.2.2 Captions (Prerecorded) (A): https://www.w3.org/TR/WCAG22/#captions-prerecorded
- 1.2.5 Audio Description (Prerecorded) (AA): https://www.w3.org/TR/WCAG22/#audio-description-prerecorded
- 1.3.1 Info and Relationships (A): https://www.w3.org/TR/WCAG22/#info-and-relationships
- 1.4.1 Use of Color (A): https://www.w3.org/TR/WCAG22/#use-of-color
- 1.4.3 Contrast (Minimum) (AA): https://www.w3.org/TR/WCAG22/#contrast-minimum
- 1.4.4 Resize Text (AA): https://www.w3.org/TR/WCAG22/#resize-text
- 1.4.10 Reflow (AA): https://www.w3.org/TR/WCAG22/#reflow
- 1.4.11 Non-text Contrast (AA): https://www.w3.org/TR/WCAG22/#non-text-contrast
- 2.1.1 Keyboard (A): https://www.w3.org/TR/WCAG22/#keyboard
- 2.2.2 Pause, Stop, Hide (A): https://www.w3.org/TR/WCAG22/#pause-stop-hide
- 2.3.3 Animation from Interactions (AAA): https://www.w3.org/TR/WCAG22/#animation-from-interactions
- 2.4.2 Page Titled (A): https://www.w3.org/TR/WCAG22/#page-titled
- 2.4.3 Focus Order (A): https://www.w3.org/TR/WCAG22/#focus-order
- 2.5.1 Pointer Gestures (A): https://www.w3.org/TR/WCAG22/#pointer-gestures
- 2.5.3 Label in Name (A): https://www.w3.org/TR/WCAG22/#label-in-name
- 2.5.5 Target Size (Enhanced) (AAA, 44 by 44 CSS pixels): https://www.w3.org/TR/WCAG22/#target-size-enhanced
- 2.5.7 Dragging Movements (AA): https://www.w3.org/TR/WCAG22/#dragging-movements
- 2.5.8 Target Size (Minimum) (AA, 24 by 24 CSS pixels): https://www.w3.org/TR/WCAG22/#target-size-minimum
- 3.3.4 Error Prevention (Legal, Financial, Data) (AA): https://www.w3.org/TR/WCAG22/#error-prevention-legal-financial-data
- 4.1.2 Name, Role, Value (A): https://www.w3.org/TR/WCAG22/#name-role-value
- 4.1.3 Status Messages (AA): https://www.w3.org/TR/WCAG22/#status-messages

For an AA report, target size is 2.5.8. Use 2.5.5 only when the report targets AAA. 4.1.1 Parsing is obsolete and removed in WCAG 2.2.

## Working rules

- A finding's `hig_reference_url` is always the `source_url` of its `clause_id` in `../../corpus/index.json`, so analyze and validate never disagree about it. When another Apple page states the rule more directly (for example HIG Buttons for a hit-target clause whose index URL is HIG Accessibility), cite that page in the description text.
- Verify each clause's source once per audit and reuse the result for every finding that cites it. Apple pages are rendered with JavaScript: use a scraper MCP that renders pages (Firecrawl, Tavily extract, Exa fetch) or Apple's JSON form from SKILL.md, because a plain fetch can return an empty "requires JavaScript" shell.
- Only corpus clauses become findings. A real HIG problem with no clause goes into the description of a finding whose fix also closes it, or into `scan_context.notes`.
- Summarize Apple's guidance in your own words and link to it. Do not paste long excerpts into the report.
