"""Language detection for English and Telugu queries.

Uses character-level Unicode script analysis to identify whether the user
is asking in Telugu (Unicode range U+0C00 - U+0C7F), English (Latin), or
a code-mixed combination.
"""

import re
from typing import Dict, Any


TELUGU_CHAR_PATTERN = re.compile(r"[\u0c00-\u0c7f]")
LATIN_CHAR_PATTERN = re.compile(r"[a-zA-Z]")


def detect_language(text: str) -> Dict[str, Any]:
    """Detect whether text is predominantly Telugu or English.
    
    Args:
        text: Input user question string.
        
    Returns:
        Dictionary with:
            - lang: 'te' or 'en'
            - telugu_char_count: int
            - latin_char_count: int
            - is_code_mixed: bool
            - confidence: float
    """
    if not text or not text.strip():
        return {
            "lang": "en",
            "telugu_char_count": 0,
            "latin_char_count": 0,
            "is_code_mixed": False,
            "confidence": 0.5,
        }

    clean_text = text.strip()
    telugu_matches = TELUGU_CHAR_PATTERN.findall(clean_text)
    latin_matches = LATIN_CHAR_PATTERN.findall(clean_text)

    telugu_count = len(telugu_matches)
    latin_count = len(latin_matches)
    total_alpha = telugu_count + latin_count

    if total_alpha == 0:
        # Punctuation or digits only, default to English
        return {
            "lang": "en",
            "telugu_char_count": 0,
            "latin_char_count": 0,
            "is_code_mixed": False,
            "confidence": 0.5,
        }

    is_mixed = telugu_count > 0 and latin_count > 0

    # If any meaningful Telugu characters are present, prioritize Telugu response
    if telugu_count > 0:
        telugu_ratio = telugu_count / total_alpha
        primary_lang = "te"
        conf = 0.6 + (0.4 * telugu_ratio)
    else:
        primary_lang = "en"
        conf = 0.95

    return {
        "lang": primary_lang,
        "telugu_char_count": telugu_count,
        "latin_char_count": latin_count,
        "is_code_mixed": is_mixed,
        "confidence": round(conf, 2),
    }
