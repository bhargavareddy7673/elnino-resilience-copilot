"""Text normalization for English, Telugu, and code-mixed agricultural queries.

Performs case folding, punctuation removal, whitespace canonicalization,
morphological stem/suffix decomposition, phonetic mapping, and fuzzy matching
for spoken, dialectal, and transliterated agricultural terms.
"""

import re
import difflib
from typing import Dict, List, Optional


# Comprehensive phonetic transliteration map for Telugu agricultural vocabulary
TRANSLITERATION_MAP: Dict[str, str] = {
    # Turmeric & crops
    "pasupu": "turmeric",
    "paspu": "turmeric",
    "paspupanta": "turmeric crop",
    "paspupantaku": "turmeric crop to",
    "paspupantako": "turmeric crop to",
    "paspupantaki": "turmeric crop to",
    "pasupupanta": "turmeric crop",
    "pasupupantaku": "turmeric crop to",
    "pasupupantaki": "turmeric crop to",
    "pasupuki": "turmeric to",
    "pasupuku": "turmeric to",
    "pasupulo": "turmeric in",
    "paspulo": "turmeric in",
    "kasubuya": "turmeric",
    "kasubu": "turmeric",
    "kasupu": "turmeric",
    "pasupuya": "turmeric",
    "tumeric": "turmeric",
    "tumerik": "turmeric",
    "turmaric": "turmeric",
    "turmarick": "turmeric",
    "arati": "banana",
    "ariti": "banana",
    "aratithota": "banana orchard",
    "aratiki": "banana to",
    "aratiku": "banana to",
    "aratilo": "banana in",
    "vari": "paddy",
    "varipanta": "paddy crop",
    "variki": "paddy to",
    "variku": "paddy to",
    "varilo": "paddy in",

    # Harvesting, Curing & Drying
    "koto": "harvest",
    "kotha": "harvest",
    "kota": "harvest",
    "koyyali": "harvest",
    "koyali": "harvest",
    "koi": "harvest",
    "koy": "harvest",
    "thavvali": "harvest",
    "tavvali": "harvest",
    "tavvadam": "harvest",
    "arabalce": "dry",
    "arabettali": "dry",
    "aarabettali": "dry",
    "arabetali": "dry",
    "aarabetali": "dry",
    "arabeeyali": "dry",
    "endabettali": "dry",
    "yendabettali": "dry",
    "endaniyali": "dry",
    "curing": "curing",
    "boil": "boil",
    "boiling": "boil",
    "udikinchali": "curing",
    "udakabettali": "curing",
    "udikichali": "curing",
    "polishing": "polishing",
    "polish": "polishing",

    # Fertilizers & nutrients
    "yerbulu": "fertilizer",
    "yerubulu": "fertilizer",
    "yeruvulu": "fertilizer",
    "yeruvu": "fertilizer",
    "eruvulu": "fertilizer",
    "eruvu": "fertilizer",
    "eruvulanu": "fertilizer",
    "yeruvulanu": "fertilizer",
    "eruvula": "fertilizer",
    "yeruvula": "fertilizer",
    "manure": "fertilizer",
    "fym": "fertilizer",
    "compost": "compost",
    "kompost": "compost",
    "vermicompost": "vermicompost",
    "neem": "neem",
    "vepapindi": "neem cake",
    "urea": "urea",
    "dap": "dap",
    "potash": "potash",
    "mop": "potash",
    "ssp": "phosphorus",
    "poshakalu": "nutrients",
    "poshakamulu": "nutrients",

    # Diseases, Pathology & Fungicides
    "dumpakullu": "rhizome rot",
    "dumpa kullu": "rhizome rot",
    "verukullu": "root rot",
    "veru kullu": "root rot",
    "mandarogam": "rhizome rot",
    "manda rogam": "rhizome rot",
    "aakumacha": "leaf spot",
    "aaku macha": "leaf spot",
    "tegulu": "disease",
    "teguluki": "disease to",
    "teguluku": "disease to",
    "tegulanu": "disease",
    "rogam": "disease",
    "roganiki": "disease to",
    "rogamu": "disease",
    "blight": "blight",
    "rot": "rot",
    "wilt": "wilt",
    "blast": "blast",
    "sigatoka": "sigatoka",
    "sheath blight": "sheath blight",
    "fungicide": "fungicide",
    "fungus": "fungus",

    # Pests, Insects & Insecticides
    "purugu": "pest",
    "purugulu": "pests",
    "puruguki": "pest to",
    "puruguku": "pest to",
    "purugulaku": "pests to",
    "sudidoma": "bph brown planthopper",
    "sudi doma": "bph brown planthopper",
    "tamarapurugu": "thrips",
    "tamara purugu": "thrips",
    "telladoma": "whitefly",
    "tella doma": "whitefly",
    "borer": "stem borer",
    "shoot borer": "shoot borer",
    "scale": "rhizome scale",
    "weevil": "weevil",
    "pesticide": "pesticide",
    "insecticide": "insecticide",
    "keetam": "pest",
    "keetakamulu": "pests",

    # Sprays, Medicines & Herbicides
    "mandu": "medicine spray",
    "mandulu": "medicines spray",
    "mandhu": "medicine spray",
    "spray": "spray",
    "spraying": "spray",
    "picikari": "spray",
    "pichikari": "spray",
    "kottali": "spray apply",
    "kottala": "spray apply",
    "kottadam": "spray apply",
    "kalupu": "weed",
    "kalupumandu": "herbicide weedicide",
    "kalupu mandu": "herbicide weedicide",
    "weedicide": "herbicide",
    "herbicide": "herbicide",
    "atrazine": "atrazine herbicide",
    "pendimethalin": "pendimethalin herbicide",

    # Irrigation & Water Management
    "water": "water",
    "neeru": "water",
    "neellu": "water",
    "neeti": "water",
    "thadi": "irrigation",
    "tadi": "irrigation",
    "thadulu": "irrigation",
    "tadulu": "irrigation",
    "irrigate": "irrigation",
    "irrigation": "irrigation",
    "kattali": "irrigate water",
    "pettali": "irrigate apply",
    "ivvali": "irrigate give",
    "drip": "drip",
    "borewell": "borewell",
    "bore": "borewell",
    "baavi": "well",
    "bavi": "well",

    # Seeds, Varieties & Sowing
    "vithanam": "seed",
    "vithanalu": "seeds",
    "vithana": "seed",
    "natadam": "sowing planting",
    "nattadam": "sowing planting",
    "veydam": "sowing planting",
    "rakalu": "varieties",
    "variety": "variety",
    "varieties": "varieties",
    "spacing": "spacing",
    "salu": "row spacing",
    "dubbara": "seed rate spacing",

    # Action & timing words
    "pudo": "when",
    "epudo": "when",
    "yopude": "when",
    "yopudu": "when",
    "yepude": "when",
    "yepudu": "when",
    "eppudu": "when",
    "eppude": "when",
    "yeppudu": "when",
    "epudu": "when",
    "eppatiki": "when",
    "ela": "how",
    "yela": "how",
    "yem": "what",
    "emi": "what",
    "em": "what",
    "enti": "what",
    "yali": "apply",
    "hali": "apply",
    "vali": "apply",
    "veyyali": "apply",
    "veyali": "apply",
    "veyaali": "apply",
    "veyala": "apply",
    "eyyali": "apply",
    "eyali": "apply",
    "cheyyali": "do",
    "cheyali": "do",

    # Pronouns & Prepositions
    "naha": "my",
    "na": "my",
    "naa": "my",
    "ko": "to",
    "ki": "to",
    "ku": "to",
    "lo": "in",
    "la": "in",

    # Weather & agronomic terms
    "varsham": "rain",
    "vaana": "rain",
    "yenda": "heat",
    "enda": "heat",
    "nela": "soil",
    "bhoomi": "soil",
    "matti": "soil",
    "roju": "day",
    "rojulu": "days",
    "panta": "crop",
    "pantaku": "crop to",
    "pantaki": "crop to",
    "thota": "orchard",
}

# Suffix decomposition patterns for compound vernacular words
COMMON_SUFFIXES = [
    ("panta", " panta"),
    ("thota", " thota"),
    ("mandulu", " mandu"),
    ("mandu", " mandu"),
    ("kullu", " kullu"),
    ("macha", " macha"),
    ("rogam", " rogam"),
    ("tegulu", " tegulu"),
    ("purugu", " purugu"),
    ("kottali", " kottali"),
    ("pettali", " pettali"),
    ("veyyali", " veyyali"),
    ("koyyali", " koyyali"),
    ("kattali", " kattali"),
]

# Punctuation stripper preserving Telugu diacritics and alphanumeric characters
CLEAN_PUNCT_PATTERN = re.compile(r"[^\w\s\u0c00-\u0c7f]")


def _phonetic_preclean(token: str) -> str:
    """Apply deterministic phonetic canonicalization on unknown tokens."""
    t = token
    # Strip initial 'y' before 'e', 'o'
    if len(t) > 2 and t[0] == "y" and t[1] in ("e", "o"):
        t = t[1:]
    # Replace 'b' with 'v' if preceded or followed by vowel (e.g. yerbulu -> ervulu)
    if "rbul" in t:
        t = t.replace("rbul", "ruvulu")
    return t


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

    # 4. Decompose compound tokens & apply phonetic mapping
    mapped_tokens = []
    keys_list = list(TRANSLITERATION_MAP.keys())

    for token in tokens:
        # Check direct exact match
        if token in TRANSLITERATION_MAP:
            mapped_tokens.append(TRANSLITERATION_MAP[token])
            continue

        # Check morphological decomposition (compound words like 'pasupupantaki', 'dumpakullurogam')
        decomposed = token
        for suf_raw, suf_rep in COMMON_SUFFIXES:
            if decomposed.endswith(suf_raw) and len(decomposed) > len(suf_raw):
                decomposed = decomposed[:-len(suf_raw)] + suf_rep
                break

        if decomposed != token:
            sub_tokens = decomposed.split()
            sub_mapped = []
            for st in sub_tokens:
                sub_mapped.append(TRANSLITERATION_MAP.get(st, st))
            mapped_tokens.append(" ".join(sub_mapped))
            continue

        # Check phonetic pre-cleaning
        cleaned_t = _phonetic_preclean(token)
        if cleaned_t in TRANSLITERATION_MAP:
            mapped_tokens.append(TRANSLITERATION_MAP[cleaned_t])
            continue

        # Check fuzzy matching against known vocabulary (cutoff 0.76)
        close_matches = difflib.get_close_matches(token, keys_list, n=1, cutoff=0.76)
        if close_matches:
            best_match = close_matches[0]
            mapped_tokens.append(TRANSLITERATION_MAP[best_match])
            continue

        mapped_tokens.append(token)

    return " ".join(mapped_tokens)
