from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import sources


def _mock_response(json_data=None, content=None):
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    if json_data is not None:
        resp.json.return_value = json_data
    if content is not None:
        resp.content = content
    return resp


@patch("sources.requests.get")
def test_fetch_reddit_normalizes_items(mock_get):
    since = datetime.now(timezone.utc) - timedelta(days=30)
    mock_get.return_value = _mock_response(json_data={
        "data": {"children": [{"data": {
            "title": "Ofgem announces new price cap",
            "permalink": "/r/unitedkingdom/comments/abc/ofgem/",
            "selftext": "", "author": "someone",
            "created_utc": datetime.now(timezone.utc).timestamp(),
            "ups": 120, "num_comments": 45, "subreddit": "unitedkingdom",
        }}]}
    })
    items = sources.fetch_reddit("price cap", since)
    assert len(items) == 1
    assert items[0]["source"] == "reddit"
    assert items[0]["engagement"] == 120
    assert items[0]["url"] == "https://www.reddit.com/r/unitedkingdom/comments/abc/ofgem/"


@patch("sources.requests.get")
def test_fetch_reddit_filters_old_posts(mock_get):
    since = datetime.now(timezone.utc) - timedelta(days=30)
    old_ts = (since - timedelta(days=5)).timestamp()
    mock_get.return_value = _mock_response(json_data={
        "data": {"children": [{"data": {
            "title": "Old post", "permalink": "/r/x/1/", "selftext": "",
            "author": "a", "created_utc": old_ts, "ups": 1, "num_comments": 0,
            "subreddit": "unitedkingdom",
        }}]}
    })
    assert sources.fetch_reddit("price cap", since) == []


@patch("sources.requests.get")
def test_fetch_hackernews_builds_query_and_normalizes(mock_get):
    since = datetime.now(timezone.utc) - timedelta(days=30)
    mock_get.return_value = _mock_response(json_data={"hits": [{
        "title": "UK grid connection reform", "url": "https://example.com/story",
        "objectID": "123", "author": "someone", "points": 88, "num_comments": 12,
        "created_at_i": int(datetime.now(timezone.utc).timestamp()),
    }]})
    items = sources.fetch_hackernews("grid connection reform", since)
    assert len(items) == 1
    assert items[0]["engagement"] == 88
    called_params = mock_get.call_args.kwargs["params"]
    assert "grid connection reform" in called_params["query"]


@patch("sources.requests.get")
def test_fetch_github_uses_token_when_available(mock_get, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    since = datetime.now(timezone.utc) - timedelta(days=30)
    mock_get.return_value = _mock_response(json_data={"items": [{
        "full_name": "org/uk-grid-data", "html_url": "https://github.com/org/uk-grid-data",
        "description": "UK grid open data", "owner": {"login": "org"},
        "pushed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stargazers_count": 42,
    }]})
    items = sources.fetch_github("grid data", since)
    assert items[0]["engagement"] == 42
    headers = mock_get.call_args.kwargs["headers"]
    assert headers["Authorization"] == "Bearer test-token"


def test_fetch_x_raises_without_credentials(monkeypatch):
    monkeypatch.delenv("X_BEARER_TOKEN", raising=False)
    since = datetime.now(timezone.utc) - timedelta(days=30)
    try:
        sources.fetch_x("hydrogen", since)
        assert False, "expected SourceNotConfigured"
    except sources.SourceNotConfigured:
        pass


@patch("sources.requests.get")
def test_fetch_x_uses_bearer_token_when_configured(mock_get, monkeypatch):
    monkeypatch.setenv("X_BEARER_TOKEN", "test-bearer")
    since = datetime.now(timezone.utc) - timedelta(days=30)
    mock_get.return_value = _mock_response(json_data={"data": [{
        "id": "1", "text": "Ofgem price cap update thread",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "public_metrics": {"like_count": 10, "retweet_count": 2}, "author_id": "42",
    }]})
    items = sources.fetch_x("price cap", since)
    assert items[0]["engagement"] == 14  # 10 likes + 2*2 retweets
    assert mock_get.call_args.kwargs["headers"]["Authorization"] == "Bearer test-bearer"


def test_fetch_youtube_raises_without_credentials(monkeypatch):
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    since = datetime.now(timezone.utc) - timedelta(days=30)
    try:
        sources.fetch_youtube("hydrogen", since)
        assert False, "expected SourceNotConfigured"
    except sources.SourceNotConfigured:
        pass


@patch("sources.requests.get")
def test_fetch_polymarket_skips_untitled_events(mock_get):
    since = datetime.now(timezone.utc) - timedelta(days=30)
    mock_get.return_value = _mock_response(json_data={"events": [
        {"title": "Will the UK energy price cap fall in 2026?", "slug": "uk-price-cap-2026", "volume": "1500"},
        {"title": None, "slug": "no-title"},
    ]})
    items = sources.fetch_polymarket("price cap", since)
    assert len(items) == 1
    assert items[0]["engagement"] == 1500
