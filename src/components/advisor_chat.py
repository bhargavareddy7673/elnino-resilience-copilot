"""AI Farm Advisor Chat Component.

Interactive bilingual conversational interface allowing farmers to ask questions
in Telugu and English about real-time weather, 7-day agricultural forecasts,
crop-specific precautions, water stress, and farm digital twin attributes.
"""

from typing import Dict, Any, List
import streamlit as st

from src.localization import get_text
from src.agents.controller import process_farmer_query


def init_chat_session_state() -> None:
    """Initialize chat conversation history in Streamlit session state if missing."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def render_advisor_chat(farm_profile: Dict[str, Any], lang: str = "en") -> None:
    """Render the AI Farm Advisor chat interface.
    
    Args:
        farm_profile: Active digital twin dictionary from session state.
        lang: Active language toggle ('en' or 'te').
    """
    init_chat_session_state()

    crop = farm_profile.get("crop", "Turmeric")
    district = farm_profile.get("district", "Kadapa (YSR Kadapa)")

    # Title & Agent Status Bar
    st.markdown(f"### {get_text('advisor_tab_title', lang)}")
    st.caption(get_text("advisor_tab_subtitle", lang))

    # Specialist Subagent Pills
    col_pill, col_clear = st.columns([4, 1])
    with col_pill:
        st.markdown(
            """
            <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;">
                <span style="background-color: #e8f5e9; color: #1b4332; border: 1px solid #c8e6c9; padding: 4px 10px; border-radius: 999px; font-size: 0.8rem; font-weight: 600;">
                    🌤️ Weather Agent
                </span>
                <span style="background-color: #e8f5e9; color: #1b4332; border: 1px solid #c8e6c9; padding: 4px 10px; border-radius: 999px; font-size: 0.8rem; font-weight: 600;">
                    🌱 Crop Agronomist
                </span>
                <span style="background-color: #e8f5e9; color: #1b4332; border: 1px solid #c8e6c9; padding: 4px 10px; border-radius: 999px; font-size: 0.8rem; font-weight: 600;">
                    📊 Climate Risk Analyst
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_clear:
        if st.button("🗑️ " + get_text("btn_clear_chat", lang), key="btn_clear_chat_hist", width="stretch"):
            st.session_state.chat_history = []
            st.rerun()

    # Quick Suggestion Chips
    st.markdown(f"**💡 {get_text('quick_questions_title', lang)}:**")
    if lang == "te":
        chips = [
            "ప్రస్తుతం ఉష్ణోగ్రత ఎంత?",
            "వచ్చే ఏడు రోజుల్లో వర్షం పడుతుందా?",
            "ఎన్ని వర్షాభావ రోజులు గడిచాయి?",
            "నా పసుపు పంటకు వాతావరణం అనుకూలంగా ఉందా?",
            "నా అరటి పంటకు ఎలాంటి జాగ్రత్తలు తీసుకోవాలి?",
            "నా వరి పంటకు నీటి కొరత ప్రమాదం ఉందా?",
            "నా పసుపు పంటకు ఏ పరిస్థితి ఎక్కువ ప్రమాదకరం?",
            "వర్షాలు తగ్గితే నా పంటకు ఏమవుతుంది?",
            "నీటి సౌకర్యం లేకపోతే నేను ఏ జాగ్రత్తలు తీసుకోవాలి?",
        ]
    else:
        chips = [
            "What is the current temperature in my area?",
            "Will it rain in the next 7 days?",
            "How many dry days have occurred?",
            "Is the weather suitable for my crop?",
            "What precautions should I take for my banana crop?",
            "Is my paddy crop at risk of water shortage?",
            "Which scenario is most concerning for my turmeric crop?",
            "What happens if rainfall decreases by 30%?",
            "What precautions should I take if irrigation becomes unavailable?",
        ]

    chip_cols = st.columns(len(chips))
    selected_chip = None
    for idx, chip_text in enumerate(chips):
        with chip_cols[idx]:
            # Shortened label for display
            btn_label = chip_text if len(chip_text) <= 22 else chip_text[:20] + ".."
            if st.button(btn_label, key=f"chip_q_{idx}", help=chip_text, width="stretch"):
                selected_chip = chip_text

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

    # Chat History Container
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            # Welcoming prompt
            welcome_msg = (
                f"నమస్కారం! నేను మీ ఏఐ వ్యవసాయ సలహాదారుని. మీ పొలం ({district}, {crop}) మరియు ఓపెన్-మెటియో ప్రత్యక్ష వాతావరణ సమాచారం ఆధారంగా మీకు సలహాలు అందించగలను. క్రింద ఉన్న ప్రశ్నలపై క్లిక్ చేయండి లేదా మీ ప్రశ్నను టైప్ చేయండి."
                if lang == "te"
                else f"Welcome to the AI Farm Advisor! I synthesize real-time Open-Meteo weather telemetry with your Farm Digital Twin ({district}, {crop}) to deliver personalized agronomic insights. Select a suggested question above or type your query below."
            )
            st.markdown(
                f"""
                <div style="background-color: #f4f8f5; border: 1px dashed #2d6a4f; border-radius: 8px; padding: 18px 20px; color: #1b4332; font-size: 0.94rem; line-height: 1.5; margin-bottom: 16px;">
                    🌿 {welcome_msg}
                </div>
                """,
                unsafe_allow_html=True,
            )

        for msg in st.session_state.chat_history:
            role = msg["role"]
            content = msg["content"]
            meta = msg.get("metadata", {})

            if role == "user":
                with st.chat_message("user", avatar="🧑‍🌾"):
                    st.markdown(content)
            else:
                with st.chat_message("assistant", avatar="🌾"):
                    st.markdown(content)
                    grounding = meta.get("grounding_data")
                    refs = meta.get("references")
                    intent = meta.get("intent")
                    if grounding or refs:
                        with st.expander(f"🔍 {get_text('grounding_details_title', lang)} (Intent: `{intent}`)", expanded=False):
                            if grounding:
                                st.markdown("**Real-Time Data Points Used:**")
                                st.json(grounding)
                            if refs:
                                st.markdown("**Institutional Citations:**")
                                for r in refs:
                                    st.markdown(f"- **{r['authority']}**: [{r['document']}]({r['url']})")

    # Chat Input Box
    user_input = st.chat_input(placeholder=get_text("chat_input_placeholder", lang))

    # Check for pending query transferred from Simulator
    pending_query = st.session_state.pop("pending_advisor_query", None)

    # Handle submission from either text input, clicked chip, or transferred pending query
    active_query = user_input or selected_chip or pending_query

    if active_query:
        # 1. Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": active_query})

        # 2. Process query with Master Controller
        with st.spinner("Processing with Agricultural Agents..."):
            result = process_farmer_query(
                query=active_query,
                farm_profile=farm_profile,
                active_ui_lang=lang,
            )

        # 3. Add assistant response to history
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

        st.rerun()
