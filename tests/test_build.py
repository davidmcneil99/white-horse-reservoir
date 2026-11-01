import json
from pathlib import Path
from generator.build import load_all_data, build


def test_timeline_is_distant_future_flag():
    """Items with year >= today().year + 3 get is_distant_future=True."""
    data = load_all_data()
    near = [t for t in data["timeline"] if t.get("date", "").startswith("202")]
    far  = [t for t in data["timeline"] if t.get("date", "").startswith("204")]
    assert all(not t["is_distant_future"] for t in near), "recent items should not be distant future"
    assert all(t["is_distant_future"] for t in far), "2040 item should be distant future"


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
    html = Path("docs/actions/index.html").read_text(encoding="utf-8")
    # ac006 has letter_key = "thames-water"
    assert "thames-water" in html
    assert "Generate letter" in html


def test_actions_page_has_deadlines():
    """actions.html output shows deadline for actions that have one."""
    build()
    html = Path("docs/actions/index.html").read_text(encoding="utf-8")
    assert "2026-11-30" in html or "November 2026" in html or "30 November" in html


def test_letters_page_has_template_note():
    """letters.html output contains the template note."""
    build()
    html = Path("docs/letters/index.html").read_text(encoding="utf-8")
    assert "template" in html.lower() and "adjust" in html.lower()


def test_facts_page_has_details_element():
    """facts.html output contains a <details> element for distant-future items."""
    build()
    facts_html = Path("docs/facts/index.html").read_text(encoding="utf-8")
    assert "<details" in facts_html
    assert "2040" in facts_html  # distant-future item appears somewhere


def test_facts_page_action_links():
    """facts.html output contains links to actions for timeline items with action_ids."""
    build()
    facts_html = Path("docs/facts/index.html").read_text(encoding="utf-8")
    # t024 has action_ids linking to ac019 and ac012
    assert 'href="../actions/#action-ac019"' in facts_html or \
           'href="/actions/#action-ac019"' in facts_html or \
           '#action-ac019' in facts_html


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
        "about/index.html",
        "facts/index.html",
        "actions/index.html",
        "letters/index.html",
        "corrections/index.html",
        "access-points/index.html",
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
    shutil.copy("data/overrides.json", tmp_path / "overrides_backup.json")
    overrides = [{"item_type": "quote", "item_id": "q001",
                  "corrected_on": "2026-11-15", "corrected_by": "test",
                  "correction_note": "test correction", "field": "quote",
                  "new_value": "corrected text"}]
    Path("data/overrides.json").write_text(json.dumps(overrides))
    try:
        build(output_dir=tmp_path)
        facts = (tmp_path / "facts" / "index.html").read_text()
        assert "test correction" in facts
    finally:
        shutil.copy(tmp_path / "overrides_backup.json", "data/overrides.json")
