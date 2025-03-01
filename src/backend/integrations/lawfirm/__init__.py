"""
Initialization file for the law firm integration module. Exposes key classes and functions for integrating with law firm billing systems to import attorney profiles and export approved rates.
"""

from .client import LawFirmClient  # Assuming version 1.0
from .client import GenericLawFirmClient  # Assuming version 1.0
from .client import get_law_firm_client  # Assuming version 1.0
from .mapper import LawFirmAttorneyMapper  # Assuming version 1.0
from .mapper import LawFirmRateMapper  # Assuming version 1.0
from .mapper import normalize_date  # Assuming version 1.0
from .mapper import normalize_currency  # Assuming version 1.0

__all__ = [
    'LawFirmClient',
    'GenericLawFirmClient',
    'get_law_firm_client',
    'LawFirmAttorneyMapper',
    'LawFirmRateMapper',
    'normalize_date',
    'normalize_currency'
]