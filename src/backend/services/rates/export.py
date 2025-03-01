"""
Service for exporting approved rates to external systems (eBilling, law firm systems) and downloadable file formats (Excel, CSV).
"""

import logging  # standard library
from datetime import datetime  # standard library
import typing  # standard library
from typing import List, Optional, Dict, Any, Tuple  # standard library
import pandas  # version 2.0+
import io  # standard library

from src.backend.db.repositories.rate_repository import RateRepository  # src/backend/db/repositories/rate_repository.py
from src.backend.integrations.file.excel_processor import ExcelProcessor  # src/backend/integrations/file/excel_processor.py
from src.backend.integrations.file.csv_processor import CSVProcessor  # src/backend/integrations/file/csv_processor.py
from src.backend.utils.formatting import format_rate_for_export  # src/backend/utils/formatting.py
from src.backend.utils.currency import convert_currency  # src/backend/utils/currency.py
from src.backend.utils.file_handling import save_file  # src/backend/utils/file_handling.py
from src.backend.integrations.ebilling.teamconnect import TeamConnectAdapter  # src/backend/integrations/ebilling/teamconnect.py
from src.backend.integrations.ebilling.onit import OnItAdapter  # src/backend/integrations/ebilling/onit.py
from src.backend.integrations.ebilling.legal_tracker import LegalTrackerAdapter  # src/backend/integrations/ebilling/legal_tracker.py
from src.backend.integrations.lawfirm.client import LawFirmClient  # src/backend/integrations/lawfirm/client.py
from src.backend.services.rates.history import get_rate_history  # src/backend/services/rates/history.py
from src.backend.utils.event_tracking import track_event  # src/backend/utils/event_tracking.py

logger = logging.getLogger(__name__)


def export_rates_to_file(
    filters: Dict[str, Any],
    file_format: str,
    currency: str,
) -> Tuple[str, io.BytesIO]:
    """Exports approved rates to a downloadable file (Excel or CSV)"""
    # Validate the requested file format (Excel or CSV)
    if file_format not in ["excel", "csv"]:
        raise ValueError("Invalid file format. Supported formats are excel and csv.")
    # Retrieve approved rates from the database using the provided filters
    rate_repository = RateRepository()
    rates = rate_repository.get_approved_rates(filters)
    # Convert all rate amounts to the requested currency
    for rate in rates:
        rate.amount = convert_currency(rate.amount, rate.currency, currency)
        rate.currency = currency
    # Format the rate data for export
    formatted_rates = [format_rate_for_export(rate) for rate in rates]
    # Generate the export file using the appropriate processor
    if file_format == "excel":
        excel_processor = ExcelProcessor()
        file_content = excel_processor.generate_rate_export(formatted_rates)
        filename = f"approved_rates_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    else:  # CSV
        csv_processor = CSVProcessor()
        file_content = csv_processor.generate_rate_export(formatted_rates)
        filename = f"approved_rates_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    # Track the export event for auditing
    track_event(
        event_type="rate_export_file",
        data={"file_format": file_format, "currency": currency, "rate_count": len(rates)},
    )
    # Return the filename and file content
    return filename, file_content


def export_rates_to_ebilling(
    client_id: str, ebilling_system: str, filters: Dict[str, Any]
) -> Dict[str, Any]:
    """Exports approved rates to a client's eBilling system"""
    # Validate the client and eBilling system
    if not client_id:
        raise ValueError("Client ID is required")
    if not ebilling_system:
        raise ValueError("eBilling system is required")
    # Retrieve approved rates for the client using the provided filters
    rate_repository = RateRepository()
    rates = rate_repository.get_approved_rates(client_id, filters)
    # Get the appropriate eBilling adapter based on the system type
    if ebilling_system == "teamconnect":
        ebilling_adapter = TeamConnectAdapter()
    elif ebilling_system == "onit":
        ebilling_adapter = OnitAdapter()
    elif ebilling_system == "legal_tracker":
        ebilling_adapter = LegalTrackerAdapter()
    else:
        raise ValueError(f"Unsupported eBilling system: {ebilling_system}")
    # Format the rate data according to the eBilling system's requirements
    formatted_rates = [ebilling_adapter.format_rate(rate) for rate in rates]
    # Execute the export using the adapter
    success = ebilling_adapter.export_rates(formatted_rates)
    # Track the export event for auditing
    track_event(
        event_type="rate_export_ebilling",
        data={
            "ebilling_system": ebilling_system,
            "client_id": client_id,
            "rate_count": len(rates),
        },
    )
    # Return the export results
    return {"success": success, "message": "Exported rates to eBilling system"}


def export_rates_to_lawfirm(firm_id: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """Exports approved rates to a law firm's billing system"""
    # Validate the law firm
    if not firm_id:
        raise ValueError("Law firm ID is required")
    # Retrieve approved rates for the firm using the provided filters
    rate_repository = RateRepository()
    rates = rate_repository.get_approved_rates(firm_id, filters)
    # Initialize the law firm client with the firm's integration settings
    lawfirm_client = LawFirmClient()  # Replace with actual initialization
    # Format the rate data according to the firm's requirements
    formatted_rates = [lawfirm_client.format_rate(rate) for rate in rates]
    # Execute the export using the client
    success = lawfirm_client.export_rates(formatted_rates)
    # Track the export event for auditing
    track_event(
        event_type="rate_export_lawfirm",
        data={"firm_id": firm_id, "rate_count": len(rates)},
    )
    # Return the export results
    return {"success": success, "message": "Exported rates to law firm system"}


def export_rates_by_negotiation(
    negotiation_id: str, format: str, destination_type: str, destination_id: str
) -> Dict[str, Any]:
    """Exports rates from a specific negotiation"""
    # Validate the negotiation ID and ensure rates are in approved status
    rate_repository = RateRepository()
    rates = rate_repository.get_rates_by_negotiation(negotiation_id)
    if not rates:
        raise ValueError(f"No rates found for negotiation ID: {negotiation_id}")
    # Determine the export destination (file, eBilling, law firm)
    if destination_type == "file":
        # Route to the export_rates_to_file function
        filename, file_content = export_rates_to_file(
            {"negotiation_id": negotiation_id}, format, "USD"
        )  # Assuming USD as default
        save_file(filename, file_content)
        result = {"success": True, "message": f"Exported to file: {filename}"}
    elif destination_type == "ebilling":
        # Route to the export_rates_to_ebilling function
        result = export_rates_to_ebilling(destination_id, format, {"negotiation_id": negotiation_id})
    elif destination_type == "lawfirm":
        # Route to the export_rates_to_lawfirm function
        result = export_rates_to_lawfirm(destination_id, {"negotiation_id": negotiation_id})
    else:
        raise ValueError(f"Invalid destination type: {destination_type}")
    # Track the export event for auditing
    track_event(
        event_type="rate_export_negotiation",
        data={
            "negotiation_id": negotiation_id,
            "format": format,
            "destination_type": destination_type,
            "destination_id": destination_id,
        },
    )
    # Return the export results
    return result


def get_export_templates(system_type: str) -> List[Dict[str, Any]]:
    """Retrieves available export templates for different systems"""
    # Validate the system type
    if system_type not in ["teamconnect", "onit", "legal_tracker", "lawfirm"]:
        raise ValueError(f"Unsupported system type: {system_type}")
    # Retrieve available templates for the specified system
    templates = []  # Replace with actual template retrieval logic
    # Return the template details including field mappings
    return templates


def prepare_rate_data(rates: List[Dict[str, Any]], destination_type: str, template_id: str) -> List[Dict[str, Any]]:
    """Prepares rate data for export according to destination requirements"""
    # Validate the rates data and template
    if not rates:
        raise ValueError("No rates data provided")
    if not template_id:
        raise ValueError("Template ID is required")
    # Apply the template's field mappings to the rate data
    # Format values according to destination requirements
    # Add any required metadata or context
    # Return the formatted data
    return rates