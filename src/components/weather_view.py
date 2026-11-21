"""Weather Screen Component: Regional Climate Intelligence & Agricultural Weather.

Provides a clean commercial-grade meteorological interface:
1. Current atmospheric telemetry cards.
2. Future Weather Explorer & Farm Planning Desk (interactive target date selector).
3. 16-day numerical weather forecast (Plotly charts, daily cards, extended horizon).
4. Recent 30-day precipitation history, cumulative rainfall, and dry-spell duration.
5. Transparent agricultural climate risk indicators.
6. Scientific boundary education: Forecast Horizon vs. What-If Scenario Simulator.
7. Factual reanalysis and forecast data source attribution (Open-Meteo, CC BY 4.0).
"""

from typing import Dict, Any, Optional, Callable
import datetime
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.localization import get_text
from src.weather.location_service import get_district_coordinates
from src.weather.weather_api import get_weather_intelligence, get_weather_description
from src.weather.weather_analysis import (
    compute_dry_spell_metrics,
    compute_forecast_dry_spells,
    evaluate_climate_indicators,
    analyze_future_date_plan,
)
from src.knowledge.crop_knowledge import (
    get_crop_profile,
    get_growth_stage_by_days,
)


def render_weather_view(
    farm_profile: Dict[str, Any],
    lang: str = "en",
    navigate_to: Optional[Callable[[str], None]] = None,
) -> None:
    """Render the Weather screen.
    
    Args:
        farm_profile: Active digital twin dictionary from session state.
        lang: Selected language ('en' or 'te').
        navigate_to: Optional navigation callback to switch screens.
    """
    state = farm_profile.get("state", "Andhra Pradesh")
    district = farm_profile.get("district", "Kurnool")
    village = farm_profile.get("village", "").strip()
    crop = farm_profile.get("crop", "Turmeric")
    sowing_date_val = farm_profile.get("sowing_date")

    # 1. Resolve Geographic Coordinates
    loc_info = get_district_coordinates(state=state, district=district, village=village)
    lat = loc_info["latitude"]
    lon = loc_info["longitude"]

    # Header Row
    col_hdr, col_ref = st.columns([3, 1])
    with col_hdr:
        location_display = f"**{village}**, {district}" if village else f"**{district}**, {state}"
        st.markdown(f"### 🌦️ {get_text('weather_section_title', lang)}")
        st.caption(f"📍 {location_display} • Coordinates: `{lat:.4f}°N, {lon:.4f}°E`")
    with col_ref:
        refresh_clicked = st.button(
            label=f"🔄 {get_text('btn_refresh_weather', lang)}",
            key="btn_refresh_wx_view",
            width="stretch",
        )

    # 2. Fetch Live Weather Data from Open-Meteo
    weather_data = get_weather_intelligence(
        latitude=lat,
        longitude=lon,
        force_refresh=refresh_clicked,
    )

    # Offline cache notification
    if weather_data.get("is_offline_cached"):
        cached_ts = weather_data.get("cached_at", "earlier")
        warn_txt = (
            f"ఆఫ్‌లైన్ క్యాష్ స్నాప్‌షాట్: ప్రత్యక్ష వాతావరణ సేవ తాత్కాలికంగా అందుబాటులో లేదు. "
            f"గతంలో భద్రపరచబడిన స్నాప్‌షాట్ ({cached_ts}) ప్రదర్శించబడుతోంది."
            if lang == "te"
            else f"Offline Cached Snapshot: Live weather service is temporarily unreachable. "
            f"Displaying snapshot previously retrieved on {cached_ts}."
        )
        col_w1, col_w2 = st.columns([4, 1])
        with col_w1:
            st.warning(f"⚠️ {warn_txt}")
        with col_w2:
            if st.button(
                label=f"🔄 {get_text('btn_refresh_live_weather', lang)}",
                key="btn_retry_live_banner",
                width="stretch",
            ):
                st.session_state["weather_force_retry"] = True
                st.rerun()

    # 3. Handle Failure State
    if not weather_data.get("success", False):
        err_msg = weather_data.get("error", "Network connection unavailable")
        diag_msg = weather_data.get("diagnostic", "Check internet access and click Refresh.")
        st.markdown(
            f"""
            <div style="background-color: #fdf2f2; border: 1px solid #f5c6cb; border-left: 5px solid #d90429; padding: 18px 20px; border-radius: 10px; margin: 16px 0;">
                <h4 style="color: #9b111e; margin: 0 0 8px 0; font-size: 1.05rem;">⚠️ {get_text('api_error_title', lang)}</h4>
                <p style="color: #4a1515; margin: 0 0 10px 0; font-size: 0.92rem;">{get_text('api_error_desc', lang)}</p>
                <div style="background-color: #ffffff; border: 1px solid #fed7d7; border-radius: 6px; padding: 8px 12px; font-size: 0.82rem; color: #742a2a;">
                    <strong>Error Diagnostic:</strong> {err_msg} ({diag_msg})
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(f"🔄 {get_text('btn_refresh_weather', lang)}", key="btn_retry_after_failure"):
            st.rerun()
        return

    # Extract Data Elements
    current = weather_data.get("current", {})
    forecast_df = weather_data.get("forecast_df")
    historical_df = weather_data.get("historical_df")
    retrieved_at = weather_data.get("retrieved_at", "Just now")
    dry_metrics = compute_dry_spell_metrics(historical_df)
    forecast_metrics = compute_forecast_dry_spells(forecast_df)

    curr_temp = current.get("temperature")
    curr_rh = current.get("relative_humidity")
    curr_wind = current.get("wind_speed")
    curr_precip = current.get("precipitation")
    w_code = current.get("weather_code")
    sky_desc = get_weather_description(w_code, lang=lang) if w_code is not None else get_text("not_available", lang)

    temp_str = f"{curr_temp:.1f} °C" if curr_temp is not None else get_text("not_available", lang)
    rh_str = f"{curr_rh:.0f} %" if curr_rh is not None else get_text("not_available", lang)
    wind_str = f"{curr_wind:.1f} km/h" if curr_wind is not None else get_text("not_available", lang)
    precip_str = f"{curr_precip:.1f} mm" if curr_precip is not None else get_text("not_available", lang)

    rh_sub = "సాపేక్ష గాలి తేమ" if lang == "te" else "Relative Air Moisture"
    wind_sub = "10 మీటర్ల ఎత్తులో గాలి వేగం" if lang == "te" else "Velocity at 10m height"
    precip_sub = "ప్రస్తుత వర్షపాతం" if lang == "te" else "Current Precipitation"

    st.markdown(
        f"<div style='font-size: 0.82rem; color: #406a52; margin-bottom: 14px;'>"
        f"<strong>{get_text('weather_retrieved_at', lang)}:</strong> {retrieved_at} • "
        f"<strong>Source:</strong> Open-Meteo High-Resolution Model (Asia/Kolkata)</div>",
        unsafe_allow_html=True,
    )

    # =========================================================================
    # 1. CURRENT TELEMETRY (4 Clean Cards)
    # =========================================================================
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div style="background-color: #ffffff; border: 1px solid #e2ebe5; border-radius: 12px; padding: 18px 20px; box-shadow: 0 2px 8px rgba(27,67,50,0.04);">
                <div style="color: #406a52; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">🌡️ {get_text('curr_temperature', lang)}</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #1b4332; margin: 4px 0;">{temp_str}</div>
                <div style="color: #557c66; font-size: 0.82rem;">{sky_desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div style="background-color: #ffffff; border: 1px solid #e2ebe5; border-radius: 12px; padding: 18px 20px; box-shadow: 0 2px 8px rgba(27,67,50,0.04);">
                <div style="color: #406a52; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">💧 {get_text('curr_humidity', lang)}</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #1b4332; margin: 4px 0;">{rh_str}</div>
                <div style="color: #557c66; font-size: 0.82rem;">{rh_sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div style="background-color: #ffffff; border: 1px solid #e2ebe5; border-radius: 12px; padding: 18px 20px; box-shadow: 0 2px 8px rgba(27,67,50,0.04);">
                <div style="color: #406a52; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">💨 {get_text('curr_wind_speed', lang)}</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #1b4332; margin: 4px 0;">{wind_str}</div>
                <div style="color: #557c66; font-size: 0.82rem;">{wind_sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
            <div style="background-color: #ffffff; border: 1px solid #e2ebe5; border-radius: 12px; padding: 18px 20px; box-shadow: 0 2px 8px rgba(27,67,50,0.04);">
                <div style="color: #406a52; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">🌧️ {get_text('curr_precipitation', lang)}</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #1b4332; margin: 4px 0;">{precip_str}</div>
                <div style="color: #557c66; font-size: 0.82rem;">{precip_sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top: 26px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # 2. FUTURE WEATHER EXPLORER & FARM PLANNING DESK (Interactive Date Selector)
    # =========================================================================
    st.markdown(f"#### 🧭 {get_text('future_planner_heading', lang)}")
    st.caption(get_text("future_planner_subheading", lang))

    today_val = datetime.date.today()
    default_target_date = today_val + datetime.timedelta(days=1)

    # Phenological stage detection from farm profile
    stage_info = None
    if sowing_date_val:
        try:
            s_d = sowing_date_val if isinstance(sowing_date_val, datetime.date) else datetime.date.fromisoformat(str(sowing_date_val))
            days_in_field = max(0, (today_val - s_d).days)
            stage_info = get_growth_stage_by_days(crop, days_in_field)
        except Exception:
            stage_info = None

    col_pick, col_info = st.columns([1, 2], gap="medium")
    with col_pick:
        selected_date = st.date_input(
            label=f"📅 {get_text('future_date_picker_label', lang)}",
            value=default_target_date,
            min_value=today_val - datetime.timedelta(days=30),
            max_value=today_val + datetime.timedelta(days=45),
            help=get_text("future_date_picker_help", lang),
            key="wx_target_planning_date_input",
        )
        if isinstance(selected_date, (list, tuple)):
            selected_date = selected_date[0] if selected_date else default_target_date

    # Analyze selected date
    plan = analyze_future_date_plan(
        target_date=selected_date,
        weather_data=weather_data,
        crop=crop,
        stage_info=stage_info,
        lang=lang,
    )

    with col_info:
        plan_status = plan.get("status", "UNAVAILABLE")

        if plan_status == "FORECAST":
            lead_d = plan.get("lead_days", 0)
            lead_text = "Today" if lead_d == 0 else f"+{lead_d} days ahead"
            conf_tier = plan.get("confidence_tier", "Moderate")
            
            # Confidence badge styling
            if conf_tier == "High":
                conf_bg = "#dcfce7"
                conf_color = "#166534"
                conf_border = "#86efac"
            elif conf_tier == "Moderate":
                conf_bg = "#fef9c3"
                conf_color = "#854d0e"
                conf_border = "#fde047"
            else:
                conf_bg = "#e0f2fe"
                conf_color = "#075985"
                conf_border = "#7dd3fc"

            st.markdown(
                f"""
                <div style="background-color: #ffffff; border: 1px solid #c8ded0; border-radius: 12px; padding: 16px 18px; box-shadow: 0 2px 6px rgba(27,67,50,0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <div>
                            <strong style="color: #1b4332; font-size: 1.05rem;">{selected_date.strftime('%A, %d %B %Y')}</strong>
                            <span style="color: #557c66; font-size: 0.85rem; margin-left: 6px;">({lead_text})</span>
                        </div>
                        <span style="background-color: {conf_bg}; color: {conf_color}; border: 1px solid {conf_border}; font-size: 0.78rem; font-weight: 700; padding: 3px 10px; border-radius: 999px;">
                            {get_text('planning_confidence_label', lang)}: {conf_tier} • {plan.get('confidence_lead_label', '')}
                        </span>
                    </div>
                    <div style="font-size: 0.84rem; color: #406a52; margin-bottom: 12px;">
                        <em>{plan.get('confidence_desc', '')}</em>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 14px;">
                        <div style="background-color: #f8faf8; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #e2ebe5;">
                            <div style="font-size: 0.74rem; color: #628672; text-transform: uppercase;">Max Temp</div>
                            <div style="font-size: 1.15rem; font-weight: 700; color: #d90429;">{plan.get('temp_max', 0):.1f}°C</div>
                        </div>
                        <div style="background-color: #f8faf8; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #e2ebe5;">
                            <div style="font-size: 0.74rem; color: #628672; text-transform: uppercase;">Min Temp</div>
                            <div style="font-size: 1.15rem; font-weight: 700; color: #f77f00;">{plan.get('temp_min', 0):.1f}°C</div>
                        </div>
                        <div style="background-color: #f8faf8; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #e2ebe5;">
                            <div style="font-size: 0.74rem; color: #628672; text-transform: uppercase;">Rainfall</div>
                            <div style="font-size: 1.15rem; font-weight: 700; color: #1b4332;">{plan.get('precipitation', 0):.1f} mm</div>
                        </div>
                        <div style="background-color: #f8faf8; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #e2ebe5;">
                            <div style="font-size: 0.74rem; color: #628672; text-transform: uppercase;">Rain Chance</div>
                            <div style="font-size: 1.15rem; font-weight: 700; color: #2d6a4f;">{plan.get('precip_probability', 0):.0f}%</div>
                        </div>
                    </div>
                    <div style="background-color: #f4f8f5; border: 1px solid #c8ded0; border-radius: 8px; padding: 12px 14px; margin-bottom: 10px;">
                        <div style="font-weight: 600; color: #1b4332; font-size: 0.88rem; margin-bottom: 4px;">
                            💧 {get_text('planning_irrigation_guidance', lang)}
                        </div>
                        <div style="font-size: 0.86rem; color: #2d5a3f; line-height: 1.45;">
                            {plan.get('irrigation_advice', '')}
                        </div>
                    </div>
                    <div style="background-color: #f4f8f5; border: 1px solid #c8ded0; border-radius: 8px; padding: 12px 14px; margin-bottom: 10px;">
                        <div style="font-weight: 600; color: #1b4332; font-size: 0.88rem; margin-bottom: 4px;">
                            🛡️ {get_text('planning_spray_guidance', lang)}
                        </div>
                        <div style="font-size: 0.86rem; color: #2d5a3f; line-height: 1.45;">
                            {plan.get('spray_advice', '')}
                        </div>
                    </div>
                    <div style="font-size: 0.8rem; color: #628672; border-top: 1px dashed #d1e2d7; padding-top: 8px;">
                        🌾 <strong>{get_text('planning_crop_stage_label', lang)} ({crop}):</strong> {plan.get('stage_name', 'Active Development')} • 
                        <em>{plan.get('disclaimer_te' if lang == 'te' else 'disclaimer_en', '')}</em>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        elif plan_status == "BEYOND_FORECAST":
            st.markdown(
                f"""
                <div style="background-color: #fffbeb; border: 1px solid #fde68a; border-left: 5px solid #d97706; padding: 18px 20px; border-radius: 10px;">
                    <h5 style="color: #92400e; margin: 0 0 8px 0; font-size: 1.02rem;">{plan.get('title_te' if lang == 'te' else 'title_en')}</h5>
                    <p style="color: #78350f; font-size: 0.9rem; line-height: 1.5; margin: 0 0 12px 0;">
                        {plan.get('message_te' if lang == 'te' else 'message_en')}
                    </p>
                    <div style="background-color: #ffffff; border: 1px solid #fef3c7; border-radius: 6px; padding: 10px 12px; font-size: 0.82rem; color: #92400e; margin-bottom: 12px;">
                        <strong>Scientific Limitation:</strong> Numerical Weather Prediction (NWP) models lose deterministic skill beyond 14–16 days due to atmospheric chaos. Day-to-day weather beyond {plan.get('max_supported_date')} cannot be deterministically computed.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if navigate_to:
                st.button(
                    label=get_text("btn_open_simulator_for_date", lang),
                    key="btn_nav_sim_beyond_horizon",
                    type="primary",
                    on_click=navigate_to,
                    args=("SIMULATOR",),
                )

        elif plan_status == "HISTORICAL":
            hist_row = plan.get("row") or {}
            st.markdown(
                f"""
                <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; border-left: 5px solid #475569; padding: 18px 20px; border-radius: 10px;">
                    <h5 style="color: #1e293b; margin: 0 0 8px 0; font-size: 1.02rem;">{plan.get('title_te' if lang == 'te' else 'title_en')}</h5>
                    <p style="color: #334155; font-size: 0.9rem; line-height: 1.5; margin: 0 0 12px 0;">
                        {plan.get('message_te' if lang == 'te' else 'message_en')}
                    </p>
                    <div style="display: flex; gap: 14px; font-size: 0.88rem; color: #1e293b; background-color: #ffffff; padding: 10px 14px; border-radius: 6px; border: 1px solid #e2e8f0;">
                        <div>🌡️ <strong>Max:</strong> {hist_row.get('temp_max', 'N/A')}°C</div>
                        <div>❄️ <strong>Min:</strong> {hist_row.get('temp_min', 'N/A')}°C</div>
                        <div>🌧️ <strong>Rainfall:</strong> {hist_row.get('precipitation', 'N/A')} mm</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:  # UNAVAILABLE
            st.markdown(
                f"""
                <div style="background-color: #fdf2f2; border: 1px solid #f5c6cb; border-left: 5px solid #d90429; padding: 18px 20px; border-radius: 10px;">
                    <h5 style="color: #9b111e; margin: 0 0 8px 0; font-size: 1.02rem;">{plan.get('title_te' if lang == 'te' else 'title_en')}</h5>
                    <p style="color: #4a1515; font-size: 0.9rem; line-height: 1.5; margin: 0 0 12px 0;">
                        {plan.get('message_te' if lang == 'te' else 'message_en')}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.button(
                label=f"🔄 {get_text('btn_refresh_weather', lang)}",
                key="btn_retry_unavailable_plan",
                on_click=lambda: None,
            )

    st.markdown("<div style='margin-top: 26px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # 3. 16-DAY AGRICULTURAL FORECAST (Plotly Chart & Day Cards)
    # =========================================================================
    fc_len = len(forecast_df) if forecast_df is not None and not forecast_df.empty else 7
    st.markdown(f"#### 📅 {fc_len}-Day Agricultural Weather Forecast")
    st.caption(get_text("forecast_subheading", lang))

    # 16-day aggregate summary banner
    if forecast_metrics.get("is_valid", False):
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric(
                label=f"{fc_len}-Day Forecast Rain",
                value=f"{forecast_metrics['total_forecast_rain']:.1f} mm",
                help="Estimated cumulative precipitation expected across the forecast horizon",
            )
        with m2:
            st.metric(
                label="Forecast Rainy Days",
                value=f"{forecast_metrics['rainy_days_count']} days",
                help="Days with precipitation >= 2.5 mm",
            )
        with m3:
            st.metric(
                label="Longest Dry Run",
                value=f"{forecast_metrics['longest_forecast_dry_spell']} days",
                help="Maximum consecutive dry days (< 1.0 mm) in forecast period",
            )
        with m4:
            st.metric(
                label="Peak Single-Day Rain",
                value=f"{forecast_metrics['max_single_day_rain']:.1f} mm",
                help="Highest 24h rainfall volume in forecast",
            )

    if forecast_df is not None and not forecast_df.empty:
        # Polished modern Plotly Chart displaying full horizon
        fig_forecast = make_subplots(specs=[[{"secondary_y": True}]])
        date_labels = [d.strftime("%a, %d %b") for d in forecast_df["date"]]

        # 1. Rainfall bars
        fig_forecast.add_trace(
            go.Bar(
                x=date_labels,
                y=forecast_df["precipitation"],
                name="Rainfall (mm)" if lang == "en" else "వర్షపాతం (మి.మీ)",
                marker_color="#52b788",
                opacity=0.8,
                hovertemplate="%{x}<br>Rainfall: %{y:.1f} mm<extra></extra>",
            ),
            secondary_y=True,
        )

        # 2. Max temp line
        fig_forecast.add_trace(
            go.Scatter(
                x=date_labels,
                y=forecast_df["temp_max"],
                name="Max Temp (°C)" if lang == "en" else "గరిష్ట ఉష్ణోగ్రత (°C)",
                mode="lines+markers",
                line=dict(color="#d90429", width=2.5),
                marker=dict(size=6),
                hovertemplate="%{x}<br>Max Temp: %{y:.1f} °C<extra></extra>",
            ),
            secondary_y=False,
        )

        # 3. Min temp line
        fig_forecast.add_trace(
            go.Scatter(
                x=date_labels,
                y=forecast_df["temp_min"],
                name="Min Temp (°C)" if lang == "en" else "కనిష్ట ఉష్ణోగ్రత (°C)",
                mode="lines+markers",
                line=dict(color="#f77f00", width=2.2, dash="dot"),
                marker=dict(size=5),
                hovertemplate="%{x}<br>Min Temp: %{y:.1f} °C<extra></extra>",
            ),
            secondary_y=False,
        )

        # 35°C Heat Stress Threshold Reference Line
        fig_forecast.add_hline(
            y=35.0,
            line_dash="dash",
            line_color="#e63946",
            annotation_text="35°C Heat Alert Threshold" if lang == "en" else "35°C ఉష్ణోగ్రత హెచ్చరిక పరిమితి",
            annotation_position="bottom right",
            secondary_y=False,
        )

        fig_forecast.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(244,248,245,0.7)",
            margin=dict(l=30, r=30, t=25, b=30),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.05,
                xanchor="right",
                x=1,
                font=dict(size=12),
            ),
            hovermode="x unified",
            height=320,
        )
        fig_forecast.update_xaxes(showgrid=True, gridcolor="#e0ece4", tickangle=-20)
        fig_forecast.update_yaxes(
            title_text="Temperature (°C)" if lang == "en" else "ఉష్ణోగ్రత (°C)",
            secondary_y=False,
            showgrid=True,
            gridcolor="#e0ece4",
        )
        fig_forecast.update_yaxes(
            title_text="Rainfall (mm)" if lang == "en" else "వర్షం (మి.మీ)",
            secondary_y=True,
            showgrid=False,
            rangemode="tozero",
        )

        st.plotly_chart(fig_forecast, width="stretch")

        # Daily Forecast Card Grid (Days 1 to 7)
        first_7_df = forecast_df.head(7)
        st.markdown("**Days 1–7 (High to Moderate Model Confidence):**")
        f_cols = st.columns(len(first_7_df))
        for idx, row in first_7_df.reset_index().iterrows():
            with f_cols[idx]:
                day_name = row["date"].strftime("%a")
                day_date = row["date"].strftime("%d %b")
                max_t = row["temp_max"]
                min_t = row["temp_min"]
                prec = row["precipitation"]
                prob = row.get("precip_probability", 0)

                st.markdown(
                    f"""
                    <div style="background-color: #ffffff; border: 1px solid #e2ebe5; border-radius: 10px; padding: 12px 8px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.02);">
                        <div style="font-weight: 700; color: #1b4332; font-size: 0.88rem;">{day_name}</div>
                        <div style="color: #628672; font-size: 0.74rem; margin-bottom: 6px;">{day_date}</div>
                        <div style="color: #d90429; font-weight: 700; font-size: 0.94rem;">{max_t:.1f}°</div>
                        <div style="color: #f77f00; font-size: 0.82rem;">{min_t:.1f}°</div>
                        <div style="color: #2d6a4f; font-weight: 600; font-size: 0.8rem; margin-top: 6px;">💧 {prec:.1f}m</div>
                        <div style="color: #7b9987; font-size: 0.72rem;">{prob:.0f}% rain</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Extended Horizon Days 8–16 Expander
        if len(forecast_df) > 7:
            extended_df = forecast_df.iloc[7:]
            with st.expander(f"📊 {get_text('view_days_8_to_16_expander', lang)} ({len(extended_df)} additional days)", expanded=False):
                st.caption(
                    "⚠️ *Note: Forecasts beyond 7 days reflect indicative medium-range ensemble trends (50–65% confidence). "
                    "Atmospheric variability is higher; verify updates closer to operational dates.*"
                    if lang == "en"
                    else "⚠️ *గమనిక: 7 రోజుల కంటే ఎక్కువ కాలం అంచనాలు కేవలం సూచనాప్రాయమైనవి (50–65% విశ్వసనీయత). "
                    "సాగు పనుల అమలుకు ముందు తాజా సూచనలను సరిచూసుకోండి.*"
                )
                ext_cols = st.columns(len(extended_df))
                for idx, row in extended_df.reset_index().iterrows():
                    with ext_cols[idx]:
                        day_name = row["date"].strftime("%a")
                        day_date = row["date"].strftime("%d %b")
                        max_t = row["temp_max"]
                        min_t = row["temp_min"]
                        prec = row["precipitation"]
                        prob = row.get("precip_probability", 0)

                        st.markdown(
                            f"""
                            <div style="background-color: #fbfdfc; border: 1px solid #dbe7e0; border-radius: 8px; padding: 10px 6px; text-align: center;">
                                <div style="font-weight: 700; color: #2d5a3f; font-size: 0.82rem;">{day_name}</div>
                                <div style="color: #628672; font-size: 0.70rem; margin-bottom: 4px;">{day_date}</div>
                                <div style="color: #d90429; font-weight: 600; font-size: 0.88rem;">{max_t:.1f}°</div>
                                <div style="color: #f77f00; font-size: 0.78rem;">{min_t:.1f}°</div>
                                <div style="color: #2d6a4f; font-size: 0.76rem; margin-top: 4px;">💧 {prec:.1f}m</div>
                                <div style="color: #7b9987; font-size: 0.68rem;">{prob:.0f}%</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

    st.markdown("<div style='margin-top: 26px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # 4. RECENT 30-DAY RAINFALL & DRY SPELL INTELLIGENCE
    # =========================================================================
    st.markdown(f"#### 🌧️ {get_text('recent_rain_heading', lang)}")
    st.caption(get_text("recent_rain_subheading", lang))

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.metric(
            label=get_text("stat_current_dry_spell", lang),
            value=f"{dry_metrics['current_consecutive_dry_days']} {get_text('unit_days', lang)}",
            help="Consecutive days with daily precipitation < 1.0 mm up to yesterday",
        )
    with r2:
        st.metric(
            label=get_text("stat_total_30d_rain", lang),
            value=f"{dry_metrics['total_30d_rainfall']:.1f} mm",
            help="Estimated cumulative precipitation over the last 30 calendar days from meteorological reanalysis",
        )
    with r3:
        st.metric(
            label=get_text("stat_rainy_days", lang),
            value=f"{dry_metrics['rainy_days_count']} {get_text('unit_days', lang)}",
            help="Days receiving >= 2.5 mm estimated precipitation (IMD Standard rainy day definition)",
        )
    with r4:
        st.metric(
            label=get_text("stat_max_day_rain", lang),
            value=f"{dry_metrics['max_single_day_rain']:.1f} mm",
            help="Highest single-day precipitation estimated in the 30-day reanalysis window",
        )

    # 30-Day Precipitation Plotly Chart
    if historical_df is not None and not historical_df.empty:
        fig_hist = make_subplots(specs=[[{"secondary_y": True}]])
        hist_dates = [d.strftime("%d %b") for d in historical_df["date"]]

        # Daily rainfall bars
        fig_hist.add_trace(
            go.Bar(
                x=hist_dates,
                y=historical_df["precipitation"],
                name="Estimated Daily Rain (mm)" if lang == "en" else "అంచనా రోజువారీ వర్షం (మి.మీ)",
                marker_color="#2d6a4f",
                opacity=0.8,
                hovertemplate="%{x}<br>Daily Rain: %{y:.1f} mm<extra></extra>",
            ),
            secondary_y=False,
        )

        # Cumulative line
        fig_hist.add_trace(
            go.Scatter(
                x=hist_dates,
                y=historical_df["cumulative_precipitation"],
                name="Estimated Cumulative Rain (mm)" if lang == "en" else "అంచనా సంచిత వర్షం (మి.మీ)",
                mode="lines",
                line=dict(color="#1b4332", width=3),
                hovertemplate="%{x}<br>Cumulative: %{y:.1f} mm<extra></extra>",
            ),
            secondary_y=True,
        )

        # 1.0 mm Dry Threshold Reference Line
        fig_hist.add_hline(
            y=1.0,
            line_dash="dot",
            line_color="#e63946",
            annotation_text="Dry Day Threshold (1.0 mm)" if lang == "en" else "వర్షాభావ పరిమితి (1.0 మి.మీ)",
            annotation_position="top left",
            secondary_y=False,
        )

        fig_hist.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(244,248,245,0.7)",
            margin=dict(l=30, r=30, t=25, b=30),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.05,
                xanchor="right",
                x=1,
                font=dict(size=12),
            ),
            hovermode="x unified",
            height=300,
        )
        fig_hist.update_xaxes(showgrid=True, gridcolor="#e0ece4", tickangle=-20)
        fig_hist.update_yaxes(
            title_text="Estimated Daily Rain (mm)" if lang == "en" else "అంచనా రోజువారీ వర్షం (మి.మీ)",
            secondary_y=False,
            showgrid=True,
            gridcolor="#e0ece4",
        )
        fig_hist.update_yaxes(
            title_text="Estimated Cumulative Rain (mm)" if lang == "en" else "అంచనా సంచిత వర్షం (మి.మీ)",
            secondary_y=True,
            showgrid=False,
        )

        st.plotly_chart(fig_hist, width="stretch")

    # Reanalysis Notice Callout
    st.markdown(
        f"""
        <div style="background-color: #f4f8f5; border: 1px solid #c8ded0; padding: 12px 16px; border-radius: 8px; font-size: 0.86rem; color: #2d5a3f; margin-top: 8px;">
            {get_text('reanalysis_data_notice', lang)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-top: 26px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # 5. AGRICULTURAL CLIMATE INDICATORS
    # =========================================================================
    st.markdown(f"#### 📊 {get_text('indicators_heading', lang)}")
    st.caption(get_text("indicators_subheading", lang))

    indicators = evaluate_climate_indicators(
        forecast_df=forecast_df,
        historical_df=historical_df,
        farm_profile=farm_profile,
        current_temp=curr_temp,
        lang=lang,
    )

    ind_col1, ind_col2 = st.columns(2, gap="medium")
    for idx, ind in enumerate(indicators):
        target_col = ind_col1 if idx % 2 == 0 else ind_col2
        with target_col:
            risk = ind["risk_level"]
            if risk == "Alert":
                badge_bg = "#fde8e8"
                badge_color = "#9b111e"
                border_color = "#f5c6cb"
            elif risk == "Watch":
                badge_bg = "#fef3c7"
                badge_color = "#92400e"
                border_color = "#fde68a"
            elif risk in ["Low", "Normal"]:
                badge_bg = "#e8f5e9"
                badge_color = "#1b5e20"
                border_color = "#c8e6c9"
            else:
                badge_bg = "#f3f4f6"
                badge_color = "#374151"
                border_color = "#d1d5db"

            card_title = ind["name_te"] if lang == "te" else ind["name_en"]
            data_used = ind["data_used_te"] if lang == "te" else ind["data_used_en"]

            st.markdown(
                f"""
                <div style="background-color: #ffffff; border: 1px solid {border_color}; border-radius: 10px; padding: 16px 18px; margin-bottom: 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <h5 style="margin: 0; color: #1b4332; font-size: 0.98rem;">{card_title}</h5>
                        <span style="background-color: {badge_bg}; color: {badge_color}; font-size: 0.78rem; font-weight: 700; padding: 3px 10px; border-radius: 999px;">
                            {ind['risk_level_display']}
                        </span>
                    </div>
                    <p style="color: #22382c; font-size: 0.9rem; line-height: 1.45; margin: 0 0 10px 0;">{ind['explanation']}</p>
                    <div style="background-color: #f8faf8; border-radius: 6px; padding: 8px 10px; font-size: 0.78rem; color: #406a52;">
                        <strong>Data Used:</strong> {data_used}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-top: 26px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # 6. BOUNDARY EDUCATION: WEATHER FORECAST VS. WHAT-IF SIMULATOR
    # =========================================================================
    st.markdown(
        f"""
        <div style="background-color: #f4f8f5; border: 1px solid #c8ded0; border-radius: 12px; padding: 18px 22px; box-shadow: 0 2px 6px rgba(27,67,50,0.03);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h5 style="color: #1b4332; margin: 0 0 6px 0; font-size: 1.02rem;">
                        🔬 {get_text('weather_vs_simulator_title', lang)}
                    </h5>
                    <p style="color: #2d5a3f; font-size: 0.88rem; line-height: 1.55; margin: 0 0 10px 0;">
                        {get_text('weather_vs_simulator_desc', lang)}
                    </p>
                </div>
            </div>
            <div style="font-size: 0.82rem; color: #557c66;">
                <strong>Scientific Principles:</strong> NWP forecasts (1–16 days) use mathematical fluid dynamics initialized from physical observations. Seasonal scenarios (30, 60, 90 days) in the Simulator use transparent ICAR/ANGRAU physiological stress baselines to explore hypothetical rainfall deficits and thermal anomalies.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if navigate_to:
        c_sim_btn, _ = st.columns([1, 2])
        with c_sim_btn:
            st.button(
                label=f"🔮 {get_text('btn_go_to_simulator', lang) if get_text('btn_go_to_simulator', lang) != 'btn_go_to_simulator' else 'Open What-If Simulator'}",
                key="btn_open_simulator_from_weather",
                on_click=navigate_to,
                args=("SIMULATOR",),
            )

    # Attribution
    st.markdown(
        f"""
        <div style="margin-top: 32px; padding-top: 14px; border-top: 1px solid #e2ebe5; font-size: 0.8rem; color: #628672; text-align: center;">
            {get_text('attribution_text', lang)}
        </div>
        """,
        unsafe_allow_html=True,
    )
