# Question Patterns

Ask only questions that materially change the app/epic UX, accessibility strategy, navigation architecture, review scope, or implementation path. Every question must be multiple-choice when the environment supports options.

## Format

- Ask 1-3 questions per round.
- Use 2-3 mutually exclusive choices per question.
- Put the recommended option first and label it as recommended when the tool supports labels.
- Avoid "anything else?" or broad discovery questions.
- If the user chooses "Other", convert their answer into a concrete assumption and continue with another closed question only if needed.

## Epic Intake

Use these patterns for multi-screen epics or app-from-scratch work:

- Product shape:
  - Add a multi-screen feature to an existing app
  - Redesign an existing iOS flow
  - Plan a new iOS app from scratch
- Navigation model:
  - Tab-based top-level areas
  - Single stack with pushed destinations
  - Split view or adaptive iPad-first layout
- Primary user journey:
  - Create or submit content
  - Browse, filter, and inspect content
  - Configure, manage, or administer data
- Accessibility strategy:
  - Standard HIG baseline for all screens
  - High-accessibility baseline with full VoiceOver and Dynamic Type review
  - Specialized support for keyboard, Switch Control, Voice Control, or App Intents
- Platform scope:
  - iPhone-first with iPad adaptation
  - Universal iPhone/iPad from the start
  - iOS now, iPadOS later

## Cross-Screen Tradeoffs

- State restoration:
  - Preserve per-tab navigation history
  - Reset flow after completion
  - Return to the entry screen after completion
- Modal policy:
  - Sheets for focused tasks
  - Push navigation for durable destinations
  - Full-screen cover only for immersive or blocking flows
- Empty/error strategy:
  - Per-screen local states
  - Shared reusable state components
  - Centralized error surface with local recovery
- System surfaces:
  - No external system actions
  - App Intents for key actions
  - Widgets/Shortcuts/Spotlight as first-class entry points

## Screenshot Requests

Ask for screenshots only when visual evidence changes review quality. Be specific so the user can identify the screens.

- Flow overview: "Send the first screen, the main action screen, and the completion screen."
- Dynamic Type: "Send the most text-heavy screen at one of the largest accessibility text sizes."
- Navigation: "Send the tab/sidebar/root screen and one pushed detail screen."
- Modal: "Send the sheet or full-screen modal at its default state."
- Error/empty: "Send one representative error state and one representative empty state."
- Destructive: "Send the confirmation UI before the destructive action."

## Review Disposition

When findings need a decision, ask closed choices:

- Fix timing:
  - Fix before merge
  - Track as follow-up epic ticket
  - Accept as intentional deviation
- Scope:
  - Apply to one screen
  - Apply to the whole flow
  - Apply as app-wide design-system rule
- Evidence:
  - Proceed with code-only review
  - Wait for requested screenshots
  - Run simulator review if available
