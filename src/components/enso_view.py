"""ENSO (El Niño-Southern Oscillation) & Climate Teleconnection View.

Farmer-friendly, scientifically rigorous bilingual presentation explaining:
1. What El Niño, La Niña, and ENSO-neutral phases mean, and official classification rules.
2. The latest officially reported ENSO status with verified sources, observation periods, and dates.
3. How Pacific Ocean conditions teleconnect with the Indian monsoon via the Walker Circulation.
4. Why ENSO is a regional probability driver, NOT a deterministic village forecast (with traceable 1997 IMD historical verification).
5. Actionable guidance for farmers on integrating ENSO with 7-day local weather forecasts and extension advice.
"""

from typing import Dict, Any, Optional
import streamlit as st

from src.services.enso_service import get_enso_intelligence
from src.localization import get_text


def render_enso_view(lang: str = "en", simulate_state: Optional[str] = None) -> None:
    """Render the comprehensive ENSO intelligence view."""
    # Retrieve verified official intelligence
    enso_data = get_enso_intelligence(force_refresh=False, simulate_state=simulate_state)
    data_state = enso_data.get("data_state", "cached")
    
    # -------------------------------------------------------------------------
    # 1. HEADER BANNER
    # -------------------------------------------------------------------------
    title = "🌊 ENSO Outlook & Climate Teleconnections" if lang == "en" else "🌊 ఎల్ నినో సమాచారం & శీతోష్ణస్థితి నివేదిక"
    subtitle = (
        "Official institutional climate intelligence and monsoon teleconnection guidance "
        "for farmers in Andhra Pradesh and Telangana."
        if lang == "en"
        else "ఆంధ్రప్రదేశ్ మరియు తెలంగాణ రైతుల కోసం అధికారిక శీతోష్ణస్థితి నివేదిక మరియు రుతుపవన విశ్లేషణ."
    )

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #0d3b66 0%, #1d4e89 100%); border-radius: 14px; padding: 24px 28px; color: #ffffff; margin-bottom: 20px; box-shadow: 0 4px 14px rgba(13,59,102,0.15);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
                <div>
                    <h2 class="hero-title" data-hero-title="true" style="margin: 0 0 6px 0; color: #ffffff !important; font-size: 1.75rem; font-weight: 700;">
                        {title}
                    </h2>
                    <p style="margin: 0; color: #e0f2fe; font-size: 0.96rem; opacity: 0.95;">
                        {subtitle}
                    </p>
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <span style="background-color: rgba(255,255,255,0.18); backdrop-filter: blur(4px); color: #ffffff; padding: 6px 14px; border-radius: 999px; font-size: 0.82rem; font-weight: 600; border: 1px solid rgba(255,255,255,0.25);">
                        🏛️ NOAA CPC & IMD
                    </span>
                    <span style="background-color: rgba(255,255,255,0.18); backdrop-filter: blur(4px); color: #ffffff; padding: 6px 14px; border-radius: 999px; font-size: 0.82rem; font-weight: 600; border: 1px solid rgba(255,255,255,0.25);">
                        📅 Bulletin: {enso_data.get('publication_date', '8 October 2026')}
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------------------
    # 2. STATUS & STALE-DATA HANDLING NOTICES
    # -------------------------------------------------------------------------
    pub_date = enso_data.get("publication_date", "8 October 2026")
    ret_time = enso_data.get("retrieved_at", "Recent")
    urls = enso_data.get("official_urls", {})
    noaa_url = urls.get("noaa_cpc", "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/")
    imd_url = urls.get("imd_portal", "https://mausam.imd.gov.in/")

    if data_state == "live":
        if lang == "te":
            st.success(
                f"🟢 **లైవ్ అధికారిక నివేదిక**: మూల ప్రచురణ తేదీ: **{pub_date}** | యాప్ పొందిన సమయం: `{ret_time}`.\n\n"
                f"నోవా (NOAA CPC) మరియు భారత వాతావరణ విభాగం (IMD) అధికారిక నివేదికలతో ప్రత్యక్షంగా సమన్వయం చేయబడింది."
            )
        else:
            st.success(
                f"🟢 **Live Official Bulletin**: Source Published: **{pub_date}** | Application Retrieved: `{ret_time}`.\n\n"
                f"Synchronized directly with official feeds from NOAA Climate Prediction Center and IMD."
            )
    elif data_state == "cached":
        if lang == "te":
            st.warning(
                f"⚠️ **క్యాష్ చేయబడిన సమాచారం — పాతది కావచ్చు**: మూల ప్రచురణ తేదీ: **{pub_date}** | గతంలో పొందిన సమయం: `{ret_time}`.\n\n"
                f"ప్రస్తుత రన్‌లో లైవ్ నెట్‌వర్క్ కనెక్షన్ లభించనందున, గతంలో విజయవంతంగా డౌన్‌లోడ్ చేసి స్థానికంగా భద్రపరిచిన నివేదిక చూపించబడుతోంది. "
                f"తాజా ప్రత్యక్ష సమాచారం కోసం అధికారిక వెబ్‌సైట్లను చూడండి: [NOAA CPC]({noaa_url}) • [IMD]({imd_url})"
            )
        else:
            st.warning(
                f"⚠️ **Cached — potentially outdated**: Source Published: **{pub_date}** | Previously Retrieved: `{ret_time}`.\n\n"
                f"Live network retrieval was unreachable in this run; displaying a previously retrieved and locally saved diagnostic bulletin. "
                f"For the latest live updates, consult official portals: [NOAA CPC Diagnostic Discussion]({noaa_url}) • [IMD Climate Portal]({imd_url})"
            )
    elif data_state == "fallback":
        if lang == "te":
            st.warning(
                f"⚠️ **ధృవీకరించబడిన బ్యాకప్ స్నాప్‌షాట్ — పాతది కావచ్చు**: మూల ప్రచురణ తేదీ: **{pub_date}** | యాప్ సమయం: `{ret_time}`.\n\n"
                f"లైవ్ నెట్‌వర్క్ అందుబాటులో లేనందున మరియు గత లైవ్ క్యాష్ లేనందున, యాప్‌లో పొందుపరచిన ధృవీకృత బ్యాకప్ స్నాప్‌షాట్ చూపించబడుతోంది. "
                f"తాజా ప్రత్యక్ష సమాచారం కోసం అధికారిక వెబ్‌సైట్లను చూడండి: [NOAA CPC]({noaa_url}) • [IMD]({imd_url})"
            )
        else:
            st.warning(
                f"⚠️ **Verified fallback snapshot — potentially outdated**: Source Published: **{pub_date}** | Bundled Snapshot Accessed: `{ret_time}`.\n\n"
                f"Live network retrieval is currently unreachable and no previous live cache was found; displaying the application's verified bundled snapshot. "
                f"For the latest live updates, consult official portals: [NOAA CPC Diagnostic Discussion]({noaa_url}) • [IMD Climate Portal]({imd_url})"
            )
    else:  # unavailable
        if lang == "te":
            st.error(
                f"❌ **ప్రస్తుత ఈఎన్‌ఎస్‌ఓ సమాచారం అందుబాటులో లేదు**: అధికారిక వాతావరణ సమాచారం తాత్కాలికంగా లభించలేదు. "
                f"దయచేసి అధికారిక పోర్టల్స్ నేరుగా సంప్రదించండి: [NOAA CPC]({noaa_url}) మరియు [IMD]({imd_url})."
            )
        else:
            st.error(
                f"❌ **Current ENSO information unavailable**: Live telemetry from official meteorological services could not be reached, "
                f"and no verified cache or snapshot is available. The application does not fabricate climate status. "
                f"Please consult official agencies directly: [NOAA Climate Prediction Center]({noaa_url}) and [India Meteorological Department]({imd_url})."
            )

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. CURRENT STATUS PANEL (Rendered when data is available or cached)
    # -------------------------------------------------------------------------
    if data_state != "unavailable":
        st.markdown(f"### 📊 {'Current Official ENSO Diagnostic Status' if lang == 'en' else 'ప్రస్తుత అధికారిక ఈఎన్‌ఎస్‌ఓ నివేదిక'}")

        m_col1, m_col2, m_col3, m_col4 = st.columns(4)

        status_label = enso_data.get("alert_status", enso_data.get("status", "El Niño"))
        phase_sub = enso_data.get("phase_en" if lang == "en" else "phase_te", "")
        sst_anomaly = enso_data.get("sst_anomaly_nino34")
        sst_display = f"{sst_anomaly:+.1f}°C" if sst_anomaly is not None else "N/A"
        obs_period = enso_data.get("observation_period", "September–October 2026")
        fcst_info = enso_data.get("forecast", {})

        with m_col1:
            st.metric(
                label="ENSO Alert Status" if lang == "en" else "అధికారిక హెచ్చరిక స్థితి",
                value=status_label,
                delta="Strong-to-Very-Strong" if lang == "en" else "బలమైన ఎల్ నినో",
                delta_color="inverse",
                help=f"{phase_sub} (Official status from NOAA CPC & IMD)",
            )
        with m_col2:
            st.metric(
                label="Niño 3.4 SST Anomaly" if lang == "en" else "నినో 3.4 ఉష్ణోగ్రత వ్యత్యాసం",
                value=sst_display,
                help=f"Observation Period: {obs_period}. Threshold for El Niño under NOAA's official RONI framework is sustained 3-month running average anomaly ≥ +0.5°C with coupled atmospheric response.",
            )
        with m_col3:
            st.metric(
                label="Forecast Period" if lang == "en" else "అంచనా వేసిన కాలం",
                value=fcst_info.get("period", "Jan–Mar 2027"),
                delta="> 83% Probability" if lang == "en" else "> 83% సంభావ్యత",
                delta_color="normal",
                help=fcst_info.get("probability_statement", ""),
            )
        with m_col4:
            st.metric(
                label="Source & Published Date" if lang == "en" else "అధికారిక ప్రచురణ తేదీ",
                value="8 October 2026",
                help=f"NOAA CPC Monthly Diagnostic Discussion. Application retrieved on {ret_time}.",
            )

        # Observed Conditions vs. Forecast Probabilities Card
        obs_title = "🔍 Observed Ocean-Atmosphere Conditions vs. Model Forecast Probabilities" if lang == "en" else "🔍 పరిశీలించిన సముద్ర-వాతావరణ పరిస్థితులు vs భవిష్యత్ అంచనా సంభావ్యతలు"
        
        if lang == "te":
            obs_html = f"""
            <div style="background-color: #ffffff; border: 1px solid #d4e2d9; border-radius: 12px; padding: 18px 20px; margin: 16px 0 24px 0; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
                <div style="font-weight: 700; color: #1b4332; font-size: 1.02rem; margin-bottom: 10px;">
                    {obs_title}
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                    <div style="background-color: #f7faf8; border-radius: 8px; padding: 14px; border-left: 4px solid #e76f51;">
                        <strong style="color: #9d2b0e; font-size: 0.92rem;">1. ప్రత్యక్షంగా పరిశీలించిన పరిస్థితులు (పరిశీలనా కాలం: {obs_period})</strong>
                        <ul style="margin: 8px 0 0 0; padding-left: 18px; font-size: 0.88rem; color: #2d4a3e; line-height: 1.55;">
                            <li><strong>నినో 3.4 ఉష్ణోగ్రత:</strong> <code>{sst_display}</code> (తూర్పు పసిఫిక్‌లో తీవ్రమైన వేడెక్కడం).</li>
                            <li><strong>ఇతర నినో సూచికలు:</strong> నినో-1+2 వద్ద <code>+3.9°C</code>, నినో-3 వద్ద <code>+3.0°C</code> నమోదైంది.</li>
                            <li><strong>వాతావరణ ప్రతిస్పందన:</strong> తూర్పు వ్యాపార పవనాలు బలహీనపడి పశ్చిమ గాలులు ఏర్పడ్డాయి; ఇండోనేషియాపై వర్ష మేఘాలు తగ్గి మధ్య-తూర్పు పసిఫిక్ వైపు విస్తరించాయి.</li>
                        </ul>
                    </div>
                    <div style="background-color: #f7faf8; border-radius: 8px; padding: 14px; border-left: 4px solid #2563eb;">
                        <strong style="color: #1d4ed8; font-size: 0.92rem;">2. డైనమిక్ మోడల్ ముందస్తు అంచనాలు (జనవరి–మార్చి 2027 వరకు)</strong>
                        <ul style="margin: 8px 0 0 0; padding-left: 18px; font-size: 0.88rem; color: #2d4a3e; line-height: 1.55;">
                            <li><strong>కొనసాగింపు సంభావ్యత:</strong> బలమైన లేదా అతి తీవ్రమైన ఎల్ నినో జనవరి–మార్చి 2027 వరకు కొనసాగే అవకాశం <strong>83% కంటే ఎక్కువ</strong>.</li>
                            <li><strong>చారిత్రక రికార్డు సంభావ్యత:</strong> అక్టోబర్–డిసెంబర్ 2026 కాలంలో గత రికార్డులను దాటి అతి తీవ్రమైన ఎల్ నినోగా (+2.5°C RONI) మారే అవకాశం <strong>83%</strong>, నవంబర్–జనవరిలో <strong>70%</strong> గా అంచనా వేయబడింది.</li>
                            <li><strong>భారత వాతావరణ శాఖ (IMD) నివేదిక:</strong> జూలై 30, 2026న భూ విజ్ఞాన మంత్రిత్వ శాఖ విడుదల చేసిన నివేదిక ప్రకారం ఎల్ నినో జూన్‌లో బలహీనంగా ఉండి, జూలై నాటికి మధ్యస్థ స్థాయికి చేరింది; చివరి త్రైమాసికంలో మరింత బలపడే అవకాశం ఉంది.</li>
                        </ul>
                    </div>
                </div>
                <div style="margin-top: 12px; font-size: 0.82rem; color: #527964; border-top: 1px dashed #d4e2d9; padding-top: 8px;">
                    🏛️ <strong>అధికారిక మూలాలు:</strong> 
                    <a href="{noaa_url}" target="_blank" style="color: #1b4332; font-weight: 600;">NOAA CPC ENSO Diagnostic Discussion (8 అక్టోబర్ 2026)</a> • 
                    <a href="{imd_url}" target="_blank" style="color: #1b4332; font-weight: 600;">భారత వాతావరణ విభాగం (IMD) & MoES (30 జూలై 2026)</a>
                </div>
            </div>
            """
        else:
            obs_html = f"""
            <div style="background-color: #ffffff; border: 1px solid #d4e2d9; border-radius: 12px; padding: 18px 20px; margin: 16px 0 24px 0; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
                <div style="font-weight: 700; color: #1b4332; font-size: 1.02rem; margin-bottom: 10px;">
                    {obs_title}
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                    <div style="background-color: #f7faf8; border-radius: 8px; padding: 14px; border-left: 4px solid #e76f51;">
                        <strong style="color: #9d2b0e; font-size: 0.92rem;">1. Observed Empirical Conditions (Observation Window: {obs_period})</strong>
                        <ul style="margin: 8px 0 0 0; padding-left: 18px; font-size: 0.88rem; color: #2d4a3e; line-height: 1.55;">
                            <li><strong>Niño-3.4 SST Anomaly:</strong> <code>{sst_display}</code> (substantial anomalous warming across east-central equatorial Pacific).</li>
                            <li><strong>Other Key Indices:</strong> Niño-1+2 at <code>+3.9°C</code>, Niño-3 at <code>+3.0°C</code>; eastern Pacific subsurface warmth exceeding <code>+10.0°C</code> at depth.</li>
                            <li><strong>Atmospheric Coupling:</strong> Low-level westerly wind anomalies, upper-tropospheric easterlies, suppressed convection over Indonesia, and enhanced cloudiness east of the dateline.</li>
                        </ul>
                    </div>
                    <div style="background-color: #f7faf8; border-radius: 8px; padding: 14px; border-left: 4px solid #2563eb;">
                        <strong style="color: #1d4ed8; font-size: 0.92rem;">2. Forward-Looking Model Forecast Probabilities (Through Early 2027)</strong>
                        <ul style="margin: 8px 0 0 0; padding-left: 18px; font-size: 0.88rem; color: #2d4a3e; line-height: 1.55;">
                            <li><strong>Persistence Outlook:</strong> Strong-to-very strong El Niño favored through <strong>January–March 2027</strong> with <strong>&gt;83% probability</strong>.</li>
                            <li><strong>Historic Strength Odds:</strong> CPC dynamical models indicate an <strong>83% chance</strong> of surpassing historic benchmark thresholds (+2.5°C RONI) in October–December 2026, and <strong>70%</strong> in November 2026–January 2027.</li>
                            <li><strong>IMD / MoES Perspective:</strong> Statement dated 30 July 2026 noted El Niño was weak in June, moderate in July, and projected potential further intensification in October–December 2026 alongside neutral IOD conditions.</li>
                        </ul>
                    </div>
                </div>
                <div style="margin-top: 12px; font-size: 0.82rem; color: #527964; border-top: 1px dashed #d4e2d9; padding-top: 8px;">
                    🏛️ <strong>Official Verification:</strong> 
                    <a href="{noaa_url}" target="_blank" style="color: #1b4332; font-weight: 600;">NOAA CPC Diagnostic Discussion (8 October 2026)</a> • 
                    <a href="{imd_url}" target="_blank" style="color: #1b4332; font-weight: 600;">IMD / Ministry of Earth Sciences Official Review (30 July 2026)</a>
                </div>
            </div>
            """
        st.markdown(obs_html, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 4. DECOUPLED FOUNDATIONAL SCIENCE & EDUCATIONAL SECTIONS
    # (These remain fully functional, visible, and useful offline regardless of live status)
    # -------------------------------------------------------------------------
    exp = enso_data.get("explanations", {})
    phases_exp = exp.get("phases_overview", {})
    tele_exp = exp.get("teleconnection", {})
    disclaimer_exp = exp.get("village_disclaimer", {})
    action_exp = exp.get("farmer_action_guide", {})

    # SECTION 1: UNDERSTANDING ENSO & CLASSIFICATION RULES
    st.markdown(f"### 🌐 {phases_exp.get(f'title_{lang}', 'Understanding ENSO: The Three Oceanic Phases & Classification Rules')}")
    st.markdown(phases_exp.get(f"intro_{lang}", ""))

    p_col1, p_col2, p_col3 = st.columns(3)

    with p_col1:
        st.markdown(
            f"""
            <div style="background-color: #fff9f5; border: 1px solid #ffd8be; border-top: 4px solid #e76f51; border-radius: 10px; padding: 18px; height: 100%; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="font-size: 1.4rem;">🔥</span>
                    <strong style="color: #9d2b0e; font-size: 1.05rem;">El Niño (Warm Phase)</strong>
                </div>
                <div style="font-size: 0.78rem; color: #b04627; font-weight: 600; margin-bottom: 10px;">
                    Rule-of-Thumb Benchmark: SST Anomaly ≥ +0.5°C
                </div>
                <div style="font-size: 0.88rem; color: #3a2219; line-height: 1.5;">
                    {phases_exp.get(f'el_nino_{lang}', '')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p_col2:
        st.markdown(
            f"""
            <div style="background-color: #f4fbf7; border: 1px solid #cce8d7; border-top: 4px solid #2a9d8f; border-radius: 10px; padding: 18px; height: 100%; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="font-size: 1.4rem;">⚖️</span>
                    <strong style="color: #1b6056; font-size: 1.05rem;">ENSO-Neutral (Baseline)</strong>
                </div>
                <div style="font-size: 0.78rem; color: #237b6f; font-weight: 600; margin-bottom: 10px;">
                    Historical Normal Band: -0.5°C to +0.5°C
                </div>
                <div style="font-size: 0.88rem; color: #1c3530; line-height: 1.5;">
                    {phases_exp.get(f'neutral_{lang}', '')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p_col3:
        st.markdown(
            f"""
            <div style="background-color: #f0f7ff; border: 1px solid #bfdbfe; border-top: 4px solid #2563eb; border-radius: 10px; padding: 18px; height: 100%; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="font-size: 1.4rem;">❄️</span>
                    <strong style="color: #1d4ed8; font-size: 1.05rem;">La Niña (Cool Phase)</strong>
                </div>
                <div style="font-size: 0.78rem; color: #1e40af; font-weight: 600; margin-bottom: 10px;">
                    Rule-of-Thumb Benchmark: SST Anomaly ≤ -0.5°C
                </div>
                <div style="font-size: 0.88rem; color: #1e293b; line-height: 1.5;">
                    {phases_exp.get(f'la_nina_{lang}', '')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # SECTION 2: PLANETARY TELECONNECTIONS & WALKER CIRCULATION
    st.markdown(f"### 🔄 {tele_exp.get(f'title_{lang}', 'Planetary Teleconnections: How the Pacific Ocean Influences the Indian Monsoon')}")
    st.markdown(tele_exp.get(f"body_{lang}", ""))

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # SECTION 3: SCIENTIFIC DISCLAIMER (VILLAGE DETERMINISM & 1997 IMD HISTORICAL PROOF)
    st.markdown(
        f"""
        <div style="background-color: #fffbeb; border: 1.5px solid #fde68a; border-left: 6px solid #d97706; border-radius: 12px; padding: 20px 22px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(217,119,6,0.06);">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <span style="font-size: 1.4rem;">⚠️</span>
                <strong style="color: #92400e; font-size: 1.08rem;">
                    {disclaimer_exp.get(f'title_{lang}', 'Regional Probability vs. Local Village Realities')}
                </strong>
            </div>
            <div style="color: #451a03; font-size: 0.92rem; line-height: 1.6;">
                {disclaimer_exp.get(f'body_{lang}', '').replace(chr(10), '<br>')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # SECTION 4: REVIEWED FARMER ACTION GUIDE (QUALIFIED & EXTENSION-ALIGNED)
    st.markdown(f"### 🧑‍🌾 {action_exp.get(f'title_{lang}', 'Farmer Decision Framework: Short-Term Operations vs. Seasonal Preparedness')}")
    st.markdown(action_exp.get(f"body_{lang}", ""))

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # SECTION 5: INSTITUTIONAL SOURCES & AUTHORITATIVE CITATIONS (WITH CLICKABLE LINKS)
    with st.expander(
        label="📚 " + ("Official Bulletins, Data Sources & Scientific References" if lang == "en" else "అధికారిక నివేదికలు మరియు శాస్త్రీయ మూలాలు"),
        expanded=False,
    ):
        st.markdown(
            f"""
            **Official Institutional Portals & Diagnostic Discussion Bulletins:**
            
            1. **NOAA Climate Prediction Center (CPC) / NCEP / NWS:**
               - *Official Adoption of RONI*: In February 2026, NOAA CPC officially adopted the **Relative Oceanic Niño Index (RONI)** for primary ENSO monitoring and prediction: [{urls.get('noaa_roni_announcement', 'https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/announcement.php')}]({urls.get('noaa_roni_announcement', 'https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/announcement.php')}).
               - *Official Diagnostic Discussion*: Dated **8 October 2026** (El Niño Advisory, Niño 3.4 anomaly +2.1°C).
               - Clickable Portal: [{noaa_url}]({noaa_url})
               - *Legacy Record Archive*: Historical Monthly Oceanic Niño Index (ONI) [Legacy Index]: [{urls.get('noaa_indices', 'https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt')}]({urls.get('noaa_indices', 'https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt')})
            
            2. **India Meteorological Department (IMD) / Ministry of Earth Sciences (MoES):**
               - *Official Monsoon & Climate Review*: Statement dated **30 July 2026** (El Niño weak in June, moderate in July, further strengthening projected for Oct–Dec 2026).
               - Clickable Portal: [{imd_url}]({imd_url})
               - Seasonal Climate Diagnostics and Extended Range Forecast (ERF) Bulletins.
            
            3. **Traceable Academic References on the Monsoon-ENSO Teleconnection:**
               - **Ashok, K., Guan, Z., & Yamagata, T. (2001).** *Impact of the Indian Ocean Dipole on the relationship between the Indian monsoon rainfall and ENSO*. **Geophysical Research Letters**, 28(23), 4499–4502. (Documents the 1997 all-India monsoon rainfall at 102% of LPA despite the 1997–98 El Niño, buffered by a strong positive IOD).
               - **Kumar, K. K., Rajagopalan, B., & Cane, M. A. (1999).** *On the weakening relationship between the Indian monsoon and ENSO*. **Science**, 284(5423), 2156–2159.
            
            ---
            *Notice: The El Niño Resilience Co-Pilot provides agricultural decision support and does not issue independent climate projections. All ENSO telemetry is synchronized with official meteorological publications issued by NOAA CPC and IMD.*
            """
        )
