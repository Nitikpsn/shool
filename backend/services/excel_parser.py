import os
import re
import pandas as pd
from collections import Counter
from typing import Any, Optional
from utils.normalize import normalize_gender, normalize_category, normalize_language

CRITICAL_FIELDS = {"admission_no", "student_name"}

# ---- Column name patterns for each field ----
# Exact matches first, then substring fallbacks
FIELD_EXACT = {
    "admission_no": [
        "admission_no", "admission number", "admn no", "adm no", "roll no",
        "roll number", "student id", "student_id", "enrollment no", "reg no",
        "registration no", "admission no", "admn. no", "adm. no",
    ],
    "student_name": [
        "student_name", "student name", "name", "child name", "full name",
        "childs name", "pupil name", "name of pupil", "name of student",
        "candidate name",
    ],
    "class_name": ["class_name", "class name", "class", "grade", "standard", "cls"],
    "gender": ["gender", "sex", "gender of student", "student gender"],
    "category": ["category", "caste", "community", "cat", "social category", "student category"],
    "language": ["language", "medium", "lang", "language medium", "medium of instruction"],
}

FIELD_SUBSTRING = {
    "admission_no": ["admission", "admn", "adm", "roll", "enrol", "reg no"],
    "student_name": ["student name", "child", "full name", "pupil", "candidate name"],
    "class_name": ["class", "grade", "standard", "cls"],
    "gender": ["gender", "sex"],
    "category": ["category", "caste", "community"],
    "language": ["language", "medium"],
}

# ---- Data type detection keywords ----
STUDENT_KEYWORDS = [
    "admission", "admn", "adm", "roll", "enrol", "student name",
    "student_name", "child name", "childs name", "full name",
]
CATEGORY_KEYWORDS = [
    "sc", "st", "obc", "general", "सामान्य", "एस.सी.", "एस.टी.", "ओ.बी.सी.",
    "scheduled caste", "scheduled tribe", "minority", "cwsn", "rte", "sgc",
    "muslim", "christian", "sikh", "buddhist", "parsi", "jain", "अल्पसंख्यक",
    "बालक", "बालिका", "boys", "girls", "छात्र", "छात्रा",
]
SUBTOTAL_KEYWORDS = ["योग", "कुल", "subtotal", "total", "grand total", "संख्या", "sum"]
CLASS_KEYWORDS = ["class", "grade", "standard", "cls", "कक्षा", "क्लास", "वर्ग"]
SECTION_KEYWORDS = ["section", "अनुभाग", "सेक्शन", "sec", "भाग"]


def _normalize_admission(val: str) -> str:
    """Strip prefixes like 'ADM/', 'ROLL-', etc. and keep only alphanumeric."""
    v = val.strip()
    v = re.sub(r'^(admn?|adm|roll|enrol|reg)[/\s\-]*', '', v, flags=re.IGNORECASE)
    v = re.sub(r'[^0-9a-zA-Z]', '', v)
    return v.lstrip('0') or v or '0'


def read_file(filepath: str) -> pd.DataFrame:
    """Read an Excel or CSV file into a DataFrame."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".csv":
        return pd.read_csv(filepath, dtype=str)
    return pd.read_excel(filepath, dtype=str)


def detect_data_type(filepath: str) -> str:
    """
    Determine if a file contains individual student records or aggregate summary data.
    Uses keyword matching on headers and row content, plus numeric density analysis.
    """
    ext = os.path.splitext(filepath)[1].lower()
    df = pd.read_csv(filepath, dtype=str, nrows=20) if ext == ".csv" else pd.read_excel(filepath, dtype=str, nrows=20)
    df.columns = [str(c).strip() for c in df.columns]
    lower_cols = [str(c).strip().lower() for c in df.columns]

    student_score = _score_by_keywords(lower_cols, STUDENT_KEYWORDS, weight=2)
    aggregate_score = _score_by_keywords(lower_cols, CATEGORY_KEYWORDS)

    # Subtotal rows in data strongly suggest aggregate file
    for _, row in df.iterrows():
        row_text = " ".join(str(v).strip().lower() for v in row.values if pd.notna(v))
        if any(kw in row_text for kw in SUBTOTAL_KEYWORDS):
            aggregate_score += 3

    # Many numeric columns = aggregate summary table
    numeric_cols = sum(1 for col in df.columns if len(pd.to_numeric(df[col], errors="coerce").dropna()) >= 3)
    if numeric_cols >= 4:
        aggregate_score += 2

    # Class/Section keywords boost aggregate
    aggregate_score += _score_by_keywords(lower_cols, CLASS_KEYWORDS)
    aggregate_score += _score_by_keywords(lower_cols, SECTION_KEYWORDS)

    # Small files tend to be aggregate, large files tend to be student lists
    row_count = len(df)
    if row_count <= 30:
        aggregate_score += 1
    elif row_count > 100:
        student_score += 1

    return "aggregate" if aggregate_score > student_score else "student"


def _score_by_keywords(lower_cols: list[str], keywords: list[str], weight: int = 1) -> int:
    """Count how many columns match any keyword."""
    score = 0
    for col in lower_cols:
        if any(kw in col for kw in keywords):
            score += weight
    return score


def infer_columns(df: pd.DataFrame, ai_fallback: Optional[Any] = None) -> dict[str, str]:
    """
    Map DataFrame column names to standard field names (admission_no, student_name, etc.).
    
    Strategy:
      1. Try exact column name matches
      2. Fall back to substring matching
      3. If critical fields still missing, ask AI for help
    """
    col_map = {}
    lower_cols = {col: str(col).strip().lower() for col in df.columns}

    # Step 1: Exact matches
    for field, exact_names in FIELD_EXACT.items():
        for raw_col, lower_col in lower_cols.items():
            if lower_col in exact_names:
                col_map[field] = raw_col
                break

    # Step 2: Substring fallbacks for still-missing fields
    for field, substrings in FIELD_SUBSTRING.items():
        if field in col_map:
            continue
        already_used = set(col_map.values())
        for raw_col, lower_col in lower_cols.items():
            if raw_col in already_used:
                continue
            if any(sub in lower_col for sub in substrings):
                col_map[field] = raw_col
                break

    # Step 3: Special case - "name" without "admission" in it
    if "student_name" not in col_map:
        for raw_col, lower_col in lower_cols.items():
            if raw_col == col_map.get("admission_no"):
                continue
            if "name" in lower_col and "admission" not in lower_col:
                col_map["student_name"] = raw_col
                break

    # Step 4: AI fallback for critical fields
    missing_critical = CRITICAL_FIELDS - set(col_map.keys())
    if missing_critical and ai_fallback is not None:
        try:
            ai_map = ai_fallback.column_mapping(list(df.columns))
            for field in missing_critical:
                if field in ai_map and ai_map[field] in df.columns:
                    col_map[field] = ai_map[field]
        except Exception:
            pass

    return col_map


def parse_excel(filepath: str, source_sheet: str, ai_fallback: Optional[Any] = None) -> list[dict[str, Any]]:
    """
    Parse an Excel/CSV file into a list of normalized student record dictionaries.
    Handles column inference, admission number normalization, and duplicate detection.
    """
    df = read_file(filepath)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x).fillna("")

    col_map = infer_columns(df, ai_fallback=ai_fallback)
    adm_col = col_map.get("admission_no", "")
    name_col = col_map.get("student_name", "")

    records = []
    seen_ids: Counter = Counter()

    for _, row in df.iterrows():
        # Extract and normalize admission number
        raw_adm = str(row.get(adm_col, "")).strip() if adm_col else ""
        adm_id = _normalize_admission(raw_adm)

        # Skip empty rows
        if not adm_id or adm_id == "0":
            continue

        # Deduplicate by appending suffix
        if seen_ids[adm_id] > 0:
            adm_id = f"{adm_id}_dup{seen_ids[adm_id] + 1}"
        seen_ids[adm_id] += 1

        # Build the record
        record = {
            "admission_no_raw": raw_adm,
            "admission_no": adm_id,
            "student_name": _safe_str(row, name_col),
            "class_name": _safe_str(row, col_map.get("class_name", "")),
            "gender": normalize_gender(_safe_str(row, col_map.get("gender", ""))),
            "category": normalize_category(_safe_str(row, col_map.get("category", ""))),
            "language": normalize_language(_safe_str(row, col_map.get("language", ""))),
            "source_sheet": source_sheet,
            "extra_fields": _collect_extra_fields(row, df.columns, set(col_map.values())),
        }

        records.append(record)

    return records


def _safe_str(row: pd.Series, col: str) -> str:
    """Safely extract a string value from a row."""
    if not col:
        return ""
    return str(row.get(col, "")).strip()


def _collect_extra_fields(row: pd.Series, all_columns, mapped_columns: set) -> dict:
    """Collect any unmapped non-empty columns as extra fields."""
    extra = {}
    for col in all_columns:
        if col in mapped_columns:
            continue
        val = str(row.get(col, "")).strip()
        if val:
            extra[col] = val
    return extra


def export_excel(data: list[dict], output_path: str):
    """Export a list of records to an Excel file."""
    pd.DataFrame(data).to_excel(output_path, index=False)
