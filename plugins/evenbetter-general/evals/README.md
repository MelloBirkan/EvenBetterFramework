# evenbetter-general evals

`claude plugin eval` loads this plugin into a headless Claude Code session, sends a plain request and grades what the session did. No prompt names a skill.

## What the suite covers

`routing/` has 3 cases tagged `routing`. `routing-feature` and `routing-epic` check that a plain request reaches evenbetter-general-feature or evenbetter-general-epic. `routing-trap-feature-not-epic` asks for one menu action "done properly: a plan, tickets, then the build and a review". That wording pulls toward the epic skill, but the scope is one feature, so the case passes only when the feature skill loads and the epic skill does not.

A system prompt in each routing case tells the session to pick the one skill that fits best, load it and stop. A case costs about USD 0.04 that way, but it only shows which skill wins once the session has decided to use one. Whether a skill fires without that push is what the `loads-evenbetter-general-feature` grader in `behaviour-feature` measures.

`behaviour-feature` (tag `behaviour`) runs evenbetter-general-feature for real on a small Express todo API and asks it to plan due dates. It passes when the skill loads, the reply ends on closed questions with concrete options and a recommended choice (or says it took the recommended options as assumptions and ends with what waits on the user), nothing outside `.evenbetter/` is written or edited, and `src/server.js` and `src/store.js` still hold their original code. One `llm` grader judges the questions. The rest are regexes and `tool_used` limits.

The API lives in `_shared/todo-api/`. The case's `setup.sh` copies it into the empty workspace through `"$(dirname "$0")"`, because the scaffold runs with the workspace as its current directory and `$0` is the script's absolute path in this folder. `_shared/` has no `case.yaml` or `prompt.md`, so the runner does not treat it as a case.

## Running it

Use a throwaway config folder so nothing touches your own Claude Code settings, and keep the report local with `--no-publish`. From this plugin's folder:

```bash
export CLAUDE_CONFIG_DIR="$(mktemp -d)"
claude auth login   # once: a new config folder can start signed out; skip when ANTHROPIC_API_KEY is set

claude plugin eval . --ablation none --runs 1 \
  --scaffold --allow-tools Write Edit \
  --no-publish --trust-plugin --max-cost-usd 2
```

Drop `--runs 1` to use each case's `runs: 3`, and use `--tag routing` or `--case behaviour-feature` to run part of the suite. Write and Edit are granted only so that the "no writes" graders can catch a skill that starts coding before it asks.

## Reading the scores

A case's score is the share of its graders that passed, averaged over runs. A case passes at 1.0 unless you set `--threshold`. Per-grader verdicts are in `results/<timestamp>/aggregate-result.json` and `report.html`. `results/` is gitignored. A trap that scores 0.5 usually loaded both skills.

`behaviour-feature` at 0.57 (4 of 7 graders) means the skill never loaded: the session planned on its own, so the skill, recommendation and question graders all fail together while the file graders pass. It happened in 3 of the first 7 smoke runs, so run the case with its default `runs: 3` before you read anything into one result.

With the default `--ablation with-without`, every case also runs without the plugin. `tool_used: Skill` graders then become indicators and drop out of the score, and the delta between the arms shows what the plugin adds. That doubles the cost, so the command above uses `--ablation none`.
