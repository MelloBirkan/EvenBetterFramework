# Official Sources

Use this file when planning or reviewing multi-screen iOS UX, accessibility strategy, Apple HIG conformance, and SwiftUI implementation details. Prefer official Apple sources and verify current API behavior when availability or guidance matters.

## Core Apple HIG

- Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines/
- What's new in design (dated HIG change log): https://developer.apple.com/design/whats-new/
- Accessibility: https://developer.apple.com/design/human-interface-guidelines/accessibility
- Typography and Dynamic Type: https://developer.apple.com/design/human-interface-guidelines/typography
- Layout: https://developer.apple.com/design/human-interface-guidelines/layout
- Designing for iPhone Duo: https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo
- Gestures: https://developer.apple.com/design/human-interface-guidelines/gestures
- Buttons: https://developer.apple.com/design/human-interface-guidelines/buttons
- Color: https://developer.apple.com/design/human-interface-guidelines/color
- VoiceOver: https://developer.apple.com/design/human-interface-guidelines/voiceover
- Playing haptics: https://developer.apple.com/design/human-interface-guidelines/playing-haptics
- Icons and SF Symbols: https://developer.apple.com/design/human-interface-guidelines/icons
- Tab bars: https://developer.apple.com/design/human-interface-guidelines/tab-bars
- Toolbars: https://developer.apple.com/design/human-interface-guidelines/toolbars
- Sidebars: https://developer.apple.com/design/human-interface-guidelines/sidebars
- Split views: https://developer.apple.com/design/human-interface-guidelines/split-views
- Sheets: https://developer.apple.com/design/human-interface-guidelines/sheets
- Alerts: https://developer.apple.com/design/human-interface-guidelines/alerts
- Search fields: https://developer.apple.com/design/human-interface-guidelines/search-fields
- Text fields: https://developer.apple.com/design/human-interface-guidelines/text-fields

## Developer Documentation

- SwiftUI accessibility modifiers: https://developer.apple.com/documentation/swiftui/view-accessibility
- SwiftUI accessibility fundamentals: https://developer.apple.com/documentation/swiftui/accessibility-fundamentals
- Enhancing SwiftUI accessibility: https://developer.apple.com/documentation/accessibility/enhancing-the-accessibility-of-your-swiftui-app
- Performing accessibility testing: https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app
- Accessibility Inspector: https://developer.apple.com/documentation/accessibility/accessibility-inspector
- NavigationStack: https://developer.apple.com/documentation/swiftui/navigationstack
- TabView: https://developer.apple.com/documentation/swiftui/tabview
- Dynamic Type size: https://developer.apple.com/documentation/swiftui/dynamictypesize
- Safe areas: https://developer.apple.com/documentation/swiftui/safearearegions
- Adopting Liquid Glass: https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass
- App Intents overview: https://developer.apple.com/documentation/appintents

## App Store and WCAG

- Accessibility Nutrition Labels overview: https://developer.apple.com/help/app-store-connect/manage-app-accessibility/overview-of-accessibility-nutrition-labels/. The labels declare support for VoiceOver, Voice Control, Larger Text, Dark Interface, Differentiate Without Color Alone, Sufficient Contrast, Reduced Motion, Captions, and Audio Descriptions. They are voluntary for now, and Apple says they will become required for new apps and updates. An app can declare a feature only when people can complete all of its common tasks with it, so set the epic's accessibility baseline with the labels in mind.
- Before release, use `evenbetter-accessibility-nutrition-labels` to work out which of these labels the app can declare in App Store Connect.
- WCAG 2.2, the current W3C Recommendation: https://www.w3.org/TR/WCAG22/
- WCAG 2.2 SC 2.5.8 Target Size (Minimum), Level AA, 24x24 CSS px: https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html. SC 2.5.5 Target Size (Enhanced) is Level AAA. Apple's 44x44 pt iOS target is the stricter rule for native controls.

## Local iOS Skills

- `evenbetter-swiftui-ui-patterns`: app wiring, tab architecture, NavigationStack, sheets, split views, forms, controls, theming, Dynamic Type, async state, and previews.
- `evenbetter-swiftui-view-refactor`: SwiftUI view decomposition, MV-first structure, state ownership, and accessibility modifier review.
- `evenbetter-swiftui-accessibility`: the corpus accessibility clauses (`../../corpus/ios/accessibility.md`) for VoiceOver, Dynamic Type, contrast, and hit targets, with correct-code examples.
- `evenbetter-ios-haptics`: `.sensoryFeedback` choices per event, Core Haptics for custom patterns, and haptics that stay accessible and consistent across screens.
- `evenbetter-swiftui-liquid-glass`: iOS 26+ Liquid Glass design and API usage.
- `evenbetter-ios-debugger-agent`: simulator runs, screenshots, UI hierarchy, logs, and runtime behavior, through the Xcode MCP server first when it is connected.
- `evenbetter-accessibility-tests`: runtime accessibility evidence from Apple's accessibility audit in UI tests and, on Xcode 27, a VoiceOver walk, recorded against an evenbetter-analyze report's findings.
- `evenbetter-ios-app-intents`: Siri, Shortcuts, Spotlight, widgets, controls, and system action surfaces.
- `evenbetter-swiftui-performance-audit`: SwiftUI performance when UX is affected by lag, hangs, or heavy rendering.

## Working Rules

- Do not paste large HIG content into specs or reviews. Summarize the relevant rule and cite the official source URL.
- Treat Apple HIG as design guidance and Apple Developer Documentation as API guidance.
- When a HIG page may have changed recently, check its entry on the what's new page before relying on older wording.
- For multi-screen planning, trace HIG and accessibility implications across entry points, transitions, state restoration, tabs, sheets, deep links, and completion states.
- For code, review whether SwiftUI standard controls already provide accessibility before adding custom modifiers.
