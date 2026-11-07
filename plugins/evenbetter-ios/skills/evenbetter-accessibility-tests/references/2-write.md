# 2-write

Contents: Files, Before writing, Support file, Allowlist, Audit tests, VoiceOver walk, Route arguments in app code, After writing, Rules for generated code.

## Files

Write into `[UITestFolder]/EvenBetterAccessibility/`, where `[UITestFolder]` is the folder chosen in `1-plan`:

| File | Holds | Written when |
| --- | --- | --- |
| `EBAccessibilitySupport.swift` | Launch configurations, route steps, the audit runner and the marker lines | always |
| `EBAccessibilityAllowlist.swift` | Accepted issues, one reason each | only if it does not exist yet |
| `EBAccessibilityAuditTests.swift` | One audit test per screen and configuration, except Increase Contrast | always |
| `EBIncreaseContrastTests.swift` | The `_IncreaseContrast` audit tests | only when that configuration is planned |
| `EBVoiceOverWalkTests.swift` | The walk tests and the walk support | only for Xcode 27 or later |

The walk lives in its own file because `XCUIVoiceOverService` does not exist in older SDKs, and `#available` checks the iOS version at run time but cannot hide a symbol the compiler does not know. The Increase Contrast tests have their own class so `3-run` can run them alone while the setting is on.

The allowlist is the one file the team edits by hand, so a later run keeps it. The other files are regenerated from the plan and replaced on each run of this stage.

## Before writing

Show the file list with each test name and its findings, then ask once:

- With no app code change planned: write the files (Recommended) / show the code only.
- With an app code change from "Route arguments in app code": show its diff first, then ask: write the test files and apply the app change (Recommended) / write the test files only and leave [Screen] untested / show the code only.

In "show the code only", print the files and stop, because `3-run` and `4-record` then have nothing to run. Leave out the tests of a screen whose app change was declined, and list its findings as untested in the plan.

## Support file

`EBAccessibilitySupport.swift`, written as is:

```swift
// EvenBetter accessibility tests: launch configurations, route steps, the audit runner
// and the marker lines that evenbetter-accessibility-tests reads back from the test log.
import XCTest

enum EBConfig: String {
    case standard, ax5, dark, increaseContrast, rtl
}

@MainActor
enum EBLaunch {
    /// English keeps VoiceOver's trait words, such as "button", predictable for the walk checks.
    static let baseArguments = ["-AppleLanguages", "(en)", "-AppleLocale", "en_US"]
    private static var originalAppearance: XCUIDevice.Appearance?

    static func app(_ config: EBConfig, arguments: [String] = []) -> XCUIApplication {
        if originalAppearance == nil { originalAppearance = XCUIDevice.shared.appearance }
        let app = XCUIApplication()
        app.launchArguments = baseArguments + arguments
        switch config {
        case .ax5:
            // Common practice rather than documented API: the largest accessibility text size for this launch.
            app.launchArguments += ["-UIPreferredContentSizeCategoryName", "UICTContentSizeCategoryAccessibilityXXXL"]
        case .rtl:
            // Right-to-left layout, from Apple's internationalization testing guide.
            app.launchArguments += ["-AppleTextDirection", "YES"]
        case .standard, .dark, .increaseContrast:
            break
        }
        // Increase Contrast has no launch argument. 3-run turns it on with simctl around those tests.
        XCUIDevice.shared.appearance = config == .dark ? .dark : .light
        return app
    }

    /// Puts the simulator back in the appearance it had before the first EvenBetter test.
    static func restoreAppearance() {
        if let originalAppearance { XCUIDevice.shared.appearance = originalAppearance }
    }
}

@MainActor
struct EBRoute {
    let app: XCUIApplication
    let test: String

    /// Waits up to 10 seconds for the element, then taps it unless `tap` is false.
    /// A missing element prints EB-ROUTE-FAIL, so the test reads as inconclusive instead of passing.
    func step(_ name: String, _ element: XCUIElement, tap: Bool = true) -> Bool {
        guard element.waitForExistence(timeout: 10) else {
            print("EB-ROUTE-FAIL \(test) \(name)")
            XCTFail("EvenBetter route step not found: \(name)")
            return false
        }
        if tap { element.tap() }
        return true
    }

    /// Scrolls one screen down. The audit only sees elements that are on screen.
    func swipeUp() -> Bool {
        app.swipeUp()
        return true
    }
}

struct EBIssue: Encodable {
    let test: String
    let config: String
    let findings: [String]
    let auditType: String
    let fails: Bool
    let allowlisted: Bool
    let summary: String
    let detail: String
    let label: String
    let identifier: String
}

@MainActor
enum EBAudit {
    static let typeNames: [(XCUIAccessibilityAuditType, String)] = [
        (.contrast, "contrast"), (.dynamicType, "dynamicType"), (.elementDetection, "elementDetection"),
        (.hitRegion, "hitRegion"), (.sufficientElementDescription, "sufficientElementDescription"),
        (.textClipped, "textClipped"), (.trait, "trait"), (.action, "action"), (.parentChild, "parentChild"),
    ]

    static func name(of type: XCUIAccessibilityAuditType) -> String {
        let names = typeNames.filter { type.contains($0.0) }.map { $0.1 }
        return names.isEmpty ? "other(\(type.rawValue))" : names.joined(separator: "+")
    }

    /// Launches the app, follows the route, then audits the screen.
    static func screen(_ testCase: XCTestCase, test: String, config: EBConfig, arguments: [String] = [],
                       findings: [String], failOn: XCUIAccessibilityAuditType,
                       route: (EBRoute) -> Bool) throws {
        let app = EBLaunch.app(config, arguments: arguments)
        defer { EBLaunch.restoreAppearance() }
        app.launch()
        guard route(EBRoute(app: app, test: test)) else { return }
        attachScreenshot(app, in: testCase, name: "\(test) \(config.rawValue)")
        try run(app, test: test, config: config, findings: findings, failOn: failOn)
    }

    /// Audits every type. The test fails only on `failOn` types that are not allowlisted;
    /// every other issue is printed as a lead and ignored.
    static func run(_ app: XCUIApplication, test: String, config: EBConfig,
                    findings: [String], failOn: XCUIAccessibilityAuditType) throws {
        var count = 0
        try app.performAccessibilityAudit(for: .all) { issue in
            count += 1
            let label = issue.element?.label ?? ""
            let identifier = issue.element?.identifier ?? ""
            let type = name(of: issue.auditType)
            let allowlisted = EBAllowlist.allows(type: type, label: label, identifier: identifier)
            let fails = !failOn.isDisjoint(with: issue.auditType) && !allowlisted
            emit("EB-AUDIT", EBIssue(test: test, config: config.rawValue, findings: findings,
                                     auditType: type, fails: fails, allowlisted: allowlisted,
                                     summary: issue.compactDescription, detail: issue.detailedDescription,
                                     label: label, identifier: identifier))
            // true ignores the issue, false reports it as a test failure.
            return !fails
        }
        print("EB-AUDIT-DONE \(test) \(config.rawValue) issues=\(count)")
    }

    static func emit<T: Encodable>(_ marker: String, _ value: T) {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.sortedKeys, .withoutEscapingSlashes]
        guard let data = try? encoder.encode(value), let line = String(data: data, encoding: .utf8) else { return }
        print("\(marker) \(line)")
    }

    static func attachScreenshot(_ app: XCUIApplication, in testCase: XCTestCase, name: String) {
        let shot = XCTAttachment(screenshot: app.screenshot())
        shot.name = name
        shot.lifetime = .keepAlways
        testCase.add(shot)
    }
}
```

Notes:

- `-AppleTextDirection YES` comes from Apple's archived guide "Testing Your Internationalized App". `-UIPreferredContentSizeCategoryName` is common practice that Apple does not document. When a run shows AX5 screenshots at the normal text size, the argument did not take effect: record the AX5 results as `inconclusive` and say so in the log. Recent simulators may also offer `xcrun simctl ui [udid] content_size`, which `3-run` checks with `xcrun simctl help ui`.
- `XCUIDevice.shared.appearance` sets the appearance for every app on the simulator. Apple's example saves the previous value before setting a new one; the support file does the same, sets it before each launch, and puts it back when the test ends.
- In the audit handler, returning `true` ignores an issue and `false` reports it as a test failure, as Apple's WWDC23 session describes.

## Allowlist

`EBAccessibilityAllowlist.swift`, written only when it does not exist:

```swift
// EvenBetter accessibility tests: audit issues the team accepted.
// Add an entry only after the team agrees, with a one-line reason. 4-record lists every allowlisted issue.
enum EBAllowlist {
    struct Entry {
        let type: String        // the audit type as EBAudit prints it, for example "contrast"
        let label: String       // matched when identifier is empty
        let identifier: String  // preferred when the element has one
        let reason: String
    }

    static let entries: [Entry] = [
        // Entry(type: "contrast", label: "Sponsored", identifier: "", reason: "Accepted: third-party ad view we cannot restyle."),
        // Entry(type: "contrast", label: "Today", identifier: "", reason: "False positive: white on the dark photo checks out at 7:1."),
    ]

    static func allows(type: String, label: String, identifier: String) -> Bool {
        entries.contains { entry in
            entry.type == type && (entry.identifier.isEmpty ? entry.label == label : entry.identifier == identifier)
        }
    }
}
```

`type` is the audit type as the `EB-AUDIT` line prints it. When an issue covers several types, the name joins them with `+`, and the entry has to match that whole name.

The reason says whether the team accepts a real issue or judges it a false positive, as in Apple's WWDC23 example of a contrast issue that checked out fine. `4-record` reads it: an accepted issue still confirms its finding, and a false positive leaves the finding inconclusive.

## Audit tests

`EBAccessibilityAuditTests.swift` holds one method per audit row of the plan. This example shows a plain launch and a screen opened with a launch argument:

```swift
// EvenBetter accessibility tests: performAccessibilityAudit per screen and configuration.
// Plan: .evenbetter/plant-care/evenbetter-accessibility-tests.md
import XCTest

final class EBAccessibilityAuditTests: XCTestCase {
    // EB-012, EB-023 (PlantListView.swift)
    @MainActor
    func test_PlantList_dark() throws {
        try EBAudit.screen(self, test: "test_PlantList_dark", config: .dark,
                           findings: ["EB-012", "EB-023"], failOn: [.contrast]) { r in
            r.step("list loaded", r.app.staticTexts["Monstera"], tap: false)
        }
    }

    // EB-001, EB-002, EB-005, EB-008, EB-011, EB-019, EB-020 (PlantDetailView.swift)
    @MainActor
    func test_PlantDetail_standard() throws {
        try EBAudit.screen(self, test: "test_PlantDetail_standard", config: .standard,
                           arguments: ["-EBScreen", "PlantDetail"],
                           findings: ["EB-001", "EB-002", "EB-005", "EB-008", "EB-011", "EB-019", "EB-020"],
                           failOn: [.contrast, .sufficientElementDescription, .elementDetection,
                                    .trait, .hitRegion, .action]) { r in
            r.step("detail shown", r.app.staticTexts["Water now"], tap: false)
        }
    }
}
```

- The comment above each method lists its findings and files.
- `findings` and `failOn` come from the plan row. `failOn` lists only the types the map gives for those findings, so issues of other types are logged as leads without failing the test.
- Each route step goes through `r.step`, so a broken route prints `EB-ROUTE-FAIL` and the test reads as inconclusive instead of passing. Chain several steps with `&&`. Use `r.swipeUp()` as a step for an element below the fold.
- `EBIncreaseContrastTests.swift` has the same shape, with a class named `EBIncreaseContrastTests`, methods named `test_[Screen]_IncreaseContrast` and `config: .increaseContrast`. Its first line says: "Run with Increase Contrast on in the simulator (3-run turns it on)."

## VoiceOver walk

`EBVoiceOverWalkTests.swift` holds the walk tests from the plan, then the walk support written as is. Example test, with a route of three steps:

```swift
// EvenBetter accessibility tests: VoiceOver walks. Needs Xcode 27 and an iOS 27 simulator.
// Plan: .evenbetter/plant-care/evenbetter-accessibility-tests.md
import XCTest

final class EBVoiceOverWalkTests: XCTestCase {
    // EB-015 (PlantListView.swift, AddPlantView.swift)
    @MainActor
    func test_AddPlant_VoiceOver() throws {
        guard #available(iOS 27, *) else { throw XCTSkip("XCUIVoiceOverService needs iOS 27") }
        try EBVoiceOver.screen(self, test: "test_AddPlant_VoiceOver", items: [
            EBWalkItem(.dismissControl, findings: ["EB-015"]),
            // Guard for a correct pattern: the hidden divider should stay silent.
            EBWalkItem(.silent(["divider-flourish", "divider flourish"]), findings: []),
        ]) { r in
            r.step("list loaded", r.app.staticTexts["Monstera"], tap: false)
                && r.step("open Add", r.app.navigationBars.buttons.firstMatch)
                && r.step("sheet shown", r.app.textFields["Name"], tap: false)
        }
    }
}
```

Walk support, after the test class in the same file:

```swift
// MARK: - Walk support

enum EBWalkCheck {
    case spoken([String])                      // one of these texts is spoken
    case button([String])                      // the utterance with one of these texts includes "button"
    case oneStop([String])                     // all of these texts are spoken in one utterance
    case value(label: [String], value: String) // the utterance with the label includes the value
    case silent([String])                      // none of these texts is spoken
    case dismissControl                        // a Cancel, Close or Done button is spoken
    case noRepeatedTrait([String])             // the label part does not repeat a trait word VoiceOver adds

    var name: String {
        switch self {
        case .spoken(let texts): return "spoken(\(texts.joined(separator: " | ")))"
        case .button(let texts): return "button(\(texts.joined(separator: " | ")))"
        case .oneStop(let texts): return "oneStop(\(texts.joined(separator: " + ")))"
        case .value(let label, let value): return "value(\(label.joined(separator: " | ")) = \(value))"
        case .silent(let texts): return "silent(\(texts.joined(separator: " | ")))"
        case .dismissControl: return "dismissControl"
        case .noRepeatedTrait(let texts): return "noRepeatedTrait(\(texts.joined(separator: " | ")))"
        }
    }
}

struct EBWalkItem {
    let check: EBWalkCheck
    let findings: [String]

    init(_ check: EBWalkCheck, findings: [String]) {
        self.check = check
        self.findings = findings
    }
}

struct EBWalkPath {
    let utterances: [String]
    let end: String   // "wrapped", "stalled", "maxSteps" or "error: ..."

    /// The walk saw the whole screen: focus came back to the start, or stopped moving at the end.
    var complete: Bool { end == "wrapped" || end == "stalled" }
}

struct EBWalkProblem: Encodable {
    let check: String
    let detail: String
    let findings: [String]
}

struct EBWalkResult: Encodable {
    let test: String
    let findings: [String]
    let utterances: [String]
    let end: String
    let complete: Bool
    let failures: [EBWalkProblem]
    let unresolved: [EBWalkProblem]
}

@available(iOS 27, *)
@MainActor
enum EBVoiceOver {
    /// Navigates with VoiceOver off, because taps behave differently while it runs, then walks the screen.
    static func screen(_ testCase: XCTestCase, test: String, arguments: [String] = [],
                       items: [EBWalkItem], route: (EBRoute) -> Bool) throws {
        let app = EBLaunch.app(.standard, arguments: arguments)
        defer { EBLaunch.restoreAppearance() }
        app.launch()
        guard route(EBRoute(app: app, test: test)) else { return }
        EBAudit.attachScreenshot(app, in: testCase, name: "\(test) standard")
        let path = try walk(maxSteps: 80)
        check(items, path: path, test: test)
    }

    static func walk(maxSteps: Int) throws -> EBWalkPath {
        let voiceOver = XCUIDevice.shared.voiceOverService
        try voiceOver.enable()
        defer { try? voiceOver.disable() }
        // Move back first, so the forward walk starts at the top of the screen.
        var previous = ""
        for _ in 0..<maxSteps {
            guard let text = try? voiceOver.moveBackward().utterance, text != previous else { break }
            previous = text
        }
        var spoken: [String] = []
        if let start = try? voiceOver.currentSpeech().utterance { spoken.append(start) }
        var repeats = 0
        for _ in 0..<maxSteps {
            let text: String
            do {
                text = try voiceOver.moveForward().utterance
            } catch {
                return EBWalkPath(utterances: spoken, end: "error: \(error)")
            }
            if spoken.count > 1, text == spoken[0], text != spoken.last {
                // Focus is back on something that sounds like the first element. It wrapped only
                // if the second utterance follows too; otherwise another element sounds the same.
                guard let next = try? voiceOver.moveForward().utterance else {
                    return EBWalkPath(utterances: spoken + [text], end: "error: no speech after a repeat of the first element")
                }
                if next == spoken[1] { return EBWalkPath(utterances: spoken, end: "wrapped") }
                spoken.append(text)
                if next != text { spoken.append(next) }
                repeats = 0
                continue
            }
            if text == spoken.last {
                repeats += 1
                if repeats == 2 { return EBWalkPath(utterances: spoken, end: "stalled") }
                continue
            }
            repeats = 0
            spoken.append(text)
        }
        return EBWalkPath(utterances: spoken, end: "maxSteps")
    }

    static func check(_ items: [EBWalkItem], path: EBWalkPath, test: String) {
        var failures: [EBWalkProblem] = []
        var unresolved: [EBWalkProblem] = []
        for item in items {
            guard let result = evaluate(item.check, path) else { continue }
            let (failed, detail) = result
            let problem = EBWalkProblem(check: item.check.name, detail: detail, findings: item.findings)
            if failed { failures.append(problem) } else { unresolved.append(problem) }
            let ids = item.findings.joined(separator: ", ")
            XCTFail("EvenBetter VoiceOver \(failed ? "failure" : "not checked") \(problem.check): \(detail) [\(ids)]")
        }
        EBAudit.emit("EB-VO", EBWalkResult(test: test, findings: Array(Set(items.flatMap { $0.findings })).sorted(),
                                           utterances: path.utterances, end: path.end, complete: path.complete,
                                           failures: failures, unresolved: unresolved))
    }

    /// nil when the check passes; otherwise (true, detail) for a failure and (false, detail) when it could not run.
    static func evaluate(_ check: EBWalkCheck, _ path: EBWalkPath) -> (Bool, String)? {
        func find(_ texts: [String]) -> String? {
            path.utterances.first { utterance in texts.contains { utterance.localizedCaseInsensitiveContains($0) } }
        }
        func parts(_ utterance: String) -> [String] {
            utterance.components(separatedBy: ", ")
        }
        let notReached = (false, "not reached; the walk ended with \(path.end)")
        let shortWalk = (false, "the walk ended with \(path.end), so absence is not proven")
        switch check {
        case .spoken(let texts):
            if find(texts) != nil { return nil }
            return path.complete ? (true, "not spoken") : notReached
        case .button(let texts):
            guard let utterance = find(texts) else { return notReached }
            let isButton = parts(utterance).dropFirst().contains { $0.localizedCaseInsensitiveContains("button") }
            return isButton ? nil : (true, "spoken without the button trait: \"\(utterance)\"")
        case .oneStop(let texts):
            if path.utterances.contains(where: { u in texts.allSatisfy { u.localizedCaseInsensitiveContains($0) } }) {
                return nil
            }
            let reached = texts.allSatisfy { text in path.utterances.contains { $0.localizedCaseInsensitiveContains(text) } }
            return reached ? (true, "spoken as separate stops") : notReached
        case .value(let label, let value):
            guard let utterance = find(label) else { return notReached }
            return utterance.localizedCaseInsensitiveContains(value) ? nil : (true, "spoken without \(value): \"\(utterance)\"")
        case .silent(let texts):
            if let utterance = find(texts) { return (true, "spoken: \"\(utterance)\"") }
            return path.complete ? nil : shortWalk
        case .dismissControl:
            let found = path.utterances.contains { utterance in
                let words = parts(utterance)
                let named = ["Cancel", "Close", "Done"].contains { name in
                    words.first?.localizedCaseInsensitiveContains(name) ?? false
                }
                return named && words.dropFirst().contains { $0.localizedCaseInsensitiveContains("button") }
            }
            if found { return nil }
            return path.complete ? (true, "no Cancel, Close or Done button was spoken") : shortWalk
        case .noRepeatedTrait(let texts):
            guard let utterance = find(texts) else { return notReached }
            let words = parts(utterance)
            let head = words.first ?? ""
            // Only the trait words VoiceOver adds in English count, so a value or hint that
            // shares a word with the label is not reported.
            let traitWords = ["button", "heading", "link", "image", "selected", "dimmed", "adjustable",
                              "tab", "toggle", "switch button", "text field", "search field"]
            let repeated = words.dropFirst().filter { part in
                traitWords.contains { part.caseInsensitiveCompare($0) == .orderedSame }
                    && head.localizedCaseInsensitiveContains(part)
            }
            return repeated.isEmpty ? nil : (true, "the label repeats \(repeated.joined(separator: ", ")): \"\(utterance)\"")
        }
    }
}
```

How the walk works:

- The route runs with VoiceOver off, because taps behave differently while it runs. Then the walk turns VoiceOver on, steps back to the first element, and moves forward with `moveForward()`, keeping each `utterance`. It turns VoiceOver off at the end.
- Apple documents what `moveForward()` returns for the next element, but not what happens after the last one. The walk therefore counts as complete only when focus comes back to the start (`wrapped`: the first two utterances come back in order) or stops moving (`stalled`: the same utterance three times in a row). An error or 80 steps leaves it incomplete, and checks that need the whole screen, such as `silent` and `dismissControl`, report "not checked" instead of passing.
- Both endings are guesses from speech alone. Three neighbouring elements that sound the same, such as a row of unlabelled star buttons, also read as `stalled`, so the results log prints each walk's utterances for the user to check where it stopped.
- `XCUIVoiceOverService.Error.Code` includes `noSpeech` ("VoiceOver did not produce any speech within the timeout"). After the first real run, look at the `end` values in the log. If every walk ends with that error right after the last element, tell the user, because the absence checks will stay unresolved until the walk treats it as the end.
- Utterances are read in English. VoiceOver puts the label first and the traits after commas, as in Apple's example "Add Favorites, button".
- `noRepeatedTrait` looks only for the trait words in its list. Apple publishes no such list, so the list is EvenBetter's; add a word when a real run shows VoiceOver speaking a trait the list lacks.
- Each failed or unresolved check calls `XCTFail` with its findings, and the `EB-VO` line lists them separately so `4-record` can tell a real failure from a check that could not run.

## Route arguments in app code

When the user chose a DEBUG-only launch argument for an unreachable screen, show this kind of diff in "Before writing" and apply it only after a yes:

```swift
// File: PlantCare/PlantCareApp.swift
@main
struct PlantCareApp: App {
    @State private var store = PlantStore()

    var body: some Scene {
        WindowGroup {
            root
                .environment(store)
        }
    }

    @ViewBuilder private var root: some View {
        #if DEBUG
        // UI tests only: `-EBScreen PlantDetail` opens a screen that no route reaches yet.
        if UserDefaults.standard.string(forKey: "EBScreen") == "PlantDetail", let plant = store.plants.first {
            NavigationStack { PlantDetailView(plant: plant) }
        } else {
            PlantListView()
        }
        #else
        PlantListView()
        #endif
    }
}
```

- Read the value with `UserDefaults.standard.string(forKey: "EBScreen")`: a `-EBScreen PlantDetail` launch argument lands in the arguments domain of `UserDefaults`.
- Keep the change inside `#if DEBUG`, so release builds do not change. The tests run the Debug configuration unless the scheme says otherwise.
- Use the sample data the app already has. When it has none, ask before adding any.
- Add the change to the plan's "App code changes" list. Repair or a later refactor may remove it once a real route exists.
- The edit can move the line numbers of findings in that file. evenbetter-validate re-reads them on its next run, so this skill leaves `line_number` alone.
- An accessibility identifier for a route step follows the same rule: show the one-line diff, wait for a yes.

Without a yes, leave the app unchanged and mark the screen's findings untested with the reason. The same holds when the session cannot ask: the change stays a proposal in the plan's "App code changes" list.

## After writing

How the new files join the target, from `1-plan`:

- Xcode 16 folder (`fileSystemSynchronizedGroups`): nothing to do.
- Classic groups: ask the user to add the `EvenBetterAccessibility` folder to the UI test target in Xcode, with the target ticked, and wait for them to confirm before `3-run`.
- XcodeGen or Tuist: when the tool is installed, ask: run `xcodegen generate` (or `tuist generate`) now (Recommended) / I'll run it. When it is not, tell the user to run it before the tests.
- No target yet: tell the user to create the UI Testing Bundle and add the folder to it.

When unsure whether Xcode picked the files up, ask the user to check in Xcode's File inspector that they belong to the UI test target.

## Rules for generated code

- Mark each test method `@MainActor`, as Xcode's UI test template does. Do not mark the class or override `setUp`; the helpers set everything per test.
- No `import Testing` and no `@Test`.
- Write route queries and labels exactly as the plan has them. Never weaken an expected label, drop a check or loosen a `failOn` set to get a pass.
- Do not touch other test files, and do not touch app code except for a diff the user accepted.
- Test names carry only the screen and configuration. Finding IDs go in `findings` arrays and in comments.
