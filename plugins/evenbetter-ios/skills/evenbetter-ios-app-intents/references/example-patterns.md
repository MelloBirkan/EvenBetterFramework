# Example patterns

Use these as starting points when deciding what to expose first.

Contents:

- 1) Open-app handoff intent
- 2) Inline background action intent
- 3) Paired open-app and inline variants
- 4) Fixed choice via `AppEnum`
- 5) Entity-backed selection via `AppEntity`
- 6) Query dependency between parameters
- 7) Widget configuration intent
- 8) Shortcut phrase design

The run-mode lines below depend on the deployment target. `supportedModes` is iOS 26 and later, and `openAppWhenRun`, deprecated from iOS 26, stays correct below it. See the run-mode table in `references/code-templates.md`.

## 1) Open-app handoff intent

Best for:

- compose flows
- editors
- navigation to a destination
- actions that need the full app scene, auth state, or richer UI

Pattern:

- iOS 26 or later: `supportedModes = .foreground`; below iOS 26: `openAppWhenRun = true`
- keep the intent in the app target, since `openAppWhenRun = true` raises an error in an app extension
- collect lightweight input in the intent
- store one handled-intent payload in a central router or handoff service
- let the app scene translate that payload into tabs, sheets, routes, or windows

Example:

- "Open the app to compose a draft"
- "Open the app on a selected section"
- "Open an editor prefilled with content from the previous shortcut step"

## 2) Inline background action intent

Best for:

- quick create or update actions
- send, archive, mark, favorite or toggle operations
- actions that can finish without the main app UI

Pattern:

- iOS 26 or later: `supportedModes = .background`; below iOS 26: leave `openAppWhenRun` out, since it defaults to `false`
- perform the operation directly in `perform()`
- return dialog or snippet feedback so the result feels complete in Shortcuts or Siri
- keep a snippet under the HIG's 400-point height limit and let its view, not the dialogue text, carry the result

Example:

- "Create a task"
- "Send a message"
- "Archive a document"

## 3) Paired open-app and inline variants

Best for:

- actions that need both automation and richer manual review
- flows where some users want a background shortcut but others want to land in the app

Pattern:

- keep parameter names aligned between the two intents
- let the open-app version hand off to UI
- let the inline version call the same domain service directly
- expose both in `AppShortcutsProvider` with clear titles

Example:

- "Draft in app" and "Send now"
- "Open image post editor" and "Post images in background"

## 4) Fixed choice via `AppEnum`

Best for:

- tabs
- modes
- visibility levels
- small sets of filters or categories

Pattern:

- define an `AppEnum`
- give every case a user-facing `DisplayRepresentation`
- map enum cases into app-specific types in one place

Example:

- open a selected tab
- run an action in "public", "private", or "team" mode

## 5) Entity-backed selection via `AppEntity`

Best for:

- accounts
- projects
- lists
- destinations
- saved searches

Pattern:

- expose only the fields needed for display and lookup
- add `suggestedEntities()` for picker UX
- add `defaultResult()` only when there is a helpful default
- keep network or database fetch logic inside the query type, not the view layer

Example:

- choose an account to post from
- pick a project to open
- select a saved list for a widget

## 6) Query dependency between parameters

Best for:

- when one parameter changes the valid choices for another
- widget or control configuration where "account" determines "project"

Pattern:

- use `@IntentParameterDependency` inside the query
- read the upstream parameter
- scope entity fetching to the chosen parent value

Example:

- selected workspace filters available documents
- selected account filters available lists

## 7) Widget configuration intent

Best for:

- widgets that need a selected account, project, filter, or destination
- intent-driven controls that should reuse the same parameter model

Pattern:

- define a `WidgetConfigurationIntent`
- use the same `AppEntity` types that your shortcuts already use
- provide preview-friendly sample values when the widget needs them

Example:

- choose account plus list
- choose project plus status filter

## 8) Shortcut phrase design

Best for:

- making actions discoverable in Siri and Shortcuts

Pattern:

- keep phrases short and verb-led, and include the app name in each
- expose one or two canonical phrases, then add only a few natural variants
- use at most one optional parameter, with values people can say without seeing a list
- use precise `shortTitle` and `systemImageName`
- prefer an app schema over a custom phrase when the action fits one of Apple's app schema domains

Example:

- "Create a note with \(.applicationName)"
- "Open inbox in \(.applicationName)"
- "Send image with \(.applicationName)"
