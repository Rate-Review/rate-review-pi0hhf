"""
Database package initialization module that configures SQLAlchemy components and exports the key database objects for the Justice Bid Rate Negotiation System. This file serves as the main entry point for database-related imports throughout the application.
"""

# Import Base and BaseModel from .base module
from .base import Base, BaseModel

# Import database session components from .session module
from .session import (
    init_db,
    get_db,
    get_read_db,
    session_scope,
    read_session_scope,
    close_db,
    engine,
    Session
)

# Define __all__ to explicitly specify exported symbols
__all__ = [
    "Base",
    "BaseModel",
    "init_db",
    "get_db", 
    "get_read_db",
    "session_scope",
    "read_session_scope",
    "close_db",
    "engine",
    "Session"
]