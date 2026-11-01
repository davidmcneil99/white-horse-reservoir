# Two-Project Extension: Design Addendum

**Date:** 2026-11-01
**Author:** Design session with David McNeil
**Status:** Approved for implementation
**Extends:** `docs/superpowers/specs/2026-11-01-white-horse-reservoir-design.md`

---

## 1. Intent

Add Cearn Solar Farm (Planning Inspectorate EN0110044) as a second project alongside the White Horse Reservoir (WA010005). The site now covers both projects, with clearly distinct sections for each and a shared Combined Impacts area covering cumulative effects.

**Cearn Solar Farm** is a proposed 500MW solar and battery storage scheme (approximately 2,800 acres) around Garford, Charney Bassett, West Hanney, Goosey and Baulking in the Vale of White Horse. Applicant: Cearn Solar Farm Limited (wholly owned subsidiary of Telis Energy UK). Decision-maker: Secretary of State for Energy Security and Net Zero (currently Miatta Fahnbulleh). This is not the reservoir's solar relocation scheme; the two projects are separate.

The site supports Protect the Vale (<https://protect-the-vale.org.uk/>) for the Cearn section, presenting itself as an independent community resource — not Protect the Vale's official site. The same independence framing as GARD applies.

---

## 2. Goals Added by this Addendum

- Give any resident a clear path from "I heard about the solar farm" to "I have registered as an Interested Party" for EN0110044, at a different stage than the reservoir.
- Show the cumulative impact of both projects on shared roads, construction timelines, and land take, with clearly sourced and qualified statements.
- Make explicit that the Vale is a statutory consultee for Cearn, not the decision-maker, so letter recipients and actions are correct (DESNZ not Defra).
- Handle forecast dates gracefully: Stage 2 consultation (February to March 2027), DCO application (September 2027), decision (approximately 2028 to 2029).

---

## 3. New Non-goals

- Do not merge the two examinations or timelines into one stream; residents may oppose one project and not the other.
- Do not reproduce the developer's Stage 2 consultation materials before they are published.

---

## 4. Data Folder Reorganisation

### 4.1 Decision

Move the existing flat `data/` reservoir files into `data/reservoir/`. Add cearn files under `data/cearn/`. Code paths in `generator/build.py`, `generator/fetch.py` and all tests update accordingly.

```
data/
  reservoir/
    white-horse-reservoir-sources.json   (moved from data/)
    representatives.csv                  (merged, see 4.3)
    local-councils.csv                   (moved)
    access-points.csv                    (moved)
    national-and-other-sources.csv       (moved)
    overrides.json                       (moved)
    original-build.py                    (reference copy, not run)
    original-index.html                  (reference copy, not served)
    content/
      timeline.json
      quotes.json
      actions.json
      ward-aliases.json
      letters/
        mp.md
        county-councillor.md
        district-councillor.md
        parish-clerk.md
        thames-water.md
        planning-inspectorate-relevant-representation.md
        ofwat.md
        defra-secretary-of-state.md
        foi-missing-minutes.md
        eir-thames-water.md
    fetched/
      news_items.json
      page_hashes.json
  cearn/
    cearn-solar-farm-sources.json        (copied from E:\cearn)
    key-dates.csv
    nearby-solar-schemes.csv
    local-councils.csv
    representatives.csv
    council-positions.csv
    campaign-groups.csv
    national-and-other-sources.csv
    how-to-get-involved.csv
    README.md                            (copied from README_1.md, _1 stripped)
    project-context.md
    research-report.md
    build.py                             (original cearn build.py; not run by the app)
    index.html                           (copied from index_1.html; reference only)
    boundary-parishes.json               (produced by Task 2: boundary overlay)
    overrides.json                       (empty array to start)
    content/
      timeline.json                      (seeded from key_dates)
      quotes.json                        (seeded from council_positions)
      actions.json                       (seeded from how_to_get_involved)
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
```

### 4.2 Generator path constant

`generator/build.py` currently uses `DATA_DIR = _ROOT / "data"`. After the move:

```python
DATA_DIR      = _ROOT / "data"
RES_DATA_DIR  = DATA_DIR / "reservoir"
CEARN_DATA_DIR = DATA_DIR / "cearn"
```

All existing paths that previously used `DATA_DIR / "representatives.csv"` etc. change to `RES_DATA_DIR / ...`.

### 4.3 Shared representatives

Twelve representatives appear in both datasets. Three have apparent conflicts: **Jenny Hannaby**, **Lee Evans**, and **Ron Batstone** each appear as District in one dataset and County in the other. These are dual-mandate councillors who hold seats on both Oxfordshire County Council and the Vale of White Horse District Council. Both records are kept (different body, different email, different profile), each tagged with `projects: reservoir,cearn`. There is no duplication; the roles are genuinely distinct.

All other shared representatives are tagged with `projects: reservoir,cearn` in a single merged record in `data/reservoir/representatives.csv`. Cearn-only representatives are held in `data/cearn/representatives.csv`. The generator loads both and merges at build time, producing a combined `lookup-data.json` for the client-side postcode lookup.

`projects` field values: `reservoir`, `cearn`, `reservoir,cearn`.

---

## 5. Page and URL Structure

Existing reservoir pages keep their current URLs to preserve inbound links:

| Page | URL | Change |
|---|---|---|
| Homepage | `index.html` | Updated: both projects featured, nav updated |
| Reservoir facts | `facts.html` | Minor: project label added |
| Reservoir actions | `actions.html` | Minor: project label added |
| Reservoir letters | `letters.html` | Minor: project label |
| About | `about.html` | Updated: two campaigns described |
| Corrections | `corrections.html` | Updated: both project corrections |
| Access points | `access-points.html` | Reservoir only for now |

New pages:

| Page | URL |
|---|---|
| Solar facts | `solar-facts.html` |
| Solar actions | `solar-actions.html` |
| Solar letters | `solar-letters.html` |
| Combined impacts | `combined-impacts.html` |

---

## 6. Navigation

`base.html` is updated to a two-tier nav. Desktop: a horizontal bar with dropdowns. Mobile: a hamburger toggle with accordion expansion. No JavaScript dependency for display; CSS `:hover` for desktop, a single checkbox-hack for mobile toggle.

```
[Home]  [Reservoir ▾]  [Solar Farm ▾]  [Combined Impacts]  [About]
             |                |
        Facts           Solar Facts
        Actions         Solar Actions
        Letters         Solar Letters
        Access Points
```

Current page is highlighted with an `aria-current="page"` attribute. Project name is shown in the page `<h1>` so the context is unambiguous without relying on the nav highlight alone.

---

## 7. Forecast Dates

The Cearn timeline is at an earlier stage and includes forecast dates. The timeline entry schema gains an optional `status` field:

```json
{
  "id": "ct001",
  "date": "2027-02",
  "date_precision": "month",
  "event": "Stage 2 public consultation",
  "status": "forecast",
  "source_url": "https://cearnsolarfarm.co.uk/",
  "source_label": "Cearn developer: Stage 2 consultation",
  "last_checked": "2026-11-01"
}
```

`status` values: `confirmed` (default, rendered normally) or `forecast` (rendered with a "(forecast)" label and a `class="forecast"` for distinct styling). No `status` field implies `confirmed`.

---

## 8. Combined Impacts Area

`combined-impacts.html` is generated from `links_to_reservoir` in `data/cearn/cearn-solar-farm-sources.json`, supplemented by reservoir timeline entries that reference construction timing. Sections:

1. **Construction timing overlap** -- reservoir main works 2029–2039 (Thames Water), Cearn construction expected 2028–2029 onwards; marked as forecast where not confirmed.
2. **Shared roads** -- A338 through the Hanneys, A417, A415; sourced from `links_to_reservoir.construction_overlap`.
3. **Combined land take** -- Protect the Vale combined figure of at least 5,300 acres; clearly attributed.
4. **Who has raised the cumulative issue** -- sourced list from `links_to_reservoir.who_has_raised_it`.

Every statement is labelled `confirmed`, `claimed` (developer or campaign figure) or `not yet confirmed`. GARD's position (has not linked the two projects) is stated accurately.

---

## 9. Map (Two Boundaries)

The existing Leaflet map is extended to show both Planning Inspectorate boundaries:

- **WA010005** (reservoir): already shown, currently the official DCO boundary GeoJSON from PINS; colour: blue.
- **EN0110044** (solar): GeoJSON from PINS `/projects/EN0110044/download-boundary`; committed to `data/cearn/` after download in Task 2; colour: amber.

Layer toggles: two checkboxes in the map UI let the user show/hide each boundary independently. Each layer's checkbox is labelled with the project name and Planning Inspectorate reference.

The postcode lookup result shows which project area(s) the postcode is inside or near. Distance calculation uses the centroid of each boundary polygon.

---

## 10. Letter Templates (Solar)

Solar letter templates are in `data/cearn/content/letters/`. All follow the same Markdown frontmatter + `{{placeholder}}` body format as reservoir templates.

**Decision-maker note in every solar letter:** Each template includes a note that the Vale of White Horse is a statutory consultee, not the decision-maker; letters to the Vale ask it to represent residents in its Local Impact Report, not to rule on the application. The decision-maker for Cearn is the Secretary of State for Energy Security and Net Zero (DESNZ), not Defra.

Templates:

| File | Recipient | Notes |
|---|---|---|
| `desnz-secretary-of-state.md` | Miatta Fahnbulleh, DESNZ | Post only: Ministerial Correspondence Team, Level 3, 55 Whitehall, London SW1A 2HP. No email address published. |
| `cearn-developer.md` | Cearn Solar Farm Limited | `info@cearnsolarfarm.co.uk`; Freepost CEARN SOLAR FARM. For pre-application concerns. |
| `solar-mp.md` | User's MP | Same postcode lookup as reservoir; different letter body focused on Cearn concerns. |
| `solar-county-councillor.md` | User's OCC councillor | OCC is a statutory consultee as highway authority; letter asks for strong LIR. |
| `solar-district-councillor.md` | User's Vale councillor | Vale motion of 21 Oct 2026 acknowledged; ask Vale to press for field-level land grades, viewpoints, HGV routes, cumulative assessment. |
| `solar-planning-inspectorate.md` | Planning Inspectorate | Relevant Representation template for EN0110044; not yet active (needed after acceptance). |

**Optional combined-impact paragraph:** Each template contains a placeholder `{{combined_impact_para}}`. The letters page offers a checkbox: "Include combined impacts with White Horse Reservoir". When checked, the placeholder is replaced with a standard paragraph covering the A338/A417/A415 corridor and the construction timing overlap. When unchecked, the placeholder is removed.

---

## 11. Update Pipeline (Cearn Sources)

`generator/fetch.py` is extended to monitor cearn sources from `data/cearn/cearn-solar-farm-sources.json`. Sources with confirmed working feeds:

| Source | Method |
|---|---|
| Planning Inspectorate EN0110044 | Page-change detection (no RSS) |
| Cearn developer site (`/feed/` empty) | Page-change detection |
| Protect the Vale | Page-change detection (no feed) |
| Vale news feed | RSS (filter for "Cearn" and "solar") |
| Vale ModernGov RSS | RSS (filter for EN0110044) |
| Charney Bassett PC (news + meetings) | RSS |
| East Hanney PC | RSS (Parish Online pattern) |
| CPRE Oxfordshire | RSS |
| Oxford Magazine Cearn topic | RSS |
| Hansard / written questions | JSON API (add "Cearn", "EN0110044" to keywords) |

Sources with no usable feed or no online presence (Goosey, Baulking, Denchworth, Garford, Lyford, Frilford, Hatford, Besselsleigh) are flagged in the pipeline log as "no automated monitoring -- manual check required."

Cearn news items are stored in `data/cearn/fetched/news_items.json` (separate from the reservoir cache). Each item is tagged `project: cearn` in the JSON. The build reads both caches and passes them to templates as `reservoir_news` and `cearn_news`. The homepage shows both, labelled by project.

---

## 12. Representative Data Conflicts

Three shared representatives appear with different roles in the two datasets:

| Name | In reservoir dataset | In cearn dataset | Resolution |
|---|---|---|---|
| Jenny Hannaby | District (Vale of White Horse) | County (Oxfordshire County Council) | Dual-mandate: TWO records, each tagged `projects: reservoir,cearn`. |
| Lee Evans | County (Oxfordshire County Council) | District (Vale of White Horse) | Dual-mandate: TWO records, same tagging. |
| Ron Batstone | District (Vale of White Horse) | County (Oxfordshire County Council) | Dual-mandate: TWO records, same tagging. |

These are not data errors but genuine dual mandates. The About page notes that some councillors hold seats on both County and District councils, and are listed under both in the representatives lookup.

---

## 13. Cearn Still-to-Check Follow-ups

These 12 items from `data/cearn/cearn-solar-farm-sources.json` (`still_to_check_by_hand`) are added to the plan as tracked tasks alongside the 11 reservoir items:

1. Which parishes are inside the Cearn boundary and cable corridor (boundary overlay task -- **first solar task**).
2. Scoping report contents once published on the PINS documents page (construction period, access routes, traffic, lifespan, battery size, cumulative list).
3. Final wording and vote on the Vale Cearn motion once the 21 Oct 2026 minutes are published.
4. MP positions on Cearn (Olly Glover, Charlie Maynard, Layla Moran): their websites block automated checks.
5. Protect the Vale organisers, social media and any petition as they appear.
6. Original BBC and Herald Series article URLs (only mirrors found).
7. Botley West decision on 10 November 2026 and any effect on the Farmoor substation.
8. Manor Solar Farm construction start.
9. West Hanney, Kingston Bagpuize, Fyfield and Tubney sites for Cearn mentions (blocked or errors during research).
10. Charney Bassett's next meeting date (18 or 11 Nov 2026) and the 9 Sep 2026 minutes contents.
11. East Hanney extraordinary meeting of 24 August 2026: subject.
12. Which DESNZ minister will sign the decision.

---

## 14. Key Dates and Alerts

| Date | Event | Alert needed |
|---|---|---|
| 10 November 2026 | Botley West decision (affects Farmoor substation) | Check PINS EN010147 page; update cearn data |
| 23 November 2026 | Vale scoping response deadline | Update cearn timeline; add Vale response when published |
| December 2026 | Scoping Opinion expected | Monitor EN0110044 documents page daily |
| February to March 2027 | Stage 2 public consultation | Switch cearn actions panel to "Stage 2 open now" |
| September 2027 | DCO application expected | Switch to 28-day acceptance monitoring |
| 1 April 2028 | Ridgeway Council vesting | Update local council records for both projects |

These dates should be embedded in the cearn timeline as forecast entries and checked by the pipeline. When a forecast date passes without the event being confirmed, the pipeline should flag it in the log (not silently drop it).

---

## 15. Builder Calls (Addendum Decisions)

- **`data/reservoir/` + `data/cearn/` subfolder structure**: David's decision (confirmed 1 Nov 2026 session).
- **Existing reservoir page URLs unchanged**: avoids breaking inbound links; reservoir pages gain a project label in the `<h1>`.
- **Dual-role reps kept as two records**: different bodies, different emails; tagged both projects. Merging into one record would require a multi-role schema; two records follow the existing single-role schema.
- **`projects` field as comma-separated string** (not JSON array): consistent with the existing CSV format.
- **Forecast timeline entries**: distinguished by `status: forecast` in JSON, rendered with "(forecast)" label; not guessed at from date alone.
- **Separate news caches per project** (`reservoir/fetched/` and `cearn/fetched/`): prevents reservoir items appearing on solar pages and vice versa.
- **Combined-impact paragraph as an opt-in checkbox**, not a default inclusion: residents may oppose one project and not want the paragraph conflating both.
- **DESNZ letter by post only**: no email address is published; the template gives the postal address and notes the absence of an email.
