# White Horse Reservoir Campaign App: Design Document

**Date:** 2026-11-01
**Author:** Design session with David McNeil
**Status:** Approved for implementation

---

## 1. Intent and Why

Thames Water is expected to submit its Development Consent Order (DCO) application for the White Horse Reservoir (formerly SESRO) to the Planning Inspectorate imminently -- the project page (WA010005) says "expected November 2026". Once the application is accepted there is a window of at least 30 days in which residents can register a Relevant Representation and become an Interested Party. Only Interested Parties have full participation rights in the examination. Missing this window cannot be remedied.

The purpose of this app is to make sure every resident affected by the reservoir or its construction routes can find out what is happening, contact the right people, and take the right action at the right time -- without needing to navigate the Planning Inspectorate, find their councillors, or draft letters from scratch.

The site supports GARD (Group Against Reservoir Development) but presents itself as an independent community resource, not GARD's official site.

---

## 2. Goals

- Give any resident the path from "I heard about this reservoir" to "I have registered as an Interested Party" in under five minutes.
- Provide a location lookup (postcode or map click) that returns the resident's parish, district councillor(s), county councillor, MP, and nearest construction access points.
- Pre-fill letter templates to each representative and body, ready to copy or open in a mail client.
- Show what officials and politicians have publicly said, accurately quoted with dated source links.
- Display a timeline of the project from 2006 to date.
- Keep content current automatically via a daily GitHub Actions pipeline with zero running cost.
- Provide a public corrections mechanism so factual errors can be fixed transparently.
- Work fully without AI summarisation, paid APIs, or email infrastructure.

---

## 3. Non-goals (v1)

- Email alerts when the DCO is accepted (design for it, do not build it yet).
- Interactive map with geocoded access point markers (access points table only in v1).
- Council meeting notes section with PDF extraction.
- AI summarisation of minutes or news.
- Visitor analytics or tracking.
- The site is not GARD's official site and makes no claim to be.

---

## 4. Anti-goals

- Do not reproduce full article text from news sources (headline, date, short summary and link only).
- Do not make legal claims or give legal advice -- present as general information only.
- Do not use any service requiring a paid key or account.
- Do not build infrastructure on Smartling or any work account; personal GitHub account only (davidmcneil99).
- Do not rely on Thames Water's community polling (commissioned, not independent) to characterise public opinion.

---

## 5. Constraints

- Hosted free on GitHub Pages from a public repo at github.com/davidmcneil99/white-horse-reservoir.
- Zero running cost unless a GitHub secret (OpenAI key or similar) is voluntarily provided for AI features.
- Mobile-first, WCAG 2.2 AA target.
- UK English. No em dashes. No emojis in site copy.
- Respect robots.txt; fetch politely (single requests, reasonable delays, normal user-agent).
- Representative data lives in JSON/CSV files, not in code, for easy replacement at the May 2027 elections and the April 2028 Ridgeway Council vesting day.
- Access points currently have road and locality descriptions but no coordinates. v1 uses a static table; coordinates are a v2 task.
- The DCO submission is the most critical monitoring target once it happens (switch to daily polling of the Planning Inspectorate project page).
- Local government reorganisation: elections May 2027, new council (Ridgeway) vests 1 April 2028. All affected places fall in Ridgeway Council.

---

## 6. Architecture

### 6.1 Overview

```
E:\white-horse-reservoir\
  data/                   Source data (copied from E:\reservoir, then extended)
    white-horse-reservoir-sources.json   Master dataset (do not edit directly)
    representatives.csv
    local-councils.csv
    access-points.csv
    national-and-other-sources.csv
    overrides.json          Corrections (edit this to correct items)
    content/
      timeline.json         Timeline entries (seeded from research-report.md)
      quotes.json           What officials have said (sourced, dated)
      actions.json          "What you can do" entries with timing and sources
      letters/              Letter templates (one .md file per letter type)
    fetched/                Cache written by the update pipeline (not committed)
  templates/              Jinja2 HTML templates
  generator/
    build.py               Main generator (extends existing build.py logic)
    fetch.py               Feed fetcher and page-change monitor
    apply_overrides.py     Applies overrides.json to content before rendering
  docs/                   Generated site output (GitHub Pages root)
    index.html
    about.html
    facts.html
    letters.html
    actions.html
    corrections.html
    access-points.html
    assets/
      style.css
      map.js
      lookup.js
  .github/
    workflows/
      update.yml           Daily update and deploy workflow
  requirements.txt
  README.md
```

### 6.2 Generator

Python 3.11, standard library plus:
- `jinja2` for HTML templates
- `feedparser` for RSS
- `requests` for HTTP fetches
- `pdfplumber` (v2, off by default: for meeting notes PDF extraction)

The generator is invoked as `python generator/build.py`. It:
1. Reads all `data/*.json` and `data/*.csv` files.
2. Applies `data/overrides.json` to produce a corrected dataset.
3. Reads `data/fetched/*.json` (written by `fetch.py`) for new items from feeds.
4. Renders all pages from `templates/` to `docs/`.

The updater `generator/fetch.py`:
1. Fetches all sources listed in `data/white-horse-reservoir-sources.json`.
2. For sources with RSS/JSON APIs: parses and deduplicates against a local cache.
3. For sources without feeds: compares a hash of the current page against the stored hash; if different, records the change.
4. Writes results to `data/fetched/`.
5. Exits cleanly if a source is unreachable (logs a warning; does not fail the build).

### 6.3 GitHub Actions

`.github/workflows/update.yml` runs on:
- A daily schedule (06:00 UTC).
- Manual `workflow_dispatch` trigger (for testing and urgent updates).
- Push to `main` (for committed data changes).

Steps:
1. Check out repository.
2. Set up Python 3.11.
3. Install dependencies.
4. Run `python generator/fetch.py`.
5. Run `python generator/build.py`.
6. Commit any changed files in `data/fetched/` (cache) back to the repo.
7. Deploy `docs/` to GitHub Pages via the `actions/deploy-pages` action.

AI summarisation (v2): if the secret `OPENAI_API_KEY` is present, `fetch.py` passes new items through a summarisation function and stores the result with a `ai_generated: true` flag. The generator then labels those items on the page.

### 6.4 GitHub Pages

- Source: the `docs/` folder on the `main` branch.
- Custom domain: not in v1 (use the github.io subdomain).
- The `docs/` folder is regenerated on every push and every scheduled run.

---

## 7. Data Model

### 7.1 Source data (copied from E:\reservoir, do not modify)

- `white-horse-reservoir-sources.json`: authoritative. 26 parish/town councils, 34 representatives, 20 access points, 3 principal councils, 17 national/other sources, local government reorganisation metadata, 11 still-to-check items.
- `representatives.csv`, `local-councils.csv`, `access-points.csv`, `national-and-other-sources.csv`: flat exports; rebuilt by `build.py`. Edit the JSON, not the CSVs.

### 7.2 Content data (maintained by the project)

**`data/content/timeline.json`** -- seeded from `research-report.md` section 1.3:
```json
[
  {
    "id": "t001",
    "date": "2006",
    "date_precision": "year",
    "event": "Thames Water proposes an Upper Thames reservoir near Abingdon",
    "source_url": "https://...",
    "source_label": "BBC",
    "last_checked": "2026-11-01"
  }
]
```

**`data/content/quotes.json`** -- what officials/bodies have said:
```json
[
  {
    "id": "q001",
    "speaker": "Oxfordshire County Council",
    "role": "Highway authority and statutory consultee",
    "date": "2026-01-13",
    "quote": "Oxfordshire County Council cannot support the application in its current form due to the significant environmental impacts",
    "source_url": "https://www.ofwat.gov.uk/...",
    "source_label": "OCC statutory consultation response, published by Ofwat",
    "last_checked": "2026-11-01"
  }
]
```

**`data/content/actions.json`** -- "what you can do" entries (see section 11):
```json
[
  {
    "id": "ac001",
    "title": "Register for Planning Inspectorate updates",
    "timing": "Now",
    "dco_stage": "pre-submission",
    "who_can": "Anyone",
    "how": "...",
    "source_url": "...",
    "source_label": "Planning Inspectorate"
  }
]
```

**`data/content/letters/`** -- one Markdown file per letter type:
- `mp.md`
- `county-councillor.md`
- `district-councillor.md`
- `parish-clerk.md`
- `thames-water.md`
- `planning-inspectorate-relevant-representation.md`
- `ofwat.md`
- `defra-secretary-of-state.md`
- `foi-missing-minutes.md`
- `eir-thames-water.md`

Each template uses placeholders: `{{recipient_name}}`, `{{recipient_address}}`, `{{sender_area}}`, `{{mp_name}}` etc. The generator renders them with real data from the location lookup. Letters are rendered client-side in JavaScript using the postcodes.io lookup result.

### 7.3 Corrections (`data/overrides.json`)

```json
[
  {
    "item_type": "quote",
    "item_id": "q001",
    "corrected_on": "2026-11-15",
    "corrected_by": "David McNeil",
    "correction_note": "Source URL updated after council website redesign",
    "original_value": "https://old-url",
    "new_value": "https://new-url"
  }
]
```

The generator applies these at build time. Each corrected item gets a visible note on the page: "Corrected on [date]: [correction_note]". All corrections also appear on `corrections.html`.

### 7.4 Fetched data (`data/fetched/`)

Written by `fetch.py`, not committed to the repo (in `.gitignore`). The exception is a `page_hashes.json` file tracking page-change detection, which is committed so the action can detect changes across runs.

Wait -- `data/fetched/` needs to be committed to persist the cache between Action runs. It will be committed by the Action itself after each run. Individual fetched items should be small (headlines, dates, URLs) so the repo size stays manageable.

---

## 8. Pages

### 8.1 Homepage (`index.html`)

Top section: large call to action. "The DCO application has not yet been submitted" (updated automatically when submission is detected). Once submitted: countdown-style note on the registration window.

Below: postcode lookup widget. Resident types their postcode; the page calls postcodes.io; the result shows their area summary (parish, district, county, MP) with links to the relevant letters.

Below: latest news items from the feed pipeline (headline, date, source link). Max 10 items, newest first.

Below: links to Facts, Actions, Letters, About.

### 8.2 Facts page (`facts.html`)

- What the reservoir is (summary table from project-context.md).
- Timeline (from `timeline.json`), in reverse-chronological order, each item with source and last-checked date.
- Positions section: what each body has said (from `quotes.json`), grouped by tier (national government, regulators, county, district, campaign). Short quotes with source links. Campaign framing absent here -- straight record.

### 8.3 Actions page (`actions.html`)

"What you can do", grouped by timing (do this now / when the DCO is submitted / during examination / ongoing). Each action shows: who can do it, when, how, and a source link.

Sources for the actions content -- from research and the project brief:
- **Registering as an Interested Party:** Planning Inspectorate guidance at national-infrastructure-consenting.planninginspectorate.gov.uk; GARD DCO explainer at groupagainstreservoirdevelopment.org/dco-planning-process/
- **Speaking at council meetings:** public participation rules in `white-horse-reservoir-sources.json` (Vale/SODC: email democratic.services@southandvale.gov.uk; OCC: form at service.oxfordshire.gov.uk/addressameeting)
- **Lobbying for strong Local Impact Reports:** Planning Inspectorate guidance on LIRs; previous NSIP campaign guidance (HS2, Sizewell C)
- **Petitions:** petition.parliament.uk (100 signatures = response from government, 10,000 = consideration for debate, 100,000 = considered for debate); GARD/38 Degrees petition already running
- **FOI/EIR requests:** ICO model publication scheme; EIR 2004; FOI 2000; the distinction that Thames Water is covered by EIR but not FOI (it is a regulated utility, treated as a public authority for environmental information)
- **Statutory blight:** Town and Country Planning Act 1990 Part VI; blight notices can be served once land is identified in a DCO application; residents should seek a RICS-qualified surveyor
- **Compensation Code:** general statutory framework; project-specific scheme not found
- **Judicial review:** public law remedy available on process grounds (Gunning principles); Oxfordshire County Council's targeted consultation objection is relevant; JR is expensive and time-limited (3 months from the decision); present as outline only
- **Crowdfunding GARD's legal challenge:** GARD crowdfunder launched October 2026; reached £5k in first week
- **Parish surveys:** the eight-parish survey launched October 2026 as a model
- **Community liaison group:** Thames Water's Code of Construction Practice process; residents can ask for a CoCP to mandate a community group

Every action links to a source. Presentation: general information, not legal advice (stated explicitly).

### 8.4 Letters page (`letters.html`)

Two-step widget: (1) enter postcode or select area from a dropdown; (2) choose letter type from a list. The letter appears pre-filled with the correct recipient name, address, and area details. Buttons: "Copy to clipboard" and "Open in email app" (opens a `mailto:` link with subject and body pre-filled).

All rendering is client-side JavaScript. No server. The representative data is a small JSON file embedded in the page or fetched as a static file.

The FOI/EIR templates explain the legal basis and the council's publication obligations, based on project-context.md section "What councils must publish".

### 8.5 About page (`about.html`)

- Who runs the site (David McNeil, community volunteer).
- Independence statement: independent of GARD; supports GARD's campaign; not GARD's official site.
- Sources and methodology: where data comes from, how often it is updated, what "verified" means.
- How to report a correction: email address or GitHub issue link.
- Corrections are public: link to corrections.html.
- GARD's official site and contact (clearly labelled as separate).

### 8.6 Corrections page (`corrections.html`)

Generated from `data/overrides.json`. Table of all corrections in reverse-chronological order: date, item corrected, what changed. Empty state: "No corrections have been made."

### 8.7 Access points page (`access-points.html`)

Table of all 20 access points from the JSON: ID, roads, localities, purpose, status (permanent/temporary), peak HGV/LGV per hour, figure confidence. Notes on approximate figures. Link to Thames Water's map book PDF as the source.

---

## 9. Location Lookup

### 9.1 postcodes.io

Free, no API key. Endpoint: `https://api.postcodes.io/postcodes/{postcode}`. Returns:
- `parliamentary_constituency` (maps to MP)
- `admin_ward` (maps to district councillor via ward name matching)
- `county_electoral_division` (maps to county councillor)
- `parish` (used for parish council lookup)
- `latitude`, `longitude` (for distance to access points in v2)

### 9.2 Matching logic

The generator produces a small static JSON file (`docs/assets/lookup-data.json`) containing:
- All representatives with their area/ward/division as listed in `representatives.csv`.
- All parish councils with their parish name.
- All access points (name, locality strings).

The client-side `lookup.js` script does fuzzy matching between postcodes.io field values and the lookup data. Known mismatches (e.g. the postcodes.io ward name may not exactly match the ModernGov ward name) are handled by a `data/content/ward-aliases.json` mapping file.

### 9.3 Mapping (v1)

The homepage has a simple Leaflet map showing the reservoir footprint area and the 20 access points as markers. The footprint is derived from the order limit description in the research (approximate polygon; not the exact GeoJSON, which requires the Planning Inspectorate boundary download). Access point markers are positioned at approximate road/locality intersections using manually entered coordinates -- a v1 limitation noted in the UI.

Accurate coordinates for access points: the Thames Water map book PDF (URL in the JSON) shows each access point on a map. These can be georeferenced manually or extracted via PDF coordinate analysis. This is listed as a tracked follow-up (see section 12).

Map tiles: OpenStreetMap via Leaflet (no key needed).

---

## 10. Update Pipeline Detail

### 10.1 Sources monitored

| Source | Method | Frequency |
|---|---|---|
| Planning Inspectorate WA010005 | Page change detection (HTML hash of /projects/WA010005 and /documents) | Daily |
| Vale of White Horse ModernGov RSS | RSS feed | Daily |
| South Oxfordshire ModernGov RSS | RSS feed | Daily |
| Hansard API | JSON API (keyword: "White Horse Reservoir", "SESRO", "Abingdon reservoir") | Daily |
| Parliament written questions API | JSON API (same keywords) | Daily |
| GOV.UK search API | JSON API (same keywords) | Daily |
| GARD feed | RSS | Daily |
| Cllr Nathan Ley Substack | RSS | Daily |
| Thames Water project site | Page change detection | Daily |
| Thames Water document library | Page change detection | Daily |
| Sutton Courtenay PC | RSS | Daily |
| Drayton PC | RSS | Daily |
| East Hanney PC | RSS | Daily |
| Culham PC | RSS | Daily |
| Steventon PC | RSS (main /feed/) | Daily |
| West Hanney PC | Page change detection (feeds are empty) | Daily |
| Marcham PC | Page change detection (no feed) | Daily |
| Harwell PC | RSS (to be tested from server) | Daily |
| OCC ModernGov RSS | RSS (to be tested from server -- was blocked) | Daily |
| Oxford Mail | Not automated in v1 (blocked); track manually | Manual |
| BBC Oxford feed | RSS (to be tested from server) | Daily |
| Abingdon Blog | Page change detection (feed gave error) | Daily |

### 10.2 Robots.txt compliance

`fetch.py` checks `robots.txt` for each domain on first run and caches the result. Sources confirmed to block automated access in the research data (West Hanney, Steventon, OCC ModernGov) are fetched with a standard browser user-agent (not a bot string); if they still return 403 or robots.txt blocks crawling, they are skipped and logged, and the pipeline continues.

### 10.3 Page change detection

For sources without feeds, `fetch.py` stores a SHA-256 hash of the page content. On each run it refetches and compares. A change triggers manual review (logged in `data/fetched/changes.json`). In v1, changed pages are flagged for human review rather than automatically extracted. This is noted in the site's "last checked" dates.

### 10.4 News item deduplication

Each news item is keyed by URL. Items already in `data/fetched/news_items.json` are not added again. The store is a JSON array with a maximum of 500 items (oldest dropped first).

---

## 11. "What You Can Do": Research Findings

All actions are general information, not legal advice. Sources are listed inline.

### Before DCO submission (now)

| Action | Who | Source |
|---|---|---|
| Sign up for Planning Inspectorate email updates on WA010005 | Anyone | national-infrastructure-consenting.planninginspectorate.gov.uk/projects/WA010005/get-updates/start |
| Write to your MP and councillors | Residents | Representatives in JSON; contact details verified 1 Nov 2026 |
| Attend a parish council meeting and speak in the public participation slot | Residents of any parish | Local Government Act 1972; each council's standing orders set the slot |
| Ask your parish council to pass a resolution and contribute to its Local Impact Report | Residents | Planning Act 2008 s.60; examiner gives significant weight to LIRs from principal councils |
| Sign the GARD/38 Degrees petition | Anyone | you.38degrees.org.uk/petitions/stop-thames-water-s-plans-for-a-devastating-mega-reservoir |
| Support GARD's crowdfunder for DCO expertise | Anyone | groupagainstreservoirdevelopment.org |
| Ask your parish council for a parish survey (the eight-parish model of Oct 2026) | Residents | East Hanney, Drayton, Steventon, Marcham, Culham, Sutton Courtenay, Appleford, Harwell survey, Oct 2026 |
| Submit an FOI request for missing minutes | Anyone | Freedom of Information Act 2000; ICO model publication scheme |
| Submit an EIR request to Thames Water | Anyone | Environmental Information Regulations 2004; Thames Water is a regulated utility covered by EIR |
| Register for Thames Water's project newsletter | Anyone | thames-sro.co.uk/contact-us/#subscribe |

### When the DCO application is submitted and accepted (within 28 days of submission)

| Action | Who | Source |
|---|---|---|
| Register a Relevant Representation (the most important action) | Anyone -- at least 30-day window | Planning Inspectorate; Planning Act 2008 s.56 |
| Speak at open floor hearings (as an Interested Party) | Interested Parties only | Planning Act 2008 s.93; Planning Inspectorate guidance |
| Submit written representations at examination deadlines | Interested Parties only | Planning Act 2008 |
| Ask a principal council to commission a strong Local Impact Report | Residents and councillors | Planning Inspectorate guidance on LIRs |
| Contact your MP to press the Secretary of State | Residents | Secretary of State is the decision-maker (Planning Act 2008 s.114) |
| Start a UK Parliament petition (100,000 signatures triggers consideration for debate) | UK residents | petition.parliament.uk; Parliament website on thresholds |

### Ongoing

| Action | Who | Source |
|---|---|---|
| Attend and speak at district and county council meetings | Residents | Public speaking rules in JSON (democratic.services@southandvale.gov.uk; OCC form 3 working days before) |
| Contact local media | Residents | Oxford Mail, BBC Oxford, Abingdon Blog |
| Ask Thames Water to secure a community liaison group in the Code of Construction Practice | Residents, parish councils | CoCP is a DCO requirement; NSIP precedent from Hinkley Point C, HS2 |
| Check your statutory blight rights if your land is in the Order limits | Landowners | Town and Country Planning Act 1990 Part VI; Compensation Code; RICS-qualified surveyor advised |
| Monitor the DCO examination timetable (as an Interested Party) | Interested Parties | Planning Inspectorate; Planning Act 2008 |
| Judicial review of procedural failures | Any person with standing | Public law; 3-month time limit from decision; Oxfordshire County Council raised Gunning principles concerns about the targeted consultation -- source: GARD 12 Oct 2026 (council's own document not found) |

**Cross-references used:**
- Planning Act 2008 (DCO regime)
- Planning Inspectorate: Advice Note 8.3 (Relevant Representations); Advice Note 8.4 (LIRs); Advice Note 16.1 (how to participate)
- GARD DCO process explainer: groupagainstreservoirdevelopment.org/dco-planning-process/
- project-context.md section "How residents can take part in the DCO"
- research-report.md Part 6
- Other NSIP campaigns: Sizewell C (community liaison group model); HS2 (JR precedent)

---

## 12. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| DCO submitted before v1 ships | High -- expected November 2026 | The sign-up link for Planning Inspectorate updates works now; even a minimal one-page site with that link has value. Ship the smallest thing that helps first. |
| postcodes.io returns a ward name that does not match the representative data | Medium | `ward-aliases.json` mapping file; show raw postcodes.io output as fallback |
| Council website blocks automated fetching | High for OCC, West Hanney, Steventon | Pipeline exits cleanly; source is flagged as "not checked automatically"; site shows last-known date |
| Representatives change (elections, resignation) | High -- elections May 2027 | Data in JSON/CSV, not code; update file, rebuild |
| Local government reorganisation (1 Apr 2028) | Certain | Plan for new ModernGov hosts and councillors from May 2027; Ridgeway Council takes over |
| Thames Water restructuring delays or reshapes the project | Medium | Covered in facts page; pipeline monitors Thames Water news |
| Access point coordinates are inaccurate | Certain for v1 | Map shows approximate positions with a disclaimer; coordinates noted as "approximate, from road/locality description" |
| GARD has not formally agreed to be cited | Unknown | About page makes independence clear; site is not presented as GARD's official resource; David to confirm with GARD |

---

## 13. V1 vs Later

### V1 (target: ship within one week)

- Homepage with "what to do now", postcode lookup, and latest news items
- Facts page: project summary, timeline, positions/quotes
- Actions page: full "what you can do" content
- Letters page: 10 pre-filled letter templates, client-side rendering
- About page: independence statement, corrections process
- Corrections page: generated from overrides.json
- Access points page: static table
- GitHub Actions pipeline for 6+ sources
- Corrections mechanism

### V2

- Interactive map with geocoded access point markers (manually sourced from Thames Water map book)
- Council meeting notes: PDF text extraction, per-council meeting history
- Representatives quotes page: what each named person has said, in full
- Improved postcode matching with ward-aliases.json fully populated

### V3 / Later

- AI summarisation of minutes (off by default, GitHub secret)
- Email alerts for DCO acceptance and examination milestones
- WCAG 2.2 AA audit and fix pass
- Custom domain

---

## 14. Still-to-Check Follow-ups (from JSON `still_to_check_by_hand`)

These appear as tracked tasks in the implementation plan, not silently dropped:

1. Steventon minutes page: URL, latest minutes date and format
2. Frilford: whether any parish meeting exists and how to contact it
3. Oxfordshire County Council ModernGov (mycouncil.oxfordshire.gov.uk): retry; blocked on 1 Nov 2026
4. West Hanney clerk email: not shown on pages checked
5. Oxfordshire County Council RSS and all three ModernGov web services: test from app server
6. Map book HGV figures for A4, A9, A12, A15, A16, A17 (currently "approximate")
7. Which parishes the reservoir footprint itself covers (not stated in access documents)
8. Exact Vale ward for Marcham Road and Drayton Road stretches in Abingdon (Caldecott confirmed; Fitzharris and Dunmore possible)
9. Oxfordshire County Council leader: verify current member page
10. Feeds that failed here but may work from a normal server: Abingdon Town Council, Wantage Town Council, Ofwat, Abingdon Blog, BBC, Oxford Mail, Google News
11. Access point coordinates: georeference from Thames Water map book PDF or manually from road/locality descriptions

---

## 15. Additional GARD Source Material (from physical leaflets, 1 Nov 2026)

Physical leaflets from GARD provide the following confirmed details:

- **GARD crowdfunder:** https://www.crowdfunder.co.uk/p/better-water-future (funds DCO legal scrutiny)
- **8-council parish survey:** https://ee-eu.kobotoolbox.org/x/fXVdDnek (East Hanney, Drayton, Steventon, Marcham, Culham, Sutton Courtenay, Appleford, Harwell)
- **Petition signatures:** 8,000+ as at summer/autumn 2026
- **Secretary of State (current holder Nov 2026):** Emma Reynolds MP (High Wycombe), emma.reynolds.mp@parliament.uk, House of Commons, London SW1A 0AA. The letter template must use this name and be easy to update when the minister changes. Note: an earlier GARD leaflet shows angela.eagle.mp@parliament.uk, confirming the holder has already changed once; design for easy substitution.
- **Relevant Representation window (GARD estimate):** probably January/February 2027 -- consistent with 28-day acceptance decision plus 2-3 months pre-examination.
- **Key campaign concerns to include in actions/facts content (from GARD leaflets, presented as GARD's stated position, not as verified facts):**
  - 1 metre groundwater rise described as "very probable", causing increased flood risk in Steventon and East Hanney; Thames Water says it "will be mitigated" but designs are said to be unfinished
  - Emergency drawdown design "has not been completed" and no public consultation on it
  - Air pollution and noise affecting school children's journeys and health
  - "Land-grab expansion" framing: solar farm and biodiversity replacement land on farmland in Garford
  - A34 Marcham Interchange most affected; plan for a "Reservoir junction" off A34 between Drayton and Abingdon
  - Cost tripled "without any explanation" from Thames Water

These must be presented on the site as GARD's stated positions with attribution, not as independently verified facts, with a link to GARD as the source.

- **Map from GARD leaflet:** Shows the approximate reservoir footprint (red outline = Thames Water land reservation), surrounding villages, inlet/outlet near Culham, rail sidings south of East Hanney, new solar farm area in Garford, and biodiversity compensation areas. Use as a visual reference for the approximate polygon in v1. Sources credited as OpenStreetMap and Thames Water (thames-sro.co.uk/public-consultations/sesro-statutory-consultation-2025-document-library/).

---

## 16. Builder Calls (Decisions Made Without David's Input)

- **Python 3.11 + Jinja2:** same language as existing build.py; no new toolchain required.
- **Leaflet + OpenStreetMap:** standard, well-documented, no key. Tiles from tile.openstreetmap.org.
- **postcodes.io client-side:** avoids a proxy server; the API is free and stable.
- **`data/fetched/` committed to repo:** needed to persist cache between GitHub Actions runs. Kept small (headlines, dates, URLs only).
- **No custom domain in v1:** saves DNS setup time; can be added later.
- **`docs/` as GitHub Pages root:** standard pattern for project sites; avoids a separate `gh-pages` branch.
- **No visitor analytics in v1:** no Plausible/Fathom setup needed; can be added.
- **AI summarisation off by default:** activated only if `OPENAI_API_KEY` secret is set. Site works fully without it.
- **`ward-aliases.json` for postcode matching:** handles the known mismatch between postcodes.io ward names and ModernGov ward names without hardcoding.
- **Letter templates in Markdown with `{{placeholder}}` syntax:** simple, editable, renderable in any context.
- **`mailto:` links for letter submission:** no server, no tracking, works on mobile.
