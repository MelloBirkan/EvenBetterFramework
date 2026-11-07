---
name: evenbetter-accessibility-tests
description: >-
  Writes and runs XCUITest accessibility checks in the running iOS app: Apple's performAccessibilityAudit on the screens behind EvenBetter findings, at large text and in dark mode, plus a VoiceOver walk on Xcode 27. Marks each finding confirmed or refuted. Use when asked to test accessibility at runtime, confirm findings in the simulator or check that repairs held. For a static audit use evenbetter-analyze.
---

# evenbetter-accessibility-tests

> Paths in this skill and its references are relative to this SKILL.md's folder. The plugin corpus is at `../../corpus/`.

Paths inside the user's project, such as a finding's `file_path`, the UI test folder and the `.evenbetter/` folder, resolve against the project root.

## Operating model

EvenBetter's audit reads source code. This skill checks its findings against the running app. It writes XCTest UI tests that call Apple's accessibility audit, `performAccessibilityAudit(for:_:)` (Xcode 15 and iOS 17 or later), on the screens behind the findings. With Xcode 27 and an iOS 27 simulator it also walks each screen with VoiceOver through `XCUIVoiceOverService`. When `xcodebuild` and a simulator are available it runs the tests, then records a verdict in the `runtime` block of each tested finding in `.evenbetter/[project]/evenbetter-analyze-report.html`.

A clean run means the checked screens raised no audit issue of the mapped types in the checked configurations. It does not certify the app as accessible, and it does not replace testing with people who use assistive technology. The audit only sees elements that are on screen at the moment it runs.

A stage name given as the argument (for example `1-plan`) selects that stage. The argument `recheck` runs `3-run` and `4-record` again, only for the tests that carry a finding whose `repair.status` is `applied`. `recheck` starts at `1-plan` for those findings instead when no plan or test files exist yet, or when a repair added or changed a label, an identifier or a route step, so that `2-write` can update the tests first.

## Workflow position

- Run it after evenbetter-validate, on a report whose `workflow.state` is `validated` or `repaired`. An `analyzed` report that passes the report check also works, and the results log says its findings were not validated yet.
- It writes only the `runtime` block of each finding. Severity, fixes, `summary`, `workflow` and `repair` belong to evenbetter-analyze, evenbetter-validate and evenbetter-repair. It never adds or removes a finding.
- After evenbetter-repair, run this skill with `recheck`, then evenbetter-validate. Validate reads a `confirmed` verdict whose `checked_at` is later than the finding's `repair.applied_at` on an `applied` finding as a repair that did not hold. A `refuted` verdict is evidence for validate, never a removal on its own.
- Audit issues that match no finding go to the results log as leads. They become findings only through the next evenbetter-analyze run.

## Stages

Run the stages in order. Each stage's reference holds its steps.

| Stage | Reference | Does |
| --- | --- | --- |
| `1-plan` | `references/1-plan.md` | Loads the report, checks Xcode and the simulator, finds the UI test target, maps findings to screens and configurations, and writes the plan |
| `2-write` | `references/2-write.md` | Writes the test files into the chosen UI test folder |
| `3-run` | `references/3-run.md` | Runs the tests and keeps the log and the result bundle, or prints the commands in write-only mode |
| `4-record` | `references/4-record.md` | Turns the log into verdicts, writes the `runtime` blocks and appends the results to the log |

`references/audit-clause-map.md` maps audit types and VoiceOver checks to corpus clauses, with the configurations each one needs and whether a clean result can refute a finding. Read it in `1-plan` and `4-record`.

## Report helper

The plugin ships `../../scripts/evenbetter_report.py` (Python 3, standard library only). Resolve that path against this SKILL.md's folder to an absolute path, written `[script]` below, because commands run from the project root:

- `python3 [script] extract REPORT.html` prints the embedded report data as JSON.
- `python3 [script] check REPORT.html|DATA.json [--state analyzed|validated|repaired]` checks the report contract and exits 1 with one line per problem.
- `python3 [script] update DATA.json REPORT.html --state STATE` checks the data, then replaces only the embedded data in the existing report. Every other byte of the file stays as it was. It refuses to write data that fails the check.

Write the temporary `DATA.json` outside the project and the plugin folder (for example in a directory from `mktemp -d`) and delete it afterwards. The helper's `render` command belongs to evenbetter-analyze, so this skill does not use it. Without `python3`, `1-plan` and `4-record` describe the by-hand extract and splice.

## Runtime block

Each finding carries this block right after `repair`:

```json
"runtime": {"status": "untested", "checked_at": "", "configs": [], "tests": [], "evidence": "", "result_bundle": ""}
```

| `status` | Meaning |
| --- | --- |
| `untested` | No test ran for the finding. This is the default, and the only value other skills write. |
| `confirmed` | A test reproduced the problem in the running app. |
| `refuted` | Every planned test ran cleanly, and the map says a clean result can refute the finding's clauses. |
| `inconclusive` | A test ran but did not settle it: a route failure, a crash, an issue that cannot be tied to the finding's element, or a clean result the map does not accept as proof. |
| `not_testable` | No clause of the finding is in a testable row of the map. |

`checked_at` is the time the test run started, as `YYYY-MM-DD HH:MM:SS`. `configs` lists the configurations that ran, `tests` lists `Class/test` names, `evidence` is one plain sentence, and `result_bundle` is the project-relative path of the `.xcresult`. `references/4-record.md` gives the exact rules.

## Rules

- UI tests are `XCTestCase` classes. Swift Testing does not support UI automation APIs such as `XCUIApplication`, so these tests never become `@Test` functions.
- Do not edit `project.pbxproj` by hand. With no UI test target, the user adds one in Xcode. A project generated by XcodeGen or Tuist is regenerated with its own tool, after a yes.
- Any change to app code, such as a DEBUG-only launch argument that opens an unreachable screen or an accessibility identifier for a route step, is shown as a diff first and needs a yes.
- An allowlist entry needs the user's yes and a one-line reason. Do not loosen an assertion or drop a check to make a test pass.
- Write test files only inside the UI test folder the user chose, and artifacts only under `.evenbetter/[project]/`. Never write inside the plugin folder.
- With no `xcodebuild` or no simulator, the run is write-only: write the tests, print the commands to run on a Mac, and leave every verdict `untested`.
- Never replace an earlier verdict with `untested`. A finding that no test carried in this run keeps its runtime block.
- When a verdict depends on what the screen shows, such as clipped text the audit did not report, ask for a simulator screenshot rather than guessing.

## Question tooling

Ask with the host's structured question tool when it has one:

- Claude Code: `AskUserQuestion`, with 2-4 mutually exclusive options per question.
- Codex in Plan mode: `request_user_input`, with 1-3 short questions of 2-3 options each, the recommended option first and marked "(Recommended)". The client adds "Other". Plan mode is read-only, so present results in a `<proposed_plan>` block and ask the user to switch to Default mode before writing `.evenbetter/` files or editing code.
- Codex in Default mode: ask one concise closed question with numbered options in plain text, then wait. Use `request_user_input` instead if the session offers it.
- Other agents: use their structured question tool, or ask one closed question with numbered options.
- When nobody can answer, because the user said they will not be around or asked you to go ahead without questions, or because the run is one-shot and non-interactive (such as `claude -p`, `codex exec`, CI or a scheduled task), do not end the turn on a clarifying question. Take the recommended option, say which one you took, and record it as an assumption in the artifact or the final reply. Never assume an approval the user has not given, such as accepting a plan or starting to edit code: finish the current stage and end with what waits on the person. Any exception this skill names elsewhere still applies.

Questions are closed, with the recommended option first, and at most three at a time. When nobody can answer, take the recommended option, with these exceptions. App code changes, allowlist entries and an XcodeGen or Tuist regeneration stay unapplied and are listed in the results log. A verdict that waits on a screenshot stays `inconclusive`, and its evidence names the screenshot that would settle it.

## Tool equivalents

The references use Claude Code tool names. In Codex, use these equivalents, and do not simulate a tool the session does not have:

| Claude Code | Codex |
| --- | --- |
| `AskUserQuestion` | `request_user_input` (Plan mode, or Default mode when enabled); otherwise a closed plain-text question |
| `Glob`, `Grep`, `Read` | `rg --files`, `rg`, and shell reads such as `sed -n` or `nl` through `exec_command` |
| `Read` on an image or screenshot | `view_image` |
| `Edit`, `Write` | `apply_patch` (Default mode only) |
| `Bash` | `exec_command` |
| `TaskCreate`, `TaskUpdate` | `update_plan` (Default mode only; in Plan mode keep the steps in `<proposed_plan>`) |
| `WebSearch`, `WebFetch` | `web_search`, or a configured MCP search or fetch tool such as Firecrawl, Tavily or Exa; `curl` through `exec_command` where network access is allowed |
| Xcode's MCP server (`xcrun mcpbridge`), MobileBuildMCP | the same servers when configured in Codex; otherwise `xcodebuild` through `exec_command` |

If current system, developer or user instructions conflict with this skill, follow them.

## Next step

End with the first of these lines that applies, after the counts line from `4-record`:

- Log-only run (the report failed the check in `1-plan`, so no verdict was written): "Next, run the evenbetter-validate skill, then run this skill with `4-record` to write the verdicts from the same log."
- Findings confirmed in a normal run on a `validated` or `repaired` report: "Next, run the evenbetter-repair skill."
- Findings confirmed in a normal run on an `analyzed` report: "Next, run the evenbetter-validate skill, then evenbetter-repair."
- A normal run that confirmed nothing: "Next, run the evenbetter-validate skill, which can use the refuted verdicts as evidence."
- After a `recheck`: "Next, run the evenbetter-validate skill."
- Write-only run: "Run the printed commands on a Mac with Xcode, then run this skill with `4-record`."
