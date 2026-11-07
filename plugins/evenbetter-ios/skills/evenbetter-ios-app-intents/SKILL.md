---
name: evenbetter-ios-app-intents
description: >-
  Designs App Intents, app entities and App Shortcuts that expose an iOS app's actions and content to Shortcuts, Siri,
  Spotlight, widgets and controls, including iOS 27 schemas and snippets. Use when adding AppIntent, AppEntity or
  EntityQuery types or Shortcuts phrases, or when routing an intent into the app. To plan the screen an intent opens,
  use evenbetter-ios-feature.
---

# iOS App Intents

> Paths in this skill and its references are relative to this SKILL.md's folder.

## Overview

Expose the smallest useful action and entity surface to the system. Start with the verbs and objects people would want outside the app, then build a narrow App Intents layer that completes in place or hands off cleanly into the main app.

Read these references as needed:

- `references/first-pass-checklist.md` for choosing the first intent and entity surface
- `references/example-patterns.md` for concrete example shapes to copy and adapt
- `references/code-templates.md` for generalized App Intents code templates
- `references/system-surfaces.md` for Shortcuts, Siri, Spotlight, widgets, snippets and other system entry points

Apple's Xcode 27 agent skills for App Intents may also be installed. `xcrun agent skills export` copies them out of Xcode for other agents, and third-party copies name them app-intents-specialist and app-intents-whats-new-27. Use them for framework API detail. This skill keeps the design layer: which actions to expose, how they hand off, and what Apple's HIG asks of phrases, snippets and dialogue.

If current system, developer or user instructions conflict with this skill, follow them.

## Questions

Ask only when the answer changes what gets built: which actions to expose first, or whether an action opens the app. Ask one closed question with numbered options and the recommended option first. In Claude Code use `AskUserQuestion`. In Codex use `request_user_input` in Plan mode, and a plain-text numbered question in Default mode. Other agents use their own question tool or a numbered plain-text question.

Codex Plan mode is read-only. There, present the proposed intents in a `<proposed_plan>` block and ask the user to switch to Default mode before editing code.

## Core workflow

### 1. Start with actions, not screens

- Identify the one to three highest-value actions that should work outside the app UI.
- Prefer verbs like compose, open, find, filter, continue, inspect or start.
- Do not mirror the app's whole navigation tree as intents.

### 2. Define a small entity surface

- Add `AppEntity` types only for the objects the system needs to understand or route.
- Keep the entity shape narrower than the app's persistence model.
- Add `EntityQuery` or other query types only where disambiguation or suggestions help.

### 3. Decide whether the action completes in place or opens the app

- Use intents that run in the background for actions that can finish from the system surface.
- For an action that should land in a specific in-app workflow, pick the API by deployment target:
  - iOS 26 or later: declare `static let supportedModes: IntentModes = .foreground`. Use `[.background, .foreground(.deferred)]` when the action starts in the background and finishes in the app, or `[.background, .foreground(.dynamic)]` when it may or may not need the app. `openAppWhenRun` is deprecated from iOS 26.
  - Below iOS 26: keep `static let openAppWhenRun = true`, which is still the right API there. Replace it with `supportedModes` when the target moves to iOS 26.
- Keep an intent that opens the app in the app target. Apple documents that `openAppWhenRun = true` raises an error when the intent runs in an app extension.
- When the app must react inside the main scene, add one clear runtime handoff path instead of scattered ad hoc routing.
- If the action works both ways, consider shipping an inline version and an open-app version rather than forcing one compromise.

### 4. Make the actions discoverable

- Prefer an app schema when the action fits one of Apple's app schema domains, and use App Shortcuts for features unique to the app.
- Add `AppShortcutsProvider` entries for the first set of high-value intents. Apple allows up to 10 per app.
- Choose titles, phrases and symbols that make sense in Shortcuts, Siri and Spotlight. Keep phrases direct and task-oriented; each one includes the app name and is short enough to say aloud.
- Reuse the same action model for widgets and controls when a widget configuration or intent-driven control already needs the same parameters.

### 5. Validate the runtime handoff

- Build the app and confirm the intents target compiles cleanly.
- Verify the app opens or routes to the expected place when an intent runs.
- With an iOS 27 SDK, cover intents, entities and queries with the AppIntentsTesting framework.
- Summarize which actions are now exposed, which entities back them and how the app handles invocation.

## iOS 27 additions

Use these only when the deployment target and SDK allow. Sources: Apple's App Intents updates page, the HIG change log and WWDC26 sessions 240, 295 and 345.

- Schemas: an app entity that adopts an entity schema feeds Spotlight's semantic index, and an intent that adopts an intent schema needs no App Shortcut phrases for Siri to find it. In Xcode 27, Fix-Its point out related schemas that are missing.
- View Annotations: an API that maps on-screen views to app entities, so the system can tell which entity each view shows. `NSUserActivity` still covers a single primary item.
- AppIntentsTesting: runs intents, entities, enums and queries out of process, the way Siri and Shortcuts do, and tests Siri and Spotlight integration without UI automation.
- Other new types: `EntityCollection` for large entity sets that resolve on demand, `LongRunningIntent` for longer background work with progress, and `allowedExecutionTargets` to say which target (app, App Intents extension or widget extension) may run an intent.
- HIG Snippets (new page, June 2026): a snippet is a confirmation or a result, built from dialogue, a custom view at most 400 points tall and system buttons. Keep it legible in light and dark mode and at large text sizes, and deep-link into the app for more detail. Give a confirmation's primary button a descriptive label such as Order, since the default is Continue. Let the custom view carry the purpose instead of the dialogue text. Snippets are not supported on tvOS, visionOS or watchOS.
- HIG App Shortcuts (updated June 2026): prefer app schemas for common domains and keep App Shortcuts for features no schema covers. Give a shortcut at most one optional parameter, with predictable values people can say without seeing a list. Order shortcuts by importance, surface them with Siri tips (`SiriTipUIView`), and put all critical information in the full dialogue for audio-only devices such as AirPods and HomePod.

## Strong defaults

- Prefer a dedicated intents target or module for the system-facing layer.
- Keep intent types thin. Business logic stays in app services or domain models.
- Keep app entities small and display-friendly.
- Use `AppEnum` for fixed app choices such as tabs, modes or visibility levels before reaching for a full entity type.
- Prefer one predictable routing surface in the main app scene or root router.
- Treat App Intents as system integration infrastructure, not only as a Shortcuts feature.

## Anti-patterns

- Exposing every screen or tab as its own intent without real user value.
- Mirroring the entire model graph as `AppEntity` types.
- Hiding runtime handoff in global side effects with no clear app entry path.
- Adding App Shortcuts with vague phrases or generic titles.
- Declaring `supportedModes` while the deployment target is below iOS 26, where it does not exist, or keeping `openAppWhenRun` after the target has moved to iOS 26.
- Treating the first App Intents pass as a broad taxonomy project instead of a small useful release.

## Notes

- Apple documentation to use as primary references:
  - [Making actions and content discoverable by Apple Intelligence](https://developer.apple.com/documentation/appintents/making-actions-and-content-discoverable-by-apple-intelligence)
  - [Creating your first app intent](https://developer.apple.com/documentation/appintents/creating-your-first-app-intent)
  - [Adopting App Intents to support system experiences](https://developer.apple.com/documentation/appintents/adopting-app-intents-to-support-system-experiences)
  - [Configuring the runtime behavior of your app intents](https://developer.apple.com/documentation/appintents/configuring-the-runtime-behavior-of-your-app-intents)
  - [App Intents updates](https://developer.apple.com/documentation/updates/appintents)
  - [App schema domains](https://developer.apple.com/documentation/appintents/app-schema-domains)
  - [App Shortcuts](https://developer.apple.com/documentation/appintents/app-shortcuts) and [Displaying static and interactive snippets](https://developer.apple.com/documentation/appintents/displaying-static-and-interactive-snippets)
  - [Testing your App Intents code](https://developer.apple.com/documentation/appintentstesting/testing-your-app-intents-code)
  - [HIG: Snippets](https://developer.apple.com/design/human-interface-guidelines/snippets) and [HIG: App Shortcuts](https://developer.apple.com/design/human-interface-guidelines/app-shortcuts)
- When App Intents APIs or platform behavior may have changed, check Apple's documentation with the session's web tools. Apple pages render with JavaScript, so prefer a scraper that renders pages, or the JSON form at `https://developer.apple.com/tutorials/data/documentation/<path>.json`.
- A good first pass often includes one open-app intent, one action intent, one or two entity types and a small `AppShortcutsProvider`.
- Good example families to cover:
  - open a destination or editor in the app
  - perform a lightweight action inline without opening the app
  - choose from a fixed enum such as a tab or mode
  - resolve one or more entities through `EntityQuery`
  - power widget configuration or controls from the same entity surface
