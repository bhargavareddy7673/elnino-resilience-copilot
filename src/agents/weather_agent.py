"""Weather Agent: Specialist module for atmospheric telemetry and forecast synthesis.

Responsible for:
1. Current weather reporting (temperature, humidity, wind, current rain, condition).
2. 7-day agricultural forecast evaluation (daily max/min, rain expectation, rain probability).
3. 30-day historical precipitation evaluation (reanalysis volume, rainy days).
4. Dry-spell status reporting (consecutive dry days, IMD rainy-day benchmark).

Always grounds responses in verified data from Open-Meteo, never fabricates values,
and reports clear diagnostics if live telemetry is unavailable.
"""

from typing import Dict, Any
import pandas as pd


def answer_current_weather(
    weather_data: Dict[str, Any],
    location_name: str,
    lang: str = "en",
) -> Dict[str, Any]:
    """Generate response for current atmospheric conditions."""
    if not weather_data.get("success", False):
        err = weather_data.get("error", "Service unavailable")
        text_en = f"Live weather data is currently unavailable for {location_name} ({err}). Please check your connection and refresh."
        text_te = f"{location_name} ప్రాంతానికి ప్రత్యక్ష వాతావరణ సమాచారం అందుబాటులో లేదు ({err}). దయచేసి ఇంటర్నెట్ సరిచూసి మళ్లీ ప్రయత్నించండి."
        return {
            "response": text_te if lang == "te" else text_en,
            "grounding_data": {"status": "unavailable", "error": err},
        }

    curr = weather_data.get("current", {})
    temp = curr.get("temperature")
    rh = curr.get("relative_humidity")
    wind = curr.get("wind_speed")
    precip = curr.get("precipitation", 0.0)
    retrieved_at = weather_data.get("retrieved_at", "Recently")
    is_cached = weather_data.get("is_offline_cached", False)

    grounding = {
        "location": location_name,
        "temperature_c": temp,
        "relative_humidity_pct": rh,
        "wind_speed_kmh": wind,
        "precipitation_mm": precip,
        "retrieved_at": retrieved_at,
        "is_offline_cached": is_cached,
        "source": weather_data.get("source", "Open-Meteo Live Model API"),
    }

    if lang == "te":
        source_note = (
            f"⚠️ *ఆఫ్‌లైన్ క్యాష్ స్నాప్‌షాట్:* `{retrieved_at}` వద్ద సేకరించబడిన డేటా (లైవ్ సర్వీస్ అందుబాటులో లేదు)."
            if is_cached
            else f"*సమాచారం అప్‌డేట్ అయిన సమయం:* `{retrieved_at}` (Open-Meteo లైవ్ మోడల్ డేటా)."
        )
        resp = (
            f"📍 **{location_name}** వద్ద వాతావరణ వివరాలు:\n\n"
            f"- 🌡️ **ఉష్ణోగ్రత:** `{temp:.1f}°C`\n"
            f"- 💧 **గాలిలో తేమ (Humidity):** `{rh:.0f}%`\n"
            f"- 💨 **గాలి వేగం:** `{wind:.1f} km/h`\n"
            f"- 🌧️ **ప్రస్తుత వర్షపాతం:** `{precip:.1f} mm`\n\n"
            f"{source_note}"
        )
    else:
        source_note = (
            f"⚠️ *Offline Cached Snapshot:* Recorded at `{retrieved_at}` (Live weather service is currently unreachable)."
            if is_cached
            else f"*Telemetry timestamp:* `{retrieved_at}` (Open-Meteo NWP High-Resolution Surface Analysis)."
        )
        resp = (
            f"📍 Current atmospheric telemetry for **{location_name}**:\n\n"
            f"- 🌡️ **Temperature:** `{temp:.1f}°C` (Dry-bulb air temperature at 2m)\n"
            f"- 💧 **Relative Humidity:** `{rh:.0f}%`\n"
            f"- 💨 **Wind Speed:** `{wind:.1f} km/h` (at 10m height)\n"
            f"- 🌧️ **Current Rain Rate:** `{precip:.1f} mm`\n\n"
            f"{source_note}"
        )

    return {"response": resp, "grounding_data": grounding}


def answer_weather_forecast(
    weather_data: Dict[str, Any],
    location_name: str,
    crop: str = "Turmeric",
    lang: str = "en",
) -> Dict[str, Any]:
    """Generate response for upcoming 7-day agricultural forecast."""
    if not weather_data.get("success", False):
        err = weather_data.get("error", "Service unavailable")
        text_en = f"Forecast data is currently unavailable for {location_name} ({err})."
        text_te = f"{location_name} ప్రాంతానికి రాబోయే వాతావరణ అంచనా సమాచారం అందుబాటులో లేదు ({err})."
        return {"response": text_te if lang == "te" else text_en, "grounding_data": {}}

    fc_df = weather_data.get("forecast_df")
    if fc_df is None or fc_df.empty:
        text_en = f"No forecast records returned for {location_name}."
        text_te = f"{location_name} ప్రాంతానికి సూచన వివరాలు లభించలేదు."
        return {"response": text_te if lang == "te" else text_en, "grounding_data": {}}

    fc_df_7 = fc_df.head(7)
    total_fc_rain = round(float(fc_df_7["precipitation"].sum()), 1)
    rainy_days_fc = int((fc_df_7["precipitation"] >= 1.0).sum())
    max_precip_day = round(float(fc_df_7["precipitation"].max()), 1)
    peak_max_temp = round(float(fc_df_7["temp_max"].max()), 1)
    min_temp = round(float(fc_df_7["temp_min"].min()), 1)

    grounding = {
        "location": location_name,
        "forecast_window_days": 7,
        "total_forecast_rain_mm": total_fc_rain,
        "rainy_forecast_days": rainy_days_fc,
        "peak_forecast_temp_c": peak_max_temp,
        "min_forecast_temp_c": min_temp,
        "available_horizon_days": len(fc_df),
    }

    if lang == "te":
        if total_fc_rain >= 5.0:
            rain_msg = (
                f"రాబోయే 7 రోజుల్లో మొత్తం దాదాపు `{total_fc_rain:.1f} మి.మీ` వర్షం పడే అవకాశం ఉంది "
                f"({rainy_days_fc} రోజులు వర్షం సూచన, గరిష్ట ఒకరోజు వర్షం: `{max_precip_day:.1f} మి.మీ`)."
            )
        elif total_fc_rain > 0.0:
            rain_msg = (
                f"రాబోయే 7 రోజుల్లో చాలా స్వల్ప వర్షం (`{total_fc_rain:.1f} మి.మీ`) మాత్రమే సూచించబడింది. "
                f"పంటకు సరిపడా వర్షపాతం లభించకపోవచ్చు."
            )
        else:
            rain_msg = (
                f"రాబోయే 7 రోజులలో ఎటువంటి వర్ష సూచన లేదు (`0.0 మి.మీ`). "
                f"పొలంలో తేమ ఆరిపోకుండా తగిన నీటి తడులు ప్లాన్ చేసుకోవాలి."
            )

        resp = (
            f"📅 **{location_name}** కొరకు రాబోయే 7 రోజుల వాతావరణ అంచనా:\n\n"
            f"- 🌧️ **వర్షపాత సూచన:** {rain_msg}\n"
            f"- 🌡️ **గరిష్ట ఉష్ణోగ్రత:** `{peak_max_temp:.1f}°C` వరకు చేరవచ్చు.\n"
            f"- ❄️ **కనిష్ట ఉష్ణోగ్రత:** `{min_temp:.1f}°C` గా నమోదవుతుంది.\n\n"
            f"💡 *{crop} పంటకు సూచన:* వర్షాలు లేని ఎండ సమయంలో నీటి వనరులను సమర్థవంతంగా వాడుకోవడం మంచిది."
        )
    else:
        if total_fc_rain >= 5.0:
            rain_msg = (
                f"Yes, approximately `{total_fc_rain:.1f} mm` of cumulative rainfall is forecast over the next 7 days "
                f"across {rainy_days_fc} day(s) (Peak single day: `{max_precip_day:.1f} mm`)."
            )
        elif total_fc_rain > 0.0:
            rain_msg = (
                f"Only trace to light precipitation is expected: approximately `{total_fc_rain:.1f} mm` over the coming 7 days. "
                f"This volume is insufficient to meet crop water needs independently."
            )
        else:
            rain_msg = (
                f"No measurable rainfall (`0.0 mm`) is forecast for the next 7 days. "
                f"Dry conditions will prevail across the area."
            )

        resp = (
            f"📅 7-Day Agricultural Weather Forecast for **{location_name}**:\n\n"
            f"- 🌧️ **Rainfall Outlook:** {rain_msg}\n"
            f"- 🌡️ **Peak Maximum Temperature:** Projected at `{peak_max_temp:.1f}°C`\n"
            f"- ❄️ **Minimum Night Temperature:** Expected around `{min_temp:.1f}°C`\n\n"
            f"💡 *Implication for {crop}:* Plan scheduled irrigation based on soil retention; rely on available water reserves rather than expected precipitation."
        )

    if len(fc_df) > 7:
        if lang == "te":
            resp += f"\n\n🧭 *పొడిగించిన ప్రణాళిక:* రాబోయే {len(fc_df)} రోజుల వరకు రోజువారీ వాతావరణ వివరాలను **Weather** విభాగంలో పరిశీలించవచ్చు."
        else:
            resp += f"\n\n🧭 *Extended Planning:* Day-by-day operational weather planning up to {len(fc_df)} days ahead is available in the **Weather** tab."

    return {"response": resp, "grounding_data": grounding}


def answer_rainfall_status(
    weather_data: Dict[str, Any],
    location_name: str,
    crop: str = "Turmeric",
    lang: str = "en",
) -> Dict[str, Any]:
    """Generate response for recent 30-day cumulative precipitation from reanalysis."""
    hist_df = weather_data.get("historical_df")
    if hist_df is None or hist_df.empty:
        text_en = f"Historical reanalysis records are currently unavailable for {location_name}."
        text_te = f"{location_name} ప్రాంతానికి గత 30 రోజుల వర్షపాత రికార్డులు అందుబాటులో లేవు."
        return {"response": text_te if lang == "te" else text_en, "grounding_data": {}}

    total_rain = round(float(hist_df["precipitation"].sum()), 1)
    rainy_days = int((hist_df["precipitation"] >= 2.5).sum())
    max_day = round(float(hist_df["precipitation"].max()), 1)

    grounding = {
        "location": location_name,
        "window_days": 30,
        "estimated_cumulative_rain_mm": total_rain,
        "rainy_days_count": rainy_days,
        "max_single_day_rain_mm": max_day,
        "model": "Open-Meteo Operational Analysis & Reanalysis Model Grid (~11 km)",
    }

    if lang == "te":
        resp = (
            f"📊 **{location_name}** కొరకు గత 30 రోజుల వర్షపాత నివేదిక (రీఅనాలిసిస్ మోడల్ అంచనా):\n\n"
            f"- 🌧️ **సంచిత వర్షపాతం (Estimated Total):** `{total_rain:.1f} మి.మీ`\n"
            f"- 🗓️ **వర్షపు రోజులు (≥ 2.5 మి.మీ):** `{rainy_days} రోజులు`\n"
            f"- 🌊 **గరిష్ట ఒకరోజు వర్షం:** `{max_day:.1f} మి.మీ`\n\n"
            f"ℹ️ *డేటా గమనిక:* ఈ వివరాలు ఓపెన్-మెటియో ఆపరేషనల్ రీఅనాలిసిస్ మరియు మోడల్ అంచనాలు (~11 కి.మీ గ్రిడ్). "
            f"పంట పూర్తి నీటి అవసరాలతో పోలిస్తే ఇది కేవలం వాతావరణ నీటి చేరికను మాత్రమే సూచిస్తుంది."
        )
    else:
        resp = (
            f"📊 Recent 30-Day Precipitation Summary for **{location_name}**:\n\n"
            f"- 🌧️ **Estimated Cumulative Rainfall:** `{total_rain:.1f} mm`\n"
            f"- 🗓️ **Rainy Days (≥ 2.5 mm, IMD Standard):** `{rainy_days} days`\n"
            f"- 🌊 **Highest Single-Day Rainfall:** `{max_day:.1f} mm`\n\n"
            f"ℹ️ *Data Source Note:* Historical totals represent Open-Meteo operational meteorological analysis and reanalysis "
            f"grid estimates (~11 km spatial resolution) rather than in-situ on-farm ground rain-gauge measurements. "
            f"Cumulative rainfall indicates atmospheric precipitation input, not full crop evapotranspiration balance."
        )

    return {"response": resp, "grounding_data": grounding}


def answer_dry_spell_status(
    weather_data: Dict[str, Any],
    location_name: str,
    crop: str = "Turmeric",
    lang: str = "en",
) -> Dict[str, Any]:
    """Generate response for observed consecutive dry days (< 1.0 mm)."""
    hist_df = weather_data.get("historical_df")
    if hist_df is None or hist_df.empty:
        text_en = f"Precipitation history is unavailable to compute dry spell duration for {location_name}."
        text_te = f"{location_name} కొరకు వర్షాభావ రోజుల సమాచారం అందుబాటులో లేదు."
        return {"response": text_te if lang == "te" else text_en, "grounding_data": {}}

    precip_series = hist_df["precipitation"].dropna().tolist()
    current_dry = 0
    for val in reversed(precip_series):
        if val < 1.0:
            current_dry += 1
        else:
            break

    grounding = {
        "location": location_name,
        "consecutive_dry_days": current_dry,
        "dry_day_threshold_mm": 1.0,
        "source": "Open-Meteo Reanalysis",
    }

    if lang == "te":
        if current_dry >= 14:
            eval_te = "ఇది సుదీర్ఘ వర్షాభావ పరిస్థితి. వర్షాధార పంటలకు నీటి ఎద్దడి తీవ్రంగా ఉంటుంది."
        elif current_dry >= 7:
            eval_te = "ఇది మోస్తరు వర్షాభావ కాలం. నేలలోని తేమ క్రమంగా తగ్గుతుంటుంది."
        else:
            eval_te = "ఇటీవలే వర్షపు జల్లులు నమోదయ్యాయి. ప్రస్తుతానికి సుదీర్ఘ వర్షాభావం లేదు."

        resp = (
            f"☀️ **{location_name}** వర్షాభావ పరిస్థితి (Dry Spell Status):\n\n"
            f"- ⏳ **గడిచిన వరుస వర్షాభావ రోజులు:** `{current_dry} రోజులు` (రోజువారీ వర్షం < 1.0 మి.మీ)\n"
            f"- 📋 **పరిస్థితి విశ్లేషణ:** {eval_te}\n\n"
            f"💡 *గమనిక:* నేలలో తేమ నిల్వ ఉండటం అనేది కేవలం వర్షం లేని రోజుల పైనే కాకుండా, "
            f"నేల రకం మరియు ఇచ్చే నీటి తడులపై ఆధారపడి ఉంటుంది."
        )
    else:
        if current_dry >= 14:
            eval_en = "This represents an extended dry spell. Rainfed plots face elevated moisture deficits."
        elif current_dry >= 7:
            eval_en = "This indicates a moderate dry interval. Evaporative moisture depletion is active."
        else:
            eval_en = "A rainfall event occurred recently. No extended meteorological dry spell is currently active."

        resp = (
            f"☀️ Dry Spell Intelligence for **{location_name}**:\n\n"
            f"- ⏳ **Consecutive Dry Days:** `{current_dry} days` (daily precipitation < 1.0 mm)\n"
            f"- 📋 **Meteorological Evaluation:** {eval_en}\n\n"
            f"💡 *Agronomic Context:* A low dry-day count does not automatically guarantee long-term root-zone stability; "
            f"actual soil moisture retention depends on soil texture, canopy shading, and regular irrigation intervals."
        )

    return {"response": resp, "grounding_data": grounding}
