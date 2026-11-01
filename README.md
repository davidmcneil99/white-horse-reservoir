# White Horse Reservoir Campaign Site

A static campaign web app that lets residents near the proposed White Horse Reservoir (formerly SESRO, the "Abingdon reservoir") find out what is happening, look up their representatives by postcode, and send pre-filled letters to officials.

**Live site:** https://davidmcneil99.github.io/white-horse-reservoir/

**Planning Inspectorate reference:** WA010005

## About the reservoir

Thames Water proposes a fully embanked off-river storage reservoir near East Hanney, about 5 km south-west of Abingdon. It would hold approximately 150 billion litres and cover about 6.7 km2. The project requires a Development Consent Order (DCO) from the Secretary of State for Environment, Food and Rural Affairs.

This site is independent of GARD (Group Against Reservoir Development) but shares the same opposition to the scheme.

## Local government reorganisation

Elections to new Oxfordshire unitary councils take place in May 2027. The current county and district councils are abolished on 1 April 2028. All affected places fall in the new Ridgeway Council.

## Development

### Requirements

- Python 3.11+

```bash
pip install -r requirements-dev.txt
```

### Build

```bash
python generator/build.py
```

Renders templates to `docs/`.

### Fetch latest data

```bash
python generator/fetch.py
```

Polls RSS feeds, JSON APIs, and monitored pages. Updates `data/fetched/`.

### Tests

```bash
pytest
```

### Data corrections

Add entries to `data/overrides.json`. Each entry must include `item_type`, `item_id`, `corrected_on`, `corrected_by`, `correction_note`, `field`, and `new_value`. The generator applies them at build time and shows a visible note on corrected items.

## Deployment

GitHub Actions runs `fetch.py` then `build.py` daily at 06:00 UTC and on every push to `main`. The site is served from `docs/` via GitHub Pages.

## Data sources

Research data is in `data/`. The master file is `data/white-horse-reservoir-sources.json`. See `data/README.md` for the full source list and verification statuses.

## Licence

Content: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Code: MIT.
