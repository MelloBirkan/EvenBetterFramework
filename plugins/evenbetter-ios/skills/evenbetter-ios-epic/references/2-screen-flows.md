# 2 Screen Flows

## Role

Design multi-screen user journeys and interaction flows at the product level.

## Process

1. Read `.evenbetter/<epic-name>/ios-ux-brief.md`.
2. Explore current app flows and navigation if the project already exists.
3. Read `question-patterns.md`, especially `2 Screen Flows`, and use multiple-choice questions for flow decisions. Ask roughly 3-10 questions in this phase when needed to close cross-screen assumptions, edge cases, and unspoken flow expectations. For app-scale work, expect multiple rounds and exceed 10 total questions when the flow map is still ambiguous.
4. Run the core-flow interview below before drafting. Ask flow-by-flow questions for every primary flow; do not rely on a single generic navigation question.
5. Think through entry, each action, visible feedback, navigation, completion, cancellation, and recovery for each flow.
6. Write `.evenbetter/<epic-name>/screen-flows.html` using the structure in `HTML Output Structure` below. The HTML replaces the previous Markdown spec — do not also write `screen-flows.md`.

## Core-Flow Interview

Use closed questions from `question-patterns.md`. Keep each round to 1-3 questions, then continue with another round when answers expose new gaps.

### Round 1: Flow Inventory

Clarify:

- The set of primary, secondary, and deferred flows.
- The top-level navigation model and owning root screen for each flow.
- Whether each flow starts in-app, from onboarding/auth/permissions, or from external system surfaces.
- Whether iPad/adaptive behavior changes the flow structure.

### Round 2: Per-Flow Decisions

Repeat this round for each primary flow. Do not write the flow until every item is decided or intentionally deferred:

- Entry state: existing data, empty/first-use, signed-out, permission-blocked, offline, or deep-linked.
- Screen sequence: root, list/detail, task, confirmation, completion, and any optional branch screens.
- Presentation style: push, tab, sheet, popover, split view, alert, full-screen cover, or external entry.
- Primary and destructive actions: visible placement, disabled/loading behavior, confirmation, and undo/recovery.
- Completion: return target, success feedback, next suggested action, and cross-screen state update.
- Cancellation/back behavior: standard back, dismiss, confirmation, draft preservation, or blocked dismissal.
- Failure/recovery: inline retry, preserved input, error screen, permission education, offline queue, or central error surface.

### Round 3: Cross-Flow Edge Cases

Ask this round before drafting when more than one screen or more than one user state exists:

- State restoration, per-tab history, draft persistence, and post-completion reset behavior.
- Authentication, permissions, empty/loading/error states, destructive actions, offline/degraded mode, and data conflicts.
- Dynamic Type reflow, VoiceOver headings/grouping/announcements, custom actions, gesture alternatives, keyboard/Switch Control/Voice Control implications.
- Screenshot or simulator evidence for default, large text, dark mode, error, empty, modal, destructive, and completion states.

## Drafting Gate

Do not write `screen-flows.html` until every primary flow has:

- Purpose and owning root or entry point.
- Screens involved and presentation style for each meaningful step.
- Primary action, visible feedback, and loading/disabled behavior.
- Completion destination and cross-screen state update.
- Failure, cancellation, back/dismiss, and recovery behavior.
- Accessibility notes for Dynamic Type and VoiceOver.
- Screenshots or simulator states needed for later review, or an explicit code-only rationale.

## HTML Output Structure

`screen-flows.html` is one self-contained file. No external CSS, no external JS, no remote fonts. Use system fonts (`-apple-system, "SF Pro Text", system-ui, sans-serif`). Buttons, controls, and inputs must look like iOS but do not need to be interactive. Pixel-perfect fidelity is not the goal — recognizability is.

For each meaningful screen state, render a `.device-frame` containing a `.ios-screen` that visually approximates the corresponding iOS surface using HTML and CSS alone (no images, no remote assets). Use CSS shapes or inline `<svg>` for icons. Use real copy from the spec, not Lorem Ipsum.

Each preview is accompanied by a sibling `<details class="swiftui-mapping">` block that explains how an implementing agent should translate the preview into SwiftUI. This is the artifact's iOS-specific contribution: the HTML preview is the visual target, and the mapping block is the bridge to SwiftUI.

Minimum structure:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Screen Flows — <epic name></title>
  <style>
    /* See "iOS Preview Styles" below. Keep all CSS in this single <style> block. */
  </style>
</head>
<body>
  <header class="doc-header">
    <h1>Screen Flows: <epic name></h1>
    <p class="doc-summary">One-paragraph reminder of the epic's audience, navigation model, and accessibility baseline.</p>
  </header>

  <main>
    <section class="flow" id="flow-<kebab-name>">
      <header class="flow-header">
        <h2>Flow: <Name></h2>
        <p class="flow-purpose"><short description></p>
      </header>

      <dl class="flow-meta">
        <dt>Entry point</dt><dd>...</dd>
        <dt>Owning root or surface</dt><dd>e.g., Home tab → Stack</dd>
        <dt>Presentation</dt><dd>push, sheet, full-screen cover, etc.</dd>
        <dt>Primary action</dt><dd>...</dd>
        <dt>Completion</dt><dd>...</dd>
        <dt>Cancellation / back</dt><dd>...</dd>
        <dt>Failure / recovery</dt><dd>...</dd>
        <dt>Accessibility notes</dt><dd>Dynamic Type, VoiceOver headings, custom actions, gesture alternatives.</dd>
        <dt>Screenshots needed for review</dt><dd>default, large Dynamic Type, dark mode, error, empty, destructive confirmation, loading, success.</dd>
      </dl>

      <ol class="flow-steps">
        <li>
          <h3>Step 1 — <screen name></h3>
          <p>User action and system response in plain prose.</p>

          <figure class="preview">
            <div class="device-frame" aria-hidden="true">
              <div class="ios-screen">
                <div class="status-bar"><!-- time, signal, battery as CSS shapes --></div>
                <div class="nav-bar">
                  <button class="nav-back" type="button">Back</button>
                  <h4 class="nav-title">Screen Title</h4>
                  <button class="nav-trailing" type="button">Action</button>
                </div>
                <div class="screen-content">
                  <!-- List rows, form fields, hero, etc. using the classes below -->
                </div>
                <div class="tab-bar"><!-- if this surface lives under a TabView --></div>
              </div>
            </div>
            <figcaption>Step 1 — default state</figcaption>
          </figure>

          <details class="swiftui-mapping">
            <summary>SwiftUI mapping</summary>
            <ul>
              <li><strong>Container:</strong> e.g., <code>NavigationStack</code> with a <code>List</code> root.</li>
              <li><strong>Nav bar:</strong> <code>.navigationTitle("Screen Title")</code>, <code>.toolbar { ToolbarItem(placement: .topBarTrailing) { Button("Action") {} } }</code>.</li>
              <li><strong>Rows:</strong> <code>ForEach(items) { item in NavigationLink(value: item) { RowView(item) } }</code>.</li>
              <li><strong>Primary action:</strong> Button style and placement (e.g., <code>.borderedProminent</code> at the bottom, or trailing toolbar item).</li>
              <li><strong>Destructive action:</strong> <code>.foregroundStyle(.red)</code> or <code>role: .destructive</code> with <code>.confirmationDialog</code>.</li>
              <li><strong>Presentation:</strong> push vs. <code>.sheet</code> vs. <code>.fullScreenCover</code> vs. <code>.alert</code>.</li>
              <li><strong>State:</strong> which <code>@State</code>, <code>@Bindable</code>, or model-owned property drives this step.</li>
              <li><strong>Accessibility:</strong> <code>.accessibilityLabel</code>, <code>.accessibilityHint</code>, <code>.accessibilityAddTraits(.isHeader)</code>, Dynamic Type strategy, custom actions.</li>
              <li><strong>Edge states:</strong> how the empty, loading, error, and offline states are produced (e.g., <code>ContentUnavailableView</code>, <code>ProgressView</code>, inline error row).</li>
            </ul>
          </details>
        </li>
        <!-- Repeat <li> per meaningful step / state. -->
      </ol>
    </section>
    <!-- Repeat <section class="flow"> per primary flow. -->
  </main>
</body>
</html>
```

### iOS Preview Styles

Include a single `<style>` block. The goal is an iOS-like silhouette, not a real device shell. Keep it lightweight. Adjust visuals as needed but keep the class names so previews stay consistent across flows:

- `body` uses a neutral background and the system font stack above.
- `.device-frame` is a phone-shaped container: about 390×844 logical units, rounded corners around 44px, 1px outer border, soft shadow. It exists only to bound the screen — do not draw a notch, dynamic island, or speaker.
- `.ios-screen` fills the frame, has a white (or `#000` in dark variants) background, and uses flex/column layout so `.status-bar`, `.nav-bar`, `.screen-content`, and optional `.tab-bar` stack from top to bottom.
- `.status-bar` is a thin top row with time on the left and signal/battery shapes on the right. Keep it minimal; it is a recognition cue, not real chrome.
- `.nav-bar` is a row with a back-style leading button, a centered or large title, and an optional trailing button. Use the large-title style by default (title appears below the row) and switch to the inline style when the spec dictates.
- `.screen-content` uses standard iOS spacing (16px horizontal padding, 12–16px vertical rhythm). Lists use grouped or inset styles via classes `.list-grouped` and `.list-inset`. Form sections use `.form-section` with subtle headers.
- `.tab-bar` is a bottom row with 3–5 evenly-spaced items, each a small icon (CSS shape or inline SVG) over a label. Mark the selected item with `.tab-selected`.
- Buttons: `.btn-primary` (filled, accent background, white text, 12–14px radius), `.btn-secondary` (tinted text only), `.btn-destructive` (red text), and `.btn-bordered` (1px border with tint text). Use `<button type="button">` and do not wire handlers. Disabled buttons use reduced opacity.
- Form inputs: `.text-field` (1px hairline border, rounded corners, 44pt minimum hit target). Switches use a small pill shape (`.switch` + `.switch-on`/`.switch-off`). Steppers and segmented controls use class hooks even if static.
- Sheets, alerts, and full-screen covers render as nested `.ios-screen` variants: `.sheet` (rounded top corners, partial height, dimmed backdrop), `.alert` (centered card over backdrop), `.full-screen-cover` (full screen with leading dismiss).
- Dark mode previews use a `.dark` modifier on `.ios-screen` and flip backgrounds and label colors accordingly.
- Dynamic Type previews use a `.dt-xl` modifier that bumps font sizes and lets rows reflow so the user can see what large text looks like.

### Per-Step Preview Rules

- One `.device-frame` per state. Default, loading, empty, error, success, dark mode, and Dynamic Type variants each get their own frame with a `<figcaption>` describing the state.
- Use real copy. If the spec says the title is "Add Note", the preview must say "Add Note", not "Title".
- Mark destructive actions with `.btn-destructive` so reviewers can spot them at a glance.
- For sheet, alert, popover, full-screen cover, and split-view presentations, render the parent surface dimmed in the background and the modal in the foreground so the relationship is obvious.
- Every preview that the spec calls out as needing a screenshot for later review must exist in the HTML before drafting is considered done.

### SwiftUI Mapping Block Rules

Every `.preview` figure is followed by exactly one `<details class="swiftui-mapping"><summary>SwiftUI mapping</summary>…</details>` block. The mapping block:

- Lists the container, navigation, primary controls, presentation modifier, state ownership, accessibility, and edge-state strategy as concrete SwiftUI references.
- Names APIs (e.g., `NavigationStack`, `List`, `ContentUnavailableView`, `.confirmationDialog`, `.sheet(item:)`, `.toolbar`, `.searchable`, `.accessibilityLabel`, `Observation`, `@Bindable`).
- Does not write full SwiftUI source; it sketches the structure so the implementing skill (`evenbetter-swiftui-ui-patterns`, `evenbetter-swiftui-view-refactor`, `evenbetter-swiftui-accessibility`) can produce code.
- Calls out HIG-sensitive choices (e.g., "use `.borderedProminent` rather than a custom filled `Capsule` to keep system tinting") with a short rationale.
- Stays consistent with the `ios-hig-tech-plan.md` once it exists; if the mapping contradicts the tech plan, prefer the tech plan and update the mapping.

## Flow Design Rules

- Keep the prose product-level. Do not include code or file paths outside the SwiftUI mapping blocks.
- Use native iOS presentation language: tab, stack, sheet, alert, toolbar, split view, or modal only when the choice matters.
- Make primary and destructive actions explicit.
- Record how VoiceOver users understand screen changes and completion.
- Record where Dynamic Type can force layout changes across screens.
- Record how back, dismiss, cancel, and resume behave when data may be lost.
- Record how external entry points, permissions, auth state, and offline state affect the journey.

## Next Step

Route through validation before ticketing. Recommend `3-ux-prd-validation` when flows are complex or high-risk; otherwise proceed to `4-ios-hig-tech-plan`. After the technical plan, run `5-architecture-validation` before `6-ticket-breakdown`. Do not recommend ticket breakdown directly from screen flows.
