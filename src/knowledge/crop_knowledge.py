"""Structured Agricultural Knowledge Base for Regional Crops.

Covers Turmeric, Banana, and Paddy with physiological baselines,
thermal and hydrological thresholds, resilience measures, and authentic
institutional references (ICAR, ANGRAU, IMD, PJTSAU).

Provides fully localized English and Telugu content across soils, growth stages,
water demands, climate resilience practices, and citations.
No unsupported yield claims or uncalibrated volumetric irrigation mandates.
"""

from typing import Dict, Any, List


CROP_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "Turmeric": {
        "botanical_name": "Curcuma longa",
        "crop_name_en": "Turmeric",
        "crop_name_te": "పసుపు",
        "optimal_temperature_c": {"min": 20.0, "max": 35.0, "stress_above": 38.0},
        "annual_rainfall_mm": {"min": 1000.0, "max": 2000.0},
        "suitable_soils": [
            "Well-drained red sandy loam",
            "Deep friable alluvial loam",
            "Clay loam with gravelly subsoil",
        ],
        "suitable_soils_te": [
            "మురుగు నీరు నిలవని ఎర్ర ఇసుక గరప నేలలు (Well-drained Red Sandy Loam)",
            "లోతైన, గుల్లగా ఉండే సారవంతమైన ఒండ్రు నేలలు (Deep Friable Alluvial Loam)",
            "కంకర ఉపరితలం గల బంకమట్టి గరప నేలలు (Clay Loam with gravelly subsoil)",
        ],
        "vulnerable_soils": [
            "Heavy ill-drained black clay (susceptible to water stagnation & rhizome rot)",
        ],
        "vulnerable_soils_te": [
            "మురుగు నీరు ఇంకని బరువైన నల్లరేగడి నేలలు (నీరు నిలిస్తే దుంప కుళ్లు తెగులు ఆశించే ప్రమాదం)",
        ],
        "growth_stages": [
            {
                "stage": "Sprouting & Vegetative",
                "stage_te": "మొలక & శాఖీయ ఎదుగుదల దశ",
                "days": "0-60",
                "water_need": "Moderate",
                "water_need_te": "మధ్యస్థ",
            },
            {
                "stage": "Tillering & Rhizome Initiation",
                "stage_te": "పిలకలు & కొమ్ము ప్రారంభ దశ",
                "days": "60-120",
                "water_need": "High",
                "water_need_te": "అధిక",
            },
            {
                "stage": "Rhizome Development & Bulking",
                "stage_te": "కొమ్ము ఊరే & పరిమాణం పెరిగే దశ",
                "days": "120-210",
                "water_need": "Critical",
                "water_need_te": "అత్యంత కీలక",
            },
            {
                "stage": "Maturity & Leaf Senescence",
                "stage_te": "పక్వత & ఆకులు ఎండిపోయే దశ",
                "days": "210-270",
                "water_need": "Low to tapering",
                "water_need_te": "తక్కువ (తగ్గిస్తూ ఆపాలి)",
            },
        ],
        "temperature_sensitivity": {
            "en": (
                "Turmeric is adapted to humid tropical conditions. Daytime temperatures exceeding 38°C "
                "trigger rapid stomatal closure and transpirational leaf-tip scorch during midday hours."
            ),
            "te": (
                "పసుపు పంట వేడి మరియు తేమతో కూడిన వాతావరణంలో బాగా పెరుగుతుంది. పగటి ఉష్ణోగ్రతలు 38°C మించినప్పుడు "
                "ఆకుల నుండి నీరు వేగంగా ఆవిరై, మధ్యాహ్నం వేళల్లో ఆకుల చివర్లు మాడిపోవడం జరుగుతుంది."
            ),
        },
        "water_sensitivity": {
            "en": (
                "Continuous, uniform root-zone moisture is required during rhizome enlargement (120-210 days). "
                "Moisture deficits limit rhizome expansion, whereas water stagnation in heavy soils promotes "
                "Pythium / fungal rhizome rot."
            ),
            "te": (
                "కొమ్ము ఊరే దశలో (120-210 రోజులు) వేరు మండలంలో నిరంతరం పదును ఉండటం ఎంతో అవసరం. నీటి కొరత ఏర్పడితే "
                "కొమ్ముల పెరుగుదల మందగిస్తుంది; అదే సమయంలో నీరు నిలిచిపోతే దుంప కుళ్లు తెగులు (Pythium) ఆశిస్తుంది."
            ),
        },
        "resilience_practices": [
            {
                "practice_en": "Organic Surface Mulching",
                "practice_te": "సేంద్రీయ ఆచ్ఛాదన (వరి గడ్డి లేదా పచ్చి రొట్ట మల్చింగ్)",
                "details_en": "Apply 10-12 tons/ha of green leaf mulch or paddy straw to buffer soil temperature and suppress evaporative moisture loss.",
                "details_te": "ఎకరానికి 4-5 టన్నుల వరి గడ్డి లేదా పచ్చి రొట్టతో మల్చింగ్ చేయడం వల్ల నేల ఉష్ణోగ్రత నియంత్రణలో ఉండి, తేమ ఆవిరి కాకుండా ఎక్కువ కాలం నిల్వ ఉంటుంది.",
            },
            {
                "practice_en": "Drainage Trenches",
                "practice_te": "మురుగు నీటి కాలువలు ఏర్పాటు",
                "details_en": "Provide 30 cm drainage furrows across ridges to prevent waterlogging during unseasonal cyclonic downpours.",
                "details_te": "అకాల వర్షాలు లేదా తుఫానుల సమయంలో పొలంలో నీరు నిలవకుండా బోదెల మధ్య 30 సెం.మీ లోతు మురుగు కాలువలను ఏర్పాటు చేయాలి.",
            },
            {
                "practice_en": "Foliar Nutrition under Heat",
                "practice_te": "ఎండ తీవ్రత ఉన్నప్పుడు పొటాషియం పిచికారీ",
                "details_en": "Foliar spray of 1% Potassium Nitrate (KNO3) during prolonged dry heat improves osmotic regulation in leaves.",
                "details_te": "ఎండ తీవ్రత ఎక్కువగా ఉన్నప్పుడు 1% పొటాషియం నైట్రేట్ (13-0-45 / KNO3) పిచికారీ చేయడం వల్ల ఆకులలో నీటి నిల్వ సామర్థ్యం పెరిగి ఎండ వేడిమిని తట్టుకుంటుంది.",
            },
        ],
        "references": [
            {
                "authority": "ICAR - Indian Institute of Spices Research (IISR)",
                "authority_te": "ఐకార్ - భారత సుగంధ ద్రవ్యాల పరిశోధనా సంస్థ",
                "document": "Turmeric: Package of Practices and Climate Advisory",
                "document_te": "పసుపు సమగ్ర సాగు పద్ధతులు మరియు వాతావరణ సలహాలు",
                "url": "https://spices.res.in",
            },
            {
                "authority": "Acharya N.G. Ranga Agricultural University (ANGRAU)",
                "authority_te": "ఆచార్య ఎన్.జి. రంగా వ్యవసాయ విశ్వవిద్యాలయం",
                "document": "Vyavasaya Panchangam - Spices Crop Management Guide",
                "document_te": "వ్యవసాయ పంచాంగం - సుగంధ ద్రవ్య పంటల యాజమాన్య దర్శిని",
                "url": "https://angrau.ac.in",
            },
        ],
    },
    "Banana": {
        "botanical_name": "Musa acuminata",
        "crop_name_en": "Banana",
        "crop_name_te": "అరటి",
        "optimal_temperature_c": {"min": 25.0, "max": 32.0, "stress_above": 38.0},
        "annual_rainfall_mm": {"min": 1200.0, "max": 2200.0},
        "suitable_soils": [
            "Deep rich loamy soil",
            "Well-drained alluvial soil",
            "Clay loam rich in organic matter",
        ],
        "suitable_soils_te": [
            "సేంద్రియ గుణాలు గల లోతైన సారవంతమైన గరప నేలలు (Deep Rich Loamy Soil)",
            "మురుగు నీరు త్వరగా వడిసిపోయే సారవంతమైన ఒండ్రు నేలలు (Well-drained Alluvial Soil)",
            "సేంద్రియ పదార్థం అధికంగా ఉన్న బంకమట్టి గరప నేలలు (Clay Loam rich in organic matter)",
        ],
        "vulnerable_soils": [
            "Shallow saline/alkaline soils or waterlogged soils causing root asphyxiation",
        ],
        "vulnerable_soils_te": [
            "లోతు తక్కువ చౌడు లేదా క్షార నేలలు, నీరు నిలిచి వేర్లకు గాలి అందకుండా చేసే చిత్తడి నేలలు",
        ],
        "growth_stages": [
            {
                "stage": "Vegetative & Sucker Management",
                "stage_te": "శాఖీయ ఎదుగుదల & పిలకల యాజమాన్య దశ",
                "days": "0-150",
                "water_need": "Moderate to High",
                "water_need_te": "మధ్యస్థం నుండి అధిక",
            },
            {
                "stage": "Shooting & Bunch Emergence",
                "stage_te": "గెల వేసే & దూత బయటకు వచ్చే దశ",
                "days": "150-240",
                "water_need": "High",
                "water_need_te": "అధిక",
            },
            {
                "stage": "Bunch Development & Finger Filling",
                "stage_te": "గెల అభివృద్ధి & కాయ ఊరే దశ",
                "days": "240-330",
                "water_need": "Critical",
                "water_need_te": "అత్యంత కీలక",
            },
            {
                "stage": "Harvest Maturity",
                "stage_te": "పంట కోత పక్వత దశ",
                "days": "330-360",
                "water_need": "Tapering",
                "water_need_te": "క్రమంగా తగ్గించాలి",
            },
        ],
        "temperature_sensitivity": {
            "en": (
                "Banana requires 25°C to 32°C. Temperatures exceeding 38°C in combination with low relative humidity "
                "cause transpirational stress, marginal leaf necrosis, and sunburn on exposed fruit bunches."
            ),
            "te": (
                "అరటి పంటకు 25°C నుండి 32°C ఉష్ణోగ్రతలు చాలా అనుకూలం. ఉష్ణోగ్రతలు 38°C దాటి గాలిలో తేమ తగ్గినప్పుడు "
                "ఆకుల అంచులు ఎండిపోవడం మరియు ఎండ తీవ్రత వల్ల గెలలపై మాడు మచ్చలు రావడం జరుగుతుంది."
            ),
        },
        "water_sensitivity": {
            "en": (
                "With broad leaves and high canopy transpiration, banana is extremely sensitive to moisture deficits. "
                "Drought during shooting and bunch emergence severely impairs fruit finger length and market grade."
            ),
            "te": (
                "వెడల్పాటి ఆకులు ఉండటం వల్ల అరటి మొక్కలకు నీటి వినియోగం అత్యధికం. గెల వేసే సమయంలో మరియు కాయ ఊరే దశలో "
                "నీటి కొరత ఏర్పడితే కాయ పరిమాణం మరియు నాణ్యత బాగా తగ్గిపోతాయి."
            ),
        },
        "resilience_practices": [
            {
                "practice_en": "Perimeter Windbreaks",
                "practice_te": "తోట సరిహద్దు రక్షణ చెట్లు (విండ్‌బ్రేక్స్ - Windbreaks)",
                "details_en": "Plant two rows of Sesbania grandiflora (Avisa) or Subabul on the field boundaries to reduce wind velocity and leaf shredding.",
                "details_te": "తోట సరిహద్దుల్లో రెండు వరుసలలో అవిశ (Sesbania grandiflora) లేదా సుబాబుల్ చెట్లను పెంచడం ద్వారా ఈదురు గాలుల వేగాన్ని అడ్డుకుని అరటి ఆకులు చీలిపోకుండా కాపాడవచ్చు.",
            },
            {
                "practice_en": "Drip Irrigation Scheduling",
                "practice_te": "బిందు సేద్యం (డ్రిప్) ద్వారా క్రమబద్ధమైన నీటి తడులు",
                "details_en": "Schedule frequent, micro-dosed drip irrigations during dry spells to maintain consistent root-zone moisture tension.",
                "details_te": "ఎండ తీవ్రత ఉన్నప్పుడు బిందు సేద్యం (డ్రిప్) ద్వారా క్రమం తప్పకుండా తక్కువ వ్యవధిలో తడులు అందించి వేరు మండలంలో తగినంత తేమను నిరంతరం కాపాడాలి.",
            },
            {
                "practice_en": "Bunch Sleeving",
                "practice_te": "గెలలకు రక్షణ తొడుగులు (బంచ్ స్లీవ్స్ - Bunch Sleeving)",
                "details_en": "Cover emerging bunches with perforated polypropylene or non-woven sleeves to prevent sunburn and thrips damage.",
                "details_te": "ఎండ తీవ్రత నుండి మరియు తామర పురుగుల మచ్చల నుండి గెలలను కాపాడేందుకు సన్నని రంధ్రాలు గల పాలీప్రొఫిలీన్ లేదా నాన్-వోవెన్ సంచులతో గెలలను కప్పాలి.",
            },
        ],
        "references": [
            {
                "authority": "ICAR - National Research Centre for Banana (NRCB)",
                "authority_te": "ఐకార్ - జాతీయ అరటి పరిశోధనా కేంద్రం",
                "document": "Banana Production Manual & Climate Resilience Recommendations",
                "document_te": "అరటి ఉత్పత్తి కరదీపిక మరియు వాతావరణ సమగ్ర మార్గదర్శకాలు",
                "url": "https://nrcb.icar.gov.in",
            },
            {
                "authority": "Acharya N.G. Ranga Agricultural University (ANGRAU)",
                "authority_te": "ఆచార్య ఎన్.జి. రంగా వ్యవసాయ విశ్వవిద్యాలయం",
                "document": "Vyavasaya Panchangam - Fruit Crops Management",
                "document_te": "వ్యవసాయ పంచాంగం - ఉద్యాన పంటల యాజమాన్య దర్శిని",
                "url": "https://angrau.ac.in",
            },
        ],
    },
    "Paddy": {
        "botanical_name": "Oryza sativa",
        "crop_name_en": "Paddy (Rice)",
        "crop_name_te": "వరి",
        "optimal_temperature_c": {"min": 22.0, "max": 33.0, "stress_above": 35.0},
        "annual_rainfall_mm": {"min": 1000.0, "max": 1800.0},
        "suitable_soils": [
            "Heavy clay or clayey loam with high water holding capacity",
            "Black cotton soil with impervious subsoil",
        ],
        "suitable_soils_te": [
            "నీటిని నిల్వ ఉంచే అధిక సామర్థ్యం గల బరువైన బంకమట్టి నేలలు (Heavy Clay)",
            "అడుగున గట్టి పొర ఉన్న నల్లరేగడి నేలలు (Black Cotton Soil)",
        ],
        "vulnerable_soils": [
            "Light sandy soil with excessive percolation causing rapid drying and high percolation loss",
        ],
        "vulnerable_soils_te": [
            "నీరు త్వరగా ఇంకిపోయే తేలికపాటి ఇసుక నేలలు (అధిక ఇంకుడు నష్టం మరియు త్వరగా ఎండిపోవడం)",
        ],
        "growth_stages": [
            {
                "stage": "Nursery & Seedling Establishment",
                "stage_te": "నారుమడి & మొలకల స్థిరీకరణ దశ",
                "days": "0-25",
                "water_need": "Moderate",
                "water_need_te": "మధ్యస్థ",
            },
            {
                "stage": "Active Tillering",
                "stage_te": "చురుకైన పిలకలు తొడిగే దశ",
                "days": "25-55",
                "water_need": "High",
                "water_need_te": "అధిక",
            },
            {
                "stage": "Panicle Initiation & Booting",
                "stage_te": "చిరుపొట్ట & వెన్ను పిండం ఏర్పడే దశ",
                "days": "55-80",
                "water_need": "Critical",
                "water_need_te": "అత్యంత కీలక",
            },
            {
                "stage": "Flowering / Anthesis",
                "stage_te": "పూత దశ (పుష్పించే దశ - Anthesis)",
                "days": "80-95",
                "water_need": "Most Critical",
                "water_need_te": "అత్యంత సున్నితమైన & కీలక",
            },
            {
                "stage": "Grain Filling & Dough Stage",
                "stage_te": "గింజ పాలుపోసుకునే & గింజ ముదిరే దశ",
                "days": "95-120",
                "water_need": "Moderate",
                "water_need_te": "మధ్యస్థ",
            },
            {
                "stage": "Maturity",
                "stage_te": "పంట కోత పక్వత దశ",
                "days": "120-135",
                "water_need": "Tapering to Dry",
                "water_need_te": "తగ్గిస్తూ ఆరబెట్టాలి",
            },
        ],
        "temperature_sensitivity": {
            "en": (
                "Temperatures between 22°C and 33°C are optimal. Ambient temperatures exceeding 35°C during flowering (anthesis) "
                "cause pollen desiccation, leading to spikelet sterility and chaffy grains."
            ),
            "te": (
                "వరి పంటకు 22°C నుండి 33°C ఉష్ణోగ్రతలు అనుకూలం. ముఖ్యంగా పూత సమయంలో ఉష్ణోగ్రత 35°C దాటితే "
                "పుప్పొడి ఎండిపోయి తాలు గింజలు (తాలు కాయడం) ఏర్పడే ప్రమాదం పెరుగుతుంది."
            ),
        },
        "water_sensitivity": {
            "en": (
                "Water deficit during panicle initiation and flowering causes severe spikelet sterility. "
                "However, continuous deep submergence is not required in vegetative stages; Alternate Wetting and Drying (AWD) saves water."
            ),
            "te": (
                "చిరుపొట్ట మరియు పూత దశల్లో నీటి ఎద్దడి ఏర్పడితే తాలు గింజలు ఎక్కువగా వచ్చి దిగుబడి దెబ్బతింటుంది. "
                "అయితే ఎదుగుదల దశలో నిరంతరం నీరు నిలబెట్టకుండా 'ఆరబెట్టి తడపడం' (AWD పద్ధతి) ద్వారా నీటిని ఆదా చేయవచ్చు."
            ),
        },
        "resilience_practices": [
            {
                "practice_en": "Alternate Wetting and Drying (AWD)",
                "practice_te": "ఆరబెట్టి తడపడం (AWD - Alternate Wetting and Drying పద్ధతి)",
                "details_en": "Allow standing water to subside until field soil develops fine hairline cracks before reapplying 2-3 cm of water during vegetative phase.",
                "details_te": "పైరు శాఖీయ ఎదుగుదల దశలో నిరంతరం నీరు నిల్వ ఉంచకుండా, పొలంలోని నీరు ఇంకి నేలపై సన్నని నెర్రలు వచ్చే సమయంలో మళ్లీ 2-3 సెం.మీ తడి ఇవ్వడం (ఆరబెట్టి తడపడం - AWD పద్ధతి) ద్వారా 25-30% నీరు ఆదా అవుతుంది.",
            },
            {
                "practice_en": "Critical Stage Protection",
                "practice_te": "కీలక దశలలో నిరంతర నీటి నిల్వ",
                "details_en": "Maintain 3-5 cm standing water during panicle initiation and flowering to prevent floral heat stress and pollen sterility.",
                "details_te": "చిరుపొట్ట మరియు పూత దశలలో తప్పనిసరిగా 3 నుండి 5 సెం.మీ మేర పొలంలో నీరు ఉండేలా చూసుకోవాలి; ఇది అధిక ఎండ వేడిమి వల్ల పుప్పొడి ఎండిపోయి తాలు గింజలు రాకుండా రక్షిస్తుంది.",
            },
            {
                "practice_en": "Nutrient Buffering",
                "practice_te": "పోషకాల సమతుల్యత (పొటాష్ & జింక్ ఎరువులు)",
                "details_en": "Split application of Potassium (MOP) enhances stalk strength, drought tolerance, and grain filling under thermal stress.",
                "details_te": "పొటాష్ (మ్యూరేట్ ఆఫ్ పొటాష్ - MOP) ఎరువును ఆఖరి దఫాగా వేయడం వల్ల పైరు కాండం బలంగా ఉండి నీటి ఎద్దడిని, ఎండ వేడిమిని తట్టుకుని గింజ బరువు పెరుగుతుంది.",
            },
        ],
        "references": [
            {
                "authority": "ICAR - Indian Institute of Rice Research (IIRR, Hyderabad)",
                "authority_te": "ఐకార్ - భారత వరి పరిశోధనా సంస్థ (IIRR, హైదరాబాద్)",
                "document": "Rice Knowledge Management Portal (RKMP) - Climate Resilient Rice Production",
                "document_te": "వరి విజ్ఞాన వేదిక (RKMP) - వాతావరణాన్ని తట్టుకునే వరి సాగు సూచనలు",
                "url": "https://www.icar-iirr.org",
            },
            {
                "authority": "Professor Jayashankar Telangana State Agricultural University (PJTSAU)",
                "authority_te": "ప్రొఫెసర్ జయశంకర్ తెలంగాణ రాష్ట్ర వ్యవసాయ విశ్వవిద్యాలయం",
                "document": "Package of Practices for Irrigated and Rainfed Rice",
                "document_te": "నీటిపారుదల మరియు వర్షాధార వరి సాగు సమగ్ర పద్ధతులు",
                "url": "https://pjtsau.edu.in",
            },
            {
                "authority": "Acharya N.G. Ranga Agricultural University (ANGRAU)",
                "authority_te": "ఆచార్య ఎన్.జి. రంగా వ్యవసాయ విశ్వవిద్యాలయం",
                "document": "Vyavasaya Panchangam - Rice Cultivation Guidelines",
                "document_te": "వ్యవసాయ పంచాంగం - వరి పంట యాజమాన్య మార్గదర్శకాలు",
                "url": "https://angrau.ac.in",
            },
        ],
    },
}


def get_crop_profile(crop: str) -> Dict[str, Any]:
    """Retrieve full knowledge profile for the given crop, defaulting to Turmeric."""
    return CROP_KNOWLEDGE_BASE.get(crop, CROP_KNOWLEDGE_BASE["Turmeric"])


def get_growth_stage_by_days(crop: str, days_in_field: int) -> Dict[str, str]:
    """Determine estimated growth stage for the crop based on days since sowing."""
    profile = get_crop_profile(crop)
    stages = profile.get("growth_stages", [])
    
    for s in stages:
        day_range = s["days"].split("-")
        if len(day_range) == 2:
            start_d, end_d = int(day_range[0]), int(day_range[1])
            if start_d <= days_in_field <= end_d:
                return s
        elif len(day_range) == 1:
            start_d = int(day_range[0].replace("+", ""))
            if days_in_field >= start_d:
                return s
                
    return stages[-1] if stages else {
        "stage": "General Cultivation",
        "stage_te": "సాధారణ సాగు దశ",
        "days": "N/A",
        "water_need": "Moderate",
        "water_need_te": "మధ్యస్థ",
    }
