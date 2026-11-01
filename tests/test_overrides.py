from generator.overrides import apply_overrides
from generator.utils import format_date, truncate

def test_apply_overrides_replaces_field():
    items = [{"id": "q001", "quote": "old text"}]
    overrides = [{"item_type": "quote", "item_id": "q001",
                  "corrected_on": "2026-11-15", "corrected_by": "David McNeil",
                  "correction_note": "Source updated",
                  "field": "quote", "new_value": "new text"}]
    result = apply_overrides(items, overrides, "quote")
    assert result[0]["quote"] == "new text"
    assert result[0]["_corrected_on"] == "2026-11-15"
    assert result[0]["_correction_note"] == "Source updated"

def test_apply_overrides_does_not_mutate_originals():
    items = [{"id": "q001", "quote": "original"}]
    overrides = [{"item_type": "quote", "item_id": "q001",
                  "corrected_on": "2026-11-01", "correction_note": "fix",
                  "field": "quote", "new_value": "changed"}]
    apply_overrides(items, overrides, "quote")
    assert items[0]["quote"] == "original"

def test_apply_overrides_unknown_id_logs_and_skips(caplog):
    items = [{"id": "q001", "quote": "text"}]
    overrides = [{"item_type": "quote", "item_id": "q999",
                  "correction_note": "x", "corrected_on": "2026-11-01",
                  "field": "quote", "new_value": "y"}]
    result = apply_overrides(items, overrides, "quote")
    assert result[0]["quote"] == "text"
    assert "q999" in caplog.text

def test_format_date_year():
    assert format_date("2006", "year") == "2006"

def test_format_date_month_from_full_date():
    # Month-precision dates are stored as YYYY-MM-01 in our data.
    assert format_date("2025-11-01", "month") == "November 2025"

def test_format_date_month_from_partial_date():
    # Fallback: YYYY-MM format also accepted.
    assert format_date("2025-11", "month") == "November 2025"

def test_format_date_day():
    assert format_date("2026-11-01", "day") == "1 November 2026"

def test_format_date_invalid_returns_original(caplog):
    result = format_date("not-a-date", "day")
    assert result == "not-a-date"
    assert "not-a-date" in caplog.text

def test_truncate():
    assert truncate("hello world", 5) == "hello..."
    assert truncate("hi", 10) == "hi"
