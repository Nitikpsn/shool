from typing import Any

CATEGORY_METRICS = [
    "general", "obc", "obc_cl", "obc_ncl", "sc", "st",
    "muslim", "christian", "sikh", "buddhist", "parsi", "jain",
    "minority_total", "cwsn", "rte", "sgc",
]

OBC_COMBINED = ["obc", "obc_cl", "obc_ncl"]


def _safe_int(v: Any) -> int:
    try:
        return int(v)
    except (ValueError, TypeError):
        return 0


def compare_categories(
    school_data: dict[str, Any],
    govt_data: dict[str, Any],
) -> dict[str, Any]:
    school_agg = school_data.get("aggregated", {})
    govt_agg = govt_data.get("aggregated", {})

    school_sec = school_data.get("section_aggregated", {})
    govt_sec = govt_data.get("section_aggregated", {})

    # Summary from class-level aggregates
    school_total = sum(_safe_int(d.get("total", 0)) for d in school_agg.values())
    govt_total = sum(_safe_int(d.get("total", 0)) for d in govt_agg.values())

    # Discrepancies at class+section level
    all_section_keys = sorted(set(school_sec.keys()) | set(govt_sec.keys()),
                              key=lambda x: (_safe_int(x.split("-")[0]) if x.split("-")[0].lstrip("-").isdigit() else 999, x))

    discrepancies = []
    for class_id in all_section_keys:
        s = school_sec.get(class_id, {})
        g = govt_sec.get(class_id, {})

        metrics = {}

        s_total = _safe_int(s.get("total", 0))
        g_total = _safe_int(g.get("total", 0))
        metrics["students"] = {
            "from": s_total,
            "to": g_total,
            "delta": g_total - s_total,
        }

        for cat in CATEGORY_METRICS:
            sv = _safe_int(s.get(cat, 0))
            gv = _safe_int(g.get(cat, 0))
            if sv != 0 or gv != 0:
                metrics[cat] = {
                    "from": sv,
                    "to": gv,
                    "delta": gv - sv,
                }

        discrepancies.append({
            "class_id": class_id,
            "metrics": metrics,
        })

    return {
        "summary": {
            "school_total": school_total,
            "portal_total": govt_total,
            "net_difference": govt_total - school_total,
        },
        "discrepancies": discrepancies,
    }
