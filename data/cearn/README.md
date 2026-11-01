# Cearn Solar Farm: data sources

Source data for the solar section of the community web app that also covers the White Horse Reservoir. Cearn Solar Farm is a proposed solar and battery storage scheme (grid connection up to 500MW, about 2,800 acres) around Garford, Charney Bassett, West Hanney, Goosey and Baulking in the Vale of White Horse. Planning Inspectorate reference: EN0110044.

The two projects are separate and should have clearly separate areas of the site. They are linked through cumulative impacts (construction traffic on shared roads, overlapping construction periods, combined land take). Residents may oppose one and not the other.

Last verified: 1 November 2026.

## Files

- `cearn-solar-farm-sources.json`: the master file. Everything else is generated from it. Edit this file, not the CSVs.
- `key-dates.csv`: timeline of past, upcoming and forecast dates, each with a source.
- `nearby-solar-schemes.csv`: Cearn, Manor Solar Farm (30MW, consented on appeal), the existing solar farms on the reservoir site, and Botley West (which shares Cearn's proposed grid substation at Farmoor).
- `local-councils.csv`: parish and town councils and parish meetings for the scheme area and the possible cable corridor, with websites, meeting patterns, feeds, Cearn mentions and contacts.
- `representatives.csv`: decision-maker (DESNZ Secretary of State), the energy minister, MPs, county and district councillors for each affected place, with official contacts and any stated position on Cearn.
- `council-positions.csv`: formal positions (the Vale motion of 21 October 2026, written answers, CPRE).
- `campaign-groups.csv`: Protect the Vale (the group opposing Cearn), GARD (reservoir only), CPRE Oxfordshire, and Stop Botley West as a model campaign.
- `national-and-other-sources.csv`: monitoring sources with feed or API status.
- `how-to-get-involved.csv`: actions by stage, from scoping now to a possible legal challenge after a decision.
- `project-context.md`: background, timeline, process, cumulative impacts and how residents can take part.
- `research-report.md`: the original research report, with a list of points corrected by later verification at the top. Where it conflicts with the JSON, the JSON is correct.
- `build.py`: regenerates the CSVs and `index.html` from the JSON. Run `python build.py cearn-solar-farm-sources.json`. It stops if it finds an em dash.
- `index.html`: browsable, filterable view of the data.

## JSON structure

Top-level keys:

- `meta`: check date, project, applicant, Planning Inspectorate reference, consenting route, current stage, verification key, and a pointer to the reservoir data set.
- `key_dates`: timeline of events.
- `scheme`: capacity, area, components, grid connection, location, affected parishes named by the Vale, land and flood information, what is not yet published, the boundary GeoJSON link, and developer documents.
- `nearby_solar_schemes`: other solar schemes in the area.
- `links_to_reservoir`: how the two projects relate, and guidance for the app.
- `local_councils`, `representatives`, `council_positions`, `campaign_groups`, `national_and_other_sources`, `how_to_get_involved`: as the CSVs above.
- `still_to_check_by_hand`: known gaps.

The field names follow the reservoir data set where they overlap. Some councils and councillors appear in both data sets. Treat each person or council as one record in the app, tagged with the projects that affect them.

## Verification status

- **verified**: page or feed fetched and confirmed on the check date.
- **partly verified**: some fields confirmed, others from directories or search results.
- **unverified**: could not be fetched; needs a manual check.

## How to monitor

- **Most important source**: the Planning Inspectorate project page for EN0110044. It has no RSS, so poll `/documents` and `/project-updates`, and sign up for its email updates. The scoping report and, later, all application documents will appear here.
- **RSS feeds that work**:
  - Charney Bassett PC `/news/feed/` and `/meetings/feed/`
  - East Hanney and Hinton Waldrist (Parish Online pattern)
  - Appleton with Eaton `/feed/`
  - the Vale's main news feed `/feed/`
  - Vale ModernGov `mgRss.aspx`
  - CPRE Oxfordshire
  - the Oxford Magazine Cearn topic feed
- **No usable feed**: the developer's site (its `/feed/` is valid but empty), Protect the Vale, Cumnor, Uffington, Marcham and The Hanneys. Watch these pages for changes.
- **No online presence**: Goosey, Baulking, Denchworth, Garford, Lyford, Frilford, Hatford and Besselsleigh are parish meetings with no website. Residents will have to rely on noticeboards or word of mouth for these.

## Map boundary

The Planning Inspectorate publishes the scheme boundary as GeoJSON at `/projects/EN0110044/download-boundary`. It appears to include the cable corridor to Farmoor. Overlay it on ONS civil parish boundaries to confirm which parishes are inside the scheme. The research tools could not download it, so this is the first task for the app build. The reservoir's boundary is available at the same path for WA010005, so both can be shown on one map.

## Known gaps

See `still_to_check_by_hand` in the JSON. The main gaps are:

- Which parishes are inside the boundary.
- The scoping report contents, which are not published yet.
- The final wording of the Vale motion, which awaits the minutes.
- MP positions.
- Construction details, which the developer has not published.

## Future changes to plan for

- **Scoping**: Vale response due 23 November 2026, then a Scoping Opinion expected December 2026.
- **Stage 2 consultation**, February to March 2027. The cable route will be shown then.
- **DCO submission**, expected September 2027. After the 28-day acceptance decision, a window of at least 30 days opens to register as an Interested Party. The app should alert on this.
- **Local government reorganisation**: Ridgeway Council takes over on 1 April 2028 and will be the host authority during any examination.
- **Botley West decision**, due 10 November 2026. It affects the Farmoor substation that Cearn depends on.
