# EvenBetter General

EvenBetter General is a pair of agent skills for Claude Code and Codex that plan software work before any code exists. They interview you with closed questions, write a plan you can review, check it, break it into tickets and guide the implementation. They work for any platform; for iOS and SwiftUI, the EvenBetter iOS plugin has the same workflow with Apple's design and accessibility guidelines built in.

| Skill | Use it for |
| --- | --- |
| `evenbetter-general-feature` | One feature or a narrow change: plan, plan validation, tickets, execution and implementation review. |
| `evenbetter-general-epic` | A larger initiative: epic brief, core flows, PRD and architecture validation, tech plan, tickets and execution. |

Both skills write plain Markdown to `.evenbetter/` in your project, plus one self-contained HTML file for an epic's core flows, so you can read, edit and commit every artifact. They need no MCP servers.

## Install

Claude Code 2.1.275 or later adds the marketplace and installs the plugin in one step:

```text
/plugin install evenbetter-general --marketplace MelloBirkan/EvenBetterFramework
```

From a terminal, run `claude plugin install evenbetter-general --marketplace MelloBirkan/EvenBetterFramework`. In Codex:

```bash
codex plugin marketplace add MelloBirkan/EvenBetterFramework
codex plugin add evenbetter-general@evenbetter
```

The [repository README](https://github.com/MelloBirkan/EvenBetterFramework#readme) has the full guide.

## License

MIT, see [LICENSE](LICENSE).
