"""What-If Farm Simulator View.

Interactive climate scenario stress-testing for Turmeric, Banana, and Paddy
in Andhra Pradesh and Telangana.

Features:
1. Scenario Controls: Rainfall reduction (0-60%), Temperature increase (0-5°C),
   Irrigation availability (Normal, Limited, Unavailable), Duration (30, 60, 90 days).
2. Standard 4-Scenario Comparative Suite (Reference, Reduced Rainfall, Drought+Heat, Crisis).
3. Mathematical Water Demand & Thermal Threshold Balance.
4. Stage-specific vulnerability (respecting saved sowing date).
5. Grounded ICAR/ANGRAU/PJTSAU practical precautions.
6. One-click transition to AI Farm Advisor.
"""

from typing import Dict, Any, Optional
import datetime
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from src.localization import get_text
from src.knowledge.crop_knowledge import get_crop_profile
from src.simulation.simulator_engine import (
    get_baseline_climate,
    calculate_scenario,
    generate_comparison_scenarios,
)


def render_simulator_view(
    farm_profile: Dict[str, Any],
    lang: str = "en",
    navigate_to: Optional[Any] = None,
) -> None:
    """Render the What-If Farm Simulator screen."""
    crop = farm_profile.get("crop", "Turmeric")
    crop_info = get_crop_profile(crop)
    district = farm_profile.get("district", "Kurnool").split("(")[0].strip()

    # 1. Header & Title
    st.markdown(f"## 🔮 {get_text('simulator_tab_title', lang)}")
    st.caption(get_text("simulator_tab_subtitle", lang))

    # Duration selector and plot badge
    col_hdr_left, col_hdr_right = st.columns([3, 2])
    with col_hdr_left:
        st.markdown(
            f"""
            <div style="background-color: #ffffff; border: 1px solid #d8e6dc; border-radius: 10px; padding: 10px 14px; margin-bottom: 12px; box-shadow: 0 1px 4px rgba(27,67,50,0.02);">
                <div style="font-size: 0.75rem; font-weight: 700; color: #557c66; text-transform: uppercase;">
                    {'Active Plot Twin' if lang == 'en' else 'ప్రస్తుత పొలం'}
                </div>
                <div style="font-size: 0.96rem; font-weight: 700; color: #1b4332;">
                    📍 {district} • 🌿 {crop_info['crop_name_te'] if lang == 'te' else crop} ({crop_info['botanical_name']})
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_hdr_right:
        duration_choice = st.radio(
            label=get_text("radio_duration_days", lang),
            options=[30, 60, 90],
            format_func=lambda d: f"{d} {'Days' if lang == 'en' else 'రోజులు'}",
            index=0,
            horizontal=True,
            key="sim_duration_radio",
        )

    # 2. Retrieve Baseline Climate & 4-Scenario Comparison Suite
    comparison_bundle = generate_comparison_scenarios(
        farm_profile=farm_profile,
        duration_days=duration_choice,
    )
    baseline = comparison_bundle["baseline"]
    scenarios = comparison_bundle["scenarios"]

    # Save to session state for seamless AI Advisor integration
    st.session_state["simulation_state"] = comparison_bundle

    # Baseline Metadata Banner
    base_rain = baseline["baseline_rainfall_mm"]
    base_temp = baseline["baseline_temp_c"]
    obs_30_r = baseline["observed_30d_rainfall_mm"]
    is_illus = baseline["is_illustrative"]

    banner_bg = "#FFF9C4" if is_illus else "#E8F5E9"
    banner_border = "#FBC02D" if is_illus else "#81C784"
    banner_icon = "⚠️" if is_illus else "ℹ️"

    st.markdown(
        f"""
        <div style="background-color: {banner_bg}; border-left: 4px solid {banner_border}; padding: 10px 14px; border-radius: 6px; font-size: 0.84rem; color: #24332B; margin-bottom: 16px;">
            <strong>{banner_icon} {'Baseline Telemetry:' if lang == 'en' else 'బేస్‌లైన్ వివరాలు:'}</strong> 
            {baseline['source_label']}.<br>
            <span style="color: #406A52;">
                {'Reference' if lang == 'en' else 'సాధారణ'} ({duration_choice}d): <strong>{base_rain} mm</strong> rainfall, 
                <strong>{base_temp}°C</strong> peak daily temperature.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Standard Presets Bar
    st.markdown(f"**⚡ {'Quick Scenario Presets' if lang == 'en' else 'ముందస్తు పరిస్థితులు'}:**")
    preset_cols = st.columns(4)

    # Track selected preset in session state
    if "sim_preset_key" not in st.session_state:
        st.session_state["sim_preset_key"] = "B"

    presets_data = [
        ("A", "Reference", "సాధారణం", 0.0, 0.0, "Normal"),
        ("B", "Rainfall -30%", "వర్షం -30%", 30.0, 0.0, "Normal"),
        ("C", "Drought + Heat", "ఎండ + కరువు", 40.0, 2.5, "Limited"),
        ("D", "Irrigation Crisis", "నీటి కొరత", 50.0, 3.0, "Unavailable"),
    ]

    for idx, (p_key, p_lbl_en, p_lbl_te, p_r, p_t, p_irr) in enumerate(presets_data):
        with preset_cols[idx]:
            p_label = p_lbl_te if lang == "te" else p_lbl_en
            if st.button(
                f"{p_key}: {p_label}",
                key=f"btn_preset_{p_key}",
                width="stretch",
            ):
                st.session_state["sim_preset_key"] = p_key
                st.session_state["sim_slider_rain"] = p_r
                st.session_state["sim_slider_temp"] = p_t
                st.session_state["sim_radio_irr"] = p_irr
                st.rerun()

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    # 4. Interactive Scenario Controls & Active Calculation
    col_ctrl, col_metrics = st.columns([5, 6], gap="medium")

    # Ensure slider state defaults
    if "sim_slider_rain" not in st.session_state:
        st.session_state["sim_slider_rain"] = 30.0
    if "sim_slider_temp" not in st.session_state:
        st.session_state["sim_slider_temp"] = 0.0
    if "sim_radio_irr" not in st.session_state:
        st.session_state["sim_radio_irr"] = "Normal"

    with col_ctrl:
        st.markdown(
            f"""
            <div style="font-size: 0.95rem; font-weight: 700; color: #1B4332; margin-bottom: 8px;">
                🎛️ {get_text('simulator_controls_heading', lang)}
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container():
            custom_rain_red = st.slider(
                label=get_text("slider_rain_reduction", lang),
                min_value=0.0,
                max_value=60.0,
                step=5.0,
                key="sim_slider_rain",
                help="Simulated reduction in cumulative precipitation relative to baseline.",
            )

            custom_temp_inc = st.slider(
                label=get_text("slider_temp_increase", lang),
                min_value=0.0,
                max_value=5.0,
                step=0.5,
                key="sim_slider_temp",
                help="Simulated increase in daily peak temperatures.",
            )

            irr_options = ["Normal", "Limited", "Unavailable"]
            irr_labels = {
                "Normal": get_text("irr_normal", lang),
                "Limited": get_text("irr_limited", lang),
                "Unavailable": get_text("irr_unavailable", lang),
            }
            custom_irr = st.radio(
                label=get_text("radio_irrigation_status", lang),
                options=irr_options,
                format_func=lambda x: irr_labels[x],
                key="sim_radio_irr",
                horizontal=False,
            )

    # Compute custom active scenario
    active_result = calculate_scenario(
        baseline=baseline,
        crop_profile=crop_info,
        farm_profile=farm_profile,
        rain_reduction_pct=custom_rain_red,
        temp_increase_c=custom_temp_inc,
        irrigation_status=custom_irr,
        scenario_name="Active Custom Scenario",
    )

    # Update active scenario in session state
    st.session_state["simulation_active_result"] = active_result

    with col_metrics:
        st.markdown(
            f"""
            <div style="font-size: 0.95rem; font-weight: 700; color: #1B4332; margin-bottom: 8px;">
                📊 {'Impact Assessment' if lang == 'en' else 'ప్రభావ విశ్లేషణ'}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 4 Key Metric Cards
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            rain_val = f"{active_result['rainfall']['scenario_mm']} mm"
            rain_delta = f"-{active_result['rainfall']['deficit_mm']} mm (-{custom_rain_red:.0f}%)" if custom_rain_red > 0 else "0 mm (Normal)"
            st.metric(
                label="🌧️ " + ("Rainfall" if lang == "en" else "వర్షపాతం"),
                value=rain_val,
                delta=rain_delta,
                delta_color="inverse" if custom_rain_red > 0 else "off",
            )
        with m_col2:
            temp_val = f"{active_result['temperature']['scenario_c']}°C"
            temp_delta = f"+{custom_temp_inc:.1f}°C" if custom_temp_inc > 0 else "0.0°C (Normal)"
            st.metric(
                label="🌡️ " + ("Peak Temperature" if lang == "en" else "గరిష్ట ఉష్ణోగ్రత"),
                value=temp_val,
                delta=temp_delta,
                delta_color="inverse" if custom_temp_inc > 0 else "off",
            )

        m_col3, m_col4 = st.columns(2)
        with m_col3:
            sat_val = f"{active_result['water_balance']['satisfaction_pct']}%"
            sat_delta = f"-{active_result['water_balance']['net_deficit_mm']} mm deficit" if active_result['water_balance']['net_deficit_mm'] > 0 else "Demand Satisfied"
            st.metric(
                label="💧 " + ("Water Satisfaction" if lang == "en" else "నీటి సంతృప్తి"),
                value=sat_val,
                delta=sat_delta,
                delta_color="inverse" if active_result['water_balance']['net_deficit_mm'] > 0 else "normal",
            )
        with m_col4:
            comp_eval = active_result["evaluations"]["composite"]
            risk_name = comp_eval["risk_level_te"] if lang == "te" else comp_eval["risk_level"]
            st.markdown(
                f"""
                <div style="background-color: {comp_eval['badge_bg']}; border: 1.5px solid {comp_eval['color']}; border-radius: 10px; padding: 12px 14px; text-align: center; margin-top: 4px;">
                    <div style="font-size: 0.72rem; font-weight: 700; color: #555; text-transform: uppercase;">
                        {'Risk Status' if lang == 'en' else 'రిస్క్ స్థాయి'}
                    </div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: {comp_eval['color']}; margin-top: 2px;">
                        {risk_name}
                    </div>
                    <div style="font-size: 0.75rem; color: #666; margin-top: 2px;">
                        {'Composite Score:' if lang == 'en' else 'స్కోర్:'} {comp_eval['score']}/10
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<hr style='border: none; border-top: 1px solid #E2EBE5; margin: 20px 0;'>", unsafe_allow_html=True)

    # 5. Side-by-Side 4-Scenario Comparative Matrix
    st.markdown(f"### 📋 {get_text('simulator_comparison_heading', lang)}")
    st.caption(
        "Compare reference conditions against drought, elevated thermal regimes, and irrigation shortages."
        if lang == "en"
        else "సాధారణ వాతావరణం, వర్షాభావం, అధిక వేడి మరియు నీటి కొరత పరిస్థితుల మధ్య తేడాలను పరిశీలించండి."
    )

    # Matrix Table Display
    matrix_rows = []
    for k in ["A", "B", "C", "D"]:
        sc = scenarios[k]
        matrix_rows.append({
            "Scenario / పరిస్థితి": sc["name_te"] if lang == "te" else sc["name_en"],
            "Rainfall (mm)": f"{sc['rainfall']['scenario_mm']} mm",
            "Rain Delta": f"-{sc['rainfall']['reduction_pct']:.0f}%",
            "Temp (°C)": f"{sc['temperature']['scenario_c']}°C",
            "Irrigation": sc["inputs"]["irrigation_status"],
            "Water Saturation (%)": f"{sc['water_balance']['satisfaction_pct']}%",
            "Net Deficit (mm)": f"{sc['water_balance']['net_deficit_mm']} mm",
            "Risk Level": sc["evaluations"]["composite"]["risk_level_te"] if lang == "te" else sc["evaluations"]["composite"]["risk_level"],
            "Score": f"{sc['evaluations']['composite']['score']}/10",
        })

    df_matrix = pd.DataFrame(matrix_rows)
    st.dataframe(df_matrix, width="stretch", hide_index=True)

    # 6. Interactive Visual Comparison Chart
    st.markdown(f"#### 📈 {'Comparative Water & Thermal Stress Chart' if lang == 'en' else 'నీటి లభ్యత & ఉష్ణోగ్రత పోలిక చార్ట్'}")

    sc_labels = [scenarios[k]["name_en"].split(":")[0] for k in ["A", "B", "C", "D"]]
    sc_effective_water = [scenarios[k]["water_balance"]["effective_water_mm"] for k in ["A", "B", "C", "D"]]
    sc_demand = [scenarios[k]["water_balance"]["crop_demand_mm"] for k in ["A", "B", "C", "D"]]
    sc_temps = [scenarios[k]["temperature"]["scenario_c"] for k in ["A", "B", "C", "D"]]
    stress_temp = crop_info["optimal_temperature_c"]["stress_above"]

    fig = go.Figure()

    # Bar 1: Effective Water Supply
    fig.add_trace(go.Bar(
        x=sc_labels,
        y=sc_effective_water,
        name="Effective Water (mm)" if lang == "en" else "లభించే నీరు (మి.మీ)",
        marker_color="#2D6A4F",
        yaxis="y1",
    ))

    # Bar 2: Crop Water Demand
    fig.add_trace(go.Bar(
        x=sc_labels,
        y=sc_demand,
        name="Crop Demand (mm)" if lang == "en" else "పంట నీటి అవసరం (మి.మీ)",
        marker_color="#B7E4C7",
        yaxis="y1",
    ))

    # Line: Peak Temperature
    fig.add_trace(go.Scatter(
        x=sc_labels,
        y=sc_temps,
        name="Scenario Temp (°C)" if lang == "en" else "ఉష్ణోగ్రత (°C)",
        marker=dict(color="#D9534F", size=9),
        line=dict(color="#D9534F", width=3, dash="dot"),
        yaxis="y2",
    ))

    fig.update_layout(
        barmode="group",
        height=340,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(
            title=dict(
                text="Water (mm)" if lang == "en" else "నీరు (మి.మీ)",
                font=dict(color="#1B4332"),
            ),
            tickfont=dict(color="#1B4332"),
        ),
        yaxis2=dict(
            title=dict(
                text="Temperature (°C)" if lang == "en" else "ఉష్ణోగ్రత (°C)",
                font=dict(color="#D9534F"),
            ),
            tickfont=dict(color="#D9534F"),
            overlaying="y",
            side="right",
            range=[20, 45],
        ),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FAFCFA",
    )

    st.plotly_chart(fig, width="stretch")

    # 7. Crop Phenology & Stage Vulnerability (Respecting actual sowing date)
    st.markdown(f"### 🌾 {'Crop-Stage Vulnerability Assessment' if lang == 'en' else 'పంట ఎదుగుదల దశ & సున్నితత్వం'}")

    pheno = active_result["phenology"]
    if pheno["has_valid_sowing"]:
        days_f = pheno["days_in_field"]
        stage_name = pheno["stage_name"]
        water_need = pheno["water_need"]
        st.markdown(
            f"""
            <div style="background-color: #ffffff; border: 1px solid #d8e6dc; border-radius: 10px; padding: 14px 18px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(27,67,50,0.03);">
                <div style="display: flex; gap: 20px; align-items: center; flex-wrap: wrap;">
                    <div>
                        <span style="font-size: 0.75rem; color: #557c66; font-weight: 700; text-transform: uppercase;">
                            {'Days in Field' if lang == 'en' else 'పంట వయస్సు'}
                        </span>
                        <div style="font-size: 1.15rem; font-weight: 700; color: #1b4332;">{days_f} {'days' if lang == 'en' else 'రోజులు'}</div>
                    </div>
                    <div>
                        <span style="font-size: 0.75rem; color: #557c66; font-weight: 700; text-transform: uppercase;">
                            {'Active Phenological Stage' if lang == 'en' else 'ప్రస్తుత దశ'}
                        </span>
                        <div style="font-size: 1.15rem; font-weight: 700; color: #1b4332;">{stage_name}</div>
                    </div>
                    <div>
                        <span style="font-size: 0.75rem; color: #557c66; font-weight: 700; text-transform: uppercase;">
                            {'Stage Water Demand' if lang == 'en' else 'దశ నీటి అవసరం'}
                        </span>
                        <div style="font-size: 1.15rem; font-weight: 700; color: #1b4332;">{water_need} ({pheno['daily_et_mm']} mm/day)</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style="background-color: #F8F9FA; border: 1px dashed #B0BEC5; border-radius: 8px; padding: 14px 16px; margin-bottom: 16px; font-size: 0.88rem; color: #37474F;">
                🗓️ <strong>{'Crop Age Not Set:' if lang == 'en' else 'విత్తిన తేదీ నమోదు చేయలేదు:'}</strong> 
                {'Phenological growth stage is not determined because no sowing date is recorded. Using general crop baseline (4.0-6.8 mm/day). To enable stage-calibrated assessments, please specify your sowing date in the' if lang == 'en' else 'ఖచ్చితమైన దశలవారీ నీటి అవసరాల కోసం దయచేసి'} 
                <strong>{'My Farm' if lang == 'en' else 'నా పొలం'}</strong> {'screen.' if lang == 'en' else 'విభాగంలో విత్తిన తేదీని నమోదు చేయండి.'}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 8. Practical Precautions (ICAR & ANGRAU Grounded)
    st.markdown(f"### 🛡️ {'Recommended Institutional Precautions' if lang == 'en' else 'సిఫార్సు చేయబడిన రక్షణ చర్యలు'}")

    precautions = active_result["precautions_te"] if lang == "te" else active_result["precautions_en"]
    for p in precautions:
        st.markdown(
            f"""
            <div style="background-color: #ffffff; border: 1px solid #d8e6dc; border-left: 4px solid #2D6A4F; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(27,67,50,0.02);">
                <div style="font-size: 0.94rem; font-weight: 700; color: #1B4332;">
                    {p['title']}
                </div>
                <div style="font-size: 0.86rem; color: #24332B; margin-top: 4px; line-height: 1.5;">
                    {p['details']}
                </div>
                <div style="font-size: 0.72rem; color: #64736B; margin-top: 4px;">
                    📚 <em>{'Authority:' if lang == 'en' else 'మూలం:'} {p.get('source', 'ICAR & ANGRAU')}</em>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 9. One-Click AI Advisor Integration Button
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    col_ask_adv, _ = st.columns([2, 1])
    with col_ask_adv:
        adv_prompt = (
            "నా పసుపు పంటకు ఏ పరిస్థితి ఎక్కువ ప్రమాదకరం?"
            if lang == "te"
            else f"Which scenario is most concerning for my {crop.lower()} crop?"
        )
        def _on_ask_advisor():
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
            st.session_state["pending_advisor_query"] = adv_prompt
            if navigate_to:
                navigate_to("AI FARM ADVISOR")

        st.button(
            "🤖 " + get_text("btn_ask_advisor_sim", lang),
            key="btn_goto_advisor_from_sim",
            width="stretch",
            type="primary",
            on_click=_on_ask_advisor,
        )

    # 10. Uncertainty & Methodology Expander
    expander_title = "ℹ️ " + ("Mathematical Engine Assumptions & Disclaimers" if lang == "en" else "సిమ్యులేషన్ సూత్రాలు & పరిమితులు")
    disclaimer_str = get_text("simulator_disclaimer", lang)
    with st.expander(expander_title, expanded=False):
        st.markdown(
            "- **Reference Climate Period:** Open-Meteo Operational Analysis Grid (~11 km resolution) derived from past 30-day precipitation.\n"
            "- **Extrapolation Policy:** For 60-day and 90-day durations, rainfall is linearly scaled from the 30-day observed rate. It serves as an illustrative stress test, not a 30-year IMD climatological normal.\n"
            "- **Water Balance Formula:** Water Satisfaction (%) = min(100, (Scenario_Rainfall + Supplemental_Irrigation) / Crop_Water_Demand * 100)\n"
            "- **Thermal Sensitivity Limits:** Turmeric (20-35°C, stress > 38°C); Banana (25-32°C, stress > 38°C); Paddy (22-33°C, spikelet sterility > 35°C).\n"
            f"- **Disclaimer:** {disclaimer_str}"
        )
