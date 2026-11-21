"""Location service providing verified geographic coordinates for AP and Telangana districts.

Maps administrative districts from the farmer profile to verified district-headquarters
coordinates for Open-Meteo climate intelligence queries.
"""

from typing import Dict, Any

# Verified District Headquarters Coordinates (WGS84 Latitude, Longitude)
# Default demo district: Kadapa (YSR Kadapa), Andhra Pradesh
DISTRICT_COORDINATES: Dict[str, Dict[str, Any]] = {
    # --- ANDHRA PRADESH (26 Districts) ---
    "Kadapa (YSR Kadapa)": {
        "lat": 14.4673,
        "lon": 78.8242,
        "state": "Andhra Pradesh",
        "hq": "Kadapa",
    },
    "Alluri Sitharama Raju": {
        "lat": 18.0833,
        "lon": 82.6667,
        "state": "Andhra Pradesh",
        "hq": "Paderu",
    },
    "Anakapalli": {
        "lat": 17.6913,
        "lon": 83.0039,
        "state": "Andhra Pradesh",
        "hq": "Anakapalli",
    },
    "Ananthapuramu": {
        "lat": 14.6819,
        "lon": 77.6006,
        "state": "Andhra Pradesh",
        "hq": "Anantapur",
    },
    "Annamayya": {
        "lat": 14.0569,
        "lon": 78.7523,
        "state": "Andhra Pradesh",
        "hq": "Rayachoty",
    },
    "Bapatla": {
        "lat": 15.9042,
        "lon": 80.4674,
        "state": "Andhra Pradesh",
        "hq": "Bapatla",
    },
    "Chittoor": {
        "lat": 13.2172,
        "lon": 79.1003,
        "state": "Andhra Pradesh",
        "hq": "Chittoor",
    },
    "Dr. B.R. Ambedkar Konaseema": {
        "lat": 16.5787,
        "lon": 82.0061,
        "state": "Andhra Pradesh",
        "hq": "Amalapuram",
    },
    "East Godavari": {
        "lat": 17.0005,
        "lon": 81.8040,
        "state": "Andhra Pradesh",
        "hq": "Rajahmundry",
    },
    "Eluru": {
        "lat": 16.7107,
        "lon": 81.0952,
        "state": "Andhra Pradesh",
        "hq": "Eluru",
    },
    "Guntur": {
        "lat": 16.3067,
        "lon": 80.4365,
        "state": "Andhra Pradesh",
        "hq": "Guntur",
    },
    "Kakinada": {
        "lat": 16.9891,
        "lon": 82.2475,
        "state": "Andhra Pradesh",
        "hq": "Kakinada",
    },
    "Krishna": {
        "lat": 16.1875,
        "lon": 81.1389,
        "state": "Andhra Pradesh",
        "hq": "Machilipatnam",
    },
    "Kurnool": {
        "lat": 15.8281,
        "lon": 78.0373,
        "state": "Andhra Pradesh",
        "hq": "Kurnool",
    },
    "Nandyal": {
        "lat": 15.4886,
        "lon": 78.4836,
        "state": "Andhra Pradesh",
        "hq": "Nandyal",
    },
    "NTR": {
        "lat": 16.5062,
        "lon": 80.6480,
        "state": "Andhra Pradesh",
        "hq": "Vijayawada",
    },
    "Palnadu": {
        "lat": 16.2360,
        "lon": 80.0540,
        "state": "Andhra Pradesh",
        "hq": "Narasaraopet",
    },
    "Parvathipuram Manyam": {
        "lat": 18.7797,
        "lon": 83.4283,
        "state": "Andhra Pradesh",
        "hq": "Parvathipuram",
    },
    "Prakasam": {
        "lat": 15.5057,
        "lon": 80.0499,
        "state": "Andhra Pradesh",
        "hq": "Ongole",
    },
    "Sri Potti Sriramulu Nellore": {
        "lat": 14.4426,
        "lon": 79.9865,
        "state": "Andhra Pradesh",
        "hq": "Nellore",
    },
    "Sri Sathya Sai": {
        "lat": 14.1652,
        "lon": 77.8105,
        "state": "Andhra Pradesh",
        "hq": "Puttaparthi",
    },
    "Srikakulam": {
        "lat": 18.2969,
        "lon": 83.8968,
        "state": "Andhra Pradesh",
        "hq": "Srikakulam",
    },
    "Tirupati": {
        "lat": 13.6288,
        "lon": 79.4192,
        "state": "Andhra Pradesh",
        "hq": "Tirupati",
    },
    "Visakhapatnam": {
        "lat": 17.6868,
        "lon": 83.2185,
        "state": "Andhra Pradesh",
        "hq": "Visakhapatnam",
    },
    "Vizianagaram": {
        "lat": 18.1124,
        "lon": 83.4150,
        "state": "Andhra Pradesh",
        "hq": "Vizianagaram",
    },
    "West Godavari": {
        "lat": 16.5449,
        "lon": 81.5212,
        "state": "Andhra Pradesh",
        "hq": "Bhimavaram",
    },

    # --- TELANGANA (33 Districts) ---
    "Adilabad": {
        "lat": 19.6641,
        "lon": 78.5320,
        "state": "Telangana",
        "hq": "Adilabad",
    },
    "Bhadradri Kothagudem": {
        "lat": 17.5552,
        "lon": 80.6195,
        "state": "Telangana",
        "hq": "Kothagudem",
    },
    "Hanamkonda": {
        "lat": 18.0138,
        "lon": 79.5519,
        "state": "Telangana",
        "hq": "Hanamkonda",
    },
    "Hyderabad": {
        "lat": 17.3850,
        "lon": 78.4867,
        "state": "Telangana",
        "hq": "Hyderabad",
    },
    "Jagtial": {
        "lat": 18.7946,
        "lon": 78.9125,
        "state": "Telangana",
        "hq": "Jagtial",
    },
    "Jangaon": {
        "lat": 17.7259,
        "lon": 79.1818,
        "state": "Telangana",
        "hq": "Jangaon",
    },
    "Jayashankar Bhupalpally": {
        "lat": 18.4314,
        "lon": 79.8647,
        "state": "Telangana",
        "hq": "Bhupalpally",
    },
    "Jogulamba Gadwal": {
        "lat": 16.2333,
        "lon": 77.8000,
        "state": "Telangana",
        "hq": "Gadwal",
    },
    "Kamareddy": {
        "lat": 18.3228,
        "lon": 78.3396,
        "state": "Telangana",
        "hq": "Kamareddy",
    },
    "Karimnagar": {
        "lat": 18.4386,
        "lon": 79.1288,
        "state": "Telangana",
        "hq": "Karimnagar",
    },
    "Khammam": {
        "lat": 17.2473,
        "lon": 80.1514,
        "state": "Telangana",
        "hq": "Khammam",
    },
    "Kumuram Bheem Asifabad": {
        "lat": 19.3588,
        "lon": 79.2882,
        "state": "Telangana",
        "hq": "Asifabad",
    },
    "Mahabubabad": {
        "lat": 17.5996,
        "lon": 80.0039,
        "state": "Telangana",
        "hq": "Mahabubabad",
    },
    "Mahabubnagar": {
        "lat": 16.7488,
        "lon": 77.9856,
        "state": "Telangana",
        "hq": "Mahabubnagar",
    },
    "Mancherial": {
        "lat": 18.8679,
        "lon": 79.4639,
        "state": "Telangana",
        "hq": "Mancherial",
    },
    "Medak": {
        "lat": 18.0461,
        "lon": 78.2631,
        "state": "Telangana",
        "hq": "Medak",
    },
    "Medchal-Malkajgiri": {
        "lat": 17.4968,
        "lon": 78.5583,
        "state": "Telangana",
        "hq": "Shamirpet",
    },
    "Mulugu": {
        "lat": 18.1917,
        "lon": 79.9431,
        "state": "Telangana",
        "hq": "Mulugu",
    },
    "Nagarkurnool": {
        "lat": 16.4857,
        "lon": 78.3188,
        "state": "Telangana",
        "hq": "Nagarkurnool",
    },
    "Nalgonda": {
        "lat": 17.0575,
        "lon": 79.2684,
        "state": "Telangana",
        "hq": "Nalgonda",
    },
    "Narayanpet": {
        "lat": 16.7381,
        "lon": 77.4988,
        "state": "Telangana",
        "hq": "Narayanpet",
    },
    "Nirmal": {
        "lat": 19.0964,
        "lon": 78.3436,
        "state": "Telangana",
        "hq": "Nirmal",
    },
    "Nizamabad": {
        "lat": 18.6725,
        "lon": 78.0941,
        "state": "Telangana",
        "hq": "Nizamabad",
    },
    "Peddapalli": {
        "lat": 18.6162,
        "lon": 79.3789,
        "state": "Telangana",
        "hq": "Peddapalli",
    },
    "Rajanna Sircilla": {
        "lat": 18.3844,
        "lon": 78.8106,
        "state": "Telangana",
        "hq": "Sircilla",
    },
    "Ranga Reddy": {
        "lat": 17.2403,
        "lon": 78.4294,
        "state": "Telangana",
        "hq": "Shamshabad",
    },
    "Sangareddy": {
        "lat": 17.6191,
        "lon": 78.0814,
        "state": "Telangana",
        "hq": "Sangareddy",
    },
    "Siddipet": {
        "lat": 18.1018,
        "lon": 78.8520,
        "state": "Telangana",
        "hq": "Siddipet",
    },
    "Suryapet": {
        "lat": 17.1415,
        "lon": 79.6236,
        "state": "Telangana",
        "hq": "Suryapet",
    },
    "Vikarabad": {
        "lat": 17.3364,
        "lon": 77.9048,
        "state": "Telangana",
        "hq": "Vikarabad",
    },
    "Wanaparthy": {
        "lat": 16.3622,
        "lon": 78.0631,
        "state": "Telangana",
        "hq": "Wanaparthy",
    },
    "Warangal": {
        "lat": 17.9689,
        "lon": 79.5941,
        "state": "Telangana",
        "hq": "Warangal",
    },
    "Yadadri Bhuvanagiri": {
        "lat": 17.5108,
        "lon": 78.8826,
        "state": "Telangana",
        "hq": "Bhuvanagiri",
    },
}

DEFAULT_COORDINATES = DISTRICT_COORDINATES["Kurnool"]


def get_district_coordinates(state: str, district: str, village: str = "") -> Dict[str, Any]:
    """Retrieve verified geographic coordinates for a district.
    
    Args:
        state: State name ('Andhra Pradesh' or 'Telangana').
        district: District name from the supported district lists.
        village: Optional village name entered by the farmer.
        
    Returns:
        Dictionary containing verified latitude, longitude, representation type,
        and localized descriptive context.
    """
    coord_info = DISTRICT_COORDINATES.get(district)
    
    if not coord_info:
        # Fallback safely to Kurnool default
        coord_info = DEFAULT_COORDINATES
        is_fallback = True
        district_name = "Kurnool"
        state_name = "Andhra Pradesh"
    else:
        is_fallback = False
        district_name = district
        state_name = coord_info["state"]

    has_village = bool(village and village.strip())
    
    return {
        "district": district_name,
        "state": state_name,
        "latitude": coord_info["lat"],
        "longitude": coord_info["lon"],
        "headquarters": coord_info.get("hq", district_name),
        "has_village": has_village,
        "village": village.strip() if has_village else "",
        "is_fallback": is_fallback,
        "is_district_representative": True,  # True since model uses district HQ centroid
    }
