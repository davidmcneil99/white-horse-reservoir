// Guard: only run on index.html which has #reservoir-map
(function () {
  'use strict';

  var container = document.getElementById('reservoir-map');
  if (!container) return;   // <-- Ruling 7: guard

  // DCO Order Limits polygon — Planning Inspectorate WA010005 (received 2026-09-03).
  // Simplified from 3,197 points to 43 using Ramer-Douglas-Peucker (ε=0.002°).
  // Source: https://national-infrastructure-consenting.planninginspectorate.gov.uk/projects/WA010005/download-boundary
  // Note: this is the full project order limits (includes Thames intake/tunnel corridor
  // east to Sutton Courtenay), not just the reservoir body.
  var WHR_DCO_BOUNDARY = [
    [51.670652, -1.308901],
    [51.668359, -1.306466],
    [51.666096, -1.311730],
    [51.669668, -1.315432],
    [51.664544, -1.315509],
    [51.665006, -1.313044],
    [51.657808, -1.316193],
    [51.656313, -1.278573],
    [51.658456, -1.273667],
    [51.657081, -1.276341],
    [51.652756, -1.274609],
    [51.646856, -1.283651],
    [51.652624, -1.306094],
    [51.651868, -1.313465],
    [51.649316, -1.310445],
    [51.651792, -1.313647],
    [51.648924, -1.319429],
    [51.647134, -1.320489],
    [51.644496, -1.313039],
    [51.646983, -1.320505],
    [51.634959, -1.316387],
    [51.628793, -1.320505],
    [51.627883, -1.334809],
    [51.621441, -1.337980],
    [51.620794, -1.331281],
    [51.618215, -1.409411],
    [51.634053, -1.395162],
    [51.634806, -1.386873],
    [51.637983, -1.391576],
    [51.650638, -1.380497],
    [51.653726, -1.354341],
    [51.653873, -1.358707],
    [51.655890, -1.356200],
    [51.662087, -1.359646],
    [51.661986, -1.352828],
    [51.658830, -1.352354],
    [51.653962, -1.338739],
    [51.662030, -1.341855],
    [51.666558, -1.334517],
    [51.667743, -1.336666],
    [51.670292, -1.311578],
    [51.674823, -1.308143],
    [51.670652, -1.308901]
  ];

  // Access point coordinates.
  // Sources: Nominatim/OpenStreetMap geocoding or map estimate from road/locality
  // description in data/access-points.csv. See coord_source column for per-point detail.
  var WHR_ACCESS_POINTS = [
    {id: 'A1',  lat: 51.6190, lon: -1.4148, label: 'A415 Marcham Road (main entrance / A34 interchange)'},
    {id: 'A2',  lat: 51.6302, lon: -1.4490, label: 'A338 near East Hanney (rail siding)'},
    {id: 'A4',  lat: 51.6368, lon: -1.4680, label: 'A338 near Garford (eastern wetlands)'},
    {id: 'A5',  lat: 51.6063, lon: -1.3890, label: 'Steventon to Hanney Road (east end, Steventon)'},
    {id: 'A6',  lat: 51.6492, lon: -1.2911, label: 'Drayton Road / Stonehill Lane, Sutton Courtenay'},
    {id: 'A7',  lat: 51.6472, lon: -1.2813, label: 'A415 east / The Burycroft, Caldecott (Thames berm)'},
    {id: 'A8',  lat: 51.6758, lon: -1.3879, label: 'A415 Kingston Road near Frilford / Hanney Road'},
    {id: 'A9',  lat: 51.5908, lon: -1.4128, label: 'A417 near Ardington Lane, Ardington'},
    {id: 'A10', lat: 51.5936, lon: -1.3752, label: "A417 / Wood's Farm Road near East Hendred"},
    {id: 'A11', lat: 51.6143, lon: -1.3141, label: 'A417 Featherbed Lane near A4130/A34 (Rowstock)'},
    {id: 'A12', lat: 51.6112, lon: -1.3935, label: 'A417/A338 Grove Park Drive (King Alfred Way), Grove'},
    {id: 'A13', lat: 51.6315, lon: -1.3900, label: 'A415 / road to Dalton Barracks, Shippon / Marcham'},
    {id: 'A14', lat: 51.6210, lon: -1.4012, label: 'A415 Marcham Road (east of A34 interchange)'},
    {id: 'A15', lat: 51.6278, lon: -1.4368, label: 'East Hanney to Steventon Road (west end, E. Hanney)'},
    {id: 'A16', lat: 51.6404, lon: -1.3098, label: 'Drayton Road, Drayton (river tunnel shaft access)'},
    {id: 'A17', lat: 51.6168, lon: -1.4879, label: 'A417 Faringdon Road / Network Rail, near Goosey'},
    {id: 'A20', lat: 51.6132, lon: -1.4155, label: 'A338 / Network Rail near Grove'}
  ];  // 17 entries total (A18/A19 dropped per plan)

  var map = L.map('reservoir-map').setView([51.630, -1.370], 11);

  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18
  }).addTo(map);

  L.polygon(WHR_DCO_BOUNDARY, {
    color: '#c0392b', weight: 2, fillOpacity: 0.1, dashArray: '8 4'
  }).bindPopup(
    'DCO Order Limits — Planning Inspectorate WA010005<br>' +
    '<small>Official boundary (simplified). Includes reservoir site, Thames intake/tunnel ' +
    'corridor east to Sutton Courtenay. Source: Planning Inspectorate download-boundary, ' +
    'received 2026-09-03.</small>'
  ).addTo(map);

  WHR_ACCESS_POINTS.forEach(function (ap) {
    L.circleMarker([ap.lat, ap.lon], {radius: 6, color: '#00539b', fillOpacity: 0.8})
      .bindPopup('<strong>' + ap.id + '</strong><br>' + ap.label + '<br><em>Position estimated from road/locality description</em>')
      .addTo(map);
  });
}());
