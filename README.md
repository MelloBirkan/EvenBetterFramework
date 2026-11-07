# EvenBetter

EvenBetter is a set of curated agent skills for Claude Code and Codex. The skills help an AI coding agent plan SwiftUI apps and audit them against Apple's Human Interface Guidelines (HIG) and WCAG 2.2, then fix what the audit finds, while you keep the decisions that need a person.

[Website](https://evenbetter.mellofattura.com) · [Install](#install) · [Audit workflow](#how-the-audit-works) · [Skills](#skills) · [iOS corpus](#the-ios-corpus) · [Research](#research)

## Why it exists

Ask a coding agent for a SwiftUI screen and you will usually get one that compiles and looks fine. The agent fills the gaps in your request with guesses, and the gaps are often about accessibility: VoiceOver labels, Dynamic Type, contrast, touch targets, the confirmation before a destructive action.

EvenBetter hands the agent a written procedure for the job. A planning skill asks closed questions about screens, states and accessibility before any code exists. An audit skill reads the Swift sources and ties every finding to a file and line, a rule in the EvenBetter corpus, and the Apple page that rule comes from. When a fix depends on product intent (copy, navigation, visual design), the skill asks you instead of guessing.

The skills are written and reviewed before they ship, so the agent follows a known procedure instead of making one up mid-task.

## What you get

The repository is a plugin marketplace called `evenbetter` with two plugins:

| Plugin | Skills | Covers |
| --- | --- | --- |
| `evenbetter-ios` | 18 | iOS feature and epic planning, the analyze → validate → repair audit, runtime accessibility tests, SwiftUI build and review guides, Accessibility Nutrition Labels, App Store launch and research. Ships the 61-clause iOS corpus. |
| `evenbetter-general` | 2 | The same feature and epic planning workflow, without a platform design system. |

Claude Code and Codex install the same skill files. Only the manifests differ.

## Install

### Claude Code

Inside Claude Code:

```text
/plugin marketplace add MelloBirkan/EvenBetterFramework
/plugin install evenbetter-ios@evenbetter
/plugin install evenbetter-general@evenbetter
/reload-plugins
```

Or from a terminal:

```bash
claude plugin marketplace add MelloBirkan/EvenBetterFramework
claude plugin install evenbetter-ios@evenbetter
```

On Claude Code 2.1.275 or later, one command does both: `claude plugin install evenbetter-ios --marketplace MelloBirkan/EvenBetterFramework`.

Install only the plugin you need. Claude Code puts the plugin name in front of each skill, so the skills show up as `/evenbetter-ios:evenbetter-analyze`, `/evenbetter-ios:evenbetter-ios-feature`, `/evenbetter-general:evenbetter-general-feature` and so on. You rarely need the full name: describe the task and the agent picks the skill.

### Codex

```bash
codex plugin marketplace add MelloBirkan/EvenBetterFramework
codex plugin add evenbetter-ios@evenbetter
codex plugin add evenbetter-general@evenbetter
```

You can also install from the Codex app (Plugins → evenbetter → Add to Codex) or from the `/plugins` browser inside `codex`. Start a new thread afterwards. Ask for what you need in plain words, mention a skill with `$`, such as `$evenbetter-analyze`, or mention the whole plugin with `@`.

### Xcode tools (optional)

`evenbetter-ios` registers Xcode's MCP bridge (`xcrun mcpbridge`) as an MCP server named `xcode`. The bridge comes with Xcode 26.3 or later. Xcode has to be running, with "Allow External Agents to Use Xcode Tools" switched on in its Intelligence settings. Apple explains the setup in [Giving external agents access to Xcode](https://developer.apple.com/documentation/xcode/giving-external-agents-access-to-xcode). The skills still work without it.

`evenbetter-ios-debugger-agent` uses the Xcode server first. When it isn't available, the skill falls back to [MobileBuildMCP](https://github.com/getsentry/MobileBuildMCP) (formerly XcodeBuildMCP), a separate MCP server you install yourself, and then to `xcodebuild` and `simctl`.

## Quick start

Open your SwiftUI project in the agent and describe the task in plain words. The agent picks the skill from your request, or you can name it.

| You ask | Skill that runs | What it leaves in your project |
| --- | --- | --- |
| "Plan a favorites screen for my iOS app" | `evenbetter-ios-feature` | `.evenbetter/<feature>/ios-ux-plan.md` and tickets |
| "Plan an iOS app for splitting household chores" | `evenbetter-ios-epic` | `.evenbetter/<epic>/` with a UX brief, screen flows, a tech plan and tickets |
| "Audit this SwiftUI app for accessibility" | `evenbetter-analyze` | `.evenbetter/<project>/evenbetter-analyze-report.html` |
| "Validate the EvenBetter report" | `evenbetter-validate` | The same report, checked and stamped `validated` |
| "Fix the critical findings" | `evenbetter-repair` | Edits to your Swift files, with each outcome recorded in the report |
| "Confirm these findings on the simulator" | `evenbetter-accessibility-tests` | XCUITest accessibility tests, and a runtime verdict on each finding in the report |
| "Which Accessibility Nutrition Labels can we declare?" | `evenbetter-accessibility-nutrition-labels` | A per-device evaluation and draft App Store Connect answers for you to enter |

EvenBetter's plans, reports and records land in `.evenbetter/` at the project root as plain Markdown, HTML and JSON. Only code goes elsewhere: repair edits your Swift files, and the runtime tests add XCUITest files to the UI test folder you pick. You can commit `.evenbetter/` next to the code or add the folder to `.gitignore`.

## How the audit works

EvenBetter splits work on an iOS app into four states: planning, analysis, validation and repair. Each state is a separate skill invocation, and each one leaves a file you can open and review. Runtime tests can check the findings on a simulator after any of the audit steps.

```mermaid
flowchart LR
    P["Planning<br/>evenbetter-ios-feature<br/>evenbetter-ios-epic"] --> A["Analysis<br/>evenbetter-analyze"]
    A -- "state: analyzed" --> V["Validation<br/>evenbetter-validate"]
    V -- "state: validated" --> R["Repair<br/>evenbetter-repair"]
    R -- "state: repaired" --> V
    T["Runtime tests<br/>evenbetter-accessibility-tests"] -.->|"runtime verdicts"| V
```

The audit states share one artifact, `.evenbetter/<project>/evenbetter-analyze-report.html`.

1. `evenbetter-analyze` reads the Swift sources against the corpus and writes the report. Each finding has file and line evidence, the clause it breaks, a link to Apple's documentation, a minimal fix, a recommended fix and a prompt you can hand back to the agent. If the agent can't find an Apple source for a finding, it drops the finding. When a report already exists, analyze keeps the old one in `history/` before writing the new one.
2. `evenbetter-validate` reopens the report and checks every finding against the live source, the corpus and Apple's documentation. It drops false positives, merges duplicates, adjusts severities and rewrites any fix that wouldn't resolve the violation, then stamps the report `validated`.
3. `evenbetter-repair` goes through the validated findings by severity. It applies technical fixes in the source, such as accessibility modifiers, API updates and semantic substitutions. Product copy, navigation and visual design go back to you as closed questions with options taken from your code. Every finding ends as `applied`, `deferred`, `skipped` or `failed` in the report.
4. `evenbetter-accessibility-tests` is optional and needs a Mac with Xcode. It writes XCUITest accessibility audits for the screens in the report, plus a VoiceOver walk on Xcode 27, runs them, and records whether each finding was confirmed, refuted or couldn't be tested.

Repair won't run on a report that hasn't been validated, or on one whose validation is older than its last scan. It says which skill to run first and stops, so unchecked findings never turn into code changes.

Running `evenbetter-validate` again after a repair closes the loop. Findings that were fixed drop out of the report. If repair marked a finding as applied but the violation is still in the code, or a runtime test still confirms it, validate flips it to `failed` and the next repair run picks it up.

The skills read and write the report through a small Python script that ships with the plugin (`scripts/evenbetter_report.py`, standard library only). It checks the report against its contract before every write. Without Python, the skills edit the embedded data by hand.

![An evenbetter-analyze report for the Aroma Care SwiftUI app, showing 55 findings split by severity and the first findings with their clause IDs and file locations](docs/images/analyze-report.jpg)

*The report the study participants read: Aroma Care, a SwiftUI app, after analyze and validate.*

## Skills

### evenbetter-ios

#### Planning

| Skill | Use it for |
| --- | --- |
| `evenbetter-ios-feature` | A single screen or small feature: UX plan, plan review, tickets, implementation review. |
| `evenbetter-ios-epic` | A multi-screen flow or a whole app: UX brief, screen flows, HIG tech plan, tickets. |

#### Audit

| Skill | Use it for |
| --- | --- |
| `evenbetter-analyze` | Scan the project and write the HTML report. |
| `evenbetter-validate` | Recheck the report and stamp it as validated. |
| `evenbetter-repair` | Apply the validated findings to the source. |
| `evenbetter-accessibility-tests` | Confirm findings at runtime with XCUITest accessibility audits and a VoiceOver walk. |

#### Building and reviewing SwiftUI

| Skill | Use it for |
| --- | --- |
| `evenbetter-swiftui-accessibility` | VoiceOver, Dynamic Type and contrast checks on one view or a few, with corpus clause IDs. |
| `evenbetter-swiftui-ui-patterns` | Navigation, sheets, forms, controls and layout patterns. |
| `evenbetter-swiftui-view-refactor` | Splitting oversized views and cleaning up data flow. |
| `evenbetter-swiftui-performance-audit` | Slow rendering, janky scrolling and extra view updates, with Instruments or `xctrace`. |
| `evenbetter-swiftui-liquid-glass` | The Liquid Glass APIs from iOS 26 on. |
| `evenbetter-ios-haptics` | Matching `.sensoryFeedback` and Core Haptics to events. |
| `evenbetter-ios-app-intents` | App Intents, App Shortcuts, Siri and Spotlight. |
| `evenbetter-design` | Distinctive SwiftUI interfaces that don't look like the default iOS template. |
| `evenbetter-ios-debugger-agent` | Building, running and inspecting the app on a booted simulator. |

#### Product and launch

| Skill | Use it for |
| --- | --- |
| `evenbetter-app-opportunity-research` | Market and competitor research for an app idea, with a cited source for every claim. |
| `evenbetter-app-launcher` | App Store submission, review, pricing and launch. |
| `evenbetter-accessibility-nutrition-labels` | Deciding which Accessibility Nutrition Labels the app can declare on each device, from audit findings, runtime results and manual checks. |

### evenbetter-general

| Skill | Use it for |
| --- | --- |
| `evenbetter-general-feature` | Feature planning and tickets for any platform. |
| `evenbetter-general-epic` | Epic planning, core flows and tickets for any platform. |

## The iOS corpus

The audit skills don't work from the model's memory of the HIG. They read a Markdown corpus that ships inside the iOS plugin, at [`plugins/evenbetter-ios/corpus/`](plugins/evenbetter-ios/corpus/). It holds 61 clauses in seven domains:

| Domain | ID prefix | Clauses | Focus |
| --- | --- | --- | --- |
| Typography | `TYPO` | 11 | Text styles, Dynamic Type, hierarchy, Large Content Viewer |
| Color and theming | `CLR` | 7 | Dark Mode, contrast, semantic colors, Smart Invert |
| Components and patterns | `COMP` | 7 | Native controls, destructive actions, feedback |
| Layout and interaction | `LAY` | 9 | Touch targets, spacing, empty and loading states |
| Navigation and flow | `NAV` | 8 | Navigation stacks, back behavior, modals |
| Accessibility | `A11Y` | 15 | Labels, grouping, traits, Voice Control, gestures, charts, captions |
| Haptics | `HAPT` | 4 | When and how to use sensory feedback |

Each clause has a stable ID such as `TYPO-UI-001`, a severity (`error`, `warning` or `info`), a dimension (UI, UX or A11Y), the source URL and the date it was retrieved. The body says what to check, why it matters to users, and what correct SwiftUI looks like. A guideline becomes a clause only if it can be observed in SwiftUI code and traced to a public Apple or W3C source. Where the sources give numbers, such as minimum touch target size or contrast ratio, the clause keeps them.

Every clause was checked again on 2026-11-07 against the current HIG, which Apple revised in June and September 2026. The twelve newest clauses come from Apple's Accessibility Nutrition Label evaluation criteria.

`index.json` lists every clause for lookup and has to stay in sync with the Markdown files. The format is documented in [`SCHEMA.md`](plugins/evenbetter-ios/corpus/SCHEMA.md).

## Research

EvenBetter is the subject of *Curated Agent Skills for Context-Aware Intelligent Support in iOS UX and Accessibility*, by Marcello Gonzatto Birkan, Daniela Brazolin Flauto and Valéria Farinazzo Martins (Universidade Presbiteriana Mackenzie). The paper was accepted at the 8th Workshop on Intelligent Interactive Systems (8WoSI²), part of the 12th Ibero-American Conference on Human-Computer Interaction (12JIHC'26) in Talca, Chile. The [project website](https://evenbetter.mellofattura.com) covers the study in Portuguese.

Ten iOS developers took part in a formative study. They explored the website, planned an app with an EvenBetter skill and read an audit report. They rated the workflow with a mean System Usability Scale score of 79.5 (median 81.25). All ten read the report's totals correctly, and eight ran analyze and then validate in the right order. The study looked at whether developers could understand and use the workflow. It didn't check whether every finding was technically correct, so treat a report as material for review rather than an accessibility certification.

The paper describes 17 skills. `evenbetter-repair` came later, and `evenbetter-accessibility-tests` and `evenbetter-accessibility-nutrition-labels` followed in November 2026, which brings the total to 20. The runtime tests add a check the study did not have: whether a finding shows up in the running app.

```bibtex
@inproceedings{birkan2026evenbetter,
  title     = {Curated Agent Skills for Context-Aware Intelligent Support in iOS UX and Accessibility},
  author    = {Gonzatto Birkan, Marcello and Brazolin Flauto, Daniela and Farinazzo Martins, Val{\'e}ria},
  booktitle = {8{\textdegree} Workshop en Sistemas Interactivos Inteligentes (8WoSI{\textsuperscript{2}}), 12{\textdegree} Jornadas Iberoamericanas de Interacci{\'o}n Humano-Computadora (12JIHC'26)},
  address   = {Talca, Chile},
  year      = {2026},
  note      = {Accepted paper}
}
```

## Updating

Claude Code, from a terminal:

```bash
claude plugin marketplace update evenbetter
claude plugin update evenbetter-ios@evenbetter
claude plugin update evenbetter-general@evenbetter
```

Restart Claude Code, or run `/reload-plugins`, to load the new version.

Codex:

```bash
codex plugin marketplace upgrade evenbetter
```

If the new version doesn't show up, reopen Codex or the plugin browser.

The manifests have no `version` field on purpose. Without one, Claude Code uses the git commit SHA as the version, so every commit on `main` counts as a new development release. Codex doesn't document the same fallback, so update it with `codex plugin marketplace upgrade` until the project adopts versioned releases.

## Limitations

- The platform-specific skills cover iOS only. Android will come when there are Android skills to ship.
- This is a custom GitHub marketplace. It isn't listed in either official plugin directory.
- The skills run on whatever model your agent uses, so two model versions can produce different reports from the same code. Validation catches some of this, not all.
- Runtime tests need a Mac with Xcode, and the VoiceOver walk needs Xcode 27 with an iOS 27 simulator. Without them, findings keep a runtime status of `untested`.
- Accessibility Nutrition Labels are your declaration to Apple. The skill drafts answers from the evidence it has; you review them and enter them in App Store Connect.
- Installing from a private fork only works if your local Git, Claude Code or Codex setup can authenticate to it.

## Contributing

The skills that ship to users live in two places:

- `plugins/evenbetter-ios/skills/`
- `plugins/evenbetter-general/skills/`

Edit them there. Don't keep copies at the repository root.

```text
.claude-plugin/marketplace.json        Claude Code marketplace
.agents/plugins/marketplace.json       Codex marketplace
.github/workflows/validate.yml         Checks that run on every pull request
scripts/check-skills.py                Skill, manifest and corpus checks
plugins/
  evenbetter-ios/
    .claude-plugin/plugin.json         Claude Code manifest
    .codex-plugin/plugin.json          Codex manifest
    .mcp.json                          Xcode MCP bridge, read by both hosts
    corpus/                            61-clause iOS corpus and index.json
    scripts/evenbetter_report.py       Report helper used by the audit skills
    skills/                            18 skills
    evals/                             claude plugin eval suite (routing and behaviour)
  evenbetter-general/
    .claude-plugin/plugin.json
    .codex-plugin/plugin.json
    skills/                            2 skills
    evals/                             claude plugin eval suite
```

A few rules keep both hosts working:

- Only `plugin.json` goes inside `.claude-plugin/` and `.codex-plugin/`. Skills, agents, hooks and other components sit at the plugin root.
- Marketplace entries point at `./plugins/evenbetter-ios` and `./plugins/evenbetter-general`.
- Each skill has a `SKILL.md` whose frontmatter `name` matches its folder name, plus optional `references/`, `scripts/` and `agents/openai.yaml`.
- Frontmatter uses only fields both hosts read: `name`, `description` and, when needed, `license`, `compatibility` and `metadata`. No skill names a model.
- Write skills so any agent can follow them. Refer to other skills by name, not by one host's slash syntax.
- Leave `version` out of the manifests until there is a release process.

[`AGENTS.md`](AGENTS.md) lists the checks to run before you open a pull request. `python3 scripts/check-skills.py` covers most of them: frontmatter, description length, broken paths and links, manifests, and the sync between the corpus and `index.json`. The same checks run in GitHub Actions, together with `claude plugin validate` and a Codex install in a throwaway home.

Each plugin also has an eval suite in `evals/`, run with `claude plugin eval`. Routing cases check that a plain request reaches the right skill, and behaviour cases run a skill on a small fixture app and grade what it leaves behind. They cost tokens, so CI does not run them. Run them by hand after you change a skill's description or stages, with a throwaway `CLAUDE_CONFIG_DIR` and `--no-publish`, as the Evals section of `AGENTS.md` shows.

## License and credits

EvenBetter is released under the [MIT License](LICENSE). Some skills are adapted from other open-source projects: the SwiftUI skills from OpenAI's `build-ios-apps` plugin and Thomas Ricouard's Dimillian/Skills, and `evenbetter-design` from Anthropic's `frontend-design` skill (Apache 2.0). [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) lists each source, its license and what changed.

## Documentation used

- [Claude Code: create a marketplace](https://code.claude.com/docs/en/plugins/create-marketplace)
- [Claude Code: plugin manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference)
- [Claude Code: skills](https://code.claude.com/docs/en/skills)
- [Claude Code: plugin evals](https://code.claude.com/docs/en/plugin-evals)
- [Codex and ChatGPT: plugins](https://learn.chatgpt.com/docs/plugins)
- [Codex and ChatGPT: package your plugin](https://developers.openai.com/plugins/build/plugins)
- [Codex and ChatGPT: build skills](https://learn.chatgpt.com/docs/build-skills)
- [Agent Skills specification](https://agentskills.io/specification)
