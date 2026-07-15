# Sources

| Source | Config needed | Notes |
|---|---|---|
| Reddit | none | Multi-subreddit search across `unitedkingdom`, `CasualUK`, `AskUK`, `ukpolitics`, `energy`, `UKPersonalFinance`, `solar`, `electricvehicles`. Ranked by upvotes. |
| Hacker News | none | Algolia HN Search API, ranked by points. |
| GitHub | optional `GITHUB_TOKEN` | Public repo search; a token lifts the rate limit from 10/min to 30/min. Ranked by stars. |
| arXiv | none | Public Atom API, filtered to papers mentioning both the topic and "energy". No engagement metric — ranked by recency only. |
| Polymarket | none | Gamma API event search — surfaces prediction-market odds when a relevant market exists. Ranked by trading volume. |
| Bluesky | none | Public `app.bsky.feed.searchPosts` endpoint, no auth required for read access. Ranked by likes + reposts. |
| GOV.UK | none | Official `gov.uk/search/all.atom` feed — surfaces DESNZ, Ofgem, NSTA, and other government publications and consultations. |
| UK Energy Trade Press | none | RSS from Utility Week, Current±, edie, Solar Power Portal, Smart Energy International. These feeds aren't searchable, so recent entries are pulled and keyword-filtered locally. |
| Techmeme | none | General tech-news aggregator feed, filtered to entries mentioning the topic or "energy". Usually low yield but occasionally relevant (grid software, AI-for-energy, etc). |
| StockTwits | none | Public symbol streams for `NG`, `SSE`, `CNA`, `DRX`, `SHEL`, `BP.`, `UU` (LSE-listed energy stocks), filtered to messages mentioning the topic. |
| X / Twitter | `X_BEARER_TOKEN` | Recent search API v2. Needs an X developer project with at least Basic tier access. |
| YouTube | `YOUTUBE_API_KEY` | Data API v3 search + video statistics, region-biased to GB. Ranked by view count. |
| Perplexity Sonar | `PERPLEXITY_API_KEY` | One extra AI-grounded, cited summary per topic via the Sonar chat-completions endpoint. |
| Brave Search | `BRAVE_API_KEY` | General web-search fallback for anything the other sources miss. |
| TikTok | `SCRAPECREATORS_API_KEY` | Via [scrapecreators.com](https://scrapecreators.com) — TikTok has no official public search API. |
| Instagram | `SCRAPECREATORS_API_KEY` | Same vendor as above. |
| Threads | `SCRAPECREATORS_API_KEY` | Same vendor as above. |
| Pinterest | `SCRAPECREATORS_API_KEY` | Same vendor as above. |
| LinkedIn | `SCRAPECREATORS_API_KEY` | Same vendor as above. |
| Xiaohongshu | `SCRAPECREATORS_API_KEY` | Same vendor as above; low relevance for UK energy specifically but kept for parity with the original last30days source list. |

The six ScrapeCreators-backed connectors (`tiktok`, `instagram`, `threads`, `pinterest`, `linkedin`,
`xiaohongshu`) parse a best-effort response shape based on that vendor's
documented API. It's a third-party paid service that can change its schema;
if one of these starts returning nothing despite a valid key, check
scrapecreators.com's current docs against the field names in `scripts/sources.py`.

Run `python3 scripts/uk_energy_search.py --diagnose` at any time to see which
sources are ready and which need a credential.
