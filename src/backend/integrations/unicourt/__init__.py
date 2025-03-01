"""
Package initialization file for the UniCourt integration module, exposing key classes and functions
for attorney performance data integration through the UniCourt API.
"""

from src.backend.integrations.unicourt.client import UniCourtClient  # Version: N/A - Client for interacting with the UniCourt API
from src.backend.integrations.unicourt.mapper import UniCourtMapper  # Version: N/A - Data mapper for transforming UniCourt data
from src.backend.integrations.unicourt.mapper import map_attorney_to_unicourt  # Version: N/A - Function to map Justice Bid attorneys to UniCourt attorneys
from src.backend.integrations.unicourt.mapper import transform_unicourt_attorney  # Version: N/A - Transform UniCourt attorney data to internal format
from src.backend.integrations.unicourt.mapper import transform_performance_data  # Version: N/A - Transform UniCourt performance data to internal format

__version__ = "1.0.0"
__all__ = ["UniCourtClient", "UniCourtMapper", "map_attorney_to_unicourt", "transform_unicourt_attorney", "transform_performance_data"]