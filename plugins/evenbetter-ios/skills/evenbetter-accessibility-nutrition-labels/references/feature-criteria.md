# Feature criteria

Contents: How to read this file, VoiceOver, Voice Control, Larger Text, Dark Interface, Differentiate Without Color Alone, Sufficient Contrast, Reduced Motion, Captions, Audio Descriptions.

## How to read this file

This file summarizes Apple's evaluation criteria pages, read on 2026-11-07. Each page lives under `https://developer.apple.com/help/app-store-connect/manage-app-accessibility/` with the slug given in its section. When a page disagrees with this summary, the page wins. Apple renders these pages with JavaScript, so read them with a scraper that renders pages.

Each section gives:

- **Devices**: where App Store Connect offers the feature. `2-evidence` leaves a feature out of a device's matrix when Apple does not offer it there.
- **Apple's bar**: when Apple says you may indicate support.
- **Check**: the criteria a manual check should cover.
- **Turn it on**: the iPhone and iPad setting, from Apple's "Performing accessibility testing for your app". Each criteria page links Apple's guide for every other device.
- **Code signals**: patterns that contradict a criterion. They are notes for the manual check, never blockers, because this skill does not add findings. Suggest evenbetter-analyze to record one.
- **Manual check**: what the person does for the question in `2-evidence`.

Apple's general rule applies to every feature: people must be able to complete all of the common tasks with the feature on, and bugs significant enough to change that answer mean you don't indicate support. Apple also says not to build your own version of VoiceOver or Voice Control. For the other features, a custom implementation such as the app's own dark theme can count, and an in-app setting should match the system setting or be more granular.

## VoiceOver

Page: `voiceover-evaluation-criteria`. Devices: all.

Apple's bar: people can navigate and interact with every visual element, including text, media, buttons and controls, using only VoiceOver, and complete the common tasks that way.

Check:

- Every control has a concise label that makes sense out of context. Labels leave out control types and states such as "checkbox" or "checked", which come from traits.
- Meaningful images are described, and decorative ones are ignored. Charts carry accessibility information or a text alternative. When people can upload images, they can add a description.
- VoiceOver speaks each element's type and its state or value.
- All visible text can be spoken. Custom keyboards and PIN entry work with VoiceOver.
- Temporary status banners and important alerts are announced, often with an `AccessibilityNotification`.
- Navigation reaches every element in a logical order, forward and backward, without skipping or looping. The reading position doesn't reset when content reloads.
- When a modal appears, focus moves into it, and the content behind it can't be reached. People can dismiss it with Escape or `accessibilityPerformEscape`.
- Long presses and context menus are also offered as custom actions. Drag and drop and multi-touch gestures have an accessible route.
- Custom controls behave like the system ones.

Turn it on: Settings > Accessibility > VoiceOver. Use a physical device, because Apple says VoiceOver isn't available in Simulator.

Code signals: an `onTapGesture` on `Text` or `Image` that performs an action, an icon-only control with no label, a gesture with no other way to do the same thing.

Manual check: with VoiceOver on, complete each task using only VoiceOver gestures, with the screen curtain on if you can (a three-finger triple tap). Move forward and back through every screen, open and dismiss each sheet and alert, and listen for each element's name, type and state.

## Voice Control

Page: `voice-control-evaluation-criteria`. Devices: iPhone, iPad, Mac and Vision. Apple says it isn't supported on Apple TV or Apple Watch.

Apple's bar: people can complete all of the common tasks using only voice commands, without touch.

Check:

- Saying "Show numbers" puts a number on every interactive element. Saying "Show names" shows a name on every one.
- "Tap" or "Click" plus a name or number drives each task.
- Names match the visible text. When people would say something else, add it with `accessibilityInputLabels(_:)`.
- Controls hidden behind swipes, long presses or hover can be reached by voice, for example through a custom action.
- Scrolling works ("Scroll down"), and so do panning and zooming in maps or canvases ("Pan left", "Zoom out"). Multi-touch gestures can be spoken.
- Recording or custom dictation starts and stops by voice.
- People can dictate into every text field ("Type" and the text), select text ("Select" and the text) and delete it ("Delete that").
- Apple also suggests letting people cancel or extend auto-play and auto-hide delays.

Turn it on: Settings > Accessibility > Voice Control. Use a physical device, because Apple says Voice Control isn't available in Simulator.

Code signals: an `accessibilityLabel` that differs from the visible text, swipe-only or long-press-only actions, a custom text field.

Manual check: with Voice Control on, complete each task by voice alone. Say "Show names" and "Show numbers" on every screen, and dictate and edit text in every field.

## Larger Text

Page: `larger-text-evaluation-criteria`. Devices: iPhone, iPad, Apple TV, Apple Watch and Vision. Apple says it isn't supported on Mac.

Apple's bar: people can enlarge text to at least 200 percent, or to the system's largest size. On iOS, Dynamic Type goes past 200 percent at AX3, and body text can go past 300 percent at AX5. On watchOS the largest size is more than 140 percent of the default.

Check:

- Text and meaningful icons grow as large as possible while the layout keeps its hierarchy.
- Body text grows without overlapping layouts or severe truncation. Truncated text is available in full somewhere else.
- Controls that can't grow, such as tab bars, show the Large Content Viewer.
- Web views in common tasks offer their own text size control, or hand off to Safari.
- Zoom and Hover Text don't count.
- Test in a language with long words, a right-to-left language, and one with diacritics, where the app is localized.

Turn it on: Settings > Accessibility > Display & Text Size > Larger Text. Turn on Larger Accessibility Sizes, then try AX3 and the largest size.

Code signals: `.font(.system(size:))` without a text style, `.dynamicTypeSize(_:)` with a cap below AX3, `.lineLimit(1)` on primary text, fixed `.frame(height:)` around text.

Manual check: complete each task at AX3 and at the largest size. Check that no text overlaps, clips or disappears.

## Dark Interface

Page: `dark-interface-evaluation-criteria`. Devices: all.

Apple's bar: every common task is dark by default, leaving out third-party and user content, or the app lets people turn on a mode or setting that keeps it dark. That can be the system's Dark Mode, the app's own dark color scheme, or, as a last resort, Smart Invert.

Check:

- The interface stays dark. Apple says even a temporary flash of bright content can cause discomfort, so check launch screens, web views, images, empty states and every transition.
- With Smart Invert, colors keep their meaning (a red Delete button can invert to green), and media does not invert.
- For translucent views, consider reducing translucency under Increase Contrast or Reduce Transparency.
- Test dark mode together with Increase Contrast.

Turn it on: Settings > Appearance > Dark. On iOS 26 and earlier, the Dark Mode options are under Display & Brightness. Control Center has it too: touch and hold the brightness control, then tap Dark Mode.

Code signals: `.preferredColorScheme(.light)` on a whole screen or the app, hard-coded white backgrounds, color assets without a dark variant.

Manual check: set the appearance to Dark and complete each task. Watch for any bright screen, sheet, image or flash, and repeat with Increase Contrast on.

## Differentiate Without Color Alone

Page: `differentiate-without-color-alone-evaluation-criteria`. Devices: all.

Apple's bar: people can complete every common task without relying on color. Shapes, text or position carry any meaning that color carries.

Check:

- Statuses, errors, selection states, required fields and chart series can be told apart without color.
- Chart colors follow the same order as the legend.
- Where color is the only difference (for example in some charts), a setting or several color schemes can solve it. Apple calls a setting the last resort.

Turn it on: Apple suggests testing with the Grayscale color filter: Settings > Accessibility > Display & Text Size > Color Filters, then Grayscale. Apple notes that grayscale is not what color-blind people see, but it finds the problems. When the app reads `accessibilityDifferentiateWithoutColor`, also turn on Display & Text Size > Differentiate Without Color.

Code signals: a status shown only by `.foregroundColor` or a colored dot, red and green used as the only pair.

Manual check: turn on the Grayscale filter and complete each task. Every status, error and selection must still be clear.

## Sufficient Contrast

Page: `sufficient-contrast-evaluation-criteria`. Devices: all.

Apple's bar: the common tasks' text, buttons and other controls meet general contrast guidelines by default, usually 4.5 to 1 for most text. When they don't, apps built on Apple frameworks can still indicate support if Increase Contrast brings everything to sufficient contrast, and apps on other frameworks can offer several color schemes.

Check:

- Text, icons and controls, in light mode and, if the app supports it, dark mode.
- Interactive controls and non-text states, such as a checked and unchecked box. Apple says 3 to 1 is commonly recommended for non-text contrast.
- Translucent materials and blurs behind text.
- Test with Increase Contrast on and Reduce Transparency off, and with both on.

Turn it on: Apple asks for Bold Text, Increase Contrast and Reduce Transparency all on while testing. On iPhone and iPad they are under Settings > Accessibility > Display & Text Size. Measure with Xcode's Accessibility Inspector or another contrast checker.

Code signals: gray text on a colored background, `.opacity(_:)` on text, custom colors without an increased-contrast variant.

Manual check: with the three settings on, complete each task and measure the text and controls you are unsure of. Check light and dark when the app supports both.

## Reduced Motion

Page: `reduced-motion-evaluation-criteria`. Devices: all.

Apple's bar: once the app shows no problematic motion triggers to people who turn on Reduce Motion, you may indicate support.

Check:

- Depth effects (parallax, animated blur, depth of field) are turned off or changed.
- Multi-axis motion, multi-speed motion, spinning and vortex effects are turned off or changed.
- Apple says to consider stopping auto-advancing carousels and other ongoing motion, or to give people a control that stops it.
- Decorative animation can stop entirely. Motion that carries meaning, such as an item moving to a cart, becomes a dissolve, a highlight fade or a color shift instead of disappearing.

Turn it on: Settings > Accessibility > Motion > Reduce Motion.

Code signals: `repeatForever` animations, scale or rotation effects, and parallax that never read `accessibilityReduceMotion`.

Manual check: turn on Reduce Motion and complete each task. Note any motion that still zooms, spins, slides across axes or never stops.

## Captions

Page: `captions-evaluation-criteria`. Devices: all. Apple notes that watchOS apps don't play video, though they can offer transcripts.

Apple's bar: video played in the app has captions, including game interstitials and audible dialogue, or audio-only content has text transcripts. Transcripts don't need to be time-synchronized.

Check:

- Captions come on by default when the system captions setting is on. Apple prefers CC or SDH, which include relevant sounds, to dialogue-only subtitles.
- For third-party video, people can include caption data, and they can tell which items have captions, for example from a CC or SDH badge.
- If the app can show captions but very little captioned content is available, Apple says not to indicate support.

Turn it on: Settings > Accessibility > Subtitles & Captioning > Closed Captions + SDH.

Code signals: a custom player that ignores the system caption setting, a player that picks a media option on its own.

Manual check: turn on Closed Captions + SDH and play the media in each task. Captions should appear without any in-app change. For third-party media, check that captioned items are marked and that a fair share of the content has captions.

## Audio Descriptions

Page: `audio-descriptions-evaluation-criteria`. Devices: all.

Apple's bar: video has narrated descriptions of what happens on screen, including interstitials, opening sequences, cut scenes and tips shown only visually.

Check:

- Descriptions come on by default when the system Audio Descriptions setting is on.
- For third-party video, people can include an audio description track, and they can tell which items have one, for example from an AD badge.
- If the app can select descriptions but very little described content is available, Apple says not to indicate support.

Turn it on: Settings > Accessibility > Audio Descriptions.

Code signals: a custom player that ignores the system setting.

Manual check: turn on Audio Descriptions and play the video in each task. The described track should play without any in-app change.
