# EvenBetter Plugin Marketplace

EvenBetter Plugin Marketplace is a GitHub-hosted marketplace for distributing curated EvenBetter skills as installable plugins. The MVP ships `evenbetter-ios` for iOS product workflows, SwiftUI implementation, Apple HIG review, accessibility, analysis, validation, and remediation, plus `evenbetter-general` for platform-agnostic feature and epic workflows.

The marketplace currently targets both Claude Code and Codex. Both platforms install the same plugin payloads from `plugins/evenbetter-ios/skills/` and `plugins/evenbetter-general/skills/`; only the platform metadata files differ.

## Install in Claude Code

Add the marketplace:

```text
/plugin marketplace add MelloBirkan/EvenBetterFramework
```

Install the iOS plugin:

```text
/plugin install evenbetter-ios@evenbetter
```

Install the general workflow plugin:

```text
/plugin install evenbetter-general@evenbetter
```

Reload plugins in the current Claude Code session after installing or updating:

```text
/reload-plugins
```

Claude Code namespaces plugin skills by plugin name, so installed skills appear under names such as `/evenbetter-ios:evenbetter-ios-feature`, `/evenbetter-ios:evenbetter-swiftui-ui-patterns`, and `/evenbetter-general:evenbetter-general-feature`.

## Install in Codex

Add the marketplace:

```bash
codex plugin marketplace add MelloBirkan/EvenBetterFramework
```

Then install from Codex:

```text
Codex Desktop -> Plugins -> evenbetter -> evenbetter-ios -> Add to Codex
Codex Desktop -> Plugins -> evenbetter -> evenbetter-general -> Add to Codex
```

Or from the Codex CLI:

```text
codex
/plugins
```

In the plugin browser, choose the `evenbetter` marketplace, open `evenbetter-ios` or `evenbetter-general`, and select `Install plugin`.

After installation, start a new thread and either ask Codex directly or invoke the plugin or one of its bundled skills with `@`.

## Update

Claude Code:

```text
/plugin marketplace update evenbetter
/plugin update evenbetter-ios@evenbetter
/plugin update evenbetter-general@evenbetter
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
  evenbetter-general/
    .claude-plugin/
      plugin.json
    .codex-plugin/
      plugin.json
    skills/
      ...
  evenbetter-ios/
    .claude-plugin/
      plugin.json
    .codex-plugin/
      plugin.json
    skills/
      ...
```

The plugin content sources of truth are `plugins/evenbetter-ios/skills/` and `plugins/evenbetter-general/skills/`.

Do not maintain parallel copies of installable plugin skills under the repository root. If a skill should ship to users, edit it inside the matching `plugins/*/skills/` directory.

## Plugin Contents

`evenbetter-ios` contains:

- `evenbetter-ios-feature`
- `evenbetter-ios-epic`
- `evenbetter-ios-app-intents`
- `evenbetter-ios-debugger-agent`
- `evenbetter-swiftui-accessibility`
- `evenbetter-swiftui-liquid-glass`
- `evenbetter-swiftui-performance-audit`
- `evenbetter-swiftui-ui-patterns`
- `evenbetter-swiftui-view-refactor`

`evenbetter-general` contains:

- `evenbetter-general-feature`
- `evenbetter-general-epic`

## MVP Limitations

- Android distribution is intentionally omitted until Android-specific skills exist.
- The marketplace is a GitHub custom marketplace, not an official public Plugin Directory listing.
- Codex Desktop installs custom GitHub marketplaces after the marketplace has been added with `codex plugin marketplace add`.
- No commands, hooks, MCP servers, app connectors, LSP servers, monitors, themes, or visual assets are included in this MVP.
- The repository should be public for frictionless install. Private repositories only work for users whose local Git/Codex/Claude environment can authenticate to the repository.

## Maintainer Workflow

1. Edit installable skills in the matching plugin skill root:
   - iOS: `plugins/evenbetter-ios/skills/`
   - General: `plugins/evenbetter-general/skills/`
2. Keep platform-specific metadata in the platform manifest directories:
   - Claude Code: `plugins/evenbetter-ios/.claude-plugin/plugin.json`
   - Codex: `plugins/evenbetter-ios/.codex-plugin/plugin.json`
   - Claude Code: `plugins/evenbetter-general/.claude-plugin/plugin.json`
   - Codex: `plugins/evenbetter-general/.codex-plugin/plugin.json`
3. Keep marketplace entries pointed at plugin roots such as `./plugins/evenbetter-ios` and `./plugins/evenbetter-general`:
   - Claude Code: `.claude-plugin/marketplace.json`
   - Codex: `.agents/plugins/marketplace.json`
4. Keep plugin components at the plugin root. Do not put `skills/`, `commands/`, `agents/`, hooks, or other components inside `.claude-plugin/` or `.codex-plugin/`; only `plugin.json` belongs there.
5. Avoid host-specific invocation syntax inside skill instructions. Refer to bundled skills by stable skill name unless a platform format requires otherwise.
6. During active Claude Code development, keep `version` omitted unless adopting an explicit release process.

## Documentation Basis

- [Claude Code plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [Claude Code plugin manifest reference](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/plugin-structure/references/manifest-reference.md)
- [Codex plugins](https://developers.openai.com/codex/plugins/)
- [Build Codex plugins](https://developers.openai.com/codex/plugins/build)
