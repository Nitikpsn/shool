from utils.normalize import GENDER_MAP, CATEGORY_MAP, LANGUAGE_MAP

HINDI_KEYWORDS = {
    "लड़का", "लड़की", "अनुसूचित", "जाति", "जनजाति", "पिछड़ा", "वर्ग",
    "हिंदी", "अंग्रेज़ी", "कक्षा", "छात्र", "विद्यार्थी",
}


def contains_hindi(text: str) -> bool:
    for char in text:
        if '\u0900' <= char <= '\u097F':
            return True
    return False


def normalize_query(text: str) -> str:
    tokens = text.strip().lower().split()
    mapped = []
    for token in tokens:
        if token in GENDER_MAP:
            mapped.append(GENDER_MAP[token])
        elif token in CATEGORY_MAP:
            mapped.append(CATEGORY_MAP[token])
        elif token in LANGUAGE_MAP:
            mapped.append(LANGUAGE_MAP[token])
        else:
            mapped.append(token)
    return " ".join(mapped)