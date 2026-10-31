"""Agricultural Multi-Agent package."""
from src.agents.controller import process_farmer_query
from src.agents.weather_agent import (
    answer_current_weather,
    answer_weather_forecast,
    answer_rainfall_status,
    answer_dry_spell_status,
)
from src.agents.risk_analysis_agent import (
    answer_temperature_risk,
    answer_water_stress,
)
from src.agents.crop_advisory_agent import answer_crop_advisory

__all__ = [
    "process_farmer_query",
    "answer_current_weather",
    "answer_weather_forecast",
    "answer_rainfall_status",
    "answer_dry_spell_status",
    "answer_temperature_risk",
    "answer_water_stress",
    "answer_crop_advisory",
]
