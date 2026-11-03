"""Generator core: load_all_data() and build()."""

import csv
import json
import logging
import shutil
from datetime import date, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from generator.overrides import apply_overrides
from generator.utils import format_date

# Paths are resolved relative to the project root (the parent of this file's
# directory), so the generator can be called from any working directory.
_HERE = Path(__file__).parent
_ROOT = _HERE.parent

DATA_DIR = _ROOT / "data"
RES_DATA_DIR   = DATA_DIR / "reservoir"
CEARN_DATA_DIR = DATA_DIR / "cearn"
CONTENT_DIR    = RES_DATA_DIR / "content"
TEMPLATES_DIR = _ROOT / "templates"


def _parse_frontmatter(text: str) -> dict:
    """Parse a simple YAML-like frontmatter block from a Markdown file.

    Looks for content between the first pair of '---' delimiters and splits
    each line on the first ':' to build a flat string-to-string dict.
    Leading/trailing whitespace and surrounding quotes are stripped from
    values.

    Args:
        text: Full text of a Markdown file.

    Returns:
        Dict of key/value pairs found in the frontmatter.
    """
    lines = text.splitlines()
    delimiters = [i for i, line in enumerate(lines) if line.strip() == "---"]
    if len(delimiters) < 2:
        return {}
    block_lines = lines[delimiters[0] + 1 : delimiters[1]]
    result: dict = {}
    for line in block_lines:
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        result[key] = value
    return result


def load_all_data() -> dict:
    """Load all project data and return a single context dict.

    Reads JSON content files, CSV data files, fetched news and overrides,
    applies any overrides, and normalises date display strings.

    Returns:
        Dict with keys:
            timeline, quotes, actions, representatives, local_councils,
            access_points, news_items, corrections, still_to_check.
    """
    # --- JSON content files ---
    timeline: list[dict] = json.loads(
        (CONTENT_DIR / "timeline.json").read_text(encoding="utf-8")
    )
    quotes: list[dict] = json.loads(
        (CONTENT_DIR / "quotes.json").read_text(encoding="utf-8")
    )
    actions: list[dict] = json.loads(
        (CONTENT_DIR / "actions.json").read_text(encoding="utf-8")
    )

    # --- CSV files ---
    with (RES_DATA_DIR / "representatives.csv").open(encoding="utf-8", newline="") as fh:
        representatives: list[dict] = list(csv.DictReader(fh))

    with (RES_DATA_DIR / "local-councils.csv").open(encoding="utf-8", newline="") as fh:
        local_councils: list[dict] = list(csv.DictReader(fh))

    with (RES_DATA_DIR / "access-points.csv").open(encoding="utf-8", newline="") as fh:
        access_points: list[dict] = list(csv.DictReader(fh))

    # --- Sources: still_to_check_by_hand ---
    sources_raw = json.loads(
        (RES_DATA_DIR / "white-horse-reservoir-sources.json").read_text(encoding="utf-8")
    )
    still_to_check: list[str] = sources_raw.get("still_to_check_by_hand", [])

    # --- Fetched news items ---
    news_items_path = RES_DATA_DIR / "fetched" / "news_items.json"
    if news_items_path.exists():
        news_items: list[dict] = json.loads(news_items_path.read_text(encoding="utf-8"))
    else:
        news_items = []

    # --- Overrides ---
    overrides_path = RES_DATA_DIR / "overrides.json"
    if overrides_path.exists():
        overrides: list[dict] = json.loads(overrides_path.read_text(encoding="utf-8"))
    else:
        overrides = []

    # Apply overrides to content items.
    timeline = apply_overrides(timeline, overrides, "timeline")
    quotes = apply_overrides(quotes, overrides, "quote")
    actions = apply_overrides(actions, overrides, "action")

    # Normalise display dates for timeline and quotes (T2/T3 ruling).
    for item in timeline:
        item["date_display"] = format_date(item["date"], item.get("date_precision", "day"))
    for item in quotes:
        item["date_display"] = format_date(item["date"], item.get("date_precision", "day"))

    # Build corrections list: items that have been corrected.
    corrections: list[dict] = [
        item for item in (timeline + quotes + actions)
        if "_correction_note" in item
    ]

    # --- Enrichment ---

    # Build actions_by_id lookup.
    actions_by_id: dict = {a["id"]: a for a in actions}

    # Add is_distant_future flag to timeline items.
    # Items with year >= today.year + 3 (i.e. >= 2029 as of 2026) are distant future.
    threshold_year = datetime.today().year + 3
    for item in timeline:
        try:
            item_year = int(str(item.get("date", "0"))[:4])
            item["is_distant_future"] = item_year >= threshold_year
        except (ValueError, TypeError):
            item["is_distant_future"] = False

    # Add linked_actions to timeline items.
    for item in timeline:
        linked: list[dict] = []
        for aid in item.get("action_ids", []):
            action = actions_by_id.get(aid)
            if action:
                linked.append({"id": action["id"], "title": action["title"]})
        item["linked_actions"] = linked

    # Add deadline_display to action items.
    for action in actions:
        if action.get("deadline"):
            try:
                dt = datetime.strptime(action["deadline"], "%Y-%m-%d")
                action["deadline_display"] = dt.strftime("%d %B %Y").lstrip("0")
            except ValueError:
                action["deadline_display"] = action["deadline"]

    # Sort actions by (timing_order, deadline_nulls_last, original_index).
    timing_order = {"now": 0, "on-submission": 1, "on-acceptance": 2, "ongoing": 3}
    indexed_actions = list(enumerate(actions))
    indexed_actions.sort(
        key=lambda x: (
            timing_order.get(x[1].get("timing", ""), 99),
            x[1].get("deadline") or "9999-12-31",
            x[0],
        )
    )
    actions[:] = [a for _, a in indexed_actions]

    # Extract featured actions sorted by featured_order.
    featured_actions = sorted(
        [a for a in actions if a.get("featured")],
        key=lambda a: a.get("featured_order", 99),
    )

    cearn_data = load_cearn_data()

    return {
        "timeline": timeline,
        "quotes": quotes,
        "actions": actions,
        "actions_by_id": actions_by_id,
        "featured_actions": featured_actions,
        "featured_actions_intro": (
            "These are the most time-sensitive actions. "
            "This is a nationally significant infrastructure project at a critical stage."
        ),
        "representatives": representatives,
        "local_councils": local_councils,
        "access_points": access_points,
        "news_items": news_items,
        "corrections": corrections,
        "still_to_check": still_to_check,
        "built_on": date.today().isoformat(),
        "cearn_timeline":          cearn_data["cearn_timeline"],
        "cearn_quotes":            cearn_data["cearn_quotes"],
        "cearn_actions":           cearn_data["cearn_actions"],
        "cearn_featured_actions":  cearn_data["cearn_featured_actions"],
        "cearn_news_items":        cearn_data["cearn_news_items"],
        "links_to_reservoir":      cearn_data["links_to_reservoir"],
    }


def load_cearn_data() -> dict:
    """Load Cearn Solar Farm content data and return a context sub-dict."""
    cearn_content = CEARN_DATA_DIR / "content"
    timeline: list[dict] = json.loads((cearn_content / "timeline.json").read_text(encoding="utf-8"))
    quotes: list[dict] = json.loads((cearn_content / "quotes.json").read_text(encoding="utf-8"))
    actions: list[dict] = json.loads((cearn_content / "actions.json").read_text(encoding="utf-8"))
    overrides_path = CEARN_DATA_DIR / "overrides.json"
    overrides = json.loads(overrides_path.read_text(encoding="utf-8")) if overrides_path.exists() else []

    timeline = apply_overrides(timeline, overrides, "timeline")
    quotes   = apply_overrides(quotes,   overrides, "quote")
    actions  = apply_overrides(actions,  overrides, "action")

    for item in timeline:
        item["date_display"] = format_date(item["date"], item.get("date_precision", "day"))
        item["is_forecast"] = item.get("status") == "forecast"

    for item in quotes:
        item["date_display"] = format_date(item["date"], item.get("date_precision", "day"))

    # Sort actions by timing order
    timing_order = {"now": 0, "on-submission": 1, "on-acceptance": 2, "ongoing": 3}
    indexed = list(enumerate(actions))
    indexed.sort(key=lambda x: (timing_order.get(x[1].get("timing", ""), 99), x[1].get("deadline") or "9999-12-31", x[0]))
    actions[:] = [a for _, a in indexed]

    cearn_news_path = CEARN_DATA_DIR / "fetched" / "news_items.json"
    cearn_news = json.loads(cearn_news_path.read_text(encoding="utf-8")) if cearn_news_path.exists() else []

    cearn_featured_actions = sorted(
        [a for a in actions if a.get("featured")],
        key=lambda a: a.get("featured_order", 99),
    )

    cearn_sources = json.loads((CEARN_DATA_DIR / "cearn-solar-farm-sources.json").read_text(encoding="utf-8"))
    links_to_reservoir = cearn_sources.get("links_to_reservoir", {})

    return {
        "cearn_timeline": timeline,
        "cearn_quotes":   quotes,
        "cearn_actions":  actions,
        "cearn_featured_actions": cearn_featured_actions,
        "cearn_news_items": cearn_news,
        "links_to_reservoir": links_to_reservoir,
    }


def _build_lookup_data(data: dict) -> dict:
    """Construct the lookup-data.json payload from the loaded context dict.

    Args:
        data: The dict returned by load_all_data().

    Returns:
        Dict ready to be serialised as lookup-data.json.
    """
    # Representatives: include all rows with key fields.
    reps = [
        {
            "tier": r.get("tier", ""),
            "area": r.get("area", ""),
            "name": r.get("name", ""),
            "email": r.get("email", ""),
            "profile_url": r.get("profile_url", ""),
            "places": r.get("places", ""),
            "stance": r.get("stance", ""),
            "projects": r.get("projects", "reservoir"),
        }
        for r in data["representatives"]
    ]

    # Parishes: local_councils rows of type 'Parish council'.
    parishes = [
        {
            "name": c.get("name", ""),
            "website": c.get("website", ""),
            "contact": c.get("contact", ""),
        }
        for c in data["local_councils"]
        if c.get("type", "").lower().startswith("parish") or c.get("type", "").lower().startswith("town council")
    ]

    # Access points.
    aps = [
        {
            "id": ap.get("id", ""),
            "roads": ap.get("roads", ""),
            "localities": ap.get("localities", ""),
            "peak_hgv_per_hr": ap.get("peak_hgv_per_hr", ""),
        }
        for ap in data["access_points"]
    ]

    # Letter recipients.
    # 'mp' uses placeholder tokens for client-side JS substitution.
    mp_recipient = {
        "name": "{{mp_name}}",
        "email": "{{mp_email}}",
        "address": "House of Commons, London SW1A 0AA",
    }

    # 'defra' is read from the defra letter's frontmatter.
    defra_letter_path = CONTENT_DIR / "letters" / "defra-secretary-of-state.md"
    defra_fm = _parse_frontmatter(defra_letter_path.read_text(encoding="utf-8"))
    defra_recipient = {
        "name": defra_fm.get("recipient_name", ""),
        "email": defra_fm.get("recipient_email", ""),
        "address": defra_fm.get("recipient_address", ""),
    }

    desnz_recipient = {
        "name": "Miatta Fahnbulleh MP",
        "email": "",
        "address": "Ministerial Correspondence Team, Level 3, 55 Whitehall, London SW1A 2HP",
    }

    return {
        "representatives": reps,
        "parishes": parishes,
        "access_points": aps,
        "letter_recipients": {
            "mp": mp_recipient,
            "defra": defra_recipient,
            "desnz": desnz_recipient,
        },
    }


def _build_letters_data() -> dict:
    """Read all letter template .md files and return a dict for letters-data.json.

    Reads from both ``data/reservoir/content/letters/`` and
    ``data/cearn/content/letters/``.  Each entry key is the filename stem
    (e.g. ``mp.md`` -> ``"mp"``).  Each value is the flat frontmatter dict
    with an added ``"body"`` key containing the template body text (plain text
    with ``{{placeholder}}`` tokens) and a ``"project"`` key (``"reservoir"``
    or ``"cearn"``).

    Returns:
        Dict mapping template key -> entry dict.
    """
    letters_dirs = [
        (CONTENT_DIR / "letters", "reservoir"),
        (CEARN_DATA_DIR / "content" / "letters", "cearn"),
    ]
    result: dict = {}
    for letters_dir, default_project in letters_dirs:
        if not letters_dir.exists():
            continue
        for path in sorted(letters_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            fm = _parse_frontmatter(text)
            # Extract body: everything after the second '---' delimiter.
            lines = text.splitlines()
            delimiters = [i for i, ln in enumerate(lines) if ln.strip() == "---"]
            if len(delimiters) >= 2:
                body = "\n".join(lines[delimiters[1] + 1 :]).strip()
            else:
                body = text.strip()
            entry = dict(fm)
            entry["body"] = body
            # Tag with project; use frontmatter value if present, else default.
            if "project" not in entry:
                entry["project"] = default_project
            result[path.stem] = entry
    return result


def build(output_dir: Path = Path("docs")) -> None:
    """Render all site pages to output_dir.

    Loads data, builds the Jinja2 environment from templates/, renders each
    page template, and writes lookup-data.json to output_dir/assets/.

    Args:
        output_dir: Destination directory. Created if it does not exist.
    """
    output_dir = Path(output_dir)
    docs_res_dir   = output_dir / "reservoir"
    docs_solar_dir = output_dir / "solar"
    docs_comb_dir  = output_dir / "combined"

    output_dir.mkdir(parents=True, exist_ok=True)
    for d in [docs_res_dir, docs_solar_dir, docs_comb_dir]:
        d.mkdir(parents=True, exist_ok=True)

    data = load_all_data()

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True,
    )

    pages = [
        # Root
        ("root-redirect.html",                output_dir / "index.html",              None,         None),
        ("about.html",                         output_dir / "about.html",              None,         "about"),
        # Reservoir
        ("reservoir/index.html",               docs_res_dir / "index.html",            "reservoir",  "reservoir-home"),
        ("reservoir/facts.html",               docs_res_dir / "facts.html",            "reservoir",  "reservoir-facts"),
        ("reservoir/actions.html",             docs_res_dir / "actions.html",          "reservoir",  "reservoir-actions"),
        ("reservoir/letters.html",             docs_res_dir / "letters.html",          "reservoir",  "reservoir-letters"),
        ("reservoir/access-points.html",       docs_res_dir / "access-points.html",    "reservoir",  "reservoir-access"),
        # Solar
        ("solar/index.html",                   docs_solar_dir / "index.html",          "solar",      "solar-home"),
        ("solar/facts.html",                   docs_solar_dir / "facts.html",          "solar",      "solar-facts"),
        ("solar/actions.html",                 docs_solar_dir / "actions.html",        "solar",      "solar-actions"),
        ("solar/letters.html",                 docs_solar_dir / "letters.html",        "solar",      "solar-letters"),
        # Combined
        ("combined/index.html",                docs_comb_dir / "index.html",           "combined",   "combined-home"),
        ("combined/facts.html",                docs_comb_dir / "facts.html",           "combined",   "combined-facts"),
        ("combined/actions.html",              docs_comb_dir / "actions.html",         "combined",   "combined-actions"),
        ("combined/letters.html",              docs_comb_dir / "letters.html",         "combined",   "combined-letters"),
    ]

    for template_name, output_path, section, page_id in pages:
        tmpl = env.get_template(template_name)
        html = tmpl.render(**data, section=section, page_id=page_id)
        output_path.write_text(html, encoding="utf-8")
        logging.info("Wrote %s", output_path)

    # Old flat-URL redirect stubs: keep pre-restructure links from hard-404ing.
    # Written inline (not via Jinja) because each is a bare meta-refresh page.
    redirect_stubs = [
        (output_dir / "facts.html",            "/white-horse-reservoir/reservoir/facts.html"),
        (output_dir / "actions.html",          "/white-horse-reservoir/reservoir/actions.html"),
        (output_dir / "letters.html",          "/white-horse-reservoir/reservoir/letters.html"),
        (output_dir / "access-points.html",    "/white-horse-reservoir/reservoir/access-points.html"),
        (output_dir / "solar-facts.html",      "/white-horse-reservoir/solar/facts.html"),
        (output_dir / "solar-actions.html",    "/white-horse-reservoir/solar/actions.html"),
        (output_dir / "solar-letters.html",    "/white-horse-reservoir/solar/letters.html"),
        (output_dir / "combined-impacts.html", "/white-horse-reservoir/combined/"),
    ]
    for stub_path, target_url in redirect_stubs:
        stub_path.write_text(
            f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta http-equiv="refresh" content="0;url={target_url}">'
            f'<title>Redirecting — Vale Watch</title></head>'
            f'<body><p><a href="{target_url}">Redirecting…</a></p></body></html>',
            encoding="utf-8",
        )
        logging.info("Wrote redirect stub %s", stub_path)

    # Write lookup-data.json.
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    lookup = _build_lookup_data(data)
    (assets_dir / "lookup-data.json").write_text(
        json.dumps(lookup, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logging.info("Wrote %s", assets_dir / "lookup-data.json")

    # Write letters-data.json.
    letters_data = _build_letters_data()
    (assets_dir / "letters-data.json").write_text(
        json.dumps(letters_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logging.info("Wrote %s", assets_dir / "letters-data.json")

    # Copy ward-aliases.json so lookup.js can fetch it alongside lookup-data.json.
    ward_aliases_src = CONTENT_DIR / "ward-aliases.json"
    if ward_aliases_src.exists():
        shutil.copy2(ward_aliases_src, assets_dir / "ward-aliases.json")
        logging.info("Copied %s -> %s", ward_aliases_src, assets_dir / "ward-aliases.json")


if __name__ == "__main__":
    build()
