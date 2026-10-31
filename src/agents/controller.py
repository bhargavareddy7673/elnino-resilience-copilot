"""Transparent Master Controller for Multilingual NLP Farm Advisor.

Coordinates:
1. NLP Pipeline: Language Detection, Normalization, Entity Extraction, Intent Classification.
2. Context Resolution: Merging query entities with active Farm Digital Twin parameters.
3. Live Weather Telemetry: Integrating existing Open-Meteo services without duplicate calls.
4. Specialist Routing:
   - Weather Agent (current weather, 7-day forecast, 30-day rain, dry spells)
   - Risk Analysis Agent (temperature risk, water stress)
   - Crop Advisory Agent (precautions, crop management, institutional references)
   - General Farm Digital Twin synthesis

Documents actual rule-based functions and does not claim to be an unconstrained black-box AGI.
"""

from typing import Dict, Any, Optional
import datetime

from src.nlp.language_detection import detect_language
from src.nlp.text_normalization import normalize_text
from src.nlp.entity_extractor import extract_entities
from src.nlp.intent_classifier import classify_intent, INTENT_DEFINITIONS

from src.weather.location_service import get_district_coordinates
from src.weather.weather_api import get_weather_intelligence
from src.agents.weather_agent import (
    answer_current_weather,
    answer_weather_forecast,
    answer_rainfall_status,
    answer_dry_spell_status,
)
from src.agents.risk_analysis_agent import (
    answer_temperature_risk,
    answer_water_stress,
)
from src.agents.crop_advisory_agent import answer_crop_advisory
from src.agents.simulation_agent import answer_simulation_query


def answer_general_farm_question(
    farm_profile: Dict[str, Any],
    location_name: str,
    lang: str = "en",
) -> Dict[str, Any]:
    """Synthesize active Farm Digital Twin profile attributes."""
    state = farm_profile.get("state", "Andhra Pradesh")
    district = farm_profile.get("district", "Kadapa (YSR Kadapa)")
    village = farm_profile.get("village", "").strip() or "Not specified"
    crop = farm_profile.get("crop", "Turmeric")
    land_area = farm_profile.get("land_area", 4.0)
    soil = farm_profile.get("soil_type", "Red Sandy Loam")
    irrigation = farm_profile.get("irrigation", "Borewell / Groundwater")
    sowing_raw = farm_profile.get("sowing_date")
    if sowing_raw:
        sowing_date_display = str(sowing_raw)
    else:
        sowing_date_display = "నమోదు చేయలేదు (Not set)" if lang == "te" else "Not set"

    grounding = {
        "state": state,
        "district": district,
        "village": village,
        "crop": crop,
        "land_area_acres": land_area,
        "soil_type": soil,
        "irrigation_source": irrigation,
        "sowing_date": sowing_date_display,
    }

    if lang == "te":
        resp = (
            f"🌾 **మీ ఫార్మ్ డిజిటల్ ట్విన్ (Farm Digital Twin) వివరాలు:**\n\n"
            f"- 📍 **ప్రాంతం:** `{district}`, {state} (గ్రామం: `{village}`)\n"
            f"- 🌿 **సాగు చేస్తున్న పంట:** `{crop}`\n"
            f"- 📐 **సాగు విస్తీర్ణం:** `{land_area:.2f} ఎకరాలు`\n"
            f"- 🏞️ **నేల రకం:** `{soil}`\n"
            f"- 💧 **నీటి పారుదల వనరు:** `{irrigation}`\n"
            f"- 📅 **విత్తిన/నాటిన తేదీ:** `{sowing_date_display}`\n\n"
            f"💡 ఈ వివరాల ఆధారంగానే వాతావరణ మరియు శీతోష్ణస్థితి సూచికలు లెక్కించబడుతున్నాయి."
        )
    else:
        resp = (
            f"🌾 **Farm Digital Twin Summary for Your Plot:**\n\n"
            f"- 📍 **Location:** `{district}`, {state} (Village: `{village}`)\n"
            f"- 🌿 **Selected Crop:** `{crop}`\n"
            f"- 📐 **Cultivated Area:** `{land_area:.2f} Acres`\n"
            f"- 🏞️ **Predominant Soil:** `{soil}`\n"
            f"- 💧 **Primary Water Source:** `{irrigation}`\n"
            f"- 📅 **Sowing/Plantation Date:** `{sowing_date_display}`\n\n"
            f"💡 Real-time weather intelligence and risk calculations are continuously synchronized with this profile."
        )

    return {"response": resp, "grounding_data": grounding}


def answer_unclear_question(
    raw_query: str,
    lang: str = "en",
) -> Dict[str, Any]:
    """Generate helpful clarification response when intent cannot be resolved."""
    if lang == "te":
        resp = (
            f"క్షమించండి, మీ ప్రశ్న సరిగా అర్థం కాలేదు. "
            f"నేను క్రింది అంశాలపై ఖచ్చితమైన వివరాలను అందించగలను:\n\n"
            f"1. 🌡️ **ప్రస్తుత ఉష్ణోగ్రత & వాతావరణం** (ఉదా: *'ప్రస్తుతం ఉష్ణోగ్రత ఎంత?'*)\n"
            f"2. 🌧️ **7 రోజుల వర్ష సూచన** (ఉదా: *'వచ్చే ఏడు రోజుల్లో వర్షం పడుతుందా?'*)\n"
            f"3. ☀️ **వర్షాభావ రోజుల వివరాలు** (ఉదా: *'ఎన్ని వర్షాభావ రోజులు గడిచాయి?'*)\n"
            f"4. 🌾 **పంట రక్షణ జాగ్రత్తలు** (ఉదా: *'నా పసుపు పంటకు ఎలాంటి జాగ్రత్తలు తీసుకోవాలి?'*)\n"
            f"5. 💧 **నీటి కొరత రిస్క్** (ఉదా: *'నా పంటకు నీటి కొరత ప్రమాదం ఉందా?'*)\n"
            f"6. 📍 **పొలం ప్రొఫైల్ వివరాలు** (ఉదా: *'నా పొలం వివరాలు చెప్పండి'*)"
        )
    else:
        resp = (
            f"I could not clearly identify the specific agricultural intent for your query. "
            f"As your Farm Advisor, I can assist you with:\n\n"
            f"1. 🌡️ **Current Weather & Temperatures** (e.g., *'What is the current temperature in my area?'*)\n"
            f"2. 🌧️ **7-Day Rain Forecast** (e.g., *'Will it rain in the next 7 days?'*)\n"
            f"3. ☀️ **Dry Spell Duration** (e.g., *'How many dry days have occurred?'*)\n"
            f"4. 🌿 **Crop Precautions & Care** (e.g., *'What precautions should I take for my banana crop?'*)\n"
            f"5. 💧 **Water Shortage & Soil Risk** (e.g., *'Is my paddy crop at risk of water shortage?'*)\n"
            f"6. 🌾 **Farm Digital Twin Details** (e.g., *'Tell me about my farm'*)"
        )

    return {"response": resp, "grounding_data": {"intent": "clarification_needed"}}


def process_farmer_query(
    query: str,
    farm_profile: Dict[str, Any],
    active_ui_lang: str = "en",
    simulation_state: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Process a user query through the NLP pipeline and route to the appropriate agent.
    
    Args:
        query: Raw string query entered by the farmer.
        farm_profile: Active digital twin dictionary from session state.
        active_ui_lang: Active UI language toggle ('en' or 'te').
        simulation_state: Optional active simulation bundle from session state.
        
    Returns:
        Structured response dictionary with response text, intent, detected language,
        grounding data, and academic references.
    """
    if not query or not query.strip():
        return answer_unclear_question("", lang=active_ui_lang)

    # Check Streamlit session state for active simulation if not passed explicitly
    if simulation_state is None:
        try:
            import streamlit as st
            if hasattr(st, "session_state") and "simulation_state" in st.session_state:
                simulation_state = st.session_state.get("simulation_state")
        except Exception:
            pass

    # 1. NLP Step 1: Language Detection
    lang_info = detect_language(query)
    # If the user typed in Telugu, respond in Telugu; otherwise use UI setting
    response_lang = lang_info["lang"] if lang_info["telugu_char_count"] > 0 else active_ui_lang

    # 2. NLP Step 2: Text Normalization
    normalized = normalize_text(query)

    # 3. NLP Step 3: Entity Extraction with Profile Fallback
    entities = extract_entities(query, farm_profile=farm_profile)
    crop = entities["crop"]
    target_district = entities["district"]
    target_state = farm_profile.get("state", "Andhra Pradesh")
    village = farm_profile.get("village", "").strip()

    # 4. NLP Step 4: Intent Classification
    classification = classify_intent(
        normalized_text=normalized,
        raw_text=query,
        extracted_entities=entities,
    )
    intent = classification["intent"]

    # 5. Coordinate Resolution & Weather Retrieval from Existing Stage 2 Service
    coords = get_district_coordinates(
        state=target_state,
        district=target_district,
        village=village,
    )
    weather_data = get_weather_intelligence(
        latitude=coords["latitude"],
        longitude=coords["longitude"],
        force_refresh=False,
    )

    location_name = target_district
    if village:
        location_name = f"{village}, {target_district}"

    # 6. Route to Specialist Agent
    grounding: Dict[str, Any] = {}
    references: list = []

    if intent == "current_weather":
        agent_res = answer_current_weather(
            weather_data=weather_data,
            location_name=location_name,
            lang=response_lang,
        )
        response_text = agent_res["response"]
        grounding = agent_res.get("grounding_data", {})

    elif intent == "weather_forecast":
        agent_res = answer_weather_forecast(
            weather_data=weather_data,
            location_name=location_name,
            crop=crop,
            lang=response_lang,
        )
        response_text = agent_res["response"]
        grounding = agent_res.get("grounding_data", {})

    elif intent == "rainfall_status":
        agent_res = answer_rainfall_status(
            weather_data=weather_data,
            location_name=location_name,
            crop=crop,
            lang=response_lang,
        )
        response_text = agent_res["response"]
        grounding = agent_res.get("grounding_data", {})

    elif intent == "dry_spell_status":
        agent_res = answer_dry_spell_status(
            weather_data=weather_data,
            location_name=location_name,
            crop=crop,
            lang=response_lang,
        )
        response_text = agent_res["response"]
        grounding = agent_res.get("grounding_data", {})

    elif intent == "temperature_risk":
        curr_temp = weather_data.get("current", {}).get("temperature") if weather_data.get("success", False) else None
        agent_res = answer_temperature_risk(
            forecast_df=weather_data.get("forecast_df"),
            historical_df=weather_data.get("historical_df"),
            farm_profile=farm_profile,
            current_temp=curr_temp,
            target_crop=crop,
            lang=response_lang,
        )
        response_text = agent_res["response"]
        grounding = agent_res.get("grounding_data", {})

    elif intent == "water_stress":
        curr_temp = weather_data.get("current", {}).get("temperature") if weather_data.get("success", False) else None
        agent_res = answer_water_stress(
            forecast_df=weather_data.get("forecast_df"),
            historical_df=weather_data.get("historical_df"),
            farm_profile=farm_profile,
            current_temp=curr_temp,
            target_crop=crop,
            lang=response_lang,
        )
        response_text = agent_res["response"]
        grounding = agent_res.get("grounding_data", {})

    elif intent == "crop_advisory":
        agent_res = answer_crop_advisory(
            farm_profile=farm_profile,
            weather_summary=weather_data.get("current", {}),
            target_crop=crop,
            lang=response_lang,
        )
        response_text = agent_res["response"]
        grounding = agent_res.get("grounding_data", {})
        references = agent_res.get("references", [])

    elif intent == "general_farm_question":
        agent_res = answer_general_farm_question(
            farm_profile=farm_profile,
            location_name=location_name,
            lang=response_lang,
        )
        response_text = agent_res["response"]
        grounding = agent_res.get("grounding_data", {})

    elif intent == "whatif_simulation":
        agent_res = answer_simulation_query(
            query=query,
            farm_profile=farm_profile,
            simulation_state=simulation_state,
            weather_data=weather_data,
            lang=response_lang,
        )
        response_text = agent_res["response"]
        grounding = agent_res.get("grounding_data", {})
        references = agent_res.get("references", [])

    else:
        # Fallback / Clarification
        agent_res = answer_unclear_question(raw_query=query, lang=response_lang)
        response_text = agent_res["response"]
        grounding = agent_res.get("grounding_data", {})

    return {
        "response_text": response_text,
        "intent": intent,
        "detected_language": response_lang,
        "is_code_mixed": lang_info["is_code_mixed"],
        "confidence": classification["confidence"],
        "entities": entities,
        "grounding_data": grounding,
        "references": references,
    }
