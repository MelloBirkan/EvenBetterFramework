---
name: evenbetter-accessibility-nutrition-labels
description: >-
  Works out which App Store Accessibility Nutrition Labels an iOS app can truthfully declare on each device, from its common tasks, EvenBetter findings, runtime results and manual checks, and drafts the answers for a person to enter. Use when filling in App Accessibility in App Store Connect or deciding which labels to claim. For other store prep, use evenbetter-app-launcher.
---

# evenbetter-accessibility-nutrition-labels

> Paths in this skill and its references are relative to this SKILL.md's folder. The plugin corpus is at `../../corpus/`.

Paths inside the user's project, such as a finding's `file_path` and the `.evenbetter/` folder, resolve against the project root.

## Operating model

Accessibility Nutrition Labels are the accessibility section of an App Store product page. For each device the app runs on, the developer says which of nine features it supports: VoiceOver, Voice Control, Larger Text, Dark Interface, Differentiate Without Color Alone, Sufficient Contrast, Reduced Motion, Captions and Audio Descriptions. Apple asks developers to indicate a feature only when people can complete all of the app's common tasks with it, and to leave it out when bugs would change that answer.

This skill builds the answer from evidence. It lists the common tasks and builds a matrix of tasks against features for each device. It fills each cell from the validated EvenBetter report, runtime verdicts and manual checks, then asks the person to decide. It writes three files: an evaluation log, a draft of the answers in the App Store Connect API's attribute shape, and an outline for the optional accessibility URL page.

The person enters the answers in App Store Connect, under App Accessibility in the app's sidebar, and publishes them there. The skill never calls the App Store Connect API and never publishes. A Declare in the draft is EvenBetter's reading of the evidence the person supplied. It does not certify the app as accessible.

What Apple says about the labels (App Store Connect Help, read 2026-11-07):

- They are voluntary to start. Apple says that over time they will be required to submit new apps and app updates, and gives no date.
- They appear on the product page on devices running iOS 26, iPadOS 26, macOS 26, tvOS 26, visionOS 26 or watchOS 26 and later, for the type of device the visitor is using. A device with no answers shows that support has not been indicated yet.
- App Store search uses them: for a query such as "VoiceOver note taking apps", apps that declare the feature rank as more relevant.
- App Review Guideline 2.3 (accurate metadata) applies to the answers. When labels look intentionally misleading or harmful, App Review can contact the developer and ask for an update.
- iPhone and iPad apps that run on Apple silicon Macs or on Apple Vision Pro need no separate answers there. Those stores show the iPhone or iPad labels.

A stage name given as the argument (for example `1-common-tasks`) selects that stage.

## Stages

Run the stages in order. Each stage's reference holds its steps.

| Stage | Reference | Does |
| --- | --- | --- |
| `0-intake` | `references/0-intake.md` | Reads the report and runtime results, works out the devices and media, and loads the last evaluation |
| `1-common-tasks` | `references/1-common-tasks.md` | Lists the common tasks from the code and confirms them with the person |
| `2-evidence` | `references/2-evidence.md` | Builds the matrix for each device and fills it from findings, runtime verdicts and manual checks |
| `3-decide` | `references/3-decide.md` | Gets the person's decision for each feature on each device |
| `4-write` | `references/4-write.md` | Writes the evaluation log, the declaration draft and the accessibility URL outline |

`references/feature-criteria.md` summarizes Apple's evaluation criteria for each feature, with device availability and the manual test steps. Read it in `2-evidence` and `3-decide`. `references/feature-clause-map.md` maps each feature to corpus clauses and to the runtime checks of evenbetter-accessibility-tests. Read it in `2-evidence`.

Say nothing about which features a finding blocks or leaves clear before `2-evidence` has built the matrix from that map. A finding's clause often maps to a feature its title does not name (a missing button trait blocks Voice Control as well as VoiceOver), so a guess from titles gets cells wrong. When a turn ends on a question before that stage, list the open findings and say that `2-evidence` assesses the features.

## Evidence rules

These decide every cell. `references/2-evidence.md` applies them.

- A cell is `pass`, `blocked`, `untested` or `n/a`. Every cell starts as `untested`, and an untested cell is not a pass.
- A cell passes only when a person reports completing the task with the feature on and nothing blocks the cell. Clean code scans, clean runtime audits and passing specialist results stay notes, because none of them completes a task.
- An open finding of severity `critical` or `high` on one of the task's screens, whose clause maps to the feature, blocks the cell. A `medium` or `low` finding adds a note that the manual check asks about.
- A `confirmed` runtime verdict blocks the cell whatever the finding's severity. `refuted` and `inconclusive` verdicts are notes and never lift a block, because only evenbetter-validate removes a finding. `not_testable` means the manual check is the only test. `untested` adds nothing.
- A manual check where the person got stuck blocks that task's cell. So does a failing result from an Xcode accessibility specialist, labelled unconfirmed.
- Recommend Declare only when every cell for that feature on that device is `pass` or `n/a`, with at least one `pass`.
- Assess each device on its own. An iPad answer needs iPad evidence, even when the iPad build shares the iPhone code.
- The person's choice wins. A Declare against a blocked or untested cell is recorded under "Declared against evidence" in the log.

## Rules

- Read the analyze report and the accessibility-tests log, and never write them. This skill never adds, removes or re-rates a finding.
- Never call the App Store Connect API and never publish or submit anything. The person enters the answers.
- Write only the three files under `.evenbetter/[project]/` that `references/4-write.md` names. Never edit app code, and never write inside the plugin folder.
- When a manual check reports a blocked task, ask for a screenshot or a screen recording from the device or simulator.
- Name each blocking finding by its ID and clause, so evenbetter-repair can pick it up.

## Workflow position

- Run it after evenbetter-validate, on a report whose `workflow.state` is `validated`. Runtime verdicts from evenbetter-accessibility-tests add evidence. With less evidence the skill still runs, and more cells stay untested.
- Blockers go to evenbetter-repair. After a repair, run evenbetter-accessibility-tests with `recheck` if it ran before, then evenbetter-validate, then this skill again. Run it before each release too, since the log compares each run with the last one.
- Xcode 27 ships Apple-built specialists for targeted tasks, accessibility among them. When the person shares their results, they count as evidence in `2-evidence`.
- App Privacy labels are a different App Store Connect section, and this skill does not cover them. Writing accessibility modifiers such as `accessibilityLabel(_:)` belongs to evenbetter-swiftui-accessibility.
- For screenshots, metadata, App Review and the rest of submission, use evenbetter-app-launcher.

## Question tooling

Ask with the host's structured question tool when it has one:

- Claude Code: `AskUserQuestion`, with 2-4 mutually exclusive options per question.
- Codex in Plan mode: `request_user_input`, with 1-3 short questions of 2-3 options each, the recommended option first and marked "(Recommended)". The client adds "Other". Plan mode is read-only, so present results in a `<proposed_plan>` block and ask the user to switch to Default mode before writing `.evenbetter/` files or editing code.
- Codex in Default mode: ask one concise closed question with numbered options in plain text, then wait. Use `request_user_input` instead if the session offers it.
- Other agents: use their structured question tool, or ask one closed question with numbered options.
- When nobody can answer, because the user said they will not be around or asked you to go ahead without questions, or because the run is one-shot and non-interactive (such as `claude -p`, `codex exec`, CI or a scheduled task), do not end the turn on a clarifying question. Take the recommended option, say which one you took, and record it as an assumption in the artifact or the final reply. Never assume an approval the user has not given, such as accepting a plan or starting to edit code: finish the current stage and end with what waits on the person. Any exception this skill names elsewhere still applies.

Questions are closed, with the recommended option first, and at most three at a time. When nobody can answer, take the recommended option. The report-state question in `0-intake` is the one place where that ends the run, with the skill to run first as the next step. Past it, run every stage to `4-write`. The recommended answer to a manual check is always "Not tested yet", so a run nobody answers never records a pass.

## Tool equivalents

The references use Claude Code tool names. In Codex, use these equivalents, and do not simulate a tool the session does not have:

| Claude Code | Codex |
| --- | --- |
| `AskUserQuestion` | `request_user_input` (Plan mode, or Default mode when enabled); otherwise a closed plain-text question |
| `Glob`, `Grep`, `Read` | `rg --files`, `rg`, and shell reads such as `sed -n` or `nl` through `exec_command` |
| `Read` on an image or screenshot | `view_image` |
| `Edit`, `Write` | `apply_patch` (Default mode only) |
| `Bash` | `exec_command` |
| `WebSearch`, `WebFetch` | `web_search`, or a configured MCP search or fetch tool such as Firecrawl, Tavily or Exa; `curl` through `exec_command` where network access is allowed |

Apple pages are rendered with JavaScript; a plain fetch can return a "requires JavaScript" shell. Prefer a scraper MCP that renders pages (Firecrawl, Tavily extract, Exa fetch) or Apple's JSON form: `https://developer.apple.com/tutorials/data/documentation/[path].json` for API docs.

If current system, developer or user instructions conflict with this skill, follow them.

## Next step

After the summary lines from `4-write`, end with each line that applies, in this order:

- Blocking findings on a `validated` report whose `validated_at` is not earlier than `scan_date`: "Next, run the evenbetter-repair skill for [finding IDs]."
- Blocking findings on an `analyzed`, stale `validated` or `repaired` report used as it stands: "Next, run the evenbetter-validate skill, then evenbetter-repair for the blockers that remain."
- Findings still `untested` at runtime whose clauses have a runtime check: "Run the evenbetter-accessibility-tests skill for [finding IDs], then run this skill again."
- Pending manual checks: "Run the pending checks in the log on a device, then run this skill again."
- Always last: "When you are ready, enter the answers in App Store Connect under App Accessibility and publish them there. For the rest of submission, run the evenbetter-app-launcher skill."
