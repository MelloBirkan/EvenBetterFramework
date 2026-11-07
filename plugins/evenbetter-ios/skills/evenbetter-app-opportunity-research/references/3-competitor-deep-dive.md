# Stage 3: Competitor deep-dive

Contents:
- 3a. App Store listing data
- 3b. Revenue and business data
- 3c. Comparisons and review sentiment
- Data to collect per competitor
- Signals to watch for
- Exit

Pick the 5-8 most relevant competitors from stage 2 and research each one closely.

## 3a. App Store listing data

Find the App Store URL if you do not have it:

```
Search: {app name} site:apps.apple.com
```

Fetch the listing and extract a structured record. A schema gives you records you can compare side by side, which is far more reliable than parsing search snippets. Firecrawl's `firecrawl_scrape` with its JSON format and a schema fits best; Exa's `web_fetch_exa`, Tavily's `tavily_extract` or the host's fetch tool with the prompt below also work.

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
           - descriptionSummary (string, 2-3 sentences)
           - keyFeatures (array of strings, the bullet/list highlights)
           - sourceUrl (the App Store listing URL)
           - retrievedAt (today's date in YYYY-MM-DD)"
```

Keep `sourceUrl` and `retrievedAt` on every record so the report can cite them.

## 3b. Revenue and business data

```
Search: {app name} app revenue ARR
Search: {app name} app downloads MAU
Search: {app name} indie hacker income report
Search: {app name} app funding raised seed
```

Fetch each strong hit and pull the exact numbers:

```
Fetch: <article URL>
  prompt: "Extract the dollar revenue, download count, MAU, and any funding mentioned
           for {app name}, with the date or quarter of the figure and the source it
           cites. Note whether the number is reported, estimated, or self-disclosed,
           and include the article URL so I can cite it."
```

When no figure is public, estimate from the proxies in `references/benchmarks.md`, label the result "inferred" and show the arithmetic.

## 3c. Comparisons and review sentiment

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

## Data to collect per competitor

Every field carries its source URL. A row without a citation is incomplete.

| Field | Tool role | Source |
| --- | --- | --- |
| Name, rating, price | Fetch | App Store listing page |
| Ratings count | Fetch | App Store listing page |
| Key features | Fetch | App Store description |
| Estimated revenue | Search, then fetch | Sensor Tower, Appfigures, indie hacker blogs |
| Top complaints | Search, then fetch | Reddit, HN, forums, review sites |
| Missing features | Search, then fetch | Comparison posts, "wish" threads |
| Competitor comparisons | Search, then fetch | Blog posts, review articles |

## Signals to watch for

Green flags (pursue):

- Top competitors have mediocre reviews (3.0-3.5 stars), so there is room to win on quality.
- Solo developers or small teams make meaningful revenue, which shows an indie can win here.
- Users of several apps complain about the same missing feature.
- People clearly pay in this category: $5-15 a month subscriptions exist.
- Apple features apps in the category (Editors' Choice, App of the Day history).

Red flags (avoid, or proceed with care):

- One app dominates with 500K+ ratings: an entrenched incumbent.
- The category needs hardware integration or complex platform APIs.
- Heavy regulation (medical diagnosis, financial trading).
- Every competitor is free, with no clear path to revenue.
- Search interest in the niche is falling year over year.

## Exit

Append one cited record per competitor to `research-notes.md`, plus the green and red flags you found with their sources. Then move to stage 4.
