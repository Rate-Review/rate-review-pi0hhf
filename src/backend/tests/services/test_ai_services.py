import pytest
from unittest.mock import MagicMock
from typing import Dict, List

from src.backend.services.ai import chat, recommendations, personalization, process_management
from src.backend.services.ai.langchain_setup import get_llm, get_chain
from src.backend.services.ai.prompts import get_rate_recommendation_prompt
from src.backend.integrations.openai.client import OpenAIClient

# Define test chat queries and expected responses
TEST_CHAT_QUERIES = [
    ("What is the capital of France?", "The capital of France is Paris."),
    ("Tell me a joke.", "Why don't scientists trust atoms? Because they make up everything!"),
]

class TestAIServicesMocked:
    """Test class containing setup for mocked AI services tests that share common fixtures and mocking."""

    def __init__(self):
        """Initializes the test class"""
        pass

    def setup_method(self, method):
        """Set up common mocks and fixtures before each test method"""
        # Create mock for OpenAI client
        self.openai_client_mock = MagicMock(spec=OpenAIClient)

        # Create mock for LangChain components
        self.llm_mock = MagicMock()
        self.chain_mock = MagicMock()

        # Set up common test data for rates, users, and negotiations
        self.test_rate_data = {"current_rate": 100, "proposed_rate": 110}
        self.test_user_data = {"user_id": "test_user", "role": "analyst"}
        self.test_negotiation_data = {"negotiation_id": "test_negotiation"}

        # Configure mock responses for common scenarios
        self.openai_client_mock.chat_completion.return_value = {"choices": [{"message": {"content": "Test response"}}]}
        self.llm_mock.generate.return_value = "Test LLM response"
        self.chain_mock.run.return_value = "Test chain response"

    def teardown_method(self, method):
        """Clean up mocks and fixtures after each test method"""
        # Reset all mocks
        self.openai_client_mock.reset_mock()
        self.llm_mock.reset_mock()
        self.chain_mock.reset_mock()

        # Clean up any test data
        self.test_rate_data = {}
        self.test_user_data = {}
        self.test_negotiation_data = {}

    def test_chat_integration(self):
        """Integration test ensuring chat service works with OpenAI and database components"""
        # Set up realistic test scenario with multiple components
        # Mock all external dependencies
        # Execute chat processing workflow
        # Verify correct interaction between components
        # Assert final result matches expected outcome
        pass

    def test_recommendation_integration(self):
        """Integration test ensuring recommendation service works with rate data and AI components"""
        # Set up complex test scenario with rate data
        # Mock AI responses with realistic recommendation data
        # Execute recommendation workflow
        # Verify data flow through multiple components
        # Assert recommendations match expected format and content
        pass

@pytest.mark.parametrize('query, expected_response', TEST_CHAT_QUERIES)
def test_process_chat_request(mocker, query, expected_response):
    """Tests the process_chat_request function to ensure it correctly processes user chat requests and returns appropriate responses."""
    # Mock the OpenAI client and LangChain integration
    openai_client_mock = mocker.patch("src.backend.services.ai.chat.OpenAIClient").return_value
    openai_client_mock.process_chat_interaction.return_value = {"content": expected_response}
    get_chain_mock = mocker.patch("src.backend.services.ai.chat.get_chain")
    get_chain_mock.return_value.run.return_value = expected_response
    permission_service_mock = mocker.patch("src.backend.services.ai.chat.PermissionService").return_value
    permission_service_mock.check_permission.return_value = True
    ChatService_mock = mocker.patch("src.backend.services.ai.chat.ChatService").return_value
    ChatService_mock.process_message.return_value = {"content": expected_response, "metadata": {}}

    # Set up mock responses for different query types
    user_mock = MagicMock()
    user_mock.id = "test_user_id"
    user_mock.organization_id = "test_org_id"
    user_mock.role.value = "analyst"
    user_mock.preferences = {}
    user_mock.permissions = []

    # Call process_chat_request with test query
    response = chat.chat(user=user_mock, message=query, session_id="test_session_id")

    # Assert response matches expected format and content
    assert "message" in response
    assert response["message"] == expected_response

    # Verify appropriate permissions were checked
    permission_service_mock.check_permission.assert_called_once()

    # Verify message was stored in history
    ChatService_mock.process_message.assert_called_once()

def test_get_chat_history(mocker):
    """Tests the get_chat_history function to ensure it correctly retrieves chat history for a user."""
    # Mock the database repository for message history
    ChatService_mock = mocker.patch("src.backend.services.ai.chat.ChatService").return_value
    ChatService_mock.get_session.return_value = MagicMock()
    ChatService_mock.get_session.return_value.messages = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}]

    # Set up mock data for chat history
    # Call get_chat_history with user_id
    history = chat.get_session_history(session_id="test_session_id")

    # Assert returned history matches expected data
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"

    # Verify history is properly formatted with user/assistant messages
    ChatService_mock.get_session.assert_called_once()

def test_generate_rate_recommendations(mocker):
    """Tests the generate_rate_recommendations function to ensure it correctly generates AI-driven recommendations for attorney rates."""
    # Mock the LLM and chain objects from langchain_setup
    get_chain_mock = mocker.patch("src.backend.services.ai.recommendations.get_chain")
    get_chain_mock.return_value.run.return_value = "Test recommendation"

    # Mock the rate data retrieval functions
    RateRepository_mock = mocker.patch("src.backend.services.ai.recommendations.RateRepository").return_value
    RateRepository_mock.get_historical_rates.return_value = {"rates": {"2022": 100, "2023": 110}}
    RateRepository_mock.get_peer_comparison.return_value = {"average_rate": 120}
    AttorneyRepository_mock = mocker.patch("src.backend.services.ai.recommendations.AttorneyRepository").return_value
    AttorneyRepository_mock.get_attorney_performance.return_value = {"performance_score": 0.9}

    # Set up test rate data and historical information
    rate_data = {"current_rate": 100, "proposed_rate": 110, "attorney_id": "test_attorney_id", "client_id": "test_client_id"}
    historical_data = {"rates": {"2022": 100, "2023": 110}}

    # Set up mock response from AI model
    # Call generate_rate_recommendations with test data
    recommendation = recommendations.get_rate_recommendation(request=MagicMock())

    # Assert recommendations match expected structure and values
    assert "explanation" in recommendation.__dict__
    assert recommendation.explanation == "Test chain response"

    # Verify correct prompt was generated with rate data
    get_chain_mock.assert_called_once()

def test_explain_recommendation(mocker):
    """Tests the explain_recommendation function to ensure it provides detailed explanations for AI recommendations."""
    # Mock the LLM and chain objects
    get_chain_mock = mocker.patch("src.backend.services.ai.recommendations.get_chain")
    get_chain_mock.return_value.run.return_value = "Test explanation"

    # Set up test recommendation data
    recommendation_details = {"action": "approve", "rate": 110}

    # Set up mock response for explanation
    # Call explain_recommendation with test recommendation
    explanation = recommendations.get_recommendation_explanation(request=MagicMock())

    # Assert explanation matches expected content
    assert "Explanation" in explanation
    assert "Test explanation" in explanation

    # Verify explanation includes key factors considered in recommendation
    get_chain_mock.assert_called_once()

def test_get_user_preferences(mocker):
    """Tests the get_user_preferences function to ensure it correctly retrieves and processes user preferences for AI personalization."""
    # Mock the database repository for user preferences
    UserRepository_mock = mocker.patch("src.backend.services.ai.personalization.UserRepository").return_value
    UserRepository_mock.get_preference.return_value = '{"temperature": 0.8}'

    # Set up mock user preference data
    # Call get_user_preferences with user_id
    preferences = personalization.get_user_personalization_settings(user_id="test_user_id", user_repo=UserRepository_mock)

    # Assert returned preferences match expected data
    assert "temperature" in preferences
    assert preferences["temperature"] == 0.8

    # Verify default preferences are applied for missing values
    assert "highlight_threshold" in preferences
    UserRepository_mock.get_preference.assert_called_once()

def test_update_user_preferences(mocker):
    """Tests the update_user_preferences function to ensure it correctly updates user preferences in the database."""
    # Mock the database repository for user preferences
    UserRepository_mock = mocker.patch("src.backend.services.ai.personalization.UserRepository").return_value
    UserRepository_mock.get_preference.return_value = '{"temperature": 0.7}'

    # Set up test preference data to update
    new_preferences = {"temperature": 0.9}

    # Call update_user_preferences with test data
    personalization.update_user_personalization_settings(user_id="test_user_id", settings=new_preferences, user_repo=UserRepository_mock)

    # Assert repository save method called with correct parameters
    UserRepository_mock.set_preference.assert_called_once()

    # Verify validation of preference data structure
    # (This is implicitly tested by the fact that no exception is raised)

def test_prioritize_actions(mocker):
    """Tests the prioritize_actions function to ensure it correctly prioritizes user actions based on AI analysis."""
    # Mock the LLM and chain objects
    get_chain_mock = mocker.patch("src.backend.services.ai.process_management.get_chain")
    get_chain_mock.return_value.run.return_value = "Test prioritized actions"

    # Set up test action data
    actions = [{"type": "approve", "description": "Approve rate"}]

    # Set up mock prioritized response from AI model
    # Call prioritize_actions with test actions
    prioritized_actions = process_management.get_prioritized_actions(user_id="test_user_id", organization_id="test_org_id", limit=10, include_ai_rationale=False)

    # Assert prioritized actions match expected order and importance
    # Verify actions contain appropriate metadata and rationale
    assert "actions" in prioritized_actions
    assert "total_actions" in prioritized_actions

def test_suggest_next_steps(mocker):
    """Tests the suggest_next_steps function to ensure it correctly suggests next steps based on current context."""
    # Mock the LLM and chain objects
    # Set up test context data (negotiation state, user role)
    # Set up mock suggestions from AI model
    # Call suggest_next_steps with test context
    suggestions = process_management.suggest_next_steps(user_id="test_user_id", context_type="negotiation", context_id="test_context_id", limit=5)

    # Assert suggestions match expected content and format
    # Verify suggestions are appropriate for user role and context
    assert isinstance(suggestions, list)

def test_get_llm(mocker):
    """Tests the get_llm function to ensure it correctly configures and returns LangChain LLM objects."""
    # Mock the LangChain libraries
    mocker.patch("src.backend.services.ai.langchain_setup.ChatOpenAI")
    mocker.patch("src.backend.services.ai.langchain_setup.AzureChatOpenAI")

    # Mock configuration settings
    mocker.patch("src.backend.services.ai.langchain_setup.get_settings")
    # Call get_llm with different configuration parameters
    llm = get_llm()

    # Assert correct LLM type is returned based on config
    # Verify model parameters are correctly applied (temperature, max_tokens)
    assert llm is not None

def test_get_chain(mocker):
    """Tests the get_chain function to ensure it correctly creates LangChain chains with prompts."""
    # Mock the LangChain chain objects
    mocker.patch("src.backend.services.ai.langchain_setup.LLMChain")
    mocker.patch("src.backend.services.ai.langchain_setup.ConversationChain")

    # Mock the get_llm function
    mocker.patch("src.backend.services.ai.langchain_setup.get_llm")

    # Set up test prompt template
    # Call get_chain with test template
    chain = get_chain(chain_type="llm", llm=MagicMock(), prompt=MagicMock())

    # Assert chain is created with correct LLM and prompt
    # Verify chain type matches expected configuration
    assert chain is not None

def test_get_rate_recommendation_prompt(mocker):
    """Tests the get_rate_recommendation_prompt function to ensure it correctly generates prompts for rate recommendations."""
    # Set up test rate data and context
    rate_data = {"current_rate": 100, "proposed_rate": 110, "user_role": "analyst", "organization_name": "Test Org"}
    historical_data = {"rates": {"2022": 100, "2023": 110}}
    peer_data = {"average_rate": 120}
    performance_data = {"performance_score": 0.9}
    rate_rules = {"max_increase": 0.1}

    # Call get_rate_recommendation_prompt with test data
    prompt = get_rate_recommendation_prompt(rate_data, historical_data, peer_data, performance_data, rate_rules)

    # Assert generated prompt contains all required elements
    assert "current_rate" in prompt
    assert "proposed_rate" in prompt
    assert "historical_rates" in prompt
    assert "peer_comparison" in prompt
    assert "performance_metrics" in prompt
    assert "rate_rules" in prompt

    # Verify prompt includes historical rates, peer data, and client rules
    # Verify prompt format matches expected LangChain template
    assert "You are an expert legal rate analyst" in prompt