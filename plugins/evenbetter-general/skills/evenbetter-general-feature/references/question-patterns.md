# Question Patterns

Ask only questions that materially change the feature's scope, user goal, behavior, data shape, integration boundaries, failure handling, or validation decisions. Prefer multiple-choice questions whenever the answer space can be enumerated. Fall back to open-text only when the answer is a name, a citation, an existing schema, or another value that cannot reasonably be listed.

## Format

- Ask 1-4 questions per round (Claude `AskUserQuestion`) or 1-3 per round (Codex `request_user_input`).
- Before ticket breakdown, aim for roughly 3-10 questions per phase on average across `0-trigger-workflow`, `1-plan`, and `2-plan-validation`.
- Do not treat 10 as a total cap. The cumulative pre-ticket interview can and should exceed 10 questions when complexity warrants it (15-30 is normal for mixed product/technical work, novel integrations, or unfamiliar domains).
- Use 2-3 mutually exclusive choices per question when option sets are well-bounded; up to 4 in Claude when the space is wider.
- Put the recommended option first and label it as recommended when the tool supports labels.
- Avoid "anything else?" or broad discovery questions. Convert open uncertainty into specific closed questions.
- If the user chooses "Other", convert their answer into a concrete assumption and continue with another closed question only if any uncertainty remains.
- Use initial questions in each phase to close gaps and assumptions. Use later questions to cover edge cases, failure states, integration risks, data conflicts, destructive actions, and decisions the user has not explicitly confirmed.

## 0 Trigger Workflow

Use these patterns for feature intake. Ask roughly 3-10 questions across one or more rounds.

### Round 1: Work shape and goal

- Work nature:
  - Recommended: Product-facing feature with new or changed user behavior
  - Pure technical work (refactor, performance, infrastructure, bug fix)
  - Mixed: technical changes with user-visible consequences
- Primary user goal (product-facing) or improvement target (technical):
  - Recommended: Complete a focused user task
  - Browse, search, or compare information
  - Configure a preference or setting
  - Reduce latency, cost, error rate, or technical debt
- Entry point:
  - Recommended: Add to an existing primary surface
  - Add a new surface that lives alongside existing flows
  - Triggered by an external event (link, notification, schedule, webhook)
- Audience:
  - Recommended: End users
  - Internal operators, admins, or support staff
  - Developers consuming an API or SDK
  - System or infrastructure only (no direct human user)

### Round 2: Scope and constraints

- Scope boundary:
  - Recommended: Core happy path plus named out-of-scope follow-ups
  - One narrowly defined behavior; defer everything else explicitly
  - Whole-feature scope across both happy path and edge cases
  - Review-only scope for existing behavior
- Constraint posture:
  - Recommended: Technical and product constraints discovered during planning
  - Hard regulatory, security, or compliance constraints stated upfront
  - Hard performance, scale, or SLA constraints stated upfront
  - Hard deadline or budget constraints stated upfront
- Existing-behavior posture:
  - Recommended: Net-new behavior with no impact on existing flows
  - Extends existing behavior; backward compatibility required
  - Replaces existing behavior; explicit migration required

### Round 3: Edge-case pass

Ask this round whenever the feature involves data writes, account state, permissions, sync, deletion, payments, integrations, or background processing.

- Failure handling posture:
  - Recommended: Inline retry with preserved user input
  - Centralized error surface with local recovery
  - Hard fail with explicit escalation path
- Auth/permissions posture:
  - Recommended: Gate only the actions that need access
  - Gate the whole feature behind a single auth/permission check
  - Provide read-only or preview mode before sign-in/permission
- Offline/degraded posture:
  - Recommended: Read existing data and queue safe actions where feasible
  - Show explicit unavailable states with retry
  - Require online access for this release
- Destructive/irreversible actions:
  - Recommended: Confirmation step with clear consequence text
  - Undoable action with a recovery window
  - Separate review flow before the action runs

## 1 Plan

Use these patterns before drafting `plan.md`. Apply the rounds relevant to the work's nature (product-facing, technical, or mixed).

### Problem & Context

- Problem framing:
  - Recommended: Solve one specific user or system pain point
  - Address a cluster of related pains together
  - Investigate root cause before committing to a solution
- Success criteria:
  - Recommended: Observable user-visible behavior matches the agreed flow
  - Specific metric improvement (latency, error rate, cost, conversion)
  - Internal code health, maintainability, or test coverage improvement
- Acceptance evidence:
  - Recommended: Manual verification of the agreed flow
  - Automated tests cover the critical path
  - Stakeholder demo or sign-off

### User Experience (product-facing or mixed)

- Flow set:
  - Recommended: One primary happy path with documented edge states
  - Multiple alternate flows depending on user state
  - One linear setup/onboarding flow
- Entry state:
  - Recommended: User enters with existing data loaded
  - User starts from an empty or first-use state
  - User enters after auth, permission, or setup is required
- Primary action placement:
  - Recommended: Prominent action visible from the main surface
  - Inline action on each item or row
  - Triggered by an external event rather than direct input
- Feedback model:
  - Recommended: Inline feedback near the action source
  - Dedicated completion view or confirmation
  - System-wide toast, banner, or notification
- Completion:
  - Recommended: Return to the most useful source state with success feedback
  - Stay on a completion or receipt view
  - Continue into the next suggested action
- Cancellation/back behavior:
  - Recommended: Standard cancel/back with confirmation only when data could be lost
  - Always confirm cancellation
  - Block dismissal until the user saves, discards, or resolves an error
- Failure and recovery:
  - Recommended: Inline error with retry and preserved user input
  - Error surface with clear recovery action
  - Centralized error/notification with local recovery options
- Empty and loading states:
  - Recommended: Local empty and loading states per surface
  - Shared reusable empty/loading components
  - Skeleton or placeholder states for content-heavy surfaces
- Destructive actions:
  - Recommended: Confirmation step with clear consequence text
  - Undoable action with recovery window
  - Separate review flow before the action runs

### Technical Approach

- Architectural style:
  - Recommended: Extend the dominant pattern already in the codebase
  - Introduce a new pattern with explicit boundaries
  - Refactor the existing pattern before adding new work
- Service boundary:
  - Recommended: Keep the work inside the current service or module
  - Split into a new service or module with a defined contract
  - Move existing functionality across services as part of this feature
- Sync vs async:
  - Recommended: Synchronous request/response for user-driven flows
  - Asynchronous job, queue, or event-driven processing
  - Mixed: sync acknowledgement plus async fulfillment
- Data model change:
  - Recommended: Additive changes with backfill for existing rows
  - New fields with default values and no backfill
  - Versioned schema with explicit migration plan
  - No data model change required
- Identity and ownership:
  - Recommended: Tie new records to an existing primary owner
  - Introduce a new ownership concept with explicit relationship
  - Reuse existing identifiers without introducing new ones
- Integration boundary:
  - Recommended: Use existing internal interfaces only
  - Add one new external integration with a defined contract
  - Add multiple external integrations and document the orchestration
- Failure handling:
  - Recommended: Retry with bounded backoff and surface terminal failures
  - Compensating action or rollback on terminal failures
  - Operator-driven recovery with alerts and runbooks
- Idempotency posture:
  - Recommended: Idempotent operations via request keys or natural keys
  - At-most-once execution with deduplication windows
  - At-least-once execution with downstream tolerance
- Observability:
  - Recommended: Structured logs plus metrics on the critical path
  - Add tracing across the new boundary
  - Defer observability to a follow-up

## 2 Plan Validation

Use these option banks when validation surfaces unresolved findings.

- Risk classification (per finding):
  - Recommended: Most-important (will force major rework if unaddressed)
  - Significant (must address before proceeding)
  - Moderate (clarify and decide now)
  - Minor (note for awareness only)
- Fix routing:
  - Recommended: Update the Plan now and re-validate
  - Return to `0-trigger-workflow` if the gap is at requirements level
  - Accept as intentional and record the trade-off
- Simplicity vs flexibility:
  - Recommended: Simpler approach now, with a documented extension path
  - More flexible approach now, justified by a near-term requirement
  - Keep both options open until implementation reveals which is needed
- Codebase fit:
  - Recommended: Follow the dominant pattern in the codebase
  - Introduce a new pattern with explicit boundaries and rationale
  - Refactor the existing pattern before extending it
- Cross-dimensional consistency (mixed work):
  - Recommended: Technical approach fully supports the documented user experience
  - Adjust the user experience to match what the architecture can deliver
  - Adjust the architecture to deliver the intended user experience

## Review Disposition

When implementation review or cross-artifact validation surfaces findings, ask closed disposition questions:

- Fix timing:
  - Recommended: Fix before merge
  - Track as follow-up ticket
  - Accept as intentional deviation
- Scope:
  - Recommended: Apply to this feature only
  - Apply as a shared module-level rule
  - Apply as a codebase-wide standard
- Evidence:
  - Recommended: Re-run code review against the updated plan
  - Add or update automated tests for the finding
  - Manual demo or stakeholder confirmation
