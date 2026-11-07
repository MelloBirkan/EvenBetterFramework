# EvenBetter iOS

EvenBetter iOS is a set of agent skills for Claude Code and Codex that plan SwiftUI apps, audit them against Apple's Human Interface Guidelines (HIG) and WCAG 2.2, and fix what the audit finds. Decisions about product copy, navigation and visual design stay with you: the skills ask closed questions instead of guessing.

The full guide lives in the [repository README](https://github.com/MelloBirkan/EvenBetterFramework#readme).

## Install

Claude Code 2.1.275 or later adds the marketplace and installs the plugin in one step:

```text
/plugin install evenbetter-ios --marketplace MelloBirkan/EvenBetterFramework
```

From a terminal, run `claude plugin install evenbetter-ios --marketplace MelloBirkan/EvenBetterFramework`. In Codex:

```bash
codex plugin marketplace add MelloBirkan/EvenBetterFramework
codex plugin add evenbetter-ios@evenbetter
```

## Skills

| Group | Skills |
| --- | --- |
| Planning | `evenbetter-ios-feature` for one screen, `evenbetter-ios-epic` for a multi-screen flow or a new app |
| Audit | `evenbetter-analyze` writes the report, `evenbetter-validate` checks it, `evenbetter-repair` applies the validated fixes, `evenbetter-accessibility-tests` confirms findings at runtime with XCUITest audits |
| SwiftUI | `evenbetter-swiftui-accessibility`, `evenbetter-swiftui-ui-patterns`, `evenbetter-swiftui-view-refactor`, `evenbetter-swiftui-performance-audit`, `evenbetter-swiftui-liquid-glass`, `evenbetter-ios-haptics`, `evenbetter-ios-app-intents`, `evenbetter-design`, `evenbetter-ios-debugger-agent` |
| Product and launch | `evenbetter-app-opportunity-research`, `evenbetter-app-launcher`, `evenbetter-accessibility-nutrition-labels` |

The audit skills read the corpus in [`corpus/`](corpus/): 61 clauses traced to Apple and W3C pages, each with a check, a reason and correct SwiftUI code.

## What it needs

- Planning, auditing and repair need nothing else. The skills read your Swift files and write their artifacts to `.evenbetter/` in your project.
- Optional: the plugin registers Xcode's MCP bridge (`xcrun mcpbridge`) as a server named `xcode`. It needs Xcode 26.3 or later, running, with "Allow External Agents to Use Xcode Tools" switched on in Xcode's Intelligence settings. See [Giving external agents access to Xcode](https://developer.apple.com/documentation/xcode/giving-external-agents-access-to-xcode).
- Optional: [MobileBuildMCP](https://github.com/getsentry/MobileBuildMCP) (formerly XcodeBuildMCP), which `evenbetter-ios-debugger-agent` falls back to when the Xcode server is not available. You install it yourself.
- `evenbetter-accessibility-tests` runs its tests on a Mac with Xcode. The iOS 27 VoiceOver walk needs Xcode 27.

## License

MIT, see [LICENSE](LICENSE). Some skills are adapted from other projects; [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) lists them and their licenses.
