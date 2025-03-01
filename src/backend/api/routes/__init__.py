"""API routes package initialization that imports and exposes the main route blueprints for REST API v1 and GraphQL endpoints."""
from flask import Blueprint  # flask==2.3+

from .api_v1 import api_v1_bp  # src/backend/api/routes/api_v1.py
from .graphql import graphql_bp  # src/backend/api/routes/graphql.py

__all__ = ['api_v1_bp', 'graphql_bp']