"""Source connectors for the UK Energy /last30days pipeline.

Every fetch_* function takes (topic, since, limit) and returns a list of
normalized item dicts (see `_item`). A connector either returns results or
raises:

  - `SourceNotConfigured` if a required credential is missing (the source is
    real but not set up yet) — the pipeline reports this distinctly from a
    hard failure so `--diagnose` can tell users exactly what to add.
  - any other exception on a genuine fetch/parse error — the pipeline
    catches and logs this per-source so one dead API never sinks a run.

Zero-config sources (Reddit, Hacker News, GitHub, arXiv, Polymarket,
Bluesky, GOV.UK, UK trade press RSS, Techmeme, StockTwits) hit public APIs
that need no credentials. Credentialed sources (X, YouTube, Perplexity,
Brave, and the ScrapeCreators-backed TikTok/Instagram/Threads/Pinterest/
LinkedIn/Xiaohongshu group) degrade gracefully when unset.
"""
from __future__ import annotations

import calendar
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import requests

import config
from context import (
    ENERGY_STOCK_TICKERS,
    TRADE_PRESS_RSS_FEEDS,
    UK_ENERGY_SUBREDDITS,
)

USER_AGENT = "uk-energy-last30days/1.0 (+https://github.com/tomspotlight1989/test)"
TIMEOUT = 15


class SourceNotConfigured(RuntimeError):
    """Raised by a connector when a required credential is missing."""


def _get(url, **kwargs):
    headers = kwargs.pop("headers", {}) or {}
    headers.setdefault("User-Agent", USER_AGENT)
    return requests.get(url, headers=headers, timeout=TIMEOUT, **kwargs)


def _iso(dt: datetime | None) -> str | None:
    return dt.astimezone(timezone.utc).isoformat() if dt else None


def _parse_iso(raw) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except ValueError:
        return None


def _struct_time_to_dt(struct) -> datetime | None:
    if not struct:
        return None
    return datetime.fromtimestamp(calendar.timegm(struct), tz=timezone.utc)


def _item(source, type_, title, url, snippet, author, published, engagement, engagement_label):
    return {
        "source": source,
        "type": type_,
        "title": (title or "").strip(),
        "url": url,
        "snippet": (snippet or "").strip()[:500],
        "author": author,
        "published": _iso(published),
        "engagement": engagement or 0,
        "engagement_label": engagement_label or "",
    }


# --------------------------------------------------------------------------
# Zero-config sources
# --------------------------------------------------------------------------

def fetch_reddit(topic, since, limit=25):
    subs = "+".join(UK_ENERGY_SUBREDDITS)
    resp = _get(
        f"https://www.reddit.com/r/{subs}/search.json",
        params={"q": topic, "restrict_sr": 1, "sort": "top", "t": "month", "limit": limit},
    )
    resp.raise_for_status()
    data = resp.json()
    items = []
    for child in data.get("data", {}).get("children", []):
        d = child.get("data", {})
        created = datetime.fromtimestamp(d.get("created_utc", 0), tz=timezone.utc)
        if created < since:
            continue
        items.append(_item(
            source="reddit", type_="post",
            title=d.get("title"),
            url="https://www.reddit.com" + d.get("permalink", ""),
            snippet=d.get("selftext") or d.get("title"),
            author=d.get("author"),
            published=created,
            engagement=d.get("ups", 0),
            engagement_label=f"{d.get('ups', 0)} upvotes · {d.get('num_comments', 0)} comments · r/{d.get('subreddit')}",
        ))
    return items


def fetch_hackernews(topic, since, limit=25):
    resp = _get(
        "https://hn.algolia.com/api/v1/search",
        params={
            "query": f"{topic} UK energy",
            "tags": "story",
            "numericFilters": f"created_at_i>{int(since.timestamp())}",
            "hitsPerPage": limit,
        },
    )
    resp.raise_for_status()
    data = resp.json()
    items = []
    for hit in data.get("hits", []):
        created = datetime.fromtimestamp(hit.get("created_at_i", 0), tz=timezone.utc)
        items.append(_item(
            source="hackernews", type_="story",
            title=hit.get("title"),
            url=hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
            snippet=hit.get("story_text") or hit.get("title"),
            author=hit.get("author"),
            published=created,
            engagement=hit.get("points", 0),
            engagement_label=f"{hit.get('points', 0)} points · {hit.get('num_comments', 0)} comments",
        ))
    return items


def fetch_github(topic, since, limit=25):
    headers = {"Accept": "application/vnd.github+json"}
    token = config.credential("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    since_str = since.strftime("%Y-%m-%d")
    query = f"{topic} energy in:name,description,readme pushed:>={since_str}"
    resp = _get(
        "https://api.github.com/search/repositories",
        headers=headers,
        params={"q": query, "sort": "updated", "order": "desc", "per_page": limit},
    )
    resp.raise_for_status()
    data = resp.json()
    items = []
    for repo in data.get("items", []):
        pushed = datetime.strptime(repo["pushed_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        items.append(_item(
            source="github", type_="repo",
            title=repo.get("full_name"),
            url=repo.get("html_url"),
            snippet=repo.get("description"),
            author=(repo.get("owner") or {}).get("login"),
            published=pushed,
            engagement=repo.get("stargazers_count", 0),
            engagement_label=f"{repo.get('stargazers_count', 0)} stars",
        ))
    return items


def fetch_arxiv(topic, since, limit=20):
    resp = _get(
        "http://export.arxiv.org/api/query",
        params={
            "search_query": f'all:"{topic}" AND all:energy',
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": limit,
        },
    )
    resp.raise_for_status()
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(resp.content)
    items = []
    for entry in root.findall("atom:entry", ns):
        published_raw = entry.findtext("atom:published", default="", namespaces=ns)
        try:
            published = datetime.strptime(published_raw, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if published < since:
            continue
        authors = [a.findtext("atom:name", namespaces=ns) for a in entry.findall("atom:author", ns)]
        items.append(_item(
            source="arxiv", type_="paper",
            title=entry.findtext("atom:title", namespaces=ns),
            url=entry.findtext("atom:id", namespaces=ns),
            snippet=entry.findtext("atom:summary", namespaces=ns),
            author=", ".join(a for a in authors if a),
            published=published,
            engagement=0,
            engagement_label="arXiv preprint",
        ))
    return items


def fetch_polymarket(topic, since, limit=15):
    resp = _get(
        "https://gamma-api.polymarket.com/events",
        params={"search": topic, "limit": limit, "closed": "false"},
    )
    resp.raise_for_status()
    data = resp.json()
    events = data if isinstance(data, list) else data.get("events", [])
    items = []
    for ev in events:
        created = _parse_iso(ev.get("startDate") or ev.get("createdAt"))
        volume = float(ev.get("volume") or 0)
        title = ev.get("title")
        if not title:
            continue
        items.append(_item(
            source="polymarket", type_="market",
            title=title,
            url=f"https://polymarket.com/event/{ev.get('slug')}" if ev.get("slug") else None,
            snippet=ev.get("description"),
            author=None,
            published=created,
            engagement=int(volume),
            engagement_label=f"${volume:,.0f} traded",
        ))
    return items


def fetch_bluesky(topic, since, limit=25):
    resp = _get(
        "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts",
        params={"q": f"{topic} energy UK", "limit": limit, "sort": "top"},
    )
    resp.raise_for_status()
    data = resp.json()
    items = []
    for post in data.get("posts", []):
        record = post.get("record", {})
        created = _parse_iso(record.get("createdAt"))
        if created and created < since:
            continue
        author = (post.get("author") or {}).get("handle")
        uri = post.get("uri", "")
        rkey = uri.rsplit("/", 1)[-1] if uri else ""
        likes = post.get("likeCount", 0)
        reposts = post.get("repostCount", 0)
        items.append(_item(
            source="bluesky", type_="post",
            title=(record.get("text") or "")[:120],
            url=f"https://bsky.app/profile/{author}/post/{rkey}" if author and rkey else None,
            snippet=record.get("text"),
            author=author,
            published=created,
            engagement=likes + reposts,
            engagement_label=f"{likes} likes · {reposts} reposts",
        ))
    return items


def fetch_govuk(topic, since, limit=20):
    import feedparser

    resp = _get(
        "https://www.gov.uk/search/all.atom",
        params={"keywords": f"{topic} energy", "order": "updated-newest", "count": limit},
    )
    resp.raise_for_status()
    parsed = feedparser.parse(resp.content)
    items = []
    for entry in parsed.entries[:limit]:
        published = _struct_time_to_dt(entry.get("updated_parsed") or entry.get("published_parsed"))
        if published and published < since:
            continue
        items.append(_item(
            source="govuk", type_="publication",
            title=entry.get("title"),
            url=entry.get("link"),
            snippet=entry.get("summary"),
            author=entry.get("author"),
            published=published,
            engagement=0,
            engagement_label="GOV.UK publication",
        ))
    return items


def fetch_trade_press(topic, since, limit=10):
    import feedparser

    topic_words = [w for w in topic.lower().split() if len(w) > 2]
    items = []
    for name, feed_url in TRADE_PRESS_RSS_FEEDS.items():
        try:
            resp = _get(feed_url)
            resp.raise_for_status()
        except requests.RequestException:
            continue
        parsed = feedparser.parse(resp.content)
        for entry in parsed.entries:
            published = _struct_time_to_dt(entry.get("published_parsed") or entry.get("updated_parsed"))
            if published and published < since:
                continue
            haystack = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
            if not any(w in haystack for w in topic_words):
                continue
            items.append(_item(
                source="trade_press", type_="article",
                title=entry.get("title"),
                url=entry.get("link"),
                snippet=entry.get("summary"),
                author=name,
                published=published,
                engagement=0,
                engagement_label=name,
            ))
            if len(items) >= limit:
                return items
    return items


def fetch_techmeme(topic, since, limit=10):
    import feedparser

    resp = _get("https://www.techmeme.com/feed.xml")
    resp.raise_for_status()
    parsed = feedparser.parse(resp.content)
    topic_lower = topic.lower()
    items = []
    for entry in parsed.entries:
        published = _struct_time_to_dt(entry.get("published_parsed"))
        if published and published < since:
            continue
        haystack = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
        if topic_lower not in haystack and "energy" not in haystack:
            continue
        items.append(_item(
            source="techmeme", type_="article",
            title=entry.get("title"),
            url=entry.get("link"),
            snippet=entry.get("summary"),
            author="Techmeme",
            published=published,
            engagement=0,
            engagement_label="Techmeme",
        ))
        if len(items) >= limit:
            break
    return items


def fetch_stocktwits(topic, since, limit=10):
    items = []
    for ticker in ENERGY_STOCK_TICKERS:
        try:
            resp = _get(f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json")
            resp.raise_for_status()
        except requests.RequestException:
            continue
        data = resp.json()
        for msg in data.get("messages", []):
            created = _parse_iso(msg.get("created_at"))
            if created and created < since:
                continue
            body = msg.get("body", "")
            if topic.lower() not in body.lower():
                continue
            likes = (msg.get("likes") or {}).get("total", 0)
            items.append(_item(
                source="stocktwits", type_="post",
                title=body[:120],
                url=f"https://stocktwits.com/message/{msg.get('id')}",
                snippet=body,
                author=(msg.get("user") or {}).get("username"),
                published=created,
                engagement=likes,
                engagement_label=f"{likes} likes · ${ticker}",
            ))
            if len(items) >= limit:
                return items
    return items


# --------------------------------------------------------------------------
# Credentialed sources
# --------------------------------------------------------------------------

def fetch_x(topic, since, limit=25):
    token = config.credential("X_BEARER_TOKEN")
    if not token:
        raise SourceNotConfigured("Set X_BEARER_TOKEN to enable X/Twitter search.")
    query = f"{topic} (energy OR Ofgem OR electricity OR gas) lang:en -is:retweet"
    resp = _get(
        "https://api.twitter.com/2/tweets/search/recent",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "query": query,
            "max_results": min(max(limit, 10), 100),
            "start_time": since.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tweet.fields": "created_at,public_metrics,author_id",
        },
    )
    resp.raise_for_status()
    data = resp.json()
    items = []
    for tw in data.get("data", []):
        metrics = tw.get("public_metrics", {})
        engagement = metrics.get("like_count", 0) + metrics.get("retweet_count", 0) * 2
        items.append(_item(
            source="x", type_="post",
            title=(tw.get("text") or "")[:120],
            url=f"https://x.com/i/web/status/{tw.get('id')}",
            snippet=tw.get("text"),
            author=tw.get("author_id"),
            published=_parse_iso(tw.get("created_at")),
            engagement=engagement,
            engagement_label=f"{metrics.get('like_count', 0)} likes · {metrics.get('retweet_count', 0)} reposts",
        ))
    return items


def fetch_youtube(topic, since, limit=15):
    api_key = config.credential("YOUTUBE_API_KEY")
    if not api_key:
        raise SourceNotConfigured("Set YOUTUBE_API_KEY to enable YouTube search.")
    resp = _get(
        "https://www.googleapis.com/youtube/v3/search",
        params={
            "key": api_key, "part": "snippet", "q": f"{topic} UK energy",
            "type": "video", "order": "viewCount",
            "publishedAfter": since.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "maxResults": limit, "regionCode": "GB",
        },
    )
    resp.raise_for_status()
    data = resp.json()
    video_ids = [it["id"]["videoId"] for it in data.get("items", []) if "videoId" in it.get("id", {})]
    stats = {}
    if video_ids:
        stats_resp = _get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={"key": api_key, "part": "statistics", "id": ",".join(video_ids)},
        )
        stats_resp.raise_for_status()
        for v in stats_resp.json().get("items", []):
            stats[v["id"]] = v.get("statistics", {})
    items = []
    for it in data.get("items", []):
        vid = it.get("id", {}).get("videoId")
        snippet = it.get("snippet", {})
        views = int(stats.get(vid, {}).get("viewCount", 0)) if vid else 0
        items.append(_item(
            source="youtube", type_="video",
            title=snippet.get("title"),
            url=f"https://www.youtube.com/watch?v={vid}" if vid else None,
            snippet=snippet.get("description"),
            author=snippet.get("channelTitle"),
            published=_parse_iso(snippet.get("publishedAt")),
            engagement=views,
            engagement_label=f"{views:,} views",
        ))
    return items


def fetch_perplexity(topic, since, limit=1):
    api_key = config.credential("PERPLEXITY_API_KEY")
    if not api_key:
        raise SourceNotConfigured("Set PERPLEXITY_API_KEY to enable Perplexity/Sonar grounding.")
    resp = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": "sonar",
            "messages": [{
                "role": "user",
                "content": f"What has happened in the last 30 days regarding {topic} in the UK energy industry? Cite sources.",
            }],
        },
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    choice = (data.get("choices") or [{}])[0]
    content = choice.get("message", {}).get("content", "")
    if not content:
        return []
    citations = data.get("citations", [])
    return [_item(
        source="perplexity", type_="summary",
        title=f"Perplexity Sonar grounding: {topic}",
        url=citations[0] if citations else None,
        snippet=content,
        author="Perplexity Sonar",
        published=datetime.now(timezone.utc),
        engagement=0,
        engagement_label="AI-grounded summary",
    )]


def fetch_brave(topic, since, limit=15):
    api_key = config.credential("BRAVE_API_KEY")
    if not api_key:
        raise SourceNotConfigured("Set BRAVE_API_KEY to enable Brave web search fallback.")
    resp = _get(
        "https://api.search.brave.com/res/v1/web/search",
        headers={"X-Subscription-Token": api_key, "Accept": "application/json"},
        params={"q": f"{topic} UK energy", "count": limit, "freshness": "pm"},
    )
    resp.raise_for_status()
    data = resp.json()
    items = []
    for r in data.get("web", {}).get("results", []):
        items.append(_item(
            source="brave", type_="article",
            title=r.get("title"),
            url=r.get("url"),
            snippet=r.get("description"),
            author=(r.get("profile") or {}).get("name"),
            published=None,
            engagement=0,
            engagement_label=r.get("age") or "web result",
        ))
    return items


def _scrapecreators_search(platform, query, limit):
    """Shared client for the ScrapeCreators-backed platforms.

    TikTok/Instagram/Threads/Pinterest/LinkedIn/Xiaohongshu have no official
    public search API, which is why the original last30days project pays for
    a third-party scraping API (scrapecreators.com) instead. Field names below
    are best-effort against that vendor's documented shape as of writing —
    check docs/SETUP.md and the vendor's live docs if a platform starts
    returning empty results.
    """
    api_key = config.credential("SCRAPECREATORS_API_KEY")
    if not api_key:
        raise SourceNotConfigured(
            f"Set SCRAPECREATORS_API_KEY to enable {platform} search (via scrapecreators.com)."
        )
    resp = _get(
        f"https://api.scrapecreators.com/v1/{platform}/search",
        headers={"x-api-key": api_key},
        params={"query": query, "limit": limit},
    )
    resp.raise_for_status()
    return resp.json().get("results", [])


def fetch_tiktok(topic, since, limit=15):
    results = _scrapecreators_search("tiktok", f"{topic} UK energy", limit)
    items = []
    for r in results:
        created = _parse_iso(r.get("create_time"))
        if created and created < since:
            continue
        stats = r.get("stats", {})
        engagement = stats.get("diggCount", 0) + stats.get("shareCount", 0)
        items.append(_item(
            source="tiktok", type_="video",
            title=(r.get("desc") or "")[:120],
            url=r.get("url"),
            snippet=r.get("desc"),
            author=(r.get("author") or {}).get("uniqueId"),
            published=created,
            engagement=engagement,
            engagement_label=f"{stats.get('diggCount', 0)} likes · {stats.get('playCount', 0)} views",
        ))
    return items


def fetch_instagram(topic, since, limit=15):
    results = _scrapecreators_search("instagram", f"{topic} UK energy", limit)
    items = []
    for r in results:
        created = _parse_iso(r.get("taken_at") or r.get("created_at"))
        if created and created < since:
            continue
        likes = r.get("like_count", 0)
        comments = r.get("comment_count", 0)
        items.append(_item(
            source="instagram", type_="post",
            title=(r.get("caption") or "")[:120],
            url=r.get("url") or r.get("permalink"),
            snippet=r.get("caption"),
            author=r.get("username"),
            published=created,
            engagement=likes + comments,
            engagement_label=f"{likes} likes · {comments} comments",
        ))
    return items


def fetch_threads(topic, since, limit=15):
    results = _scrapecreators_search("threads", f"{topic} UK energy", limit)
    items = []
    for r in results:
        created = _parse_iso(r.get("taken_at") or r.get("created_at"))
        if created and created < since:
            continue
        likes = r.get("like_count", 0)
        items.append(_item(
            source="threads", type_="post",
            title=(r.get("text") or "")[:120],
            url=r.get("url"),
            snippet=r.get("text"),
            author=r.get("username"),
            published=created,
            engagement=likes,
            engagement_label=f"{likes} likes",
        ))
    return items


def fetch_pinterest(topic, since, limit=15):
    results = _scrapecreators_search("pinterest", f"{topic} UK energy", limit)
    items = []
    for r in results:
        saves = r.get("save_count", 0)
        items.append(_item(
            source="pinterest", type_="pin",
            title=r.get("title") or (r.get("description") or "")[:120],
            url=r.get("url"),
            snippet=r.get("description"),
            author=r.get("author"),
            published=_parse_iso(r.get("created_at")),
            engagement=saves,
            engagement_label=f"{saves} saves",
        ))
    return items


def fetch_linkedin(topic, since, limit=15):
    results = _scrapecreators_search("linkedin", f"{topic} UK energy", limit)
    items = []
    for r in results:
        created = _parse_iso(r.get("posted_at") or r.get("created_at"))
        if created and created < since:
            continue
        reactions = r.get("reaction_count", 0)
        items.append(_item(
            source="linkedin", type_="post",
            title=(r.get("text") or "")[:120],
            url=r.get("url"),
            snippet=r.get("text"),
            author=r.get("author_name"),
            published=created,
            engagement=reactions,
            engagement_label=f"{reactions} reactions",
        ))
    return items


def fetch_xiaohongshu(topic, since, limit=10):
    results = _scrapecreators_search("xiaohongshu", topic, limit)
    items = []
    for r in results:
        likes = r.get("liked_count", 0)
        items.append(_item(
            source="xiaohongshu", type_="post",
            title=(r.get("title") or "")[:120],
            url=r.get("url"),
            snippet=r.get("desc"),
            author=r.get("author"),
            published=_parse_iso(r.get("created_at")),
            engagement=likes,
            engagement_label=f"{likes} likes",
        ))
    return items


# --------------------------------------------------------------------------
# Registry
# --------------------------------------------------------------------------

SOURCE_REGISTRY = {
    "reddit": {"fetch": fetch_reddit, "zero_config": True, "label": "Reddit"},
    "hackernews": {"fetch": fetch_hackernews, "zero_config": True, "label": "Hacker News"},
    "github": {"fetch": fetch_github, "zero_config": True, "label": "GitHub"},
    "arxiv": {"fetch": fetch_arxiv, "zero_config": True, "label": "arXiv"},
    "polymarket": {"fetch": fetch_polymarket, "zero_config": True, "label": "Polymarket"},
    "bluesky": {"fetch": fetch_bluesky, "zero_config": True, "label": "Bluesky"},
    "govuk": {"fetch": fetch_govuk, "zero_config": True, "label": "GOV.UK"},
    "trade_press": {"fetch": fetch_trade_press, "zero_config": True, "label": "UK Energy Trade Press"},
    "techmeme": {"fetch": fetch_techmeme, "zero_config": True, "label": "Techmeme"},
    "stocktwits": {"fetch": fetch_stocktwits, "zero_config": True, "label": "StockTwits"},
    "x": {"fetch": fetch_x, "zero_config": False, "label": "X / Twitter", "env_var": "X_BEARER_TOKEN"},
    "youtube": {"fetch": fetch_youtube, "zero_config": False, "label": "YouTube", "env_var": "YOUTUBE_API_KEY"},
    "perplexity": {"fetch": fetch_perplexity, "zero_config": False, "label": "Perplexity Sonar", "env_var": "PERPLEXITY_API_KEY"},
    "brave": {"fetch": fetch_brave, "zero_config": False, "label": "Brave Search", "env_var": "BRAVE_API_KEY"},
    "tiktok": {"fetch": fetch_tiktok, "zero_config": False, "label": "TikTok", "env_var": "SCRAPECREATORS_API_KEY"},
    "instagram": {"fetch": fetch_instagram, "zero_config": False, "label": "Instagram", "env_var": "SCRAPECREATORS_API_KEY"},
    "threads": {"fetch": fetch_threads, "zero_config": False, "label": "Threads", "env_var": "SCRAPECREATORS_API_KEY"},
    "pinterest": {"fetch": fetch_pinterest, "zero_config": False, "label": "Pinterest", "env_var": "SCRAPECREATORS_API_KEY"},
    "linkedin": {"fetch": fetch_linkedin, "zero_config": False, "label": "LinkedIn", "env_var": "SCRAPECREATORS_API_KEY"},
    "xiaohongshu": {"fetch": fetch_xiaohongshu, "zero_config": False, "label": "Xiaohongshu", "env_var": "SCRAPECREATORS_API_KEY"},
}
