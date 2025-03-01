import typing
from typing import List, Dict, Any, Optional, Tuple
import uuid
from datetime import date

from src.backend.db.models.rate import Rate
from src.backend.db.models.negotiation import Negotiation
from src.backend.db.repositories.rate_repository import RateRepository
from src.backend.db.repositories.negotiation_repository import NegotiationRepository
from src.backend.services.negotiations.validation import validate_counter_proposal_values
from src.backend.services.ai.recommendations import RateRecommendationService
from src.backend.utils.constants import RATE_TYPES, RATE_STATUSES, NEGOTIATION_STATUSES
from src.backend.utils.logging import logger
from src.backend.api.core.errors import CounterProposalException


class CounterProposalService:
    """
    Service class that manages the creation and processing of counter-proposals during rate negotiations
    """

    def __init__(self, rate_repository: RateRepository, negotiation_repository: NegotiationRepository, ai_service: RateRecommendationService):
        """
        Initializes a new CounterProposalService with required repositories

        Args:
            rate_repository: Repository for rate data operations
            negotiation_repository: Repository for negotiation data operations
            ai_service: AI service for rate recommendations
        """
        self._rate_repository = rate_repository
        self._negotiation_repository = negotiation_repository
        self._ai_service = ai_service
        print("CounterProposalService initialized")

    def create_counter_proposal(self, rate_id: str, counter_amount: float, user_id: str, message: str, is_client: bool) -> Rate:
        """
        Creates a counter-proposal for a rate

        Args:
            rate_id: ID of the rate
            counter_amount: Counter-proposed amount
            user_id: ID of the user creating the counter-proposal
            message: Message associated with the counter-proposal
            is_client: True if the counter-proposal is from the client, False if from the law firm

        Returns:
            Updated rate with counter-proposal
        """
        print(f"Creating counter-proposal for rate {rate_id} with amount {counter_amount}")
        # Log the counter-proposal creation attempt
        logger.info(f"Attempting to create counter-proposal for rate {rate_id} by user {user_id}")

        # Retrieve the rate using _rate_repository.get_by_id
        rate = self._rate_repository.get_by_id(rate_id)

        # Validate that the rate exists
        if not rate:
            logger.warning(f"Rate with ID {rate_id} not found")
            raise CounterProposalException(f"Rate with ID {rate_id} not found", details={"rate_id": rate_id})

        # Validate the counter_amount using validate_counter_proposal_rate
        validation_result = validate_counter_proposal_values(rate, counter_amount)
        if not validation_result["success"]:
            logger.warning(f"Counter-proposal validation failed: {validation_result['errors']}")
            raise CounterProposalException(
                f"Invalid counter-proposal for rate {rate_id}: {validation_result['errors']}",
                details={"rate_id": rate_id, "errors": validation_result["errors"]},
            )

        # Call _rate_repository.add_counter_proposal with validated data
        updated_rate = self._rate_repository.add_counter_proposal(rate_id, counter_amount, user_id, message)

        # Update the rate type to 'CLIENT_COUNTER_PROPOSED' or 'FIRM_COUNTER_PROPOSED' based on is_client
        if is_client:
            rate.type = RATE_TYPES["CLIENT_COUNTER_PROPOSED"]
        else:
            rate.type = RATE_TYPES["FIRM_COUNTER_PROPOSED"]

        # Update the rate status to 'UnderReview' if needed
        if rate.status != RATE_STATUSES["UNDER_REVIEW"]:
            rate.status = RATE_STATUSES["UNDER_REVIEW"]

        # Return the updated rate
        logger.info(f"Counter-proposal created successfully for rate {rate_id}")
        return updated_rate

    def process_batch_counter_proposal(self, negotiation_id: str, counter_rates: Dict[str, float], user_id: str, message: str, is_client: bool) -> Dict[str, Any]:
        """
        Processes multiple counter-proposals for a negotiation

        Args:
            negotiation_id: ID of the negotiation
            counter_rates: Dictionary mapping rate IDs to counter-proposed amounts
            user_id: ID of the user creating the counter-proposals
            message: Message associated with the counter-proposals
            is_client: True if the counter-proposals are from the client, False if from the law firm

        Returns:
            Result with success count, error count, and detailed errors
        """
        # Log the batch counter-proposal processing
        logger.info(f"Processing batch counter-proposals for negotiation {negotiation_id} by user {user_id}")

        # Retrieve the negotiation using _negotiation_repository.get_by_id
        negotiation = self._negotiation_repository.get_by_id(negotiation_id)

        # Validate that the negotiation exists and is in a valid state for counter-proposals
        if not negotiation:
            logger.warning(f"Negotiation with ID {negotiation_id} not found")
            return {"success_count": 0, "error_count": len(counter_rates), "errors": [f"Negotiation with ID {negotiation_id} not found"]}

        # Initialize counters for success, errors, and detailed error messages
        success_count = 0
        error_count = 0
        errors = []

        # For each rate_id and counter_amount in counter_rates:
        for rate_id, counter_amount in counter_rates.items():
            try:
                # Try to create a counter-proposal using create_counter_proposal
                self.create_counter_proposal(rate_id, counter_amount, user_id, message, is_client)
                # On success, increment success counter
                success_count += 1
            except CounterProposalException as e:
                # On failure, increment error counter and store error message
                error_count += 1
                errors.append(str(e))

        # If message is provided, add it to the negotiation thread
        if message:
            negotiation.add_message(user_id, [negotiation.client_id, negotiation.firm_id], message)

        # Update negotiation status if needed based on counter-proposal results
        if success_count > 0 and negotiation.status != NEGOTIATION_STATUSES["IN_PROGRESS"]:
            negotiation.status = NEGOTIATION_STATUSES["IN_PROGRESS"]

        # Return result dictionary with counts and any errors
        result = {"success_count": success_count, "error_count": error_count, "errors": errors}
        logger.info(f"Batch counter-proposal processing completed for negotiation {negotiation_id}: {result}")
        return result

    def get_ai_counter_proposal_recommendations(self, negotiation_id: str, rate_ids: List[str], is_client: bool) -> Dict[str, float]:
        """
        Gets AI-recommended counter-proposal values for multiple rates

        Args:
            negotiation_id: ID of the negotiation
            rate_ids: List of rate IDs
            is_client: True if the recommendations are for the client, False if for the law firm

        Returns:
            Dictionary mapping rate IDs to recommended counter-proposal amounts
        """
        # Log the AI recommendation request
        logger.info(f"Getting AI counter-proposal recommendations for negotiation {negotiation_id} and rates {rate_ids}")

        # Retrieve the negotiation using _negotiation_repository.get_by_id
        negotiation = self._negotiation_repository.get_by_id(negotiation_id)

        # Validate that the negotiation exists
        if not negotiation:
            logger.warning(f"Negotiation with ID {negotiation_id} not found")
            return {}

        # Initialize empty dictionary for recommendations
        recommendations = {}

        # For each rate_id in rate_ids:
        for rate_id in rate_ids:
            # Retrieve the rate using _rate_repository.get_by_id
            rate = self._rate_repository.get_by_id(rate_id)

            # If rate exists and is in a valid state for counter-proposals:
            if rate and rate.status in [RATE_STATUSES["UNDER_REVIEW"], RATE_STATUSES["CLIENT_COUNTER_PROPOSED"], RATE_STATUSES["FIRM_COUNTER_PROPOSED"]]:
                try:
                    # Get suggested counter-proposal using suggest_counter_proposal_rate
                    suggestion = self.suggest_counter_proposal_rate(rate, is_client, self._ai_service)
                    # Add rate_id and suggestion to recommendations dictionary
                    recommendations[rate_id] = suggestion
                except Exception as e:
                    logger.error(f"Error getting AI recommendation for rate {rate_id}: {str(e)}")

        # Return the recommendations dictionary
        logger.info(f"Generated AI counter-proposal recommendations: {recommendations}")
        return recommendations

    def suggest_counter_proposal_rate(self, rate: Rate, is_client: bool, ai_service: RateRecommendationService) -> float:
        """
        Suggests a counter-proposal rate using the AI service.

        Args:
            rate (Rate): The rate object.
            is_client (bool): Whether the counter-proposal is for the client.
            ai_service (RateRecommendationService): The AI recommendation service.

        Returns:
            float: The suggested counter-proposal rate amount.
        """
        # Log the recommendation request
        logger.info(f"Suggesting counter-proposal rate for rate {rate.id}")

        # Get the valid bounds for the counter-proposal using get_counter_proposal_bounds
        min_amount, max_amount = self.get_counter_proposal_bounds(rate, is_client)

        # Prepare context data including historical rates, peer data, and rate rules
        context_data = {
            "historical_rates": [],  # Placeholder for historical rates
            "peer_data": {},  # Placeholder for peer data
            "rate_rules": {}  # Placeholder for rate rules
        }

        # Call the AI service's suggest_counter_rate method with rate data and context
        suggested_rate = ai_service.suggest_counter_rate(rate, context_data)

        # Ensure the suggested rate is within the valid bounds
        suggested_rate = max(min_amount, min(suggested_rate, max_amount))

        # Return the suggested counter-proposal amount
        logger.info(f"Suggested counter-proposal rate: {suggested_rate}")
        return suggested_rate

    def get_counter_proposal_bounds(self, rate: Rate, is_client: bool) -> Tuple[float, float]:
        """
        Calculates the valid bounds (min/max) for a counter-proposal based on negotiation context.

        Args:
            rate (Rate): The rate object.
            is_client (bool): Whether the counter-proposal is for the client.

        Returns:
            Tuple[float, float]: Minimum and maximum allowed counter-proposal values.
        """
        # Determine the current rate amount
        current_amount = rate.amount

        # Determine the proposed or counter-proposed amount
        if is_client:
            proposed_amount = rate.amount  # Placeholder: Replace with actual proposed amount
        else:
            proposed_amount = rate.amount  # Placeholder: Replace with actual counter-proposed amount

        # For client counter-proposals: min = current rate, max = proposed rate
        if is_client:
            min_amount = current_amount
            max_amount = proposed_amount
        # For firm counter-proposals: min = client counter-proposal, max = firm's initial proposal
        else:
            min_amount = current_amount  # Placeholder: Replace with actual client counter-proposal
            max_amount = proposed_amount

        # Apply any additional business rules or constraints from client configuration
        # Placeholder: Implement logic to fetch and apply client-specific rules

        # Return tuple of (min_amount, max_amount)
        return min_amount, max_amount

    def accept_counter_proposal(self, rate_id: str, user_id: str, message: str, is_client: bool) -> Rate:
        """
        Accepts a counter-proposal, updating the rate to the counter-proposed amount

        Args:
            rate_id: ID of the rate
            user_id: ID of the user accepting the counter-proposal
            message: Message associated with the acceptance
            is_client: True if the acceptance is from the client, False if from the law firm

        Returns:
            Updated rate with accepted counter-proposal
        """
        # Log the counter-proposal acceptance
        logger.info(f"Accepting counter-proposal for rate {rate_id} by user {user_id}")

        # Retrieve the rate using _rate_repository.get_by_id
        rate = self._rate_repository.get_by_id(rate_id)

        # Validate that the rate exists and has a counter-proposal
        if not rate:
            logger.warning(f"Rate with ID {rate_id} not found")
            raise CounterProposalException(f"Rate with ID {rate_id} not found", details={"rate_id": rate_id})

        if rate.status not in [RATE_STATUSES["CLIENT_COUNTER_PROPOSED"], RATE_STATUSES["FIRM_COUNTER_PROPOSED"]]:
            logger.warning(f"Rate with ID {rate_id} does not have a pending counter-proposal")
            raise CounterProposalException(f"Rate with ID {rate_id} does not have a pending counter-proposal", details={"rate_id": rate_id})

        # Determine the new rate status based on is_client (FIRM_ACCEPTED or CLIENT_APPROVED)
        if is_client:
            new_status = RATE_STATUSES["CLIENT_APPROVED"]
        else:
            new_status = RATE_STATUSES["FIRM_ACCEPTED"]

        # Extract the counter-proposal amount from rate history
        counter_amount = None
        for entry in reversed(rate.history):
            if "counter_amount" in entry:
                counter_amount = entry["counter_amount"]
                break

        if not counter_amount:
            logger.warning(f"No counter-proposal amount found in history for rate {rate_id}")
            raise CounterProposalException(f"No counter-proposal amount found in history for rate {rate_id}", details={"rate_id": rate_id})

        # Update the rate amount to the counter-proposal amount
        rate.amount = counter_amount

        # Update the rate status and add history entry
        rate.status = new_status
        rate.add_history_entry(rate.amount, rate.status, rate.type, user_id, message)

        # If the AI service was used for this counter-proposal, record acceptance feedback
        # Placeholder: Implement AI service feedback recording

        # Return the updated rate
        logger.info(f"Counter-proposal accepted successfully for rate {rate_id}")
        return rate

    def reject_counter_proposal(self, rate_id: str, user_id: str, message: str) -> Rate:
        """
        Rejects a counter-proposal, maintaining the original rate amount

        Args:
            rate_id: ID of the rate
            user_id: ID of the user rejecting the counter-proposal
            message: Message associated with the rejection

        Returns:
            Updated rate with rejected counter-proposal status
        """
        # Log the counter-proposal rejection
        logger.info(f"Rejecting counter-proposal for rate {rate_id} by user {user_id}")

        # Retrieve the rate using _rate_repository.get_by_id
        rate = self._rate_repository.get_by_id(rate_id)

        # Validate that the rate exists and has a counter-proposal
        if not rate:
            logger.warning(f"Rate with ID {rate_id} not found")
            raise CounterProposalException(f"Rate with ID {rate_id} not found", details={"rate_id": rate_id})

        if rate.status not in [RATE_STATUSES["CLIENT_COUNTER_PROPOSED"], RATE_STATUSES["FIRM_COUNTER_PROPOSED"]]:
            logger.warning(f"Rate with ID {rate_id} does not have a pending counter-proposal")
            raise CounterProposalException(f"Rate with ID {rate_id} does not have a pending counter-proposal", details={"rate_id": rate_id})

        # Update the rate status to REJECTED
        rate.status = RATE_STATUSES["REJECTED"]

        # Add history entry for the rejection with user_id and message
        rate.add_history_entry(rate.amount, rate.status, rate.type, user_id, message)

        # If the AI service was used for this counter-proposal, record rejection feedback
        # Placeholder: Implement AI service feedback recording

        # Return the updated rate
        logger.info(f"Counter-proposal rejected successfully for rate {rate_id}")
        return rate

# Initialize global logger
logger = logger.getLogger(__name__)