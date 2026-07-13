import os
import re
import pandas as pd
import numpy as np
from collections import defaultdict
from typing import Any
from utils.normalize import (
    CATEGORY_ALIASES,
    resolve_alias,
    normalize_class_label,
    CLASS_ORDER,
)

GENDER_SUFFIX_PATTERNS: list[tuple[str, list[str]]] = [
    ("boys", ["(b)", "(ब)", "boys", "boy"]),
    ("girls", ["(g)", "(ल)", "girls", "girl"]),
]

CATEGORY_CANONICAL = sorted(
    {k for k in CATEGORY_ALIASES if k not in ("boys", "girls", "total")}
)

CATEGORY_COMPARE_FIELDS = [
    "general", "obc", "obc_cl", "obc_ncl", "sc", "st",
    "muslim", "christian", "sikh", "buddhist", "parsi", "jain",
    "minority_total", "cwsn", "rte", "sgc",
]


def read_file(filepath: str) -> pd.DataFrame:
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".csv":
        return pd.read_csv(filepath, dtype=str)
    return pd.read_excel(filepath, dtype=str)


def _parse_gender_suffix(col: str) -> tuple[str | None, str | None]:
    lower = re.sub(r"[\s\-_]+", " ", col.strip().lower())
    for gender, suffixes in GENDER_SUFFIX_PATTERNS:
        for sfx in suffixes:
            sfx_clean = re.sub(r"[\s\-_]+", " ", sfx.lower())
            if sfx_clean not in lower:
                continue
            base = lower.replace(sfx_clean, "").strip()
            base = re.sub(r"[\s\-_]+", " ", base).strip()
            base = re.sub(r"[\(\)]", "", base).strip()
            if not base:
                continue
            cat = _exact_category_match(base)
            if cat:
                return cat, gender
    return None, None


def _exact_category_match(label: str) -> str | None:
    clean = label.strip().lower()
    if not clean:
        return None
    from utils.normalize import CATEGORY_ALIASES
    for canonical, aliases in CATEGORY_ALIASES.items():
        if clean == canonical.lower():
            return canonical
        for alias in aliases:
            if clean == alias.lower():
                return canonical
    return None


def resolve_columns(df: pd.DataFrame) -> dict[str, str]:
    category_counters: dict[str, int] = defaultdict(int)
    col_map: dict[str, str] = {}
    gender_split_cols: dict[str, list[tuple[str, str, str]]] = defaultdict(list)

    for raw_col in df.columns:
        col_str = str(raw_col)
        cat, gender = _parse_gender_suffix(col_str)
        if cat:
            gender_split_cols[(cat, gender)].append((raw_col, cat, gender))
            continue
        cat, _ = resolve_alias(col_str)
        if cat == "class":
            pass
        if cat == "total":
            pass
        if cat:
            category_counters[cat] += 1
            col_map[raw_col] = cat
            continue
        if "class" in col_str.lower():
            col_map[raw_col] = "class"
            continue

    for (cat, gender), cols in gender_split_cols.items():
        if len(cols) == 1:
            col_map[cols[0][0]] = f"{cat}_{gender}"
        else:
            for raw, c, g in cols:
                category_counters[c] += 1
                col_map[raw] = f"{c}_{g}"

    return col_map


SUBTOTAL_KEYWORDS = ["योग", "कुल", "subtotal", "total", "grand total", "संख्या"]


def _is_subtotal_row(row: pd.Series, class_col: str | None) -> bool:
    for col_val in row.values:
        val = str(col_val).strip().lower()
        if any(kw in val for kw in SUBTOTAL_KEYWORDS):
            return True
    return False


def _get_class_value(row: pd.Series, class_col: str | None) -> int | str | None:
    if class_col is None:
        return None
    val = str(row[class_col]).strip()
    if not val:
        return None
    nv = str(row[class_col]).strip().lower()
    if any(kw in nv for kw in SUBTOTAL_KEYWORDS):
        return None
    return normalize_class_label(val)


def _parse_numeric(val: Any) -> int:
    try:
        return int(float(str(val)))
    except (ValueError, TypeError):
        return 0


def aggregate_by_class(
    df: pd.DataFrame, col_map: dict[str, str]
) -> dict[int | str, dict[str, int]]:
    class_col = None
    for raw, mapped in col_map.items():
        if mapped == "class":
            class_col = raw
            break

    aggregated: dict[int | str, dict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    subtotal_values: dict[int | str, dict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    has_subtotal_rows = False

    for _, row in df.iterrows():
        if _is_subtotal_row(row, class_col):
            has_subtotal_rows = True
            cls_val = None
            for raw, mapped in col_map.items():
                if mapped == "class":
                    cls_val_raw = str(row[raw]).strip().lower()
                    if any(kw in cls_val_raw for kw in ["कुल", "grand total", "संख्या"]):
                        continue
                    cls_val = normalize_class_label(str(row[raw]).strip())
                elif mapped not in ("class", "total", "boys", "girls"):
                    if mapped.endswith("_boys") or mapped.endswith("_girls"):
                        base = mapped.rsplit("_", 1)[0]
                        subtotal_values[cls_val][base] += _parse_numeric(row[raw])
                    else:
                        subtotal_values[cls_val][mapped] += _parse_numeric(row[raw])
            continue

        cls_val = _get_class_value(row, class_col)
        if cls_val is None:
            continue

        for raw, mapped in col_map.items():
            if mapped == "class":
                continue
            if mapped in ("boys", "girls", "total"):
                continue
            if mapped.endswith("_boys"):
                base = mapped.rsplit("_", 1)[0]
                aggregated[cls_val][base] += _parse_numeric(row[raw])
            elif mapped.endswith("_girls"):
                base = mapped.rsplit("_", 1)[0]
                aggregated[cls_val][base] += _parse_numeric(row[raw])
            else:
                aggregated[cls_val][mapped] += _parse_numeric(row[raw])

    result = {}
    all_classes = set(aggregated.keys()) | set(subtotal_values.keys())
    for cls in all_classes:
        merged = defaultdict(int, aggregated.get(cls, {}))
        if has_subtotal_rows and cls in subtotal_values:
            for k, v in subtotal_values[cls].items():
                merged[k] = max(merged[k], v)
        result[cls] = dict(merged)

    return result


def has_gender_split(df: pd.DataFrame, col_map: dict[str, str]) -> bool:
    for mapped in col_map.values():
        if mapped.endswith("_boys") or mapped.endswith("_girls"):
            return True
    return False


def get_gender_totals(
    df: pd.DataFrame, col_map: dict[str, str], aggregated: dict
) -> dict[int | str, dict[str, int]]:
    boys_col = next((r for r, m in col_map.items() if m == "boys"), None)
    girls_col = next((r for r, m in col_map.items() if m == "girls"), None)
    total_col = next((r for r, m in col_map.items() if m == "total"), None)

    if boys_col or girls_col:
        result = {}
        for cls_val in aggregated:
            b = 0
            g = 0
        return result

    result = {}
    for cls_val in aggregated:
        b = 0
        g = 0
        if boys_col:
            pass
        if girls_col:
            pass
        result[cls_val] = {"boys": b, "girls": g}
    return result


def internal_consistency_check(
    aggregated: dict[int | str, dict[str, int]],
    file_label: str,
) -> list[dict]:
    checks: list[dict] = []
    for cls, cats in aggregated.items():
        category_sum = sum(cats.get(c, 0) for c in CATEGORY_COMPARE_FIELDS)
        students_total = cats.get("total", 0)
        if students_total > 0 and category_sum != students_total:
            gap = students_total - category_sum
            checks.append({
                "file": file_label,
                "class": cls,
                "category_sum": category_sum,
                "students_total": students_total,
                "gap": gap,
                "severity": "warning" if abs(gap) / students_total < 0.1 else "error",
            })
    return checks


def parse_category_file(
    filepath: str, file_label: str
) -> dict[str, Any]:
    df = read_file(filepath)
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    col_map = resolve_columns(df)

    class_col = next((r for r, m in col_map.items() if m == "class"), None)
    if class_col is None:
        for c in df.columns:
            if "class" in str(c).strip().lower():
                col_map[c] = "class"
                class_col = c
                break

    aggregated = aggregate_by_class(df, col_map)

    has_subtotal = False
    for _, row in df.iterrows():
        if _is_subtotal_row(row, class_col):
            has_subtotal = True
            break

    checks = internal_consistency_check(aggregated, file_label)

    gender_split = has_gender_split(df, col_map)

    return {
        "file_label": file_label,
        "aggregated": {str(k): v for k, v in aggregated.items()},
        "col_map": col_map,
        "has_subtotal_rows": has_subtotal,
        "has_gender_split": gender_split,
        "consistency_checks": checks,
        "total_classes": len(aggregated),
    }
