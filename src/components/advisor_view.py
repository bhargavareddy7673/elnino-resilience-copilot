"""RythuMithra AI Farm Advisor Screen: Bilingual Conversational & Spoken Voice Co-Pilot.

Allows farmers to ask questions in Telugu, English, or code-mixed Tanglish phrasing about:
- Atmospheric telemetry & 7-day rainfall forecasts.
- Dry spells, heat index, and El Niño contingency planning.
- Plot-specific water budgeting & fertilizer dosage schedules.
- Integrated pest, disease, weed, seed, and harvesting SOPs.
- Instant leaf pathology inspection via Leaf Doctor.

Supports BOTH Spoken Voice Interaction (One-Tap Native Audio Recorder) and Text Chatbot.
"""

from typing import Dict, Any, List, Optional
import re
import html
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components

from src.localization import get_text
from src.agents.controller import process_farmer_query
from src.multimodal.audio_transcriber import transcribe_audio, synthesize_speech
from src.multimodal.crop_vision import diagnose_crop_image


def get_clean_spoken_advisory(content: str, lang: str = "en") -> str:
    """Extract actionable, complete agronomic & weather advice for voice output, skipping titles/metadata."""
    if not content:
        return ""

    lines = content.split("\n")
    spoken_lines = []

    # Boilerplate headers to completely ignore
    pure_headers = (
        "###", "##", "#",
        "🌱", "🌾", "📍", "📅",
        "**Plot Parameters:**", "**Current Crop Status:**",
        "**పొలం వివరాలు:**", "**పంట వయస్సు & దశ:**", "**పంట స్థితి:**",
        "ℹ️", "#### 📚", "#### 🔍"
    )

    # 1. Actionable Section Check (under direct answer, practices, fertilizer, recommendations)
    in_action_section = False
    for line in lines:
        ls = line.strip()
        if not ls:
            continue

        if any(h in ls for h in ["#### 🎯", "🛡️", "పాటించవలసిన", "ముఖ్యమైన జాగ్రత్తలు", "Recommended", "సమగ్ర ఎరువుల", "షెడ్యూల్", "Direct Answer"]):
            in_action_section = True
            continue
        elif ls.startswith("#### 📚") or ls.startswith("### 🌾") or ls.startswith("### 📅"):
            in_action_section = False

        if in_action_section:
            # Skip metadata bullets
            if any(ls.startswith(p) for p in ["- 🗓️", "- 🌾", "- 🏞️", "- 📍", "ℹ️", "**పొలం వివరాలు", "**పంట వయస్సు"]):
                continue
            clean = re.sub(r"\[.*?\]\(.*?\)", "", ls)
            clean = re.sub(r"[*#`_>•\-]", " ", clean).strip()
            clean = re.sub(r"\$.*?\$", "", clean).strip()
            clean = re.sub(r"\s+", " ", clean).strip()
            if len(clean) > 15:
                spoken_lines.append(clean)
                if len(spoken_lines) >= 3:
                    break

    # 2. Informational bullet items (Weather telemetry, Forecast points, Agronomic tips)
    if not spoken_lines:
        for line in lines:
            ls = line.strip()
            if not ls:
                continue
            is_bullet = (
                ls.startswith("•") or
                re.match(r"^-\s+[🌡️💧💨🌧️☀️⚠️🌾🛡️]", ls) or
                re.match(r"^\d+\.\s+", ls)
            )
            is_meta = any(ls.startswith(p) for p in ["- 🗓️", "- 🌾", "- 🏞️", "- 📍"]) and ("వయస్సు" in ls or "నమోదు" in ls or "Age" in ls)
            if is_bullet and not is_meta:
                clean = re.sub(r"\[.*?\]\(.*?\)", "", ls)
                clean = re.sub(r"[*#`_>•\-]", " ", clean).strip()
                clean = re.sub(r"\$.*?\$", "", clean).strip()
                clean = re.sub(r"\s+", " ", clean).strip()
                if len(clean) > 12:
                    spoken_lines.append(clean)
                    if len(spoken_lines) >= 3:
                        break

    # 3. Informational paragraphs (skipping headers and metadata)
    if not spoken_lines:
        for p in content.split("\n\n"):
            ps = p.strip()
            if not ps:
                continue
            is_header_or_meta = any(ps.startswith(h) for h in pure_headers) or ps.endswith(":") or ps.endswith(":\n")
            if not is_header_or_meta:
                clean = re.sub(r"\[.*?\]\(.*?\)", "", ps)
                clean = re.sub(r"[*#`_>•\-]", " ", clean).strip()
                clean = re.sub(r"\$.*?\$", "", clean).strip()
                clean = re.sub(r"\s+", " ", clean).strip()
                if len(clean) > 20:
                    spoken_lines.append(clean)
                    if len(spoken_lines) >= 2:
                        break

    res = ". ".join(spoken_lines)
    res = re.sub(r"\s+", " ", res).replace("..", ".").strip()

    if len(res) > 380:
        last_period = res[:380].rfind(".")
        if last_period > 120:
            res = res[:last_period + 1].strip()
        else:
            res = res[:380].strip() + "."

    return res


def initialize_chat_history() -> None:
    """Ensure chat conversation history exists in session state."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    st.session_state.is_processing_advisor = False


def render_advisor_view(farm_profile: Dict[str, Any], lang: str = "en") -> None:
    """Render the RythuMithra AI Farm Advisor screen with simultaneous Voice & Chat capability."""
    initialize_chat_history()

    # 0. Check for incoming URL voice query parameter
    if "voice_query" in st.query_params:
        raw_vq = st.query_params.get("voice_query", "").strip()
        vq = urllib.parse.unquote(raw_vq).strip()
        try:
            del st.query_params["voice_query"]
        except Exception:
            st.query_params.clear()
        if vq:
            st.session_state.pending_advisor_query = vq
            st.session_state.pending_advisor_modality = "voice"
            st.rerun()

    crop = farm_profile.get("crop", "Turmeric")
    district = farm_profile.get("district", "Kurnool")
    village = farm_profile.get("village", "").strip()
    loc_str = f"{village}, {district}" if village else district

    crop_te_map = {"Turmeric": "పసుపు", "Banana": "అరటి", "Paddy": "వరి"}
    crop_te = crop_te_map.get(crop, crop)

    # 1. Header Card with Active Farm Context and Clear Action
    adv_title = "RythuMithra NLP: బహుభాషా ఏఐ వ్యవసాయ సలహాదారు (రైతు మిత్ర)" if lang == "te" else "RythuMithra NLP: Multilingual Conversational Voice Assistant (రైతు మిత్ర)"
    adv_sub = (
        f"📍 {loc_str} • 🌿 {crop_te if lang == 'te' else crop} ({farm_profile.get('land_area', 4.0)} ఎకరాలు) • రియల్-టైమ్ వ్యవసాయ & వాతావరణ మార్గదర్శనం"
        if lang == "te"
        else f"📍 {loc_str} • 🌿 {crop} ({farm_profile.get('land_area', 4.0)} Acres) • Real-Time Agronomic & Weather Decision Support"
    )

    st.markdown(
        f"""
        <div style="background-color: #FFFFFF; border: 1.5px solid #D8EADB; border-radius: 14px; padding: 18px 22px; margin-bottom: 14px; box-shadow: 0 2px 6px rgba(27,67,50,0.03);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
                <div>
                    <div style="font-size: 1.35rem; font-weight: 800; color: #1B4332; display: flex; align-items: center; gap: 8px;">
                        🤖 {adv_title}
                    </div>
                    <div style="font-size: 0.85rem; color: #527964; margin-top: 4px; font-weight: 500;">
                        {adv_sub}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Clear chat button row
    clear_row_col1, clear_row_col2 = st.columns([3, 1])
    with clear_row_col2:
        clear_label = "🗑️ " + ("చాట్ క్లియర్ చేయండి" if lang == "te" else "Clear Chat")
        if st.button(clear_label, key="btn_clear_chat_hist", width="stretch"):
            st.session_state.chat_history = []
            st.session_state.is_processing_advisor = False
            st.rerun()

    # 2. PROMINENT SPOKEN VOICE CHAT ASSISTANT (Native Top-Level Microphone)
    v_card_title = "🎙️ రైతు వాయిస్ అసిస్టెంట్ • RythuMithra Spoken NLP Co-Pilot" if lang == "te" else "🎙️ RythuMithra Spoken NLP Co-Pilot (రైతు మిత్ర)"
    v_card_sub = (
        "మైక్రోఫోన్ నొక్కి తెలుగు లేదా ఇంగ్లీషులో మాట్లాడండి • రికార్డింగ్ ఆపిన వెంటనే నేరుగా సమాధానం వస్తుంది"
        if lang == "te"
        else "Tap the microphone below, speak in Telugu or English, then tap stop. Your voice advisory is answered aloud instantly!"
    )

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 60%, #40916C 100%); border-radius: 12px; padding: 16px 20px; color: #FFFFFF; box-shadow: 0 4px 14px rgba(27,67,50,0.18); border: 1.5px solid #52B788; margin-bottom: 12px;">
            <div style="font-size: 1.15rem; font-weight: 800; color: #FFFFFF; display: flex; align-items: center; gap: 8px;">
                {v_card_title}
            </div>
            <div style="font-size: 0.88rem; color: #E8F5E9; margin-top: 4px; font-weight: 500; line-height: 1.5;">
                {v_card_sub}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Voice language selection (Default to Telugu for Andhra Pradesh / Telangana farmers)
    v_lang_choice = st.pills(
        "🗣️ " + ("వాయిస్ మాట్లాడే భాష (Voice Language):" if lang == "te" else "Voice Language / మాట్లాడే భాష:"),
        ["🌾 తెలుగు (Telugu)", "🌐 English"],
        default="🌾 తెలుగు (Telugu)",
        key="advisor_voice_lang_pills",
    )
    v_lang = "te" if "తెలుగు" in (v_lang_choice or "తెలుగు") else "en"

    v_col1, v_col2 = st.columns([3, 2])
    with v_col1:
        audio_mic = st.audio_input(
            "🎙️ " + ("మాట్లాడటానికి మైక్ నొక్కండి (Tap to Speak):" if v_lang == "te" else "Tap mic to record question:"),
            key="advisor_main_mic",
        )
    with v_col2:
        audio_file = st.file_uploader(
            "📁 " + ("వాయిస్ నోట్ అప్‌లోడ్ చేయండి:" if v_lang == "te" else "Or upload voice audio note:"),
            type=["wav", "mp3", "m4a", "ogg"],
            key="advisor_main_file",
        )

    # Automatic Voice Transcription & Direct Answering upon recording stop
    active_audio = audio_mic or audio_file
    if active_audio is not None:
        audio_sig = f"{getattr(active_audio, 'name', 'mic')}_{getattr(active_audio, 'size', 0)}"
        if st.session_state.get("last_voice_query_sig") != audio_sig:
            with st.spinner("🎙️ " + ("మీ మాటలను విశ్లేషించి సమాధానం తయారుచేస్తున్నాము..." if v_lang == "te" else "Transcribing voice and synthesizing agricultural advisory...")):
                res = transcribe_audio(active_audio, lang=v_lang)
                st.session_state["last_voice_query_sig"] = audio_sig
                if res.get("success"):
                    tx_text = res.get("text", "").strip()
                    if tx_text:
                        st.session_state["last_voice_text"] = tx_text
                        st.session_state.pending_advisor_query = tx_text
                        st.session_state.pending_advisor_modality = "voice"
                        st.session_state.pending_advisor_lang = v_lang
                        st.rerun()
                else:
                    st.warning(f"⚠️ {res.get('error', 'Could not transcribe audio.')}")

        last_tx = st.session_state.get("last_voice_text")
        if last_tx:
            st.success(f"🗣️ **{'మీరు అడిగిన ప్రశ్న' if lang == 'te' else 'Transcribed Voice'}:** *\"{last_tx}\"* — **{'క్రింద సమాధానం చూడండి 👇' if lang == 'te' else 'Directly answered below 👇'}**")

    # 3. LEAF DOCTOR / CROP PATHOLOGY INSPECTOR (Expander)
    leaf_doc_title = "🔬 ఆకు తెగుళ్ల పరీక్ష & నివారణ (Leaf Doctor: Inspect Crop Disease & Pests)" if lang == "te" else "🔬 Leaf Doctor: Inspect Crop Disease & Pests (Camera / Photo)"
    with st.expander(leaf_doc_title, expanded=False):
        vis_choice = st.radio(
            "ఫోటో మూలం (Photo Source):" if lang == "te" else "Photo Source:",
            ["ఫైల్ అప్‌లోడ్ (Upload File)", "కెమెరా ద్వారా ఫోటో (Take Camera Photo)"] if lang == "te" else ["Upload Photo", "Take Camera Photo"],
            horizontal=True,
            label_visibility="collapsed",
            key="vis_input_source_choice",
        )

        img_file = None
        if "కెమెరా" in vis_choice or "Camera" in vis_choice:
            img_file = st.camera_input("ఆకు ఫోటో తీయండి" if lang == "te" else "Capture crop leaf photo", key="vision_cam_input")
        else:
            img_file = st.file_uploader("ఆకు ఫోటో ఎంచుకోండి" if lang == "te" else "Upload crop leaf photo", type=["jpg", "jpeg", "png", "webp"], key="vision_file_upload")

        if img_file is not None:
            img_sig = f"{getattr(img_file, 'name', 'cam')}_{getattr(img_file, 'size', 0)}"
            if st.session_state.get("last_diagnosed_sig") != img_sig:
                with st.spinner("🔬 " + ("ఆకును పరిశీలించి వ్యాధిని నిర్ధారిస్తున్నాము..." if lang == "te" else "Diagnosing leaf sample against ICAR pathology benchmarks...")):
                    diag = diagnose_crop_image(img_file, crop_hint=crop, lang=lang)
                    st.session_state["last_diagnosed_sig"] = img_sig
                    st.session_state["last_diagnosed_result"] = diag

            cached_diag = st.session_state.get("last_diagnosed_result")
            if cached_diag:
                d_col1, d_col2 = st.columns([1, 2])
                with d_col1:
                    st.image(img_file, caption=f"{crop} Sample", use_container_width=True)
                with d_col2:
                    sev_colors = {
                        "Healthy": ("#2D6A4F", "#D8EADB"),
                        "Mild": ("#1E3A8A", "#DBEAFE"),
                        "Moderate": ("#B45309", "#FEF3C7"),
                        "Severe": ("#991B1B", "#FEE2E2"),
                    }
                    txt_c, bg_c = sev_colors.get(cached_diag.severity_level, ("#1B4332", "#E8F5E9"))
                    disease_name = cached_diag.disease_name_te if lang == "te" else cached_diag.disease_name_en

                    st.markdown(
                        f"""
                        <div style="background-color: {bg_c}; border-radius: 10px; padding: 12px 16px; margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-weight: 800; font-size: 1.15rem; color: {txt_c};">🔬 {disease_name}</span>
                                <span style="font-weight: 700; font-size: 0.85rem; background-color: {txt_c}; color: #FFF; padding: 3px 8px; border-radius: 6px;">
                                    {cached_diag.severity_level} ({cached_diag.confidence_score}%)
                                </span>
                            </div>
                            <div style="font-size: 0.85rem; color: #374151; margin-top: 4px; font-style: italic;">
                                Pathogen: {cached_diag.pathogen_scientific}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"**{'లక్షణాలు' if lang == 'te' else 'Observed Symptoms'}:** {cached_diag.symptoms_summary}")
                    st.markdown(f"**{'నివారణ చర్యలు (ICAR)' if lang == 'te' else 'Recommended Treatment (ICAR)'}:** {cached_diag.chemical_control}")

                    ask_prompt = (
                        f"నా {crop_te} పంటకు {disease_name} ({cached_diag.pathogen_scientific}) సోకింది. "
                        f"నా {farm_profile.get('land_area', 4.0)} ఎకరాల పొలానికి పూర్తి నివారణ మరియు ఎరువుల ప్రణాళిక తెలపండి."
                        if lang == "te"
                        else f"My {crop} has been diagnosed with {cached_diag.disease_name_en} ({cached_diag.pathogen_scientific}). "
                        f"What is the complete treatment schedule and dosage for my {farm_profile.get('land_area', 4.0)} acre plot?"
                    )
                    if st.button("💬 " + ("సలహాదారుని అడగండి (Ask Advisor)" if lang == "te" else "Ask Advisor for Plot Plan"), key="btn_ask_from_vision"):
                        st.session_state.pending_advisor_query = ask_prompt
                        st.rerun()

    # 4. SUGGESTED QUESTIONS (Quick 1-Click Buttons)
    st.markdown(f"**💡 {get_text('quick_questions_title', lang)}:**")

    if lang == "te":
        primary_chips = [
            "ప్రస్తుతం ఉష్ణోగ్రత ఎంత?",
            "వచ్చే 7 రోజుల్లో వర్షం పడుతుందా?",
            f"నా {crop_te} పంటకు ఎరువులు ఎప్పుడు వేయాలి?",
            f"నా {crop_te} పంటకు నీటి తడుల ప్రణాళిక ఏమిటి?",
        ]
        secondary_chips = [
            f"వర్షాభావ సమయంలో నా {crop_te} పంటను ఎలా కాపాడుకోవాలి?",
            f"నా {crop_te} పంటకు ఎలాంటి జాగ్రత్తలు తీసుకోవాలి?",
            "నా పొలం వనరుల వివరాలు చెప్పండి",
        ]
    else:
        primary_chips = [
            "What is the current temperature in my area?",
            "Will it rain in the next 7 days?",
            f"How to budget fertilizers and resources for my {crop.lower()} farm?",
            f"How to plan irrigation for my {crop.lower()} crop?",
        ]
        secondary_chips = [
            f"How to protect my {crop.lower()} during an El Niño dry spell?",
            f"What precautions and resilience practices are recommended?",
            "Tell me about my farm resources.",
        ]

    selected_chip = None

    # 2x2 Grid of Primary Chips
    r1_col1, r1_col2 = st.columns(2)
    with r1_col1:
        if st.button(f"💬 {primary_chips[0]}", key="chip_pri_0", width="stretch"):
            st.session_state.pending_advisor_query = primary_chips[0]
            st.session_state.pending_advisor_modality = "text"
            st.session_state.pending_advisor_lang = lang
            st.rerun()
    with r1_col2:
        if st.button(f"💬 {primary_chips[1]}", key="chip_pri_1", width="stretch"):
            st.session_state.pending_advisor_query = primary_chips[1]
            st.session_state.pending_advisor_modality = "text"
            st.session_state.pending_advisor_lang = lang
            st.rerun()

    r2_col1, r2_col2 = st.columns(2)
    with r2_col1:
        if st.button(f"💬 {primary_chips[2]}", key="chip_pri_2", width="stretch"):
            st.session_state.pending_advisor_query = primary_chips[2]
            st.session_state.pending_advisor_modality = "text"
            st.session_state.pending_advisor_lang = lang
            st.rerun()
    with r2_col2:
        if st.button(f"💬 {primary_chips[3]}", key="chip_pri_3", width="stretch"):
            st.session_state.pending_advisor_query = primary_chips[3]
            st.session_state.pending_advisor_modality = "text"
            st.session_state.pending_advisor_lang = lang
            st.rerun()

    # Secondary suggestions in expander
    with st.expander(f"➕ {get_text('more_suggestions', lang)}", expanded=False):
        sec_cols = st.columns(len(secondary_chips))
        for s_idx, sec_chip in enumerate(secondary_chips):
            with sec_cols[s_idx]:
                if st.button(f"💬 {sec_chip}", key=f"chip_sec_{s_idx}", width="stretch"):
                    st.session_state.pending_advisor_query = sec_chip
                    st.session_state.pending_advisor_modality = "text"
                    st.session_state.pending_advisor_lang = lang
                    st.rerun()

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

    # 5. CHAT MESSAGES CONTAINER
    chat_box = st.container()
    with chat_box:
        if not st.session_state.chat_history:
            # Welcoming prompt card
            welcome_head = "నమస్కారం! El Niño Resilience Co-Pilot • రైతు మిత్ర (RythuMithra)" if lang == "te" else "Welcome to El Niño Resilience Co-Pilot (రైతు మిత్ర)"
            welcome_msg = (
                f"మీ పొలం ({loc_str}, {crop_te}), నేల రకం, నీటి వనరులు మరియు ప్రత్యక్ష వాతావరణ సమాచారం ఆధారంగా సమగ్ర సాగు సలహాలు, "
                f"ఎరువుల మోతాదులు, నీటి తడుల ప్రణాళికలు, మరియు ఎల్ నినో రక్షణ చర్యలు అందించగలను. "
                f"పైన ఉన్న మైక్రోఫోన్ నొక్కి వాయిస్ ద్వారా మాట్లాడండి లేదా క్రింద సందేశ బాక్స్‌లో టైప్ చేయండి."
                if lang == "te"
                else f"I provide comprehensive agronomic intelligence tailored to your {loc_str} plot ({crop}, {farm_profile.get('land_area', 4.0)} Acres): "
                f"fertilizer schedule calculations, water budgeting, 7-day weather outlooks, and El Niño contingency planning. "
                f"Tap the microphone above to speak freely in Telugu or English, or type in the box below."
            )
            st.markdown(
                f"""
                <div style="background-color: #FFFFFF; border: 1.5px solid #D8EADB; border-radius: 14px; padding: 20px 24px; box-shadow: 0 2px 8px rgba(27,67,50,0.03); margin-bottom: 20px;">
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

        for msg_idx, msg in enumerate(st.session_state.chat_history):
            role = msg["role"]
            content = msg["content"]
            meta = msg.get("metadata", {})

            if role == "user":
                with st.chat_message("user"):
                    if meta.get("input_modality") == "voice":
                        st.markdown(f"🎙️ **{'వాయిస్ ప్రశ్న (Voice Input)' if lang == 'te' else 'Voice Input'}:** {content}")
                    else:
                        st.markdown(content)
            else:
                with st.chat_message("assistant"):
                    st.markdown(content)

                    # VOICE OUTPUT HANDLING:
                    # If input came from VOICE: Auto-play spoken audio with Equalizer & Controls
                    # If input came from TEXT: Provide interactive optional listen button
                    is_voice_input = (meta.get("input_modality") == "voice")
                    is_latest = (msg_idx == len(st.session_state.chat_history) - 1)
                    msg_lang = meta.get("detected_language", lang)
                    clean_spoken = get_clean_spoken_advisory(content, lang=msg_lang)
                    speech_bytes = meta.get("voice_bytes")

                    if is_voice_input:
                        if not speech_bytes:
                            speech_bytes = synthesize_speech(clean_spoken, lang=msg_lang)
                            meta["voice_bytes"] = speech_bytes

                        safe_spoken_txt = html.escape(clean_spoken)
                        title_text = "🔊 రైతు వాయిస్ సమాధానం (Telugu Audio Advisory)" if msg_lang == "te" else "🔊 Spoken Voice Advisory"
                        sub_badge = "స్పష్టమైన తెలుగు ఆడియో" if msg_lang == "te" else "Single Clear Voice Output"

                        # High-contrast, clean, bright card with ZERO overlapping JavaScript voice
                        st.markdown(
                            f"""
                            <div style="background-color: #FFFFFF; border: 2px solid #2D6A4F; border-radius: 12px; padding: 16px 20px; margin: 12px 0 10px 0; box-shadow: 0 2px 10px rgba(45,106,79,0.08);">
                                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                                    <div style="font-weight: 800; font-size: 1.05rem; color: #1B4332; display: flex; align-items: center; gap: 8px;">
                                        {title_text}
                                    </div>
                                    <span style="background-color: #E8F5E9; color: #1B5E20; font-size: 0.75rem; font-weight: 700; padding: 3px 10px; border-radius: 999px;">
                                        {sub_badge}
                                    </span>
                                </div>
                                <div style="font-size: 0.98rem; color: #1B4332; font-weight: 500; line-height: 1.6; background-color: #F4F9F4; padding: 12px 16px; border-radius: 8px; border-left: 4px solid #2D6A4F; margin-bottom: 8px;">
                                    <i>"{safe_spoken_txt}"</i>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        # EXACTLY ONE SINGLE AUDIO PLAYER (Zero overlapping JS SpeechSynthesis!)
                        if speech_bytes:
                            st.audio(speech_bytes, format="audio/mp3", autoplay=is_latest)
                    else:
                        # For text questions: provide an optional listen expander without auto-playing
                        with st.expander("🔊 " + ("వాయిస్ సలహా వినండి (Listen to Advisory)" if lang == "te" else "Listen to Spoken Advisory"), expanded=False):
                            if not speech_bytes:
                                speech_bytes = synthesize_speech(clean_spoken, lang=lang)
                                meta["voice_bytes"] = speech_bytes
                            if speech_bytes:
                                st.audio(speech_bytes, format="audio/mp3", autoplay=False)
                            else:
                                st.info("ఆడియో సదుపాయం తాత్కాలికంగా అందుబాటులో లేదు." if lang == "te" else "Spoken audio unavailable offline.")

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

    # 6. CHAT INPUT BOX (Bottom Fixed Composer)
    user_input = st.chat_input(placeholder="వ్యవసాయం, ఎరువులు, నీటి తడులు లేదా వాతావరణం గురించి అడగండి..." if lang == "te" else "Ask about farming, weather, water budgets, fertilizer planning, or El Niño...")

    # Check for pending query transferred from Voice, Vision, or URL
    pending_query = st.session_state.pop("pending_advisor_query", None)
    pending_modality = st.session_state.pop("pending_advisor_modality", None)

    active_query = None
    input_modality = "text"
    if pending_query:
        active_query = pending_query
        input_modality = pending_modality or "text"
    elif user_input:
        active_query = user_input
        input_modality = "text"
    elif selected_chip:
        active_query = selected_chip
        input_modality = "text"

    cleaned_query = active_query.strip() if (active_query and isinstance(active_query, str)) else None

    if cleaned_query and not st.session_state.is_processing_advisor:
        st.session_state.is_processing_advisor = True
        try:
            # Append user message with modality
            st.session_state.chat_history.append({
                "role": "user",
                "content": cleaned_query,
                "metadata": {"input_modality": input_modality},
            })

            eff_lang = st.session_state.pop("pending_advisor_lang", lang)
            # Process with controller inside friendly loading spinner
            with st.spinner(get_text("advisor_analyzing", eff_lang)):
                result = process_farmer_query(
                    query=cleaned_query,
                    farm_profile=farm_profile,
                    active_ui_lang=eff_lang,
                    chat_history=st.session_state.chat_history,
                )

            # Pre-generate voice bytes ONLY IF input came from VOICE
            voice_bytes = None
            if input_modality == "voice":
                resp_lang = result.get("detected_language", eff_lang)
                clean_spoken_res = get_clean_spoken_advisory(result.get("response_text", ""), lang=resp_lang)
                voice_bytes = synthesize_speech(clean_spoken_res, lang=resp_lang)

            # Append assistant response
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": result.get("response_text", ""),
                "metadata": {
                    "intent": result.get("intent", "unknown"),
                    "detected_language": result.get("detected_language", lang),
                    "grounding_data": result.get("grounding_data", {}),
                    "references": result.get("references", []),
                    "input_modality": input_modality,
                    "voice_bytes": voice_bytes,
                },
            })
        except Exception as exc:
            err_msg_te = "క్షమించండి, మీ ప్రశ్నకు సమాధానం ఇవ్వడంలో సమస్య ఎదురైంది. దయచేసి మళ్లీ ప్రయత్నించండి."
            err_msg_en = "I apologize, but an issue occurred while processing your request. Please try asking again."
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": err_msg_te if lang == "te" else err_msg_en,
                "metadata": {
                    "intent": "error",
                    "detected_language": lang,
                    "grounding_data": {"status": "error", "error_type": type(exc).__name__},
                    "references": [],
                },
            })
        finally:
            st.session_state.is_processing_advisor = False

        st.rerun()
