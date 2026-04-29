# Review Checklist

Use this checklist for `5-ux-implementation-review` and whenever a user asks for an iOS UX, HIG, accessibility, or screenshot review. Default to plan + visual + code review.

## Evidence

- Read `.evenbetter/<feature-name>/ios-ux-plan.md` and relevant `UX-TICKET-NNN.md` files.
- Inspect changed SwiftUI/iOS code with `git diff`, paths from tickets, or user-provided files.
- Review screenshots when available. If missing, request only the states needed to resolve visual uncertainty.
- Consult `official-sources.md` for current Apple links and relevant local iOS skills.

## Severity

- Blocker: core task is inaccessible, impossible, data-loss-prone, or violates a planned requirement.
- High: likely HIG/accessibility regression affecting many users or assistive technology users.
- Medium: meaningful UX gap with a clear fix, but the core flow still works.
- Low: polish, consistency, or documentation issue.
- Validated: explicitly confirm important planned behavior that works.

## Visual and Interaction Review

- Information hierarchy: primary content appears first in reading order and remains clear at large text sizes.
- Navigation: screen title, back/close affordance, tab/sheet/push behavior, and destination after completion are clear.
- Actions: primary, secondary, cancel, and destructive roles are visually distinct and placed consistently.
- Touch targets: interactive controls have at least a 44x44 pt hit region on iOS unless a standard component guarantees it.
- Feedback: loading, disabled, success, error, and empty states are visible and do not rely on color alone.
- Gestures: important actions have a visible non-gesture alternative.
- Layout: safe areas, Dynamic Island, keyboard, orientation, and iPad size changes do not obscure controls.
- Color: semantic/system colors are preferred; custom colors handle light, dark, and increased contrast contexts.
- Typography: system text styles or scalable custom fonts support Dynamic Type and minimize truncation.

## Accessibility Review

- VoiceOver labels describe custom controls, images, and non-text content accurately.
- Values, hints, traits, and custom actions are present only when they add useful context.
- Decorative images are hidden from accessibility.
- Grouping and reading order match visible relationships.
- Text fields expose labels, validation state, keyboard type, submit behavior, and focus order.
- Dynamic Type at accessibility sizes avoids overlap, clipped text, and lost primary actions.
- Switch Control, Voice Control, keyboard, and pointer interaction are not blocked by custom gestures.
- Motion-heavy transitions respect Reduce Motion or have a calmer fallback.

## Code Review

- Prefer native SwiftUI controls before custom controls.
- Avoid giant views, inline side effects, and unstable root branch swapping; use `swiftui-view-refactor` if needed.
- Use `swiftui-ui-patterns` for NavigationStack, sheets, forms, controls, theming, and async state.
- Add accessibility modifiers at the smallest useful view boundary.
- Avoid hard-coded colors, font sizes, and layout constants that break Dynamic Type or contrast.
- Gate iOS 26+ Liquid Glass with availability and use `swiftui-liquid-glass` for review.

## Output

Write `.evenbetter/<feature-name>/ios-ux-review.md` when the stage is a formal review. Lead with findings ordered by severity, include file/screenshot/spec references, cite Apple sources for HIG claims, and finish with validated behavior plus any screenshot or test gaps.
