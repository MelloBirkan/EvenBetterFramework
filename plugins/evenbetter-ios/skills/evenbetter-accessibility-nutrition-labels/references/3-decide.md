# 3-decide

Contents: Recommend, Show the recommendations, Ask, Record the decisions, Output of this stage.

Read `references/feature-criteria.md` before this stage, for Apple's bar on each feature.

## Recommend

Take each device's matrix from `2-evidence`, and give each feature in its columns one recommendation:

| Recommendation | When |
| --- | --- |
| Not applicable | Every cell in the column is `n/a`. |
| Declare | Every cell is `pass` or `n/a`, at least one is `pass`, and no note shows that Apple's bar is missed. |
| Don't declare yet | Anything else: a `blocked` cell, an `untested` cell, or a note that shows Apple's bar is missed. |

A note shows Apple's bar is missed when the person's answers say so. For example, the media is third-party and the person reported that very little of it has captions, which Apple says rules out Captions.

The reason for each recommendation, in a few words:

- Declare: "every task passed the manual check on [date]".
- Don't declare yet, blocked: "blocked by EB-002, EB-008" or "stuck on [task] in the manual check".
- Don't declare yet, untested: "[n] of [m] tasks not tested", with the check that is pending.
- Not applicable: "no video" or "no media".

## Show the recommendations

Show one table per device before asking:

| Feature | Recommendation | Why |
| --- | --- | --- |
| VoiceOver | Don't declare yet | Blocked by EB-001, EB-002, EB-008, EB-014, EB-015, EB-019, EB-020 |
| Captions | Not applicable | No video or audio |

Say plainly that Declare is EvenBetter's reading of the evidence the person supplied, not a certification. App Review Guideline 2.3 asks for accurate metadata, and App Review can ask the developer to update labels that look intentionally misleading or harmful.

## Ask

Not applicable features are recorded without asking. App Store Connect gets no box ticked for them.

Ask one question per device, at most three devices at a time:

"Use these decisions for [device]? Declare: [features or none]. Don't declare yet: [features]. Not applicable: [features]." Use the recommended decisions (Recommended) / Review each feature.

**Review each feature**: ask once for each feature that is not Not applicable, at most three at a time, with the recommendation first: Declare / Don't declare yet. When the recommendation is Declare, Declare is first and marked Recommended. Otherwise Don't declare yet is.

The person's choice wins. When the person chooses Declare against a `blocked` or `untested` cell, record it and say, once, which tasks and blockers it covers. Don't ask again.

## Record the decisions

For each device and feature, keep:

- The recommendation and the decision. They differ only after a review.
- The feature's state for the comparison in the next run: `blocked` when any cell is blocked, `pass` when every cell is `pass` or `n/a` with at least one `pass`, `n/a` when every cell is `n/a`, and `untested` otherwise.
- The blockers and the untested tasks.
- "Declared against evidence" for each Declare whose state is `blocked` or `untested`.

## Output of this stage

- For each device, the table of features with their recommendation, decision, state, blockers and untested tasks.
- The list of features declared against the evidence.
