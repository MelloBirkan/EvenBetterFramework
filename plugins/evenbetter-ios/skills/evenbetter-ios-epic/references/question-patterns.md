# Question Patterns

Ask only questions that materially change the app/epic UX, accessibility strategy, navigation architecture, review scope, or implementation path. Every question must be multiple-choice when the environment supports options.

## Format

- Ask 1-3 questions per round.
- Before ticket breakdown, aim for roughly 3-10 questions per phase on average across `0-trigger-workflow`, `1-ios-ux-brief`, `2-screen-flows`, `3-ux-prd-validation`, `4-ios-hig-tech-plan`, and `5-architecture-validation`.
- Do not treat 10 as a total cap. The cumulative pre-ticket interview can exceed 10 questions when needed to close gaps and uncommunicated assumptions.
- Use 2-3 mutually exclusive choices per question.
- Put the recommended option first and label it as recommended when the tool supports labels.
- Avoid "anything else?" or broad discovery questions.
- If the user chooses "Other", convert their answer into a concrete assumption and continue with another closed question only if needed.
- Use initial questions in each phase to close gaps and assumptions. Use later questions to cover edge cases, accessibility risks, failure states, destructive actions, cross-screen consistency, review evidence, and any assumptions the user has not explicitly confirmed.

## 0 Trigger Workflow

Use these patterns for multi-screen epics or app-from-scratch intake:

- Product shape:
  - Recommended: Plan a new iOS app from scratch
  - Add a multi-screen feature to an existing app
  - Redesign or audit an existing iOS flow
- Epic scale:
  - Recommended: Full app or full product area with multiple flows
  - One complex flow across several screens
  - UX review of a built or partially built experience
- Primary user journey:
  - Recommended: Create, submit, or complete a task
  - Browse, filter, compare, and inspect content
  - Configure, manage, or administer data
- Initial screen inventory:
  - Recommended: Define root, list/detail, task, settings, and completion screens now
  - Define only the first release screens now
  - Start from existing screens and identify gaps
- Platform scope:
  - Recommended: iPhone-first with explicit iPad adaptation notes
  - Universal iPhone/iPad from the start
  - iOS now, iPadOS later

## 1 iOS UX Brief

Use these patterns before drafting `ios-ux-brief.md`:

- Audience priority:
  - Recommended: Primary user group first, secondary users explicitly deferred
  - Multiple user groups supported in the first release
  - Internal/admin users drive the first release
- Context of use:
  - Recommended: Short mobile sessions with interruption recovery
  - Focused long-form work where progress must persist
  - Occasional utility use from notifications, widgets, or shortcuts
- Scope boundary:
  - Recommended: Core launch scope plus named out-of-scope follow-ups
  - Broad app plan with release phases
  - Review-only scope for existing behavior
- Success criteria:
  - Recommended: Task completion, understandable feedback, and recoverable errors
  - Engagement or browsing success
  - Operational/admin accuracy success
- Accessibility baseline:
  - Recommended: Dynamic Type through accessibility sizes plus VoiceOver labels and headings
  - High-accessibility baseline with Switch Control, Voice Control, keyboard, motion, and contrast review
  - Minimal baseline only for a prototype, with follow-up accessibility tickets required
- Visual evidence:
  - Recommended: Record screenshots needed for review, not for brief drafting
  - Ask for screenshots before drafting because existing UI drives scope
  - No screenshots needed because this is a greenfield plan

## 2 Screen Flows

Use these patterns before writing `screen-flows.md`. Ask at least one inventory round, one per-flow round for each primary flow, and one cross-flow round for edge cases and accessibility when the epic has more than one screen.

### Flow Inventory

- Flow set:
  - Recommended: One primary happy path plus supporting browse/manage flows
  - Several equally important top-level flows
  - One linear onboarding or setup flow
- Top-level navigation:
  - Recommended: Tab-based root with independent stacks for durable areas
  - Single `NavigationStack` with pushed destinations
  - Split view or sidebar-based adaptive layout
- Entry strategy:
  - Recommended: Start from an in-app root screen
  - Start from a notification, deep link, widget, shortcut, or App Intent
  - Start from onboarding, auth, or permission gating
- Flow ownership:
  - Recommended: Each flow has one owning root screen and one completion state
  - Flow spans multiple top-level areas
  - Flow starts externally and returns into the app

### Per-Flow Decisions

- Entry state:
  - Recommended: User enters with existing data loaded
  - User starts from an empty or first-use state
  - User enters after auth, permission, or setup is required
- Screen sequence:
  - Recommended: Root/list screen, detail or task screen, confirmation/completion state
  - Linear step-by-step screens
  - Dashboard or overview with optional drill-downs
- Presentation style:
  - Recommended: Push durable destinations in a navigation stack
  - Sheet for focused creation, editing, or filtering
  - Full-screen cover only for blocking or immersive flows
- Primary action placement:
  - Recommended: Toolbar or prominent in-content button depending on screen hierarchy
  - Bottom safe-area action for a repeated task
  - Inline row action for item-scoped work
- Branching:
  - Recommended: Keep one happy path and document explicit alternate branches
  - Split by user role or account state
  - Split by data availability, permissions, or offline state
- Completion:
  - Recommended: Return to the most useful source screen with visible success feedback
  - Stay on a completion or receipt screen
  - Continue into the next suggested action
- Cancellation/back behavior:
  - Recommended: Standard back or dismiss with confirmation only when data could be lost
  - Always confirm cancellation
  - Block dismissal until the user saves, discards, or resolves an error
- Failure and recovery:
  - Recommended: Inline error with retry and preserved user input
  - Error screen with clear recovery action
  - Centralized app-level error surface plus local recovery
- Loading and empty states:
  - Recommended: Local loading, empty, and error states per screen
  - Shared reusable state components
  - Skeleton or placeholder states for content-heavy screens
- Destructive actions:
  - Recommended: Confirmation alert or sheet with clear consequence text
  - Undoable destructive action
  - Separate review flow before deletion or irreversible submission

### Cross-Flow Decisions

- State restoration:
  - Recommended: Preserve per-tab navigation history and unfinished safe drafts
  - Reset the flow after completion
  - Return to the entry screen after completion
- Authentication and permissions:
  - Recommended: Gate only the screens/actions that need access
  - Gate the whole app before core navigation
  - Provide read-only or preview mode before sign-in/permission
- Offline or degraded mode:
  - Recommended: Read existing content and queue safe actions where feasible
  - Show explicit unavailable states with retry
  - Require online access for this release
- iPad/adaptive behavior:
  - Recommended: Document iPad layout behavior even if implementation is later
  - Design universal split/sidebar behavior now
  - Defer iPad and record it as out of scope
- Dynamic Type:
  - Recommended: Reflow dense screens vertically at accessibility sizes
  - Move secondary content to detail screens
  - Allow truncation only for nonessential metadata
- VoiceOver:
  - Recommended: Standard labels plus headings, grouping, and success announcements
  - Custom accessibility values and hints for complex controls
  - Custom actions for repeated row or card operations
- System surfaces:
  - Recommended: No external system actions until core app flow is stable
  - App Intents for key user-valued actions
  - Widgets, Shortcuts, Spotlight, or controls as first-class entry points
- Review evidence:
  - Recommended: Capture default, completion, error/empty, and large Dynamic Type states
  - Capture every top-level flow and modal
  - Code-only review is enough for this phase

## Cross-Screen Tradeoffs

Use this shorter bank when validating or revising an existing flow artifact:

- Modal policy:
  - Recommended: Sheets for focused tasks
  - Push navigation for durable destinations
  - Full-screen cover only for immersive or blocking flows
- Empty/error strategy:
  - Recommended: Per-screen local states
  - Shared reusable state components
  - Centralized error surface with local recovery
- Cross-screen feedback:
  - Recommended: Inline success/error near the action source
  - Dedicated completion screen
  - App-wide banner only for cross-flow status

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
  - Recommended: Fix before merge
  - Track as follow-up epic ticket
  - Accept as intentional deviation
- Scope:
  - Recommended: Apply to the whole flow
  - Apply to one screen
  - Apply as app-wide design-system rule
- Evidence:
  - Recommended: Wait for requested screenshots when visual behavior is central
  - Proceed with code-only review
  - Run simulator review if available
