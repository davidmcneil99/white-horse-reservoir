"""Tests for docs/assets/lookup-data.json completeness.

Note: letter_recipients.mp intentionally contains {{mp_name}} and
{{mp_email}} as client-side JS placeholders, so the unfilled-placeholder
check covers only representatives, parishes, and access_points.
"""
import json
from pathlib import Path


def test_lookup_data_has_all_tiers():
    data = json.loads(Path("docs/assets/lookup-data.json").read_text())
    tiers = {r["tier"] for r in data["representatives"]}
    assert "MP" in tiers
    assert "County" in tiers
    assert "District" in tiers


def test_lookup_data_mp_has_email():
    data = json.loads(Path("docs/assets/lookup-data.json").read_text())
    mps = [r for r in data["representatives"] if r["tier"] == "MP"]
    assert len(mps) == 3
    assert all(r["email"] for r in mps)


def test_lookup_data_access_points_complete():
    data = json.loads(Path("docs/assets/lookup-data.json").read_text())
    assert len(data["access_points"]) == 17  # A1-A17, A20 (A18/A19 dropped)


def test_lookup_data_no_unfilled_placeholder():
    # letter_recipients.mp intentionally contains {{mp_name}} / {{mp_email}}
    # for client-side substitution -- exclude that section from this check.
    data = json.loads(Path("docs/assets/lookup-data.json").read_text())
    for section in ("representatives", "parishes", "access_points"):
        assert "{{" not in json.dumps(data[section]), (
            f"Unfilled placeholder in {section}"
        )
