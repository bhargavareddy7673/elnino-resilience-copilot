"""Crop Guidance Screen Component: Agronomic Package of Practices & Resilience Measures.

Comprehensive, practical guide for Turmeric, Banana, and Paddy:
1. Physiological baseline (temperature thresholds, water demand, soil suitability).
2. Growth stages and phenological water requirements.
3. Climate contingency practices (organic mulching, AWD, drainage furrows, windbreaks).
4. Authoritative institutional references (ICAR, ANGRAU, IMD, PJTSAU).
"""

from typing import Dict, Any
import streamlit as st

from src.localization import get_text
from src.knowledge.crop_knowledge import (
    get_crop_profile,
)


def render_crop_guidance_view(farm_profile: Dict[str, Any], lang: str = "en") -> None:
    """Render the Crop Guidance screen.
    
    Args:
        farm_profile: Active digital twin dictionary from session state.
        lang: Active language ('en' or 'te').
    """
    st.markdown(f"### 📖 {get_text('guidance_title', lang)}")
    st.caption(get_text("guidance_subtitle", lang))

    current_crop = farm_profile.get("crop", "Turmeric")
    crop_keys = ["Turmeric", "Banana", "Paddy"]

    # Interactive Crop Selector Pills (Bilingual)
    crop_display_names = {
        "Turmeric": "🌿 Turmeric (పసుపు)" if lang == "en" else "🌿 పసుపు (Turmeric)",
        "Banana": "🍌 Banana (అరటి)" if lang == "en" else "🍌 అరటి (Banana)",
        "Paddy": "🌾 Paddy / Rice (వరి)" if lang == "en" else "🌾 వరి (Paddy / Rice)",
    }

    selected_crop = st.radio(
        label="Select Crop to Inspect / పంటను ఎంచుకోండి:" if lang == "en" else "పంటను ఎంచుకోండి (Select Crop):",
        options=crop_keys,
        format_func=lambda k: crop_display_names[k],
        index=crop_keys.index(current_crop) if current_crop in crop_keys else 0,
        horizontal=True,
        key="crop_guide_selector",
    )

    info = get_crop_profile(selected_crop)
    botanical = info.get("botanical_name", "")
    crop_name = info.get(f"crop_name_{lang}", selected_crop)
    opt_temp = info.get("optimal_temperature_c", {})
    rain_range = info.get("annual_rainfall_mm", {})
    suitable_soils = info.get("suitable_soils", [])
    vulnerable_soils = info.get("vulnerable_soils", [])
    stages = info.get("growth_stages", [])
    practices = info.get("resilience_practices", [])
    refs = info.get("references", [])

    is_farmer_crop = selected_crop == current_crop
    active_crop_badge = (
        f"<span style='background-color: #2d6a4f; color: #ffffff; padding: 4px 12px; border-radius: 999px; font-size: 0.78rem; font-weight: 600; white-space: nowrap; display: inline-block;'>{'✓ Your Active Farm Crop' if lang == 'en' else '✓ మీ ప్రస్తుత వ్యవసాయ పంట'}</span>"
        if is_farmer_crop
        else ""
    )

    # Header Card: Clean, robust, single-block HTML with zero whitespace indentation
    header_html = (
        f"<div style='background-color: #ffffff; border: 1px solid #c8ded0; border-radius: 12px; padding: 20px 24px; margin: 16px 0 22px 0; box-shadow: 0 2px 8px rgba(27,67,50,0.04);'>"
        f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;'>"
        f"<h3 style='margin: 0; color: #1b4332; font-size: 1.45rem; line-height: 1.3; flex-shrink: 0;'>"
        f"{crop_name} <span style='font-weight: 400; color: #557c66; font-size: 1.05rem;'>({botanical})</span>"
        f"</h3>"
        f"{active_crop_badge}"
        f"</div>"
        f"<p style='margin: 0; color: #2e4a3b; font-size: 0.94rem; line-height: 1.55;'>"
        f"{info['temperature_sensitivity'][lang]}"
        f"</p>"
        f"</div>"
    )
    st.markdown(header_html, unsafe_allow_html=True)

    # Section 1: Physiological Baseline & Soil Compatibility
    col_bio1, col_bio2 = st.columns(2, gap="large")

    with col_bio1:
        heat_val = f"Above {opt_temp.get('stress_above')}°C" if lang == "en" else f"{opt_temp.get('stress_above')}°C కంటే ఎక్కువ"
        water_val = f"{rain_range.get('min')} - {rain_range.get('max')} mm / {'year' if lang == 'en' else 'సంవత్సరానికి'}"
        col1_html = (
            f"<div style='background-color: #f4f8f5; border: 1px solid #c8ded0; border-radius: 10px; padding: 18px 20px; height: 100%; box-shadow: 0 1px 4px rgba(27,67,50,0.02);'>"
            f"<h4 style='margin: 0 0 12px 0; color: #1b4332; font-size: 1.05rem;'>🌡️ {'Temperature & Rainfall Thresholds' if lang == 'en' else 'ఉష్ణోగ్రత & వర్షపాతం కొలమానాలు'}</h4>"
            f"<div style='margin-bottom: 8px; color: #22382c; font-size: 0.9rem;'>"
            f"<strong>{'Optimal Thermal Range' if lang == 'en' else 'అనుకూల ఉష్ణోగ్రత పరిధి'}:</strong> <code>{opt_temp.get('min')}°C - {opt_temp.get('max')}°C</code>"
            f"</div>"
            f"<div style='margin-bottom: 8px; color: #22382c; font-size: 0.9rem;'>"
            f"<strong>{'High Heat Stress Limit' if lang == 'en' else 'అధిక వేడిమి ఒత్తిడి పరిమితి'}:</strong> <code>{heat_val}</code>"
            f"</div>"
            f"<div style='margin-bottom: 8px; color: #22382c; font-size: 0.9rem;'>"
            f"<strong>{'Optimal Water Range' if lang == 'en' else 'అనుకూల వార్షిక వర్షపాతం'}:</strong> <code>{water_val}</code>"
            f"</div>"
            f"<div style='margin-top: 10px; font-size: 0.85rem; color: #406a52; line-height: 1.45;'>"
            f"{info['water_sensitivity'][lang]}"
            f"</div>"
            f"</div>"
        )
        st.markdown(col1_html, unsafe_allow_html=True)

    with col_bio2:
        soils = info.get("suitable_soils_te", suitable_soils) if lang == "te" else suitable_soils
        vuln = info.get("vulnerable_soils_te", vulnerable_soils) if lang == "te" else vulnerable_soils
        soils_li = "".join(f"<li style='margin-bottom: 4px;'>{s}</li>" for s in soils)
        vuln_li = "".join(f"<li style='margin-bottom: 4px;'>{v}</li>" for v in vuln)
        col2_html = (
            f"<div style='background-color: #f4f8f5; border: 1px solid #c8ded0; border-radius: 10px; padding: 18px 20px; height: 100%; box-shadow: 0 1px 4px rgba(27,67,50,0.02);'>"
            f"<h4 style='margin: 0 0 12px 0; color: #1b4332; font-size: 1.05rem;'>🏞️ {'Soil Compatibility' if lang == 'en' else 'నేల అనుకూలత'}</h4>"
            f"<div style='margin-bottom: 10px; font-size: 0.88rem; color: #1b4332;'>"
            f"<strong>{'Recommended Soils' if lang == 'en' else 'సిఫార్సు చేయబడిన నేలలు'}:</strong>"
            f"<ul style='margin: 4px 0 0 16px; padding: 0; color: #2d5a3f; line-height: 1.4;'>"
            f"{soils_li}"
            f"</ul>"
            f"</div>"
            f"<div style='font-size: 0.88rem; color: #9b111e;'>"
            f"<strong>{'Vulnerable Soils' if lang == 'en' else 'సున్నితమైన / ప్రమాదకర నేలలు'}:</strong>"
            f"<ul style='margin: 4px 0 0 16px; padding: 0; color: #742a2a; line-height: 1.4;'>"
            f"{vuln_li}"
            f"</ul>"
            f"</div>"
            f"</div>"
        )
        st.markdown(col2_html, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 26px;'></div>", unsafe_allow_html=True)

    # Section 2: Growth Stages & Water Demand (Balanced responsive rows)
    st.markdown(f"#### 🗓️ {get_text('crop_stages_heading', lang)}")
    cols_per_row = 3 if len(stages) > 4 else len(stages)
    for row_idx in range(0, len(stages), cols_per_row):
        row_stages = stages[row_idx : row_idx + cols_per_row]
        stage_cols = st.columns(len(row_stages), gap="small")
        for c_idx, s in enumerate(row_stages):
            idx = row_idx + c_idx
            with stage_cols[c_idx]:
                water_color = (
                    "#9b111e"
                    if s["water_need"] in ["Critical", "Most Critical"]
                    else ("#f77f00" if s["water_need"] == "High" else "#2d6a4f")
                )
                stage_name = s.get("stage_te", s["stage"]) if lang == "te" else s["stage"]
                water_badge_text = (
                    f"{s['water_need']} Water"
                    if lang == "en"
                    else f"{s.get('water_need_te', s['water_need'])} నీటి అవసరం"
                )
                stage_html = (
                    f"<div style='background-color: #ffffff; border: 1px solid #e2ebe5; border-radius: 10px; padding: 14px 12px; height: 100%; box-shadow: 0 1px 4px rgba(0,0,0,0.02); text-align: center; margin-bottom: 10px;'>"
                    f"<div style='color: #628672; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;'>{'Stage' if lang == 'en' else 'దశ'} {idx+1}</div>"
                    f"<div style='color: #1b4332; font-weight: 700; font-size: 0.92rem; margin: 4px 0; min-height: 2.4rem; display: flex; align-items: center; justify-content: center;'>{stage_name}</div>"
                    f"<div style='color: #557c66; font-size: 0.78rem; margin-bottom: 8px;'>{s['days']} {'Days' if lang == 'en' else 'రోజులు'}</div>"
                    f"<span style='background-color: #f4f8f5; color: {water_color}; border: 1px solid #d8e5dc; padding: 2px 10px; border-radius: 999px; font-size: 0.74rem; font-weight: 700; display: inline-block;'>"
                    f"{water_badge_text}"
                    f"</span>"
                    f"</div>"
                )
                st.markdown(stage_html, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 26px;'></div>", unsafe_allow_html=True)

    # Section 3: Recommended Climate Resilience Practices
    st.markdown(f"#### 🛡️ {get_text('crop_resilience_heading', lang)}")
    prac_col1, prac_col2, prac_col3 = st.columns(3, gap="medium")
    cols = [prac_col1, prac_col2, prac_col3]

    for idx, p in enumerate(practices):
        target_col = cols[idx % 3]
        with target_col:
            p_title = p["practice_te"] if lang == "te" else p["practice_en"]
            p_desc = p["details_te"] if lang == "te" else p["details_en"]
            prac_html = (
                f"<div style='background-color: #ffffff; border: 1px solid #e2ebe5; border-left: 4px solid #2d6a4f; border-radius: 10px; padding: 16px 18px; height: 100%; box-shadow: 0 1px 4px rgba(0,0,0,0.02); margin-bottom: 12px;'>"
                f"<strong style='color: #1b4332; font-size: 0.96rem; display: block; margin-bottom: 6px;'>{p_title}</strong>"
                f"<p style='margin: 0; color: #2e4a3b; font-size: 0.88rem; line-height: 1.55;'>{p_desc}</p>"
                f"</div>"
            )
            st.markdown(prac_html, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 26px;'></div>", unsafe_allow_html=True)

    # Section 4: Authoritative Institutional References
    st.markdown(f"#### 📚 {get_text('institutional_sources_heading', lang)}")
    ref_container = st.container()
    with ref_container:
        for r in refs:
            auth = f"{r['authority']} ({r['authority_te']})" if (lang == "te" and "authority_te" in r) else r["authority"]
            doc = f"{r.get('document_te', r['document'])}" if lang == "te" else r["document"]
            st.markdown(
                f"- **{auth}**: *{doc}* — [{r['url']}]({r['url']})"
            )
