# 1-plan

Contents: Load the report, Check the environment, Find the UI test target, Map findings to screens, Plan the tests, Ask, Write the plan.

## Load the report

1. Find reports with `rg --files -uu -g 'evenbetter-analyze-report.html' .evenbetter`, leaving out `history/` folders. With more than one, ask which. The folder that holds the chosen report is `.evenbetter/[project]/` for the rest of the run.
2. With no report, ask: run evenbetter-analyze first (Recommended) / stop. This skill only annotates existing findings, so it has nothing to test without a report.
3. Make a temporary directory outside the project and the plugin folder with `mktemp -d`, written `[tmp]` in this skill, and extract the data into it: `python3 [script] extract [report] > [tmp]/data.json`. Without `python3`, read the HTML, find the exact prefix `const reportData = `, and walk forward from the first `{` with a brace counter that skips JSON string literals (only `"` opens and closes one) and the character after each backslash, until the counter returns to 0. The next character must be `;`. Parse that slice as JSON, and keep its start and end offsets for `4-record`.
4. Backfill a `runtime` block right after `repair` on every finding that lacks one, in the temporary file only. `4-record` writes the report.

```bash
python3 - [tmp]/data.json <<'EOF'
import json, sys
path = sys.argv[1]
data = json.load(open(path, encoding="utf-8"))
default = {"status": "untested", "checked_at": "", "configs": [], "tests": [],
           "evidence": "", "result_bundle": ""}
for i, issue in enumerate(data["issues"]):
    if "runtime" not in issue:
        items = list(issue.items())
        at = next((n + 1 for n, (key, _) in enumerate(items) if key == "repair"), len(items))
        items.insert(at, ("runtime", dict(default)))
        data["issues"][i] = dict(items)
json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
EOF
```

5. Run `python3 [script] check [tmp]/data.json`. If it reports problems, `4-record` could not write the verdicts, because `update` refuses data that fails the check. Ask: run evenbetter-validate first (Recommended) / write and run the tests now, and record verdicts in the results log only. Without `python3`, check by hand that `issues` is an array with unique `id`s and that each finding has `clause_id`, `related_clause_ids`, `file_path`, `line_number` and `repair`.
6. Note `workflow.state`, `scan_date`, `workflow.validated_at` and `workflow.repaired_at`. The plan records them, and `4-record` compares them before writing.
7. Choose the findings:
   - Normal run: every finding.
   - `recheck`: only findings whose `repair.status` is `applied`. Read their `repair.changed_files`, because a fix may have added or changed a label, an identifier or a route step. When it did, update the plan rows (including the `spoken` checks in "Plan the tests") and regenerate the files with `2-write` before `3-run`.
   - A finding is testable when its `clause_id` or one of its `related_clause_ids` has a row in the audit or walk tables of `references/audit-clause-map.md`. List the others as not testable, with their clauses.

## Check the environment

- `xcodebuild -version` gives the Xcode version. The audit needs Xcode 15 or later and an iOS 17 or later simulator. The VoiceOver walk needs Xcode 27 or later and an iOS 27 or later simulator, so with Xcode present, plan walk tests only when both are there.
- `xcrun simctl list devices available` lists simulators. Pick an iPhone on the newest iOS runtime, preferring one that is already booted, and note its UDID.
- When either command is missing (Linux, a container, or CI without Xcode), the run is write-only. Ask which Xcode the tests will run on: Xcode 27 or later (Recommended) / Xcode 15 to 26. The answer decides whether `2-write` writes the VoiceOver walk file.

## Find the UI test target

Search in this order and stop at the first hit:

1. `project.pbxproj` (with `rg -uu --files -g 'project.pbxproj'`): a target whose `productType` is `"com.apple.product-type.bundle.ui-testing"`. Note the target name and the folder its sources live in. If the target lists the folder under `fileSystemSynchronizedGroups` (Xcode 16 folders), new files in it join the target without any project edit. Otherwise the user adds the new folder to the target in Xcode after `2-write`.
2. XcodeGen `project.yml`: a target with `type: bundle.ui-testing`. Its `sources` give the folder. New files need `xcodegen generate`.
3. Tuist `Project.swift`: a target with `product: .uiTests`. Its `sources` glob gives the folder. New files need `tuist generate`.

A Swift package cannot host UI tests, so an app built only from `Package.swift` needs an Xcode project with a UI Testing Bundle first. With no UI test target, the folder is `[AppName]UITests/` at the project root, and the user creates a UI Testing Bundle that uses it.

Read the target's existing tests for launch helpers, launch arguments and accessibility identifiers that the new tests can reuse. Find the app scheme with `xcodebuild -list` when Xcode is present.

## Map findings to screens

For each testable finding:

1. **Screen.** `file_path` names the file. The screen is the top-level view the user sees with that code on it. A row view such as `PlantRow` belongs to the list screen that shows it. When the finding is about presented content, such as a sheet with no Cancel button flagged on its `.sheet` modifier, the screen is the presented view. Name the screen after the view without its `View` suffix (`PlantListView` is `PlantList`).
2. **Route.** Trace how the running app reaches the screen, starting at the `@main` App's `WindowGroup`, through `NavigationLink`, `navigationDestination`, `TabView` tabs, `.sheet`, `.fullScreenCover`, `.popover`, `.alert` and `.confirmationDialog`. Write each step as an XCUIElement query, preferring in this order:
   - an existing `accessibilityIdentifier`;
   - the visible label (`app.buttons["Save"]`, `app.staticTexts["Monstera"]`);
   - a structural query that matches one element, such as `app.navigationBars.buttons.firstMatch` when the bar has a single button;
   - otherwise the step is a gap. Adding an identifier is an app code change and needs a yes.
3. **State.** Note what the screen needs at launch: sample data, a signed-in user, a finished onboarding. Look for launch arguments the app already reads: `ProcessInfo.processInfo.arguments`, `CommandLine.arguments`, and `UserDefaults` keys, which a `-key value` launch argument sets.
4. **Route gaps.** A screen is unreachable when no route leads to it, for example a `NavigationLink(value:)` with no matching `navigationDestination`, or when it needs state the app cannot be launched into. That is often a finding in itself. The tests can still reach it through a DEBUG-only launch argument, which `2-write` shows as a diff.
5. **Anchor.** Pick one element that proves the screen is up, such as a title or a row label from sample data.
6. **Element.** Write down how the finding's element appears to UI tests: its identifier, or its label (a `Text` string, a `Button` title, an `accessibilityLabel`). For a label built from data, write `*` for the changing part, as in `Every * days` for `Text("Every \(plant.wateringIntervalDays) days")`. Give alternatives with ` | ` (written `\|` inside a table) when the runtime label is uncertain. An icon without a label may be spoken as the SF Symbol's usual meaning instead of its name, so `Image(systemName: "trash")` gets `trash | Delete` and `plus` gets `plus | Add`. Leave the element empty when the code gives nothing to match. Walk checks take plain text without `*`, so give them a constant part of the label.
7. **Below the fold.** The audit sees only elements on screen. When the element is not visible at launch on an iPhone, add a scroll step. A clean audit refutes a finding only when the element was on screen, which `4-record` checks on the test's screenshot.

## Plan the tests

- **Audit tests**: one per screen and configuration. A test carries every testable finding on its screen whose map rows include that configuration. Its `failOn` types are the union of those rows' audit types. Name it `test_[Screen]_[config]`, with `standard`, `AX5`, `dark`, `IncreaseContrast` or `RTL` as the suffix, for example `test_PlantList_AX5`. Leave out a screen and configuration that would carry no finding.
- **Walk tests** (Xcode 27 or later only): one per screen with at least one walk check, named `test_[Screen]_VoiceOver`. Write each check with the finding IDs it serves, using the check names from the map. A `silent` check may also guard a correct pattern with no finding, such as a decorative image already hidden with `accessibilityHidden(true)`. That check should pass.
- In `recheck` mode, add a `spoken` check for each applied fix that added a label, using the label from `repair.changed_files` and the finding's `recommended_fix` or `minimal_fix`.
- Test method names are unique across the test classes, because `4-record` keys results on them.
- Each test lists its finding IDs, so `4-record` can map results back without guessing.

## Ask

Use closed questions with the recommended option first, at most three at once:

1. Test target, when one exists: use `[target]` and its folder `[folder]` (Recommended) / stop. When none exists: write the files into `[AppName]UITests/` now, and I'll add a UI Testing Bundle in Xcode (Recommended) / stop. With no target, the reply gives the steps: in Xcode choose File, New, Target, UI Testing Bundle, then add the folder to it.
2. Xcode version, only in write-only mode: Xcode 27 or later (Recommended) / Xcode 15 to 26.
3. Screens: every screen with a testable finding (Recommended) / only screens with critical or high findings.
4. Configurations: standard, AX5 and dark mode (Recommended) / also Increase Contrast and right-to-left / standard only.
5. Route gaps, one question per gap:
   - The app already has a launch argument that opens the screen or sets the state: use `[argument]` (Recommended) / leave this screen's findings untested.
   - It has none: add a DEBUG-only launch argument that opens `[Screen]`, shown as a diff first (Recommended) / leave this screen's findings untested.
6. After the run: keep the tests as a regression suite (Recommended) / delete them once the verdicts are recorded.

Findings the answers leave out (a screen not chosen, a gap left open) stay `untested`, and the plan says why.

## Write the plan

Create `.evenbetter/[project]/evenbetter-accessibility-tests.md` if it does not exist, starting with `# EvenBetter accessibility tests: [project_name]`. Replace its `## Plan` section on each new plan, and keep every `## Results` section below it. The plan holds:

- Plan time, report path, `workflow.state`, `scan_date`, `validated_at` and `repaired_at`.
- Environment: Xcode version and simulator, or "write-only, for Xcode [answer]".
- UI test target, test folder, scheme, and how new files join the target (Xcode 16 folder, user adds them, `xcodegen generate` or `tuist generate`).
- Configurations, and the launch arguments for route gaps.
- App code changes: each proposed launch argument or identifier, with its file and whether the user accepted it. `2-write` fills in the answer.
- An audit test table:

| Test | Findings | Screen | Route | Anchor | failOn | Config | Elements |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `test_PlantList_dark` | EB-012, EB-023 | PlantList | launch | `staticTexts["Monstera"]` | contrast | dark | EB-012, EB-023: `Every * days` |

- A walk test table with columns Test, Screen, Route, Checks, where each check reads like `button(Water now): EB-008`.
- Not testable: finding, clauses, and the reason from the map.
- Untested: finding and reason, such as a screen not chosen or a route gap left open.
