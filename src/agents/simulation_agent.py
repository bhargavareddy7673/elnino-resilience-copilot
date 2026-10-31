"""Simulation Agent: Specialist module for What-If scenario assessments and farmer queries.

Responsible for:
1. Grounding responses in actual calculated values from simulator_engine.py.
2. Answering comparative scenario questions, rainfall reductions, and irrigation constraints.
3. Formulating authentic ICAR/ANGRAU/PJTSAU precautions for hypothetical drought/thermal stress.
4. Strictly distinguishing hypothetical simulation stress tests from real-time weather forecasts.
"""

from typing import Dict, Any, List, Optional
import re

from src.simulation.simulator_engine import (
    generate_comparison_scenarios,
    calculate_scenario,
    get_baseline_climate,
)
from src.knowledge.crop_knowledge import get_crop_profile


def answer_simulation_query(
    query: str,
    farm_profile: Dict[str, Any],
    simulation_state: Optional[Dict[str, Any]] = None,
    weather_data: Optional[Dict[str, Any]] = None,
    lang: str = "en",
) -> Dict[str, Any]:
    """Generate precise, grounded response to agricultural What-If simulation queries.
    
    Args:
        query: Farmer query in English, Telugu, or code-mixed.
        farm_profile: Active digital twin dictionary.
        simulation_state: Pre-calculated simulation bundle or None.
        weather_data: Pre-fetched weather intelligence dictionary or None.
        lang: Active language ('en' or 'te').
        
    Returns:
        Structured response dictionary with response text, grounding data, and references.
    """
    crop = farm_profile.get("crop", "Turmeric")
    crop_info = get_crop_profile(crop)

    # 1. Ensure comparison suite is available
    if simulation_state and "scenarios" in simulation_state:
        sim_data = simulation_state
    else:
        sim_data = generate_comparison_scenarios(
            farm_profile=farm_profile,
            weather_data=weather_data,
            duration_days=30,
        )

    scenarios = sim_data["scenarios"]
    baseline = sim_data["baseline"]
    duration = sim_data.get("duration_days", 30)

    sc_a = scenarios["A"]
    sc_b = scenarios["B"]
    sc_c = scenarios["C"]
    sc_d = scenarios["D"]

    q_lower = query.lower()

    # Determine query intent type
    is_scenario_comparison = any(term in q_lower for term in [
        "which scenario", "most concerning", "highest risk", "compare", "scenarios",
        "ఏ పరిస్థితి", "ఎక్కువ ప్రమాదకరం", "ప్రమాదం", "పోలిక", "ఏది ఎక్కువ",
    ])
    is_irrigation_unavailable = any(term in q_lower for term in [
        "irrigation becomes unavailable", "no irrigation", "without irrigation", "irrigation unavailable",
        "నీటి సౌకర్యం లేకపోతే", "నీరు లేకపోతే", "నీరు అందకపోతే", "నీటి లభ్యత లేకపోతే",
    ])
    is_rainfall_reduction = any(term in q_lower for term in [
        "rainfall decreases", "if rainfall", "rain decreases", "rainfall drops", "వర్షాలు తగ్గితే", "వర్షం తగ్గితే",
        "30%", "20%", "40%", "50%", "తగ్గితే", "వర్షపాతం తగ్గితే",
    ])

    # -------------------------------------------------------------------------
    # CASE 1: SCENARIO COMPARISON ("Which scenario is most concerning?")
    # -------------------------------------------------------------------------
    if is_scenario_comparison:
        # Identify most concerning scenario by highest composite score
        sorted_scenarios = sorted(
            [sc_a, sc_b, sc_c, sc_d],
            key=lambda s: s["evaluations"]["composite"]["score"],
            reverse=True,
        )
        most_critical = sorted_scenarios[0]
        crit_key = most_critical.get("key", "D")
        crit_score = most_critical["evaluations"]["composite"]["score"]
        crit_risk = most_critical["evaluations"]["composite"]["risk_level"]
        crit_risk_te = most_critical["evaluations"]["composite"]["risk_level_te"]

        c_rain = most_critical["rainfall"]["scenario_mm"]
        c_red = most_critical["rainfall"]["reduction_pct"]
        c_temp = most_critical["temperature"]["scenario_c"]
        c_inc = most_critical["temperature"]["increase_c"]
        c_sat = most_critical["water_balance"]["satisfaction_pct"]
        c_def = most_critical["water_balance"]["net_deficit_mm"]

        grounding = {
            "query_type": "scenario_comparison",
            "crop": crop,
            "most_concerning_scenario": f"Scenario {crit_key}",
            "composite_score": crit_score,
            "risk_level": crit_risk,
            "scenario_rainfall_mm": c_rain,
            "scenario_temp_c": c_temp,
            "water_satisfaction_pct": c_sat,
            "net_deficit_mm": c_def,
            "duration_days": duration,
            "is_hypothetical_simulation": True,
        }

        if lang == "te":
            resp_lines = [
                f"🔮 **వాట్-ఇఫ్ సిమ్యులేషన్ విశ్లేషణ (ఊహాజనిత నమూనా — ప్రత్యక్ష సూచన కాదు):**\n",
                f"మీ **{crop_info['crop_name_te']} ({crop})** పంటకు **పరిస్థితి D (తీవ్రమైన నీటి కొరత / కరువు సంక్షోభం)** అత్యంత ప్రమాదకరమైనది (రిస్క్ స్కోర్: `{crit_score}/10` — `{crit_risk_te}`).\n",
                f"**📊 4 పరిస్థితుల ముఖ్యాంశాల పోలిక ({duration} రోజుల వ్యవధికి):**",
                f"- **పరిస్థితి A (సాధారణం):** వర్షపాతం `{sc_a['rainfall']['scenario_mm']} మి.మీ`, ఉష్ణోగ్రత `{sc_a['temperature']['scenario_c']}°C`, నీటి సంతృప్తి `{sc_a['water_balance']['satisfaction_pct']}%` (`{sc_a['evaluations']['composite']['risk_level']}`)",
                f"- **పరిస్థితి B (30% వర్ష లోటు):** వర్షపాతం `{sc_b['rainfall']['scenario_mm']} మి.మీ`, ఉష్ణోగ్రత `{sc_b['temperature']['scenario_c']}°C`, నీటి సంతృప్తి `{sc_b['water_balance']['satisfaction_pct']}%` (`{sc_b['evaluations']['composite']['risk_level']}`)",
                f"- **పరిస్థితి C (ఎండ + వర్షాభావం):** వర్షపాతం `{sc_c['rainfall']['scenario_mm']} మి.మీ`, ఉష్ణోగ్రత `{sc_c['temperature']['scenario_c']}°C` (+2.5°C), నీటి సంతృప్తి `{sc_c['water_balance']['satisfaction_pct']}%` (`{sc_c['evaluations']['composite']['risk_level']}`)",
                f"- **పరిస్థితి D (నీటి సంక్షోభం):** వర్షపాతం `{sc_d['rainfall']['scenario_mm']} మి.మీ` (-50%), ఉష్ణోగ్రత `{sc_d['temperature']['scenario_c']}°C` (+3.0°C), నీటి సంతృప్తి కేవలం `{sc_d['water_balance']['satisfaction_pct']}%` (`{sc_d['evaluations']['composite']['risk_level']}`)\n",
                f"⚠️ **పరిస్థితి D ఎందుకు అత్యంత ప్రమాదకరం:**",
                f"ఈ పరిస్థితిలో వర్షపాతం 50% తగ్గడంతో పాటు బోరుబావుల నీటి లభ్యత పూర్తిగా నిలిచిపోతుంది. దీనివల్ల పంటకు అవసరమైన నీటిలో కేవలం `{c_sat}%` మాత్రమే లభ్యమై, `{c_def} మి.మీ` తీవ్ర నీటి లోటు ఏర్పడుతుంది. ఉష్ణోగ్రత `{c_temp}°C`కి చేరినప్పుడు వేడిమి మరియు నీటి ఎద్దడి కలిసి పైరును తీవ్రంగా దెబ్బతీస్తాయి.\n",
                f"🛡️ **సిఫార్సు చేయబడిన రక్షణ చర్యలు:**",
                f"1. తక్షణమే ఎకరానికి 4-5 టన్నుల వరి గడ్డి లేదా పచ్చి రొట్టతో మల్చింగ్ చేయాలి.",
                f"2. ఎండ వేడిమి మరియు నీటి ఎద్దడిని తట్టుకోవడానికి 1% పొటాషియం నైట్రేట్ (10 గ్రా/లీ) పిచికారీ చేయాలి (ANGRAU సిఫార్సు).",
            ]
        else:
            resp_lines = [
                f"🔮 **What-If Simulation Assessment (Hypothetical Stress Test — Not Real Weather Forecast):**\n",
                f"For your **{crop} ({crop_info['botanical_name']})**, **Scenario D (Severe Irrigation Crisis)** is by far the most concerning scenario, evaluated at a composite risk score of `{crit_score}/10` (`{crit_risk}`).\n",
                f"**📊 Comparison across all 4 Evaluated Scenarios ({duration}-Day Horizon):**",
                f"- **Scenario A (Reference Baseline):** Rain `{sc_a['rainfall']['scenario_mm']} mm`, Temp `{sc_a['temperature']['scenario_c']}°C`, Water Satisfaction `{sc_a['water_balance']['satisfaction_pct']}%` (`{sc_a['evaluations']['composite']['risk_level']}`)",
                f"- **Scenario B (30% Rainfall Drop):** Rain `{sc_b['rainfall']['scenario_mm']} mm`, Temp `{sc_b['temperature']['scenario_c']}°C`, Water Satisfaction `{sc_b['water_balance']['satisfaction_pct']}%` (`{sc_b['evaluations']['composite']['risk_level']}`)",
                f"- **Scenario C (Drought + Heat):** Rain `{sc_c['rainfall']['scenario_mm']} mm`, Temp `{sc_c['temperature']['scenario_c']}°C` (+2.5°C), Water Satisfaction `{sc_c['water_balance']['satisfaction_pct']}%` (`{sc_c['evaluations']['composite']['risk_level']}`)",
                f"- **Scenario D (Severe Crisis):** Rain `{sc_d['rainfall']['scenario_mm']} mm` (-50%), Temp `{sc_d['temperature']['scenario_c']}°C` (+3.0°C), Water Satisfaction only `{sc_d['water_balance']['satisfaction_pct']}%` (`{sc_d['evaluations']['composite']['risk_level']}`)\n",
                f"⚠️ **Why Scenario D represents the greatest vulnerability:**",
                f"In Scenario D, a 50% precipitation shortfall is compounded by a total failure of supplemental irrigation. Your crop would experience an acute moisture deficit of `{c_def} mm`, meeting only `{c_sat}%` of its physiological demand. Combined with elevated canopy heat at `{c_temp}°C`, stomata close and transpirational cooling collapses.\n",
                f"🛡️ **Strategic Precautions (ICAR & ANGRAU):**",
                f"1. Apply 10-12 tons/ha of organic mulch (paddy straw or green manure) to suppress soil evaporation.",
                f"2. Apply foliar Potassium Nitrate (1% KNO3 @ 10 g/L) to enhance osmotic cell turgor under acute water stress.",
            ]

        return {
            "response": "\n".join(resp_lines),
            "grounding_data": grounding,
            "references": crop_info.get("references", []),
        }

    # -------------------------------------------------------------------------
    # CASE 2: RAINFALL REDUCTION ("What happens if rainfall decreases by 30%?")
    # -------------------------------------------------------------------------
    elif is_rainfall_reduction and not is_irrigation_unavailable:
        # Extract percentage if specified
        pct_match = re.search(r"(\d+)\s*%", query)
        target_pct = float(pct_match.group(1)) if pct_match else 30.0
        target_pct = max(0.0, min(60.0, target_pct))

        # Evaluate scenario with specified rain reduction and normal irrigation
        sc_rain = calculate_scenario(
            baseline=baseline,
            crop_profile=crop_info,
            farm_profile=farm_profile,
            rain_reduction_pct=target_pct,
            temp_increase_c=0.0,
            irrigation_status="Normal",
            scenario_name=f"Rainfall Reduction -{target_pct:.0f}%",
        )

        base_r = sc_rain["rainfall"]["baseline_mm"]
        scen_r = sc_rain["rainfall"]["scenario_mm"]
        def_r = sc_rain["rainfall"]["deficit_mm"]
        demand_w = sc_rain["water_balance"]["crop_demand_mm"]
        sat_w = sc_rain["water_balance"]["satisfaction_pct"]
        supp_w = sc_rain["water_balance"]["irrigation_supplied_mm"]
        risk_lvl = sc_rain["evaluations"]["composite"]["risk_level"]
        risk_lvl_te = sc_rain["evaluations"]["composite"]["risk_level_te"]

        grounding = {
            "query_type": "rainfall_reduction_impact",
            "crop": crop,
            "rain_reduction_pct": target_pct,
            "baseline_rainfall_mm": base_r,
            "scenario_rainfall_mm": scen_r,
            "rainfall_deficit_mm": def_r,
            "crop_water_demand_mm": demand_w,
            "irrigation_buffer_mm": supp_w,
            "water_satisfaction_pct": sat_w,
            "risk_level": risk_lvl,
            "duration_days": duration,
            "is_hypothetical_simulation": True,
        }

        if lang == "te":
            resp_lines = [
                f"🔮 **వాట్-ఇఫ్ సిమ్యులేషన్ విశ్లేషణ (ఊహాజనిత నమూనా — ప్రత్యక్ష సూచన కాదు):**\n",
                f"మీ **{crop_info['crop_name_te']} ({crop})** పంటపై వర్షపాతం **{target_pct:.0f}% తగ్గితే** ఏర్పడే ప్రభావం ({duration} రోజుల వ్యవధికి):\n",
                f"- 🌧️ **వర్షపాతం వివరాలు:** సాధారణ వర్షపాతం `{base_r} మి.మీ` నుండి `{scen_r} మి.మీ`కి తగ్గుతుంది (`{def_r} మి.మీ` వర్ష లోటు).",
                f"- 💧 **పంట నీటి అవసరం:** ఈ దశలో పంటకు మొత్తం `{demand_w} మి.మీ` నీరు అవసరం.",
                f"- 🛡️ **బోరుబావి/నీటి పారుదల రక్షణ:** మీ వద్ద సాధారణ నీటి పారుదల అందుబాటులో ఉంటే, బోరుబావి ద్వారా `{supp_w} మి.మీ` నీటిని అందించి నీటి సంతృప్తిని `{sat_w}%` వద్ద నిలకడగా ఉంచవచ్చు (రిస్క్: `{risk_lvl_te}`).\n",
                f"⚠️ **ముఖ్య గమనిక:** వర్షాలు తగ్గినప్పుడు నేలలో తేమ ఆరిపోకుండా రక్షించుకోవడానికి ముందస్తు చర్యలు అవసరం.",
                f"**చేయవలసిన పనులు:**",
                f"1. వరి గడ్డి లేదా రొట్టతో మల్చింగ్ చేసి తేమను ఆదా చేయండి.",
                f"2. నీటి తడులను ఒక సాలు విడిచి ఒక సాలుకు అందించడం (ఆల్టర్నేట్ ఫర్రో) ద్వారా నీటి వినియోగాన్ని 30% తగ్గించవచ్చు.",
            ]
        else:
            resp_lines = [
                f"🔮 **What-If Simulation Assessment (Hypothetical Stress Test — Not Real Weather Forecast):**\n",
                f"If rainfall decreases by **{target_pct:.0f}%** over the {duration}-day simulation horizon for your **{crop} ({crop_info['botanical_name']})**:\n",
                f"- 🌧️ **Rainfall Impact:** Expected rainfall drops from baseline `{base_r} mm` to `{scen_r} mm` (an atmospheric deficit of `{def_r} mm`).",
                f"- 💧 **Crop Water Requirement:** Estimated evapotranspirative demand is `{demand_w} mm`.",
                f"- 🛡️ **Irrigation Buffer:** With **Normal irrigation** available, supplemental borewell pumping can provide up to `{supp_w} mm`, maintaining `{sat_w}%` water satisfaction (Risk Level: `{risk_lvl}`).\n",
                f"⚠️ **Key Agronomic Vulnerability:** If groundwater levels decline or power rationing restricts pumping, this deficit immediately translates into root-zone moisture stress.",
                f"**Actionable Precautions (ICAR & ANGRAU):**",
                f"1. Implement surface mulching with paddy straw (10-12 t/ha) to suppress soil evaporative loss.",
                f"2. Switch to alternate-furrow irrigation or night-time drip operation to curtail evaporative losses.",
            ]

        return {
            "response": "\n".join(resp_lines),
            "grounding_data": grounding,
            "references": crop_info.get("references", []),
        }

    # -------------------------------------------------------------------------
    # CASE 3: IRRIGATION UNAVAILABLE ("What precautions if irrigation unavailable?")
    # -------------------------------------------------------------------------
    elif is_irrigation_unavailable:
        sc_unavail = calculate_scenario(
            baseline=baseline,
            crop_profile=crop_info,
            farm_profile=farm_profile,
            rain_reduction_pct=30.0,
            temp_increase_c=1.5,
            irrigation_status="Unavailable",
            scenario_name="Unavailable Irrigation Crisis",
        )

        base_r = sc_unavail["rainfall"]["baseline_mm"]
        scen_r = sc_unavail["rainfall"]["scenario_mm"]
        demand_w = sc_unavail["water_balance"]["crop_demand_mm"]
        net_def = sc_unavail["water_balance"]["net_deficit_mm"]
        sat_w = sc_unavail["water_balance"]["satisfaction_pct"]
        risk_lvl = sc_unavail["evaluations"]["composite"]["risk_level"]
        risk_lvl_te = sc_unavail["evaluations"]["composite"]["risk_level_te"]
        comp_score = sc_unavail["evaluations"]["composite"]["score"]

        grounding = {
            "query_type": "irrigation_unavailable_precautions",
            "crop": crop,
            "irrigation_status": "Unavailable",
            "scenario_rainfall_mm": scen_r,
            "crop_water_demand_mm": demand_w,
            "net_deficit_mm": net_def,
            "water_satisfaction_pct": sat_w,
            "composite_score": comp_score,
            "risk_level": risk_lvl,
            "duration_days": duration,
            "is_hypothetical_simulation": True,
        }

        if lang == "te":
            resp_lines = [
                f"🔮 **వాట్-ఇఫ్ సిమ్యులేషన్ విశ్లేషణ (ఊహాజనిత నమూనా — ప్రత్యక్ష సూచన కాదు):**\n",
                f"మీ **{crop_info['crop_name_te']} ({crop})** పంటకు **నీటి పారుదల సౌకర్యం పూర్తిగా నిలిచిపోతే (Unavailable Irrigation)** తీవ్ర సంక్షోభం ఏర్పడుతుంది (రిస్క్ స్కోర్: `{comp_score}/10` — `{risk_lvl_te}`).\n",
                f"- 💧 **లభ్యత & లోటు:** పంటకు `{demand_w} మి.మీ` నీరు అవసరం కాగా, కేవలం వర్షం ద్వారా `{scen_r} మి.మీ` మాత్రమే లభిస్తుంది (నీటి సంతృప్తి కేవలం `{sat_w}%`).",
                f"- 📉 **తీవ్రమైన నీటి లోటు:** `{net_def} మి.మీ` మేర లోటు ఏర్పడి పైరు ఎండిపోయే ప్రమాదం ఉంది.\n",
                f"🛡️ **తప్పనిసరిగా పాటించవలసిన అత్యవసర రక్షణ చర్యలు (ICAR & ANGRAU):**",
                f"1. **తక్షణ సేంద్రీయ మల్చింగ్:** ఎకరానికి 4 నుండి 5 టన్నుల వరి గడ్డి లేదా పచ్చి రొట్టతో మట్టి కనిపించకుండా మల్చింగ్ చేయండి. ఇది నేలలోని తేమ ఆవిరి కాకుండా కాపాడుతుంది.",
                f"2. **పొటాషియం పిచికారీ:** లీటరు నీటికి 10 గ్రాముల పొటాషియం నైట్రేట్ (13-0-45) లేదా MOP కలిపి పిచికారీ చేయండి. ఇది ఆకుల రంధ్రాల (స్టొమాటా) నియంత్రణను పెంచి నీటి ఎద్దడిని తట్టుకునే శక్తిని ఇస్తుంది.",
                f"3. **కలుపు నివారణ:** పొలంలో కలుపు మొక్కలు లేకుండా వెంటనే తొలగించండి, లేకపోతే అవి నేలలోని స్వల్ప తేమను కూడా పీల్చుకుంటాయి.",
                f"4. **గాలి తీవ్రత తగ్గింపు:** అరటి లేదా పసుపు తోట చుట్టూ రక్షణగా అవిశ లేదా సుబాబుల్ చెట్లతో గాలుల వేగాన్ని అడ్డుకోండి.",
            ]
        else:
            resp_lines = [
                f"🔮 **What-If Simulation Assessment (Hypothetical Stress Test — Not Real Weather Forecast):**\n",
                f"If irrigation becomes **completely unavailable** for your **{crop} ({crop_info['botanical_name']})**, the plot faces critical moisture stress (Composite Risk Score: `{comp_score}/10` — `{risk_lvl}`).\n",
                f"- 💧 **Water Satisfaction:** Total crop demand is `{demand_w} mm`, but with no irrigation, only `{scen_r} mm` is received via rainfall (satisfying only `{sat_w}%` of water demand).",
                f"- 📉 **Unbuffered Deficit:** A severe deficit of `{net_def} mm` threatens normal physiological development.\n",
                f"🛡️ **Critical Institutional Precautions (ICAR & ANGRAU):**",
                f"1. **Emergency Surface Mulching:** Immediately apply 10-12 tons/ha of paddy straw or green crop residues across ridges and beds to suppress soil moisture evaporation.",
                f"2. **Foliar Potassium Spray:** Apply 1% Potassium Nitrate (10 g/L KNO3) or Sulfate of Potash. Potassium maintains stomatal guard cell turgor and osmotic balance under severe moisture stress.",
                f"3. **Immediate Weed Eradication:** Remove all weed growth immediately to prevent severe vegetative competition for residual root-zone soil water.",
                f"4. **Shade & Windbreak Buffering:** For banana and turmeric, ensure perimeter border plants (Sesbania) reduce wind velocity and transpirational pull.",
            ]

        return {
            "response": "\n".join(resp_lines),
            "grounding_data": grounding,
            "references": crop_info.get("references", []),
        }

    # -------------------------------------------------------------------------
    # CASE 4: GENERAL SIMULATION QUERY / CUSTOM PARAMETERS
    # -------------------------------------------------------------------------
    else:
        sc_active = sc_c
        grounding = {
            "query_type": "general_simulation_summary",
            "crop": crop,
            "scenario": sc_active["scenario_name"],
            "composite_score": sc_active["evaluations"]["composite"]["score"],
            "risk_level": sc_active["evaluations"]["composite"]["risk_level"],
            "duration_days": duration,
            "is_hypothetical_simulation": True,
        }

        if lang == "te":
            resp_lines = [
                f"🔮 **వాట్-ఇఫ్ సిమ్యులేషన్ విశ్లేషణ (ఊహాజనిత నమూనా — ప్రత్యక్ష సూచన కాదు):**\n",
                f"మీ **{crop_info['crop_name_te']} ({crop})** పంట కోసం వాట్-ఇఫ్ సిమ్యులేటర్‌లో క్రింది పరిస్థితులను విశ్లేషించవచ్చు:\n",
                f"- **పరిస్థితి A (బేస్‌లైన్):** సాధారణ వర్షపాతం మరియు ఉష్ణోగ్రత.",
                f"- **పరిస్థితి B (తక్కువ వర్షం):** 30% వర్షపాతం తగ్గినప్పుడు ప్రభావం.",
                f"- **పరిస్థితి C (ఎండ + కరువు):** 40% వర్ష లోటు మరియు +2.5°C ఉష్ణోగ్రత పెరుగుదల.",
                f"- **పరిస్థితి D (నీటి సంక్షోభం):** 50% వర్ష లోటు, +3.0°C వేడిమి మరియు నీటి పారుదల లేకపోవడం.\n",
                f"మీరు నిర్దిష్ట శాతం మార్పులు లేదా రక్షణ చర్యల గురించి ప్రశ్నలు అడగవచ్చు (ఉదా: *'వర్షాలు 30% తగ్గితే ఏమవుతుంది?'* లేదా *'నీరు లేకపోతే ఏ జాగ్రత్తలు తీసుకోవాలి?'*)."
            ]
        else:
            resp_lines = [
                f"🔮 **What-If Simulation Assessment (Hypothetical Stress Test — Not Real Weather Forecast):**\n",
                f"The What-If Simulator models 4 standardized climate stress scenarios for your **{crop}**:\n",
                f"- **Scenario A (Reference Baseline):** Normal seasonal conditions.",
                f"- **Scenario B (Reduced Rainfall):** 30% precipitation reduction.",
                f"- **Scenario C (Drought + Heat):** 40% rain reduction with +2.5°C temperature increase.",
                f"- **Scenario D (Severe Crisis):** 50% rain reduction, +3.0°C heat, and total irrigation failure.\n",
                f"You can ask specific questions like: *'Which scenario is most concerning for my turmeric crop?'*, *'What happens if rainfall decreases by 30%?'*, or *'What precautions should I take if irrigation becomes unavailable?'*."
            ]

        return {
            "response": "\n".join(resp_lines),
            "grounding_data": grounding,
            "references": crop_info.get("references", []),
        }
