# 4-record

Contents: Read the logs, Match issues to findings, Decide each verdict, Write the runtime blocks, Write the results, Write-only and log-only runs, Close.

When this stage runs on its own, for example with the argument `4-record` after a write-only run, read the `## Plan` section of `.evenbetter/[project]/evenbetter-accessibility-tests.md` for the tests, findings and elements, and make `[tmp]` with `mktemp -d` as `1-plan` does.

## Read the logs

Parse every log of this run (`[stamp].log`, and `[stamp]-contrast.log` when it exists) into one summary per test:

```bash
python3 - .evenbetter/[project]/runtime/[stamp].log <<'EOF'
import json, re, sys
tests = {}
def entry(name):
    return tests.setdefault(name, {"done": [], "issues": [], "route_fail": [], "walk": None, "status": ""})
for path in sys.argv[1:]:
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        if m := re.search(r"EB-AUDIT (\{.*\})\s*$", line):
            issue = json.loads(m.group(1))
            entry(issue["test"])["issues"].append(issue)
        elif m := re.search(r"EB-AUDIT-DONE (\S+) (\S+) issues=(\d+)", line):
            entry(m.group(1))["done"].append(m.group(2))
        elif m := re.search(r"EB-ROUTE-FAIL (\S+) (.+)$", line):
            entry(m.group(1))["route_fail"].append(m.group(2))
        elif m := re.search(r"EB-VO (\{.*\})\s*$", line):
            walk = json.loads(m.group(1))
            entry(walk["test"])["walk"] = walk
        elif m := re.search(r"Test [Cc]ase '[^']*?\b(test\w+)(?:\(\))?\]?' (passed|failed|skipped)", line):
            entry(m.group(1))["status"] = m.group(2)
json.dump(tests, sys.stdout, indent=2, ensure_ascii=False)
EOF
```

Add the contrast log as a second path when it exists. A planned test missing from the summary did not run. Without `python3`, read the same lines by hand. Each `EB-AUDIT` and `EB-VO` line ends in one JSON object.

When the user ran the tests on a Mac after a write-only run, take the newest `.log` under `.evenbetter/[project]/runtime/` whose name does not end in `-contrast.log`. Its file name without `.log` is `[stamp]`, and `[stamp]-contrast.log` next to it, when present, belongs to the same run. Write `.evenbetter/[project]/runtime/.gitignore` as `3-run` describes if it is missing.

## Match issues to findings

Take each `EB-AUDIT` issue in turn. It belongs to a finding carried by the same test when both hold:

- **Type.** One of the issue's `auditType` names (several are joined with `+`) maps to one of the finding's clauses in that configuration, in `references/audit-clause-map.md`.
- **Element.** The issue's `identifier` equals the finding's planned identifier, or the issue's `label` contains one of the finding's planned labels, ignoring case, with `*` matching any text. When the finding has no planned element, or the issue has neither a label nor an identifier, the issue still belongs to the finding if it is the only issue of that type in the test and every finding of the test that maps to the type has the same planned element.

An issue that belongs to no finding is a lead. An issue "could be" a finding's when the type matches and either the finding has no planned element or the issue has neither a label nor an identifier.

A walk problem in `EB-VO` belongs to the findings it lists, for the clauses the map gives its check. `failures` are real failures. `unresolved` are checks that could not run.

## Decide each verdict

Work through the findings in report order and take the first status that applies:

1. `not_testable`: no clause of the finding has a row in the audit or walk tables.
2. `untested`: none of the finding's planned tests ran, or the plan carried it in no test (screen not chosen, route gap left open, configuration not run).
3. `confirmed`: an audit issue belongs to it, failing or allowlisted, or a walk failure lists it. The exception is an allowlisted issue whose reason calls it a false positive: it makes the finding `inconclusive`, with that reason as the evidence.
4. `inconclusive`, when any of these is true:
   - one of its tests printed `EB-ROUTE-FAIL`, crashed or was skipped: an audit test with no `EB-AUDIT-DONE` line, or a walk test with no `EB-VO` line;
   - one of its planned configurations or tests did not run;
   - an issue that matched no finding "could be" this finding's;
   - a walk check listing it is in `unresolved`;
   - a clause of the finding has no row with Refutes `yes` for the checks that ran, or its row says "yes, when the walk is complete" and the walk was not.
5. `refuted`: everything planned ran, nothing belongs to it, and each of its clauses has a Refutes `yes` row among the checks that ran. An audit row counts only when the finding's element is on the screenshot the test attached, because the audit sees only what is on screen. Export it into `[tmp]` as `3-run` "Results to read" describes and look at it; when the element is not on it, or the screenshot cannot be read, the finding is `inconclusive` with "element not shown to be on screen".

Fill the block:

- `checked_at`: the run's `[stamp]` as `YYYY-MM-DD HH:MM:SS`, for every status except `untested`, which keeps `""`.
- `configs`: the configurations of the finding's tests that ran, in plan order, spelled as `EBConfig` spells them: `standard`, `ax5`, `dark`, `increaseContrast`, `rtl`. Walk tests count as `standard`.
- `tests`: those tests as `Class/test`, such as `EBAccessibilityAuditTests/test_PlantDetail_standard`.
- `evidence`: one sentence. For an audit issue: `hitRegion issue in standard on 'Delete': [summary]`, adding the allowlist reason when there is one. For a walk failure: `VoiceOver button(Water now): spoken without the button trait: "Water now"`. For `refuted`: which types and checks came back clean in which configurations. For `inconclusive`: the reason, for example "Route step 'detail shown' not found" or "Clean, but a clean hitRegion audit does not rule out LAY-UI-001". For `not_testable`: the clauses and "no runtime check". For `untested`: why, or `""` in write-only mode.
- `result_bundle`: the project-relative `.xcresult` path of the run that gave the evidence, the main run's when several did, and `""` for `untested` and `not_testable`.

When a verdict hangs on what the screen shows, for example an AX5 screenshot that may not show the large text size, ask: attach a simulator screenshot (Recommended) / leave it inconclusive.

## Write the runtime blocks

1. Extract the report again into `[tmp]/before.json`. If `scan_date` differs from the plan's, the findings may have been renumbered: ask: run `1-plan` and `2-write` again (Recommended) / stop. If only `validated_at` or `repaired_at` changed, drop the verdicts of findings that are gone, list them in the results, and go on.
2. Copy `before.json` to `[tmp]/data.json` and run the backfill from `1-plan`.
3. Write the verdicts as a JSON object keyed by finding `id` into `[tmp]/verdicts.json`, each value a full runtime block, and apply them. An `untested` verdict never replaces an earlier verdict:

```bash
python3 - [tmp]/data.json [tmp]/verdicts.json <<'EOF'
import json, sys
data_path, verdicts_path = sys.argv[1], sys.argv[2]
data = json.load(open(data_path, encoding="utf-8"))
verdicts = json.load(open(verdicts_path, encoding="utf-8"))
keys = ("status", "checked_at", "configs", "tests", "evidence", "result_bundle")
for issue in data["issues"]:
    new = verdicts.get(issue["id"])
    if new is None:
        continue
    if new["status"] == "untested" and issue["runtime"]["status"] != "untested":
        continue
    issue["runtime"] = {key: new[key] for key in keys}
json.dump(data, open(data_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
EOF
```

4. `python3 [script] update [tmp]/data.json [report] --state [state]`, with `[state]` the report's own `workflow.state`. This stage never changes it.
5. Confirm that only runtime blocks changed. Extract the report into `[tmp]/after.json` and run:

```bash
python3 - [tmp]/before.json [tmp]/after.json <<'EOF'
import json, sys
before, after = (json.load(open(p, encoding="utf-8")) for p in sys.argv[1:3])
for data in (before, after):
    for issue in data["issues"]:
        issue.pop("runtime", None)
print("only runtime blocks changed" if before == after else "other fields changed")
EOF
```

If other fields changed, put the report back from `before.json` with `update`, stop, and tell the user. Delete the `[tmp]` directory at the end.

Without `python3`, edit the parsed data by hand: set each `runtime` block right after `repair`, serialize the whole object as JSON in the key order it had, write `</` as `<\/`, `<!--` as `\u003c!--`, and the characters U+2028 and U+2029 as `\u2028` and `\u2029`, as the helper does, and replace only the slice between the start and end of the data as step 1 found it again, the same way `1-plan` finds them, because the report may have been rewritten since the plan. Change nothing else in the file.

## Write the results

Append a `## Results [checked_at]` section to `.evenbetter/[project]/evenbetter-accessibility-tests.md` and keep the earlier ones. It holds:

- Environment: Xcode version, simulator name, iOS version and UDID.
- The log and result bundle paths, the report path and its `workflow.state`. For an `analyzed` report, add that its findings were not validated yet.
- Configurations run and not run, with the reason for each one not run.
- One counts line: confirmed, refuted, inconclusive, not testable, untested.
- A table with columns Finding, Clause, Verdict, Evidence, Tests.
- Leads: one row per screen, audit type and element, with the summary and the clauses the map gives that type. The next evenbetter-analyze run can check them.
- Allowlisted issues, each with its reason from `EBAllowlist`.
- Walks: for each walk test, its `end` value and the utterances in order, so the user can read what VoiceOver said.
- Pending decisions: app code changes, allowlist entries or a project regeneration that were proposed and not applied.

## Write-only and log-only runs

- Write-only (nothing ran): if any finding lacks a `runtime` block, write the backfilled data with steps 1, 2, 4 and 5 above, so the report gains `untested` blocks and nothing else. Append `## Results [time] (not run)` with the commands printed in `3-run`. The user runs them on a Mac, then runs this skill with `4-record`, which reads the newest log under `.evenbetter/[project]/runtime/`.
- Log-only (the report failed the check in `1-plan` and the user chose to go on): leave the report as it is and put the verdicts in the results section only, saying they were not written. After evenbetter-validate fixes the report, running this skill with `4-record` writes them from the same log.

## Close

- Print the counts line.
- Name each confirmed finding with its evidence, most severe first.
- If the user chose to delete the tests, delete `[UITestFolder]/EvenBetterAccessibility/` and say so. Then, if this skill changed app code for a route, ask: revert that change (Recommended) / keep it. When the tests stay as a regression suite, keep the change, because they launch with it.
- End with the next-step line from SKILL.md.
