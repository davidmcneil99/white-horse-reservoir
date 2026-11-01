// Guard: only run on index.html which has #reservoir-map
(function () {
  'use strict';

  var container = document.getElementById('reservoir-map');
  if (!container) return;   // <-- Ruling 7: guard

  var WHR_APPROXIMATE_BOUNDS = [
    [51.6500, -1.4650], [51.6500, -1.3700],
    [51.5900, -1.3700], [51.5900, -1.4650]
  ];

  var WHR_ACCESS_POINTS = [
    {id: 'A1',  lat: 51.6270, lon: -1.4380, label: 'A415 Marcham Road (main entrance)'},
    {id: 'A2',  lat: 51.6350, lon: -1.4700, label: 'A338 near East Hanney'},
    {id: 'A4',  lat: 51.6200, lon: -1.4550, label: 'A338 near Garford'},
    {id: 'A5',  lat: 51.6100, lon: -1.4050, label: 'Steventon to Hanney Road'},
    {id: 'A6',  lat: 51.6400, lon: -1.3550, label: 'Drayton Road / Stonehill Lane'},
    {id: 'A7',  lat: 51.6550, lon: -1.3450, label: 'A415 east / The Burycroft'},
    {id: 'A8',  lat: 51.6250, lon: -1.4600, label: 'A415 Kingston Road'},
    {id: 'A9',  lat: 51.5900, lon: -1.4200, label: 'A417 Ardington Lane'},
    {id: 'A10', lat: 51.5950, lon: -1.4050, label: "A417 Wood's Farm Road"},
    {id: 'A11', lat: 51.5980, lon: -1.3900, label: 'A417 Featherbed Lane'},
    {id: 'A12', lat: 51.5850, lon: -1.4700, label: 'A417/A338 Grove Park Drive'},
    {id: 'A13', lat: 51.6300, lon: -1.4250, label: 'A415 / Dalton Barracks road'},
    {id: 'A14', lat: 51.6280, lon: -1.4150, label: 'A415 east of interchange'},
    {id: 'A15', lat: 51.6300, lon: -1.4550, label: 'East Hanney to Steventon Road west'},
    {id: 'A16', lat: 51.6500, lon: -1.3700, label: 'Drayton Road'},
    {id: 'A17', lat: 51.6200, lon: -1.5000, label: 'A417 Faringdon Road'},
    {id: 'A20', lat: 51.6250, lon: -1.4650, label: 'A338 / Network Rail'}
  ];  // 17 entries total (A18/A19 dropped per plan)

  var map = L.map('reservoir-map').setView([51.615, -1.415], 12);

  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18
  }).addTo(map);

  L.polygon(WHR_APPROXIMATE_BOUNDS, {
    color: '#c0392b', weight: 2, fillOpacity: 0.1, dashArray: '8 4'
  }).bindPopup('Approximate reservoir order limits (rectangle - not the exact boundary)').addTo(map);

  WHR_ACCESS_POINTS.forEach(function (ap) {
    L.circleMarker([ap.lat, ap.lon], {radius: 6, color: '#00539b', fillOpacity: 0.8})
      .bindPopup('<strong>' + ap.id + '</strong><br>' + ap.label + '<br><em>Position approximate</em>')
      .addTo(map);
  });
}());
