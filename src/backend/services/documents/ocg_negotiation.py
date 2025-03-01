"""
Service module for managing the Outside Counsel Guidelines (OCGs) negotiation process between law firms and clients in the Justice Bid Rate Negotiation System.
This service provides functionality for initiating negotiation, managing point budgets, tracking firm selections of alternative language options, validating selections against point budgets, and completing the negotiation process.
"""

import uuid
import datetime
import typing
import json
from typing import Union, Optional, Dict, List, Tuple, Any

from src.backend.db.models.ocg import OCG, OCGSection, OCGAlternative, OCGFirmSelection, OCGStatus
from src.backend.db.repositories.ocg_repository import OCGRepository
from src.backend.services.documents.ocg_generation import OCGGenerator, generate_ocg_document
from src.backend.services.messaging.notifications import NotificationService
from src.backend.services.messaging.thread import MessageService
from src.backend.utils.logging import get_logger
from src.backend.db.session import get_db
from src.backend.db.repositories.organization_repository import OrganizationRepository

logger = get_logger(__name__)


class OCGNegotiationError(Exception):
    """Base exception class for OCG negotiation errors"""

    def __init__(self, message: str):
        """Initialize a new OCGNegotiationError"""
        super().__init__(message)


class OCGNotFoundError(OCGNegotiationError):
    """Exception raised when an OCG is not found"""

    def __init__(self, ocg_id: uuid.UUID):
        """Initialize a new OCGNotFoundError"""
        message = f"OCG with ID '{ocg_id}' not found"
        super().__init__(message)


class OCGStatusError(OCGNegotiationError):
    """Exception raised when an operation is not allowed in the current OCG status"""

    def __init__(self, current_status: OCGStatus, required_status: OCGStatus, operation: str):
        """Initialize a new OCGStatusError"""
        message = f"Operation '{operation}' not allowed: OCG is in status '{current_status}', requires '{required_status}'"
        super().__init__(message)


class PointBudgetExceededError(OCGNegotiationError):
    """Exception raised when a firm's point budget would be exceeded by selections"""

    def __init__(self, budget: int, required: int):
        """Initialize a new PointBudgetExceededError"""
        message = f"Point budget exceeded: budget '{budget}', required '{required}'"
        super().__init__(message)


class OCGNegotiationService:
    """Service class for managing OCG negotiation processes, including publishing OCGs, initiating negotiations, managing firm selections and point budgets, and completing negotiations."""

    def __init__(
        self,
        ocg_repository: Optional[OCGRepository] = None,
        ocg_generator: Optional[OCGGenerator] = None,
        notification_service: Optional[NotificationService] = None,
        message_service: Optional[MessageService] = None,
        org_repository: Optional[OrganizationRepository] = None,
    ):
        """Initialize the OCGNegotiationService with required repositories and services"""
        self._ocg_repository = ocg_repository or OCGRepository(get_db())
        self._ocg_generator = ocg_generator or OCGGenerator(self._ocg_repository)
        self._notification_service = notification_service or NotificationService()
        self._message_service = message_service or MessageService()
        self._org_repository = org_repository or OrganizationRepository(get_db())
        logger.info("OCGNegotiationService initialized")

    def publish_ocg(self, ocg_id: uuid.UUID) -> OCG:
        """Publish an OCG, making it available for negotiation"""
        ocg = self._ocg_repository.get_by_id(ocg_id)
        if not ocg:
            raise OCGNotFoundError(ocg_id)
        if ocg.status != OCGStatus.DRAFT:
            raise OCGStatusError(ocg.status, OCGStatus.DRAFT, "publish")
        validate_ocg(str(ocg_id))
        ocg = self._ocg_repository.update_ocg_status(ocg_id, OCGStatus.PUBLISHED)
        self._ocg_generator.generate_document(str(ocg_id), "pdf")
        logger.info(f"OCG published: {ocg_id}")
        return ocg

    def initiate_negotiation(self, ocg_id: uuid.UUID, firm_id: uuid.UUID, point_budget: Optional[int] = None, message: Optional[str] = None) -> dict:
        """Initiate OCG negotiation with a law firm"""
        ocg = self._ocg_repository.get_by_id(ocg_id)
        if not ocg:
            raise OCGNotFoundError(ocg_id)
        if ocg.status != OCGStatus.PUBLISHED:
            raise OCGStatusError(ocg.status, OCGStatus.PUBLISHED, "initiate_negotiation")
        firm = self._org_repository.get_by_id(firm_id)
        if not firm:
            logger.error(f"Firm not found: {firm_id}")
            raise ValueError(f"Firm not found: {firm_id}")
        self._ocg_repository.update_ocg_status(ocg_id, OCGStatus.NEGOTIATING)
        if point_budget is not None:
            self._ocg_repository.set_firm_point_budget(ocg_id, firm_id, point_budget)
        thread = self._message_service.get_thread_by_context(context_type="ocg", context_id=str(ocg_id))
        if message:
            self._message_service.create_message(thread_id=thread.id, sender_id=ocg.client_id, recipient_ids=[firm_id], content=message)
        self._notification_service.send_ocg_negotiation_notification(recipient_email=firm.email, organization_name=ocg.client.name, ocg_id=str(ocg_id), status="Negotiation Started")
        return {"ocg": ocg, "point_budget": point_budget, "available_sections": ocg.sections}

    def select_alternative(self, ocg_id: uuid.UUID, firm_id: uuid.UUID, section_id: uuid.UUID, alternative_id: uuid.UUID) -> dict:
        """Record a firm's selection of an alternative for a negotiable section"""
        ocg = self._ocg_repository.get_by_id(ocg_id)
        if not ocg:
            raise OCGNotFoundError(ocg_id)
        if ocg.status != OCGStatus.NEGOTIATING:
            raise OCGStatusError(ocg.status, OCGStatus.NEGOTIATING, "select_alternative")
        section = self._ocg_repository.get_section(section_id)
        if not section or not section.is_negotiable:
            raise ValueError("Section not found or not negotiable")
        alternative = self._ocg_repository.get_alternative(alternative_id)
        if not alternative:
            raise ValueError("Alternative not found")
        current_points = self._ocg_repository.calculate_points_used(ocg_id, firm_id)
        budget = self._ocg_repository.get_firm_point_budget(ocg_id, firm_id)
        if current_points + alternative.points > budget:
            raise PointBudgetExceededError(budget, current_points + alternative.points)
        self._ocg_repository.create_firm_selection(ocg_id, firm_id, section_id, alternative_id)
        return {"selection": alternative, "points_used": current_points + alternative.points}

    def get_selections(self, ocg_id: uuid.UUID, firm_id: uuid.UUID) -> list:
        """Get a firm's current selections for an OCG"""
        ocg = self._ocg_repository.get_by_id(ocg_id)
        if not ocg:
            raise OCGNotFoundError(ocg_id)
        selections = self._ocg_repository.get_selections_by_firm(ocg_id, firm_id)
        return self._prepare_selections_response(selections)

    def get_points_summary(self, ocg_id: uuid.UUID, firm_id: uuid.UUID) -> dict:
        """Get summary of a firm's point budget and usage"""
        ocg = self._ocg_repository.get_by_id(ocg_id)
        if not ocg:
            raise OCGNotFoundError(ocg_id)
        budget = self._ocg_repository.get_firm_point_budget(ocg_id, firm_id)
        used = self._ocg_repository.calculate_points_used(ocg_id, firm_id)
        remaining = budget - used
        return {"budget": budget, "used": used, "remaining": remaining}

    def update_point_budget(self, ocg_id: uuid.UUID, firm_id: uuid.UUID, points: int) -> dict:
        """Update a firm's point budget for an OCG"""
        ocg = self._ocg_repository.get_by_id(ocg_id)
        if not ocg:
            raise OCGNotFoundError(ocg_id)
        if not isinstance(points, int) or points < 0:
            raise ValueError("Points must be a non-negative integer")
        self._ocg_repository.set_firm_point_budget(ocg_id, firm_id, points)
        used = self._ocg_repository.calculate_points_used(ocg_id, firm_id)
        if used > points:
            logger.warning("Points used exceeds new budget")
        remaining = points - used
        return {"budget": points, "used": used, "remaining": remaining}

    def generate_document(self, ocg_id: uuid.UUID, format_type: str, firm_id: Optional[uuid.UUID] = None, options: Optional[dict] = None) -> bytes:
        """Generate an OCG document with firm selections if applicable"""
        ocg = self._ocg_repository.get_by_id(ocg_id)
        if not ocg:
            raise OCGNotFoundError(ocg_id)
        if options is None:
            options = {}
        if firm_id:
            selections = self._ocg_repository.get_selections_by_firm(ocg_id, firm_id)
            options["selections"] = selections
        return generate_ocg_document(str(ocg_id), format_type, str(firm_id) if firm_id else None, options)

    def complete_negotiation(self, ocg_id: uuid.UUID, firm_id: uuid.UUID, message: Optional[str] = None) -> dict:
        """Complete the negotiation process for an OCG with a firm"""
        ocg = self._ocg_repository.get_by_id(ocg_id)
        if not ocg:
            raise OCGNotFoundError(ocg_id)
        if ocg.status != OCGStatus.NEGOTIATING:
            raise OCGStatusError(ocg.status, OCGStatus.NEGOTIATING, "complete_negotiation")
        valid, missing = self._validate_required_selections(ocg, firm_id)
        if not valid:
            raise ValueError(f"Missing required selections: {missing}")
        budget = self._ocg_repository.get_firm_point_budget(ocg_id, firm_id)
        used = self._ocg_repository.calculate_points_used(ocg_id, firm_id)
        if used > budget:
            raise PointBudgetExceededError(budget, used)
        self._ocg_repository.update_ocg_status(ocg_id, OCGStatus.SIGNED)
        document = self.generate_document(ocg_id, "pdf", firm_id)
        thread = self._message_service.get_thread_by_context(context_type="ocg", context_id=str(ocg_id))
        if message:
            self._message_service.create_message(thread_id=thread.id, sender_id=ocg.client_id, recipient_ids=[firm_id], content=message)
        self._notification_service.send_ocg_negotiation_notification(recipient_email=ocg.client.email, organization_name=ocg.client.name, ocg_id=str(ocg_id), status="Negotiation Completed")
        return {"completion": "success", "document_url": document}

    def get_summary(self, ocg_id: uuid.UUID, firm_id: uuid.UUID) -> dict:
        """Get summary of OCG negotiation with a firm"""
        ocg = self._ocg_repository.get_by_id(ocg_id)
        if not ocg:
            raise OCGNotFoundError(ocg_id)
        firm = self._org_repository.get_by_id(firm_id)
        if not firm:
            logger.error(f"Firm not found: {firm_id}")
            raise ValueError(f"Firm not found: {firm_id}")
        selections = self._ocg_repository.get_selections_by_firm(ocg_id, firm_id)
        points = self.get_points_summary(ocg_id, firm_id)
        thread = self._message_service.get_thread_by_context(context_type="ocg", context_id=str(ocg_id))
        return {"ocg": ocg, "firm": firm, "selections": selections, "points": points, "thread": thread}

    def get_available_sections(self, ocg_id: uuid.UUID, firm_id: Optional[uuid.UUID] = None) -> list:
        """Get negotiable sections available for a firm"""
        ocg = self._ocg_repository.get_by_id(ocg_id)
        if not ocg:
            raise OCGNotFoundError(ocg_id)
        sections = self._ocg_repository.get_negotiable_sections(ocg_id)
        if firm_id:
            selections = self._ocg_repository.get_selections_by_firm(ocg_id, firm_id)
        else:
            selections = []
        return sections

    def validate_selection_proposal(self, ocg_id: uuid.UUID, firm_id: uuid.UUID, proposed_selections: list) -> dict:
        """Validate a proposed set of selections against point budget"""
        ocg = self._ocg_repository.get_by_id(ocg_id)
        if not ocg:
            raise OCGNotFoundError(ocg_id)
        budget = self._ocg_repository.get_firm_point_budget(ocg_id, firm_id)
        total_points_required = 0
        valid_selections = []
        invalid_selections = []
        for selection in proposed_selections:
            section = self._ocg_repository.get_section(selection["section_id"])
            alternative = self._ocg_repository.get_alternative(selection["alternative_id"])
            if not section or not section.is_negotiable or not alternative:
                invalid_selections.append(selection)
            else:
                total_points_required += alternative.points
                valid_selections.append(selection)
        if total_points_required > budget:
            return {"valid": False, "valid_selections": valid_selections, "invalid_selections": invalid_selections, "points_required": total_points_required, "budget": budget}
        return {"valid": True, "valid_selections": valid_selections, "invalid_selections": invalid_selections, "points_required": total_points_required, "budget": budget}

    def reset_firm_selections(self, ocg_id: uuid.UUID, firm_id: uuid.UUID) -> bool:
        """Reset all selections made by a firm for an OCG"""
        ocg = self._ocg_repository.get_by_id(ocg_id)
        if not ocg:
            raise OCGNotFoundError(ocg_id)
        if ocg.status != OCGStatus.NEGOTIATING:
            raise OCGStatusError(ocg.status, OCGStatus.NEGOTIATING, "reset_firm_selections")
        self._ocg_repository.clear_firm_selections(ocg_id, firm_id)
        logger.info(f"Firm selections reset for OCG {ocg_id} and firm {firm_id}")
        return True

    def _validate_ocg_exists(self, ocg_id: uuid.UUID) -> OCG:
        """Helper method to validate OCG exists and return it"""
        ocg = self._ocg_repository.get_by_id(ocg_id)
        if not ocg:
            raise OCGNotFoundError(ocg_id)
        return ocg

    def _check_ocg_status(self, ocg: OCG, required_status: OCGStatus, operation: str) -> None:
        """Helper method to check if OCG has required status for an operation"""
        if ocg.status != required_status:
            raise OCGStatusError(ocg.status, required_status, operation)

    def _prepare_selections_response(self, selections: List[OCGFirmSelection]) -> List[dict]:
        """Helper method to prepare selection data for API responses"""
        result = []
        for selection in selections:
            section = self._ocg_repository.get_section(selection.section_id)
            alternative = self._ocg_repository.get_alternative(selection.alternative_id)
            selection_dict = {
                "section_id": selection.section_id,
                "alternative_id": selection.alternative_id,
                "section_title": section.title if section else None,
                "alternative_title": alternative.title if alternative else None,
                "points_used": selection.points_used,
            }
            result.append(selection_dict)
        return result

    def _validate_required_selections(self, ocg: OCG, firm_id: uuid.UUID) -> Tuple[bool, list]:
        """Helper method to validate all required sections have selections"""
        negotiable_sections = self._ocg_repository.get_negotiable_sections(ocg.id)
        selections = self._ocg_repository.get_selections_by_firm(ocg.id, firm_id)
        selection_map = {str(s.section_id): s for s in selections}
        missing_sections = []
        for section in negotiable_sections:
            if str(section.id) not in selection_map:
                missing_sections.append(section.title)
        return len(missing_sections) == 0, missing_sections