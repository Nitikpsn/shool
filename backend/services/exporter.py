import pandas as pd
from typing import Any
from services.stats_engine import class_wise_stats, language_wise_stats, compute_stats


def build_report_data(portal_records: list[dict], comparison: dict) -> dict[str, Any]:
    """Assemble all report data: stats, comparison results, and breakdowns."""
    portal_stats = compute_stats(portal_records)

    return {
        "summary": {
            "total_school": comparison.get("matched", 0) + comparison.get("missing", 0),
            "total_portal": comparison.get("matched", 0) + comparison.get("new", 0),
            "matched": comparison.get("matched", 0),
            "missing": comparison.get("missing", 0),
            "modified": comparison.get("modified", 0),
            "new": comparison.get("new", 0),
            "fuzzy_matched": len(comparison.get("fuzzy_matched", [])),
        },
        "class_wise": class_wise_stats(portal_records),
        "category_wise": {
            "SC": portal_stats.get("sc", 0),
            "ST": portal_stats.get("st", 0),
            "OBC": portal_stats.get("obc", 0),
            "EWS": portal_stats.get("ews", 0),
            "GEN": portal_stats.get("gen", 0),
        },
        "gender_wise": {
            "Boys": portal_stats.get("boys", 0),
            "Girls": portal_stats.get("girls", 0),
        },
        "language_wise": language_wise_stats(portal_records),
        "missing_records": comparison.get("missing_records", []),
        "new_records": comparison.get("new_records", []),
        "mismatch_report": comparison.get("modifications", []),
        "fuzzy_matched": comparison.get("fuzzy_matched", []),
    }


def export_report_to_excel(report_data: dict[str, Any], output_path: str):
    """Write report data to a multi-sheet Excel file."""
    writer = pd.ExcelWriter(output_path, engine="openpyxl")

    sheets = [
        ("Summary", lambda: pd.DataFrame(list(report_data["summary"].items()), columns=["Metric", "Count"])),
        ("Class Wise", lambda: _build_class_sheet(report_data)),
        ("Category Wise", lambda: pd.DataFrame(list(report_data["category_wise"].items()), columns=["Category", "Count"])),
        ("Gender Wise", lambda: pd.DataFrame(list(report_data["gender_wise"].items()), columns=["Gender", "Count"])),
        ("Language Wise", lambda: pd.DataFrame(list(report_data["language_wise"].items()), columns=["Language", "Count"])),
        ("Missing Records", lambda: _build_record_sheet(report_data, "missing_records")),
        ("New Records", lambda: _build_record_sheet(report_data, "new_records")),
        ("Mismatch Report", lambda: _build_record_sheet(report_data, "mismatch_report")),
        ("Fuzzy Matched", lambda: pd.DataFrame(report_data["fuzzy_matched"])),
    ]

    for sheet_name, builder in sheets:
        df = builder()
        if df is not None and not df.empty:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    writer.close()


def _build_class_sheet(report_data: dict) -> pd.DataFrame | None:
    """Build the Class Wise sheet from class_wise stats."""
    cw = report_data.get("class_wise", {})
    if not cw:
        return None
    df = pd.DataFrame.from_dict(cw, orient="index")
    df.index.name = "Class"
    return df


def _build_record_sheet(report_data: dict, key: str) -> pd.DataFrame | None:
    """Build a sheet from a list of records, filtering out extra_fields."""
    records = report_data.get(key, [])
    if not records:
        return None
    safe = [{k: v for k, v in r.items() if k != "extra_fields"} for r in records]
    return pd.DataFrame(safe)
