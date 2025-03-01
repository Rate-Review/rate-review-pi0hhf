"""
Implements the AI chat service for the Justice Bid Rate Negotiation System. This module provides functionality for processing user chat interactions with proper context management, permission handling, and response generation. It powers the persistent AI chat interface that's available throughout the application.
"""

import uuid
from typing import Optional, Dict, List
import json
from datetime import datetime

from .models import AIUseCase, get_default_model
from .prompts import create_chat_prompt
from .langchain_setup import LangChainManager
from ...integrations.openai.client import OpenAIClient  # version 1.0.0+
from ...utils.logging import logger
from ...services.auth.permissions import PermissionService
from ...db.models.user import User
from ...db.models.organization import Organization
from ...utils.event_tracking import track_event  # Ensure this import is correct

# Constants for default values and session management
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1024
SESSION_EXPIRY_MINUTES = 60
DEFAULT_MEMORY_WINDOW = 10

# Global LangChain manager instance
lang_chain_manager = LangChainManager()


async def chat(
    user: User,
    message: str,
    session_id: str,
    context: Optional[dict] = None
) -> Dict:
    """
    Process a user chat message and generate a response with appropriate context.

    Args:
        user: User object representing the user sending the message
        message: The chat message from the user
        session_id: Unique identifier for the chat session
        context: Optional context data to enrich the prompt

    Returns:
        Chat response containing the AI message and metadata
    """
    logger.info(f"Received chat request from user {user.id} with session ID {session_id}")

    # Validate user has chat permission
    permission_service = PermissionService()
    if not permission_service.check_permission(user, "ai", "use_chat"):
        logger.warning(f"User {user.id} does not have permission to use chat")
        return {"message": "You do not have permission to use this feature.", "metadata": {}}

    # Get or create chat session for the provided session_id
    chat_service = ChatService(lang_chain_manager=lang_chain_manager, openai_client=OpenAIClient(), permission_service=permission_service)
    session = chat_service.get_or_create_session(session_id=session_id, user=user, metadata=context)

    # Build user context based on user information and permissions
    user_context = get_user_context(user, additional_context=context)

    # Build system context with allowed data access scopes
    system_context = get_system_context(user)

    # Retrieve message history from session
    history = session.get_formatted_history(limit=DEFAULT_MEMORY_WINDOW)

    # Process message using ChatService.process_message
    response = chat_service.process_message(session=session, message=message, user=user, user_context=user_context, system_context=system_context)

    # Track chat interaction event
    track_event(
        event_type="chat_interaction",
        category="ai",
        user_id=str(user.id),
        organization_id=str(user.organization_id),
        data={"message": message, "response": response.get("content", "")},
    )

    # Return formatted response with message and metadata
    return response


def get_available_functions(user: User) -> list:
    """
    Get a list of API functions available to the user based on permissions.

    Args:
        user: User object

    Returns:
        List of function definitions available to this user
    """
    available_functions = []

    # Check user permissions for various function categories
    has_rate_permissions = True  # Replace with actual permission check
    has_negotiation_permissions = True  # Replace with actual permission check
    has_analytics_permissions = True  # Replace with actual permission check
    has_admin_permissions = True  # Replace with actual permission check

    # Add rate-related functions if user has rate permissions
    if has_rate_permissions:
        available_functions.extend([
            {"name": "get_rate_data", "description": "Get rate information"},
            {"name": "submit_rate_proposal", "description": "Submit a rate proposal"}
        ])

    # Add negotiation functions if user has negotiation permissions
    if has_negotiation_permissions:
        available_functions.extend([
            {"name": "approve_rate", "description": "Approve a rate"},
            {"name": "reject_rate", "description": "Reject a rate"}
        ])

    # Add analytics functions if user has analytics permissions
    if has_analytics_permissions:
        available_functions.extend([
            {"name": "get_rate_impact", "description": "Get rate impact analysis"},
            {"name": "generate_report", "description": "Generate a report"}
        ])

    # Add organization functions if user has admin permissions
    if has_admin_permissions:
        available_functions.extend([
            {"name": "create_user", "description": "Create a new user"},
            {"name": "update_user", "description": "Update user information"}
        ])

    return available_functions


def get_user_context(user: User, additional_context: Optional[dict] = None) -> Dict:
    """
    Build context information about the user for AI prompts.

    Args:
        user: User object
        additional_context: Optional dictionary with additional context

    Returns:
        User context dictionary for AI prompt
    """
    context = {
        "user_id": str(user.id),
        "user_name": user.name,
        "user_email": user.email,
        "user_role": user.role.value,
        "organization_id": str(user.organization_id),
    }

    # Add organization type (law firm or client)
    org = Organization.query.get(user.organization_id)
    if org:
        context["organization_type"] = org.type.value

    # Add user preferences from user model
    if user.preferences:
        context.update(user.preferences)

    # Add user permissions scope summary
    context["permissions_summary"] = f"User has permissions: {user.permissions}"

    # Merge with additional_context if provided
    if additional_context:
        context.update(additional_context)

    return context


def get_system_context(user: User) -> Dict:
    """
    Build system context information for AI prompts.

    Args:
        user: User object

    Returns:
        System context dictionary for AI prompt
    """
    context = {
        "system_time": datetime.now().isoformat(),
        "system_version": "1.0",
    }

    # Determine data access scopes based on user permissions
    data_access_scopes = []
    if user.has_permission("rates:read"):
        data_access_scopes.append("rates")
    if user.has_permission("negotiations:read"):
        data_access_scopes.append("negotiations")
    context["data_access_scopes"] = ", ".join(data_access_scopes)

    # Add system capabilities based on user permissions
    system_capabilities = []
    if user.has_permission("rates:submit"):
        system_capabilities.append("rate submission")
    if user.has_permission("negotiations:approve"):
        system_capabilities.append("negotiation approval")
    context["system_capabilities"] = ", ".join(system_capabilities)

    return context


def clear_chat_session(session_id: str) -> bool:
    """
    Clear the chat history for a specific session.

    Args:
        session_id: The ID of the session to clear

    Returns:
        True if session was cleared, False if not found
    """
    chat_service = ChatService(lang_chain_manager=lang_chain_manager, openai_client=OpenAIClient(), permission_service=PermissionService())
    return chat_service.clear_session(session_id)


def get_session_history(session_id: str) -> List:
    """
    Get the message history for a specific chat session.

    Args:
        session_id: The ID of the session to retrieve history for

    Returns:
        List of message dictionaries
    """
    chat_service = ChatService(lang_chain_manager=lang_chain_manager, openai_client=OpenAIClient(), permission_service=PermissionService())
    session = chat_service.get_session(session_id)
    if session:
        return session.messages
    else:
        return []


class ChatSession:
    """
    Represents a chat session with message history and metadata.
    """

    def __init__(self, session_id: str, user_id: uuid.UUID, metadata: Optional[dict] = None):
        """
        Initialize a new chat session.

        Args:
            session_id: Unique identifier for the session
            user_id: ID of the user associated with the session
            metadata: Optional metadata for the session
        """
        self.session_id = session_id
        self.user_id = user_id
        self.messages = []
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.metadata = metadata or {}

    def add_message(self, role: str, content: str, metadata: Optional[dict] = None) -> Dict:
        """
        Add a message to the session history.

        Args:
            role: Role of the message sender (user or assistant)
            content: Message content
            metadata: Optional metadata for the message

        Returns:
            The added message
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        if metadata:
            message.update(metadata)
        self.messages.append(message)
        self.last_updated = datetime.now()
        return message

    def get_messages(self, limit: int) -> List:
        """
        Get all messages in the session.

        Args:
            limit: Number of messages to retrieve

        Returns:
            List of message dictionaries, limited by count if specified
        """
        if limit and limit < len(self.messages):
            return self.messages[-limit:]
        else:
            return self.messages

    def get_formatted_history(self, limit: int) -> List:
        """
        Get messages formatted for LangChain.

        Args:
            limit: Number of messages to retrieve

        Returns:
            List of messages formatted for LangChain
        """
        messages = self.get_messages(limit)
        formatted_messages = []
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            formatted_messages.append(f"{role.upper()}: {content}")
        return formatted_messages

    def is_expired(self) -> bool:
        """
        Check if the session has expired.

        Returns:
            True if session has expired, False otherwise
        """
        time_difference = datetime.now() - self.last_updated
        return time_difference.total_seconds() > SESSION_EXPIRY_MINUTES * 60

    def to_dict(self) -> Dict:
        """
        Convert session to dictionary for serialization.

        Returns:
            Dictionary representation of session
        """
        return {
            "session_id": self.session_id,
            "user_id": str(self.user_id),
            "messages": self.messages,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ChatSession':
        """
        Create session from dictionary representation.

        Args:
            data: Dictionary containing session data

        Returns:
            Reconstructed ChatSession object
        """
        session = cls(session_id=data['session_id'], user_id=uuid.UUID(data['user_id']))
        session.messages = data['messages']
        session.created_at = datetime.datetime.fromisoformat(data['created_at'])
        session.last_updated = datetime.datetime.fromisoformat(data['last_updated'])
        session.metadata = data['metadata']
        return session


class ChatService:
    """
    Service for managing chat interactions and sessions.
    """

    def __init__(self, lang_chain_manager: LangChainManager, openai_client: OpenAIClient, permission_service: PermissionService):
        """
        Initialize the chat service.

        Args:
            lang_chain_manager: LangChain manager instance
            openai_client: OpenAI client instance
            permission_service: Permission service instance
        """
        self._chat_sessions = {}
        self._lang_chain_manager = lang_chain_manager
        self._openai_client = openai_client
        self._permission_service = permission_service
        logger.info("ChatService initialized")

    def get_or_create_session(self, session_id: str, user: User, metadata: Optional[dict] = None) -> ChatSession:
        """
        Get existing chat session or create a new one.

        Args:
            session_id: Unique identifier for the session
            user: User object
            metadata: Optional metadata for the session

        Returns:
            Existing or new chat session
        """
        if session_id in self._chat_sessions:
            session = self._chat_sessions[session_id]
            if session.user_id == user.id and not session.is_expired():
                return session
            else:
                logger.warning(f"Existing session {session_id} is invalid or expired, creating a new one")

        # Create new ChatSession
        session = ChatSession(session_id=session_id, user_id=user.id, metadata=metadata)
        self._chat_sessions[session_id] = session
        return session

    def process_message(self, session: ChatSession, message: str, user: User, user_context: Dict, system_context: Dict) -> Dict:
        """
        Process a chat message and generate a response.

        Args:
            session: ChatSession object
            message: The chat message from the user
            user: User object
            user_context: User context dictionary
            system_context: System context dictionary

        Returns:
            Response dictionary with message and metadata
        """
        # Add user message to session history
        session.add_message(role="user", content=message)

        # Get available API functions based on user permissions
        available_functions = get_available_functions(user)

        # Get formatted message history from session
        history = session.get_formatted_history(limit=DEFAULT_MEMORY_WINDOW)

        # Process message using direct OpenAI client or LangChain based on complexity
        if available_functions:
            response = self.process_with_openai(message=message, history=history, user=user, user_context=user_context, system_context=system_context, available_functions=available_functions)
        else:
            response = self.process_with_langchain(message=message, history=history, session_id=session.session_id, user_context=user_context, system_context=system_context)

        # Extract response content from AI response
        response_content = response.get("content", "")

        # Add AI message to session history
        session.add_message(role="assistant", content=response_content, metadata=response.get("metadata"))

        # Format and return response dictionary
        return {"message": response_content, "metadata": response.get("metadata", {})}

    def process_with_langchain(self, message: str, history: List, session_id: str, user_context: Dict, system_context: Dict) -> str:
        """
        Process message using LangChain for complex conversations.

        Args:
            message: The chat message from the user
            history: Formatted message history
            session_id: Unique identifier for the chat session
            user_context: User context dictionary
            system_context: System context dictionary

        Returns:
            AI response text
        """
        # Create chat prompt using create_chat_prompt
        chat_prompt = create_chat_prompt(user_context=user_context, system_context=system_context, message_history=history)

        # Get chat chain from lang_chain_manager with session_id
        chain = self._lang_chain_manager.get_chat_chain(prompt=chat_prompt, session_id=session_id)

        # Run the chain with the message and context
        response = chain.run(message)

        # Extract and return the response text
        return response

    def process_with_openai(self, message: str, history: List, user: User, user_context: Dict, system_context: Dict, available_functions: List) -> Dict:
        """
        Process message directly with OpenAI for function calling support.

        Args:
            message: The chat message from the user
            history: Formatted message history
            user: User object
            user_context: User context dictionary
            system_context: System context dictionary
            available_functions: List of available API functions

        Returns:
            AI response with possible function calls
        """
        # Use OpenAIClient.process_chat_interaction with all parameters
        response = self._openai_client.process_chat_interaction(
            user_message=message,
            conversation_history=history,
            user_context=user_context,
            system_context=system_context,
            available_functions=available_functions
        )

        # Return the processed response dictionary
        return response

    def clear_session(self, session_id: str) -> bool:
        """
        Clear a chat session.

        Args:
            session_id: The ID of the session to clear

        Returns:
            True if session was cleared, False if not found
        """
        # Check if session exists in _chat_sessions
        if session_id in self._chat_sessions:
            # Remove session from _chat_sessions
            del self._chat_sessions[session_id]

            # Clear LangChain memory for this session
            self._lang_chain_manager.clear_memory(session_id)

            logger.info(f"Cleared chat session: {session_id}")
            return True
        else:
            logger.warning(f"Chat session not found: {session_id}")
            return False

    def get_session(self, session_id: str) -> Optional['ChatSession']:
        """
        Get a chat session by ID.

        Args:
            session_id: The ID of the session to retrieve

        Returns:
            Chat session if found, None otherwise
        """
        if session_id in self._chat_sessions:
            return self._chat_sessions[session_id]
        else:
            return None

    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired chat sessions.

        Returns:
            Number of sessions cleared
        """
        cleared_count = 0
        for session_id, session in list(self._chat_sessions.items()):
            if session.is_expired():
                # Remove expired sessions and clear their LangChain memory
                del self._chat_sessions[session_id]
                self._lang_chain_manager.clear_memory(session_id)
                cleared_count += 1
                logger.info(f"Cleared expired chat session: {session_id}")

        return cleared_count

    def check_data_access_permission(self, user: User, resource_type: str, resource_id: uuid.UUID) -> bool:
        """
        Check if user has permission to access specific data.

        Args:
            user: User object
            resource_type: Type of resource being accessed
            resource_id: ID of the resource being accessed

        Returns:
            True if user has access, False otherwise
        """
        # Use permission_service to check resource permission
        return self._permission_service.check_permission(user, resource_type, resource_id)