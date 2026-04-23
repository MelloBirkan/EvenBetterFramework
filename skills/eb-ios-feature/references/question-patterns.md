# Question Patterns

Ask only questions that materially change the UX/accessibility plan, review scope, or implementation path. Every question must be multiple-choice when the environment supports options.

## Format

- Ask 1-3 questions per round.
- Use 2-3 mutually exclusive choices per question.
- Put the recommended option first and label it as recommended when the tool supports labels.
- Avoid "anything else?" or broad discovery questions.
- If the user chooses "Other", convert their answer into a concrete assumption and continue with another closed question only if needed.

## Feature Intake

Use these patterns to clarify a small feature or single screen:

- Primary user goal:
  - Complete one focused task
  - Browse or compare information
  - Configure a preference
- Screen type:
  - Native form or settings screen
  - List/detail or content screen
  - Modal task flow
- Navigation entry:
  - Existing tab or screen
  - Sheet from a current action
  - New pushed destination
- Accessibility baseline:
  - Standard Dynamic Type through accessibility sizes
  - Large and extra-large Dynamic Type only
  - Fixed text size only when product constraints require it
- VoiceOver behavior:
  - Standard control labels are enough
  - Custom labels, values, or hints are required
  - Custom actions or grouping are required

## HIG Tradeoffs

Use these patterns when a HIG-sensitive choice appears:

- Primary action placement:
  - Trailing toolbar or prominent button
  - Inline row action
  - Bottom safe-area action
- Destructive action handling:
  - Confirmation alert
  - Undoable action
  - Separate destructive flow
- Gesture policy:
  - Standard gesture plus visible control
  - Visible control only
  - Custom gesture plus visible alternative
- Feedback state:
  - Inline loading and disabled action
  - Progress view in content
  - Toast/banner for transient confirmation
- Text scaling:
  - Reflow to vertical layout at accessibility sizes
  - Preserve compact layout with truncation fallback
  - Move secondary content to detail view

## Screenshot Requests

Ask for screenshots only when visual evidence changes review quality. Be specific so the user can identify the screen.

- Default state screenshot: "Send the screen as it appears after opening it normally."
- Large Dynamic Type screenshot: "Send the same screen with Larger Text enabled near the largest accessibility size."
- Dark mode screenshot: "Send the same screen in Dark Mode."
- Error state screenshot: "Send the screen after the main operation fails."
- Empty state screenshot: "Send the screen when there is no content or no search result."
- Destructive confirmation screenshot: "Send the alert or confirmation shown before the destructive action."
- Post-action screenshot: "Send the screen immediately after the action succeeds."

## Review Disposition

When findings need a decision, ask closed choices:

- Fix timing:
  - Fix before merge
  - Track as follow-up ticket
  - Accept as intentional deviation
- Scope:
  - Apply only to this screen
  - Apply to shared component
  - Apply as design-system rule
- Evidence:
  - Proceed with code-only review
  - Wait for requested screenshots
  - Run simulator review if available
