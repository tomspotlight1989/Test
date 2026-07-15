"""Fetch orchestration, deduplication, and scoring for the UK Energy /last30days pipeline."""
from __future__ import annotations

import math
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from context import RELEVANCE_VOCAB
from sources import SOURCE_REGISTRY, SourceNotConfigured

WINDOW_DAYS = 30


def run_sources(topic: str, since: datetime, only=None):
    """Fetch every registered (or selected) source concurrently.

    Returns (items, status). `status` maps source name -> {"ok": bool, ...}
    so a broken or unconfigured source is visible without killing the run.
    """
    names = only or list(SOURCE_REGISTRY.keys())
    status = {}
    all_items = []

    def _run(name):
        entry = SOURCE_REGISTRY[name]
        return name, entry["fetch"](topic, since)

    with ThreadPoolExecutor(max_workers=min(len(names), 10) or 1) as pool:
        futures = {pool.submit(_run, name): name for name in names}
        for future in as_completed(futures):
            name = futures[future]
            try:
                _, items = future.result()
                status[name] = {"ok": True, "count": len(items)}
                all_items.extend(items)
            except SourceNotConfigured as exc:
                status[name] = {"ok": False, "reason": "not_configured", "detail": str(exc)}
            except Exception as exc:  # noqa: BLE001 - one bad source must not sink the run
                status[name] = {"ok": False, "reason": "error", "detail": str(exc)}
    return all_items, status


def _normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", (title or "").lower()).strip()


def cluster_items(items):
    """Group items that are almost certainly the same story across sources."""
    clusters = []
    seen_urls = {}
    for item in items:
        url_key = item.get("url")
        title_key = _normalize_title(item.get("title"))
        cluster = seen_urls.get(url_key) if url_key else None
        if cluster is None and title_key:
            for c in clusters:
                if title_key == _normalize_title(c["items"][0].get("title")):
                    cluster = c
                    break
        if cluster is None:
            cluster = {"items": []}
            clusters.append(cluster)
        cluster["items"].append(item)
        if url_key:
            seen_urls[url_key] = cluster
    return clusters


def _engagement_score(item):
    return math.log1p(max(item.get("engagement", 0), 0))


def _freshness_score(item, now):
    published = item.get("published")
    if not published:
        return 0.4  # neutral score for undated items (e.g. some GOV.UK/arXiv entries)
    try:
        dt = datetime.fromisoformat(published)
    except ValueError:
        return 0.4
    age_days = max((now - dt).total_seconds() / 86400, 0)
    return math.exp(-age_days / 15)  # roughly halves every ~10 days


def _relevance_score(item, topic):
    haystack = f"{item.get('title', '')} {item.get('snippet', '')}".lower()
    topic_words = re.findall(r"[a-z]+", topic.lower())
    topic_hits = sum(1 for w in topic_words if w in haystack)
    vocab_hits = sum(1 for w in RELEVANCE_VOCAB if w in haystack)
    return topic_hits * 2 + min(vocab_hits, 8) * 0.5


def score_cluster(cluster, topic, now):
    items = cluster["items"]
    best = max(items, key=_engagement_score)
    engagement = sum(_engagement_score(i) for i in items)
    freshness = max(_freshness_score(i, now) for i in items)
    relevance = max(_relevance_score(i, topic) for i in items)
    sources = sorted({i["source"] for i in items})
    score = (engagement + 1) * freshness * (relevance + 1) * (1 + 0.25 * (len(sources) - 1))
    return {
        "score": round(score, 3),
        "representative": best,
        "sources": sources,
        "items": items,
    }


def build_brief_data(topic: str, since: datetime, only=None, top_n: int = 40):
    now = datetime.now(timezone.utc)
    items, status = run_sources(topic, since, only=only)
    clusters = cluster_items(items)
    ranked = sorted(
        (score_cluster(c, topic, now) for c in clusters),
        key=lambda c: c["score"],
        reverse=True,
    )
    return {
        "topic": topic,
        "generated_at": now.isoformat(),
        "window_days": (now - since).days,
        "since": since.isoformat(),
        "source_status": status,
        "total_raw_items": len(items),
        "total_clusters": len(clusters),
        "ranked": ranked[:top_n],
    }
