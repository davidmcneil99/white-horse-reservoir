/**
 * White Horse Reservoir -- client-side letter rendering.
 *
 * Exposes window.WHRLetters:
 *   render(templateKey, lookupResult)  -- async, returns filled HTML string
 *   wire(containerId, lookupResult)    -- wires up the letters.html page
 *
 * Placeholder map ({{token}} -> value):
 *   mp_name              -> lookupResult.mp.name
 *   mp_email             -> lookupResult.mp.email
 *   sender_area          -> lookupResult.raw.parish or admin_ward
 *   sender_constituency  -> lookupResult.raw.parliamentary_constituency
 *   current_date         -> today in "1 January 2026" format
 *   <frontmatter key>    -> filled frontmatter value (e.g. recipient_title)
 *   anything else        -> "[not found - please fill in]"
 */
window.WHRLetters = (function () {
  'use strict';

  // Capture base URL at script load time (document.currentScript is only set
  // during synchronous script execution, not inside deferred callbacks).
  var _scriptBase = (function () {
    var s = document.currentScript;
    return s ? new URL('.', s.src).href : '/white-horse-reservoir/assets/';
  }());

  var _cache = null;
  var _currentKey = null;
  var _currentLookup = null;

  function _esc(str) {
    return String(str == null ? '' : str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  async function _loadData() {
    if (_cache) return _cache;
    var data = await fetch(_scriptBase + 'letters-data.json').then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    });
    _cache = data;
    return _cache;
  }

  /**
   * Build the substitution map for a template + lookup result, then return
   * the filled body string (plain text, not HTML).
   *
   * Frontmatter values are expanded first (using the base map), then added to
   * the map so the body can reference them (e.g. {{recipient_title}}).
   */
  function _fill(template, lookupResult) {
    var r = lookupResult || {};
    var NOT_FOUND = '[not found - please fill in]';

    var map = {
      mp_name:                  (r.mp && r.mp.name)  || NOT_FOUND,
      mp_email:                 (r.mp && r.mp.email) || NOT_FOUND,
      county_councillor_name:   (r.countyCouncillors && r.countyCouncillors[0] && r.countyCouncillors[0].name) || NOT_FOUND,
      county_councillor_email:  (r.countyCouncillors && r.countyCouncillors[0] && r.countyCouncillors[0].email) || NOT_FOUND,
      district_councillor_name:  (r.districtCouncillors && r.districtCouncillors[0] && r.districtCouncillors[0].name) || NOT_FOUND,
      district_councillor_email: (r.districtCouncillors && r.districtCouncillors[0] && r.districtCouncillors[0].email) || NOT_FOUND,
      parish_contact: (function () {
        var contact = r.parish && r.parish.contact;
        if (!contact) return NOT_FOUND;
        var m = contact.match(/[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}/);
        return m ? m[0] : NOT_FOUND;
      }()),
      sender_area:              (r.raw && (r.raw.parish || r.raw.admin_ward)) || NOT_FOUND,
      sender_ward:              (r.raw && r.raw.admin_ward) || NOT_FOUND,
      sender_constituency:      (r.raw && r.raw.parliamentary_constituency) || NOT_FOUND,
      current_date: new Date().toLocaleDateString('en-GB', {
        day: 'numeric', month: 'long', year: 'numeric'
      }),
    };

    function subst(str) {
      return String(str == null ? '' : str).replace(/\{\{([^}]+)\}\}/g, function (_, token) {
        var k = token.trim();
        return Object.prototype.hasOwnProperty.call(map, k) ? map[k] : NOT_FOUND;
      });
    }

    // Step 1: expand each frontmatter field value using the base map, then
    // add the result to the map so the body can reference it.
    var key;
    for (key in template) {
      if (key !== 'body' && Object.prototype.hasOwnProperty.call(template, key)) {
        map[key] = subst(String(template[key] == null ? '' : template[key]));
      }
    }

    // Step 2: expand the body with the full map.
    return subst(template.body || '');
  }

  /**
   * Render a letter template.  Returns an HTML string.
   *
   * @param {string} templateKey - Key from letters-data.json (e.g. "mp").
   * @param {object|null} lookupResult - Result from WHRLookup.lookup(), or null.
   * @returns {Promise<string>} HTML string.
   */
  async function render(templateKey, lookupResult) {
    try {
      var data = await _loadData();
      var tpl = data[templateKey];
      if (!tpl) {
        return '<p class="letter-error">Letter template not found: ' + _esc(templateKey) + '</p>';
      }
      var filled = _fill(tpl, lookupResult);
      return '<pre class="letter-preview">' + _esc(filled) + '</pre>';
    } catch (e) {
      return '<p class="letter-error">Could not load letter template. Please try again.</p>';
    }
  }

  /**
   * Wire up the letters.html letter controls.
   *
   * Finds: #letter-type, #letter-output, #copy-letter, #email-letter.
   * On select change: resolves the current postcode (from #lookup-postcode),
   * calls render(), and updates the output div and action buttons.
   *
   * @param {string} containerId - Unused (kept for API symmetry); DOM ids are global.
   * @param {object|null} initialLookupResult - Seed lookup result (may be null).
   */
  async function wire(containerId, initialLookupResult) {
    _currentLookup = initialLookupResult || null;

    var select   = document.getElementById('letter-type');
    var output   = document.getElementById('letter-output');
    var copyBtn  = document.getElementById('copy-letter');
    var emailBtn = document.getElementById('email-letter');

    if (!select || !output) return;

    async function renderCurrent() {
      var key = select.value;
      if (!key) {
        output.innerHTML = '';
        if (copyBtn)  copyBtn.style.display  = 'none';
        if (emailBtn) emailBtn.style.display = 'none';
        _currentKey = null;
        return;
      }

      // Re-run postcode lookup using current input value so the letter is
      // freshly personalised after the user has looked up their postcode.
      var postcodeInput = document.getElementById('lookup-postcode');
      if (postcodeInput && postcodeInput.value.trim() && window.WHRLookup) {
        try {
          _currentLookup = await window.WHRLookup.lookup(postcodeInput.value.trim());
          window._WHRLastLookup = _currentLookup;
        } catch (_e) {
          _currentLookup = null;
        }
      }

      _currentKey = key;
      var zipBtn = document.getElementById('download-zip');
      try {
        var html = await render(key, _currentLookup);
        output.innerHTML = html;
        if (copyBtn)  copyBtn.style.display  = '';
        if (emailBtn) emailBtn.style.display = '';
        if (zipBtn)   zipBtn.style.display   = '';
      } catch (e) {
        output.textContent = 'Error loading letter template. Please try again.';
        if (copyBtn)  copyBtn.style.display  = 'none';
        if (emailBtn) emailBtn.style.display = 'none';
        if (zipBtn)   zipBtn.style.display   = 'none';
      }
    }

    select.addEventListener('change', renderCurrent);

    // Copy button: writes the letter plain text to the clipboard.
    if (copyBtn) {
      copyBtn.addEventListener('click', async function () {
        var pre = output.querySelector('pre.letter-preview');
        if (!pre) return;
        try {
          await navigator.clipboard.writeText(pre.textContent);
        } catch (_e) {
          // Clipboard API unavailable; user can select and copy manually.
        }
      });
    }

    // Email button: opens the default mail client with recipient, subject and body.
    if (emailBtn) {
      emailBtn.addEventListener('click', async function () {
        if (!_currentKey) return;
        try {
          var data = await _loadData();
          var tpl = data[_currentKey];
          if (!tpl) return;

          // Re-build the filled frontmatter to get recipient_email and subject.
          var r = _currentLookup || {};
          var NOT_FOUND = '[not found - please fill in]';
          var fmMap = {
            mp_name:                  (r.mp && r.mp.name)  || NOT_FOUND,
            mp_email:                 (r.mp && r.mp.email) || NOT_FOUND,
            county_councillor_name:   (r.countyCouncillors && r.countyCouncillors[0] && r.countyCouncillors[0].name) || NOT_FOUND,
            county_councillor_email:  (r.countyCouncillors && r.countyCouncillors[0] && r.countyCouncillors[0].email) || NOT_FOUND,
            district_councillor_name:  (r.districtCouncillors && r.districtCouncillors[0] && r.districtCouncillors[0].name) || NOT_FOUND,
            district_councillor_email: (r.districtCouncillors && r.districtCouncillors[0] && r.districtCouncillors[0].email) || NOT_FOUND,
            parish_contact: (function () {
              var contact = r.parish && r.parish.contact;
              if (!contact) return NOT_FOUND;
              var m = contact.match(/[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}/);
              return m ? m[0] : NOT_FOUND;
            }()),
            sender_area:              (r.raw && (r.raw.parish || r.raw.admin_ward)) || NOT_FOUND,
            sender_ward:              (r.raw && r.raw.admin_ward) || NOT_FOUND,
            sender_constituency:      (r.raw && r.raw.parliamentary_constituency) || NOT_FOUND,
            current_date: new Date().toLocaleDateString('en-GB', {
              day: 'numeric', month: 'long', year: 'numeric'
            }),
          };
          function substFm(str) {
            return String(str == null ? '' : str).replace(/\{\{([^}]+)\}\}/g, function (_, token) {
              var k = token.trim();
              return Object.prototype.hasOwnProperty.call(fmMap, k) ? fmMap[k] : NOT_FOUND;
            });
          }
          var fmKey;
          for (fmKey in tpl) {
            if (fmKey !== 'body' && Object.prototype.hasOwnProperty.call(tpl, fmKey)) {
              fmMap[fmKey] = substFm(String(tpl[fmKey] == null ? '' : tpl[fmKey]));
            }
          }

          var recipientEmail = (fmMap['recipient_email'] !== NOT_FOUND ? fmMap['recipient_email'] : '') || '';
          var subject        = fmMap['subject']         || fmMap['title'] || '';
          var pre            = output.querySelector('pre.letter-preview');
          var bodyText       = pre ? pre.textContent : '';

          var mailto = 'mailto:' + encodeURIComponent(recipientEmail) +
            '?subject=' + encodeURIComponent(subject) +
            '&body='    + encodeURIComponent(bodyText);
          window.location.href = mailto;
        } catch (_e) {
          // Silently ignore; the user can still copy the letter manually.
        }
      });
    }
  }

  /**
   * Download all 10 letter templates as a ZIP file.
   *
   * @param {object} lookupResult - Lookup result to personalise letters (may be empty).
   */
  var _LETTER_KEYS = [
    'county-councillor',
    'defra-secretary-of-state',
    'district-councillor',
    'eir-thames-water',
    'foi-missing-minutes',
    'mp',
    'ofwat',
    'parish-clerk',
    'planning-inspectorate-relevant-representation',
    'thames-water',
  ];

  async function _downloadAllAsZip(lookupResult) {
    if (typeof JSZip === 'undefined') {
      alert('ZIP library not loaded. Please try again.');
      return;
    }
    try {
      var data = await _loadData();
      var zip = new JSZip();
      _LETTER_KEYS.forEach(function (key) {
        var tpl = data[key];
        var text = tpl ? _fill(tpl, lookupResult || {}) : '';
        zip.file(key + '.txt', text);
      });
      var blob = await zip.generateAsync({ type: 'blob' });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'white-horse-reservoir-letters.zip';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(a.href);
    } catch (e) {
      alert('Could not generate ZIP. Please try again.');
    }
  }

  // Auto-wire on DOMContentLoaded when running in a browser.
  if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function () {
      wire('letter-section', null);

      // Pre-select letter type from URL hash (e.g. letters.html#mp).
      (function () {
        var hash = window.location.hash.replace('#', '');
        if (hash) {
          var sel = document.getElementById('letter-type');
          if (sel) {
            var opt = sel.querySelector('option[value="' + hash + '"]');
            if (opt) {
              sel.value = hash;
              sel.dispatchEvent(new Event('change'));
            }
          }
        }
      }());

      // Wire ZIP download button.
      var zipBtn = document.getElementById('download-zip');
      if (zipBtn) {
        zipBtn.addEventListener('click', function () {
          _downloadAllAsZip(window._WHRLastLookup || {});
        });
      }
    });
  }

  return { render: render, wire: wire };
}());
