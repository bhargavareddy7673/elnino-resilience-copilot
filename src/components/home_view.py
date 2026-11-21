"""Home Screen Component for El Niño Resilience Co-Pilot.

Delivers a modern, commercial-grade agricultural dashboard:
1. Warm, personalized farmer greeting with plot attributes.
2. Real-time atmospheric conditions at a glance.
3. 30-day precipitation and dry spell snapshot.
4. Active crop alerts and climate indicators.
5. Personalized, stage-specific agronomic advice.
6. One-click shortcuts to Weather, Advisor, Farm, and Crop Guidance.
"""

from typing import Dict, Any, Callable
import datetime
import streamlit as st

from src.localization import get_text
from src.config import SOIL_TYPES, IRRIGATION_SOURCES
from src.weather.location_service import get_district_coordinates
from src.weather.weather_api import get_weather_intelligence, get_weather_description
from src.weather.weather_analysis import (
    compute_dry_spell_metrics,
    evaluate_climate_indicators,
)
from src.knowledge.crop_knowledge import (
    get_crop_profile,
    get_growth_stage_by_days,
)


def render_home_view(
    farm_profile: Dict[str, Any],
    lang: str = "en",
    navigate_to: Callable[[str], None] = None,
) -> None:
    """Render the Home screen.
    
    Args:
        farm_profile: Active digital twin dictionary from session state.
        lang: Active language ('en' or 'te').
        navigate_to: Callback to change navigation section.
    """
    state = farm_profile.get("state", "Andhra Pradesh")
    district = farm_profile.get("district", "Kurnool")
    village = farm_profile.get("village", "").strip()
    crop = farm_profile.get("crop", "Turmeric")
    land_area = farm_profile.get("land_area", 4.0)
    soil = farm_profile.get("soil_type", "Red Sandy Loam")
    irrigation = farm_profile.get("irrigation", "Borewell / Groundwater")
    sowing_date_val = farm_profile.get("sowing_date")

    # Calculate days in field
    sowing_date_val = farm_profile.get("sowing_date")
    has_valid_sowing = False
    days_in_field = None
    s_date = None
    if sowing_date_val:
        try:
            if isinstance(sowing_date_val, str) and sowing_date_val.strip():
                s_date = datetime.date.fromisoformat(sowing_date_val.strip())
            elif isinstance(sowing_date_val, (datetime.date, datetime.datetime)):
                s_date = sowing_date_val if isinstance(sowing_date_val, datetime.date) else sowing_date_val.date()
            else:
                s_date = None
            if s_date and s_date <= datetime.date.today():
                days_in_field = max(0, (datetime.date.today() - s_date).days)
                has_valid_sowing = True
        except Exception:
            has_valid_sowing = False
            days_in_field = None
            s_date = None

    crop_info = get_crop_profile(crop)
    if has_valid_sowing and days_in_field is not None:
        stage_info = get_growth_stage_by_days(crop, days_in_field)
        days_badge_text = f"🌱 {get_text('stat_days_in_field', lang)}: {days_in_field} {get_text('unit_days', lang)}"
        planting_date_str = s_date.strftime("%d %b %Y") if s_date else str(sowing_date_val)
    else:
        stage_info = None
        days_badge_text = f"🌱 {get_text('stat_days_in_field', lang)}: {get_text('sowing_date_not_provided', lang)}"
        planting_date_str = get_text("sowing_date_not_provided", lang)

    # Resolve coordinates and fetch live weather
    coords = get_district_coordinates(state=state, district=district, village=village)
    weather_data = get_weather_intelligence(
        latitude=coords["latitude"],
        longitude=coords["longitude"],
        force_refresh=False,
    )

    location_str = f"{village}, {district}" if village else f"{district}, {state}"

    # =========================================================================
    # 1. WELCOME HERO BANNER (Modern App Header)
    # =========================================================================
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%); border-radius: 14px; padding: 24px 28px; color: #ffffff; margin-bottom: 22px; box-shadow: 0 4px 14px rgba(27,67,50,0.12);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
                <div>
                    <h2 class="hero-title" data-hero-title="true" style="margin: 0 0 6px 0; color: #ffffff !important; font-size: 1.75rem; font-weight: 700;">
                        {get_text('home_greeting', lang)} 👋
                    </h2>
                    <p style="margin: 0; color: #d8f3dc; font-size: 0.98rem; opacity: 0.95;">
                        📍 <strong>{location_str}</strong> • {get_text('home_subtitle', lang)}
                    </p>
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <span style="background-color: rgba(255,255,255,0.16); backdrop-filter: blur(4px); color: #ffffff; padding: 6px 14px; border-radius: 999px; font-size: 0.84rem; font-weight: 600; border: 1px solid rgba(255,255,255,0.25);">
                        🌿 {crop_info.get(f'crop_name_{lang}', crop)}
                    </span>
                    <span style="background-color: rgba(255,255,255,0.16); backdrop-filter: blur(4px); color: #ffffff; padding: 6px 14px; border-radius: 999px; font-size: 0.84rem; font-weight: 600; border: 1px solid rgba(255,255,255,0.25);">
                        📐 {land_area:.2f} {get_text('unit_acres', lang)}
                    </span>
                    <span style="background-color: rgba(255,255,255,0.16); backdrop-filter: blur(4px); color: #ffffff; padding: 6px 14px; border-radius: 999px; font-size: 0.84rem; font-weight: 600; border: 1px solid rgba(255,255,255,0.25);">
                        🗓️ {get_text('sowing_date_label', lang)}: {planting_date_str}
                    </span>
                    <span style="background-color: rgba(255,255,255,0.16); backdrop-filter: blur(4px); color: #ffffff; padding: 6px 14px; border-radius: 999px; font-size: 0.84rem; font-weight: 600; border: 1px solid rgba(255,255,255,0.25);">
                        {days_badge_text}
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # =========================================================================
    # 1.5 PROMINENT MULTIMODAL AI FARM ADVISOR SPOTLIGHT BANNER
    # =========================================================================
    st.markdown(
        f"""
        <div style="background-color: #FFFFFF; border: 2px solid #2D6A4F; border-radius: 14px; padding: 18px 22px; margin-bottom: 16px; box-shadow: 0 3px 10px rgba(45,106,79,0.08);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div>
                    <div style="font-size: 1.2rem; font-weight: 800; color: #1B4332; display: flex; align-items: center; gap: 8px;">
                        🤖 {'AI Farm Advisor (Voice Microphone & Leaf Pathology Vision)' if lang == 'en' else 'ఏఐ వ్యవసాయ సలహాదారు (వాయిస్ మైక్ & తెగుళ్ల ఫోటో పరీక్ష)'}
                    </div>
                    <div style="font-size: 0.9rem; color: #527964; margin-top: 4px;">
                        {'Speak in English or Telugu (Whisper ASR), snap a photo of diseased leaves for instant ICAR diagnosis, or ask farm planning questions.' if lang == 'en' else 'తెలుగు లేదా ఇంగ్లీషులో మాట్లాడండి, ఆకు తెగులు ఫోటో తీసి తక్షణ నివారణ చర్యలను పొందండి.'}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col_adv1, col_adv2 = st.columns(2)
    with col_adv1:
        st.button(
            "🎙️ " + ("Open Voice & Chat Advisor" if lang == "en" else "వాయిస్ & చాట్ సలహాదారుని తెరవండి"),
            key="home_btn_open_voice_adv",
            type="primary",
            width="stretch",
            on_click=navigate_to,
            args=("AI FARM ADVISOR",),
        )
    with col_adv2:
        st.button(
            "📷 " + ("Open Leaf Disease Diagnosis" if lang == "en" else "ఆకు తెగులు ఫోటో పరీక్ష తెరవండి"),
            key="home_btn_open_vision_adv",
            width="stretch",
            on_click=navigate_to,
            args=("AI FARM ADVISOR",),
        )

    st.markdown("<div style='margin-bottom: 18px;'></div>", unsafe_allow_html=True)

    # Weather extraction
    is_wx_success = weather_data.get("success", False)
    if is_wx_success and weather_data.get("is_offline_cached"):
        cached_ts = weather_data.get("cached_at", "earlier")
        warn_txt = (
            f"ఆఫ్‌లైన్ క్యాష్ స్నాప్‌షాట్ ({cached_ts}): లైవ్ వాతావరణ సేవ తాత్కాలికంగా అందుబాటులో లేదు."
            if lang == "te"
            else f"Offline Cached Snapshot ({cached_ts}): Live weather service is temporarily unreachable."
        )
        st.warning(f"⚠️ {warn_txt}")

    curr = weather_data.get("current", {}) if is_wx_success else {}
    temp = curr.get("temperature")
    rh = curr.get("relative_humidity")
    wind = curr.get("wind_speed")
    precip = curr.get("precipitation")
    w_code = curr.get("weather_code")
    sky_desc = (
        get_weather_description(w_code, lang=lang)
        if (is_wx_success and w_code is not None)
        else get_text("not_available", lang)
    )

    hist_df = weather_data.get("historical_df") if is_wx_success else None
    dry_metrics = compute_dry_spell_metrics(hist_df)
    has_valid_dry = dry_metrics.get("is_valid", False)
    consec_dry = dry_metrics.get("current_consecutive_dry_days") if has_valid_dry else None
    total_30d_rain = dry_metrics.get("total_30d_rainfall") if has_valid_dry else None
    rainy_days = dry_metrics.get("rainy_days_count") if has_valid_dry else None

    fc_df = weather_data.get("forecast_df") if is_wx_success else None
    has_valid_fc_rain = fc_df is not None and not fc_df.empty and "precipitation" in fc_df.columns
    forecast_rain_sum = (
        round(float(fc_df["precipitation"].sum()), 1)
        if has_valid_fc_rain
        else None
    )
    has_valid_fc_temp = fc_df is not None and not fc_df.empty and "temp_max" in fc_df.columns
    peak_fc_temp = (
        round(float(fc_df["temp_max"].max()), 1)
        if has_valid_fc_temp
        else temp
    )

    # Evaluate indicators safely
    indicators = evaluate_climate_indicators(
        forecast_df=fc_df,
        historical_df=hist_df,
        farm_profile=farm_profile,
        current_temp=temp,
        lang=lang,
    )

    heat_ind = next((i for i in indicators if i["id"] == "heat_stress"), None)
    water_ind = next((i for i in indicators if i["id"] == "water_stress"), None)

    # =========================================================================
    # 2. KEY METRICS ROW (Clean Commercial App Cards)
    # =========================================================================
    col1, col2, col3, col4 = st.columns(4)

    temp_val_str = f"{temp:.1f} °C" if temp is not None else get_text("not_available", lang)
    temp_sub_str = f"{sky_desc}" + (f" • 💧 {rh:.0f}%" if rh is not None else "")

    rain_val_str = f"{total_30d_rain:.1f} mm" if total_30d_rain is not None else get_text("not_available", lang)
    rain_sub_str = (
        f"{rainy_days} {get_text('stat_rainy_days', lang).split('(')[0]}"
        if rainy_days is not None
        else get_text("risk_insufficient", lang)
    )

    dry_val_str = f"{consec_dry} {get_text('unit_days', lang)}" if consec_dry is not None else get_text("not_available", lang)
    dry_sub_str = (
        ('Dry days (< 1.0 mm)' if lang == 'en' else 'వర్షం లేని రోజులు')
        if consec_dry is not None
        else get_text("risk_insufficient", lang)
    )

    fc_rain_val_str = f"{forecast_rain_sum:.1f} mm" if forecast_rain_sum is not None else get_text("not_available", lang)
    peak_temp_sub_str = (
        f"{get_text('home_peak_temp', lang)}: {peak_fc_temp:.1f} °C"
        if peak_fc_temp is not None
        else f"{get_text('home_peak_temp', lang)}: {get_text('not_available', lang)}"
    )

    with col1:
        st.markdown(
            f"""
            <div style="background-color: #ffffff; border: 1px solid #e2ebe5; border-radius: 12px; padding: 18px 20px; box-shadow: 0 2px 8px rgba(27,67,50,0.04);">
                <div style="color: #406a52; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                    🌡️ {get_text('curr_temperature', lang)}
                </div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #1b4332; margin-bottom: 4px;">
                    {temp_val_str}
                </div>
                <div style="color: #557c66; font-size: 0.82rem;">
                    {temp_sub_str}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div style="background-color: #ffffff; border: 1px solid #e2ebe5; border-radius: 12px; padding: 18px 20px; box-shadow: 0 2px 8px rgba(27,67,50,0.04);">
                <div style="color: #406a52; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                    🌧️ {get_text('stat_total_30d_rain', lang)}
                </div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #1b4332; margin-bottom: 4px;">
                    {rain_val_str}
                </div>
                <div style="color: #557c66; font-size: 0.82rem;">
                    {rain_sub_str}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div style="background-color: #ffffff; border: 1px solid #e2ebe5; border-radius: 12px; padding: 18px 20px; box-shadow: 0 2px 8px rgba(27,67,50,0.04);">
                <div style="color: #406a52; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                    ☀️ {get_text('stat_current_dry_spell', lang)}
                </div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #1b4332; margin-bottom: 4px;">
                    {dry_val_str}
                </div>
                <div style="color: #557c66; font-size: 0.82rem;">
                    {dry_sub_str}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div style="background-color: #ffffff; border: 1px solid #e2ebe5; border-radius: 12px; padding: 18px 20px; box-shadow: 0 2px 8px rgba(27,67,50,0.04);">
                <div style="color: #406a52; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                    📅 {get_text('home_7d_rain', lang)}
                </div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #1b4332; margin-bottom: 4px;">
                    {fc_rain_val_str}
                </div>
                <div style="color: #557c66; font-size: 0.82rem;">
                    {peak_temp_sub_str}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top: 22px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # 3. ALERTS & PERSONALIZED FARM SUMMARY ROW
    # =========================================================================
    left_col, right_col = st.columns([3, 2], gap="large")

    with left_col:
        st.markdown(f"#### 🛡️ {get_text('home_alerts_title', lang)}")

        # Thermal condition card
        heat_level = heat_ind["risk_level"] if heat_ind else "Insufficient Data"
        heat_badge = heat_ind["risk_level_display"] if heat_ind else get_text("risk_insufficient", lang)
        heat_exp = heat_ind["explanation"] if heat_ind else get_text("risk_insufficient", lang)
        heat_title = heat_ind.get(f"name_{lang}", "Thermal Regime & Heat Conditions") if heat_ind else ("ఉష్ణోగ్రత పరిస్థితులు" if lang == "te" else "Thermal Regime")

        if heat_level == "Alert":
            badge_bg = "#fde8e8"
            badge_color = "#9b111e"
        elif heat_level == "Watch":
            badge_bg = "#fef3c7"
            badge_color = "#92400e"
        elif heat_level == "Insufficient Data":
            badge_bg = "#f3f4f6"
            badge_color = "#4b5563"
        else:
            badge_bg = "#e8f5e9"
            badge_color = "#1b5e20"

        st.markdown(
            f"""
            <div style="background-color: #ffffff; border: 1px solid #e2ebe5; border-left: 5px solid {badge_color}; border-radius: 10px; padding: 16px 18px; margin-bottom: 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.02);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <strong style="color: #1b4332; font-size: 0.96rem;">🌡️ {heat_title}</strong>
                    <span style="background-color: {badge_bg}; color: {badge_color}; padding: 3px 10px; border-radius: 999px; font-size: 0.78rem; font-weight: 700;">
                        {heat_badge}
                    </span>
                </div>
                <p style="margin: 0; color: #2e4a3b; font-size: 0.89rem; line-height: 1.45;">
                    {heat_exp}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Moisture & Water condition card
        water_level = water_ind["risk_level"] if water_ind else "Insufficient Data"
        water_badge = water_ind["risk_level_display"] if water_ind else get_text("risk_insufficient", lang)
        water_exp = water_ind["explanation"] if water_ind else get_text("risk_insufficient", lang)
        water_title = water_ind.get(f"name_{lang}", "Soil Moisture & Irrigation Vulnerability") if water_ind else ("నేల తేమ & నీటి వనరుల స్థితి" if lang == "te" else "Soil Moisture & Water Vulnerability")

        if water_level == "Alert":
            w_bg = "#fde8e8"
            w_color = "#9b111e"
        elif water_level == "Watch":
            w_bg = "#fef3c7"
            w_color = "#92400e"
        elif water_level == "Insufficient Data":
            w_bg = "#f3f4f6"
            w_color = "#4b5563"
        else:
            w_bg = "#e8f5e9"
            w_color = "#1b5e20"

        st.markdown(
            f"""
            <div style="background-color: #ffffff; border: 1px solid #e2ebe5; border-left: 5px solid {w_color}; border-radius: 10px; padding: 16px 18px; margin-bottom: 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.02);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <strong style="color: #1b4332; font-size: 0.96rem;">💧 {water_title}</strong>
                    <span style="background-color: {w_bg}; color: {w_color}; padding: 3px 10px; border-radius: 999px; font-size: 0.78rem; font-weight: 700;">
                        {water_badge}
                    </span>
                </div>
                <p style="margin: 0; color: #2e4a3b; font-size: 0.89rem; line-height: 1.45;">
                    {water_exp}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown(f"#### 💡 {get_text('home_advice_card', lang)}")

        # Personalized stage-based agronomic card
        if has_valid_sowing and days_in_field is not None and stage_info:
            days_str_en = f"(approx. {days_in_field} days in field)"
            days_str_te = f"(సుమారు {days_in_field} రోజులు)"
            stage_header = f"{stage_info.get('stage')} ({stage_info.get('days')} {get_text('unit_days', lang)})"
            if lang == "te":
                advice_text = (
                    f"మీ <strong>{crop_info.get('crop_name_te', crop)}</strong> పంట ప్రస్తుతం <strong>{stage_info.get('stage')}</strong> దశలో ఉంది "
                    f"{days_str_te}. <strong>{soil}</strong> నేలలో నీరు త్వరగా ఆరిపోయే అవకాశం ఉన్నందున, "
                    f"<strong>{irrigation}</strong> ద్వారా క్రమం తప్పకుండా తేలికపాటి తడులు అందించాలి. "
                    f"ఎండ వేడిమి ఎక్కువగా ఉన్నప్పుడు నేలపై వరి గడ్డితో మల్చింగ్ చేయడం వల్ల తేమ ఎక్కువ కాలం నిల్వ ఉంటుంది."
                )
            else:
                advice_text = (
                    f"Your <strong>{crop}</strong> plot is currently in the <strong>{stage_info.get('stage')}</strong> stage "
                    f"{days_str_en}. On <strong>{soil}</strong>, moisture percolation is relatively fast. "
                    f"Maintain regular scheduled irrigations using your <strong>{irrigation}</strong> setup during early morning hours. "
                    f"Surface organic mulching helps shield root-zone moisture from elevated daytime heating."
                )
            stage_water_demand = stage_info.get("water_need", "Standard")
        else:
            stage_header = get_text("stage_not_determined", lang)
            soil_dict = {s["en"]: s[lang] for s in SOIL_TYPES}
            irrig_dict = {i["en"]: i[lang] for i in IRRIGATION_SOURCES}
            soil_loc = soil_dict.get(soil, soil)
            irrig_loc = irrig_dict.get(irrigation, irrigation)
            if lang == "te":
                advice_text = (
                    f"మీ <strong>{crop_info.get('crop_name_te', crop)}</strong> పంటకు సంబంధించి విత్తిన తేదీ నమోదు కాలేదు. "
                    f"దశలవారీ ఖచ్చితమైన నీటి మరియు పోషక యాజమాన్య సలహాల కోసం దయచేసి <strong>'నా పొలం' (My Farm)</strong> విభాగంలో విత్తిన తేదీని నమోదు చేయండి. "
                    f"ప్రస్తుతానికి <strong>{soil_loc}</strong> నేల మరియు <strong>{irrig_loc}</strong> నీటి వనరుకు అనుగుణంగా సాధారణ తేమ పరిరక్షణ జాగ్రత్తలు పాటించండి."
                )
            else:
                advice_text = (
                    f"Planting date for your <strong>{crop}</strong> plot is not provided. "
                    f"Please enter your planting/sowing date in the <strong>My Farm</strong> screen to enable stage-calibrated irrigation and phenological guidance. "
                    f"In the meantime, maintain baseline moisture conservation suitable for <strong>{soil}</strong> and <strong>{irrigation}</strong>."
                )
            stage_water_demand = get_text("stage_not_determined", lang)

        st.markdown(
            f"""
            <div style="background-color: #f4f8f5; border: 1px solid #c8ded0; border-radius: 12px; padding: 18px 20px; box-shadow: 0 2px 6px rgba(27,67,50,0.03);">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                    <span style="font-size: 1.25rem;">🌾</span>
                    <strong style="color: #1b4332; font-size: 0.98rem;">{stage_header}</strong>
                </div>
                <p style="margin: 0 0 14px 0; color: #22382c; font-size: 0.9rem; line-height: 1.55;">
                    {advice_text}
                </p>
                <div style="font-size: 0.8rem; color: #527964; border-top: 1px dashed #c8ded0; padding-top: 8px;">
                    ℹ️ <em>{'Water Demand' if lang == 'en' else 'నీటి అవసరం'}: <strong>{stage_water_demand}</strong> • {get_text('source_icar_angrau', lang)}</em>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # 4. QUICK SHORTCUT ACTIONS (App-Style Navigation Cards)
    # =========================================================================
    st.markdown(f"#### ⚡ {get_text('home_quick_actions', lang)}")

    qcol1, qcol2, qcol3, qcol4, qcol5, qcol6 = st.columns(6)

    nav_cb = navigate_to if navigate_to else None

    with qcol1:
        st.button(
            f"🤖 {get_text('btn_ask_advisor', lang)}",
            key="home_btn_advisor",
            width="stretch",
            on_click=nav_cb,
            args=("AI FARM ADVISOR",),
        )

    with qcol2:
        st.button(
            f"🌦️ {get_text('btn_view_weather', lang)}",
            key="home_btn_weather",
            width="stretch",
            on_click=nav_cb,
            args=("WEATHER",),
        )

    with qcol3:
        st.button(
            f"🌱 {get_text('btn_edit_farm', lang)}",
            key="home_btn_farm",
            width="stretch",
            on_click=nav_cb,
            args=("MY FARM",),
        )

    with qcol4:
        st.button(
            f"📖 {get_text('btn_crop_guide', lang)}",
            key="home_btn_guide",
            width="stretch",
            on_click=nav_cb,
            args=("CROP GUIDANCE",),
        )

    with qcol5:
        st.button(
            f"🔮 {'Simulator' if lang == 'en' else 'సిమ్యులేటర్'}",
            key="home_btn_sim",
            width="stretch",
            on_click=nav_cb,
            args=("SIMULATOR",),
        )

    with qcol6:
        st.button(
            f"🌊 {'ENSO' if lang == 'en' else 'ఎల్ నినో'}",
            key="home_btn_enso",
            width="stretch",
            on_click=nav_cb,
            args=("ENSO",),
        )

    # Footer note
    st.markdown(
        f"""
        <div style="margin-top: 36px; padding-top: 14px; border-top: 1px solid #e2ebe5; font-size: 0.82rem; color: #628672; text-align: center;">
            {get_text('app_disclaimer', lang)}
        </div>
        """,
        unsafe_allow_html=True,
    )
