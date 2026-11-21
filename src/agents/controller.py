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

from typing import Dict, Any, List, Optional
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
from src.rag.synthesizer import FarmChatbotSynthesizer, get_retriever

# Global cached synthesizer instance
_SYNTHESIZER: Optional[FarmChatbotSynthesizer] = None


def get_synthesizer() -> FarmChatbotSynthesizer:
    """Retrieve or initialize the global singleton FarmChatbotSynthesizer."""
    global _SYNTHESIZER
    if _SYNTHESIZER is None:
        _SYNTHESIZER = FarmChatbotSynthesizer(get_retriever())
    return _SYNTHESIZER


def is_planning_or_resource_query(query: str) -> bool:
    """Detect if the query asks for farm resource planning, input budgeting, or contingencies."""
    q_low = query.lower()
    planning_tokens = [
        "plan", "planning", "resource", "resources", "budget", "budgeting",
        "schedule", "fertilizer", "fertilizers", "manure", "fym", "dosage",
        "allocation", "contingency", "el nino", "drought", "management", "cost", "input",
        "yerbulu", "yerubulu", "yeruvulu", "eruvulu", "eruvu", "yeruvu", "paspupanta", "paspu",
        "ప్రణాళిక", "ప్రణాళికలు", "బడ్జెట్", "వనరులు", "వనరుల", "ఎరువులు", "ఎరువుల",
        "నిర్వహణ", "షెడ్యూల్", "ఖర్చు", "కార్యాచరణ", "ఎల్ నినో", "వర్షాభావ"
    ]
    return any(token in q_low or token in query for token in planning_tokens)


def has_agricultural_context(query: str, crop: Optional[str] = None) -> bool:
    """Detect if query contains genuine agricultural, meteorological, or farm terminology."""
    q_low = query.lower()
    from src.nlp.text_normalization import normalize_text
    q_norm = normalize_text(query).lower()
    if crop and (crop.lower() in q_low or crop.lower() in q_norm):
        return True

    agri_terms = [
        "turmeric", "banana", "paddy", "rice", "curcuma", "musa", "oryza", "crop", "crops",
        "plant", "plants", "sucker", "suckers", "rhizome", "rhizomes", "seed", "seeds",
        "seedling", "panicle", "bunch", "tillering",
        "paspupanta", "paspu", "pasupu", "arati", "vari",
        "kasubuya", "kasubu", "kasupu", "pasupuya",
        "yerbulu", "yerubulu", "yeruvulu", "eruvulu", "eruvu", "yeruvu",
        "dumpakullu", "verukullu", "aakumacha", "mandarogam", "tegulu", "teguluki", "rogam", "roganiki", "puruguki",
        "mandu", "mandulu", "kottali", "kottala", "kattali", "pettali", "ivvali",
        "koto", "kotha", "koyyali", "koi", "arabalce", "arabettali", "aarabettali", "udikinchali",
        "పసుపు", "అరటి", "వరి", "పంట", "పంటలు", "మొక్క", "పిలక", "పిలకలు", "కొమ్ము",
        "కొమ్ములు", "విత్తనం", "విత్తనాలు", "ఈనిక", "పూత", "గెల",
        "soil", "sand", "sandy", "clay", "loam", "red soil", "black soil", "land", "acre",
        "acres", "field", "farm", "farming",
        "నేల", "మట్టి", "ఇసుక", "రేగడి", "ఎర్ర", "నల్ల", "భూమి", "పొలం", "చేను", "ఎకరం", "ఎకరాలు",
        "water", "irrigate", "irrigation", "drip", "borewell", "canal", "well", "flood",
        "moisture", "drainage", "awd",
        "నీరు", "నీళ్ళు", "నీళ్లు", "నీటి", "తడి", "తడులు", "డ్రిప్", "బిందు", "బోరు", "బోరుబావి",
        "బావి", "కాలువ", "మురుగు", "తేమ",
        "rain", "rainfall", "dry", "dry spell", "weather", "temperature", "heat", "monsoon",
        "drought", "climate", "el nino", "la nina",
        "వర్షం", "వాన", "వర్షపాతం", "వర్షాభావ", "ఎండ", "ఉష్ణోగ్రత", "వాతావరణం", "కరువు", "ఎల్ నినో",
        "fertilizer", "fertilizers", "manure", "fym", "urea", "dap", "potash", "npk", "nitrogen",
        "neem", "nutrient", "nutrients", "pest", "pests", "disease", "diseases", "rot", "blight",
        "bph", "borer", "weevil", "fungus", "spray", "spraying", "mulch", "mulching", "weed", "weeds",
        "ఎరువు", "ఎరువులు", "ఎరువుల", "పశువుల", "వేపపిండి", "యూరియా", "డీఏపీ", "పొటాష్",
        "నత్రజని", "భాస్వరం", "పోషకాలు", "పురుగు", "పురుగులు", "తెగులు", "తెగుళ్ళు",
        "దుంపకుళ్లు", "అగ్గితెగులు", "సుడిదోమ", "పిచికారీ", "మల్చింగ్", "కలుపు",
        "plan", "planning", "budget", "schedule", "contingency", "harvest", "harvesting", "yield",
        "precaution", "precautions", "care", "guide", "advisory",
        "ప్రణాళిక", "బడ్జెట్", "షెడ్యూల్", "దిగుబడి", "కోత", "జాగ్రత్తలు", "సలహా", "సూచనలు"
    ]
    return any(term in q_low or term in query or term in q_norm for term in agri_terms)


def answer_general_farm_question(
    farm_profile: Dict[str, Any],
    location_name: str,
    lang: str = "en",
) -> Dict[str, Any]:
    """Synthesize active Farm Digital Twin profile attributes."""
    state = farm_profile.get("state", "Andhra Pradesh")
    district = farm_profile.get("district", "Kurnool")
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
    chat_history: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Process a user query through the NLP pipeline and route to the appropriate agent.
    
    Args:
        query: Raw string query entered by the farmer.
        farm_profile: Active digital twin dictionary from session state.
        active_ui_lang: Active UI language toggle ('en' or 'te').
        simulation_state: Optional active simulation bundle from session state.
        chat_history: Optional multi-turn chat history for conversational continuity.
        
    Returns:
        Structured response dictionary with response text, intent, detected language,
        grounding data, and academic references.
    """
    if not query or not query.strip():
        unclear_res = answer_unclear_question("", lang=active_ui_lang)
        return {
            "response_text": unclear_res["response"],
            "intent": "unknown",
            "detected_language": active_ui_lang,
            "is_code_mixed": False,
            "confidence": 0.0,
            "entities": {
                "crop": farm_profile.get("crop", "Turmeric"),
                "district": farm_profile.get("district", "Kurnool"),
                "time_period": "general",
                "concepts": [],
            },
            "grounding_data": unclear_res.get("grounding_data", {"intent": "clarification_needed"}),
            "references": [],
        }

    try:
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
        # If user asked in Telugu (Unicode or Tanglish) or UI is in Telugu, answer in Telugu!
        response_lang = "te" if (lang_info["lang"] == "te" or active_ui_lang == "te") else "en"

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

        # 6. Route to Specialist Agent or Farm Chatbot Synthesizer
        grounding: Dict[str, Any] = {}
        references: list = []

        is_planning = is_planning_or_resource_query(query)

        if intent == "current_weather":
            agent_res = answer_current_weather(
                weather_data=weather_data,
                location_name=location_name,
                lang=response_lang,
            )
            response_text = agent_res["response"]
            grounding = agent_res.get("grounding_data", {})

        elif intent == "weather_forecast":
            if is_planning:
                synth = get_synthesizer()
                synth_res = synth.synthesize_response(
                    query=query,
                    farm_profile=farm_profile,
                    weather_intelligence=weather_data,
                    chat_history=chat_history,
                    lang=response_lang,
                    crop_override=crop if entities.get("crop_source") == "query" else None,
                )
                response_text = synth_res["response_text"]
                grounding = synth_res.get("grounding_data", {})
                references = synth_res.get("references", [])
                intent = "farm_chatbot_advisory"
            else:
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

        elif intent in ["crop_advisory", "irrigation_guidance", "irrigation_guide"]:
            # Check if this is a resource planning, fertilizer budgeting, or specialized agronomic topic query
            is_resource_or_fertilizer = any(
                k in query.lower() or k in query or k in normalized for k in [
                    "fertilizer", "fertilizers", "manure", "fym", "resource", "resources",
                    "budget", "budgeting", "ఎరువులు", "ఎరువుల", "వనరులు", "వనరుల", "బడ్జెట్",
                    "yerbulu", "yerubulu", "yeruvulu", "eruvulu", "eruvu", "yeruvu", "యూరియా", "వేపపిండి"
                ]
            )
            is_specialized_agri = any(
                k in query.lower() or k in query or k in normalized for k in [
                    "rot", "blight", "spot", "blotch", "wilt", "blast", "sigatoka", "pest", "pests", "borer",
                    "scale", "thrips", "bph", "weed", "weeds", "herbicide", "seed", "seeds", "sowing", "spacing",
                    "variety", "varieties", "harvest", "harvesting", "curing", "boil", "cure", "storage",
                    "spray", "spraying", "fungicide", "pesticide", "insecticide", "mandu", "mandulu", "kottali", "kottala",
                    "dumpakullu", "verukullu", "aakumacha", "mandarogam", "tegulu", "teguluki", "rogam", "roganiki", "puruguki",
                    "dumpakullu", "verukullu", "aakumacha", "mandarogam", "tegulu", "teguluki", "rogam", "roganiki", "puruguki",
        "mandu", "mandulu", "kottali", "kottala", "kattali", "pettali", "ivvali",
        "koto", "kotha", "koyyali", "koi", "arabalce", "arabettali", "aarabettali", "udikinchali",
                    "kasubuya", "kasubu", "kasupu", "water", "irrigate", "irrigation", "kattali", "pettali", "ivvali",
                    "తెగులు", "తెగుళ్ళు", "పురుగు", "పురుగులు", "కలుపు", "విత్తన", "నాటడం", "కోత", "నిల్వ", "పిచికారీ", "మందు"
                ]
            )
            if is_resource_or_fertilizer or (is_planning and entities.get("topic") != "Water management"):
                synth = get_synthesizer()
                synth_res = synth.synthesize_response(
                    query=query,
                    farm_profile=farm_profile,
                    weather_intelligence=weather_data,
                    chat_history=chat_history,
                    lang=response_lang,
                    crop_override=crop if entities.get("crop_source") == "query" else None,
                )
                response_text = synth_res["response_text"]
                grounding = synth_res.get("grounding_data", {})
                references = synth_res.get("references", [])
                intent = "farm_chatbot_advisory"
            elif is_specialized_agri:
                synth = get_synthesizer()
                synth_res = synth.synthesize_response(
                    query=query,
                    farm_profile=farm_profile,
                    weather_intelligence=weather_data,
                    chat_history=chat_history,
                    lang=response_lang,
                    crop_override=crop if entities.get("crop_source") == "query" else None,
                )
                response_text = synth_res["response_text"]
                grounding = synth_res.get("grounding_data", {})
                references = synth_res.get("references", [])
                intent = "crop_advisory"
            else:
                agent_res = answer_crop_advisory(
                    farm_profile=farm_profile,
                    weather_summary=weather_data.get("current", {}),
                    target_crop=crop,
                    query=query,
                    topic=entities.get("topic", "General agronomy"),
                    lang=response_lang,
                )
                response_text = agent_res["response"]
                grounding = agent_res.get("grounding_data", {})
                references = agent_res.get("references", [])

        elif intent == "general_farm_question":
            if is_planning:
                synth = get_synthesizer()
                synth_res = synth.synthesize_response(
                    query=query,
                    farm_profile=farm_profile,
                    weather_intelligence=weather_data,
                    chat_history=chat_history,
                    lang=response_lang,
                    crop_override=crop if entities.get("crop_source") == "query" else None,
                )
                response_text = synth_res["response_text"]
                grounding = synth_res.get("grounding_data", {})
                references = synth_res.get("references", [])
                intent = "farm_chatbot_advisory"
            else:
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
            # Fallback / General Agricultural Chatbot Resolution
            crop_kw = crop if entities.get("crop_source") == "query" else None
            is_agri = has_agricultural_context(query, crop=crop_kw)
            
            if is_agri:
                synth = get_synthesizer()
                synth_res = synth.synthesize_response(
                    query=query,
                    farm_profile=farm_profile,
                    weather_intelligence=weather_data,
                    chat_history=chat_history,
                    lang=response_lang,
                    crop_override=crop_kw,
                )
                response_text = synth_res["response_text"]
                grounding = synth_res.get("grounding_data", {})
                references = synth_res.get("references", [])
                intent = "farm_chatbot_advisory"
                classification["confidence"] = 0.85
            else:
                agent_res = answer_unclear_question(raw_query=query, lang=response_lang)
                response_text = agent_res["response"]
                grounding = agent_res.get("grounding_data", {})
                intent = "unknown"

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
    except Exception as exc:
        err_msg_te = "క్షమించండి, మీ ప్రశ్నను విశ్లేషించడంలో సమస్య ఎదురైంది. దయచేసి కొద్దిసేపటి తర్వాత మళ్లీ ప్రయత్నించండి."
        err_msg_en = "I encountered an issue analyzing your request. Please check your question or try again in a moment."
        return {
            "response_text": err_msg_te if active_ui_lang == "te" else err_msg_en,
            "intent": "unknown",
            "detected_language": active_ui_lang,
            "is_code_mixed": False,
            "confidence": 0.0,
            "entities": {
                "crop": farm_profile.get("crop", "Turmeric"),
                "district": farm_profile.get("district", "Kurnool"),
                "time_period": "general",
                "concepts": [],
            },
            "grounding_data": {"status": "error", "error_type": type(exc).__name__},
            "references": [],
        }
