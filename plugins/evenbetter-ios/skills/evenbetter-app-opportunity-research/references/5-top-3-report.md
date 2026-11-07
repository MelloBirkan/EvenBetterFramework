# Stage 5: Top 3 opportunity report

Write a ranked report of three concepts. Each one stands on its own, so the user can read only #2 and still follow the case.

Every factual claim (competitor names, revenue numbers, complaints, trend signals) carries a citation: an inline Markdown link or a short `[S#]` tag defined in the Sources section. Mark a claim you could not source as `(Estimated, no public source)`.

Base the revenue path on what the developer keeps, not the sticker price. Apple's commission depends on the product type and on Small Business Program membership; `references/benchmarks.md` has the rates with their Apple sources.

## Template

```markdown
# Top 3 iOS App Opportunities: {Category}

## #1: {Concept Name} (recommended)
**Pitch:** {What it does in ≤15 words}
**The gap:** {What's missing in the market and why it matters} [S1][S2]
**Target user:** {Who they are, what pain they feel, why they'd pay}
**Revenue model:** {Free tier + premium at $X/mo, expected conversion %}
**Revenue path:** {Realistic path to $Y/mo after Apple's commission, with assumptions backed by competitor data} [S3]
**Competition:** {Who exists and why this concept wins; link each competitor} [S4][S5]
**Build complexity:** {Low / Medium / High, and what drives the complexity}
**Confidence:** {High / Medium / Low, with specific reasoning and the sources that support it}

## #2: {Concept Name}
...

## #3: {Concept Name}
...

## Recommendation
{Why #1 is the best bet. Be specific: name the gap, the revenue signal and the competitive weakness it exploits, with citations.}

## Sources
- [S1] {Short title}: <https://...> (Retrieved YYYY-MM-DD)
- [S2] {Short title}: <https://...> (Retrieved YYYY-MM-DD)
- [S3] {Short title}: <https://...> (Retrieved YYYY-MM-DD)
- [S4] {App Store listing}: <https://apps.apple.com/...> (Retrieved YYYY-MM-DD)
- [S5] {Reddit thread / blog post}: <https://...> (Retrieved YYYY-MM-DD)
```

## Exit

Save the report as `top-3-report.md` in the niche folder and show it to the user. Then ask one closed question: which concept should get the MVP brief? Options are #1 (Recommended), #2, #3, and "None, research another niche". Choosing is the user's call. Wait for the answer before stage 6, and go back to stage 1 if they pick "None".
