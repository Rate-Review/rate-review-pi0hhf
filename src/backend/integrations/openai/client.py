"""
Client for interacting with OpenAI's API services.

This module provides a centralized interface for AI-powered features in the
Justice Bid Rate Negotiation System, handling API communication, error handling,
and domain-specific AI functionality for legal rate negotiation tasks.
"""

import os
import json
import enum
from typing import List, Dict, Union, Optional, Any
import time
from datetime import datetime

import openai  # version 1.0.0+
import tiktoken  # version 0.4.0+
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ...api.core.config import get_config
from ...utils.logging import logger
from ...utils.security import sanitize_input

# Default configuration
DEFAULT_CHAT_MODEL = "gpt-4"
DEFAULT_EMBEDDING_MODEL = "text-embedding-ada-002"
MAX_RETRIES = 3
RETRY_WAIT = 2
REQUEST_TIMEOUT = 60


class OpenAIModelType(enum.Enum):
    """Enumeration of OpenAI model types for different AI capabilities."""
    CHAT = "chat"
    EMBEDDING = "embedding"
    COMPLETION = "completion"
    RECOMMENDATION = "recommendation"
    DOCUMENT_ANALYSIS = "document_analysis"


def count_tokens(text: str, model_name: str = DEFAULT_CHAT_MODEL) -> int:
    """
    Counts the number of tokens in a text string for a specified model.
    
    Args:
        text: The text to count tokens for
        model_name: The name of the model to use for tokenization
        
    Returns:
        Number of tokens in the text
    """
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # Fall back to cl100k_base encoding for default
        encoding = tiktoken.get_encoding("cl100k_base")
    
    return len(encoding.encode(text))


def estimate_chat_tokens(messages: List[Dict[str, str]], model_name: str = DEFAULT_CHAT_MODEL) -> int:
    """
    Estimates the number of tokens in a chat completion request.
    
    Args:
        messages: List of message dictionaries
        model_name: The name of the model to use for tokenization
        
    Returns:
        Estimated token count
    """
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # Fall back to cl100k_base encoding for default
        encoding = tiktoken.get_encoding("cl100k_base")
    
    # Base tokens for the request format
    total_tokens = 0
    
    # Add tokens for each message
    for message in messages:
        # Add tokens for message role and content
        total_tokens += 4  # Format overhead per message
        
        for key, value in message.items():
            total_tokens += len(encoding.encode(value))
            # Add additional token for each key
            total_tokens += 1
    
    # Add tokens for the completion format
    total_tokens += 2  # Format overhead for the completion
    
    return total_tokens


class OpenAIClient:
    """Client for interacting with OpenAI API, providing access to various AI capabilities."""
    
    def __init__(self, api_key: Optional[str] = None, organization_id: Optional[str] = None):
        """
        Initializes the OpenAI client with configuration settings.
        
        Args:
            api_key: OpenAI API key (optional, will use environment/config if not provided)
            organization_id: OpenAI organization ID (optional)
        """
        # Load configuration
        self._config = get_config()
        self._client = None
        self._models_cache = {}
        self._initialized = False
        
        # Use provided API key or get from config/environment
        self._api_key = api_key or self._config.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self._organization_id = organization_id or self._config.get("OPENAI_ORGANIZATION_ID") or os.environ.get("OPENAI_ORGANIZATION_ID")
        
        if not self._api_key:
            logger.warning("OpenAI API key not provided. Client initialized but not functional.")
            return
            
        # Initialize OpenAI client
        try:
            self._client = openai.Client(
                api_key=self._api_key,
                organization=self._organization_id,
                timeout=REQUEST_TIMEOUT
            )
            self._initialized = True
            logger.info("OpenAI client initialized successfully.")
            
            # Test connection and cache available models
            self.validate_connection()
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        functions: List[Dict] = None,
        **kwargs
    ) -> Dict:
        """
        Generates a chat completion response from OpenAI.
        
        Args:
            messages: List of message dictionaries with role and content
            model: The model to use (defaults to configured chat model)
            temperature: Controls randomness (0-1)
            max_tokens: Maximum tokens to generate
            functions: Function definitions for function calling
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            OpenAI completion response
        
        Raises:
            ValueError: If the client is not initialized or the request fails
        """
        if not self._initialized or not self._client:
            raise ValueError("OpenAI client not initialized. Check API key and connection.")
        
        # Use configured model if not specified
        model = model or self.get_model_by_type(OpenAIModelType.CHAT)
        
        # Prepare parameters
        params = {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        # Add functions if provided
        if functions:
            params["functions"] = functions
        
        # Apply input sanitization for security
        sanitized_messages = []
        for message in messages:
            sanitized_message = {}
            for key, value in message.items():
                if key == "content" and isinstance(value, str):
                    sanitized_message[key] = sanitize_input(value)
                else:
                    sanitized_message[key] = value
            sanitized_messages.append(sanitized_message)
        
        # Estimate token usage for logging
        estimated_tokens = estimate_chat_tokens(sanitized_messages, model)
        logger.debug(f"Estimated token usage for chat completion: {estimated_tokens}")
        
        # Apply retry logic for API calls
        @retry(
            retry=retry_if_exception_type((openai.APIError, openai.APIConnectionError, openai.RateLimitError)),
            stop=stop_after_attempt(MAX_RETRIES),
            wait=wait_exponential(multiplier=RETRY_WAIT, min=1, max=10),
            reraise=True
        )
        def _make_chat_request():
            start_time = time.time()
            response = self._client.chat.completions.create(
                messages=sanitized_messages,
                **params
            )
            elapsed_time = time.time() - start_time
            logger.debug(f"Chat completion request took {elapsed_time:.2f}s")
            return response
        
        try:
            response = _make_chat_request()
            
            # Log token usage for monitoring
            if hasattr(response, 'usage'):
                logger.info(
                    f"Token usage: prompt={response.usage.prompt_tokens}, "
                    f"completion={response.usage.completion_tokens}, "
                    f"total={response.usage.total_tokens}"
                )
            
            # Convert response to dictionary
            if hasattr(response, "model_dump"):
                return response.model_dump()
            else:
                # Handle different response formats
                return json.loads(json.dumps(response, default=lambda o: o.__dict__))
                
        except Exception as e:
            logger.error(f"Error in chat completion request: {str(e)}")
            raise ValueError(f"Failed to generate chat completion: {str(e)}")
    
    def create_embeddings(self, texts: Union[str, List[str]], model: str = None) -> List[List[float]]:
        """
        Generates text embeddings for vector-based search and similarity.
        
        Args:
            texts: Text or list of texts to generate embeddings for
            model: The model to use (defaults to configured embedding model)
            
        Returns:
            Vector embeddings for the provided texts
            
        Raises:
            ValueError: If the client is not initialized or the request fails
        """
        if not self._initialized or not self._client:
            raise ValueError("OpenAI client not initialized. Check API key and connection.")
        
        # Use configured model if not specified
        model = model or self.get_model_by_type(OpenAIModelType.EMBEDDING)
        
        # Ensure texts is a list
        if isinstance(texts, str):
            texts = [texts]
        
        # Apply retry logic for API calls
        @retry(
            retry=retry_if_exception_type((openai.APIError, openai.APIConnectionError, openai.RateLimitError)),
            stop=stop_after_attempt(MAX_RETRIES),
            wait=wait_exponential(multiplier=RETRY_WAIT, min=1, max=10),
            reraise=True
        )
        def _make_embeddings_request():
            start_time = time.time()
            response = self._client.embeddings.create(
                model=model,
                input=texts
            )
            elapsed_time = time.time() - start_time
            logger.debug(f"Embeddings request took {elapsed_time:.2f}s")
            return response
        
        try:
            response = _make_embeddings_request()
            
            # Extract embeddings from response
            embeddings = [item.embedding for item in response.data]
            
            # Log token usage for monitoring
            if hasattr(response, 'usage'):
                logger.info(f"Token usage for embeddings: {response.usage.total_tokens}")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error in embeddings request: {str(e)}")
            raise ValueError(f"Failed to generate embeddings: {str(e)}")
    
    def rate_recommendation(
        self,
        rate_data: Dict,
        historical_data: Dict,
        performance_data: Optional[Dict] = None,
        peer_comparison: Optional[Dict] = None,
        client_guidelines: Optional[Dict] = None
    ) -> Dict:
        """
        Generates AI-driven recommendations for rate proposals.
        
        Args:
            rate_data: Current rate information
            historical_data: Historical rate and billing data
            performance_data: Attorney performance metrics (optional)
            peer_comparison: Peer rate comparison data (optional)
            client_guidelines: Client rate guidelines (optional)
            
        Returns:
            Recommendation with action and suggested rates
        """
        # Construct a detailed prompt with all the provided data
        system_prompt = """
        You are an expert legal rate analyst in the Justice Bid Rate Negotiation System. 
        You analyze rate proposals and provide data-driven recommendations.
        
        Based on the provided data, you will recommend whether to approve, 
        reject, or counter-propose each rate, with specific counter-proposal values 
        where appropriate. Include brief explanations for your recommendations.
        
        Your recommendations should be fair, balanced, and aligned with market standards.
        """
        
        # Build the user prompt with the rate data and context
        user_prompt = f"""
        Please analyze the following rate proposal and provide recommendations:
        
        PROPOSED RATE DATA:
        {json.dumps(rate_data, indent=2)}
        
        HISTORICAL DATA:
        {json.dumps(historical_data, indent=2)}
        """
        
        # Add optional context if available
        if performance_data:
            user_prompt += f"\nPERFORMANCE DATA:\n{json.dumps(performance_data, indent=2)}"
        
        if peer_comparison:
            user_prompt += f"\nPEER COMPARISON:\n{json.dumps(peer_comparison, indent=2)}"
        
        if client_guidelines:
            user_prompt += f"\nCLIENT GUIDELINES:\n{json.dumps(client_guidelines, indent=2)}"
        
        # Define the expected response format using function calling
        functions = [
            {
                "name": "provide_rate_recommendation",
                "description": "Provide recommendations for the proposed rates",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recommendations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "attorney_id": {"type": "string"},
                                    "attorney_name": {"type": "string"},
                                    "current_rate": {"type": "number"},
                                    "proposed_rate": {"type": "number"},
                                    "action": {"type": "string", "enum": ["approve", "reject", "counter"]},
                                    "counter_rate": {"type": "number"},
                                    "explanation": {"type": "string"}
                                },
                                "required": ["attorney_id", "action", "explanation"]
                            }
                        },
                        "overall_assessment": {"type": "string"}
                    },
                    "required": ["recommendations", "overall_assessment"]
                }
            }
        ]
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Make the chat completion request
        response = self.chat_completion(
            messages=messages,
            functions=functions,
            function_call={"name": "provide_rate_recommendation"},
            temperature=0.3,  # Lower temperature for more consistent recommendations
            model=self.get_model_by_type(OpenAIModelType.RECOMMENDATION)
        )
        
        # Process the response
        try:
            function_call = response.get("choices", [{}])[0].get("message", {}).get("function_call", {})
            if function_call and function_call.get("name") == "provide_rate_recommendation":
                recommendation_data = json.loads(function_call.get("arguments", "{}"))
                return {
                    "recommendations": recommendation_data.get("recommendations", []),
                    "overall_assessment": recommendation_data.get("overall_assessment", ""),
                    "model_used": response.get("model", "")
                }
            else:
                raise ValueError("Failed to get structured recommendation from AI response")
        except Exception as e:
            logger.error(f"Error processing rate recommendation response: {str(e)}")
            raise ValueError(f"Failed to process rate recommendations: {str(e)}")
    
    def process_management_recommendations(
        self,
        user_context: Dict,
        pending_items: Dict,
        historical_actions: Optional[Dict] = None
    ) -> Dict:
        """
        Provides AI recommendations for workflow prioritization and next steps.
        
        Args:
            user_context: Information about the user and their role
            pending_items: List of items requiring action
            historical_actions: Previous actions taken by the user (optional)
            
        Returns:
            Prioritized actions and recommendations
        """
        # Construct a detailed system prompt
        system_prompt = """
        You are an AI assistant in the Justice Bid Rate Negotiation System specialized in process management.
        You help users prioritize their workflow and provide recommendations for next actions.
        
        Based on the user's role, pending items, and historical actions, you will:
        1. Prioritize pending items in order of importance and urgency
        2. Recommend specific actions for each item
        3. Provide a brief explanation of your prioritization logic
        
        Your recommendations should be practical, actionable, and designed to streamline the user's workflow.
        """
        
        # Build the user prompt with the context
        user_prompt = f"""
        Please help me prioritize my workflow and recommend next actions:
        
        USER CONTEXT:
        {json.dumps(user_context, indent=2)}
        
        PENDING ITEMS:
        {json.dumps(pending_items, indent=2)}
        """
        
        # Add historical actions if available
        if historical_actions:
            user_prompt += f"\nHISTORICAL ACTIONS:\n{json.dumps(historical_actions, indent=2)}"
        
        # Define the expected response format using function calling
        functions = [
            {
                "name": "provide_workflow_recommendations",
                "description": "Provide prioritized workflow recommendations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prioritized_items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "item_id": {"type": "string"},
                                    "priority": {"type": "integer", "minimum": 1},
                                    "recommended_action": {"type": "string"},
                                    "reason": {"type": "string"}
                                },
                                "required": ["item_id", "priority", "recommended_action", "reason"]
                            }
                        },
                        "overall_recommendations": {"type": "string"}
                    },
                    "required": ["prioritized_items", "overall_recommendations"]
                }
            }
        ]
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Make the chat completion request
        response = self.chat_completion(
            messages=messages,
            functions=functions,
            function_call={"name": "provide_workflow_recommendations"},
            temperature=0.3,
            model=self.get_model_by_type(OpenAIModelType.RECOMMENDATION)
        )
        
        # Process the response
        try:
            function_call = response.get("choices", [{}])[0].get("message", {}).get("function_call", {})
            if function_call and function_call.get("name") == "provide_workflow_recommendations":
                recommendation_data = json.loads(function_call.get("arguments", "{}"))
                return {
                    "prioritized_items": recommendation_data.get("prioritized_items", []),
                    "overall_recommendations": recommendation_data.get("overall_recommendations", ""),
                    "model_used": response.get("model", "")
                }
            else:
                raise ValueError("Failed to get structured workflow recommendations from AI response")
        except Exception as e:
            logger.error(f"Error processing workflow recommendations response: {str(e)}")
            raise ValueError(f"Failed to process workflow recommendations: {str(e)}")
    
    def analyze_document(
        self,
        document_text: str,
        document_type: str,
        analysis_parameters: Optional[Dict] = None
    ) -> Dict:
        """
        Analyzes legal documents including Outside Counsel Guidelines.
        
        Args:
            document_text: The text content of the document
            document_type: Type of document (e.g., "OCG", "Agreement", "Rate Card")
            analysis_parameters: Additional parameters for analysis (optional)
            
        Returns:
            Document analysis results
        """
        # Validate document length
        if len(document_text) > 100000:
            logger.warning(f"Document length ({len(document_text)} chars) exceeds recommended limit. Analysis may be incomplete.")
            document_text = document_text[:100000] + "... [TRUNCATED]"
        
        # Prepare the system prompt based on document type
        system_prompt = """
        You are an expert legal document analyzer in the Justice Bid Rate Negotiation System.
        You analyze legal documents and extract key information, focusing on elements relevant
        to rate negotiations and outside counsel arrangements.
        """
        
        analysis_instructions = ""
        if document_type.upper() == "OCG":
            analysis_instructions = """
            For Outside Counsel Guidelines, focus on:
            1. Identifying negotiable sections and alternatives
            2. Rate-related provisions and requirements
            3. Billing restrictions and requirements
            4. Staffing limitations and approval requirements
            5. Alternative fee arrangements
            """
        elif document_type.upper() == "AGREEMENT":
            analysis_instructions = """
            For Agreements, focus on:
            1. Rate-related terms and conditions
            2. Term length and renewal provisions
            3. Termination clauses
            4. Billing and payment terms
            5. Scope of services
            """
        elif document_type.upper() == "RATE_CARD":
            analysis_instructions = """
            For Rate Cards, focus on:
            1. Standard rates by timekeeper level
            2. Discount structures
            3. Volume commitments
            4. Alternative fee options
            5. Rate increase provisions
            """
        else:
            analysis_instructions = """
            Analyze the document for any content relevant to legal services rates,
            billing practices, attorney staffing, or client requirements.
            """
        
        system_prompt += analysis_instructions
        
        # Prepare user prompt
        user_prompt = f"""
        Please analyze the following {document_type} document:
        
        {document_text}
        """
        
        if analysis_parameters:
            user_prompt += f"\n\nAnalysis parameters:\n{json.dumps(analysis_parameters, indent=2)}"
        
        # Define response format for structure
        functions = [
            {
                "name": "analyze_legal_document",
                "description": f"Analyze a {document_type} document and extract key information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key_sections": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "content": {"type": "string"},
                                    "importance": {"type": "string", "enum": ["high", "medium", "low"]},
                                    "negotiable": {"type": "boolean"},
                                    "alternatives": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "text": {"type": "string"},
                                                "impact": {"type": "string"}
                                            }
                                        }
                                    }
                                },
                                "required": ["title", "content", "importance"]
                            }
                        },
                        "rate_related_provisions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "description": {"type": "string"},
                                    "impact": {"type": "string"}
                                }
                            }
                        },
                        "summary": {"type": "string"},
                        "recommendations": {"type": "string"}
                    },
                    "required": ["key_sections", "summary"]
                }
            }
        ]
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Make the chat completion request
        response = self.chat_completion(
            messages=messages,
            functions=functions,
            function_call={"name": "analyze_legal_document"},
            temperature=0.3,
            max_tokens=4000,  # Higher token limit for document analysis
            model=self.get_model_by_type(OpenAIModelType.DOCUMENT_ANALYSIS)
        )
        
        # Process the response
        try:
            function_call = response.get("choices", [{}])[0].get("message", {}).get("function_call", {})
            if function_call and function_call.get("name") == "analyze_legal_document":
                analysis_data = json.loads(function_call.get("arguments", "{}"))
                return {
                    "document_type": document_type,
                    "key_sections": analysis_data.get("key_sections", []),
                    "rate_related_provisions": analysis_data.get("rate_related_provisions", []),
                    "summary": analysis_data.get("summary", ""),
                    "recommendations": analysis_data.get("recommendations", ""),
                    "model_used": response.get("model", "")
                }
            else:
                raise ValueError("Failed to get structured document analysis from AI response")
        except Exception as e:
            logger.error(f"Error processing document analysis response: {str(e)}")
            raise ValueError(f"Failed to analyze document: {str(e)}")
    
    def process_chat_interaction(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        user_context: Dict,
        system_context: Optional[Dict] = None,
        available_functions: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Processes a user chat message with appropriate context.
        
        Args:
            user_message: The user's message text
            conversation_history: Previous messages in the conversation
            user_context: Information about the user and their permissions
            system_context: Additional system context (optional)
            available_functions: Functions the AI can call (optional)
            
        Returns:
            AI response with potential function calls
        """
        # Sanitize user message for security
        sanitized_message = sanitize_input(user_message)
        
        # Prepare system prompt with appropriate context
        system_prompt = """
        You are Justice Bid, an AI assistant specialized in legal rate negotiations and analytics.
        You help legal professionals with rate negotiations, analytics, and workflow management.
        
        You have access to data about rates, negotiations, law firms, and clients, but you must
        respect user permissions when accessing or discussing this data.
        
        Be helpful, concise, and focused on providing actionable insights and recommendations.
        """
        
        # Add role-specific instructions based on user context
        role = user_context.get("role", "").lower()
        if "client" in role or "corporate" in role:
            system_prompt += """
            This user represents a client/corporate legal department. Focus on:
            - Analyzing rate proposals from law firms
            - Recommending approval/rejection/counter-proposal actions
            - Providing context about market rates and peer comparisons
            - Highlighting potential cost impacts
            """
        elif "firm" in role or "attorney" in role:
            system_prompt += """
            This user represents a law firm. Focus on:
            - Advising on competitive and reasonable rate proposals
            - Explaining client rate rules and guidelines
            - Suggesting justifications for rate increases
            - Recommending negotiation strategies
            """
        
        # Add system context if provided
        if system_context:
            system_prompt += f"\n\nAdditional system context:\n{json.dumps(system_context, indent=2)}"
        
        # Prepare messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add the current message
        messages.append({"role": "user", "content": sanitized_message})
        
        # Make the chat completion request
        response_params = {
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
            "model": self.get_model_by_type(OpenAIModelType.CHAT)
        }
        
        # Add functions if provided
        if available_functions:
            response_params["functions"] = available_functions
        
        response = self.chat_completion(**response_params)
        
        # Process the response
        try:
            message = response.get("choices", [{}])[0].get("message", {})
            response_data = {
                "content": message.get("content", ""),
                "role": "assistant",
                "created_at": datetime.now().isoformat(),
                "model_used": response.get("model", "")
            }
            
            # Include function call if present
            if "function_call" in message:
                response_data["function_call"] = message["function_call"]
            
            return response_data
        except Exception as e:
            logger.error(f"Error processing chat interaction response: {str(e)}")
            raise ValueError(f"Failed to process chat interaction: {str(e)}")
    
    def validate_connection(self) -> bool:
        """
        Validates the connection to OpenAI API.
        
        Returns:
            True if connection is valid, False otherwise
        """
        if not self._initialized or not self._client:
            return False
        
        try:
            # Make a minimal API call to test the connection
            self.get_available_models(refresh=True)
            return True
        except Exception as e:
            logger.error(f"Connection validation failed: {str(e)}")
            self._initialized = False
            return False
    
    def get_available_models(self, refresh: bool = False) -> List[Dict]:
        """
        Retrieves a list of available models from OpenAI.
        
        Args:
            refresh: Whether to refresh the cached models list
            
        Returns:
            List of available model information
            
        Raises:
            ValueError: If the client is not initialized or the request fails
        """
        if not self._initialized or not self._client:
            raise ValueError("OpenAI client not initialized. Check API key and connection.")
        
        # Return cached models if available and refresh not requested
        if self._models_cache and not refresh:
            return self._models_cache
        
        try:
            response = self._client.models.list()
            
            # Convert to list of dictionaries
            models = []
            for model in response.data:
                if hasattr(model, "model_dump"):
                    models.append(model.model_dump())
                else:
                    # Handle different response formats
                    models.append(json.loads(json.dumps(model, default=lambda o: o.__dict__)))
            
            # Cache the results
            self._models_cache = models
            return models
            
        except Exception as e:
            logger.error(f"Error fetching available models: {str(e)}")
            raise ValueError(f"Failed to retrieve available models: {str(e)}")
    
    def get_model_by_type(self, model_type: OpenAIModelType) -> str:
        """
        Gets the appropriate model name for a given model type.
        
        Args:
            model_type: The type of model needed
            
        Returns:
            Model name to use for the specified type
        """
        # Get configuration for models
        config = self._config or {}
        openai_config = config.get("openai", {})
        
        # Map model types to config keys and defaults
        model_mapping = {
            OpenAIModelType.CHAT: ("chat_model", DEFAULT_CHAT_MODEL),
            OpenAIModelType.EMBEDDING: ("embedding_model", DEFAULT_EMBEDDING_MODEL),
            OpenAIModelType.COMPLETION: ("completion_model", DEFAULT_CHAT_MODEL),
            OpenAIModelType.RECOMMENDATION: ("recommendation_model", DEFAULT_CHAT_MODEL),
            OpenAIModelType.DOCUMENT_ANALYSIS: ("document_analysis_model", DEFAULT_CHAT_MODEL)
        }
        
        config_key, default_model = model_mapping.get(model_type, (None, DEFAULT_CHAT_MODEL))
        
        # Return the configured model or default
        if config_key:
            return openai_config.get(config_key, default_model)
        return default_model