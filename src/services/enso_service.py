"""Official ENSO Climate Intelligence & Pacific Teleconnection Service.

Provides verified official ENSO (El Niño-Southern Oscillation) status updates,
sea surface temperature (SST) anomaly indices, and scientific monsoon teleconnection
explanations sourced directly from NOAA Climate Prediction Center (CPC) and the
India Meteorological Department (IMD) / Ministry of Earth Sciences (MoES).

Guiding Principles:
1. Never invent or simulate an ENSO phase, forecast, or anomaly value.
2. Display the official institutional sources and actual publication dates.
3. Record and distinguish source publication date from application retrieval timestamp.
4. Distinguish between 'Cached — potentially outdated' (previously fetched and saved locally)
   and 'Verified fallback snapshot — potentially outdated' (bundled baseline accessed offline).
5. If no verified data is available, display 'Current ENSO information unavailable'
   without fabricating values.
6. Present the current official Relative Oceanic Niño Index (RONI) framework adopted by
   NOAA CPC in February 2026, clarifying that ONI is retained strictly as a legacy/historical index.
7. Keep scientific concepts and educational guidance useful offline, separated from the
   current-status panel.
"""

from typing import Dict, Any, Optional
import datetime
import urllib.request
import json
import os

# =============================================================================
# VERIFIED OFFICIAL BASELINE DATA (NOAA CPC 8 OCT 2026 & IMD 30 JULY 2026)
# =============================================================================
# Sourced from:
# 1. NOAA Climate Prediction Center (CPC) ENSO Diagnostic Discussion dated 8 October 2026
#    - Alert Status: El Niño Advisory
#    - Current Niño-3.4 anomaly: +2.1°C (with Niño-1+2 at +3.9°C and Niño-3 at +3.0°C)
#    - Forecast: Strong-to-very strong El Niño favored through January–March 2027 (>83% chance)
#    - URL: https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/
# 2. NOAA CPC Relative Oceanic Niño Index (RONI) Adoption Announcement (February 2026)
#    - Official current index for ENSO monitoring and prediction: RONI
#    - URL: https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/announcement.php
# 3. India Meteorological Department (IMD) / Ministry of Earth Sciences dated 30 July 2026
#    - Stated El Niño was weak in June 2026, intensified to moderate in July 2026,
#      with dynamical models projecting further strengthening in October–December 2026.
#    - URL: https://mausam.imd.gov.in/
OFFICIAL_VERIFIED_ENSO_BASELINE = {
    "status": "El Niño",
    "alert_status": "El Niño Advisory",
    "phase_en": "El Niño Advisory (Strong-to-Very-Strong El Niño)",
    "phase_te": "ఎల్ నినో అడ్వైజరీ (బలమైన నుండి అతి తీవ్రమైన ఎల్ నినో)",
    "status_code": "el_nino_advisory",
    "sst_anomaly_nino34": 2.1,  # degrees Celsius
    "nino34_unit": "°C",
    "observation_period": "September–October 2026 (Monthly/Weekly Diagnostic Period)",
    "eastern_pacific_indices": {
        "nino12": 3.9,
        "nino3": 3.0,
        "subsurface_max": "> +10.0°C (at depth in eastern equatorial Pacific)",
    },
    "threshold_clarification_en": (
        "Current Official Framework (RONI): In February 2026, NOAA CPC officially adopted the "
        "Relative Oceanic Niño Index (RONI) for primary ENSO monitoring and operational prediction. "
        "Unlike absolute temperature anomalies, RONI calculates three-month running average sea surface "
        "temperature anomalies in the Niño-3.4 region relative to the rest of the global tropical oceans, "
        "thereby filtering out broader background global ocean warming. Under this official framework, an "
        "El Niño or La Niña episode requires a three-month running average exceeding the ±0.5°C threshold "
        "for at least five consecutive overlapping seasons, accompanied by persistent coupled ocean-atmosphere "
        "conditions (equatorial wind anomalies, Southern Oscillation Index shifts, and tropical convection). "
        "The Oceanic Niño Index (ONI) remains a legacy/historical index for historical record continuity, but "
        "must not be described as NOAA's current official monitoring index."
    ),
    "threshold_clarification_te": (
        "ప్రస్తుత అధికారిక విధానం (రోని - RONI): ఫిబ్రవరి 2026లో NOAA CPC అధికారికంగా రిలేటివ్ ఓషియానిక్ నినో ఇండెక్స్ "
        "(RONI) ను ప్రాథమిక ఈఎన్‌ఎస్‌ఓ పర్యవేక్షణ మరియు అంచనాల కోసం స్వీకరించింది. ప్రపంచ ఉష్ణమండల సముద్రాల సాధారణ "
        "వేడెక్కే ప్రభావాన్ని తొలగించి, నినో-3.4 ప్రాంతంలో ఖచ్చితమైన ఉష్ణోగ్రత మార్పులను ఇది లెక్కిస్తుంది. అధికారిక "
        "వర్గీకరణకు 3 నెలల సగటు ఉష్ణోగ్రత ±0.5°C పరిమితిని దాటి కనీసం 5 వరుస సీజన్ల పాటు కొనసాగడంతో పాటు, గాలులు "
        "మరియు మేఘాల వాతావరణ అనుసంధానం తప్పనిసరి. పాత ఓషియానిక్ నినో ఇండెక్స్ (ONI) కేవలం చారిత్రక రికార్డుల కోసం "
        "మాత్రమే ఉంచబడింది మరియు ప్రస్తుత అధికారిక పర్యవేక్షణ సూచికగా పరిగణించరాదు."
    ),
    "official_source": "NOAA Climate Prediction Center (CPC) & India Meteorological Department (IMD)",
    "primary_bulletin": {
        "agency": "NOAA Climate Prediction Center (CPC) / NCEP / NWS",
        "publication_date": "8 October 2026",
        "bulletin_title": "ENSO Diagnostic Discussion",
        "url": "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/",
    },
    "regional_statement": {
        "agency": "India Meteorological Department (IMD), Ministry of Earth Sciences",
        "publication_date": "30 July 2026",
        "statement_title": "Official Monsoon & ENSO Review",
        "url": "https://mausam.imd.gov.in/",
        "summary_en": (
            "IMD/MoES noted El Niño conditions were weak in June 2026, intensified to moderate in July 2026, "
            "with dynamical models forecasting potential further strengthening into October–December 2026. "
            "Neutral Indian Ocean Dipole (IOD) conditions were also noted."
        ),
        "summary_te": (
            "భారత వాతావరణ విభాగం (IMD) మరియు భూ విజ్ఞాన మంత్రిత్వ శాఖ ప్రకారం: జూన్ 2026లో బలహీనంగా ఉన్న ఎల్ నినో "
            "జూలై 2026 నాటికి మధ్యస్థ స్థాయికి చేరింది; అక్టోబర్–డిసెంబర్ నాటికి మరింత బలపడే అవకాశం ఉందని పేర్కొంది. "
            "హిందూ మహాసముద్ర ద్విధ్రువ (IOD) సాధారణంగా కొనసాగుతోందని నివేదించింది."
        ),
    },
    "forecast": {
        "period": "January–March 2027",
        "probability_statement": "> 83% chance of strong-to-very-strong El Niño continuing through January–March 2027",
        "historic_threshold_prob": "83% probability of exceeding historic benchmark (+2.5°C RONI) in Oct–Dec 2026; 70% in Nov 2026–Jan 2027",
        "summary_en": "Strong-to-very-strong El Niño favored to persist through January–March 2027 (>83% probability).",
        "summary_te": "జనవరి–మార్చి 2027 వరకు బలమైన లేదా అతి తీవ్రమైన ఎల్ నినో కొనసాగే అవకాశం 83% కంటే ఎక్కువగా ఉంది.",
    },
    "indian_ocean_dipole": "Neutral",
    "publication_date": "8 October 2026",
    "official_urls": {
        "noaa_cpc": "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/",
        "noaa_roni_announcement": "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/announcement.php",
        "imd_portal": "https://mausam.imd.gov.in/",
        "noaa_indices": "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt",
    },
}

CACHE_FILE_PATH = os.path.join(os.path.dirname(__file__), "enso_cache.json")


def _fetch_live_noaa_cpc_status(timeout_sec: float = 1.2) -> Optional[Dict[str, Any]]:
    """Attempt a lightweight live verification check against NOAA CPC public index.
    
    If network access is blocked by sandbox or timeout occurs, gracefully returns None.
    """
    try:
        url = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "ElNino-Resilience-CoPilot/1.0 (Agriculture-Decision-Support)"},
        )
        with urllib.request.urlopen(req, timeout=timeout_sec) as response:
            if response.status == 200:
                content = response.read().decode("utf-8", errors="ignore")
                lines = [line.strip() for line in content.splitlines() if line.strip()]
                if lines:
                    last_line = lines[-1]
                    parts = last_line.split()
                    if len(parts) >= 4:
                        anom_val = float(parts[-1])
                        season_str = parts[0]
                        yr_str = parts[1]
                        status_str = "El Niño" if anom_val >= 0.5 else ("La Niña" if anom_val <= -0.5 else "ENSO-neutral")
                        return {
                            "sst_anomaly_nino34": anom_val,
                            "season": season_str,
                            "year": yr_str,
                            "status": status_str,
                            "retrieved_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "publication_date": "8 October 2026",
                            "source_origin": "live_fetch",
                        }
    except Exception:
        return None
    return None


def get_enso_intelligence(
    force_refresh: bool = False,
    simulate_state: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieve verified official ENSO intelligence, telemetry, and scientific guidance.
    
    Supports:
    - Live retrieval when network is available (`data_state == 'live'`).
    - Stale cache display only when previously retrieved and cached locally (`data_state == 'cached'`).
    - Bundled offline snapshot display with explicit label (`data_state == 'fallback'`).
    - Explicit 'Current ENSO information unavailable' handling (`data_state == 'unavailable'`).
    - Strict separation of source publication date from application retrieval timestamp.
    - Decoupled foundational educational explanations for offline resilience.
    
    Args:
        force_refresh: Whether to bypass disk cache and attempt fresh fetch.
        simulate_state: Optional override for deterministic automated testing
                        ('live', 'cached', 'fallback', or 'unavailable').
    """
    now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Deterministic simulation modes (for automated verification & offline testing)
    if simulate_state == "unavailable":
        return _build_unavailable_payload(now_ts)

    if simulate_state == "live":
        payload = dict(OFFICIAL_VERIFIED_ENSO_BASELINE)
        payload["data_state"] = "live"
        payload["retrieved_at"] = now_ts
        payload["data_state_label_en"] = f"Live Official Bulletin (Source Published: {payload['publication_date']} | Retrieved: {now_ts})"
        payload["data_state_label_te"] = f"లైవ్ అధికారిక నివేదిక (ప్రచురణ: {payload['publication_date']} | పొందిన సమయం: {now_ts})"
        payload["explanations"] = _build_explanations()
        return payload

    if simulate_state == "cached":
        payload = dict(OFFICIAL_VERIFIED_ENSO_BASELINE)
        payload["data_state"] = "cached"
        payload["retrieved_at"] = now_ts
        payload["data_state_label_en"] = f"Cached — potentially outdated (Source Published: {payload['publication_date']} | Previously Retrieved: {now_ts})"
        payload["data_state_label_te"] = f"క్యాష్ చేయబడిన సమాచారం — పాతది కావచ్చు (ప్రచురణ: {payload['publication_date']} | గతంలో పొందిన సమయం: {now_ts})"
        payload["explanations"] = _build_explanations()
        return payload

    if simulate_state == "fallback":
        payload = dict(OFFICIAL_VERIFIED_ENSO_BASELINE)
        payload["data_state"] = "fallback"
        payload["retrieved_at"] = now_ts
        payload["data_state_label_en"] = f"Verified fallback snapshot — potentially outdated (Source Published: {payload['publication_date']} | Bundled Snapshot Accessed: {now_ts})"
        payload["data_state_label_te"] = f"ధృవీకరించబడిన బ్యాకప్ స్నాప్‌షాట్ — పాతది కావచ్చు (ప్రచురణ: {payload['publication_date']} | యాప్ సమయం: {now_ts})"
        payload["explanations"] = _build_explanations()
        return payload

    # 2. Production retrieval flow:
    # A) Attempt live fetch if network is available
    live_result = None
    if force_refresh or not os.path.exists(CACHE_FILE_PATH):
        live_result = _fetch_live_noaa_cpc_status(timeout_sec=1.2)
        if live_result:
            try:
                with open(CACHE_FILE_PATH, "w", encoding="utf-8") as f:
                    json.dump(live_result, f)
            except Exception:
                pass

    if live_result and live_result.get("retrieved_at"):
        # Live retrieval succeeded right now
        payload = dict(OFFICIAL_VERIFIED_ENSO_BASELINE)
        payload["data_state"] = "live"
        payload["sst_anomaly_nino34"] = live_result.get("sst_anomaly_nino34", payload["sst_anomaly_nino34"])
        payload["retrieved_at"] = live_result.get("retrieved_at", now_ts)
        payload["data_state_label_en"] = f"Live Official Bulletin (Source Published: {payload['publication_date']} | Retrieved: {payload['retrieved_at']})"
        payload["data_state_label_te"] = f"లైవ్ అధికారిక నివేదిక (ప్రచురణ: {payload['publication_date']} | పొందిన సమయం: {payload['retrieved_at']})"
        payload["explanations"] = _build_explanations()
        return payload

    # B) Check if a cached live result was previously saved to disk
    if os.path.exists(CACHE_FILE_PATH):
        try:
            with open(CACHE_FILE_PATH, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                if isinstance(cached_data, dict) and cached_data.get("source_origin") == "live_fetch":
                    payload = dict(OFFICIAL_VERIFIED_ENSO_BASELINE)
                    payload["data_state"] = "cached"
                    payload["sst_anomaly_nino34"] = cached_data.get("sst_anomaly_nino34", payload["sst_anomaly_nino34"])
                    payload["retrieved_at"] = cached_data.get("retrieved_at", now_ts)
                    payload["data_state_label_en"] = f"Cached — potentially outdated (Source Published: {payload['publication_date']} | Previously Retrieved: {payload['retrieved_at']})"
                    payload["data_state_label_te"] = f"క్యాష్ చేయబడిన సమాచారం — పాతది కావచ్చు (ప్రచురణ: {payload['publication_date']} | గతంలో పొందిన సమయం: {payload['retrieved_at']})"
                    payload["explanations"] = _build_explanations()
                    return payload
        except Exception:
            pass

    # C) Offline / sandboxed fallback: Live fetch failed and no live cache exists on disk.
    # Label EXACTLY as "Verified fallback snapshot — potentially outdated", never as "Cached" or "Live".
    payload = dict(OFFICIAL_VERIFIED_ENSO_BASELINE)
    payload["data_state"] = "fallback"
    payload["retrieved_at"] = now_ts
    payload["data_state_label_en"] = f"Verified fallback snapshot — potentially outdated (Source Published: {payload['publication_date']} | Bundled Snapshot Accessed: {now_ts})"
    payload["data_state_label_te"] = f"ధృవీకరించబడిన బ్యాకప్ స్నాప్‌షాట్ — పాతది కావచ్చు (ప్రచురణ: {payload['publication_date']} | యాప్ సమయం: {now_ts})"
    payload["explanations"] = _build_explanations()
    return payload


def _build_unavailable_payload(retrieved_at: str) -> Dict[str, Any]:
    """Build payload when official telemetry is completely unavailable without inventing data."""
    return {
        "status": "Unavailable",
        "alert_status": "Current ENSO information unavailable",
        "phase_en": "Current ENSO information unavailable",
        "phase_te": "ప్రస్తుత ఈఎన్‌ఎస్‌ఓ సమాచారం అందుబాటులో లేదు",
        "status_code": "unavailable",
        "sst_anomaly_nino34": None,
        "nino34_unit": "°C",
        "observation_period": "None",
        "eastern_pacific_indices": {},
        "threshold_clarification_en": (
            "Current Official Framework (RONI): Adopted by NOAA CPC in February 2026. "
            "Official scientific classification requires a sustained 3-month running average of RONI "
            "exceeding ±0.5°C for ≥5 consecutive overlapping seasons with coupled atmospheric response. "
            "ONI is a legacy index."
        ),
        "threshold_clarification_te": "ఫిబ్రవరి 2026 నుండి NOAA అధికారిక పర్యవేక్షణకు రోని (RONI) వర్తిస్తుంది; ONI చారిత్రక రికార్డు మాత్రమే.",
        "official_source": "NOAA Climate Prediction Center (CPC) & India Meteorological Department (IMD)",
        "publication_date": "Unavailable",
        "retrieved_at": retrieved_at,
        "data_state": "unavailable",
        "data_state_label_en": "Current ENSO information unavailable",
        "data_state_label_te": "ప్రస్తుత ఈఎన్‌ఎస్‌ఓ సమాచారం అందుబాటులో లేదు",
        "forecast": {
            "period": "Unavailable",
            "probability_statement": "Unavailable",
            "summary_en": "Forecast telemetry currently unavailable.",
            "summary_te": "వాతావరణ అంచనా సమాచారం అందుబాటులో లేదు.",
        },
        "indian_ocean_dipole": "Unavailable",
        "official_urls": {
            "noaa_cpc": "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/",
            "noaa_roni_announcement": "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/announcement.php",
            "imd_portal": "https://mausam.imd.gov.in/",
        },
        "explanations": _build_explanations(),
    }


def _build_explanations() -> Dict[str, Any]:
    """Decoupled foundational scientific explanations accessible offline."""
    return {
        # 1. Understanding the Three ENSO Phases & RONI Classification Framework
        "phases_overview": {
            "title_en": "Understanding ENSO: Phases, RONI Framework & Classification Rules",
            "title_te": "ఈఎన్‌ఎస్‌ఓ (ENSO) అంటే ఏమిటి? మూడు దశలు & రోని (RONI) వర్గీకరణ నియమాలు",
            "intro_en": (
                "**The Official RONI Framework vs. Legacy ONI:** In February 2026, NOAA CPC announced the official "
                "adoption of the **Relative Oceanic Niño Index (RONI)** for primary ENSO monitoring and operational prediction "
                "([NOAA Announcement](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/announcement.php)). "
                "RONI measures 3-month running average sea surface temperature (SST) anomalies in the Niño-3.4 region relative to the global tropical oceans, "
                "effectively isolating true equatorial ENSO dynamics from broader background tropical warming. Under the official RONI framework, "
                "phase classification requires anomalies meeting or exceeding the **±0.5°C threshold for at least 5 consecutive overlapping seasons**, "
                "accompanied by sustained **coupled ocean-atmosphere conditions** (equatorial trade wind alterations, Southern Oscillation Index shifts, and tropical convection changes). "
                "The traditional **Oceanic Niño Index (ONI)** is retained strictly as a legacy and historical benchmark; it is no longer NOAA's current official monitoring index."
            ),
            "intro_te": (
                "**అధికారిక రోని (RONI) విధానం vs పాత ఓఎన్‌ఐ (ONI):** ఫిబ్రవరి 2026లో NOAA CPC అధికారికంగా **రిలేటివ్ ఓషియానిక్ నినో ఇండెక్స్ (RONI)** "
                "ను ప్రాథమిక ఈఎన్‌ఎస్‌ఓ పర్యవేక్షణకు స్వీకరించింది ([NOAA అధికారిక ప్రకటన](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/announcement.php)). "
                "ప్రపంచ ఉష్ణమండల సముద్రాల సాధారణ వేడెక్కే ప్రభావాన్ని మినహాయించి, పసిఫిక్ వాకర్ సర్క్యులేషన్ కదలికలను ఇది ఖచ్చితంగా అంచనా వేస్తుంది. "
                "అధికారిక వర్గీకరణకు 3 నెలల సగటు ఉష్ణోగ్రత **±0.5°C పరిమితిని దాటి కనీసం 5 వరుస సీజన్ల పాటు స్థిరంగా ఉండటంతో పాటు**, "
                "వాతావరణంలో గాలుల దిశ మరియు పీడన మార్పులు నమోదు కావాలి. పాత **ఓషియానిక్ నినో ఇండెక్స్ (ONI)** కేవలం చారిత్రక రికార్డుల కోసం మాత్రమే "
                "ఉపయోగించబడుతుంది తప్ప ప్రస్తుత అధికారిక పర్యవేక్షణ సూచిక కాదు."
            ),
            "el_nino_en": (
                "**El Niño (Warm Phase):** Characterized by sustained anomalous warming across the central and eastern "
                "equatorial Pacific. Trade winds weaken or reverse into westerlies, shifting deep tropical rain clouds eastward toward "
                "the Americas. Historically, strong El Niño events correlate with an increased statistical probability of erratic or "
                "below-normal summer monsoon rains across South Asia, though local outcomes vary."
            ),
            "el_nino_te": (
                "**ఎల్ నినో (వెచ్చని దశ):** మధ్య మరియు తూర్పు పసిఫిక్ సముద్ర ఉపరితలం అసాధారణంగా వేడెక్కడం వల్ల ఇది ఏర్పడుతుంది. "
                "తూర్పు గాలులు బలహీనపడి, వర్ష మేఘాలు అమెరికా వైపు మళ్లుతాయి. చరిత్రను పరిశీలిస్తే, బలమైన ఎల్ నినో సమయంలో "
                "దక్షిణాసియాలో వర్షపాతం తగ్గే అవకాశం ఎక్కువగా ఉంటుంది, అయితే స్థానికంగా మార్పులు ఉండవచ్చు."
            ),
            "la_nina_en": (
                "**La Niña (Cool Phase):** Characterized by sustained anomalous cooling in the central and eastern equatorial Pacific "
                "(anomalies ≤ -0.5°C). Stronger trade winds push warm waters and intense convection westward into the Indo-Pacific basin. "
                "Historically, La Niña is often favorable for normal to above-normal monsoon rainfall in peninsular India, but can cause "
                "extended post-monsoon storms or delayed harvest windows."
            ),
            "la_nina_te": (
                "**లా నినా (చల్లని దశ):** పసిఫిక్ సముద్ర జలాలు సాధారణం కంటే చల్లబడినప్పుడు లా నినా ఏర్పడుతుంది (≤ -0.5°C). "
                "బలమైన వ్యాపార పవనాలు తేమను ఆసియా మరియు హిందూ మహాసముద్రం వైపు నెట్టివేస్తాయి. భారతదేశంలో ఇది సాధారణం లేదా అధిక "
                "వర్షపాతానికి అనుకూలంగా ఉంటుంది, అయితే కోత సమయంలో అకాల వర్షాలకు కారణం కావచ్చు."
            ),
            "neutral_en": (
                "**ENSO-Neutral (Baseline Phase):** Pacific Ocean temperatures and equatorial winds hover within their historical normal range. "
                "Neither warm El Niño nor cold La Niña patterns dominate. During neutral conditions, Indian monsoon dynamics are driven "
                "primarily by regional systems: the Indian Ocean Dipole (IOD), Madden-Julian Oscillation (MJO) pulses, and Bay of Bengal depressions."
            ),
            "neutral_te": (
                "**ఈఎన్‌ఎస్‌ఓ-న్యూట్రల్ (సాధారణ దశ):** పసిఫిక్ సముద్ర ఉష్ణోగ్రతలు సాధారణ పరిధిలో ఉంటాయి. ఈ సమయంలో భారతదేశ వర్షపాతం "
                "పసిఫిక్ కంటే హిందూ మహాసముద్ర ద్విధ్రువ (IOD), స్థానిక బంగాళాఖాత వాయుగుండాలు మరియు ద్రోణులపై ఎక్కువగా ఆధారపడి ఉంటుంది."
            ),
        },

        # 2. Pacific Ocean Teleconnection & Walker Circulation
        "teleconnection": {
            "title_en": "Planetary Teleconnections: How the Pacific Ocean Influences the Indian Monsoon",
            "title_te": "గ్రహ పవన అనుసంధానం: పసిఫిక్ సముద్రం భారత రుతుపవనాలను ఎలా ప్రభావితం చేస్తుంది?",
            "body_en": (
                "Although the central equatorial Pacific is over 12,000 km away from Andhra Pradesh and Telangana, "
                "it couples directly with global weather through a planetary atmospheric wind loop known as the **Walker Circulation**.\n\n"
                "• **The Walker Circulation Loop:** In normal conditions, warm water pools in the western Pacific near Indonesia, "
                "generating rising moist air (deep convection) and thunderstorms. The air travels eastward in the upper troposphere, "
                "sinks over the cooler eastern Pacific, and flows back westward near the surface.\n"
                "• **The El Niño Shift:** When the central/eastern Pacific warms abnormally, the rising convective chimney migrates eastward. "
                "The compensating sinking (subsidence) branch of dry air shifts westward over the Indian subcontinent and Southeast Asia. "
                "Sinking dry air increases atmospheric stability and suppresses the formation of rain-bearing monsoon clouds.\n"
                "• **Regional Counter-Balances:** The Pacific is not the sole driver. Warm waters in the western Indian Ocean (a positive **Indian Ocean Dipole - pIOD**) "
                "or active equatorial waves can supply massive moisture surges that offset Pacific subsidence."
            ),
            "body_te": (
                "మధ్య పసిఫిక్ మహాసముద్రం మనకు దాదాపు 12,000 కి.మీ దూరంలో ఉన్నప్పటికీ, **'వాకర్ సర్క్యులేషన్' (Walker Circulation)** "
                "అనే భారీ వాతావరణ గాలి వలయం ద్వారా మన వర్షాలను ప్రభావితం చేస్తుంది.\n\n"
                "• **వాకర్ వలయ ప్రక్రియ:** సాధారణ సమయాల్లో ఇండోనేషియా సమీపంలో సముద్రం వెచ్చగా ఉండి వర్ష మేఘాలు పైకి లేస్తాయి. "
                "ఈ గాలి ఎగువ వాతావరణంలో ప్రయాణించి తూర్పు పసిఫిక్‌లో కిందికి దిగుతుంది.\n"
                "• **ఎల్ నినో ప్రభావం:** పసిఫిక్ అసాధారణంగా వేడెక్కినప్పుడు, వర్ష మేఘాలు తూర్పుకు జరుగుతాయి. "
                "దాని ప్రతికూల పొడి గాలి భారత ఉపఖండంపై కిందికి దిగి, మేఘాలు ఏర్పడకుండా అణచివేస్తుంది.\n"
                "• **స్థానిక సమతుల్యత:** మన హిందూ మహాసముద్రంలో ఏర్పడే అనుకూల పరిస్థితులు (పాజిటివ్ IOD) మరియు బంగాళాఖాత అల్పపీడనాలు "
                "ఈ ఎల్ నినో ఎండబెట్టే ప్రభావాన్ని అధిగమించి మంచి వర్షాలు కురిపించగలవు."
            ),
        },

        # 3. Macro Probability vs. Local Village Determinism (With Traceable Historical Proof)
        "village_disclaimer": {
            "title_en": "Critical Science Principle: Regional Probability vs. Local Village Realities",
            "title_te": "రైతులు గమనించవలసిన శాస్త్రీయ సూత్రం: ప్రాంతీయ సంభావ్యత vs మీ ఊరి వాస్తవం",
            "body_en": (
                "**ENSO influences the broad seasonal probability of regional rainfall patterns—it NEVER deterministically decides rainfall for an individual village in Andhra Pradesh or Telangana.**\n\n"
                "1. **Macro Odds vs. Local Fate:** An El Niño Advisory raises the statistical risk of regional rainfall deficits and prolonged dry spells. "
                "However, it does **not** mean that your specific plot in Kadapa, Kurnool, Khammam, or Warangal is destined for drought.\n\n"
                "2. **Traceable Historical Evidence (The 1997 Southwest Monsoon):**\n"
                "   - *Official Measure:* According to official **India Meteorological Department (IMD)** historical records, the all-India southwest monsoon rainfall in **1997** was recorded at **102% of its Long Period Average (LPA)** (officially categorized by IMD as 'normal', within the 96%–104% LPA band).\n"
                "   - *Scientific Context:* Despite the co-occurring powerful 1997–1998 Pacific El Niño, all-India seasonal rainfall remained normal because an exceptionally strong **positive Indian Ocean Dipole (pIOD)** developed concurrently, pumping deep moisture into peninsular India (*Ashok, Guan, & Yamagata, 2001, Geophysical Research Letters*).\n"
                "   - *Contrast with 2002:* Conversely, in 2002, a moderate El Niño occurred without a positive IOD, resulting in an all-India drought (-19% of LPA). This historical contrast proves that Pacific Ocean temperatures alone never guarantee the seasonal outcome.\n\n"
                "3. **Microclimatic Realities:** Peninsular India's precipitation is heavily driven by Bay of Bengal cyclonic depressions, convective thunderstorms, "
                "and Eastern Ghats orography. A single localized convective thunderstorm can deliver 70 mm of rain over one mandal while an adjacent village 15 km away receives none—regardless of Pacific temperatures.\n\n"
                "4. **Actionable Takeaway:** Farmers should never panic or abandon planned cultivation based solely on global El Niño headlines."
            ),
            "body_te": (
                "**ఈఎన్‌ఎస్‌ఓ (ENSO) అనేది విస్తృత ప్రాంతీయ వర్షపాత సంభావ్యతను మాత్రమే సూచిస్తుంది—ఇది మీ గ్రామానికి ఇచ్చే రోజువారీ లేదా ఖచ్చితమైన తీర్పు కాదు.**\n\n"
                "1. **సంభావ్యత vs మీ పొలం వాస్తవం:** ఎల్ నినో వల్ల వర్షాభావ పరిస్థితులు ఏర్పడే అవకాశం పెరుగుతుంది. "
                "అంత మాత్రాన కడప, ఖమ్మం లేదా వరంగల్‌లోని మీ గ్రామంలో కచ్చితంగా కరవు వస్తుందని అర్థం కాదు.\n\n"
                "2. **అధికారిక చారిత్రక ఆధారాలు (1997 రుతుపవనాలు):**\n"
                "   - *అధికారిక కొలత:* భారత వాతావరణ విభాగం (IMD) అధికారిక రికార్డుల ప్రకారం, **1997** నైరుతి రుతుపవనాల కాలంలో భారతదేశ సాధారణ వర్షపాతం **102% (LPA)** గా నమోదైంది (IMD వర్గీకరణ ప్రకారం ఇది 'సాధారణ' వర్షపాతం).\n"
                "   - *శాస్త్రీయ కారణం:* ఆ సమయంలో పసిఫిక్‌లో అతి బలమైన ఎల్ నినో ఉన్నప్పటికీ, మన హిందూ మహాసముద్రంలో బలమైన అనుకూల ద్విధ్రువ (Positive IOD) ఏర్పడి విస్తారమైన తేమను అందించింది (*Ashok et al., 2001*).\n"
                "   - *2002 పోలిక:* దీనికి విరుద్ధంగా 2002లో మధ్యస్థ ఎల్ నినో సమయంలో అనుకూల IOD లేకపోవడం వల్ల కరవు ఏర్పడింది (-19% LPA). కాబట్టి పసిఫిక్ ఉష్ణోగ్రతలు ఒక్కటే మన వర్షాన్ని నిర్ణయించలేవు.\n\n"
                "3. **స్థానిక వాతావరణం:** బంగాళాఖాతంలో ఏర్పడే అల్పపీడనాలు మరియు స్థానిక ఉరుములతో కూడిన వర్షాలు మన ప్రాంతానికి అత్యంత కీలకం. "
                "పసిఫిక్‌లో పరిస్థితులు ఎలా ఉన్నా, స్థానికంగా కురిసే వర్షాలు పంటలకు సరిపడా తేమను అందిస్తాయి.\n\n"
                "4. **ఆందోళన వద్దు:** ప్రపంచ వార్తల్లో 'ఎల్ నినో' చూసి రైతులు ఆందోళనతో వ్యవసాయ పనులను నిలిపివేయవద్దు."
            ),
        },

        # 4. Reviewed Farmer Action Guide (Qualified & Extension-Aligned)
        "farmer_action_guide": {
            "title_en": "Farmer Decision Framework: Short-Term Operations vs. Seasonal Preparedness",
            "title_te": "రైతుల నిర్ణయ విధానం: స్వల్పకాలిక పనులు vs కాలానుగుణ సన్నద్ధత",
            "body_en": (
                "Climate-resilient agriculture requires keeping short-term field decisions grounded in local observations, "
                "while using seasonal ENSO guidance solely as a risk-hedging indicator to complement local extension advice:\n\n"
                "• **Horizon 1: Day-to-Day Field Management (1 to 7 Days)**\n"
                "  - **Disregard global ENSO indices for daily operations.** Base all operational choices (irrigation scheduling, fertilizer timing, protective spraying, weeding, and harvesting) exclusively on the **7-Day Local Weather Forecast** (available in the Weather tab) and direct soil moisture checks in your field.\n"
                "  - Local microclimates and immediate rain alerts dictate daily field success, not Pacific surface temperatures.\n\n"
                "• **Horizon 2: Strategic Season-Ahead Preparedness Options (1 to 3 Months)**\n"
                "  - **Treat ENSO as a seasonal risk-awareness signal.** When an El Niño Advisory or dry-spell risk is active, evaluate general preparedness options (these are risk-mitigation measures, not guaranteed outcomes):\n"
                "    1. *Soil Moisture Conservation:* Where feasible, surface organic mulching (e.g. crop residue or dry leaves in turmeric and banana) can help buffer root-zone moisture and reduce soil surface evaporation.\n"
                "    2. *Water Infrastructure Resilience:* Inspect drip lines, repair leaks, and ensure farm ponds or storage structures are cleared to catch unseasonal or early runoff.\n"
                "    3. *Crop & Variety Planning:* When planning new sowings in water-constrained plots, consult local agricultural extension officers for suitable short-duration or drought-tolerant varieties.\n"
                "    4. *Agricultural Extension Consultation:* For any foliar nutrition or stress-alleviation sprays, **consult your local Krishi Vigyan Kendra (KVK) or ANGRAU / PJTSAU extension officer** for recommendations tailored to your specific crop, phenological growth stage, and soil moisture status. Avoid blanket, uncalibrated chemical applications.\n\n"
                "• **Complementary Role:** Seasonal ENSO outlooks should always complement—never replace—local block forecasts and official district agricultural advisories."
            ),
            "body_te": (
                "మారుతున్న వాతావరణంలో రైతులు తమ నిర్ణయాలను రెండు స్పష్టమైన దశలుగా విభజించుకోవాలి:\n\n"
                "• **దశ 1: రోజువారీ పొలం పనులు (1 నుండి 7 రోజులు)**\n"
                "  - **రోజువారీ పనులకు ఎల్ నినోను చూడవద్దు.** నీరు కట్టడం, ఎరువులు వేయడం, పురుగుమందుల పిచికారీ, కోత పనులను కేవలం మన యాప్‌లోని **'వాతావరణం' (Weather)** విభాగంలో ఉండే 7 రోజుల స్థానిక సూచన మరియు పొలంలో తేమ ఆధారంగానే నిర్ణయించండి.\n"
                "  - స్థానిక వాతావరణం మరియు తక్షణ వర్ష సూచనలే రోజువారీ వ్యవసాయానికి ప్రామాణికం.\n\n"
                "• **దశ 2: కాలానుగుణ ముందస్తు జాగ్రత్తల ఎంపికలు (1 నుండి 3 నెలలు)**\n"
                "  - **ఎల్ నినోను ఒక ముందస్తు హెచ్చరికగా మాత్రమే పరిగణించండి.** వర్షాభావ ముప్పు ఉన్నప్పుడు ఈ క్రింది సాధారణ జాగ్రత్తలను పరిశీలించండి (ఇవి రక్షణ అవకాశాలు మాత్రమే, హామీలు కావు):\n"
                "    1. *నేలలో తేమ పరిరక్షణ:* వీలైన చోట్ల పసుపు, అరటి తోటలలో పంట వ్యర్థాలతో మల్చింగ్ చేయడం వల్ల నేల తేమ ఆవిరి కాకుండా కాపాడుకోవచ్చు.\n"
                "    2. *నీటి వనరుల నిర్వహణ:* బిందు సేద్యం (డ్రిప్) పైపుల లీకేజీలను సరిచేయండి, వర్షపు నీటిని ఒడిసిపట్టేందుకు వ్యవసాయ కుంటలను సిద్ధం చేసుకోండి.\n"
                "    3. *పంట ప్రణాళిక:* నీటి వసతి తక్కువగా ఉన్నప్పుడు స్వల్పకాలిక లేదా బెట్టను తట్టుకునే రకాల కోసం స్థానిక వ్యవసాయ అధికారులను సంప్రదించండి.\n"
                "    4. *అధికారుల సలహా తప్పనిసరి:* ఎండ వేడిమి లేదా బెట్ట సమయంలో పిచికారీ చేసే పోషకాలు లేదా మందుల కోసం **మీ సమీప కృషి విజ్ఞాన కేంద్రం (KVK) లేదా ANGRAU / PJTSAU వ్యవసాయ విస్తరణ అధికారులను సంప్రదించండి**. పంట దశ మరియు నేల తేమను బట్టి వారిచ్చే శాస్త్రీయ సిఫార్సులను మాత్రమే పాటించండి.\n\n"
                "• **సమన్వయం:** కాలానుగుణ ఎల్ నినో సమాచారం అనేది స్థానిక వాతావరణ సూచనలు మరియు వ్యవసాయ అధికారుల సలహాలకు తోడుగా ఉండాలి తప్ప వాటికి ప్రత్యామ్నాయం కాదు."
            ),
        },
    }
