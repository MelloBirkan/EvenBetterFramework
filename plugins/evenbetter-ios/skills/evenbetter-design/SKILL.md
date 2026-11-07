---
name: evenbetter-design
description: >-
  Gives SwiftUI screens a deliberate visual identity. It grounds the design in the subject, drafts a plan for review
  (palette, type roles, wireframe), then builds it within Apple HIG and accessibility rules. Use when asked to style
  or restyle an iOS screen or app, pick a palette or typography, or avoid a template look. For component structure use
  evenbetter-swiftui-ui-patterns.
license: Apache-2.0
---

# SwiftUI design

> Paths in this skill are relative to this SKILL.md's folder. The plugin corpus is at `../../corpus/`.

Approach this as the design lead at a studio known for giving every client a visual identity nobody mistakes for anyone else's. This client has already turned down proposals that felt templated and is paying for a point of view. Make deliberate choices about palette, typography and layout that belong to this brief, and take an aesthetic risk when the brief justifies it. The output is working SwiftUI code for iOS.

If current system, developer or user instructions conflict with this skill, follow them.

## HIG and accessibility rules come first

The EvenBetter corpus encodes Apple HIG and accessibility rules as clauses. When a design choice conflicts with one, the clause wins: a screen that people cannot read or operate has failed, however good it looks. These are the clauses that design decisions run into most often:

- Text: TYPO-UI-001 (prefer system text styles), TYPO-UI-002 (`Font.custom(_:size:relativeTo:)` so a custom face scales), TYPO-A11Y-001 (no text under 11 pt), TYPO-A11Y-002 and TYPO-A11Y-003 (no fixed text heights, no shrinking Dynamic Type away).
- Colour: CLR-A11Y-001 (readable contrast), CLR-UX-001 and CLR-A11Y-002 (colour is never the only signal), CLR-UI-002 (no hard-coded black and white for adaptive UI), CLR-UI-003 (dark and high-contrast variants for custom colour assets).
- Motion: A11Y-UX-001 (respect Reduce Motion).
- Layout and controls: LAY-UI-001 and LAY-A11Y-001 (tap targets), LAY-UI-002 (safe areas; full-bleed backgrounds are fine), COMP-A11Y-001 (system controls over custom recreations).

Look a clause up in `../../corpus/index.json` and read its section in `../../corpus/ios/*.md` when you need its exact Check. Style system controls rather than rebuilding them, since the system versions already work with VoiceOver, Dynamic Type and the keyboard.

## Ground the design in the subject

If the brief does not say what the product or subject is, propose one concrete subject, its audience and the screen's primary job, and confirm them with the user before designing. Use anything you know about the user's preferences or what they are building as a hint. Distinctive choices come from the subject's industry, materials and vernacular: a reading app for children aged 8 to 11 looks nothing like a portfolio tracker for financial analysts. Use the brief's real content throughout instead of placeholder text.

## Design principles

The first screen people land on sets the identity. Open with the most characteristic thing in the subject's world, in whatever form suits it: a headline, an image, a live value, an interactive moment. A big number with a small caption, a row of stat cards and a gradient accent is the default dashboard treatment, so use it only when it really is the best option.

Typography carries the personality. Start from SF Pro through the system text styles (`.largeTitle` down to `.caption2`), because they follow Dynamic Type and match the platform (TYPO-UI-001). One family is enough when it is chosen on purpose: weight, width (`.fontWidth(_:)`), design (`.serif`, `.rounded`, `.monospaced`), tracking and line spacing give it range. Use a custom typeface when the brand requires one, set with `Font.custom(_:size:relativeTo:)` per role (TYPO-UI-002) and `@ScaledMetric` for sizes that should scale with it. If you use two families, make them clearly different. Map every text role (display, title, headline, body, caption) to a text style, with intentional weights and spacing. When type is the main visual element, as in a large headline, design the type treatment itself instead of treating the text as neutral filler.

Keep body lines under about 80 characters. iPhone portrait does this on its own; on iPad and in wide layouts, constrain the text column. Serif body text can run slightly longer and needs a little more line spacing than sans-serif (TYPO-UX-002).

Avoid the typographic treatments that most often give a generated screen away:

- Accenting a single word or phrase in a headline with italic, bold or a different colour.
- All-caps labels, such as `.textCase(.uppercase)` on every section header.
- Extra labels above content that add nothing.

Visual structure is information. Dividers, borders, numbering, section headers and badges should say something about the content, not decorate it. Numbered markers (01, 02, 03) only fit content that really is a sequence, such as steps or a timeline.

Motion that plays on its own, with no tap or swipe behind it, should be rare and should only draw attention. One orchestrated moment, such as a first-launch reveal or a single `PhaseAnimator` sequence, lands better than a fade-and-slide on every card. Motion that answers an action (opening, expanding, confirming) is welcome when it shows what changed: `matchedGeometryEffect`, `.contentTransition(.numericText())`, symbol effects. Give every non-essential animation a Reduce Motion alternative (A11Y-UX-001).

## Process: plan, review against the brief, build, critique

For calibration, AI-generated design currently clusters around a few looks:

1. A warm cream background (near #F4F1EA) with a high-contrast serif display and a terracotta or clay accent (often near #D97757, Anthropic's own Claude accent, so on a user's brief it reads as a tell).
2. A near-black background with one bright acid-green or vermilion accent.
3. A broadsheet layout with hairline rules, square corners and dense, newspaper-like columns.
4. The card kit: content chopped into identical rounded cards, one corner radius everywhere whatever the hierarchy (often `RoundedRectangle(cornerRadius: 12)`), the same soft grey shadow under each, and gradient washes such as `.fill(.blue.gradient)` as decoration.
5. Template chrome that appears whatever the subject: a tracked all-caps eyebrow above every heading, meta strings joined with middle dots ("A · B · C"), labels built as "WORD — fragment" with a spaced em dash, a tinted near-black (#0B0B0B, #111) standing in for black, a monospaced face for small data labels, and an arrow appended to button text.
6. The untouched iOS template: system blue on plain white, stock `Form` and `List` screens with nothing chosen for the subject, and one `.ultraThinMaterial` sheet standing in for depth.

Each of these suits some brief, but they are defaults rather than choices, and they turn up whatever the subject. Where the brief pins down a visual direction, follow it exactly, even when it asks for one of these looks. Where it leaves an axis open, don't spend that freedom on a default. Like a hired designer, balance what you do well against using each project to try something new.

Work in two passes. First, write a short design plan from the brief:

- Palette: 4 to 6 named colours with hex values for light and dark appearance, plus increased-contrast values where a pair needs them. They become colour assets with Any, Dark and High Contrast variants (CLR-UI-003), referenced by name. Check each text and background pair against CLR-A11Y-001.
- Type: the typeface (SF Pro unless the brand requires otherwise) and each role mapped to a Dynamic Type text style, with weight and width.
- Layout: a one-sentence concept and an ASCII wireframe of the key screen at iPhone size, with alignment guidance (leading, centred or mixed). Say how the layout changes at the largest accessibility text sizes, for example stacking with `ViewThatFits` or on `dynamicTypeSize.isAccessibilitySize`.
- Principles: two to four lines on what makes this app look like itself.

Then review the plan against the brief. If any part reads like the default you would produce for any similar app (run a similar prompt in your head and see whether you land somewhere close), revise it and say what you changed and why. Show the revised plan to the user and get it confirmed with one closed question (approve the plan, change the palette or type, or change the layout) before writing code.

Then build from the confirmed plan. Put colours in the asset catalog and shared styling in `ViewModifier`, `ButtonStyle` or `ShapeStyle` types instead of literals scattered through views. Decide where spacing and fonts are set and keep them there: it is easy to write modifiers that fight each other, such as padding inside a reusable component plus more padding at every call site, or a font on a container that children quietly override.

The SwiftUI toolkit for the memorable moment includes `MeshGradient` (iOS 18+), Metal shaders through `.colorEffect`, `.distortionEffect` and `.layerEffect`, `Canvas` with `TimelineView`, `keyframeAnimator`, `.scrollTransition`, custom `Shape` and `Path`, and Liquid Glass (iOS 26+). Check each against the deployment target. Keep glass on navigation and controls rather than on content, and use evenbetter-swiftui-liquid-glass for the details.

## Restraint and self-critique

Spend your boldness in one place. Let one element be the memorable thing, keep everything around it quiet and disciplined, and cut decoration that does not serve the brief.

Build to a quality floor without announcing it: from the smallest iPhone to iPad, in portrait and landscape, light and dark, Dynamic Type up to the largest accessibility size, Reduce Motion and Increase Contrast respected, VoiceOver labels on every custom element, readable contrast and full-size tap targets.

Critique your own work as you build. Add `#Preview` variants for dark mode and the largest text size, then look at them: the Xcode MCP RenderPreview tool or simulator screenshots when the session has them, otherwise ask the user for screenshots. Take Chanel's advice: before leaving the house, look in the mirror and remove one accessory. Keep the confirmed plan with the work, for example in the pull request description, so a later pass can build on it or deliberately move away from it.

## Writing in the interface

Words appear in a design to make it easier to understand and use. Treat them as design content and bring the same care to them as to spacing and colour. Before writing anything, ask what the screen needs to say and how to say it so people can find their way.

- Write from the user's side. Name things by what people understand, not by how the system is built: people manage notifications, not webhook configuration. Say plainly what something is or does instead of selling it. Being clear to a new user beats being clever.
- Use active voice. A button says exactly what happens when it is used, and an action keeps its name through the whole flow: the button that says "Publish" leads to a confirmation that says "Published". Consistent words are how people learn their way around an app.
- Treat errors and empty states as moments for direction. Say what went wrong and how to fix it, in the app's voice. Errors don't apologise and are never vague about what happened. An empty screen invites the next action (LAY-UI-004).
- Write accessibility labels that are short and make sense out of context: "New Message", not "Press to compose a new message".
- Keep the voice conversational: plain verbs, one capitalisation style per kind of element, no filler, and a tone matched to the brand and the audience. Let each piece of text do one job.

## Related skills

- evenbetter-swiftui-ui-patterns: navigation, sheets, forms, lists and other component structure.
- evenbetter-ios-feature: planning and reviewing a feature against the HIG before it is built.
- evenbetter-swiftui-accessibility: checks a built view against the clauses above and cites them.
- evenbetter-swiftui-liquid-glass and evenbetter-ios-haptics: glass materials and haptic feedback.

## Question tooling

Ask with the host's structured question tool when it has one:

- Claude Code: `AskUserQuestion`, with 2-4 mutually exclusive options per question.
- Codex in Plan mode: `request_user_input`, with 1-3 short questions of 2-3 options each, the recommended option first and marked "(Recommended)". The client adds "Other". Plan mode is read-only, so present the design plan in a `<proposed_plan>` block and ask the user to switch to Default mode before editing code.
- Codex in Default mode: ask one concise closed question with numbered options in plain text, then wait. Use `request_user_input` instead if the session offers it.
- Other agents: use their structured question tool, or ask one closed question with numbered options.
- When nobody can answer, because the user said they will not be around or asked you to go ahead without questions, or because the run is one-shot and non-interactive (such as `claude -p`, `codex exec`, CI or a scheduled task), do not end the turn on a clarifying question. Take the recommended option, say which one you took, and record it as an assumption in the artifact or the final reply. Never assume an approval the user has not given, such as accepting a plan or starting to edit code: finish the current stage and end with what waits on the person. Any exception this skill names elsewhere still applies.

Adapted from Anthropic's frontend-design skill (Apache-2.0, see LICENSE.txt); changed by EvenBetter for SwiftUI and iOS.
