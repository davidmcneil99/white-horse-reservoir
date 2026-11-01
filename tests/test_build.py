import json
from pathlib import Path
from generator.build import load_all_data, build


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
    expected = ["index.html", "about.html", "facts.html", "actions.html",
                "letters.html", "corrections.html", "access-points.html"]
    for page in expected:
        assert (tmp_path / page).exists(), f"Missing: {page}"


def test_build_creates_lookup_data(tmp_path):
    build(output_dir=tmp_path)
    lp = tmp_path / "assets" / "lookup-data.json"
    assert lp.exists()
    data = json.loads(lp.read_text())
    assert "representatives" in data
    assert len(data["representatives"]) >= 30


def test_correction_note_appears_in_output(tmp_path):
    # Write a temp override and verify it appears in facts.html
    import json, shutil
    shutil.copy("data/overrides.json", tmp_path / "overrides_backup.json")
    overrides = [{"item_type": "quote", "item_id": "q001",
                  "corrected_on": "2026-11-15", "corrected_by": "test",
                  "correction_note": "test correction", "field": "quote",
                  "new_value": "corrected text"}]
    Path("data/overrides.json").write_text(json.dumps(overrides))
    try:
        build(output_dir=tmp_path)
        facts = (tmp_path / "facts.html").read_text()
        assert "test correction" in facts
    finally:
        shutil.copy(tmp_path / "overrides_backup.json", "data/overrides.json")
