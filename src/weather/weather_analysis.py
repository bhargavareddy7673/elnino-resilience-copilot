"""Agricultural weather analytics and scientifically consistent rule-based indicators.

Analyzes temperature regimes, dry spells, rainfall availability, and crop-specific
physiological sensitivities for smallholder farmers in AP and Telangana.
"""

from typing import Dict, Any, List, Optional
import pandas as pd


def compute_dry_spell_metrics(historical_df: Optional[pd.DataFrame]) -> Dict[str, Any]:
    """Calculate dry spell characteristics from the recent 30-day precipitation history.
    
    A dry day is defined as precipitation < 1.0 mm (standard meteorological dry day).
    A rainy day is defined as precipitation >= 2.5 mm (standard IMD definition).
    Missing values in the precipitation series are omitted from contiguous run calculations.
    """
    if historical_df is None or historical_df.empty or "precipitation" not in historical_df.columns:
        return {
            "is_valid": False,
            "current_consecutive_dry_days": 0,
            "total_30d_rainfall": 0.0,
            "rainy_days_count": 0,
            "max_single_day_rain": 0.0,
            "longest_dry_spell_30d": 0,
            "missing_days_count": 0,
            "total_records": 0,
        }

    # Handle missing / null precipitation records cleanly
    precip_col = historical_df["precipitation"]
    missing_count = int(precip_col.isna().sum())
    valid_df = historical_df.dropna(subset=["precipitation"])

    if valid_df.empty:
        return {
            "is_valid": False,
            "current_consecutive_dry_days": 0,
            "total_30d_rainfall": 0.0,
            "rainy_days_count": 0,
            "max_single_day_rain": 0.0,
            "longest_dry_spell_30d": 0,
            "missing_days_count": missing_count,
            "total_records": len(historical_df),
        }

    precip_series = valid_df["precipitation"].tolist()
    total_rain = round(float(valid_df["precipitation"].sum()), 1)
    rainy_days = int((valid_df["precipitation"] >= 2.5).sum())
    max_rain = round(float(valid_df["precipitation"].max()), 1) if precip_series else 0.0

    # 1. Current contiguous dry days (< 1.0 mm) scanning backwards from latest available day
    current_dry = 0
    for val in reversed(precip_series):
        if val < 1.0:
            current_dry += 1
        else:
            break

    # 2. Longest contiguous dry spell in window
    longest_dry = 0
    temp_run = 0
    for val in precip_series:
        if val < 1.0:
            temp_run += 1
            if temp_run > longest_dry:
                longest_dry = temp_run
        else:
            temp_run = 0

    return {
        "is_valid": True,
        "current_consecutive_dry_days": current_dry,
        "total_30d_rainfall": total_rain,
        "rainy_days_count": rainy_days,
        "max_single_day_rain": max_rain,
        "longest_dry_spell_30d": longest_dry,
        "missing_days_count": missing_count,
        "total_records": len(historical_df),
    }


def evaluate_climate_indicators(
    forecast_df: Optional[pd.DataFrame] = None,
    historical_df: Optional[pd.DataFrame] = None,
    farm_profile: Optional[Dict[str, Any]] = None,
    current_temp: Optional[float] = None,
    lang: str = "en",
    **kwargs: Any,
) -> List[Dict[str, Any]]:
    """Generate transparent, scientifically consistent agricultural climate indicators.
    
    Ensures:
    1. Thermal stress logic accurately reflects the actual max temperature without contradictions.
    2. Current temperature is displayed separately from 7-day forecast peak.
    3. Rainfall availability distinguishes atmospheric accumulation from crop water demand.
    4. Dry spell avoids unsupported soil moisture claims.
    5. Reanalysis estimates are clearly labeled as model estimates, not ground rain gauges.
    6. If input data is missing or invalid, status is marked as 'Insufficient weather data'.
    """
    if forecast_df is None:
        forecast_df = pd.DataFrame()
    if historical_df is None:
        historical_df = pd.DataFrame()
    if farm_profile is None:
        farm_profile = {}
    if current_temp is None:
        current_temp = kwargs.get("curr_temp", kwargs.get("temp", kwargs.get("temperature")))

    dry_metrics = compute_dry_spell_metrics(historical_df)
    soil_type = farm_profile.get("soil_type", "Red Sandy Loam")
    irrigation = farm_profile.get("irrigation", "Borewell / Groundwater")
    crop = farm_profile.get("crop", "Turmeric")

    indicators = []

    # =========================================================================
    # INDICATOR 1: THERMAL REGIME & HEAT CONDITIONS
    # =========================================================================
    has_forecast_temps = (
        forecast_df is not None
        and not forecast_df.empty
        and "temp_max" in forecast_df.columns
        and forecast_df["temp_max"].dropna().shape[0] > 0
    )

    if not has_forecast_temps:
        indicators.append({
            "id": "heat_stress",
            "name_en": "Thermal Regime & Heat Conditions",
            "name_te": "ఉష్ణోగ్రత పరిస్థితులు మరియు తాపం",
            "risk_level": "Insufficient Data",
            "risk_level_display": "వాతావరణ సమాచారం సరిపోదు" if lang == "te" else "Insufficient weather data",
            "data_used_en": "7-day forecast maximum temperatures",
            "data_used_te": "7 రోజుల గరిష్ట ఉష్ణోగ్రత అంచనా",
            "method_en": "Continuous temperature monitoring over 7-day forecast window",
            "method_te": "7 రోజుల ఉష్ణోగ్రత అంచనాల పరిశీలన",
            "explanation": (
                "వాతావరణ సమాచారం సరిపోదు. గరిష్ట ఉష్ణోగ్రత అంచనా వివరాలు అందుబాటులో లేవు."
                if lang == "te"
                else "Insufficient weather data. Forecast maximum temperature data is currently unavailable to compute thermal load."
            ),
            "is_experimental": True,
        })
    else:
        valid_max_temps = [float(t) for t in forecast_df["temp_max"].dropna().tolist()]
        peak_forecast_temp = max(valid_max_temps)
        min_forecast_max = min(valid_max_temps)
        days_above_38 = sum(1 for t in valid_max_temps if t >= 38.0)
        days_above_35 = sum(1 for t in valid_max_temps if t >= 35.0)

        curr_temp_str = f"{current_temp:.1f}°C" if current_temp is not None else "N/A"

        # Classification without contradictions
        if days_above_38 >= 3 or peak_forecast_temp >= 40.0:
            heat_risk = "Alert"
            heat_risk_display = "తీవ్రం (Alert)" if lang == "te" else "Alert"
            heat_desc_en = (
                f"Sustained high temperatures forecast: Peak daily maximum is projected at {peak_forecast_temp:.1f}°C, "
                f"with {days_above_38} of 7 days reaching or exceeding 38.0°C (Current temperature: {curr_temp_str}). "
                f"Prolonged heat accelerates canopy transpiration and soil surface drying."
            )
            heat_desc_te = (
                f"తీవ్రమైన ఉష్ణోగ్రతలు నమోదయ్యే అవకాశం: రాబోయే 7 రోజుల్లో గరిష్ట ఉష్ణోగ్రత {peak_forecast_temp:.1f}°C వరకు "
                f"చేరుకోనుండగా, {days_above_38} రోజులు 38.0°C దాటవచ్చు (ప్రస్తుత ఉష్ణోగ్రత: {curr_temp_str}). "
                f"ఈ వేడి వల్ల పంట ఆకుల నుండి నీటి ఆవిరి వేగవంతమవుతుంది."
            )
        elif days_above_35 >= 2 or peak_forecast_temp >= 38.0:
            heat_risk = "Watch"
            heat_risk_display = "ఓ మోస్తరు (Watch)" if lang == "te" else "Watch"
            heat_desc_en = (
                f"Elevated temperatures forecast: Peak daily maximum reaches {peak_forecast_temp:.1f}°C, "
                f"with {days_above_35} of 7 days forecast at or above 35.0°C (Current temperature: {curr_temp_str}). "
                f"Thermal conditions are warmer than average; monitor canopy hydration during peak afternoon hours."
            )
            heat_desc_te = (
                f"సాధారణం కంటే ఎక్కువ ఉష్ణోగ్రతలు: రాబోయే వారంలో గరిష్ట ఉష్ణోగ్రత {peak_forecast_temp:.1f}°C గా నమోదయ్యే సూచన ఉంది, "
                f"ఇందులో {days_above_35} రోజులు 35.0°C దాటవచ్చు (ప్రస్తుత ఉష్ణోగ్రత: {curr_temp_str}). "
                f"మధ్యాహ్న సమయాల్లో పంట తేమ కోల్పోకుండా గమనించాలి."
            )
        elif days_above_35 == 1:
            heat_risk = "Watch"
            heat_risk_display = "ఓ మోస్తరు (Watch)" if lang == "te" else "Watch"
            heat_desc_en = (
                f"Transient elevated temperature: Forecast daily maximum reaches a peak of {peak_forecast_temp:.1f}°C on 1 day, "
                f"while the remaining 6 days stay between {min_forecast_max:.1f}°C and 34.9°C (Current temperature: {curr_temp_str}). "
                f"Brief daytime heating observed; adverse impacts depend on developmental stage and irrigation status."
            )
            heat_desc_te = (
                f"స్వల్పకాలిక గరిష్ట ఉష్ణోగ్రత: 7 రోజుల్లో కేవలం 1 రోజు గరిష్టంగా {peak_forecast_temp:.1f}°C నమోదయ్యే అవకాశం ఉండగా, "
                f"మిగిలిన 6 రోజులు {min_forecast_max:.1f}°C నుండి 34.9°C మధ్య ఉంటాయి (ప్రస్తుత ఉష్ణోగ్రత: {curr_temp_str}). "
                f"ఇది స్వల్పకాలిక వేడి మాత్రమే; పంట దశను బట్టి జాగ్రత్తలు అవసరం."
            )
        else:
            heat_risk = "Normal"
            heat_risk_display = "సాధారణం (Normal)" if lang == "te" else "Normal"
            heat_desc_en = (
                f"Moderate temperature regime: All 7 forecast days remain between {min_forecast_max:.1f}°C and {peak_forecast_temp:.1f}°C, "
                f"consistently below 35.0°C (Current temperature: {curr_temp_str}). "
                f"Forecast thermal conditions fall within typical vegetative tolerance for regional crops."
            )
            heat_desc_te = (
                f"అనుకూలమైన ఉష్ణోగ్రతలు: రాబోయే 7 రోజులలో గరిష్ట ఉష్ణోగ్రతలు {min_forecast_max:.1f}°C నుండి {peak_forecast_temp:.1f}°C లోపే "
                f"(35.0°C కంటే తక్కువగా) నమోదవుతాయి (ప్రస్తుత ఉష్ణోగ్రత: {curr_temp_str}). "
                f"పంట పెరుగుదలకు ఉష్ణోగ్రత సాధారణ పరిధిలోనే ఉంది."
            )

        indicators.append({
            "id": "heat_stress",
            "name_en": "Thermal Regime & Heat Conditions",
            "name_te": "ఉష్ణోగ్రత పరిస్థితులు మరియు తాపం",
            "risk_level": heat_risk,
            "risk_level_display": heat_risk_display,
            "data_used_en": (
                f"Current Temp: {curr_temp_str} | 7-day forecast peak max: {peak_forecast_temp:.1f}°C "
                f"({days_above_35} days ≥35°C, {days_above_38} days ≥38°C)"
            ),
            "data_used_te": (
                f"ప్రస్తుత ఉష్ణోగ్రత: {curr_temp_str} | 7 రోజుల గరిష్ట అంచనా: {peak_forecast_temp:.1f}°C "
                f"({days_above_35} రోజులు ≥35°C, {days_above_38} రోజులు ≥38°C)"
            ),
            "method_en": (
                "Experimental meteorological thresholding: Alert if ≥3 days ≥38°C or peak ≥40°C; "
                "Watch if peak ≥35°C; Normal if all days <35°C. Note: Crop damage thresholds vary by species & flowering stage."
            ),
            "method_te": (
                "ప్రయోగాత్మక వాతావరణ వర్గీకరణ: ≥3 రోజులు ≥38°C లేదా గరిష్టం ≥40°C అయితే అలర్ట్; "
                "గరిష్టం ≥35°C అయితే వాచ్; అన్ని రోజులు <35°C అయితే సాధారణం. గమనిక: పంట దశను బట్టి ఉష్ణోగ్రత ప్రభావం మారుతుంది."
            ),
            "explanation": heat_desc_te if lang == "te" else heat_desc_en,
            "is_experimental": True,
        })

    # =========================================================================
    # INDICATOR 2: OBSERVED DRY SPELL DURATION
    # =========================================================================
    if not dry_metrics.get("is_valid", False):
        indicators.append({
            "id": "dry_spell",
            "name_en": "Recent Dry Spell Duration",
            "name_te": "వర్షాభావ రోజుల వ్యవధి",
            "risk_level": "Insufficient Data",
            "risk_level_display": "వాతావరణ సమాచారం సరిపోదు" if lang == "te" else "Insufficient weather data",
            "data_used_en": "Historical precipitation series",
            "data_used_te": "గత వర్షపాత డేటా",
            "method_en": "Contiguous days calculation with precipitation < 1.0 mm",
            "method_te": "రోజువారీ వర్షం < 1.0 మి.మీ ఉన్న వరుస రోజుల గణన",
            "explanation": (
                "వాతావరణ సమాచారం సరిపోదు. వర్షాభావ విశ్లేషణకు అవసరమైన గత వర్షపాత సమాచారం అందుబాటులో లేదు."
                if lang == "te"
                else "Insufficient weather data. Historical daily rainfall data is insufficient to compute dry-spell duration."
            ),
            "is_experimental": True,
        })
    else:
        current_dry_days = dry_metrics["current_consecutive_dry_days"]
        missing_note_en = f" ({dry_metrics['missing_days_count']} missing days omitted)" if dry_metrics["missing_days_count"] > 0 else ""
        missing_note_te = f" ({dry_metrics['missing_days_count']} రోజుల డేటా లోపించింది)" if dry_metrics["missing_days_count"] > 0 else ""

        if current_dry_days >= 14:
            dry_risk = "Alert"
            dry_risk_display = "తీవ్రం (Alert)" if lang == "te" else "Alert"
            dry_desc_en = (
                f"Extended dry run observed: {current_dry_days} consecutive days with estimated daily rainfall below 1.0 mm "
                f"in meteorological reanalysis{missing_note_en}. An extended absence of rain increases crop dependency on irrigation. "
                f"(Note: Actual soil moisture depletion depends on soil texture, root depth, and antecedent rain, not dry days alone.)"
            )
            dry_desc_te = (
                f"సుదీర్ఘ వర్షాభావ కాలం: వాతావరణ రీఅనాలిసిస్ ప్రకారం గత {current_dry_days} రోజులుగా రోజువారీ వర్షం 1.0 మి.మీ కంటే తక్కువగా ఉంది{missing_note_te}. "
                f"వర్షం లేని రోజులు పెరిగేకొద్దీ పంట నీటి తడులపైనే ఆధారపడాల్సి వస్తుంది. "
                f"(గమనిక: నేలలోని వాస్తవ తేమ నేల రకం, వేరు లోతు మరియు పంట నీటి వాడకంపై ఆధారపడి ఉంటుంది.)"
            )
        elif current_dry_days >= 7:
            dry_risk = "Watch"
            dry_risk_display = "ఓ మోస్తరు (Watch)" if lang == "te" else "Watch"
            dry_desc_en = (
                f"Moderate dry interval observed: {current_dry_days} consecutive days with daily rainfall below 1.0 mm{missing_note_en}. "
                f"Evaporative moisture loss continues; check soil surface condition and plan next irrigation accordingly."
            )
            dry_desc_te = (
                f"మోస్తరు వర్షాభావ వ్యవధి: గత {current_dry_days} రోజులుగా రోజువారీ వర్షం 1.0 మి.మీ కంటే తక్కువగా నమోదైంది{missing_note_te}. "
                f"నేలలోని తేమ క్రమంగా తగ్గుతుంటుంది; పొలంలో పదును గమనించి తదుపరి తడికి సిద్ధం కావాలి."
            )
        else:
            dry_risk = "Normal"
            dry_risk_display = "సాధారణం (Normal)" if lang == "te" else "Normal"
            dry_desc_en = (
                f"Recent rainfall event observed in reanalysis: {current_dry_days} days since the last estimated rainfall event (≥1.0 mm){missing_note_en}. "
                f"No extended meteorological dry spell is currently active. "
                f"(Note: A brief rain event does not guarantee long-term root-zone moisture stability across all soil profiles.)"
            )
            dry_desc_te = (
                f"ఇటీవలే వర్షపాతం అంచనా నమోదైంది: రీఅనాలిసిస్ ప్రకారం చివరి వర్షం (≥1.0 మి.మీ) పడి {current_dry_days} రోజులు మాత్రమే అయ్యింది{missing_note_te}. "
                f"ప్రస్తుతానికి సుదీర్ఘ వర్షాభావ పరిస్థితి లేదు. "
                f"(గమనిక: స్వల్ప వర్షం పడినంత మాత్రాన అన్ని నేలల్లో తేమ ఎక్కువ కాలం నిల్వ ఉంటుందని చెప్పలేము.)"
            )

        indicators.append({
            "id": "dry_spell",
            "name_en": "Recent Dry Spell Duration",
            "name_te": "వర్షాభావ రోజుల వ్యవధి",
            "risk_level": dry_risk,
            "risk_level_display": dry_risk_display,
            "data_used_en": f"Past 30-day reanalysis history: {current_dry_days} contiguous dry days (< 1.0 mm/day)",
            "data_used_te": f"గత 30 రోజుల రీఅనాలిసిస్ చరిత్ర: వరుసగా {current_dry_days} వర్షాభావ రోజులు (< 1.0 మి.మీ/రోజు)",
            "method_en": "Standard meteorological dry-day criterion (<1.0 mm rain): Alert if ≥14 days; Watch if ≥7 days; Normal if <7 days",
            "method_te": "వాతావరణ ప్రమాణం (<1.0 మి.మీ వర్షం): ≥14 రోజులు అయితే అలర్ట్; ≥7 రోజులు అయితే వాచ్; <7 రోజులు అయితే సాధారణం",
            "explanation": dry_desc_te if lang == "te" else dry_desc_en,
            "is_experimental": True,
        })

    # =========================================================================
    # INDICATOR 3: 30-DAY CUMULATIVE RAINFALL & MOISTURE AVAILABILITY
    # =========================================================================
    if not dry_metrics.get("is_valid", False):
        indicators.append({
            "id": "rainfall_availability",
            "name_en": "Cumulative Rainfall & Moisture Availability",
            "name_te": "సంచిత వర్షపాతం మరియు తేమ లభ్యత",
            "risk_level": "Insufficient Data",
            "risk_level_display": "వాతావరణ సమాచారం సరిపోదు" if lang == "te" else "Insufficient weather data",
            "data_used_en": "Historical 30-day precipitation series",
            "data_used_te": "గత 30 రోజుల వర్షపాత డేటా",
            "method_en": "30-day cumulative precipitation and distribution evaluation",
            "method_te": "30 రోజుల సంచిత వర్షపాతం మరియు వర్షపు రోజుల విశ్లేషణ",
            "explanation": (
                "వాతావరణ సమాచారం సరిపోదు. సంచిత వర్షపాత విశ్లేషణకు డేటా అందుబాటులో లేదు."
                if lang == "te"
                else "Insufficient weather data. Historical rainfall data is insufficient to compute cumulative precipitation availability."
            ),
            "is_experimental": True,
        })
    else:
        total_30d_rain = dry_metrics["total_30d_rainfall"]
        rainy_days_count = dry_metrics["rainy_days_count"]
        max_day_rain = dry_metrics["max_single_day_rain"]
        forecast_rain_sum = (
            round(float(forecast_df["precipitation"].sum()), 1)
            if not forecast_df.empty and "precipitation" in forecast_df.columns
            else 0.0
        )

        is_rainfed = "Rainfed" in irrigation
        is_high_water_crop = crop in ["Paddy", "Banana"]

        if total_30d_rain < 15.0:
            rain_risk = "Alert"
            rain_risk_display = "తీవ్ర లోటు (Alert)" if lang == "te" else "Alert"
            rain_desc_en = (
                f"Severe cumulative rainfall deficit: Estimated 30-day cumulative rainfall is only {total_30d_rain:.1f} mm "
                f"across {rainy_days_count} rainy days (Open-Meteo reanalysis). Upcoming 7-day forecast indicates {forecast_rain_sum:.1f} mm rain. "
                f"This volume is critically below vegetative evapotranspiration requirements; rainfed plots face high hydrological deficit, "
                f"while plots with {irrigation} depend entirely on irrigation reserves."
            )
            rain_desc_te = (
                f"తీవ్ర సంచిత వర్షపాత లోటు: రీఅనాలిసిస్ ప్రకారం గత 30 రోజులలో కేవలం {total_30d_rain:.1f} మి.మీ వర్షం మాత్రమే నమోదైంది "
                f"({rainy_days_count} వర్షపు రోజులు). వచ్చే 7 రోజుల్లో {forecast_rain_sum:.1f} మి.మీ వర్ష సూచన ఉంది. "
                f"ఈ వర్షపాతం పంట నీటి అవసరాలకు ఏమాత్రం సరిపోదు; వర్షాధార పంటలకు తీవ్ర లోటు ఉండగా, "
                f"{irrigation} ఉన్న పొలాలు పూర్తిగా నీటి వనరులపైనే ఆధారపడాలి."
            )
        elif total_30d_rain < 60.0:
            rain_risk = "Watch"
            rain_risk_display = "ఓ మోస్తరు లోటు (Watch)" if lang == "te" else "Watch"
            rain_desc_en = (
                f"Moderate rainfall accumulation: Estimated 30-day cumulative rainfall is {total_30d_rain:.1f} mm over {rainy_days_count} rainy days, "
                f"with {forecast_rain_sum:.1f} mm projected in the next 7 days. "
                f"While providing transient surface wetting, {total_30d_rain:.1f} mm remains substantially below monthly water requirements for {crop}. "
                f"Supplementary irrigation with {irrigation} is necessary to sustain crop development."
            )
            rain_desc_te = (
                f"ఓ మోస్తరు సంచిత వర్షపాతం: గత 30 రోజులలో {total_30d_rain:.1f} మి.మీ వర్షం ({rainy_days_count} వర్షపు రోజులు) నమోదైంది, "
                f"రాబోయే 7 రోజుల్లో {forecast_rain_sum:.1f} మి.మీ వర్ష సూచన ఉంది. "
                f"ఇది నేల పైపొరను స్వల్పంగా తడిపినప్పటికీ, {crop} పంట నెలవారీ నీటి అవసరాలతో పోలిస్తే తక్కువ. "
                f"{irrigation} ద్వారా అదనపు తడులు అందించడం తప్పనిసరి."
            )
        else:
            # When total_30d_rain >= 60.0, evaluate distribution and crop requirements
            if rainy_days_count <= 2:
                # Poor distribution (concentrated downpour)
                rain_risk = "Watch"
                rain_risk_display = "ఓ మోస్తరు (Watch)" if lang == "te" else "Watch"
                rain_desc_en = (
                    f"Substantial volume with uneven distribution: Estimated 30-day cumulative rainfall is {total_30d_rain:.1f} mm, "
                    f"but occurred on only {rainy_days_count} rainy days (peak single day: {max_day_rain:.1f} mm). "
                    f"Concentrated precipitation often yields significant surface runoff rather than uniform root-zone recharge. "
                    f"For {crop}, continuous availability depends on {irrigation} intervals."
                )
                rain_desc_te = (
                    f"అసమాన వర్షపాత పంపిణీ: గత 30 రోజులలో {total_30d_rain:.1f} మి.మీ వర్షం కురిసినప్పటికీ, "
                    f"ఇది కేవలం {rainy_days_count} రోజుల్లోనే నమోదైంది (ఒకే రోజు గరిష్టంగా {max_day_rain:.1f} మి.మీ). "
                    f"ఒకేసారి భారీగా పడిన వర్షపు నీరు ఎక్కువగా కొట్టుకుపోతుంది కానీ ఎక్కువ రోజులు నిల్వ ఉండదు. "
                    f"{crop} పంటకు {irrigation} ద్వారా నిరంతర నీటి పర్యవేక్షణ అవసరం."
                )
            elif is_high_water_crop and is_rainfed:
                rain_risk = "Watch"
                rain_risk_display = "ఓ మోస్తరు (Watch)" if lang == "te" else "Watch"
                rain_desc_en = (
                    f"Active rainfall accumulation ({total_30d_rain:.1f} mm estimated across {rainy_days_count} days), "
                    f"yet rainfed {crop} has high ongoing evapotranspiration demands that exceed intermittent rainfall alone. "
                    f"7-day forecast indicates {forecast_rain_sum:.1f} mm."
                )
                rain_desc_te = (
                    f"గత 30 రోజులలో {total_30d_rain:.1f} మి.మీ సంచిత వర్షపాతం నమోదైనప్పటికీ ({rainy_days_count} వర్షపు రోజులు), "
                    f"వర్షాధార {crop} పంటకు నీటి అవసరం చాలా ఎక్కువ కాబట్టి పూర్తి సంతృప్తికరంగా చెప్పలేము. "
                    f"వచ్చే వారంలో {forecast_rain_sum:.1f} మి.మీ వర్ష సూచన ఉంది."
                )
            else:
                rain_risk = "Normal"
                rain_risk_display = "సాధారణం / అనుకూల పరిమాణం" if lang == "te" else "Favorable Volume"
                rain_desc_en = (
                    f"Favorable cumulative precipitation volume: Estimated {total_30d_rain:.1f} mm across {rainy_days_count} distributed rainy days "
                    f"(Open-Meteo reanalysis). 7-day forecast adds {forecast_rain_sum:.1f} mm. "
                    f"(Note: Cumulative rainfall indicates atmospheric input, not complete crop evapotranspiration balance. "
                    f"Irrigation availability via {irrigation} provides additional management buffer.)"
                )
                rain_desc_te = (
                    f"అనుకూలమైన సంచిత వర్షపాతం: రీఅనాలిసిస్ ప్రకారం గత 30 రోజులలో {total_30d_rain:.1f} మి.మీ వర్షం ({rainy_days_count} వర్షపు రోజులు) నమోదైంది. "
                    f"రాబోయే 7 రోజుల్లో {forecast_rain_sum:.1f} మి.మీ వర్షం పడే సూచన ఉంది. "
                    f"(గమనిక: సంచిత వర్షపాతం వాతావరణ నీటి చేరికను మాత్రమే సూచిస్తుంది; పంట పూర్తి నీటి సమతుల్యత నేల తేమ మరియు {irrigation} పై ఆధారపడి ఉంటుంది.)"
                )

        indicators.append({
            "id": "rainfall_availability",
            "name_en": "Cumulative Rainfall & Moisture Availability",
            "name_te": "సంచిత వర్షపాతం మరియు తేమ లభ్యత",
            "risk_level": rain_risk,
            "risk_level_display": rain_risk_display,
            "data_used_en": (
                f"30d reanalysis estimate: {total_30d_rain:.1f} mm ({rainy_days_count} rainy days, peak {max_day_rain:.1f} mm) | "
                f"7d forecast: {forecast_rain_sum:.1f} mm | Crop: {crop}"
            ),
            "data_used_te": (
                f"30 రోజుల అంచనా: {total_30d_rain:.1f} మి.మీ ({rainy_days_count} వర్షపు రోజులు, గరిష్టం {max_day_rain:.1f} మి.మీ) | "
                f"7 రోజుల అంచనా: {forecast_rain_sum:.1f} మి.మీ | పంట: {crop}"
            ),
            "method_en": (
                "Experimental evaluation combining 30-day cumulative volume, rainy-day distribution, "
                "crop hydrological profile, and irrigation buffer. Cumulative rain ≠ crop water requirement (ETc)."
            ),
            "method_te": (
                "30 రోజుల సంచిత వర్షం, పంపిణీ, పంట నీటి అవసరాలు మరియు నీటి వనరులను కలిపి విశ్లేషించే ప్రయోగాత్మక పద్ధతి. "
                "సంచిత వర్షపాతం అంటే పంట పూర్తి నీటి అవసరం కాదు."
            ),
            "explanation": rain_desc_te if lang == "te" else rain_desc_en,
            "is_experimental": True,
        })

    # =========================================================================
    # INDICATOR 4: WATER STRESS (Synthesis of Soil, Irrigation & Dry Interval)
    # =========================================================================
    if not dry_metrics.get("is_valid", False):
        indicators.append({
            "id": "water_stress",
            "name_en": "Soil Moisture & Irrigation Vulnerability",
            "name_te": "నేల తేమ & నీటి పారుదల వనరుల స్థితి",
            "risk_level": "Insufficient Data",
            "risk_level_display": "వాతావరణ సమాచారం సరిపోదు" if lang == "te" else "Insufficient weather data",
            "data_used_en": "Farm soil profile and historical precipitation",
            "data_used_te": "నేల రకం మరియు గత వర్షపాత డేటా",
            "method_en": "Synthesis of soil drainage, irrigation source, and dry interval",
            "method_te": "నేల నీటి నిల్వ, నీటి వనరు మరియు వర్షాభావ రోజుల సమ్మేళనం",
            "explanation": (
                "వాతావరణ సమాచారం సరిపోదు. నీటి ఒత్తిడి విశ్లేషణకు అవసరమైన వాతావరణ వివరాలు లేవు."
                if lang == "te"
                else "Insufficient weather data. Precipitation history is insufficient to compute water stress vulnerability."
            ),
            "is_experimental": True,
        })
    else:
        current_dry_days = dry_metrics["current_consecutive_dry_days"]
        is_rainfed = "Rainfed" in irrigation
        is_light_soil = "Sandy" in soil_type or "Red" in soil_type
        is_borewell_or_drip = "Borewell" in irrigation or "Drip" in irrigation

        if is_rainfed and current_dry_days >= 10:
            stress_risk = "Alert"
            stress_risk_display = "తీవ్రం (Alert)" if lang == "te" else "Alert"
            stress_desc_en = (
                f"Elevated soil moisture vulnerability: The plot is managed under rainfed conditions on {soil_type} "
                f"with {current_dry_days} consecutive dry days observed. In coarse/loamy profiles, infiltration capacity is high but "
                f"water holding capacity is limited. Soil moisture conservation (such as surface mulching) is recommended."
            )
            stress_desc_te = (
                f"తీవ్రమైన నీటి ఒత్తిడి అవకాశం: {soil_type} నేలలో వర్షాధార సాగు చేస్తూ గత {current_dry_days} రోజులుగా వర్షం లేకపోవడం గమనార్హం. "
                f"ఇటువంటి నేలల్లో నీటి నిల్వ సామర్థ్యం తక్కువ కాబట్టి తేమ వేగంగా ఆరిపోతుంది. "
                f"తేమ సంరక్షణ చర్యలు (మల్చింగ్) చేపట్టడం ఎంతో అవసరం."
            )
        elif is_light_soil and current_dry_days >= 7:
            stress_risk = "Watch"
            stress_risk_display = "ఓ మోస్తరు (Watch)" if lang == "te" else "Watch"
            stress_desc_en = (
                f"Moderate moisture monitoring indicated: {soil_type} exhibits relatively rapid percolation and modest retention. "
                f"With {current_dry_days} dry days observed in reanalysis, maintaining regular scheduled irrigations using {irrigation} "
                f"helps avoid transient root-zone water stress for {crop}."
            )
            stress_desc_te = (
                f"మోస్తరు నీటి పర్యవేక్షణ అవసరం: {soil_type} నేలల్లో నీరు త్వరగా ఇంకిపోతుంది కాబట్టి తేమ ఎక్కువ రోజులు నిలవదు. "
                f"గత {current_dry_days} రోజులుగా వర్షం లేనందున, {irrigation} ద్వారా సకాలంలో తడులు అందించి {crop} పంటను కాపాడుకోవాలి."
            )
        elif is_borewell_or_drip:
            stress_risk = "Low"
            stress_risk_display = "అదుపులో ఉంది (Low)" if lang == "te" else "Low"
            stress_desc_en = (
                f"Buffered moisture condition: Available {irrigation} on {soil_type} provides an active operational buffer "
                f"against current meteorological dry intervals. Continue scheduled application based on crop developmental stage."
            )
            stress_desc_te = (
                f"నియంత్రణలో ఉన్న నీటి వనరులు: {soil_type} నేలలో {irrigation} సౌకర్యం ఉండటం వల్ల ప్రస్తుత వర్షాభావ పరిస్థితుల నుండి "
                f"పంటకు తగిన రక్షణ లభిస్తుంది. పంట దశను బట్టి సాధారణ నీటి తడులను కొనసాగించవచ్చు."
            )
        else:
            stress_risk = "Watch"
            stress_risk_display = "ఓ మోస్తరు (Watch)" if lang == "te" else "Watch"
            stress_desc_en = (
                f"Dependent water management: Surface or canal irrigation on {soil_type} relies on rotational reservoir releases. "
                f"Monitor local canal scheduling during prevailing dry intervals."
            )
            stress_desc_te = (
                f"కాలువ/బావి ఆధారిత నీటి నిర్వహణ: {soil_type} నేలలో కాలువ నీరు లేదా బావుల ఆధారంగా సాగు జరుగుతోంది. "
                f"వర్షాలు లేని సమయంలో కాలువ నీటి విడుదల షెడ్యూల్‌ను గమనించి తడులు ప్లాన్ చేసుకోవాలి."
            )

        indicators.append({
            "id": "water_stress",
            "name_en": "Soil Moisture & Irrigation Vulnerability",
            "name_te": "నేల తేమ & నీటి పారుదల వనరుల స్థితి",
            "risk_level": stress_risk,
            "risk_level_display": stress_risk_display,
            "data_used_en": f"Soil: {soil_type} | Irrigation: {irrigation} | Observed dry days: {current_dry_days}",
            "data_used_te": f"నేల: {soil_type} | నీటి వనరు: {irrigation} | వర్షాభావ రోజులు: {current_dry_days}",
            "method_en": "Agronomic synthesis: Rainfed + ≥10 dry days = Alert; Light soils + ≥7 dry days = Watch; Active irrigation = Low buffer",
            "method_te": "సమ్మేళన విశ్లేషణ: వర్షాధార సాగు + ≥10 రోజులు వర్షం లేకపోతే అలర్ట్; తేలికపాటి నేలలు + ≥7 రోజులు అయితే వాచ్; డ్రిప్/బోరుబావి ఉంటే లో రిస్క్",
            "explanation": stress_desc_te if lang == "te" else stress_desc_en,
            "is_experimental": True,
        })

    return indicators


def get_crop_climate_context(crop: str, lang: str = "en") -> Dict[str, Any]:
    """Retrieve educational agronomic context for the selected crop regarding weather variables.
    
    Explains physiological principles of temperature, moisture, and water availability
    without making unsupported yield claims or exact volumetric irrigation mandates.
    """
    contexts = {
        "Turmeric": {
            "title_en": "Crop Physiological Sensitivity: Turmeric (Curcuma longa)",
            "title_te": "పంట శారీరక వాతావరణ సున్నితత్వం: పసుపు (Turmeric)",
            "temp_importance_en": (
                "Turmeric is adapted to warm, humid tropical conditions, typically thriving between 20°C and 35°C. "
                "When ambient temperatures exceed 38°C, transpirational demand increases sharply, which may cause "
                "leaf-tip drying and temporary stomatal closure during midday hours."
            ),
            "temp_importance_te": (
                "పసుపు పంట 20°C నుండి 35°C మధ్య గల ఉష్ణమండల వాతావరణంలో బాగా పెరుగుతుంది. "
                "ఉష్ణోగ్రతలు 38°C మించినప్పుడు ఆకుల నుండి నీరు వేగంగా ఆవిరై, మధ్యాహ్న సమయాల్లో ఆకుల చివర్లు వాడిపోవడం గమనించవచ్చు."
            ),
            "water_importance_en": (
                "During rhizome initiation and development, regular soil moisture in the root zone is critical. "
                "Extended dry intervals without irrigation can restrict rhizome enlargement, whereas poor drainage or "
                "water stagnation in heavy clay soils creates an anaerobic environment favorable to fungal rhizome rot."
            ),
            "water_importance_te": (
                "కొమ్ము ఊరే దశలో వేరు మండలంలో నిరంతరం తేమ ఉండటం అవసరం. నీటి కొరత ఏర్పడితే కొమ్ముల పెరుగుదల మందగిస్తుంది; "
                "అలాగే బంక నేలల్లో ఎక్కువ కాలం నీరు నిలిచిపోతే గాలి ఆడక దుంప కుళ్లు తెగులు వచ్చే అవకాశం పెరుగుతుంది."
            ),
            "resilience_tips_en": (
                "Agronomic best practices include maintaining organic surface mulching (e.g., crop residues or green leaves) "
                "to buffer soil temperature fluctuations and reduce surface evaporation during dry periods."
            ),
            "resilience_tips_te": (
                "రైతులకు సూచన: ఎండ తీవ్రత మరియు వర్షాభావ పరిస్థితులలో నేలపై వరి గడ్డి లేదా ఎండుటాకులతో మల్చింగ్ చేయడం వల్ల "
                "నేల వేడెక్కకుండా తేమ ఎక్కువ కాలం నిల్వ ఉంటుంది."
            ),
        },
        "Banana": {
            "title_en": "Crop Physiological Sensitivity: Banana (Musa acuminata)",
            "title_te": "పంట శారీరక వాతావరణ సున్నితత్వం: అరటి (Banana)",
            "temp_importance_en": (
                "Banana thrives within an optimal thermal range of 25°C to 32°C. Sustained exposure to high temperatures (>38°C), "
                "especially in conjunction with dry winds, can lead to marginal leaf scorch, lamina tearing, and sunburn on exposed fruit."
            ),
            "temp_importance_te": (
                "అరటి పంటకు 25°C నుండి 32°C ఉష్ణోగ్రతలు చాలా అనుకూలం. ఉష్ణోగ్రతలు 38°C కంటే పెరిగి వేడి గాలులు వీచినప్పుడు "
                "ఆకులు చీలిపోవడం, గెలలపై ఎండమాడు మచ్చలు ఏర్పడటం జరుగుతుంది."
            ),
            "water_importance_en": (
                "Given its broad leaves and high transpirational surface, banana has high ongoing moisture requirements. "
                "Water deficit during shooting, bunch emergence, and finger filling directly impacts fruit development."
            ),
            "water_importance_te": (
                "వెడల్పాటి ఆకులు ఉండటం వల్ల అరటి మొక్కలకు నీటి వినియోగం చాలా ఎక్కువ. "
                "గెల వేసే దశలో మరియు కాయ ఊరే దశలో నీటి ఎద్దడి ఏర్పడితే కాయల అభివృద్ధి మరియు నాణ్యత దెబ్బతింటుంది."
            ),
            "resilience_tips_en": (
                "Windbreak barriers along field perimeters mitigate mechanical leaf shredding, and scheduled micro-irrigation "
                "helps maintain a consistent root-zone moisture profile during rainless spells."
            ),
            "resilience_tips_te": (
                "రైతులకు సూచన: తోట చుట్టూ గాలి తీవ్రతను అడ్డుకునే చెట్లను పెంచడం మంచిది. "
                "వర్షాలు లేని కాలంలో డ్రిప్ ద్వారా క్రమం తప్పకుండా తడులు ఇస్తూ గెలలకు రక్షణ తొడుగులు వాడాలి."
            ),
        },
        "Paddy": {
            "title_en": "Crop Physiological Sensitivity: Paddy (Oryza sativa)",
            "title_te": "పంట శారీరక వాతావరణ సున్నితత్వం: వరి (Paddy)",
            "temp_importance_en": (
                "Optimal growth temperatures for rice range between 22°C and 33°C. Temperatures exceeding 35°C during flowering "
                "(anthesis) can cause pollen desiccation, leading to spikelet sterility and chaffy grains."
            ),
            "temp_importance_te": (
                "వరి పంట పెరుగుదలకు 22°C నుండి 33°C ఉష్ణోగ్రతలు ఉత్తమం. ముఖ్యంగా ఈనిన దశలో మరియు పూత సమయంలో "
                "ఉష్ణోగ్రతలు 35°C దాటితే పుప్పొడి ఎండిపోయి తాలు గింజలు (తాలు కాయడం) పెరిగే ప్రమాదం ఉంది."
            ),
            "water_importance_en": (
                "Tillering, panicle initiation, and flowering represent stages of peak hydrological vulnerability. "
                "In light or red soils with high percolation, rainless intervals deplete surface standing water rapidly, "
                "increasing weed pressure and requiring prompt irrigation recharging."
            ),
            "water_importance_te": (
                "పిలకలు తొడిగే దశ మరియు చిరుపొట్ట దశలలో వరికి నీరు అత్యంత అవసరం. "
                "తేలికపాటి నేలల్లో నీరు త్వరగా ఇంకిపోవడం వల్ల వర్షాభావ సమయంలో భూమి నెర్రలు చాచి, కలుపు పెరిగి పంట ఎదుగుదల మందగిస్తుంది."
            ),
            "resilience_tips_en": (
                "Under limited canal or borewell recharge, Alternate Wetting and Drying (AWD) practices help optimize water use "
                "without compromising root aeration during vegetative phases."
            ),
            "resilience_tips_te": (
                "రైతులకు సూచన: నీటి లభ్యత తక్కువగా ఉన్నప్పుడు 'ఆరబెట్టి తడపడం' (Alternate Wetting and Drying) పద్ధతిని పాటించాలి. "
                "ఎల్లప్పుడూ ఎక్కువ నీరు నిల్వ ఉంచకుండా, భూమిలో తడి ఆరిన వెంటనే తడులు ఇవ్వడం ద్వారా నీటిని సమర్థవంతంగా వాడుకోవచ్చు."
            ),
        },
    }

    info = contexts.get(crop, contexts["Turmeric"])
    return {
        "title": info[f"title_{lang}"],
        "temperature_importance": info[f"temp_importance_{lang}"],
        "water_importance": info[f"water_importance_{lang}"],
        "resilience_tips": info[f"resilience_tips_{lang}"],
    }


def compute_forecast_dry_spells(forecast_df: Optional[pd.DataFrame]) -> Dict[str, Any]:
    """Calculate prospective dry spell characteristics from upcoming numerical forecast.
    
    A dry day is defined as daily precipitation < 1.0 mm.
    A rainy day is defined as precipitation >= 2.5 mm (IMD benchmark).
    """
    if forecast_df is None or forecast_df.empty or "precipitation" not in forecast_df.columns:
        return {
            "is_valid": False,
            "total_days": 0,
            "dry_days_count": 0,
            "rainy_days_count": 0,
            "total_forecast_rain": 0.0,
            "max_single_day_rain": 0.0,
            "longest_forecast_dry_spell": 0,
            "first_rain_date": None,
        }

    valid_df = forecast_df.dropna(subset=["precipitation"])
    if valid_df.empty:
        return {
            "is_valid": False,
            "total_days": 0,
            "dry_days_count": 0,
            "rainy_days_count": 0,
            "total_forecast_rain": 0.0,
            "max_single_day_rain": 0.0,
            "longest_forecast_dry_spell": 0,
            "first_rain_date": None,
        }

    precip_list = valid_df["precipitation"].tolist()
    dates_list = valid_df["date"].tolist() if "date" in valid_df.columns else []
    total_rain = round(float(valid_df["precipitation"].sum()), 1)
    dry_count = int((valid_df["precipitation"] < 1.0).sum())
    rainy_count = int((valid_df["precipitation"] >= 2.5).sum())
    max_rain = round(float(valid_df["precipitation"].max()), 1)

    # Longest dry run in forecast
    longest_dry = 0
    cur_run = 0
    first_rain = None
    for idx, p in enumerate(precip_list):
        if p >= 2.5 and first_rain is None and idx < len(dates_list):
            first_rain = dates_list[idx]
        if p < 1.0:
            cur_run += 1
            if cur_run > longest_dry:
                longest_dry = cur_run
        else:
            cur_run = 0

    return {
        "is_valid": True,
        "total_days": len(valid_df),
        "dry_days_count": dry_count,
        "rainy_days_count": rainy_count,
        "total_forecast_rain": total_rain,
        "max_single_day_rain": max_rain,
        "longest_forecast_dry_spell": longest_dry,
        "first_rain_date": first_rain,
    }


def analyze_future_date_plan(
    target_date: Any,
    weather_data: Dict[str, Any],
    crop: str = "Turmeric",
    stage_info: Optional[Dict[str, Any]] = None,
    lang: str = "en",
) -> Dict[str, Any]:
    """Evaluate a requested farm planning date against available meteorological horizons.
    
    Categorizes target_date into:
    1. 'HISTORICAL': Within past 30 days reanalysis.
    2. 'TODAY': Current date observation.
    3. 'FORECAST': Supported future NWP forecast horizon (up to 16 days).
    4. 'BEYOND_FORECAST': Exceeds numerical weather forecast horizon (guidance to What-If simulator).
    """
    import datetime
    from src.weather.weather_api import get_weather_description

    if hasattr(target_date, "date"):
        target_d = target_date.date()
    elif isinstance(target_date, str):
        target_d = datetime.date.fromisoformat(target_date.strip())
    else:
        target_d = target_date

    today = datetime.date.today()
    lead_days = (target_d - today).days

    forecast_df = weather_data.get("forecast_df", pd.DataFrame())
    historical_df = weather_data.get("historical_df", pd.DataFrame())
    forecast_status = weather_data.get("forecast_status", "available")
    is_cached = weather_data.get("is_offline_cached", False)
    cached_at = weather_data.get("cached_at", "earlier")
    retrieved_at = weather_data.get("retrieved_at", "Recent")

    max_forecast_date = forecast_df["date"].max() if (forecast_df is not None and not forecast_df.empty and "date" in forecast_df.columns) else today

    # 1. Historical Date (< today)
    if lead_days < 0:
        hist_row = None
        if historical_df is not None and not historical_df.empty and "date" in historical_df.columns:
            matches = historical_df[historical_df["date"] == target_d]
            if not matches.empty:
                hist_row = matches.iloc[0].to_dict()

        return {
            "status": "HISTORICAL",
            "target_date": target_d,
            "lead_days": lead_days,
            "is_supported": True,
            "row": hist_row,
            "title_en": f"Past Date ({target_d.strftime('%d %b %Y')}): Historical Reanalysis",
            "title_te": f"గత తేదీ ({target_d.strftime('%d %b %Y')}): చారిత్రక వాతావరణ రికార్డు",
            "message_en": (
                f"The selected date is in the past ({abs(lead_days)} days ago). "
                f"Displaying historical operational reanalysis recorded by Open-Meteo (~11 km grid)."
            ),
            "message_te": (
                f"మీరు ఎంచుకున్న తేదీ గతంలో ఉంది ({abs(lead_days)} రోజుల క్రితం). "
                f"ఓపెన్-మెటియో రికార్డు చేసిన గత వాతావరణ వివరాలు చూపించబడుతున్నాయి."
            ),
        }

    # 2. Check if Forecast is completely unavailable (stale offline cache or API failure)
    if (forecast_df is None or forecast_df.empty or forecast_status == "unavailable") and lead_days > 0:
        return {
            "status": "UNAVAILABLE",
            "target_date": target_d,
            "lead_days": lead_days,
            "is_supported": False,
            "title_en": "Forecast Unavailable",
            "title_te": "వాతావరణ అంచనా అందుబాటులో లేదు",
            "message_en": (
                f"Valid future forecast data is unavailable for {target_d.strftime('%d %b %Y')}. "
                f"{'The offline snapshot has expired. Please reconnect to internet and click Refresh.' if is_cached else 'The weather service could not be reached.'} "
                f"The application does not fabricate future weather."
            ),
            "message_te": (
                f"{target_d.strftime('%d %b %Y')} తేదీకి తాజా వాతావరణ అంచనాలు అందుబాటులో లేవు. "
                f"ఆఫ్‌లైన్ డేటా గడువు ముగిసింది. దయచేసి ఇంటర్నెట్ ఆన్ చేసి రిఫ్రెష్ బటన్ నొక్కండి. "
                f"ఊహాజనిత సంఖ్యలను యాప్ సృష్టించదు."
            ),
        }

    # 3. Beyond Provider Horizon (> max_forecast_date)
    if target_d > max_forecast_date or lead_days > 16:
        return {
            "status": "BEYOND_FORECAST",
            "target_date": target_d,
            "lead_days": lead_days,
            "max_supported_date": max_forecast_date,
            "horizon_days": len(forecast_df) if forecast_df is not None else 16,
            "is_supported": False,
            "title_en": f"⚠️ Date Exceeds {len(forecast_df) if forecast_df is not None else 16}-Day Forecast Horizon",
            "title_te": f"⚠️ తేదీ {len(forecast_df) if forecast_df is not None else 16} రోజుల సూచన పరిమితిని మించింది",
            "message_en": (
                f"The requested date ({target_d.strftime('%d %b %Y')}) is {lead_days} days ahead. "
                f"Open-Meteo and global Numerical Weather Prediction (NWP) models only provide deterministic forecasts up to "
                f"{len(forecast_df) if forecast_df is not None else 16} days (through {max_forecast_date.strftime('%d %b %Y')}). "
                f"No artificial or fabricated forecast numbers are generated. "
                f"For seasonal planning across 30, 60, or 90 days, please use the What-If Simulator."
            ),
            "message_te": (
                f"మీరు ఎంచుకున్న తేదీ ({target_d.strftime('%d %b %Y')}) రాబోయే {lead_days} రోజుల తర్వాత ఉంది. "
                f"ఓపెన్-మెటియో మరియు ప్రపంచ వాతావరణ నమూనాలు గరిష్టంగా {len(forecast_df) if forecast_df is not None else 16} రోజుల వరకు మాత్రమే "
                f"({max_forecast_date.strftime('%d %b %Y')} వరకు) ఖచ్చితమైన అంచనాలను అందిస్తాయి. "
                f"యాప్ ఎటువంటి ఊహాజనిత లేదా నకిలీ వాతావరణ సంఖ్యలను చూపించదు. "
                f"30, 60 లేదా 90 రోజుల దీర్ఘకాలిక సాగు ప్రణాళిక కోసం 'వాట్-ఇఫ్ సిమ్యులేటర్' విభాగాన్ని ఉపయోగించండి."
            ),
        }

    # 4. Today or Supported Future Forecast Day
    matches = forecast_df[forecast_df["date"] == target_d] if (forecast_df is not None and not forecast_df.empty) else pd.DataFrame()
    if matches.empty:
        # Fallback if edge date
        return {
            "status": "UNAVAILABLE",
            "target_date": target_d,
            "lead_days": lead_days,
            "is_supported": False,
            "title_en": "Record Not Found in Forecast Range",
            "title_te": "సూచన పరిధిలో రికార్డు లభించలేదు",
            "message_en": "No specific daily record returned by Open-Meteo for this date.",
            "message_te": "ఈ తేదీకి సంబంధించి ఓపెన్-మెటియో వివరాలు లభించలేదు.",
        }

    row = matches.iloc[0].to_dict()
    temp_max = float(row.get("temp_max", 32.0))
    temp_min = float(row.get("temp_min", 24.0))
    precip = float(row.get("precipitation", 0.0))
    precip_prob = float(row.get("precip_probability", 0.0))
    w_code = row.get("weather_code")
    sky_desc = get_weather_description(w_code, lang=lang)

    # Lead time and confidence calibration (descriptive lead-time categories grounded in NWP predictability)
    if lead_days <= 1:
        conf_tier = "High"
        conf_lead_label_en = "Short-Range NWP (24–48h)"
        conf_lead_label_te = "స్వల్పకాలిక అంచనా (24–48 గంటలు)"
        conf_desc_en = "High model confidence based on short-range Numerical Weather Prediction (24–48h lead time)."
        conf_desc_te = "స్వల్పకాలిక న్యూమరికల్ వెదర్ ప్రిడిక్షన్ ఆధారంగా అధిక విశ్వసనీయత (24–48 గంటల వ్యవధి)."
    elif lead_days <= 7:
        conf_tier = "Moderate"
        conf_lead_label_en = "Medium-Range Guidance (Days 2–7)"
        conf_lead_label_te = "మధ్యంతర సూచన (2–7 రోజులు)"
        conf_desc_en = "Moderate model confidence: Synoptic patterns reliable, but precipitation timing/amounts carry uncertainty. Re-verify prior to critical spraying."
        conf_desc_te = "మధ్యస్థ విశ్వసనీయత: వాతావరణ ధోరణి స్థిరంగా ఉన్నప్పటికీ, వర్షం సమయం/పరిమాణంలో అనిశ్చితి ఉండవచ్చు. పిచికారీకి ముందు సరిచూసుకోండి."
    else:
        conf_tier = "Indicative"
        conf_lead_label_en = "Extended Horizon Trend (Days 8–16)"
        conf_lead_label_te = "పొడిగించిన ట్రెండ్ (8–16 రోజులు)"
        conf_desc_en = "Indicative synoptic trend only. Forecast skill degrades with extended lead time (>7 days) due to atmospheric chaos. Do not use for irreversible decisions."
        conf_desc_te = "కేవలం సూచనాప్రాయమైన ధోరణి మాత్రమే. వాతావరణ మార్పుల దృష్ట్యా 7 రోజుల దాటిన తర్వాత ఖచ్చితత్వం తగ్గుతుంది. మార్చలేని నిర్ణయాలకు వాడవద్దు."

    # Crop-specific thermal threshold inspection
    crop_heat_threshold = 35.0
    crop_critical_heat = 38.0
    if crop == "Banana":
        crop_heat_threshold = 36.5
        crop_critical_heat = 38.5
    elif crop == "Paddy":
        crop_heat_threshold = 35.0
        crop_critical_heat = 37.0

    heat_risk_level = "Normal"
    if temp_max >= crop_critical_heat:
        heat_risk_level = "High"
    elif temp_max >= crop_heat_threshold:
        heat_risk_level = "Moderate"

    # Crop-specific precipitation risk
    rain_risk_level = "Low"
    if precip >= 30.0 or w_code in [95, 96, 99]:
        rain_risk_level = "High"
    elif precip >= 10.0 or precip_prob >= 70:
        rain_risk_level = "Moderate"

    # Operational Agronomic Recommendations for Farmer (Explicitly distinguishing heuristics from verified thresholds)
    irrig_advice_en = ""
    irrig_advice_te = ""
    if precip >= 5.0 or precip_prob >= 70:
        irrig_advice_en = (
            f"Rainfall expected ({precip:.1f} mm, {precip_prob:.0f}% chance). "
            f"Decision heuristic (ANGRAU / KVK water management): Suspend scheduled irrigation to conserve groundwater/electricity and avoid root-zone waterlogging."
        )
        irrig_advice_te = (
            f"వర్ష సూచన ఉంది ({precip:.1f} మి.మీ, {precip_prob:.0f}% అవకాశం). "
            f"యాజమాన్య సూచన (ANGRAU / KVK మార్గదర్శకాలు): విద్యుత్ మరియు నీటిని ఆదా చేయడానికి, నీరు నిలవకుండా ఉండటానికి నీటి తడులు వాయిదా వేయండి."
        )
    elif precip < 1.0 and temp_max >= crop_heat_threshold:
        irrig_advice_en = (
            f"Dry conditions with elevated temperature ({temp_max:.1f}°C vs {crop} threshold {crop_heat_threshold}°C). "
            f"Decision heuristic (ICAR stress guidance): Maintain light, frequent irrigation to prevent thermal and moisture stress."
        )
        irrig_advice_te = (
            f"వర్షం లేని పొడి వాతావరణం మరియు అధిక వేడి ({temp_max:.1f}°C, {crop} పరిమితి {crop_heat_threshold}°C కంటే ఎక్కువ). "
            f"యాజమాన్య సూచన (ICAR మార్గదర్శకాలు): నేలలో తేమ ఆరిపోకుండా క్రమం తప్పకుండా తేలికపాటి తడులు ఇవ్వండి."
        )
    else:
        irrig_advice_en = "Standard scheduled irrigation can proceed based on local soil moisture observation."
        irrig_advice_te = "నేలలోని తేమను బట్టి సాధారణ నీటి తడులను కొనసాగించవచ్చు."

    spray_advice_en = ""
    spray_advice_te = ""
    if precip >= 5.0 or precip_prob >= 60 or w_code in [80, 81, 82, 95, 96]:
        spray_advice_en = (
            "Unfavorable for pesticide spraying or top-dressing nitrogen. "
            "Decision heuristic (CIAE / ANGRAU GAP): Chemical wash-off and leaching risk; minimum 4-6 hour rain-free drying window required. Postpone until clear weather."
        )
        spray_advice_te = (
            "పురుగు మందుల పిచికారీ లేదా ఎరువులు వేయడానికి అనుకూలం కాదు. "
            "యాజమాన్య సూచన (CIAE / ANGRAU GAP): వర్షంలో కొట్టుకుపోయే ప్రమాదం ఉంది; కనీసం 4-6 గంటల పొడి వాతావరణం అవసరం. వాతావరణం అనుకూలించే వరకు వేచి ఉండండి."
        )
    else:
        spray_advice_en = "Weather window suitable for scheduled pesticide sprays or fertilizer application if needed."
        spray_advice_te = "పురుగు మందుల పిచికారీ లేదా పైపాటు ఎరువులు వేయడానికి వాతావరణం అనుకూలంగా ఉంది."

    if stage_info:
        stage_name = stage_info.get("stage_te" if lang == "te" else "stage", stage_info.get("stage", "Active Growing Stage"))
    else:
        stage_name = "General Development" if lang == "en" else "సాధారణ ఎదుగుదల దశ"

    return {
        "status": "FORECAST",
        "target_date": target_d,
        "lead_days": lead_days,
        "is_supported": True,
        "is_today": lead_days == 0,
        "temp_max": temp_max,
        "temp_min": temp_min,
        "precipitation": precip,
        "precip_probability": precip_prob,
        "weather_code": w_code,
        "sky_desc": sky_desc,
        "confidence_tier": conf_tier,
        "confidence_lead_label": conf_lead_label_te if lang == "te" else conf_lead_label_en,
        "confidence_desc": conf_desc_te if lang == "te" else conf_desc_en,
        "heat_risk_level": heat_risk_level,
        "rain_risk_level": rain_risk_level,
        "irrigation_advice": irrig_advice_te if lang == "te" else irrig_advice_en,
        "spray_advice": spray_advice_te if lang == "te" else spray_advice_en,
        "crop": crop,
        "stage_name": stage_name,
        "retrieved_at": retrieved_at,
        "is_cached": is_cached,
        "cached_at": cached_at,
        "disclaimer_en": "Numerical forecast values are model estimates subject to atmospheric variability, not guaranteed outcomes. Operational guidance represents rule-based decision heuristics grounded in ANGRAU & ICAR extension guidelines.",
        "disclaimer_te": "ఈ వాతావరణ వివరాలు న్యూమరికల్ మోడల్ అంచనాలు మాత్రమే; వాతావరణ మార్పులను బట్టి మారవచ్చు. వ్యవసాయ సూచనలు ANGRAU మరియు ICAR మార్గదర్శకాల ఆధారంగా రూపొందించిన రూల్-బేస్డ్ నిర్ణయాలు.",
    }
