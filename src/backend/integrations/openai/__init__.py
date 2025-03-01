"""
OpenAI integration module for the Justice Bid Rate Negotiation System.

This module provides a centralized interface for AI-powered features including
chat interface, rate recommendations, document analysis, and process management through
OpenAI's large language models. It handles API communication, configuration, and
domain-specific AI functionality for legal rate negotiation tasks.

Version: 0.1.0
"""

import logging  # standard library

# Import core components from client module
from .client import (
    OpenAIClient,
    count_tokens,
    estimate_chat_tokens,
    OpenAIModelType
)

# Configure logger for the module
logger = logging.getLogger(__name__)

# Define version for tracking OpenAI API compatibility
VERSION = '0.1.0'

# Export public interface
__all__ = [
    'OpenAIClient',
    'count_tokens',
    'estimate_chat_tokens',
    'OpenAIModelType'
]