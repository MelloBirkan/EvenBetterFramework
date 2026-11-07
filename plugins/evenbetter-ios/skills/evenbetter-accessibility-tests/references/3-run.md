# 3-run

Contents: Write-only mode, Pick the runner, Run the tests, Increase Contrast, While it runs, Failures, Results to read.

## Write-only mode

With no `xcodebuild` or no simulator, nothing runs here. Print the commands from "Run the tests" and "Increase Contrast" with every placeholder filled in that the project gives, and say they have to run on a Mac with Xcode, from the project root. For the destination, use `-destination 'platform=iOS Simulator,name=[iPhone name]'` and tell the user to pick a name from `xcrun simctl list devices available`. For the timestamp, start the block with `stamp=$(date +%Y%m%d-%H%M%S)` and write `$stamp` where the commands say `[stamp]`. Include `xcodegen generate` or `tuist generate` first when the project needs it. Then go to `4-record`, which leaves every verdict `untested`.

## Pick the runner

1. `xcodebuild` in the shell. Prefer it, because `4-record` needs the full console output with the `EB-` marker lines.
2. When the shell cannot run `xcodebuild` but the session has Xcode's MCP server or MobileBuildMCP, use that server's test tool on the UI test target. Xcode's server is reached through `xcrun mcpbridge` (Xcode 26.3 or later, with the project open in Xcode); Xcode 27 also previews `xcrun mcp-server`, which runs without an open workspace. List the server's tools first, because the names change between releases. Pass the same `-only-testing` filters (MobileBuildMCP takes extra `xcodebuild` arguments), and save the tool's complete output as the log. If the output lacks the `EB-` lines, read them from the result bundle as "Results to read" describes.

## Run the tests

Pick the timestamp `[stamp]` once, from `date +%Y%m%d-%H%M%S`, and write it out in every command of this run, because shell variables may not survive between tool calls. `checked_at` in `4-record` is the same moment, written `YYYY-MM-DD HH:MM:SS`.

1. Find the scheme with `xcodebuild -list` (`-workspace [App].xcworkspace` when the project has a workspace, otherwise `-project [App].xcodeproj`). For an XcodeGen or Tuist project whose `project.pbxproj` does not list every file in `EvenBetterAccessibility/` yet, ask the regeneration question from `2-write` first, unless `2-write` regenerated it in this run. When nobody can answer, leave the project as it is and follow Write-only mode above.
2. Boot the simulator if it is not booted: `xcrun simctl boot [udid]`. An "already booted" error is fine.
3. Run the audit and walk classes on one line. Leave out the walk filter when `2-write` wrote no walk file:

```bash
mkdir -p .evenbetter/[project]/runtime && set -o pipefail && xcodebuild test -project [App].xcodeproj -scheme [Scheme] -destination 'platform=iOS Simulator,id=[udid]' -only-testing:[UITarget]/EBAccessibilityAuditTests -only-testing:[UITarget]/EBVoiceOverWalkTests -resultBundlePath .evenbetter/[project]/runtime/[stamp].xcresult 2>&1 | tee .evenbetter/[project]/runtime/[stamp].log
```

- With a workspace, write `-workspace [App].xcworkspace` in place of `-project [App].xcodeproj`, here and in "Increase Contrast".
- `-only-testing:[UITarget]/[Class]/[test]` narrows the run to single tests. In `recheck` mode, pass one per test that carries an applied finding.
- Parallel testing can keep `print` output out of the console log. Run `xcodebuild -help` and, when it lists `-parallel-testing-enabled`, add `-parallel-testing-enabled NO` to the command. This flag is not on an Apple documentation page, so check it on the installed Xcode.
- If `xcodebuild` says the scheme has no test action, or the UI test target is not in it, ask: I'll add the UI test target to the scheme's Test action in Xcode (Recommended) / stop.

4. Write `.evenbetter/[project]/runtime/.gitignore` with the line `*.xcresult` if it does not exist, because result bundles are large. Logs stay small enough to keep.

## Increase Contrast

Run this only when the plan has `_IncreaseContrast` tests. The setting is not a launch argument and changes the whole simulator, so it gets its own run.

1. Run `xcrun simctl help ui`. The `simctl ui` options are not on an Apple documentation page. Use only what this help lists, with the value words it prints. If it has no `increase_contrast` option, record the configuration as not run and skip the rest.
2. `xcrun simctl ui [udid] increase_contrast enabled`, with `enabled` replaced by the help's word for on if it differs.
3. Run the contrast class alone, with its own log:

```bash
set -o pipefail && xcodebuild test -project [App].xcodeproj -scheme [Scheme] -destination 'platform=iOS Simulator,id=[udid]' -only-testing:[UITarget]/EBIncreaseContrastTests -resultBundlePath .evenbetter/[project]/runtime/[stamp]-contrast.xcresult 2>&1 | tee .evenbetter/[project]/runtime/[stamp]-contrast.log
```

4. `xcrun simctl ui [udid] increase_contrast disabled` (or the help's word for off), also when the run failed, so the simulator goes back to normal.

## While it runs

UI tests take minutes. Run them in the background when the host allows it, and poll the end of the log until `xcodebuild` exits. Do not start a second run on the same simulator meanwhile.

## Failures

- Build error in the generated test files: show the first error, then ask: show the error and stop (Recommended) / fix the test code only and retry once. A retry may change only files in `EvenBetterAccessibility/`, and never a check, a label or a `failOn` set.
- Build error in app code: stop and show it. Repairing app code belongs to evenbetter-repair.
- The simulator does not boot, or no simulator matches: stop, and print the commands as in write-only mode.
- An app crash, a route failure or a skipped test: let the run finish. `4-record` marks the affected findings `inconclusive`.

## Results to read

- The `.log` files: `EB-AUDIT`, `EB-AUDIT-DONE`, `EB-ROUTE-FAIL` and `EB-VO` lines, and XCTest's `Test Case '...' passed`, `failed` or `skipped` lines.
- The `.xcresult` bundles hold the screenshots each test attached, and the console output. When a log has test case lines but no `EB-` lines, read the console output from the bundle: `xcrun xcresulttool help get log` shows the options on this Xcode. `xcrun xcresulttool get test-results tests --path [bundle]` lists each test's result. These subcommands came with Xcode 16, as the Xcode 16.3 release notes say. Before Xcode 16 the form is `xcrun xcresulttool get --path [bundle]`, which later versions mark as deprecated and accept with `--legacy`.
- To look at screenshots, `xcrun xcresulttool help export attachments` shows how to export them from the bundle.
