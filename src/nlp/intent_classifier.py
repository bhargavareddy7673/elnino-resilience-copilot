"""Transparent, Rule-Based Intent Classifier for Agricultural Queries.

Classifies farmer questions in Telugu and English into one of 8 distinct intents:
1. current_weather
2. weather_forecast
3. rainfall_status
4. dry_spell_status
5. temperature_risk
6. crop_advisory
7. water_stress
8. general_farm_question

Uses weighted keyword, regex pattern matching, and entity context.
Does not claim to be a trained machine-learning model.
"""

import os
import re
import numpy as np
from typing import Dict, Any, List, Tuple, Optional

_SETFIT_MODEL = None
_SETFIT_TRIED = False

# Production Private Hugging Face Model Configuration
# Immutable commit hash pinned to prevent tracking mutable 'main' branch
DEFAULT_HF_MODEL_REPO_ID = "BHARGAVAREDDY1/elnino-agri-setfit"
DEFAULT_HF_MODEL_REVISION = "0a50cfd0b1e2e6fcf9e2cd3a3bafcaecbd5fd0f0"


def validate_model_directory(directory_path: str) -> bool:
    """Validate that a local or cached snapshot directory contains essential model files."""
    if not directory_path or not os.path.isdir(directory_path):
        return False
    required_files = ["model_head.pkl", "model.safetensors", "config_setfit.json", "tokenizer.json"]
    return all(os.path.isfile(os.path.join(directory_path, f)) for f in required_files)


def get_hf_config() -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """Retrieve Hugging Face repository configuration and authentication.
    
    Resolution order:
    1. Streamlit secrets (st.secrets) for hosted/cloud deployments.
    2. Environment variables (os.getenv) for Docker/local/CI environments.
    3. Cached token from Hugging Face CLI login (~/.cache/huggingface/token).
    4. Pinned immutable production defaults for repository ID and commit revision.
       (Note: HF_TOKEN is NEVER defaulted or hardcoded; must be supplied via secrets or env).
    
    Returns:
        (repo_id, token, revision, cache_dir)
    """
    repo_id = None
    token = None
    revision = None
    cache_dir = None

    # 1. Attempt retrieval from Streamlit secrets
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            try:
                repo_id = st.secrets.get("HF_MODEL_REPO_ID")
                token = st.secrets.get("HF_TOKEN")
                revision = st.secrets.get("HF_MODEL_REVISION")
                cache_dir = st.secrets.get("HF_CACHE_DIR")
            except Exception:
                pass
    except Exception:
        pass

    # 2. Fall back to environment variables
    if not repo_id:
        repo_id = os.getenv("HF_MODEL_REPO_ID")
    if not token:
        token = os.getenv("HF_TOKEN")
    if not revision:
        revision = os.getenv("HF_MODEL_REVISION")
    if not cache_dir:
        cache_dir = os.getenv("HF_CACHE_DIR")

    # 3. Fall back to cached Hugging Face CLI token if not provided in env/secrets
    if not token:
        try:
            from huggingface_hub import get_token
            cached_token = get_token()
            if cached_token:
                token = cached_token
        except Exception:
            pass

    # 4. Use production defaults for repository ID and immutable commit revision
    if not repo_id:
        repo_id = DEFAULT_HF_MODEL_REPO_ID
    if not revision:
        revision = DEFAULT_HF_MODEL_REVISION

    # Clean whitespace and normalize empty strings
    repo_id = repo_id.strip() if repo_id and repo_id.strip() else None
    token = token.strip() if token and token.strip() else None
    revision = revision.strip() if revision and revision.strip() else None
    cache_dir = cache_dir.strip() if cache_dir and cache_dir.strip() else None

    return repo_id, token, revision, cache_dir


def get_ml_classifier():
    """Lazily load the SetFit model from local storage or secure private Hugging Face Hub.
    
    Resolution Order:
    1. Local storage at models/setfit_best (Development / Local tests)
    2. Previously cached Hugging Face snapshot (local_files_only=True)
    3. Authenticated remote download from private Hugging Face Hub via HF_TOKEN
    4. Graceful fallback to rule-based NLP if any step fails or is unconfigured.
    """
    global _SETFIT_MODEL, _SETFIT_TRIED
    if _SETFIT_TRIED:
        return _SETFIT_MODEL
    _SETFIT_TRIED = True

    base_dir = os.path.dirname(os.path.abspath(__file__))

    # -------------------------------------------------------------------------
    # Tier 1: Local Development Path (models/setfit_best)
    # -------------------------------------------------------------------------
    local_path = os.path.abspath(os.path.join(base_dir, "..", "..", "models", "setfit_best"))
    if validate_model_directory(local_path):
        try:
            from setfit import SetFitModel
            _SETFIT_MODEL = SetFitModel.from_pretrained(local_path)
            return _SETFIT_MODEL
        except Exception:
            _SETFIT_MODEL = None

    # -------------------------------------------------------------------------
    # Tier 2 & 3: Hugging Face Private Repository Loading
    # -------------------------------------------------------------------------
    repo_id, token, revision, cache_dir = get_hf_config()

    # If no repository ID is configured, smoothly disengage ML model
    if not repo_id:
        _SETFIT_MODEL = None
        return None

    # Default cache directory if not explicitly customized
    if not cache_dir:
        cache_dir = os.path.abspath(os.path.join(base_dir, "..", "..", "models", "hf_cache"))

    # Tier 2: Check for previously cached snapshot (local_files_only=True)
    try:
        from huggingface_hub import snapshot_download
        from setfit import SetFitModel
        cached_dir = snapshot_download(
            repo_id=repo_id,
            revision=revision,
            token=token,
            cache_dir=cache_dir,
            local_files_only=True,
        )
        if validate_model_directory(cached_dir):
            _SETFIT_MODEL = SetFitModel.from_pretrained(cached_dir)
            return _SETFIT_MODEL
    except Exception:
        # Cache miss or invalid cache, proceed to remote download
        pass

    # Tier 3: Authenticated download from private repository
    try:
        from huggingface_hub import snapshot_download
        from setfit import SetFitModel

        os.makedirs(cache_dir, exist_ok=True)
        snapshot_dir = snapshot_download(
            repo_id=repo_id,
            revision=revision,
            token=token,
            cache_dir=cache_dir,
            local_files_only=False,
        )
        if validate_model_directory(snapshot_dir):
            _SETFIT_MODEL = SetFitModel.from_pretrained(snapshot_dir)
        else:
            _SETFIT_MODEL = None
    except Exception:
        # Network down, token invalid, or repo not found - fall back gracefully
        _SETFIT_MODEL = None

    return _SETFIT_MODEL


def reset_ml_classifier():
    """Reset the singleton instance of the ML classifier to reload updated weights."""
    global _SETFIT_MODEL, _SETFIT_TRIED
    _SETFIT_MODEL = None
    _SETFIT_TRIED = False


# Defined Intents with Descriptions and Example Phrases
INTENT_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "current_weather": {
        "description": "Current atmospheric conditions including temperature, humidity, wind, and sky condition.",
        "examples_en": [
            "What is the current temperature in my area?",
            "What is the weather right now?",
            "How humid is it today?",
            "Is it raining right now in Kadapa?",
        ],
        "examples_te": [
            "ప్రస్తుతం మా ప్రాంతంలో ఉష్ణోగ్రత ఎంత?",
            "ఈరోజు వాతావరణం ఎలా ఉంది?",
            "ప్రస్తుత వాతావరణ పరిస్థితులు ఏమిటి?",
        ],
    },
    "weather_forecast": {
        "description": "Upcoming 7-day weather outlook, upcoming rain probability, and weekly temperatures.",
        "examples_en": [
            "Will it rain in the next 7 days?",
            "What is the weather forecast for coming week?",
            "Is rainfall expected tomorrow?",
            "Will it rain this week?",
        ],
        "examples_te": [
            "వచ్చే ఏడు రోజుల్లో వర్షం పడుతుందా?",
            "రాబోయే వారంలో వాతావరణం ఎలా ఉండబోతోంది?",
            "రాబోయే 7 రోజుల్లో వర్ష సూచన ఉందా?",
        ],
    },
    "rainfall_status": {
        "description": "Recent 30-day cumulative precipitation and historical reanalysis rainfall evaluation.",
        "examples_en": [
            "How much rain was estimated in the last 30 days?",
            "What is my 30-day total rainfall?",
            "How many rainy days occurred recently?",
        ],
        "examples_te": [
            "గత 30 రోజుల్లో ఎంత వర్షపాతం నమోదైంది?",
            "గడిచిన నెలలో మొత్తం వర్షం ఎంత?",
            "ఇటీవల ఎన్ని వర్షపు రోజులు వచ్చాయి?",
        ],
    },
    "dry_spell_status": {
        "description": "Consecutive days with precipitation < 1.0 mm and duration of recent dry intervals.",
        "examples_en": [
            "How many dry days have occurred?",
            "What is the current dry spell duration?",
            "How long has it been without rain?",
        ],
        "examples_te": [
            "ఎన్ని వర్షాభావ రోజులు గడిచాయి?",
            "వర్షం పడకుండా ఎన్ని రోజులు అయ్యింది?",
            "ప్రస్తుత వర్షాభావ రోజుల సంఖ్య ఎంత?",
        ],
    },
    "temperature_risk": {
        "description": "Thermal stress analysis, excessive heat, scorching sun, and crop thermal thresholds.",
        "examples_en": [
            "Is there a heat stress risk for my crop?",
            "Are temperatures too high for turmeric?",
            "Is the weather suitable for my crop?",
            "Will heat damage my flowering paddy?",
        ],
        "examples_te": [
            "నా పసుపు పంటకు వాతావరణం అనుకూలంగా ఉందా?",
            "ఎండ తీవ్రత వల్ల పంటకు నష్టం జరుగుతుందా?",
            "అధిక ఉష్ణోగ్రతల వల్ల రిస్క్ ఉందా?",
        ],
    },
    "crop_advisory": {
        "description": "Agronomic advice, stage-specific precautions, mulching, resilience tips, and crop management.",
        "examples_en": [
            "What precautions should I take for my banana crop?",
            "How to manage turmeric in hot weather?",
            "What agronomic practices are recommended for paddy?",
        ],
        "examples_te": [
            "నా అరటి పంటకు ఎలాంటి జాగ్రత్తలు తీసుకోవాలి?",
            "పసుపు పంటలో ఎండ వేడికి ఏం చేయాలి?",
            "నా పంట రక్షణకు సూచనలు ఇవ్వండి",
        ],
    },
    "water_stress": {
        "description": "Soil moisture vulnerability, irrigation buffer, water deficit, and drought pressure.",
        "examples_en": [
            "Is my paddy crop at risk of water shortage?",
            "Do I have irrigation deficit on my sandy soil?",
            "Will my crop suffer water stress?",
        ],
        "examples_te": [
            "నా వరి పంటకు నీటి కొరత ప్రమాదం ఉందా?",
            "నీటి ఎద్దడి వచ్చే అవకాశం ఉందా?",
            "నా నేలలో తేమ ఆరిపోయే రిస్క్ ఉందా?",
        ],
    },
    "general_farm_question": {
        "description": "Farm plot attributes, digital twin status, acreage, crop type, and overall farm overview.",
        "examples_en": [
            "Tell me about my farm.",
            "What is my farm digital twin profile?",
            "Summarize my farm plot details.",
        ],
        "examples_te": [
            "నా పొలం వివరాలు చెప్పండి",
            "నా డిజిటల్ ట్విన్ సమాచారం ఏమిటి?",
            "నా ఫార్మ్ ప్రొఫైల్ వివరాలు చూపించండి",
        ],
    },
    "whatif_simulation": {
        "description": "What-If hypothetical climate scenario simulation, rainfall reduction stress, heat elevation, irrigation unavailable.",
        "examples_en": [
            "Which scenario is most concerning for my turmeric crop?",
            "What happens if rainfall decreases by 30%?",
            "What precautions should I take if irrigation becomes unavailable?",
            "How does drought combined with high temperature affect my crop?",
        ],
        "examples_te": [
            "నా పసుపు పంటకు ఏ పరిస్థితి ఎక్కువ ప్రమాదకరం?",
            "వర్షాలు తగ్గితే నా పంటకు ఏమవుతుంది?",
            "నీటి సౌకర్యం లేకపోతే నేను ఏ జాగ్రత్తలు తీసుకోవాలి?",
            "వర్షపాతం 30% తగ్గితే ఏమవుతుంది?",
        ],
    },
}


# Weighted keyword patterns for each intent
INTENT_PATTERNS: List[Tuple[str, List[str], int]] = [
    # 1. General farm / profile questions
    (
        "general_farm_question",
        [
            r"tell me about my farm",
            r"about my farm",
            r"my farm details",
            r"farm digital twin",
            r"my profile",
            r"digital twin",
            r"నా పొలం వివరాలు",
            r"నా పొలం గురించి",
            r"నా డిజిటల్ ట్విన్",
            r"ఫార్మ్ వివరాలు",
        ],
        10,
    ),
    # 2. Dry spell status
    (
        "dry_spell_status",
        [
            r"how many dry days",
            r"dry days have occurred",
            r"dry days count",
            r"dry spell",
            r"consecutive dry",
            r"days without rain",
            r"వర్షాభావ రోజులు",
            r"వర్షాభావం",
            r"వర్షం లేని రోజులు",
            r"ఎండగట్టిన రోజులు",
        ],
        8,
    ),
    # 3. Weather forecast
    (
        "weather_forecast",
        [
            r"next 7 days",
            r"7 days",
            r"coming week",
            r"upcoming week",
            r"will it rain",
            r"is it going to rain",
            r"rain in the next",
            r"forecast",
            r"రాబోయే",
            r"వచ్చే ఏడు రోజుల్లో",
            r"వచ్చే 7 రోజుల్లో",
            r"వచ్చే వారం",
            r"వర్షం పడుతుందా",
            r"వర్ష సూచన",
            r"రేపు వర్షం",
            r"rain.*padutunda",
            r"varsham.*padutunda",
            r"rain.*vachhe",
        ],
        7,
    ),
    # 4. Rainfall status (historical / 30-day cumulative)
    (
        "rainfall_status",
        [
            r"last 30 days",
            r"past 30 days",
            r"30 day rainfall",
            r"30-day total",
            r"cumulative rainfall",
            r"how much rain",
            r"rainy days",
            r"గత 30 రోజులు",
            r"30 రోజుల్లో ఎంత వర్షం",
            r"సంచిత వర్షపాతం",
            r"మొత్తం వర్షం",
            r"వర్షపు రోజులు",
        ],
        7,
    ),
    # 5. Current weather
    (
        "current_weather",
        [
            r"current temperature",
            r"temperature in my area",
            r"current weather",
            r"weather today",
            r"weather right now",
            r"is it raining right now",
            r"humidity today",
            r"wind speed now",
            r"temperature.*entha",
            r"temp.*entha",
            r"weather.*ela undi",
            r"weather.*today",
            r"ప్రస్తుతం.*ఉష్ణోగ్రత",
            r"ఉష్ణోగ్రత ఎంత",
            r"ఈరోజు వాతావరణం",
            r"ప్రస్తుత వాతావరణం",
        ],
        7,
    ),
    # 6. Water stress
    (
        "water_stress",
        [
            r"water shortage",
            r"water stress",
            r"water deficit",
            r"irrigation risk",
            r"soil moisture deficit",
            r"drought risk",
            r"neellu",
            r"neeti.*koratha",
            r"నీటి కొరత",
            r"నీటి ఎద్దడి",
            r"నీటి సమస్య",
            r"నీటి కొరత ప్రమాదం",
            r"తేమ కొరత",
        ],
        8,
    ),
    # 7. Temperature risk / Thermal suitability
    (
        "temperature_risk",
        [
            r"heat stress",
            r"temperature risk",
            r"too hot",
            r"weather suitable",
            r"climate suitable",
            r"suitable for my crop",
            r"crop.*ki.*weather",
            r"weather.*anukoolama",
            r"వాతావరణం అనుకూలంగా ఉందా",
            r"వాతావరణం ఎలా ఉంది",
            r"వేడిమి రిస్క్",
            r"ఎండ తీవ్రత",
            r"అధిక ఉష్ణోగ్రత",
        ],
        7,
    ),
    # 8. Crop advisory
    (
        "crop_advisory",
        [
            r"precautions?",
            r"care\b",
            r"teeskovali",
            r"teesukovali",
            r"advisory",
            r"management",
            r"guidance",
            r"tips",
            r"resilience",
            r"what to do",
            r"what should i do",
            r"how to protect",
            r"how to manage",
            r"how to care",
            r"protect.*crop",
            r"fertilizer",
            r"mulching",
            r"windbreak",
            r"how should i irrigate",
            r"precautions.*emiti",
            r"jagratthalu",
            r"జాగ్రత్తలు",
            r"ఎలాంటి జాగ్రత్తలు",
            r"యాజమాన్య పద్ధతులు",
            r"యాజమాన్యం",
            r"ఎలా కాపాడుకోవాలి",
            r"ఏం చేయాలి",
            r"ఏమి చేయాలి",
            r"సలహా",
            r"నీరు ఎలా పెట్టాలి",
            r"నీటి యాజమాన్యం",
        ],
        8,
    ),
    # 9. What-If Simulation
    (
        "whatif_simulation",
        [
            r"which scenario",
            r"most concerning",
            r"highest risk scenario",
            r"scenario.*concerning",
            r"what if",
            r"what-if",
            r"what happens if",
            r"rainfall decrease",
            r"rainfall drops?",
            r"rain decrease",
            r"if rainfall",
            r"rainfall.*30%",
            r"temperature increase",
            r"temp increase",
            r"if temp",
            r"irrigation.*unavailable",
            r"without irrigation",
            r"no irrigation",
            r"drought combined",
            r"simulate",
            r"simulation",
            r"ఏ పరిస్థితి.*ప్రమాదకరం",
            r"ఏ పరిస్థితి.*ప్రమాదం",
            r"ఎక్కువ ప్రమాదకరం",
            r"వర్షాలు తగ్గితే",
            r"వర్షం తగ్గితే",
            r"వర్షపాతం తగ్గితే",
            r"నీటి సౌకర్యం లేకపోతే",
            r"నీరు లేకపోతే",
            r"సిమ్యులేషన్",
            r"సిమ్యులేటర్",
            r"వాట్-ఇఫ్",
        ],
        12,
    ),
]


def classify_intent(
    normalized_text: str,
    raw_text: Optional[str] = None,
    extracted_entities: Optional[Dict[str, Any]] = None,
    use_ml: bool = True,
) -> Dict[str, Any]:
    """Classify the user query into one of 8 target intents with confidence score.
    
    Uses a hybrid approach:
    1. Checks for hard override rules (e.g. What-If simulator triggers).
    2. Uses lightweight fine-tuned SetFit MiniLM-L12-v2 model (if confidence >= 0.55).
    3. Seamlessly falls back to transparent keyword/regex heuristics if ML is uncertain.
    
    Args:
        normalized_text: Lowercased, transliteration-mapped text.
        raw_text: Original raw input string (defaults to normalized_text if omitted).
        extracted_entities: Output from entity_extractor.py (defaults to empty dict).
        use_ml: Whether to use the fine-tuned SetFit model when available.
        
    Returns:
        Dictionary with:
            - intent: str (one of the 8 intents or 'unknown')
            - confidence: float (0.0 to 1.0)
            - matched_rule: str
            - all_scores: Dict[str, int]
    """
    if raw_text is None:
        raw_text = normalized_text
    if extracted_entities is None:
        extracted_entities = {}

    scores: Dict[str, int] = {k: 0 for k in INTENT_DEFINITIONS}
    scores["whatif_simulation"] = 0
    matched_rules: Dict[str, str] = {}

    combined_text = f"{raw_text} {normalized_text}".lower()

    # 1. Match regex patterns
    for intent_name, patterns, weight in INTENT_PATTERNS:
        for pat in patterns:
            if re.search(pat, combined_text, re.IGNORECASE):
                scores[intent_name] += weight
                if intent_name not in matched_rules:
                    matched_rules[intent_name] = pat

    # 2. Contextual boosts from extracted entities
    time_p = extracted_entities.get("time_period", "general")
    concepts = extracted_entities.get("concepts", [])

    if time_p == "next_7_days" or time_p == "tomorrow":
        scores["weather_forecast"] += 4
    elif time_p == "current":
        scores["current_weather"] += 4
    elif time_p == "last_30_days":
        scores["rainfall_status"] += 4

    if "dry_spell" in concepts:
        scores["dry_spell_status"] += 5
    if "water_stress" in concepts:
        scores["water_stress"] += 5
    if "temperature" in concepts:
        if time_p == "current":
            scores["current_weather"] += 3
        else:
            scores["temperature_risk"] += 3

    # Disambiguation heuristics
    # "Will it rain in the next 7 days?" -> has rainfall concept + next_7_days -> weather_forecast
    if "rainfall" in concepts and (time_p == "next_7_days" or "will it rain" in combined_text or "వర్షం పడుతుందా" in combined_text):
        scores["weather_forecast"] += 6

    # "How many dry days have occurred?" -> dry_spell_status
    if "dry days" in combined_text or "వర్షాభావ రోజులు" in combined_text:
        scores["dry_spell_status"] += 8

    # "What is the current temperature in my area?" -> current_weather
    if "current temperature" in combined_text or "ప్రస్తుతం" in combined_text and "ఉష్ణోగ్రత" in combined_text:
        scores["current_weather"] += 8

    # "వాతావరణం అనుకూలంగా ఉందా?" -> temperature_risk
    if "అనుకూలంగా ఉందా" in combined_text or "suitable" in combined_text:
        scores["temperature_risk"] += 6

    # "జాగ్రత్తలు" / "precautions" / "care" / "protect" -> crop_advisory
    if any(k in combined_text for k in ["జాగ్రత్తలు", "precaution", "teeskovali", "teesukovali", "em care", "protect my"]):
        scores["crop_advisory"] += 8

    # What-If Simulation disambiguation heuristic
    if any(k in combined_text for k in [
        "scenario", "most concerning", "rainfall decrease", "rain decrease", "if rainfall",
        "irrigation becomes unavailable", "irrigation unavailable", "without irrigation", "no irrigation",
        "పరిస్థితి", "ఎక్కువ ప్రమాదకరం", "వర్షాలు తగ్గితే", "వర్షం తగ్గితే", "నీటి సౌకర్యం లేకపోతే", "నీరు లేకపోతే"
    ]):
        scores["whatif_simulation"] += 15

    # Check for direct high-priority rule overrides (e.g. whatif simulation)
    if scores.get("whatif_simulation", 0) >= 15:
        return {
            "intent": "whatif_simulation",
            "confidence": 0.95,
            "matched_rule": "what-if simulation trigger",
            "all_scores": scores,
        }

    # Attempt ML Classification via fine-tuned SetFit model
    if use_ml:
        ml_clf = get_ml_classifier()
        if ml_clf is not None:
            try:
                probs = ml_clf.predict_proba([raw_text])[0]
                best_idx = int(np.argmax(probs))
                ml_conf = float(probs[best_idx])
                ml_intent = ml_clf.labels[best_idx]
                if ml_conf >= 0.55:
                    if ml_intent == "out_of_scope":
                        # Explicit ML rejection for unrelated/non-agricultural queries
                        return {
                            "intent": "unknown",
                            "confidence": round(ml_conf, 2),
                            "matched_rule": f"SetFit MiniLM-L12-v2 (ML OOS Rejection, conf={ml_conf:.2f})",
                            "all_scores": scores,
                        }
                    elif ml_intent in INTENT_DEFINITIONS:
                        return {
                            "intent": ml_intent,
                            "confidence": round(ml_conf, 2),
                            "matched_rule": f"SetFit MiniLM-L12-v2 (ML, conf={ml_conf:.2f})",
                            "all_scores": scores,
                        }
            except Exception:
                pass  # Fallback smoothly to rule-based logic

    # Find highest scoring intent (Rule-based Fallback)
    best_intent = "unknown"
    highest_score = 0
    for intent, score in scores.items():
        if score > highest_score:
            highest_score = score
            best_intent = intent

    if highest_score < 4:
        best_intent = "unknown"
        conf = 0.3
    else:
        conf = min(0.95, 0.5 + (highest_score * 0.05))

    return {
        "intent": best_intent,
        "confidence": round(conf, 2),
        "matched_rule": matched_rules.get(best_intent, "keyword/entity heuristic"),
        "all_scores": scores,
    }
