"""Feed fetcher for the White Horse Reservoir campaign site.

Fetches RSS feeds, JSON APIs, and monitors pages for changes.
Run as a script (python3 generator/fetch.py) to update data/reservoir/fetched/.
"""

import csv
import hashlib
import json
import logging
import urllib.robotparser
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import feedparser
import requests

USER_AGENT = "WHReservoir/1.0 (+https://github.com/davidmcneil99/white-horse-reservoir)"
_HEADERS = {"User-Agent": USER_AGENT}

logger = logging.getLogger(__name__)

_HERE = Path(__file__).parent
_ROOT = _HERE.parent
RES_DATA_DIR = _ROOT / "data" / "reservoir"
CEARN_DATA_DIR = _ROOT / "data" / "cearn"

_robots_cache: dict[str, urllib.robotparser.RobotFileParser] = {}


def _robots_allowed(url: str) -> bool:
    """Return True if our user-agent is allowed to fetch url per robots.txt.

    Fetches robots.txt via requests (correct user-agent, 10 s timeout).
    4xx or network error is treated as "allowed" -- we cannot know, so we
    proceed optimistically.
    """
    try:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin not in _robots_cache:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(origin + "/robots.txt")
            try:
                resp = requests.get(origin + "/robots.txt", headers=_HEADERS, timeout=10)
                if resp.status_code == 200:
                    rp.parse(resp.text.splitlines())
                else:
                    # No usable robots.txt (404, 4xx, 5xx) -- treat as allowed.
                    rp.allow_all = True
            except Exception:
                rp.allow_all = True
            _robots_cache[origin] = rp
        return _robots_cache[origin].can_fetch(USER_AGENT, url)
    except Exception:
        return True


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
    if not _robots_allowed(url):
        logging.warning("fetch_rss: robots.txt disallows fetching %s (%s)", source_name, url)
        return []
    try:
        response = requests.get(url, headers=_HEADERS, timeout=15)
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        code = exc.response.status_code if exc.response is not None else 0
        logging.warning("fetch_rss: HTTP %s for %s (%s)", code, source_name, url)
        return []
    except Exception as exc:
        logging.warning("fetch_rss: request failed for %s (%s): %s", source_name, url, exc)
        return []

    result = feedparser.parse(response.text)
    entries = getattr(result, "entries", [])
    if not entries:
        logging.info("fetch_rss: no entries for %s (%s)", source_name, url)
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
    if not _robots_allowed(url):
        logging.warning("fetch_json_api: robots.txt disallows fetching %s (%s)", source_name, url)
        return []
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

        if not title or not item_url:
            continue

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
    if not _robots_allowed(url):
        logging.warning("detect_page_change: robots.txt disallows fetching %s", url)
        return False, old_hashes.get(url, "")
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
    """Load sources from both reservoir CSV and cearn JSON, merged into one list."""
    csv_path = RES_DATA_DIR / "national-and-other-sources.csv"
    reservoir_sources: list[dict] = []
    if not csv_path.exists():
        logging.warning("load_sources: CSV not found at %s", csv_path)
    else:
        with csv_path.open(encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                entry = dict(row)
                entry.setdefault("project", "reservoir")
                reservoir_sources.append(entry)

    cearn_sources = load_cearn_sources()
    return reservoir_sources + cearn_sources


# Names of cearn local-council sources with no online presence that require
# manual monitoring only.
_CEARN_UNMONITORABLE = [
    "Goosey",
    "Baulking",
    "Denchworth",
    "Garford",
    "Lyford",
    "Frilford",
    "Hatford",
    "Besselsleigh",
]


def load_cearn_sources() -> list[dict]:
    """Load monitoring sources from data/cearn/cearn-solar-farm-sources.json.

    Returns a list of source dicts tagged project: cearn.
    Sources with no online presence are logged once per run; they are not
    returned because there is nothing to poll automatically.
    """
    json_path = CEARN_DATA_DIR / "cearn-solar-farm-sources.json"
    if not json_path.exists():
        logging.warning("load_cearn_sources: JSON not found at %s", json_path)
        return []

    with json_path.open(encoding="utf-8") as fh:
        data = json.load(fh)

    # Log unmonitorable sources once per call.
    for name in _CEARN_UNMONITORABLE:
        logging.info(
            "No automated monitoring for %s: no online presence; manual check required.",
            name,
        )

    sources: list[dict] = []

    # --- National and other sources from the JSON ---
    for item in data.get("national_and_other_sources", []):
        url = item.get("url", "").strip()
        name = item.get("name", "").strip()
        feed_info = item.get("feed", "").strip().lower()
        status = item.get("status", "").lower()

        if not url or not name:
            continue
        if "mirror only" in item.get("notes", "").lower():
            continue

        if "rss" in feed_info or "atom" in feed_info:
            sources.append({
                "name": name,
                "type": "rss",
                "url": url,
                "project": "cearn",
            })
        elif "json" in feed_info or "json api" in feed_info:
            # Hansard and written questions
            sources.append({
                "name": name,
                "type": "json_api",
                "url": url,
                "title_field": "title",
                "url_field": "url",
                "date_field": "date",
                "summary_field": "summary",
                "project": "cearn",
            })
        elif "none" in feed_info or feed_info == "" or "email" in feed_info:
            # Page-change detection for key pages with no RSS feed.
            if "works" in status and url.startswith("http"):
                sources.append({
                    "name": name,
                    "type": "page_change",
                    "url": url,
                    "project": "cearn",
                })

    # --- Local council RSS feeds ---
    for council in data.get("local_councils", []):
        council_name = council.get("name", "").strip()
        for feed_entry in council.get("feeds", []):
            feed_url = feed_entry.get("url", "").strip()
            feed_status = feed_entry.get("status", "").lower()
            if not feed_url:
                continue
            if "works" not in feed_status:
                continue
            sources.append({
                "name": f"{council_name} feed",
                "type": "rss",
                "url": feed_url,
                "project": "cearn",
            })

    return sources


def check_forecast_dates(timeline: list) -> None:
    """Warn if a forecast date has passed without confirmation."""
    today = date.today()
    for item in timeline:
        if not item.get("is_forecast"):
            continue
        raw = str(item.get("date", ""))
        try:
            if len(raw) == 7:  # YYYY-MM
                item_date = date.fromisoformat(raw + "-01")
            elif len(raw) == 10:
                item_date = date.fromisoformat(raw)
            else:
                continue
        except ValueError:
            continue
        if item_date < today:
            logging.warning(
                "Forecast date %s passed without confirmation: %s",
                raw, item.get("event", "")
            )


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
    hashes_path = RES_DATA_DIR / "fetched" / "page_hashes.json"
    news_path = RES_DATA_DIR / "fetched" / "news_items.json"

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

    cearn_timeline_path = CEARN_DATA_DIR / "content" / "timeline.json"
    if cearn_timeline_path.exists():
        cearn_timeline = json.loads(cearn_timeline_path.read_text(encoding="utf-8"))
        check_forecast_dates(cearn_timeline)
