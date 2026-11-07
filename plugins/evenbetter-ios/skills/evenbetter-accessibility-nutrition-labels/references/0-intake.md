# 0-intake

Contents: Find the report, Check its state, Read the runtime results, Work out the devices, Work out the media, Load the last evaluation, Ask, Output of this stage.

The plugin ships `../../scripts/evenbetter_report.py` (Python 3, standard library only). Resolve that path against the SKILL.md folder to an absolute path, written `[script]` below, because commands run from the project root. This skill uses only its `extract` and `check` commands, because it never writes the report.

## Find the report

1. Find reports with `rg --files -uu -g 'evenbetter-analyze-report.html' .evenbetter`, leaving out `history/` folders. With more than one, ask which. The folder that holds the chosen report is `.evenbetter/[project]/` for the rest of the run.
2. With no report, `[project]` is the repository root folder name in kebab-case, as evenbetter-analyze names it, and the state is "no report" in the table below.
3. Make a temporary directory outside the project and the plugin folder with `mktemp -d`, written `[tmp]` below. Extract the data: `python3 [script] extract [report] > [tmp]/data.json`. Exit status 2 means the file cannot be read as a report: stop and pass the message on. Without `python3`, follow "Reading the data by hand" in `../evenbetter-validate/references/1-load.md`.
4. Run `python3 [script] check [report]` and keep its lines for the log's Open questions. A contract problem does not stop this skill, because it only reads `id`, `title`, `clause_id`, `related_clause_ids`, `severity`, `file_path`, `repair.status` and, when present, `runtime`. Stop only when a finding lacks one of the fields other than `runtime`, and recommend evenbetter-validate.
5. Note `project_name`, `scan_date`, `workflow.state`, `workflow.validated_at` and `workflow.repaired_at`.

## Check its state

| State | What it means here | Ask |
| --- | --- | --- |
| `validated`, with `validated_at` not earlier than `scan_date` | Every finding in the report is open. Validation removed the fixed ones. | Nothing. |
| `validated`, with `validated_at` earlier than `scan_date` | The scan is newer than the validation, so the findings are unconfirmed. | Same question as `analyzed`. |
| `repaired` | Fixes went in after the last validation. | Run evenbetter-validate first (Recommended) / use the findings as they stand / continue without the report. |
| `analyzed` | No one has confirmed the findings yet. | Run evenbetter-validate first (Recommended) / use the findings unconfirmed / continue without the report. |
| No report | There are no findings to check. | Run evenbetter-analyze, then evenbetter-validate, first (Recommended) / continue with manual checks only. |

Ask this question on its own, before any other, because the recommended answer ends the run. When the answer is to run another skill first, stop and end with that skill's name as the next step.

The open findings, and the label each blocker carries in the log:

- `validated`: every finding. No label.
- `repaired`, used as it stands: every finding. A finding whose `repair.status` is `applied` is labelled "repair not validated". If its `runtime.status` is `confirmed` and `runtime.checked_at` is later than its `repair.applied_at`, the label is "repair did not hold" instead.
- `analyzed` or stale, used unconfirmed: every finding, labelled "unconfirmed".
- Continue without the report, or no report: none. Every cell then depends on the manual checks.

## Read the runtime results

1. Each finding's `runtime.status` is the runtime verdict. A finding without a `runtime` block counts as `untested`.
2. When a finding's `repair.applied_at` is set and its verdict, other than `untested`, has a `runtime.checked_at` earlier than that stamp, the verdict describes the code before the repair. Keep the verdict, and add "checked before the last repair" to its note.
3. Read `.evenbetter/[project]/evenbetter-accessibility-tests.md` when it exists. Take the newest `## Results [time]` section whose heading does not end in `(not run)`. Keep its environment line (Xcode and simulator) and the rows of its `### Leads` table. With no such section, there are no leads.

## Work out the devices

Find the app's targets and the devices each one ships to. Search in this order and use every hit:

1. `project.pbxproj` (with `rg -uu --files -g 'project.pbxproj'`): targets whose `productType` is `"com.apple.product-type.application"`, and their build settings `SDKROOT`, `TARGETED_DEVICE_FAMILY`, `SUPPORTS_MACCATALYST`, `SUPPORTS_MAC_DESIGNED_FOR_IPHONE_IPAD` and `SUPPORTS_XR_DESIGNED_FOR_IPHONE_IPAD`.
2. XcodeGen `project.yml`: targets with `type: application`, their `platform`, and the same keys under `settings`.
3. Tuist `Project.swift`: targets with `product: .app`, and their `destinations`.

Map what you find to App Store Connect device families:

| Build setting | Device family |
| --- | --- |
| `TARGETED_DEVICE_FAMILY` contains `1` | `IPHONE` |
| `TARGETED_DEVICE_FAMILY` contains `2` | `IPAD` |
| `TARGETED_DEVICE_FAMILY` is `3`, or an app target for tvOS | `APPLE_TV` |
| `TARGETED_DEVICE_FAMILY` is `4`, or an app target for watchOS | `APPLE_WATCH` |
| `TARGETED_DEVICE_FAMILY` is `7`, or an app target for visionOS | `VISION` |
| An app target for macOS, `SUPPORTS_MACCATALYST = YES`, or `TARGETED_DEVICE_FAMILY` contains `6` | `MAC` |

Apple's build settings reference gives these values: `1` is iPhone, `2` is iPad (and Mac Catalyst "Scaled to Match iPad"), `3` Apple TV, `4` Apple Watch, `6` Mac Catalyst "Optimize for Mac" and `7` Apple Vision.

- XcodeGen applies its platform presets to each target before the target's own `settings`, unless `options.settingPresets` is `project` or `none` (the default is `all`). Its iOS preset sets `TARGETED_DEVICE_FAMILY` to `1,2`, so an iOS app target in `project.yml` that sets no `TARGETED_DEVICE_FAMILY` ships to iPhone and iPad. A target that lists `supportedDestinations` instead is unknown: ask the device question.
- `SUPPORTS_MAC_DESIGNED_FOR_IPHONE_IPAD` and `SUPPORTS_XR_DESIGNED_FOR_IPHONE_IPAD` add no device. Apple says an iPhone or iPad app that runs on an Apple silicon Mac or on Apple Vision Pro needs no separate answers there, because those stores show its iPhone or iPad labels. Note it in the Summary.
- Mac Catalyst is listed as `MAC` with its own matrix. That is this skill's reading, because Apple's pages do not say how a Mac Catalyst build is labelled. Confirm it in the device question and add it to Open questions.
- When an Xcode app target has no `TARGETED_DEVICE_FAMILY`, a Tuist target has no `destinations`, or the project files are missing, the devices are unknown. Ask the device question.

iPad signals in the code: `NavigationSplitView`, a layout that reads `horizontalSizeClass`, or a check for `userInterfaceIdiom == .pad`.

## Work out the media

Search the app's sources for media playback: `VideoPlayer`, `AVPlayer`, `AVQueuePlayer`, `AVPlayerLayer`, `AVPlayerViewController`, `AVAudioPlayer`, a web view that loads video pages, and media files in the bundle (`.mp4`, `.mov`, `.m4v`, `.mp3`, `.m4a`, `.aac`). Interface sounds and alert tones are not media for these labels. Note the file of each hit, because the tasks that pass through it are the ones that play media.

## Load the last evaluation

Read `.evenbetter/[project]/evenbetter-accessibility-nutrition-labels.md` when it exists, and take its last `## Evaluation [time]` section. Keep its Common tasks table as the starting list for `1-common-tasks`, and its Decisions tables, with their State and Decision columns, for the comparison in `4-write`. Earlier manual results do not carry over. Each run asks again, because the code may have changed since.

## Ask

Ask the report-state question first and alone when the table calls for it. Then ask these together, closed, with the recommended option first:

1. Devices, when they are unknown: "Which devices does the App Store list for this app?" iPhone and iPad (Recommended when the code has an iPad signal) / iPhone only (Recommended otherwise) / iPhone, iPad and another platform (name it in the answer). Put the recommended option first.
2. Mac Catalyst, when found: "Does this app ship a Mac version built with Mac Catalyst?" Yes, assess Mac separately (Recommended) / No, leave Mac out.
3. Media: "Does the app play video or audio content in its common tasks? Interface sounds don't count." No video or audio (Recommended when the search found nothing) / Video, with or without audio (Recommended when it found video) / Audio only, such as podcasts or music (Recommended when it found only audio). Put the recommended option first. Audio that is the soundtrack of video programs counts as Video.
4. Only after Video or Audio only: "Where does the media come from?" Only the app's own media (Recommended) / Also media from other people, such as uploads or partner content.

## Output of this stage

- The report path, its state, the open findings with their labels, and the `check` lines.
- Each finding's runtime verdict, the tests log's environment line, and its leads.
- The devices, each with how it was found (build setting or answer).
- The media answer, the files that play media, and who supplies the media.
- The last evaluation's tasks, matrix and decisions, or "first evaluation".
- `[tmp]`, which holds `data.json`.

This stage gives no verdict for any feature. The findings map to features only in `2-evidence`, through `feature-clause-map.md`.
