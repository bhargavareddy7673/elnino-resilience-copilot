"""Configuration and static data for El Niño Resilience Co-Pilot.

Contains district lists for Andhra Pradesh and Telangana, supported crops,
soil types, irrigation methods, and default demo values.
"""

# Default demo location requested: Kadapa district, Andhra Pradesh
DEFAULT_STATE = "Andhra Pradesh"
DEFAULT_DISTRICT = "Kadapa (YSR Kadapa)"
DEFAULT_VILLAGE = ""  # Editable default without assuming any specific village
DEFAULT_CROP = "Turmeric"
DEFAULT_LAND_ACRES = 3.00
DEFAULT_SOIL = "Red Sandy Loam"
DEFAULT_IRRIGATION = "Borewell / Groundwater"

# Supported States
SUPPORTED_STATES = ["Andhra Pradesh", "Telangana"]

# Districts for Andhra Pradesh (including reorganized districts)
AP_DISTRICTS = [
    "Kadapa (YSR Kadapa)",
    "Alluri Sitharama Raju",
    "Anakapalli",
    "Ananthapuramu",
    "Annamayya",
    "Bapatla",
    "Chittoor",
    "Dr. B.R. Ambedkar Konaseema",
    "East Godavari",
    "Eluru",
    "Guntur",
    "Kakinada",
    "Krishna",
    "Kurnool",
    "Nandyal",
    "NTR",
    "Palnadu",
    "Parvathipuram Manyam",
    "Prakasam",
    "Sri Potti Sriramulu Nellore",
    "Sri Sathya Sai",
    "Srikakulam",
    "Tirupati",
    "Visakhapatnam",
    "Vizianagaram",
    "West Godavari",
]

# Districts for Telangana
TELANGANA_DISTRICTS = [
    "Adilabad",
    "Bhadradri Kothagudem",
    "Hanamkonda",
    "Hyderabad",
    "Jagtial",
    "Jangaon",
    "Jayashankar Bhupalpally",
    "Jogulamba Gadwal",
    "Kamareddy",
    "Karimnagar",
    "Khammam",
    "Kumuram Bheem Asifabad",
    "Mahabubabad",
    "Mahabubnagar",
    "Mancherial",
    "Medak",
    "Medchal-Malkajgiri",
    "Mulugu",
    "Nagarkurnool",
    "Nalgonda",
    "Narayanpet",
    "Nirmal",
    "Nizamabad",
    "Peddapalli",
    "Rajanna Sircilla",
    "Ranga Reddy",
    "Sangareddy",
    "Siddipet",
    "Suryapet",
    "Vikarabad",
    "Wanaparthy",
    "Warangal",
    "Yadadri Bhuvanagiri",
]

# State-to-District mapping
STATE_DISTRICT_MAP = {
    "Andhra Pradesh": sorted(AP_DISTRICTS),
    "Telangana": sorted(TELANGANA_DISTRICTS),
}

# The three project-supported crops with bilingual names and agronomic metadata
SUPPORTED_CROPS = {
    "Turmeric": {
        "en": "Turmeric",
        "te": "పసుపు (Turmeric)",
        "category_en": "Commercial / Spices",
        "category_te": "వాణిజ్య పంట / సుగంధ ద్రవ్యం",
        "duration_en": "8 - 9 months",
        "duration_te": "8 - 9 నెలలు",
        "typical_sowing_en": "May - July",
        "typical_sowing_te": "మే - జూలై",
    },
    "Banana": {
        "en": "Banana",
        "te": "అరటి (Banana)",
        "category_en": "Horticultural / Fruit",
        "category_te": "ఉద్యానవన పంట",
        "duration_en": "10 - 12 months",
        "duration_te": "10 - 12 నెలలు",
        "typical_sowing_en": "Feb - May / Aug - Oct",
        "typical_sowing_te": "ఫిబ్రవరి - మే / ఆగస్టు - అక్టోబర్",
    },
    "Paddy": {
        "en": "Paddy",
        "te": "వరి (Paddy)",
        "category_en": "Cereal / Food Grain",
        "category_te": "ఆహార ధాన్య పంట",
        "duration_en": "4 - 5 months",
        "duration_te": "4 - 5 నెలలు",
        "typical_sowing_en": "Kharif (Jun - Jul) / Rabi (Nov - Dec)",
        "typical_sowing_te": "ఖరీఫ్ (జూన్ - జూలై) / రబీ (నవంబర్ - డిసెంబర్)",
    },
}

# Common Soil Types in AP & Telangana
SOIL_TYPES = [
    {"en": "Red Sandy Loam", "te": "ఎర్ర ఇసుక నేల"},
    {"en": "Black Cotton Soil", "te": "నల్లరేగడి నేల"},
    {"en": "Clay Loam", "te": "బంక మట్టి నేల"},
    {"en": "Alluvial Soil", "te": "ఒండ్రు నేల"},
    {"en": "Sandy Loam", "te": "ఇసుక నేల"},
]

# Common Irrigation Sources in AP & Telangana
IRRIGATION_SOURCES = [
    {"en": "Borewell / Groundwater", "te": "బోరుబావి / భూగర్భ జలం"},
    {"en": "Canal / River Water", "te": "కాలువ / నది నీరు"},
    {"en": "Drip Irrigation", "te": "బిందు సేద్యం (డ్రిప్)"},
    {"en": "Sprinkler Irrigation", "te": "తుంపర సేద్యం (స్ప్రింక్లర్)"},
    {"en": "Rainfed (No Irrigation)", "te": "వర్షాధార సేద్యం"},
    {"en": "Open Well / Farm Pond", "te": "బావి / వ్యవసాయ కుంట"},
]
