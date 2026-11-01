"""Feed fetcher for the White Horse Reservoir campaign site.

Fetches RSS feeds, JSON APIs, and monitors pages for changes.
Run as a script (python3 generator/fetch.py) to update data/fetched/.
"""

import csv
import hashlib
import logging
import time
from datetime import date
from pathlib import Path

import feedparser
import requests

USER_AGENT = "WHReservoir/1.0 (+https://github.com/davidmcneil99/white-horse-reservoir)"
_HEADERS = {"User-Agent": USER_AGENT}

logger = logging.getLogger(__name__)


def _struct_time_to_date(st) -> str:
    """Convert a struct_time (from feedparser) to YYYY-MM-DD string."""
    if st is None:
        return date.today().isoformat()
    try:
        return date(st.tm_year, st.tm_mon, st.tm_mday).isoformat()
    except (AttributeError, ValueError):
        return date.today().isoformat()


def fetch_rss(url: str, source_name: str) -> list[dict]:
    """Fetch an RSS/Atom feed and return a list of new_item dicts."""
    result = feedparser.parse(url)

    # Check for HTTP error status
    status = getattr(result, "status", None)
    if status == 403:
        logging.warning("fetch_rss: 403 Forbidden for %s (%s)", source_name, url)
        return []

    entries = getattr(result, "entries", [])
    if not entries:
        return []

    items = []
    for entry in entries:
        title = getattr(entry, "title", "") or ""
        title = title[:120]

        link = getattr(entry, "link", "") or ""

        published_parsed = getattr(entry, "published_parsed", None)
        date_str = _struct_time_to_date(published_parsed)

        summary = getattr(entry, "summary", "") or ""
        summary = summary[:300]

        items.append({
            "title": title,
            "url": link,
            "date": date_str,
            "source_name": source_name,
            "summary": summary,
            "ai_generated": False,
        })

    return items


def fetch_json_api(
    url: str,
    source_name: str,
    title_field: str,
    url_field: str,
    date_field: str,
    summary_field: str,
) -> list[dict]:
    """Fetch a JSON API endpoint and return a list of new_item dicts."""
    try:
        response = requests.get(url, headers=_HEADERS, timeout=15)
    except Exception as exc:
        logging.warning("fetch_json_api: request failed for %s (%s): %s", source_name, url, exc)
        return []

    if not response.ok:
        logging.warning(
            "fetch_json_api: HTTP %s for %s (%s)", response.status_code, source_name, url
        )
        return []

    try:
        data = response.json()
    except Exception as exc:
        logging.warning("fetch_json_api: JSON parse error for %s (%s): %s", source_name, url, exc)
        return []

    # Support both a top-level list and a dict with a "results" / "items" key
    if isinstance(data, list):
        raw_items = data
    elif isinstance(data, dict):
        # Try common envelope keys
        for key in ("results", "items", "entries", "data"):
            if key in data and isinstance(data[key], list):
                raw_items = data[key]
                break
        else:
            raw_items = []
    else:
        raw_items = []

    items = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            continue
        title = str(raw.get(title_field, ""))[:120]
        item_url = str(raw.get(url_field, ""))
        date_str = str(raw.get(date_field, date.today().isoformat()))[:10]
        summary = str(raw.get(summary_field, ""))[:300]

        items.append({
            "title": title,
            "url": item_url,
            "date": date_str,
            "source_name": source_name,
            "summary": summary,
            "ai_generated": False,
        })

    return items


def detect_page_change(url: str, old_hashes: dict) -> tuple[bool, str]:
    """Fetch a page and detect whether its content has changed.

    Returns (changed: bool, new_hash: str).
    If the request fails, returns (False, old hash or "").
    """
    try:
        response = requests.get(url, headers=_HEADERS, timeout=15)
    except Exception as exc:
        logging.warning("detect_page_change: request failed for %s: %s", url, exc)
        return False, old_hashes.get(url, "")

    if not response.ok:
        logging.warning(
            "detect_page_change: HTTP %s for %s", response.status_code, url
        )
        return False, old_hashes.get(url, "")

    new_hash = hashlib.sha256(response.text.encode()).hexdigest()
    old_hash = old_hashes.get(url)
    changed = old_hash is None or new_hash != old_hash
    return changed, new_hash


def load_sources() -> list[dict]:
    """Load sources from data/national-and-other-sources.csv."""
    csv_path = Path("data/national-and-other-sources.csv")
    if not csv_path.exists():
        logging.warning("load_sources: CSV not found at %s", csv_path)
        return []

    sources = []
    with csv_path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            sources.append(dict(row))
    return sources


def fetch_all(sources: list[dict], hashes: dict) -> tuple[list[dict], dict]:
    """Dispatch each source to the appropriate fetch function.

    Returns (new_items, updated_hashes).
    """
    new_items: list[dict] = []
    updated_hashes = dict(hashes)

    for source in sources:
        # The CSV uses 'name'; also support 'source_name' as an alias.
        name = source.get("name") or source.get("source_name", "")
        source_type = (source.get("type") or source.get("feed", "")).strip().lower()
        url = source.get("url", "").strip()

        if not url:
            continue

        if source_type == "rss":
            items = fetch_rss(url, name)
            new_items.extend(items)

        elif source_type in ("json_api", "json api"):
            title_field = source.get("title_field", "title")
            url_field = source.get("url_field", "url")
            date_field = source.get("date_field", "date")
            summary_field = source.get("summary_field", "summary")
            items = fetch_json_api(url, name, title_field, url_field, date_field, summary_field)
            new_items.extend(items)

        elif source_type in ("page_change", "page change"):
            changed, new_hash = detect_page_change(url, updated_hashes)
            updated_hashes[url] = new_hash
            if changed:
                new_items.append({
                    "title": f"Page updated: {name}",
                    "url": url,
                    "date": date.today().isoformat(),
                    "source_name": name,
                    "summary": "",
                    "ai_generated": False,
                })

    return new_items, updated_hashes


if __name__ == "__main__":
    import json

    sources = load_sources()
    hashes_path = Path("data/fetched/page_hashes.json")
    news_path = Path("data/fetched/news_items.json")

    hashes = json.loads(hashes_path.read_text(encoding="utf-8")) if hashes_path.exists() else {}
    existing = json.loads(news_path.read_text(encoding="utf-8")) if news_path.exists() else []

    new_items, new_hashes = fetch_all(sources, hashes)

    existing_urls = {i["url"] for i in existing}
    to_add = [i for i in new_items if i["url"] not in existing_urls]
    all_items = (to_add + existing)[:500]  # max 500, newest first

    news_path.parent.mkdir(parents=True, exist_ok=True)
    news_path.write_text(json.dumps(all_items, indent=2, ensure_ascii=False), encoding="utf-8")
    hashes_path.write_text(json.dumps(new_hashes, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Fetched {len(to_add)} new items")
