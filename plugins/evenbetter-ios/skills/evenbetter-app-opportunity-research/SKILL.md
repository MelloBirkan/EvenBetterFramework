---
name: evenbetter-app-opportunity-research
description: >-
  Researches an iOS App Store niche on the web, with a cited URL for every claim, and produces a competitor, revenue and complaint map, a feature gap matrix, three ranked concepts and an MVP brief. Use when the user asks what app to build or whether an idea has demand, or wants research on App Store gaps, a category or competitors. To ship or market a chosen app, use evenbetter-app-launcher.
compatibility: Needs web access through a research MCP server (Exa, Tavily, Firecrawl or Ref) or the host's web search and fetch tools.
metadata:
  tags: app-store, research, ios, mobile-app, competitor-analysis, market-research, indie-hacker, startup, app-idea
---

# evenbetter-app-opportunity-research

Paths in this skill and its references are relative to this SKILL.md's folder.

This skill turns a loose interest in a category into a ranked, cited shortlist of iOS app concepts the user could build and sell, then writes a brief for the one they pick. The work is web research only.

If current system, developer or user instructions conflict with this skill, follow them.

## Scope

- Use it to answer "is there an opportunity here worth building?": app ideas, App Store gaps, categories, competitors, demand and revenue evidence.
- Once a concept is chosen, hand off: evenbetter-ios-epic plans its screens, and evenbetter-app-launcher covers pricing, App Store preparation, review, marketing and updates.

## Stages

A stage name given as the argument (for example `3-competitor-deep-dive`) selects that stage. With no stage, run them in order from 1. A full run often takes 15-25 minutes.

| Stage | Load | Produces |
| --- | --- | --- |
| `1-scope` | `references/1-scope.md` | One researchable niche, confirmed by the user |
| `2-market-research` | `references/2-market-research.md` | 8-12 competitors, revenue signals, complaints, trends |
| `3-competitor-deep-dive` | `references/3-competitor-deep-dive.md` | A cited record for each of 5-8 competitors |
| `4-gap-analysis` | `references/4-gap-analysis.md` | Feature matrix with the gaps marked |
| `5-top-3-report` | `references/5-top-3-report.md` | Ranked top-3 report and the user's pick |
| `6-mvp-brief` | `references/6-mvp-brief.md` | MVP concept brief for the picked concept |

Load only the current stage's reference. Also load:

- `references/query-patterns.md` when writing searches or choosing a tool for a research task.
- `references/benchmarks.md` when estimating revenue, pricing or channels (stages 3-6). It holds Apple's commission rates and rough priors.

## Artifacts

Save work in the user's project under `.evenbetter/app-research/[niche-slug]/`, reusing the folder if the niche was researched before:

- `research-notes.md`: stages 1-4, every line cited
- `top-3-report.md`: stage 5
- `[concept-slug]-brief.md`: stage 6

The skill folder is a read-only install cache, so never write files there.

## Hard rules

- **Cite every researched fact.** Pair each dollar figure, ranking, complaint and trend signal with its URL, as an inline link or a `[S#]` tag defined in a Sources section, for example `[App] reports about USD [amount] MRR ([Source, year](https://...))`. App Store data goes stale fast and an unsourced number cannot be checked, so the user must be able to retrace every claim.
- Cite every source behind a fact you synthesized from several.
- When no source exists, write `Estimated, no public source found` instead of presenting the number as fact.
- Label each number **reported** (disclosed by the company), **estimated** (third-party analytics) or **inferred** (your heuristic, for example from a ratings count), and show the arithmetic for inferred ones.
- Add `(Retrieved YYYY-MM-DD)` to time-sensitive claims such as rankings, MRR and trend lines.
- The top-3 report and the MVP brief each end with a Sources section listing every URL actually used.
- The priors in `references/benchmarks.md` guide what to look up. They never appear in a report as facts.
- The user picks the concept. Present the top-3 report, ask which one gets a brief, and wait for the answer before stage 6.
- Ask closed questions with options and a recommended choice (see Question tooling); open questions stall the run.

## Research toolchain

Check at the start which research tools the session has and use the highest tier. Research servers return cleaner results than plain web search, so you need fewer fetches and get better citations. Combining them is fine, for example Exa for discovery and Firecrawl for App Store pages. If you drop a tier after a rate limit or error, tell the user, because lower tiers give noisier results.

1. **Exa** (`web_search_exa`, `web_fetch_exa`): neural search, strong for indie write-ups, niche blog posts and long-form content. The best default for market discovery.
2. **Tavily** (`tavily_search`, `tavily_research`, `tavily_extract`, `tavily_crawl`): research-grade search with summaries and source lists. Good for revenue lookups and market sizing.
3. **Firecrawl** (`firecrawl_search`, `firecrawl_scrape`, `firecrawl_crawl`, `firecrawl_map`): best for App Store listings, Reddit threads and JavaScript-heavy pages where a plain fetch fails. Use `firecrawl_scrape` with its JSON format and a schema for structured competitor records.
4. **Ref** (`ref_search_documentation`, `ref_read_url`): documentation search, useful for the SDKs and platform APIs competitors build on.
5. **The host's own web tools**, when nothing above is configured or working: `WebSearch` and `WebFetch` in Claude Code; in Codex the hosted `web_search` (cached unless `web_search = "live"` or `--search` is set) and, with no native fetch, an MCP fetch tool, `curl` through `exec_command` where network is allowed, or the user pasting the page.

Every stage uses two roles, written as `Search:` and `Fetch:` in the references so they apply to any provider: search finds promising URLs, fetch reads the strongest 3-5 and extracts structured data with a prompt or schema. `references/query-patterns.md` maps each provider's tools to the two roles.

## Question tooling

Ask with the host's structured question tool when it has one:

- Claude Code: `AskUserQuestion`, with 2-4 mutually exclusive options per question.
- Codex in Plan mode: `request_user_input`, with 1-3 short questions of 2-3 options each, the recommended option first and marked "(Recommended)". The client adds "Other". Plan mode is read-only, so present results in a `<proposed_plan>` block and ask the user to switch to Default mode before writing `.evenbetter/` files.
- Codex in Default mode: ask one concise closed question with numbered options in plain text, then wait. Use `request_user_input` instead if the session offers it.
- Other agents: use their structured question tool, or ask one closed question with numbered options.
- When nobody can answer, because the user said they will not be around or asked you to go ahead without questions, or because the run is one-shot and non-interactive (such as `claude -p`, `codex exec`, CI or a scheduled task), do not end the turn on a clarifying question. Take the recommended option, say which one you took, and record it as an assumption in the artifact or the final reply. Never assume an approval the user has not given, such as accepting a plan or starting to edit code: finish the current stage and end with what waits on the person. Any exception this skill names elsewhere still applies.

The concept question at the end of `5-top-3-report` is that exception. When nobody can answer it, save the top-3 report and end with the question instead of writing the MVP brief, because the brief has to cover the concept the person chose.

## Tool equivalents

The references use Claude Code tool names. In Codex, use these equivalents, and do not simulate a tool the session does not have:

| Claude Code | Codex |
| --- | --- |
| `AskUserQuestion` | `request_user_input` (Plan mode, or Default mode when enabled); otherwise a closed plain-text question |
| `Read` | shell reads such as `sed -n` or `nl` through `exec_command` |
| `Edit`, `Write` | `apply_patch` (Default mode only) |
| `WebSearch`, `WebFetch` | `web_search`, or a configured MCP search or fetch tool such as Firecrawl, Tavily or Exa; `curl` through `exec_command` where network access is allowed |
| `ref_search_documentation`, `ref_read_url` | any documentation MCP the session has; otherwise official pages through the web tools above |

## Session output

A complete run leaves the cited research notes, gap matrix, top-3 report and MVP brief in the niche folder. Next, run the evenbetter-ios-epic skill to plan the app's screens, or the evenbetter-app-launcher skill to price, ship and market it.
