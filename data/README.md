# White Horse Reservoir tracker: data sources

Source data for a community app that lets residents affected by the proposed White Horse Reservoir (formerly SESRO, the "Abingdon reservoir") see what is being discussed, follow the latest news, see what their councillors and MPs are saying, and find out how to get involved and who to contact.

The app covers every area affected by the reservoir or its construction access routes. It is not specific to any one village.

Last verified: 1 November 2026.

## Files

- `white-horse-reservoir-sources.json`: the master file. Everything else is generated from it. Edit this file, not the CSVs.
- `local-councils.csv`: one row per parish or town council. Columns: name, type, access points, how affected, website, meetings page, meeting pattern, latest minutes, minutes format, platform, feeds, reservoir mention, contact, Facebook, verification status, notes.
- `representatives.csv`: MPs, county councillors and district councillors for each affected area, with official contact details and any public stance on the reservoir.
- `access-points.csv`: Thames Water's construction access points (September 2026 targeted consultation), with roads, localities, purpose and peak lorry and van movements per hour.
- `national-and-other-sources.csv`: Planning Inspectorate, GOV.UK, Parliament, regulators, Thames Water, campaign groups and media, with feed or API details.
- `research-report.md`: the full original research report with all sources. It opens with a list of points superseded by later verification; where it conflicts with the JSON, the JSON is correct.
- `project-context.md`: background on the project, timeline, construction impacts, the planning process, and the legal rules on what councils must publish.

## JSON structure

Top-level keys:

- `meta`: check date, project name, Planning Inspectorate reference (WA010005), current stage, and the verification key.
- `access_points`, `access_points_sources`, `access_points_notes`: the access point table and where it came from.
- `local_councils`: parish and town councils. Each entry has a `feeds` list of `{url, status}`.
- `representatives`: one entry per person per role. The same person can appear twice if they sit on two councils (for example, a county and a district councillor).
- `principal_councils`: Vale of White Horse, South Oxfordshire and Oxfordshire County Council. Covers their ModernGov sites, RSS, web service status, committee IDs and public speaking rules.
- `national_and_other_sources`: everything above parish level that is not a principal council.
- `local_government_reorganisation`: the move to three unitary councils (vesting day 1 April 2028) and what it means for the app.
- `still_to_check_by_hand`: known gaps.

## Verification status

- **verified**: page or feed fetched and confirmed on the check date.
- **partly verified**: some fields confirmed, others taken from directories, file names or search results.
- **unverified**: could not be fetched (usually because the site blocks automated access). Needs a manual check.

Entries marked "checked by hand" were confirmed in a phone browser on 1 November 2026.

## How to monitor each type of source

- **RSS feeds that work**: poll them. These include Parish Online `/meetings/feed/` and `/news/feed/`, Vale and South Oxfordshire `mgRss.aspx`, council reservoir news categories, GARD, and Cllr Nathan Ley's Substack.
- **JSON APIs**: query by keyword. These include GOV.UK search, Hansard, Parliament written questions, petitions and Find a Tender. Use several terms: "White Horse Reservoir", "SESRO", "Abingdon reservoir".
- **No feed** (Planning Inspectorate, Thames Water, Marcham, West Hanney, Milton, Didcot and others): watch the page for changes, then download any new PDFs or Word files and extract the text.
- **Empty feeds**: some sites have feeds that are valid but always empty. West Hanney's `/meetings/feed/` and `/news/feed/` are comment feeds and do not carry posts. Do not rely on them.
- **Sites that block automated access**: West Hanney, Steventon, and Oxfordshire County Council's ModernGov site blocked the checking tools. Test them from the app's own server using a normal browser user agent before relying on them.

Suggested polling: daily for the Planning Inspectorate project page once the DCO is submitted (expected November 2026), and weekly for everything else.

## Known gaps

See `still_to_check_by_hand` in the JSON. The main gaps are:

- Steventon's minutes page.
- Frilford, which has no website or directory entry.
- Oxfordshire County Council's RSS feed and all three ModernGov web services, none of which could be tested.
- Approximate lorry figures for some access points.
- West Hanney has published no minutes since January 2026.

## Future changes to plan for

- **DCO submission**, expected November 2026. Once the Planning Inspectorate accepts the application, there is a window of at least 30 days to register as an Interested Party. The app should alert on this.
- **Local government reorganisation**: elections to the new councils in May 2027, and the current county and district councils abolished on 1 April 2028. All affected places fall in the new Ridgeway Council. Councillors and ModernGov addresses will change.
- **Thames Water's finances**: restructuring is ongoing and could affect who promotes or delivers the project.

## Regenerating the CSVs and the browsable page

Run `python build.py white-horse-reservoir-sources.json`. It rewrites the four CSVs and `index.html` from the JSON, and stops if it finds an em dash in the data.
