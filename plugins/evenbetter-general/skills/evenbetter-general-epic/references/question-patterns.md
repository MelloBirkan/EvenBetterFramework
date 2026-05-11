# Question Patterns

Ask only questions that materially change the epic's scope, audience, user journeys, technical approach, data model, integration boundaries, failure handling, or validation decisions. Prefer multiple-choice questions whenever the answer space can be enumerated. Fall back to open-text only when the answer is a name, a citation, an existing schema, or another value that cannot reasonably be listed.

## Format

- Ask 1-4 questions per round (Claude `AskUserQuestion`) or 1-3 per round (Codex `request_user_input`).
- Before ticket breakdown, aim for roughly 3-10 questions per phase on average across `0-trigger-workflow`, `1-epic-brief`, `2-core-flows`, `3-prd-validation`, `4-tech-plan`, and `5-architecture-validation`.
- Do not treat 10 as a total cap. The cumulative pre-ticket interview can and should exceed 10 questions when complexity warrants it (20-40 is normal for new-product or multi-area epics).
- Use 2-3 mutually exclusive choices per question when option sets are well-bounded; up to 4 in Claude when the space is wider.
- Put the recommended option first and label it as recommended when the tool supports labels.
- Avoid "anything else?" or broad discovery questions. Convert open uncertainty into specific closed questions.
- If the user chooses "Other", convert their answer into a concrete assumption and continue with another closed question only if any uncertainty remains.
- Use initial questions in each phase to close gaps and assumptions. Use later questions to cover edge cases, failure states, integration risks, data conflicts, destructive actions, scaling concerns, and cross-spec consistency.

## 0 Trigger Workflow

Use these patterns for initial epic intake. Ask roughly 3-10 questions across one or more rounds.

### Round 1: Problem shape and audience

- Product shape:
  - Recommended: Add a new capability to an existing product
  - Build a new product or product area from scratch
  - Redesign or refactor existing behavior
  - Investigate or audit existing behavior before changing it
- Epic scale:
  - Recommended: One coherent capability that spans multiple flows
  - Multiple related capabilities released together
  - A single complex flow with deep edge cases
  - A foundational refactor that unblocks future capabilities
- Primary user audience:
  - Recommended: End users of the product
  - Internal operators, admins, or support staff
  - Developers consuming an API or SDK
  - Mixed audience with one priority tier
- Primary user goal:
  - Recommended: Complete or submit a task
  - Browse, search, compare, or inspect information
  - Configure, manage, or administer data
  - Monitor, observe, or be alerted about state

### Round 2: Initial scope and success

- Initial scope inventory:
  - Recommended: Core happy-path scope plus named out-of-scope follow-ups
  - First release scope only; defer everything else explicitly
  - Whole-epic scope across multiple releases
  - Start from existing behavior and identify gaps
- Success measure:
  - Recommended: Task completion with understandable feedback and recoverable errors
  - Engagement, retention, or browsing success
  - Operational accuracy or throughput success
  - System reliability, performance, or cost success
- Constraint posture:
  - Recommended: Technical and product constraints discovered during planning
  - Hard regulatory, security, or compliance constraints stated upfront
  - Hard performance, scale, or SLA constraints stated upfront
  - Hard deadline or budget constraints stated upfront

### Round 3: Edge-case pass

Ask this round whenever the epic involves data creation, submission, account state, permissions, sync, deletion, payments, integrations, or background processing.

- Failure handling posture:
  - Recommended: Inline retry with preserved user input
  - Centralized error surface with local recovery
  - Hard fail with explicit escalation path
- Auth/permissions posture:
  - Recommended: Gate only the actions or screens that need access
  - Gate the entire epic behind a single auth/permission check
  - Provide read-only or preview mode before sign-in/permission
- Offline/degraded posture:
  - Recommended: Read existing data and queue safe actions where feasible
  - Show explicit unavailable states with retry
  - Require online access for this release
- Destructive/irreversible actions:
  - Recommended: Confirmation step with clear consequence text
  - Undoable action with a recovery window
  - Separate review flow before the action runs

## 1 Epic Brief

Use these patterns before drafting `epic-brief.md`. Ask at least one round on audience/scope and one risk round for new-product or multi-area epics.

### Round 1: Audience and context

- Audience priority:
  - Recommended: Primary user group first, secondary users explicitly deferred
  - Multiple user groups supported in the first release
  - Internal/admin users drive the first release
- Context of use:
  - Recommended: Short interactive sessions with interruption recovery
  - Focused long-running work where progress must persist
  - Occasional utility entry from notifications, links, or triggers
  - Background or scheduled execution with periodic human review
- Adjacent product context:
  - Recommended: Integrate with existing core flows and patterns
  - Sit alongside existing flows as a new independent surface
  - Replace or deprecate an existing behavior

### Round 2: Scope and boundary

- Scope boundary:
  - Recommended: Core launch scope plus named out-of-scope follow-ups
  - Broad epic plan with explicit release phases
  - Review-only scope for existing behavior
- Dependency posture:
  - Recommended: All required systems/services already exist and are stable
  - One or more required systems must be built or modified inside this epic
  - One or more required systems are external and need explicit contracts
- Cross-team boundary:
  - Recommended: All work owned inside this team or codebase
  - Coordination required with one other team or service owner
  - Coordination required across multiple teams or vendors

### Round 3: Success and evidence

- Success criteria:
  - Recommended: Task completion, understandable feedback, and recoverable errors
  - Engagement or browsing success
  - Operational, throughput, or accuracy success
  - Reliability, performance, or cost success
- Non-functional priorities:
  - Recommended: Correctness and clarity first; performance second
  - Performance and scaling first; feature breadth second
  - Security, privacy, or compliance first; everything else within those constraints
- Evidence plan:
  - Recommended: Code-level evidence plus targeted manual verification
  - Automated test coverage as the primary acceptance signal
  - Manual review or stakeholder demo as the primary acceptance signal
- Risk-state coverage (ask when the epic has data writes, payments, account changes, permissions, sync, deletion, or external integrations):
  - Recommended: Cover failure, retry, conflict, and permission states explicitly
  - Cover only the most likely failure modes; defer rare ones
  - Defer all error-state design to implementation

## 2 Core Flows

Use these patterns before writing `core-flows.md`. Ask at least one inventory round, one per-flow round for each primary flow, and one cross-flow round for edge cases.

### Flow Inventory

- Flow set:
  - Recommended: One primary happy path plus supporting browse/manage flows
  - Several equally important top-level flows
  - One linear onboarding or setup flow
  - A background or scheduled flow with optional human steps
- Entry strategy:
  - Recommended: Start from an in-product root or main entry
  - Start from an external trigger (link, notification, event, webhook)
  - Start from onboarding, auth, or permission gating
- Flow ownership:
  - Recommended: Each flow has one owning entry surface and one completion state
  - Flow spans multiple top-level areas
  - Flow starts externally and returns into the product
- Integration boundary:
  - Recommended: Stay inside one system or codebase per flow
  - Cross one well-defined integration per flow
  - Cross multiple integrations or third-party services per flow

### Per-Flow Decisions

Repeat for each primary flow. Do not write the flow until every item is decided or intentionally deferred.

- Entry state:
  - Recommended: User enters with existing data loaded
  - User starts from an empty or first-use state
  - User enters after auth, permission, or setup is required
  - System triggers the flow on the user's behalf
- Step sequence:
  - Recommended: Root or list view, focused task, confirmation/completion
  - Linear step-by-step sequence
  - Dashboard or overview with optional drill-downs
  - Single-screen task with inline outcomes
- Primary action placement:
  - Recommended: Prominent primary action visible from the main view
  - Inline action attached to each item or row
  - Action triggered by external event rather than user input
- Branching:
  - Recommended: Keep one happy path and document explicit alternate branches
  - Split by user role or account state
  - Split by data availability, permissions, or environment
- Completion:
  - Recommended: Return to the most useful source state with visible success feedback
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

### Cross-Flow Edge Cases

- State restoration:
  - Recommended: Preserve safe unfinished drafts across sessions
  - Reset state after completion
  - Return to the entry surface after completion
- Authentication and permissions:
  - Recommended: Gate only the actions/areas that need access
  - Gate the whole epic before any flow runs
  - Provide read-only or preview mode before sign-in/permission
- Offline or degraded mode:
  - Recommended: Read existing data and queue safe actions where feasible
  - Show explicit unavailable states with retry
  - Require online access for this release
- Data conflicts:
  - Recommended: Last-writer-wins with surfaced conflict notice
  - Server-side merge with user reconciliation when conflicts surface
  - Block conflicting writes until resolved
- Feedback model:
  - Recommended: Inline feedback near the action source
  - Dedicated completion view
  - System-wide banner, toast, or notification for cross-flow status

## 3 PRD Validation

Use these option banks when validation surfaces unresolved gaps.

- Gap disposition:
  - Recommended: Update Epic Brief or Core Flows now and re-validate
  - Defer to a later validation pass with an explicit owner
  - Accept as intentional and document the trade-off
- Severity weighting:
  - Recommended: Address most-important gaps first, then significant, then moderate
  - Address everything in source-spec order
  - Address only blockers; defer the rest
- Source spec routing:
  - Recommended: Audience/scope/success gaps return to `1-epic-brief`
  - Flow/step/edge-case gaps return to `2-core-flows`
  - Both apply and need a coordinated edit

## 4 Tech Plan

Use these patterns before drafting `tech-plan.md`. Ask roughly 3-10 questions across architecture, data, and integration rounds.

### Architectural Approach

- Architectural style:
  - Recommended: Extend the dominant pattern already in the codebase
  - Introduce a new pattern with explicit boundaries
  - Refactor the existing pattern before adding new work
- Service boundary:
  - Recommended: Keep the work inside the current service or module
  - Split into a new service or module with a defined contract
  - Move existing functionality across services as part of this epic
- Sync vs async:
  - Recommended: Synchronous request/response for user-driven flows
  - Asynchronous job, queue, or event-driven processing
  - Mixed: sync acknowledgement plus async fulfillment
- Concurrency posture:
  - Recommended: Single-writer per resource with optimistic checks
  - Multi-writer with explicit conflict resolution
  - Strict serialized writes with locking

### Data Model

- Storage shape:
  - Recommended: Extend the existing primary store
  - Add a new table/collection alongside the existing store
  - Introduce a new store type only if existing storage cannot satisfy the requirement
- Schema change strategy:
  - Recommended: Additive changes with backfill for existing rows
  - New fields with default values and no backfill
  - Versioned schema with explicit migration plan
- Identity and ownership:
  - Recommended: Tie new records to an existing primary owner (user, account, tenant)
  - Introduce a new ownership concept with explicit relationship
  - Reuse existing identifiers without introducing new ones
- Data lifecycle:
  - Recommended: Soft-delete with retention window
  - Hard-delete with explicit cascade rules
  - No deletion path in this release

### Integration and Failure

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

## 5 Architecture Validation

Use these patterns when validation surfaces unresolved tradeoffs.

- Risk classification (per finding):
  - Recommended: Most-important (will force major rework if unaddressed)
  - Significant (must address before proceeding)
  - Moderate (clarify and decide now)
  - Minor (note for awareness only)
- Fix routing:
  - Recommended: Update the Tech Plan now and re-validate
  - Return to `1-epic-brief` or `2-core-flows` if the gap is product-level
  - Accept as intentional and record the trade-off
- Simplicity vs flexibility:
  - Recommended: Simpler approach now, with a documented extension path
  - More flexible approach now, justified by a near-term requirement
  - Keep both options open until implementation reveals which is needed
- Codebase fit:
  - Recommended: Follow the dominant pattern in the codebase
  - Introduce a new pattern with explicit boundaries and rationale
  - Refactor the existing pattern before extending it

## Review Disposition

When implementation review or cross-artifact validation surfaces findings, ask closed disposition questions:

- Fix timing:
  - Recommended: Fix before merge
  - Track as follow-up ticket
  - Accept as intentional deviation
- Scope:
  - Recommended: Apply to this epic only
  - Apply as a shared module-level rule
  - Apply as a codebase-wide standard
- Evidence:
  - Recommended: Re-run code review against the updated artifact
  - Add or update automated tests for the finding
  - Manual demo or stakeholder confirmation
