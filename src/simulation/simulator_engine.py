"""Transparent Mathematical Simulation Engine for Agricultural What-If Scenarios.

Grounds agricultural stress testing for Turmeric, Banana, and Paddy in Andhra Pradesh
and Telangana against real weather baselines, ICAR/ANGRAU physiological limits, and
explicit water demand balance calculations.

Core Principles:
1. Reference weather is transparently derived from Open-Meteo operational analysis (~11 km grid).
2. Linear extrapolation for 60/90 days is explicitly disclosed as an illustrative benchmark,
   not an empirical 30-year IMD climatological normal.
3. Crop phenological stages are inferred strictly when a valid sowing date is provided.
   Silent fallbacks or assumed ages are prohibited.
4. Outputs are rule-based decision-support indices, never claiming econometric yield loss predictions.
"""

from typing import Dict, Any, List, Optional, Tuple
import datetime
import pandas as pd

from src.knowledge.crop_knowledge import (
    get_crop_profile,
    get_growth_stage_by_days,
)
from src.weather.location_service import get_district_coordinates
from src.weather.weather_api import get_weather_intelligence


# Daily crop evapotranspiration baselines (ETc in mm/day) by phenological stage
# Source: ICAR-IISR (Turmeric), ICAR-NRCB (Banana), ICAR-IIRR (Paddy), ANGRAU
CROP_ET_BASELINES: Dict[str, Dict[str, float]] = {
    "Turmeric": {
        "Sprouting & Vegetative": 2.5,
        "Tillering & Rhizome Initiation": 4.2,
        "Rhizome Development & Bulking": 5.5,
        "Maturity & Leaf Senescence": 2.2,
        "_default": 4.0,
    },
    "Banana": {
        "Vegetative & Sucker Management": 4.8,
        "Shooting & Bunch Emergence": 5.8,
        "Bunch Development & Finger Filling": 6.2,
        "Harvest Maturity": 3.5,
        "_default": 5.5,
    },
    "Paddy": {
        "Nursery & Seedling Establishment": 4.0,
        "Active Tillering": 6.5,
        "Panicle Initiation & Booting": 7.5,
        "Flowering / Anthesis": 8.5,
        "Grain Filling & Dough Stage": 5.5,
        "Maturity": 2.5,
        "_default": 6.8,
    },
}


def get_baseline_climate(
    farm_profile: Dict[str, Any],
    weather_data: Optional[Dict[str, Any]] = None,
    duration_days: int = 30,
) -> Dict[str, Any]:
    """Extract transparent baseline climate parameters from telemetry or regional defaults.
    
    Args:
        farm_profile: Active digital twin dictionary with district, state, village.
        weather_data: Optional pre-fetched weather intelligence dictionary.
        duration_days: Target scenario duration (30, 60, or 90 days).
        
    Returns:
        Structured baseline dictionary with rainfall, baseline temperature,
        data provenance labels, and extrapolation disclosures.
    """
    state = farm_profile.get("state", "Andhra Pradesh")
    district = farm_profile.get("district", "Kadapa (YSR Kadapa)")
    village = farm_profile.get("village", "").strip()

    if weather_data is None:
        coords = get_district_coordinates(state=state, district=district, village=village)
        weather_data = get_weather_intelligence(coords["latitude"], coords["longitude"], force_refresh=False)

    duration = int(duration_days) if duration_days in [30, 60, 90] else 30
    scale_factor = duration / 30.0

    hist_df = weather_data.get("historical_df", pd.DataFrame())
    fc_df = weather_data.get("forecast_df", pd.DataFrame())
    is_live_success = weather_data.get("success", False)

    has_hist = (
        isinstance(hist_df, pd.DataFrame)
        and not hist_df.empty
        and "precipitation" in hist_df.columns
        and "temp_max" in hist_df.columns
    )

    if has_hist:
        obs_30_rain = float(hist_df["precipitation"].sum())
        obs_30_temp_max_mean = float(hist_df["temp_max"].mean())

        # Thermal regime: blend past 30 days mean peak with 7-day forecast peak if available
        if isinstance(fc_df, pd.DataFrame) and not fc_df.empty and "temp_max" in fc_df.columns:
            fc_7_temp_max_mean = float(fc_df["temp_max"].mean())
            baseline_temp = round(max(obs_30_temp_max_mean, fc_7_temp_max_mean), 1)
        else:
            baseline_temp = round(obs_30_temp_max_mean, 1)

        baseline_rain = round(obs_30_rain * scale_factor, 1)
        is_illustrative = False
        source_label = (
            f"Open-Meteo Operational Analysis Grid (~11 km) scaled from past 30-day accumulation "
            f"({obs_30_rain:.1f} mm for {district})"
        )
        uncertainty_note = (
            f"Baseline rainfall for {duration} days ({baseline_rain:.1f} mm) is derived from "
            f"recent 30-day operational grid estimates ({obs_30_rain:.1f} mm) scaled linearly. "
            f"This serves as an illustrative benchmark for farm stress-testing, not an official 30-year IMD climatological normal."
        )
    else:
        # Fallback to regional illustrative baseline when telemetry is unreachable
        obs_30_rain = 50.0  # Regional illustrative 30-day baseline
        baseline_rain = round(obs_30_rain * scale_factor, 1)
        baseline_temp = 33.5
        is_illustrative = True
        source_label = "Illustrative Regional Baseline (Live weather telemetry unavailable)"
        uncertainty_note = (
            f"Weather telemetry was unavailable. Using an illustrative baseline of {baseline_rain:.1f} mm "
            f"and {baseline_temp}°C for {duration} days. Field verification recommended."
        )

    return {
        "duration_days": duration,
        "scale_factor": scale_factor,
        "baseline_rainfall_mm": baseline_rain,
        "baseline_temp_c": baseline_temp,
        "observed_30d_rainfall_mm": round(obs_30_rain, 1),
        "is_illustrative": is_illustrative,
        "source_label": source_label,
        "uncertainty_note": uncertainty_note,
        "district": district,
    }


def get_crop_phenology(
    crop: str,
    sowing_date_val: Optional[Any] = None,
) -> Dict[str, Any]:
    """Resolve crop phenological stage strictly from saved sowing date without silent guessing."""
    has_valid_sowing = False
    days_in_field: Optional[int] = None
    stage_name = "Not determined (sowing date required)"
    water_need = "General baseline"

    if sowing_date_val:
        try:
            if isinstance(sowing_date_val, datetime.date):
                s_date = sowing_date_val
            else:
                s_date = datetime.date.fromisoformat(str(sowing_date_val).strip())

            if s_date <= datetime.date.today():
                days_in_field = max(0, (datetime.date.today() - s_date).days)
                has_valid_sowing = True
                stage_info = get_growth_stage_by_days(crop, days_in_field)
                stage_name = stage_info.get("stage", stage_name)
                water_need = stage_info.get("water_need", water_need)
        except Exception:
            has_valid_sowing = False
            days_in_field = None

    # Retrieve daily ET demand
    crop_et_dict = CROP_ET_BASELINES.get(crop, CROP_ET_BASELINES["Turmeric"])
    if has_valid_sowing and stage_name in crop_et_dict:
        daily_et_mm = crop_et_dict[stage_name]
    else:
        daily_et_mm = crop_et_dict["_default"]

    return {
        "crop": crop,
        "has_valid_sowing": has_valid_sowing,
        "days_in_field": days_in_field,
        "stage_name": stage_name,
        "water_need": water_need,
        "daily_et_mm": daily_et_mm,
    }


def calculate_scenario(
    baseline: Dict[str, Any],
    crop_profile: Dict[str, Any],
    farm_profile: Dict[str, Any],
    rain_reduction_pct: float = 0.0,
    temp_increase_c: float = 0.0,
    irrigation_status: str = "Normal",
    scenario_name: str = "Custom Scenario",
) -> Dict[str, Any]:
    """Execute transparent mathematical scenario calculations for a single configuration.
    
    Args:
        baseline: Output from get_baseline_climate.
        crop_profile: Crop profile dictionary from crop_knowledge.py.
        farm_profile: Active farm profile dictionary.
        rain_reduction_pct: Rainfall reduction percentage (0.0 to 60.0).
        temp_increase_c: Temperature increase in °C (0.0 to 5.0).
        irrigation_status: "Normal", "Limited", or "Unavailable".
        scenario_name: Descriptive scenario label.
        
    Returns:
        Comprehensive scenario result dictionary.
    """
    # 1. Parameter Bounds Enforcement
    rain_red = max(0.0, min(60.0, float(rain_reduction_pct)))
    temp_inc = max(0.0, min(5.0, float(temp_increase_c)))
    irr_status = irrigation_status if irrigation_status in ["Normal", "Limited", "Unavailable"] else "Normal"
    duration = int(baseline.get("duration_days", 30))

    crop = farm_profile.get("crop", "Turmeric")
    sowing_date = farm_profile.get("sowing_date")
    pheno = get_crop_phenology(crop, sowing_date)

    # 2. Rainfall Calculations
    base_rain = float(baseline.get("baseline_rainfall_mm", 50.0))
    scenario_rain = round(max(0.0, base_rain * (1.0 - (rain_red / 100.0))), 1)
    rain_deficit = round(base_rain - scenario_rain, 1)

    # 3. Temperature Calculations
    base_temp = float(baseline.get("baseline_temp_c", 33.5))
    scenario_temp = round(base_temp + temp_inc, 1)

    # 4. Crop Water Demand & Hydrological Balance
    total_water_demand = round(pheno["daily_et_mm"] * duration, 1)

    # Irrigation efficiency factor (eta_irr)
    irr_factors = {"Normal": 1.0, "Limited": 0.5, "Unavailable": 0.0}
    eta_irr = irr_factors[irr_status]

    # Required supplemental irrigation after rainfall
    irr_needed = max(0.0, total_water_demand - scenario_rain)
    irr_supplied = round(eta_irr * irr_needed, 1)

    # Total effective water supply
    effective_water = round(scenario_rain + irr_supplied, 1)
    net_moisture_deficit = round(max(0.0, total_water_demand - effective_water), 1)

    if total_water_demand > 0:
        water_satisfaction_pct = round(min(100.0, (effective_water / total_water_demand) * 100.0), 1)
    else:
        water_satisfaction_pct = 100.0

    # 5. Thermal Stress Evaluation
    opt_temp = crop_profile.get("optimal_temperature_c", {"min": 20.0, "max": 35.0, "stress_above": 38.0})
    stress_thresh = float(opt_temp.get("stress_above", 38.0))
    opt_max = float(opt_temp.get("max", 35.0))

    if scenario_temp <= opt_max:
        thermal_level = "Normal"
        thermal_score = 1.0
        thermal_note_en = f"Temperatures ({scenario_temp}°C) remain within optimal range ({opt_temp['min']}-{opt_max}°C)."
        thermal_note_te = f"ఉష్ణోగ్రతలు ({scenario_temp}°C) అనుకూల పరిధిలో ({opt_temp['min']}-{opt_max}°C) ఉన్నాయి."
    elif scenario_temp <= stress_thresh:
        thermal_level = "Watch"
        thermal_score = 5.0
        thermal_note_en = (
            f"Elevated temperatures ({scenario_temp}°C) exceed optimal {opt_max}°C. "
            f"Moderate transpirational water loss expected."
        )
        thermal_note_te = (
            f"ఉష్ణోగ్రతలు ({scenario_temp}°C) అనుకూల పరిమితి ({opt_max}°C) కంటే పెరిగాయి. "
            f"ఆకుల నుండి నీటి ఆవిరి వేగం పెరుగుతుంది."
        )
    else:
        thermal_level = "Alert"
        thermal_score = 9.5
        if crop == "Paddy":
            thermal_score = 10.0
            thermal_note_en = (
                f"Critical thermal threshold ({stress_thresh}°C) breached at {scenario_temp}°C! "
                f"Severe spikelet sterility and floret desiccation risk if crop is flowering."
            )
            thermal_note_te = (
                f"తీవ్రమైన ఉష్ణోగ్రత హెచ్చరిక ({scenario_temp}°C)! పూత దశలో ఉంటే తాలు గింజలు వచ్చే ప్రమాదం అత్యధికం."
            )
        else:
            thermal_note_en = (
                f"Severe thermal stress threshold ({stress_thresh}°C) breached at {scenario_temp}°C! "
                f"Triggers stomatal closure, leaf-tip scorch, and vegetative wilting."
            )
            thermal_note_te = (
                f"తీవ్రమైన ఉష్ణోగ్రత హెచ్చరిక ({scenario_temp}°C)! ఆకుల చివర్లు మాడిపోవడం మరియు వడలిపోవడం జరుగుతుంది."
            )

    # 6. Hydrological Deficit Evaluation
    if water_satisfaction_pct >= 90.0:
        hydro_level = "Normal"
        hydro_score = 1.0
        hydro_note_en = f"Water satisfaction is high ({water_satisfaction_pct}% of {total_water_demand} mm demand)."
        hydro_note_te = f"నీటి లభ్యత సమృద్ధిగా ఉంది ({water_satisfaction_pct}% లభ్యత)."
    elif water_satisfaction_pct >= 70.0:
        hydro_level = "Watch"
        hydro_score = 4.5
        hydro_note_en = (
            f"Mild moisture deficit ({water_satisfaction_pct}% satisfaction). "
            f"Net deficit is {net_moisture_deficit} mm."
        )
        hydro_note_te = (
            f"స్వల్ప నీటి కొరత ({water_satisfaction_pct}% లభ్యత). నికర లోటు {net_moisture_deficit} మి.మీ."
        )
    elif water_satisfaction_pct >= 50.0:
        hydro_level = "Alert"
        hydro_score = 7.5
        hydro_note_en = (
            f"Significant water stress ({water_satisfaction_pct}% satisfaction). "
            f"Irrigation shortage leaves a {net_moisture_deficit} mm deficit."
        )
        hydro_note_te = (
            f"గణనీయమైన నీటి ఎద్దడి ({water_satisfaction_pct}% లభ్యత). {net_moisture_deficit} మి.మీ లోటు ఏర్పడింది."
        )
    else:
        hydro_level = "Emergency"
        hydro_score = 10.0
        hydro_note_en = (
            f"Critical moisture crisis ({water_satisfaction_pct}% satisfaction). "
            f"Severe deficit of {net_moisture_deficit} mm threatens vegetative survival."
        )
        hydro_note_te = (
            f"తీవ్రమైన నీటి సంక్షోభం ({water_satisfaction_pct}% మాత్రమే లభ్యం). "
            f"{net_moisture_deficit} మి.మీ నీటి లోటు వల్ల పంట ఎండిపోయే ప్రమాదం ఉంది."
        )

    # 7. Composite Multi-Factor Risk Score
    composite_score = round(0.45 * thermal_score + 0.55 * hydro_score, 1)

    if composite_score < 3.0:
        overall_risk = "Low"
        overall_risk_te = "సాధారణం (Low Risk)"
        risk_color = "#2D6A4F"
        badge_bg = "#E8F5E9"
    elif composite_score < 6.0:
        overall_risk = "Moderate"
        overall_risk_te = "మితమైన రిస్క్ (Moderate Risk - Watch)"
        risk_color = "#E08700"
        badge_bg = "#FFF8E1"
    elif composite_score < 8.5:
        overall_risk = "High"
        overall_risk_te = "అధిక రిస్క్ (High Risk - Alert)"
        risk_color = "#D9534F"
        badge_bg = "#FFEBEE"
    else:
        overall_risk = "Critical"
        overall_risk_te = "తీవ్రమైన రిస్క్ (Critical - Emergency)"
        risk_color = "#990000"
        badge_bg = "#FFCDD2"

    # 8. Practical Precautions Formulations
    precautions_en: List[Dict[str, str]] = []
    precautions_te: List[Dict[str, str]] = []

    # Thermal precautions
    if thermal_level in ["Watch", "Alert"]:
        if crop == "Turmeric":
            precautions_en.append({
                "title": "Organic Surface Mulching",
                "details": "Apply 10-12 tons/ha of paddy straw or green leaf mulch to buffer root-zone soil temperatures and curb evaporation.",
                "source": "ICAR-IISR & ANGRAU",
            })
            precautions_te.append({
                "title": "వరి గడ్డి లేదా పచ్చి రొట్టతో మల్చింగ్",
                "details": "ఎకరానికి 4-5 టన్నుల వరి గడ్డితో మల్చింగ్ చేయడం వల్ల నేల వేడెక్కకుండా తేమ ఎక్కువ కాలం నిల్వ ఉంటుంది.",
                "source": "ICAR-IISR & ANGRAU",
            })
        elif crop == "Banana":
            precautions_en.append({
                "title": "Bunch Sleeving & Sun Protection",
                "details": "Cover developing fruit bunches with perforated non-woven polypropylene sleeves to shield against sunburn.",
                "source": "ICAR-NRCB",
            })
            precautions_te.append({
                "title": "గెలలకు రక్షణ తొడుగులు (స్లీవ్స్)",
                "details": "ఎండ తీవ్రత నుండి గెలలను రక్షించడానికి రంధ్రాలు ఉన్న పాలిథిన్ కవర్లతో గెలలను కప్పాలి.",
                "source": "ICAR-NRCB",
            })
        elif crop == "Paddy":
            precautions_en.append({
                "title": "Standing Water Buffer during Flowering",
                "details": "Maintain 3-5 cm standing water in the field during panicle initiation and anthesis to lower canopy temperatures.",
                "source": "ICAR-IIRR",
            })
            precautions_te.append({
                "title": "పూత సమయంలో నీటి నిల్వ",
                "details": "పూత మరియు చిరుపొట్ట దశలలో పొలంలో 3-5 సెం.మీ నీరు ఉంచడం ద్వారా వేడిమిని తగ్గించి తాలు కాయకుండా కాపాడవచ్చు.",
                "source": "ICAR-IIRR",
            })

    # Hydrological precautions
    if hydro_level in ["Watch", "Alert", "Emergency"]:
        if crop == "Paddy":
            precautions_en.append({
                "title": "Alternate Wetting and Drying (AWD)",
                "details": "Implement AWD during vegetative tillering: irrigate only when field water level drops 15 cm below soil surface.",
                "source": "ICAR-IIRR",
            })
            precautions_te.append({
                "title": "ఆరబెట్టి తడపడం (AWD పద్ధతి)",
                "details": "ఎదుగుదల దశలో నిరంతరం నీరు నిలబెట్టకుండా నేలలో తడి ఆరిన తర్వాత మళ్లీ తడి ఇవ్వడం ద్వారా 25-30% నీటిని ఆదా చేయవచ్చు.",
                "source": "ICAR-IIRR",
            })
        elif crop == "Banana":
            precautions_en.append({
                "title": "Drip Irrigation Rationing",
                "details": "Operate drip systems during early morning or evening hours to minimize evaporative loss; prioritize shooting-stage plants.",
                "source": "ICAR-NRCB",
            })
            precautions_te.append({
                "title": "డ్రిప్ ద్వారా క్రమబద్ధమైన తడులు",
                "details": "ఉదయం లేదా సాయంత్రం వేళల్లో మాత్రమే డ్రిప్ ద్వారా నీరు అందించి ఆవిరి నష్టాన్ని తగ్గించాలి.",
                "source": "ICAR-NRCB",
            })
        else:
            precautions_en.append({
                "title": "Deficit Irrigation & Drainage Trench Management",
                "details": "Confine irrigations to alternate furrows and apply light frequent waterings to safeguard rhizome expansion.",
                "source": "ICAR-IISR",
            })
            precautions_te.append({
                "title": "విడతలవారీ తేలికపాటి తడులు",
                "details": "కాలువల ద్వారా ఒక సాలు విడిచి ఒక సాలుకు నీరివ్వడం ద్వారా అందుబాటులో ఉన్న నీటితో ఎక్కువ విస్తీర్ణాన్ని కాపాడవచ్చు.",
                "source": "ICAR-IISR",
            })

    # Foliar emergency spray for severe compound stress
    if composite_score >= 6.0:
        precautions_en.append({
            "title": "Foliar Potassium Spray (1% KNO3 / MOP)",
            "details": "Spray 10 g/L Potassium Nitrate or Sulfate of Potash to improve stomatal regulation and osmotic stress tolerance.",
            "source": "ANGRAU & PJTSAU",
        })
        precautions_te.append({
            "title": "పొటాషియం నైట్రేట్ (1%) పిచికారీ",
            "details": "లీటరు నీటికి 10 గ్రాముల పొటాషియం నైట్రేట్ (13-0-45) కలిపి పిచికారీ చేయడం వల్ల పైరు ఎండ వేడిమి మరియు నీటి కొరతను తట్టుకుంటుంది.",
            "source": "ANGRAU & PJTSAU",
        })

    # Default general resilience if conditions are normal
    if not precautions_en:
        precautions_en.append({
            "title": "Standard Agronomic Monitoring",
            "details": "Maintain standard soil moisture management and regular pest-disease monitoring as per local package of practices.",
            "source": "ANGRAU",
        })
        precautions_te.append({
            "title": "సాధారణ యాజమాన్య పద్ధతులు",
            "details": "సాధారణ పద్ధతులలో నీటి తడులు మరియు చీడపీడల నివారణ చర్యలను కొనసాగించండి.",
            "source": "ANGRAU",
        })

    return {
        "scenario_name": scenario_name,
        "duration_days": duration,
        "crop": crop,
        "inputs": {
            "rain_reduction_pct": rain_red,
            "temp_increase_c": temp_inc,
            "irrigation_status": irr_status,
        },
        "phenology": pheno,
        "rainfall": {
            "baseline_mm": base_rain,
            "scenario_mm": scenario_rain,
            "deficit_mm": rain_deficit,
            "reduction_pct": rain_red,
        },
        "temperature": {
            "baseline_c": base_temp,
            "scenario_c": scenario_temp,
            "increase_c": temp_inc,
            "stress_threshold_c": stress_thresh,
            "optimal_max_c": opt_max,
        },
        "water_balance": {
            "crop_demand_mm": total_water_demand,
            "daily_et_mm": pheno["daily_et_mm"],
            "effective_water_mm": effective_water,
            "irrigation_supplied_mm": irr_supplied,
            "net_deficit_mm": net_moisture_deficit,
            "satisfaction_pct": water_satisfaction_pct,
            "eta_irr": eta_irr,
        },
        "evaluations": {
            "thermal": {
                "level": thermal_level,
                "score": thermal_score,
                "note_en": thermal_note_en,
                "note_te": thermal_note_te,
            },
            "hydrological": {
                "level": hydro_level,
                "score": hydro_score,
                "note_en": hydro_note_en,
                "note_te": hydro_note_te,
            },
            "composite": {
                "score": composite_score,
                "risk_level": overall_risk,
                "risk_level_te": overall_risk_te,
                "color": risk_color,
                "badge_bg": badge_bg,
            },
        },
        "precautions_en": precautions_en,
        "precautions_te": precautions_te,
        "uncertainty_note": baseline.get("uncertainty_note", ""),
    }


def generate_comparison_scenarios(
    farm_profile: Dict[str, Any],
    weather_data: Optional[Dict[str, Any]] = None,
    duration_days: int = 30,
) -> Dict[str, Dict[str, Any]]:
    """Generate the standardized 4-scenario comparative assessment suite.
    
    A: Reference Baseline (0% rain reduction, +0°C, Normal irrigation)
    B: Reduced Rainfall (30% rain reduction, +0°C, Normal irrigation)
    C: Compound Heat & Drought (40% rain reduction, +2.5°C, Limited irrigation)
    D: Severe Irrigation Crisis (50% rain reduction, +3.0°C, Unavailable irrigation)
    
    Args:
        farm_profile: Active digital twin dictionary.
        weather_data: Pre-fetched weather intelligence dictionary or None.
        duration_days: 30, 60, or 90 days.
        
    Returns:
        Dictionary mapping scenario keys ('A', 'B', 'C', 'D') to calculation results.
    """
    baseline = get_baseline_climate(farm_profile, weather_data, duration_days=duration_days)
    crop = farm_profile.get("crop", "Turmeric")
    crop_info = get_crop_profile(crop)

    scenarios_config = {
        "A": {
            "name_en": "Scenario A: Reference Conditions",
            "name_te": "పరిస్థితి A: సాధారణ బేస్‌లైన్",
            "rain_red": 0.0,
            "temp_inc": 0.0,
            "irrigation": "Normal",
        },
        "B": {
            "name_en": "Scenario B: Reduced Rainfall (-30%)",
            "name_te": "పరిస్థితి B: వర్షపాతం తగ్గినప్పుడు (-30%)",
            "rain_red": 30.0,
            "temp_inc": 0.0,
            "irrigation": "Normal",
        },
        "C": {
            "name_en": "Scenario C: Drought + High Temperature",
            "name_te": "పరిస్థితి C: ఎండ తీవ్రత & కరువు",
            "rain_red": 40.0,
            "temp_inc": 2.5,
            "irrigation": "Limited",
        },
        "D": {
            "name_en": "Scenario D: Severe Irrigation Crisis",
            "name_te": "పరిస్థితి D: నీటి కొరత / కరువు సంక్షోభం",
            "rain_red": 50.0,
            "temp_inc": 3.0,
            "irrigation": "Unavailable",
        },
    }

    results = {}
    for key, cfg in scenarios_config.items():
        results[key] = calculate_scenario(
            baseline=baseline,
            crop_profile=crop_info,
            farm_profile=farm_profile,
            rain_reduction_pct=cfg["rain_red"],
            temp_increase_c=cfg["temp_inc"],
            irrigation_status=cfg["irrigation"],
            scenario_name=cfg["name_en"],
        )
        results[key]["key"] = key
        results[key]["name_te"] = cfg["name_te"]
        results[key]["name_en"] = cfg["name_en"]

    return {
        "baseline": baseline,
        "scenarios": results,
        "crop": crop,
        "duration_days": duration_days,
    }
