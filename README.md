# EvenBetter Claude Code Marketplace

EvenBetter Claude Code Marketplace is a GitHub-hosted plugin marketplace for distributing platform-specific EvenBetter skills through Claude Code. The MVP currently ships only the iOS plugin under the `evenbetter` marketplace name.

## Install

Add the marketplace:

```text
/plugin marketplace add MelloBirkan/evenbetter-claude-marketplace
```

Install the iOS plugin:

```text
/plugin install evenbetter-ios@evenbetter
```

After installing, reload plugins in the current Claude Code session:

```text
/reload-plugins
```

Claude Code namespaces plugin skills by plugin name. For example, the iOS plugin exposes skills with names like `/evenbetter-ios:evenbetter-ios-feature` and `/evenbetter-ios:swiftui-ui-patterns`.

## Update

Refresh the marketplace catalog:

```text
/plugin marketplace update evenbetter
```

Claude Code can also auto-update marketplaces and installed plugins at startup when auto-update is enabled for the marketplace. If plugins are updated during a running session, use:

```text
/reload-plugins
```

This MVP intentionally omits explicit `version` fields from `marketplace.json` plugin entries and plugin manifests. Claude Code resolves the plugin version from the git commit SHA when no explicit version is set, so every marketplace commit can be treated as a new development version.

## Plugins

### `evenbetter-ios`

Contains the current iOS-focused EvenBetter skill set:

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

The source skill packages remain in the repository's original `skills/` tree. The plugin copies live under `plugins/evenbetter-ios/skills/` so Claude Code can install them as a self-contained plugin. Repo-local `agents/openai.yaml` helper metadata is intentionally not shipped in the Claude Code plugin copy.

## MVP Limitations

- Android distribution is intentionally omitted from this MVP until Android-specific skills exist.
- The marketplace currently uses local plugin paths, which require adding the marketplace from a git repository or local directory. Direct URL-based marketplace installation is not suitable for these relative plugin paths.
- No commands, agents, hooks, MCP servers, LSP servers, monitors, or themes are declared for this MVP.
- iOS skills were copied from the current repository state; maintainers should keep the plugin copy synchronized when source skills change.

## Maintainer Workflow

1. Add or update source skills in the main `skills/` tree.
2. Copy platform-specific skill directories into the matching plugin under `plugins/<plugin-name>/skills/`, excluding repo-local single-agent helper metadata that is not part of the Claude Code plugin format.
3. Keep plugin components at the plugin root. Do not put `skills/`, `commands/`, `agents/`, hooks, or other components inside `.claude-plugin/`; only `plugin.json` belongs there.
4. Add new plugin entries to `.claude-plugin/marketplace.json` with a kebab-case name and a local `./plugins/<plugin-name>` source path.
5. Keep `version` omitted during active development unless a release process needs semantic version pinning.
6. Validate with:

```bash
claude plugin validate .
claude --plugin-dir ./plugins/evenbetter-ios
```

## Documentation Basis

This marketplace follows the current Claude Code documentation for plugin marketplaces, plugin manifests, skill placement, local relative plugin sources, validation, and git-SHA version resolution:

- [Create and distribute a plugin marketplace](https://docs.anthropic.com/en/docs/claude-code/plugin-marketplaces)
- [Create plugins](https://docs.anthropic.com/en/docs/claude-code/plugins)
- [Plugins reference](https://docs.anthropic.com/en/docs/claude-code/plugins-reference)
- [Discover and install prebuilt plugins](https://docs.anthropic.com/en/docs/claude-code/discover-plugins)
