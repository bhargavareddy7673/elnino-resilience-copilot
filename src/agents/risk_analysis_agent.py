"""Risk Analysis Agent: Specialist module for explaining climate indicators.

Analyzes:
1. Temperature Risk & Thermal Suitability (evaluates peak forecast vs crop physiological thresholds).
2. Soil Moisture & Water Stress Vulnerability (synthesizes soil structure, irrigation buffer, and dry days).

Grounds answers in real data and transparently labels indicators as experimental
rule-based decision-support models without claiming automated statutory authority.
"""

from typing import Dict, Any, List, Optional
import pandas as pd

from src.weather.weather_analysis import evaluate_climate_indicators
from src.knowledge.crop_knowledge import get_crop_profile


def answer_temperature_risk(
    forecast_df: Optional[pd.DataFrame] = None,
    historical_df: Optional[pd.DataFrame] = None,
    farm_profile: Optional[Dict[str, Any]] = None,
    current_temp: Optional[float] = None,
    target_crop: Optional[str] = None,
    lang: str = "en",
    **kwargs: Any,
) -> Dict[str, Any]:
    """Generate response for crop thermal risk and climate suitability."""
    if farm_profile is None:
        farm_profile = {}
    if forecast_df is None:
        forecast_df = pd.DataFrame()
    if historical_df is None:
        historical_df = pd.DataFrame()

    crop = target_crop or farm_profile.get("crop", "Turmeric")
    crop_info = get_crop_profile(crop)
    opt_temp = crop_info["optimal_temperature_c"]

    eval_profile = dict(farm_profile)
    eval_profile["crop"] = crop

    indicators = evaluate_climate_indicators(
        forecast_df=forecast_df,
        historical_df=historical_df,
        farm_profile=eval_profile,
        current_temp=current_temp,
        lang=lang,
    )

    heat_ind = next((i for i in indicators if i["id"] == "heat_stress"), None)
    if not heat_ind or heat_ind.get("risk_level") == "Insufficient Data":
        msg_en = "Forecast temperature data is currently insufficient to perform a thermal risk evaluation."
        msg_te = "ఉష్ణోగ్రత రిస్క్ విశ్లేషణ చేయడానికి సరిపడా సమాచారం అందుబాటులో లేదు."
        return {
            "response": msg_te if lang == "te" else msg_en,
            "grounding_data": {"status": "insufficient_data"},
        }

    risk_level = heat_ind["risk_level"]
    risk_display = heat_ind["risk_level_display"]
    explanation = heat_ind["explanation"]
    data_used = heat_ind["data_used_te"] if lang == "te" else heat_ind["data_used_en"]

    grounding = {
        "crop": crop,
        "current_temperature_c": current_temp if current_temp is not None else "N/A",
        "optimal_temperature_range_c": f"{opt_temp['min']} - {opt_temp['max']} °C",
        "stress_threshold_c": opt_temp["stress_above"],
        "evaluated_risk_level": risk_level,
        "data_used": data_used,
        "indicator_type": "Experimental Decision Support",
    }

    if lang == "te":
        resp = (
            f"🌡️ **{crop_info['crop_name_te']} ({crop}) పంటకు వాతావరణ అనుకూలత & ఉష్ణోగ్రత విశ్లేషణ:**\n\n"
            f"- 📊 **అంచనా వేసిన రిస్క్ స్థాయి:** `{risk_display}`\n"
            f"- 🎯 **అనుకూల ఉష్ణోగ్రత పరిధి:** `{opt_temp['min']}°C నుండి {opt_temp['max']}°C` (38°C దాటితే ఒత్తిడి పెరుగుతుంది)\n"
            f"- 🔍 **పరిస్థితి వివరణ:** {explanation}\n\n"
            f"🌱 **ఈ పరిస్థితి {crop_info['crop_name_te']}కు ఎందుకు ముఖ్యం:**\n"
            f"{crop_info['temperature_sensitivity']['te']}\n\n"
            f"*గమనిక: ఈ సూచిక ప్రయోగాత్మక రూల్-బేస్డ్ పరిశోధనా నమూనా. నిర్దిష్ట నష్టం పంట దశ మరియు తేమపై ఆధారపడి ఉంటుంది.*"
        )
    else:
        resp = (
            f"🌡️ **Thermal Risk & Climate Suitability for {crop} ({crop_info['botanical_name']}):**\n\n"
            f"- 📊 **Evaluated Risk Level:** `{risk_display}`\n"
            f"- 🎯 **Optimal Thermal Baseline:** `{opt_temp['min']}°C - {opt_temp['max']}°C` (Transpirational stress above `{opt_temp['stress_above']}°C`)\n"
            f"- 🔍 **Indicator Assessment:** {explanation}\n\n"
            f"🌱 **Why this matters for your {crop}:**\n"
            f"{crop_info['temperature_sensitivity']['en']}\n\n"
            f"*Note: Evaluated via experimental rule-based thresholding for academic decision-support.*"
        )

    return {"response": resp, "grounding_data": grounding}


def answer_water_stress(
    forecast_df: Optional[pd.DataFrame] = None,
    historical_df: Optional[pd.DataFrame] = None,
    farm_profile: Optional[Dict[str, Any]] = None,
    current_temp: Optional[float] = None,
    target_crop: Optional[str] = None,
    lang: str = "en",
    **kwargs: Any,
) -> Dict[str, Any]:
    """Generate response for soil moisture deficit and irrigation vulnerability."""
    if farm_profile is None:
        farm_profile = {}
    if forecast_df is None:
        forecast_df = pd.DataFrame()
    if historical_df is None:
        historical_df = pd.DataFrame()

    crop = target_crop or farm_profile.get("crop", "Paddy")
    soil_type = farm_profile.get("soil_type", "Red Sandy Loam")
    irrigation = farm_profile.get("irrigation", "Borewell / Groundwater")
    crop_info = get_crop_profile(crop)

    eval_profile = dict(farm_profile)
    eval_profile["crop"] = crop

    indicators = evaluate_climate_indicators(
        forecast_df=forecast_df,
        historical_df=historical_df,
        farm_profile=eval_profile,
        current_temp=current_temp,
        lang=lang,
    )

    water_ind = next((i for i in indicators if i["id"] == "water_stress"), None)
    if not water_ind or water_ind.get("risk_level") == "Insufficient Data":
        msg_en = "Historical precipitation and farm profile data are insufficient to evaluate water stress."
        msg_te = "నీటి ఒత్తిడి విశ్లేషణ చేయడానికి తగిన వాతావరణ సమాచారం అందుబాటులో లేదు."
        return {
            "response": msg_te if lang == "te" else msg_en,
            "grounding_data": {"status": "insufficient_data"},
        }

    risk_level = water_ind["risk_level"]
    risk_display = water_ind["risk_level_display"]
    explanation = water_ind["explanation"]

    grounding = {
        "crop": crop,
        "soil_type": soil_type,
        "irrigation_source": irrigation,
        "risk_level": risk_level,
        "indicator_type": "Experimental Agronomic Synthesis",
    }

    if lang == "te":
        resp = (
            f"💧 **{crop_info['crop_name_te']} పంటకు నీటి కొరత & నేల తేమ విశ్లేషణ:**\n\n"
            f"- 📊 **ప్రమాద స్థాయి:** `{risk_display}`\n"
            f"- 🌾 **పొలం లక్షణాలు:** నేల రకం: `{soil_type}` | నీటి వనరు: `{irrigation}`\n"
            f"- 🔍 **విశ్లేషణ వివరాలు:** {explanation}\n\n"
            f"🌊 **{crop_info['crop_name_te']} నీటి ప్రాముఖ్యత:**\n"
            f"{crop_info['water_sensitivity']['te']}\n\n"
            f"*గమనిక: వాస్తవ నేల తేమ శాతాన్ని కొలవడానికి పొలంలో ప్రత్యక్ష సెన్సార్లు లేదా పదును పరీక్ష అవసరం.*"
        )
    else:
        resp = (
            f"💧 **Water Stress & Soil Moisture Vulnerability for {crop}:**\n\n"
            f"- 📊 **Evaluated Risk Level:** `{risk_display}`\n"
            f"- 🌾 **Plot Parameters:** Soil: `{soil_type}` | Primary Water Source: `{irrigation}`\n"
            f"- 🔍 **Agronomic Assessment:** {explanation}\n\n"
            f"🌊 **Hydrological Sensitivity of {crop}:**\n"
            f"{crop_info['water_sensitivity']['en']}\n\n"
            f"*Note: Synthesized from meteorological dry run, soil percolation traits, and irrigation buffering.*"
        )

    return {"response": resp, "grounding_data": grounding}
