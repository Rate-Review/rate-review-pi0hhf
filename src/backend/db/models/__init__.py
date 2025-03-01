"""
Initialization file for the database models package that imports and exports all SQLAlchemy model classes,
enabling simplified imports throughout the application.
"""

# Import common model components and base classes
from .common import *  # Import all items from common.py

# Import User model
from .user import User

# Import Organization model
from .organization import Organization

# Import Attorney model
from .attorney import Attorney

# Import StaffClass model
from .staff_class import StaffClass

# Import PeerGroup model
from .peer_group import PeerGroup

# Import Billing model
from .billing import BillingHistory as Billing

# Import Rate model
from .rate import Rate

# Import Message model
from .message import Message

# Import Document model
from .document import Document

# Import Negotiation model
from .negotiation import Negotiation

# Import OCG (Outside Counsel Guidelines) model
from .ocg import OCG

# Import ApprovalWorkflow model
from .approval_workflow import ApprovalWorkflow

# Export User model for easy importing
__all__ = ['User']

# Export Organization model for easy importing
__all__.append('Organization')

# Export Attorney model for easy importing
__all__.append('Attorney')

# Export StaffClass model for easy importing
__all__.append('StaffClass')

# Export PeerGroup model for easy importing
__all__.append('PeerGroup')

# Export Billing model for easy importing
__all__.append('Billing')

# Export Rate model for easy importing
__all__.append('Rate')

# Export Message model for easy importing
__all__.append('Message')

# Export Document model for easy importing
__all__.append('Document')

# Export Negotiation model for easy importing
__all__.append('Negotiation')

# Export OCG model for easy importing
__all__.append('OCG')

# Export ApprovalWorkflow model for easy importing
__all__.append('ApprovalWorkflow')