// Guard: only run on index.html which has #reservoir-map
(function () {
  'use strict';

  var container = document.getElementById('reservoir-map');
  if (!container) return;   // <-- Ruling 7: guard

  // Layer definitions for both Planning Inspectorate projects.
  var layers = {
    reservoir: { color: '#2563eb', label: 'White Horse Reservoir (WA010005)' },
    cearn:     { color: '#d97706', label: 'Cearn Solar Farm (EN0110044)' }
  };

  // DCO project boundary — OSM-anchored coordinates, 61-point polygon traced
  // against the Thames Water statutory consultation Order Limits map (WA010005).
  // Covers: main reservoir body, NE arm (A1/A13/A14, Abingdon A415 corridor),
  // E arm (A6/A7/A16, Sutton Courtenay/Thames berm), W rail siding corridor (A17),
  // SE corner (A11, Rowstock), NW (A8, Kingston Bagpuize). Single connected polygon;
  // isolated DCO parcels (A10, A11 outlier etc.) are not included.
  var WHR_RESERVOIR_BODY = [
    [51.65368, -1.31711],
    [51.65200, -1.31793],
    [51.64716, -1.31948],
    [51.64236, -1.31896],
    [51.63858, -1.31544],
    [51.62990, -1.31930],
    [51.62873, -1.32823],
    [51.62404, -1.33192],
    [51.60701, -1.33128],
    [51.59810, -1.37660],
    [51.61077, -1.38908],
    [51.61389, -1.41273],
    [51.61695, -1.41140],
    [51.61077, -1.49242],
    [51.61482, -1.49174],
    [51.62079, -1.41998],
    [51.62612, -1.40934],
    [51.62676, -1.39904],
    [51.64732, -1.38247],
    [51.65057, -1.39380],
    [51.64966, -1.40084],
    [51.64545, -1.40728],
    [51.64023, -1.40934],
    [51.64013, -1.41260],
    [51.64551, -1.41449],
    [51.64924, -1.41664],
    [51.65467, -1.41595],
    [51.65669, -1.39887],
    [51.66260, -1.39252],
    [51.65472, -1.39123],
    [51.65557, -1.38591],
    [51.65621, -1.37904],
    [51.66372, -1.37681],
    [51.66217, -1.36857],
    [51.66643, -1.36625],
    [51.66925, -1.36213],
    [51.66585, -1.34780],
    [51.66377, -1.34565],
    [51.66489, -1.33372],
    [51.66878, -1.33398],
    [51.67053, -1.31913],
    [51.67011, -1.31184],
    [51.67554, -1.30720],
    [51.67468, -1.30574],
    [51.66973, -1.30883],
    [51.66936, -1.30506],
    [51.66979, -1.29458],
    [51.65705, -1.30265],
    [51.65592, -1.29832],
    [51.65584, -1.29291],
    [51.65528, -1.28905],
    [51.65464, -1.28467],
    [51.65712, -1.28390],
    [51.65917, -1.28334],
    [51.65837, -1.27665],
    [51.64884, -1.27622],
    [51.64902, -1.28390],
    [51.65123, -1.28832],
    [51.65155, -1.28948],
    [51.65339, -1.29694],
    [51.65480, -1.30523]
  ];

  // Access point coordinates.
  // Sources: Nominatim/OpenStreetMap geocoding or map estimate from road/locality
  // description in data/access-points.csv. See coord_source column for per-point detail.
  var WHR_ACCESS_POINTS = [
    {id: 'A1',  lat: 51.6694, lon: -1.313, label: 'A415 Marcham Road (main entrance / A34 interchange)'},
    {id: 'A2',  lat: 51.6218, lon: -1.4061, label: 'A338 near East Hanney (rail siding)'},
    {id: 'A4',  lat: 51.6561, lon: -1.3757, label: 'A338 near Garford (eastern wetlands)'},
    {id: 'A5',  lat: 51.6299, lon: -1.3407, label: 'Steventon to Hanney Road (east end, Steventon)'},
    {id: 'A6',  lat: 51.6572, lon: -1.3027, label: 'Drayton Road / Stonehill Lane, Sutton Courtenay'},
    {id: 'A7',  lat: 51.6583, lon: -1.2763, label: 'A415 east / The Burycroft, Caldecott (Thames berm)'},
    {id: 'A8',  lat: 51.6496, lon: -1.4132, label: 'A415 Kingston Road near Frilford / Hanney Road'},
    {id: 'A9',  lat: 51.5981, lon: -1.3766, label: 'A417 near Ardington Lane, Ardington'},
    {id: 'A10', lat: 51.6017, lon: -1.3395, label: "A417 / Wood's Farm Road near East Hendred"},
    {id: 'A11', lat: 51.6064, lon: -1.326, label: 'A417 Featherbed Lane near A4130/A34 (Rowstock)'},
    {id: 'A12', lat: 51.6103, lon: -1.3899, label: 'A417/A338 Grove Park Drive (King Alfred Way), Grove'},
    {id: 'A13', lat: 51.6705, lon: -1.3178, label: 'A415 / road to Dalton Barracks, Shippon / Marcham'},
    {id: 'A14', lat: 51.6682, lon: -1.3041, label: 'A415 Marcham Road (east of A34 interchange)'},
    {id: 'A15', lat: 51.6347, lon: -1.3862, label: 'East Hanney to Steventon Road (west end, E. Hanney)'},
    {id: 'A16', lat: 51.6528, lon: -1.3065, label: 'Drayton Road, Drayton (river tunnel shaft access)'},
    {id: 'A17', lat: 51.6124, lon: -1.4877, label: 'A417 Faringdon Road / Network Rail, near Goosey'},
    {id: 'A20', lat: 51.619, lon: -1.4085, label: 'A338 / Network Rail near Grove'}
  ];  // 17 entries total (A18/A19 dropped per plan)

  var map = L.map('reservoir-map').setView([51.630, -1.370], 11);

  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18
  }).addTo(map);

  var reservoirLayer = L.polygon(WHR_RESERVOIR_BODY, {
    color: layers.reservoir.color, weight: 2, fillOpacity: 0.1, dashArray: '8 4'
  }).bindPopup(
    'Proposed Reservoir — DCO Project Area<br>' +
    '<small>Indicative outline based on Thames Water reference maps. ' +
    'Full DCO Order Limits (Planning Inspectorate WA010005) cover a larger area ' +
    'including the Thames intake/tunnel corridor to Sutton Courtenay.</small>'
  ).addTo(map);

  WHR_ACCESS_POINTS.forEach(function (ap) {
    L.circleMarker([ap.lat, ap.lon], {radius: 6, color: '#00539b', fillOpacity: 0.8})
      .bindPopup('<strong>' + ap.id + '</strong><br>' + ap.label + '<br><em>Position estimated from road/locality description</em>')
      .addTo(map);
  });

  // Fetch EN0110044 (Cearn Solar Farm) boundary at runtime with a graceful fallback.
  var cearnLayer = null;
  fetch('assets/cearn-boundary.geojson')
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (data) {
      if (data) {
        cearnLayer = L.geoJSON(data, {
          style: { color: layers.cearn.color, weight: 2, fillOpacity: 0.1 }
        });
        var cearnCheckbox = document.getElementById('show-cearn');
        if (!cearnCheckbox || cearnCheckbox.checked) {
          cearnLayer.addTo(map);
        }
      } else {
        console.warn('Cearn boundary not available');
      }
    })
    .catch(function () { console.warn('Cearn boundary fetch failed'); });

  // Layer toggle checkboxes - wire up after DOM ready.
  var reservoirToggle = document.getElementById('show-reservoir');
  var cearnToggle = document.getElementById('show-cearn');

  if (reservoirToggle) {
    reservoirToggle.addEventListener('change', function () {
      if (this.checked) {
        map.addLayer(reservoirLayer);
      } else {
        map.removeLayer(reservoirLayer);
      }
    });
  }

  if (cearnToggle) {
    cearnToggle.addEventListener('change', function () {
      if (cearnLayer) {
        if (this.checked) {
          map.addLayer(cearnLayer);
        } else {
          map.removeLayer(cearnLayer);
        }
      }
    });
  }
}());
