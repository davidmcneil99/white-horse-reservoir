# Vale Watch — Three-Section Redesign: Design Document

**Date:** 2026-11-03
**Author:** Design session with David McNeil
**Status:** Awaiting David's approval
**Extends:** `docs/superpowers/specs/2026-11-01-two-projects-design.md`

---

## 1. Intent

Rename and restructure the site from a single-project page ("White Horse Reservoir") into a three-section community resource called **Vale Watch**, covering both the White Horse Reservoir (WA010005) and Cearn Solar Farm (EN0110044) as distinct sections, with a Combined Concerns section for cumulative impacts.

The site presents itself as an independent community resource, not affiliated with GARD or Protect the Vale.

---

## 2. Goals

- Give the site a name and structure that reflects its two-project scope.
- Let a resident who cares only about one project navigate it without noise from the other.
- Give a resident who cares about both a single combined view of the timeline, actions and letters.
- Keep all existing content, URLs for shared/linked content, and the generator pipeline intact.

---

## 3. Non-goals

- Renaming the GitHub repository or changing the GitHub Pages URL (`davidmcneil99.github.io/white-horse-reservoir/`). The Vale Watch name lives in the page title and header only.
- Merging the two projects' planning processes or decision-makers into one narrative.
- Redesigning the visual theme or colour palette.

---

## 4. Site Name

| Before | After |
|---|---|
| White Horse Reservoir (page title, header wordmark) | Vale Watch |

The wordmark "Vale Watch" appears in the global `<header>` on every page, as a home link pointing to `/reservoir/` (the default landing section).

---

## 5. URL Structure

All pages move into one of three subfolders. The root `index.html` redirects to `/reservoir/`. Existing flat URLs (e.g. `facts.html`) become 404s; any inbound links that matter will be noted in the plan and given redirect `<meta>` tags.

```
docs/
  index.html                     ← meta-refresh redirect to reservoir/
  about.html                     ← shared About page (builder call — see §13)
  reservoir/
    index.html                   ← Reservoir Home
    facts.html                   ← Reservoir Facts & Timeline
    actions.html                 ← Reservoir Actions
    letters.html                 ← Reservoir Letters
  solar/
    index.html                   ← Solar Farm Home
    facts.html                   ← Solar Facts & Timeline
    actions.html                 ← Solar Actions
    letters.html                 ← Solar Letters
  combined/
    index.html                   ← Combined Concerns Home
    facts.html                   ← Combined Facts & Timeline
    actions.html                 ← Combined Actions
    letters.html                 ← Combined Letters
  assets/
    map.js, lookup.js, style.css, …   (unchanged paths)
```

The generator's `build()` function is updated to write to these paths. `PAGES` list is restructured accordingly.

---

## 6. Global Header

Replaces the current single-tier nav entirely. Present on every page.

```
┌─────────────────────────────────────────────────────────────────┐
│  Vale Watch   [White Horse Reservoir] [Combined Concerns] [Solar Farm]  │
└─────────────────────────────────────────────────────────────────┘
```

- **Vale Watch** wordmark: links to `/reservoir/`.
- Three section tabs. The active section tab is highlighted (e.g. underline + bold). Clicking a tab navigates to that section's `index.html`.
- On mobile: the three tabs stack or collapse to a hamburger that expands to show the three section options, then the secondary nav below.
- No dropdown sub-items in the global header — those live in the secondary nav.

---

## 7. Secondary Navigation Bar

Sits directly below the global header. Its links change based on the active section. All secondary navs share the same five tab labels; their `href` targets change per section.

| Tab | Reservoir | Solar Farm | Combined |
|---|---|---|---|
| Home | `/reservoir/` | `/solar/` | `/combined/` |
| Facts & Timeline | `/reservoir/facts.html` | `/solar/facts.html` | `/combined/facts.html` |
| Actions | `/reservoir/actions.html` | `/solar/actions.html` | `/combined/actions.html` |
| Letters | `/reservoir/letters.html` | `/solar/letters.html` | `/combined/letters.html` |
| About | `/about.html` | `/about.html` | `/about.html` |

Current page is marked with `aria-current="page"` on its tab.

---

## 8. Section Home Pages (`index.html`)

Each section's home page has four blocks in this order:

1. **Blurb** — two or three sentences on what this section covers and why it matters. Section-specific copy (see §12 for Combined).
2. **Most urgent actions** — the `featured_actions` panel (already implemented for Reservoir; Solar and Combined versions added).
3. **Map** — the Leaflet map, filtered to this section's boundary:
   - Reservoir home: WA010005 boundary only, reservoir access points.
   - Solar home: EN0110044 boundary only.
   - Combined home: both boundaries, layer toggles.
4. **Latest news** — the `news_items` feed, filtered to this section's project (`reservoir`, `cearn`, or both).

The map's postcode lookup on the Reservoir and Solar homes returns representatives and letter recipients for that project only. On the Combined home it returns all representatives, tagged by project.

---

## 9. Combined Concerns Section

### 9.1 Combined Home (`/combined/`)

Same four-block structure as other homes. Blurb: introduces both projects, explains the shared construction corridor and cumulative land take, and links to the Combined Facts & Timeline.

### 9.2 Combined Facts & Timeline (`/combined/facts.html`)

A single merged, reverse-chronological timeline drawn from both `timeline` (reservoir) and `cearn_timeline` (solar). Each entry carries a colour-coded project tag:

- **Blue tag** — White Horse Reservoir (matches the reservoir map boundary colour)
- **Amber tag** — Solar Farm (matches the solar map boundary colour)
- Entries with `links_to_reservoir` relevance may carry both tags.

Forecast entries carry the "(forecast)" label as in the individual sections.

### 9.3 Combined Actions (`/combined/actions.html`)

Full merged list of actions from both `actions` and `cearn_actions`, each carrying the same blue/amber project tag. Grouped by timing (`now`, `on-submission`, `on-acceptance`, `ongoing`) with the tag making the project clear within each group.

### 9.4 Combined Letters (`/combined/letters.html`)

All letter templates from both `data/reservoir/content/letters/` and `data/cearn/content/letters/`, grouped by project (Reservoir section, then Solar section), each carrying the project tag. The combined-impact paragraph opt-in checkbox is shown on Combined Letters only.

---

## 10. Map Changes

The map JavaScript (`docs/assets/map.js`) is updated to accept a `section` parameter passed from each page (via a `data-section` attribute on the map container or an inline variable set by the template):

- `section="reservoir"` — show WA010005 layer only; hide EN0110044 layer and its toggle.
- `section="solar"` — show EN0110044 layer only; hide WA010005 layer and its toggle.
- `section="combined"` — show both layers with independent toggles (existing Combined Impacts behaviour).

The postcode lookup (`lookup.js`) filters `lookup-data.json` by the same `section` value so results show only relevant representatives.

---

## 11. Generator Changes

### 11.1 Path constants

```python
DOCS_RES_DIR   = DOCS_DIR / "reservoir"
DOCS_SOLAR_DIR = DOCS_DIR / "solar"
DOCS_COMB_DIR  = DOCS_DIR / "combined"
```

### 11.2 Pages list (restructured)

```python
pages = [
    # Root
    ("root-redirect.html", "index.html"),
    ("about.html",          "about.html"),
    # Reservoir
    ("reservoir/index.html",   "reservoir/index.html"),
    ("reservoir/facts.html",   "reservoir/facts.html"),
    ("reservoir/actions.html", "reservoir/actions.html"),
    ("reservoir/letters.html", "reservoir/letters.html"),
    # Solar
    ("solar/index.html",   "solar/index.html"),
    ("solar/facts.html",   "solar/facts.html"),
    ("solar/actions.html", "solar/actions.html"),
    ("solar/letters.html", "solar/letters.html"),
    # Combined
    ("combined/index.html",   "combined/index.html"),
    ("combined/facts.html",   "combined/facts.html"),
    ("combined/actions.html", "combined/actions.html"),
    ("combined/letters.html", "combined/letters.html"),
]
```

Each template receives a `section` context key (`"reservoir"`, `"solar"`, `"combined"`, or `None` for About).

### 11.3 Template reorganisation

Templates move from a flat `templates/` list to a matching subfolder structure:

```
templates/
  base.html                    ← global header + secondary nav (section-aware)
  root-redirect.html           ← meta-refresh to reservoir/
  about.html
  reservoir/
    index.html
    facts.html
    actions.html
    letters.html
  solar/
    index.html
    facts.html
    actions.html
    letters.html
  combined/
    index.html
    facts.html
    actions.html
    letters.html
```

### 11.4 Existing flat templates

The current flat templates (`solar-facts.html`, `solar-actions.html`, `solar-letters.html`, `combined-impacts.html`, `facts.html`, `actions.html`, `letters.html`, `access-points.html`) are replaced by the subfolder versions. `access-points.html` moves to `reservoir/access-points.html` and gets a secondary nav entry added as a sixth tab for the Reservoir section only.

### 11.5 Redirect stubs

The following old flat URLs get a `<meta http-equiv="refresh">` stub so inbound links do not hard-404:

| Old URL | Redirects to |
|---|---|
| `facts.html` | `reservoir/facts.html` |
| `actions.html` | `reservoir/actions.html` |
| `letters.html` | `reservoir/letters.html` |
| `solar-facts.html` | `solar/facts.html` |
| `solar-actions.html` | `solar/actions.html` |
| `solar-letters.html` | `solar/letters.html` |
| `combined-impacts.html` | `combined/` |
| `access-points.html` | `reservoir/access-points.html` |

---

## 12. Page IDs and Active-State Rules

Every page receives a `page_id` context key used for `aria-current` in both navs.

| Page | `page_id` |
|---|---|
| `/reservoir/` | `reservoir-home` |
| `/reservoir/facts.html` | `reservoir-facts` |
| `/reservoir/actions.html` | `reservoir-actions` |
| `/reservoir/letters.html` | `reservoir-letters` |
| `/reservoir/access-points.html` | `reservoir-access` |
| `/solar/` | `solar-home` |
| `/solar/facts.html` | `solar-facts` |
| `/solar/actions.html` | `solar-actions` |
| `/solar/letters.html` | `solar-letters` |
| `/combined/` | `combined-home` |
| `/combined/facts.html` | `combined-facts` |
| `/combined/actions.html` | `combined-actions` |
| `/combined/letters.html` | `combined-letters` |
| `/about.html` | `about` |

**Active section tab rule:** the global header highlights the section tab whose prefix matches the `page_id` prefix (`reservoir-*` → Reservoir tab, `solar-*` → Solar tab, `combined-*` → Combined tab). When `page_id` is `about`, no section tab is highlighted (builder call — a shared About belongs to no one section).

**Asset paths:** All asset references in `base.html` use root-relative paths including the GitHub Pages subpath (e.g. `/white-horse-reservoir/assets/style.css`). This convention is unchanged and works correctly from pages in any subfolder depth. The wordmark link to the home page must also be root-relative: `/white-horse-reservoir/reservoir/`.

---

## 13. Featured Actions for Solar and Combined

The `featured_actions` panel on each Home page requires `featured: true` and a `featured_order` field in the relevant `actions.json`. These are not yet seeded in the cearn content data. The builder must add them.

### Solar featured actions (add to `data/cearn/content/actions.json`)

| `featured_order` | Action | `id` | Rationale |
|---|---|---|---|
| 1 | Sign up for Planning Inspectorate EN0110044 email updates | ca001 | Free, immediate, no commitment |
| 2 | Ask your Vale ward councillor to press for the scoping response (deadline 23 Nov 2026) | ca002 | Time-sensitive; Vale motion passed 21 Oct |
| 3 | Contact the developer with your concerns | ca003 | Pre-application window open now |

Set `featured: true` and `featured_order: 1/2/3` on those three entries. The `featured_actions_intro` for the solar home: *"These are the most time-sensitive actions right now. The Vale's scoping response is due 23 November 2026."*

### Combined featured actions (add to `data/combined/content/actions.json` — new file)

A new combined actions content file is created by the generator from both action lists, but featured combined actions are defined separately in `data/combined/content/featured-actions.json` (a short list):

| `featured_order` | Action | Source |
|---|---|---|
| 1 | Write to your MP about both projects — ask them to call for a joint cumulative impact assessment | new entry |
| 2 | Ask your Vale district councillor to press for a combined traffic assessment covering both schemes | new entry |

The `featured_actions_intro` for the combined home: *"Both projects are in active pre-application consultation. These actions address their shared impacts."*

---

## 14. Section Blurbs (copy)

**Reservoir home:**
> "Thames Water proposes to build a large reservoir in the Vale of White Horse to supply the South East of England. This is a nationally significant infrastructure project (WA010005). The Planning Inspectorate examines the application; the Secretary of State for Environment, Food and Rural Affairs decides."

**Solar Farm home:**
> "Telis Energy UK proposes a 500 MW solar and battery storage scheme covering around 2,800 acres near Garford, Charney Bassett, West Hanney, Goosey and Baulking. This is a nationally significant infrastructure project (EN0110044). The Secretary of State for Energy Security and Net Zero decides."

**Combined Concerns home:**
> "Two large nationally significant infrastructure projects are proposed in the Vale of White Horse at the same time. This section covers the issues they share: overlapping construction periods, shared roads including the A338 through the Hanneys and the A417, and a combined land take of at least 5,300 acres. Each project has its own decision-maker and its own planning process."

---

## 15. Builder Calls (this designer's decisions)

- **About is one shared page** at `/about.html`, linked from all three sections' secondary navs. A separate About per section would duplicate content. David can override this.
- **Access points is Reservoir-only**, appearing as a sixth secondary nav tab for the Reservoir section only (no solar or combined equivalent yet).
- **Colour tags use the existing map colours**: blue (`#2563eb`) for Reservoir, amber (`#d97706`) for Solar. These are already defined in `map.js` and can be extracted to a CSS custom property for use in tags.
- **Root redirect is a meta-refresh**, not a server redirect, because GitHub Pages has no redirect config. A `<meta http-equiv="refresh" content="0;url=reservoir/">` stub is the standard approach here.
- **Template subfolder structure** mirrors the URL subfolder structure exactly, one template per output page.

---

## 16. Dependency

This design builds on the V5 two-project work (PR #17, branch `feature/v5-two-projects`). PR #17 must be merged into `main` before implementation begins, so that the solar pages and cearn data pipeline are in place to restructure.

---

## 17. Risks

- **Inbound links to old flat URLs:** mitigated by redirect stubs (§11.5). The GARD and Protect the Vale sites may link to old URLs; the stubs prevent hard 404s.
- **`data-**` path trigger in GitHub Actions workflow:** the workflow triggers on `data/**` — this is unaffected by the URL restructure since data files don't move.
- **PR #17 merge first:** if PR #17 is not merged, the solar templates and cearn pipeline are absent and Tasks 3+ cannot proceed.
