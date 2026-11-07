# Stage 2: Market research

Contents:
- 2a. Market landscape
- 2b. Revenue signals
- 2c. User complaints and sentiment
- 2d. Trend validation
- 2e. Deep niche research (optional)
- Exit

No single search gives the full picture, so run several angles and merge what they find. `Search:` and `Fetch:` below are roles, not tool names: use the highest-tier provider the session has (Research toolchain in SKILL.md). Replace `{year}` with the current year, and add the previous year when results are thin. See `references/query-patterns.md` for the query levers.

Record the source URL next to every fact you keep. The report and brief cite them later, and an uncited figure cannot go into either.

## 2a. Market landscape

Run 3-5 broad searches to find the top competitors and the shape of the category.

```
Search: top {category} iOS apps {year} best
Search: best {category} app iPhone {year} review
Search: {category} iOS app comparison ranked
Search: most popular {category} apps App Store {year}
```

Fetch the most useful roundups, "best of" lists and comparisons in full:

```
Fetch: <URL of competitor roundup or review article>
  prompt: "List every {category} app mentioned. For each: name, developer, pricing,
           rating, and any quoted strengths or weaknesses. Return the source URL alongside
           each extracted fact so I can cite it."
```

Build an initial competitor list of 8-12 names, each with the URL where you found it.

## 2b. Revenue signals

Target analytics and indie sources with `site:` filters.

```
Search: indie iOS {category} app revenue MRR ARR {year}
Search: {category} app revenue site:sensortower.com
Search: {category} app revenue site:appfigures.com
Search: {category} app revenue site:data.ai
Search: solo developer {category} app income report {year}
```

Pull the exact numbers from each strong hit:

```
Fetch: <URL of revenue/analytics article>
  prompt: "Extract every {category}-related app mentioned with its estimated monthly
           or annual revenue, download numbers, and the source/date of the estimate.
           Return the source URL alongside each figure, and mark each number as
           'reported', 'estimated', or 'inferred'."
```

## 2c. User complaints and sentiment

Reddit, Hacker News and forums carry the strongest unmet-need signal. Firecrawl helps here because Reddit's JavaScript rendering defeats plain fetchers.

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

These threads are direct gap signals: people describing what they want and cannot find. Keep the permalink with every quote, because a complaint without one carries no weight in the report.

## 2d. Trend validation

Check whether the niche is growing or shrinking by biasing toward recent activity.

```
Search: {category} app trend growing {year}
Search: {category} iOS app new launch {year}
Search: {category} app market size growth
Search: new {category} app site:producthunt.com {year}
```

Recent launches suggest a growing category. No new entrants in 12 months or more can mean the niche is saturated or fading. Keep the launch URL or Product Hunt listing for each example.

## 2e. Deep niche research (optional)

Reserve this pass for the primary niche: it is the most thorough and the slowest. Run 8-12 targeted searches across these subtopics, then synthesize. Tavily's `tavily_research` fits well here because it batches sub-queries.

1. Top competitors with ratings and pricing
2. Common user complaints across apps
3. Underserved user segments
4. Revenue benchmarks for solo and indie developers
5. Recent trends and new entrants
6. Most common monetization strategies

```
Search: top 10 {category} apps ratings pricing {year}
Search: {category} app underserved audience unmet need
Search: indie {category} app monetization subscription
Search: {category} app new entrants {year} launch
Search: {category} app freemium vs subscription conversion rate
```

Fetch the 3-5 deepest articles for full quotes and numbers, keeping each URL.

## Exit

Append to `research-notes.md`: the competitor list, revenue signals, complaints and trend evidence, each line with its URL, its reported, estimated or inferred label, and a retrieval date for time-sensitive data. Then move to stage 3.
