"""Crop Advisory Agent: Specialist module for agronomic best practices and precautions.

Responsible for:
1. Providing stage-specific agronomic management recommendations.
2. Formulating resilience measures (mulching, irrigation tuning, drainage furrows, windbreaks).
3. Grounding recommendations in authentic agricultural references (ICAR, ANGRAU, IMD, PJTSAU).

Separates established crop physiology principles from real-time weather alerts.
"""

from typing import Dict, Any, List, Optional
import datetime

from src.knowledge.crop_knowledge import (
    get_crop_profile,
    get_growth_stage_by_days,
)


def answer_crop_advisory(
    farm_profile: Dict[str, Any],
    weather_summary: Dict[str, Any],
    target_crop: Optional[str] = None,
    lang: str = "en",
) -> Dict[str, Any]:
    """Generate personalized agronomic precautions and guidance based on crop and plot status."""
    crop = target_crop or farm_profile.get("crop", "Turmeric")
    soil = farm_profile.get("soil_type", "Red Sandy Loam")
    irrigation = farm_profile.get("irrigation", "Borewell / Groundwater")
    sowing_date_str = farm_profile.get("sowing_date", "")

    # Calculate days in field based strictly on saved sowing date (no silent fallback)
    days_in_field: Optional[int] = None
    has_valid_sowing: bool = False
    
    if sowing_date_str:
        try:
            if isinstance(sowing_date_str, datetime.date):
                s_date = sowing_date_str
            else:
                s_date = datetime.date.fromisoformat(str(sowing_date_str).strip())
            
            if s_date <= datetime.date.today():
                days_in_field = max(0, (datetime.date.today() - s_date).days)
                has_valid_sowing = True
        except Exception:
            days_in_field = None
            has_valid_sowing = False

    crop_info = get_crop_profile(crop)
    
    # Only infer growth stage when actual sowing date is provided
    stage_info: Optional[Dict[str, Any]] = None
    if has_valid_sowing and days_in_field is not None:
        stage_info = get_growth_stage_by_days(crop, days_in_field)
        
    practices = crop_info.get("resilience_practices", [])
    refs = crop_info.get("references", [])

    grounding = {
        "crop": crop,
        "days_in_field": days_in_field if has_valid_sowing else "Not provided (unknown)",
        "estimated_stage": stage_info.get("stage") if stage_info else "Not determined (sowing date required)",
        "stage_water_demand": stage_info.get("water_need") if stage_info else "General crop baseline",
        "soil_type": soil,
        "irrigation_source": irrigation,
        "references": refs,
    }

    if lang == "te":
        resp_lines = [
            f"🌱 **{crop_info['crop_name_te']} ({crop}) పంట రక్షణ & యాజమాన్య సూచనలు:**\n",
        ]
        
        if has_valid_sowing and days_in_field is not None and stage_info:
            resp_lines.append(f"- 🗓️ **ప్రస్తుత పంట వయస్సు:** సుమారు `{days_in_field} రోజులు`")
            resp_lines.append(f"- 🌾 **అంచనా వేసిన దశ:** `{stage_info.get('stage')}` (నీటి అవసరం: `{stage_info.get('water_need')}`)")
        else:
            resp_lines.append(f"- 🗓️ **ప్రస్తుత పంట వయస్సు:** `నమోదు చేయలేదు (Unknown)`")
            resp_lines.append(f"- 🌾 **ఎదుగుదల దశ:** `నిర్ణయించబడలేదు (విత్తిన తేదీ అవసరం)`")
            resp_lines.append(f"ℹ️ *గమనిక: ఖచ్చితమైన దశలవారీ నీటి అవసరాల కోసం దయచేసి **'నా పొలం' (My Farm)** విభాగంలో విత్తిన తేదీని నమోదు చేయండి.*")
            
        resp_lines.append(f"- 🏞️ **నేల మరియు నీరు:** `{soil}`, ప్రధాన వనరు: `{irrigation}`\n")
        resp_lines.append(f"🛡️ **పాటించవలసిన ముఖ్యమైన జాగ్రత్తలు & మెళకువలు:**\n")

        for p in practices:
            resp_lines.append(f"• **{p['practice_te']}:** {p['details_te']}")

        resp = "\n".join(resp_lines)
    else:
        resp_lines = [
            f"🌱 **Agronomic Advisory & Protective Precautions for {crop} ({crop_info['botanical_name']}):**\n",
        ]
        
        if has_valid_sowing and days_in_field is not None and stage_info:
            resp_lines.append(f"- 🗓️ **Crop Age in Field:** Approximately `{days_in_field} days`")
            resp_lines.append(f"- 🌾 **Estimated Phenological Stage:** `{stage_info.get('stage')}` (Water Requirement: `{stage_info.get('water_need')}`)")
        else:
            resp_lines.append(f"- 🗓️ **Crop Age in Field:** `Not Set (Unknown)`")
            resp_lines.append(f"- 🌾 **Phenological Growth Stage:** `Not Determined (requires planting date)`")
            resp_lines.append(f"ℹ️ *Advisory Note: Please specify your planting/sowing date in the **My Farm** screen to enable stage-calibrated irrigation and phenological guidance.*")
            
        resp_lines.append(f"- 🏞️ **Field Configuration:** `{soil}` with `{irrigation}`\n")
        resp_lines.append(f"🛡️ **Recommended Climate Resilience Practices for {crop}:**\n")

        for p in practices:
            resp_lines.append(f"• **{p['practice_en']}:** {p['details_en']}")

        resp = "\n".join(resp_lines)

    return {"response": resp, "grounding_data": grounding, "references": refs}
