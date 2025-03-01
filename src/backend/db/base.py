"""
Base declarative class for SQLAlchemy ORM models.
This module defines the base class that all database models will inherit from,
providing consistent metadata and session management capabilities.
"""
from sqlalchemy.orm import DeclarativeBase  # SQLAlchemy 2.0+


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models in the application.
    
    All database models should inherit from this class to ensure
    consistent metadata and session management across the application.
    This base class is used by Alembic for database migrations.
    """
    pass