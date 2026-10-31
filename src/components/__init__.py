"""UI Components package for El Niño Resilience Co-Pilot."""
from src.components.home_view import render_home_view
from src.components.farm_view import render_farm_view, initialize_farm_state
from src.components.weather_view import render_weather_view
from src.components.advisor_view import render_advisor_view
from src.components.crop_guidance_view import render_crop_guidance_view

# Retain backward-compatible exports
from src.components.profile_form import render_farmer_profile_form, render_digital_twin_summary
from src.components.weather_dashboard import render_weather_dashboard
from src.components.advisor_chat import render_advisor_chat

__all__ = [
    "render_home_view",
    "render_farm_view",
    "render_weather_view",
    "render_advisor_view",
    "render_crop_guidance_view",
    "initialize_farm_state",
    "render_farmer_profile_form",
    "render_digital_twin_summary",
    "render_weather_dashboard",
    "render_advisor_chat",
]
