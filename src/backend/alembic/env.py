"""
Alembic migration environment configuration.

This file configures the Alembic migration environment for the Justice Bid Rate
Negotiation System. It connects Alembic to the application's models and database,
enabling versioned database schema migrations with tracking and rollback support.
"""

from logging.config import fileConfig
import logging
import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine.url import URL, make_url

# Ensure the application's root directory is in sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

# Import application components
from db.base import Base  # noqa: E402
from db.session import engine, get_db  # noqa: E402
from config import AppConfig  # noqa: E402

# Set up logger for Alembic operations
logger = logging.getLogger('alembic')

# Get Alembic configuration from alembic.ini file
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set SQLAlchemy metadata target for Alembic
target_metadata = Base.metadata


def include_object(object, name, type_, reflected, compare_to):
    """
    Filter function that determines which database objects are included in migrations.
    
    Args:
        object: The database object
        name: The object name
        type_: The object type (e.g., 'table', 'column')
        reflected: Whether the object was reflected
        compare_to: The object being compared to
        
    Returns:
        bool: True if the object should be included in migrations, False otherwise
    """
    # Exclude specific system tables or tables that should be ignored
    if type_ == 'table':
        # Skip special PostgreSQL tables
        if name.startswith('pg_') or name.startswith('sql_'):
            return False
        
        # Skip Alembic version table
        if name == 'alembic_version':
            return False
            
    return True


def get_engine():
    """
    Get database engine from application or create one from configuration.
    
    Returns:
        Engine: SQLAlchemy engine instance
    """
    # Check if engine is already imported from session module
    if engine is not None:
        logger.info("Using existing database engine")
        return engine
    
    # If not, create engine from configuration
    logger.info("Creating new database engine from configuration")
    app_config = AppConfig.get_instance()
    
    # Get database URL from configuration
    db_url = app_config.SQLALCHEMY_DATABASE_URI
    
    # Set SQLAlchemy URL in Alembic config
    config_section = config.get_section(config.config_ini_section)
    config_section["sqlalchemy.url"] = db_url
    
    # Create engine with appropriate connection pooling settings
    return engine_from_config(
        config_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )


def run_migrations_offline():
    """
    Run migrations in 'offline' mode, generating SQL scripts without connecting to the database.
    
    This mode generates SQL that can be run later or reviewed, rather than
    executing changes directly against a database.
    """
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        # If URL not in Alembic config, get from application config
        app_config = AppConfig.get_instance()
        url = app_config.SQLALCHEMY_DATABASE_URI
    
    # Configure context with URL and target metadata
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        # Configure one transaction per migration for better isolation
        transaction_per_migration=True
    )

    # Run migration context to generate SQL scripts
    with context.begin_transaction():
        context.run_migrations()
        
    logger.info("Offline migrations completed")


def run_migrations_online():
    """
    Run migrations in 'online' mode, directly applying changes to the connected database.
    
    This connects to the database and executes migration operations directly.
    """
    # Get the engine (either from session or create new one)
    connectable = get_engine()

    # Create a connection from the engine
    with connectable.connect() as connection:
        # Configure connection context with target metadata
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            # Configure one transaction per migration for better isolation
            transaction_per_migration=True
        )

        # Begin a transaction and run migrations
        with context.begin_transaction():
            context.run_migrations()
            
    logger.info("Online migrations completed")


# Determine which mode to run in
if context.is_offline_mode():
    logger.info("Running migrations offline")
    run_migrations_offline()
else:
    logger.info("Running migrations online")
    run_migrations_online()