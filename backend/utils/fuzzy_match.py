from rapidfuzz import fuzz
from utils.normalize import normalize_class_label


def fuzzy_match_score(str1: str, str2: str) -> float:
    """Exact fuzzy ratio between two strings (0.0 - 1.0)."""
    s1, s2 = str1.strip().lower(), str2.strip().lower()
    if not s1 or not s2:
        return 0.0
    return fuzz.ratio(s1, s2) / 100.0


def partial_match_score(str1: str, str2: str) -> float:
    """Partial fuzzy match - substring containment (0.0 - 1.0)."""
    s1, s2 = str1.strip().lower(), str2.strip().lower()
    if not s1 or not s2:
        return 0.0
    return fuzz.partial_ratio(s1, s2) / 100.0


def token_sort_score(str1: str, str2: str) -> float:
    """Token-sort match - order-independent word matching (0.0 - 1.0)."""
    s1, s2 = str1.strip().lower(), str2.strip().lower()
    if not s1 or not s2:
        return 0.0
    return fuzz.token_sort_ratio(s1, s2) / 100.0


def token_set_score(str1: str, str2: str) -> float:
    """Token-set match - handles duplicate words (0.0 - 1.0)."""
    s1, s2 = str1.strip().lower(), str2.strip().lower()
    if not s1 or not s2:
        return 0.0
    return fuzz.token_set_ratio(s1, s2) / 100.0


def is_fuzzy_match(str1: str, str2: str, threshold: float = 0.85) -> bool:
    """Check if two strings are similar enough to be considered a match."""
    return fuzzy_match_score(str1, str2) >= threshold


def _normalize_class(class_str: str) -> str:
    """Normalize class label for comparison purposes."""
    val = normalize_class_label(class_str.strip())
    return str(val).strip().lower() if val else ""


def multi_field_score(record_a: dict, record_b: dict) -> float:
    """
    Compute a weighted similarity score between two student records.
    
    Weights:
      - Name: 50% (most important for identification)
      - Class: 20% (must match for same student)
      - Gender: 15% (strong indicator)
      - Category: 15% (secondary indicator)
    
    Returns score from 0.0 (no match) to 1.0 (perfect match).
    """
    # Name: best of 4 fuzzy methods
    name_a = record_a.get("student_name", "")
    name_b = record_b.get("student_name", "")
    name_score = max(
        fuzzy_match_score(name_a, name_b),
        partial_match_score(name_a, name_b),
        token_sort_score(name_a, name_b),
        token_set_score(name_a, name_b),
    )

    # Class: exact match after normalization (0 or 1, or 0.5 if unknown)
    cls_a = _normalize_class(record_a.get("class_name", ""))
    cls_b = _normalize_class(record_b.get("class_name", ""))
    class_score = _binary_score(cls_a, cls_b)

    # Gender: exact match (0 or 1, or 0.5 if unknown)
    gen_a = record_a.get("gender", "").strip().lower()
    gen_b = record_b.get("gender", "").strip().lower()
    gender_score = _binary_score(gen_a, gen_b)

    # Category: exact match (0 or 1, or 0.5 if unknown)
    cat_a = record_a.get("category", "").strip().upper()
    cat_b = record_b.get("category", "").strip().upper()
    category_score = _binary_score(cat_a, cat_b)

    return (
        name_score * 0.50
        + class_score * 0.20
        + gender_score * 0.15
        + category_score * 0.15
    )


def _binary_score(a: str, b: str) -> float:
    """Returns 1.0 if both match, 0.0 if both present but differ, 0.5 if either is unknown."""
    if not a or not b:
        return 0.5
    return 1.0 if a == b else 0.0


def find_best_match(name: str, candidates: list[str], threshold: float = 0.8):
    """Find the best matching name from a list of candidates."""
    best_score = 0.0
    best_match = None
    for candidate in candidates:
        score = fuzzy_match_score(name, candidate)
        if score > best_score:
            best_score = score
            best_match = candidate
    if best_score >= threshold:
        return best_match, best_score
    return None, 0.0
