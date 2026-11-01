/**
 * White Horse Reservoir -- client-side postcode lookup.
 *
 * Exposes window.WHRLookup with:
 *   lookup(postcode)      -- async, returns result object or null
 *   renderWidget(id)      -- wires up the #lookup-widget div
 */
window.WHRLookup = (function () {
  'use strict';

  let _cache = null;

  async function _loadData() {
    if (_cache) return _cache;
    const base = document.currentScript
      ? new URL('.', document.currentScript.src).href
      : '/white-horse-reservoir/assets/';
    const [ld, wa] = await Promise.all([
      fetch(base + 'lookup-data.json').then(function (r) { return r.json(); }),
      fetch(base + 'ward-aliases.json').then(function (r) { return r.json(); }).catch(function () { return {}; })
    ]);
    // Build alias map, skipping keys that begin with '_' (notes/comments).
    const aliases = {};
    for (const key of Object.keys(wa)) {
      if (!key.startsWith('_')) {
        aliases[key.toLowerCase()] = wa[key].toLowerCase();
      }
    }
    _cache = Object.assign({}, ld, { _aliases: aliases });
    return _cache;
  }

  function _match(list, field, value) {
    if (!value) return [];
    const v = value.toLowerCase();
    return list.filter(function (r) {
      return (r[field] || '').toLowerCase() === v;
    });
  }

  /**
   * Look up a postcode and return matched representatives, parish, and access
   * points.
   *
   * @param {string} postcode - UK postcode string (case-insensitive).
   * @returns {Promise<object|null>} Result object, or null if postcode not found.
   */
  async function lookup(postcode) {
    if (!postcode) return null;
    const clean = postcode.trim().toUpperCase().replace(/\s+/g, ' ');

    try {
      // Fetch postcodes.io.
      const res = await fetch(
        'https://api.postcodes.io/postcodes/' + encodeURIComponent(clean)
      );
      if (!res.ok) return null;
      const json = await res.json();
      if (json.status !== 200) return null;
      const pcData = json.result;

      // Load static data (cached after first call).
      const data = await _loadData();
      const reps = data.representatives;
      const aliases = data._aliases;

      const constituency = pcData.parliamentary_constituency || '';
      const rawWard = pcData.admin_ward || '';
      const ward = aliases[rawWard.toLowerCase()] || rawWard;
      const division = pcData.county_electoral_division || '';
      const parish = pcData.parish || '';

      return {
        mp: _match(reps, 'area', constituency).find(function (r) { return r.tier === 'MP'; }) || null,
        countyCouncillors: _match(reps, 'area', division).filter(function (r) { return r.tier === 'County'; }),
        districtCouncillors: _match(reps, 'area', ward).filter(function (r) { return r.tier === 'District'; }),
        parish: data.parishes.find(function (p) {
          return parish && (p.name || '').toLowerCase() === parish.toLowerCase();
        }) || null,
        accessPoints: data.access_points,
        raw: pcData
      };
    } catch (e) {
      return null;
    }
  }

  function _esc(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function _renderResult(r) {
    const parts = [];

    // MP section.
    if (r.mp) {
      parts.push(
        '<div class="lookup-rep">' +
        '<h3>Your MP</h3>' +
        '<p><a href="' + _esc(r.mp.profile_url) + '">' + _esc(r.mp.name) + '</a>' +
        ' (' + _esc(r.mp.area) + ')</p>' +
        '<p>Email: <a href="mailto:' + _esc(r.mp.email) + '">' + _esc(r.mp.email) + '</a></p>' +
        '<p>Stance: ' + _esc(r.mp.stance || 'Not recorded') + '</p>' +
        '</div>'
      );
    } else {
      parts.push(
        '<div class="lookup-rep">' +
        '<h3>Your MP</h3>' +
        '<p>We could not automatically match your MP for constituency: ' +
        _esc(r.raw.parliamentary_constituency || 'unknown') + '.</p>' +
        '</div>'
      );
    }

    // District councillors.
    if (r.districtCouncillors.length) {
      const list = r.districtCouncillors.map(function (c) {
        return '<li><a href="' + _esc(c.profile_url) + '">' + _esc(c.name) + '</a>' +
          ' (' + _esc(c.area) + ')</li>';
      }).join('');
      parts.push(
        '<div class="lookup-rep"><h3>District councillors</h3>' +
        '<ul>' + list + '</ul></div>'
      );
    } else {
      parts.push(
        '<div class="lookup-rep"><h3>District councillors</h3>' +
        '<p>We could not automatically match district councillors for ward: ' +
        _esc(r.raw.admin_ward || 'unknown') + '.</p></div>'
      );
    }

    // County councillors.
    if (r.countyCouncillors.length) {
      const list = r.countyCouncillors.map(function (c) {
        return '<li><a href="' + _esc(c.profile_url) + '">' + _esc(c.name) + '</a>' +
          ' (' + _esc(c.area) + ')</li>';
      }).join('');
      parts.push(
        '<div class="lookup-rep"><h3>County councillors</h3>' +
        '<ul>' + list + '</ul></div>'
      );
    } else {
      parts.push(
        '<div class="lookup-rep"><h3>County councillors</h3>' +
        '<p>We could not automatically match county councillors for division: ' +
        _esc(r.raw.county_electoral_division || 'unknown') + '.</p></div>'
      );
    }

    // Parish council.
    if (r.parish) {
      parts.push(
        '<div class="lookup-rep"><h3>Parish council</h3>' +
        '<p><a href="' + _esc(r.parish.website) + '">' + _esc(r.parish.name) + '</a></p>' +
        '<p>Contact: ' + _esc(r.parish.contact) + '</p></div>'
      );
    }

    return parts.join('') || '<p>No representatives found for this postcode area.</p>';
  }

  /**
   * Wire up a lookup widget inside containerId.
   *
   * Expects the container to already contain elements with ids:
   *   #lookup-postcode  (text input)
   *   #lookup-btn       (submit button)
   *   #lookup-result    (result container div)
   *
   * @param {string} containerId - id of the host element.
   */
  async function renderWidget(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const input = container.querySelector('#lookup-postcode');
    const btn = container.querySelector('#lookup-btn');
    const resultDiv = container.querySelector('#lookup-result');
    if (!input || !btn || !resultDiv) return;

    btn.addEventListener('click', async function () {
      const pc = input.value.trim();
      if (!pc) return;
      resultDiv.textContent = 'Looking up…';
      const result = await lookup(pc);
      if (!result) {
        resultDiv.innerHTML = '<p class="lookup-error">Postcode not found. Please check and try again.</p>';
        return;
      }
      resultDiv.innerHTML = _renderResult(result);
    });

    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') btn.click();
    });
  }

  // Auto-initialise on DOMContentLoaded when running in a browser.
  if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function () {
      renderWidget('lookup-widget');
    });
  }

  return { lookup: lookup, renderWidget: renderWidget };
}());
