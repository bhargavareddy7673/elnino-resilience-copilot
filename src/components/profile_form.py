"""Farmer Profile Form and Digital Twin Visualization Component.

Manages the input form, validation, session state synchronization, and
digital twin snapshot display in English and Telugu.
"""

from datetime import date, datetime
import streamlit as st

from src.config import (
    DEFAULT_STATE,
    DEFAULT_DISTRICT,
    DEFAULT_VILLAGE,
    DEFAULT_CROP,
    DEFAULT_LAND_ACRES,
    DEFAULT_SOIL,
    DEFAULT_IRRIGATION,
    SUPPORTED_STATES,
    STATE_DISTRICT_MAP,
    SUPPORTED_CROPS,
    SOIL_TYPES,
    IRRIGATION_SOURCES,
)
from src.localization import get_text


def initialize_session_state() -> None:
    """Ensure default farm profile attributes exist in Streamlit session state."""
    if "farm_profile" not in st.session_state:
        st.session_state.farm_profile = {
            "state": DEFAULT_STATE,
            "district": DEFAULT_DISTRICT,
            "village": DEFAULT_VILLAGE,
            "crop": DEFAULT_CROP,
            "land_area": DEFAULT_LAND_ACRES,
            "soil_type": DEFAULT_SOIL,
            "irrigation": DEFAULT_IRRIGATION,
            "sowing_date": date.today(),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    if "selected_state" not in st.session_state:
        st.session_state.selected_state = st.session_state.farm_profile["state"]


def reset_to_defaults() -> None:
    """Reset the farmer profile state to default demo values (Kadapa, AP)."""
    st.session_state.farm_profile = {
        "state": DEFAULT_STATE,
        "district": DEFAULT_DISTRICT,
        "village": DEFAULT_VILLAGE,
        "crop": DEFAULT_CROP,
        "land_area": DEFAULT_LAND_ACRES,
        "soil_type": DEFAULT_SOIL,
        "irrigation": DEFAULT_IRRIGATION,
        "sowing_date": date.today(),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    st.session_state.selected_state = DEFAULT_STATE
    # Clear widget keys if present to ensure inputs reset cleanly
    for key in ["w_state", "w_district", "w_village", "w_crop", "w_area", "w_soil", "w_irrigation", "w_sowing"]:
        if key in st.session_state:
            del st.session_state[key]


def render_farmer_profile_form(lang: str = "en") -> dict:
    """Render the Farmer Profile input form and handle interactive updates.
    
    Args:
        lang: Selected language code ('en' or 'te').
        
    Returns:
        The current active farm profile dictionary.
    """
    initialize_session_state()
    current = st.session_state.farm_profile

    st.markdown(f"### {get_text('form_heading', lang)}")
    st.caption(get_text("form_caption", lang))

    with st.container(border=True):
        col1, col2 = st.columns(2, gap="large")

        # Column 1: Geographic & Land Attributes
        with col1:
            st.markdown(f"##### {get_text('state_label', lang)} & {get_text('district_label', lang)}")
            
            # State Selection (Reactive)
            state_options = SUPPORTED_STATES
            current_state = current.get("state", DEFAULT_STATE)
            if current_state not in state_options:
                current_state = DEFAULT_STATE
            state_idx = state_options.index(current_state)

            selected_state = st.selectbox(
                label=get_text("state_label", lang),
                options=state_options,
                index=state_idx,
                key="w_state",
            )

            # District Selection (Updates dynamically based on selected state)
            districts_list = STATE_DISTRICT_MAP.get(selected_state, [])
            current_district = current.get("district", DEFAULT_DISTRICT)
            if current_district in districts_list:
                district_idx = districts_list.index(current_district)
            elif selected_state == DEFAULT_STATE and DEFAULT_DISTRICT in districts_list:
                district_idx = districts_list.index(DEFAULT_DISTRICT)
            else:
                district_idx = 0

            selected_district = st.selectbox(
                label=get_text("district_label", lang),
                options=districts_list,
                index=district_idx,
                key="w_district",
            )

            # Village / Mandal Input (Editable, not assumed)
            village_value = current.get("village", "")
            selected_village = st.text_input(
                label=get_text("village_label", lang),
                value=village_value,
                placeholder=get_text("village_placeholder", lang),
                key="w_village",
            )

            # Cultivated Land Area (Exact decimal input: 0.5, 1.25, 2.75, 4.00, etc.)
            area_value = float(current.get("land_area", DEFAULT_LAND_ACRES))
            selected_area = st.number_input(
                label=get_text("land_area_label", lang),
                min_value=0.0,
                max_value=500.0,
                value=area_value,
                step=0.01,
                format="%.2f",
                help=get_text("land_area_help", lang),
                key="w_area",
            )

        # Column 2: Crop, Soil, and Water Attributes
        with col2:
            st.markdown(f"##### {get_text('crop_label', lang)} & {get_text('soil_type_label', lang)}")

            # Crop Selection using canonical keys and localized display
            crop_keys = list(SUPPORTED_CROPS.keys())
            current_crop = current.get("crop", DEFAULT_CROP)
            crop_idx = crop_keys.index(current_crop) if current_crop in crop_keys else 0

            selected_crop_key = st.selectbox(
                label=get_text("crop_label", lang),
                options=crop_keys,
                index=crop_idx,
                format_func=lambda k: SUPPORTED_CROPS[k][lang],
                key="w_crop",
            )

            # Soil Type Selection
            soil_keys = [s["en"] for s in SOIL_TYPES]
            soil_dict = {s["en"]: s[lang] for s in SOIL_TYPES}
            current_soil = current.get("soil_type", DEFAULT_SOIL)
            soil_idx = soil_keys.index(current_soil) if current_soil in soil_keys else 0

            selected_soil_en = st.selectbox(
                label=get_text("soil_type_label", lang),
                options=soil_keys,
                index=soil_idx,
                format_func=lambda k: soil_dict.get(k, k),
                key="w_soil",
            )

            # Irrigation Source Selection
            irr_keys = [i["en"] for i in IRRIGATION_SOURCES]
            irr_dict = {i["en"]: i[lang] for i in IRRIGATION_SOURCES}
            current_irr = current.get("irrigation", DEFAULT_IRRIGATION)
            irr_idx = irr_keys.index(current_irr) if current_irr in irr_keys else 0

            selected_irr_en = st.selectbox(
                label=get_text("irrigation_label", lang),
                options=irr_keys,
                index=irr_idx,
                format_func=lambda k: irr_dict.get(k, k),
                key="w_irrigation",
            )

            # Sowing / Plantation Date
            current_sowing = current.get("sowing_date", date.today())
            if isinstance(current_sowing, str):
                try:
                    current_sowing = datetime.strptime(current_sowing, "%Y-%m-%d").date()
                except ValueError:
                    current_sowing = date.today()

            selected_sowing = st.date_input(
                label=get_text("sowing_date_label", lang),
                value=current_sowing,
                key="w_sowing",
            )

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

        # Action Buttons
        btn_col1, btn_col2 = st.columns([2, 1])
        with btn_col1:
            save_clicked = st.button(
                label=get_text("submit_button", lang),
                type="primary",
                width="stretch",
            )
        with btn_col2:
            reset_clicked = st.button(
                label=get_text("reset_button", lang),
                width="stretch",
            )

        if reset_clicked:
            reset_to_defaults()
            st.rerun()

        if save_clicked:
            # Validate land area
            if selected_area <= 0.0:
                st.error(get_text("invalid_area_error", lang))
            else:
                st.session_state.farm_profile = {
                    "state": selected_state,
                    "district": selected_district,
                    "village": selected_village.strip(),
                    "crop": selected_crop_key,
                    "land_area": round(float(selected_area), 2),
                    "soil_type": selected_soil_en,
                    "irrigation": selected_irr_en,
                    "sowing_date": selected_sowing,
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
                st.session_state.selected_state = selected_state
                st.success(get_text("profile_saved_success", lang))
                st.rerun()

    return st.session_state.farm_profile


def render_digital_twin_summary(profile: dict, lang: str = "en") -> None:
    """Render the high-contrast, professional visual snapshot card of the Farm Digital Twin.
    
    Args:
        profile: Dictionary containing active farm profile attributes.
        lang: Selected language code ('en' or 'te').
    """
    crop_info = SUPPORTED_CROPS.get(profile["crop"], SUPPORTED_CROPS[DEFAULT_CROP])
    
    # Calculate days since sowing
    sowing_date_val = profile.get("sowing_date")
    has_valid_sow = False
    s_date = None
    days_elapsed = None
    if sowing_date_val:
        try:
            if isinstance(sowing_date_val, str) and sowing_date_val.strip():
                s_date = datetime.strptime(sowing_date_val.strip(), "%Y-%m-%d").date()
            elif isinstance(sowing_date_val, (date, datetime)):
                s_date = sowing_date_val if isinstance(sowing_date_val, date) else sowing_date_val.date()
            if s_date and s_date <= date.today():
                days_elapsed = max(0, (date.today() - s_date).days)
                has_valid_sow = True
        except Exception:
            has_valid_sow = False
            days_elapsed = None

    days_display = f"{days_elapsed} {get_text('unit_days', lang)}" if (has_valid_sow and days_elapsed is not None) else get_text("sowing_date_not_provided", lang)
    sow_date_display = s_date.strftime('%d %b %Y') if (has_valid_sow and s_date) else get_text("sowing_date_not_provided", lang)

    st.markdown(f"### {get_text('twin_summary_heading', lang)}")
    st.caption(get_text("twin_summary_subheading", lang))

    # Location text construction
    village_text = profile.get("village", "").strip()
    location_value = profile["district"]
    location_subtext = f"{village_text}, {profile['state']}" if village_text else profile["state"]

    # Metric Row (4 columns)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            label=get_text("metric_location", lang),
            value=location_value,
            help=location_subtext,
        )
    with m2:
        st.metric(
            label=get_text("metric_crop", lang),
            value=crop_info[lang],
            help=crop_info[f"category_{lang}"],
        )
    with m3:
        st.metric(
            label=get_text("metric_area", lang),
            value=f"{profile['land_area']:.2f} {get_text('unit_acres', lang)}",
        )
    with m4:
        st.metric(
            label=get_text("metric_days_since_sowing", lang),
            value=days_display,
            help=f"{get_text('metric_sowing_date', lang)}: {sow_date_display}",
        )

    # Detailed Farm Attributes Container
    with st.container(border=True):
        detail_col1, detail_col2 = st.columns(2, gap="large")
        with detail_col1:
            st.markdown(f"##### {get_text('agronomic_heading', lang)}: {crop_info[lang]}")
            st.markdown(f"• **{get_text('crop_classification', lang)}:** {crop_info[f'category_{lang}']}")
            st.markdown(f"• **{get_text('crop_duration', lang)}:** {crop_info[f'duration_{lang}']}")
            st.markdown(f"• **{get_text('typical_sowing_window', lang)}:** {crop_info[f'typical_sowing_{lang}']}")

        with detail_col2:
            # Soil and irrigation localization
            soil_display = profile["soil_type"]
            for s in SOIL_TYPES:
                if s["en"] == profile["soil_type"]:
                    soil_display = s[lang]
                    break

            irr_display = profile["irrigation"]
            for irr in IRRIGATION_SOURCES:
                if irr["en"] == profile["irrigation"]:
                    irr_display = irr[lang]
                    break

            st.markdown(f"##### {get_text('soil_water_heading', lang)}")
            st.markdown(f"• **{get_text('metric_soil', lang)}:** {soil_display}")
            st.markdown(f"• **{get_text('metric_irrigation', lang)}:** {irr_display}")
            st.markdown(f"• **{get_text('metric_sowing_date', lang)}:** {sow_date_display}")
            st.markdown(f"• **{get_text('sync_timestamp_label', lang)}:** `{profile.get('last_updated', 'Just now')}`")
