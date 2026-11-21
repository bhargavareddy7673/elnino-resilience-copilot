"""
Multilingual Agricultural Chatbot Response Synthesizer.

Synthesizes rich, evidence-grounded conversational responses by combining:
1. User query and conversational intent.
2. Authentic RAG knowledge base evidence from ICAR-IISR, ICAR-NRCB, ICAR-IIRR, IMD MoES.
3. Farmer's active digital twin resources (land area, soil type, irrigation source, crop stage).
4. Real-time atmospheric telemetry and 7-day rainfall forecasts from Open-Meteo.
5. Multi-turn conversational history.

Provides actionable agronomic guidance, resource-specific planning, weather integration,
and academic citation provenance in English and Telugu.
"""

import os
import re
import datetime
from typing import Dict, Any, List, Optional

from src.rag.retriever import HybridRetriever, SearchResult
from src.knowledge.crop_knowledge import (
    get_crop_profile,
    get_growth_stage_by_days,
)

# Global cached retriever instance for high-speed sub-20ms inference
_GLOBAL_RETRIEVER: Optional[HybridRetriever] = None


def get_retriever() -> HybridRetriever:
    """Retrieve or initialize the global singleton HybridRetriever."""
    global _GLOBAL_RETRIEVER
    if _GLOBAL_RETRIEVER is None:
        _GLOBAL_RETRIEVER = HybridRetriever()
        _GLOBAL_RETRIEVER.load_index()
    return _GLOBAL_RETRIEVER


class FarmChatbotSynthesizer:
    """
    Core conversational reasoning and response synthesis engine for the
    AI Farm Advisor.
    """

    def __init__(self, retriever: Optional[HybridRetriever] = None):
        self.retriever = retriever or get_retriever()

    def synthesize_response(
        self,
        query: str,
        farm_profile: Dict[str, Any],
        weather_intelligence: Dict[str, Any],
        chat_history: Optional[List[Dict[str, Any]]] = None,
        lang: str = "en",
        crop_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive, resource-aware, evidence-grounded agricultural response.

        Args:
            query: User's natural language question.
            farm_profile: Active farm digital twin dictionary.
            weather_intelligence: Live Open-Meteo weather payload.
            chat_history: Prior conversation turns for conversational continuity.
            lang: Language for output ('en' or 'te').
            crop_override: Optional crop detected from query.

        Returns:
            Dictionary containing 'response_text', 'grounding_data', 'references', and 'evidence_found'.
        """
        # 1. Resolve Farm Profile Parameters & Detect Query Crop Override
        detected_crop = crop_override
        if not detected_crop:
            q_lower = query.lower()
            if any(k in q_lower for k in ["banana", "arati", "ariti", "అరటి"]):
                detected_crop = "Banana"
            elif any(k in q_lower for k in ["paddy", "rice", "vari", "వరి"]):
                detected_crop = "Paddy"
            elif any(k in q_lower for k in ["turmeric", "pasupu", "paspu", "పసుపు"]):
                detected_crop = "Turmeric"

        crop = detected_crop or farm_profile.get("crop", "Turmeric")
        land_area = farm_profile.get("land_area", 4.0)
        soil = farm_profile.get("soil_type", "Red Sandy Loam")
        irrigation = farm_profile.get("irrigation", "Borewell / Groundwater")
        state = farm_profile.get("state", "Andhra Pradesh")
        district = farm_profile.get("district", "Kurnool")
        village = farm_profile.get("village", "").strip()
        location_str = f"{village}, {district}" if village else district

        crop_info = get_crop_profile(crop)
        crop_te = crop_info.get("crop_name_te", crop)

        # 2. Determine Crop Phenological Stage from Sowing Date
        sowing_date_str = farm_profile.get("sowing_date", "")
        days_in_field: Optional[int] = None
        stage_info: Optional[Dict[str, Any]] = None

        if sowing_date_str:
            try:
                if isinstance(sowing_date_str, datetime.date):
                    s_date = sowing_date_str
                else:
                    s_date = datetime.date.fromisoformat(str(sowing_date_str).strip())
                if s_date <= datetime.date.today():
                    days_in_field = max(0, (datetime.date.today() - s_date).days)
                    stage_info = get_growth_stage_by_days(crop, days_in_field)
            except Exception:
                days_in_field = None
                stage_info = None

        # 3. Extract Live Telemetry
        curr_weather = weather_intelligence.get("current", {})
        curr_temp = curr_weather.get("temperature", 32.0)
        curr_humidity = curr_weather.get("relative_humidity", 55.0)
        curr_rain = curr_weather.get("precipitation", 0.0)

        forecast_summary = weather_intelligence.get("forecast_summary", {})
        rain_7d = forecast_summary.get("total_rain_next_7_days", 0.0)
        max_temp_7d = forecast_summary.get("max_temp_next_7_days", 36.0)

        dry_spell_info = weather_intelligence.get("dry_spells", {})
        observed_dry_days = dry_spell_info.get("observed_dry_days", 0)

        # 4. Perform Hybrid RAG Retrieval across authentic ICAR / IMD Publications
        crop_filter = crop.lower() if crop.lower() in ["turmeric", "banana", "paddy"] else None
        from src.nlp.text_normalization import normalize_text
        norm_q = normalize_text(query)
        search_query = f"{crop} {norm_q}" if crop.lower() not in norm_q.lower() else norm_q

        rag_search = self.retriever.search_hybrid(
            query=search_query,
            top_k=4,
            crop_filter=crop_filter,
            suppress_legacy=True,
            suppress_boilerplate=True,
        )
        if not rag_search.get("results"):
            rag_search = self.retriever.search_hybrid(
                query=query,
                top_k=4,
                crop_filter=crop_filter,
                suppress_legacy=True,
                suppress_boilerplate=True,
            )

        evidence_chunks = rag_search.get("results", [])
        evidence_found = rag_search.get("evidence_found", False)

        # Build citations list
        references = []
        seen_refs = set()
        for chk in evidence_chunks:
            ref_key = (chk.document_title, chk.page_number)
            if ref_key not in seen_refs:
                seen_refs.add(ref_key)
                references.append({
                    "authority": chk.organization,
                    "document": f"{chk.document_title} (Page {chk.page_number})",
                    "url": chk.source_url,
                    "page": chk.page_number,
                    "chunk_id": chk.chunk_id,
                    "similarity": chk.dense_score,
                })

        # 5. Build Comprehensive Grounding Telemetry
        grounding_data = {
            "farm_resources": {
                "crop": crop,
                "land_area_acres": land_area,
                "soil_type": soil,
                "irrigation_system": irrigation,
                "days_in_field": days_in_field if days_in_field is not None else "Not specified",
                "growth_stage": stage_info.get("stage") if stage_info else "General baseline",
                "water_need": stage_info.get("water_need") if stage_info else "Moderate",
                "location": location_str,
            },
            "weather_telemetry": {
                "current_temperature": f"{curr_temp:.1f} °C",
                "relative_humidity": f"{curr_humidity:.0f} %",
                "rain_forecast_7d": f"{rain_7d:.1f} mm",
                "max_temp_7d": f"{max_temp_7d:.1f} °C",
                "observed_dry_days": observed_dry_days,
            },
            "rag_evidence": {
                "chunks_retrieved": len(evidence_chunks),
                "top_chunk_id": evidence_chunks[0].chunk_id if evidence_chunks else None,
                "top_similarity": evidence_chunks[0].dense_score if evidence_chunks else 0.0,
            },
            "citations": references,
        }

        # 6. Synthesize Response Text (English or Telugu)
        if lang == "te":
            response_text = self._synthesize_telugu(
                query=query,
                crop=crop,
                crop_te=crop_te,
                land_area=land_area,
                soil=soil,
                irrigation=irrigation,
                location_str=location_str,
                days_in_field=days_in_field,
                stage_info=stage_info,
                curr_temp=curr_temp,
                curr_humidity=curr_humidity,
                rain_7d=rain_7d,
                max_temp_7d=max_temp_7d,
                observed_dry_days=observed_dry_days,
                evidence_chunks=evidence_chunks,
                references=references,
            )
        else:
            response_text = self._synthesize_english(
                query=query,
                crop=crop,
                land_area=land_area,
                soil=soil,
                irrigation=irrigation,
                location_str=location_str,
                days_in_field=days_in_field,
                stage_info=stage_info,
                curr_temp=curr_temp,
                curr_humidity=curr_humidity,
                rain_7d=rain_7d,
                max_temp_7d=max_temp_7d,
                observed_dry_days=observed_dry_days,
                evidence_chunks=evidence_chunks,
                references=references,
            )

        return {
            "response_text": response_text,
            "grounding_data": grounding_data,
            "references": references,
            "evidence_found": evidence_found,
        }

    def _synthesize_english(
        self,
        query: str,
        crop: str,
        land_area: float,
        soil: str,
        irrigation: str,
        location_str: str,
        days_in_field: Optional[int],
        stage_info: Optional[Dict[str, Any]],
        curr_temp: float,
        curr_humidity: float,
        rain_7d: float,
        max_temp_7d: float,
        observed_dry_days: int,
        evidence_chunks: List[SearchResult],
        references: List[Dict[str, Any]],
    ) -> str:
        """Construct a structured, professional English advisory response."""
        lines = []

        # Header with resource context
        lines.append(f"### 🌾 Farm Advisory & Planning: **{crop}** ({location_str})")
        lines.append(
            f"**Plot Parameters:** `{land_area:.1f} Acres` • `{soil}` • `{irrigation}`"
        )

        if days_in_field is not None and stage_info:
            lines.append(
                f"**Current Crop Status:** Day `{days_in_field}` in field • **Stage:** `{stage_info['stage']}` (Water Demand: `{stage_info['water_need']}`)"
            )
        else:
            lines.append(
                f"**Current Crop Status:** Sowing date not specified in profile (using seasonal baseline for {crop})."
            )

        lines.append("")

        # Detect specific agricultural question topic
        from src.nlp.text_normalization import normalize_text
        q_norm = f"{query} {normalize_text(query)}".lower()
        is_fertilizer = any(k in q_norm for k in [
            "fertilizer", "fertilizers", "manure", "fym", "urea", "dap", "potash", "mop", "ssp",
            "yerbulu", "yerubulu", "yeruvulu", "eruvulu", "eruvu", "yeruvu", "poshakalu",
            "nutrient", "nutrients", "vepapindi", "neem cake",
            "ఎరువులు", "ఎరువు", "ఎరువుల", "యూరియా", "డిఎపి", "పొటాష్", "వేపపిండి", "పోషకాలు"
        ])
        is_irrigation = (
            any(k in q_norm for k in ["irrigate", "irrigation", "water", "watering", "kattali", "pettali", "ivvali", "tadi", "thadi", "నీరు", "నీళ్లు", "నీళ్ళు", "నీటి", "తడి", "తడులు"])
            and not any(k in q_norm for k in ["rot", "blight", "spot", "pest", "purugu", "tegulu", "fertilizer", "eruvulu", "yerbulu"])
        )
        is_disease = any(k in q_norm for k in ["rot", "blight", "spot", "blotch", "wilt", "blast", "sigatoka", "rust", "pathogen", "fungus", "fungicide", "cure", "treatment", "symptom", "spray", "tegulu", "kullu", "dumpakullu", "verukullu", "aakumacha"])
        is_pest = any(k in q_norm for k in ["pest", "pests", "insect", "insects", "borer", "scale", "thrips", "aphid", "bph", "weevil", "worm", "caterpillar", "armyworm", "purugu", "sudidoma", "telladoma"])
        is_weed = any(k in q_norm for k in ["weed", "weeds", "herbicide", "weeding", "atrazine", "pendimethalin", "kalupu", "కలుపు"])
        is_seed_sowing = any(k in q_norm for k in ["seed", "seeds", "sowing", "sow", "plant", "planting", "spacing", "variety", "varieties", "rate", "germination", "vithanam"])
        is_harvest_curing = any(k in q_norm for k in ["harvest", "harvesting", "curing", "cure", "boil", "boiling", "dry", "drying", "polish", "storage", "yield", "koto", "kotha", "koyyali", "koi", "arabalce", "arabettali", "aarabettali", "udikinchali", "కోత", "ఉడకబెట్టడం", "నిల్వ", "దిగుబడి", "ఆరబెట్టడం"])

        # Top Section: Direct Actionable Guidance for specific agricultural intent
        if is_fertilizer:
            lines.append("#### 🎯 Direct Answer: Fertilizer Schedule & Application Timings (ICAR-IISR Package)")
            if crop == "Turmeric":
                lines.append(f"**Specific Split Dosages for your {land_area:.1f} Acres:**")
                lines.append(f"1. **Basal Dose (At Planting / Final Tilth):** Well-decomposed FYM @ 10 t/acre ({land_area * 10:.0f} tonnes total) + Neem cake @ 200 kg/acre ({land_area * 200:.0f} kg) + 100% Phosphorus (Single Super Phosphate SSP @ 125 kg/acre -> {land_area * 125:.0f} kg or DAP @ 45 kg/acre -> {land_area * 45:.0f} kg) incorporated in soil.")
                lines.append(f"2. **30–40 Days After Planting (First Top Dressing):** Top dress 1/3rd Nitrogen (Urea @ 25 kg/acre -> {land_area * 25:.0f} kg) and 1/3rd Potash (MOP @ 20 kg/acre -> {land_area * 20:.0f} kg) immediately following the first weeding.")
                lines.append(f"3. **60–70 Days After Planting (Second Top Dressing):** Top dress 1/3rd Nitrogen (Urea @ 25 kg/acre -> {land_area * 25:.0f} kg) and 1/3rd Potash (MOP @ 20 kg/acre -> {land_area * 20:.0f} kg) followed by earthing-up and mulch replenishment.")
                lines.append(f"4. **90–100 Days After Planting (Final Top Dressing):** Apply final 1/3rd Nitrogen (Urea @ 25 kg/acre -> {land_area * 25:.0f} kg) and Potash (MOP @ 20 kg/acre -> {land_area * 20:.0f} kg) before rapid rhizome enlargement.")
                lines.append("5. **Micronutrient Foliar Sprays:** Spray IISR Turmeric Special or ZnSO4 (0.2%) + FeSO4 (0.2%) at 60 and 90 days after planting to prevent deficiency.")
            elif crop == "Banana":
                lines.append(f"**Fertilizer Schedule for {crop} ({land_area:.1f} Acres):**")
                lines.append("1. **Basal (At Planting):** FYM 10 kg/pit + Neem cake 250 g/pit.")
                lines.append("2. **Top Dressing per Plant:** Total 300 g Urea + 300 g MOP applied in 4 equal splits at 2nd, 4th, 6th, and 8th month after planting.")
                lines.append("3. **Bunch Emergence:** Spray 0.5% Potassium Sulphate ($K_2SO_4$) on developing bunch to improve fruit size and grade.")
            elif crop == "Paddy":
                lines.append(f"**Fertilizer Schedule for {crop} ({land_area:.1f} Acres):**")
                lines.append(f"1. **Basal (At Transplanting):** 100% Phosphorus (DAP @ 50 kg/acre -> {land_area * 50:.0f} kg) + 50% Potash (MOP @ 20 kg/acre -> {land_area * 20:.0f} kg) + 25% Nitrogen (Urea @ 25 kg/acre -> {land_area * 25:.0f} kg) + Zinc Sulphate @ 10 kg/acre.")
                lines.append(f"2. **Active Tillering (20–25 DAT):** Top dress 50% Nitrogen (Urea @ 50 kg/acre -> {land_area * 50:.0f} kg).")
                lines.append(f"3. **Panicle Initiation (40–45 DAT):** Top dress remaining 25% Nitrogen (Urea @ 25 kg/acre -> {land_area * 25:.0f} kg) + 50% Potash (MOP @ 20 kg/acre -> {land_area * 20:.0f} kg).")
            lines.append("")

        elif is_irrigation:
            lines.append("#### 🎯 Direct Answer: Irrigation Scheduling & Water Management (ICAR-IISR Standard)")
            if crop == "Turmeric":
                lines.append(f"• **Irrigation Interval ({soil}):** Irrigate every 7–10 days under normal weather; shorten to 5–7 days during dry spells or elevated temperatures (>34°C).")
                lines.append("• **Critical Moisture Windows:** Sprouting stage, vegetative tillering (40–60 days), and rhizome bulking stage (90–150 days). Moisture deficit at bulking drastically cuts yield.")
                lines.append("• **Drip Irrigation:** Run drip emitters 2–3 hours every alternate day to maintain optimal 70–80% root-zone field capacity.")
                lines.append("• **Drainage Protection:** Maintain 30 cm drainage furrows across ridges to prevent waterlogging and fungal rhizome rot.")
            elif crop == "Banana":
                lines.append("• **Irrigation Interval:** Irrigate every 4–5 days in summer/dry spell, 7–8 days in winter. Drip fertigation: 15–20 Liters/plant/day.")
            elif crop == "Paddy":
                lines.append("• **Alternate Wetting & Drying (AWD):** Allow water level to recede 5 cm below soil surface before re-flooding 2–3 cm during vegetative stage. Keep continuous 3–5 cm water during panicle to flowering stage.")
            lines.append("")

        elif is_harvest_curing:
            lines.append("#### 🎯 Direct Answer: Harvesting & Post-Harvest Processing (ICAR-IISR SOP)")
            if crop == "Turmeric":
                lines.append("1. **🗓️ Harvest Window & Maturity Indicators:** Crop matures in 7–9 months (January–March). Harvest when lower leaves turn completely yellow, dry, and collapse to the ground.")
                lines.append("2. **♨️ Curing & Boiling Method:** Clean rhizomes and boil in perforated iron pans or steam boilers for 45–60 minutes until finger easily penetrates rhizome with characteristic aroma and white frothing.")
                lines.append("3. **☀️ Sun Drying & Moisture Target:** Spread boiled rhizomes on clean tarpaulins in 5–7 cm layers under sun for 10–15 days until moisture drops to 8–10% (snaps crisply when broken).")
                lines.append("4. **⚙️ Polishing & Safe Storage:** Polish dried fingers in mechanical drums to remove rough outer skin. Store in cool, well-ventilated godowns in clean gunny bags.")
            elif crop == "Banana":
                lines.append("• **Harvesting:** Harvest when bunch fingers are rounded and fruit ribs disappear (75–80% maturity for distant transport). Wash latex in 1% alum solution, air dry, and pack in cartons.")
            elif crop == "Paddy":
                lines.append("• **Harvesting:** Harvest when 80–85% of grains turn golden yellow and grain moisture is around 20%. Thresh and sun-dry to 12–14% moisture before bagging.")
            lines.append("")

        elif is_disease:
            lines.append("#### 🎯 Direct Answer: Plant Pathology & Disease Management (ICAR Package)")
            if crop == "Turmeric":
                lines.append("• **Rhizome Rot (*Pythium aphanidermatum*):** Progressive leaf yellowing and soft rotting of basal rhizomes with foul odor. Dip seed rhizomes in Metalaxyl-Mancozeb (Ridomil MZ) @ 2.5 g/L for 30 mins before planting. Drench infected clumps and surrounding plants with Copper Oxychloride (COC) @ 2.5 g/L (0.25%) or Metalaxyl-Mancozeb @ 1.25 g/L. Apply *Trichoderma viride* @ 2.5 kg/acre enriched in 50 kg FYM.")
                lines.append("• **Leaf Blotch (*Taphrina*) & Leaf Spot (*Colletotrichum*):** Spray Mancozeb 75% WP @ 2.5 g/L or Azoxystrobin 23% SC @ 1.0 ml/L or Propiconazole 25% EC @ 1.0 ml/L at 15-day intervals from first symptom appearance.")
            elif crop == "Banana":
                lines.append("• **Sigatoka Leaf Spot (*Mycosphaerella musicola*):** Spray Propiconazole 25% EC @ 1.0 ml/L or Carbendazim 50% WP @ 1.0 g/L combined with mineral oil 1% at 20-30 day intervals.")
                lines.append("• **Panama Wilt (*Fusarium oxysporum*):** Corm injection with Carbendazim 2% (20 g/L) solution (3 ml/plant) or capsule application with 50-60 mg Carbendazim.")
            elif crop == "Paddy":
                lines.append("• **Blast (*Magnaporthe oryzae*):** Spray Tricyclazole 75% WP @ 0.6 g/L or Isoprothiolane 40% EC @ 1.5 ml/L at early tillering and panicle emergence.")
                lines.append("• **Sheath Blight (*Rhizoctonia solani*):** Spray Validamycin 3% L @ 2.0 ml/L or Hexaconazole 5% EC @ 2.0 ml/L at boot leaf stage.")
            lines.append("")

        elif is_pest:
            lines.append("#### 🎯 Direct Answer: Entomology & Integrated Pest Management (ICAR-IPM)")
            if crop == "Turmeric":
                lines.append("• **Shoot Borer (*Conogethes punctiferalis*):** Larvae bore into shoots causing central shoot drying ('dead heart'). Spray Chlorantraniliprole 18.5% SC @ 0.3 ml/L or Dimethoate 30% EC @ 1.7 ml/L or Flubendiamide 39.35% SC @ 0.2 ml/L at 21-day intervals from July to October. Biocontrol: Release *Trichogramma chilonis* egg parasitoids @ 40,000/acre.")
                lines.append("• **Rhizome Scale (*Aspidiotus hartii*):** Scales suck sap from stored and field rhizomes. Dip seed rhizomes in Quinalphos 25% EC @ 2.0 ml/L for 15 mins prior to storage and planting.")
                lines.append("• **Thrips & Whiteflies:** Spray Neem seed kernel extract (NSKE 5%) or Imidacloprid 17.8% SL @ 0.3 ml/L at early infestation.")
            elif crop == "Banana":
                lines.append("• **Pseudostem Weevil (*Odoiporus longicollis*):** Swab stem with Chlorpyrifos 20% EC @ 2.5 ml/L or inject 0.5 ml/plant. Use longitudinal split pseudostem traps (20 traps/acre).")
            elif crop == "Paddy":
                lines.append("• **Brown Planthopper (BPH - *Nilaparvata lugens*):** Maintain 30 cm alleyways every 2.5–3 m. Spray Triflumezopyrim 10% SC @ 0.5 ml/L or Pymetrozine 50% WDG @ 0.6 g/L directed at plant bases.")
                lines.append("• **Stem Borer (*Scirpophaga incertulas*):** Apply Cartap hydrochloride 4% G @ 10 kg/acre or spray Chlorantraniliprole 18.5% SC @ 0.3 ml/L at ETL (5% dead hearts).")
            lines.append("")

        elif is_weed:
            lines.append("#### 🎯 Direct Answer: Weed Management & Herbicide Guidance (ICAR SOP)")
            if crop == "Turmeric":
                lines.append("• **Pre-emergence Herbicide:** Spray Pendimethalin 30% EC @ 1.0 kg a.i./ha (1.3 Liters/acre) or Atrazine 50% WP @ 1.0 kg a.i./ha within 2–3 days after planting in moist soil.")
                lines.append("• **Hand Weeding Schedule:** Conduct 3 hand weedings at 30, 60, and 90 days after planting, accompanied by earthing-up.")
                lines.append("• **Mulch Weed Suppression:** Thick layer of green leaf mulch or paddy straw @ 4–5 tonnes/acre suppresses weed emergence and keeps root-zone soil cool.")
            elif crop == "Banana":
                lines.append("• **Inter-row Weed Control:** Directed spray of Glyphosate 41% SL @ 1.0 L/acre with protective hood between rows; keep basins clean by manual hoeing.")
            elif crop == "Paddy":
                lines.append("• **Weed Control in Paddy:** Pre-emergence Pretilachlor 50% EC @ 400 ml/acre at 3-5 days after transplanting; post-emergence Bispyribac-sodium 10% SC @ 100 ml/acre at 15-20 days.")
            lines.append("")

        elif is_seed_sowing:
            lines.append("#### 🎯 Direct Answer: Seed Selection, Sowing & Spacing Standards")
            if crop == "Turmeric":
                lines.append("• **Seed Rate:** 1,000 kg (10 quintals) of disease-free mother or primary finger rhizomes per acre.")
                lines.append("• **Planting Geometry:** 45 cm between rows x 15 cm between plants on ridges and furrows; or 30 cm x 15 cm on raised beds (1.2 m width).")
                lines.append("• **Rhizome Treatment:** Dip seed rhizomes in Mancozeb 75% WP @ 3.0 g/L + Chlorpyrifos 20% EC @ 2.0 ml/L for 30 minutes; shade dry for 24 hours before planting.")
                lines.append("• **High-Yielding Varieties:** IISR Prathibha (6.25% curcumin), IISR Kedaram, IISR Alleppey Supreme, BSR-2, Ranga.")
            elif crop == "Banana":
                lines.append("• **Planting Material:** 1,000–1,200 healthy sword suckers (1.5–2.0 kg) or tissue culture plantlets per acre. Spacing: 1.8 m x 1.8 m.")
                lines.append("• **Sucker Treatment:** Dip corms in hot water at 50°C for 20 minutes to kill nematodes and corm borers.")
            elif crop == "Paddy":
                lines.append("• **Seed Rate & Spacing:** 20–25 kg/acre for transplanting (20 x 15 cm spacing); 12–15 kg/acre for direct drum seeding.")
                lines.append("• **Seed Treatment:** Treat seeds with Carbendazim 50% WP @ 2.0 g/kg seed or *Pseudomonas fluorescens* @ 10 g/kg seed.")
            lines.append("")

        # Section: Core Recommendations & Agronomic Guidance (Grounded in RAG Evidence)
        lines.append("#### 📋 Core Recommendations & Agronomic Guidance")
        if evidence_chunks:
            primary_chunk = evidence_chunks[0]
            clean_snippet = primary_chunk.text.replace("\n\n", " ").strip()
            if len(clean_snippet) > 420:
                clean_snippet = clean_snippet[:420] + "..."
            lines.append(f"> *\"{clean_snippet}\"*")
            lines.append(
                f"> — **Source:** {primary_chunk.organization}, *{primary_chunk.document_title}*, Page {primary_chunk.page_number}\n"
            )

        # Crop-specific technical practices
        if crop == "Turmeric":
            lines.append("• **Water Scheduling:** In red sandy loam soils, irrigate at 7–10 day intervals; reduce to 5–7 days during dry spells. Avoid continuous flood irrigation.")
            lines.append("• **Drainage Protection:** Ensure 30 cm drainage furrows across field ridges. Standing water triggers severe rhizome rot (*Pythium aphanidermatum*).")
            lines.append("• **Mulching for Moisture:** Apply 4–4.8 tonnes/acre of green leaf mulch or paddy straw at planting and repeat at 40 and 90 days to conserve soil moisture.")
        elif crop == "Banana":
            lines.append("• **Drip Fertigation:** Adopt daily or alternate-day micro-dosing drip irrigation to prevent nitrogen leaching and potassium fixation.")
            lines.append("• **Sucker Management:** Perform hot water treatment of suckers prior to planting to suppress nematodes and corm weevil larvae.")
            lines.append("• **Nutrient-Irrigation Coupling:** Immediate irrigation is essential following urea (300 g/plant) and DAP (50 g/plant) side-dressing.")
        elif crop == "Paddy":
            lines.append("• **Alternate Wetting & Drying (AWD):** Allow water to subside until hairline cracks appear before reapplying 2–3 cm water during vegetative stage to save 25–30% water.")
            lines.append("• **Critical Panicle Stage:** Maintain continuous 3–5 cm water layer from panicle initiation to flowering to prevent spikelet sterility.")
            lines.append("• **Pest Management:** Form 30 cm alleyways every 2.5–3 m to suppress brown planthopper (BPH) and sheath blight.")

        lines.append("")

        lines.append("")

        # Section 2: Farm Resource Planning & Budgeting
        lines.append("#### 🛠️ Resource & Input Planning (Tailored to your Land)")
        if crop == "Turmeric":
            water_vol_per_acre = "1.5–2.0 acre-inches (~150,000–200,000 Liters)"
            fert_plan = (
                f"For **{land_area:.1f} acres** Fertilizer Schedule (ICAR-IISR Package of Practices):\n"
                f"  1. **Basal Application (At Planting):** FYM @ 10 t/acre ({land_area * 10:.0f} tonnes total) + Neem cake @ 200 kg/acre + 100% Phosphorus (SSP/DAP).\n"
                f"  2. **30–40 Days After Planting:** First top dressing with 1/3 Nitrogen (Urea) and 1/3 Potash (MOP) after first weeding.\n"
                f"  3. **60 Days After Planting:** Second top dressing with 1/3 Nitrogen and 1/3 Potash followed by earthing up and mulching.\n"
                f"  4. **90–100 Days After Planting:** Final Nitrogen & Potash split before rapid rhizome bulking."
            )
        elif crop == "Banana":
            water_vol_per_acre = "15–20 Liters/plant/day via drip"
            fert_plan = f"For **{land_area:.1f} acres** (~1,000–1,200 plants/acre): Plan 300 g Urea, 50 g DAP, 300 g MOP per mat in 4 scheduled fertigation splits."
        else:
            water_vol_per_acre = "AWD water management (~1,000–1,200 mm total requirement)"
            fert_plan = f"For **{land_area:.1f} acres**: Balanced NPK (120:60:60 kg/ha baseline). Apply 50% N + full P & 50% K basal, with remaining N at tillering and panicle initiation."

        lines.append(f"• **Water Budget:** Estimated requirement is {water_vol_per_acre}. With `{irrigation}`, ensure pipe networks or drip emitters are flushed of mineral deposits.")
        lines.append(f"• **Nutrient Allocation:** {fert_plan}")
        lines.append(f"• **Soil Suitability ({soil}):** Ensure high organic matter addition to buffer water retention and avoid compaction.")

        lines.append("")

        # Section 3: Weather Telemetry & Climate Integration
        lines.append("#### ⛅ Real-Time Atmospheric Intelligence & El Niño Contingency")
        lines.append(
            f"• **Current Readings:** Temperature `{curr_temp:.1f} °C` | Humidity `{curr_humidity:.0f} %`"
        )
        lines.append(
            f"• **7-Day Rain Outlook:** **`{rain_7d:.1f} mm`** expected | Peak Temp: **`{max_temp_7d:.1f} °C`**"
        )

        if rain_7d < 5.0:
            lines.append(
                f"⚠️ **Dry Spell Alert ({observed_dry_days} dry days recorded):** Low precipitation expected over the next week. Prioritize night or early-morning irrigation to curb evaporation loss."
            )
            lines.append(
                "• **Contingency Measure (IMD SOP):** Apply 0.5% potassium nitrate ($KNO_3$) or Kaolin (6%) anti-transpirant spray to alleviate heat and water stress."
            )
        else:
            lines.append(
                f"🌧️ **Precipitation Expected ({rain_7d:.1f} mm):** Postpone planned foliar sprays and clear field drainage channels to prevent water accumulation."
            )

        # Section 4: Verified Institutional Citations
        if references:
            lines.append("\n#### 📚 Verified Institutional Citations")
            for ref in references[:3]:
                lines.append(f"- **{ref['authority']}**: [{ref['document']}]({ref['url']})")

        return "\n".join(lines)

    def _synthesize_telugu(
        self,
        query: str,
        crop: str,
        crop_te: str,
        land_area: float,
        soil: str,
        irrigation: str,
        location_str: str,
        days_in_field: Optional[int],
        stage_info: Optional[Dict[str, Any]],
        curr_temp: float,
        curr_humidity: float,
        rain_7d: float,
        max_temp_7d: float,
        observed_dry_days: int,
        evidence_chunks: List[SearchResult],
        references: List[Dict[str, Any]],
    ) -> str:
        """Construct a structured, professional Telugu advisory response."""
        lines = []

        # Header with resource context
        lines.append(f"### 🌾 వ్యవసాయ సలహా & ప్రణాళిక: **{crop_te} ({crop})** — {location_str}")
        lines.append(
            f"**పొలం వివరాలు:** `{land_area:.1f} ఎకరాలు` • నేల: `{soil}` • నీటి వనరు: `{irrigation}`"
        )

        if days_in_field is not None and stage_info:
            stage_te = stage_info.get("stage_te", stage_info.get("stage"))
            water_te = stage_info.get("water_need_te", stage_info.get("water_need"))
            lines.append(
                f"**పంట వయస్సు & దశ:** విత్తిన తర్వాత `{days_in_field} రోజులు` • దశ: `{stage_te}` (నీటి అవసరం: `{water_te}`)"
            )
        else:
            lines.append(
                f"**పంట స్థితి:** విత్తిన తేదీ నమోదు చేయలేదు (సాధారణ ప్రాంతీయ సూచనలు వర్తిస్తాయి)."
            )

        lines.append("")

        # Telugu Topic Detection
        from src.nlp.text_normalization import normalize_text
        q_norm = f"{query} {normalize_text(query)}".lower()
        is_fertilizer = any(k in q_norm for k in [
            "fertilizer", "fertilizers", "manure", "fym", "urea", "dap", "potash", "mop", "ssp",
            "yerbulu", "yerubulu", "yeruvulu", "eruvulu", "eruvu", "yeruvu", "poshakalu",
            "nutrient", "nutrients", "vepapindi", "neem cake",
            "ఎరువులు", "ఎరువు", "ఎరువుల", "యూరియా", "డిఎపి", "పొటాష్", "వేపపిండి", "పోషకాలు"
        ])
        is_irrigation = (
            any(k in q_norm for k in ["irrigate", "irrigation", "water", "watering", "kattali", "pettali", "ivvali", "tadi", "thadi", "నీరు", "నీళ్లు", "నీళ్ళు", "నీటి", "తడి", "తడులు"])
            and not any(k in q_norm for k in ["rot", "blight", "spot", "pest", "purugu", "tegulu", "fertilizer", "eruvulu", "yerbulu"])
        )
        is_disease = any(k in q_norm for k in ["rot", "blight", "spot", "blotch", "wilt", "blast", "sigatoka", "rust", "pathogen", "fungus", "fungicide", "cure", "treatment", "symptom", "spray", "tegulu", "kullu", "dumpakullu", "verukullu", "aakumacha", "తెగులు", "తెగుళ్ళు", "కుళ్లు", "మచ్చ", "నివారణ", "పిచికారీ"])
        is_pest = any(k in q_norm for k in ["pest", "pests", "insect", "insects", "borer", "scale", "thrips", "aphid", "bph", "weevil", "worm", "caterpillar", "armyworm", "purugu", "పురుగు", "పురుగులు", "సుడిదోమ", "పీక"])
        is_weed = any(k in q_norm for k in ["weed", "weeds", "herbicide", "weeding", "atrazine", "pendimethalin", "kalupu", "కలుపు"])
        is_seed_sowing = any(k in q_norm for k in ["seed", "seeds", "sowing", "sow", "plant", "planting", "spacing", "variety", "varieties", "rate", "germination", "విత్తన", "విత్తనాలు", "నాటడం", "రకాలు", "ఎడము"])
        is_harvest_curing = any(k in q_norm for k in ["harvest", "harvesting", "curing", "cure", "boil", "boiling", "dry", "drying", "polish", "storage", "yield", "koto", "kotha", "koyyali", "koi", "arabalce", "arabettali", "aarabettali", "udikinchali", "కోత", "ఉడకబెట్టడం", "నిల్వ", "దిగుబడి", "ఆరబెట్టడం"])

        if is_fertilizer:
            lines.append("#### 🎯 ప్రత్యక్ష సమాధానం: సమగ్ర ఎరువుల ప్రణాళిక & వేళలు (ICAR-IISR శాస్త్రీయ మోతాదులు)")
            if crop == "Turmeric":
                lines.append(f"**మీ {land_area:.1f} ఎకరాల పొలానికి దశలవారీ ఎరువుల మోతాదు:**")
                lines.append(f"1. **నాటే సమయంలో (ఆఖరి దుక్కిలో):** ఎకరానికి 10 టన్నుల పశువుల ఎరువు (మొత్తం: {land_area * 10:.0f} టన్నులు) + వేపపిండి 200 కిలోలు (మొత్తం: {land_area * 200:.0f} కిలోలు) + 100% భాస్వరం ఎరువు (సింగిల్ సూపర్ ఫాస్ఫేట్ SSP @ 125 కిలోలు లేదా DAP @ 45 కిలోలు) వేసి కలియదున్నాలి.")
                lines.append(f"2. **మొదటి దఫా (నాటిన 30–40 రోజులకు):** మొదటి కలుపు తీసిన వెంటనే 1/3 వంతు నత్రజని (యూరియా @ 25 కిలోలు/ఎకరా -> {land_area * 25:.0f} కిలోలు) మరియు 1/3 వంతు పొటాష్ (MOP @ 20 కిలోలు/ఎకరా -> {land_area * 20:.0f} కిలోలు) వేసి తడి ఇవ్వాలి.")
                lines.append(f"3. **రెండవ దఫా (నాటిన 60–70 రోజులకు):** రెండవ దఫాగా 1/3 వంతు నత్రజని (యూరియా @ 25 కిలోలు/ఎకరా -> {land_area * 25:.0f} కిలోలు) మరియు 1/3 వంతు పొటాష్ (MOP @ 20 కిలోలు/ఎకరా -> {land_area * 20:.0f} కిలోలు) వేసి, మొక్కల మొదళ్లకు మట్టి ఎగదోసి మల్చింగ్ చేయాలి.")
                lines.append(f"4. **మూడవ దఫా (నాటిన 90–100 రోజులకు):** దుంప ఊరే దశలో మిగిలిన 1/3 వంతు నత్రజని (యూరియా @ 25 కిలోలు/ఎకరా -> {land_area * 25:.0f} కిలోలు) మరియు పొటాష్ (MOP @ 20 కిలోలు/ఎకరా -> {land_area * 20:.0f} కిలోలు) వేయాలి.")
                lines.append("5. **సూక్ష్మ పోషకాల పిచికారీ:** నాటిన 60 మరియు 90 రోజులకు ఐఐఎస్ఆర్ టర్మరిక్ స్పెషల్ లేదా జింక్ సల్ఫేట్ @ 2 గ్రా/లీటర్ + ఫెర్రస్ సల్ఫేట్ @ 2 గ్రా/లీటర్ కలిపి పిచికారీ చేయాలి.")
            elif crop == "Banana":
                lines.append(f"**అరటి పంటకు ఎరువుల షెడ్యూల్ ({land_area:.1f} ఎకరాలు):**")
                lines.append("1. **నాటే గుంతల్లో:** 10 కిలోల పశువుల ఎరువు + 250 గ్రాముల వేపపిండి.")
                lines.append("2. **టాప్ డ్రెస్సింగ్ (చెట్టుకు):** మొత్తం 300 గ్రాముల యూరియా + 300 గ్రాముల పొటాష్‌ను 2, 4, 6, మరియు 8వ నెలల్లో 4 సమభాగాలుగా విభజించి వేయాలి.")
                lines.append("3. **గెల ఊరే దశ:** గెల నాణ్యత మరియు బరువు పెరగడానికి 0.5% పొటాషియం సల్ఫేట్ పిచికారీ చేయాలి.")
            elif crop == "Paddy":
                lines.append(f"**వరి పంటకు ఎరువుల షెడ్యూల్ ({land_area:.1f} ఎకరాలు):**")
                lines.append(f"1. **నాటు వేసే సమయంలో:** 100% భాస్వరం (DAP @ 50 కి/ఎకరా -> {land_area * 50:.0f} కిలోలు) + 50% పొటాష్ (MOP @ 20 కి/ఎకరా -> {land_area * 20:.0f} కిలోలు) + 25% యూరియా ({land_area * 25:.0f} కిలోలు) + జింక్ సల్ఫేట్ @ 10 కి/ఎకరా.")
                lines.append(f"2. **పిలకల దశలో (20-25 రోజులు):** 50% యూరియా ({land_area * 50:.0f} కిలోలు).")
                lines.append(f"3. **చిరుపొట్ట దశలో (40-45 రోజులు):** మిగిలిన 25% యూరియా ({land_area * 25:.0f} కిలోలు) + 50% పొటాష్ ({land_area * 20:.0f} కిలోలు).")
            lines.append("")

        elif is_irrigation:
            lines.append("#### 🎯 ప్రత్యక్ష సమాధానం: సాగునీటి యాజమాన్యం & తడుల ప్రణాళిక (ICAR ప్రామాణికం)")
            if crop == "Turmeric":
                lines.append(f"• **నీటి తడుల వ్యవధి ({soil}):** సాధారణ రోజుల్లో ప్రతి 7–10 రోజులకు ఒకసారి తడి ఇవ్వాలి; ఎండ తీవ్రత లేదా వర్షాభావ రోజుల్లో 5–7 రోజులకు ఒకసారి తడి ఇవ్వాలి.")
                lines.append("• **ముఖ్యమైన దశలు:** దుంప మొలకెత్తే దశ, పిలకలు వేసే దశ (40–60 రోజులు), మరియు దుంప ఊరే దశ (90–150 రోజులు) లో తేమ తగ్గకుండా చూడాలి.")
                lines.append("• **డ్రిప్ పద్ధతి:** రోజు విడిచి రోజు 2–3 గంటలు డ్రిప్ ద్వారా నీటిని అందించాలి (ఎకరానికి సుమారు 40,000 లీటర్లు).")
                lines.append("• **మురుగు నీటి కాలువలు:** పొలంలో నీరు నిల్వ ఉండకుండా 30 సెం.మీ లోతు కాలువలు తీయాలి. నిల్వ నీటి వల్ల దుంపకుళ్లు తెగులు ఆశిస్తుంది.")
            elif crop == "Banana":
                lines.append("• **నీటి తడులు:** వేసవిలో ప్రతి 4–5 రోజులకు, శీతాకాలంలో 7–8 రోజులకు తడి ఇవ్వాలి. డ్రిప్ ద్వారా మొక్కకు రోజుకు 15–20 లీటర్ల నీరు అవసరం.")
            elif crop == "Paddy":
                lines.append("• **పొడి-తడి పద్ధతి (AWD):** పిలకల దశలో నేల తేమ ఆరిపోయి చిన్న పగుళ్లు వచ్చేవరకు ఆగి 2-3 సెం.మీ నీరు పెట్టాలి. చిరుపొట్ట నుండి ఈనిక పూర్తయ్యే వరకు పొలంలో నిరంతరం 3-5 సెం.మీ నీరు ఉంచాలి.")
            lines.append("")

        elif is_harvest_curing:
            lines.append("#### 🎯 ప్రత్యక్ష సమాధానం: పంట కోత & ఉడకబెట్టి ఆరబెట్టే విధానం (ICAR మార్గదర్శకాలు)")
            if crop == "Turmeric":
                lines.append("1. **🗓️ కోత సమయం & పక్వత సూచికలు:** నాటిన 7–9 నెలలకు (జనవరి–మార్చి) ఆకులు పూర్తిగా పసుపు రంగులోకి మారి ఎండిపోయి నేలకొరిగినప్పుడు దుంపలను తవ్వాలి.")
                lines.append("2. **♨️ ఉడకబెట్టే విధానం (Curing / Boiling):** శుభ్రపరిచిన పసుపు కొమ్ములను ఇనుప బాణళ్లలో లేదా స్టీమ్ బాయిలర్లలో 45–60 నిమిషాలు ఉడకబెట్టాలి. వేలితో నొక్కితే మెత్తగా ఉండి, తెల్లటి నురుగు మరియు పసుపు సువాసన వచ్చేవరకు ఉడికించాలి.")
                lines.append("3. **☀️ ఆరబెట్టే విధానం (Sun Drying):** ఉడికించిన కొమ్ములను శుభ్రమైన టార్పాలిన్లపై 5–7 సెం.మీ మందంలో పరచి 10–15 రోజులు ఎండబెట్టాలి. తేమ 8–10% కి తగ్గే వరకు ఆరబెట్టాలి (విరిస్తే టక్ మని శబ్దం రావాలి).")
                lines.append("4. **⚙️ పాలిషింగ్ & నిల్వ:** డ్రమ్ పాలిషర్ల ద్వారా గరుకు పొరను తొలగించి పాలిష్ చేయాలి. గాలి వెలుతురు ఉండే గోదాముల్లో శుభ్రమైన గన్నీ సంచులలో నిల్వ చేయాలి.")
            elif crop == "Banana":
                lines.append("• **కోత:** గెలల కాయలలోని గీతలు పోయి గుండ్రంగా మారినప్పుడు (75-80% పక్వత) కోయాలి. 1% పటిక నీటిలో పాలు కడిగి ఆరబెట్టి ప్యాక్ చేయాలి.")
            elif crop == "Paddy":
                lines.append("• **కోత & నిల్వ:** 80-85% గింజలు బంగారు రంగులోకి మారినప్పుడు కోయాలి. నూర్పిడి చేసి తేమ 12-14% వచ్చే వరకు ఆరబెట్టి నిల్వ చేయాలి.")
            lines.append("")

        elif is_disease:
            lines.append("#### 🎯 ప్రత్యక్ష సమాధానం: తెగుళ్ల నివారణ & రసాయన మందుల మోతాదు (ICAR ప్యాకేజీ)")
            if crop == "Turmeric":
                lines.append("• **దుంపకుళ్లు తెగులు (*Pythium*):** ఆకులు పసుపు రంగులోకి మారి మొదళ్ల వద్ద మెత్తబడి దుర్వాసన వస్తుంది. నాటే ముందు దుంపలను మెటాలాక్సిల్-మాంకోజెబ్ (రిడోమిల్) @ 2.5 గ్రా/లీటర్ నీటిలో 30 నిమిషాలు నానబెట్టి విత్తన శుద్ధి చేయాలి. తెగులు ఆశించిన మొక్కల మొదళ్లలో కాపర్ ఆక్సిక్లోరైడ్ (COC) @ 2.5 గ్రా/లీటర్ లేదా రిడోమిల్ @ 1.25 గ్రా/లీటర్ కలిపి నేల తడిసేలా పిచికారీ చేయాలి. ఎకరానికి 50 కిలోల పశువుల ఎరువులో 2.5 కిలోల ట్రైకోడెర్మా విరిడి కలిపి నేలలో వేయాలి.")
                lines.append("• **ఆకుమచ్చ & కొమ్మ ఎండు తెగులు (*Taphrina* / *Colletotrichum*):** మాంకోజెబ్ @ 2.5 గ్రా/లీటర్ లేదా అజాక్సిస్ట్రోబిన్ @ 1.0 మి.లీ/లీటర్ లేదా ప్రొపికొనజోల్ @ 1.0 మి.లీ/లీటర్ చొప్పున 15 రోజుల వ్యవధిలో రెండుసార్లు పిచికారీ చేయాలి.")
            elif crop == "Banana":
                lines.append("• **సిగటోకా ఆకుమచ్చ తెగులు:** ప్రొపికొనజోల్ @ 1.0 మి.లీ లేదా కార్బెండజిమ్ @ 1.0 గ్రా/లీటర్ నీటిలో కలిపి మినరల్ ఆయిల్ 1% తో కలిపి పిచికారీ చేయాలి.")
                lines.append("• **పనామా వాడి తెగులు (*Fusarium*):** కార్బెండజిమ్ 2% ద్రావణాన్ని పిలకలలో ఇంజెక్ట్ చేయాలి లేదా 50-60 మి.గ్రా కార్బెండజిమ్ క్యాప్సూల్ వేయాలి.")
            elif crop == "Paddy":
                lines.append("• **అగ్గితెగులు (Blast):** ట్రైసైక్లాజోల్ 75% WP @ 0.6 గ్రా/లీటర్ లేదా ఐసోప్రోథియోలేన్ 40% EC @ 1.5 మి.లీ/లీటర్ పిచికారీ చేయాలి.")
                lines.append("• **పొడతెగులు (Sheath Blight):** వేలిడామైసిన్ 3% L @ 2.0 మి.లీ లేదా హెక్సాకొనజోల్ 5% EC @ 2.0 మి.లీ/లీటర్ పిచికారీ చేయాలి.")
            lines.append("")

        elif is_pest:
            lines.append("#### 🎯 ప్రత్యక్ష సమాధానం: పురుగుల నివారణ & సమగ్ర సస్యరక్షణ (ICAR-IPM)")
            if crop == "Turmeric":
                lines.append("• **దుంప ఈగ & కాండం తొలిచే పురుగు (Shoot Borer):** లార్వాలు పిలకల లోపలికి తొలిచి ఎండిపోయేలా చేస్తాయి. క్లోరాంట్రానిలిప్రోల్ 18.5% SC @ 0.3 మి.లీ లేదా డైమిథోయేట్ 30% EC @ 1.7 మి.లీ/లీటర్ నీటిలో కలిపి పిచికారీ చేయాలి. జైవిక నివారణగా ఎకరానికి 40,000 ట్రైకోగ్రామా చిలోనిస్ గుడ్ల కార్డులను విడుదల చేయాలి.")
                lines.append("• **దుంప పొలుసు పురుగు (Rhizome Scale):** నాటే ముందు మరియు నిల్వ చేసే ముందు దుంపలను క్వినాల్‌ఫాస్ 25% EC @ 2.0 మి.లీ/లీటర్ ద్రావణంలో 15 నిమిషాలు ముంచాలి.")
                lines.append("• **తామర పురుగులు & నల్లి:** వేప నూనె 5 మి.లీ/లీటర్ లేదా ఇమిడాక్లోప్రిడ్ 17.8% SL @ 0.3 మి.లీ/లీటర్ పిచికారీ చేయాలి.")
            elif crop == "Banana":
                lines.append("• **కాండం తొలుచు పురుగు (Pseudostem Weevil):** క్లోర్‌పైరిఫాస్ 20% EC @ 2.5 మి.లీ/లీటర్ కాండంపై పూయాలి లేదా 20 చీల్చిన కాండపు ఉచ్చులు పెట్టాలి.")
            elif crop == "Paddy":
                lines.append("• **సుడిదోమ (BPH):** ప్రతి 2.5-3 మీటర్లకు 30 సెం.మీ బాటలు తీయాలి. ట్రైఫ్లూమెజోపైరిమ్ 10% SC @ 0.5 మి.లీ లేదా పైమెట్రోజిన్ 50% WDG @ 0.6 గ్రా/లీటర్ మొక్కల మొదళ్లకు తగిలేలా పిచికారీ చేయాలి.")
                lines.append("• **కాండం తొలిచే పురుగు:** కార్టాప్ హైడ్రోక్లోరైడ్ 4% గుళికలు ఎకరానికి 10 కిలోలు లేదా క్లోరాంట్రానిలిప్రోల్ 0.3 మి.లీ/లీటర్ పిచికారీ చేయాలి.")
            lines.append("")

        elif is_weed:
            lines.append("#### 🎯 ప్రత్యక్ష సమాధానం: కలుపు యాజమాన్యం & నివారణ పద్ధతులు")
            if crop == "Turmeric":
                lines.append("• **మొలక రాకముందు కలుపు మందు:** నాటిన 2-3 రోజులలోపు నేలలో తగినంత తేమ ఉన్నప్పుడు పెండిమిథాలిన్ 30% EC ఎకరానికి 1.3 లీటర్లు లేదా అట్రాజిన్ 50% WP ఎకరానికి 800 గ్రాములు పిచికారీ చేయాలి.")
                lines.append("• **చేతితో కలుపు తీత:** నాటిన 30, 60, 90 రోజులకు చేతితో కలుపు తీసి మొదళ్లకు మట్టి ఎగదోయాలి.")
                lines.append("• **మల్చింగ్ రక్షణ:** ఎకరానికి 4-5 టన్నుల పచ్చిరొట్ట లేదా ఎండుగడ్డితో మల్చింగ్ చేయడం వల్ల కలుపు మొలకెత్తకుండా అణచివేయబడుతుంది.")
            elif crop == "Banana":
                lines.append("• **వరుసల మధ్య కలుపు:** వరుసల మధ్య గ్లైఫోసేట్ 41% SL ఎకరానికి 1 లీటరు హుడ్ వాడి పిచికారీ చేయాలి; మొదళ్ల వద్ద గరిటెలతో శుభ్రం చేయాలి.")
            elif crop == "Paddy":
                lines.append("• **వరిలో కలుపు మందులు:** నాటిన 3-5 రోజుల్లో ప్రిటిలాక్లోర్ 50% EC ఎకరానికి 400 మి.లీ; నాటిన 15-20 రోజుల్లో బిస్పైరిబాక్ సోడియం ఎకరానికి 100 మి.లీ పిచికారీ చేయాలి.")
            lines.append("")

        elif is_seed_sowing:
            lines.append("#### 🎯 ప్రత్యక్ష సమాధానం: విత్తన మోతాదు, విత్తన శుద్ధి & నాటే పద్ధతి")
            if crop == "Turmeric":
                lines.append("• **విత్తన మోతాదు:** ఎకరానికి 1,000 కిలోలు (10 క్వింటాళ్లు) తెగుళ్లు లేని తల్లి దుంపలు లేదా గడ్డ దుంపలు అవసరం.")
                lines.append("• **ఎడము (Spacing):** బోదెల పద్ధతిలో సాళ్ల మధ్య 45 సెం.మీ, మొక్కల మధ్య 15 సెం.మీ; ఎత్తైన మడులపై 30 x 15 సెం.మీ దూరంలో నాటాలి.")
                lines.append("• **విత్తన శుద్ధి:** మాంకోజెబ్ 3 గ్రా/లీ + క్లోర్‌పైరిఫాస్ 2 మి.లీ/లీటర్ ద్రావణంలో దుంపలను 30 నిమిషాలు నానబెట్టి, నీడలో ఆరబెట్టి నాటాలి.")
                lines.append("• **అధిక దిగుబడి రకాలు:** ఐఐఎస్ఆర్ ప్రతిభ (కుర్కుమిన్ 6.25%), ఐఐఎస్ఆర్ కేదారం, బిఎస్ఆర్-2, రంగా, రోమా.")
            elif crop == "Banana":
                lines.append("• **పిలకల ఎంపిక:** ఎకరానికి 1,000-1,200 సూది పిలకలు (1.5-2 కిలోలు) లేదా కణజాల వర్ధన మొక్కలు. దూరం: 1.8 x 1.8 మీటర్లు.")
                lines.append("• **పిలకల శుద్ధి:** పిలకలను 50°C వేడినీటిలో 20 నిమిషాలు ముంచి నులిపురుగులను నివారించాలి.")
            elif crop == "Paddy":
                lines.append("• **విత్తన మోతాదు:** నాటు పద్ధతికి ఎకరానికి 20-25 కిలోలు; డ్రమ్ సీడర్ పద్ధతికి 12-15 కిలోలు. దూరం: 20 x 15 సెం.మీ.")
                lines.append("• **విత్తన శుద్ధి:** కిలో విత్తనానికి 2 గ్రాముల కార్బెండజిమ్ లేదా 10 గ్రాముల సూడోమోనాస్ కలిపి శుద్ధి చేయాలి.")
            lines.append("")

        # Section: Core Recommendations & Agronomic Guidance
        lines.append("#### 📋 ప్రామాణిక వ్యవసాయ సూచనలు & సలహాలు")
        if evidence_chunks:
            primary_chunk = evidence_chunks[0]
            clean_snippet = primary_chunk.text.replace("\n\n", " ").strip()
            if len(clean_snippet) > 350:
                clean_snippet = clean_snippet[:350] + "..."
            lines.append(f"> *\"{clean_snippet}\"*")
            lines.append(
                f"> — **ఆధారం:** {primary_chunk.organization}, *{primary_chunk.document_title}*, పేజీ {primary_chunk.page_number}\n"
            )

        if crop == "Turmeric":
            lines.append("• **నీటిపారుదల షెడ్యూల్:** ఎర్ర ఇసుక నేలల్లో 7-10 రోజులకు ఒకసారి, ఎండలు తీవ్రంగా ఉంటే 5-7 రోజులకు తడి ఇవ్వాలి. వరద నీరు నిలవకుండా చూడాలి.")
            lines.append("• **మురుగునీటి నివారణ:** దుంపకుళ్లు తెగులు (*Pythium*) రాకుండా మడులలో 30 సెం.మీ లోతైన మురుగునీటి కాలువలు తీయాలి.")
            lines.append("• **మల్చింగ్ (రక్షక పొర):** నేలలో తేమను కాపాడటానికి ఎకరానికి 4-4.8 టన్నుల పచ్చిరొట్ట లేదా ఎండుగడ్డితో మల్చింగ్ చేయాలి.")
        elif crop == "Banana":
            lines.append("• **బిందు సేద్యం (డ్రిప్):** పోషకాల వృథా అరికట్టడానికి బిందు సేద్యం ద్వారా ప్రతిరోజూ లేదా రోజు విడిచి రోజు నీరు అందించాలి.")
            lines.append("• **పిలకల వేడినీటి చికిత్స:** నాటే ముందు పిలకలను 50°C వేడినీటిలో ముంచి నిప్పు పురుగులు మరియు వేరుపురుగులను నివారించాలి.")
            lines.append("• **ఎరువుల తర్వాత తడి:** యూరియా మరియు డీఏపీ వేసిన వెంటనే తేలికపాటి తడి అందించడం తప్పనిసరి.")
        elif crop == "Paddy":
            lines.append("• **ఆల్టర్నేట్ వెట్టింగ్ & డ్రైయింగ్ (AWD):** వరిలో నీరు ఆరిన తర్వాత మాత్రమే 2-3 సెం.మీ తడి ఇవ్వడం ద్వారా 25-30% నీటిని ఆదా చేయవచ్చు.")
            lines.append("• **కీలక దశ:** ఈనిక మరియు పూత దశలో పొలంలో 3-5 సెం.మీ మేర నీరు నిరంతరం ఉండేలా చూసుకోవాలి.")
            lines.append("• **బాటలు తీయడం:** సుడిదోమ మరియు అగ్గితెగులు రాకుండా ప్రతి 2.5-3 మీటర్లకు 30 సెం.మీ బాటలు తీయాలి.")

        lines.append("")

        lines.append("")

        # Section 2: Resource Allocation
        lines.append("#### 🛠️ మీ పొలానికి అనుగుణంగా వనరుల ప్రణాళిక")
        if crop == "Turmeric":
            fert_te = (
                f"మీ **{land_area:.1f} ఎకరాలకు** ఎరువుల షెడ్యూల్ (ICAR-IISR సిఫార్సు):\n"
                f"  1. **నాటే సమయంలో (Basal):** ఎకరానికి 10 టన్నుల పశువుల ఎరువు ({land_area * 10:.0f} టన్నులు) + 200 కిలోల వేపపిండి + పూర్తి భాస్వరం ఎరువు (SSP లేదా DAP).\n"
                f"  2. **నాటిన 30–40 రోజులకు:** మొదటి దఫాగా 1/3 వంతు యూరియా మరియు 1/3 వంతు పొటాష్ వేసి కలుపు తీయాలి.\n"
                f"  3. **నాటిన 60 రోజులకు:** రెండవ దఫాగా 1/3 వంతు యూరియా మరియు పొటాష్ వేసి మొదళ్ల వద్ద మట్టి ఎగదోసి బోదెలు చేయాలి.\n"
                f"  4. **నాటిన 90–100 రోజులకు:** మిగిలిన యూరియా మరియు పొటాష్ అందించి దుంపలు ఊరే దశలో తేలికపాటి తడి ఇవ్వాలి."
            )
        elif crop == "Banana":
            fert_te = f"మీ **{land_area:.1f} ఎకరాలకు**: సుమారు {land_area * 1000:.0f} మొక్కలకు షెడ్యూల్ ప్రకారం ఎరువులను డ్రిప్ ద్వారా అందించండి."
        else:
            fert_te = f"మీ **{land_area:.1f} ఎకరాలకు**: ఎకరాకు సిఫార్సు చేసిన నత్రజని, భాస్వరం, పొటాష్ ఎరువులను 3 సమ భాగాలుగా వేయాలి."

        lines.append(f"• **ఎరువుల నిర్వహణ:** {fert_te}")
        lines.append(f"• **నీటి వనరు ({irrigation}):** నీటి కొరత ఉంటే రక్షక తడులు మాత్రమే ఇవ్వండి; రాత్రి లేదా వేకువజామున నీటిపారుదల చేపట్టడం శ్రేయస్కరం.")

        lines.append("")

        # Section 3: Weather Intelligence
        lines.append("#### ⛅ ప్రత్యక్ష వాతావరణం & ఎల్ నినో కార్యాచరణ")
        lines.append(
            f"• **ప్రస్తుత ఉష్ణోగ్రత:** `{curr_temp:.1f} °C` | తేమ: `{curr_humidity:.0f} %`"
        )
        lines.append(
            f"• **రాబోయే 7 రోజుల వర్షం అంచనా:** **`{rain_7d:.1f} మి.మీ`** | గరిష్ట ఉష్ణోగ్రత: **`{max_temp_7d:.1f} °C`**"
        )

        if rain_7d < 5.0:
            lines.append(
                f"⚠️ **వర్షాభావ హెచ్చరిక ({observed_dry_days} పొడి రోజులు నమోదయ్యాయి):** రాబోయే వారం రోజులు వర్షం పడే అవకాశం చాలా తక్కువ. ఆవిరి నష్టాన్ని నివారించడానికి ఉదయం లేదా సాయంత్రం వేళల్లోనే నీరు పెట్టండి."
            )
            lines.append(
                "• **ఐఎండీ సూచన:** వేడి ఒత్తిడిని తట్టుకోవడానికి 0.5% పొటాషియం నైట్రేట్ లేదా 6% కయోలిన్ పిచికారీ చేయండి."
            )
        else:
            lines.append(
                f"🌧️ **వర్ష సూచన ({rain_7d:.1f} మి.మీ):** పిచికారీలను వాయిదా వేయండి; పొలంలో మురుగునీరు బయటకు పోయేలా కాలువలను సరిచేసుకోండి."
            )

        if references:
            lines.append("\n#### 📚 ప్రామాణిక పరిశోధనా ఆధారాలు")
            for ref in references[:3]:
                lines.append(f"- **{ref['authority']}**: [{ref['document']}]({ref['url']})")

        return "\n".join(lines)
