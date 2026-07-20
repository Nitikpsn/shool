import re
from rapidfuzz import fuzz

# ---- Gender: map any variant to "boy" or "girl" ----
GENDER_MAP = {
    # English
    "male": "boy", "m": "boy", "b": "boy", "boy": "boy",
    "male (boy)": "boy", "boy (m)": "boy",
    # Hindi
    "लड़का": "boy", "बालक": "boy", "छात्र": "boy", "पुरुष": "boy",
    # English
    "female": "girl", "f": "girl", "g": "girl", "girl": "girl",
    "female (girl)": "girl", "girl (f)": "girl",
    # Hindi
    "लड़की": "girl", "बालिका": "girl", "छात्रा": "girl", "महिला": "girl",
}

# ---- Category: map any variant to standard code ----
CATEGORY_MAP = {
    # SC
    "sc": "SC", "scheduled caste": "SC", "s.c.": "SC", "s c": "SC",
    "अनुसूचित जाति": "SC", "एस.सी.": "SC", "एससी": "SC",
    # ST
    "st": "ST", "scheduled tribe": "ST", "s.t.": "ST", "s t": "ST",
    "अनुसूचित जनजाति": "ST", "एस.टी.": "ST", "एसटी": "ST",
    # OBC
    "obc": "OBC", "other backward class": "OBC", "o.b.c.": "OBC",
    "o b c": "OBC", "अन्य पिछड़ा वर्ग": "OBC",
    "ओ.बी.सी.": "OBC", "ओबीसी": "OBC",
    # EWS
    "ews": "EWS", "economically weaker section": "EWS",
    "e.w.s.": "EWS", "आर्थिक रूप से कमजोर": "EWS",
    # General
    "general": "GEN", "gen": "GEN", "general category": "GEN",
    "g general": "GEN", "सामान्य": "GEN", "जनरल": "GEN",
    "none": "GEN", "n/a": "GEN", "ur": "GEN", "unreserved": "GEN",
}

# ---- Category aliases for aggregate/summary tables ----
CATEGORY_ALIASES = {
    "general": ["सामान्य", "general", "gen", "general category", "जनरल", "unreserved", "ur"],
    "obc": ["अन्य पिछड़ा वर्ग", "obc", "other backward class", "o.b.c.", "ओ.बी.सी.", "ओबीसी"],
    "obc_cl": ["अन्य पिछड़ा वर्ग (सीएल)", "obc cl", "obc-cl", "obc (cl)", "obc-creamy layer"],
    "obc_ncl": ["अन्य पिछड़ा वर्ग (एनसीएल)", "obc ncl", "obc-ncl", "obc (ncl)", "obc-non creamy layer"],
    "sc": ["एस.सी.", "अनुसूचित जाति", "sc", "scheduled caste", "s.c.", "एससी"],
    "st": ["एस.टी.", "अनुसूचित जनजाति", "st", "scheduled tribe", "s.t.", "एसटी"],
    "muslim": ["मुस्लिम", "muslim", "इस्लाम"],
    "christian": ["क्रिस्चियन", "christian", "ईसाई"],
    "sikh": ["सिख", "sikh"],
    "buddhist": ["बुद्धिस्ट", "buddhist", "बौद्ध"],
    "parsi": ["पारसी", "parsi"],
    "jain": ["जैन", "jain"],
    "minority_total": ["अल्पसंख्यक", "minority", "अल्पसंख्यक कुल"],
    "cwsn": ["विकलांग", "cwsn", "divyang", "disabled", "विशेष आवश्यकता"],
    "rte": ["rte", "आरटीई", "शिक्षा का अधिकार"],
    "sgc": ["sgc", "एसजीसी"],
    "boys": ["छात्र", "boys", "male", "बालक", "पुरुष"],
    "girls": ["छात्रा", "girls", "female", "बालिका", "महिला"],
    "total": ["कुल", "योग", "total", "grand total", "संख्या", "कुल योग", "संख्या योग"],
}

# ---- Roman numerals for class labels ----
ROMAN_MAP = {
    "i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5,
    "vi": 6, "vii": 7, "viii": 8, "ix": 9, "x": 10,
    "xi": 11, "xii": 12,
}

# ---- Named classes (pre-primary etc.) ----
NAMED_CLASSES = {
    "nursery": -2, "nur": -2, "prep": -2,
    "lkg": -1, "lower kindergarten": -1,
    "ukg": 0, "upper kindergarten": 0,
    "pre-primary": -1, "pre primary": -1, "preprimary": -1,
}

# ---- Language normalization ----
LANGUAGE_MAP = {
    "hindi": "Hindi", "hi": "Hindi", "हिंदी": "Hindi",
    "english": "English", "en": "English", "अंग्रेज़ी": "English",
    "hindi/english": "Hindi/English", "both": "Hindi/English",
    "hindi & english": "Hindi/English", "hindi and english": "Hindi/English",
    "हिंदी/अंग्रेज़ी": "Hindi/English",
}


def normalize_gender(value: str) -> str:
    """Convert any gender variant (English/Hindi) to 'boy' or 'girl'."""
    clean = value.strip().lower()
    if not clean:
        return ""
    return GENDER_MAP.get(clean, value.strip().title())


def normalize_category(value: str) -> str:
    """Convert any category variant to standard code (SC, ST, OBC, EWS, GEN)."""
    clean = value.strip().lower()
    if not clean:
        return ""
    return CATEGORY_MAP.get(clean, value.strip().upper())


def normalize_language(value: str) -> str:
    """Convert language variant to standard form."""
    clean = value.strip().lower()
    if not clean:
        return ""
    return LANGUAGE_MAP.get(clean, value.strip().title())


def resolve_alias(label: str, threshold: float = 80) -> tuple[str | None, str | None]:
    """
    Given a label like "OBC", "SC", "General", etc., find its canonical name
    using exact match first, then fuzzy match as fallback.
    Returns (canonical_name, matched_alias) or (None, None).
    """
    clean = label.strip().lower()
    if not clean:
        return None, None

    # Try exact match first
    for canonical, aliases in CATEGORY_ALIASES.items():
        if clean == canonical.lower():
            return canonical, canonical
        for alias in aliases:
            if clean == alias.lower():
                return canonical, alias

    # Fallback: fuzzy match
    for canonical, aliases in CATEGORY_ALIASES.items():
        for alias in aliases:
            if fuzz.partial_ratio(clean, alias.lower()) >= threshold:
                return canonical, alias

    return None, None


def normalize_class_label(label: str) -> int | str:
    """
    Convert a class label to a standard form:
      - Roman numerals -> numbers (e.g., "VIII" -> 8)
      - Named classes -> ordered numbers (e.g., "LKG" -> -1)
      - Numeric strings -> int (e.g., "6" -> 6)
      - Unknown -> pass through as string
    """
    clean = label.strip().lower()
    if not clean:
        return ""

    # Strip common prefixes like "Class", "Grade", "कक्षा" etc.
    clean = re.sub(r'\s*(class|grade|standard|cls|कक्षा|क्लास|वर्ग)\s*', '', clean).strip()

    if clean in NAMED_CLASSES:
        return NAMED_CLASSES[clean]
    if clean in ROMAN_MAP:
        return ROMAN_MAP[clean]
    try:
        return int(float(clean))
    except (ValueError, TypeError):
        return clean
