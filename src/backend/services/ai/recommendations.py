"""
AI service module that provides rate recommendations and counter-proposal suggestions for rate negotiations.

This module integrates with LangChain and OpenAI to generate AI-driven recommendations
for proposed rates, considering historical data, peer comparisons, and attorney performance.
It also provides detailed explanations for the recommendations.
"""

import typing
from typing import Dict, List, Optional
from datetime import date

# Third-party imports
from langchain.chains import LLMChain  # Version 0.0.27+
import numpy as np  # Version 1.24+

# Internal imports
from ..ai.models import RateRecommendationRequest, RateRecommendationResponse, ExplanationRequest, RecommendationAction
from ..ai.prompts import RATE_RECOMMENDATION_PROMPT, COUNTER_PROPOSAL_PROMPT, RECOMMENDATION_EXPLANATION_PROMPT
from ..ai.langchain_setup import get_llm, get_chain
from ...db.repositories.rate_repository import RateRepository
from ...db.repositories.attorney_repository import AttorneyRepository
from ...utils.logging import logger
from ...utils.cache import cache
from ...utils.event_tracking import track_recommendation_feedback


@cache.cached(ttl=300)
def get_rate_recommendation(request: RateRecommendationRequest) -> RateRecommendationResponse:
    """
    Generates AI-driven recommendations for proposed rates.

    Args:
        request (RateRecommendationRequest): Request object containing rate data and context.

    Returns:
        RateRecommendationResponse: Response containing recommendation actions and counter-proposal values.
    """
    logger.info("Generating rate recommendation", extra={"additional_data": request.dict()})

    # 1. Retrieve historical rate data for the attorney/staff class
    rate_repository = RateRepository()
    historical_data = rate_repository.get_historical_rates(
        attorney_id=str(request.attorney_id),
        client_id=str(request.client_id)
    )

    # 2. Retrieve peer comparison data for benchmark analysis
    peer_data = rate_repository.get_peer_comparison(
        attorney_id=str(request.attorney_id),
        client_id=str(request.client_id)
    )

    # 3. Retrieve attorney performance metrics if available
    attorney_repository = AttorneyRepository()
    performance_data = attorney_repository.get_attorney_performance(
        attorney_id=str(request.attorney_id)
    ) if request.include_performance_data else {}

    # 4. Prepare the prompt with all context data
    prompt = RATE_RECOMMENDATION_PROMPT.format(
        current_rate=request.current_rate,
        proposed_rate=request.proposed_rate,
        historical_data=historical_data,
        peer_data=peer_data,
        performance_data=performance_data,
        rate_rules=request.rate_rules
    )

    # 5. Get the LLM instance from langchain_setup
    llm = get_llm()

    # 6. Execute the recommendation chain with the prepared prompt
    chain = get_chain(chain_type="llm", llm=llm)
    recommendation_text = chain.run(prompt)

    # 7. Parse the LLM response into a structured recommendation
    recommendation = RateRecommendationResponse(
        action=RecommendationAction.APPROVE,  # Placeholder - replace with actual parsing
        counter_proposal_value=None,  # Placeholder - replace with actual parsing
        explanation=recommendation_text
    )

    # 8. Log the generated recommendation for auditing
    logger.info("Generated rate recommendation", extra={"additional_data": recommendation.dict()})

    # 9. Return the structured recommendation response
    return recommendation


def get_counter_proposal_value(
    current_rate: float,
    proposed_rate: float,
    historical_data: Dict,
    peer_data: Dict,
    performance_data: Dict,
    rate_rules: Dict
) -> float:
    """
    Calculates suggested counter-proposal values for rates.

    Args:
        current_rate (float): The current rate.
        proposed_rate (float): The proposed rate.
        historical_data (Dict): Historical rate data.
        peer_data (Dict): Peer rate data.
        performance_data (Dict): Attorney performance data.
        rate_rules (Dict): Client rate rules.

    Returns:
        float: Suggested counter-proposal rate value.
    """
    # 1. Calculate the percentage increase from current to proposed rate
    increase_percentage = (proposed_rate - current_rate) / current_rate * 100 if current_rate else 0

    # 2. Check if increase exceeds client rate rules maximum
    max_increase = rate_rules.get("max_increase", float('inf'))
    if increase_percentage > max_increase:
        # Reduce to maximum allowed increase
        proposed_rate = current_rate * (1 + max_increase / 100)

    # 3. Analyze peer rate data for comparable positions
    peer_average = peer_data.get("average_rate", current_rate)
    peer_range = peer_data.get("rate_range", (current_rate * 0.8, current_rate * 1.2))

    # 4. Factor in attorney performance metrics if available
    performance_factor = 1.0
    if performance_data:
        # Adjust based on performance metrics
        performance_factor += performance_data.get("performance_score", 0) * 0.01

    # 5. Consider historical rate increase patterns
    historical_increase = historical_data.get("average_increase", 0)

    # 6. Apply AI model to suggest optimal counter-proposal value
    # (This is a simplified example - a real implementation would use a trained model)
    counter_proposal = min(proposed_rate * performance_factor, peer_average + historical_increase)

    # 7. Ensure the counter-proposal is within reasonable bounds
    counter_proposal = max(counter_proposal, current_rate)
    counter_proposal = min(counter_proposal, proposed_rate)

    # 8. Return the calculated counter-proposal value
    return counter_proposal


@cache.cached(ttl=300)
def get_recommendation_explanation(request: ExplanationRequest) -> str:
    """
    Provides detailed explanations for rate recommendations.

    Args:
        request (ExplanationRequest): Request object containing recommendation details.

    Returns:
        str: Detailed explanation of the recommendation rationale.
    """
    logger.info("Generating recommendation explanation", extra={"additional_data": request.dict()})

    # 1. Log the explanation request
    logger.info(f"Generating explanation for recommendation: {request.recommendation_id}")

    # 2. Retrieve the original recommendation context
    # (This would typically involve retrieving data from a database or cache)
    context_data = {"example_context": "This is a placeholder for context data"}

    # 3. Prepare the explanation prompt with recommendation details
    prompt = RECOMMENDATION_EXPLANATION_PROMPT.format(
        recommendation=request.recommendation_details,
        context_data=context_data
    )

    # 4. Get the LLM instance from langchain_setup
    llm = get_llm()

    # 5. Execute the explanation chain with the prepared prompt
    chain = get_chain(chain_type="llm", llm=llm)
    explanation_text = chain.run(prompt)

    # 6. Format the explanation text for readability
    formatted_explanation = f"Explanation: {explanation_text}"

    # 7. Return the formatted explanation
    return formatted_explanation


def process_recommendation_feedback(
    recommendation_id: str,
    was_accepted: bool,
    user_action: str,
    context_data: Dict
) -> bool:
    """
    Processes user feedback on recommendations to improve future suggestions.

    Args:
        recommendation_id (str): ID of the recommendation being evaluated.
        was_accepted (bool): Whether the recommendation was accepted by the user.
        user_action (str): The action taken by the user (e.g., "approve", "counter").
        context_data (Dict): Contextual data related to the recommendation.

    Returns:
        bool: Success status of feedback processing.
    """
    logger.info(f"Processing feedback for recommendation: {recommendation_id}")

    # 1. Log the feedback received for the recommendation
    logger.info(f"Feedback: Accepted={was_accepted}, Action={user_action}")

    # 2. Track the feedback using event_tracking module
    event_tracking.track_recommendation_feedback(
        recommendation_id=recommendation_id,
        was_accepted=was_accepted,
        user_action=user_action,
        context_data=context_data
    )

    # 3. Store the feedback data for model improvement
    # (This would typically involve storing the data in a database or data lake)
    # For now, we'll just log the data
    logger.info(f"Storing feedback data for model improvement: {context_data}")

    # 4. Update recommendation success metrics
    # (This would typically involve updating metrics in a monitoring system)
    logger.info("Updating recommendation success metrics")

    # 5. Return success status of the feedback processing
    return True


def analyze_rate_factors(
    historical_data: Dict,
    peer_data: Dict,
    performance_data: Dict,
    rate_rules: Dict
) -> Dict:
    """
    Analyzes various factors that influence rate recommendations.

    Args:
        historical_data (Dict): Historical rate data.
        peer_data (Dict): Peer rate data.
        performance_data (Dict): Attorney performance data.
        rate_rules (Dict): Client rate rules.

    Returns:
        Dict: Analysis results with factor weightings and insights.
    """
    # 1. Calculate historical rate increase patterns
    historical_increase = historical_data.get("average_increase", 0)

    # 2. Analyze peer rate comparisons and deviations
    peer_average = peer_data.get("average_rate", 0)
    peer_deviation = peer_data.get("deviation", 0)

    # 3. Evaluate attorney performance metrics relative to peers
    performance_score = performance_data.get("performance_score", 0)

    # 4. Consider client rate rules and constraints
    max_increase = rate_rules.get("max_increase", float('inf'))

    # 5. Determine appropriate weightings for each factor
    # (This is a simplified example - a real implementation would use a trained model)
    weights = {
        "historical": 0.2,
        "peer": 0.3,
        "performance": 0.3,
        "rules": 0.2
    }

    # 6. Generate insights based on the weighted factors
    insights = {
        "historical_trend": f"Historical rate increases have averaged {historical_increase:.2f}%",
        "peer_comparison": f"Peer rates average ${peer_average:.2f} with a deviation of ${peer_deviation:.2f}",
        "performance_impact": f"Attorney performance score is {performance_score:.2f}",
        "rule_constraint": f"Maximum allowed increase is {max_increase:.2f}%"
    }

    # 7. Return the comprehensive factor analysis
    return {
        "weights": weights,
        "insights": insights
    }


class RateRecommendationService:
    """
    Service class that provides rate recommendation functionality.
    """

    def __init__(self, rate_repository: RateRepository, attorney_repository: AttorneyRepository):
        """
        Initializes the rate recommendation service with necessary repositories.

        Args:
            rate_repository (RateRepository): Repository for accessing rate data.
            attorney_repository (AttorneyRepository): Repository for accessing attorney data.
        """
        # 1. Initialize repositories
        self._rate_repository = rate_repository
        self._attorney_repository = attorney_repository

        # 2. Get LLM instance from langchain_setup
        self._llm = get_llm()

    def recommend_rate_action(self, rate_data: Dict, context_data: Dict) -> RecommendationAction:
        """
        Recommends an action for a proposed rate (approve, reject, counter).

        Args:
            rate_data (Dict): Data for the rate being evaluated.
            context_data (Dict): Contextual data for the recommendation.

        Returns:
            RecommendationAction: Recommended action (APPROVE, REJECT, COUNTER).
        """
        # 1. Retrieve historical rate data
        historical_data = self._rate_repository.get_historical_rates(
            attorney_id=rate_data["attorney_id"],
            client_id=rate_data["client_id"]
        )

        # 2. Retrieve peer comparison data
        peer_data = self._rate_repository.get_peer_comparison(
            attorney_id=rate_data["attorney_id"],
            client_id=rate_data["client_id"]
        )

        # 3. Retrieve attorney performance data if available
        performance_data = self._attorney_repository.get_attorney_performance(
            attorney_id=rate_data["attorney_id"]
        ) if context_data.get("include_performance_data") else {}

        # 4. Call get_rate_recommendation with gathered data
        recommendation = get_rate_recommendation(
            RateRecommendationRequest(
                current_rate=rate_data["current_rate"],
                proposed_rate=rate_data["proposed_rate"],
                historical_data=historical_data,
                peer_data=peer_data,
                performance_data=performance_data,
                rate_rules=context_data["rate_rules"],
                attorney_id=rate_data["attorney_id"],
                client_id=rate_data["client_id"],
                include_performance_data=context_data.get("include_performance_data", False)
            )
        )

        # 5. Extract and return the recommended action
        return recommendation.action

    def suggest_counter_rate(self, rate_data: Dict, context_data: Dict) -> float:
        """
        Suggests a counter-proposal value for a rate.

        Args:
            rate_data (Dict): Data for the rate being evaluated.
            context_data (Dict): Contextual data for the recommendation.

        Returns:
            float: Suggested counter-proposal rate value.
        """
        # 1. Retrieve historical rate data
        historical_data = self._rate_repository.get_historical_rates(
            attorney_id=rate_data["attorney_id"],
            client_id=rate_data["client_id"]
        )

        # 2. Retrieve peer comparison data
        peer_data = self._rate_repository.get_peer_comparison(
            attorney_id=rate_data["attorney_id"],
            client_id=rate_data["client_id"]
        )

        # 3. Retrieve attorney performance data if available
        performance_data = self._attorney_repository.get_attorney_performance(
            attorney_id=rate_data["attorney_id"]
        ) if context_data.get("include_performance_data") else {}

        # 4. Call get_counter_proposal_value with gathered data
        counter_proposal_value = get_counter_proposal_value(
            current_rate=rate_data["current_rate"],
            proposed_rate=rate_data["proposed_rate"],
            historical_data=historical_data,
            peer_data=peer_data,
            performance_data=performance_data,
            rate_rules=context_data["rate_rules"]
        )

        # 5. Return the suggested counter-proposal value
        return counter_proposal_value

    def explain_recommendation(self, recommendation_id: str) -> str:
        """
        Provides a detailed explanation for a recommendation.

        Args:
            recommendation_id (str): ID of the recommendation to explain.

        Returns:
            str: Detailed explanation of the recommendation.
        """
        # 1. Retrieve the recommendation record
        # (This would typically involve retrieving data from a database or cache)
        recommendation_details = {"example_recommendation": "This is a placeholder for recommendation details"}

        # 2. Gather the context data used for the recommendation
        context_data = {"example_context": "This is a placeholder for context data"}

        # 3. Call get_recommendation_explanation with context data
        explanation = get_recommendation_explanation(
            ExplanationRequest(
                recommendation_id=recommendation_id,
                recommendation_details=recommendation_details,
                context_data=context_data
            )
        )

        # 4. Return the formatted explanation
        return explanation

    def record_feedback(self, recommendation_id: str, was_accepted: bool, user_action: str) -> bool:
        """
        Records user feedback on a recommendation.

        Args:
            recommendation_id (str): ID of the recommendation being evaluated.
            was_accepted (bool): Whether the recommendation was accepted by the user.
            user_action (str): The action taken by the user (e.g., "approve", "counter").

        Returns:
            bool: Success status.
        """
        # 1. Retrieve the recommendation record
        # (This would typically involve retrieving data from a database or cache)
        recommendation_details = {"example_recommendation": "This is a placeholder for recommendation details"}

        # 2. Gather the context data used for the recommendation
        context_data = {"example_context": "This is a placeholder for context data"}

        # 3. Call process_recommendation_feedback with data
        return process_recommendation_feedback(
            recommendation_id=recommendation_id,
            was_accepted=was_accepted,
            user_action=user_action,
            context_data=context_data
        )

    def get_batch_recommendations(self, rate_data_list: List[Dict], shared_context: Dict) -> List:
        """
        Generates recommendations for multiple rates in batch.

        Args:
            rate_data_list (List): List of rate data dictionaries.
            shared_context (Dict): Context data shared across all rates.

        Returns:
            List: List of recommendations for each rate.
        """
        recommendations = []

        # 1. Process each rate in the batch
        for rate_data in rate_data_list:
            # 2. Gather shared context data once for efficiency
            # (In a real implementation, this might involve retrieving data from a cache)
            context_data = shared_context

            # 3. Call recommend_rate_action for each rate
            action = self.recommend_rate_action(rate_data, context_data)

            # 4. For counter recommendations, call suggest_counter_rate
            counter_proposal = None
            if action == RecommendationAction.COUNTER:
                counter_proposal = self.suggest_counter_rate(rate_data, context_data)

            # 5. Compile results into a structured response
            recommendations.append({
                "rate_id": rate_data["rate_id"],
                "action": action,
                "counter_proposal": counter_proposal
            })

        # 6. Return the batch recommendations
        return recommendations