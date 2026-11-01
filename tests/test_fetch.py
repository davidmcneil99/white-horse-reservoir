import feedparser
from unittest.mock import patch, Mock
from generator.fetch import fetch_rss, detect_page_change


def test_fetch_rss_returns_items():
    rss = """<?xml version="1.0"?><rss version="2.0"><channel>
    <item><title>Test</title><link>https://example.com</link>
    <pubDate>Mon, 01 Nov 2026 00:00:00 GMT</pubDate></item></channel></rss>"""
    parsed = feedparser.parse(rss)
    with patch("generator.fetch.feedparser") as mock_fp:
        mock_fp.parse.return_value = parsed
        items = fetch_rss("https://example.com/feed", "Test Source")
    assert len(items) == 1
    assert items[0]["title"] == "Test"
    assert items[0]["url"] == "https://example.com"


def test_fetch_rss_empty_feed_returns_empty_list():
    empty = """<?xml version="1.0"?><rss version="2.0"><channel></channel></rss>"""
    parsed = feedparser.parse(empty)
    with patch("generator.fetch.feedparser") as mock_fp:
        mock_fp.parse.return_value = parsed
        items = fetch_rss("https://example.com/feed", "Empty")
    assert items == []


def test_fetch_rss_403_returns_empty_list():
    mock_result = Mock()
    mock_result.entries = []
    mock_result.status = 403
    with patch("generator.fetch.feedparser") as mock_fp:
        mock_fp.parse.return_value = mock_result
        items = fetch_rss("https://blocked.example.com/feed", "Blocked")
    assert items == []


def test_detect_page_change_returns_true_on_change():
    old_hashes = {"https://example.com": "aaaaaa"}
    with patch("generator.fetch.requests") as mock_req:
        mock_req.get.return_value = Mock(status_code=200, text="new content", ok=True)
        changed, new_hash = detect_page_change("https://example.com", old_hashes)
    assert changed is True
    assert new_hash != "aaaaaa"


def test_detect_page_change_returns_false_on_no_change():
    import hashlib
    content = "same content"
    h = hashlib.sha256(content.encode()).hexdigest()
    old_hashes = {"https://example.com": h}
    with patch("generator.fetch.requests") as mock_req:
        mock_req.get.return_value = Mock(status_code=200, text=content, ok=True)
        changed, new_hash = detect_page_change("https://example.com", old_hashes)
    assert changed is False


def test_detect_page_change_403_returns_false_and_logs(caplog):
    with patch("generator.fetch.requests") as mock_req:
        mock_req.get.return_value = Mock(status_code=403, ok=False)
        changed, new_hash = detect_page_change("https://blocked.com", {})
    assert changed is False
