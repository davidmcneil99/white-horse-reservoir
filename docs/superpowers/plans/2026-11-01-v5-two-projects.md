# Two-Project Extension: V5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the White Horse Reservoir campaign app to cover Cearn Solar Farm (EN0110044) as a second project alongside the reservoir (WA010005), with project-specific pages, a shared Combined Impacts page, two Planning Inspectorate boundaries on the map, and a pipeline monitoring both projects.

**Architecture:** The Python generator grows from single-project to two-project: `load_all_data()` reads both `data/reservoir/` and `data/cearn/` and returns separate context keys for each project. New page templates (`solar-facts.html`, `solar-actions.html`, `solar-letters.html`, `combined-impacts.html`) are added alongside existing reservoir pages (whose URLs are preserved). The navigation in `base.html` gains project dropdowns. Client-side JS (`lookup.js`, `map.js`) is updated to show both Planning Inspectorate boundaries and both project contexts for a postcode lookup.

**Tech Stack:** Python 3.11, Jinja2, feedparser, requests; HTML5/CSS3/vanilla JS; Leaflet 1.9.4 + OpenStreetMap; postcodes.io; GitHub Pages; GitHub Actions. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-11-01-two-projects-design.md` (addendum to `docs/superpowers/specs/2026-11-01-white-horse-reservoir-design.md`)

## Global Constraints

- Python 3.11 minimum; no new third-party packages; same requirements.txt
- UK English throughout; no em dashes; no emojis in site copy
- `E:\reservoir` and `E:\cearn` are READ ONLY -- never edit them
- `data/cearn/cearn-solar-farm-sources.json` is the cearn master dataset: read-only
- `data/reservoir/white-horse-reservoir-sources.json` is the reservoir master dataset: read-only
- Existing reservoir page URLs (`facts.html`, `actions.html`, `letters.html` etc.) must not change
- `projects` field on representatives is a comma-separated string: `reservoir`, `cearn`, or `reservoir,cearn`
- Cearn letters must address DESNZ as decision-maker, not Defra; include a note that the Vale is a statutory consultee only
- Every combined-impact statement is labelled `confirmed`, `claimed`, or `not yet confirmed`
- Forecast timeline entries use `status: forecast` in JSON and render with a "(forecast)" label
- `python -m pytest tests/ -q` must pass (42 baseline) after every task

## Review Focus

1. **Dual-mandate reps appear twice in the postcode lookup** -- Jenny Hannaby, Lee Evans and Ron Batstone each hold a District and a County role. The lookup must show both roles with their distinct bodies, not deduplicate by name. Add to Task 5.
2. **Cearn letter uses `{{mp_name}}` without a lookup result** -- like the reservoir letter, the solar MP letter must degrade gracefully: unfilled placeholders render as `[not found -- please fill in]`. Add to Task 9.
3. **Forecast date passes without confirmation** -- pipeline must log "forecast date YYYY-MM passed without confirmation" rather than silently passing. Add to Task 12.
4. **Combined-impact paragraph included in a reservoir letter** -- the checkbox toggle must not add the solar combined-impact paragraph to reservoir letters. Project-specific. Add to Task 9.
5. **Both map boundaries load independently** -- if the cearn GeoJSON fetch fails (e.g., PINS returns 404), the reservoir boundary and the rest of the map still render; the cearn boundary shows "boundary not available" in the layer control. Add to Task 11.

---

## File Map Changes

```
data/
  reservoir/                              (moved from data/ flat)
    white-horse-reservoir-sources.json
    representatives.csv                   (merged with cearn shared reps; projects field added)
    local-councils.csv
    access-points.csv
    national-and-other-sources.csv
    overrides.json
    original-build.py
    original-index.html
    content/
      timeline.json
      quotes.json
      actions.json
      ward-aliases.json
      letters/                            (10 existing templates, unchanged)
    fetched/
      news_items.json
      page_hashes.json
  cearn/
    cearn-solar-farm-sources.json         (copied from E:\cearn)
    key-dates.csv, nearby-solar-schemes.csv, local-councils.csv,
    representatives.csv, council-positions.csv, campaign-groups.csv,
    national-and-other-sources.csv, how-to-get-involved.csv
    README.md, project-context.md, research-report.md
    build.py, index.html                  (reference copies, not run)
    boundary-parishes.json                (produced by Task 2)
    overrides.json                        (empty array)
    content/
      timeline.json                       (seeded from key_dates)
      quotes.json                         (seeded from council_positions)
      actions.json                        (seeded from how_to_get_involved)
      letters/
        desnz-secretary-of-state.md
        cearn-developer.md
        solar-mp.md
        solar-county-councillor.md
        solar-district-councillor.md
        solar-planning-inspectorate.md
    fetched/
      news_items.json
      page_hashes.json
generator/
  build.py                                (extended: RES_DATA_DIR, CEARN_DATA_DIR)
  fetch.py                                (extended: cearn sources)
  overrides.py                            (unchanged)
  utils.py                                (unchanged)
templates/
  base.html                               (updated: two-project nav)
  index.html                              (updated: both projects featured)
  facts.html                              (minor: project label)
  actions.html                            (minor: project label)
  letters.html                            (minor: project label)
  corrections.html                        (updated: both projects' corrections)
  about.html                              (updated: two campaigns described)
  access-points.html                      (unchanged)
  solar-facts.html                        (new)
  solar-actions.html                      (new)
  solar-letters.html                      (new)
  combined-impacts.html                   (new)
docs/assets/
  map.js                                  (updated: EN0110044 boundary)
  lookup.js                               (updated: both project contexts)
  lookup-data.json                        (updated: cearn reps + solar letter recipients)
tests/
  test_build.py                           (updated: new paths + cearn context keys)
  test_fetch.py                           (updated: cearn sources)
  test_lookup_data.py                     (updated: cearn reps in lookup-data.json)
```

---

## Task 0: Data Folder Reorganisation

**Files:**
- Move: all `data/*.json`, `data/*.csv`, `data/overrides.json` → `data/reservoir/`
- Move: `data/content/` → `data/reservoir/content/`
- Move: `data/fetched/` → `data/reservoir/fetched/`
- Modify: `generator/build.py` -- update `DATA_DIR` usage to `RES_DATA_DIR`
- Modify: `generator/fetch.py` -- update data paths
- Modify: `tests/test_build.py`, `tests/test_fetch.py`, `tests/test_lookup_data.py` -- update paths

**Interfaces:**
- Produces: `data/reservoir/` with all existing files; tests still pass 42/42

- [ ] **Step 1: Move flat data files to data/reservoir/**

  ```bash
  mkdir -p data/reservoir/content/letters
  mkdir -p data/reservoir/fetched
  # Move root-level data files
  mv data/white-horse-reservoir-sources.json data/reservoir/
  mv data/representatives.csv data/reservoir/
  mv data/local-councils.csv data/reservoir/
  mv data/access-points.csv data/reservoir/
  mv data/national-and-other-sources.csv data/reservoir/
  mv data/overrides.json data/reservoir/
  mv data/original-build.py data/reservoir/ 2>/dev/null || true
  mv data/original-index.html data/reservoir/ 2>/dev/null || true
  # Move content/
  mv data/content/* data/reservoir/content/
  rmdir data/content
  # Move fetched/
  mv data/fetched/* data/reservoir/fetched/ 2>/dev/null || true
  rmdir data/fetched 2>/dev/null || true
  ```

- [ ] **Step 2: Update generator/build.py path constants**

  In `generator/build.py`, after `DATA_DIR = _ROOT / "data"`, add:

  ```python
  RES_DATA_DIR   = DATA_DIR / "reservoir"
  CEARN_DATA_DIR = DATA_DIR / "cearn"
  CONTENT_DIR    = RES_DATA_DIR / "content"
  ```

  Replace every occurrence of `DATA_DIR / "<file>"` (for reservoir files) with `RES_DATA_DIR / "<file>"`. The existing `CONTENT_DIR` already points to content; confirm it now resolves under `reservoir/`.

  Files changed:
  - `DATA_DIR / "representatives.csv"` → `RES_DATA_DIR / "representatives.csv"`
  - `DATA_DIR / "local-councils.csv"` → `RES_DATA_DIR / "local-councils.csv"`
  - `DATA_DIR / "access-points.csv"` → `RES_DATA_DIR / "access-points.csv"`
  - `DATA_DIR / "white-horse-reservoir-sources.json"` → `RES_DATA_DIR / "white-horse-reservoir-sources.json"`
  - `DATA_DIR / "overrides.json"` → `RES_DATA_DIR / "overrides.json"`
  - `DATA_DIR / "fetched" / ...` → `RES_DATA_DIR / "fetched" / ...`
  - `CONTENT_DIR` → already resolves under `reservoir/` after Step 2

- [ ] **Step 3: Update generator/fetch.py paths**

  Change `DATA_DIR` references to `RES_DATA_DIR` for all reservoir-related paths. (Cearn sources are added in Task 12.)

- [ ] **Step 4: Update tests**

  In `tests/test_build.py` and `tests/test_lookup_data.py`, update any hardcoded `data/` path strings to `data/reservoir/`.

  Run: `python -m pytest tests/ -q`
  Expected: 42 passed, 0 failed.

- [ ] **Step 5: Commit**

  ```bash
  git add data/reservoir/ data/cearn/ generator/build.py generator/fetch.py tests/
  git status --short  # confirm no data/ root files remain
  git commit -m "refactor: move reservoir data to data/reservoir/ for two-project structure"
  ```

---

## Task 1: Copy Cearn Source Data

**Files:**
- Create: `data/cearn/` with all files from `E:\cearn` (strip `_1` suffix from `README_1.md` → `README.md` and `index_1.html` → `index.html`)
- Create: `data/cearn/overrides.json` (empty array)
- Create: `data/cearn/fetched/news_items.json` (empty array)
- Create: `data/cearn/fetched/page_hashes.json` (empty object)
- Create: `data/cearn/content/` directory tree

**Interfaces:**
- Produces: `data/cearn/` with all source files; generator can reference them

- [ ] **Step 1: Copy files from E:\cearn**

  ```python
  import shutil, pathlib

  src = pathlib.Path(r"E:\cearn")
  dst = pathlib.Path("data/cearn")
  dst.mkdir(parents=True, exist_ok=True)

  renames = {"README_1.md": "README.md", "index_1.html": "index.html"}
  for f in src.iterdir():
      if f.is_file():
          dst_name = renames.get(f.name, f.name)
          shutil.copy2(f, dst / dst_name)
          src_size = f.stat().st_size
          dst_size = (dst / dst_name).stat().st_size
          assert src_size == dst_size, f"Size mismatch: {f.name}"
          print(f"  OK: {f.name} -> {dst_name} ({src_size} bytes)")
  ```

  Expected: all 14 files copied with matching sizes.

- [ ] **Step 2: Create cearn supporting files**

  ```bash
  mkdir -p data/cearn/content/letters
  mkdir -p data/cearn/fetched
  echo '[]' > data/cearn/overrides.json
  echo '[]' > data/cearn/fetched/news_items.json
  echo '{}' > data/cearn/fetched/page_hashes.json
  ```

- [ ] **Step 3: Verify E:\cearn is unchanged**

  ```python
  import os
  src = r"E:\cearn"
  for f in os.listdir(src):
      p = os.path.join(src, f)
      print(f"  {f}: {os.path.getsize(p)} bytes")
  ```

  Expected: same 14 files, same sizes as before Task 1.

- [ ] **Step 4: Commit**

  ```bash
  git add data/cearn/
  git commit -m "data: copy Cearn Solar Farm source data to data/cearn/"
  ```

---

## Task 2: EN0110044 Boundary GeoJSON and Parish Overlay

**Files:**
- Create: `scripts/cearn_boundary.py`
- Create: `data/cearn/boundary-parishes.json` (output of the script)
- Create: `tests/test_cearn_boundary.py`

**Interfaces:**
- Produces: `data/cearn/boundary-parishes.json` with keys `scheme_parishes`, `corridor_parishes`, `source`, `checked_date`
- Consumed by: Task 4 (generator), Task 7 (solar-facts.html), Task 11 (map layer labels)

The Planning Inspectorate publishes both boundaries at:
- WA010005: `https://national-infrastructure-consenting.planninginspectorate.gov.uk/projects/WA010005/download-boundary`
- EN0110044: `https://national-infrastructure-consenting.planninginspectorate.gov.uk/projects/EN0110044/download-boundary`

The ONS civil parish boundaries are available from the ONS Open Geography Portal. Use the Parishes and Non Civil Parished Areas (PNCP) dataset (GeoJSON API or bulk download). The open dataset URL as at November 2026: `https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/Parishes_and_Non_Civil_Parished_Areas_December_2023_EW_BGC_2022/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json` (paginated; see script below for full retrieval). If this URL has changed, the ONS Open Geography Portal at `geoportal.statistics.gov.uk` has the current endpoint.

- [ ] **Step 1: Write the failing test**

  ```python
  # tests/test_cearn_boundary.py
  import json, pathlib

  def test_boundary_parishes_file_exists():
      p = pathlib.Path("data/cearn/boundary-parishes.json")
      assert p.exists(), "boundary-parishes.json not produced by cearn_boundary.py"

  def test_expected_scheme_parishes_present():
      data = json.loads(pathlib.Path("data/cearn/boundary-parishes.json").read_text(encoding="utf-8"))
      scheme = [p.lower() for p in data.get("scheme_parishes", [])]
      for expected in ["garford", "charney bassett", "west hanney", "goosey", "baulking"]:
          assert any(expected in p for p in scheme), f"Expected parish missing: {expected}"

  def test_source_and_date_present():
      data = json.loads(pathlib.Path("data/cearn/boundary-parishes.json").read_text(encoding="utf-8"))
      assert data.get("source"), "source field missing"
      assert data.get("checked_date"), "checked_date field missing"
  ```

  Run: `python -m pytest tests/test_cearn_boundary.py -v`
  Expected: FAIL (file does not exist yet).

- [ ] **Step 2: Write scripts/cearn_boundary.py**

  ```python
  """Download EN0110044 boundary GeoJSON and overlay on ONS civil parish boundaries."""
  import json, pathlib, datetime, sys
  import requests
  from shapely.geometry import shape

  PINS_URL = "https://national-infrastructure-consenting.planninginspectorate.gov.uk/projects/EN0110044/download-boundary"
  ONS_URL = (
      "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/"
      "Parishes_and_Non_Civil_Parished_Areas_December_2023_EW_BGC_2022/FeatureServer/0/query"
      "?where=1%3D1&outFields=PARNM23&outSR=4326&f=json&resultOffset={offset}&resultRecordCount=1000"
  )
  USER_AGENT = "WHReservoir/1.0 (+https://github.com/davidmcneil99/white-horse-reservoir)"

  def fetch_geojson(url: str) -> dict:
      r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
      r.raise_for_status()
      return r.json()

  def fetch_all_parishes() -> list:
      """Fetch all ONS parish features (paginated)."""
      features, offset = [], 0
      while True:
          data = fetch_geojson(ONS_URL.format(offset=offset))
          batch = data.get("features", [])
          if not batch:
              break
          features.extend(batch)
          offset += len(batch)
          if len(batch) < 1000:
              break
      return features

  def main():
      print("Fetching EN0110044 boundary from PINS...")
      boundary_data = fetch_geojson(PINS_URL)
      # The PINS response is a GeoJSON FeatureCollection
      boundary_geom = shape(boundary_data["features"][0]["geometry"]) \
          if boundary_data.get("features") else shape(boundary_data["geometry"])

      print("Fetching ONS civil parish boundaries (paginated)...")
      parish_features = fetch_all_parishes()
      print(f"  {len(parish_features)} parish features loaded")

      scheme_parishes = []
      for feat in parish_features:
          try:
              parish_geom = shape(feat["geometry"])
              if boundary_geom.intersects(parish_geom):
                  name = feat.get("properties", {}).get("PARNM23", "")
                  if name:
                      scheme_parishes.append(name)
          except Exception as e:
              pass  # malformed geometry

      result = {
          "scheme_parishes": sorted(scheme_parishes),
          "corridor_parishes": [],  # populated manually once Stage 2 cable route published
          "source": PINS_URL,
          "ons_source": "ONS Open Geography Portal: Parishes and Non Civil Parished Areas Dec 2023",
          "checked_date": datetime.date.today().isoformat(),
          "notes": "Cable corridor parishes not yet determinable; cable route published at Stage 2 consultation (Feb-Mar 2027).",
      }
      out = pathlib.Path("data/cearn/boundary-parishes.json")
      out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
      print(f"Written {out}: {len(scheme_parishes)} scheme parishes")
      print("Parishes:", ", ".join(scheme_parishes))

  if __name__ == "__main__":
      main()
  ```

  Note: `shapely` is required. Add it to `requirements.txt` if not already present (`shapely>=2.0`).

- [ ] **Step 3: Run the script**

  ```bash
  pip install shapely  # if not already installed
  python scripts/cearn_boundary.py
  ```

  Expected: `data/cearn/boundary-parishes.json` created, output lists at least Garford, Charney Bassett, West Hanney, Goosey, Baulking.

  If PINS returns a 403 or the boundary format differs: the script prints the raw response and exits with a clear error. In that case, manually create `data/cearn/boundary-parishes.json` using the five known parishes from the research and set `"notes": "Manually populated; automated download blocked."`.

- [ ] **Step 4: Run the test**

  ```bash
  python -m pytest tests/test_cearn_boundary.py -v
  python -m pytest tests/ -q
  ```

  Expected: `test_cearn_boundary.py` 3/3 pass; total 45/45 pass.

- [ ] **Step 5: Add `shapely` to requirements.txt if used**

  Add the line `shapely>=2.0` to `requirements.txt`.

- [ ] **Step 6: Commit**

  ```bash
  git add scripts/cearn_boundary.py data/cearn/boundary-parishes.json tests/test_cearn_boundary.py requirements.txt
  git commit -m "feat: download EN0110044 boundary and overlay on ONS parish boundaries"
  ```

---

## Task 3: Seed Cearn Content Data

**Files:**
- Create: `data/cearn/content/timeline.json` (from `key_dates`)
- Create: `data/cearn/content/quotes.json` (from `council_positions`)
- Create: `data/cearn/content/actions.json` (from `how_to_get_involved`)

**Interfaces:**
- Produces: three JSON content files following the same schema as the reservoir equivalents (with `status: forecast` additions for timeline)
- Consumed by: Task 4 (generator loads them)

- [ ] **Step 1: Write the failing test**

  ```python
  # in tests/test_build.py -- add:
  def test_cearn_content_files_exist():
      for name in ["timeline.json", "quotes.json", "actions.json"]:
          p = Path("data/cearn/content") / name
          assert p.exists(), f"Missing: {p}"

  def test_cearn_timeline_has_forecast_entries():
      data = json.loads(Path("data/cearn/content/timeline.json").read_text(encoding="utf-8"))
      forecasts = [e for e in data if e.get("status") == "forecast"]
      assert len(forecasts) >= 3, "Expected at least 3 forecast entries (Stage 2, DCO, decision)"
  ```

  Run: `python -m pytest tests/test_build.py::test_cearn_content_files_exist -v`
  Expected: FAIL.

- [ ] **Step 2: Create data/cearn/content/timeline.json**

  Seed from `key_dates` in `data/cearn/cearn-solar-farm-sources.json`. Each entry:
  ```json
  {
    "id": "ct001",
    "date": "2022-11-24",
    "date_precision": "day",
    "event": "Manor Solar Farm consultation event at Denchworth Village Hall",
    "status": "confirmed",
    "source_url": "https://www.westchallow.org/news/solar-farm-pv-proposal-east-of-denchworth-invitation-to-a-consultation",
    "source_label": "West Challow: Manor Solar Farm consultation notice",
    "last_checked": "2026-11-01"
  }
  ```
  For future entries (Stage 2 consultation, DCO application, acceptance decision), use `"status": "forecast"`. IDs run `ct001` through `ct018` (one per key_date entry in the JSON). Use `date_precision: "year"`, `"month"`, or `"day"` as appropriate from the data.

  Mark these as forecast (`status: forecast`):
  - "23 November 2026: Vale scoping response" -- confirmed deadline, so `confirmed`
  - "December 2026: Scoping Opinion expected" -- `forecast`
  - "February to March 2027: Stage 2 consultation" -- `forecast`
  - "September 2027: DCO application" -- `forecast`
  - "Late 2027 to 2029: Examination and decision" -- `forecast`

- [ ] **Step 3: Create data/cearn/content/quotes.json**

  Seed from `council_positions` (4 entries) plus any stated positions from `representatives` and `project-context.md`. Schema follows reservoir `quotes.json`. IDs run `cq001`+. Example:
  ```json
  {
    "id": "cq001",
    "speaker": "Vale of White Horse District Council",
    "role": "Statutory consultee; local planning authority",
    "date": "2026-10-21",
    "quote": "The Vale Council passed a motion calling for solar development to prioritise non-agricultural land, avoid high-grade farmland, and consider cumulative impacts with the White Horse Reservoir and other local infrastructure projects.",
    "source_url": "https://www.whitehorsedc.gov.uk/vale-of-white-horse-district-council/planning-and-development/nationally-significant-infrastructure-projects-nsips/cearn-solar-farm/",
    "source_label": "Vale of White Horse: Cearn Solar Farm page",
    "last_checked": "2026-11-01"
  }
  ```

- [ ] **Step 4: Create data/cearn/content/actions.json**

  Seed from `how_to_get_involved` (9 entries). Schema follows reservoir `actions.json`. IDs run `ca001`+. Map `when` to `timing` using: "Now" → `now`; "February to March 2027" → `on-submission`; "After acceptance" → `on-acceptance`; "During examination" → `on-acceptance`; "At any time" → `ongoing`; "After a decision" → `on-acceptance`. Set `is_legal_info: true` only for the judicial review entry.

  Important fields to add per the design spec:
  - Actions that write to the Vale: add `note: "The Vale is a statutory consultee, not the decision-maker. Its planning committee has no vote on the application. Ask it to strengthen its Local Impact Report."` (rendered on the page).
  - Decision-maker for any letter action: set `letter_key: desnz-secretary-of-state` for actions targeting DESNZ.

- [ ] **Step 5: Run the tests**

  ```bash
  python -m pytest tests/test_build.py -v
  ```

  Expected: all passing including the two new tests.

- [ ] **Step 6: Commit**

  ```bash
  git add data/cearn/content/
  git commit -m "data: seed Cearn timeline, quotes and actions content"
  ```

---

## Task 4: Generator Two-Project Support

**Files:**
- Modify: `generator/build.py` -- add `load_cearn_data()`, extend `load_all_data()`, add `cearn_*` keys to build context, handle `status: forecast` on timeline items

**Interfaces:**
- Produces: `load_all_data()` returns additional keys: `cearn_timeline`, `cearn_quotes`, `cearn_actions`, `cearn_featured_actions`, `cearn_news_items`
- Consumed by: all new solar templates (Tasks 7, 8, 9, 10)

- [ ] **Step 1: Write the failing test**

  ```python
  # in tests/test_build.py -- add:
  def test_cearn_keys_in_context():
      data = load_all_data()
      for key in ["cearn_timeline", "cearn_quotes", "cearn_actions", "cearn_news_items"]:
          assert key in data, f"Missing key: {key}"

  def test_cearn_timeline_forecast_flag():
      data = load_all_data()
      forecasts = [e for e in data["cearn_timeline"] if e.get("is_forecast")]
      assert len(forecasts) >= 3
  ```

  Run: `python -m pytest tests/test_build.py::test_cearn_keys_in_context -v`
  Expected: FAIL (keys not yet in context).

- [ ] **Step 2: Add load_cearn_data() to generator/build.py**

  Add after the existing `load_all_data()` function:

  ```python
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

      return {
          "cearn_timeline": timeline,
          "cearn_quotes":   quotes,
          "cearn_actions":  actions,
          "cearn_news_items": cearn_news,
      }
  ```

- [ ] **Step 3: Call load_cearn_data() from load_all_data()**

  At the end of `load_all_data()`, before the `return` statement:

  ```python
  cearn_data = load_cearn_data()
  ```

  Merge into the return dict:
  ```python
  return {
      # ... existing keys ...
      "cearn_timeline":   cearn_data["cearn_timeline"],
      "cearn_quotes":     cearn_data["cearn_quotes"],
      "cearn_actions":    cearn_data["cearn_actions"],
      "cearn_news_items": cearn_data["cearn_news_items"],
  }
  ```

- [ ] **Step 4: Add cearn solar letter recipients to _build_lookup_data()**

  In `_build_lookup_data()`, alongside the existing `defra_recipient`, add a `desnz` recipient read from `data/cearn/content/letters/desnz-secretary-of-state.md` (created in Task 9). For now use a placeholder:

  ```python
  desnz_recipient = {
      "name": "Miatta Fahnbulleh MP",
      "email": "",
      "address": "Ministerial Correspondence Team, Level 3, 55 Whitehall, London SW1A 2HP",
  }
  ```

  Add to the `letter_recipients` dict: `"desnz": desnz_recipient`.

- [ ] **Step 5: Add solar pages to the build() page list**

  In `build()`, extend the `pages` list:

  ```python
  ("solar-facts.html", "solar-facts.html"),
  ("solar-actions.html", "solar-actions.html"),
  ("solar-letters.html", "solar-letters.html"),
  ("combined-impacts.html", "combined-impacts.html"),
  ```

  These templates do not exist yet; the build will fail until Tasks 7-10 create them. Wrap the new entries in a try/except or gate them behind `template_name in env.list_templates()` for now.

- [ ] **Step 6: Run the tests**

  ```bash
  python -m pytest tests/test_build.py -v
  ```

  Expected: all passing including the two new tests.

- [ ] **Step 7: Commit**

  ```bash
  git add generator/build.py tests/test_build.py
  git commit -m "feat: extend generator for two-project support (cearn context keys)"
  ```

---

## Task 5: Shared Representatives Merged Model

**Files:**
- Modify: `data/reservoir/representatives.csv` -- add `projects` column; tag existing entries as `reservoir`; merge in cearn-only and dual-role entries
- No changes to `data/cearn/representatives.csv` (kept as cearn source of truth)

**Interfaces:**
- Produces: `data/reservoir/representatives.csv` with a `projects` column; 12 shared reps tagged `reservoir,cearn`; 3 dual-role reps appear as two records each
- Consumed by: `generator/build.py` `_build_lookup_data()`, `lookup.js`

- [ ] **Step 1: Write the failing test**

  ```python
  # in tests/test_lookup_data.py -- add:
  def test_reservoir_reps_have_projects_field():
      with open("data/reservoir/representatives.csv", encoding="utf-8") as f:
          reader = csv.DictReader(f)
          assert "projects" in reader.fieldnames, "projects column missing from representatives.csv"

  def test_shared_reps_tagged_both_projects():
      shared_names = {"Bethia Thomas", "Charlie Maynard", "Hannah Griffin", "James Plumb",
                      "Jenny Hannaby", "Jill Rayner", "Layla Moran", "Lee Evans",
                      "Olly Glover", "Robert Clegg", "Ron Batstone",
                      "Sally Whiteman (nee Povolotsky)"}
      with open("data/reservoir/representatives.csv", encoding="utf-8") as f:
          rows = list(csv.DictReader(f))
      # For each shared name, at least one row must be tagged "reservoir,cearn"
      tagged = {r["name"].strip() for r in rows if "cearn" in r.get("projects", "")}
      for name in shared_names:
          assert name in tagged, f"{name} not tagged with both projects"
  ```

- [ ] **Step 2: Add projects column to data/reservoir/representatives.csv**

  Add a `projects` column as the last column. Set `projects=reservoir` for all existing 34 rows. For the 12 shared names (those also in the cearn CSV), update to `projects=reservoir,cearn`. For the 3 dual-role reps, ADD a second row from the cearn CSV (with their County/District role respectively), also tagged `reservoir,cearn`.

  Check step: confirm no row has an empty `projects` field. Total rows after: 34 original + 3 extra dual-mandate rows = 37 rows.

- [ ] **Step 3: Update _build_lookup_data() to filter by project**

  In `generator/build.py` `_build_lookup_data()`, the lookup now passes `projects` to the client so `lookup.js` can filter representatives relevant to a given postcode's projects. Add `"projects": r.get("projects", "reservoir")` to each rep entry in the `reps` list.

- [ ] **Step 4: Run the tests**

  ```bash
  python -m pytest tests/ -q
  ```

  Expected: all tests pass (including the two new ones).

- [ ] **Step 5: Commit**

  ```bash
  git add data/reservoir/representatives.csv generator/build.py tests/test_lookup_data.py
  git commit -m "data: add projects field to representatives; tag shared reps reservoir,cearn"
  ```

---

## Task 6: Navigation Update

**Files:**
- Modify: `templates/base.html` -- two-tier nav with project dropdowns; CSS in `docs/assets/style.css`

**Interfaces:**
- Produces: all generated pages have a nav with Reservoir and Solar Farm sections; `aria-current="page"` on the active item

- [ ] **Step 1: Write the failing test**

  ```python
  # in tests/test_build.py -- add:
  def test_nav_contains_both_projects():
      build()
      html = Path("docs/index.html").read_text(encoding="utf-8")
      assert "Solar Farm" in html
      assert "Reservoir" in html
      assert "Combined Impacts" in html
  ```

- [ ] **Step 2: Update templates/base.html nav**

  Replace the existing `<nav>` block with a two-tier nav. Exact HTML:

  ```html
  <nav aria-label="Site navigation">
    <ul class="nav-primary">
      <li><a href="index.html" {% if page_id == 'home' %}aria-current="page"{% endif %}>Home</a></li>
      <li class="has-dropdown">
        <a href="facts.html" {% if page_id in ('res-facts','res-actions','res-letters','access-points') %}aria-current="true"{% endif %}>Reservoir</a>
        <ul class="nav-dropdown">
          <li><a href="facts.html" {% if page_id == 'res-facts' %}aria-current="page"{% endif %}>Facts &amp; timeline</a></li>
          <li><a href="actions.html" {% if page_id == 'res-actions' %}aria-current="page"{% endif %}>What you can do</a></li>
          <li><a href="letters.html" {% if page_id == 'res-letters' %}aria-current="page"{% endif %}>Write letters</a></li>
          <li><a href="access-points.html" {% if page_id == 'access-points' %}aria-current="page"{% endif %}>Access points</a></li>
        </ul>
      </li>
      <li class="has-dropdown">
        <a href="solar-facts.html" {% if page_id in ('solar-facts','solar-actions','solar-letters') %}aria-current="true"{% endif %}>Solar Farm</a>
        <ul class="nav-dropdown">
          <li><a href="solar-facts.html" {% if page_id == 'solar-facts' %}aria-current="page"{% endif %}>Facts &amp; timeline</a></li>
          <li><a href="solar-actions.html" {% if page_id == 'solar-actions' %}aria-current="page"{% endif %}>What you can do</a></li>
          <li><a href="solar-letters.html" {% if page_id == 'solar-letters' %}aria-current="page"{% endif %}>Write letters</a></li>
        </ul>
      </li>
      <li><a href="combined-impacts.html" {% if page_id == 'combined' %}aria-current="page"{% endif %}>Combined Impacts</a></li>
      <li><a href="about.html" {% if page_id == 'about' %}aria-current="page"{% endif %}>About</a></li>
    </ul>
  </nav>
  ```

  Pass `page_id` to each template render call in `build()`.

- [ ] **Step 3: Add nav CSS to docs/assets/style.css**

  Add dropdown CSS: desktop hover-reveal (`.has-dropdown:hover .nav-dropdown { display: block; }`), mobile hidden-by-default with a checkbox-hack toggle. The existing style.css must not break; add the dropdown rules after the existing nav rules.

- [ ] **Step 4: Run the test**

  Run: `python -m pytest tests/test_build.py::test_nav_contains_both_projects -v`
  Expected: PASS.

  Run full suite: `python -m pytest tests/ -q`
  Expected: all passing.

- [ ] **Step 5: Commit**

  ```bash
  git add templates/base.html docs/assets/style.css generator/build.py
  git commit -m "feat: two-project navigation in base.html"
  ```

---

## Task 7: Solar Facts Page

**Files:**
- Create: `templates/solar-facts.html`
- No new data files

**Interfaces:**
- Consumes: `cearn_timeline`, `cearn_quotes` from `load_all_data()`
- Produces: `docs/solar-facts.html`

- [ ] **Step 1: Write the failing test**

  ```python
  # in tests/test_build.py -- add:
  def test_solar_facts_page_generated():
      build()
      html = Path("docs/solar-facts.html").read_text(encoding="utf-8")
      assert "EN0110044" in html
      assert "Cearn Solar Farm" in html

  def test_solar_facts_has_forecast_label():
      build()
      html = Path("docs/solar-facts.html").read_text(encoding="utf-8")
      assert "forecast" in html.lower()
  ```

- [ ] **Step 2: Create templates/solar-facts.html**

  Sections:
  1. `<h1>Cearn Solar Farm (EN0110044)</h1>` -- project label in heading; link to Combined Impacts.
  2. Scheme summary table: applicant (Telis Energy UK), size (up to 500MW, ~2,800 acres), location (south of Garford, east of Charney Bassett, north of West Hanney, south of Goosey, north-east of Baulking), decision-maker (DESNZ Secretary of State), Planning Inspectorate reference (EN0110044). All values from `data/cearn/project-context.md` content or `cearn-solar-farm-sources.json`.
  3. Timeline: loop over `cearn_timeline`, reverse-chronological. Forecast entries get `<span class="forecast-label">(forecast)</span>` and `class="forecast-item"`.
  4. Positions section: loop over `cearn_quotes`, grouped by tier.
  5. Note: "The Vale of White Horse is a statutory consultee, not the planning authority for this application."
  6. Links: Planning Inspectorate EN0110044 page, Protect the Vale, Cearn developer site.

- [ ] **Step 3: Add forecast-item CSS to style.css**

  Add: `.forecast-label { color: var(--color-muted); font-style: italic; }` and `.forecast-item { border-left: 3px solid var(--color-muted); }`.

- [ ] **Step 4: Run the tests and full suite**

  ```bash
  python -m pytest tests/ -q
  ```

  Expected: all passing.

- [ ] **Step 5: Commit**

  ```bash
  git add templates/solar-facts.html docs/assets/style.css
  git commit -m "feat: solar facts page (solar-facts.html)"
  ```

---

## Task 8: Solar Actions Page

**Files:**
- Create: `templates/solar-actions.html`

**Interfaces:**
- Consumes: `cearn_actions` from `load_all_data()`
- Produces: `docs/solar-actions.html`

- [ ] **Step 1: Write the failing test**

  ```python
  def test_solar_actions_page_generated():
      build()
      html = Path("docs/solar-actions.html").read_text(encoding="utf-8")
      assert "DESNZ" in html or "Energy Security" in html
      assert "statutory consultee" in html.lower()
  ```

- [ ] **Step 2: Create templates/solar-actions.html**

  Structure mirrors `actions.html`. Add a banner at the top:

  > "The Vale of White Horse is a statutory consultee for this application, not the decision-maker. Write to your Vale councillors asking them to strengthen the Vale's Local Impact Report -- not to block the scheme. The decision is made by the Secretary of State for Energy Security and Net Zero (DESNZ), not Defra."

  Group actions by timing (`now`, `on-submission`, `on-acceptance`, `ongoing`). Each action shows: who can do it, when, how, source link, and a "Generate letter" button where `letter_key` is set (linking to `solar-letters.html#{{action.letter_key}}`).

- [ ] **Step 3: Run the tests**

  ```bash
  python -m pytest tests/ -q
  ```

- [ ] **Step 4: Commit**

  ```bash
  git add templates/solar-actions.html
  git commit -m "feat: solar actions page (solar-actions.html)"
  ```

---

## Task 9: Solar Letters Page and Templates

**Files:**
- Create: `templates/solar-letters.html`
- Create: `data/cearn/content/letters/desnz-secretary-of-state.md`
- Create: `data/cearn/content/letters/cearn-developer.md`
- Create: `data/cearn/content/letters/solar-mp.md`
- Create: `data/cearn/content/letters/solar-county-councillor.md`
- Create: `data/cearn/content/letters/solar-district-councillor.md`
- Create: `data/cearn/content/letters/solar-planning-inspectorate.md`

**Interfaces:**
- Consumes: cearn letter templates via `_build_letters_data()` (extend to read cearn letters dir)
- Produces: `docs/solar-letters.html`; cearn letter templates in `assets/letters-data.json`

- [ ] **Step 1: Write the failing tests**

  ```python
  def test_solar_letters_page_generated():
      build()
      html = Path("docs/solar-letters.html").read_text(encoding="utf-8")
      assert "DESNZ" in html or "Energy Security" in html
      assert "desnz-secretary-of-state" in html

  def test_desnz_letter_has_postal_address():
      build()
      html = Path("docs/solar-letters.html").read_text(encoding="utf-8")
      assert "55 Whitehall" in html

  def test_combined_impact_placeholder_in_solar_letter():
      data = _build_letters_data()
      assert "{{combined_impact_para}}" in data.get("desnz-secretary-of-state", {}).get("body", "")
  ```

- [ ] **Step 2: Create the six letter templates**

  All templates use the same frontmatter + body format. Each body includes `{{combined_impact_para}}` as a removable placeholder. DESNZ template explicitly states no email address is published and gives postal address only. District councillor template explains the Vale's role as statutory consultee.

  `desnz-secretary-of-state.md` frontmatter:
  ```yaml
  ---
  title: Write to the Secretary of State for Energy Security and Net Zero
  recipient_name: Miatta Fahnbulleh MP
  recipient_address: "Ministerial Correspondence Team, Level 3, 55 Whitehall, London SW1A 2HP"
  recipient_email: ""
  note: "There is no published ministerial email address. This letter must be sent by post."
  project: cearn
  ---
  ```

  `solar-district-councillor.md` body must include the note: "I understand the Vale of White Horse is a statutory consultee for this application and that its planning committee does not vote on it. I am writing to ask you to ensure the Vale's Local Impact Report addresses..."

- [ ] **Step 3: Extend _build_letters_data() to read cearn letters**

  In `generator/build.py`, update `_build_letters_data()` to iterate over both `data/reservoir/content/letters/` and `data/cearn/content/letters/`. Tag each entry with `project: cearn` or `project: reservoir` from the frontmatter (add `project` field to templates).

- [ ] **Step 4: Create templates/solar-letters.html**

  Mirrors `letters.html`. The combined-impact checkbox replaces `{{combined_impact_para}}` with a standard paragraph or removes the placeholder. The paragraph text:

  > "I also wish to draw your attention to the cumulative impact of the proposed Cearn Solar Farm and the Thames Water White Horse Reservoir (WA010005). Both schemes would affect roads including the A338 through the Hanneys, the A417 and the A415 during overlapping construction periods estimated from 2029 onwards. No combined traffic or cumulative impact assessment has been published."

  This paragraph is only shown on solar letters; it is never inserted into reservoir letter templates.

- [ ] **Step 5: Run the tests**

  ```bash
  python -m pytest tests/ -q
  ```

  Expected: all passing.

- [ ] **Step 6: Commit**

  ```bash
  git add templates/solar-letters.html data/cearn/content/letters/ generator/build.py
  git commit -m "feat: solar letters page and six letter templates"
  ```

---

## Task 10: Combined Impacts Page

**Files:**
- Create: `templates/combined-impacts.html`
- Modify: `generator/build.py` -- expose `links_to_reservoir` dict in build context

**Interfaces:**
- Consumes: `links_to_reservoir` from `data/cearn/cearn-solar-farm-sources.json` (add to context)
- Produces: `docs/combined-impacts.html`

- [ ] **Step 1: Write the failing test**

  ```python
  def test_combined_impacts_page_generated():
      build()
      html = Path("docs/combined-impacts.html").read_text(encoding="utf-8")
      assert "A338" in html
      assert "not yet confirmed" in html.lower() or "not established" in html.lower()
  ```

- [ ] **Step 2: Expose links_to_reservoir in build context**

  In `load_cearn_data()`, read:
  ```python
  cearn_sources = json.loads((CEARN_DATA_DIR / "cearn-solar-farm-sources.json").read_text(encoding="utf-8"))
  links_to_reservoir = cearn_sources.get("links_to_reservoir", {})
  ```
  Return as `"links_to_reservoir": links_to_reservoir` and merge into `load_all_data()` return.

- [ ] **Step 3: Create templates/combined-impacts.html**

  Sections:
  1. `<h1>Combined Impacts</h1>` with intro: both projects are separate; they share roads and construction timelines.
  2. **Construction timing** -- tabbed or side-by-side: reservoir (main works from 2029/2032, over 10 years) vs. Cearn (decision ~2028, construction follows). Source: Thames Water and Cearn developer statements. Mark as "claimed (developer figures)" and "forecast".
  3. **Shared roads** -- A338 through the Hanneys, A417, A415. Source: `links_to_reservoir.construction_overlap`. Label: "not yet confirmed -- Cearn construction routes not published."
  4. **Combined land take** -- Protect the Vale figure of at least 5,300 acres. Label: "claimed (Protect the Vale figure, November 2026)."
  5. **Who has raised the combined impact** -- bulleted list from `links_to_reservoir.who_has_raised_it`. GARD's non-position stated: "GARD has not publicly linked the two projects."
  6. **GARD note** -- "GARD's campaign focuses on the White Horse Reservoir only. This page is independent of both GARD and Protect the Vale."

- [ ] **Step 4: Run the tests**

  ```bash
  python -m pytest tests/ -q
  ```

- [ ] **Step 5: Commit**

  ```bash
  git add templates/combined-impacts.html generator/build.py
  git commit -m "feat: combined impacts page"
  ```

---

## Task 11: Map Update (Two Boundaries)

**Files:**
- Modify: `docs/assets/map.js` -- add EN0110044 boundary layer, layer toggles, postcode result for both projects

**Interfaces:**
- Consumes: `data/cearn/boundary-parishes.json` (for layer labels); EN0110044 GeoJSON fetched at runtime from PINS or committed as a static file
- Produces: map shows both boundaries with independent layer toggles

- [ ] **Step 1: Write the failing test**

  ```python
  def test_map_js_references_both_projects():
      js = Path("docs/assets/map.js").read_text(encoding="utf-8")
      assert "WA010005" in js
      assert "EN0110044" in js
  ```

- [ ] **Step 2: Add EN0110044 boundary to map.js**

  If the GeoJSON was committed to `data/cearn/` in Task 2, copy it to `docs/assets/cearn-boundary.geojson` at build time (add to `build()` in `build.py`). If PINS serves it at a stable URL, fetch it at runtime in `map.js` with a fallback.

  In `map.js`:
  ```javascript
  // Layer toggles
  const layers = {
    reservoir: { color: '#2563eb', label: 'White Horse Reservoir (WA010005)' },
    cearn:     { color: '#d97706', label: 'Cearn Solar Farm (EN0110044)' },
  };
  // Fetch EN0110044 boundary
  fetch('assets/cearn-boundary.geojson')
    .then(r => r.ok ? r.json() : null)
    .then(data => {
      if (data) {
        L.geoJSON(data, { style: { color: layers.cearn.color, weight: 2, fillOpacity: 0.1 } })
          .addTo(map);
      } else {
        console.warn('Cearn boundary not available');
      }
    })
    .catch(() => console.warn('Cearn boundary fetch failed'));
  ```

- [ ] **Step 3: Layer control in map UI**

  Add two visible checkboxes above the map (not Leaflet's layer control, which requires a key):
  ```html
  <div class="map-layer-toggles">
    <label><input type="checkbox" id="show-reservoir" checked> Reservoir (WA010005)</label>
    <label><input type="checkbox" id="show-cearn" checked> Solar Farm (EN0110044)</label>
  </div>
  ```
  Wire them to `layer.setOpacity(0/1)` or `map.addLayer/removeLayer`.

- [ ] **Step 4: Run the tests**

  ```bash
  python -m pytest tests/ -q
  ```

- [ ] **Step 5: Commit**

  ```bash
  git add docs/assets/map.js docs/assets/cearn-boundary.geojson generator/build.py
  git commit -m "feat: add EN0110044 solar boundary to Leaflet map"
  ```

---

## Task 12: Pipeline Update for Cearn Sources

**Files:**
- Modify: `generator/fetch.py` -- add cearn source monitoring; log unmonitorable sources; warn on passed forecast dates

**Interfaces:**
- Produces: `data/cearn/fetched/news_items.json` updated by pipeline; forecast-date warnings in log

- [ ] **Step 1: Write the failing test**

  ```python
  # in tests/test_fetch.py -- add:
  def test_cearn_sources_loaded():
      from generator.fetch import load_sources
      sources = load_sources()
      cearn_sources = [s for s in sources if s.get("project") == "cearn"]
      assert len(cearn_sources) >= 5, "Expected at least 5 cearn monitoring sources"

  def test_forecast_date_warning_logged(caplog):
      from generator.fetch import check_forecast_dates
      import logging
      past_forecast = [{"date": "2020-01", "event": "Past forecast", "status": "forecast", "is_forecast": True}]
      with caplog.at_level(logging.WARNING):
          check_forecast_dates(past_forecast)
      assert "forecast date" in caplog.text.lower() or "passed without confirmation" in caplog.text.lower()
  ```

- [ ] **Step 2: Extend generator/fetch.py for cearn sources**

  Add a `load_cearn_sources()` function that reads `data/cearn/cearn-solar-farm-sources.json` and returns sources tagged `project: cearn`. Add monitoring for:
  - Planning Inspectorate EN0110044 (page-change detection)
  - Cearn developer site (page-change detection)
  - Protect the Vale (page-change detection)
  - Vale news RSS feed (filter for "Cearn" and "solar")
  - Charney Bassett PC RSS
  - East Hanney PC RSS
  - CPRE Oxfordshire RSS
  - Hansard / written questions API (add "Cearn" and "EN0110044" keywords)

  Sources with no usable feed (Goosey, Baulking, Denchworth, Garford, Lyford, Frilford, Hatford, Besselsleigh): log once per run: `"No automated monitoring for [name]: no online presence; manual check required."`

- [ ] **Step 3: Add check_forecast_dates() to fetch.py**

  ```python
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
  ```

  Call this from the cearn pipeline section on each run.

- [ ] **Step 4: Run the tests**

  ```bash
  python -m pytest tests/ -q
  ```

  Expected: all passing.

- [ ] **Step 5: Commit**

  ```bash
  git add generator/fetch.py tests/test_fetch.py
  git commit -m "feat: extend pipeline for Cearn source monitoring and forecast-date warnings"
  ```

---

## Tracked Follow-ups

The following items are known gaps to address manually or in a future session. They are NOT blocking for implementation; they are tracked here so they are not lost.

### From Cearn (cearn-solar-farm-sources.json: still_to_check_by_hand)

1. Which parishes are inside the Cearn boundary and cable corridor (addressed in Task 2; cable corridor parishes pending Stage 2, February to March 2027).
2. Scoping report contents once published on the PINS EN0110044 documents page: construction period, access routes, traffic, lifespan, battery size, cumulative list.
3. Final wording and vote on the Vale Cearn motion -- 21 October 2026 minutes not yet published.
4. MP positions on Cearn (Olly Glover, Charlie Maynard, Layla Moran): websites block automated checks.
5. Protect the Vale organisers, social media and any petition as they appear.
6. Original BBC and Herald Series article URLs (only mirrors found).
7. **10 November 2026**: Botley West decision -- check effect on Farmoor substation; update cearn data.
8. Manor Solar Farm construction start.
9. West Hanney, Kingston Bagpuize, Fyfield and Tubney sites for Cearn mentions (blocked or errors).
10. Charney Bassett next meeting date (18 or 11 November 2026) and 9 September 2026 minutes.
11. East Hanney extraordinary meeting of 24 August 2026: subject.
12. Which DESNZ minister will sign the decision (watch for a ministerial reshuffle).

### Key dates to watch

| Date | Action |
|---|---|
| 10 November 2026 | Check Botley West decision; update `nearby_solar_schemes` entry in cearn data |
| 23 November 2026 | Vale scoping response deadline; add Vale response to `cearn_quotes` when published |
| December 2026 | Scoping Opinion expected; update EN0110044 PINS documents page |
| February to March 2027 | Stage 2 opens; update cearn actions to "Stage 2 now open"; add cable corridor parishes to `boundary-parishes.json` |
| September 2027 | DCO application expected; switch cearn pipeline to daily acceptance-decision monitoring |
| 1 April 2028 | Ridgeway Council vesting; update all local council records for both projects |

### From Reservoir (carried from original design, section 14)

Items 1-11 from `docs/superpowers/specs/2026-11-01-white-horse-reservoir-design.md` section 14 remain open. Most critical for the two-project work: item 11 (access point coordinates) and item 7 (which parishes the reservoir footprint covers, needed for the Combined Impacts page).
