from pathlib import Path


def test_map_js_references_both_projects():
    js = Path("docs/assets/map.js").read_text(encoding="utf-8")
    assert "WA010005" in js
    assert "EN0110044" in js
