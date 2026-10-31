"""What-If Farm Simulator Package for El Niño Resilience Co-Pilot."""

from src.simulation.simulator_engine import (
    calculate_scenario,
    generate_comparison_scenarios,
    get_baseline_climate,
)

__all__ = [
    "calculate_scenario",
    "generate_comparison_scenarios",
    "get_baseline_climate",
]
