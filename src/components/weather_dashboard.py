"""Regional Climate Intelligence Dashboard Component.

Renders current atmospheric telemetry, 7-day agricultural forecasts,
recent 30-day precipitation & dry spell analytics, and rule-based
agricultural climate indicators in English and Telugu using Open-Meteo.
"""

from typing import Dict, Any
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.localization import get_text
from src.weather.location_service import get_district_coordinates
from src.weather.weather_api import get_weather_intelligence, get_weather_description
from src.weather.weather_analysis import (
    compute_dry_spell_metrics,
    evaluate_climate_indicators,
    get_crop_climate_context,
)


def render_weather_dashboard(farm_profile: Dict[str, Any], lang: str = "en") -> None:
    """Render the complete Regional Climate Intelligence dashboard.
    
    Args:
        farm_profile: Active farmer profile dictionary from session state.
        lang: Selected language code ('en' or 'te').
    """
    state = farm_profile.get("state", "Andhra Pradesh")
    district = farm_profile.get("district", "Kurnool")
    village = farm_profile.get("village", "").strip()

    # 1. Resolve Geographic Coordinates
    loc_info = get_district_coordinates(state=state, district=district, village=village)
    lat = loc_info["latitude"]
    lon = loc_info["longitude"]

    # Header & Refresh Row
    st.markdown(f"### {get_text('weather_section_title', lang)}")
    st.caption(get_text("weather_section_subtitle", lang))

    col_meta1, col_meta2 = st.columns([3, 1])
    with col_meta1:
        if village:
            location_display = f"**{village}**, {district}, {state}"
            rep_text = (
                f"ℹ️ {get_text('location_rep_notice', lang).format(district=district, lat=lat, lon=lon)}"
            )
        else:
            location_display = f"**{district}**, {state}"
            rep_text = f"📍 Coordinates: `{lat:.4f}°N, {lon:.4f}°E`"

        st.markdown(f"📍 **Target Location:** {location_display}")
        st.caption(rep_text)

    with col_meta2:
        refresh_clicked = st.button(
            label=f"🔄 {get_text('btn_refresh_weather', lang)}",
            key="btn_refresh_wx_dashboard",
            width="stretch",
        )

    # 2. Fetch Live Weather Data from Open-Meteo
    weather_data = get_weather_intelligence(
        latitude=lat,
        longitude=lon,
        force_refresh=refresh_clicked,
    )

    # 3. Handle API Failure State
    if not weather_data.get("success", False):
        err_msg = weather_data.get("error", "Network failure")
        diag_msg = weather_data.get("diagnostic", "Verify internet connectivity and DNS resolution.")
        st.markdown(
            f"""
            <div style="background-color: #fdf2f2; border: 1px solid #f5c6cb; border-left: 5px solid #d90429; padding: 18px 20px; border-radius: 8px; margin: 16px 0;">
                <h4 style="color: #9b111e; margin: 0 0 8px 0; font-size: 1.1rem;">⚠️ {get_text('api_error_title', lang)}</h4>
                <p style="color: #4a1515; margin: 0 0 10px 0; font-size: 0.95rem; line-height: 1.5;">{get_text('api_error_desc', lang)}</p>
                <div style="background-color: #ffffff; border: 1px solid #fed7d7; border-radius: 6px; padding: 10px 14px; font-size: 0.85rem; color: #742a2a; line-height: 1.5;">
                    <div><strong>Error:</strong> {err_msg}</div>
                    <div style="margin-top: 4px;"><strong>Diagnostic:</strong> {diag_msg}</div>
                    <div style="margin-top: 4px; color: #a12b2b;"><em>Notice: Unvalidated or fake simulated weather data is never substituted.</em></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Extract Data Elements
    current = weather_data.get("current", {})
    forecast_df = weather_data.get("forecast_df")
    historical_df = weather_data.get("historical_df")
    retrieved_at = weather_data.get("retrieved_at", "Just now")
    dry_metrics = compute_dry_spell_metrics(historical_df)

    st.markdown(
        f"<small style='color: #406a52;'><strong>{get_text('weather_retrieved_at', lang)}:</strong> {retrieved_at} • "
        f"<strong>Source:</strong> Open-Meteo Meteorological Model (Asia/Kolkata)</small>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # SECTION 1: CURRENT ATMOSPHERIC CONDITIONS
    # =========================================================================
    st.markdown(f"#### {get_text('current_conditions_heading', lang)}")
    curr_temp = current.get("temperature")
    curr_rh = current.get("relative_humidity")
    curr_wind = current.get("wind_speed")
    curr_precip = current.get("precipitation", 0.0)
    weather_code = current.get("weather_code")
    weather_desc = get_weather_description(weather_code, lang=lang)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            label=get_text("curr_temperature", lang),
            value=f"{curr_temp:.1f} °C" if curr_temp is not None else "N/A",
            help="Dry-bulb air temperature at 2 meters above ground",
        )
    with c2:
        st.metric(
            label=get_text("curr_humidity", lang),
            value=f"{curr_rh:.0f} %" if curr_rh is not None else "N/A",
            help="Relative air moisture content",
        )
    with c3:
        st.metric(
            label=get_text("curr_wind_speed", lang),
            value=f"{curr_wind:.1f} km/h" if curr_wind is not None else "N/A",
            help="Wind velocity at 10 meters height",
        )
    with c4:
        st.metric(
            label=get_text("curr_precipitation", lang),
            value=f"{curr_precip:.1f} mm",
            help=f"{get_text('curr_condition', lang)}: {weather_desc}",
        )

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # SECTION 2: SEVEN-DAY AGRICULTURAL FORECAST (Plotly Chart & Summary)
    # =========================================================================
    st.markdown(f"#### {get_text('forecast_heading', lang)}")
    st.caption(get_text("forecast_subheading", lang))

    if not forecast_df.empty:
        # Create dual-axis interactive Plotly chart
        fig_forecast = make_subplots(specs=[[{"secondary_y": True}]])

        date_labels = [d.strftime("%a, %d %b") for d in forecast_df["date"]]

        # 1. Daily Rainfall Bar Chart (Secondary Y-axis)
        fig_forecast.add_trace(
            go.Bar(
                x=date_labels,
                y=forecast_df["precipitation"],
                name="Rainfall (mm)" if lang == "en" else "వర్షపాతం (మి.మీ)",
                marker_color="#52b788",
                opacity=0.75,
                hovertemplate="%{x}<br>Rainfall: %{y:.1f} mm<extra></extra>",
            ),
            secondary_y=True,
        )

        # 2. Maximum Temperature Curve (Primary Y-axis)
        fig_forecast.add_trace(
            go.Scatter(
                x=date_labels,
                y=forecast_df["temp_max"],
                name="Max Temp (°C)" if lang == "en" else "గరిష్ట ఉష్ణోగ్రత (°C)",
                mode="lines+markers",
                line=dict(color="#d90429", width=2.5),
                marker=dict(size=7),
                hovertemplate="%{x}<br>Max Temp: %{y:.1f} °C<extra></extra>",
            ),
            secondary_y=False,
        )

        # 3. Minimum Temperature Curve (Primary Y-axis)
        fig_forecast.add_trace(
            go.Scatter(
                x=date_labels,
                y=forecast_df["temp_min"],
                name="Min Temp (°C)" if lang == "en" else "కనిష్ట ఉష్ణోగ్రత (°C)",
                mode="lines+markers",
                line=dict(color="#f77f00", width=2.5, dash="dot"),
                marker=dict(size=6),
                hovertemplate="%{x}<br>Min Temp: %{y:.1f} °C<extra></extra>",
            ),
            secondary_y=False,
        )

        fig_forecast.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(244,248,245,0.6)",
            margin=dict(l=40, r=40, t=30, b=40),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.05,
                xanchor="right",
                x=1,
                font=dict(size=12),
            ),
            hovermode="x unified",
            height=340,
        )

        fig_forecast.update_xaxes(
            showgrid=True,
            gridcolor="#e0ece4",
            tickangle=-15,
        )
        fig_forecast.update_yaxes(
            title_text="Temperature (°C)" if lang == "en" else "ఉష్ణోగ్రత (°C)",
            secondary_y=False,
            showgrid=True,
            gridcolor="#e0ece4",
        )
        fig_forecast.update_yaxes(
            title_text="Precipitation (mm)" if lang == "en" else "వర్షం (మి.మీ)",
            secondary_y=True,
            showgrid=False,
            rangemode="tozero",
        )

        st.plotly_chart(fig_forecast, width="stretch")

        # Forecast Daily Table Summary
        with st.expander(
            "📋 View Daily Forecast Data Table" if lang == "en" else "📋 రోజువారీ వాతావరణ పట్టిక",
            expanded=False,
        ):
            table_rows = []
            for _, row in forecast_df.iterrows():
                table_rows.append({
                    "Date": row["date"].strftime("%d %b %Y"),
                    "Max Temp (°C)": f"{row['temp_max']:.1f}",
                    "Min Temp (°C)": f"{row['temp_min']:.1f}",
                    "Rainfall (mm)": f"{row['precipitation']:.1f}",
                    "Rain Probability (%)": f"{row['precip_probability']:.0f}%",
                    "Sky Condition": get_weather_description(row["weather_code"], lang=lang),
                })
            st.dataframe(pd.DataFrame(table_rows), width="stretch", hide_index=True)

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # SECTION 3: RECENT 30-DAY RAINFALL & DRY SPELL INTELLIGENCE
    # =========================================================================
    st.markdown(f"#### {get_text('recent_rain_heading', lang)}")
    st.caption(get_text("recent_rain_subheading", lang))

    # Metric Row for Dry Spell & Cumulative Rain
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.metric(
            label=get_text("stat_current_dry_spell", lang),
            value=f"{dry_metrics['current_consecutive_dry_days']} {get_text('unit_days', lang)}",
            help="Consecutive days with daily precipitation < 1.0 mm (standard meteorological dry day) up to yesterday",
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
    if not historical_df.empty:
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
            annotation_text="Dry Threshold (1.0 mm)" if lang == "en" else "వర్షాభావ పరిమితి (1.0 మి.మీ)",
            annotation_position="top left",
            secondary_y=False,
        )

        fig_hist.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(244,248,245,0.6)",
            margin=dict(l=40, r=40, t=30, b=40),
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
        fig_hist.update_xaxes(
            showgrid=True,
            gridcolor="#e0ece4",
            tickangle=-25,
        )
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

    # Reanalysis Data Source Callout
    st.markdown(
        f"""
        <div style="background-color: #f4f8f5; border: 1px solid #c8ded0; padding: 12px 16px; border-radius: 6px; font-size: 0.88rem; color: #2d5a3f; margin-top: 8px;">
            {get_text('reanalysis_data_notice', lang)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # SECTION 4: AGRICULTURAL CLIMATE INDICATORS (Rule-Based Synthesis)
    # =========================================================================
    st.markdown(f"#### {get_text('indicators_heading', lang)}")
    st.caption(get_text("indicators_subheading", lang))

    indicators = evaluate_climate_indicators(
        forecast_df=forecast_df,
        historical_df=historical_df,
        farm_profile=farm_profile,
        current_temp=current.get("temperature"),
        lang=lang,
    )

    # Render in 2 columns of 2 cards
    ind_col1, ind_col2 = st.columns(2, gap="medium")
    for idx, ind in enumerate(indicators):
        target_col = ind_col1 if idx % 2 == 0 else ind_col2
        with target_col:
            risk = ind["risk_level"]
            # Color code badge
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
            else:  # Insufficient Data
                badge_bg = "#f3f4f6"
                badge_color = "#374151"
                border_color = "#d1d5db"

            card_title = ind["name_te"] if lang == "te" else ind["name_en"]
            data_used = ind["data_used_te"] if lang == "te" else ind["data_used_en"]
            method_text = ind["method_te"] if lang == "te" else ind["method_en"]

            st.markdown(
                f"""
                <div style="background-color: #ffffff; border: 1px solid {border_color}; border-radius: 8px; padding: 16px; margin-bottom: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <h5 style="margin: 0; color: #1b4332; font-size: 1.02rem;">{card_title}</h5>
                        <span style="background-color: {badge_bg}; color: {badge_color}; font-size: 0.78rem; font-weight: 700; padding: 3px 8px; border-radius: 999px;">
                            {ind['risk_level_display']}
                        </span>
                    </div>
                    <p style="color: #22382c; font-size: 0.92rem; line-height: 1.45; margin: 0 0 10px 0;">{ind['explanation']}</p>
                    <div style="background-color: #f8faf8; border-radius: 4px; padding: 8px 10px; font-size: 0.8rem; color: #406a52; line-height: 1.4;">
                        <div><strong>Data:</strong> {data_used}</div>
                        <div><strong>Method:</strong> {method_text}</div>
                        <div style="margin-top: 3px; font-style: italic; color: #6b8f79;">* {get_text('experimental_badge', lang)}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # SECTION 5: CROP-SPECIFIC CLIMATE VULNERABILITY CONTEXT
    # =========================================================================
    selected_crop = farm_profile.get("crop", "Turmeric")
    crop_context = get_crop_climate_context(crop=selected_crop, lang=lang)

    st.markdown(f"#### {get_text('crop_context_heading', lang)}")
    st.caption(get_text("crop_context_subheading", lang))

    with st.container(border=True):
        st.markdown(f"##### {crop_context['title']}")
        ctx1, ctx2 = st.columns(2, gap="large")
        with ctx1:
            st.markdown(f"**🌡️ Temperature Sensitivity:**")
            st.markdown(crop_context["temperature_importance"])
            st.markdown(f"**💧 Moisture & Rainfall Demand:**")
            st.markdown(crop_context["water_importance"])
        with ctx2:
            st.markdown(f"**🛡️ Agronomic Resilience Measures:**")
            st.markdown(crop_context["resilience_tips"])
            st.markdown(
                "<small style='color: #557c66;'><em>* Notice: Agronomic context represents established crop physiology principles for educational decision-support. Exact crop yields and volumetric irrigation rates require localized agronomic calibration.</em></small>",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # SECTION 6: OPEN-METEO ATTRIBUTION & LICENSING
    # =========================================================================
    st.markdown(
        f"""
        <div style="border-top: 1px solid #d8e5dc; padding-top: 14px; font-size: 0.82rem; color: #4e735e; text-align: center;">
            {get_text('attribution_text', lang)}
        </div>
        """,
        unsafe_allow_html=True,
    )
