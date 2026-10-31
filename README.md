# 🌾 El Niño Resilience Co-Pilot
### Agentic Farm Digital Twin with Multilingual NLP Advisor

> **Academic Level:** College Capstone / Individual Project  
> **Target Region:** Andhra Pradesh (Default: Kadapa District) & Telangana  
> **Key Crops:** Turmeric (పసుపు), Banana (అరటి), Paddy (వరి)  
> **Platform:** Python 3.11+ & Streamlit (Optimized for macOS / Apple Silicon M1)

---

## 📖 Project Overview

Climate phenomena such as **El Niño** induce significant weather variability across South India, leading to delayed monsoon onset, extended dry spells, and thermal stress during critical crop phenological stages.

This project develops a **Farm Digital Twin**: a virtual software representation of a farmer's plot that tracks location, soil characteristics, water availability, and crop age. This digital twin forms the foundation for subsequent modules that simulate climate risk and deliver bilingual advisory (English & Telugu) to assist farmers in decision-making.

> **Transparency Note:** This project is an academic simulation and educational prototype. Weather risk factors and crop vulnerability models are formulated for educational exploration and research, avoiding unsubstantiated claims of live field sensor validation.

---

## 📂 Project Architecture & Modules

The codebase is structured into modular components to ensure clean separation of concerns and maintainability:

```text
ElNino_Resilience_CoPilot/
├── app.py                      # Main Streamlit web application entrypoint
├── requirements.txt            # Python dependencies (Streamlit, Requests, Plotly, Pandas)
├── README.md                   # Beginner-friendly documentation and guide
├── .gitignore                  # Files and folders to exclude from version control
├── venv/                       # Isolated Python virtual environment
└── src/                        # Core source code package
    ├── __init__.py             # Marks 'src' as a Python package
    ├── config.py               # Constants: AP & Telangana districts, crops, soil, defaults
    ├── localization.py         # English and Telugu (తెలుగు) UI translations
    ├── components/
    │   ├── __init__.py         # Marks 'components' as a sub-package
    │   ├── home_view.py        # 1. HOME: Welcome hero, weather glance, alerts, quick actions
    │   ├── farm_view.py        # 2. MY FARM: Profile configuration & Digital Twin snapshot
    │   ├── weather_view.py     # 3. WEATHER: Telemetry, 7-day forecast, 30-day rain & indicators
    │   ├── advisor_view.py     # 4. AI FARM ADVISOR: Bilingual chat UI with suggested prompts
    │   └── crop_guidance_view.py # 5. CROP GUIDANCE: Turmeric, Banana, Paddy agronomic guide
    ├── nlp/
    │   ├── __init__.py         # NLP pipeline package
    │   ├── language_detection.py # Unicode Telugu vs English detection & code-mixing
    │   ├── text_normalization.py # Lowercasing, cleaning, transliteration mapping
    │   ├── entity_extractor.py # Crops (పసుపు, అరటి, వరి), districts, time periods
    │   └── intent_classifier.py # Transparent 8-intent rule-based classification
    ├── knowledge/
    │   ├── __init__.py         # Crop knowledge package
    │   └── crop_knowledge.py   # ICAR/ANGRAU crop physiology, stages, & resilience
    ├── agents/
    │   ├── __init__.py         # Agricultural agents package
    │   ├── controller.py       # Master agent coordinator & pipeline dispatcher
    │   ├── weather_agent.py    # Atmospheric telemetry & forecast synthesis
    │   ├── risk_analysis_agent.py # Climate indicator explanation & thermal risk
    │   └── crop_advisory_agent.py # Agronomic precautions & institutional references
    └── weather/
        ├── __init__.py         # Marks 'weather' as a sub-package
        ├── location_service.py # Verified district coordinates (AP 26, TS 33)
        ├── weather_api.py      # Open-Meteo live forecast & archive client with cache
        └── weather_analysis.py # Dry-spell detection, climate indicators, crop context
```

### Module Breakdown:
1. **`app.py`**: The entrypoint that launches the dashboard, handles page configuration, applies custom agricultural styling, and arranges the tabs and sidebar.
2. **`src/config.py`**: Holds structured lists of all 26 districts of Andhra Pradesh (with Kadapa as default), 33 districts of Telangana, crop characteristics (Turmeric, Banana, Paddy), soil types, and irrigation methods.
3. **`src/localization.py`**: Contains translations for all text elements in English and Telugu (`en` and `te`), allowing farmers to toggle the interface seamlessly.
4. **`src/components/profile_form.py`**: Renders the input form, saves data into `st.session_state` (persisting user inputs during the session), and renders the **Farm Digital Twin** snapshot card.
5. **`src/weather/location_service.py`**: Maps farmer profile locations to verified district headquarters coordinates across Andhra Pradesh and Telangana.
6. **`src/weather/weather_api.py`**: Queries Open-Meteo Forecast and Reanalysis APIs with 15-minute caching, timeouts, and transparent error reporting without substituting fake values.
7. **`src/weather/weather_analysis.py`**: Computes consecutive dry days, thermal stress, rainfall availability, and crop-specific sensitivity context for Turmeric, Banana, and Paddy.
8. **`src/components/weather_dashboard.py`**: Renders current atmospheric metrics, dual-axis interactive Plotly charts, 30-day precipitation history, and agricultural climate indicators.

---

## 🚀 How to Run the Application (Beginner-Friendly Guide)

Follow these step-by-step instructions in your terminal:

### Step 1: Open Terminal and Navigate to the Project Folder
Ensure your terminal is located in the project directory:
```bash
cd ElNino_Resilience_CoPilot
```
*What this does:* Moves your terminal session into the root directory of this project.

---

### Step 2: Activate the Virtual Environment
A virtual environment (`venv`) keeps project dependencies self-contained without affecting your global computer settings:
```bash
source venv/bin/activate
```
*What this does:* Sets your active Python and Pip binaries to the project's local `./venv/bin/` folder. Your terminal prompt will display `(venv)`.

---

### Step 3: Install Dependencies (Already Pre-installed in setup)
If you ever need to reinstall or install on another machine:
```bash
pip install -r requirements.txt
```
*What this does:* Installs `streamlit` and its lightweight helper packages into the `venv` directory.

---

### Step 4: Run the Streamlit Web Application
Execute the following command:
```bash
streamlit run app.py
```
*What this does:*
1. Starts a lightweight local web server on your Mac.
2. Opens your default web browser automatically at `http://localhost:8501`.
3. Displays the **El Niño Resilience Co-Pilot** dashboard.

To stop the web server when you are done, press `Ctrl + C` in the terminal.

---

## 🛠️ Features & Enhancements Implemented in Stage 1

- [x] **Lightweight Streamlit Web App:** Fast, responsive, running locally on Apple Silicon M1.
- [x] **High-Contrast Agricultural Design System:**
  - Deep forest green (`#1b4332`), muted sage (`#d8f3dc`), and warm off-white tones.
  - Custom CSS ensuring complete readability for dashboard metric cards in both **Light and Dark themes** (no white-on-white text).
- [x] **Robust Land Area Input & Validation:**
  - Accepts exact decimal values (e.g., `0.5`, `1.25`, `2.75`, `4.00`) without rounding or false step errors.
  - Validates that area must be greater than 0 acres.
- [x] **Refined Bilingual Telugu & English Localization:**
  - Full translations for labels, dropdown options, units, buttons, metrics, and academic notices.
  - Proper administrative nouns (district names) kept clean and uncorrupted.
  - Telugu typography with enhanced line height to prevent diacritic clipping.
- [x] **Flexible Farmer Profile Defaults:**
  - Default district is **Kadapa (YSR Kadapa)**, Andhra Pradesh.
  - Village name is fully editable without forcing assumptions of Duvvur or Khajipet.
  - Reactive state-district synchronization: switching to Telangana immediately displays Telangana districts.
- [x] **Interactive Farm Digital Twin Snapshot:**
  - Real-time synchronization displaying cultivated area, crop classification, days since planting, and water source.
- [x] **Clean, Professional UI Polish:**
  - Minimal, intentional icons; removed clutter and excess emojis.
  - Responsive cards suited for both laptop and mobile viewports.

- [x] **Regional Climate Intelligence Module (Stage 2) & Scientific Consistency Audit:**
  - Open-Meteo live API integration for real-time atmospheric telemetry (temperature, humidity, wind, rain rate).
  - 7-day agricultural forecast with dual-axis interactive Plotly charts and expandable daily data tables.
  - Recent 30-day precipitation history, cumulative rainfall curves, and dry-spell duration tracking.
  - **Scientific Consistency Enhancements:**
    - **Thermal Stress:** Fixed contradictions between forecast peak and temperature thresholds; reports peak forecast (e.g. 36.8°C), counts days ≥35°C and ≥38°C, and displays current observed temperature separately.
    - **Rainfall Availability:** Distinguishes cumulative rainfall from crop evapotranspiration (ETc); analyzes rainfall distribution (rainy days and concentration) and farm irrigation availability.
    - **Dry Spell:** Reports factual consecutive dry days (<1.0 mm) without unsupported claims regarding soil moisture stability; explicitly notes texture and irrigation influence.
    - **Reanalysis Attribution:** Explicitly identifies Open-Meteo high-resolution meteorological reanalysis (ECMWF ERA5 / ERA5-Land gridded data at ~11 km resolution) and distinguishes model estimates from in-situ ground rain-gauge measurements.
    - **Crop-Specific Sensitivity:** Provides separate physiological context for Turmeric, Banana, and Paddy without unsubstantiated yield claims or exact volumetric irrigation mandates.
    - **Risk Classification:** Every risk badge matches its explanatory text; returns "Insufficient Data" when input telemetry is missing or incomplete.
  - 15-minute caching with manual refresh, timeout protection, and zero fake-data substitution.
  - Full Open-Meteo CC BY 4.0 data attribution and disclaimers.

- [x] **Premium Commercial Frontend Redesign:**
  - **Clean 5-Section Architecture:**
    - **1. HOME:** Personalized farmer welcome greeting, plot overview badge (village, district, crop, acreage, crop age), real-time atmospheric snapshot card, 30-day rain and dry spell metrics, active crop alerts, personalized stage-based agronomic advice, and one-click quick action shortcuts.
    - **2. MY FARM:** Intuitive farm profile management (state, district, village, crop, exact decimal acreage, soil, irrigation, sowing date) paired with an active visual Digital Twin representation.
    - **3. WEATHER:** Real-time telemetry, 7-day agricultural forecast with interactive dual-axis Plotly charts and daily summary cards, 30-day reanalysis history with cumulative rain curves, and climate risk indicators.
    - **4. AI FARM ADVISOR:** Conversational assistant with suggested question chips in English and Telugu, clean message bubbles, and discreet data grounding dropdowns without internal agent terminology.
    - **5. CROP GUIDANCE:** Authoritative agronomic guide for Turmeric, Banana, and Paddy with physiological thresholds, growth stage timelines, climate resilience measures, and institutional citations (ICAR, ANGRAU, IMD, PJTSAU).
  - **Elimination of Technical Bloat:** Completely removed all college/academic prototype notices, roadmap text, internal NLP explanations, and agent names from the farmer-facing UI.
  - **Visual Design Identity:** Forest green (`#1b4332`), fresh sage (`#52b788`), warm off-white (`#fafbfa`), clean white cards with subtle shadows, and responsive layout optimized for laptop demonstration and mobile viewports.

---

## 🗺️ Project Navigation & Features

1. **🏡 HOME:** Overview of the farm, live weather snapshot, active alerts, and instant shortcuts.
2. **🌱 MY FARM:** Live plot configuration and synchronized Farm Digital Twin.
3. **🌦️ WEATHER:** Live Open-Meteo observations, 7-day forecast, 30-day reanalysis, and climate indicators.
4. **🤖 AI FARM ADVISOR:** Natural language advisory in Telugu and English grounded in farm and weather data.
5. **📖 CROP GUIDANCE:** Agronomic packages of practices and resilience measures for Turmeric, Banana, and Paddy.
6. **🔮 WHAT-IF SIMULATOR:** Climate stress-testing engine evaluating hypothetical rainfall deficits and thermal spikes.
7. **🌊 ENSO OUTLOOK:** Official oceanic monitoring via Relative Oceanic Niño Index (RONI) with diagnostic data from NOAA CPC and IMD.

---

## 🔒 Private Model Repository Configuration

The fine-tuned multilingual SetFit intent classifier is hosted on a private Hugging Face repository and pinned to an exact immutable commit revision:

- **Repository ID**: `BHARGAVAREDDY1/elnino-agri-setfit`
- **Pinned Revision**: `0a50cfd0b1e2e6fcf9e2cd3a3bafcaecbd5fd0f0`

### Cloud & Streamlit Deployment Secrets
For cloud environments (e.g. Streamlit Community Cloud), add the following in the dashboard secrets manager (or `.streamlit/secrets.toml` locally, see `.streamlit/secrets.toml.example`):

```toml
# Hugging Face Model Configuration
HF_MODEL_REPO_ID = "BHARGAVAREDDY1/elnino-agri-setfit"
HF_MODEL_REVISION = "0a50cfd0b1e2e6fcf9e2cd3a3bafcaecbd5fd0f0"
HF_TOKEN = "hf_your_read_access_token_placeholder"
```

### Docker / Container Environment Variables
```bash
export HF_MODEL_REPO_ID="BHARGAVAREDDY1/elnino-agri-setfit"
export HF_MODEL_REVISION="0a50cfd0b1e2e6fcf9e2cd3a3bafcaecbd5fd0f0"
export HF_TOKEN="hf_your_read_access_token_placeholder"
```

*Note: If `HF_TOKEN` is unavailable or network access fails, the application automatically engages the deterministic 3.0 ms rule-based agricultural intent classifier.*
