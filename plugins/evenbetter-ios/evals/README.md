# evenbetter-ios evals

`claude plugin eval` loads this plugin into a headless Claude Code session, sends a plain request and grades what the session did. No prompt names a skill. The routing cases check which skill wins a request, and the behaviour cases check that a skill fires on its own and then does its job.

## What the suite covers

`routing/` has 20 cases tagged `routing`. Twelve check that a plain request reaches the right skill: analyze, validate, repair, ios-feature, ios-epic, accessibility-tests, accessibility-nutrition-labels, swiftui-accessibility, design, app-launcher, app-opportunity-research and ios-debugger-agent. The eight `trap-*` cases sit between two close skills: one screen against a whole app, a repo audit against one view, App Store labels against labels in code, and a runtime check against a static audit. A trap passes only when the right skill loads and its neighbour does not.

A system prompt in each routing case tells the session to pick the one skill that fits best, load it and stop. That keeps a case at about USD 0.05, but it also means a routing case measures which skill wins once the session has decided to use one. It does not show that the skill would fire without being told to. The `loads-*` grader in each behaviour case covers that, because those sessions get no such instruction.

`behaviour/` has 7 cases tagged `behaviour`. They run the skill for real on PlantCare, a five-file SwiftUI app with 12 planted HIG and accessibility problems and two correct patterns that look like problems:

| Case | Seed report | What passes |
| --- | --- | --- |
| `behaviour-analyze` | none | The report lands in `.evenbetter/plant-care/`, names a clause for each planted problem and flags neither correct pattern |
| `behaviour-validate` | analyzed, with 2 planted false positives | State becomes validated, EB-031 and EB-032 are gone, and every planted problem's clause is still in the report |
| `behaviour-repair-gate` | analyzed | Repair refuses, edits nothing and points to evenbetter-validate |
| `behaviour-repair` | validated | The trash control is labelled "Delete" with a destructive role, the plus is labelled "Add", and the report becomes repaired |
| `behaviour-ios-feature` | none | Planning a favourites screen ends on closed questions with a recommended option, or on the recommended options taken as assumptions, and no Swift is written |
| `behaviour-accessibility-tests-no-xcode` | validated | With no Xcode it says a Mac is needed, offers the write-only path, and leaves app code and verdicts alone |
| `behaviour-accessibility-nutrition-labels` | validated | It starts from intake or its matrix, claims no label, does not call VoiceOver, Voice Control or Larger Text clear, leaves app code alone and never calls the App Store Connect API |

Most graders need no judgement. They are regexes on the files the run leaves behind, and `tool_used` limits such as "no Edit on a `.swift` file". Each case has at most one `llm` grader.

## How the fixture gets into a run

Each run starts in an empty workspace. The scaffold script runs there with that workspace as its current directory, and `$0` is the absolute path of the case's `setup.sh` inside this folder. A relative path such as `data/x` does not reach the case folder, but `"$(dirname "$0")/..."` does. `scaffold_script` has to name a file inside the case folder (`../` is refused), so each `setup.sh` is a few lines that source `_shared/scaffold.sh` and call its helpers:

- `plantcare_fixture` copies `_shared/plantcare/PlantCare/` into the workspace.
- `plantcare_report analyzed|validated` runs `_shared/seed_report.py`. It builds the report data from `_shared/plantcare-findings.json`, renders it with the plugin's own `scripts/evenbetter_report.py` and checks it. If the report contract changes and the seed stops passing, the scaffold fails loudly, so the agent never gets a broken report.

`_shared/` holds no `case.yaml` or `prompt.md`, so the runner does not treat it as a case. The agent under test cannot read anything under `evals/`, so it never sees the graders or the planted answers.

PlantCare's list uses a value-based `NavigationLink` inside a `NavigationView` and declares no `navigationDestination`, so the detail screen never opens. This belongs to planted problem v01 (NavigationView), and the repair for v01 adds the destination. An audit that reports it is right, and no grader counts it against the run. A case that runs the unrepaired app on a Mac would need this fixed first.

## Running it

Use a throwaway config folder so nothing touches your own Claude Code settings, and keep the report local with `--no-publish`. From this plugin's folder:

```bash
export CLAUDE_CONFIG_DIR="$(mktemp -d)"
claude auth login   # once: a new config folder can start signed out; skip when ANTHROPIC_API_KEY is set

# Routing: read-only, about USD 1 for all 20 cases at one run each.
claude plugin eval . --tag routing --ablation none --runs 1 \
  --no-publish --trust-plugin --max-cost-usd 3

# Behaviour: runs the scaffolds and grants the tools the skills need.
# About USD 2.5 for all 7 cases at one run each. analyze and validate cost the most.
claude plugin eval . --tag behaviour --ablation none --runs 1 \
  --scaffold --allow-tools Bash Write Edit \
  --no-publish --trust-plugin --max-cost-usd 10
```

Drop `--runs 1` to use each case's `runs: 3`. Add `--case behaviour-repair` to run one case. `--case` takes a single name glob, and if you pass it twice only the last one counts.

Things that trip a first run:

- The Bash grant needs the sandbox backend. On Linux that is `bubblewrap` and `socat`. Without them, every case that lists Bash fails at start.
- On Linux the eval sandbox makes everything under `/tmp` read-only, including a workspace that lives there, so Bash cannot write the report. Point `TMPDIR` at an existing folder outside both `/tmp` and your home folder, which the sandbox also hides, for example `export TMPDIR=/srv/eb-eval-tmp`. The workspace is then `$TMPDIR/claude-eval-XXXXXX/home/cwd`.
- Every Bash result in the trace starts with `.bashrc: Permission denied` twice. It is noise: the command still runs.
- `.mcp.json` declares the Xcode server. The runner does not start it without a mock and prints a warning per case. None of these cases need it.
- WebFetch is not granted. analyze and validate then rely on the corpus and say in `scan_context.notes` that sources were not re-fetched, which is what the skills document for that case. Add `WebFetch` to `--allow-tools` to test the fetching path. It costs more and takes longer.
- `--keep-temp` keeps each workspace and its `out/trace.jsonl` for debugging. Delete the folders afterwards.

## Reading the scores

A case's score is the share of its graders that passed, averaged over runs. A case passes at 1.0 unless you set `--threshold`. Per-grader verdicts are in `results/<timestamp>/aggregate-result.json` and `report.html`. `results/` is gitignored.

- Routing: 1.0 means the right skill loaded, and for a trap that the neighbour did not. 0.5 on a trap usually means both loaded.
- `behaviour-analyze`: graders `v01` to `v13` are one per planted problem, so their pass rate is the audit's recall. There is no `v08`. It expected A11Y-UI-003 on the plant row, but the row is the label of a `NavigationLink`, which VoiceOver already reads as one element, so the audit was right to skip it. The other graders check the report state, that the 28x28 pt trash target is filed as LAY-UI-001 and not LAY-A11Y-001, that no Swift file changed, and that neither correct pattern in AddPlantView.swift was flagged. One regex catches an A11Y-UI-001 or A11Y-UI-002 finding on that file, and the `llm` grader catches the same claim under any other clause.
- The clause graders in analyze and validate count a clause only in a finding's `clause_id` or `related_clause_ids`. A clause that appears only in `scan_context.notes` does not count. `v02` and the trash label share A11Y-UI-001, so `v02` cannot tell them apart.
- `behaviour-validate`: the run may merge findings, and the merges vary from run to run. `keeps-planted-problems` therefore checks clauses rather than finding IDs. A merged finding keeps its clauses in `related_clause_ids`.
- With the default `--ablation with-without`, every case also runs without the plugin. `tool_used: Skill` graders then become indicators and drop out of the score, and the delta between the arms shows what the plugin adds. That doubles the cost, so the commands above use `--ablation none`.

## Notes for case authors

- A tool in a case's `allowed_tools` is only offered when the run also grants it with `--allow-tools`. Without the grant the run warns that the grader cannot pass.
- A `tool_used` grader with `max: 0` also needs `min: 0`, because `min` defaults to 1.
- A `{source: file, path: ...}` target takes an exact path, not a glob. That is why the analyze prompt names `.evenbetter/plant-care/`. Left to the skill's own rule, the folder would be named after the workspace folder, `cwd`.
- To check that app code was left alone, match the app's own paths (`/PlantCare/`) and check the file contents. Do not exempt `/tmp/` from a "no writes" grader: with the default `TMPDIR` on Linux the workspace itself is under `/tmp`, and the grader would let every write through. Scratch files that skills write with `mktemp -d` land in `$TMPDIR/claude-eval-XXXXXX/tmp/`, outside the workspace.
- The session has no AskUserQuestion tool and cannot wait for an answer. A skill either asks in plain text and ends the turn, or, when it can tell that nobody will answer, takes the recommended option and says so (the shared Question tooling rule). Grade questions on `last_message`, and accept both. When a case needs the run to go past the first question, put the answers in the prompt, as `behaviour-repair` does.
