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
    query: Optional[str] = None,
    topic: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate personalized agronomic precautions and guidance based on crop, plot status, and question topic."""
    crop = target_crop or farm_profile.get("crop", "Turmeric")
    soil = farm_profile.get("soil_type", "Red Sandy Loam")
    irrigation = farm_profile.get("irrigation", "Borewell / Groundwater")
    sowing_date_str = farm_profile.get("sowing_date", "")

    # Detect if query or topic is focused on irrigation / water management
    q_lower = query.lower() if query else ""
    is_irrigation = (
        topic == "Water management"
        or any(k in q_lower for k in [
            "irrigate", "irrigation", "water", "watering", "how often", "schedule", "how much water",
            "needs water", "manage water"
        ])
        or any(k in (query or "") for k in [
            "నీరు", "నీళ్ళు", "నీళ్లు", "నీటి", "తడి", "తడులు", "యాజమాన్యం", "అవసరం"
        ])
    )

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
    refs = list(crop_info.get("references", []))
    rain_range = crop_info.get("annual_rainfall_mm", {"min": 1000.0, "max": 2000.0})

    # Augment references with live authentic RAG citations if available
    try:
        from src.rag.synthesizer import get_retriever
        retriever = get_retriever()
        rag_search = retriever.search_hybrid(
            query=query or crop,
            top_k=2,
            crop_filter=crop.lower() if crop.lower() in ["turmeric", "banana", "paddy"] else None,
            suppress_legacy=True,
            suppress_boilerplate=True,
        )
        for chk in rag_search.get("results", []):
            doc_label = f"{chk.document_title} (Page {chk.page_number})"
            if not any(r.get("document") == doc_label for r in refs):
                refs.append({
                    "authority": chk.organization,
                    "authority_te": chk.organization,
                    "document": doc_label,
                    "document_te": doc_label,
                    "url": chk.source_url,
                    "page": chk.page_number,
                })
    except Exception:
        pass

    grounding = {
        "crop": crop,
        "topic": "Water management" if is_irrigation else "General agronomy",
        "days_in_field": days_in_field if has_valid_sowing else "Not provided (unknown)",
        "estimated_stage": stage_info.get("stage") if stage_info else "Not determined (sowing date required)",
        "stage_water_demand": stage_info.get("water_need") if stage_info else "General crop baseline",
        "soil_type": soil,
        "irrigation_source": irrigation,
        "water_requirement_mm": f"{rain_range['min']:.0f} - {rain_range['max']:.0f} mm",
        "references": refs,
    }

    if is_irrigation:
        # Specialized Irrigation & Water Management Advisory
        if lang == "te":
            resp_lines = [
                f"💧 **{crop_info['crop_name_te']} ({crop}) పంటకు సమగ్ర నీటి యాజమాన్య & తడుల సూచనలు:**\n",
            ]
            if has_valid_sowing and days_in_field is not None and stage_info:
                resp_lines.append(f"- 🗓️ **ప్రస్తుత పంట వయస్సు:** సుమారు `{days_in_field} రోజులు`")
                resp_lines.append(f"- 🌾 **ఎదుగుదల దశ & నీటి అవసరం:** `{stage_info.get('stage_te', stage_info.get('stage'))}` — నీటి డిమాండ్: **`{stage_info.get('water_need_te', stage_info.get('water_need'))}`**")
            else:
                resp_lines.append(f"- 🗓️ **పంట వయస్సు:** `నమోదు చేయలేదు` (ఖచ్చితమైన దశలవారీ నీటి అవసరాల కోసం 'నా పొలం' స్క్రీన్‌లో విత్తిన తేదీని నమోదు చేయండి)")

            resp_lines.append(f"- 🏞️ **పొలం లక్షణాలు:** నేల రకం: `{soil}`, నీటి వనరు: `{irrigation}`")
            resp_lines.append(f"- 🌊 **మొత్తం నీటి అవసరం:** ఏడాదికి సుమారు `{rain_range['min']:.0f} - {rain_range['max']:.0f} మి.మీ`\n")

            resp_lines.append(f"🌊 **నీటి సున్నితత్వం & ముఖ్యమైన అంశాలు:**")
            resp_lines.append(f"{crop_info['water_sensitivity']['te']}\n")

            resp_lines.append(f"🛡️ **సిఫార్సు చేయబడిన నీటి పారుదల పద్ధతులు & తడుల షెడ్యూల్:**")
            if crop == "Turmeric":
                resp_lines.append("• **తడుల వ్యవధి (Irrigation Interval):** ఎర్ర ఇసుక గరప నేలల్లో సాధారణంగా 7-10 రోజులకు ఒకసారి తడి ఇవ్వాలి. ఎండ తీవ్రత ఎక్కువగా ఉన్నప్పుడు 5-7 రోజుల వ్యవధిలో తడులు అందించాలి.")
                resp_lines.append("• **కీలక దశలు:** కొమ్ము ఊరే మరియు పరిమాణం పెరిగే దశలో (120-210 రోజులు) వేరు మండలంలో నిరంతరం తగినంత పదును ఉండాలి.")
                resp_lines.append("• **తేమ సంరక్షణ:** వరి గడ్డి లేదా పచ్చి రొట్టతో సేంద్రీయ మల్చింగ్ చేయడం వల్ల నేలలో తేమ ఆవిరి కాకుండా ఎక్కువ కాలం నిల్వ ఉంటుంది.")
                resp_lines.append("• **మురుగు నీటి యాజమాన్యం:** అధిక వర్షాలు లేదా నీరు నిలవడం వల్ల దుంప కుళ్లు తెగులు రాకుండా బోదెల మధ్య 30 సెం.మీ మురుగు కాలువలు తీయాలి.")
            elif crop == "Banana":
                resp_lines.append("• **బిందు సేద్యం (Drip Scheduling):** ఎండ తీవ్రత ఉన్నప్పుడు బిందు సేద్యం ద్వారా రోజూ తగిన మోతాదులో నీటి తడులు అందించడం ద్వారా వేరు మండలంలో తేమ సమతుల్యతను కాపాడాలి.")
                resp_lines.append("• **కీలక దశలు:** గెల వేసే సమయంలో మరియు కాయ ఊరే దశలో నీటి కొరత రానివ్వకూడదు; కొరత ఏర్పడితే కాయ పరిమాణం, గెల నాణ్యత దెబ్బతింటుంది.")
            elif crop == "Paddy":
                resp_lines.append("• **ఆరబెట్టి తడపడం (AWD పద్ధతి):** శాఖీయ ఎదుగుదల దశలో నిరంతరం నీరు నిలపకుండా, పొలంలోని నీరు ఇంకి సన్నని నెర్రలు వచ్చే సమయంలో మళ్లీ 2-3 సెం.మీ తడి ఇవ్వడం ద్వారా 25-30% నీరు ఆదా అవుతుంది.")
                resp_lines.append("• **కీలక దశలు:** చిరుపొట్ట మరియు పూత దశల్లో తప్పనిసరిగా 3-5 సెం.మీ నీరు నిల్వ ఉండేలా చూసుకోవాలి; ఇది తాలు గింజలు రాకుండా రక్షిస్తుంది.")

            resp = "\n".join(resp_lines)
        else:
            resp_lines = [
                f"💧 **Irrigation & Water Management Guidance for {crop} ({crop_info['botanical_name']}):**\n",
            ]
            if has_valid_sowing and days_in_field is not None and stage_info:
                resp_lines.append(f"- 🗓️ **Current Crop Age:** Approximately `{days_in_field} days`")
                resp_lines.append(f"- 🌾 **Phenological Stage & Water Need:** `{stage_info.get('stage')}` — Water Requirement: **`{stage_info.get('water_need')}`**")
            else:
                resp_lines.append(f"- 🗓️ **Crop Age in Field:** `Not Set` (Record sowing date in 'My Farm' for stage-calibrated irrigation advice)")

            resp_lines.append(f"- 🏞️ **Field Baseline:** `{soil}` with `{irrigation}`")
            resp_lines.append(f"- 🌊 **Total Crop Water Requirement:** Approximately `{rain_range['min']:.0f} - {rain_range['max']:.0f} mm` annual equivalent\n")

            resp_lines.append(f"🌊 **Hydrological Sensitivity & Critical Growth Phases:**")
            resp_lines.append(f"{crop_info['water_sensitivity']['en']}\n")

            resp_lines.append(f"🛡️ **Recommended Irrigation Practices & Scheduling:**")
            if crop == "Turmeric":
                resp_lines.append("• **Irrigation Interval:** On red sandy loam soils, irrigate at 7-10 day intervals; shorten to 5-7 days during hot dry spells. In heavy soils, irrigate every 10-14 days.")
                resp_lines.append("• **Critical Moisture Window:** Maintain uniform root-zone moisture during the rhizome development and bulking stage (120-210 days).")
                resp_lines.append("• **Soil Moisture Conservation:** Apply 10-12 tons/ha of paddy straw or green leaf mulch to buffer soil temperature and suppress transpirational loss.")
                resp_lines.append("• **Drainage Protection:** Ensure 30 cm drainage furrows across ridges to prevent waterlogging and fungal rhizome rot (Pythium).")
            elif crop == "Banana":
                resp_lines.append("• **Drip Irrigation Scheduling:** Schedule frequent, micro-dosed drip irrigations during dry spells to maintain consistent root-zone moisture tension.")
                resp_lines.append("• **Critical Phases:** Drought stress during shooting, bunch emergence (150-240 days), and finger filling (240-330 days) severely impairs finger length and market grade.")
            elif crop == "Paddy":
                resp_lines.append("• **Alternate Wetting and Drying (AWD):** Allow standing water to subside until hairline cracks appear before reapplying 2-3 cm of water during vegetative phase to conserve 25-30% water.")
                resp_lines.append("• **Critical Phases:** Maintain 3-5 cm standing water continuously during panicle initiation and flowering to prevent spikelet sterility.")

            resp = "\n".join(resp_lines)

        return {"response": resp, "grounding_data": grounding, "references": refs}

    # Standard Agronomic Advisory (non-irrigation general precautions)
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
