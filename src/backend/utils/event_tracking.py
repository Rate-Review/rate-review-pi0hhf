"""
Utility module for tracking events across the Justice Bid system, providing a consistent 
interface for recording user actions, system events, and audit information.

This module implements a flexible event tracking system that supports both logging and
event-driven architecture patterns. It provides structured event recording with contextual
enrichment, allowing for comprehensive audit trails and event sourcing.
"""

import logging
import datetime
import threading
import json
import uuid
from typing import Dict, Any, Optional, Callable, List

try:
    from flask import request, has_request_context
except ImportError:
    # Flask might not be available in all contexts
    has_request_context = lambda: False

# Internal imports
from src.backend.config import settings
from src.backend.utils.mongodb_client import get_mongodb_client

# Initialize logger
logger = logging.getLogger('event_tracking')

# Thread-local storage for context information
context_data = threading.local()

# List of registered event handlers
event_handlers = []


def set_context(context: Dict[str, Any]) -> None:
    """
    Sets thread-local context information that will be attached to all events recorded in this thread.
    
    Args:
        context (Dict[str, Any]): Context dictionary to set
    """
    if not hasattr(context_data, 'data'):
        context_data.data = {}
    
    # Update context with new values
    context_data.data.update(context)


def get_context() -> Dict[str, Any]:
    """
    Retrieves the current thread-local context information.
    
    Returns:
        Dict[str, Any]: The current context dictionary or an empty dictionary if no context is set
    """
    if not hasattr(context_data, 'data'):
        context_data.data = {}
    
    return context_data.data


def clear_context() -> None:
    """
    Clears the thread-local context information.
    """
    if hasattr(context_data, 'data'):
        context_data.data = {}


def register_handler(handler: Callable[[Dict[str, Any]], None]) -> None:
    """
    Registers a handler function that will be called for each event.
    
    Args:
        handler (Callable[[Dict[str, Any]], None]): Function that accepts an event dictionary
    """
    if handler not in event_handlers:
        event_handlers.append(handler)
        logger.debug(f"Registered event handler: {handler.__name__}")


def unregister_handler(handler: Callable[[Dict[str, Any]], None]) -> bool:
    """
    Removes a previously registered handler function.
    
    Args:
        handler (Callable[[Dict[str, Any]], None]): Handler function to remove
        
    Returns:
        bool: True if the handler was removed, False if it was not found
    """
    if handler in event_handlers:
        event_handlers.remove(handler)
        logger.debug(f"Unregistered event handler: {handler.__name__}")
        return True
    return False


def _enrich_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adds standard contextual information to an event.
    
    Args:
        event (Dict[str, Any]): Event dictionary to enrich
        
    Returns:
        Dict[str, Any]: The enriched event dictionary
    """
    # Add timestamp
    event['timestamp'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # Add unique event ID
    event['event_id'] = str(uuid.uuid4())
    
    # Add thread-local context data
    context = get_context()
    if context:
        event['context'] = context
    
    # Add Flask request information if available
    if has_request_context():
        event['request'] = {
            'path': request.path,
            'method': request.method,
            'remote_addr': request.remote_addr,
        }
        
        # Add request ID if available
        if hasattr(request, 'id'):
            event['request']['id'] = request.id
        
        # Add user ID and organization ID from Flask session if available
        if hasattr(request, 'user_id'):
            event.setdefault('user_id', request.user_id)
        if hasattr(request, 'organization_id'):
            event.setdefault('organization_id', request.organization_id)
    
    # Add environment information if available in settings
    if hasattr(settings, 'ENVIRONMENT'):
        event['environment'] = settings.ENVIRONMENT
    elif hasattr(settings, 'FLASK_ENV'):
        event['environment'] = settings.FLASK_ENV
    else:
        event['environment'] = 'development'
        
    if hasattr(settings, 'PROJECT_NAME'):
        event['service_name'] = settings.PROJECT_NAME
    
    return event


def _dispatch_event(event: Dict[str, Any]) -> None:
    """
    Dispatches an event to all registered handlers.
    
    Args:
        event (Dict[str, Any]): Event dictionary to dispatch
    """
    for handler in event_handlers:
        try:
            handler(event)
        except Exception as e:
            logger.error(f"Error in event handler {handler.__name__}: {str(e)}")


def track_event(
    event_type: str,
    data: Dict[str, Any],
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    user_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Records an event with the provided information.
    
    Args:
        event_type (str): Type of event being recorded
        data (Dict[str, Any]): Event data
        category (Optional[str]): Event category
        subcategory (Optional[str]): Event subcategory
        user_id (Optional[str]): ID of user associated with the event
        organization_id (Optional[str]): ID of organization associated with the event
        metadata (Optional[Dict[str, Any]]): Additional metadata
        
    Returns:
        Dict[str, Any]: The recorded event dictionary
    """
    # Create base event dictionary
    event = {
        'event_type': event_type,
        'data': data
    }
    
    # Add optional fields if provided
    if category:
        event['category'] = category
    if subcategory:
        event['subcategory'] = subcategory
    if user_id:
        event['user_id'] = user_id
    if organization_id:
        event['organization_id'] = organization_id
    if metadata:
        event['metadata'] = metadata
        
    # Enrich the event with contextual information
    event = _enrich_event(event)
    
    # Log the event
    log_level = logging.INFO
    if category == 'error':
        log_level = logging.ERROR
    elif category == 'auth' and event_type in ['login_failed', 'authentication_failed', 'unauthorized_access']:
        log_level = logging.WARNING
        
    logger.log(
        log_level,
        f"Event: {event_type}",
        extra={'additional_data': event}
    )
    
    # Dispatch the event to registered handlers
    _dispatch_event(event)
    
    return event


def track_user_event(
    event_type: str,
    user_id: str,
    organization_id: str,
    data: Dict[str, Any],
    subcategory: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Records a user-related event with standard categorization.
    
    Args:
        event_type (str): Type of event being recorded
        user_id (str): ID of user associated with the event
        organization_id (str): ID of organization associated with the event
        data (Dict[str, Any]): Event data
        subcategory (Optional[str]): Event subcategory
        metadata (Optional[Dict[str, Any]]): Additional metadata
        
    Returns:
        Dict[str, Any]: The recorded event dictionary
    """
    return track_event(
        event_type=event_type,
        category='user',
        subcategory=subcategory,
        user_id=user_id,
        organization_id=organization_id,
        data=data,
        metadata=metadata
    )


def track_system_event(
    event_type: str,
    data: Dict[str, Any],
    subcategory: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Records a system-related event with standard categorization.
    
    Args:
        event_type (str): Type of event being recorded
        data (Dict[str, Any]): Event data
        subcategory (Optional[str]): Event subcategory
        metadata (Optional[Dict[str, Any]]): Additional metadata
        
    Returns:
        Dict[str, Any]: The recorded event dictionary
    """
    return track_event(
        event_type=event_type,
        category='system',
        subcategory=subcategory,
        data=data,
        metadata=metadata
    )


def track_auth_event(
    event_type: str,
    data: Dict[str, Any],
    user_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Records an authentication-related event with standard categorization.
    
    Args:
        event_type (str): Type of event being recorded
        data (Dict[str, Any]): Event data
        user_id (Optional[str]): ID of user associated with the event
        organization_id (Optional[str]): ID of organization associated with the event
        metadata (Optional[Dict[str, Any]]): Additional metadata
        
    Returns:
        Dict[str, Any]: The recorded event dictionary
    """
    return track_event(
        event_type=event_type,
        category='auth',
        user_id=user_id,
        organization_id=organization_id,
        data=data,
        metadata=metadata
    )


def track_rate_event(
    event_type: str,
    user_id: str,
    organization_id: str,
    data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Records a rate-related event with standard categorization.
    
    Args:
        event_type (str): Type of event being recorded (e.g., 'rate_created', 'rate_updated', 'rate_approved')
        user_id (str): ID of user associated with the event
        organization_id (str): ID of organization associated with the event
        data (Dict[str, Any]): Event data
        metadata (Optional[Dict[str, Any]]): Additional metadata
        
    Returns:
        Dict[str, Any]: The recorded event dictionary
    """
    return track_event(
        event_type=event_type,
        category='rate',
        subcategory=event_type.split('_')[0] if '_' in event_type else None,
        user_id=user_id,
        organization_id=organization_id,
        data=data,
        metadata=metadata
    )


def track_negotiation_event(
    event_type: str,
    user_id: str,
    organization_id: str,
    negotiation_id: str,
    data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Records a negotiation-related event with standard categorization.
    
    Args:
        event_type (str): Type of event being recorded
        user_id (str): ID of user associated with the event
        organization_id (str): ID of organization associated with the event
        negotiation_id (str): ID of the negotiation
        data (Dict[str, Any]): Event data
        metadata (Optional[Dict[str, Any]]): Additional metadata
        
    Returns:
        Dict[str, Any]: The recorded event dictionary
    """
    # Add negotiation_id to data
    data = data.copy()
    data['negotiation_id'] = negotiation_id
    
    return track_event(
        event_type=event_type,
        category='negotiation',
        subcategory=event_type.split('_')[0] if '_' in event_type else None,
        user_id=user_id,
        organization_id=organization_id,
        data=data,
        metadata=metadata
    )


def track_api_event(
    endpoint: str,
    method: str,
    data: Dict[str, Any],
    user_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Records an API-related event with standard categorization.
    
    Args:
        endpoint (str): API endpoint path
        method (str): HTTP method (GET, POST, PUT, DELETE, etc.)
        data (Dict[str, Any]): Event data
        user_id (Optional[str]): ID of user associated with the event
        organization_id (Optional[str]): ID of organization associated with the event
        metadata (Optional[Dict[str, Any]]): Additional metadata
        
    Returns:
        Dict[str, Any]: The recorded event dictionary
    """
    # Add endpoint and method to data
    data = data.copy()
    data['endpoint'] = endpoint
    data['method'] = method
    
    return track_event(
        event_type='api_request',
        category='api',
        user_id=user_id,
        organization_id=organization_id,
        data=data,
        metadata=metadata
    )


def setup_mongodb_handler(collection_name: Optional[str] = None) -> Callable:
    """
    Sets up an event handler that stores events in MongoDB.
    
    Args:
        collection_name (Optional[str]): Name of MongoDB collection to store events in.
                                          Defaults to 'events' if not specified.
    
    Returns:
        Callable: The registered handler function
    """
    if not collection_name:
        collection_name = 'events'
    
    def mongodb_handler(event: Dict[str, Any]) -> None:
        try:
            from src.backend.utils.mongodb_client import get_collection
            collection = get_collection(collection_name)
            
            # Insert the event
            collection.insert_one(event)
        except Exception as e:
            logger.error(f"Failed to store event in MongoDB: {str(e)}")
    
    # Register the handler
    register_handler(mongodb_handler)
    
    return mongodb_handler


def setup_datadog_handler() -> Callable:
    """
    Sets up an event handler that sends events to Datadog.
    
    Returns:
        Callable: The registered handler function
    """
    try:
        import datadog
        from datadog import api
        
        # Initialize Datadog if not already done
        if not datadog.initialized:
            datadog_api_key = None
            datadog_app_key = None
            
            if hasattr(settings, 'DATADOG_API_KEY'):
                datadog_api_key = settings.DATADOG_API_KEY
            
            if hasattr(settings, 'DATADOG_APP_KEY'):
                datadog_app_key = settings.DATADOG_APP_KEY
            
            if not datadog_api_key:
                logger.warning("Datadog API key not configured. Datadog event handler not initialized.")
                raise ValueError("Datadog API key not configured")
            
            datadog.initialize(
                api_key=datadog_api_key,
                app_key=datadog_app_key
            )
        
        def datadog_handler(event: Dict[str, Any]) -> None:
            try:
                # Create event title
                event_type = event.get('event_type', 'unknown')
                category = event.get('category', '')
                
                title = f"{category.upper()}: {event_type}" if category else event_type
                
                # Create event text with relevant information
                text = f"Event ID: {event.get('event_id', 'N/A')}\n"
                
                if 'user_id' in event:
                    text += f"User: {event['user_id']}\n"
                
                if 'organization_id' in event:
                    text += f"Organization: {event['organization_id']}\n"
                
                if 'data' in event:
                    text += f"Data: {json.dumps(event['data'], indent=2)}\n"
                
                # Prepare tags
                tags = [
                    f"event_type:{event_type}",
                    f"environment:{event.get('environment', 'unknown')}"
                ]
                
                if 'category' in event:
                    tags.append(f"category:{event['category']}")
                
                if 'subcategory' in event:
                    tags.append(f"subcategory:{event['subcategory']}")
                
                # Determine alert type
                alert_type = 'info'
                if event.get('category') == 'error':
                    alert_type = 'error'
                elif event.get('category') == 'auth' and event_type in ['login_failed', 'authentication_failed', 'unauthorized_access']:
                    alert_type = 'warning'
                
                # Send event to Datadog
                api.Event.create(
                    title=title,
                    text=text,
                    tags=tags,
                    alert_type=alert_type,
                    source_type_name='justice_bid'
                )
                
            except Exception as e:
                logger.error(f"Failed to send event to Datadog: {str(e)}")
        
        # Register the handler
        register_handler(datadog_handler)
        
        return datadog_handler
    
    except (ImportError, ValueError) as e:
        logger.warning(f"Datadog event handler not configured: {str(e)}")
        
        # Return a dummy handler for consistency
        def dummy_handler(event: Dict[str, Any]) -> None:
            pass
        
        return dummy_handler


class EventContext:
    """
    Context manager for setting and clearing event context.
    
    Example:
        with EventContext({"request_id": "123", "session_id": "abc"}):
            # All events tracked in this block will include the context
            track_event(...)
    """
    
    def __init__(self, context: Dict[str, Any]):
        """
        Creates a new EventContext with the provided context dictionary.
        
        Args:
            context (Dict[str, Any]): Context information to set
        """
        self.context = context
        self.previous_context = None
    
    def __enter__(self) -> 'EventContext':
        """
        Sets the context when entering the context manager.
        
        Returns:
            EventContext: Returns self for use in with statement
        """
        # Save the existing context
        self.previous_context = get_context().copy()
        
        # Set the new context
        set_context(self.context)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Restores the previous context when exiting the context manager.
        
        Args:
            exc_type: Exception type if an exception was raised in the with block
            exc_val: Exception value if an exception was raised in the with block
            exc_tb: Exception traceback if an exception was raised in the with block
            
        Returns:
            None
        """
        # Restore the previous context
        clear_context()
        if self.previous_context:
            set_context(self.previous_context)