"""Entity extraction for agricultural concepts, crops, districts, and time periods.

Extracts:
1. Crop (Turmeric, Banana, Paddy, or Telugu equivalents పసుపు, అరటి, వరి).
2. District (All 26 AP & 33 TS districts).
3. Time Period (current, tomorrow, next 7 days, last 30 days).
4. Weather Concepts (temperature, rainfall, dry spell, humidity, water stress).

Gracefully falls back to the active Farm Digital Twin profile when entities
are omitted in context-dependent questions (e.g., "Will it rain here?").
"""

import re
from typing import Dict, Any, Optional
from src.config import STATE_DISTRICT_MAP


# Crop mappings
CROP_ENTITY_MAP: Dict[str, str] = {
    # English
    "turmeric": "Turmeric",
    "curcuma": "Turmeric",
    # Telugu
    "పసుపు": "Turmeric",
    "పసుపుపంట": "Turmeric",
    # Transliterated
    "pasupu": "Turmeric",

    # Banana
    "banana": "Banana",
    "musa": "Banana",
    "plantain": "Banana",
    "అరటి": "Banana",
    "అరటితోట": "Banana",
    "arati": "Banana",

    # Paddy
    "paddy": "Paddy",
    "rice": "Paddy",
    "oryza": "Paddy",
    "వరి": "Paddy",
    "వరిపంట": "Paddy",
    "vari": "Paddy",
}

# Weather concept keyword mappings
CONCEPT_MAP: Dict[str, str] = {
    # Temperature
    "temperature": "temperature",
    "temp": "temperature",
    "heat": "temperature",
    "hot": "temperature",
    "warm": "temperature",
    "ఉష్ణోగ్రత": "temperature",
    "ఉష్ణోగ్రతలు": "temperature",
    "వేడి": "temperature",
    "ఎండ": "temperature",
    "తాపం": "temperature",

    # Rainfall
    "rain": "rainfall",
    "rainfall": "rainfall",
    "precipitation": "rainfall",
    "rains": "rainfall",
    "raining": "rainfall",
    "వర్షం": "rainfall",
    "వాన": "rainfall",
    "వర్షపాతం": "rainfall",
    "వర్షాలు": "rainfall",

    # Dry Spell
    "dry spell": "dry_spell",
    "dry days": "dry_spell",
    "dry day": "dry_spell",
    "dryness": "dry_spell",
    "no rain": "dry_spell",
    "వర్షాభావం": "dry_spell",
    "వర్షం లేని రోజులు": "dry_spell",
    "వర్షాభావ": "dry_spell",
    "ఎండగట్టిన": "dry_spell",

    # Humidity
    "humidity": "humidity",
    "relative humidity": "humidity",
    "moisture in air": "humidity",
    "తేమ": "humidity",
    "గాలిలో తేమ": "humidity",

    # Water Stress / Irrigation
    "water": "water_stress",
    "water stress": "water_stress",
    "water deficit": "water_stress",
    "irrigation": "water_stress",
    "soil moisture": "water_stress",
    "నీరు": "water_stress",
    "నీటి కొరత": "water_stress",
    "నీటి ఎద్దడి": "water_stress",
    "నీటి అవసరం": "water_stress",
    "తడి": "water_stress",
    "తడులు": "water_stress",
}


def extract_entities(
    text: str,
    farm_profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Extract agricultural domain entities from user text with farm profile fallback.
    
    Args:
        text: Normalized or raw user query text.
        farm_profile: Active digital twin profile for contextual fallback.
        
    Returns:
        Dictionary of extracted entities:
            - crop: str
            - crop_source: 'query' or 'profile_fallback'
            - district: str
            - district_source: 'query' or 'profile_fallback'
            - time_period: str ('current', 'tomorrow', 'next_7_days', 'last_30_days', 'general')
            - concepts: List[str]
    """
    raw_lower = text.lower() if text else ""
    profile = farm_profile or {}

    # 1. Extract Crop
    detected_crop = None
    crop_source = "profile_fallback"

    for token, canonical_crop in CROP_ENTITY_MAP.items():
        # Match as substring or token
        if token in text or token in raw_lower:
            detected_crop = canonical_crop
            crop_source = "query"
            break

    if not detected_crop:
        detected_crop = profile.get("crop", "Turmeric")

    # 2. Extract District
    detected_district = None
    district_source = "profile_fallback"

    all_districts = STATE_DISTRICT_MAP.get("Andhra Pradesh", []) + STATE_DISTRICT_MAP.get("Telangana", [])
    for d in all_districts:
        d_clean = d.split("(")[0].strip().lower()
        if d_clean in raw_lower:
            detected_district = d
            district_source = "query"
            break
        # Also check inside parentheses (e.g. YSR Kadapa)
        if "(" in d and ")" in d:
            inner = d.split("(")[1].split(")")[0].strip().lower()
            if inner in raw_lower:
                detected_district = d
                district_source = "query"
                break

    # Check common Telugu district names
    telugu_district_map = {
        "కడప": "Kadapa (YSR Kadapa)",
        "వైఎస్ఆర్ కడప": "Kadapa (YSR Kadapa)",
        "అనంతపురం": "Ananthapuramu",
        "కర్నూలు": "Kurnool",
        "చిత్తూరు": "Chittoor",
        "గుంటూరు": "Guntur",
        "కృష్ణా": "Krishna",
        "వరంగల్": "Warangal",
        "ఖమ్మం": "Khammam",
        "కరీంనగర్": "Karimnagar",
        "హైదరాబాద్": "Hyderabad",
        "నిజామాబాద్": "Nizamabad",
    }
    for te_name, canon_name in telugu_district_map.items():
        if te_name in text:
            detected_district = canon_name
            district_source = "query"
            break

    if not detected_district:
        detected_district = profile.get("district", "Kadapa (YSR Kadapa)")

    # 3. Extract Time Period
    time_period = "general"
    if any(k in raw_lower for k in ["today", "now", "current", "right now", "at present"]) or any(
        k in text for k in ["ప్రస్తుతం", "ఈరోజు", "నేడు", "ఇప్పుడు"]
    ):
        time_period = "current"
    elif any(k in raw_lower for k in ["tomorrow", "next day"]) or "రేపు" in text:
        time_period = "tomorrow"
    elif any(k in raw_lower for k in ["7 days", "seven days", "week", "forecast", "upcoming", "coming days"]) or any(
        k in text for k in ["రాబోయే", "వచ్చే వారం", "వచ్చే 7 రోజులు", "ఏడు రోజులు", "వచ్చే ఏడు రోజుల్లో"]
    ):
        time_period = "next_7_days"
    elif any(k in raw_lower for k in ["30 days", "past month", "recent days", "last 30 days", "last month"]) or any(
        k in text for k in ["గత 30 రోజులు", "గత నెల", "30 రోజుల్లో"]
    ):
        time_period = "last_30_days"

    # 4. Extract Weather Concepts
    detected_concepts = set()
    for token, concept in CONCEPT_MAP.items():
        if token in raw_lower or token in text:
            detected_concepts.add(concept)

    return {
        "crop": detected_crop,
        "crop_source": crop_source,
        "district": detected_district,
        "district_source": district_source,
        "time_period": time_period,
        "concepts": list(detected_concepts),
    }
