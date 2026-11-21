"""El Niño Resilience Co-Pilot: Smart Farm Digital Twin & Agricultural Advisor.

A commercial-grade agricultural decision-support mobile/laptop application
for farmers in Andhra Pradesh and Telangana.

Sections:
1. HOME: Welcome, current plot overview, today's weather glance, active alerts, personalized advice.
2. MY FARM: Farm profile management and live Digital Twin visualization.
3. WEATHER: Current atmospheric telemetry, 7-day forecast, 30-day rainfall, climate indicators.
4. AI FARM ADVISOR: Bilingual AI conversational advisor with suggested prompts and real-time grounding.
5. CROP GUIDANCE: Authoritative package of practices and resilience measures for Turmeric, Banana, Paddy.
"""

from typing import Dict, Any
import streamlit as st

from src.localization import get_text
from src.components.advisor_view import render_advisor_view
from src.components.home_view import render_home_view
from src.components.farm_view import render_farm_view, initialize_farm_state
from src.components.weather_view import render_weather_view
from src.components.crop_guidance_view import render_crop_guidance_view
from src.components.simulator_view import render_simulator_view
from src.components.enso_view import render_enso_view

# =============================================================================
# 1. PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="RythuMithra NLP: Multilingual Conversational Voice Assistant for El Niño Resilience",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# 2. PREMIUM AGRICULTURAL DESIGN SYSTEM (Custom CSS)
# =============================================================================
st.markdown(
    """
    <style>
    /* Global Typography & Font Family */
    html, body, .stApp, [data-testid="stAppViewContainer"], .main {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans Telugu", "Gautami", "Kohinoor Telugu", sans-serif;
        color: #24332B !important;
        background-color: #F7F9F6 !important;
        line-height: 1.55;
    }

    p, span, label, div[data-testid="stMarkdownContainer"] p {
        color: #24332B;
    }

    /* Container Spacing for Clean Laptop View */
    .block-container,
    [data-testid="stMainBlockContainer"],
    [data-testid="block-container"] {
        padding-top: 1.8rem !important;
        padding-bottom: 7.5rem !important;
        max-width: 1120px !important;
    }

    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* Modern Headers */
    h1:not(.hero-title), h2:not(.hero-title), h3:not(.hero-title), h4:not(.hero-title), h5:not(.hero-title), h6:not(.hero-title) {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans Telugu", sans-serif;
        color: #1B4332 !important;
        font-weight: 700;
        letter-spacing: -0.3px;
    }

    /* Hero Banner White Title Overrides for Maximum Accessibility & Contrast */
    h1.hero-title, h2.hero-title, h3.hero-title, .hero-title, [data-hero-title="true"], .hero-banner h1, .hero-banner h2,
    h1.hero-title *, h2.hero-title *, h3.hero-title *, .hero-title *, [data-hero-title="true"] *, .hero-banner h1 *, .hero-banner h2 * {
        color: #FFFFFF !important;
    }

    /* Clean Card Styling */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2EBE5 !important;
        padding: 18px 20px !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(27, 67, 50, 0.04) !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: #406A52 !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #1B4332 !important;
        font-size: 1.65rem !important;
        font-weight: 700 !important;
    }

    /* Primary and Secondary Buttons */
    button[kind="primary"] {
        background-color: #2D6A4F !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.15rem !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 6px rgba(45, 106, 79, 0.2) !important;
        transition: all 0.15s ease-in-out !important;
    }
    button[kind="primary"]:hover {
        background-color: #1B4332 !important;
        transform: translateY(-1px);
    }
    button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #2D6A4F !important;
        border: 1px solid #C8DED0 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.15s ease-in-out !important;
    }
    button[kind="secondary"]:hover {
        background-color: #F4F8F5 !important;
        border-color: #2D6A4F !important;
    }

    /* Buttons with proper wrapping so labels are never truncated */
    div[data-testid="stButton"] button {
        white-space: normal !important;
        word-wrap: break-word !important;
        height: auto !important;
        min-height: 44px !important;
        text-align: left !important;
        line-height: 1.45 !important;
        font-size: 0.88rem !important;
    }

    /* Sidebar Navigation Menu Styling */
    section[data-testid="stSidebar"] {
        background-color: #F8FAF8 !important;
        border-right: 1px solid #E2EBE5 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #244B36 !important;
    }

    /* Styled Radio Navigation in Sidebar */
    div[data-testid="stSidebar"] div[role="radiogroup"] > label {
        padding: 8px 12px !important;
        border-radius: 8px !important;
        margin-bottom: 4px !important;
        transition: background-color 0.15s ease-in-out !important;
    }
    div[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: #E8F3EC !important;
    }

    /* Chat Messages Base Styling */
    div[data-testid="stChatMessage"] {
        padding: 16px 20px !important;
        margin-bottom: 14px !important;
    }

    /* High-contrast text rules inside chat messages to prevent dark-mode inheritance */
    div[data-testid="stChatMessage"] p,
    div[data-testid="stChatMessage"] span,
    div[data-testid="stChatMessage"] div,
    div[data-testid="stChatMessage"] li,
    div[data-testid="stChatMessage"] td,
    div[data-testid="stChatMessage"] th,
    div[data-testid="stChatMessage"] em {
        color: #24332B !important;
        line-height: 1.65 !important;
    }

    div[data-testid="stChatMessage"] strong,
    div[data-testid="stChatMessage"] b {
        color: #1B4332 !important;
        font-weight: 700 !important;
    }

    div[data-testid="stChatMessage"] h1,
    div[data-testid="stChatMessage"] h2,
    div[data-testid="stChatMessage"] h3,
    div[data-testid="stChatMessage"] h4 {
        color: #1B4332 !important;
        font-weight: 700 !important;
        margin-top: 0.6rem !important;
        margin-bottom: 0.35rem !important;
    }

    div[data-testid="stChatMessage"] code {
        color: #1B4332 !important;
        background-color: #EAF3ED !important;
        border: 1px solid #C8DFD2 !important;
        border-radius: 5px !important;
        padding: 2px 6px !important;
        font-size: 0.88em !important;
        font-weight: 600 !important;
    }

    /* User Chat Bubble: Right-aligned, subtle sage-green background */
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]),
    div[data-testid="stChatMessage"]:has([aria-label*="user"]),
    div[data-testid="stChatMessage"]:has([aria-label*="User"]) {
        background-color: #E8F5E9 !important;
        border: 1px solid #C8E6C9 !important;
        border-radius: 18px 18px 4px 18px !important;
        margin-left: auto !important;
        margin-right: 0 !important;
        max-width: 82% !important;
        flex-direction: row-reverse !important;
        box-shadow: 0 1px 4px rgba(27, 67, 50, 0.04) !important;
    }

    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"],
    div[data-testid="stChatMessage"]:has([aria-label*="user"]) [data-testid="stChatMessageContent"] {
        text-align: right !important;
    }

    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p,
    div[data-testid="stChatMessage"]:has([aria-label*="user"]) p {
        color: #1B4332 !important;
        font-size: 0.96rem !important;
        font-weight: 550 !important;
        line-height: 1.6 !important;
    }

    /* Assistant Chat Card: Left-aligned white card with subtle green border */
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]),
    div[data-testid="stChatMessage"]:has([aria-label*="assistant"]),
    div[data-testid="stChatMessage"]:has([aria-label*="Assistant"]) {
        background-color: #FFFFFF !important;
        border: 1px solid #E2EBE5 !important;
        border-radius: 18px 18px 18px 4px !important;
        margin-right: auto !important;
        margin-left: 0 !important;
        max-width: 95% !important;
        box-shadow: 0 2px 10px rgba(27, 67, 50, 0.04) !important;
    }

    /* Avatars */
    [data-testid="stChatMessageAvatarUser"] {
        background-color: #2D6A4F !important;
        color: #FFFFFF !important;
        border-radius: 50% !important;
    }
    [data-testid="stChatMessageAvatarAssistant"] {
        background-color: #52B788 !important;
        color: #FFFFFF !important;
        border-radius: 50% !important;
    }

    /* Fixed Bottom Container for Chat Input */
    div[data-testid="stBottom"],
    div[data-testid="stBottomBlockContainer"] {
        background-color: #F7F9F6 !important;
        background: #F7F9F6 !important;
    }

    /* Chat Input / Composer */
    div[data-testid="stChatInput"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #52B788 !important;
        border-radius: 14px !important;
        box-shadow: 0 2px 12px rgba(27, 67, 50, 0.08) !important;
        padding: 3px 6px !important;
    }

    div[data-testid="stChatInput"]:focus-within {
        border-color: #2D6A4F !important;
        box-shadow: 0 0 0 3px rgba(82, 183, 136, 0.25) !important;
    }

    div[data-testid="stChatInputTextArea"] textarea,
    div[data-testid="stChatInput"] textarea {
        color: #1B4332 !important;
        font-size: 0.95rem !important;
        line-height: 1.55 !important;
        background-color: #FFFFFF !important;
        font-family: inherit !important;
    }

    div[data-testid="stChatInputTextArea"] textarea::placeholder,
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #527964 !important;
        opacity: 0.95 !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
    }

    div[data-testid="stChatInputSubmitButton"] button {
        color: #2D6A4F !important;
        background: transparent !important;
    }

    div[data-testid="stChatInputSubmitButton"] button:hover {
        color: #1B4332 !important;
        background: #E8F5E9 !important;
    }

    /* Expander Styling */
    details {
        border-color: #DBE8E0 !important;
        border-radius: 10px !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    }
    details[open] {
        border-color: #C2DCD0 !important;
    }
    summary {
        color: #1B4332 !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        cursor: pointer !important;
    }
    details > div {
        color: #24332B !important;
    }

    /* Forms */
    div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# 3. INITIALIZE STATE & DATA
# =============================================================================
initialize_farm_state()

# Navigation Definitions
NAV_CONFIG = {
    "HOME": {"en": "🏡 Home", "te": "🏡 హోమ్"},
    "MY FARM": {"en": "🌱 My Farm", "te": "🌱 నా పొలం"},
    "WEATHER": {"en": "🌦️ Weather", "te": "🌦️ వాతావరణం"},
    "AI FARM ADVISOR": {"en": "🤖 AI Farm Advisor", "te": "🤖 ఏఐ సలహాదారు"},
    "CROP GUIDANCE": {"en": "📖 Crop Guidance", "te": "📖 పంట సాగు సూచనలు"},
    "SIMULATOR": {"en": "🔮 What-If Simulator", "te": "🔮 వాట్-ఇఫ్ సిమ్యులేటర్"},
    "ENSO": {"en": "🌊 ENSO Outlook", "te": "🌊 ఎల్ నినో సమాచారం"},
}
NAV_KEYS = list(NAV_CONFIG.keys())

if "active_nav" not in st.session_state or st.session_state["active_nav"] not in NAV_KEYS:
    st.session_state["active_nav"] = "HOME"

# Check for pending navigation request (e.g. from quick action buttons or query params)
if "tab" in st.query_params:
    qp_val = str(st.query_params.get("tab", "")).strip().lower()
    for k in NAV_KEYS:
        if qp_val in k.lower() or (qp_val in ["advisor", "chatbot", "chat", "ai"] and "ADVISOR" in k):
            st.session_state.active_nav = k
            break

if "nav_radio_select" not in st.session_state or st.session_state["nav_radio_select"] not in NAV_KEYS:
    st.session_state["nav_radio_select"] = st.session_state["active_nav"]

if "top_screen_nav_pills" not in st.session_state or st.session_state["top_screen_nav_pills"] not in NAV_KEYS:
    st.session_state["top_screen_nav_pills"] = st.session_state["active_nav"]

# Navigation helper for Home quick shortcuts and cross-screen buttons
def navigate_to_section(section_name: str) -> None:
    """Safely switch the active navigation view."""
    sec_clean = str(section_name).strip().upper()
    mapping = {
        "HOME": "HOME",
        "MY FARM": "MY FARM",
        "FARM": "MY FARM",
        "WEATHER": "WEATHER",
        "AI FARM ADVISOR": "AI FARM ADVISOR",
        "ADVISOR": "AI FARM ADVISOR",
        "AI ADVISOR": "AI FARM ADVISOR",
        "CROP GUIDANCE": "CROP GUIDANCE",
        "GUIDE": "CROP GUIDANCE",
        "SIMULATOR": "SIMULATOR",
        "WHAT-IF SIMULATOR": "SIMULATOR",
        "WHAT-IF": "SIMULATOR",
        "SIMULATE": "SIMULATOR",
        "ENSO": "ENSO",
        "ENSO INFORMATION": "ENSO",
        "EL NINO": "ENSO",
        "EL NIÑO": "ENSO",
        "ENSO OUTLOOK": "ENSO",
    }
    target = mapping.get(sec_clean, "HOME")
    st.session_state["active_nav"] = target
    for key in ["nav_radio_select", "top_screen_nav_pills"]:
        try:
            st.session_state[key] = target
        except Exception:
            pass


# =============================================================================
# 4. SIDEBAR CONFIGURATION (Clean Commercial App Sidebar)
# =============================================================================
with st.sidebar:
    # 1. App Title & Branding
    st.markdown(
        """
        <div style="padding: 6px 0 16px 0; border-bottom: 1px solid #e2ebe5; margin-bottom: 16px;">
            <div style="font-size: 1.25rem; font-weight: 800; color: #1b4332; display: flex; align-items: center; gap: 8px; line-height: 1.25;">
                🌾 RythuMithra NLP
            </div>
            <div style="font-size: 0.80rem; color: #2D6A4F; font-weight: 700; margin-top: 4px; line-height: 1.35;">
                Multilingual Conversational Voice Assistant for El Niño Resilience • రైతు మిత్ర
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Language Switcher (Prominently placed at top of sidebar)
    lang_choice = st.radio(
        label="Language / భాష",
        options=["English", "తెలుగు (Telugu)"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )
    lang = "te" if "తెలుగు" in lang_choice else "en"

    # 3. Active Farm Plot Badge
    farm_profile = st.session_state.farm_profile
    d_district = farm_profile.get("district", "Kadapa (YSR Kadapa)").split("(")[0].strip()
    d_village = farm_profile.get("village", "").strip()
    d_crop = farm_profile.get("crop", "Turmeric")
    d_area = float(farm_profile.get("land_area", 4.0))
    d_loc = f"{d_village}, {d_district}" if d_village else d_district

    st.markdown(
        f"""
        <div style="background-color: #ffffff; border: 1px solid #d8e6dc; border-radius: 10px; padding: 12px 14px; margin: 12px 0 18px 0; box-shadow: 0 1px 4px rgba(27,67,50,0.03);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span style="font-size: 0.72rem; font-weight: 700; color: #557c66; text-transform: uppercase;">
                    {'Active Farm' if lang == 'en' else 'ప్రస్తుత పొలం'}
                </span>
                <span style="background-color: #e8f5e9; color: #1b5e20; font-size: 0.7rem; font-weight: 700; padding: 2px 7px; border-radius: 999px;">
                    Synced
                </span>
            </div>
            <div style="font-size: 0.95rem; font-weight: 700; color: #1b4332;">📍 {d_loc}</div>
            <div style="font-size: 0.82rem; color: #2d5a3f; margin-top: 2px;">🌿 {d_crop} • {d_area:.2f} Ac</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4. Five Main Navigation Sections
    st.markdown(f"**{'Navigation' if lang == 'en' else 'విభాగాలు'}**")

    def on_sidebar_nav_change():
        sel = st.session_state.get("nav_radio_select")
        if sel:
            st.session_state["active_nav"] = sel
            st.session_state["top_screen_nav_pills"] = sel

    st.radio(
        label="Navigation Menu",
        options=NAV_KEYS,
        format_func=lambda k: NAV_CONFIG[k][lang],
        label_visibility="collapsed",
        key="nav_radio_select",
        on_change=on_sidebar_nav_change,
    )

    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

    # 5. Discreet Footer Attribution
    st.markdown(
        f"""
        <div style="border-top: 1px solid #e2ebe5; padding-top: 14px; font-size: 0.75rem; color: #6b8f7a; line-height: 1.4;">
            <div><strong>Weather Data:</strong> Open-Meteo API (CC BY 4.0)</div>
            <div style="margin-top: 4px;"><strong>Guidance:</strong> ICAR, ANGRAU, IMD</div>
            <div style="margin-top: 6px; color: #88a895;"><em>Decision-support advisory for smallholder farmers.</em></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# 5. MAIN APPLICATION CONTENT ROUTING (The 5 Screens)
# =============================================================================
# Prominent Top Navigation Bar (Always visible even if sidebar is collapsed)
def on_top_nav_change():
    sel = st.session_state.get("top_screen_nav_pills")
    if sel:
        st.session_state["active_nav"] = sel
        st.session_state["nav_radio_select"] = sel
    else:
        # Farmer clicked the already active pill -> keep it active
        st.session_state["top_screen_nav_pills"] = st.session_state.get("active_nav", "HOME")

st.pills(
    "Navigation Menu",
    NAV_KEYS,
    format_func=lambda k: NAV_CONFIG[k][lang],
    key="top_screen_nav_pills",
    label_visibility="collapsed",
    on_change=on_top_nav_change,
)

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

active_screen = st.session_state.get("active_nav", "HOME")

if active_screen == "HOME":
    render_home_view(
        farm_profile=st.session_state.farm_profile,
        lang=lang,
        navigate_to=navigate_to_section,
    )

elif active_screen == "MY FARM":
    render_farm_view(lang=lang)

elif active_screen == "WEATHER":
    render_weather_view(
        farm_profile=st.session_state.farm_profile,
        lang=lang,
        navigate_to=navigate_to_section,
    )

elif active_screen == "AI FARM ADVISOR":
    render_advisor_view(
        farm_profile=st.session_state.farm_profile,
        lang=lang,
    )

elif active_screen == "CROP GUIDANCE":
    render_crop_guidance_view(
        farm_profile=st.session_state.farm_profile,
        lang=lang,
    )

elif active_screen == "SIMULATOR":
    render_simulator_view(
        farm_profile=st.session_state.farm_profile,
        lang=lang,
        navigate_to=navigate_to_section,
    )

elif active_screen == "ENSO":
    render_enso_view(lang=lang)
