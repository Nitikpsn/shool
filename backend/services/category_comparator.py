from typing import Any
from collections import defaultdict

CATEGORY_COMPARE_FIELDS = [
    "general", "obc", "obc_cl", "obc_ncl", "sc", "st",
    "muslim", "christian", "sikh", "buddhist", "parsi", "jain",
    "minority_total", "cwsn", "rte", "sgc",
]

OBC_COMBINED_FIELDS = ["obc", "obc_cl", "obc_ncl"]


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

    all_classes = sorted(set(school_agg.keys()) | set(govt_agg.keys()),
                         key=lambda x: (_safe_int(x) if str(x).lstrip("-").isdigit() else 999, str(x)))

    class_diffs = []
    total_school = 0
    total_govt = 0
    total_delta_abs = 0
    reclassification_count = 0
    headcount_diff_count = 0

    for cls in all_classes:
        s_cats = school_agg.get(cls, {})
        g_cats = govt_agg.get(cls, {})

        deltas = {}
        abs_sum = 0
        for cat in CATEGORY_COMPARE_FIELDS:
            sv = _safe_int(s_cats.get(cat, 0))
            gv = _safe_int(g_cats.get(cat, 0))
            d = gv - sv
            deltas[cat] = d
            abs_sum += abs(d)

        s_total = _safe_int(s_cats.get("total",
                            sum(_safe_int(s_cats.get(c, 0)) for c in CATEGORY_COMPARE_FIELDS)))
        g_total = _safe_int(g_cats.get("total",
                            sum(_safe_int(g_cats.get(c, 0)) for c in CATEGORY_COMPARE_FIELDS)))
        students_delta = g_total - s_total
        total_school += s_total
        total_govt += g_total
        total_delta_abs += abs(students_delta)

        net_delta = sum(deltas.values())

        is_reclassification = False
        reclassification_score = 0.0
        if abs_sum > 0 and abs(net_delta) / abs_sum < 0.3:
            is_reclassification = True
            reclassification_score = 1.0 - (abs(net_delta) / abs_sum)
            reclassification_count += 1

        positive_deltas = {c: d for c, d in deltas.items() if d > 0}
        negative_deltas = {c: d for c, d in deltas.items() if d < 0}

        if students_delta != 0:
            headcount_diff_count += 1

        class_diff = {
            "class": cls,
            "deltas": deltas,
            "net_delta": net_delta,
            "abs_delta_sum": abs_sum,
            "students_delta": students_delta,
            "is_reclassification": is_reclassification,
            "reclassification_score": round(reclassification_score, 4),
            "school_totals": {c: _safe_int(s_cats.get(c, 0)) for c in CATEGORY_COMPARE_FIELDS},
            "govt_totals": {c: _safe_int(g_cats.get(c, 0)) for c in CATEGORY_COMPARE_FIELDS},
            "school_total_students": s_total,
            "govt_total_students": g_total,
            "positive_deltas": positive_deltas,
            "negative_deltas": negative_deltas,
        }
        class_diffs.append(class_diff)

    total_delta_net = total_govt - total_school

    flags = []
    if reclassification_count > 0:
        flags.append({
            "type": "reclassification_detected",
            "message": (
                f"{reclassification_count} class(es) have category shifts "
                f"where students were recorded under different categories "
                f"between school and portal, rather than new/missing enrollments."
            ),
            "classes": [
                cd["class"] for cd in class_diffs if cd["is_reclassification"]
            ],
        })

    return {
        "class_diffs": class_diffs,
        "summary": {
            "total_classes": len(all_classes),
            "total_reclassifications": reclassification_count,
            "total_headcount_diffs": headcount_diff_count,
            "total_students_school": total_school,
            "total_students_govt": total_govt,
            "total_delta_net": total_delta_net,
            "total_delta_abs": total_delta_abs,
        },
        "flags": flags,
        "school_meta": {
            "has_subtotal_rows": school_data.get("has_subtotal_rows", False),
            "has_gender_split": school_data.get("has_gender_split", False),
            "total_consistency_warnings": len(school_data.get("consistency_checks", [])),
            "consistency_checks": school_data.get("consistency_checks", []),
        },
        "govt_meta": {
            "has_subtotal_rows": govt_data.get("has_subtotal_rows", False),
            "has_gender_split": govt_data.get("has_gender_split", False),
            "total_consistency_warnings": len(govt_data.get("consistency_checks", [])),
            "consistency_checks": govt_data.get("consistency_checks", []),
        },
    }
