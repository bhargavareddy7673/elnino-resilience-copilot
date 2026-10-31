"""Text normalization for English, Telugu, and code-mixed agricultural queries.

Performs case folding, punctuation removal, whitespace canonicalization,
and phonetic token mapping for transliterated agricultural terms.
"""

import re
from typing import Dict


# Common phonetic transliterations of Telugu agricultural words in Latin script
TRANSLITERATION_MAP: Dict[str, str] = {
    "pasupu": "turmeric",
    "pasupupanta": "turmeric",
    "arati": "banana",
    "aratithota": "banana",
    "vari": "paddy",
    "varipanta": "paddy",
    "varsham": "rain",
    "vaana": "rain",
    "yenda": "heat",
    "enda": "heat",
    "neeru": "water",
    "neellu": "water",
    "nela": "soil",
    "bhoomi": "soil",
    "thadi": "irrigation",
    "roju": "day",
    "rojulu": "days",
}

# Punctuation stripper preserving Telugu diacritics and alphanumeric characters
CLEAN_PUNCT_PATTERN = re.compile(r"[^\w\s\u0c00-\u0c7f]")


def normalize_text(text: str) -> str:
    """Normalize user input text for downstream NLP processing.
    
    Args:
        text: Raw user question string.
        
    Returns:
        Cleaned, normalized string with uniform whitespace and lowercased Latin characters.
    """
    if not text:
        return ""

    # 1. Clean punctuation while retaining Telugu unicode characters
    cleaned = CLEAN_PUNCT_PATTERN.sub(" ", text)

    # 2. Lowercase Latin characters
    cleaned = cleaned.lower()

    # 3. Canonicalize multiple spaces
    tokens = cleaned.split()

    # 4. Optional phonetic replacement for transliterated Telugu words in Latin script
    mapped_tokens = []
    for token in tokens:
        mapped_token = TRANSLITERATION_MAP.get(token, token)
        mapped_tokens.append(mapped_token)

    return " ".join(mapped_tokens)
