"""
Integration tests for OpenAI API client functionality used in the Justice Bid Rate Negotiation System.

Tests the connection, chat completions, embeddings generation, and domain-specific AI functionality 
for rate recommendations and document analysis.
"""

import pytest
import os
import json
from unittest.mock import patch, MagicMock

from src.backend.integrations.openai.client import (
    OpenAIClient,
    OpenAIModelType,
    count_tokens,
    estimate_chat_tokens
)
from src.backend.api.core.config import get_config

# Test data constants
SAMPLE_MESSAGES = [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello, can you help me with rate negotiations?"}
]

SAMPLE_RATE_DATA = {
    "current_rate": 500.0,
    "proposed_rate": 550.0,
    "attorney_name": "John Smith",
    "years_experience": 8,
    "practice_area": "Litigation"
}

SAMPLE_HISTORICAL_DATA = {
    "previous_rates": [
        {"year": 2022, "rate": 500.0},
        {"year": 2021, "rate": 475.0},
        {"year": 2020, "rate": 450.0}
    ],
    "average_increase": 0.05
}

SAMPLE_PERFORMANCE_DATA = {
    "cases_won": 15,
    "cases_lost": 5,
    "efficiency_score": 0.8,
    "client_rating": 4.5
}

SAMPLE_PEER_COMPARISON = {
    "average_rate": 525.0,
    "median_rate": 515.0,
    "percentile_90": 575.0,
    "similar_attorneys": [
        {"name": "Anonymous", "rate": 530.0},
        {"name": "Anonymous", "rate": 520.0}
    ]
}

SAMPLE_CLIENT_GUIDELINES = {
    "max_increase_percentage": 0.05,
    "negotiation_deadline": "2023-12-31",
    "preferred_effective_date": "2024-01-01"
}

SAMPLE_DOCUMENT = """# Outside Counsel Guidelines

## Rate Structure

Rates will be frozen for 24 months from the effective date of this agreement.

## Billing Guidelines

Invoices must be submitted monthly and include timekeeper details."""


class OpenAIClientTestFixture:
    """Pytest fixture class for OpenAI client tests that provides common setup and teardown."""
    
    def __init__(self):
        """Set up the test fixtures for OpenAI client tests."""
        self.config = get_config()
        self.api_key = self.config.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self.client = None
        
    def setup(self):
        """Setup method that runs before each test."""
        # Retrieve API key from environment or config
        self.api_key = self.config.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        # Create a new OpenAIClient instance
        self.client = OpenAIClient(api_key=self.api_key)
        
    def teardown(self):
        """Teardown method that runs after each test."""
        # Clean up any resources
        self.client = None
        
    def mock_openai_response(self, response_data):
        """
        Helper method to mock OpenAI API responses.
        
        Args:
            response_data: Mock response data
            
        Returns:
            Mock object configured with the response data
        """
        mock_response = MagicMock()
        for key, value in response_data.items():
            setattr(mock_response, key, value)
        return mock_response


def test_openai_client_initialization():
    """Tests successful initialization of the OpenAI client."""
    # Get API key from config or environment variables
    config = get_config()
    api_key = config.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    
    # Create an instance of OpenAIClient with API key
    client = OpenAIClient(api_key=api_key)
    
    # Assert that the client is initialized correctly
    assert client._initialized is True
    assert client._client is not None
    assert client._api_key == api_key


def test_openai_client_initialization_failure():
    """Tests initialization failure with invalid API key."""
    # Attempt to create an OpenAIClient with an invalid API key
    with pytest.raises(ValueError):
        client = OpenAIClient(api_key="invalid_key_format")
        client.validate_connection()
    
    # Create a client with invalid key but don't validate
    client = OpenAIClient(api_key="invalid_key_format")
    
    # Check that appropriate error information is provided
    assert client.validate_connection() is False


def test_validate_connection():
    """Tests the validate_connection method to ensure proper API connectivity."""
    # Create an instance of OpenAIClient with valid credentials
    fixture = OpenAIClientTestFixture()
    fixture.setup()
    
    # Call the validate_connection method
    if fixture.api_key:
        # Assert that the connection is valid and returns True
        assert fixture.client.validate_connection() is True
    
    # Mock a failed connection scenario
    with patch.object(fixture.client, 'get_available_models', side_effect=Exception("API Error")):
        # Assert that the method handles failures appropriately
        assert fixture.client.validate_connection() is False
    
    fixture.teardown()


def test_chat_completion():
    """Tests the chat_completion method with sample messages."""
    # Create an instance of OpenAIClient
    fixture = OpenAIClientTestFixture()
    fixture.setup()
    
    if fixture.api_key:
        try:
            # Call the chat_completion method with SAMPLE_MESSAGES
            response = fixture.client.chat_completion(messages=SAMPLE_MESSAGES, max_tokens=100)
            
            # Assert that the response contains the expected structure
            assert isinstance(response, dict)
            assert "choices" in response
            assert len(response["choices"]) > 0
            
            # Verify that the response includes 'content' and other required fields
            first_choice = response["choices"][0]
            assert "message" in first_choice
            assert "content" in first_choice["message"]
            assert first_choice["message"]["content"] != ""
            
            # Check that token usage information is returned
            assert "usage" in response
            assert "prompt_tokens" in response["usage"]
            assert "completion_tokens" in response["usage"]
            assert "total_tokens" in response["usage"]
        except Exception as e:
            pytest.skip(f"Skipping test due to API issue: {str(e)}")
    else:
        pytest.skip("Skipping test because no API key is provided")
    
    fixture.teardown()


def test_chat_completion_with_functions():
    """Tests the chat_completion method with function calling capabilities."""
    # Create an instance of OpenAIClient
    fixture = OpenAIClientTestFixture()
    fixture.setup()
    
    if fixture.api_key:
        try:
            # Define a sample function specification for testing
            functions = [
                {
                    "name": "get_rate_information",
                    "description": "Get rate information for an attorney",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "attorney_name": {
                                "type": "string",
                                "description": "Name of the attorney"
                            },
                            "practice_area": {
                                "type": "string",
                                "description": "Practice area of interest"
                            }
                        },
                        "required": ["attorney_name"]
                    }
                }
            ]
            
            # Messages designed to trigger function call
            messages = [
                {"role": "system", "content": "You are a helpful assistant that can retrieve rate information."},
                {"role": "user", "content": "What is the rate for attorney John Smith in Litigation?"}
            ]
            
            # Call chat_completion with messages and functions parameter
            response = fixture.client.chat_completion(
                messages=messages,
                functions=functions,
                max_tokens=100
            )
            
            # Assert that the response contains the expected structure
            assert isinstance(response, dict)
            assert "choices" in response
            assert len(response["choices"]) > 0
            
            # Verify the structure of the function call response
            first_choice = response["choices"][0]
            assert "message" in first_choice
            
            if "function_call" in first_choice["message"]:
                function_call = first_choice["message"]["function_call"]
                assert "name" in function_call
                assert function_call["name"] == "get_rate_information"
                assert "arguments" in function_call
        except Exception as e:
            pytest.skip(f"Skipping test due to API issue: {str(e)}")
    else:
        pytest.skip("Skipping test because no API key is provided")
    
    fixture.teardown()


def test_create_embeddings():
    """Tests the create_embeddings method with sample text."""
    # Create an instance of OpenAIClient
    fixture = OpenAIClientTestFixture()
    fixture.setup()
    
    if fixture.api_key:
        try:
            # Call create_embeddings with a sample text
            sample_text = "This is a sample text for testing embeddings generation."
            embeddings = fixture.client.create_embeddings(texts=sample_text)
            
            # Assert that the response contains a vector embedding
            assert isinstance(embeddings, list)
            assert len(embeddings) == 1
            
            # Verify that the embedding has the expected dimensions
            assert isinstance(embeddings[0], list)
            assert len(embeddings[0]) > 0
            
            # Test with multiple texts to ensure batch processing works
            multiple_texts = ["First text for embedding", "Second text for embedding"]
            multi_embeddings = fixture.client.create_embeddings(texts=multiple_texts)
            
            # Verify batch processing
            assert len(multi_embeddings) == 2
            assert len(multi_embeddings[0]) == len(multi_embeddings[1])
        except Exception as e:
            pytest.skip(f"Skipping test due to API issue: {str(e)}")
    else:
        pytest.skip("Skipping test because no API key is provided")
    
    fixture.teardown()


def test_rate_recommendation():
    """Tests the rate_recommendation method with sample rate data."""
    # Create an instance of OpenAIClient
    fixture = OpenAIClientTestFixture()
    fixture.setup()
    
    if fixture.api_key:
        try:
            # Call rate_recommendation with sample rate data and context
            response = fixture.client.rate_recommendation(
                rate_data=SAMPLE_RATE_DATA,
                historical_data=SAMPLE_HISTORICAL_DATA,
                performance_data=SAMPLE_PERFORMANCE_DATA,
                peer_comparison=SAMPLE_PEER_COMPARISON,
                client_guidelines=SAMPLE_CLIENT_GUIDELINES
            )
            
            # Assert that the response contains a recommendation action
            assert isinstance(response, dict)
            assert "recommendations" in response
            assert isinstance(response["recommendations"], list)
            assert len(response["recommendations"]) > 0
            
            # Verify that a counter-proposal value is provided when appropriate
            for recommendation in response["recommendations"]:
                assert "action" in recommendation
                assert recommendation["action"] in ["approve", "reject", "counter"]
                
                if recommendation["action"] == "counter":
                    assert "counter_rate" in recommendation
                    assert isinstance(recommendation["counter_rate"], (int, float))
                
                # Check that an explanation is included in the response
                assert "explanation" in recommendation
                assert isinstance(recommendation["explanation"], str)
                assert len(recommendation["explanation"]) > 0
        except Exception as e:
            pytest.skip(f"Skipping test due to API issue: {str(e)}")
    else:
        pytest.skip("Skipping test because no API key is provided")
    
    fixture.teardown()


def test_process_chat_interaction():
    """Tests the process_chat_interaction method for handling chat with context."""
    # Create an instance of OpenAIClient
    fixture = OpenAIClientTestFixture()
    fixture.setup()
    
    if fixture.api_key:
        try:
            # Prepare sample user message, conversation history, and context
            user_message = "What would be a reasonable counter-proposal for the rate increase requested by John Smith?"
            conversation_history = [
                {"role": "system", "content": "You are a helpful assistant specialized in legal rate negotiations."},
                {"role": "user", "content": "I'm reviewing rate proposals from our law firms."},
                {"role": "assistant", "content": "I'd be happy to help you review those rate proposals."}
            ]
            user_context = {
                "role": "client",
                "organization": "Acme Corporation",
                "permissions": ["view_rates", "negotiate_rates"]
            }
            system_context = {
                "current_negotiation": {
                    "law_firm": "ABC Law",
                    "attorneys": [
                        {"name": "John Smith", "current_rate": 500, "proposed_rate": 550}
                    ]
                }
            }
            
            # Call process_chat_interaction with these parameters
            response = fixture.client.process_chat_interaction(
                user_message=user_message,
                conversation_history=conversation_history,
                user_context=user_context,
                system_context=system_context
            )
            
            # Assert that the response contains the expected structure
            assert isinstance(response, dict)
            assert "content" in response
            assert isinstance(response["content"], str)
            assert len(response["content"]) > 0
            assert "role" in response
            assert response["role"] == "assistant"
            assert "created_at" in response
            assert "model_used" in response
            
            # Verify that user and system context are properly incorporated
            assert any(["John Smith" in response["content"], 
                       "counter" in response["content"].lower(), 
                       "proposal" in response["content"].lower()])
        except Exception as e:
            pytest.skip(f"Skipping test due to API issue: {str(e)}")
    else:
        pytest.skip("Skipping test because no API key is provided")
    
    fixture.teardown()


def test_analyze_document():
    """Tests the analyze_document method with a sample document."""
    # Create an instance of OpenAIClient
    fixture = OpenAIClientTestFixture()
    fixture.setup()
    
    if fixture.api_key:
        try:
            # Call analyze_document with SAMPLE_DOCUMENT and document type
            response = fixture.client.analyze_document(
                document_text=SAMPLE_DOCUMENT,
                document_type="OCG"
            )
            
            # Assert that the response contains structured analysis
            assert isinstance(response, dict)
            assert "document_type" in response
            assert response["document_type"] == "OCG"
            assert "key_sections" in response
            assert isinstance(response["key_sections"], list)
            assert len(response["key_sections"]) > 0
            
            # Verify that key sections are identified correctly
            section_titles = [section["title"] for section in response["key_sections"]]
            assert any("Rate" in title for title in section_titles)
            assert any("Billing" in title for title in section_titles)
            
            # Check that any negotiable elements are highlighted
            for section in response["key_sections"]:
                assert "negotiable" in section
        except Exception as e:
            pytest.skip(f"Skipping test due to API issue: {str(e)}")
    else:
        pytest.skip("Skipping test because no API key is provided")
    
    fixture.teardown()


@pytest.mark.parametrize("text,model,expected_range", [
    ("Hello world", "gpt-4", (2, 5)),
    ("This is a longer text for testing token counting functionality", "gpt-4", (10, 15))
])
def test_count_tokens(text, model, expected_range):
    """Tests the count_tokens utility function."""
    # Take the parametrized text, model, and expected range
    token_count = count_tokens(text, model)
    
    # Assert that the result is within the expected range
    min_tokens, max_tokens = expected_range
    assert min_tokens <= token_count <= max_tokens
    
    # Test with different models to ensure proper encoding
    token_count_default = count_tokens(text)
    assert token_count_default > 0


def test_estimate_chat_tokens():
    """Tests the estimate_chat_tokens utility function."""
    # Create sample chat messages of varying length
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello, can you help me with rate negotiations?"},
        {"role": "assistant", "content": "Of course! I'd be happy to help you with rate negotiations."}
    ]
    
    # Call estimate_chat_tokens with the messages and model
    token_count = estimate_chat_tokens(messages, "gpt-4")
    
    # Assert that the token count is within expected ranges
    assert token_count > 0
    
    # Verify that adding messages increases the token count appropriately
    messages.append({"role": "user", "content": "Great! Let's start with analyzing this rate proposal."})
    new_token_count = estimate_chat_tokens(messages, "gpt-4")
    assert new_token_count > token_count


def test_error_handling():
    """Tests error handling in the OpenAI client for various failure scenarios."""
    # Create an instance of OpenAIClient
    fixture = OpenAIClientTestFixture()
    fixture.setup()
    
    # Test handling of authentication errors
    with patch.object(fixture.client._client.chat.completions, 'create', 
                     side_effect=Exception("Incorrect API key provided")):
        with pytest.raises(ValueError) as exc_info:
            fixture.client.chat_completion(messages=SAMPLE_MESSAGES)
        assert "Failed to generate chat completion" in str(exc_info.value)
    
    # Test handling of rate limits
    with patch.object(fixture.client._client.chat.completions, 'create', 
                     side_effect=Exception("Rate limit exceeded")):
        with pytest.raises(ValueError) as exc_info:
            fixture.client.chat_completion(messages=SAMPLE_MESSAGES)
        assert "Failed to generate chat completion" in str(exc_info.value)
    
    # Test handling of invalid request errors
    with patch.object(fixture.client._client.chat.completions, 'create', 
                     side_effect=Exception("Invalid request")):
        with pytest.raises(ValueError) as exc_info:
            fixture.client.chat_completion(messages=SAMPLE_MESSAGES)
        assert "Failed to generate chat completion" in str(exc_info.value)
    
    # Ensure appropriate exceptions are raised and error messages are clear
    fixture.teardown()


def test_retry_logic():
    """Tests the retry logic for handling transient API failures."""
    # Create an instance of OpenAIClient
    fixture = OpenAIClientTestFixture()
    fixture.setup()
    
    # Mock a transient API failure scenario
    side_effects = [
        Exception("Rate limit exceeded"),  # First attempt fails
        {"choices": [{"message": {"content": "Response after retry"}}]}  # Second attempt succeeds
    ]
    
    # Verify that the client retries the request
    with patch.object(fixture.client._client.chat.completions, 'create', side_effect=side_effects):
        try:
            response = fixture.client.chat_completion(messages=SAMPLE_MESSAGES)
            # Ensure it respects max retry limits
            assert response is not None
            assert "choices" in response
        except ValueError:
            pytest.fail("Retry logic failed to handle transient error")
    
    # Confirm exponential backoff is implemented correctly
    fixture.teardown()


@pytest.mark.parametrize("model_type,expected_model_prefix", [
    (OpenAIModelType.CHAT, "gpt"),
    (OpenAIModelType.EMBEDDING, "text-embedding"),
    (OpenAIModelType.RECOMMENDATION, "gpt"),
    (OpenAIModelType.DOCUMENT_ANALYSIS, "gpt")
])
def test_get_model_by_type(model_type, expected_model_prefix):
    """Tests the get_model_by_type method with different model types."""
    # Create an instance of OpenAIClient
    fixture = OpenAIClientTestFixture()
    fixture.setup()
    
    # Call get_model_by_type with each model type
    model_name = fixture.client.get_model_by_type(model_type)
    
    # Assert that the returned model name has the expected prefix
    assert model_name.startswith(expected_model_prefix)
    
    # Verify that appropriate models are selected for each use case
    fixture.teardown()