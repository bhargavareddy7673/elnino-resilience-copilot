"""Localization strings for English and Telugu.

Provides bilingual translations for UI elements, labels, messages,
weather intelligence, and system status notes in the El Niño Resilience Co-Pilot.
"""

TRANSLATIONS = {
    # App Header & Metadata
    "app_title": {
        "en": "El Niño Resilience Co-Pilot",
        "te": "ఎల్ నినో స్థితిస్థాపకత కో-పైలట్",
    },
    "app_tagline": {
        "en": "Farm Digital Twin & Multilingual Agricultural Advisor",
        "te": "రైతు డిజిటల్ పొలం & వ్యవసాయ సలహాదారు",
    },
    "app_disclaimer": {
        "en": (
            "Advisory Notice: Weather observations and forecasts are powered by Open-Meteo. "
            "Agricultural indicators provide decision-support guidance; localized field verification is recommended."
        ),
        "te": (
            "సలహా గమనిక: వాతావరణ సమాచారం ఓపెన్-మెటియో ద్వారా అందించబడింది. వ్యవసాయ సూచికలు నిర్ణయ మద్దతు "
            "కోసం ఉద్దేశించినవి; పొలంలో ప్రత్యక్ష పరిశీలన ఎల్లప్పుడూ శ్రేయస్కరం."
        ),
    },

    # Main Navigation
    "nav_home": {
        "en": "Home",
        "te": "హోమ్",
    },
    "nav_farm": {
        "en": "My Farm",
        "te": "నా పొలం",
    },
    "nav_weather": {
        "en": "Weather",
        "te": "వాతావరణం",
    },
    "nav_advisor": {
        "en": "AI Farm Advisor",
        "te": "ఏఐ వ్యవసాయ సలహాదారు",
    },
    "nav_guidance": {
        "en": "Crop Guidance",
        "te": "పంట సాగు సూచనలు",
    },
    "nav_simulator": {
        "en": "What-If Simulator",
        "te": "వాట్-ఇఫ్ సిమ్యులేటర్",
    },
    "nav_enso": {
        "en": "ENSO Outlook",
        "te": "ఎల్ నినో సమాచారం",
    },
    "stage_not_determined": {
        "en": "Not Determined (requires planting date)",
        "te": "నిర్ణయించబడలేదు (విత్తిన తేదీ అవసరం)",
    },
    "sowing_date_not_provided": {
        "en": "Not provided",
        "te": "నమోదు చేయలేదు",
    },

    # Sidebar Navigation & Context
    "language_select_label": {
        "en": "Language / భాష",
        "te": "భాషను ఎంచుకోండి / Language",
    },
    "project_info_title": {
        "en": "About the Project",
        "te": "ప్రాజెక్ట్ గురించి",
    },
    "project_info_desc": {
        "en": (
            "This co-pilot builds a virtual Digital Twin of your farm plot to help "
            "assess seasonal weather risks (such as El Niño-induced dry spells) "
            "and evaluate resilience strategies."
        ),
        "te": (
            "ఈ కో-పైలట్ మీ వ్యవసాయ పొలానికి వర్చువల్ డిజిటల్ ట్విన్‌ను రూపొందించి, "
            "ఎల్ నినో వంటి వాతావరణ మార్పుల సమయంలో పంట రక్షణకు అవసరమైన సలహాలు అందిస్తుంది."
        ),
    },
    "scope_heading": {
        "en": "Project Scope",
        "te": "ప్రాజెక్ట్ పరిధి",
    },
    "scope_details": {
        "en": (
            "• Regions: Andhra Pradesh & Telangana\n"
            "• Default Focus: Kadapa District, AP\n"
            "• Supported Crops: Turmeric, Banana, Paddy"
        ),
        "te": (
            "• ప్రాంతాలు: ఆంధ్రప్రదేశ్ & తెలంగాణ\n"
            "• డెమో కేంద్రం: కడప జిల్లా, ఆంధ్రప్రదేశ్\n"
            "• ఎంపిక చేసిన పంటలు: పసుపు, అరటి, వరి"
        ),
    },
    "system_status": {
        "en": "System Status",
        "te": "వ్యవస్థ స్థితి",
    },
    "digital_twin_ready": {
        "en": "Digital Twin: Active",
        "te": "డిజిటల్ ట్విన్: సిద్ధంగా ఉంది",
    },

    # Tabs
    "tab_profile": {
        "en": "Farm Profile & Digital Twin",
        "te": "రైతు ప్రొఫైల్ & డిజిటల్ ట్విన్",
    },
    "tab_weather": {
        "en": "Regional Climate Intelligence",
        "te": "శీతోష్ణస్థితి నిఘా విభాగం",
    },
    "tab_advisor": {
        "en": "AI Farm Advisor",
        "te": "ఏఐ వ్యవసాయ సలహాదారు",
    },
    "tab_roadmap": {
        "en": "Project Roadmap",
        "te": "ప్రాజెక్ట్ ప్రణాళిక",
    },

    # Farmer Profile Form
    "form_heading": {
        "en": "Farm Profile Configuration",
        "te": "రైతు పొలం వివరాల నమోదు",
    },
    "form_caption": {
        "en": (
            "Enter your farm plot attributes below to initialize or update your Farm Digital Twin. "
            "Default demo settings are pre-filled for Kadapa District, Andhra Pradesh."
        ),
        "te": (
            "మీ వ్యవసాయ పొలానికి డిజిటల్ ట్విన్‌ను ప్రారంభించడానికి లేదా అప్‌డేట్ చేయడానికి వివరాలను నమోదు చేయండి. "
            "ప్రాథమిక వివరాలు వైఎస్ఆర్ కడప జిల్లాకు ఎంపిక చేయబడ్డాయి."
        ),
    },
    "state_label": {
        "en": "State",
        "te": "రాష్ట్రం",
    },
    "district_label": {
        "en": "District",
        "te": "జిల్లా",
    },
    "village_label": {
        "en": "Village / Mandal (Optional)",
        "te": "గ్రామం / మండలం (ఐచ్ఛికం)",
    },
    "village_placeholder": {
        "en": "e.g. Khajipet, Duvvur, Chennur, or leave empty",
        "te": "ఉదాహరణ: ఖాజీపేట, దువ్వూరు, చెన్నూరు లేదా ఖాళీగా ఉంచండి",
    },
    "crop_label": {
        "en": "Crop",
        "te": "పంట ఎంపిక",
    },
    "land_area_label": {
        "en": "Farm Area (Acres)",
        "te": "పొలం విస్తీర్ణం (ఎకరాలలో)",
    },
    "land_area_help": {
        "en": "Enter exact cultivated area in acres (e.g. 0.5, 1.25, 2.75, 4.00)",
        "te": "సాగు విస్తీర్ణాన్ని ఎకరాలలో నమోదు చేయండి (ఉదా: 0.5, 1.25, 2.75, 4.00)",
    },
    "soil_type_label": {
        "en": "Predominant Soil Type",
        "te": "నేల రకం",
    },
    "irrigation_label": {
        "en": "Primary Water / Irrigation Source",
        "te": "ప్రధాన నీటి పారుదల వనరు",
    },
    "sowing_date_label": {
        "en": "Sowing / Plantation Date",
        "te": "విత్తిన / నాటిన తేదీ",
    },
    "submit_button": {
        "en": "Save Farm Profile",
        "te": "వివరాలను భద్రపరచండి",
    },
    "reset_button": {
        "en": "Reset to Demo Defaults",
        "te": "డిఫాల్ట్ వివరాలకు మార్చండి",
    },
    "profile_saved_success": {
        "en": "Farm profile updated successfully. Digital Twin synchronized.",
        "te": "పొలం వివరాలు విజయవంతంగా భద్రపరచబడ్డాయి. డిజిటల్ ట్విన్ అప్‌డేట్ చేయబడింది.",
    },
    "invalid_area_error": {
        "en": "Please enter a valid farm area greater than 0 acres.",
        "te": "దయచేసి 0 కంటే ఎక్కువ పొలం విస్తీర్ణాన్ని నమోదు చేయండి.",
    },

    # Digital Twin Summary Display
    "twin_summary_heading": {
        "en": "Active Farm Digital Twin Snapshot",
        "te": "ప్రస్తుత పొలం డిజిటల్ ట్విన్ సారాంశం",
    },
    "twin_summary_subheading": {
        "en": "Synchronized virtual state representing your farm for resilience assessment",
        "te": "వాతావరణ రిస్క్ అంచనా కోసం మీ వ్యవసాయ భూమి యొక్క ప్రత్యక్ష డిజిటల్ ప్రతిరూపం",
    },
    "metric_location": {
        "en": "Location",
        "te": "ప్రాంతం",
    },
    "metric_crop": {
        "en": "Selected Crop",
        "te": "ఎంచుకున్న పంట",
    },
    "metric_area": {
        "en": "Cultivated Area",
        "te": "సాగు విస్తీర్ణం",
    },
    "metric_days_since_sowing": {
        "en": "Days in Field",
        "te": "పంట కాలం",
    },
    "unit_acres": {
        "en": "Acres",
        "te": "ఎకరాలు",
    },
    "unit_days": {
        "en": "Days",
        "te": "రోజులు",
    },
    "agronomic_heading": {
        "en": "Agronomic Profile",
        "te": "వ్యవసాయ సమాచారం",
    },
    "crop_classification": {
        "en": "Crop Category",
        "te": "పంట వర్గీకరణ",
    },
    "crop_duration": {
        "en": "Growth Duration",
        "te": "మొత్తం పంట కాలం",
    },
    "typical_sowing_window": {
        "en": "Sowing Period",
        "te": "సాధారణ విత్తే కాలం",
    },
    "soil_water_heading": {
        "en": "Soil & Water Profile",
        "te": "నేల మరియు నీటి వనరు",
    },
    "metric_soil": {
        "en": "Soil Structure",
        "te": "నేల రకం",
    },
    "metric_irrigation": {
        "en": "Water Availability",
        "te": "నీటి వనరు",
    },
    "metric_sowing_date": {
        "en": "Sowing Date",
        "te": "నాటిన తేదీ",
    },
    "sync_timestamp_label": {
        "en": "Last Synchronized",
        "te": "చివరిగా అప్‌డేట్ చేసిన సమయం",
    },
    "not_specified": {
        "en": "Not specified",
        "te": "పేర్కొనబడలేదు",
    },

    # --- STAGE 2: CLIMATE INTELLIGENCE & WEATHER ---
    "weather_section_title": {
        "en": "Regional Climate Intelligence",
        "te": "ప్రాంతీయ శీతోష్ణస్థితి నిఘా",
    },
    "weather_section_subtitle": {
        "en": "Atmospheric conditions, 7-day agricultural forecast, and dry-spell risk intelligence",
        "te": "వాతావరణ పరిస్థితులు, 7 రోజుల వ్యవసాయ అంచనాలు మరియు వర్షాభావ రిస్క్ సూచికలు",
    },
    "btn_refresh_weather": {
        "en": "Refresh Weather Data",
        "te": "తాజా వాతావరణం పొందండి",
    },
    "weather_retrieved_at": {
        "en": "Last Weather Sync",
        "te": "వాతావరణం అప్‌డేట్ అయిన సమయం",
    },
    "current_conditions_heading": {
        "en": "Current Atmospheric Conditions",
        "te": "ప్రస్తుత వాతావరణ పరిస్థితులు",
    },
    "curr_temperature": {
        "en": "Temperature",
        "te": "ఉష్ణోగ్రత",
    },
    "curr_humidity": {
        "en": "Relative Humidity",
        "te": "గాలిలో తేమ",
    },
    "curr_wind_speed": {
        "en": "Wind Speed",
        "te": "గాలి వేగం",
    },
    "curr_precipitation": {
        "en": "Current Rain Rate",
        "te": "ప్రస్తుత వర్షం",
    },
    "curr_condition": {
        "en": "Sky Condition",
        "te": "ఆకాశ స్థితి",
    },
    "forecast_heading": {
        "en": "Seven-Day Agricultural Weather Forecast",
        "te": "7 రోజుల వ్యవసాయ వాతావరణ అంచనా",
    },
    "forecast_subheading": {
        "en": "Projected daily maximum/minimum temperatures and expected precipitation volume",
        "te": "రాబోయే వారంలో గరిష్ట/కనిష్ట ఉష్ణోగ్రతలు మరియు వర్షపాత సూచన",
    },
    "recent_rain_heading": {
        "en": "Recent 30-Day Rainfall & Dry Spell Intelligence",
        "te": "గత 30 రోజుల వర్షపాతం & వర్షాభావ వివరాలు",
    },
    "recent_rain_subheading": {
        "en": "Precipitation analysis based on high-resolution meteorological reanalysis (Open-Meteo)",
        "te": "ఓపెన్-మెటియో రీఅనాలిసిస్ మోడలింగ్ ఆధారంగా గత 30 రోజుల వర్షపాత విశ్లేషణ",
    },
    "stat_current_dry_spell": {
        "en": "Current Dry Spell",
        "te": "వర్షాభావ రోజుల సంఖ్య",
    },
    "stat_total_30d_rain": {
        "en": "30-Day Estimated Rain",
        "te": "30 రోజుల అంచనా వర్షపాతం",
    },
    "stat_rainy_days": {
        "en": "Rainy Days (≥2.5mm)",
        "te": "వర్షపు రోజులు (≥2.5మి.మీ)",
    },
    "stat_max_day_rain": {
        "en": "Max Single-Day Rain",
        "te": "గరిష్ట ఒకరోజు వర్షం",
    },
    "indicators_heading": {
        "en": "Agricultural Climate Indicators",
        "te": "వ్యవసాయ శీతోష్ణస్థితి సూచికలు",
    },
    "indicators_subheading": {
        "en": "Rule-based experimental decision-support metrics for seasonal crop management",
        "te": "పంట నిర్వహణ కోసం రూల్-బేస్డ్ ప్రయోగాత్మక సూచికలు",
    },
    "crop_context_heading": {
        "en": "Crop-Specific Climate Vulnerability Context",
        "te": "పంట వారీ వాతావరణ ప్రాముఖ్యత",
    },
    "crop_context_subheading": {
        "en": "Why temperature, moisture regimes, and water availability matter for your selected crop",
        "te": "మీరు ఎంచుకున్న పంటకు ఉష్ణోగ్రత, తేమ మరియు నీటి లభ్యత ఎందుకు ముఖ్యమైనవి",
    },
    "reanalysis_data_notice": {
        "en": (
            "Data Source Note: Historical 30-day rainfall values reflect meteorological operational reanalysis and analysis estimates "
            "from Open-Meteo (~11 km spatial resolution model grid). While providing consistent regional continuous records, "
            "localized physical on-farm rain-gauge observations may vary from gridded estimates."
        ),
        "te": (
            "డేటా మూలం గమనిక: గత 30 రోజుల వర్షపాత వివరాలు ఓపెన్-మెటియో ఆపరేషనల్ రీఅనాలిసిస్ మరియు అనాలిసిస్ మోడల్ "
            "(~11 కి.మీ గ్రిడ్ డేటా) ఆధారంగా అంచనా వేయబడ్డాయి. ఇది స్థిరమైన ప్రాంతీయ వివరాలను అందించినప్పటికీ, "
            "పొలంలో నేరుగా కొలిచే వర్షమాపక రీడింగులతో స్వల్ప వ్యత్యాసాలు ఉండవచ్చు."
        ),
    },
    "attribution_text": {
        "en": (
            "Atmospheric telemetry and reanalysis data provided by Open-Meteo Weather API under Creative Commons Attribution 4.0 "
            "International (CC BY 4.0). Scientific indicators are transparent, rule-based experimental decision-support tools "
            "for academic study and do not represent statutory agricultural warnings."
        ),
        "te": (
            "వాతావరణ సమాచారం మరియు రీఅనాలిసిస్ డేటా ఓపెన్-మెటియో (Open-Meteo) API ద్వారా అందించబడింది (లైసెన్స్: CC BY 4.0). "
            "ఇందులోని సూచికలు విద్యార్థి అధ్యయనం కోసం రూపొందించిన పారదర్శక ప్రయోగాత్మక నమూనాలు మాత్రమే; ఇవి అధికారిక హెచ్చరికలు కావు."
        ),
    },
    "api_error_title": {
        "en": "Live Weather Service Unavailable",
        "te": "వాతావరణ సేవ తాత్కాలికంగా అందుబాటులో లేదు",
    },
    "api_error_desc": {
        "en": (
            "Could not connect to the live Open-Meteo weather endpoint. Simulated or fake values are not substituted. "
            "Please check internet access and click 'Refresh Weather Data'."
        ),
        "te": (
            "ఓపెన్-మెటియో వాతావరణ సర్వర్లతో అనుసంధానం కాలేకపోయింది. కల్పిత వివరాలను మేము చూపించము. "
            "దయచేసి ఇంటర్నెట్ కనెక్షన్‌ని సరిచూసి 'తాజా వాతావరణం పొందండి' బటన్‌ను క్లిక్ చేయండి."
        ),
    },
    "risk_alert": {
        "en": "Alert",
        "te": "తీవ్రం (Alert)",
    },
    "risk_watch": {
        "en": "Watch",
        "te": "ఓ మోస్తరు (Watch)",
    },
    "risk_normal": {
        "en": "Normal / Favorable",
        "te": "సాధారణం / అనుకూలం",
    },
    "risk_insufficient": {
        "en": "Insufficient weather data",
        "te": "వాతావరణ సమాచారం సరిపోదు",
    },
    "stat_days_in_field": {
        "en": "Days in Field",
        "te": "పంట కాలం",
    },
    "not_provided": {
        "en": "Not provided",
        "te": "నమోదు కాలేదు",
    },
    "not_available": {
        "en": "N/A",
        "te": "అందుబాటులో లేదు",
    },
    "home_7d_rain": {
        "en": "7-Day Rain Forecast",
        "te": "7 రోజుల వర్ష సూచన",
    },
    "home_peak_temp": {
        "en": "Peak Temp",
        "te": "గరిష్ట ఉష్ణోగ్రత",
    },
    "source_icar_angrau": {
        "en": "Source: ICAR/ANGRAU Agronomic Guide",
        "te": "ఆధారం: ఐసీఏఆర్ / ఆచార్య ఎన్.జి. రంగా వ్యవసాయ మార్గదర్శకాలు",
    },
    "experimental_badge": {
        "en": "Experimental Indicator",
        "te": "ప్రయోగాత్మక సూచిక",
    },

    # --- STAGE 3: AI FARM ADVISOR ---
    "advisor_tab_title": {
        "en": "Multilingual AI Farm Advisor",
        "te": "బహుభాషా ఏఐ వ్యవసాయ సలహాదారు",
    },
    "advisor_tab_subtitle": {
        "en": "Personalized agronomic intelligence powered by your Farm Digital Twin and Open-Meteo telemetry",
        "te": "మీ ఫార్మ్ డిజిటల్ ట్విన్ మరియు ఓపెన్-మెటియో వాతావరణం ఆధారిత వ్యక్తిగత సలహాదారు",
    },
    "btn_clear_chat": {
        "en": "Clear Conversation",
        "te": "చాట్ క్లియర్ చేయండి",
    },
    "quick_questions_title": {
        "en": "Quick Suggested Prompts",
        "te": "త్వరిత ప్రశ్నలు",
    },
    "chat_input_placeholder": {
        "en": "Ask about weather, rainfall forecast, crop precautions, or water stress...",
        "te": "వాతావరణం, వర్ష సూచన, పంట జాగ్రత్తలు లేదా నీటి కొరత గురించి అడగండి...",
    },
    "grounding_details_title": {
        "en": "View Grounding Data & References",
        "te": "విశ్లేషణకు ఉపయోగించిన వాస్తవ వివరాలు & ఆధారాలు",
    },
    "more_suggestions": {
        "en": "More Suggested Questions",
        "te": "మరిన్ని ప్రశ్నలు",
    },
    "advisor_analyzing": {
        "en": "AI Advisor is analyzing farm conditions and weather telemetry...",
        "te": "వ్యవసాయ సలహాదారు విశ్లేషిస్తున్నారు...",
    },

    # --- HOME VIEW ---
    "home_greeting": {
        "en": "Welcome, Farmer",
        "te": "నమస్కారం, రైతు మిత్రమా",
    },
    "home_subtitle": {
        "en": "Your plot's live digital twin and agricultural climate companion",
        "te": "మీ పొలం ప్రత్యక్ష డిజిటల్ చిత్రం మరియు వాతావరణ సలహాదారు",
    },
    "home_weather_overview": {
        "en": "Current Weather Snapshot",
        "te": "ప్రస్తుత వాతావరణ ముఖ్యాంశాలు",
    },
    "home_farm_summary": {
        "en": "Farm Plot Attributes",
        "te": "మీ పొలం వివరాలు",
    },
    "home_quick_actions": {
        "en": "Quick Actions",
        "te": "త్వరిత ఎంపికలు",
    },
    "home_alerts_title": {
        "en": "Active Crop Alerts & Indicators",
        "te": "పంట హెచ్చరికలు & వాతావరణ సూచికలు",
    },
    "home_advice_card": {
        "en": "Personalized Farm Advisory",
        "te": "వ్యక్తిగత సాగు సలహా",
    },
    "btn_ask_advisor": {
        "en": "Chat with AI Advisor",
        "te": "ఏఐ సలహాదారుని అడగండి",
    },
    "btn_view_weather": {
        "en": "7-Day Forecast & Rain",
        "te": "7 రోజుల వాతావరణం & వర్షం",
    },
    "btn_edit_farm": {
        "en": "Update Farm Profile",
        "te": "పొలం వివరాలు మార్చండి",
    },
    "btn_crop_guide": {
        "en": "Explore Crop Guide",
        "te": "పంట సాగు మెళకువలు",
    },

    # --- CROP GUIDANCE VIEW ---
    "guidance_title": {
        "en": "Crop Cultivation & Resilience Guide",
        "te": "పంట సాగు & వాతావరణ రక్షణ మార్గదర్శి",
    },
    "guidance_subtitle": {
        "en": "Authoritative agronomic package of practices, phenological stages, and climate contingency measures",
        "te": "ప్రామాణిక వ్యవసాయ పద్ధతులు, పంట ఎదుగుదల దశలు మరియు వాతావరణ రక్షణ చర్యలు",
    },
    "crop_overview_heading": {
        "en": "Crop Physiological Baseline",
        "te": "పంట ప్రాథమిక లక్షణాలు",
    },
    "crop_stages_heading": {
        "en": "Growth Stages & Water Requirements",
        "te": "పంట దశలు & నీటి అవసరాలు",
    },
    "crop_resilience_heading": {
        "en": "Recommended Agronomic Resilience Practices",
        "te": "పంట రక్షణ & యాజమాన్య పద్ధతులు",
    },
    "institutional_sources_heading": {
        "en": "Authoritative Research References",
        "te": "అధికారిక వ్యవసాయ పరిశోధనా ఆధారాలు",
    },

    # Roadmap Section
    "roadmap_heading": {
        "en": "Project Development Stages",
        "te": "ప్రాజెక్ట్ ప్రణాళిక & దశలు",
    },

    # --- WHAT-IF SIMULATOR VIEW ---
    "simulator_tab_title": {
        "en": "What-If Climate Scenario Simulator",
        "te": "వాతావరణ మార్పుల వాట్-ఇఫ్ సిమ్యులేటర్",
    },
    "simulator_tab_subtitle": {
        "en": "Interactive stress-testing of drought, thermal elevation, and irrigation constraints on your farm plot.",
        "te": "వర్షాభావం, అధిక ఉష్ణోగ్రతలు మరియు నీటి ఎద్దడి మీ పంటపై చూపే ప్రభావాన్ని ముందస్తుగా అంచనా వేయండి.",
    },
    "simulator_controls_heading": {
        "en": "Scenario Inputs & Parameters",
        "te": "సిమ్యులేషన్ నియంత్రణలు & కొలమానాలు",
    },
    "simulator_comparison_heading": {
        "en": "Comparative Multi-Scenario Assessment",
        "te": "4 విభిన్న పరిస్థితుల సమగ్ర పోలిక",
    },
    "slider_rain_reduction": {
        "en": "Rainfall Reduction (% drop)",
        "te": "వర్షపాతం తగ్గుదల (%)",
    },
    "slider_temp_increase": {
        "en": "Temperature Elevation (°C increase)",
        "te": "ఉష్ణోగ్రత పెరుగుదల (°C)",
    },
    "radio_irrigation_status": {
        "en": "Irrigation Availability",
        "te": "నీటి పారుదల సౌకర్యం",
    },
    "radio_duration_days": {
        "en": "Scenario Duration",
        "te": "సిమ్యులేషన్ కాలపరిమితి",
    },
    "irr_normal": {
        "en": "Normal (100% capacity)",
        "te": "సాధారణం (100% లభ్యం)",
    },
    "irr_limited": {
        "en": "Limited (50% rationing)",
        "te": "పరిమితం (50% కొరత)",
    },
    "irr_unavailable": {
        "en": "Unavailable (0% - Rainfed)",
        "te": "నిలిచిపోయింది (0% - వర్షాధారం)",
    },
    "card_water_satisfaction": {
        "en": "Water Satisfaction Ratio",
        "te": "నీటి సంతృప్తి శాతం",
    },
    "card_net_deficit": {
        "en": "Net Moisture Deficit",
        "te": "నికర నీటి లోటు",
    },
    "card_thermal_peak": {
        "en": "Scenario Peak Temperature",
        "te": "గరిష్ట ఉష్ణోగ్రత",
    },
    "card_composite_risk": {
        "en": "Multi-Factor Risk Status",
        "te": "సమగ్ర రిస్క్ స్థాయి",
    },
    "btn_ask_advisor_sim": {
        "en": "Ask AI Advisor about this Scenario",
        "te": "ఈ పరిస్థితి గురించి ఏఐ సలహాదారుని అడగండి",
    },
    "simulator_disclaimer": {
        "en": (
            "Decision-Support Notice: The What-If Simulator executes rule-based sensitivity stress testing "
            "grounded in ICAR/ANGRAU physiological baselines and Open-Meteo operational grids. "
            "It serves to illustrate relative vulnerability and does NOT predict absolute harvest yields or grain loss."
        ),
        "te": (
            "నిర్ణయ మద్దతు గమనిక: వాట్-ఇఫ్ సిమ్యులేటర్ వ్యవసాయ పరిశోధనా పరిమితుల (ICAR/ANGRAU) ఆధారంగా "
            "వివిధ వాతావరణ ఒత్తిడుల తీవ్రతను ముందస్తుగా అంచనా వేస్తుంది. ఇది నిర్ణయ మద్దతు కొరకు మాత్రమే, "
            "ఖచ్చితమైన దిగుబడి నష్టాన్ని నిర్ధారించదు."
        ),
    },

    # Future Weather Planning & Forecast Boundary
    "future_planner_heading": {
        "en": "Future Weather Explorer & Farm Planning Desk",
        "te": "భవిష్యత్ వాతావరణ అన్వేషణ & వ్యవసాయ ప్రణాళిక",
    },
    "future_planner_subheading": {
        "en": "Select an upcoming date within the 16-day numerical forecast horizon to plan irrigation, spraying, and field operations",
        "te": "నీటి తడులు, మందుల పిచికారీ మరియు సాగు పనులను ప్లాన్ చేసుకోవడానికి 16 రోజుల సూచన పరిధిలో ఒక తేదీని ఎంచుకోండి",
    },
    "future_date_picker_label": {
        "en": "Select Target Planning Date",
        "te": "సాగు ప్రణాళిక తేదీని ఎంచుకోండి",
    },
    "future_date_picker_help": {
        "en": "Open-Meteo NWP models support deterministic daily forecasts up to 16 days ahead. Past dates display operational reanalysis.",
        "te": "ఓపెన్-మెటియో నమూనాలు రాబోయే 16 రోజుల వరకు సూచనలను అందిస్తాయి. గత తేదీలు రీఅనాలిసిస్ రికార్డులను చూపుతాయి.",
    },
    "planning_irrigation_guidance": {
        "en": "Irrigation Guidance",
        "te": "నీటి పారుదల సూచన",
    },
    "planning_spray_guidance": {
        "en": "Spraying & Fertilizer Guidance",
        "te": "పిచికారీ & ఎరువుల యాజమాన్యం",
    },
    "planning_confidence_label": {
        "en": "Forecast Confidence",
        "te": "సూచన విశ్వసనీయత",
    },
    "planning_crop_stage_label": {
        "en": "Active Crop Stage",
        "te": "ప్రస్తుత పంట దశ",
    },
    "planning_heat_risk_label": {
        "en": "Thermal Regime",
        "te": "ఉష్ణోగ్రత స్థితి",
    },
    "planning_rain_risk_label": {
        "en": "Precipitation Outlook",
        "te": "వర్షపాత సూచన",
    },
    "planning_beyond_horizon_title": {
        "en": "Date Exceeds 16-Day Forecast Horizon",
        "te": "తేదీ 16 రోజుల సూచన పరిమితిని మించింది",
    },
    "btn_open_simulator_for_date": {
        "en": "🔮 Stress-Test in What-If Simulator",
        "te": "🔮 వాట్-ఇఫ్ సిమ్యులేటర్‌లో పరిశీలించండి",
    },
    "btn_refresh_live_weather": {
        "en": "🔄 Retry Live Open-Meteo Connection",
        "te": "🔄 ప్రత్యక్ష వాతావరణాన్ని మళ్లీ ప్రయత్నించండి",
    },
    "weather_vs_simulator_title": {
        "en": "Weather Forecast vs. What-If Simulator: Understanding the Boundary",
        "te": "వాతావరణ సూచన vs వాట్-ఇఫ్ సిమ్యులేటర్: వ్యత్యాసాల అవగాహన",
    },
    "weather_vs_simulator_desc": {
        "en": (
            "Deterministic Numerical Weather Prediction (NWP) models (Open-Meteo, ECMWF, GFS) are scientifically constrained "
            "to a 16-day forecast horizon due to atmospheric chaotic divergence. Beyond 16 days, day-to-day deterministic forecasts cannot be generated. "
            "For 30, 60, or 90-day seasonal risk management, use the What-If Simulator, which tests physiological crop resilience under hypothetical climate scenarios."
        ),
        "te": (
            "వాతావరణ నమూనాలు (ఓపెన్-మెటియో మొదలైనవి) వాతావరణ శాస్త్ర పరిమితుల దృష్ట్యా గరిష్టంగా 16 రోజుల వరకు మాత్రమే ఖచ్చితమైన రోజువారీ అంచనాలను ఇవ్వగలవు. "
            "16 రోజుల తర్వాత నిర్దిష్ట రోజువారీ వాతావరణాన్ని అంచనా వేయడం సాధ్యం కాదు. "
            "30, 60 లేదా 90 రోజుల దీర్ఘకాలిక ప్రణాళిక కొరకు 'వాట్-ఇఫ్ సిమ్యులేటర్' ఉపయోగించి వివిధ వర్షాభావ మరియు అధిక ఉష్ణోగ్రత పరిస్థితులను పరిశీలించండి."
        ),
    },
    "forecast_16day_summary_heading": {
        "en": "16-Day Outlook & Dry Spell Projection",
        "te": "16 రోజుల ముందస్తు వాతావరణ సమగ్ర సమాచారం",
    },
    "forecast_16day_summary_subheading": {
        "en": "Aggregate precipitation and consecutive dry day projection across the 16-day horizon",
        "te": "రాబోయే 16 రోజులలో మొత్తం వర్షపాతం మరియు వర్షాభావ రోజుల సూచన",
    },
    "view_days_8_to_16_expander": {
        "en": "📊 View Extended Forecast: Days 8 to 16 (Indicative Trend)",
        "te": "📊 8 నుండి 16 రోజుల పొడిగించిన సూచనను వీక్షించండి (సూచనాప్రాయం)",
    },
}


def get_text(key: str, lang: str = "en") -> str:
    """Retrieve translated text string by key for the specified language.
    
    Falls back to English if the key or language translation is not found.
    """
    entry = TRANSLATIONS.get(key, {})
    return entry.get(lang, entry.get("en", key))
