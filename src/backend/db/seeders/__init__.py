"""
Python package initialization file for the database seeders module that exposes the seed_demo_data function.
This module provides data seeding functionality for populating the Justice Bid database with test data for development, testing, and demonstration purposes.
"""

from .demo_data import seed_demo_data  # Import the main seeding function

__all__ = ['seed_demo_data']  # Make the function available for direct import