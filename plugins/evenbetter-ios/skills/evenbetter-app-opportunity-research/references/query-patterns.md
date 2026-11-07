# Query patterns and tool choice by task

Contents:
- Search and fetch roles
- Query levers
- Tool choice by research task

## Search and fetch roles

| Role | What it does | Candidates |
| --- | --- | --- |
| Search | Finds URLs and signals across the web | `web_search_exa`, `tavily_search`, `tavily_research`, `firecrawl_search`, `ref_search_documentation`, host web search |
| Fetch | Reads a known URL and extracts structured data | `web_fetch_exa`, `tavily_extract`, `firecrawl_scrape`, `ref_read_url`, host fetch |

The pattern is: search, triage the results, fetch the strongest 3-5, then extract structured data with a prompt or schema.

## Query levers

Build precise queries instead of relying on a "research mode". These levers work across Exa, Tavily, Firecrawl and the host's own web search:

- **Site filter:** `site:reddit.com`, `site:apps.apple.com`, `site:sensortower.com`, `site:appfigures.com`, `site:data.ai`, `site:news.ycombinator.com`, `site:producthunt.com`. Exa also accepts these as domain filters.
- **Year qualifier:** add the current year, and the previous one when results are thin, to bias toward recent results.
- **Sentiment language:** "complaints", "missing features", "wish", "alternative", "vs", "review", "disappointed" surface opinionated content.
- **Source language:** "ARR", "MRR", "revenue", "indie", "solo developer", "App Store" bias toward analytics and indie blogs.

When one search is not enough, fan out with 3-5 variations and merge the results. Record the result URL for every fact you keep.

## Tool choice by research task

The tool role is generic. Pick the highest-tier provider available (Research toolchain in SKILL.md).

| Research task | Tool role | Query or prompt pattern |
| --- | --- | --- |
| Market landscape overview | Search, then fetch | `top {category} iOS apps {year} best`, then fetch the strongest roundups |
| Revenue estimates | Search, then fetch | `{category} app revenue site:sensortower.com` and similar; extract numbers and URL from each result |
| Reddit and forum complaints | Search, then fetch | `best {category} app site:reddit.com disappointed missing`, then fetch threads (Firecrawl handles Reddit's JavaScript well) |
| Trend validation | Search | `{category} app trend growing {year}` |
| Full niche report | Search fan-out, then fetch | 8-12 targeted queries across subtopics, fetch the deepest 3-5 articles (Tavily `tavily_research` if available) |
| App Store listing data | Fetch | Listing URL plus an extraction schema for name, rating, price, features (Firecrawl `firecrawl_scrape` with JSON format) |
| Find App Store URLs | Search | `{app name} site:apps.apple.com` |
| Competitor review sentiment | Search, then fetch | `{app name} review complaints site:reddit.com`, then fetch threads |
| Competitor revenue and funding | Search, then fetch | `{app name} app revenue ARR funding raised`, then fetch articles |
| Competitor comparisons | Search, then fetch | `{app name} vs {competitor name} comparison`, then fetch the comparison post |
| Platform or SDK angle | Search, then fetch | Ref `ref_search_documentation` for API surfaces competitors integrate with |
