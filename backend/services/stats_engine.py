from collections import defaultdict
from typing import Any
from utils.normalize import normalize_gender, normalize_class_label

# Map normalized category names to stat keys
CATEGORY_TO_STAT = {
    "sc": "sc", "st": "st", "obc": "obc", "ews": "ews", "gen": "gen",
}


def _count_gender(record: dict, stats: dict):
    """Increment boy/girl counter based on record's gender."""
    gender = normalize_gender(record.get("gender", "")).lower()
    if gender in ("boy", "male"):
        stats["boys"] += 1
    elif gender in ("girl", "female"):
        stats["girls"] += 1


def _count_category(record: dict, stats: dict):
    """Increment category counter (SC/ST/OBC/EWS/GEN) based on record."""
    cat = record.get("category", "").strip().lower()
    mapped = CATEGORY_TO_STAT.get(cat)

    # Fallback: try uppercase match
    if not mapped:
        cat_upper = record.get("category", "").strip().upper()
        if cat_upper.lower() in CATEGORY_TO_STAT:
            mapped = cat_upper.lower()

    if mapped and mapped in stats:
        stats[mapped] += 1


def _empty_class_stats() -> dict:
    return {"boys": 0, "girls": 0, "total": 0, "sc": 0, "obc": 0, "st": 0, "ews": 0, "gen": 0}


def compute_stats(records: list[dict[str, Any]]) -> dict[str, int]:
    """Compute overall gender and category counts for a list of records."""
    stats = {"boys": 0, "girls": 0, "sc": 0, "obc": 0, "st": 0, "ews": 0, "gen": 0, "total": len(records)}
    for r in records:
        _count_gender(r, stats)
        _count_category(r, stats)
    return stats


def class_wise_stats(records: list[dict[str, Any]]) -> dict[str, dict]:
    """Compute gender and category counts grouped by class."""
    groups = defaultdict(_empty_class_stats)

    for r in records:
        cls = str(normalize_class_label(r.get("class_name", "Unknown")))
        groups[cls]["total"] += 1
        _count_gender(r, groups[cls])
        _count_category(r, groups[cls])

    return dict(groups)


def language_wise_stats(records: list[dict[str, Any]]) -> dict[str, int]:
    """Count records by language."""
    counts = defaultdict(int)
    for r in records:
        lang = r.get("language", "Unknown") or "Unknown"
        counts[lang] += 1
    return dict(counts)
