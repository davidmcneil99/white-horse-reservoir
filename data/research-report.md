# White Horse Reservoir (formerly SESRO / "Abingdon reservoir"): Project Status, Construction Access Impacts, and a Monitoring Map of Every Relevant Body (as at 1 November 2026)

## Read this first: corrections from later verification

This is the original research report from 1 November 2026. The same day, a verification pass and hand checks were run, and the results are in `white-horse-reservoir-sources.json`. Where the two differ, the JSON is correct. Known differences:

- **Access points:** the full A1 to A20 table is now in the JSON, taken from the map book. Peak HGVs per hour from the map book are A1 51, A13 4, A14 14 and A16 3. That differs from the councillor estimates quoted below (60, 5, 4 and 12). A3 has been merged into A2, A18 and A19 have been dropped, and A20 has been added.
- **Parishes added:** Goosey (A17), Fyfield and Tubney (A8), Kingston Bagpuize with Southmoor (A8), St Helen Without (A13, A14), Ardington and Lockinge (A9, A12) and Appleford.
- **MPs:** Culham is in Didcot and Wantage, not Oxford West and Abingdon. Marcham and Shippon are in Oxford West and Abingdon. Garford, Frilford, Lyford and Kingston Bagpuize are in Witney.
- **Vale councillors:** no "Water Champion" role was found for Cllr Andy Cooke. The whitehorsedc.moderngov.co.uk alias does not work; use democratic.whitehorsedc.gov.uk.
- **Garford** is a parish meeting. Frilford has no website or directory entry.
- **Parish URLs and meeting patterns** marked "to verify" below are now verified in the JSON.
- **Local government reorganisation:** in July 2026 the government chose three unitary councils. The affected area moves to Ridgeway Council on 1 April 2028.
- **Feeds:** the verified status of each feed is in the JSON. Several "RSS likely" entries below turned out to be empty, broken or blocked.

---

Thames Water expects to submit its Development Consent Order (DCO) application for the 150 billion litre White Horse Reservoir to the Planning Inspectorate in November 2026. As of 1 November 2026 it had not been submitted. The biggest recent change is that construction access points have nearly tripled, from 6 to 17. For residents, the most important moment comes after the application is accepted: registering a Relevant Representation in that window is the only way to get full participation rights in the examination.

## TL;DR

- **Where the project stands:** Thames Water renamed SESRO "White Horse Reservoir" in January 2026. It passed RAPID gate three in May 2026. Its cost estimate has risen from £2.2bn to £5.5bn to £7.5bn. Planning Inspectorate project page WA010005 says the DCO application is "expected to be submitted November 2026". After submission there are about 28 days for the acceptance decision, roughly 3 months of pre-examination, up to 6 months of examination, and 3 months each for the recommendation and the Secretary of State's decision. A decision is therefore unlikely before late 2027 or 2028.
- **The live local issue is construction access.** A targeted consultation from 9 September to 7 October 2026 raised access points from 6 to 17, and Thames Water admits construction traffic will be "higher than previously forecast". The main A415 Marcham Road entrance would carry about 60% of construction traffic. Secondary routes would bring HGVs along:
  - the A338 (Frilford, the Hanneys, Grove, Charlton);
  - the A4130 and A417 (Milton, Rowstock, the Hendreds);
  - the B4017 (Steventon, Drayton, Caldecott in Abingdon);
  - the A34 Marcham and Milton interchanges.

  According to GARD's post of 12 October 2026, Oxfordshire County Council's submission said the targeted consultation "fails to meet three of the four Gunning Principles" and called for the DCO submission to be delayed. The council's original document was not found.
- **For the app,** build around five high-value machine-readable feeds:
  - the Planning Inspectorate project page, document library and email updates (WA010005);
  - the ModernGov systems of Oxfordshire County Council, Vale of White Horse and South Oxfordshire;
  - the Parliament APIs (Hansard, written questions) and TheyWorkForYou;
  - GOV.UK and Ofwat (RAPID) publications;
  - Thames Water's project site and news pages.

  Parish councils are the weakest link. Most run WordPress sites with PDF minutes published irregularly, so they need page-change monitoring and PDF text extraction rather than APIs.

## Key Findings

1. **The project is not yet consented, or even applied for.** The Planning Inspectorate page shows it at "pre-application", with the application "expected to be submitted November 2026". The Secretary of State issued a section 35 direction letter on 19 March 2026.
2. **Thames Water's own documents give inconsistent timelines, so treat start dates with caution.**
   - Its project page says main construction would begin in 2029, with operation in 2040.
   - The October 2025 Preliminary Environmental Information (PEI) Report gives a different sequence:
     - early works from 2027;
     - DCO granted in 2028;
     - enabling works lasting about seven years;
     - main works from 2032 to 2043;
     - filling from 2039 to 2041;
     - water available from 2040.
   - Oxford Mail/BBC coverage in October 2026 also said "major construction work would begin in 2032".
3. **Construction would last more than a decade** across draft Order limits of about 3,719 ha (37 km²). It would involve demolishing:
   - 20 homes and 9 farm complexes;
   - three solar farms;
   - Steventon Depot;
   - Landmead airstrip;
   - the existing Steventon to East Hanney road.
4. **Access points rose from 6 to 17 in September 2026.** This is the recently announced change. It widens the affected area beyond the core villages to Abingdon (Marcham Road, Drayton Road, Shippon/Dalton Barracks, the Tesco/Marcham Interchange area), Marcham, Drayton and the A338 corridor.
5. **Local political opposition is near-unanimous.** Opponents include:
   - Vale of White Horse District Council;
   - South Oxfordshire District Council (on emergency discharge);
   - Oxfordshire County Council;
   - Abingdon Town Council;
   - the three Liberal Democrat MPs (Olly Glover, Layla Moran, Charlie Maynard);
   - GARD.

   Supporters include Thames Water and its partners, and the national government. Chancellor Rachel Reeves backed the reservoir in a speech on 29 January 2025 as one of "nine new reservoirs [...] to improve our water infrastructure and provide a foundation for growth", alongside £7.9bn of agreed water resources investment. The White Horse Reservoir Growth Coalition also supports it. It was launched at a parliamentary event on 15 September 2026, and its founding members are BusinessLDN and Thames Valley Chamber of Commerce. Eleven members, including Arup, Pinsent Masons, Water UK, Britain ReMade and Peabody, wrote to the Prime Minister asking for Critical National Priority status.
6. **Thames Water's solvency remains unresolved.**
   - On 15 October 2026 it asked creditors to raise its emergency facility by £2.4bn to £5.4bn. Reuters reported it "had already drawn £2.65 billion of its existing £3 billion lifeline", and that the increase would keep it running "into autumn 2027". The creditor vote was set for 29 October.
   - On 16 October it signed a Class B creditor support agreement.
   - Special administration remains a government fallback.
   - Thames Water argues the reservoir is ring-fenced, because a separately licensed Infrastructure Provider would deliver it under the Specified Infrastructure Project Regulations (SIPR).

---

## Part 1: The Project

### 1.1 What it is

| Attribute | Detail |
|---|---|
| Current name | White Horse Reservoir (renamed January 2026; previously South East Strategic Reservoir Option, SESRO; widely called "Abingdon reservoir") |
| Promoter | Thames Water Utilities Ltd, in partnership with Affinity Water and Southern Water |
| Type | Off-line, fully bunded (embanked), non-impounding raw water storage reservoir |
| Usable capacity | 150 million m³ (150 billion litres), plus about 9 Mm³ held below operational levels |
| Drought yield | Up to 271 Ml/d |
| Surface area | About 6.7 km² ("almost as big as Gatwick Airport", Vale of White Horse District Council) |
| Embankment | Crest about 81.5 mAOD; 14.9m to 26.8m above existing ground (average about 21m); base about 400m wide; crest track about 10.4 km |
| Draft Order limits | About 3,719 ha (37 km²), mainly in Vale of White Horse; the far eastern extent (east bank of the Thames near Culham) is in South Oxfordshire |
| Core site | Bounded by the River Ock (north), the A34 and Steventon (east), the Great Western Main Line (south), and the A338 and East Hanney (west); about 5 km south-west of Abingdon |
| Customers served | About 15 million across Thames Water, Affinity Water and Southern Water areas |
| Capital cost | £5.5bn to £7.5bn (gate three submission), up from £2.2bn (2021-22 prices). The main works contract tender is valued at £5.7bn. The £6.6bn figure appears in The Water Report's coverage of the Growth Coalition and in GARD's 38 Degrees/CPRE petition. GARD now cites £9.0bn, a campaign figure that is not verified |
| Planning Inspectorate reference | WA010005 |

**How it works.** In winter high flows, water would be pumped from the River Thames near Culham through a 3.5 km river tunnel and a pumping station, with inflow capped at 1,000 Ml/d. In drought, water would flow back to the Thames under gravity. Thames Water's Lower Thames intakes and Affinity Water (via the Thames to Affinity Transfer) would then re-abstract it downstream.

Water would also go directly to:
- **Southern Water, South East Water (Basingstoke) and Thames Water (Newbury)**, via a new Thames to Southern Transfer (T2ST) water treatment works on site (up to 120 Ml/d). The works would be consented within the reservoir DCO. The 80 to 85 km onward pipeline to Hampshire needs a separate Southern Water DCO.
- **Farmoor reservoir**, via the Farmoor Transfer (up to 150 Ml/d).

Space is also safeguarded for a future Severn to Thames Transfer connection and a Swindon and Oxfordshire potable transfer.

### 1.2 Water resources context

- **Water Resources South East (WRSE):** the regional plan selected the reservoir, and RAPID's gate three draft decision followed WRSE's revised draft plan. RAPID told the three companies to update their "best value" assessment through the statutory water resources planning process by 30 June 2026. The WRMP29/WRSE cycle may therefore revisit the case for the reservoir. The outcome of that update was not found and should be monitored.
- **Thames Water WRMP24:** the government approved it in September 2024 with the reservoir included. A judicial review of the reservoir/WRMP24 began on 25 June 2025. According to Wikipedia's "Abingdon Reservoir" article, it was "dismissed in the High Court on 25 July 2025". That is a secondary source, so check it against the judgment.
- **Cost and benefit sharing:** the scheme is jointly promoted, with Thames Water leading development for all three companies. No published split of capital cost between the companies was found. The app should treat cost-sharing as an open gap; RAPID gate documents on Ofwat's site are the best place to watch for it.
- **Delivery model:** Thames Water told New Civil Engineer: "Sesro will be built by a new entity licenced through Ofwat or a future regulator". Ofwat has consulted on, and published final notices for:
  - specifying White Horse Reservoir as a Specified Infrastructure Project under SIPR 2013 (the Tideway model);
  - issuing a Preparatory Works Notice to Thames Water.

  Under this model an Infrastructure Provider would design, build and finance the reservoir, and Thames Water would operate it.

### 1.3 Timeline

| Date | Event |
|---|---|
| 2006 | Thames Water proposes the Upper Thames Reservoir near Abingdon (BBC: "biggest in 25 years") |
| 2010 to 2011 | Public inquiry into Thames Water's WRMP; government rejects the £1bn reservoir in 2011 ("need not proven") |
| Ongoing | Vale Local Plan safeguards land between Drayton, East Hanney and Steventon (Core Policy 14/14a) |
| 2019 onward | RAPID gated process for strategic resource options begins; gate one final decision January 2022 |
| June to August 2024 | Non-statutory consultation (interim masterplan, access road options) |
| 28 August 2024 | EIA scoping request; Scoping Opinion adopted 8 October 2024 |
| September 2024 | WRMP24 approved, including the reservoir |
| January 2025 | Chancellor lists it among nine new reservoirs backed by government |
| Spring/Summer 2025 | Preferred options confirmed: rail siding Option 5 (western); main access road Option B (new A415 roundabout west of Marcham Interchange); Hanney road diversion Option A (south of Steventon/north of railway) |
| 28 October 2025 to 13 January 2026 | Statutory (s42/s47) consultation with PEI Report; 9 events, more than 1,200 attendees, about 2,500 responses |
| 3 December 2025 | RAPID gate three draft decision; consultation to 29 January 2026; unlocks £100m |
| January 2026 | Renamed White Horse Reservoir; £5.7bn main works contractor tender issued on Find a Tender (notice 005547-2026) |
| 19 March 2026 | Section 35 direction letter from Secretary of State published on the Planning Inspectorate's site |
| April 2026 | Clay compaction trial summary published |
| 14 May 2026 | RAPID confirms gate three passed |
| June 2026 | Thames Water "community research" (2,004 adults; 89% said "important") |
| July 2026 | Pre-application Programme Document published |
| September 2026 | Solar farm relocation dropped; access points raised from 6 to 17; September newsletter |
| 9 September to 7 October 2026 | Targeted consultation on access points (factsheet and map book corrected 5 October 2026) |
| 1 October 2026 | Three joint ventures shortlisted for main works; bids spring 2027; award autumn 2027 |
| November 2026 (expected) | DCO application submission |
| January 2027 (planned) | RAPID gate four submission |
| 2027 to 2028 (estimated) | Acceptance, pre-examination, examination (up to 6 months), recommendation, decision |
| 2029 or 2032 | Main construction start (conflicting Thames Water statements) |
| 2039 to 2041 | Filling and commissioning; water available 2040 |
| 2043 | Main works complete (PEI Report) |

### 1.4 Construction details (PEI Report, October 2025, as updated September 2026)

- **Phases:**
  - early works (habitat creation, species translocation) from 2027, under separate consents;
  - enabling works after the DCO: archaeology, demolition, utility diversions, access roads and the main compound; watercourse diversions over about 2 years; the rail siding by 2032; and the Hanney road diversion early in the phase;
  - main works: earthworks, embankment, tunnels, pumping station, intake/outfall and the T2ST works.
- **Compounds:** up to 20. The main compound would be in the north-east of the site near the pumping station, with concrete batching and possible worker accommodation up to two storeys high.
- **Working hours:**
  - core hours of 08:00 to 18:00 on weekdays and 09:00 to 13:00 on Saturdays (13:00 to 18:00 on Saturdays for maintenance only);
  - up to one extra hour each side for start-up and close-down;
  - 24/7 working for tunnelling, rail siding works, some highway works, concrete pours and filling.

  Earthworks would mainly run from March to November, with longer hours in summer.
- **Rail siding and materials handling facility:** off the Great Western Main Line about 1 km south of East Hanney (western option). It would take about 3 train arrivals and 3 departures a day, 5 days a week, about 47 weeks a year, with 20-wagon trains and possible 24-hour operation. Track works would span a 6.1 km corridor west of the facility.
- **Materials:**
  - about 65.8 Mm³ excavated, 94.4% of it reused on site;
  - about 3.7 Mm³ surplus exported;
  - about 9.7 million tonnes imported, including 4.0 Mt of sand and gravel and 1.7 Mt of rock armour.
- **Workforce:** peak about 1,800 (about 1,500 a day during peak earthworks in 2036), with contractor transport from Abingdon and Didcot.
- **Haul roads:** mainly on the inner and outer embankment perimeter. The safeguarded Wilts and Berks Canal corridor would serve as an early haul road from the rail siding. (East Hanney PC minutes of 14 October 2026 report Thames Water now saying it will use the public road network rather than internal haul roads.)
- **Rights of way:** long-term closures and diversions in the core area, plus localised diversions of National Cycle Route 5 and the Thames Path.
- **Utilities:**
  - the 132kV overhead line would be rerouted for about 1.95 km on nine pylons (SSEN);
  - gas mains would be diverted near Drayton Road (about 150m) and south of the embankment (about 800m).

### 1.5 Permanent changes

- **Main access road:** about 3 km long, from a new 3-arm roundabout on the A415 Marcham Road west of the A34 Marcham Interchange. A fourth arm is safeguarded for the Dalton Barracks development. The road would carry construction traffic first, then visitors.
- **Steventon to East Hanney road:** the existing Hanney Road/Steventon Road would be lost under the reservoir. It would be replaced by about 5 km of new road north of the railway, running from a new roundabout on the A338 to the approach into Steventon. The new road would have:
  - noise bunds of about 4m (for example near Bradfield Barn and Steventon);
  - a shared cycle track.

  The western stub of Steventon Road in East Hanney would be kept, with a turning head, a 25-space car park and a parking Traffic Regulation Order.
- **Off-site highway works:**
  - A338/Kingston Road junction, Frilford (if third-party works do not go ahead);
  - A415/Howard Cornish Road junction, Marcham;
  - A34 Marcham Interchange slip roads and signals, with temporary access via the Tesco roundabout;
  - lay-by conversion near Milton Interchange;
  - B4017 north of Drayton (tunnel shaft access);
  - Stonehill Lane upgrade (Thames intake);
  - A417/A4130 junction at Rowstock;
  - temporary A338 accesses;
  - the private road to Drayton sewage works.
- **River Thames:** an intake/outfall weir and spillway (about 40m by 65m) on the west bank near Culham, with guard piles extending 10m into the river and a debris boom. The Abingdon sewage works outfall would be relocated. A 500m by 90m flood-compensation berm would be dug on the east bank (South Oxfordshire, Culham area), with the Thames Path reinstated.
- **Watercourses:**
  - Mere Dyke (6.57 km) and Cow Common Brook (7.7 km) diverted east and west;
  - River Ock realigned (790m);
  - Landmead Ditch realigned;
  - a 14 km groundwater drain around the reservoir.
- **Recreation:** a Recreational Lakes Centre (two lakes), a Water Sports Centre on the crest, a Nature Education Centre (south-west) and a café on the crest. Thames Water projects 1.058 million visitors a year, peaking at about 8,000 a day. There would be about 1,300 car parking spaces including overflow, with trailheads at Steventon and East Hanney (25 spaces each).
- **Energy and heritage:**
  - floating solar (about 40 MW, covering about 6% of the surface);
  - a water channel for future restoration of the Wilts and Berks Canal;
  - 515 ha of woodland and grassland habitat creation.
- **Emergency discharge:** both reservoir tunnels and the river tunnel would allow emergency drawdown into the Thames south of Abingdon. This was the focus of South Oxfordshire's and Oxfordshire County Council's 2025 motions.

### 1.6 Land, compulsory purchase and compensation

The DCO will seek powers for compulsory acquisition and temporary possession of land within the Order limits. Thames Water published a "Land and Property Factsheet" for the 2025 statutory consultation. The September 2026 targeted consultation was aimed specifically at "landowners, and those with an interest in land" affected by the new access points.

This research found no discretionary blight or property-price support scheme specific to this project. That is a significant gap the app should track.

Residents should know the general statutory framework (general law, not project-specific findings):
- statutory blight notices (Town and Country Planning Act 1990, Part VI) can apply once land is identified for compulsory purchase in a DCO application;
- compensation follows the Compensation Code;
- residents should get advice from a RICS-qualified surveyor.

### 1.7 Thames Water's finances and the project

- **15 October 2026:** Thames Water said it needed its super senior facility raised by £2.4bn to £5.4bn, because it does not expect to finish recapitalising before running out of cash "by the end of 2026 or the start of 2027" (Guardian). Reuters reported it "had already drawn £2.65 billion of its existing £3 billion lifeline", that the increase would keep it running "into autumn 2027", and that creditors would vote on 29 October. (Thames Water's news index lists the consent request results as approved on 30 October 2026.)
- **16 October 2026:** it signed a Class B creditor Transaction Support Agreement. About £1bn of Class B debt would be written down for a recovery of about 5.9%. The deal depends on:
  - a restructuring plan ("RP2") backed by the London & Valley Water (L&VW) senior creditor consortium;
  - Ofwat launching a consultation on the recapitalisation.
- **Government position:** Reuters reports that Prime Minister Andy Burnham has pledged legislation enabling public ownership of water companies. Special administration remains the government's contingency.
- **What this means for residents:** the reservoir's delivery vehicle (an Infrastructure Provider under SIPR) is designed to sit outside Thames Water's balance sheet. But Thames Water is responsible for development spending, promoting the DCO and future operation. Special administration, a change of ownership or a government-led review of water bills could delay or reshape the scheme. GARD argues the government's October 2026 intervention on bills undermines the case.
- **Funding to date:** RAPID gate three released £100m for further development. GARD claims £543m has been spent; this is unverified.

### 1.8 Key controversies

| Against (GARD, councils, MPs) | For (Thames Water, partners, government) |
|---|---|
| Cost escalation from £2.2bn to £7.5bn "significantly undermines the business case and risks leaving bill payers liable" (Glover, Moran, Maynard, January 2026) | South East faces a shortfall of more than 2 billion litres a day by 2055 (RAPID) |
| Scale "unprecedented" for a fully bunded reservoir; dam-breach and emergency-discharge risk downstream (Abingdon, Culham, Sutton Courtenay) | Designed under the Reservoirs Act 1975 with a Construction Engineer and Reservoir Advisory Panel |
| Flood risk from diverting watercourses; groundwater | Watercourse diversions with floodplain compensation, "zero detriment" target |
| Alternatives: leakage reduction, water transfers/national grid (National Infrastructure Commission), smaller reservoirs, recycling | Summer 2026 drought (four heatwaves, Farmoor 68% full in September) shows the need for storage |
| More than 10 years of construction traffic, now 17 access points | About 1,800 construction jobs, leisure destination, 89% "important" in Thames Water polling (a commissioned survey, not independent) |
| Consultation inadequate (Oxfordshire County Council: fails three of four Gunning principles) | "Best value option" (Thames Water's Leonie Dubois) |
| Carbon emissions conflict with the Vale's 2045 net zero goal | Floating solar and hydro turbines |

---

## Part 2: Construction and Access Route Impacts

### 2.1 The original six access points (PEI Report, October 2025)

| Access | Location | Purpose | Assumed HGV route from A34 |
|---|---|---|---|
| A1 | A415 Marcham Road (new roundabout) | Main access, majority of materials | A34 Marcham Interchange, A415 |
| A2 | Diverted Steventon to East Hanney road | Rail siding construction | A34 Milton Interchange, A4130, A417, King Alfred Way, A338, through Rowstock, the Hendreds, Charlton, Grove |
| A3 | A338 | Western end of Hanney road diversion | As A2 |
| A4 | A338 | Early ecology/archaeology, western watercourse diversion | As A2, and also through the Hanneys |
| A5 | Steventon Road | Eastern end of Hanney road diversion | A34 Milton Interchange, A4130, B4017 through Steventon |
| A6 | B4017 through Caldecott | Thames intake/outfall | A34 Marcham Interchange, A415, B4017 through Caldecott (Abingdon) |

The PEI Report assumes 60% of construction traffic arrives on the A34 from the north and 40% from the south. Thames Water says the lead contractor will set mandatory HGV routes, and that traffic would be "directed not to pass through local villages unless this is necessary to reach a specific site access location". A direct temporary A34 northbound access near Drayton was considered but not assessed.

### 2.2 The September 2026 increase to 17 access points

Thames Water says it needs "additional access points around the site (up from six to 17) to carry out construction and environmental mitigation works (such as new habitat creation)". It also says "the overall construction traffic movements will be higher than previously forecast".

The full list is in the factsheet and map book (now extracted into the JSON):
- https://thames-sro.co.uk/media/cbbisrwi/factsheet-developing-our-plans-for-access-points-for-the-proposed-construction-of-white-horse-reservoir.pdf
- https://thames-sro.co.uk/media/nrxh1sj1/map-book-developing-our-plans-for-access-points-for-the-proposed-construction-of-white-horse-reservoir.pdf

Figures from Oxfordshire County Councillor Nathan Ley (Abingdon North), September 2026 newsletter, based on his own reading of Thames Water's documents (see the corrections at the top for the map book figures):

| Access | Location | Purpose | Peak movements (per hour, in and out) |
|---|---|---|---|
| A1 | A415 Marcham Road | Main and only permanent entrance, about 60% of construction traffic | About 60 HGV plus 41 van movements ("close to a lorry a minute") |
| A13 | Off Marcham Road via the Dalton Barracks road (Shippon side) | Compound west of A34 Marcham Interchange | About 5 HGVs |
| A14 | Off Marcham Road (east side of interchange, near Tesco) | Compound | About 4 HGVs |
| A16 | Off Drayton Road (B4017) | River tunnel shaft | About 12 HGVs |

Other estimates and reports:
- **Vale of White Horse's January 2026 response** modelled a hypothetical 110 HGVs an hour (1,100 a day). That included about 31 HGVs an hour through local settlements, plus about 38 employee vehicles in the peak hour through Marcham.
- **Harwell Parish Council** reports that consultation events indicated contingency access via **Rowstock and Cow Lane** and modified **A34 lay-bys**.

### 2.3 Responses to the targeted consultation

- **Oxfordshire County Council:** GARD reported on 12 October 2026 that the council's submission said the consultation "fails to meet three of the four Gunning Principles" and called for the DCO submission to be delayed. This is GARD's account and the council's original document was not found. Separately, the council's statutory consultation response of 13 January 2026, published by Ofwat, said: "Oxfordshire County Council cannot support the application in its current form due to the significant environmental impacts".
- **MPs and Vale councillor:** Olly Glover, Layla Moran, Charlie Maynard and Vale Cllr Sarah James (Hendreds ward) responded about "significant traffic increases" (GARD, 11 October 2026). Glover's January 2026 statutory response said "Construction traffic impacts are unacceptable".
- **Thames Water** says it is working with National Highways and the local highway authority on mitigation. Final traffic forecasts will be in the Environmental Statement submitted with the DCO.

---

## Part 3: Affected Areas

Superseded by the verified `local_councils` and `representatives` sections of the JSON, which cover 26 parish and town bodies, councillors at every tier, and MPs by place. Points from this part not repeated in the JSON:

- **East Hanney:** western edge of the reservoir; new A338 roundabout; Steventon Road stopped up, with a trailhead car park; rail siding about 1 km south; noise bunds; Nature Education Centre nearby. The parish site hosts GARD newsletters as PDFs.
- **Steventon:** Hanney Road lost and realigned; B4017 HGV route through the village; trailhead; noise bunds; footway works on Hanney Road. Neighbourhood Plan made September 2024.
- **Drayton (including Sutton Wick):** river tunnel intermediate shaft off the B4017 Drayton Road; gas main diversion; Drayton sewage works access; Sutton Wick scheduled monument; watercourse diversions. Neighbourhood Plan 2015.
- **Marcham:** main access A1 on the A415; A415/Howard Cornish Road junction works; about 38 employee vehicles in the peak hour through the village (Vale estimate); new "Garford to Marcham" path.
- **Garford, Frilford, Lyford:** habitat land; A338 route; Frilford A338/Kingston Road junction works; Noah's Ark/Venn Mill heritage; Ock Bridge on the tunnel boring machine delivery route; new paths.
- **Abingdon:** Marcham Road, Drayton Road, Caldecott/B4017 and Shippon/Dalton Barracks road; A34 Marcham Interchange works; air quality management area; emergency discharge and flood risk; Abingdon sewage works outfall moved. The town council has formally objected.
- **Culham:** Thames intake and outfall opposite; east bank flood berm; Thames Path; emergency discharge into the Thames.
- **Sutton Courtenay:** downstream of the intake and outfall; flood concern; Stonehill Lane area.
- **Milton / Milton Heights:** A34 Milton Interchange routing; lay-by conversion south of Milton Interchange. Olly Glover MP is a former Milton parish councillor.
- **Harwell (Rowstock):** A417/A4130 Rowstock junction works; possible contingency access via Rowstock and Cow Lane; A34 lay-bys.
- **Wantage (Charlton) and Grove:** A338/King Alfred Way HGV route; Order limits extend about 5.5 km west along the railway; possible Wantage and Grove station interface.
- **Didcot / East Challow:** Didcot is a workforce transport hub. Both submitted late scoping responses (June 2025), which are in the Planning Inspectorate's document library.
- **Downstream Thames communities:** emergency discharge and flood concern (South Oxfordshire District Council motion, 11 December 2025).

**Statutory publication rules for parish and town councils:**
- the summons and agenda must be published at least three clear days before a meeting (Local Government Act 1972, Schedule 12);
- minutes are approved at the next meeting;
- councils with turnover of £25,000 or less must publish minutes (within one month), agendas and accounts online under the Transparency Code for Smaller Authorities;
- the Openness of Local Government Bodies Regulations 2014 give the public the right to film and report meetings.

---

## Part 4: National, Regulatory, Regional and Principal Councils

| Body | Role | Where it publishes |
|---|---|---|
| **Planning Inspectorate** | Examines the DCO; Examining Authority recommends to the Secretary of State | Project: https://national-infrastructure-consenting.planninginspectorate.gov.uk/projects/WA010005 (plus /documents, /project-updates, /s51advice). Email sesro@planninginspectorate.gov.uk, phone 0303 444 5000. Documents on nsip-documents.planninginspectorate.gov.uk with references WA010005-0000xx. Boundary GeoJSON download |
| **Secretary of State for Environment, Food and Rural Affairs / Defra** | Decision-maker on the DCO; water policy; National Policy Statement for Water Resources Infrastructure | GOV.UK. The office-holder has changed since 2024; verify on GOV.UK |
| **Department for Transport / National Highways** | A34 is a strategic road; Thames Water is engaging National Highways on access and lay-bys | Statutory consultee; responses appear in the Planning Inspectorate library |
| **Ofwat / RAPID** (Ofwat, Environment Agency, Drinking Water Inspectorate) | Gated process; gate three passed May 2026; gate four expected January 2027; SIPR specification | ofwat.gov.uk RAPID and consultation pages |
| **Environment Agency** | Abstraction and flood regulator; statutory consultee | GOV.UK; monthly water situation reports |
| **Natural England, Historic England** | Statutory consultees (protected species licensing; scheduled monuments such as Sutton Wick) | Positions appear in Planning Inspectorate representations |
| **Network Rail** | Great Western Main Line connection and possessions for the rail siding | Planning Inspectorate library |
| **Parliament** | Debates and questions (for example a Westminster Hall debate on the future of Thames Water, January 2026) | Hansard and written questions APIs |
| **Water Resources South East** | Regional plan (WRMP29 cycle) | wrse.org.uk |
| **Thames Water** | Promoter | Project page https://thames-sro.co.uk/whitehorsereservoir ; document library https://thames-sro.co.uk/document-library/ (dated update record) ; team email whitehorsereservoir@thameswater.co.uk ; newsletter sign-up thames-sro.co.uk/contact-us/#subscribe. Newsletters roughly seasonal. Also on X, Facebook, YouTube |
| **Southern Water / Affinity Water** | Partners; T2ST pipeline DCO (Southern Water) | Company websites |
| **Find a Tender** | Contract notice 005547-2026 | OCDS API |
| **Oxfordshire County Council** | Highway authority; statutory consultee; objects; called for DCO delay | oxfordshire.gov.uk (consultation responses as PDFs); ModernGov at mycouncil.oxfordshire.gov.uk |
| **Vale of White Horse District Council** | Host authority; objects. Leader Cllr Bethia Thomas | whitehorsedc.gov.uk/category/sesro ; official correspondence page ; democratic.whitehorsedc.gov.uk ; joint documents on southandvale.gov.uk/app/uploads/. Annual Council on 13 May 2026 passed a unanimous motion asking the Planning Inspectorate to require seven targeted consultations |
| **South Oxfordshire District Council** | Thames east bank and Culham; emergency discharge motion 11 December 2025. Leader Cllr Maggie Filipova-Rivers | southoxon.gov.uk/category/sesro/ ; democratic.southoxon.gov.uk |

---

## Part 5: Campaign Groups and Media

**GARD (Group Against Reservoir Development)**
- Chair: Derek Stork.
- Website: https://groupagainstreservoirdevelopment.org (the older site abingdonreservoir.org.uk is legacy).
- Contact: gard.secretary@gmail.com (the group's published contact).
- Channels: Facebook (facebook.com/abingdonreservoir), Instagram and an email list.
- Petition: on 38 Degrees, co-branded with CPRE: https://you.38degrees.org.uk/petitions/stop-thames-water-s-plans-for-a-devastating-mega-reservoir
- Crowdfunder: launched October 2026 to fund DCO expertise; reached £5k in its first week.
- Annual general meeting held 3 July 2026.
- Parish councils redistribute its newsletters. Its DCO process explainer is at https://groupagainstreservoirdevelopment.org/dco-planning-process/

**Other groups**
- **CPRE Oxfordshire:** opposes the scheme (petition partner).
- **Inland Waterways Association:** responded to the consultation. It welcomed the Wilts and Berks Canal provision but raised concerns about navigation.
- **White Horse Reservoir Growth Coalition:** business supporters, launched 15 September 2026, led by BusinessLDN and Thames Valley Chamber of Commerce.
- **BBOWT and the Wilts and Berks Canal Trust:** positions not verified; monitor.

**Media**
- **Oxford Mail and its Herald series** (Abingdon and Wantage Heralds): the most frequent coverage, often syndicated via Yahoo and MSN.
- **Broadcast:** BBC Oxford and ITV Meridian.
- **Trade press:** New Civil Engineer, GE Plus, Construction Enquirer, Water Magazine, The Water Report.
- **Local digital:** Abingdon Blog (abingdonblog.co.uk), Wantage.com and Cllr Nathan Ley's Substack.
- Treat aggregators (Oxford Daily, Infrastructure Now, SSBCrack) as secondary sources.

---

## Part 6: How Residents Can Get Involved

1. **Register now for Planning Inspectorate updates** on the WA010005 project page ("Get updates").
2. **When the application is accepted** (a decision is due within 28 days of submission), Thames Water must publish notices. The **Relevant Representation** window will last at least 30 days. Submit a representation online to become an **Interested Party**. Only Interested Parties can:
   - make written submissions at each examination deadline;
   - comment on the Examining Authority's questions;
   - request and speak at open floor hearings.

   Keep representations focused on specific impacts, such as named roads, access points, flooding at your property or noise.
3. **Before submission:**
   - write to Thames Water at whitehorsereservoir@thameswater.co.uk;
   - ask your parish council, the Vale and Oxfordshire County Council to press for a further consultation.

   Councils' Local Impact Reports carry significant weight in the examination.
4. **Contact your representatives:** MPs, county and district councillors and parish clerks. Contact details are in the JSON.
5. **Speak at meetings:**
   - Parish councils must let the public attend, and usually have a public participation slot set by their standing orders.
   - The Vale, South Oxfordshire and Oxfordshire County Council allow registered public speakers and questions at Full Council, Cabinet and committees. Deadlines are in the JSON.
6. **Petitions:** sign the GARD/38 Degrees petition, a council e-petition, or a UK Parliament petition (petition.parliament.uk).
7. **Information requests:**
   - Thames Water is covered by the Environmental Information Regulations 2004. It counts as a public authority for EIR purposes but not for FOI. It must reply within 20 working days.
   - Councils, Defra, the Environment Agency and Ofwat are covered by both FOI and EIR.
8. **Community liaison:** Thames Water runs Technical Liaison Groups with council officers and briefs parish councils (for example its March 2026 briefing slides). No public community liaison group for residents was found. Residents can ask for one to be secured in the DCO's Code of Construction Practice.

---

## Caveats

- **Construction start dates conflict:** 2029 (Thames Water's web page) versus 2032 (the PEI Report and October 2026 press). Both give 2040 for first water.
- **Cost figures vary:** £5.5bn to £7.5bn, £5.7bn (contract value), £6.6bn (press) and £9.0bn (GARD, unverified).
- **Responses to the targeted consultation** from Oxfordshire County Council and the MPs are known only through GARD summaries. Obtain the originals.
- **Thames Water's ownership and solvency** could change significantly within weeks.

---

## Sources

- https://thames-sro.co.uk/whitehorsereservoir
- https://thames-sro.co.uk/projects/white-horse-reservoir-previously-known-as-south-east-strategic-reservoir-option-sesro/
- https://thames-sro.co.uk/document-library/
- https://thames-sro.co.uk/media/visjqnr4/chapter-2-project-description.pdf
- https://thames-sro.co.uk/media/njgbikl2/project-update-brochure-summer-2025.pdf
- https://thames-sro.co.uk/media/l0dj1ntx/sesro-spring-2025-project-update.pdf
- https://thames-sro.co.uk/media/1mbbswi3/reservoir-newsletter-winter-2026.pdf
- https://thames-sro.co.uk/media/k40ndnes/statutory-consultation-brochure-2025-interactive.pdf
- https://thames-sro.co.uk/news/thames-water-opens-57bn-tender-notice-for-nationally-critical-reservoir/
- https://www.thameswater.co.uk/news/2026/jan/major-milestone-as-thames-water-opens-57bn-tender-notice-for-nationally-critical-reservoir
- https://www.thameswater.co.uk/news/2026/oct/class-b-creditors-update
- https://www.thameswater.co.uk/about-us/performance/reservoir-levels-and-rainfall-figures
- https://national-infrastructure-consenting.planninginspectorate.gov.uk/projects/WA010005
- https://national-infrastructure-consenting.planninginspectorate.gov.uk/projects/WA010005/documents
- https://nsip-documents.planninginspectorate.gov.uk/published-documents/WA010005-000017-SESRO%20Scoping%20Opinion%202017%20EIA%20Regs%20FINAL.pdf
- https://www.ofwat.gov.uk/wp-content/uploads/2025/12/SESRO-gate-three-draft-decision-document.pdf
- https://www.ofwat.gov.uk/wp-content/uploads/2026/04/Appendix-2-White-Horse-Reservoir-Preparatory-Works-Draft-Reasons-Notice.pdf
- https://www.ofwat.gov.uk/consultation/white-horse-reservoir-draft-reasons-for-specifying-the-project-as-a-specified-infrastructure-project-and-draft-reasons-for-issuing-a-preparatory-works-notice/
- https://www.ofwat.gov.uk/wp-content/uploads/2024/03/SESRO-case-study.pdf
- https://www.ofwat.gov.uk/rapid-opens-consultation-on-decision-to-fund-sesro-to-proceed-towards-planning/
- https://www.find-tender.service.gov.uk/Notice/005547-2026
- https://www.whitehorsedc.gov.uk/category/sesro
- https://www.whitehorsedc.gov.uk/vale-of-white-horse-district-council/council-submits-response-to-thames-water-reservoir-consultation-2
- https://www.whitehorsedc.gov.uk/vale-of-white-horse-district-council/about-the-council/official-correspondence
- https://www.whitehorsedc.gov.uk/wp-content/uploads/sites/3/2019/07/Lo-res-Local-Plan-2031-Part-2-LPP2PS.pdf
- https://www.southandvale.gov.uk/app/uploads/sites/3/2026/01/VWHDC-SESRO-Statutory-Consultation-Response_Redacted.pdf
- https://www.southandvale.gov.uk/app/uploads/sites/3/2024/08/2024-08-23-Vale-response-to-Summer-2024-SESRO-consultation.pdf
- https://www.southandvale.gov.uk/app/uploads/sites/3/2024/09/2024-09-25-SESRO-VWHDC-Scoping-Response.pdf
- https://www.southoxon.gov.uk/sesro/council-leader-calls-for-answers-on-emergency-discharge-from-the-proposed-abingdon-reservoir
- https://www.southoxon.gov.uk/south-oxfordshire-district-council/south-oxfordshire-district-council-submits-response-to-thames-water-reservoir-consultation
- https://democratic.whitehorsedc.gov.uk/mgMemberIndexMP.aspx?bcr=1
- https://www.abingdon.gov.uk/wp-content/uploads/2025/09/Item-7-report-from-district-councillors-town-council-1-October-2025.pdf
- https://harwellparish.gov.uk/white-horse-reservoir-sesro-project-update/
- https://harwellparish.gov.uk/wp-content/uploads/2025/12/SESRO-Consultation-Response-revised-v2.pdf
- https://easthanneyparish.gov.uk/wp-content/uploads/2026/01/GARD-2026-Feb-Newsletter-.pdf
- https://suttoncourtenay-pc.gov.uk/news/gard-news-update-june-2026/
- https://suttoncourtenay-pc.gov.uk/news/thames-water-reservoir-newsletter-winter-2026/
- https://nunehamcourtenay-pc.gov.uk/wp-content/uploads/sites/23/2025/11/OxonCC-News-202511.pdf
- https://groupagainstreservoirdevelopment.org/
- https://groupagainstreservoirdevelopment.org/dco-planning-process/
- https://groupagainstreservoirdevelopment.org/2025/08/15/district-council-reiterates-opposition-to-reservoir-and-calls-for-alternatives-to-be-explored/
- https://groupagainstreservoirdevelopment.org/2025/11/12/final-consultation-now-open-please-respond/
- https://you.38degrees.org.uk/petitions/stop-thames-water-s-plans-for-a-devastating-mega-reservoir
- https://cllrdrnathanley.substack.com/p/abingdon-councillor-newsletter-september
- https://www.geplus.co.uk/news/project-news/white-horse-reservoir-plans-further-refined-ahead-of-dco-submission-17-09-2026/
- https://www.newcivilengineer.com/latest/regulators-recommend-7bn-abingdon-reservoir-development-advances-but-question-value-04-12-2025/
- https://www.newcivilengineer.com/latest/thames-water-discusses-7bn-abingdon-reservoir-consultation-and-next-steps-to-dco-30-10-2025/
- https://www.newcivilengineer.com/latest/7bn-abingdon-reservoir-moves-to-next-planning-stage-with-dco-expected-in-november-14-05-2026/
- https://www.newcivilengineer.com/latest/wouldnt-trust-thames-water-to-run-a-bath-mps-weigh-up-future-of-water-company-and-its-remediation-plans-09-01-2026/
- https://smartwatermagazine.com/news/newsroom/thames-water-shortlists-three-joint-ventures-for-white-horse-reservoir
- https://www.itv.com/news/meridian/2026-01-21/abingdon-reservoir-costs-spiralling-out-of-control-oxfordshire-mps-claim
- https://www.itv.com/news/meridian/2026-08-11/thames-water-says-nine-in-10-people-back-plans-for-abingdon-reservoir
- https://www.aol.com/news/mps-demand-meeting-over-spiralling-155457287.html
- https://uk.news.yahoo.com/second-largest-uk-reservoir-moving-100000473.html
- https://uk.news.yahoo.com/thames-water-updates-plans-white-105000845.html
- https://www.infrastructure-now.co.uk/article/496840/routes-for-abingdon-reservoirs-construction-traffic-revealed
- https://abingdonblog.co.uk/?p=34576
- https://wantage.com/developments/white-horse-reservoir-sesro/
- https://en.wikipedia.org/wiki/Abingdon_Reservoir
