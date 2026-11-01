import logging


def apply_overrides(items: list[dict], overrides: list[dict], item_type: str) -> list[dict]:
    """Apply corrections from the overrides list to matching items.

    Filters overrides to those matching item_type, then looks up each override's
    target item by id. If found, the specified field is updated and correction
    metadata is attached. If not found, a warning is logged and the override
    is skipped.

    Args:
        items: List of content dicts, each with an 'id' key.
        overrides: List of override dicts with item_type, item_id, field,
                   new_value, corrected_on, and correction_note keys.
        item_type: Only process overrides where override['item_type'] matches this.

    Returns:
        The mutated items list.
    """
    relevant = [o for o in overrides if o.get("item_type") == item_type]

    id_index = {item["id"]: item for item in items}

    for override in relevant:
        target_id = override["item_id"]
        item = id_index.get(target_id)
        if item is None:
            logging.warning(f"Override references unknown id {target_id}")
            continue
        item[override["field"]] = override["new_value"]
        item["_corrected_on"] = override["corrected_on"]
        item["_correction_note"] = override["correction_note"]

    return items
