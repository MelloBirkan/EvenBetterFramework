# System surfaces

Think in system entry points, not just in shortcuts.

## Shortcuts

- Good for direct actions and automation chains.
- Expose the actions that users would actually want to reuse.
- Add `AppShortcutsProvider` entries for the first high-value intents, up to the HIG limit of 10 per app.

## Siri and app schemas

- Good for clear verbs and deep-linkable actions.
- Phrase titles and parameters so the system can present and disambiguate them clearly.
- When an action or entity fits one of Apple's app schema domains, adopt the schema. Apple's HIG prefers schemas for common domains and keeps App Shortcuts for unique features. On iOS 27, an intent that adopts an intent schema needs no App Shortcut phrases.
- Put all critical information in the full dialogue, because people may hear the response on AirPods or HomePod without a screen.

## Snippets

- A snippet is a compact view shown with an intent's response in Siri, Spotlight or Shortcuts. A confirmation snippet asks people to confirm or cancel; a result snippet shows the outcome.
- Keep the custom view at most 400 points tall, legible in light and dark mode, and mindful of large text sizes. Deep-link into the app for more detail.
- Label a confirmation's primary button with the action (Order, Send) rather than the default Continue.
- Snippets are not supported on tvOS, visionOS or watchOS.

## Spotlight

- Good for discoverability of both actions and entities.
- Use strong display representations and clear type names.
- On iOS 27, entities that adopt an entity schema feed Spotlight's semantic index.

## Widgets, Live Activities, and controls

- Good when the same actions already make sense as intent-driven entry points.
- Reuse the same intent surface where practical instead of inventing separate action models.

## General guidance

- Design one small action layer that can serve several surfaces.
- Keep action names concrete and user-facing.
- Prefer structured entities and parameters over trying to encode everything in free-form text.
- Start narrow, ship a useful set, then expand based on real use.
