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


# Crop mappings with common spelling variations and transliterations
CROP_ENTITY_MAP: Dict[str, str] = {
    # Turmeric (Curcuma longa)
    "turmeric": "Turmeric",
    "curcuma": "Turmeric",
    "tumeric": "Turmeric",
    "tumerik": "Turmeric",
    "turmaric": "Turmeric",
    "turmarick": "Turmeric",
    "పసుపు": "Turmeric",
    "పసుపుపంట": "Turmeric",
    "పసుపుకు": "Turmeric",
    "pasupu": "Turmeric",
    "paspu": "Turmeric",
    "paspupanta": "Turmeric",
    "paspupantaku": "Turmeric",
    "paspupantako": "Turmeric",
    "pasupupanta": "Turmeric",
    "pasupupantaku": "Turmeric",
    "pasupuki": "Turmeric",
    "pasupuku": "Turmeric",
    "kasubuya": "Turmeric",
    "kasubu": "Turmeric",
    "kasupu": "Turmeric",
    "pasupuya": "Turmeric",

    # Banana (Musa acuminata)
    "banana": "Banana",
    "bananna": "Banana",
    "musa": "Banana",
    "plantain": "Banana",
    "అరటి": "Banana",
    "అరటితోట": "Banana",
    "arati": "Banana",
    "ariti": "Banana",
    "aratithota": "Banana",

    # Paddy (Oryza sativa)
    "paddy": "Paddy",
    "rice": "Paddy",
    "oryza": "Paddy",
    "వరి": "Paddy",
    "వరిపంట": "Paddy",
    "vari": "Paddy",
    "varipanta": "Paddy",
}

# Weather & agronomic concept keyword mappings
CONCEPT_MAP: Dict[str, str] = {
    # Temperature & Heat
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

    # Water Stress (Risk / Deficit / Drought)
    "water stress": "water_stress",
    "water deficit": "water_stress",
    "water shortage": "water_stress",
    "soil moisture deficit": "water_stress",
    "నీటి కొరత": "water_stress",
    "నీటి ఎద్దడి": "water_stress",
    "నీటి సమస్య": "water_stress",

    # Irrigation & Water Management
    "irrigate": "irrigation",
    "irrigating": "irrigation",
    "irrigation": "irrigation",
    "water": "water_management",
    "watering": "irrigation",
    "water need": "irrigation",
    "water needs": "irrigation",
    "water requirement": "irrigation",
    "water schedule": "irrigation",
    "irrigation schedule": "irrigation",
    "manage water": "water_management",
    "water management": "water_management",
    "soil moisture": "irrigation",
    "నీరు": "irrigation",
    "నీళ్లు": "irrigation",
    "నీళ్ళు": "irrigation",
    "నీటి": "irrigation",
    "నీరు పెట్టాలి": "irrigation",
    "నీరు ఎప్పుడు పెట్టాలి": "irrigation",
    "నీటి యాజమాన్యం": "water_management",
    "నీటి అవసరం": "irrigation",
    "తడి": "irrigation",
    "తడులు": "irrigation",

    # Fertilizers & Nutrition Planning
    "fertilizer": "fertilizer",
    "fertilizers": "fertilizer",
    "manure": "fertilizer",
    "fym": "fertilizer",
    "yerbulu": "fertilizer",
    "yerubulu": "fertilizer",
    "yeruvulu": "fertilizer",
    "eruvulu": "fertilizer",
    "eruvu": "fertilizer",
    "urea": "fertilizer",
    "dap": "fertilizer",
    "potash": "fertilizer",
    "neem": "fertilizer",
    "vepapindi": "fertilizer",
    "ఎరువులు": "fertilizer",
    "ఎరువు": "fertilizer",
    "ఎరువుల": "fertilizer",
    "యూరియా": "fertilizer",
    "డిఎపి": "fertilizer",
    "పొటాష్": "fertilizer",
    "వేపపిండి": "fertilizer",

    # Harvesting & Curing
    "harvest": "harvesting",
    "harvesting": "harvesting",
    "curing": "curing",
    "boil": "curing",
    "boiling": "curing",
    "dry": "curing",
    "drying": "curing",
    "koto": "harvesting",
    "kotha": "harvesting",
    "koyyali": "harvesting",
    "koi": "harvesting",
    "arabalce": "curing",
    "arabettali": "curing",
    "aarabettali": "curing",
    "udikinchali": "curing",
    "కోత": "harvesting",
    "ఉడకబెట్టడం": "curing",
    "ఆరబెట్టడం": "curing",

    # Pathology & Diseases
    "disease": "disease",
    "diseases": "disease",
    "rot": "disease",
    "blight": "disease",
    "spot": "disease",
    "blotch": "disease",
    "wilt": "disease",
    "blast": "disease",
    "sigatoka": "disease",
    "fungicide": "disease",
    "fungus": "disease",
    "dumpakullu": "disease",
    "verukullu": "disease",
    "aakumacha": "disease",
    "mandarogam": "disease",
    "tegulu": "disease",
    "teguluki": "disease",
    "teguluku": "disease",
    "rogam": "disease",
    "roganiki": "disease",
    "తెగులు": "disease",
    "తెగుళ్ళు": "disease",
    "కుళ్లు": "disease",
    "మచ్చ": "disease",
    "దుంపకుళ్లు": "disease",
    "వేరుకుళ్లు": "disease",

    # Entomology & Pests
    "pest": "pest",
    "pests": "pest",
    "insect": "pest",
    "insects": "pest",
    "borer": "pest",
    "scale": "pest",
    "thrips": "pest",
    "aphid": "pest",
    "bph": "pest",
    "weevil": "pest",
    "caterpillar": "pest",
    "pesticide": "pest",
    "insecticide": "pest",
    "purugu": "pest",
    "purugulu": "pest",
    "puruguki": "pest",
    "puruguku": "pest",
    "sudidoma": "pest",
    "tamarapurugu": "pest",
    "telladoma": "pest",
    "పురుగు": "pest",
    "పురుగులు": "pest",
    "సుడిదోమ": "pest",
    "తామర పురుగు": "pest",
    "తెల్లదోమ": "pest",

    # Weeds & Herbicides
    "weed": "weed",
    "weeds": "weed",
    "herbicide": "weed",
    "weedicide": "weed",
    "weeding": "weed",
    "atrazine": "weed",
    "pendimethalin": "weed",
    "kalupu": "weed",
    "kalupumandu": "weed",
    "కలుపు": "weed",
    "కలుపు మందు": "weed",

    # Seeds, Sowing & Spacing
    "seed": "seed_sowing",
    "seeds": "seed_sowing",
    "sowing": "seed_sowing",
    "planting": "seed_sowing",
    "spacing": "seed_sowing",
    "variety": "seed_sowing",
    "varieties": "seed_sowing",
    "vithanam": "seed_sowing",
    "vithanalu": "seed_sowing",
    "natadam": "seed_sowing",
    "rakalu": "seed_sowing",
    "salu": "seed_sowing",
    "dubbara": "seed_sowing",
    "విత్తనం": "seed_sowing",
    "విత్తనాలు": "seed_sowing",
    "నాటడం": "seed_sowing",
    "రకాలు": "seed_sowing",

    # Sprays & Medicine
    "spray": "spray",
    "spraying": "spray",
    "mandu": "spray",
    "mandulu": "spray",
    "mandhu": "spray",
    "kottali": "spray",
    "picikari": "spray",
    "pichikari": "spray",
    "పిచికారీ": "spray",
    "మందు": "spray",
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

    from src.nlp.text_normalization import normalize_text
    norm_lower = normalize_text(text).lower() if text else ""

    # 1. Extract Crop
    detected_crop = None
    crop_source = "profile_fallback"

    for token, canonical_crop in CROP_ENTITY_MAP.items():
        # Match as substring or token in raw, telugu, or normalized text
        if token in text or token in raw_lower or token in norm_lower:
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
        detected_district = profile.get("district", "Kurnool")

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

    # 4. Extract Weather & Agronomic Concepts
    detected_concepts = set()
    for token, concept in CONCEPT_MAP.items():
        if token in raw_lower or token in text or token in norm_lower:
            detected_concepts.add(concept)

    # 5. Determine Topic & Inferred Intent
    # Topic detection
    is_irrigation_query = any(k in raw_lower for k in [
        "irrigate", "irrigation", "water turmeric", "water banana", "water paddy", "water crop",
        "how often should i water", "how much water", "when should i irrigate", "when to irrigate",
        "irrigation schedule", "needs water", "manage water", "water management", "water requirement"
    ]) or any(k in text for k in [
        "నీరు ఎప్పుడు పెట్టాలి", "ఎంత నీరు అవసరం", "నీటి యాజమాన్యం", "నీరు పెట్టాలి", "నీరు ఎలా పెట్టాలి",
        "తడి ఎప్పుడు ఇవ్వాలి", "తడులు"
    ]) or "irrigation" in detected_concepts or "water_management" in detected_concepts

    if is_irrigation_query:
        topic = "Water management"
        inferred_intent = "Irrigation guidance"
    elif "water_stress" in detected_concepts or any(k in raw_lower for k in ["water shortage", "water deficit", "water stress"]) or any(k in text for k in ["నీటి కొరత", "నీటి ఎద్దడి"]):
        topic = "Water stress evaluation"
        inferred_intent = "Water stress"
    elif "temperature" in detected_concepts or any(k in raw_lower for k in ["heat", "temperature", "too hot"]):
        topic = "Thermal management"
        inferred_intent = "Temperature risk"
    elif "rainfall" in detected_concepts or "rain" in raw_lower:
        topic = "Rainfall monitoring"
        inferred_intent = "Weather forecast" if time_period in ["next_7_days", "tomorrow"] else "Rainfall status"
    elif "dry_spell" in detected_concepts:
        topic = "Dry spell assessment"
        inferred_intent = "Dry spell status"
    else:
        topic = "General agronomy"
        inferred_intent = "Crop advisory"

    return {
        "crop": detected_crop,
        "crop_source": crop_source,
        "district": detected_district,
        "district_source": district_source,
        "time_period": time_period,
        "concepts": sorted(list(detected_concepts)),
        "topic": topic,
        "intent": inferred_intent,
    }
