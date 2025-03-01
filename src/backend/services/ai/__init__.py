"""
Initialization file for the AI services module, importing and exposing the core AI functionality used throughout the Justice Bid application. Implements the AI-first approach with chat capabilities, rate recommendations, process management, and personalization features.
"""

import logging  # Provides logging capabilities

from .chat import AIChat  # Handles natural language interactions with users
from .recommendations import RateRecommender  # Provides AI-driven rate recommendations
from .process_management import ProcessManager  # Manages AI-driven process recommendations and prioritization
from .personalization import PersonalizationEngine  # Handles user-specific AI personalization
from .models import AIModel  # Configures and manages AI models used by the system
from .prompts import PromptTemplate  # Manages templates for AI interactions
from .langchain_setup import setup_langchain  # Initializes the LangChain framework for AI operations

# Initialize logger
logger = logging.getLogger(__name__)

__all__ = [
    "AIChat",  # Expose chat functionality to the application
    "RateRecommender",  # Expose rate recommendation functionality
    "ProcessManager",  # Expose process management functionality
    "PersonalizationEngine",  # Expose personalization functionality
    "AIModel",  # Expose AI model configuration
    "PromptTemplate",  # Expose prompt template management
    "setup_langchain",  # Expose LangChain setup function
]