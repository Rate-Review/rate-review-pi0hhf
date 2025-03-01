"""
AI model configurations and interfaces for the Justice Bid Rate Negotiation System.

This module defines the AI model configurations, model selection logic, and 
interfaces to different AI providers. It acts as the foundation for all AI 
services in the Justice Bid system, enabling a flexible approach to using 
different AI models for various capabilities.

The module provides:
- Enumeration of supported AI providers and models
- Adapter classes for different AI providers
- A model registry for configuration management
- Factory functions for model instantiation
- Utility functions for model capability detection
"""

import enum
from typing import Dict, List, Any, Optional, Union
import os
import json
import abc
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI, ChatAnthropic
from langchain.llms import BaseLLM
from langchain.base_language import BaseLanguageModel, BaseChatModel

from ...api.core.config import get_config
from ...utils.constants import ErrorCode
from ...utils.logging import logger

# Default parameters for AI models
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1024

# Define enums for AI providers, models, and use cases
class AIProvider(enum.Enum):
    """Enumeration of supported AI providers."""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    CLIENT = "client"  # For client's own AI environment

class AIModel(enum.Enum):
    """Enumeration of supported AI models."""
    GPT4 = "gpt4"
    GPT35 = "gpt35"
    CLAUDE_OPUS = "claude_opus"
    CLAUDE_SONNET = "claude_sonnet"
    CLIENT_MODEL = "client_model"  # Placeholder for client's model

class AIUseCase(enum.Enum):
    """Enumeration of AI use cases in the system."""
    CHAT = "chat"  # General chat interface
    RATE_RECOMMENDATION = "rate_recommendation"  # Rate negotiation recommendations
    DOCUMENT_ANALYSIS = "document_analysis"  # OCG and document analysis
    PROCESS_MANAGEMENT = "process_management"  # Workflow and process optimization

class ModelCapability(enum.Enum):
    """Enumeration of model capabilities for feature detection."""
    FUNCTION_CALLING = "function_calling"  # Support for function/tool calling
    CODE_INTERPRETATION = "code_interpretation"  # Ability to interpret and execute code
    IMAGE_UNDERSTANDING = "image_understanding"  # Image processing capabilities
    LONG_CONTEXT = "long_context"  # Support for extended context windows
    HIGH_ACCURACY = "high_accuracy"  # Higher accuracy in complex reasoning tasks

# Model capabilities by model
MODEL_CAPABILITIES = {
    AIModel.GPT4.value: {
        "max_tokens": 8192,
        "context_window": 8192,
        "features": [
            ModelCapability.FUNCTION_CALLING.value,
            ModelCapability.CODE_INTERPRETATION.value,
            ModelCapability.HIGH_ACCURACY.value
        ],
        "suitable_for": [
            AIUseCase.CHAT.value,
            AIUseCase.RATE_RECOMMENDATION.value,
            AIUseCase.DOCUMENT_ANALYSIS.value,
            AIUseCase.PROCESS_MANAGEMENT.value
        ]
    },
    AIModel.GPT35.value: {
        "max_tokens": 4096,
        "context_window": 4096,
        "features": [
            ModelCapability.FUNCTION_CALLING.value
        ],
        "suitable_for": [
            AIUseCase.CHAT.value,
            AIUseCase.PROCESS_MANAGEMENT.value
        ]
    },
    AIModel.CLAUDE_OPUS.value: {
        "max_tokens": 4096,
        "context_window": 100000,
        "features": [
            ModelCapability.HIGH_ACCURACY.value,
            ModelCapability.LONG_CONTEXT.value
        ],
        "suitable_for": [
            AIUseCase.CHAT.value,
            AIUseCase.RATE_RECOMMENDATION.value,
            AIUseCase.DOCUMENT_ANALYSIS.value,
            AIUseCase.PROCESS_MANAGEMENT.value
        ]
    },
    AIModel.CLAUDE_SONNET.value: {
        "max_tokens": 4096,
        "context_window": 100000,
        "features": [
            ModelCapability.LONG_CONTEXT.value
        ],
        "suitable_for": [
            AIUseCase.CHAT.value,
            AIUseCase.DOCUMENT_ANALYSIS.value
        ]
    },
    # Default capabilities for unknown models
    "default": {
        "max_tokens": 2048,
        "context_window": 4096,
        "features": [],
        "suitable_for": [AIUseCase.CHAT.value]
    }
}

class BaseModelAdapter(abc.ABC):
    """
    Abstract base class for model adapters.
    
    This class defines the interface that all model adapters must implement,
    providing a consistent way to initialize and retrieve model instances
    regardless of the underlying AI provider.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the base model adapter.
        
        Args:
            config: Configuration dictionary for the model adapter
        """
        self._config = config
        self.validate_config()
    
    @abc.abstractmethod
    def get_model_instance(self) -> BaseChatModel:
        """
        Get a model instance.
        
        Returns:
            A LangChain model instance
        
        This abstract method must be implemented by concrete adapter classes
        to return the appropriate model instance for the specific AI provider.
        """
        pass
    
    def validate_config(self) -> bool:
        """
        Validate the adapter configuration.
        
        Returns:
            True if configuration is valid, raises ValueError otherwise
        
        This method performs basic validation common to all adapters.
        Subclasses should override this method to add provider-specific validation,
        but should call the parent implementation first.
        """
        # Basic validation logic for all adapters
        if not isinstance(self._config, dict):
            raise ValueError(f"Configuration must be a dictionary, got {type(self._config)}")
        
        # Check for common required fields
        for field in ["temperature"]:
            if field not in self._config:
                self._config[field] = DEFAULT_TEMPERATURE
        
        return True

class OpenAIModelAdapter(BaseModelAdapter):
    """
    Adapter for OpenAI models.
    
    This adapter handles configuration and initialization of OpenAI models,
    including GPT-4 and GPT-3.5.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the OpenAI model adapter.
        
        Args:
            config: Configuration dictionary for the OpenAI adapter
        """
        super().__init__(config)
    
    def get_model_instance(self) -> BaseChatModel:
        """
        Get an OpenAI model instance.
        
        Returns:
            A LangChain ChatOpenAI instance
        """
        model_name = self._config.get("model_name", "gpt-4")
        temperature = self._config.get("temperature", DEFAULT_TEMPERATURE)
        max_tokens = self._config.get("max_tokens", DEFAULT_MAX_TOKENS)
        
        # Map logical model name to OpenAI model name if needed
        if isinstance(model_name, AIModel):
            model_name = self.map_model_name(model_name)
        
        # Create and return ChatOpenAI instance
        return ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=self._config.get("api_key"),
            verbose=self._config.get("verbose", False)
        )
    
    def validate_config(self) -> bool:
        """
        Validate OpenAI-specific configuration.
        
        Returns:
            True if configuration is valid, raises ValueError otherwise
        """
        # Call parent validation
        super().validate_config()
        
        # Check OpenAI-specific required parameters
        api_key = self._config.get("api_key")
        if not api_key:
            # Try to get from environment
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OpenAI API key is required. Provide it in the config or set the OPENAI_API_KEY environment variable."
                )
            self._config["api_key"] = api_key
        
        return True
    
    def map_model_name(self, model_name: Union[str, AIModel]) -> str:
        """
        Map logical model names to OpenAI model identifiers.
        
        Args:
            model_name: Logical model name (can be string or AIModel enum)
            
        Returns:
            OpenAI model identifier
        """
        if isinstance(model_name, str):
            # If it's already a string, convert it to enum if it matches
            try:
                model_name = AIModel(model_name)
            except ValueError:
                # If it's not a valid enum value, return as is
                return model_name
        
        # Map enum values to OpenAI model identifiers
        if model_name == AIModel.GPT4:
            return "gpt-4"
        elif model_name == AIModel.GPT35:
            return "gpt-3.5-turbo"
        else:
            # For other values, just return the value
            return model_name.value

class AzureOpenAIModelAdapter(BaseModelAdapter):
    """
    Adapter for Azure OpenAI models.
    
    This adapter handles configuration and initialization of Azure OpenAI models,
    managing the specific requirements of Azure deployments.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the Azure OpenAI model adapter.
        
        Args:
            config: Configuration dictionary for the Azure OpenAI adapter
        """
        super().__init__(config)
    
    def get_model_instance(self) -> BaseChatModel:
        """
        Get an Azure OpenAI model instance.
        
        Returns:
            A LangChain AzureChatOpenAI instance
        """
        deployment_name = self._config.get("deployment_name")
        model_name = self._config.get("model_name")
        
        # If no deployment name specified, try to map it
        if not deployment_name and model_name:
            deployment_name = self.map_model_name(model_name)
        
        temperature = self._config.get("temperature", DEFAULT_TEMPERATURE)
        max_tokens = self._config.get("max_tokens", DEFAULT_MAX_TOKENS)
        api_version = self._config.get("api_version", "2023-05-15")
        
        # Create and return AzureChatOpenAI instance
        return AzureChatOpenAI(
            deployment_name=deployment_name,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            api_version=api_version,
            api_key=self._config.get("api_key"),
            azure_endpoint=self._config.get("azure_endpoint"),
            verbose=self._config.get("verbose", False)
        )
    
    def validate_config(self) -> bool:
        """
        Validate Azure OpenAI-specific configuration.
        
        Returns:
            True if configuration is valid, raises ValueError otherwise
        """
        # Call parent validation
        super().validate_config()
        
        # Check Azure-specific required parameters
        api_key = self._config.get("api_key")
        if not api_key:
            # Try to get from environment
            api_key = os.environ.get("AZURE_OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "Azure OpenAI API key is required. Provide it in the config or set the AZURE_OPENAI_API_KEY environment variable."
                )
            self._config["api_key"] = api_key
        
        azure_endpoint = self._config.get("azure_endpoint")
        if not azure_endpoint:
            # Try to get from environment
            azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
            if not azure_endpoint:
                raise ValueError(
                    "Azure OpenAI endpoint is required. Provide it in the config or set the AZURE_OPENAI_ENDPOINT environment variable."
                )
            self._config["azure_endpoint"] = azure_endpoint
        
        # Either deployment_name or model_name must be provided
        if not self._config.get("deployment_name") and not self._config.get("model_name"):
            raise ValueError("Either deployment_name or model_name must be provided for Azure OpenAI")
        
        return True
    
    def map_model_name(self, model_name: Union[str, AIModel]) -> str:
        """
        Map logical model names to Azure deployment names.
        
        Args:
            model_name: Logical model name (can be string or AIModel enum)
            
        Returns:
            Azure deployment name
        """
        # If the config already has a deployment name, use that
        if self._config.get("deployment_name"):
            return self._config.get("deployment_name")
        
        if isinstance(model_name, str):
            # If it's already a string, convert it to enum if it matches
            try:
                model_name = AIModel(model_name)
            except ValueError:
                # If it's not a valid enum value, return as is
                return model_name
        
        # Map enum values to Azure deployment names
        # Note: These are examples and would typically be configured per customer
        if model_name == AIModel.GPT4:
            return "gpt-4"
        elif model_name == AIModel.GPT35:
            return "gpt-35-turbo"
        else:
            # For other values, just return the value
            return model_name.value

class AnthropicModelAdapter(BaseModelAdapter):
    """
    Adapter for Anthropic Claude models.
    
    This adapter handles configuration and initialization of Anthropic's Claude models,
    including Opus and Sonnet variants.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the Anthropic model adapter.
        
        Args:
            config: Configuration dictionary for the Anthropic adapter
        """
        super().__init__(config)
    
    def get_model_instance(self) -> BaseChatModel:
        """
        Get an Anthropic model instance.
        
        Returns:
            A LangChain ChatAnthropic instance
        """
        model_name = self._config.get("model_name")
        
        # Map logical model name to Anthropic model name if needed
        if isinstance(model_name, AIModel):
            model_name = self.map_model_name(model_name)
        
        temperature = self._config.get("temperature", DEFAULT_TEMPERATURE)
        max_tokens = self._config.get("max_tokens", DEFAULT_MAX_TOKENS)
        
        # Create and return ChatAnthropic instance
        return ChatAnthropic(
            model=model_name,
            temperature=temperature,
            max_tokens_to_sample=max_tokens,
            anthropic_api_key=self._config.get("api_key"),
            verbose=self._config.get("verbose", False)
        )
    
    def validate_config(self) -> bool:
        """
        Validate Anthropic-specific configuration.
        
        Returns:
            True if configuration is valid, raises ValueError otherwise
        """
        # Call parent validation
        super().validate_config()
        
        # Check Anthropic-specific required parameters
        api_key = self._config.get("api_key")
        if not api_key:
            # Try to get from environment
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError(
                    "Anthropic API key is required. Provide it in the config or set the ANTHROPIC_API_KEY environment variable."
                )
            self._config["api_key"] = api_key
        
        # Model name is required
        if not self._config.get("model_name"):
            raise ValueError("model_name must be provided for Anthropic models")
        
        return True
    
    def map_model_name(self, model_name: Union[str, AIModel]) -> str:
        """
        Map logical model names to Anthropic model identifiers.
        
        Args:
            model_name: Logical model name (can be string or AIModel enum)
            
        Returns:
            Anthropic model identifier
        """
        if isinstance(model_name, str):
            # If it's already a string, convert it to enum if it matches
            try:
                model_name = AIModel(model_name)
            except ValueError:
                # If it's not a valid enum value, return as is
                return model_name
        
        # Map enum values to Anthropic model identifiers
        if model_name == AIModel.CLAUDE_OPUS:
            return "claude-3-opus-20240229"
        elif model_name == AIModel.CLAUDE_SONNET:
            return "claude-3-sonnet-20240229"
        else:
            # For other values, just return the value
            return model_name.value

class ClientModelAdapter(BaseModelAdapter):
    """
    Adapter for client-specific AI models.
    
    This adapter provides flexibility to integrate with a client's own AI environment,
    supporting different integration methods based on the client's infrastructure.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the client model adapter.
        
        Args:
            config: Configuration dictionary for the client model adapter
        """
        super().__init__(config)
    
    def get_model_instance(self) -> BaseChatModel:
        """
        Get a client model instance.
        
        Returns:
            A LangChain model instance for client AI
        
        This method handles various integration methods based on the client's
        AI environment configuration.
        """
        # The implementation depends on the specific integration method
        # for the client's AI environment.
        integration_type = self._config.get("integration_type", "api")
        
        if integration_type == "api":
            # Initialize appropriate adapter based on client's API
            provider = self._config.get("provider_type", "openai")
            
            if provider == "openai":
                # Use OpenAI adapter with client-specific settings
                adapter = OpenAIModelAdapter(self._config)
                return adapter.get_model_instance()
            elif provider == "azure_openai":
                # Use Azure OpenAI adapter with client-specific settings
                adapter = AzureOpenAIModelAdapter(self._config)
                return adapter.get_model_instance()
            elif provider == "anthropic":
                # Use Anthropic adapter with client-specific settings
                adapter = AnthropicModelAdapter(self._config)
                return adapter.get_model_instance()
            else:
                raise ValueError(f"Unsupported client provider type: {provider}")
        
        elif integration_type == "custom":
            # Here would be custom integration with client's AI service
            # This is highly specific to the client and would be implemented
            # on a case-by-case basis.
            raise NotImplementedError(
                "Custom client AI integration requires specific implementation"
            )
        else:
            raise ValueError(f"Unsupported integration type: {integration_type}")
    
    def validate_config(self) -> bool:
        """
        Validate client-specific configuration.
        
        Returns:
            True if configuration is valid, raises ValueError otherwise
        """
        # Call parent validation
        super().validate_config()
        
        # Check client-specific required parameters
        if not self._config.get("integration_type"):
            raise ValueError("integration_type must be provided for client model")
        
        integration_type = self._config.get("integration_type")
        
        if integration_type == "api":
            if not self._config.get("provider_type"):
                raise ValueError("provider_type must be provided for API integration")
        elif integration_type == "custom":
            # Custom integration would have its own validation requirements
            pass
        else:
            raise ValueError(f"Unsupported integration type: {integration_type}")
        
        return True

class ModelRegistry:
    """
    Registry for AI model configurations and instances.
    
    This class serves as a central registry for managing AI model configurations,
    default settings, and model instances. It handles caching of model instances
    for performance optimization and provides access to appropriate models based
    on use case and organization requirements.
    """
    
    def __init__(self) -> None:
        """Initialize the model registry."""
        # Default model configurations
        self._default_configs = {}
        
        # Organization-specific configurations
        self._org_configs = {}
        
        # Default use case mappings
        self._use_case_defaults = {}
        
        # Organization-specific use case mappings
        self._org_use_case_defaults = {}
        
        # Cache of model instances
        self._instances = {}
        
        # Load configurations from settings
        self.load_config_from_settings()
    
    def register_model_config(self, provider: str, model_name: str, config: Dict[str, Any]) -> None:
        """
        Register a model configuration.
        
        Args:
            provider: AI provider identifier
            model_name: Model name
            config: Configuration dictionary
        """
        # Validate the configuration
        validate_model_config(provider, model_name, config)
        
        # Generate a key for the configuration
        key = f"{provider}:{model_name}"
        
        # Store the configuration
        self._default_configs[key] = config
        
        logger.info(f"Registered model configuration for {key}")
    
    def register_organization_config(self, organization_id: str, provider: str, 
                                    model_name: str, config: Dict[str, Any]) -> None:
        """
        Register an organization-specific model configuration.
        
        Args:
            organization_id: Organization identifier
            provider: AI provider identifier
            model_name: Model name
            config: Configuration dictionary
        """
        # Validate the configuration
        validate_model_config(provider, model_name, config)
        
        # Generate a key for the configuration
        org_key = f"{organization_id}:{provider}:{model_name}"
        
        # Store the configuration
        self._org_configs[org_key] = config
        
        logger.info(f"Registered organization-specific model configuration for {org_key}")
    
    def set_use_case_default(self, use_case: str, provider: str, model_name: str) -> None:
        """
        Set the default model for a use case.
        
        Args:
            use_case: Use case identifier
            provider: AI provider identifier
            model_name: Model name
        """
        # Validate use case
        try:
            use_case_enum = AIUseCase(use_case)
        except ValueError:
            raise ValueError(f"Invalid use case: {use_case}")
        
        # Generate a key for the provider and model
        key = f"{provider}:{model_name}"
        
        # Check that the provider and model are registered
        if key not in self._default_configs:
            raise ValueError(f"Model configuration not found for {key}")
        
        # Store the mapping
        self._use_case_defaults[use_case] = key
        
        logger.info(f"Set default model for use case {use_case} to {key}")
    
    def set_organization_use_case_default(self, organization_id: str, use_case: str, 
                                         provider: str, model_name: str) -> None:
        """
        Set organization-specific default model for a use case.
        
        Args:
            organization_id: Organization identifier
            use_case: Use case identifier
            provider: AI provider identifier
            model_name: Model name
        """
        # Validate use case
        try:
            use_case_enum = AIUseCase(use_case)
        except ValueError:
            raise ValueError(f"Invalid use case: {use_case}")
        
        # Generate keys
        org_model_key = f"{organization_id}:{provider}:{model_name}"
        org_use_case_key = f"{organization_id}:{use_case}"
        
        # Check that the provider and model are registered for the organization
        if org_model_key not in self._org_configs:
            # Check if there's a default configuration
            default_key = f"{provider}:{model_name}"
            if default_key not in self._default_configs:
                raise ValueError(f"Model configuration not found for {org_model_key}")
        
        # Store the mapping
        if not hasattr(self, "_org_use_case_defaults"):
            self._org_use_case_defaults = {}
        
        self._org_use_case_defaults[org_use_case_key] = f"{provider}:{model_name}"
        
        logger.info(f"Set organization-specific default model for use case {use_case} to {provider}:{model_name}")
    
    def get_model(self, provider: str, model_name: str, config: Dict[str, Any]) -> BaseChatModel:
        """
        Get a model instance with specified configuration.
        
        Args:
            provider: AI provider identifier
            model_name: Model name
            config: Configuration dictionary
            
        Returns:
            A configured model instance
        """
        # Generate a cache key
        cache_key = f"{provider}:{model_name}:{hash(json.dumps(config, sort_keys=True))}"
        
        # Check if model instance exists in cache
        if cache_key in self._instances:
            logger.debug(f"Using cached model instance for {cache_key}")
            return self._instances[cache_key]
        
        # Create appropriate adapter based on provider
        try:
            provider_enum = AIProvider(provider)
        except ValueError:
            raise ValueError(f"Unsupported AI provider: {provider}")
        
        if provider_enum == AIProvider.OPENAI:
            adapter = OpenAIModelAdapter(config)
        elif provider_enum == AIProvider.AZURE_OPENAI:
            adapter = AzureOpenAIModelAdapter(config)
        elif provider_enum == AIProvider.ANTHROPIC:
            adapter = AnthropicModelAdapter(config)
        elif provider_enum == AIProvider.CLIENT:
            adapter = ClientModelAdapter(config)
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
        
        # Get model instance from adapter
        try:
            model_instance = adapter.get_model_instance()
        except Exception as e:
            logger.error(f"Error creating model instance: {str(e)}", extra={
                "additional_data": {"provider": provider, "model_name": model_name}
            })
            raise
        
        # Cache the model instance
        self._instances[cache_key] = model_instance
        
        return model_instance
    
    def get_default_model_for_use_case(self, use_case: str, organization_id: Optional[str] = None) -> BaseChatModel:
        """
        Get the default model for a specific use case.
        
        Args:
            use_case: Use case identifier
            organization_id: Optional organization identifier for organization-specific defaults
            
        Returns:
            The default model for the use case
        """
        # Validate use case
        try:
            use_case_enum = AIUseCase(use_case)
        except ValueError:
            raise ValueError(f"Invalid use case: {use_case}")
        
        provider_model_key = None
        
        # Check for organization-specific default
        if organization_id and hasattr(self, "_org_use_case_defaults"):
            org_use_case_key = f"{organization_id}:{use_case}"
            if org_use_case_key in self._org_use_case_defaults:
                provider_model_key = self._org_use_case_defaults[org_use_case_key]
        
        # If no organization-specific default, use system-wide default
        if not provider_model_key and use_case in self._use_case_defaults:
            provider_model_key = self._use_case_defaults[use_case]
        
        # If no default configured, use fallback defaults
        if not provider_model_key:
            logger.warning(f"No default model configured for use case {use_case}, using fallback")
            
            # Fallback based on use case
            if use_case == AIUseCase.CHAT.value:
                provider_model_key = f"{AIProvider.OPENAI.value}:{AIModel.GPT4.value}"
            elif use_case == AIUseCase.RATE_RECOMMENDATION.value:
                provider_model_key = f"{AIProvider.OPENAI.value}:{AIModel.GPT4.value}"
            elif use_case == AIUseCase.DOCUMENT_ANALYSIS.value:
                provider_model_key = f"{AIProvider.ANTHROPIC.value}:{AIModel.CLAUDE_OPUS.value}"
            elif use_case == AIUseCase.PROCESS_MANAGEMENT.value:
                provider_model_key = f"{AIProvider.OPENAI.value}:{AIModel.GPT4.value}"
            else:
                provider_model_key = f"{AIProvider.OPENAI.value}:{AIModel.GPT4.value}"
        
        # Split the key into provider and model name
        provider, model_name = provider_model_key.split(":")
        
        # Get configuration
        config = None
        
        # Check for organization-specific configuration
        if organization_id:
            org_model_key = f"{organization_id}:{provider}:{model_name}"
            if org_model_key in self._org_configs:
                config = self._org_configs[org_model_key]
        
        # If no organization-specific configuration, use default
        if not config:
            default_key = f"{provider}:{model_name}"
            if default_key in self._default_configs:
                config = self._default_configs[default_key]
            else:
                # Create a basic configuration
                config = {
                    "model_name": model_name,
                    "temperature": DEFAULT_TEMPERATURE,
                    "max_tokens": DEFAULT_MAX_TOKENS
                }
        
        # Get and return the model instance
        return self.get_model(provider, model_name, config)
    
    def clear_cache(self) -> None:
        """Clear the model instance cache."""
        self._instances = {}
        logger.info("Cleared model instance cache")
    
    def load_config_from_settings(self) -> None:
        """Load model configurations from application settings."""
        # Get application configuration
        config = get_config()
        
        # Extract AI model settings
        # This would typically come from the application configuration
        # For now, we'll set up some default configurations
        
        # OpenAI configuration
        openai_config = {
            "model_name": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2048,
            "api_key": getattr(config, "OPENAI_API_KEY", None)
        }
        self.register_model_config(AIProvider.OPENAI.value, AIModel.GPT4.value, openai_config)
        
        # GPT-3.5 configuration
        gpt35_config = {
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 2048,
            "api_key": getattr(config, "OPENAI_API_KEY", None)
        }
        self.register_model_config(AIProvider.OPENAI.value, AIModel.GPT35.value, gpt35_config)
        
        # Anthropic configuration
        if hasattr(config, "ANTHROPIC_API_KEY") and config.ANTHROPIC_API_KEY:
            anthropic_config = {
                "model_name": "claude-3-opus-20240229",
                "temperature": 0.7,
                "max_tokens": 4096,
                "api_key": config.ANTHROPIC_API_KEY
            }
            self.register_model_config(AIProvider.ANTHROPIC.value, AIModel.CLAUDE_OPUS.value, anthropic_config)
            
            anthropic_sonnet_config = {
                "model_name": "claude-3-sonnet-20240229",
                "temperature": 0.7,
                "max_tokens": 4096,
                "api_key": config.ANTHROPIC_API_KEY
            }
            self.register_model_config(AIProvider.ANTHROPIC.value, AIModel.CLAUDE_SONNET.value, anthropic_sonnet_config)
        
        # Set up default use case mappings
        self.set_use_case_default(AIUseCase.CHAT.value, AIProvider.OPENAI.value, AIModel.GPT4.value)
        self.set_use_case_default(AIUseCase.RATE_RECOMMENDATION.value, AIProvider.OPENAI.value, AIModel.GPT4.value)
        self.set_use_case_default(AIUseCase.DOCUMENT_ANALYSIS.value, AIProvider.OPENAI.value, AIModel.GPT4.value)
        self.set_use_case_default(AIUseCase.PROCESS_MANAGEMENT.value, AIProvider.OPENAI.value, AIModel.GPT4.value)
        
        # If Anthropic is configured, use it for document analysis
        if hasattr(config, "ANTHROPIC_API_KEY") and config.ANTHROPIC_API_KEY:
            self.set_use_case_default(AIUseCase.DOCUMENT_ANALYSIS.value, AIProvider.ANTHROPIC.value, AIModel.CLAUDE_OPUS.value)


# Create a singleton instance of the model registry
MODEL_REGISTRY = ModelRegistry()

def get_model_instance(model_name: str, provider: str, config: Dict[str, Any]) -> BaseChatModel:
    """
    Factory function that returns an instance of the specified AI model with the given configuration.
    
    This function provides a convenient interface for getting model instances
    without directly interacting with the model registry.
    
    Args:
        model_name: The name of the model to instantiate
        provider: The AI provider to use
        config: Configuration dictionary for the model
        
    Returns:
        A LangChain model instance configured according to the specified parameters
    """
    # Validate the model name and provider
    try:
        if isinstance(model_name, str) and not any(model_name == m.value for m in AIModel):
            # If string doesn't match any enum value, check if it's a direct model identifier
            logger.debug(f"Using direct model identifier: {model_name}")
        elif isinstance(model_name, AIModel):
            # If it's already an enum, convert to value
            model_name = model_name.value
    except ValueError:
        # If conversion fails, use as is (might be a custom model identifier)
        pass
    
    try:
        if isinstance(provider, str) and not any(provider == p.value for p in AIProvider):
            raise ValueError(f"Unsupported AI provider: {provider}")
        elif isinstance(provider, AIProvider):
            provider = provider.value
    except ValueError as e:
        logger.error(f"Invalid provider: {str(e)}")
        raise
    
    # Get the model registry singleton instance
    registry = MODEL_REGISTRY
    
    # Get a model instance from the registry
    try:
        return registry.get_model(provider, model_name, config)
    except Exception as e:
        logger.error(f"Error getting model instance: {str(e)}", extra={
            "additional_data": {"provider": provider, "model_name": model_name}
        })
        raise

def get_default_model(use_case: str, organization_id: Optional[str] = None) -> BaseChatModel:
    """
    Returns the default model for a specific use case based on system configuration.
    
    This function provides a convenient interface for getting the default model
    for a specific use case without directly interacting with the model registry.
    
    Args:
        use_case: The use case for which to get the default model
        organization_id: Optional organization ID for organization-specific defaults
        
    Returns:
        The default model instance for the specified use case
    """
    # Get the model registry singleton instance
    registry = MODEL_REGISTRY
    
    # Get the default model for the specified use case and organization
    try:
        return registry.get_default_model_for_use_case(use_case, organization_id)
    except Exception as e:
        logger.error(f"Error getting default model: {str(e)}", extra={
            "additional_data": {"use_case": use_case, "organization_id": organization_id}
        })
        raise

def validate_model_config(provider: str, model_name: str, config: Dict[str, Any]) -> bool:
    """
    Validates that a model configuration contains all required parameters.
    
    Args:
        provider: The AI provider
        model_name: The model name
        config: Configuration dictionary to validate
        
    Returns:
        True if configuration is valid, raises ValueError otherwise
    """
    # Check that provider is a valid AIProvider
    try:
        provider_enum = AIProvider(provider)
    except ValueError:
        raise ValueError(f"Unsupported AI provider: {provider}")
    
    # Check model name
    try:
        if isinstance(model_name, str) and not any(model_name == m.value for m in AIModel):
            # If the string doesn't match any enum value, it might be a direct model identifier
            # We'll allow this but log a warning
            logger.warning(f"Using non-standard model identifier: {model_name}")
        elif isinstance(model_name, AIModel):
            # If it's already an enum, we're good
            pass
    except ValueError:
        # If conversion fails, use as is but log a warning
        logger.warning(f"Using non-standard model identifier: {model_name}")
    
    # Basic config validation
    if not isinstance(config, dict):
        raise ValueError(f"Configuration must be a dictionary, got {type(config)}")
    
    # Provider-specific validation
    if provider_enum == AIProvider.OPENAI:
        # For OpenAI, we need an API key (either in config or environment)
        api_key = config.get("api_key") or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required")
    
    elif provider_enum == AIProvider.AZURE_OPENAI:
        # For Azure OpenAI, we need API key, endpoint, and deployment name
        api_key = config.get("api_key") or os.environ.get("AZURE_OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Azure OpenAI API key is required")
        
        endpoint = config.get("azure_endpoint") or os.environ.get("AZURE_OPENAI_ENDPOINT")
        if not endpoint:
            raise ValueError("Azure OpenAI endpoint is required")
        
        # Either deployment_name or model_name must be provided
        if not config.get("deployment_name") and not config.get("model_name"):
            raise ValueError("Either deployment_name or model_name must be provided for Azure OpenAI")
    
    elif provider_enum == AIProvider.ANTHROPIC:
        # For Anthropic, we need an API key and model name
        api_key = config.get("api_key") or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key is required")
    
    elif provider_enum == AIProvider.CLIENT:
        # For client models, we need to check the integration type
        integration_type = config.get("integration_type")
        if not integration_type:
            raise ValueError("integration_type must be provided for client models")
        
        if integration_type == "api":
            # For API integration, we need a provider type
            if not config.get("provider_type"):
                raise ValueError("provider_type must be provided for API integration")
    
    return True

def get_model_capabilities(model_name: str) -> Dict[str, Any]:
    """
    Returns the capabilities of a specified model.
    
    This function provides information about a model's capabilities,
    such as context length, supported features, and suitable use cases.
    
    Args:
        model_name: The model name to get capabilities for
        
    Returns:
        Dictionary of model capabilities including context length, features, etc.
    """
    # Convert to enum value if it's an enum
    if isinstance(model_name, AIModel):
        model_name = model_name.value
    
    # Look up capabilities
    if model_name in MODEL_CAPABILITIES:
        return MODEL_CAPABILITIES[model_name]
    else:
        # Return default capabilities if model not found
        logger.warning(f"No capabilities defined for model {model_name}, using defaults")
        return MODEL_CAPABILITIES["default"]