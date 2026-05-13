---
name: evenbetter-app-opportunity-research
description: >
  Full-pipeline iOS App Store opportunity research that prefers research MCPs (Exa, Tavily,
  Firecrawl, Ref) when available and falls back to built-in `WebSearch` / `WebFetch`. Every
  claim is anchored to a cited source URL. Discovers underserved niches, analyzes competitor
  gaps, produces revenue-validated top-3 opportunity reports, and writes MVP concept briefs —
  all through automated web research. Use this skill whenever the user wants to find
  profitable iOS app ideas, research App Store categories, analyze competitor apps, validate
  an app concept, or explore what's working in a specific niche. Trigger on phrases like
  "find app opportunities", "app store research", "what app should I build", "research this
  app category", "find a gap in the app store", "iOS app idea", "is this app idea good",
  "what's trending on the App Store", or any question about mobile app market viability.
  Also trigger when the user mentions wanting to build an app but isn't sure what to build,
  or wants to validate whether a concept has legs.
metadata:
  tags: app-store, research, ios, mobile-app, competitor-analysis, market-research, indie-hacker, startup, app-idea
---

# evenbetter-app-opportunity-research

Research and validate iOS app opportunities using web research tools, with every finding anchored to a cited source URL. The goal is to go from a vague category interest to a validated, ranked shortlist of app concepts the user could realistically build and monetize — without ever opening Xcode.

## Research Toolchain

This skill is **tool-agnostic by design**. Always pick the strongest research tool available in the current session before falling back to the agent's native primitives. Specialized research MCPs return cleaner, higher-signal results than a raw web search, which means fewer follow-up fetches and more accurate citations.

### Tool preference order

Check what's available at the start of the session and pick from the top of this list. **Do not silently downgrade** — if a higher-tier tool is available, use it. If multiple MCPs are configured, you can also combine them (e.g., Exa for discovery, Firecrawl for scraping the App Store page).

1. **Exa** (`exa:search` skill, `web_search_exa`, `web_fetch_exa`) — neural search, strong for finding indie writeups, niche blog posts, and high-signal long-form content. Best default for market discovery.
2. **Tavily** (`tavily_search`, `tavily_research`, `tavily_extract`, `tavily_crawl`) — research-grade search with built-in summarization and source surfaces. Great for revenue lookups and market sizing.
3. **Firecrawl** (`firecrawl_search`, `firecrawl_scrape`, `firecrawl_extract`, `firecrawl_crawl`, `firecrawl_map`) — best for scraping App Store listings, Reddit threads, and JS-heavy pages where a plain fetch struggles. Use `firecrawl_extract` with a JSON schema for structured competitor data.
4. **Ref** (`ref_search_documentation`, `ref_read_url`) — documentation-oriented; useful when researching SDK/framework angles or platform APIs that competitors integrate with.
5. **Native `WebSearch` + `WebFetch`** — universal fallback. Use when no MCP is configured, or when an MCP rate-limits / errors out.

### When to use search vs. fetch

Regardless of which provider you use, the workflow has two roles:

| Role | What it does | Provider candidates |
|------|--------------|---------------------|
| **Search** | Discovers URLs and surfaces signals across the web | `exa:search`, `web_search_exa`, `tavily_search`, `tavily_research`, `firecrawl_search`, `ref_search_documentation`, native `WebSearch` |
| **Fetch / extract** | Reads the full content of a known URL and pulls structured data | `web_fetch_exa`, `tavily_extract`, `firecrawl_scrape`, `firecrawl_extract`, `ref_read_url`, native `WebFetch` |

Pair them: search finds promising URLs, fetch reads them. The pattern is `search → triage results → fetch the strongest 3–5 → extract structured data with a prompt or schema`.

In the rest of this skill, examples are written as `Search: <query>` and `Fetch: <url>` so they apply to any provider. Substitute the actual tool name based on what's available.

## Citations are mandatory

Every researched fact in this skill's output must be paired with the source URL it came from. This is non-negotiable — unsourced numbers are worse than no numbers, because they look authoritative without being verifiable, and the user can't update their priors when the source goes stale.

**Why:** App Store data, revenue estimates, and trend signals decay fast. The user needs to retrace your steps months later to refresh the picture. Without a URL, every claim becomes "trust me."

**How to apply:**

- Inline every dollar figure, ranking, complaint, and trend signal with the URL it came from. Markdown link-style is fine: `Daylio reports ~$50K MRR ([IndieHackers, 2024](https://www.indiehackers.com/...))`.
- When the same source feeds multiple claims, you can use a short bracket tag (`[S1]`) and define the source once in a "Sources" section — but never drop the URL.
- If a fact came from your own synthesis across multiple sources, cite all of them.
- If you can't find a source, **say so explicitly** (`Estimated, no public source found`) rather than presenting it as fact.
- Mark whether each number is **reported** (company-disclosed), **estimated** (third-party analytics), or **inferred** (your heuristic from ratings count, etc.).
- Note retrieval date for time-sensitive claims (App Store rankings, MRR, trend lines). `(Retrieved YYYY-MM-DD)` is enough.

The Top 3 Opportunity Report and MVP Concept Brief both have a "Sources" section at the end — populate it with every URL you actually used.

### Search query patterns

Build precise queries instead of relying on a "research mode". These levers work across Exa, Tavily, Firecrawl, and native `WebSearch`:

- **Site filter:** `site:reddit.com`, `site:apps.apple.com`, `site:sensortower.com`, `site:appfigures.com`, `site:data.ai`, `site:news.ycombinator.com`, `site:producthunt.com`. (For Exa neural search, you can also pass these as domain filters when the API supports it.)
- **Year qualifier:** include `2025` or `2026` to bias toward recent results.
- **Sentiment language:** include words like "complaints", "missing features", "wish", "alternative", "vs", "review", "disappointed" to surface opinionated content.
- **Source language:** include "ARR", "MRR", "revenue", "indie", "solo developer", "App Store" to bias toward analytics and indie blogs.

When one search isn't enough, fan out with 3–5 variations and merge the results. **Record the result URL for every fact you keep** — you'll need it for citations.

## Pipeline

```
Category Scoping → Market Research → Competitor Deep-Dive → Gap Analysis → Top 3 Report → MVP Concept Brief
```

A full session takes roughly 15–25 minutes of automated research.

---

## Step 1: Scope the Category

Help the user narrow from a broad interest to a researchable niche. The sweet spot is specific enough to have identifiable competitors but broad enough to have real demand.

**Too broad:** "Health apps" — thousands of competitors, impossible to differentiate.
**Good:** "Sleep tracking for anxiety sufferers" — specific intersection of audience + problem.
**Good:** "Habit tracking for fitness beginners" — audience + niche.
**Good:** "AI-powered journaling" — tech angle + category.

Ask these questions (adapt based on what the user already shared):

1. What category or problem space interests you?
2. Consumer or B2B? Consumer apps are easier to validate quickly through App Store data.
3. Any tech preferences? (AI-powered, simple utility, widget-focused, etc.)
4. Target revenue? A hobby project at $1K/mo has different requirements than a $10K/mo business.

Once you have a niche, move to research.

---

## Step 2: Market Research

Run a layered set of `WebSearch` queries to triangulate the landscape. No single search gives the full picture — combine angles.

### 2a. Market Landscape Overview

Run 3–5 broad searches to identify the top competitors and the shape of the category. Use the highest-ranked provider available (see "Tool preference order" above).

```
Search: top {category} iOS apps 2026 best
Search: best {category} app iPhone 2025 review
Search: {category} iOS app comparison ranked
Search: most popular {category} apps App Store 2025 2026
```

For each promising article (review roundups, "best of" lists, competitor comparisons), follow up with a fetch to read the full content:

```
Fetch: <URL of competitor roundup or review article>
  prompt: "List every {category} app mentioned. For each: name, developer, pricing,
           rating, and any quoted strengths or weaknesses. Return the source URL alongside
           each extracted fact so I can cite it."
```

Use these to build the initial competitor list (target 8–12 names). **Record the source URL next to every app name** — you'll need it for the final report.

### 2b. Revenue Signals

Search for revenue data points using `site:` filters that target analytics and indie sources.

```
Search: indie iOS {category} app revenue MRR ARR 2025 2026
Search: {category} app revenue site:sensortower.com
Search: {category} app revenue site:appfigures.com
Search: {category} app revenue site:data.ai
Search: solo developer {category} app income report 2025
```

For each strong hit, pull the exact numbers with a fetch:

```
Fetch: <URL of revenue/analytics article>
  prompt: "Extract every {category}-related app mentioned with its estimated monthly
           or annual revenue, download numbers, and the source/date of the estimate.
           Return the source URL alongside each figure, and mark each number as
           'reported', 'estimated', or 'inferred'."
```

Keep the source URL next to every figure. Revenue claims without citations are unusable in the final report.

### 2c. User Complaints & Sentiment

Reddit, Hacker News, and forums are the richest source of unmet-need signal. Use `site:` filters to target community sources, and language that surfaces opinionated content. Firecrawl is particularly useful here because Reddit's JS rendering can defeat plain fetchers.

```
Search: best {category} app site:reddit.com disappointed missing
Search: {category} app alternatives site:reddit.com better than
Search: {category} app wish had feature site:reddit.com
Search: {category} app frustrating site:news.ycombinator.com
```

Fetch the threads that look promising:

```
Fetch: <Reddit / HN thread URL>
  prompt: "Extract every concrete user complaint, missing feature request, and
           'I wish X did Y' comment. Group by app name when possible. Return the
           thread URL with each extracted quote so I can cite the original."
```

These threads are direct gap signals — users describing what they want but can't find. Save the thread URL with every quote you keep; in the final report, complaints without a permalink lose all their weight.

### 2d. Trend Validation

Check whether the niche is growing or declining by biasing queries toward recent activity.

```
Search: {category} app trend growing 2025 2026
Search: {category} iOS app new launch 2026
Search: {category} app market size growth
Search: new {category} app site:producthunt.com 2025 2026
```

Recent launches signal a growing category. No new entrants in 12+ months could mean the niche is saturated or dead. Capture the launch URL or Product Hunt listing for each example you cite.

### 2e. Deep Niche Research (optional)

For a primary niche worth deep investment, run a structured fan-out. Issue 8–12 targeted searches across these subtopics, then synthesize. Tavily's `tavily_research` is a strong fit for this stage when available — it batches multiple sub-queries.

1. Top competitors with ratings and pricing
2. Common user complaints across apps
3. Underserved user segments
4. Revenue benchmarks for solo/indie developers
5. Recent trends and new entrants
6. Most common monetization strategies

```
Search: top 10 {category} apps ratings pricing 2026
Search: {category} app underserved audience unmet need
Search: indie {category} app monetization subscription
Search: {category} app new entrants 2025 2026 launch
Search: {category} app freemium vs subscription conversion rate
```

Fetch the deepest 3–5 articles for full quotes and numbers, keeping each URL. Reserve this pass for your primary niche — it's the most thorough but slowest.

---

## Step 3: Competitor Deep-Dive

Pick the 5–8 most relevant competitors and research each one more closely.

### 3a. App Store Listing Data

If you don't have the exact App Store URL, find it via search:

```
Search: {app name} site:apps.apple.com
```

Then fetch the listing page and pull structured data. The extraction prompt is what gives you a clean, comparable record per competitor. Firecrawl's `firecrawl_extract` with a JSON schema is ideal here; Exa's `web_fetch_exa` or native `WebFetch` with the prompt below also work.

```
Fetch: https://apps.apple.com/us/app/{app-slug}/{app-id}
  prompt: "Extract these fields as a structured JSON object:
           - name (string)
           - developer (string)
           - starRating (number)
           - ratingsCount (string, e.g. '12.4K')
           - price (string)
           - inAppPurchases (array of strings with name + price)
           - category (string)
           - descriptionSummary (string, 2–3 sentences)
           - keyFeatures (array of strings, the bullet/list highlights)
           - sourceUrl (the App Store listing URL)
           - retrievedAt (today's date in YYYY-MM-DD)"
```

This is far more reliable than parsing search snippets — the rendered listing page produces structured output you can compare side-by-side across competitors. Keep `sourceUrl` and `retrievedAt` on every record so the final report can cite them.

### 3b. Revenue & Business Data per Competitor

```
Search: {app name} app revenue ARR
Search: {app name} app downloads MAU
Search: {app name} indie hacker income report
Search: {app name} app funding raised seed
```

For each strong hit, fetch the article and pull the exact numbers:

```
Fetch: <article URL>
  prompt: "Extract the dollar revenue, download count, MAU, and any funding mentioned
           for {app name}, with the date or quarter of the figure and the source it
           cites. Note whether the number is reported, estimated, or self-disclosed,
           and include the article URL so I can cite it."
```

### 3c. Competitor Comparisons & Review Sentiment

```
Search: {app name} review complaints problems
Search: {app name} site:reddit.com problems missing
Search: {app name} vs {competitor name} comparison
Search: {app name} alternatives better
```

Fetch the strongest review and comparison articles:

```
Fetch: <comparison article URL>
  prompt: "Summarize how {app name} compares to its competitors. List its top 3
           strengths, top 3 weaknesses, the most-cited missing features, and which
           competitor wins for which use case. Include the article URL for citation."
```

### Data to collect per competitor

Every field below must travel with its source URL. A row without a citation is incomplete.

| Field | Tool role | Source |
|-------|-----------|--------|
| Name, rating, price | **Fetch** | App Store listing page |
| Ratings count | **Fetch** | App Store listing page |
| Key features | **Fetch** | App Store description |
| Estimated revenue | **Search + Fetch** | SensorTower, AppFigures, indie hacker blogs |
| Top complaints | **Search + Fetch** | Reddit, HN, forums, review sites |
| Missing features | **Search + Fetch** | Comparison posts, "wish" threads |
| Competitor comparisons | **Search + Fetch** | Blog posts, review articles |

### Revenue estimation heuristics

When exact revenue isn't public, use these rough proxies:
- `rating_count × 50–80 ≈ approximate total installs` (App Store rule of thumb)
- 2–5% of free users convert to paid on a freemium model
- Average iOS subscription is ~$5–7/mo for consumer apps
- Solo dev benchmarks: a niche utility can do $1–5K/mo; a well-executed category app can do $5–30K/mo

### Signals to watch for

**Green flags (pursue):**
- Top competitors have mediocre reviews (3.0–3.5 stars) — room to win on quality
- Solo devs or small teams are making meaningful revenue — proves indie viability
- Users across multiple apps complain about the same missing feature
- The category has clear willingness to pay ($5–15/mo subscriptions exist)
- Apple features apps in this category (Editors' Choice, App of the Day history)

**Red flags (avoid or proceed with caution):**
- A single app dominates with 500K+ ratings — entrenched incumbent
- The category requires hardware integration or complex platform APIs
- Heavy regulation (medical diagnosis, financial trading)
- All competitors are free with no clear monetization path
- The niche is trending downward (search interest declining year over year)

---

## Step 4: Gap Analysis

Synthesize findings into a feature comparison matrix. This is where the opportunity becomes concrete.

```markdown
| Feature            | App A | App B | App C | App D | Opportunity |
|--------------------|-------|-------|-------|-------|-------------|
| Core Feature 1     | ✓     | ✓     | ✗     | ✓     | Table stakes |
| Core Feature 2     | ✗     | ✓     | ✓     | ✗     | Table stakes |
| Gap Feature 1      | ✗     | ✗     | ✗     | ✗     | DIFFERENTIATOR |
| Gap Feature 2      | ✗     | ✗     | ✗     | ✗     | DIFFERENTIATOR |
| AI Integration     | ✗     | Basic | ✗     | ✗     | DIFFERENTIATOR |
| Price (monthly)    | $14.99| $9.99 | Free  | $6.99 | Undercut + better value |
| UX Quality         | Poor  | Good  | OK    | Good  | Win on polish |
```

The winning opportunity sits at the intersection of:
1. **Proven demand** — multiple competitors exist and make money
2. **Consistent gaps** — they all miss the same 1–2 features users want
3. **Vocal frustration** — users actively complain about the gap
4. **Viable pricing** — the category supports $5+/mo subscriptions

---

## Step 5: Top 3 Opportunity Report

Present a ranked report. Each opportunity should be self-contained — the user should be able to read just one and understand the case.

### Report template

Every factual claim in the report — competitor names, revenue numbers, complaints, trend signals — must include a citation. Use inline markdown links or short `[S#]` tags backed by the "Sources" section at the end.

```markdown
# Top 3 iOS App Opportunities: {Category}

## #1: {Concept Name} — RECOMMENDED
**Pitch:** {What it does in ≤15 words}
**The gap:** {What's missing in the market and why it matters} [S1][S2]
**Target user:** {Who they are, what pain they feel, why they'd pay}
**Revenue model:** {Free tier + premium at $X/mo, expected conversion %}
**Revenue path:** {Realistic path to $Y/mo, with assumptions backed by competitor data} [S3]
**Competition:** {Who exists, why this concept wins — link each competitor} [S4][S5]
**Build complexity:** {Low / Medium / High — and what drives complexity}
**Confidence:** {High / Medium / Low — with specific reasoning, including which sources support it}

## #2: {Concept Name}
...

## #3: {Concept Name}
...

## Recommendation
{Why #1 is the best bet. Be specific — reference the gap, the revenue signal, and the competitive weakness it exploits, with citations.}

## Sources
- [S1] {Short title} — <https://...> (Retrieved YYYY-MM-DD)
- [S2] {Short title} — <https://...> (Retrieved YYYY-MM-DD)
- [S3] {Short title} — <https://...> (Retrieved YYYY-MM-DD)
- [S4] {App Store listing} — <https://apps.apple.com/...> (Retrieved YYYY-MM-DD)
- [S5] {Reddit thread / blog post} — <https://...> (Retrieved YYYY-MM-DD)
```

If you couldn't find a source for a claim, mark it `(Estimated, no public source)` rather than implying it's sourced.

**Present this to the user and get their pick before proceeding to the concept brief.**

---

## Step 6: MVP Concept Brief

Once the user picks an opportunity, write a concept brief. This isn't a full PRD — it's enough to hand to any development approach (SwiftUI, React Native, Flutter, Expo, a no-code tool, or a freelancer) and get something built.

### Brief structure

1. **Concept Summary** — 2–3 sentence pitch. What it is, who it's for, why now.

2. **Market Context** — The gap you identified, key competitors and their weaknesses, revenue signals that validate demand.

3. **Target Users** — 2–3 personas. Name, context, pain point, what they'd pay.

4. **MVP Feature Set** — 5–8 core features grouped logically. For each: what it does, why it matters, one sentence on expected behavior. Mark which features are free vs. premium.

5. **Screens Overview** — List every screen with a one-line description. Group by navigation structure (tabs, flows). No wireframes needed — just the map.

6. **Monetization** — Free vs. premium split. Price point. Trial strategy. Why this price works given the competition.

7. **Design Direction** — Mood (minimal, playful, premium, etc.). 2–3 hex color suggestions. Typography vibe. Reference 1–2 existing apps whose aesthetic is in the right ballpark.

8. **Launch Playbook** — 3–4 marketing channels ranked by fit. Week 1–4 launch plan. One "gotcha moment" — the single feature or experience that makes someone tell a friend.

9. **Risks** — Top 3 risks and how to mitigate each.

10. **Success Metrics** — 3–5 KPIs with specific 90-day targets.

11. **Sources** — Every URL used to build this brief, grouped by section (Market Context, Target Users, Monetization, etc.) with a retrieval date. Future-you (and the user) will need these to refresh the brief once data shifts.

Save the brief as a Markdown file: `{AppConceptName}-brief.md`

---

## Quick Reference: Tool Selection by Task

The "Tool" column lists generic roles — pick the highest-tier provider available (see "Tool preference order").

| Research Task | Tool role | Query / Prompt Pattern |
|---------------|-----------|------------------------|
| Market landscape overview | Search → Fetch | `top {category} iOS apps 2026 best`, then fetch the strongest roundups |
| Revenue estimates | Search → Fetch | `{category} app revenue site:sensortower.com` (and similar), extract numbers + URL from each result |
| Reddit / forum complaints | Search → Fetch | `best {category} app site:reddit.com disappointed missing`, then fetch threads (Firecrawl handles Reddit JS well) |
| Trend validation | Search | `{category} app trend growing 2025 2026` |
| Comprehensive niche report | Search (fan-out) → Fetch | 8–12 targeted queries across subtopics, fetch the deepest 3–5 articles (Tavily `tavily_research` if available) |
| App Store listing data | Fetch | URL of listing page + extraction prompt for name / rating / price / features (Firecrawl `firecrawl_extract` ideal) |
| Find App Store URLs | Search | `{app name} site:apps.apple.com` |
| Competitor review sentiment | Search → Fetch | `{app name} review complaints site:reddit.com`, then fetch threads |
| Competitor revenue / funding | Search → Fetch | `{app name} app revenue ARR funding raised`, then fetch articles |
| Competitor comparisons | Search → Fetch | `{app name} vs {competitor name} comparison`, then fetch the comparison post |
| Platform / SDK angle research | Search → Fetch | `ref_search_documentation` for API surfaces competitors integrate with |

## Tool equivalents

This skill describes search and fetch generically so any host can run it. Substitute the actual tool name based on what's configured in the current session, and follow the preference order in "Research Toolchain" above.

| Generic role | Preferred providers (in order) | Fallback |
| --- | --- | --- |
| Search | `exa:search`, `web_search_exa` → `tavily_search`, `tavily_research` → `firecrawl_search` → `ref_search_documentation` | native `WebSearch` |
| Fetch / extract | `web_fetch_exa` → `tavily_extract` → `firecrawl_scrape`, `firecrawl_extract` → `ref_read_url` | native `WebFetch` |
| Ask the user | `AskUserQuestion` (Claude Code) | `request_user_input` (Codex Plan mode) or a concise closed question |

If current system or developer instructions conflict with this skill, follow the higher-priority instruction.

---

## Revenue Benchmarks (2025–2026)

| App Type | Solo Dev Range | Small Team | Known Reference |
|----------|---------------|------------|-----------------|
| Niche utility | $1–5K/mo | $5–20K/mo | Rootd (~$1M+ total, 1 dev) |
| Habit / tracker | $5–15K/mo | $20–80K/mo | Daylio (~$50K/mo) |
| Gamified self-care | $10–50K/mo | $100K+/mo | Finch (~$2M/mo) |
| Meditation / wellness | $5–20K/mo | $50–500K/mo | Calm ($100M+/yr) |
| Productivity | $3–10K/mo | $20–100K/mo | Various |
| AI-powered tool | $5–30K/mo | $50–300K/mo | Emerging category |

## Pricing Sweet Spots

| Tier | Monthly | Annual | Best For |
|------|---------|--------|----------|
| Impulse | $2.99–4.99 | $19.99–29.99 | Simple utilities, widgets |
| Standard | $5.99–6.99 | $34.99–44.99 | Most indie apps |
| Premium | $9.99–14.99 | $59.99–99.99 | AI-heavy or professional tools |

## Marketing Channels Ranked for Indie iOS

| Channel | Fit | Cost | Speed |
|---------|-----|------|-------|
| TikTok organic | Consumer, visual demos | Free | 2–4 weeks |
| Reddit niche subs | Technical, niche audiences | Free | 1–2 weeks |
| Product Hunt | Productivity, dev tools | Free | Launch day spike |
| Apple Search Ads | Any iOS app | $0.50–3/tap | Immediate |
| Instagram Reels | Lifestyle, wellness | Free | 2–6 weeks |
| Twitter/X indie dev | Dev tools, indie community | Free | Ongoing |

---

## Session Output

A complete session produces:
1. **Market research notes** — competitor list, revenue signals, trend data, each entry cited
2. **Gap analysis matrix** — feature comparison across top competitors, with source links per row
3. **Top 3 Opportunity Report** — ranked concepts with revenue validation and a Sources section
4. **MVP Concept Brief** — enough detail to start building with any tool or framework, with a Sources section grouped by topic

All driven by a search + fetch pair from whatever provider is available — preferring Exa, Tavily, Firecrawl, or Ref when configured, and falling back to native `WebSearch` + `WebFetch` otherwise. Every factual claim in every output ships with the URL it came from, so the user can re-check, refresh, or share the research with confidence.
