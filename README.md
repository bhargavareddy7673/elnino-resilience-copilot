# 🌾 RythuMithra NLP
### Multilingual Conversational Voice Assistant for El Niño Resilience (రైతు మిత్ర)
**An End-to-End Natural Language Processing (NLP) & Speech Decision Support System for Smallholder Farmers**

> **Target Agro-Climatic Regions:** Andhra Pradesh (Default: Kurnool & Kadapa) & Telangana  
> **Key Crops:** Turmeric (పసుపు), Banana (అరటి), Paddy (వరి)  
> **Core Framework:** Python 3.11+, Streamlit, Hugging Face Transformers & Open-Meteo Real-Time Telemetry

---

## 📖 Executive Summary

Climate phenomena such as **El Niño** induce extreme weather shocks across South India, leading to delayed monsoon onset, extended dry spells, thermal anomalies, and groundwater depletion during critical crop phenological stages.

**RythuMithra NLP (రైతు మిత్ర)** is an end-to-end intelligent agricultural Natural Language Processing & decision-support platform designed specifically for smallholder farmers. It integrates a live **Farm Digital Twin**, real-time meteorological intelligence, computer vision crop pathology, and a **bilingual spoken voice & text conversational advisor** in English, Telugu, and code-mixed Tanglish.

---

## 🌟 Key Capabilities & Architecture

### 1. 🎙️ Dual-Tier Spoken Voice & Text Farm Advisor
- **Bilingual Speech Recognition (Telugu & English):** Instant transcription supporting pure Telugu (`te-IN`), Indian English (`en-IN`), and romanized farmer phrasing (Tanglish like *"naha paspupanta ko yerbulu yopude yali"*).
- **Dual-Tier Hybrid ASR Engine:**
  - **Tier 1 (High-Speed Online):** Cloud Google Speech Recognition (~300ms latency, zero memory footprint, 100% cloud deployment compatibility).
  - **Tier 2 (Offline Edge Fallback):** Hugging Face Whisper-tiny with volume normalization and anti-hallucination guardrails.
- **Spoken Voice Advisory Output:** Conversational answers are automatically spoken aloud through an interactive audio player with animated equalizer waves (`▂ ▃ ▅ ▆ ▇ ▆ ▅ ▃ ▂`), Stop/Replay buttons, and concise, actionable bullet points.
- **Simultaneous Text Chat:** Full keyboard chat composer and 2x2 grid of 1-click suggested prompt chips tailored to the active crop.

### 2. 🌾 Farm Digital Twin & Resource Budgeting
- Virtual plot representation tracking state, district, village, crop, exact decimal acreage (e.g. 4.0 Acres), soil taxonomy, and water source (Borewell, Canal, Rainfed).
- Mathematical fertilizer dosage calculators providing split-schedule recommendations (FYM, Neem cake, Urea, DAP, MOP) based on ICAR-IISR and ANGRAU packages of practices.

### 3. 🔬 Leaf Doctor (Multimodal Crop Vision)
- Visual pathology inspection of crop leaves using camera capture or image upload.
- Diagnoses leaf spot, rhizome rot, blast, Panama wilt, and Sigatoka against DPPQS/ICAR standards with severity ratings and treatment protocols.

### 4. ⛅ Real-Time Atmospheric & El Niño Intelligence
- Live Open-Meteo API integration for temperature, relative humidity, wind speed, and precipitation.
- 7-day agricultural forecasts with interactive dual-axis Plotly charts.
- Historical 30-day precipitation curves, dry-spell duration counters, and thermal risk indicators.

### 5. 🔮 El Niño What-If Scenario Simulator
- Stress-tests farm resilience against user-adjusted climate scenarios (e.g., 30% rainfall deficit, +3°C heatwaves, irrigation canal outages).
- Simulates soil moisture depletion, yield penalty projections, and triggers IMD/ICAR contingency actions.

---

## 📂 Project Structure

```text
RythuMithra_AI/
├── app.py                      # Main Streamlit web application & routing entrypoint
├── requirements.txt            # Production dependencies for local & Streamlit Cloud
├── README.md                   # Comprehensive documentation and evaluation guide
├── src/
│   ├── config.py               # Constants: AP (26) & TS (33) districts, soils, crops
│   ├── localization.py         # Bilingual English & Telugu (తెలుగు) UI dictionaries
│   ├── agents/
│   │   ├── controller.py       # Master agent dispatcher & NLP routing
│   │   ├── crop_advisory_agent.py # Agronomic guidance & ICAR citations
│   │   ├── risk_analysis_agent.py # Thermal & precipitation risk analysis
│   │   └── weather_agent.py    # Atmospheric telemetry synthesis
│   ├── components/
│   │   ├── advisor_view.py     # AI Farm Advisor (Voice + Text Chat + Leaf Doctor)
│   │   ├── farm_view.py        # Farm Digital Twin configuration & profile
│   │   ├── home_view.py        # Welcome dashboard & quick telemetry glance
│   │   ├── simulator_view.py   # El Niño What-If Simulation Engine
│   │   └── weather_view.py     # 7-day forecast & 30-day rainfall charts
│   ├── multimodal/
│   │   ├── audio_transcriber.py # Dual-tier Google/Whisper ASR & TTS speech synthesis
│   │   └── crop_vision.py      # Leaf pathology diagnostics & symptom analysis
│   ├── nlp/
│   │   ├── entity_extractor.py # Crops, districts, dates, and agronomic concepts
│   │   ├── intent_classifier.py # Hybrid SetFit MiniLM-L12 + rule classifier
│   │   ├── language_detection.py# Unicode Telugu vs English detection
│   │   └── text_normalization.py# Tanglish transliteration & phonetic normalization
│   ├── rag/
│   │   ├── ingestor.py         # PDF document ingestion from ICAR/DPPQS manuals
│   │   ├── retriever.py        # Hybrid BM25 + dense semantic retriever
│   │   └── synthesizer.py      # Citation-grounded advisory generation
│   └── weather/
│       ├── location_service.py # Verified district coordinates
│       └── weather_api.py      # Open-Meteo live forecast & archive client
└── tests/                      # Automated unit & integration test suites
```

---

## 🚀 Quickstart & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/bhargavareddy7673/elnino-resilience-copilot.git
cd elnino-resilience-copilot
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## ☁️ Streamlit Community Cloud Deployment Guide

1. Push your repository to **GitHub**.
2. Visit [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
3. Click **"New App"** and select:
   - **Repository:** `bhargavareddy7673/elnino-resilience-copilot`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. (Optional) In **Advanced Settings -> Secrets**, add:
   ```toml
   HF_MODEL_REPO_ID = "BHARGAVAREDDY1/elnino-agri-setfit"
   HF_MODEL_REVISION = "0a50cfd0b1e2e6fcf9e2cd3a3bafcaecbd5fd0f0"
   HF_TOKEN = "hf_your_huggingface_read_token"
   ```
   *Note: If no Hugging Face token is provided, the platform automatically runs on the deterministic, verified rule & retrieval engine without crashing.*
5. Click **Deploy!**

---

## 📚 Institutional Citations & References
- **ICAR-IISR (Indian Institute of Spices Research):** Package of Practices for Turmeric.
- **DPPQS (Directorate of Plant Protection, Quarantine & Storage):** Integrated Pest Management Package for Turmeric & Paddy.
- **ANGRAU (Acharya N.G. Ranga Agricultural University):** Crop Production & Contingency Guidelines for Rayalaseema & Coastal AP.
- **IMD (India Meteorological Department):** Agromet Advisory Services & SOP for El Niño Contingencies.
- **Open-Meteo API:** High-resolution meteorological forecasts & ECMWF ERA5 reanalysis (CC BY 4.0).
