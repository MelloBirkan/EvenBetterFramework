---
name: evenbetter-app-opportunity-research
description: >
  Full-pipeline iOS App Store opportunity research using Tavily, Exa, and Firecrawl. Discovers
  underserved niches, analyzes competitor gaps, produces revenue-validated top-3 opportunity
  reports, and writes MVP concept briefs — all through automated web research. Use this skill
  whenever the user wants to find profitable iOS app ideas, research App Store categories,
  analyze competitor apps, validate an app concept, or explore what's working in a specific
  niche. Trigger on phrases like "find app opportunities", "app store research", "what app
  should I build", "research this app category", "find a gap in the app store", "iOS app idea",
  "is this app idea good", "what's trending on the App Store", or any question about mobile app
  market viability. Also trigger when the user mentions wanting to build an app but isn't sure
  what to build, or wants to validate whether a concept has legs.
metadata:
  tags: app-store, research, ios, mobile-app, competitor-analysis, market-research, indie-hacker, startup, app-idea
---

# evenbetter-app-opportunity-research

Research and validate iOS app opportunities using three complementary research tools. The goal is to go from a vague category interest to a validated, ranked shortlist of app concepts the user could realistically build and monetize — without ever opening Xcode.

## Research Toolchain

Each tool has a specific role in the pipeline. Use the right tool for each job:

| Tool | Best At | Use For |
|------|---------|---------|
| **Exa** | Semantic/neural search, domain-filtered search, synthesized multi-angle answers | User sentiment, Reddit complaints, competitor comparisons, market landscape overviews |
| **Tavily** | General search with date filtering, revenue data lookups, deep multi-subtopic research | Revenue estimates, trend validation, broad niche research, recent news |
| **Firecrawl** | Structured scraping of specific pages, autonomous multi-site research agents | App Store listing extraction, competitor page scraping, data-heavy deep dives |

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

Run searches across all three tools to build a layered picture of the landscape. No single search gives the full picture — triangulate.

### 2a. Market Landscape Overview → Exa deep_search

Use `Exa:deep_search_exa` for the initial landscape scan. Its multi-angle query expansion and synthesized answers are ideal for open-ended "what's out there" questions.

```
Exa:deep_search_exa
  objective: "Current iOS app market for {niche}: top competitors, their ratings, pricing models, common user complaints, underserved segments, and revenue benchmarks for indie developers"
  numResults: 10
  type: "deep"
```

This gives a synthesized overview with citations — use it to build the initial competitor list.

### 2b. Revenue Signals → Tavily search

Use `Tavily:tavily_search` for revenue data. Tavily's domain filtering and date range support make it best for finding specific data points from analytics sources.

```
Tavily:tavily_search
  query: "indie iOS app revenue {category} ARR MRR"
  search_depth: "advanced"
  time_range: "year"

Tavily:tavily_search
  query: "{category} app revenue estimates sensor tower appfigures"
  search_depth: "advanced"
  include_domains: ["sensortower.com", "appfigures.com", "data.ai", "appmagic.rocks"]
```

### 2c. User Complaints & Sentiment → Exa advanced search

Use `Exa:web_search_advanced_exa` for Reddit and forum complaints. Exa's neural search mode excels at finding opinionated, sentiment-rich content, and its domain filtering cleanly targets community sources.

```
Exa:web_search_advanced_exa
  query: "best {category} app disappointed missing features wish"
  type: "neural"
  includeDomains: ["reddit.com"]
  numResults: 10
  enableHighlights: true
  highlightsQuery: "complaints missing features wish alternative"

Exa:web_search_advanced_exa
  query: "{category} app alternatives better than"
  type: "neural"
  includeDomains: ["reddit.com", "news.ycombinator.com"]
  numResults: 8
  enableHighlights: true
```

Neural search surfaces posts where users describe what they want but can't find — these are direct gap signals.

### 2d. Trend Validation → Tavily search

Use `Tavily:tavily_search` with time filtering to check whether the niche is growing or declining.

```
Tavily:tavily_search
  query: "{category} app trend growing 2025 2026"
  time_range: "year"
  search_depth: "advanced"

Tavily:tavily_search
  query: "{category} iOS app new launches 2025 2026"
  time_range: "month"
```

Recent launches signal a growing category. No new entrants in 12+ months could mean the niche is saturated or dead.

### 2e. Deep Niche Research (optional) → Tavily research

If the niche warrants a thorough investigation, use `Tavily:tavily_research` in pro mode. This autonomous research agent searches across many subtopics and produces a comprehensive report.

```
Tavily:tavily_research
  input: "Research the current iOS app market for {niche}. Cover: top 10 competitors with ratings and pricing, common user complaints across apps, underserved user segments, revenue benchmarks for solo/indie developers, recent trends and new entrants, and the most common monetization strategies."
  model: "pro"
```

Reserve this for your primary niche — it's thorough but slower.

---

## Step 3: Competitor Deep-Dive

Pick the 5–8 most relevant competitors and research each one more closely.

### 3a. App Store Listing Data → Firecrawl scrape

Use `Firecrawl:firecrawl_scrape` with JSON extraction to pull structured data from App Store listing pages. This is far more reliable than parsing search snippets.

```
Firecrawl:firecrawl_scrape
  url: "https://apps.apple.com/us/app/{app-slug}/{app-id}"
  formats: ["json"]
  jsonOptions:
    prompt: "Extract the app name, developer, star rating, number of ratings, price, in-app purchase prices, category, description summary, and key features listed"
    schema:
      type: "object"
      properties:
        name: { type: "string" }
        developer: { type: "string" }
        starRating: { type: "number" }
        ratingsCount: { type: "string" }
        price: { type: "string" }
        inAppPurchases: { type: "array", items: { type: "string" } }
        category: { type: "string" }
        descriptionSummary: { type: "string" }
        keyFeatures: { type: "array", items: { type: "string" } }
```

If you don't have the exact App Store URL, use `Firecrawl:firecrawl_search` first:

```
Firecrawl:firecrawl_search
  query: "{app name} site:apps.apple.com"
  limit: 3
```

### 3b. Revenue & Business Data per Competitor → Tavily search

```
Tavily:tavily_search
  query: "{app name} app revenue ARR"
  search_depth: "advanced"
  max_results: 5

Tavily:tavily_search
  query: "{app name} app funding raised"
  search_depth: "basic"
```

### 3c. Competitor Comparisons & Review Sentiment → Exa advanced search

```
Exa:web_search_advanced_exa
  query: "{app name} review complaints problems"
  type: "neural"
  numResults: 8
  enableHighlights: true
  highlightsQuery: "problems complaints missing slow buggy"

Exa:web_search_advanced_exa
  query: "{app name} vs alternatives comparison"
  type: "neural"
  numResults: 6
  enableSummary: true
```

### Data to collect per competitor

| Field | Best Tool | Source |
|-------|-----------|--------|
| Name, rating, price | **Firecrawl scrape** | App Store listing page |
| Ratings count | **Firecrawl scrape** | App Store listing page |
| Key features | **Firecrawl scrape** | App Store description |
| Estimated revenue | **Tavily search** | SensorTower, AppFigures, press, indie blogs |
| Top complaints | **Exa neural search** | Reddit, forums, review sites |
| Missing features | **Exa neural search** | Comparison posts, "wish" threads |
| Competitor comparisons | **Exa advanced search** | Blog posts, review articles |

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

| Research Task | Tool | Why |
|---------------|------|-----|
| Market landscape overview | `Exa:deep_search_exa` | Multi-angle synthesis with citations |
| Revenue estimates | `Tavily:tavily_search` (domain-filtered) | Targets analytics sources like SensorTower |
| Reddit/forum complaints | `Exa:web_search_advanced_exa` (neural + domain filter) | Semantic matching finds sentiment-rich posts |
| Trend validation | `Tavily:tavily_search` (time-filtered) | Date range filtering catches recency signals |
| Comprehensive niche report | `Tavily:tavily_research` (pro mode) | Deep autonomous research across subtopics |
| App Store listing data | `Firecrawl:firecrawl_scrape` (JSON extraction) | Structured data from actual listing pages |
| Find App Store URLs | `Firecrawl:firecrawl_search` (site:apps.apple.com) | Search operator support for site-scoped search |
| Competitor review sentiment | `Exa:web_search_advanced_exa` (neural + highlights) | Neural search surfaces opinionated content |
| Competitor revenue/funding | `Tavily:tavily_search` (advanced) | Best at finding specific financial data points |
| Competitor comparisons | `Exa:web_search_advanced_exa` (with summaries) | Finds and summarizes "X vs Y" content |

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

All driven by Exa, Tavily, and Firecrawl research — each used where it performs best.
