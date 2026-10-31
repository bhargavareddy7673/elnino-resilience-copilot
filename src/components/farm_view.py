"""My Farm Screen Component: Profile Configuration & Digital Twin Snapshot.

Provides a clean, commercial-grade interface for farmers to review,
configure, and edit their farm plot parameters in English and Telugu.
"""

from typing import Dict, Any
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
from src.knowledge.crop_knowledge import get_crop_profile, get_growth_stage_by_days


def initialize_farm_state() -> None:
    """Ensure farm profile dictionary exists in Streamlit session state."""
    if "farm_profile" not in st.session_state:
        st.session_state.farm_profile = {
            "state": DEFAULT_STATE,
            "district": DEFAULT_DISTRICT,
            "village": DEFAULT_VILLAGE,
            "crop": DEFAULT_CROP,
            "land_area": DEFAULT_LAND_ACRES,
            "soil_type": DEFAULT_SOIL,
            "irrigation": DEFAULT_IRRIGATION,
            "sowing_date": None,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    if "selected_state" not in st.session_state:
        st.session_state.selected_state = st.session_state.farm_profile["state"]


def render_farm_view(lang: str = "en") -> Dict[str, Any]:
    """Render the My Farm configuration screen and Digital Twin snapshot.
    
    Args:
        lang: Selected language ('en' or 'te').
        
    Returns:
        The current active farm profile dictionary.
    """
    initialize_farm_state()
    current = st.session_state.farm_profile

    st.markdown(f"### 🌱 {get_text('form_heading', lang)}")
    st.caption(get_text("form_caption", lang))

    # Two column layout: Edit Form on left, Digital Twin Snapshot on right
    form_col, twin_col = st.columns([1, 1], gap="large")

    with form_col:
        form_title = "📝 " + ("Edit Plot Attributes" if lang == "en" else "పొలం వివరాల నమోదు / సవరణ")
        st.markdown(
            f"""<div style="background-color: #ffffff; border: 1px solid #e2ebe5; border-radius: 12px; padding: 16px 20px; box-shadow: 0 2px 8px rgba(27,67,50,0.04); margin-bottom: 16px;">
<h4 style="margin: 0; color: #1b4332; font-size: 1.1rem; font-weight: 700;">{form_title}</h4>
</div>""",
            unsafe_allow_html=True,
        )

        with st.form("my_farm_edit_form"):
            c_geo1, c_geo2 = st.columns(2)
            with c_geo1:
                # State
                state_opts = SUPPORTED_STATES
                cur_state = current.get("state", DEFAULT_STATE)
                state_idx = state_opts.index(cur_state) if cur_state in state_opts else 0
                selected_state = st.selectbox(
                    label=get_text("state_label", lang),
                    options=state_opts,
                    index=state_idx,
                    key="farm_w_state",
                )

            with c_geo2:
                # District
                dist_opts = STATE_DISTRICT_MAP.get(selected_state, STATE_DISTRICT_MAP[DEFAULT_STATE])
                cur_dist = current.get("district", DEFAULT_DISTRICT)
                dist_idx = dist_opts.index(cur_dist) if cur_dist in dist_opts else 0
                selected_district = st.selectbox(
                    label=get_text("district_label", lang),
                    options=dist_opts,
                    index=dist_idx,
                    key="farm_w_dist",
                )

            # Village
            selected_village = st.text_input(
                label=get_text("village_label", lang),
                value=current.get("village", DEFAULT_VILLAGE),
                placeholder=get_text("village_placeholder", lang),
                key="farm_w_village",
            )

            c_crop1, c_crop2 = st.columns(2)
            with c_crop1:
                # Crop Selection
                crop_keys = list(SUPPORTED_CROPS.keys())
                cur_crop = current.get("crop", DEFAULT_CROP)
                crop_idx = crop_keys.index(cur_crop) if cur_crop in crop_keys else 0
                crop_dict = {k: SUPPORTED_CROPS[k][lang] for k in crop_keys}
                selected_crop = st.selectbox(
                    label=get_text("crop_label", lang),
                    options=crop_keys,
                    index=crop_idx,
                    format_func=lambda k: crop_dict.get(k, k),
                    key="farm_w_crop",
                )

            with c_crop2:
                # Land Area with exact decimal support
                cur_area = float(current.get("land_area", DEFAULT_LAND_ACRES))
                selected_area = st.number_input(
                    label=get_text("land_area_label", lang),
                    min_value=0.01,
                    max_value=500.0,
                    value=cur_area,
                    step=0.25,
                    format="%.2f",
                    help=get_text("land_area_help", lang),
                    key="farm_w_area",
                )

            c_soil, c_irrig = st.columns(2)
            with c_soil:
                # Soil Type Selection
                soil_keys = [s["en"] for s in SOIL_TYPES]
                soil_dict = {s["en"]: s[lang] for s in SOIL_TYPES}
                cur_soil = current.get("soil_type", DEFAULT_SOIL)
                soil_idx = soil_keys.index(cur_soil) if cur_soil in soil_keys else 0
                selected_soil = st.selectbox(
                    label=get_text("soil_type_label", lang),
                    options=soil_keys,
                    index=soil_idx,
                    format_func=lambda k: soil_dict.get(k, k),
                    key="farm_w_soil",
                )

            with c_irrig:
                # Irrigation Source Selection
                irrig_keys = [i["en"] for i in IRRIGATION_SOURCES]
                irrig_dict = {i["en"]: i[lang] for i in IRRIGATION_SOURCES}
                cur_irrig = current.get("irrigation", DEFAULT_IRRIGATION)
                irrig_idx = irrig_keys.index(cur_irrig) if cur_irrig in irrig_keys else 0
                selected_irrigation = st.selectbox(
                    label=get_text("irrigation_label", lang),
                    options=irrig_keys,
                    index=irrig_idx,
                    format_func=lambda k: irrig_dict.get(k, k),
                    key="farm_w_irrig",
                )

            # Sowing Date
            cur_sowing = current.get("sowing_date", date.today())
            if isinstance(cur_sowing, str):
                try:
                    cur_sowing = date.fromisoformat(cur_sowing)
                except Exception:
                    cur_sowing = date.today()
            selected_sowing = st.date_input(
                label=get_text("sowing_date_label", lang),
                value=cur_sowing,
                max_value=date.today(),
                key="farm_w_sowing",
            )

            col_submit, col_reset = st.columns([2, 1])
            with col_submit:
                save_submitted = st.form_submit_button(
                    label=f"💾 {get_text('submit_button', lang)}",
                    width="stretch",
                    type="primary",
                )
            with col_reset:
                reset_submitted = st.form_submit_button(
                    label=f"↺ {get_text('reset_button', lang)}",
                    width="stretch",
                )

        if save_submitted:
            st.session_state.farm_profile = {
                "state": selected_state,
                "district": selected_district,
                "village": selected_village.strip(),
                "crop": selected_crop,
                "land_area": selected_area,
                "soil_type": selected_soil,
                "irrigation": selected_irrigation,
                "sowing_date": selected_sowing,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            st.toast(get_text("profile_saved_success", lang), icon="✅")
            st.rerun()

        if reset_submitted:
            st.session_state.farm_profile = {
                "state": DEFAULT_STATE,
                "district": DEFAULT_DISTRICT,
                "village": DEFAULT_VILLAGE,
                "crop": DEFAULT_CROP,
                "land_area": DEFAULT_LAND_ACRES,
                "soil_type": DEFAULT_SOIL,
                "irrigation": DEFAULT_IRRIGATION,
                "sowing_date": None,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            st.rerun()

    # Right Column: Visual Digital Twin Snapshot
    with twin_col:
        profile = st.session_state.farm_profile
        crop_val = profile.get("crop", DEFAULT_CROP)
        area_val = profile.get("land_area", DEFAULT_LAND_ACRES)
        soil_val = profile.get("soil_type", DEFAULT_SOIL)
        irrig_val = profile.get("irrigation", DEFAULT_IRRIGATION)
        dist_val = profile.get("district", DEFAULT_DISTRICT)
        vill_val = profile.get("village", "").strip()
        state_val = profile.get("state", DEFAULT_STATE)
        sow_val = profile.get("sowing_date")
        last_sync = profile.get("last_updated", "Just now")

        # Days in field
        has_valid_sow = False
        days_in_field = None
        s_date = None
        if sow_val:
            try:
                if isinstance(sow_val, str) and sow_val.strip():
                    s_date = date.fromisoformat(sow_val.strip())
                elif isinstance(sow_val, (date, datetime)):
                    s_date = sow_val if isinstance(sow_val, date) else sow_val.date()
                else:
                    s_date = None
                if s_date and s_date <= date.today():
                    days_in_field = max(0, (date.today() - s_date).days)
                    has_valid_sow = True
            except Exception:
                has_valid_sow = False
                days_in_field = None
                s_date = None

        if has_valid_sow and days_in_field is not None:
            crop_age_display = f"{days_in_field} {get_text('unit_days', lang)}"
            stage_info = get_growth_stage_by_days(crop_val, days_in_field)
            stage_display = stage_info.get("stage", "Unknown")
            sow_date_display = s_date.strftime("%d %b %Y") if s_date else str(sow_val)
        else:
            crop_age_display = get_text("sowing_date_not_provided", lang)
            stage_display = get_text("stage_not_determined", lang)
            sow_date_display = get_text("sowing_date_not_provided", lang)

        crop_info = get_crop_profile(crop_val)
        crop_display = crop_info.get(f"crop_name_{lang}", crop_val)
        loc_display = f"{vill_val}, {dist_val}" if vill_val else f"{dist_val}, {state_val}"

        # Localized digital twin labels
        twin_heading = "🌾 Farm Digital Twin" if lang == "en" else "🌾 ఫార్మ్ డిజిటల్ ట్విన్"
        twin_sub = "Live Virtual Plot Representation" if lang == "en" else "ప్రత్యక్ష డిజిటల్ క్షేత్ర చిత్రం"
        badge_active = "Active" if lang == "en" else "యాక్టివ్"
        lbl_loc = "Location" if lang == "en" else "ప్రాంతం"
        lbl_crop_area = "Crop & Area" if lang == "en" else "పంట & విస్తీర్ణం"
        lbl_sow_date = get_text("sowing_date_label", lang)
        lbl_stage = "Current Growth Stage" if lang == "en" else "ప్రస్తుత ఎదుగుదల దశ"
        lbl_age = get_text("stat_days_in_field", lang)
        lbl_soil = "Soil Type" if lang == "en" else "నేల రకం"
        lbl_water = "Water Source" if lang == "en" else "నీటి వనరు"
        lbl_sync_title = "Twin Synchronization:" if lang == "en" else "డిజిటల్ ట్విన్ సమన్వయం:"
        lbl_sync_body = (
            "All climate risk metrics and AI advisor recommendations in other tabs are synchronized with this plot profile."
            if lang == "en"
            else "వాతావరణ ప్రమాద సూచికలు మరియు ఏఐ సలహాలు ఈ పొలం వివరాలతో సమన్వయం చేయబడ్డాయి."
        )
        lbl_last_updated = "Last updated:" if lang == "en" else "చివరిగా అప్‌డేట్ చేసిన సమయం:"

        soil_dict = {s["en"]: s[lang] for s in SOIL_TYPES}
        irrig_dict = {i["en"]: i[lang] for i in IRRIGATION_SOURCES}
        soil_display = soil_dict.get(soil_val, soil_val)
        irrig_display = irrig_dict.get(irrig_val, irrig_val)
        area_unit = get_text("unit_acres", lang)

        digital_twin_html = (
            '<div style="background: linear-gradient(145deg, #f4f8f5 0%, #e8f3ec 100%); border: 1px solid #c2dbcd; border-radius: 14px; padding: 22px; box-shadow: 0 4px 12px rgba(27,67,50,0.06);">'
            '<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #cce2d5; padding-bottom: 12px; margin-bottom: 16px;">'
            '<div>'
            f'<h4 style="margin: 0; color: #1b4332; font-size: 1.15rem; font-weight: 700;">{twin_heading}</h4>'
            f'<small style="color: #406a52;">{twin_sub}</small>'
            '</div>'
            f'<span style="background-color: #2d6a4f; color: #ffffff; padding: 4px 12px; border-radius: 999px; font-size: 0.78rem; font-weight: 600;">{badge_active}</span>'
            '</div>'
            '<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-bottom: 18px;">'
            '<div style="background: #ffffff; border-radius: 8px; padding: 12px 14px; border: 1px solid #dbe8e0; grid-column: 1 / -1;">'
            f'<div style="color: #557c66; font-size: 0.76rem; font-weight: 600; text-transform: uppercase;">{lbl_loc}</div>'
            f'<div style="color: #1b4332; font-weight: 700; font-size: 0.98rem; margin-top: 3px; word-break: normal; overflow-wrap: break-word; line-height: 1.4;">{loc_display}</div>'
            '</div>'
            '<div style="background: #ffffff; border-radius: 8px; padding: 12px 14px; border: 1px solid #dbe8e0;">'
            f'<div style="color: #557c66; font-size: 0.76rem; font-weight: 600; text-transform: uppercase;">{lbl_crop_area}</div>'
            f'<div style="color: #1b4332; font-weight: 700; font-size: 0.96rem; margin-top: 3px; word-break: normal; overflow-wrap: break-word; line-height: 1.4;">{crop_display} ({area_val:.2f} {area_unit})</div>'
            '</div>'
            '<div style="background: #ffffff; border-radius: 8px; padding: 12px 14px; border: 1px solid #dbe8e0;">'
            f'<div style="color: #557c66; font-size: 0.76rem; font-weight: 600; text-transform: uppercase;">{lbl_sow_date}</div>'
            f'<div style="color: #1b4332; font-weight: 700; font-size: 0.96rem; margin-top: 3px; word-break: normal; overflow-wrap: break-word; line-height: 1.4;">{sow_date_display}</div>'
            '</div>'
            '<div style="background: #ffffff; border-radius: 8px; padding: 12px 14px; border: 1px solid #dbe8e0;">'
            f'<div style="color: #557c66; font-size: 0.76rem; font-weight: 600; text-transform: uppercase;">{lbl_age}</div>'
            f'<div style="color: #1b4332; font-weight: 700; font-size: 0.96rem; margin-top: 3px; word-break: normal; overflow-wrap: break-word; line-height: 1.4;">{crop_age_display}</div>'
            '</div>'
            '<div style="background: #ffffff; border-radius: 8px; padding: 12px 14px; border: 1px solid #dbe8e0;">'
            f'<div style="color: #557c66; font-size: 0.76rem; font-weight: 600; text-transform: uppercase;">{lbl_water}</div>'
            f'<div style="color: #1b4332; font-weight: 700; font-size: 0.96rem; margin-top: 3px; word-break: normal; overflow-wrap: break-word; line-height: 1.4;">{irrig_display}</div>'
            '</div>'
            '<div style="background: #ffffff; border-radius: 8px; padding: 12px 14px; border: 1px solid #dbe8e0; grid-column: 1 / -1;">'
            f'<div style="color: #557c66; font-size: 0.76rem; font-weight: 600; text-transform: uppercase;">{lbl_stage}</div>'
            f'<div style="color: #1b4332; font-weight: 700; font-size: 0.96rem; margin-top: 3px; word-break: normal; overflow-wrap: break-word; line-height: 1.4;">{stage_display}</div>'
            '</div>'
            '<div style="background: #ffffff; border-radius: 8px; padding: 12px 14px; border: 1px solid #dbe8e0; grid-column: 1 / -1;">'
            f'<div style="color: #557c66; font-size: 0.76rem; font-weight: 600; text-transform: uppercase;">{lbl_soil}</div>'
            f'<div style="color: #1b4332; font-weight: 700; font-size: 0.96rem; margin-top: 3px; word-break: normal; overflow-wrap: break-word; line-height: 1.4;">{soil_display}</div>'
            '</div>'
            '</div>'
            '<div style="background-color: #ffffff; border-radius: 8px; padding: 12px 14px; border: 1px solid #dbe8e0; font-size: 0.84rem; color: #2d5a3f; line-height: 1.5;">'
            f'💡 <strong>{lbl_sync_title}</strong> {lbl_sync_body}'
            '</div>'
            '<div style="text-align: right; margin-top: 10px; font-size: 0.76rem; color: #628672;">'
            f'{lbl_last_updated} {last_sync}'
            '</div>'
            '</div>'
        )
        st.markdown(digital_twin_html, unsafe_allow_html=True)

    return st.session_state.farm_profile
