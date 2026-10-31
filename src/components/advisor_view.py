"""AI Farm Advisor Screen Component: Modern Bilingual Agricultural Assistant.

Allows farmers to ask questions in Telugu, English, or code-mixed phrasing about:
- Current atmospheric telemetry and 7-day rainfall forecasts.
- Observed dry spells and historical precipitation.
- Thermal suitability and water stress risks.
- Stage-specific crop precautions and resilience measures.

No internal agent terminology or technical development jargon displayed to farmers.
"""

from typing import Dict, Any, List
import streamlit as st

from src.localization import get_text
from src.agents.controller import process_farmer_query


def initialize_chat_history() -> None:
    """Ensure chat conversation history exists in session state."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "is_processing_advisor" not in st.session_state:
        st.session_state.is_processing_advisor = False


def render_advisor_view(farm_profile: Dict[str, Any], lang: str = "en") -> None:
    """Render the AI Farm Advisor chat screen.
    
    Args:
        farm_profile: Active digital twin dictionary from session state.
        lang: Active language toggle ('en' or 'te').
    """
    initialize_chat_history()

    crop = farm_profile.get("crop", "Turmeric")
    district = farm_profile.get("district", "Kadapa (YSR Kadapa)")
    village = farm_profile.get("village", "").strip()
    loc_str = f"{village}, {district}" if village else district

    crop_te_map = {"Turmeric": "పసుపు", "Banana": "అరటి", "Paddy": "వరి"}
    crop_te = crop_te_map.get(crop, crop)

    # 1. Header Card with Active Farm Context and Clear Action
    st.markdown(
        f"""
        <div style="background-color: #FFFFFF; border: 1px solid #E2EBE5; border-radius: 14px; padding: 18px 22px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(27,67,50,0.03);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
                <div>
                    <div style="font-size: 1.35rem; font-weight: 800; color: #1B4332; display: flex; align-items: center; gap: 8px;">
                        🤖 {get_text('advisor_tab_title', lang)}
                    </div>
                    <div style="font-size: 0.85rem; color: #527964; margin-top: 4px; font-weight: 500;">
                        📍 {loc_str} • 🌿 {crop_te if lang == 'te' else crop} • {get_text('advisor_tab_subtitle', lang)}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Clear chat button row (discreet right alignment with ample room for full label)
    clear_row_col1, clear_row_col2 = st.columns([3, 2])
    with clear_row_col2:
        clear_label = "🗑️ " + get_text("btn_clear_chat", lang)
        if st.button(clear_label, key="btn_clear_chat_hist", width="stretch", help=get_text("btn_clear_chat", lang)):
            st.session_state.chat_history = []
            st.rerun()

    # 2. Suggested Questions (2-Tier Layout: 4 Primary in 2x2 Grid + Secondary in Expander)
    st.markdown(f"**💡 {get_text('quick_questions_title', lang)}:**")

    if lang == "te":
        primary_chips = [
            "ప్రస్తుతం ఉష్ణోగ్రత ఎంత?",
            "వచ్చే 7 రోజుల్లో వర్షం పడుతుందా?",
            "ఎన్ని వర్షాభావ రోజులు గడిచాయి?",
            f"నా {crop_te} పంటకు వాతావరణం అనుకూలంగా ఉందా?",
        ]
        secondary_chips = [
            f"నా {crop_te} పంటకు ఎలాంటి జాగ్రత్తలు తీసుకోవాలి?",
            f"నా {crop_te} పంటకు నీటి కొరత ప్రమాదం ఉందా?",
            "నా పొలం వివరాలు చెప్పండి",
        ]
    else:
        primary_chips = [
            "What is the current temperature in my area?",
            "Will it rain in the next 7 days?",
            "How many dry days have occurred?",
            f"Is the weather suitable for my {crop.lower()} crop?",
        ]
        secondary_chips = [
            f"What precautions should I take for my {crop.lower()} crop?",
            f"Is my {crop.lower()} crop at risk of water shortage?",
            "Tell me about my farm.",
        ]

    selected_chip = None

    # Tier 1: 4 Primary Suggestions in clean 2-column layout (wide buttons, full text, never truncated)
    r1_col1, r1_col2 = st.columns(2)
    with r1_col1:
        if st.button(f"💬 {primary_chips[0]}", key="chip_pri_0", width="stretch"):
            selected_chip = primary_chips[0]
    with r1_col2:
        if st.button(f"💬 {primary_chips[1]}", key="chip_pri_1", width="stretch"):
            selected_chip = primary_chips[1]

    r2_col1, r2_col2 = st.columns(2)
    with r2_col1:
        if st.button(f"💬 {primary_chips[2]}", key="chip_pri_2", width="stretch"):
            selected_chip = primary_chips[2]
    with r2_col2:
        if st.button(f"💬 {primary_chips[3]}", key="chip_pri_3", width="stretch"):
            selected_chip = primary_chips[3]

    # Tier 2: Remaining suggestions in a clean expander
    with st.expander(f"➕ {get_text('more_suggestions', lang)}", expanded=False):
        sec_cols = st.columns(len(secondary_chips))
        for s_idx, sec_chip in enumerate(secondary_chips):
            with sec_cols[s_idx]:
                if st.button(f"💬 {sec_chip}", key=f"chip_sec_{s_idx}", width="stretch"):
                    selected_chip = sec_chip

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

    # 3. Chat Messages Container
    chat_box = st.container()
    with chat_box:
        if not st.session_state.chat_history:
            # Welcoming prompt card
            welcome_head = "నమస్కారం! నేను మీ వ్యక్తిగత ఏఐ వ్యవసాయ సలహాదారుని" if lang == "te" else "Welcome to your AI Farm Advisory Desk"
            welcome_msg = (
                f"మీ పొలం ({loc_str}, {crop_te}) మరియు ప్రత్యక్ష వాతావరణ వివరాల ఆధారంగా మీకు సలహాలు అందించగలను. "
                f"పైన ఉన్న ప్రశ్నలపై క్లిక్ చేయండి లేదా క్రింది సందేశ బాక్స్‌లో మీ ప్రశ్నను అడగండి."
                if lang == "te"
                else f"I continuously synchronize real-time weather observations from Open-Meteo with your active farm plot attributes ({loc_str}, {crop}) "
                f"to provide timely agronomic guidance. Tap any suggested question above or type your question in English or Telugu below."
            )
            st.markdown(
                f"""
                <div style="background-color: #FFFFFF; border: 1.5px solid #D8EADB; border-radius: 14px; padding: 22px 24px; box-shadow: 0 2px 8px rgba(27,67,50,0.03); margin-bottom: 20px;">
                    <div style="font-size: 1.05rem; font-weight: 700; color: #1B4332; margin-bottom: 8px;">
                        🌾 {welcome_head}
                    </div>
                    <div style="color: #24332B; font-size: 0.94rem; line-height: 1.65;">
                        {welcome_msg}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        for msg in st.session_state.chat_history:
            role = msg["role"]
            content = msg["content"]
            meta = msg.get("metadata", {})

            if role == "user":
                with st.chat_message("user"):
                    st.markdown(content)
            else:
                with st.chat_message("assistant"):
                    st.markdown(content)
                    grounding = meta.get("grounding_data")
                    refs = meta.get("references")
                    if grounding or refs:
                        with st.expander(f"🔍 {get_text('grounding_details_title', lang)}", expanded=False):
                            if grounding:
                                st.markdown(
                                    "**వాస్తవ వాతావరణ & పొలం వివరాలు (Grounding Data):**"
                                    if lang == "te"
                                    else "**Real-Time Telemetry & Plot Parameters (Grounding Data):**"
                                )
                                st.json(grounding)
                            if refs:
                                st.markdown(
                                    "**ప్రామాణిక వ్యవసాయ ఆధారాలు (Institutional Citations):**"
                                    if lang == "te"
                                    else "**Institutional Agronomic Citations:**"
                                )
                                for r in refs:
                                    st.markdown(f"- **{r['authority']}**: [{r['document']}]({r['url']})")

    # 4. Chat Input Box (Fixed Bottom Composer)
    user_input = st.chat_input(placeholder=get_text("chat_input_placeholder", lang))
    active_query = user_input or selected_chip

    if active_query and not st.session_state.is_processing_advisor:
        st.session_state.is_processing_advisor = True

        # Append user message
        st.session_state.chat_history.append({"role": "user", "content": active_query})

        # Process with controller inside friendly loading spinner
        with st.spinner(get_text("advisor_analyzing", lang)):
            result = process_farmer_query(
                query=active_query,
                farm_profile=farm_profile,
                active_ui_lang=lang,
            )

        # Append assistant response
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["response_text"],
            "metadata": {
                "intent": result["intent"],
                "detected_language": result["detected_language"],
                "grounding_data": result.get("grounding_data", {}),
                "references": result.get("references", []),
            },
        })

        st.session_state.is_processing_advisor = False
        st.rerun()
