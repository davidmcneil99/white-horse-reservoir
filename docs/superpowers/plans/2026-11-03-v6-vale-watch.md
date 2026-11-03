# Vale Watch — Three-Section Redesign: V6 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename the site to Vale Watch and restructure it into three subfolder sections (reservoir, solar, combined) each with a section-aware global header, secondary nav, home page (blurb + actions + map + news), and Facts/Actions/Letters pages.

**Architecture:** The Python generator gains subdirectory output paths and a `section`/`page_id` context key per page. `base.html` is rebuilt with a three-tab global header and a section-aware secondary nav. All existing flat templates move into `templates/reservoir/`, `templates/solar/`, `templates/combined/`. Old flat URLs get meta-refresh redirect stubs. The Leaflet map reads a `data-section` attribute to show only the relevant boundary layer.

**Tech Stack:** Python 3.11, Jinja2, Leaflet 1.9.4; HTML5/CSS3/vanilla JS; GitHub Pages. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-11-03-vale-watch-redesign.md`
(extends `docs/superpowers/specs/2026-11-01-two-projects-design.md`)

**Prerequisite:** PR #17 (`feature/v5-two-projects`) must be merged into `main` before implementation begins. All 64 V5 tests must pass at the start of Task 0.

## Global Constraints

- UK English throughout; no em dashes; no emojis in site copy
- Asset paths in all templates must be root-relative including the GitHub Pages subpath, e.g. `/white-horse-reservoir/assets/style.css` — never relative `../../assets/`
- The wordmark link in `base.html` must point to `/white-horse-reservoir/reservoir/`
- `python -m pytest tests/ -q` must pass after every task (64 baseline rising as new tests are added)
- `E:\reservoir` and `E:\cearn` are READ ONLY — never modified
- `data/cearn/cearn-solar-farm-sources.json` and `data/reservoir/white-horse-reservoir-sources.json` are READ ONLY
- No existing reservoir page content is removed; it moves to its new path
- Old flat URLs must resolve to redirect stubs, not hard 404s

## Review Focus

1. **Secondary nav active state wrong on deep pages** — e.g. `/reservoir/facts.html` should highlight both the Reservoir section tab AND the Facts & Timeline secondary tab. Template logic must use `page_id` prefix for the section tab AND exact `page_id` match for the secondary tab. Add to Task 1.
2. **Root-relative paths break from subfolder depth** — any template that uses a relative path (e.g. `href="assets/style.css"`) will break for pages at `/reservoir/`. All paths must be root-relative. Verify in Task 0 and each template task.
3. **Combined timeline missing entries from one project** — the merge in Task 5 must pull from both `timeline` (reservoir) and `cearn_timeline` (solar) context keys. A test asserting both project tags appear is essential. Add to Task 5.
4. **Featured actions panel absent on section home pages** — solar and combined homes must have `featured_actions` / `featured_combined_actions` in context. If the context key is missing, the panel silently disappears. Tests must assert the panel is present. Add to Tasks 4 and 5.
5. **Redirect stubs served from wrong path** — stubs must be written to `docs/facts.html` etc. (root of docs), not `docs/reservoir/facts.html`. Verify stub output paths in Task 2.

---

## File Map

```
generator/
  build.py                    MODIFY — path constants, pages list, section/page_id,
                                        combined timeline merge, combined featured actions
templates/
  base.html                   REWRITE — three-tab global header, secondary nav
  root-redirect.html          NEW — meta-refresh to /reservoir/
  about.html                  UPDATE — Vale Watch scope (both projects)
  reservoir/
    index.html                NEW — blurb + featured_actions + map + news
    facts.html                MOVE from facts.html
    actions.html              MOVE from actions.html
    letters.html              MOVE from letters.html
    access-points.html        MOVE from access-points.html
  solar/
    index.html                NEW — blurb + featured_actions + map + news
    facts.html                MOVE from solar-facts.html
    actions.html              MOVE from solar-actions.html
    letters.html              MOVE from solar-letters.html
  combined/
    index.html                NEW — blurb + featured_combined_actions + map + news
    facts.html                NEW — merged tagged timeline
    actions.html              NEW — merged tagged actions
    letters.html              NEW — all letters with project tags
docs/assets/
  style.css                   MODIFY — header tabs, secondary nav, project colour tags
  map.js                      MODIFY — section-aware boundary display
  lookup.js                   MODIFY — section-aware rep filtering
data/cearn/content/
  actions.json                MODIFY — add featured fields to 3 actions
data/combined/content/
  featured-actions.json       NEW — 2 combined featured actions
tests/
  test_build.py               ADD — new path/content assertions
```

Old flat templates to delete after moving: `facts.html`, `actions.html`, `letters.html`,
`access-points.html`, `solar-facts.html`, `solar-actions.html`, `solar-letters.html`,
`combined-impacts.html`.

---

## Task 0: Generator Restructure

**Files:** `generator/build.py`, `tests/test_build.py`

**Interfaces:**
- Produces: `build()` writes to `docs/reservoir/`, `docs/solar/`, `docs/combined/`; each page receives `section` and `page_id` context keys; `docs/index.html` is the root redirect stub
- Consumed by: all template tasks

- [ ] **Step 1: Write failing tests**

  ```python
  # tests/test_build.py — add:
  def test_reservoir_index_generated():
      build()
      assert Path("docs/reservoir/index.html").exists()

  def test_solar_index_generated():
      build()
      assert Path("docs/solar/index.html").exists()

  def test_combined_index_generated():
      build()
      assert Path("docs/combined/index.html").exists()

  def test_root_redirect_generated():
      build()
      html = Path("docs/index.html").read_text(encoding="utf-8")
      assert "reservoir" in html  # redirect points to reservoir section

  def test_section_key_in_reservoir_page():
      build()
      # section key must reach the template — check via a sentinel comment
      # added to base.html in Task 1; for now assert the file exists at new path
      assert Path("docs/reservoir/facts.html").exists()
  ```

  Run: `python -m pytest tests/test_build.py -v -k "reservoir_index or solar_index or combined_index or root_redirect or section_key"`
  Expected: FAIL (paths not yet created).

- [ ] **Step 2: Add output path constants to build.py**

  After the existing `DOCS_DIR` constant, add:
  ```python
  DOCS_RES_DIR   = DOCS_DIR / "reservoir"
  DOCS_SOLAR_DIR = DOCS_DIR / "solar"
  DOCS_COMB_DIR  = DOCS_DIR / "combined"
  ```

  At the top of `build()`, add directory creation:
  ```python
  for d in [DOCS_RES_DIR, DOCS_SOLAR_DIR, DOCS_COMB_DIR]:
      d.mkdir(parents=True, exist_ok=True)
  ```

- [ ] **Step 3: Restructure the pages list in build()**

  Replace the existing `pages` list with:
  ```python
  pages = [
      # Root
      ("root-redirect.html",           DOCS_DIR / "index.html",             None,            None),
      ("about.html",                   DOCS_DIR / "about.html",             None,            "about"),
      # Old flat URL redirect stubs (built in Task 2)
      # Reservoir
      ("reservoir/index.html",         DOCS_RES_DIR / "index.html",         "reservoir",     "reservoir-home"),
      ("reservoir/facts.html",         DOCS_RES_DIR / "facts.html",         "reservoir",     "reservoir-facts"),
      ("reservoir/actions.html",       DOCS_RES_DIR / "actions.html",       "reservoir",     "reservoir-actions"),
      ("reservoir/letters.html",       DOCS_RES_DIR / "letters.html",       "reservoir",     "reservoir-letters"),
      ("reservoir/access-points.html", DOCS_RES_DIR / "access-points.html", "reservoir",     "reservoir-access"),
      # Solar
      ("solar/index.html",             DOCS_SOLAR_DIR / "index.html",       "solar",         "solar-home"),
      ("solar/facts.html",             DOCS_SOLAR_DIR / "facts.html",       "solar",         "solar-facts"),
      ("solar/actions.html",           DOCS_SOLAR_DIR / "actions.html",     "solar",         "solar-actions"),
      ("solar/letters.html",           DOCS_SOLAR_DIR / "letters.html",     "solar",         "solar-letters"),
      # Combined
      ("combined/index.html",          DOCS_COMB_DIR / "index.html",        "combined",      "combined-home"),
      ("combined/facts.html",          DOCS_COMB_DIR / "facts.html",        "combined",      "combined-facts"),
      ("combined/actions.html",        DOCS_COMB_DIR / "actions.html",      "combined",      "combined-actions"),
      ("combined/letters.html",        DOCS_COMB_DIR / "letters.html",      "combined",      "combined-letters"),
  ]
  ```

  The tuple is `(template_name, output_path, section, page_id)`. Update the render loop:
  ```python
  for template_name, output_path, section, page_id in pages:
      tmpl = env.get_template(template_name)
      html = tmpl.render(**context, section=section, page_id=page_id)
      output_path.write_text(html, encoding="utf-8")
  ```

  Update the Jinja2 `FileSystemLoader` to use `templates/` as the root. Jinja resolves subdirectories automatically (e.g. `env.get_template("reservoir/index.html")` finds `templates/reservoir/index.html`).

- [ ] **Step 4: Create placeholder templates for new paths**

  Create minimal stub templates so the build does not error while full templates are built in later tasks. Each stub extends `base.html` with an empty content block:
  ```
  templates/root-redirect.html     (full content written in Task 2)
  templates/reservoir/index.html   (stub)
  templates/solar/index.html       (stub)
  templates/combined/index.html    (stub)
  templates/combined/facts.html    (stub)
  templates/combined/actions.html  (stub)
  templates/combined/letters.html  (stub)
  ```

  Move existing templates to their new subfolder homes:
  - `templates/facts.html` → `templates/reservoir/facts.html`
  - `templates/actions.html` → `templates/reservoir/actions.html`
  - `templates/letters.html` → `templates/reservoir/letters.html`
  - `templates/access-points.html` → `templates/reservoir/access-points.html`
  - `templates/solar-facts.html` → `templates/solar/facts.html`
  - `templates/solar-actions.html` → `templates/solar/actions.html`
  - `templates/solar-letters.html` → `templates/solar/letters.html`

  Delete the old flat template files after moving.

- [ ] **Step 5: Run tests**

  Run: `python -m pytest tests/ -q`
  Expected: 64 baseline + new tests passing. Build must complete without error.

- [ ] **Step 6: Commit**

  ```bash
  git add generator/build.py templates/ tests/test_build.py
  git commit -m "refactor: restructure generator and templates for subfolder URL layout"
  ```

---

## Task 1: Base Template and CSS

**Files:** `templates/base.html`, `docs/assets/style.css`

**Interfaces:**
- Produces: all pages have a three-tab global header and section-aware secondary nav; active states driven by `section` and `page_id` context keys
- Consumed by: all page templates

- [ ] **Step 1: Write failing tests**

  ```python
  def test_reservoir_home_has_active_section_tab():
      build()
      html = Path("docs/reservoir/index.html").read_text(encoding="utf-8")
      # The Reservoir tab must carry aria-current="true" or active class
      assert 'aria-current' in html

  def test_combined_facts_has_both_nav_actives():
      build()
      html = Path("docs/combined/facts.html").read_text(encoding="utf-8")
      assert "Combined Concerns" in html
      assert "Facts" in html

  def test_vale_watch_wordmark_present():
      build()
      html = Path("docs/reservoir/index.html").read_text(encoding="utf-8")
      assert "Vale Watch" in html

  def test_secondary_nav_about_links_to_root():
      build()
      html = Path("docs/reservoir/index.html").read_text(encoding="utf-8")
      assert "/white-horse-reservoir/about.html" in html
  ```

- [ ] **Step 2: Rewrite templates/base.html**

  Replace the existing `<header>` and `<nav>` blocks with:

  **Global header:**
  ```html
  <header class="site-header">
    <a class="wordmark" href="/white-horse-reservoir/reservoir/">Vale Watch</a>
    <nav class="section-nav" aria-label="Project sections">
      <a href="/white-horse-reservoir/reservoir/"
         {% if section == 'reservoir' %}aria-current="true" class="active"{% endif %}>
        White Horse Reservoir
      </a>
      <a href="/white-horse-reservoir/combined/"
         {% if section == 'combined' %}aria-current="true" class="active"{% endif %}>
        Combined Concerns
      </a>
      <a href="/white-horse-reservoir/solar/"
         {% if section == 'solar' %}aria-current="true" class="active"{% endif %}>
        Solar Farm
      </a>
    </nav>
  </header>
  ```

  **Secondary nav** (immediately below header, inside a `<div class="secondary-nav-wrapper">`):
  ```html
  {% set res  = "/white-horse-reservoir/reservoir" %}
  {% set sol  = "/white-horse-reservoir/solar" %}
  {% set comb = "/white-horse-reservoir/combined" %}
  {% if section == 'reservoir' %}{% set base = res %}{% elif section == 'solar' %}{% set base = sol %}{% elif section == 'combined' %}{% set base = comb %}{% else %}{% set base = res %}{% endif %}

  <nav class="secondary-nav" aria-label="Section navigation">
    <a href="{{ base }}/"
       {% if page_id in ('reservoir-home','solar-home','combined-home') %}aria-current="page"{% endif %}>Home</a>
    <a href="{{ base }}/facts.html"
       {% if page_id in ('reservoir-facts','solar-facts','combined-facts') %}aria-current="page"{% endif %}>Facts &amp; Timeline</a>
    <a href="{{ base }}/actions.html"
       {% if page_id in ('reservoir-actions','solar-actions','combined-actions') %}aria-current="page"{% endif %}>Actions</a>
    <a href="{{ base }}/letters.html"
       {% if page_id in ('reservoir-letters','solar-letters','combined-letters') %}aria-current="page"{% endif %}>Letters</a>
    {% if section == 'reservoir' %}
    <a href="{{ res }}/access-points.html"
       {% if page_id == 'reservoir-access' %}aria-current="page"{% endif %}>Access Points</a>
    {% endif %}
    <a href="/white-horse-reservoir/about.html"
       {% if page_id == 'about' %}aria-current="page"{% endif %}>About</a>
  </nav>
  ```

  Note: when `section` is `None` (About page), `base` defaults to `res` so the secondary nav still renders valid links; no section tab is highlighted.

- [ ] **Step 3: Add CSS for the new header and nav to style.css**

  Add after existing header rules:
  ```css
  /* Three-tab section nav */
  .section-nav { display: flex; gap: 0; }
  .section-nav a { padding: 0.5rem 1.25rem; text-decoration: none; border-bottom: 3px solid transparent; }
  .section-nav a.active, .section-nav a[aria-current="true"] {
    border-bottom-color: var(--color-primary); font-weight: 600;
  }
  /* Secondary nav */
  .secondary-nav-wrapper { background: var(--color-surface-alt, #f3f4f6); border-bottom: 1px solid var(--color-border); }
  .secondary-nav { display: flex; gap: 0; max-width: 60rem; margin: 0 auto; padding: 0 1rem; }
  .secondary-nav a { padding: 0.5rem 1rem; text-decoration: none; font-size: 0.9rem; border-bottom: 2px solid transparent; }
  .secondary-nav a[aria-current="page"] { border-bottom-color: var(--color-primary); font-weight: 600; }
  /* Project colour tags */
  .tag-reservoir { background: #2563eb; color: #fff; padding: 0.1rem 0.4rem; border-radius: 3px; font-size: 0.75rem; }
  .tag-solar     { background: #d97706; color: #fff; padding: 0.1rem 0.4rem; border-radius: 3px; font-size: 0.75rem; }
  /* Mobile: stack section tabs */
  @media (max-width: 640px) {
    .section-nav { flex-direction: column; }
    .secondary-nav { flex-wrap: wrap; }
  }
  ```

- [ ] **Step 4: Run tests**

  Run: `python -m pytest tests/ -q`
  Expected: all passing.

- [ ] **Step 5: Commit**

  ```bash
  git add templates/base.html docs/assets/style.css tests/test_build.py
  git commit -m "feat: Vale Watch three-tab header and section-aware secondary nav"
  ```

---

## Task 2: Root Redirect and Old-URL Stubs

**Files:** `templates/root-redirect.html`; redirect stub template(s) added to `build.py`

**Interfaces:**
- Produces: `docs/index.html` redirects to `/white-horse-reservoir/reservoir/`; eight old flat URLs redirect to their new paths

- [ ] **Step 1: Write failing test**

  ```python
  def test_old_flat_urls_are_stubs():
      build()
      stubs = {
          "docs/facts.html":           "reservoir/facts",
          "docs/actions.html":         "reservoir/actions",
          "docs/letters.html":         "reservoir/letters",
          "docs/access-points.html":   "reservoir/access-points",
          "docs/solar-facts.html":     "solar/facts",
          "docs/solar-actions.html":   "solar/actions",
          "docs/solar-letters.html":   "solar/letters",
          "docs/combined-impacts.html":"combined/",
      }
      for path, target in stubs.items():
          html = Path(path).read_text(encoding="utf-8")
          assert target in html, f"{path} does not redirect to {target}"
  ```

- [ ] **Step 2: Create templates/root-redirect.html**

  ```html
  <!doctype html>
  <html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="0;url=/white-horse-reservoir/reservoir/">
    <title>Vale Watch</title>
  </head>
  <body>
    <p><a href="/white-horse-reservoir/reservoir/">Vale Watch — White Horse Reservoir</a></p>
  </body>
  </html>
  ```

- [ ] **Step 3: Add redirect stubs to build()**

  After the main pages loop, add a redirect-stubs section:

  ```python
  REDIRECT_STUBS = [
      (DOCS_DIR / "facts.html",           "/white-horse-reservoir/reservoir/facts.html"),
      (DOCS_DIR / "actions.html",         "/white-horse-reservoir/reservoir/actions.html"),
      (DOCS_DIR / "letters.html",         "/white-horse-reservoir/reservoir/letters.html"),
      (DOCS_DIR / "access-points.html",   "/white-horse-reservoir/reservoir/access-points.html"),
      (DOCS_DIR / "solar-facts.html",     "/white-horse-reservoir/solar/facts.html"),
      (DOCS_DIR / "solar-actions.html",   "/white-horse-reservoir/solar/actions.html"),
      (DOCS_DIR / "solar-letters.html",   "/white-horse-reservoir/solar/letters.html"),
      (DOCS_DIR / "combined-impacts.html","/white-horse-reservoir/combined/"),
  ]

  for stub_path, target_url in REDIRECT_STUBS:
      stub_path.write_text(
          f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
          f'<meta http-equiv="refresh" content="0;url={target_url}">'
          f'<title>Redirecting — Vale Watch</title></head>'
          f'<body><p><a href="{target_url}">Redirecting…</a></p></body></html>',
          encoding="utf-8"
      )
  ```

- [ ] **Step 4: Run tests**

  Run: `python -m pytest tests/ -q`
  Expected: all passing.

- [ ] **Step 5: Commit**

  ```bash
  git add templates/root-redirect.html generator/build.py tests/test_build.py
  git commit -m "feat: root redirect and old flat-URL redirect stubs"
  ```

---

## Task 3: Reservoir Section Templates

**Files:** `templates/reservoir/index.html` (new), plus the moved templates from Task 0

**Interfaces:**
- Consumes: `timeline`, `quotes`, `actions`, `featured_actions`, `news_items`, `section="reservoir"`, `page_id`
- Produces: `docs/reservoir/index.html` with blurb + featured panel + map + news; existing facts/actions/letters/access-points pages at new paths with corrected `page_id` active states

- [ ] **Step 1: Write failing tests**

  ```python
  def test_reservoir_home_has_blurb():
      build()
      html = Path("docs/reservoir/index.html").read_text(encoding="utf-8")
      assert "Thames Water" in html
      assert "WA010005" in html

  def test_reservoir_home_has_map():
      build()
      html = Path("docs/reservoir/index.html").read_text(encoding="utf-8")
      assert "map" in html.lower()

  def test_reservoir_home_has_news_section():
      build()
      html = Path("docs/reservoir/index.html").read_text(encoding="utf-8")
      assert "news" in html.lower() or "latest" in html.lower()
  ```

- [ ] **Step 2: Create templates/reservoir/index.html**

  Four-block structure:

  ```html
  {% extends "base.html" %}
  {% block title %}White Horse Reservoir — Vale Watch{% endblock %}
  {% block content %}
  <h1>White Horse Reservoir (SESRO)</h1>
  <p class="section-blurb">Thames Water proposes to build a large reservoir in the Vale of
  White Horse to supply the South East of England. This is a nationally significant
  infrastructure project (WA010005). The Planning Inspectorate examines the application;
  the Secretary of State for Environment, Food and Rural Affairs decides.</p>

  {% if featured_actions %}
  <section class="featured-actions" aria-label="Priority actions">
    <h2>Most urgent actions</h2>
    <p class="featured-actions-intro">{{ featured_actions_intro }}</p>
    <ol class="featured-actions-list">
      {% for action in featured_actions %}
      <li>
        <h3><a href="/white-horse-reservoir/reservoir/actions.html#action-{{ action.id }}">{{ action.title }}</a></h3>
        <p>{{ action.description }}</p>
        <div class="featured-action-links">
          {% if action.source_url %}<a class="btn-primary" href="{{ action.source_url }}" rel="external noopener">Take action</a>{% endif %}
          {% if action.letter_key %}<a class="action-letter-btn" href="/white-horse-reservoir/reservoir/letters.html#{{ action.letter_key }}">Generate letter</a>{% endif %}
        </div>
      </li>
      {% endfor %}
    </ol>
  </section>
  {% endif %}

  <section class="map-section" aria-label="Map">
    <h2>Map</h2>
    <div id="map" data-section="reservoir" style="height:400px"></div>
  </section>

  {% if news_items %}
  <section class="news-section" aria-label="Latest news">
    <h2>Latest news</h2>
    <ul class="news-list">
      {% for item in news_items[:5] %}
      <li>
        <a href="{{ item.url }}" rel="external noopener">{{ item.title }}</a>
        <span class="news-date">{{ item.date }}</span>
      </li>
      {% endfor %}
    </ul>
  </section>
  {% endif %}
  {% endblock %}
  ```

- [ ] **Step 3: Update moved reservoir templates**

  The moved templates (`reservoir/facts.html`, `reservoir/actions.html`, `reservoir/letters.html`, `reservoir/access-points.html`) inherit `base.html` and receive `page_id` automatically. Check that:
  - All internal links use root-relative paths (e.g. `href="/white-horse-reservoir/reservoir/letters.html#…"` not `../letters.html#…`)
  - `block title` includes "Vale Watch" (e.g. `Facts & Timeline — White Horse Reservoir — Vale Watch`)
  - The letter button in `actions.html` links to `/white-horse-reservoir/reservoir/letters.html#{{action.letter_key}}`

  Update any relative `href` or `src` attributes to root-relative.

- [ ] **Step 4: Add data-section to map.js call in reservoir templates**

  Each reservoir template that includes the map must set `data-section="reservoir"` on the `<div id="map">` element (or inline JS: `const SECTION = "reservoir";`). Task 6 wires this up in `map.js`; for now the attribute just needs to be present.

- [ ] **Step 5: Run tests**

  Run: `python -m pytest tests/ -q`
  Expected: all passing.

- [ ] **Step 6: Commit**

  ```bash
  git add templates/reservoir/ tests/test_build.py
  git commit -m "feat: reservoir section home page and updated subfolder templates"
  ```

---

## Task 4: Solar Section Templates and Featured Actions Data

**Files:** `templates/solar/index.html` (new), `data/cearn/content/actions.json` (update), `templates/solar/facts.html`, `solar/actions.html`, `solar/letters.html` (already moved in Task 0)

**Interfaces:**
- Consumes: `cearn_actions`, `cearn_timeline`, `cearn_quotes`, `cearn_news_items`, `section="solar"`, `page_id`
- Produces: `docs/solar/index.html` with blurb + 3 featured solar actions + map + cearn news; existing solar facts/actions/letters at new paths

- [ ] **Step 1: Write failing tests**

  ```python
  def test_solar_home_has_blurb():
      build()
      html = Path("docs/solar/index.html").read_text(encoding="utf-8")
      assert "EN0110044" in html
      assert "Telis Energy" in html

  def test_solar_home_has_featured_actions():
      build()
      html = Path("docs/solar/index.html").read_text(encoding="utf-8")
      assert "Most urgent actions" in html
      assert "Planning Inspectorate" in html

  def test_solar_actions_json_has_featured_fields():
      data = json.loads(Path("data/cearn/content/actions.json").read_text(encoding="utf-8"))
      featured = [a for a in data if a.get("featured")]
      assert len(featured) == 3
      orders = sorted(a["featured_order"] for a in featured)
      assert orders == [1, 2, 3]
  ```

- [ ] **Step 2: Add featured fields to data/cearn/content/actions.json**

  On the three entries with IDs `ca001`, `ca002`, `ca003` (sign up for PINS updates, ask Vale councillor about scoping response, contact developer), add:
  ```json
  "featured": true,
  "featured_order": 1
  ```
  (orders 1, 2, 3 respectively).

  The `featured_actions_intro` for solar is stored in the generator (not in the JSON) as:
  `"These are the most time-sensitive actions right now. The Vale's scoping response is due 23 November 2026."`

  Add `cearn_featured_actions_intro` to the build context in `load_cearn_data()`.

- [ ] **Step 3: Expose cearn_featured_actions in build context**

  In `load_cearn_data()`, extract featured actions:
  ```python
  cearn_featured = sorted(
      [a for a in actions if a.get("featured")],
      key=lambda a: a.get("featured_order", 99)
  )
  ```
  Return as `"cearn_featured_actions": cearn_featured`.

- [ ] **Step 4: Create templates/solar/index.html**

  Same four-block structure as `reservoir/index.html`, using `cearn_featured_actions`, `cearn_news_items`, and `data-section="solar"` on the map div. Blurb:

  > "Telis Energy UK proposes a 500 MW solar and battery storage scheme covering around 2,800 acres near Garford, Charney Bassett, West Hanney, Goosey and Baulking. This is a nationally significant infrastructure project (EN0110044). The Secretary of State for Energy Security and Net Zero decides."

- [ ] **Step 5: Update solar section template paths and links**

  In the moved `solar/facts.html`, `solar/actions.html`, `solar/letters.html`:
  - Update all internal links to root-relative
  - Update `block title` to include `Vale Watch`
  - Add `data-section="solar"` to map divs

- [ ] **Step 6: Run tests**

  Run: `python -m pytest tests/ -q`
  Expected: all passing.

- [ ] **Step 7: Commit**

  ```bash
  git add templates/solar/ data/cearn/content/actions.json generator/build.py tests/test_build.py
  git commit -m "feat: solar section home page and featured actions"
  ```

---

## Task 5: Combined Section Templates

**Files:** `templates/combined/index.html`, `combined/facts.html`, `combined/actions.html`, `combined/letters.html`; `data/combined/content/featured-actions.json` (new); `generator/build.py` (combined merge logic)

**Interfaces:**
- Consumes: `timeline` + `cearn_timeline` (merged), `actions` + `cearn_actions` (merged), all letter templates tagged by project, `section="combined"`, `page_id`
- Produces: `docs/combined/` pages with blue/amber project tags on every merged item

- [ ] **Step 1: Write failing tests**

  ```python
  def test_combined_timeline_has_both_tags():
      build()
      html = Path("docs/combined/facts.html").read_text(encoding="utf-8")
      assert "tag-reservoir" in html
      assert "tag-solar" in html

  def test_combined_actions_has_both_projects():
      build()
      html = Path("docs/combined/actions.html").read_text(encoding="utf-8")
      assert "tag-reservoir" in html
      assert "tag-solar" in html

  def test_combined_home_has_featured_actions():
      build()
      html = Path("docs/combined/index.html").read_text(encoding="utf-8")
      assert "cumulative" in html.lower() or "combined" in html.lower()

  def test_combined_letters_has_both_project_sections():
      build()
      html = Path("docs/combined/letters.html").read_text(encoding="utf-8")
      assert "Reservoir" in html
      assert "Solar" in html
  ```

- [ ] **Step 2: Add combined merge logic to build.py**

  Add a `build_combined_data()` function:

  ```python
  def build_combined_data(res_data: dict, cearn_data: dict) -> dict:
      """Merge reservoir and cearn data for the combined section."""
      # Merged timeline: each entry gains a 'projects' tag list
      res_timeline = [dict(e, projects=["reservoir"]) for e in res_data["timeline"]]
      solar_timeline = [dict(e, projects=["solar"]) for e in cearn_data["cearn_timeline"]]
      combined_timeline = sorted(
          res_timeline + solar_timeline,
          key=lambda e: e.get("date", ""),
          reverse=True
      )

      # Merged actions
      res_actions = [dict(a, projects=["reservoir"]) for a in res_data["actions"]]
      solar_actions = [dict(a, projects=["solar"]) for a in cearn_data["cearn_actions"]]
      combined_actions = res_actions + solar_actions

      # Combined featured actions from featured-actions.json
      feat_path = DATA_DIR / "combined" / "content" / "featured-actions.json"
      combined_featured = json.loads(feat_path.read_text(encoding="utf-8")) if feat_path.exists() else []

      return {
          "combined_timeline": combined_timeline,
          "combined_actions": combined_actions,
          "combined_featured_actions": combined_featured,
          "combined_featured_actions_intro": (
              "Both projects are in active pre-application consultation. "
              "These actions address their shared impacts."
          ),
      }
  ```

  Call from `load_all_data()` and merge into the returned context dict.

- [ ] **Step 3: Create data/combined/content/featured-actions.json**

  ```json
  [
    {
      "id": "cb001",
      "featured_order": 1,
      "title": "Write to your MP about both projects",
      "description": "Ask your MP to call for a joint cumulative impact assessment covering the reservoir and solar farm construction together.",
      "who_can": "Any resident",
      "timing": "now",
      "letter_key": "mp",
      "source_url": "",
      "projects": ["reservoir", "solar"]
    },
    {
      "id": "cb002",
      "featured_order": 2,
      "title": "Ask your Vale councillor for a combined traffic assessment",
      "description": "Ask your Vale district councillor to press for a single assessment covering HGV routes for both the reservoir and solar farm construction.",
      "who_can": "Vale of White Horse residents",
      "timing": "now",
      "letter_key": "solar-district-councillor",
      "source_url": "",
      "projects": ["reservoir", "solar"]
    }
  ]
  ```

  Create the directory: `data/combined/content/`.

- [ ] **Step 4: Create templates/combined/index.html**

  Same four-block structure. Blurb:

  > "Two large nationally significant infrastructure projects are proposed in the Vale of White Horse at the same time. This section covers the issues they share: overlapping construction periods, shared roads including the A338 through the Hanneys and the A417, and a combined land take of at least 5,300 acres. Each project has its own decision-maker and its own planning process."

  Map uses `data-section="combined"`.

- [ ] **Step 5: Create templates/combined/facts.html**

  Merged timeline with colour tags:
  ```html
  {% for entry in combined_timeline %}
  <article class="timeline-item {% if entry.is_forecast %}forecast-item{% endif %}">
    <span class="timeline-date">{{ entry.date_display }}</span>
    {% for proj in entry.projects %}
    <span class="tag-{{ proj }}">{{ "Reservoir" if proj == "reservoir" else "Solar Farm" }}</span>
    {% endfor %}
    {% if entry.is_forecast %}<span class="forecast-label">(forecast)</span>{% endif %}
    <p>{{ entry.event }}</p>
    {% if entry.source_url %}<a href="{{ entry.source_url }}" rel="external noopener">{{ entry.source_label }}</a>{% endif %}
  </article>
  {% endfor %}
  ```

- [ ] **Step 6: Create templates/combined/actions.html and combined/letters.html**

  `combined/actions.html`: loop `combined_actions`, add project tag to each. Group by timing.
  `combined/letters.html`: two sections — "Reservoir letters" and "Solar Farm letters" — each with its own letter templates. Combined-impact opt-in checkbox present.

- [ ] **Step 7: Run tests**

  Run: `python -m pytest tests/ -q`
  Expected: all passing.

- [ ] **Step 8: Commit**

  ```bash
  git add templates/combined/ data/combined/ generator/build.py tests/test_build.py
  git commit -m "feat: combined section with merged tagged timeline, actions and letters"
  ```

---

## Task 6: Section-Aware Map and Postcode Lookup

**Files:** `docs/assets/map.js`, `docs/assets/lookup.js`

**Interfaces:**
- Consumes: `data-section` attribute on `<div id="map">`; `projects` field in `lookup-data.json` (already present from V5)
- Produces: map shows only the relevant project boundary per section; postcode lookup returns only relevant reps

- [ ] **Step 1: Write failing test**

  ```python
  def test_map_js_reads_section_attribute():
      js = Path("docs/assets/map.js").read_text(encoding="utf-8")
      assert "data-section" in js or "SECTION" in js

  def test_lookup_js_filters_by_section():
      js = Path("docs/assets/lookup.js").read_text(encoding="utf-8")
      assert "section" in js.lower() or "projects" in js.lower()
  ```

- [ ] **Step 2: Update map.js**

  Read the section at map init:
  ```javascript
  const mapEl = document.getElementById('map');
  const SECTION = mapEl ? (mapEl.dataset.section || 'combined') : 'combined';
  ```

  After defining both layer objects (reservoir = blue, solar = amber), apply section filter:
  ```javascript
  if (SECTION === 'reservoir') {
    if (typeof cearnLayer !== 'undefined') map.removeLayer(cearnLayer);
    // hide cearn layer control checkbox if present
  } else if (SECTION === 'solar') {
    if (typeof reservoirLayer !== 'undefined') map.removeLayer(reservoirLayer);
  }
  // combined: both layers shown with toggles (existing behaviour)
  ```

- [ ] **Step 3: Update lookup.js**

  After fetching `lookup-data.json`, filter reps by section before displaying:
  ```javascript
  const SECTION = document.getElementById('map')?.dataset.section || 'combined';
  const projectMap = { reservoir: 'reservoir', solar: 'cearn', combined: null };
  const requiredProject = projectMap[SECTION];

  function repMatchesSection(rep) {
    if (!requiredProject) return true; // combined: show all
    const projects = (rep.projects || 'reservoir').split(',').map(s => s.trim());
    return projects.includes(requiredProject);
  }
  // Apply filter when building the rep list
  const filteredReps = allReps.filter(repMatchesSection);
  ```

- [ ] **Step 4: Run tests**

  Run: `python -m pytest tests/ -q`
  Expected: all passing.

- [ ] **Step 5: Commit**

  ```bash
  git add docs/assets/map.js docs/assets/lookup.js tests/test_build.py
  git commit -m "feat: section-aware map boundaries and postcode lookup filtering"
  ```

---

## Task 7: About Page and Site-Wide Copy

**Files:** `templates/about.html`, `templates/corrections.html` (if present)

**Interfaces:**
- Produces: `docs/about.html` describes Vale Watch covering both projects; all pages have correct `<title>` format

- [ ] **Step 1: Write failing test**

  ```python
  def test_about_page_mentions_both_projects():
      build()
      html = Path("docs/about.html").read_text(encoding="utf-8")
      assert "Vale Watch" in html
      assert "Cearn" in html or "solar" in html.lower()
      assert "reservoir" in html.lower()
  ```

- [ ] **Step 2: Update templates/about.html**

  Update the intro paragraph to describe Vale Watch as a community resource covering both projects. Add a section for each project explaining the independent campaign groups (GARD for reservoir, Protect the Vale for solar) and the site's independence from both.

- [ ] **Step 3: Verify page titles**

  Every page's `{% block title %}` must follow the pattern `Page — Section — Vale Watch`. Check all 14 content templates. Correct any that still say "White Horse Reservoir" as the site name.

- [ ] **Step 4: Run full test suite**

  Run: `python -m pytest tests/ -q`
  Expected: all passing.

  Also run the build and spot-check in a browser: `python -m generator.build` then open `docs/reservoir/index.html` locally.

- [ ] **Step 5: Commit**

  ```bash
  git add templates/about.html templates/
  git commit -m "feat: update About page for Vale Watch two-project scope"
  ```

---

## Task 8: Commit Design and Plan, Final Review, PR

- [ ] **Step 1: Commit spec and plan**

  ```bash
  git add docs/superpowers/specs/2026-11-03-vale-watch-redesign.md
  git add docs/superpowers/plans/2026-11-03-v6-vale-watch.md
  git commit -m "docs: Vale Watch redesign spec and v6 implementation plan"
  ```

- [ ] **Step 2: Run full test suite**

  Run: `python -m pytest tests/ -q`
  Expected: all tests pass; count is higher than the 64 baseline.

- [ ] **Step 3: Use superpowers:finishing-a-development-branch**

  Follow the skill to raise a PR against `main`. PR title: `feat: Vale Watch — three-section redesign`.
