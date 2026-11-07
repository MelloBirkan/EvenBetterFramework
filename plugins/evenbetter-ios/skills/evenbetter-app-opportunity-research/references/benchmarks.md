# Benchmarks and priors

Contents:
- How to use this file
- App Store commission (verified)
- Revenue estimation proxies
- Revenue ranges by app type
- Pricing sweet spots
- Marketing channels for indie iOS apps

## How to use this file

The commission section is checked against Apple's pages, with its sources listed. Everything after it is a rough prior carried over from earlier versions of this skill and not re-verified. Use the priors to sanity-check a number or to decide what to look up next. They are never a source: a figure from this file does not go into a report or brief as fact. Find a current, cited source, or label the number "inferred" and show the arithmetic.

## App Store commission (verified)

Checked 2026-11-07. Re-check before modelling revenue, because Apple changes these terms.

- Auto-renewable subscriptions: the developer receives 70% of the price, minus taxes, during a subscriber's first year of paid service, and 85% after that year. Source: <https://developer.apple.com/app-store/subscriptions/>
- App Store Small Business Program: a 15% commission on paid apps and in-app purchases. Developers with up to USD 1 million in proceeds in the prior calendar year, and developers new to the App Store, can qualify. Members receive 85% on subscriptions from the first year. Developers on Apple's alternative terms in the EU have different rates. Sources: <https://developer.apple.com/app-store/small-business-program/>, <https://developer.apple.com/app-store/subscriptions/>
- Outside the program, paid apps and one-time in-app purchases carry the standard 30% commission. Source: Apple's November 2025 study "What Happens to App Prices when Developers Pay Lower Commission Fees?", <https://developer.apple.com/download/files/DMA-Study-Nov-2025.pdf> ("Apple's standard business terms include a commission rate of 30%").
- Storefront rules differ: apps on the US storefront may link to other purchase methods, and some other regions offer a StoreKit External Purchase Link Entitlement (App Review Guidelines 3.1.1 and 3.1.1(a), <https://developer.apple.com/app-store/review/guidelines/>). Check the current terms before modelling link-out revenue.
- Apple Developer Program membership costs USD 99 a year. Source: <https://developer.apple.com/programs/>

## Revenue estimation proxies

When exact revenue is not public:

- `rating_count × 50-80 ≈ approximate total installs` (App Store rule of thumb)
- 2-5% of free users convert to paid on a freemium model.
- The average consumer iOS subscription is about $5-7 a month.
- A niche utility by a solo developer can make $1-5K a month; a well-executed category app can make $5-30K a month.

## Revenue ranges by app type

The example apps are leads to research, not benchmarks. Look up their current revenue and cite it before comparing.

| App type | Solo dev range | Small team | Example apps to look up |
| --- | --- | --- | --- |
| Niche utility | $1-5K/mo | $5-20K/mo | Rootd |
| Habit / tracker | $5-15K/mo | $20-80K/mo | Daylio |
| Gamified self-care | $10-50K/mo | $100K+/mo | Finch |
| Meditation / wellness | $5-20K/mo | $50-500K/mo | Calm |
| Productivity | $3-10K/mo | $20-100K/mo | Various |
| AI-powered tool | $5-30K/mo | $50-300K/mo | Emerging category |

## Pricing sweet spots

| Tier | Monthly | Annual | Best for |
| --- | --- | --- | --- |
| Impulse | $2.99-4.99 | $19.99-29.99 | Simple utilities, widgets |
| Standard | $5.99-6.99 | $34.99-44.99 | Most indie apps |
| Premium | $9.99-14.99 | $59.99-99.99 | AI-heavy or professional tools |

## Marketing channels for indie iOS apps

| Channel | Fit | Cost | Speed |
| --- | --- | --- | --- |
| TikTok organic | Consumer, visual demos | Free | 2-4 weeks |
| Reddit niche subs | Technical, niche audiences | Free | 1-2 weeks |
| Product Hunt | Productivity, dev tools | Free | Launch day spike |
| Apple Ads (formerly Apple Search Ads) | Any iOS app | Cost per tap, set by auction; varies widely by keyword and country | Immediate |
| Instagram Reels | Lifestyle, wellness | Free | 2-6 weeks |
| X (Twitter) indie dev community | Dev tools, indie community | Free | Ongoing |

Apple Ads places ads in App Store search results, the Search tab, the Today tab and on product pages, and charges per tap (<https://ads.apple.com/app-store>, checked 2026-11-07).
