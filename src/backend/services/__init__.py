"""Justice Bid Service Layer

This package contains the business logic for the Justice Bid Rate Negotiation System.
Services are organized around business domains and provide a clean interface between
the API layer and data access layer. Each service module encapsulates specific
business functionality and enforces business rules.

Services should:
- Implement business logic and rules
- Orchestrate data access through repositories
- Handle cross-cutting concerns like validation
- Remain independent of HTTP/API specific code
- Be testable in isolation

Importing services:
    from services import ai  # Import entire module
    from services.rates import validation  # Import specific submodule
    from services.negotiations.state_machine import NegotiationStateMachine  # Import specific class
"""

# Define what this package exposes
__all__ = [
    "ai",           # AI services for chat interface, recommendations, and personalization
    "analytics",    # Analytics services for rate trends, comparisons, and impact analysis
    "auth",         # Authentication and authorization services
    "documents",    # Document management and OCG-related services
    "messaging",    # Email, in-app messaging, and notification services
    "negotiations", # Rate negotiation workflow and process management
    "organizations", # Organization management for law firms and clients
    "rates"         # Rate management, validation, and calculations
]