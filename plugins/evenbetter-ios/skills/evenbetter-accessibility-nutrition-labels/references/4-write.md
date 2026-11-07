# 4-write

Contents: Files and timestamp, The evaluation log, The declaration draft, The accessibility URL outline, Check the files, Close.

## Files and timestamp

This stage writes three files, and no others:

| File | How |
| --- | --- |
| `.evenbetter/[project]/evenbetter-accessibility-nutrition-labels.md` | Appended: one new section per run |
| `.evenbetter/[project]/accessibility-declarations.json` | Overwritten |
| `.evenbetter/[project]/accessibility-url-draft.md` | Overwritten |

Take the local time once as `YYYY-MM-DD HH:MM:SS`, written `[now]` below, and use it in all three files. The `[tmp]` folder from `0-intake` can be deleted afterwards.

## The evaluation log

Create the log with `# EvenBetter Accessibility Nutrition Labels: [project_name]` when it does not exist. Then add `## Evaluation [now]` at the end of the file, below any earlier evaluation, with these sections in this order:

### Summary

- "Draft answers for a person to enter in App Store Connect under App Accessibility. EvenBetter has not submitted anything."
- The report path, `workflow.state`, `scan_date`, `validated_at` and `repaired_at`, or "no report".
- The tests log path and the time of its newest results, or "no runtime results".
- The devices and how each was found. Note any iPhone or iPad app that also runs on Mac or Vision Pro without separate answers.
- The media answer.
- For each device: how many features are Declare, Don't declare yet and Not applicable.

### Common tasks

The task table from `1-common-tasks`: #, Task, Kind, Screens, Devices, Notes. Below it, the tasks that moved to the URL outline.

### Matrix: [device]

One section per device. Rows are the tasks by number and name. Columns use these short names, in Apple's order: VO (VoiceOver), VC (Voice Control), LT (Larger Text), DI (Dark Interface), DWCA (Differentiate Without Color Alone), SC (Sufficient Contrast), RM (Reduced Motion), CC (Captions), AD (Audio Descriptions). Leave out the columns the device does not offer. Each cell is `pass`, `blocked`, `untested` or `n/a`.

| # | Task | VO | VC | LT | DI | DWCA | SC | RM | CC | AD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Browse the plant list | blocked | blocked | blocked | blocked | untested | blocked | untested | n/a | n/a |

Below the table, list the notes that the Blockers section does not already cover, as "Task [#], [feature]: [note]". Group repeated notes: "Tasks 2 and 4, VO and VC: EB-028 (A11Y-UI-002, medium) refuted at runtime".

### Decisions

One table per device, after a line that names the device: Feature, State, Recommendation, Decision, Why. State is the feature's state from `3-decide` (`pass`, `blocked`, `untested` or `n/a`). The next run compares against this column.

### Blockers

| Finding | Severity | Clause | Label | Runtime | Features | Tasks | Devices |
| --- | --- | --- | --- | --- | --- | --- | --- |

Manual blockers go below the table: device, feature, task, the step where the person got stuck, and the screenshot or recording path, or "described in words". With no blockers, write "None."

### Pending checks

| Device | Feature | Tasks | How to test | Watch for |
| --- | --- | --- | --- | --- |

"How to test" is the feature's "Turn it on" line from `references/feature-criteria.md`, shortened. List only the features that `2-evidence` asked about and the person answered "Not tested yet". A feature that was not asked because it is blocked is not pending. Its blockers come first. With nothing pending, write "None."

### Changes since the last evaluation

Compare each device and feature with the Decisions tables of the last evaluation that `0-intake` loaded: the State and the Decision columns. List only the rows that changed, as Device, Feature, Before, Now, for example "iPhone, Larger Text, blocked, untested". Also list devices and tasks that were added or removed. With no earlier evaluation, write "First evaluation." With no changes, write "None."

### Declared against evidence

Device, Feature, the cells that are `blocked` or `untested`, and their blockers. With none, write "None."

### Open questions

List what is still unsure, with what would settle it:

- Route gaps and tasks that have no files.
- Code signals that the report does not cover. Suggest running evenbetter-analyze so they become findings.
- The Mac Catalyst reading, when it applied.
- The `check` lines from `0-intake`, when there were any.
- Questions the person left unanswered, and the table changes made after the second task question.

With none, write "None."

## The declaration draft

Overwrite `.evenbetter/[project]/accessibility-declarations.json`. Each entry in `declarations` uses the attribute names of the App Store Connect API's `AccessibilityDeclarationCreateRequest`, so the person or a later tool can copy the answers without renaming anything. The draft leaves out `relationships`, because it does not know the app's App Store Connect ID. It also leaves out `state`, which App Store Connect sets itself.

```json
{
  "generated_by": "evenbetter-accessibility-nutrition-labels",
  "generated_at": "2026-11-07 09:30:00",
  "note": "Draft answers for a person to enter in App Store Connect under App Accessibility. Nothing was submitted. true means the person chose Declare.",
  "report": {
    "path": ".evenbetter/plant-care/evenbetter-analyze-report.html",
    "state": "validated",
    "scan_date": "2026-11-07 06:01:20",
    "validated_at": "2026-11-07 07:00:00",
    "repaired_at": ""
  },
  "accessibilityUrl": "",
  "declarations": [
    {
      "type": "accessibilityDeclarations",
      "attributes": {
        "deviceFamily": "IPHONE",
        "supportsVoiceover": false,
        "supportsVoiceControl": false,
        "supportsLargerText": false,
        "supportsDarkInterface": false,
        "supportsDifferentiateWithoutColorAlone": false,
        "supportsSufficientContrast": false,
        "supportsReducedMotion": false,
        "supportsCaptions": false,
        "supportsAudioDescriptions": false
      }
    }
  ],
  "evaluation": {
    "IPHONE": {
      "supportsVoiceover": {
        "recommendation": "dont_declare_yet",
        "decision": "dont_declare_yet",
        "state": "blocked",
        "blockers": ["EB-001", "EB-002"],
        "untested_tasks": []
      }
    }
  }
}
```

The rules for the file:

- One `declarations` entry per device, in the order iPhone, iPad, Apple TV, Apple Watch, Mac, Vision. `deviceFamily` is `IPHONE`, `IPAD`, `APPLE_TV`, `APPLE_WATCH`, `MAC` or `VISION`.
- The attributes follow Apple's feature order. Leave out a feature the device does not offer: `supportsVoiceControl` on `APPLE_TV` and `APPLE_WATCH`, and `supportsLargerText` on `MAC`.
- A value is `true` only when the person chose Declare. Don't declare yet and Not applicable are both `false`. An entry with every value `false` means the same as answering No in App Store Connect, so the Close section tells the person when to leave a device unanswered instead.
- `evaluation` holds one object per device and feature. `recommendation` and `decision` are `declare`, `dont_declare_yet` or `not_applicable`. `state` is `pass`, `blocked`, `untested` or `n/a`. `blockers` lists finding IDs, plus "manual: [task]" for manual blockers. `untested_tasks` lists task numbers.
- `report` is `null` when the run had no report. `accessibilityUrl` stays empty until the person has a page.
- The file holds only the data shown above. It holds no secrets and no App Store Connect credentials.

## The accessibility URL outline

Overwrite `.evenbetter/[project]/accessibility-url-draft.md`. It is an outline for the optional accessibility page on the developer's website. Apple shows the link on the product page on every device except Apple TV. The page should be specific to this app. It can cover other accessibility features, how to turn on settings in the app, caption languages, and parts of the app that don't support a feature.

Write it in plain words for the app's users, with no finding IDs or clause IDs:

- `# Accessibility in [project_name]`
- A first line for the developer: "Outline only. Publish it on your website, then add its address under App Accessibility in App Store Connect."
- **Supported features**: for each device, the features with the decision Declare, each with one sentence on what works. With none, write "No accessibility features are listed for [device] yet."
- **Settings in the app**: accessibility-related settings the app has, such as its own text size or theme. With none found, write "None found in the code" for the developer to check.
- **Known limits**: for each feature that is not declared, what people can't do yet, in the words of the blocked tasks, such as "With VoiceOver, the delete button on a plant's page is not announced as a button."
- **Other tasks**: the tasks moved out of the common list, with what is known about them.
- **Captions and audio descriptions**: languages and coverage, only when the app plays media.
- **Contact**: "[support email or form]", for the developer to fill in.

Promise nothing that the decisions don't support. The outline describes the app as tested, not plans to fix it.

## Check the files

1. Parse the draft: `python3 -m json.tool .evenbetter/[project]/accessibility-declarations.json > /dev/null` or `jq . .evenbetter/[project]/accessibility-declarations.json > /dev/null`. Fix and rewrite it until it parses.
2. Check that each device has exactly one `declarations` entry, and that every `true` matches a Declare decision in the log.
3. Confirm that this run wrote no file other than the three above. The report and the tests log are only read.

## Close

End with one summary line per device: "[Device]: declare [features, or none]; don't declare yet [features]; not applicable [features]."

Then tell the person how App Store Connect takes the answers, from Apple's "Manage Accessibility Nutrition Labels" page:

- In Apps, choose the app, then App Accessibility in the sidebar. Click Get Started the first time. App Store Connect detects the devices when the latest version is live, or when the app record supports only one device, such as Mac. While the latest version is still being prepared, the person selects the devices.
- Click Add [Device] Support for each device. Answer Yes when the app supports any of the features on that device, then select them, or No when it supports none. The answers are saved as a draft until the person clicks Publish.
- Publishing works only for a device that has a live version on the App Store. The answers are published at once but can take up to 24 hours to reach everyone. The Account Holder, Admin, Finance, App Manager or Marketing role can do it, and the answers can be edited and published again at any time.
- A device with no Declare: leaving it unanswered shows on the App Store that support hasn't been indicated yet, while No says the app supports none of the features. The person chooses which is true.
- The accessibility URL is added there too, under Add URL, and published the same way. Before the first release, it goes live with that release.

Then the next-step lines from SKILL.md.
