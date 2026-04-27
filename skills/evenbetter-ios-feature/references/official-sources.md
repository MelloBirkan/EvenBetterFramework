# Official Sources

Use this file when planning or reviewing iOS UX, accessibility, Apple HIG conformance, and SwiftUI implementation details. Prefer official Apple sources and verify current API behavior when availability or guidance matters.

## Core Apple HIG

- Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines/
- Accessibility: https://developer.apple.com/design/human-interface-guidelines/accessibility
- Typography and Dynamic Type: https://developer.apple.com/design/human-interface-guidelines/typography
- Layout: https://developer.apple.com/design/human-interface-guidelines/layout
- Gestures: https://developer.apple.com/design/human-interface-guidelines/gestures
- Buttons: https://developer.apple.com/design/human-interface-guidelines/buttons
- Color: https://developer.apple.com/design/human-interface-guidelines/color
- VoiceOver: https://developer.apple.com/design/human-interface-guidelines/voiceover
- Icons and SF Symbols: https://developer.apple.com/design/human-interface-guidelines/icons
- Tab bars: https://developer.apple.com/design/human-interface-guidelines/tab-bars
- Toolbars: https://developer.apple.com/design/human-interface-guidelines/toolbars
- Sheets: https://developer.apple.com/design/human-interface-guidelines/sheets
- Alerts: https://developer.apple.com/design/human-interface-guidelines/alerts
- Text fields: https://developer.apple.com/design/human-interface-guidelines/text-fields
- Search fields: https://developer.apple.com/design/human-interface-guidelines/search-fields

## Developer Documentation

- SwiftUI accessibility modifiers: https://developer.apple.com/documentation/swiftui/view-accessibility
- SwiftUI accessibility fundamentals: https://developer.apple.com/documentation/swiftui/accessibility-fundamentals
- Enhancing SwiftUI accessibility: https://developer.apple.com/documentation/accessibility/enhancing-the-accessibility-of-your-swiftui-app
- Performing accessibility testing: https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app
- Accessibility Inspector: https://developer.apple.com/documentation/accessibility/accessibility-inspector
- Dynamic Type size: https://developer.apple.com/documentation/swiftui/dynamictypesize
- SwiftUI gestures: https://developer.apple.com/documentation/swiftui/gestures
- Safe areas: https://developer.apple.com/documentation/swiftui/safearearegions
- App Intents overview: https://developer.apple.com/documentation/appintents

## Local iOS Skills

- `$swiftui-ui-patterns`: layout, navigation, sheets, forms, controls, theming, Dynamic Type, and component patterns.
- `$swiftui-view-refactor`: SwiftUI view decomposition, MV-first structure, state ownership, and accessibility modifier review.
- `$swiftui-liquid-glass`: iOS 26+ Liquid Glass design and API usage.
- `$ios-debugger-agent`: simulator, screenshots, UI hierarchy, logs, and runtime behavior.
- `$ios-app-intents`: Siri, Shortcuts, Spotlight, widgets, controls, and system action surfaces.
- `$swiftui-performance-audit`: SwiftUI performance when UX is affected by lag, hangs, or heavy rendering.

## Working Rules

- Do not paste large HIG content into plans or reviews. Summarize the relevant rule and cite the official source URL.
- Treat Apple HIG as design guidance and Apple Developer Documentation as API guidance.
- For screenshots, review visible hierarchy, reading order, target size, Dynamic Type resilience, color contrast, system component use, and state feedback.
- For code, review whether SwiftUI standard controls already provide accessibility before adding custom modifiers.
