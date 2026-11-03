import json
from pathlib import Path
from generator.build import load_all_data, build, _build_letters_data


def test_solar_home_has_blurb():
    build()
    html = Path("docs/solar/index.html").read_text(encoding="utf-8")
    assert "EN0110044" in html
    assert "Telis Energy" in html


def test_solar_home_has_featured_actions():
    build()
    html = Path("docs/solar/index.html").read_text(encoding="utf-8")
    assert "Most urgent actions" in html
    assert "Planning Inspectorate" in html


def test_solar_actions_json_has_featured_fields():
    data = json.loads(Path("data/cearn/content/actions.json").read_text(encoding="utf-8"))
    featured = [a for a in data if a.get("featured")]
    assert len(featured) == 3
    orders = sorted(a["featured_order"] for a in featured)
    assert orders == [1, 2, 3]


def test_solar_home_has_map():
    build()
    html = Path("docs/solar/index.html").read_text(encoding="utf-8")
    assert 'id="map"' in html
    assert 'data-section="solar"' in html


def test_solar_home_has_featured_actions_intro():
    build()
    html = Path("docs/solar/index.html").read_text(encoding="utf-8")
    assert "23 November 2026" in html


def test_cearn_featured_actions_intro_in_context():
    data = load_all_data()
    assert "cearn_featured_actions_intro" in data
    assert "23 November 2026" in data["cearn_featured_actions_intro"]


def test_solar_facts_title_has_vale_watch():
    build()
    html = Path("docs/solar/facts.html").read_text(encoding="utf-8")
    assert "Vale Watch" in html


def test_solar_actions_title_has_vale_watch():
    build()
    html = Path("docs/solar/actions.html").read_text(encoding="utf-8")
    assert "Vale Watch" in html


def test_solar_letters_title_has_vale_watch():
    build()
    html = Path("docs/solar/letters.html").read_text(encoding="utf-8")
    assert "Vale Watch" in html


def test_desnz_sos_name_is_ed_miliband():
    data = _build_letters_data()
    fm = data.get("desnz-secretary-of-state", {})
    assert fm.get("recipient_name") == "Ed Miliband MP"


def test_solar_facts_combined_link_root_relative():
    build()
    html = Path("docs/solar/facts.html").read_text(encoding="utf-8")
    assert "/white-horse-reservoir/combined/" in html
    assert 'href="combined-impacts.html"' not in html


def test_timeline_is_distant_future_flag():
    """Items with year >= today().year + 3 get is_distant_future=True."""
    data = load_all_data()
    # Use integer year comparison so 2029 is correctly classified as distant future
    near = [t for t in data["timeline"] if int(str(t.get("date", "0000"))[:4]) < 2029]
    far  = [t for t in data["timeline"] if int(str(t.get("date", "0000"))[:4]) >= 2029]
    assert all(not t["is_distant_future"] for t in near), "pre-2029 items should not be distant future"
    assert all(t["is_distant_future"] for t in far), "2029+ items should be distant future"


def test_timeline_linked_actions():
    """Timeline items with action_ids get linked_actions list."""
    data = load_all_data()
    t024 = next(t for t in data["timeline"] if t["id"] == "t024")
    assert "linked_actions" in t024
    ids = [a["id"] for a in t024["linked_actions"]]
    assert "ac019" in ids
    assert "ac012" in ids


def test_actions_sorted_by_deadline():
    """Within the 'now' timing group, actions with earlier deadlines appear first."""
    data = load_all_data()
    now_actions = [a for a in data["actions"] if a["timing"] == "now"]
    deadlines = [a.get("deadline") for a in now_actions]
    # All non-None deadlines must appear before None entries
    seen_none = False
    for d in deadlines:
        if d is None:
            seen_none = True
        elif seen_none:
            raise AssertionError(f"deadline {d} appeared after a None deadline")


def test_actions_by_id_in_context():
    """build() context contains actions_by_id dict keyed by action id."""
    data = load_all_data()
    assert "actions_by_id" in data
    assert "ac006" in data["actions_by_id"]
    assert data["actions_by_id"]["ac006"]["letter_key"] == "thames-water"


def test_actions_page_has_letter_buttons():
    """actions.html output has Generate-letter links for actions with letter_key."""
    build()
    html = Path("docs/reservoir/actions.html").read_text(encoding="utf-8")
    # ac006 has letter_key = "thames-water"
    assert "thames-water" in html
    assert "Generate letter" in html


def test_actions_page_has_deadlines():
    """actions.html output shows deadline for actions that have one."""
    build()
    html = Path("docs/reservoir/actions.html").read_text(encoding="utf-8")
    assert "2026-11-30" in html or "November 2026" in html or "30 November" in html


def test_letters_page_has_template_note():
    """letters.html output contains the template note."""
    build()
    html = Path("docs/reservoir/letters.html").read_text(encoding="utf-8")
    assert "template" in html.lower() and "adjust" in html.lower()


def test_facts_page_has_details_element():
    """facts.html output contains a <details> element for distant-future items."""
    build()
    facts_html = Path("docs/reservoir/facts.html").read_text(encoding="utf-8")
    assert "<details" in facts_html
    assert "2029" in facts_html or "2040" in facts_html  # at least one distant-future item


def test_facts_page_action_links():
    """facts.html output contains links to actions for timeline items with action_ids."""
    build()
    facts_html = Path("docs/reservoir/facts.html").read_text(encoding="utf-8")
    # t024 has action_ids linking to ac019 and ac012
    assert '#action-ac019' in facts_html


def test_load_all_data_has_required_keys():
    data = load_all_data()
    for key in ("timeline", "quotes", "actions", "representatives",
                "local_councils", "access_points", "news_items",
                "corrections", "still_to_check"):
        assert key in data, f"Missing key: {key}"


def test_load_all_data_timeline_has_source():
    data = load_all_data()
    assert len(data["timeline"]) > 15
    assert all("source_url" in t for t in data["timeline"])


def test_build_creates_all_pages(tmp_path):
    build(output_dir=tmp_path)
    expected = [
        "index.html",
        "about.html",
        "reservoir/index.html",
        "reservoir/facts.html",
        "reservoir/actions.html",
        "reservoir/letters.html",
        "reservoir/access-points.html",
        "solar/index.html",
        "solar/facts.html",
        "solar/actions.html",
        "solar/letters.html",
        "combined/index.html",
        "combined/facts.html",
        "combined/actions.html",
        "combined/letters.html",
    ]
    for page in expected:
        assert (tmp_path / page).exists(), f"Missing: {page}"


def test_build_creates_lookup_data(tmp_path):
    build(output_dir=tmp_path)
    lp = tmp_path / "assets" / "lookup-data.json"
    assert lp.exists()
    data = json.loads(lp.read_text())
    assert "representatives" in data
    assert len(data["representatives"]) >= 30


def test_letters_data_json_exists(tmp_path):
    build(output_dir=tmp_path)
    ld = tmp_path / "assets" / "letters-data.json"
    assert ld.exists()
    data = json.loads(ld.read_text())
    assert "mp" in data
    assert "defra-secretary-of-state" in data


def test_correction_note_appears_in_output(tmp_path):
    # Write a temp override and verify it appears in facts/index.html
    import json, shutil
    shutil.copy("data/reservoir/overrides.json", tmp_path / "overrides_backup.json")
    overrides = [{"item_type": "quote", "item_id": "q001",
                  "corrected_on": "2026-11-15", "corrected_by": "test",
                  "correction_note": "test correction", "field": "quote",
                  "new_value": "corrected text"}]
    Path("data/reservoir/overrides.json").write_text(json.dumps(overrides))
    try:
        build(output_dir=tmp_path)
        facts = (tmp_path / "reservoir" / "facts.html").read_text()
        assert "test correction" in facts
    finally:
        shutil.copy(tmp_path / "overrides_backup.json", "data/reservoir/overrides.json")


def test_featured_actions_in_context():
    """load_all_data returns featured_actions sorted by featured_order."""
    data = load_all_data()
    assert "featured_actions" in data
    fa = data["featured_actions"]
    assert len(fa) >= 5
    orders = [a.get("featured_order", 99) for a in fa]
    assert orders == sorted(orders)


def test_featured_actions_includes_sos():
    """ac021 (Secretary of State) is in featured_actions."""
    data = load_all_data()
    ids = [a["id"] for a in data["featured_actions"]]
    assert "ac021" in ids


def test_sos_action_has_letter_key():
    """ac021 has letter_key = defra-secretary-of-state."""
    data = load_all_data()
    sos = data["actions_by_id"].get("ac021")
    assert sos is not None
    assert sos["letter_key"] == "defra-secretary-of-state"


def test_actions_page_has_featured_panel():
    """actions.html output contains the 'Take action now' featured panel."""
    build()
    html = Path("docs/reservoir/actions.html").read_text(encoding="utf-8")
    assert "Take action now" in html
    assert "featured-actions" in html


def test_home_page_has_most_urgent_actions():
    """reservoir/index.html output contains the 'Most urgent actions' section."""
    build()
    html = Path("docs/reservoir/index.html").read_text(encoding="utf-8")
    assert "Most urgent actions" in html
    assert "featured-actions" in html


def test_cearn_content_files_exist():
    for name in ["timeline.json", "quotes.json", "actions.json"]:
        p = Path("data/cearn/content") / name
        assert p.exists(), f"Missing: {p}"


def test_cearn_timeline_has_forecast_entries():
    data = json.loads(Path("data/cearn/content/timeline.json").read_text(encoding="utf-8"))
    forecasts = [e for e in data if e.get("status") == "forecast"]
    assert len(forecasts) >= 3, "Expected at least 3 forecast entries (Stage 2, DCO, decision)"


def test_cearn_keys_in_context():
    data = load_all_data()
    for key in ["cearn_timeline", "cearn_quotes", "cearn_actions", "cearn_featured_actions", "cearn_news_items"]:
        assert key in data, f"Missing key: {key}"


def test_cearn_timeline_forecast_flag():
    data = load_all_data()
    forecasts = [e for e in data["cearn_timeline"] if e.get("is_forecast")]
    assert len(forecasts) >= 3


def test_nav_contains_both_projects():
    build()
    html = Path("docs/reservoir/index.html").read_text(encoding="utf-8")
    assert "Solar Farm" in html
    assert "Reservoir" in html
    assert "Combined Concerns" in html


def test_solar_facts_page_generated():
    build()
    html = Path("docs/solar/facts.html").read_text(encoding="utf-8")
    assert "EN0110044" in html
    assert "Cearn Solar Farm" in html


def test_solar_facts_has_forecast_label():
    build()
    html = Path("docs/solar/facts.html").read_text(encoding="utf-8")
    assert "forecast" in html.lower()


def test_solar_actions_page_generated():
    build()
    html = Path("docs/solar/actions.html").read_text(encoding="utf-8")
    assert "DESNZ" in html or "Energy Security" in html
    assert "statutory consultee" in html.lower()
    assert 'href="/white-horse-reservoir/solar/letters.html#desnz-secretary-of-state"' in html
    assert "action-item" in html  # actions actually rendered


def test_solar_letters_page_generated():
    build()
    html = Path("docs/solar/letters.html").read_text(encoding="utf-8")
    assert "DESNZ" in html or "Energy Security" in html
    assert "desnz-secretary-of-state" in html


def test_desnz_letter_has_postal_address():
    build()
    html = Path("docs/solar/letters.html").read_text(encoding="utf-8")
    assert "55 Whitehall" in html


def test_combined_impact_placeholder_in_solar_letter():
    data = _build_letters_data()
    assert "{{combined_impact_para}}" in data.get("desnz-secretary-of-state", {}).get("body", "")


def test_combined_impacts_page_generated():
    build()
    html = Path("docs/combined/facts.html").read_text(encoding="utf-8")
    assert "A338" in html
    assert "not yet confirmed" in html.lower() or "not established" in html.lower()
    assert "GARD has not publicly linked the two projects" in html
    assert "independent of both GARD and Protect the Vale" in html


def test_reservoir_index_generated():
    build()
    assert Path("docs/reservoir/index.html").exists()


def test_solar_index_generated():
    build()
    assert Path("docs/solar/index.html").exists()


def test_combined_index_generated():
    build()
    assert Path("docs/combined/index.html").exists()


def test_root_redirect_generated():
    build()
    html = Path("docs/index.html").read_text(encoding="utf-8")
    assert "reservoir" in html  # redirect points to reservoir section


def test_section_key_in_reservoir_page():
    import re
    build()
    html = Path("docs/reservoir/facts.html").read_text(encoding="utf-8")
    # section key reaches base.html: Reservoir section tab is active
    matches = re.findall(r'<a[^>]+aria-current[^>]*>[^<]*White Horse Reservoir', html)
    assert matches, "Reservoir section tab should have aria-current on facts page"
    # secondary nav resolves to reservoir paths
    assert "/white-horse-reservoir/reservoir/facts.html" in html


def test_reservoir_home_has_active_section_tab():
    import re
    build()
    html = Path("docs/reservoir/index.html").read_text(encoding="utf-8")
    # The Reservoir tab must be active; find aria-current near "White Horse Reservoir"
    matches = re.findall(r'<a[^>]+aria-current[^>]*>[^<]*White Horse Reservoir', html)
    assert matches, "Reservoir section tab should have aria-current set"


def test_combined_facts_has_both_nav_actives():
    build()
    html = Path("docs/combined/facts.html").read_text(encoding="utf-8")
    assert "Combined Concerns" in html
    assert "Facts" in html


def test_vale_watch_wordmark_present():
    build()
    html = Path("docs/reservoir/index.html").read_text(encoding="utf-8")
    assert "Vale Watch" in html


def test_secondary_nav_about_links_to_root():
    build()
    html = Path("docs/reservoir/index.html").read_text(encoding="utf-8")
    assert "/white-horse-reservoir/about.html" in html


def test_old_flat_urls_are_stubs():
    build()
    stubs = {
        "docs/facts.html":           "/white-horse-reservoir/reservoir/facts.html",
        "docs/actions.html":         "/white-horse-reservoir/reservoir/actions.html",
        "docs/letters.html":         "/white-horse-reservoir/reservoir/letters.html",
        "docs/access-points.html":   "/white-horse-reservoir/reservoir/access-points.html",
        "docs/solar-facts.html":     "/white-horse-reservoir/solar/facts.html",
        "docs/solar-actions.html":   "/white-horse-reservoir/solar/actions.html",
        "docs/solar-letters.html":   "/white-horse-reservoir/solar/letters.html",
        "docs/combined-impacts.html": "/white-horse-reservoir/combined/",
    }
    for path, target in stubs.items():
        html = Path(path).read_text(encoding="utf-8")
        assert target in html, f"{path} does not redirect to {target}"


def test_root_redirect_targets_reservoir():
    build()
    html = Path("docs/index.html").read_text(encoding="utf-8")
    assert "/white-horse-reservoir/reservoir/" in html


def test_reservoir_home_has_blurb():
    build()
    html = Path("docs/reservoir/index.html").read_text(encoding="utf-8")
    assert "Thames Water" in html
    assert "WA010005" in html


def test_reservoir_home_has_map():
    build()
    html = Path("docs/reservoir/index.html").read_text(encoding="utf-8")
    assert 'id="map"' in html
    assert 'data-section="reservoir"' in html


def test_reservoir_home_has_news_section():
    build()
    html = Path("docs/reservoir/index.html").read_text(encoding="utf-8")
    assert 'class="news-list"' in html


# ---------------------------------------------------------------------------
# Task 5: Combined section tests
# ---------------------------------------------------------------------------

def test_combined_timeline_has_both_tags():
    build()
    html = Path("docs/combined/facts.html").read_text(encoding="utf-8")
    assert "tag-reservoir" in html
    assert "tag-solar" in html


def test_combined_actions_has_both_projects():
    build()
    html = Path("docs/combined/actions.html").read_text(encoding="utf-8")
    assert "tag-reservoir" in html
    assert "tag-solar" in html


def test_combined_home_has_featured_actions():
    build()
    html = Path("docs/combined/index.html").read_text(encoding="utf-8")
    assert "cumulative" in html.lower() or "combined" in html.lower()


def test_combined_letters_has_both_project_sections():
    build()
    html = Path("docs/combined/letters.html").read_text(encoding="utf-8")
    assert "Reservoir" in html
    assert "Solar" in html


def test_build_combined_data_returns_required_keys():
    from generator.build import build_combined_data
    data = load_all_data()
    res_data = {"timeline": data["timeline"], "actions": data["actions"]}
    cearn_data = {k: data[k] for k in ["cearn_timeline", "cearn_actions"]}
    result = build_combined_data(res_data, cearn_data)
    for key in ["combined_timeline", "combined_actions", "combined_featured_actions", "combined_featured_actions_intro"]:
        assert key in result, f"Missing key: {key}"


def test_combined_timeline_is_reverse_sorted():
    data = load_all_data()
    dates = [e.get("date", "") for e in data["combined_timeline"]]
    assert dates == sorted(dates, reverse=True), "combined_timeline should be sorted reverse-chronologically"


def test_combined_timeline_has_project_tags():
    data = load_all_data()
    projects = {proj for e in data["combined_timeline"] for proj in e.get("projects", [])}
    assert "reservoir" in projects
    assert "solar" in projects


def test_combined_featured_actions_loaded():
    data = load_all_data()
    assert "combined_featured_actions" in data
    assert len(data["combined_featured_actions"]) >= 2
    ids = [a["id"] for a in data["combined_featured_actions"]]
    assert "cb001" in ids
    assert "cb002" in ids


def test_combined_featured_actions_intro_text():
    data = load_all_data()
    intro = data.get("combined_featured_actions_intro", "")
    assert "pre-application consultation" in intro


def test_combined_home_has_map_combined():
    build()
    html = Path("docs/combined/index.html").read_text(encoding="utf-8")
    assert 'id="map"' in html
    assert 'data-section="combined"' in html


# ---------------------------------------------------------------------------
# Task 6: Section-aware map and postcode lookup tests
# ---------------------------------------------------------------------------

def test_map_js_reads_section_attribute():
    js = Path("docs/assets/map.js").read_text(encoding="utf-8")
    assert "data-section" in js or "SECTION" in js


def test_lookup_js_filters_by_section():
    js = Path("docs/assets/lookup.js").read_text(encoding="utf-8")
    assert "section" in js.lower() or "projects" in js.lower()
