import json, pathlib


def test_boundary_parishes_file_exists():
    p = pathlib.Path("data/cearn/boundary-parishes.json")
    assert p.exists(), "boundary-parishes.json not produced by cearn_boundary.py"


def test_expected_scheme_parishes_present():
    data = json.loads(pathlib.Path("data/cearn/boundary-parishes.json").read_text(encoding="utf-8"))
    scheme = [p.lower() for p in data.get("scheme_parishes", [])]
    for expected in ["garford", "charney bassett", "west hanney", "goosey", "baulking"]:
        assert any(expected in p for p in scheme), f"Expected parish missing: {expected}"


def test_source_and_date_present():
    data = json.loads(pathlib.Path("data/cearn/boundary-parishes.json").read_text(encoding="utf-8"))
    assert data.get("source"), "source field missing"
    assert data.get("checked_date"), "checked_date field missing"
