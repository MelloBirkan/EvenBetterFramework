# EvenBetter Plugin Marketplace

EvenBetter Plugin Marketplace is a GitHub-hosted marketplace for distributing curated EvenBetter skills as installable plugins. The MVP ships one plugin, `evenbetter-ios`, for iOS product workflows, SwiftUI implementation, Apple HIG review, accessibility, analysis, validation, and remediation.

The marketplace currently targets both Claude Code and Codex. Both platforms install the same plugin payload from `plugins/evenbetter-ios/skills/`; only the platform metadata files differ.

## Install in Claude Code

Add the marketplace:

```text
/plugin marketplace add MelloBirkan/EvenBetterFramework
```

Install the iOS plugin:

```text
/plugin install evenbetter-ios@evenbetter
```

Reload plugins in the current Claude Code session after installing or updating:

```text
/reload-plugins
```

Claude Code namespaces plugin skills by plugin name, so installed skills appear under names such as `/evenbetter-ios:evenbetter-ios-feature` and `/evenbetter-ios:swiftui-ui-patterns`.

## Install in Codex

Add the marketplace:

```bash
codex plugin marketplace add MelloBirkan/EvenBetterFramework
```

Then install from Codex:

```text
Codex Desktop -> Plugins -> evenbetter -> evenbetter-ios -> Add to Codex
```

Or from the Codex CLI:

```text
codex
/plugins
```

In the plugin browser, choose the `evenbetter` marketplace, open `evenbetter-ios`, and select `Install plugin`.

After installation, start a new thread and either ask Codex directly or invoke the plugin or one of its bundled skills with `@`.

## Update

Claude Code:

```text
/plugin marketplace update evenbetter
/plugin update evenbetter-ios@evenbetter
/reload-plugins
```

Codex:

```bash
codex plugin marketplace upgrade evenbetter
```

Then reopen Codex or the plugin browser if the updated marketplace does not appear immediately.

For the Claude Code marketplace, this MVP intentionally omits explicit `version` fields from the marketplace entry and plugin manifest. Claude Code resolves the plugin version from the git commit SHA when no explicit version is set, so every marketplace commit can be treated as a new development version. Codex documentation currently describes marketplace refresh and plugin cache behavior, but does not document the same git-SHA fallback contract; keep Codex updates tied to `codex plugin marketplace upgrade` until a formal release/versioning policy is added.

## Repository Layout

```text
.claude-plugin/
  marketplace.json
.agents/
  plugins/
    marketplace.json
plugins/
  evenbetter-ios/
    .claude-plugin/
      plugin.json
    .codex-plugin/
      plugin.json
    skills/
      ...
```

The plugin content source of truth is `plugins/evenbetter-ios/skills/`.

Do not maintain a parallel copy of installable iOS plugin skills under the repository root. If a skill should ship to users, edit it inside `plugins/evenbetter-ios/skills/`.

## Plugin Contents

`evenbetter-ios` contains:

- `evenbetter-ios-feature`
- `evenbetter-ios-epic`
- `evenbetter-ios-analyze`
- `evenbetter-validate`
- `evenbetter-fix`
- `ios-app-intents`
- `ios-debugger-agent`
- `swiftui-accessibility`
- `swiftui-liquid-glass`
- `swiftui-performance-audit`
- `swiftui-ui-patterns`
- `swiftui-view-refactor`

## MVP Limitations

- Android distribution is intentionally omitted until Android-specific skills exist.
- The marketplace is a GitHub custom marketplace, not an official public Plugin Directory listing.
- Codex Desktop installs custom GitHub marketplaces after the marketplace has been added with `codex plugin marketplace add`.
- No commands, hooks, MCP servers, app connectors, LSP servers, monitors, themes, or visual assets are included in this MVP.
- The repository should be public for frictionless install. Private repositories only work for users whose local Git/Codex/Claude environment can authenticate to the repository.

## Maintainer Workflow

1. Edit installable iOS skills in `plugins/evenbetter-ios/skills/`.
2. Keep platform-specific metadata in the platform manifest directories:
   - Claude Code: `plugins/evenbetter-ios/.claude-plugin/plugin.json`
   - Codex: `plugins/evenbetter-ios/.codex-plugin/plugin.json`
3. Keep marketplace entries pointed at `./plugins/evenbetter-ios`:
   - Claude Code: `.claude-plugin/marketplace.json`
   - Codex: `.agents/plugins/marketplace.json`
4. Keep plugin components at the plugin root. Do not put `skills/`, `commands/`, `agents/`, hooks, or other components inside `.claude-plugin/` or `.codex-plugin/`; only `plugin.json` belongs there.
5. Avoid host-specific invocation syntax inside skill instructions. Refer to bundled skills by stable skill name unless a platform format requires otherwise.
6. During active Claude Code development, keep `version` omitted unless adopting an explicit release process.

## Documentation Basis

- [Claude Code plugin marketplaces](https://docs.anthropic.com/en/docs/claude-code/plugin-marketplaces)
- [Claude Code plugins reference](https://docs.anthropic.com/en/docs/claude-code/plugins-reference)
- [Codex plugins](https://developers.openai.com/codex/plugins/)
- [Build Codex plugins](https://developers.openai.com/codex/plugins/build)
