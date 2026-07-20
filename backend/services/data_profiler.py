import pandas as pd
from typing import Any

TOTAL_KEYWORDS = [
    "total", "grand", "subtotal", "students", "योग", "संख्या",
    "कुल", "strength", "count", "enrolled", "enrollment", "sum",
]

CLASS_KEYWORDS = ["class", "grade", "standard", "cls", "कक्षा", "क्लास"]
SECTION_KEYWORDS = ["section", "अनुभाग", "सेक्शन", "sec", "भाग"]
KNOWN_CLASS_VALUES = {
    "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII",
    "LKG", "UKG", "NURSERY", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12",
}


def find_total_students_column(df: pd.DataFrame) -> str | None:
    """
    Find the column that represents total student count.
    Strategy: keyword match first, then statistical profiling to find the best numeric column.
    """
    # Try keyword-based matching
    for col in df.columns:
        lower = str(col).strip().lower()
        if any(kw in lower for kw in TOTAL_KEYWORDS):
            vals = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(vals) > 0 and 1 <= vals.median() <= 5000 and vals.max() < 50000:
                return col

    # Profile numeric columns and pick the most likely total
    candidates = []
    for col in df.columns:
        vals = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(vals) < 2:
            continue
        candidates.append({
            "name": col,
            "sum": vals.sum(),
            "is_sequential": vals.is_monotonic_increasing,
            "unique_diffs": vals.diff().dropna().nunique() if len(vals) > 1 else 0,
            "mean": vals.mean(),
        })

    if not candidates:
        return None

    candidates.sort(key=lambda x: x["sum"], reverse=True)

    for c in candidates:
        # Skip auto-incrementing ID columns (1, 2, 3...)
        if c["is_sequential"] and c["unique_diffs"] <= 1:
            continue
        if c["mean"] < 50 and c["is_sequential"]:
            continue
        return c["name"]

    return candidates[0]["name"]


def clean_grand_total_rows(df: pd.DataFrame, total_col: str) -> pd.DataFrame:
    """Remove summary/total rows that are statistical outliers compared to class-level rows."""
    if total_col not in df.columns:
        return df

    values = pd.to_numeric(df[total_col], errors="coerce")
    median_val = values.median()

    if pd.isna(median_val) or median_val == 0:
        return df

    # A grand total row will have a value several times larger than a typical row
    cleaned = df[values < median_val * 2.5].copy()
    return cleaned if len(cleaned) > 0 else df


def detect_class_column(df: pd.DataFrame) -> str | None:
    """Find the column that contains class/grade identifiers."""
    # Keyword match
    for col in df.columns:
        if any(kw in str(col).strip().lower() for kw in CLASS_KEYWORDS):
            return col

    # Fallback: column with few unique values that look like class identifiers
    for col in df.columns:
        unique_vals = df[col].dropna().unique()
        if 3 <= len(unique_vals) <= 20:
            sample = {str(v).strip().upper() for v in unique_vals}
            if any(v in KNOWN_CLASS_VALUES for v in sample):
                return col

    return df.columns[0] if len(df.columns) > 0 else None


def detect_section_column(df: pd.DataFrame) -> str | None:
    """Find the column that contains section identifiers (A, B, C, etc.)."""
    # Keyword match
    for col in df.columns:
        if any(kw in str(col).strip().lower() for kw in SECTION_KEYWORDS):
            return col

    # Fallback: column with short alphabetic values
    for col in df.columns:
        unique_vals = df[col].dropna().unique()
        if 2 <= len(unique_vals) <= 10:
            sample = {str(v).strip().upper() for v in unique_vals}
            if all(len(v) <= 2 and v.isalpha() for v in sample if v):
                return col

    return None


def detect_category_columns(
    df: pd.DataFrame, class_col: str | None, section_col: str | None, total_col: str | None
) -> dict[str, str]:
    """
    Identify category columns (SC, ST, OBC, General, etc.).
    These are numeric columns with small values that aren't class, section, or total.
    """
    exclude = {str(c) for c in [class_col, section_col, total_col] if c}
    category_map: dict[str, str] = {}

    CATEGORY_ALIASES: dict[str, list[str]] = {
        "general": ["general", "gen", "सामान्य", "general category"],
        "obc": ["obc", "other backward class", "o.b.c.", "अन्य पिछड़ा वर्ग"],
        "obc_cl": ["obc cl", "obc-cl", "obc (cl)"],
        "obc_ncl": ["obc ncl", "obc-ncl", "obc (ncl)"],
        "sc": ["sc", "scheduled caste", "s.c.", "एस.सी.", "अनुसूचित जाति"],
        "st": ["st", "scheduled tribe", "s.t.", "एस.टी.", "अनुसूचित जनजाति"],
        "muslim": ["muslim", "मुस्लिम"],
        "christian": ["christian", "क्रिस्चियन"],
        "sikh": ["sikh", "सिख"],
        "buddhist": ["buddhist", "बुद्धिस्ट"],
        "parsi": ["parsi", "पारसी"],
        "jain": ["jain", "जैन"],
        "minority_total": ["minority", "अल्पसंख्यक"],
        "cwsn": ["cwsn", "divyang", "disabled", "विकलांग"],
        "rte": ["rte"],
        "sgc": ["sgc"],
        "boys": ["boys", "male", "बालक", "छात्र"],
        "girls": ["girls", "female", "बालिका", "छात्रा"],
    }

    # First pass: keyword match
    for col in df.columns:
        if col in exclude:
            continue
        lower = str(col).strip().lower()
        for canonical, aliases in CATEGORY_ALIASES.items():
            if any(alias in lower for alias in aliases):
                category_map[col] = canonical
                break

    # Second pass: profile remaining unmapped columns
    mapped = set(category_map.keys()) | exclude
    for col in df.columns:
        if col in mapped:
            continue
        vals = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(vals) < 2:
            continue
        if 0 <= vals.median() <= 2000 and 0 <= vals.max() <= 10000:
            category_map[col] = str(col).strip().lower().replace(" ", "_")

    return category_map


def profile_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    """
    Profile a dataframe to detect all relevant columns dynamically.
    Returns column mapping and detected metadata.
    """
    df_str = df.map(lambda x: str(x).strip() if isinstance(x, str) else x)

    total_col = find_total_students_column(df_str)
    class_col = detect_class_column(df_str)
    section_col = detect_section_column(df_str)

    col_map: dict[str, str] = {}
    if class_col:
        col_map[class_col] = "class"
    if section_col:
        col_map[section_col] = "section"
    if total_col:
        col_map[total_col] = "total"

    cat_map = detect_category_columns(df_str, class_col, section_col, total_col)
    col_map.update(cat_map)

    return {
        "col_map": col_map,
        "detected_total_col": total_col,
        "detected_class_col": class_col,
        "detected_section_col": section_col,
        "total_rows_before_clean": len(df_str),
    }
