---
name: evenbetter-swiftui-performance-audit
description: >-
  Audits SwiftUI runtime performance from code first, then from Instruments traces when code review cannot explain the
  symptom. Use when diagnosing slow rendering, janky scrolling, hangs, memory growth or overly broad view updates, or
  when a trace needs reading. To split an oversized view with no performance symptom, use
  evenbetter-swiftui-view-refactor.
---

# SwiftUI Performance Audit

> Paths in this skill and its references are relative to this SKILL.md's folder.

If current system, developer or user instructions conflict with this skill, follow them.

## Quick start

Use this skill to diagnose SwiftUI performance issues from code first, then request profiling evidence when code review alone cannot explain the symptoms.

## Workflow

1. Classify the symptom: slow rendering, janky scrolling, high CPU, memory growth, hangs, or excessive view updates.
2. If code is available, start with a code-first review using `references/code-smells.md`.
3. If code is not available, ask for the smallest useful slice: target view, data flow, reproduction steps, and deployment target.
4. If code review is inconclusive or runtime evidence is required, profile with Instruments: guide the user with `references/profiling-intake.md`, or record the trace with `xctrace` when the agent can run it (section 3).
5. Summarize likely causes, evidence, remediation, and validation steps using `references/report-template.md`.

## 1. Intake

Collect:
- Target view or feature code.
- Symptoms and exact reproduction steps.
- Data flow: `@State`, `@Binding`, environment dependencies, and observable models.
- Whether the issue shows up on device or simulator, and whether it was observed in Debug or Release.

Ask the user to classify the issue if possible:
- CPU spike or battery drain
- Janky scrolling or dropped frames
- High memory or image pressure
- Hangs or unresponsive interactions
- Excessive or unexpectedly broad view updates

For the full profiling intake checklist, read `references/profiling-intake.md`.

## 2. Code-First Review

Focus on:
- Invalidation storms from broad observation or environment reads.
- Unstable identity in lists and `ForEach`.
- Heavy derived work in `body` or view builders.
- Layout thrash from complex hierarchies, `GeometryReader`, or preference chains.
- Large image decode or resize work on the main thread.
- Animation or transition work applied too broadly.

Use `references/code-smells.md` for the detailed smell catalog and fix guidance.

Provide:
- Likely root causes with code references.
- Suggested fixes and refactors.
- If needed, a minimal repro or instrumentation suggestion.

## 3. Profile with Instruments

If code review does not explain the issue, get runtime evidence from Instruments:

- Profile a Release build with the SwiftUI template (the SwiftUI instrument with Time Profiler, Hangs and Hitches), one interaction per capture. Debug builds and mixed interactions distort the result.
- If the user runs Instruments, ask for a trace export or screenshots of the SwiftUI timeline and the Time Profiler call tree, the device, OS and build configuration, the exact interaction profiled, and before/after metrics if they are comparing a change.
- If the agent can run commands on the Mac, it can record and export the trace itself with `xcrun xctrace record` and `xcrun xctrace export`, which avoids a round trip through the user. The interaction still has to happen during the recording, performed by the user or by a UI test.
- Where Apple's xctrace agent skill from Xcode 27 is installed, use it to record and read traces (call trees, symbolication, hang triage) instead of working out the `xctrace` commands here.

Use `references/profiling-intake.md` for the full checklist and collection steps.

## 4. Analyze and Diagnose

- Map the evidence to the most likely category: invalidation, identity churn, layout thrash, main-thread work, image cost, or animation cost.
- Prioritize problems by impact, not by how easy they are to explain.
- Distinguish code-level suspicion from trace-backed evidence.
- Call out when profiling is still insufficient and what additional evidence would reduce uncertainty.

## 5. Remediate

Apply targeted fixes:
- Narrow state scope and reduce broad observation fan-out.
- Stabilize identities for `ForEach` and lists.
- Move heavy work out of `body` into derived state updated from inputs, model-layer precomputation, memoized helpers, or background preprocessing. Use `@State` only for view-owned state, not as an ad hoc cache for arbitrary computation.
- Use `equatable()` only when equality is cheaper than recomputing the subtree and the inputs are truly value-semantic.
- Downsample images before rendering.
- Reduce layout complexity or use fixed sizing where possible.

Use `references/code-smells.md` for examples, Observation-specific fan-out guidance, and remediation patterns.

## 6. Verify

Re-run the same capture (the user in Instruments, or the agent with `xctrace`) and compare it with the baseline.
Summarize the delta (CPU, frame drops, memory peak) when the numbers are available.

## Outputs

Provide:
- A short metrics table (before/after if available).
- Top issues (ordered by impact).
- Proposed fixes with estimated effort.

Use `references/report-template.md` when formatting the final audit.

## References

- Profiling intake and collection checklist: `references/profiling-intake.md`
- Common code smells and remediation patterns: `references/code-smells.md`
- Audit output template: `references/report-template.md`
- Optimizing SwiftUI performance with Instruments: `references/optimizing-swiftui-performance-instruments.md`
- Understanding and improving SwiftUI performance: `references/understanding-improving-swiftui-performance.md`
- Understanding hangs in your app: `references/understanding-hangs-in-your-app.md`
- Demystify SwiftUI performance (WWDC23): `references/demystify-swiftui-performance-wwdc23.md`
- When Instruments workflows or SwiftUI performance guidance may have changed, check current Apple Developer documentation with the session's documentation or web tools. Apple's pages are rendered with JavaScript, so prefer a scraper that renders pages, or the JSON form `https://developer.apple.com/tutorials/data/documentation/<path>.json`.

## Related skills

- Apple's swiftui-specialist skill, which ships with Xcode 27, also covers SwiftUI performance patterns (`@Observable` invalidation, `ForEach` identity); use it alongside this skill when it is installed.
- For structural cleanup without a runtime symptom, use evenbetter-swiftui-view-refactor. For component and navigation patterns, use evenbetter-swiftui-ui-patterns.
