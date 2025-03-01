import logging  # standard library

from flask import Flask  # flask==2.3+

from .main import get_application  # src/backend/main.py

# Set up logger
logger = logging.getLogger(__name__)

# Create a Flask application instance
application = get_application()

# Log that the WSGI application has been created
logger.info("WSGI application created")