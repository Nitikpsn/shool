from typing import Any, Optional
from utils.fuzzy_match import multi_field_score, is_fuzzy_match

# Fields that should be skipped during field-by-field comparison
COMPARE_SKIP_FIELDS = {
    "admission_no", "admission_no_raw", "source_sheet",
    "extra_fields", "difference_type", "ai_insight",
}


def _compare_fields(school: dict, portal: dict, fields: list[str], threshold: float = 0.85) -> list[dict]:
    """Compare two records field by field, returning only the fields that differ."""
    diffs = []
    for field in fields:
        if field in COMPARE_SKIP_FIELDS:
            continue

        old_val = str(school.get(field, "")).strip()
        new_val = str(portal.get(field, "")).strip()

        # Skip if values are the same (case-insensitive) or fuzzy-matched
        if old_val.lower() == new_val.lower():
            continue
        if is_fuzzy_match(old_val, new_val, threshold):
            continue

        diffs.append({
            "field_name": field,
            "old_value": old_val,
            "new_value": new_val,
        })
    return diffs


def _get_all_compare_fields(school_records: list[dict], portal_records: list[dict]) -> list[str]:
    """Collect all field names from both record sets, minus the skip list."""
    all_fields = set()
    for r in school_records:
        all_fields.update(r.keys())
    for r in portal_records:
        all_fields.update(r.keys())
    return sorted(all_fields - COMPARE_SKIP_FIELDS)


def compare(
    school_records: list[dict[str, Any]],
    portal_records: list[dict[str, Any]],
    threshold: float = 0.75,
    ai_service: Optional[Any] = None,
    stream_callback: Optional[callable] = None,
) -> dict[str, Any]:
    """
    Compare school and portal records in 3 phases:
    
    Phase 1: Exact ID matching
      - Records with the same admission_no are directly paired
    
    Phase 2: Fuzzy matching
      - Unmatched records are scored using name + class + gender + category
      - Best pairs above the threshold are matched
    
    Phase 3: AI matching (optional)
      - Gemini AI suggests matches for still-unmatched records
    
    After matching, each pair is compared field-by-field to find modifications.
    """
    school_by_id = {r["admission_no"]: r for r in school_records}
    portal_by_id = {r["admission_no"]: r for r in portal_records}

    school_ids = set(school_by_id.keys())
    portal_ids = set(portal_by_id.keys())

    # ---- Phase 1: Exact ID matching ----
    exact_matched_ids = school_ids & portal_ids
    new_ids = set(portal_ids - school_ids)
    missing_ids = set(school_ids - portal_ids)

    total_steps = len(exact_matched_ids) + len(new_ids) + len(missing_ids)
    step = 0

    def _progress(msg: str):
        if stream_callback:
            stream_callback("progress", {
                "message": msg,
                "current": min(step, total_steps) if total_steps > 0 else 1,
                "total": total_steps,
            })

    # ---- Phase 2: Fuzzy matching ----
    _progress("Running fuzzy matching for unmatched records...")
    fuzzy_pairs: list[tuple[str, str, float]] = []

    if missing_ids and new_ids:
        fuzzy_pairs = _fuzzy_match(
            school_by_id, portal_by_id,
            missing_ids, new_ids, threshold, stream_callback
        )

    # Update unmatched sets after fuzzy matching
    new_ids -= {pid for _, pid, _ in fuzzy_pairs}
    missing_ids -= {sid for sid, _, _ in fuzzy_pairs}

    # ---- Phase 3: AI matching ----
    if ai_service and (new_ids or missing_ids):
        _progress("AI matching remaining unmatched records...")
        _ai_match(
            ai_service, school_by_id, portal_by_id,
            missing_ids, new_ids, fuzzy_pairs, stream_callback
        )

    # ---- Phase 4: Field-by-field comparison of matched records ----
    compare_fields = _get_all_compare_fields(school_records, portal_records)
    modifications, modified_ids = [], set()

    _progress("Comparing matched records...")

    # Compare exact matches
    for sid in sorted(exact_matched_ids):
        step += 1
        diffs = _compare_fields(school_by_id[sid], portal_by_id[sid], compare_fields, threshold)
        _record_modifications(modifications, modified_ids, sid, sid, school_by_id[sid], portal_by_id[sid], diffs, ai_service, stream_callback)

    # Compare fuzzy matches
    for school_id, portal_id, score in fuzzy_pairs:
        step += 1
        diffs = _compare_fields(school_by_id[school_id], portal_by_id[portal_id], compare_fields, threshold)
        _record_modifications(
            modifications, modified_ids, school_id, portal_id,
            school_by_id[school_id], portal_by_id[portal_id], diffs,
            ai_service, stream_callback, fuzzy_score=score
        )

    # ---- Build result: new and missing records ----
    new_records = [
        {**portal_by_id[pid], "difference_type": "new"}
        for pid in sorted(new_ids)
    ]
    missing_records = [
        {**school_by_id[sid], "difference_type": "missing"}
        for sid in sorted(missing_ids)
    ]

    # Notify stream of new/missing records
    if stream_callback:
        for r in new_records:
            stream_callback("new_record", r)
        for r in missing_records:
            stream_callback("missing_record", r)

    _progress("Comparison complete!")

    return {
        "matched": len(exact_matched_ids) + len(fuzzy_pairs),
        "missing": len(missing_ids),
        "modified": len(modified_ids),
        "new": len(new_ids),
        "matched_admissions": list(exact_matched_ids),
        "fuzzy_matched": [
            {"school_id": sid, "portal_id": pid, "score": round(sc, 2)}
            for sid, pid, sc in fuzzy_pairs
        ],
        "modifications": modifications,
        "new_records": new_records,
        "missing_records": missing_records,
    }


def _fuzzy_match(
    school_by_id: dict, portal_by_id: dict,
    missing_ids: set, new_ids: set,
    threshold: float, stream_callback: Optional[callable]
) -> list[tuple[str, str, float]]:
    """Pair unmatched records using multi-field fuzzy scoring."""
    missing_list = [(sid, school_by_id[sid]) for sid in sorted(missing_ids)]
    new_list = [(pid, portal_by_id[pid]) for pid in sorted(new_ids)]

    # Score all possible pairs
    scored = []
    for pid, precord in new_list:
        for sid, srecord in missing_list:
            score = multi_field_score(precord, srecord)
            if score >= threshold:
                scored.append((score, sid, pid))

    # Sort best-first and greedily assign matches
    scored.sort(key=lambda x: -x[0])
    used_school, used_portal = set(), set()
    pairs = []

    for score, sid, pid in scored:
        if sid in used_school or pid in used_portal:
            continue
        used_school.add(sid)
        used_portal.add(pid)
        pairs.append((sid, pid, score))

        if stream_callback:
            stream_callback("fuzzy_match", {
                "school_id": sid,
                "portal_id": pid,
                "school_name": school_by_id[sid]["student_name"],
                "portal_name": portal_by_id[pid]["student_name"],
                "score": round(score, 2),
            })

    return pairs


def _ai_match(
    ai_service, school_by_id, portal_by_id,
    missing_ids, new_ids, fuzzy_pairs, stream_callback
):
    """Use AI to match remaining unmatched records."""
    MAX_CANDIDATES = 20
    MAX_PORTAL_TO_CHECK = 5

    unmatched_portal = [portal_by_id[pid] for pid in sorted(new_ids)[:MAX_CANDIDATES]]
    unmatched_school = [school_by_id[sid] for sid in sorted(missing_ids)[:MAX_CANDIDATES]]

    for pu in unmatched_portal[:MAX_PORTAL_TO_CHECK]:
        suggestions = ai_service.suggest_best_match(pu, unmatched_school)
        if not suggestions:
            continue

        best = suggestions[0]
        if not isinstance(best, dict) or best.get("score", 0) < 0.7:
            continue

        idx = best.get("candidate_index", -1)
        if not (0 <= idx < len(unmatched_school)):
            continue

        matched_sid = unmatched_school[idx]["admission_no"]
        if matched_sid in missing_ids and pu["admission_no"] in new_ids:
            fuzzy_pairs.append((matched_sid, pu["admission_no"], best["score"]))
            new_ids.discard(pu["admission_no"])
            missing_ids.discard(matched_sid)

            if stream_callback:
                stream_callback("ai_match", {
                    "school_id": matched_sid,
                    "portal_id": pu["admission_no"],
                    "school_name": unmatched_school[idx]["student_name"],
                    "portal_name": pu["student_name"],
                    "reason": best.get("reason", ""),
                    "score": best.get("score", 0),
                })


def _record_modifications(
    modifications, modified_ids, school_id, portal_id,
    school_record, portal_record, diffs,
    ai_service, stream_callback, fuzzy_score=None
):
    """Record field-level modifications for a matched pair."""
    for diff in diffs:
        record = {
            "admission_no": f"{school_id}->{portal_id}" if school_id != portal_id else school_id,
            "field_name": diff["field_name"],
            "old_value": diff["old_value"],
            "new_value": diff["new_value"],
            "student_name": portal_record.get("student_name", ""),
            "difference_type": "modified",
        }
        if fuzzy_score is not None:
            record["fuzzy_score"] = round(fuzzy_score, 2)
            record["school_id"] = school_id
            record["portal_id"] = portal_id

        if ai_service:
            record["ai_insight"] = ai_service.explain_difference(
                school_record, portal_record,
                diff["field_name"], diff["old_value"], diff["new_value"]
            )
            if stream_callback:
                stream_callback("diff_analyzed", {**record, "ai_insight": record["ai_insight"]})

        modifications.append(record)
        modified_ids.add(school_id)
