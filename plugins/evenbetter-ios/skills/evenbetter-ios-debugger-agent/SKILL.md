---
name: evenbetter-ios-debugger-agent
description: >-
  Builds the current iOS project, runs it on a simulator, drives its UI and reads screenshots, logs and debugger state
  to explain runtime behavior, through Xcode's MCP server, MobileBuildMCP or xcodebuild. Use when asked to run the
  app, tap through a flow, take a simulator screenshot, read console output or reproduce a crash. For accessibility or
  HIG audits, use evenbetter-analyze.
compatibility: >-
  macOS with Xcode and an iOS Simulator runtime. Uses the plugin's xcode MCP server (xcrun mcpbridge, Xcode 26.3 or
  later, project open in Xcode), MobileBuildMCP when the user has installed it, or xcodebuild and xcrun simctl.
---

# iOS debugger agent

This skill builds the current scheme, runs it on an iOS Simulator, drives the UI and reads logs and debugger state. The output is a short runtime report: what ran, what appeared on screen, the log lines that matter and the likely cause. It changes app code only when the user asks for a fix.

If current system, developer or user instructions conflict with this skill, follow them.

## Choose a tool path

Check which tools the session has, then take the first path that covers the step. Tool names below are the servers' own names. Each host adds its own prefix to MCP tools, so match on the name, not the prefix. Pass every setting the call needs (project, scheme, configuration, simulator) explicitly instead of relying on a server's defaults.

1. Xcode MCP server. The plugin registers it as `xcode`, launched with `xcrun mcpbridge`. It needs Xcode 26.3 or later with the project open, and Xcode > Settings > Intelligence > "Allow External Agents to Use Xcode Tools" set to Always or While Xcode is Open. Apple documents building the app as the baseline and publishes no fixed tool list, so read the tools the server reports and choose by what they do. On Xcode 27 it can also boot a simulator, install and launch the app, synthesize touches, take screenshots, report debugger run state and console output, list and switch schemes and run destinations, and read build settings, entitlements and Info.plist keys.
2. MobileBuildMCP (formerly XcodeBuildMCP). Use it when the user has it installed, or when the Xcode server lacks a step you need, such as UI automation on Xcode 26. The plugin does not bundle it. If it is missing, tell the user how to add it and let them decide: `brew tap getsentry/xcodebuildmcp && brew install mobilebuildmcp`, or `npx -y mobilebuildmcp@latest mcp` as the server command (Node 18 or later). It needs macOS 14.5 or later and Xcode 16 or later.
3. Shell. `xcodebuild` and `xcrun simctl` come with Xcode and cover building, installing, launching, screenshots and log streaming. They cannot tap or type, so for interaction ask the user to do it or move to an MCP path.

Apple's Xcode 27 agent skills may also be installed. `xcrun agent skills export` copies them out of Xcode for other agents, and third-party copies name one of them device-interaction. When it is present, follow it for how to call Apple's own tools, and use this skill for the fallback order and the debugging loop.

## Questions

Most runs need no questions. Ask only when the choice changes what gets built or booted: several app schemes, no booted simulator, or a build that fails before launch. Ask one closed question with numbered options and the recommended option first. In Claude Code use `AskUserQuestion`. In Codex use `request_user_input` in Plan mode, and a plain-text numbered question in Default mode. Other agents use their own question tool or a numbered plain-text question.

Codex Plan mode is read-only, and a build writes derived data, so in Plan mode list the steps you would run and ask the user to switch to Default mode before building.

## Workflow

Follow these steps in order unless the user asks for a narrower action.

### 1. Find the project and scheme

- Look for an `.xcworkspace` first, then an `.xcodeproj`. Use the workspace when both exist, because CocoaPods and some package setups only resolve through it.
- List the schemes through the Xcode server, the MobileBuildMCP `list_schemes` tool, or `xcodebuild -list`. If more than one app scheme fits the request, ask which one.

### 2. Pick a simulator

- Prefer a simulator that is already booted. List them with the MobileBuildMCP `list_sims` tool or `xcrun simctl list devices booted`.
- If none is booted, ask before booting one. Offer the newest iPhone simulator as the recommended option, another device, or stop. Boot the chosen one through the Xcode server on Xcode 27, the MobileBuildMCP `boot_sim` tool, or `xcrun simctl boot [UDID]`.

### 3. Set the configuration

- Use `Debug` unless the user names another configuration, and pass it on every build. Since MobileBuildMCP 2.7.0, an omitted configuration follows the scheme's Run action, which may not be Debug.
- MobileBuildMCP: call `session_set_defaults` once with `projectPath` or `workspacePath` (one of them), `scheme`, `configuration: "Debug"`, `simulatorId` (or `simulatorName`) and `bundleId` when known. Environment variables go in `env` as an array of `{ "key": "NAME", "value": "1" }` entries.
- Shell: `xcodebuild -workspace App.xcworkspace -scheme App -configuration Debug -destination "platform=iOS Simulator,id=[UDID]" -derivedDataPath build/DerivedData build`.

### 4. Build and launch

- Xcode server: build through it. On Xcode 27, install and launch with its simulator tools.
- MobileBuildMCP: `build_run_sim` builds, installs and launches, boots the simulator when needed, and returns the path of the runtime log file. For an app that is already built, use `launch_app_sim`, which also returns a log path. If the bundle id is unknown, call `get_sim_app_path`, then `get_app_bundle_id`.
- Shell: `xcrun simctl install booted [path to App.app]`, then `xcrun simctl launch --console-pty booted [bundle id]` to launch and stream the app's stdout and stderr.
- If the build fails, stop before any UI step. Report the first error with its file and line. Fix it only if the user asked for fixes. With MobileBuildMCP, retrying once with `preferXcodebuild: true` can get past a failure in its incremental build path.
- After launch, confirm the app is on screen with a screenshot or a UI snapshot before you interact with it.

### 5. Drive the UI

- MobileBuildMCP: call `snapshot_ui` first. It returns element refs. `tap`, `touch` and `type_text` each take an `elementRef` from the latest snapshot. Tap only refs whose targets list the tap action. `type_text` also takes `text` and an optional `replaceExisting`. Use `batch` for several taps on one screen with no check in between. After navigation, scrolling, a sheet or any layout change, take a new snapshot, because older refs may no longer resolve. `wait_for_ui` waits for an element to appear. `swipe`, `gesture`, `long_press`, `drag` and `key_press` cover the other inputs, and `set_sim_appearance` switches between light and dark mode.
- Xcode server on Xcode 27: use its touch and screenshot tools.
- Shell: `xcrun simctl io booted screenshot [file].png` captures the screen. It cannot tap.
- Save screenshots to a temporary directory, or to `.evenbetter/` in the user's project when another EvenBetter skill asked for the evidence.

### 6. Read logs, crashes and debugger state

- MobileBuildMCP: read the log file whose path `build_run_sim` or `launch_app_sim` returned. Its separate log-capture tools were removed in 2.5.0.
- Xcode server on Xcode 27: read the console and the debugger run state it reports.
- Shell: `xcrun simctl spawn booted log stream --level debug --predicate 'process == "App"'`, or filter on the app's `subsystem` when it uses `Logger`. Simulator crash reports land in `~/Library/Logs/DiagnosticReports/`.
- For LLDB, MobileBuildMCP has `debug_attach_sim`, then `debug_breakpoint_add`, `debug_continue`, `debug_stack`, `debug_variables` and `debug_lldb_command`.
- Quote only the lines that explain the behavior, with their timestamps.

### 7. Report

Say which tool path you used and what you ran, what appeared on screen (with screenshot paths), the relevant log lines, the likely cause with file and line, and the next step. If the user asked for a fix, make it, then rebuild and repeat the step that failed.

## Troubleshooting

- The Xcode tools do not appear: the project is not open in Xcode, or the Intelligence setting is Never. `claude mcp list` or `codex mcp list` shows whether the server connected.
- `xcrun mcpbridge` is not found: Xcode is older than 26.3, or `xcode-select -p` points at the Command Line Tools instead of Xcode.
- The build uses the wrong configuration: pass `configuration` explicitly.
- The wrong app launches: check the scheme and the bundle id.
- A tap fails or hits the wrong element: take a new `snapshot_ui` and use a ref from it.

## Related skills

- evenbetter-analyze audits a repository for HIG and accessibility issues and uses this skill for runtime screenshots. Send accessibility audits there.
- Hand runtime accessibility evidence to evenbetter-accessibility-tests. It runs Apple's accessibility audit in UI tests and, on Xcode 27, a VoiceOver walk, then records a verdict on each tested finding in the evenbetter-analyze report.
- evenbetter-ios-feature and evenbetter-ios-epic use this skill in their execution and review stages to check built screens.
