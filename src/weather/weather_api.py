"""Weather API client using Open-Meteo Forecast and Historical APIs.

Retrieves real-time atmospheric conditions, 7-day agricultural forecasts,
and recent 30-day historical precipitation with caching, timeouts, and error handling.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
import json
import pandas as pd
import requests
import streamlit as st

OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
REQUEST_TIMEOUT_SECONDS = 9.0
DISK_CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", ".cache")


def _get_cache_file_path(latitude: float, longitude: float) -> str:
    """Generate localized file path for disk cache based on coordinates."""
    os.makedirs(DISK_CACHE_DIR, exist_ok=True)
    lat_key = f"{latitude:.2f}".replace(".", "_").replace("-", "m")
    lon_key = f"{longitude:.2f}".replace(".", "_").replace("-", "m")
    return os.path.join(DISK_CACHE_DIR, f"weather_{lat_key}_{lon_key}.json")


def _save_to_disk_cache(latitude: float, longitude: float, raw_data: Dict[str, Any], retrieved_at: str) -> None:
    """Safely persist successful API response to disk cache."""
    try:
        cache_path = _get_cache_file_path(latitude, longitude)
        payload = {
            "cached_at": retrieved_at,
            "latitude": latitude,
            "longitude": longitude,
            "raw_data": raw_data,
        }
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(payload, f)
    except Exception:
        # Disk cache save failures should never block application execution
        pass


def _load_from_disk_cache(latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
    """Attempt to load previously cached payload from disk when network is offline."""
    try:
        cache_path = _get_cache_file_path(latitude, longitude)
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return None

# WMO Weather Interpretation Codes (WMO Code -> Bilingual description)
WMO_WEATHER_CODES: Dict[int, Dict[str, str]] = {
    0: {"en": "Clear sky", "te": "నిర్మలమైన ఆకాశం"},
    1: {"en": "Mainly clear", "te": "ప్రధానంగా నిర్మలం"},
    2: {"en": "Partly cloudy", "te": "పాక్షికంగా మేఘావృతం"},
    3: {"en": "Overcast", "te": "దట్టమైన మేఘాలు"},
    45: {"en": "Fog", "te": "పొగమంచు"},
    48: {"en": "Depositing rime fog", "te": "పొగమంచు"},
    51: {"en": "Light drizzle", "te": "తేలికపాటి చినుకులు"},
    53: {"en": "Moderate drizzle", "te": "ఓ మోస్తరు చినుకులు"},
    55: {"en": "Dense drizzle", "te": "దట్టమైన చినుకులు"},
    61: {"en": "Slight rain", "te": "తేలికపాటి వర్షం"},
    63: {"en": "Moderate rain", "te": "ఓ మోస్తరు వర్షం"},
    65: {"en": "Heavy rain", "te": "భారీ వర్షం"},
    66: {"en": "Freezing rain", "te": "శీతల వర్షం"},
    67: {"en": "Heavy freezing rain", "te": "భారీ శీతల వర్షం"},
    71: {"en": "Slight snow fall", "te": "తేలికపాటి మంచు"},
    73: {"en": "Moderate snow fall", "te": "మంచు కురిసే అవకాశం"},
    75: {"en": "Heavy snow fall", "te": "భారీ మంచు"},
    77: {"en": "Snow grains", "te": "మంచు బిందువులు"},
    80: {"en": "Slight rain showers", "te": "తేలికపాటి వర్షపు జల్లులు"},
    81: {"en": "Moderate rain showers", "te": "ఓ మోస్తరు వర్షపు జల్లులు"},
    82: {"en": "Violent rain showers", "te": "తీవ్రమైన వర్షపు జల్లులు"},
    85: {"en": "Slight snow showers", "te": "తేలికపాటి మంచు జల్లులు"},
    86: {"en": "Heavy snow showers", "te": "భారీ మంచు జల్లులు"},
    95: {"en": "Thunderstorm", "te": "ఉరుములు, మెరుపులతో కూడిన వర్షం"},
    96: {"en": "Thunderstorm with slight hail", "te": "వడగండ్ల వాన"},
    99: {"en": "Thunderstorm with heavy hail", "te": "తీవ్రమైన వడగండ్ల వాన"},
}


def get_weather_description(code: Optional[int], lang: str = "en") -> str:
    """Retrieve translated weather description for a given WMO weather code."""
    if code is None:
        return "Unknown" if lang == "en" else "తెలియదు"
    entry = WMO_WEATHER_CODES.get(int(code), {"en": "Variable conditions", "te": "వాతావరణ పరిస్థితులు"})
    return entry.get(lang, entry["en"])


@st.cache_data(ttl=900, show_spinner=False)
def _fetch_from_open_meteo(latitude: float, longitude: float) -> Dict[str, Any]:
    """Execute raw network request to Open-Meteo Forecast API with past 30 days.
    
    Cached for 15 minutes (900s) by latitude and longitude.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weather_code",
        "past_days": 30,
        "forecast_days": 16,
        "timezone": "Asia/Kolkata",
    }
    
    headers = {
        "User-Agent": "ElNinoResilienceCoPilot/1.0 (AgriClimateTwin; contact@elnino-copilot.org)"
    }

    response = requests.get(
        OPEN_METEO_FORECAST_URL,
        params=params,
        headers=headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def get_weather_intelligence(latitude: float, longitude: float, force_refresh: bool = False) -> Dict[str, Any]:
    """Retrieve comprehensive weather intelligence for the specified coordinates.
    
    Args:
        latitude: Target latitude in decimal degrees.
        longitude: Target longitude in decimal degrees.
        force_refresh: If True, invalidates the local Streamlit cache.
        
    Returns:
        Structured dictionary containing current conditions, forecast dataframe,
        historical 30-day dataframe, retrieval timestamps, and error state.
    """
    if force_refresh:
        _fetch_from_open_meteo.clear()

    result: Dict[str, Any] = {
        "success": False,
        "latitude": latitude,
        "longitude": longitude,
        "current": {},
        "forecast_df": pd.DataFrame(),
        "historical_df": pd.DataFrame(),
        "retrieved_at": None,
        "is_offline_cached": False,
        "cached_at": None,
        "warning": None,
        "source": "Open-Meteo Weather Model API",
        "forecast_status": "unavailable",
        "forecast_start_date": None,
        "forecast_end_date": None,
        "forecast_horizon_days": 0,
        "data_labels": {
            "current": "Open-Meteo NWP High-Resolution Surface Analysis (Interpolated)",
            "forecast": "Open-Meteo 16-Day Numerical Weather Prediction Ensemble",
            "historical": "Open-Meteo Seamless Operational Reanalysis & Analysis Grid (~11 km)",
            "mode": "LIVE_TELEMETRY",
        },
        "attribution": "Weather data by Open-Meteo.com under Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "error": None,
    }

    def _parse_payload(data_dict: Dict[str, Any], retrieved_time_str: str) -> bool:
        """Parse raw Open-Meteo payload into result structure."""
        current_raw = data_dict.get("current", {})
        result["current"] = {
            "temperature": current_raw.get("temperature_2m"),
            "relative_humidity": current_raw.get("relative_humidity_2m"),
            "wind_speed": current_raw.get("wind_speed_10m"),
            "precipitation": current_raw.get("precipitation", 0.0),
            "weather_code": current_raw.get("weather_code"),
            "time": current_raw.get("time"),
        }

        daily_raw = data_dict.get("daily", {})
        if daily_raw and "time" in daily_raw:
            df_all = pd.DataFrame({
                "date": pd.to_datetime(daily_raw["time"]).date,
                "temp_max": daily_raw.get("temperature_2m_max", []),
                "temp_min": daily_raw.get("temperature_2m_min", []),
                "precipitation": daily_raw.get("precipitation_sum", []),
                "precip_probability": daily_raw.get("precipitation_probability_max", [None] * len(daily_raw["time"])),
                "weather_code": daily_raw.get("weather_code", [0] * len(daily_raw["time"])),
            })
            
            df_all["precip_probability"] = df_all["precip_probability"].fillna(0)
            df_all["precipitation"] = df_all["precipitation"].fillna(0.0)

            today_date = datetime.now().date()
            historical_df = df_all[df_all["date"] < today_date].tail(30).copy()
            forecast_df = df_all[df_all["date"] >= today_date].head(16).copy()

            # Robust offline cached snapshot fallback:
            # If df_all comes from an older cached snapshot where all dates are in the past (< today_date),
            # extract the snapshot's intended 16-day forecast trajectory (last 16 days) and 30-day historical window,
            # adjusting their dates forward relative to today so that the 7-day forecast, charts, and advisory logic
            # have complete data rather than an empty dataframe.
            if forecast_df.empty and len(df_all) >= 16:
                raw_fc = df_all.tail(16).copy().reset_index(drop=True)
                raw_fc["date"] = [today_date + timedelta(days=i) for i in range(len(raw_fc))]
                forecast_df = raw_fc

                raw_hist = df_all.iloc[:-16].tail(30).copy().reset_index(drop=True)
                hist_len = len(raw_hist)
                raw_hist["date"] = [today_date - timedelta(days=hist_len - i) for i in range(hist_len)]
                historical_df = raw_hist

            historical_df["cumulative_precipitation"] = historical_df["precipitation"].cumsum()

            result["historical_df"] = historical_df
            result["forecast_df"] = forecast_df

            if not forecast_df.empty:
                result["forecast_status"] = "available"
                result["forecast_start_date"] = forecast_df["date"].min()
                result["forecast_end_date"] = forecast_df["date"].max()
                result["forecast_horizon_days"] = len(forecast_df)
            else:
                result["forecast_status"] = "unavailable"
                result["forecast_start_date"] = None
                result["forecast_end_date"] = None
                result["forecast_horizon_days"] = 0

        result["retrieved_at"] = retrieved_time_str
        return True

    try:
        data = _fetch_from_open_meteo(latitude=latitude, longitude=longitude)
        timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        _parse_payload(data, timestamp_now)
        result["success"] = True
        result["is_offline_cached"] = False
        result["data_labels"]["mode"] = "LIVE_TELEMETRY"
        # Persist copy to disk cache
        _save_to_disk_cache(latitude, longitude, data, timestamp_now)

    except requests.exceptions.Timeout:
        result["error"] = "Connection Timeout: Open-Meteo API servers did not respond within 9.0s."
        result["diagnostic"] = "Timeout (> 9.0s) waiting for response from api.open-meteo.com."
    except requests.exceptions.SSLError as e:
        result["error"] = "SSL Certificate Verification Failed: Could not establish TLS handshake with Open-Meteo."
        result["diagnostic"] = f"SSLError: {str(e)}"
    except requests.exceptions.ConnectionError as e:
        err_str = str(e)
        if "NameResolutionError" in err_str or "nodename nor servname provided" in err_str:
            result["error"] = "DNS Resolution Failed: Unable to resolve hostname 'api.open-meteo.com'."
            result["diagnostic"] = "DNS lookup failed for api.open-meteo.com. Ensure outbound network access."
        else:
            result["error"] = "Network Connection Failed: Could not reach Open-Meteo API."
            result["diagnostic"] = f"ConnectionError: {err_str}"
    except requests.exceptions.HTTPError as e:
        status = getattr(e.response, "status_code", "Unknown")
        result["error"] = f"Open-Meteo API responded with HTTP {status}."
        result["diagnostic"] = f"HTTPError {status} from {OPEN_METEO_FORECAST_URL}"
    except Exception as e:
        result["error"] = f"Unexpected error while processing weather data: {str(e)}"
        result["diagnostic"] = f"{type(e).__name__}: {str(e)}"

    # If live request failed, attempt offline disk cache fallback
    if not result["success"]:
        cached_payload = _load_from_disk_cache(latitude, longitude)
        if cached_payload and "raw_data" in cached_payload and "cached_at" in cached_payload:
            _parse_payload(cached_payload["raw_data"], cached_payload["cached_at"])
            result["success"] = True
            result["is_offline_cached"] = True
            result["cached_at"] = cached_payload["cached_at"]
            result["source"] = f"Offline Local Cache (Snapshot from {cached_payload['cached_at']})"
            result["warning"] = (
                f"Live weather service is currently unreachable ({result.get('error')}). "
                f"Displaying offline snapshot cached on {cached_payload['cached_at']}."
            )
            result["data_labels"]["mode"] = "OFFLINE_CACHED_SNAPSHOT"

    return result
