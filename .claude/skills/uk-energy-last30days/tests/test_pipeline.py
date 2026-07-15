from datetime import datetime, timedelta, timezone

from pipeline import cluster_items, run_sources, score_cluster
from sources import SourceNotConfigured


def _item(source, title, url, engagement=10, published=None):
    return {
        "source": source,
        "type": "post",
        "title": title,
        "url": url,
        "snippet": title,
        "author": "someone",
        "published": (published or datetime.now(timezone.utc)).isoformat(),
        "engagement": engagement,
        "engagement_label": str(engagement),
    }


def test_cluster_items_merges_same_url():
    items = [
        _item("reddit", "Ofgem raises price cap", "https://example.com/a"),
        _item("hackernews", "Ofgem raises price cap", "https://example.com/a"),
    ]
    clusters = cluster_items(items)
    assert len(clusters) == 1
    assert len(clusters[0]["items"]) == 2


def test_cluster_items_merges_same_title_different_source():
    items = [
        _item("reddit", "National Grid ESO renamed to NESO", "https://a.example/1"),
        _item("govuk", "National Grid ESO renamed to NESO", "https://b.example/2"),
    ]
    clusters = cluster_items(items)
    assert len(clusters) == 1


def test_cluster_items_keeps_distinct_stories_separate():
    items = [
        _item("reddit", "Hydrogen strategy update", "https://a.example/1"),
        _item("reddit", "Offshore wind CfD auction results", "https://a.example/2"),
    ]
    clusters = cluster_items(items)
    assert len(clusters) == 2


def test_score_cluster_rewards_cross_source_and_engagement():
    now = datetime.now(timezone.utc)
    single = {"items": [
        _item("reddit", "Energy price cap change", "https://a.example/1", engagement=5, published=now),
    ]}
    multi = {"items": [
        _item("reddit", "Energy price cap change big story", "https://b.example/1", engagement=50, published=now),
        _item("govuk", "Energy price cap change big story", "https://b.example/1", engagement=0, published=now),
    ]}
    single_score = score_cluster(single, "energy price cap", now)
    multi_score = score_cluster(multi, "energy price cap", now)
    assert multi_score["score"] > single_score["score"]


def test_score_cluster_prefers_fresher_items():
    now = datetime.now(timezone.utc)
    fresh = {"items": [_item("reddit", "Grid reform news", "https://a.example/1", engagement=10, published=now)]}
    stale = {"items": [_item("reddit", "Grid reform news old", "https://a.example/2", engagement=10, published=now - timedelta(days=25))]}
    assert score_cluster(fresh, "grid reform", now)["score"] > score_cluster(stale, "grid reform", now)["score"]


def test_run_sources_isolates_failures(monkeypatch):
    import pipeline

    def boom(topic, since):
        raise RuntimeError("network exploded")

    def ok(topic, since):
        return [_item("reddit", "fine", "https://ok.example/1")]

    monkeypatch.setitem(pipeline.SOURCE_REGISTRY, "reddit", {"fetch": ok, "zero_config": True, "label": "Reddit"})
    monkeypatch.setitem(pipeline.SOURCE_REGISTRY, "github", {"fetch": boom, "zero_config": True, "label": "GitHub"})

    since = datetime.now(timezone.utc) - timedelta(days=30)
    items, status = run_sources("energy", since, only=["reddit", "github"])

    assert status["reddit"] == {"ok": True, "count": 1}
    assert status["github"]["ok"] is False
    assert status["github"]["reason"] == "error"
    assert len(items) == 1


def test_run_sources_reports_not_configured(monkeypatch):
    import pipeline

    def needs_key(topic, since):
        raise SourceNotConfigured("Set X_BEARER_TOKEN")

    monkeypatch.setitem(pipeline.SOURCE_REGISTRY, "x", {"fetch": needs_key, "zero_config": False, "label": "X"})
    since = datetime.now(timezone.utc) - timedelta(days=30)
    items, status = run_sources("energy", since, only=["x"])
    assert status["x"]["reason"] == "not_configured"
    assert items == []
