---
name: evenbetter-app-opportunity-research
description: >
  Full-pipeline iOS App Store opportunity research using built-in `WebSearch` and `WebFetch`
  tools. Discovers underserved niches, analyzes competitor gaps, produces revenue-validated
  top-3 opportunity reports, and writes MVP concept briefs — all through automated web
  research. Use this skill whenever the user wants to find profitable iOS app ideas, research
  App Store categories, analyze competitor apps, validate an app concept, or explore what's
  working in a specific niche. Trigger on phrases like "find app opportunities", "app store
  research", "what app should I build", "research this app category", "find a gap in the app
  store", "iOS app idea", "is this app idea good", "what's trending on the App Store", or any
  question about mobile app market viability. Also trigger when the user mentions wanting to
  build an app but isn't sure what to build, or wants to validate whether a concept has legs.
metadata:
  tags: app-store, research, ios, mobile-app, competitor-analysis, market-research, indie-hacker, startup, app-idea
---

# evenbetter-app-opportunity-research

Research and validate iOS app opportunities using built-in web research tools. The goal is to go from a vague category interest to a validated, ranked shortlist of app concepts the user could realistically build and monetize — without ever opening Xcode.

## Research Toolchain

Two tools cover the entire pipeline. Use the right one for each job:

| Tool | Best At | Use For |
|------|---------|---------|
| **`WebSearch`** | Discovering pages, sources, and signals across the web | Market landscapes, revenue lookups, trend validation, user complaints, competitor comparisons, finding App Store URLs |
| **`WebFetch`** | Reading the full content of a known URL and extracting structured data via a prompt | App Store listing details (rating, price, features), specific blog posts, competitor pages, threads, articles surfaced by `WebSearch` |

Pair them: `WebSearch` finds promising URLs, `WebFetch` reads them. The pattern is `search → triage results → fetch the strongest 3–5 → extract structured data with a prompt`.

### Search query patterns

Build precise queries instead of relying on a "research mode". The key levers are:

- **Site filter:** `site:reddit.com`, `site:apps.apple.com`, `site:sensortower.com`, `site:appfigures.com`, `site:data.ai`, `site:news.ycombinator.com`, `site:producthunt.com`.
- **Year qualifier:** include `2025` or `2026` to bias toward recent results.
- **Sentiment language:** include words like "complaints", "missing features", "wish", "alternative", "vs", "review", "disappointed" to surface opinionated content.
- **Source language:** include "ARR", "MRR", "revenue", "indie", "solo developer", "App Store" to bias toward analytics and indie blogs.

When one search isn't enough, fan out with 3–5 variations and merge the results.

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

Run 3–5 broad `WebSearch` queries to identify the top competitors and the shape of the category.

```
WebSearch: top {category} iOS apps 2026 best
WebSearch: best {category} app iPhone 2025 review
WebSearch: {category} iOS app comparison ranked
WebSearch: most popular {category} apps App Store 2025 2026
```

For each promising article (review roundups, "best of" lists, competitor comparisons), follow up with `WebFetch` to read the full content:

```
WebFetch: <URL of competitor roundup or review article>
  prompt: "List every {category} app mentioned. For each: name, developer, pricing,
           rating, and any quoted strengths or weaknesses."
```

Use these to build the initial competitor list (target 8–12 names).

### 2b. Revenue Signals

Search for revenue data points using `site:` filters that target analytics and indie sources.

```
WebSearch: indie iOS {category} app revenue MRR ARR 2025 2026
WebSearch: {category} app revenue site:sensortower.com
WebSearch: {category} app revenue site:appfigures.com
WebSearch: {category} app revenue site:data.ai
WebSearch: solo developer {category} app income report 2025
```

For each strong hit, pull the exact numbers with `WebFetch`:

```
WebFetch: <URL of revenue/analytics article>
  prompt: "Extract every {category}-related app mentioned with its estimated monthly
           or annual revenue, download numbers, and the source/date of the estimate."
```

### 2c. User Complaints & Sentiment

Reddit, Hacker News, and forums are the richest source of unmet-need signal. Use `site:` filters to target community sources, and language that surfaces opinionated content.

```
WebSearch: best {category} app site:reddit.com disappointed missing
WebSearch: {category} app alternatives site:reddit.com better than
WebSearch: {category} app wish had feature site:reddit.com
WebSearch: {category} app frustrating site:news.ycombinator.com
```

`WebFetch` the threads that look promising:

```
WebFetch: <Reddit / HN thread URL>
  prompt: "Extract every concrete user complaint, missing feature request, and
           'I wish X did Y' comment. Group by app name when possible."
```

These threads are direct gap signals — users describing what they want but can't find.

### 2d. Trend Validation

Check whether the niche is growing or declining by biasing queries toward recent activity.

```
WebSearch: {category} app trend growing 2025 2026
WebSearch: {category} iOS app new launch 2026
WebSearch: {category} app market size growth
WebSearch: new {category} app site:producthunt.com 2025 2026
```

Recent launches signal a growing category. No new entrants in 12+ months could mean the niche is saturated or dead.

### 2e. Deep Niche Research (optional)

For a primary niche worth deep investment, run a structured fan-out. Issue 8–12 targeted `WebSearch` queries across these subtopics, then synthesize:

1. Top competitors with ratings and pricing
2. Common user complaints across apps
3. Underserved user segments
4. Revenue benchmarks for solo/indie developers
5. Recent trends and new entrants
6. Most common monetization strategies

```
WebSearch: top 10 {category} apps ratings pricing 2026
WebSearch: {category} app underserved audience unmet need
WebSearch: indie {category} app monetization subscription
WebSearch: {category} app new entrants 2025 2026 launch
WebSearch: {category} app freemium vs subscription conversion rate
```

`WebFetch` the deepest 3–5 articles for full quotes and numbers. Reserve this for your primary niche — it's the most thorough but slowest pass.

---

## Step 3: Competitor Deep-Dive

Pick the 5–8 most relevant competitors and research each one more closely.

### 3a. App Store Listing Data

If you don't have the exact App Store URL, find it with `WebSearch`:

```
WebSearch: {app name} site:apps.apple.com
```

Then use `WebFetch` to pull structured data from the listing page. The extraction prompt is what gives you a clean, comparable record per competitor.

```
WebFetch: https://apps.apple.com/us/app/{app-slug}/{app-id}
  prompt: "Extract these fields as a structured JSON object:
           - name (string)
           - developer (string)
           - starRating (number)
           - ratingsCount (string, e.g. '12.4K')
           - price (string)
           - inAppPurchases (array of strings with name + price)
           - category (string)
           - descriptionSummary (string, 2–3 sentences)
           - keyFeatures (array of strings, the bullet/list highlights)"
```

This is far more reliable than parsing search snippets — `WebFetch` reads the rendered listing page, and the extraction prompt produces structured output you can compare side-by-side across competitors.

### 3b. Revenue & Business Data per Competitor

```
WebSearch: {app name} app revenue ARR
WebSearch: {app name} app downloads MAU
WebSearch: {app name} indie hacker income report
WebSearch: {app name} app funding raised seed
```

For each strong hit, `WebFetch` the article and pull the exact numbers:

```
WebFetch: <article URL>
  prompt: "Extract the dollar revenue, download count, MAU, and any funding mentioned
           for {app name}, with the date or quarter of the figure and the source it
           cites. Note whether the number is reported, estimated, or self-disclosed."
```

### 3c. Competitor Comparisons & Review Sentiment

```
WebSearch: {app name} review complaints problems
WebSearch: {app name} site:reddit.com problems missing
WebSearch: {app name} vs {competitor name} comparison
WebSearch: {app name} alternatives better
```

`WebFetch` the strongest review and comparison articles:

```
WebFetch: <comparison article URL>
  prompt: "Summarize how {app name} compares to its competitors. List its top 3
           strengths, top 3 weaknesses, the most-cited missing features, and which
           competitor wins for which use case."
```

### Data to collect per competitor

| Field | Tool | Source |
|-------|------|--------|
| Name, rating, price | **`WebFetch`** | App Store listing page |
| Ratings count | **`WebFetch`** | App Store listing page |
| Key features | **`WebFetch`** | App Store description |
| Estimated revenue | **`WebSearch` + `WebFetch`** | SensorTower, AppFigures, indie hacker blogs |
| Top complaints | **`WebSearch` + `WebFetch`** | Reddit, HN, forums, review sites |
| Missing features | **`WebSearch` + `WebFetch`** | Comparison posts, "wish" threads |
| Competitor comparisons | **`WebSearch` + `WebFetch`** | Blog posts, review articles |

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

```markdown
# Top 3 iOS App Opportunities: {Category}

## #1: {Concept Name} — RECOMMENDED
**Pitch:** {What it does in ≤15 words}
**The gap:** {What's missing in the market and why it matters}
**Target user:** {Who they are, what pain they feel, why they'd pay}
**Revenue model:** {Free tier + premium at $X/mo, expected conversion %}
**Revenue path:** {Realistic path to $Y/mo, with assumptions}
**Competition:** {Who exists, why this concept wins}
**Build complexity:** {Low / Medium / High — and what drives complexity}
**Confidence:** {High / Medium / Low — with specific reasoning}

## #2: {Concept Name}
...

## #3: {Concept Name}
...

## Recommendation
{Why #1 is the best bet. Be specific — reference the gap, the revenue signal, and the competitive weakness it exploits.}
```

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

Save the brief as a Markdown file: `{AppConceptName}-brief.md`

---

## Quick Reference: Tool Selection by Task

| Research Task | Tool | Query / Prompt Pattern |
|---------------|------|------------------------|
| Market landscape overview | `WebSearch` → `WebFetch` | `top {category} iOS apps 2026 best`, then fetch the strongest roundups |
| Revenue estimates | `WebSearch` → `WebFetch` | `{category} app revenue site:sensortower.com` (and similar), extract numbers from each result |
| Reddit / forum complaints | `WebSearch` → `WebFetch` | `best {category} app site:reddit.com disappointed missing`, then fetch threads |
| Trend validation | `WebSearch` | `{category} app trend growing 2025 2026` |
| Comprehensive niche report | `WebSearch` (fan-out) → `WebFetch` | 8–12 targeted queries across subtopics, fetch the deepest 3–5 articles |
| App Store listing data | `WebFetch` | URL of listing page + extraction prompt for name / rating / price / features |
| Find App Store URLs | `WebSearch` | `{app name} site:apps.apple.com` |
| Competitor review sentiment | `WebSearch` → `WebFetch` | `{app name} review complaints site:reddit.com`, then fetch threads |
| Competitor revenue / funding | `WebSearch` → `WebFetch` | `{app name} app revenue ARR funding raised`, then fetch articles |
| Competitor comparisons | `WebSearch` → `WebFetch` | `{app name} vs {competitor name} comparison`, then fetch the comparison post |

## Tool equivalents

This skill assumes Claude-style `WebSearch` and `WebFetch`. For other agents, swap in the equivalent built-in tool — the workflow is unchanged.

| Claude command instruction | Codex / other agents equivalent |
| --- | --- |
| `WebSearch` | available web-search tooling |
| `WebFetch` | available page-fetch tooling, or direct URL reader |
| `AskUserQuestion` | `request_user_input` in Plan mode when available, otherwise a concise closed question |

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
1. **Market research notes** — competitor list, revenue signals, trend data
2. **Gap analysis matrix** — feature comparison across top competitors
3. **Top 3 Opportunity Report** — ranked concepts with revenue validation
4. **MVP Concept Brief** — enough detail to start building with any tool or framework

All driven by `WebSearch` + `WebFetch` — the two built-in primitives that work across Claude Code, Codex, and other agent hosts.
