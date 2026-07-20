import os
import re
import pandas as pd
from collections import defaultdict
from typing import Any
from utils.normalize import (
    CATEGORY_ALIASES,
    resolve_alias,
    normalize_class_label,
)
from services.data_profiler import profile_dataframe, clean_grand_total_rows

# ---- Constants ----

GENDER_SUFFIXES = {
    "boys": ["(b)", "(ब)", "boys", "boy", "बालक"],
    "girls": ["(g)", "(ल)", "girls", "girl", "बालिका"],
}

CATEGORY_REGEX_PATTERNS = {
    "sc": r"(एस\.सी\.|sc|scheduled\s*caste|अनुसूचित\s*जाति)",
    "st": r"(एस\.टी\.|st|scheduled\s*tribe|अनुसूचित\s*जनजाति)",
    "obc": r"(obc|ओ\.बी\.सी\.|पिछड़ा|अन्य\s*पिछड़ा|other\s*backward)",
    "general": r"(general|सामान्य|gen|ur|unreserved)",
    "minority": r"(minority|अल्पसंख्यक|muslim|मुस्लिम|christian|क्रिश्चियन|sikh|सिख|buddhist|बौद्ध)",
    "cwsn": r"(cwsn|divyang|disabled|विकलांग|special\s*need)",
    "rte": r"(rte|आरटीई)",
    "sgc": r"(sgc|एसजीसी)",
    "boys": r"(boys|बालक|male|पुरुष|छात्र)",
    "girls": r"(girls|बालिका|female|महिला|छात्रा)",
}

CATEGORY_COMPARE_FIELDS = [
    "general", "obc", "obc_cl", "obc_ncl", "sc", "st",
    "muslim", "christian", "sikh", "buddhist", "parsi", "jain",
    "minority_total", "cwsn", "rte", "sgc",
]

PRIMARY_CATEGORY_FIELDS = ["general", "obc", "sc", "st", "cwsn", "rte", "sgc"]

CLASS_KEYWORDS = ["class", "grade", "standard", "cls", "कक्षा", "क्लास", "वर्ग"]
SECTION_KEYWORDS = ["section", "अनुभाग", "सेक्शन", "sec", "section_name", "भाग"]
SUBTOTAL_KEYWORDS = ["योग", "कुल", "subtotal", "total", "grand total", "संख्या", "sum"]
TOTAL_COL_KEYWORDS = [
    "योग", "कुल योग", "कुल", "total", "subtotal",
    "संख्या", "total students", "total student", "sum",
    "strength", "enrolled", "enrollment", "count",
]


# ---- File Reading ----

def read_file(filepath: str) -> pd.DataFrame:
    ext = os.path.splitext(filepath)[1].lower()
    return pd.read_csv(filepath, dtype=str) if ext == ".csv" else pd.read_excel(filepath, dtype=str)


# ---- Header Detection and Flattening ----

def _looks_like_header_row(row: pd.Series) -> bool:
    """Check if a row looks like column headers (labels) rather than data rows."""
    text_vals = [str(v).strip() if isinstance(v, str) else "" for v in row.values]
    text_vals = ["" if t.lower() in ("nan", "") else t for t in text_vals]
    non_empty = [t for t in text_vals if t]

    if not non_empty:
        return True
    if sum(1 for t in text_vals if not t) / len(text_vals) > 0.2:
        return True
    if sum(1 for t in non_empty if len(t) > 4) > len(non_empty) * 0.5:
        return True

    keywords = {"class", "grade", "section", "total", "name", "general", "कक्षा", "अनुभाग", "सामान्य", "योग"}
    if sum(1 for t in non_empty if any(kw in t.lower() for kw in keywords)) > len(non_empty) * 0.3:
        return True

    return False


def flatten_nested_headers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flatten multi-row merged headers into single column names.
    Example: ['एस.सी.', NaN] + [NaN, 'बालक'] -> 'एस.सी._बालक'
    """
    if len(df) < 2:
        return df

    if not _looks_like_header_row(df.iloc[0]):
        return df

    # Count how many consecutive header rows at the top
    header_rows = 0
    while header_rows < min(3, len(df)) and _looks_like_header_row(df.iloc[header_rows]):
        header_rows += 1

    if header_rows < 2:
        return df

    # Forward-fill and combine header rows into single column names
    combined = df.iloc[:header_rows].ffill(axis=0).fillna("").astype(str)
    new_columns = []
    for col_idx in range(len(df.columns)):
        parts = [combined.iloc[r, col_idx].strip().strip("_") for r in range(header_rows)]
        parts = [p for p in parts if p]
        new_columns.append("_".join(parts) if parts else "")

    df = df.iloc[header_rows:].copy().reset_index(drop=True)
    df.columns = new_columns
    return df


# ---- Column Detection Helpers ----

def _is_nan_column(col: Any) -> bool:
    if pd.isna(col):
        return True
    s = str(col).strip()
    return s.lower() == "nan" or s.startswith("Unnamed")


def _is_class_column(col_str: str) -> bool:
    return any(kw in col_str.strip().lower() for kw in CLASS_KEYWORDS)


def _detect_gender_from_text(text: str) -> str | None:
    lower = text.strip().lower()
    for gender, suffixes in GENDER_SUFFIXES.items():
        for sfx in suffixes:
            if sfx.lower() in lower:
                return gender
    return None


def _parse_gender_suffix(col: str) -> tuple[str | None, str | None]:
    """Try to extract category + gender from column names like 'SC_Boys' or 'OBC (Girls)'."""
    lower = re.sub(r"[\s\-_]+", " ", col.strip().lower())
    for gender, suffixes in GENDER_SUFFIXES.items():
        for sfx in suffixes:
            sfx_clean = re.sub(r"[\s\-_]+", " ", sfx.lower())
            if sfx_clean not in lower:
                continue
            base = lower.replace(sfx_clean, "").strip()
            base = re.sub(r"[\[\]\(\)]", "", base).strip()
            base = re.sub(r"[\s\-_]+", " ", base).strip()
            if not base:
                continue
            cat, _ = _exact_category_match(base)
            if cat:
                return cat, gender
    return None, None


def _exact_category_match(label: str) -> tuple[str | None, None]:
    clean = label.strip().lower()
    if not clean:
        return None, None
    for canonical, aliases in CATEGORY_ALIASES.items():
        if clean == canonical.lower():
            return canonical, None
        for alias in aliases:
            if clean == alias.lower():
                return canonical, None
    return None, None


# ---- Column Resolution Strategies ----

def resolve_columns_by_regex(df: pd.DataFrame) -> dict[str, str]:
    """Map columns using regex pattern matching (language-agnostic)."""
    col_map: dict[str, str] = {}

    for raw_col in df.columns:
        if _is_nan_column(raw_col) or not str(raw_col).strip():
            continue
        lower = str(raw_col).strip().lower()

        # Priority 1: Total column
        if any(kw in lower for kw in TOTAL_COL_KEYWORDS):
            col_map[raw_col] = "total"
            continue

        # Priority 2: Section column
        if any(kw in lower for kw in SECTION_KEYWORDS):
            col_map[raw_col] = "section"
            continue

        # Priority 3: Class column
        if _is_class_column(str(raw_col)):
            col_map[raw_col] = "class"
            continue

        # Priority 4: Flattened headers (e.g., 'एस.सी._बालक')
        parts = str(raw_col).strip().split("_")
        if len(parts) >= 2:
            mapped = _try_match_split_column(parts)
            if mapped:
                col_map[raw_col] = mapped
                continue

        # Priority 5: Single-column regex match
        for canonical, pattern in CATEGORY_REGEX_PATTERNS.items():
            if re.search(pattern, lower):
                col_map[raw_col] = canonical
                break

    return col_map


def _try_match_split_column(parts: list[str]) -> str | None:
    """Try to match a flattened column like ['sc', 'boys'] to 'sc_boys'."""
    parent = parts[0].lower()
    child = "_".join(parts[1:]).lower()

    # Try parent as category, child as gender
    for canonical, pattern in CATEGORY_REGEX_PATTERNS.items():
        if re.search(pattern, parent):
            gender = _detect_gender_from_text(child)
            return f"{canonical}_{gender}" if gender else canonical

    # Try child as category, parent as gender
    for canonical, pattern in CATEGORY_REGEX_PATTERNS.items():
        if re.search(pattern, child):
            gender = _detect_gender_from_text(parent)
            return f"{canonical}_{gender}" if gender else canonical

    return None


def resolve_columns(df: pd.DataFrame) -> dict[str, str]:
    """Map columns using keyword and alias matching."""
    col_map: dict[str, str] = {}
    gender_split_cols: dict[tuple[str, str], list[str]] = defaultdict(list)

    for raw_col in df.columns:
        if _is_nan_column(raw_col):
            continue

        col_str = str(raw_col)

        # Try gender suffix parsing (e.g., "SC_Boys" -> ("SC", "boys"))
        cat, gender = _parse_gender_suffix(col_str)
        if cat:
            gender_split_cols[(cat, gender)].append(raw_col)
            continue

        lower = col_str.strip().lower()

        # Total column (check before category aliases - "Total Students" contains "st")
        if any(kw in lower for kw in TOTAL_COL_KEYWORDS):
            col_map[raw_col] = "total"
            continue

        # Category aliases (check before class - "अन्य पिछड़ा वर्ग" is OBC)
        cat, _ = resolve_alias(col_str)
        if cat:
            col_map[raw_col] = cat
            continue

        if _is_class_column(col_str):
            col_map[raw_col] = "class"
            continue

        if any(kw in lower for kw in SECTION_KEYWORDS):
            col_map[raw_col] = "section"
            continue

    # Handle NaN columns from merged cells - they inherit from the previous column
    _resolve_nan_columns(df, col_map)

    # If a category has both combined and gender-split columns,
    # prefer the gender-split (more granular)
    split_cats = {cat for (cat, _) in gender_split_cols}
    for raw_col in list(col_map.keys()):
        if col_map[raw_col] in split_cats and col_map[raw_col] not in ("class", "total"):
            del col_map[raw_col]

    for (cat, gender), cols in gender_split_cols.items():
        for raw in cols:
            col_map[raw] = f"{cat}_{gender}"

    return col_map


def _resolve_nan_columns(df: pd.DataFrame, col_map: dict[str, str]) -> None:
    """NaN columns from merged cells get assigned as _girls of the preceding category."""
    for i, raw_col in enumerate(df.columns):
        if not _is_nan_column(raw_col) or i == 0:
            continue
        prev_mapped = col_map.get(df.columns[i - 1])
        if prev_mapped and prev_mapped not in ("class", "total", "boys", "girls", "section"):
            if not prev_mapped.endswith("_boys") and not prev_mapped.endswith("_girls"):
                col_map[i] = f"{prev_mapped}_girls"


# ---- Row Filtering ----

def _is_total_row(row: pd.Series) -> bool:
    """Check if a row is a subtotal/total summary row."""
    return any(any(kw in str(v).strip().lower() for kw in SUBTOTAL_KEYWORDS) for v in row.values)


def _get_class_value(row: pd.Series, class_col: str | None) -> int | str | None:
    """Extract the class value from a row, returning None for invalid/total rows."""
    if class_col is None:
        return None
    val = str(row[class_col]).strip()
    if not val or val.lower() == "nan":
        return None
    if any(kw in val.lower() for kw in SUBTOTAL_KEYWORDS):
        return None
    return normalize_class_label(val)


def _parse_numeric(val: Any) -> int:
    try:
        return int(float(str(val)))
    except (ValueError, TypeError):
        return 0


def _validate_and_fix_total(row_data: dict[str, int]) -> dict[str, int]:
    """
    If category columns sum to more than the stated total (from double-counting
    combined+split columns), use the larger category sum as the authoritative total.
    """
    stated_total = row_data.get("total", 0)
    all_cat_sum = sum(v for k, v in row_data.items() if k != "total" and k in CATEGORY_COMPARE_FIELDS)

    if (stated_total > 0 and all_cat_sum > stated_total) or (stated_total == 0 and all_cat_sum > 0):
        row_data["total"] = all_cat_sum
        row_data["_total_corrected"] = True

    return row_data


# ---- Aggregation ----

def _find_section_col(df: pd.DataFrame, col_map: dict) -> str | None:
    for raw, mapped in col_map.items():
        if mapped == "section":
            return raw
    for c in df.columns:
        if any(kw in str(c).strip().lower() for kw in SECTION_KEYWORDS):
            return c
    return None


def _prepare_dataframe(df: pd.DataFrame, col_map: dict) -> tuple[pd.DataFrame, str | None, str | None]:
    """Common preparation: filter totals, normalize class/section, find key columns."""
    class_col = next((r for r, m in col_map.items() if m == "class"), None)
    section_col = _find_section_col(df, col_map)

    # Filter out total/summary rows
    mask = df.apply(_is_total_row, axis=1)
    df_clean = df[~mask].copy()

    # Drop rows with empty class column
    if class_col:
        df_clean = df_clean.dropna(subset=[class_col])
        df_clean = df_clean[df_clean[class_col].astype(str).str.strip() != ""]

    if df_clean.empty:
        return df_clean, class_col, section_col

    # Normalize class and section keys
    df_clean["_match_class"] = (
        df_clean[class_col].astype(str).str.upper().str.strip().apply(normalize_class_label).astype(str)
        if class_col else "?"
    )
    df_clean["_match_section"] = (
        df_clean[section_col].astype(str).str.upper().str.strip()
        if section_col else ""
    )

    return df_clean, class_col, section_col


def _get_numeric_and_category_cols(df_clean: pd.DataFrame, col_map: dict) -> tuple[list[str], dict[str, str]]:
    """Find numeric columns and build category rename mapping."""
    category_raw_cols = [raw for raw, mapped in col_map.items() if mapped not in ("class", "section", "boys", "girls")]
    total_raw_col = next((raw for raw, mapped in col_map.items() if mapped == "total"), None)
    cat_raw_cols = [c for c in category_raw_cols if c != total_raw_col]

    if not cat_raw_cols and not total_raw_col:
        return [], {}

    # Build rename map: raw_col -> canonical category name (strip _boys/_girls suffix)
    cat_rename = {}
    for raw in cat_raw_cols:
        mapped = col_map[raw]
        cat_rename[raw] = mapped.rsplit("_", 1)[0] if "_" in mapped else mapped

    # Convert to numeric
    numeric_cols = cat_raw_cols + ([total_raw_col] if total_raw_col else [])
    for c in numeric_cols:
        if c in df_clean.columns:
            df_clean[c] = pd.to_numeric(df_clean[c], errors="coerce").fillna(0)

    # Drop rows where all category values are 0
    if cat_raw_cols:
        df_clean = df_clean[df_clean[cat_raw_cols].sum(axis=1) > 0]

    return numeric_cols, cat_rename


def aggregate_by_class(df: pd.DataFrame, col_map: dict[str | int, str]) -> dict[int | str, dict[str, int]]:
    """Aggregate category data by class, summing across sections."""
    df_clean, class_col, section_col = _prepare_dataframe(df, col_map)
    if df_clean.empty:
        return {}

    numeric_cols, cat_rename = _get_numeric_and_category_cols(df_clean, col_map)
    if not numeric_cols:
        return {}

    total_raw_col = next((raw for raw, mapped in col_map.items() if mapped == "total"), None)

    # Group by class+section and sum
    numeric_subset = [c for c in numeric_cols if c in df_clean.columns]
    grouped = df_clean.groupby(["_match_class", "_match_section"])[numeric_subset].sum(min_count=1).reset_index()

    # Rename category columns
    rename_map = {k: v for k, v in cat_rename.items() if k in grouped.columns}
    if rename_map:
        grouped = grouped.rename(columns=rename_map)
    if total_raw_col and total_raw_col in grouped.columns:
        grouped = grouped.rename(columns={total_raw_col: "_row_total"})

    # Aggregate across sections per class
    available_cats = list(set(cat_rename.values()) & set(grouped.columns))
    result = {}

    for cls_val, grp in grouped.groupby("_match_class"):
        row = {}
        if available_cats:
            row.update({k: _parse_numeric(v) for k, v in grp[available_cats].sum().to_dict().items()})
        if "_row_total" in grp.columns:
            row["total"] = _parse_numeric(grp["_row_total"].sum())
        row = _validate_and_fix_total(row)
        result[normalize_class_label(cls_val)] = row

    return result


def aggregate_by_section(df: pd.DataFrame, col_map: dict[str | int, str]) -> dict[str, dict[str, int]]:
    """Aggregate at the class+section level (e.g., '1-A', '2-B')."""
    df_clean, class_col, section_col = _prepare_dataframe(df, col_map)
    if df_clean.empty:
        return {}

    numeric_cols, cat_rename = _get_numeric_and_category_cols(df_clean, col_map)
    if not numeric_cols:
        return {}

    total_raw_col = next((raw for raw, mapped in col_map.items() if mapped == "total"), None)

    numeric_subset = [c for c in numeric_cols if c in df_clean.columns]
    grouped = df_clean.groupby(["_match_class", "_match_section"])[numeric_subset].sum(min_count=1).reset_index()

    rename_map = {k: v for k, v in cat_rename.items() if k in grouped.columns}
    if rename_map:
        grouped = grouped.rename(columns=rename_map)
    if total_raw_col and total_raw_col in grouped.columns:
        grouped = grouped.rename(columns={total_raw_col: "_row_total"})

    available_cats = list(set(cat_rename.values()) & set(grouped.columns))
    result = {}

    for _, row in grouped.iterrows():
        cls = str(row["_match_class"])
        sec = str(row["_match_section"])
        class_id = f"{cls}-{sec}" if sec else cls

        entry = {}
        if available_cats:
            entry.update({c: _parse_numeric(row.get(c, 0)) for c in available_cats})
        if "_row_total" in grouped.columns:
            entry["total"] = _parse_numeric(row.get("_row_total", 0))
        entry = _validate_and_fix_total(entry)
        result[class_id] = entry

    return result


# ---- Detection Helpers ----

def has_gender_split(df: pd.DataFrame, col_map: dict[str, str]) -> bool:
    return any(v.endswith("_boys") or v.endswith("_girls") for v in col_map.values())


def internal_consistency_check(aggregated: dict, file_label: str) -> list[dict]:
    """Check if category sums match the stated total for each class."""
    checks = []
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


# ---- Main Entry Point ----

def parse_category_file(filepath: str, file_label: str) -> dict[str, Any]:
    """
    Parse an aggregate/class-level Excel file (summary tables with SC/ST/OBC counts by class).
    
    Detection strategy (in order):
      1. Regex-based column resolution
      2. Statistical data profiling
      3. Keyword-based fallback
    
    Returns aggregated data by class and section, plus metadata.
    """
    df = read_file(filepath)
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    df = flatten_nested_headers(df)

    # Phase 1: Regex-based column resolution
    col_map = resolve_columns_by_regex(df)
    class_col = next((r for r, m in col_map.items() if m == "class"), None)
    total_col = next((r for r, m in col_map.items() if m == "total"), None)
    section_col = next((r for r, m in col_map.items() if m == "section"), None)

    # Phase 2: Statistical profiling (if regex missed key columns)
    if class_col is None or total_col is None:
        profiled = profile_dataframe(df)
        for k, v in profiled["col_map"].items():
            if k not in col_map:
                col_map[k] = v
        class_col = class_col or profiled["detected_class_col"]
        total_col = total_col or profiled["detected_total_col"]
        section_col = section_col or profiled["detected_section_col"]

    # Phase 3: Keyword-based fallback
    if class_col is None or not any(v not in ("class", "section", "total") for v in col_map.values()):
        kw_map = resolve_columns(df)
        for k, v in kw_map.items():
            if k not in col_map:
                col_map[k] = v
        class_col = class_col or next((r for r, m in col_map.items() if m == "class"), None)
        total_col = total_col or next((r for r, m in col_map.items() if m == "total"), None)

    # Phase 4: Clean grand total rows
    if total_col:
        df = clean_grand_total_rows(df, total_col)
        df[total_col] = pd.to_numeric(df[total_col], errors="coerce").fillna(0)
        df = df[df[total_col] > 0]

    # Aggregate data
    aggregated = aggregate_by_class(df, col_map)
    section_agg = aggregate_by_section(df, col_map)

    # Consistency checks
    has_subtotal = any(_is_total_row(row) for _, row in df.iterrows())
    checks = internal_consistency_check(aggregated, file_label)

    return {
        "file_label": file_label,
        "aggregated": {str(k): v for k, v in aggregated.items()},
        "section_aggregated": section_agg,
        "col_map": col_map,
        "has_subtotal_rows": has_subtotal,
        "has_gender_split": has_gender_split(df, col_map),
        "consistency_checks": checks,
        "total_classes": len(aggregated),
    }
