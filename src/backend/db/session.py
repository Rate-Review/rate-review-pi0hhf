"""
Database session management module that configures SQLAlchemy connections, provides
session factories, and handles transaction management for the Justice Bid Rate Negotiation System.
"""

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from contextlib import contextmanager

from ..app.config import get_settings
from ..utils.logging import setup_logger
from ..utils.cache import redis_cache

# Set up logger for database operations
logger = setup_logger(__name__)

# Global database components
engine = None
read_engine = None
Session = None
Base = declarative_base()


def init_db():
    """
    Initialize database connections and session factories with proper connection pooling.
    
    This function configures the SQLAlchemy engine with connection pooling settings,
    sets up a read replica connection if enabled, and creates session factories.
    """
    global engine, read_engine, Session
    
    try:
        # Get database configuration from settings
        settings = get_settings()
        
        # Configure connection pool settings
        engine_options = {
            'pool_size': settings.get('DB_POOL_SIZE', 10),
            'max_overflow': settings.get('DB_MAX_OVERFLOW', 20),
            'pool_timeout': settings.get('DB_POOL_TIMEOUT', 30),
            'pool_recycle': settings.get('DB_POOL_RECYCLE', 3600),
            'echo': settings.get('DB_ECHO', False),
        }
        
        # Create primary database engine
        db_url = settings.SQLALCHEMY_DATABASE_URI
        engine = create_engine(
            db_url,
            **engine_options
        )
        
        # Configure read replica engine if enabled
        read_replica_url = settings.get('SQLALCHEMY_READ_REPLICA_URI')
        if read_replica_url:
            read_engine = create_engine(
                read_replica_url, 
                **engine_options
            )
            logger.info("Read replica database connection configured")
        else:
            read_engine = engine
            logger.info("Using primary database for read operations (no read replica configured)")
        
        # Create session factory
        session_factory = sessionmaker(bind=engine)
        
        # Create scoped session for thread-local sessions
        Session = scoped_session(session_factory)
        
        logger.info("Database connections initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database connections: {str(e)}")
        raise


def get_db():
    """
    Get a database session from the session factory.
    
    Returns:
        Session: SQLAlchemy session object
    """
    if Session is None:
        init_db()
    return Session()


def get_read_db():
    """
    Get a database session for read-only operations, potentially from a read replica.
    
    Returns:
        Session: SQLAlchemy session object configured for read-only operations
    """
    if Session is None:
        init_db()
    
    if read_engine and read_engine is not engine:
        # Create a session using the read replica connection
        session_factory = sessionmaker(bind=read_engine)
        session = session_factory()
    else:
        # Use regular session
        session = Session()
    
    # Set session to read-only mode
    session.execute("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY")
    
    return session


def close_db():
    """
    Close database connections and clean up session factories.
    """
    global Session, engine, read_engine
    
    try:
        if Session:
            Session.remove()
        
        if engine:
            engine.dispose()
        
        if read_engine and read_engine is not engine:
            read_engine.dispose()
        
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {str(e)}")


@contextmanager
def session_scope():
    """
    Context manager for handling database sessions with automatic commit/rollback.
    
    Yields:
        Session: SQLAlchemy session object
    
    Example:
        with session_scope() as session:
            user = session.query(User).filter_by(id=user_id).first()
            user.name = "New Name"
            # Session is automatically committed if no exceptions occur
            # or rolled back if an exception is raised
    """
    session = get_db()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error in database transaction, rolling back: {str(e)}")
        raise
    finally:
        session.close()


@contextmanager
def read_session_scope():
    """
    Context manager for handling read-only database sessions.
    
    Yields:
        Session: SQLAlchemy session object configured for read-only operations
    
    Example:
        with read_session_scope() as session:
            users = session.query(User).all()
            # Session is automatically closed when the block exits
    """
    session = get_read_db()
    try:
        yield session
    finally:
        session.close()