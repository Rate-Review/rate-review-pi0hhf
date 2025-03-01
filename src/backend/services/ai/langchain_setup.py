"""
Sets up and configures the LangChain environment for AI functionality across the Justice Bid system.

This module provides centralized configuration for language models, chains, memory components,
and supports switching between different AI environments (Justice Bid's or client's own).
"""

import os
from typing import Dict, Any, Optional, List, Union

from langchain.cache import LLMCache
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain.memory import (
    ConversationBufferMemory, 
    ConversationBufferWindowMemory,
    RedisBufferWindowMemory
)
from langchain.chains import LLMChain, ConversationChain, RetrievalQA

from ...api.core.config import get_settings
from ...utils.constants import AI_PROVIDERS, MODEL_TYPES
from ...utils.redis_client import get_redis_client
from ...utils.logging import logger
from ...integrations.openai.client import OpenAIClient

# Default configuration values
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1024
DEFAULT_MODEL = "gpt-4"
DEFAULT_MEMORY_KEY = "chat_history"
DEFAULT_HUMAN_PREFIX = "Human"
DEFAULT_AI_PREFIX = "AI"

def setup_langchain_cache() -> None:
    """
    Sets up caching for LLM calls to reduce API costs and improve performance.
    
    Uses Redis as the cache backend with appropriate TTL settings.
    """
    try:
        # Get Redis client for caching
        redis_client = get_redis_client()
        
        # Configure LangChain to use Redis for caching
        LLMCache.configure(
            redis_client=redis_client,
            ttl=3600  # Cache responses for 1 hour
        )
        
        logger.info("LangChain cache configured with Redis successfully")
    except Exception as e:
        logger.error(f"Failed to set up LangChain cache: {str(e)}")
        logger.info("Continuing without LLM caching")


def get_llm_provider(config: Dict) -> str:
    """
    Determines which LLM provider to use based on configuration settings.
    
    Args:
        config: Configuration dictionary containing AI settings
        
    Returns:
        The LLM provider to use (e.g., 'openai', 'azure', 'client')
    """
    # Check if client has specified their own AI environment
    client_ai_env = config.get("CLIENT_AI_ENVIRONMENT", False)
    
    if client_ai_env:
        # Use client's specified AI provider
        return config.get("CLIENT_AI_PROVIDER", AI_PROVIDERS.OPENAI)
    else:
        # Use Justice Bid's default AI provider
        return config.get("DEFAULT_AI_PROVIDER", AI_PROVIDERS.OPENAI)


def get_llm(
    model_name: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    model_kwargs: Dict = None
) -> Any:  # Returns BaseChatModel but using Any for flexibility
    """
    Gets a configured LLM instance based on specified parameters and settings.
    
    Args:
        model_name: Name of the model to use
        temperature: Temperature setting for response generation
        max_tokens: Maximum tokens to generate in responses
        model_kwargs: Additional model parameters
        
    Returns:
        A configured language model instance
    """
    if model_kwargs is None:
        model_kwargs = {}
        
    # Get system configuration
    config = get_settings()
    
    # Determine which provider to use
    provider = get_llm_provider(config)
    
    # Initialize appropriate model based on provider
    if provider == AI_PROVIDERS.OPENAI:
        llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=config.OPENAI_API_KEY,
            **model_kwargs
        )
    elif provider == AI_PROVIDERS.AZURE:
        llm = AzureChatOpenAI(
            deployment_name=config.get("AZURE_OPENAI_DEPLOYMENT", model_name),
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=config.get("AZURE_OPENAI_API_KEY"),
            openai_api_base=config.get("AZURE_OPENAI_API_BASE"),
            openai_api_version=config.get("AZURE_OPENAI_API_VERSION", "2023-05-15"),
            **model_kwargs
        )
    elif provider == AI_PROVIDERS.CLIENT:
        # For client-specific AI environments
        client_provider = config.get("CLIENT_AI_PROVIDER", AI_PROVIDERS.OPENAI)
        client_api_key = config.get("CLIENT_AI_API_KEY")
        client_api_base = config.get("CLIENT_AI_API_BASE")
        
        if client_provider == AI_PROVIDERS.OPENAI:
            llm = ChatOpenAI(
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                openai_api_key=client_api_key,
                openai_api_base=client_api_base,
                **model_kwargs
            )
        elif client_provider == AI_PROVIDERS.AZURE:
            llm = AzureChatOpenAI(
                deployment_name=config.get("CLIENT_AZURE_DEPLOYMENT", model_name),
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                openai_api_key=client_api_key,
                openai_api_base=client_api_base,
                openai_api_version=config.get("CLIENT_AZURE_API_VERSION", "2023-05-15"),
                **model_kwargs
            )
        else:
            # Fallback to OpenAI
            logger.warning(f"Unsupported client AI provider: {client_provider}. Falling back to OpenAI.")
            llm = ChatOpenAI(
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                **model_kwargs
            )
    else:
        # Default to OpenAI if provider is not recognized
        logger.warning(f"Unrecognized AI provider: {provider}. Using OpenAI as default.")
        llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            **model_kwargs
        )
    
    return llm


def create_memory(
    memory_type: str = "buffer",
    k: int = 5,
    memory_key: str = DEFAULT_MEMORY_KEY,
    human_prefix: str = DEFAULT_HUMAN_PREFIX,
    ai_prefix: str = DEFAULT_AI_PREFIX
) -> Any:  # Returns BaseChatMemory but using Any for flexibility
    """
    Creates an appropriate memory component for conversation history.
    
    Args:
        memory_type: Type of memory to use (buffer, window, redis)
        k: Window size for conversation turns to remember
        memory_key: Key to store memory under
        human_prefix: Prefix for human messages
        ai_prefix: Prefix for AI messages
        
    Returns:
        A configured memory component
    """
    # Configure memory parameters
    memory_params = {
        "memory_key": memory_key,
        "human_prefix": human_prefix,
        "ai_prefix": ai_prefix
    }
    
    # Create the appropriate memory component
    if memory_type == "buffer":
        memory = ConversationBufferMemory(**memory_params)
    elif memory_type == "window":
        memory = ConversationBufferWindowMemory(k=k, **memory_params)
    elif memory_type == "redis":
        # Get Redis client
        redis_client = get_redis_client()
        memory = RedisBufferWindowMemory(
            redis_client=redis_client,
            session_prefix="justicebid:",
            session_id="default",
            k=k,
            **memory_params
        )
    else:
        # Default to buffer memory
        logger.warning(f"Unrecognized memory type: {memory_type}. Using buffer memory as default.")
        memory = ConversationBufferMemory(**memory_params)
    
    return memory


def create_chain(
    chain_type: str,
    llm: Any,  # BaseChatModel
    prompt: Any = None,  # BasePromptTemplate
    memory: Any = None,  # BaseChatMemory
    chain_kwargs: Dict = None
) -> Any:  # Returns Chain but using Any for flexibility
    """
    Creates a LangChain chain for a specific purpose.
    
    Args:
        chain_type: Type of chain to create (llm, conversation, qa)
        llm: Language model to use
        prompt: Prompt template to use
        memory: Memory component to use
        chain_kwargs: Additional chain parameters
        
    Returns:
        A configured LangChain chain
    """
    if chain_kwargs is None:
        chain_kwargs = {}
        
    # Build parameters based on what's provided
    params = {"llm": llm, **chain_kwargs}
    
    if prompt is not None:
        params["prompt"] = prompt
        
    if memory is not None:
        params["memory"] = memory
    
    # Create the appropriate chain type
    if chain_type == "llm":
        chain = LLMChain(**params)
    elif chain_type == "conversation":
        # Ensure memory is provided for conversation chain
        if "memory" not in params:
            params["memory"] = create_memory()
        chain = ConversationChain(**params)
    elif chain_type == "qa":
        if "retriever" not in params:
            raise ValueError("Retriever is required for RetrievalQA chain")
        chain = RetrievalQA(**params)
    else:
        # Default to LLMChain
        logger.warning(f"Unrecognized chain type: {chain_type}. Using LLMChain as default.")
        chain = LLMChain(**params)
    
    return chain


def get_chat_chain(
    model_name: str = DEFAULT_MODEL,
    prompt: Any = None,  # BasePromptTemplate
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    memory_k: int = 5
) -> ConversationChain:
    """
    Creates a conversation chain optimized for chat interactions.
    
    Args:
        model_name: Name of the model to use
        prompt: Prompt template for conversation
        temperature: Temperature for response generation
        max_tokens: Maximum tokens to generate
        memory_k: Number of conversation turns to remember
        
    Returns:
        A chat-optimized conversation chain
    """
    # Get the language model
    llm = get_llm(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    # Create memory component
    memory = create_memory(memory_type="window", k=memory_k)
    
    # Create chain params
    chain_params = {"memory": memory}
    if prompt is not None:
        chain_params["prompt"] = prompt
        
    # Create and return conversation chain
    return create_chain("conversation", llm, chain_kwargs=chain_params)


def get_recommendation_chain(
    model_name: str = DEFAULT_MODEL,
    prompt: Any = None,  # BasePromptTemplate
    temperature: float = 0.3,  # Lower temperature for consistent recommendations
    max_tokens: int = DEFAULT_MAX_TOKENS
) -> LLMChain:
    """
    Creates a chain optimized for generating rate recommendations.
    
    Args:
        model_name: Name of the model to use
        prompt: Prompt template for recommendations
        temperature: Temperature for response generation
        max_tokens: Maximum tokens to generate
        
    Returns:
        A chain optimized for generating recommendations
    """
    # Get the language model with lower temperature for consistency
    llm = get_llm(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    # Create chain params
    chain_params = {}
    if prompt is not None:
        chain_params["prompt"] = prompt
        
    # Create and return LLM chain
    return create_chain("llm", llm, chain_kwargs=chain_params)


class LangChainManager:
    """
    Manages LangChain components and provides a unified interface for AI functionality.
    
    This class caches language models, memory components, and chains to avoid
    redundant creation and provides methods to access different AI capabilities.
    """
    
    def __init__(self):
        """
        Initializes the LangChain manager with default configuration.
        """
        # Initialize internal storage for components
        self._llms = {}
        self._chains = {}
        self._memories = {}
        self._config = get_settings()
        
        # Set up LangChain cache
        setup_langchain_cache()
        
        # Initialize default LLM
        self.get_llm()
    
    def get_llm(
        self,
        model_name: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        model_kwargs: Dict = None
    ) -> Any:  # BaseChatModel
        """
        Gets or creates an LLM with specified configuration.
        
        Args:
            model_name: Model name to use
            temperature: Temperature for response generation
            max_tokens: Maximum tokens to generate
            model_kwargs: Additional model parameters
            
        Returns:
            A configured LLM instance
        """
        if model_kwargs is None:
            model_kwargs = {}
            
        # Generate key for LLM based on parameters
        key = f"{model_name}_{temperature}_{max_tokens}_{str(model_kwargs)}"
        
        # Check if LLM already exists in _llms dictionary
        if key in self._llms:
            return self._llms[key]
        
        # If not, create new LLM using get_llm function
        llm = get_llm(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            model_kwargs=model_kwargs
        )
        
        # Store LLM in _llms dictionary
        self._llms[key] = llm
        return llm
    
    def get_memory(
        self,
        memory_type: str = "buffer",
        k: int = 5,
        memory_key: str = DEFAULT_MEMORY_KEY,
        session_id: str = "default"
    ) -> Any:  # BaseChatMemory
        """
        Gets or creates a memory component with specified configuration.
        
        Args:
            memory_type: Type of memory to use
            k: Window size for conversation memory
            memory_key: Key to store memory under
            session_id: Unique identifier for the session
            
        Returns:
            A configured memory component
        """
        # Generate key for memory based on parameters and session_id
        key = f"{memory_type}_{k}_{memory_key}_{session_id}"
        
        # Check if memory already exists in _memories dictionary
        if key in self._memories:
            return self._memories[key]
        
        # If not, create new memory using create_memory function
        memory = create_memory(
            memory_type=memory_type,
            k=k,
            memory_key=memory_key
        )
        
        # Special handling for Redis memory with session ID
        if memory_type == "redis" and hasattr(memory, "session_id"):
            memory.session_id = session_id
        
        # Store memory in _memories dictionary
        self._memories[key] = memory
        return memory
    
    def get_chain(
        self,
        chain_type: str,
        model_name: str = DEFAULT_MODEL,
        prompt: Any = None,  # BasePromptTemplate
        memory_type: str = "buffer",
        session_id: str = "default",
        chain_kwargs: Dict = None
    ) -> Any:  # Chain
        """
        Gets or creates a chain with specified configuration.
        
        Args:
            chain_type: Type of chain to create
            model_name: Model name to use
            prompt: Prompt template for the chain
            memory_type: Type of memory to use
            session_id: Unique identifier for the session
            chain_kwargs: Additional chain parameters
            
        Returns:
            A configured chain instance
        """
        if chain_kwargs is None:
            chain_kwargs = {}
            
        # Generate key for chain based on parameters and session_id
        prompt_key = str(prompt) if prompt else "no_prompt"
        key = f"{chain_type}_{model_name}_{prompt_key}_{memory_type}_{session_id}_{str(chain_kwargs)}"
        
        # Check if chain already exists in _chains dictionary
        if key in self._chains:
            return self._chains[key]
        
        # If not, get or create LLM
        llm = self.get_llm(model_name=model_name)
        
        # Get or create memory
        memory = None
        if chain_type == "conversation" or "memory" in chain_kwargs:
            memory = self.get_memory(
                memory_type=memory_type,
                session_id=session_id
            )
        
        # Create new chain using create_chain function
        chain = create_chain(
            chain_type=chain_type,
            llm=llm,
            prompt=prompt,
            memory=memory,
            chain_kwargs=chain_kwargs
        )
        
        # Store chain in _chains dictionary
        self._chains[key] = chain
        return chain
    
    def get_chat_chain(
        self,
        prompt: Any = None,  # BasePromptTemplate
        session_id: str = "default",
        model_name: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE
    ) -> ConversationChain:
        """
        Gets or creates a conversation chain for chat.
        
        Args:
            prompt: Prompt template for conversation
            session_id: Unique identifier for the chat session
            model_name: Model name to use
            temperature: Temperature for response generation
            
        Returns:
            A conversation chain instance
        """
        # Use get_chain with type='conversation'
        return self.get_chain(
            chain_type="conversation",
            model_name=model_name,
            prompt=prompt,
            memory_type="window",
            session_id=session_id,
            chain_kwargs={"temperature": temperature}
        )
    
    def get_recommendation_chain(
        self,
        prompt: Any = None,  # BasePromptTemplate
        model_name: str = DEFAULT_MODEL
    ) -> LLMChain:
        """
        Gets or creates a chain for generating recommendations.
        
        Args:
            prompt: Prompt template for recommendations
            model_name: Model name to use
            
        Returns:
            A recommendation chain instance
        """
        # Use get_chain with type='llm' and appropriate settings
        return self.get_chain(
            chain_type="llm",
            model_name=model_name,
            prompt=prompt,
            chain_kwargs={"temperature": 0.3}  # Lower temperature for consistent recommendations
        )
    
    def clear_memory(self, session_id: str) -> None:
        """
        Clears conversation memory for a specific session.
        
        Args:
            session_id: The session identifier to clear memory for
        """
        # Find all memory instances associated with session_id
        for key, memory in list(self._memories.items()):
            if session_id in key:
                try:
                    # Clear each memory instance
                    memory.clear()
                    logger.debug(f"Cleared memory for session {session_id}")
                except Exception as e:
                    logger.error(f"Error clearing memory for session {session_id}: {str(e)}")