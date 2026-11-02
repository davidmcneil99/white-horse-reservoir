"""Tests for docs/assets/lookup-data.json completeness.

Note: letter_recipients.mp intentionally contains {{mp_name}} and
{{mp_email}} as client-side JS placeholders, so the unfilled-placeholder
check covers only representatives, parishes, and access_points.
"""
import csv
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


def test_reservoir_reps_have_projects_field():
    with open("data/reservoir/representatives.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert "projects" in reader.fieldnames, "projects column missing from representatives.csv"


def test_shared_reps_tagged_both_projects():
    shared_names = {"Bethia Thomas", "Charlie Maynard", "Hannah Griffin", "James Plumb",
                    "Jenny Hannaby", "Jill Rayner", "Layla Moran", "Lee Evans",
                    "Olly Glover", "Robert Clegg", "Ron Batstone",
                    "Sally Whiteman (nee Povolotsky)"}
    with open("data/reservoir/representatives.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    # For each shared name, at least one row must be tagged "reservoir,cearn"
    tagged = {r["name"].strip() for r in rows if "cearn" in r.get("projects", "")}
    for name in shared_names:
        assert name in tagged, f"{name} not tagged with both projects"
