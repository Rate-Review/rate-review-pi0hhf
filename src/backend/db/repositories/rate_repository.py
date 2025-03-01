"""
Repository class for handling rate data operations in the database, providing CRUD operations 
and specialized queries for rate data in the Justice Bid Rate Negotiation System.
"""

from typing import List, Optional, Dict, Any, Tuple
import uuid
import json
from datetime import date, datetime

from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.orm import Session, Query

from ..models.rate import Rate
from ..session import get_session
from ...utils.datetime_utils import get_current_date
from ...utils.currency import convert_currency
from ...utils.logging import logger


class RateRepository:
    """
    Repository class for managing rate data in the database, providing CRUD operations and specialized 
    queries to support the rate negotiation process.
    """
    
    def __init__(self, session: Optional[Session] = None):
        """
        Initializes the RateRepository with optional session
        
        Args:
            session: Optional SQLAlchemy session, if not provided a new one will be created
        """
        self.session = session or get_session()
    
    def create(self, attorney_id: str, client_id: str, firm_id: str, 
               office_id: Optional[str] = None, staff_class_id: Optional[str] = None,
               amount: float = 0.0, currency: str = "USD", type: str = "STANDARD",
               effective_date: date = None, expiration_date: Optional[date] = None,
               status: str = "DRAFT", history: Optional[Dict] = None) -> Rate:
        """
        Creates a new rate record in the database
        
        Args:
            attorney_id: UUID of the attorney
            client_id: UUID of the client organization
            firm_id: UUID of the law firm
            office_id: UUID of the office location
            staff_class_id: UUID of the staff class
            amount: Rate amount
            currency: Currency code (e.g., USD, EUR)
            type: Rate type (STANDARD, APPROVED, PROPOSED, COUNTER_PROPOSED)
            effective_date: Date when rate becomes effective
            expiration_date: Optional date when rate expires
            status: Current status of the rate
            history: Optional history data
            
        Returns:
            Created rate instance
        """
        try:
            # Set default effective date to today if not provided
            if effective_date is None:
                effective_date = get_current_date()
            
            # Create new Rate instance
            rate = Rate(
                attorney_id=uuid.UUID(attorney_id),
                client_id=uuid.UUID(client_id),
                firm_id=uuid.UUID(firm_id),
                office_id=uuid.UUID(office_id) if office_id else None,
                staff_class_id=uuid.UUID(staff_class_id) if staff_class_id else None,
                amount=amount,
                currency=currency,
                type=type,
                effective_date=effective_date,
                expiration_date=expiration_date,
                status=status
            )
            
            # Add rate to session
            self.session.add(rate)
            self.session.commit()
            
            logger.info(f"Created new rate for attorney {attorney_id} with client {client_id}")
            
            return rate
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating rate: {str(e)}")
            raise
    
    def get_by_id(self, rate_id: str) -> Optional[Rate]:
        """
        Retrieves a rate by its ID
        
        Args:
            rate_id: UUID of the rate to retrieve
            
        Returns:
            Rate instance if found, None otherwise
        """
        try:
            return self.session.query(Rate).filter(Rate.id == uuid.UUID(rate_id)).first()
        except Exception as e:
            logger.error(f"Error retrieving rate with ID {rate_id}: {str(e)}")
            raise
    
    def update(self, rate_id: str, data: Dict[str, Any]) -> Optional[Rate]:
        """
        Updates an existing rate record
        
        Args:
            rate_id: UUID of the rate to update
            data: Dictionary of fields to update
            
        Returns:
            Updated Rate instance if found, None otherwise
        """
        try:
            # Get the rate by ID
            rate = self.get_by_id(rate_id)
            
            if not rate:
                logger.warning(f"Attempted to update non-existent rate with ID {rate_id}")
                return None
            
            # Track previous values for history
            previous_amount = rate.amount
            previous_status = rate.status.value if hasattr(rate.status, 'value') else str(rate.status)
            previous_type = rate.type.value if hasattr(rate.type, 'value') else str(rate.type)
            
            # Update rate attributes with provided data
            for key, value in data.items():
                if hasattr(rate, key):
                    # Convert UUIDs if necessary
                    if key in ['attorney_id', 'client_id', 'firm_id', 'office_id', 'staff_class_id'] and value:
                        value = uuid.UUID(value)
                    
                    setattr(rate, key, value)
            
            # Update rate history if user_id and message are provided
            if 'user_id' in data and 'message' in data:
                rate.add_history_entry(
                    previous_amount=previous_amount,
                    previous_status=previous_status,
                    previous_type=previous_type,
                    user_id=uuid.UUID(data['user_id']),
                    message=data['message']
                )
            
            self.session.commit()
            logger.info(f"Updated rate with ID {rate_id}")
            
            return rate
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating rate with ID {rate_id}: {str(e)}")
            raise
    
    def delete(self, rate_id: str) -> bool:
        """
        Deletes a rate record by ID
        
        Args:
            rate_id: UUID of the rate to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # Get the rate by ID
            rate = self.get_by_id(rate_id)
            
            if not rate:
                logger.warning(f"Attempted to delete non-existent rate with ID {rate_id}")
                return False
            
            # Delete the rate
            self.session.delete(rate)
            self.session.commit()
            
            logger.info(f"Deleted rate with ID {rate_id}")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting rate with ID {rate_id}: {str(e)}")
            raise
    
    def get_by_attorney(self, attorney_id: str, client_id: Optional[str] = None, 
                       as_of_date: Optional[date] = None, status: Optional[str] = None) -> List[Rate]:
        """
        Retrieves all rates for a specific attorney
        
        Args:
            attorney_id: UUID of the attorney
            client_id: Optional UUID of the client to filter by
            as_of_date: Optional date to get rates effective on that date
            status: Optional status to filter by
            
        Returns:
            List of Rate instances
        """
        try:
            # Start with basic query for the attorney
            query = self.session.query(Rate).filter(Rate.attorney_id == uuid.UUID(attorney_id))
            
            # Add client filter if provided
            if client_id:
                query = query.filter(Rate.client_id == uuid.UUID(client_id))
            
            # Add date filter if provided
            if as_of_date:
                query = query.filter(
                    Rate.effective_date <= as_of_date,
                    or_(
                        Rate.expiration_date >= as_of_date,
                        Rate.expiration_date == None
                    )
                )
            
            # Add status filter if provided
            if status:
                query = query.filter(Rate.status == status)
            
            # Execute query and return results
            return query.all()
            
        except Exception as e:
            logger.error(f"Error retrieving rates for attorney {attorney_id}: {str(e)}")
            raise
    
    def get_by_client(self, client_id: str, firm_id: Optional[str] = None, 
                     as_of_date: Optional[date] = None, status: Optional[str] = None) -> List[Rate]:
        """
        Retrieves all rates for a specific client
        
        Args:
            client_id: UUID of the client
            firm_id: Optional UUID of the law firm to filter by
            as_of_date: Optional date to get rates effective on that date
            status: Optional status to filter by
            
        Returns:
            List of Rate instances
        """
        try:
            # Start with basic query for the client
            query = self.session.query(Rate).filter(Rate.client_id == uuid.UUID(client_id))
            
            # Add firm filter if provided
            if firm_id:
                query = query.filter(Rate.firm_id == uuid.UUID(firm_id))
            
            # Add date filter if provided
            if as_of_date:
                query = query.filter(
                    Rate.effective_date <= as_of_date,
                    or_(
                        Rate.expiration_date >= as_of_date,
                        Rate.expiration_date == None
                    )
                )
            
            # Add status filter if provided
            if status:
                query = query.filter(Rate.status == status)
            
            # Execute query and return results
            return query.all()
            
        except Exception as e:
            logger.error(f"Error retrieving rates for client {client_id}: {str(e)}")
            raise
    
    def get_by_firm(self, firm_id: str, client_id: Optional[str] = None, 
                   as_of_date: Optional[date] = None, status: Optional[str] = None) -> List[Rate]:
        """
        Retrieves all rates for a specific law firm
        
        Args:
            firm_id: UUID of the law firm
            client_id: Optional UUID of the client to filter by
            as_of_date: Optional date to get rates effective on that date
            status: Optional status to filter by
            
        Returns:
            List of Rate instances
        """
        try:
            # Start with basic query for the firm
            query = self.session.query(Rate).filter(Rate.firm_id == uuid.UUID(firm_id))
            
            # Add client filter if provided
            if client_id:
                query = query.filter(Rate.client_id == uuid.UUID(client_id))
            
            # Add date filter if provided
            if as_of_date:
                query = query.filter(
                    Rate.effective_date <= as_of_date,
                    or_(
                        Rate.expiration_date >= as_of_date,
                        Rate.expiration_date == None
                    )
                )
            
            # Add status filter if provided
            if status:
                query = query.filter(Rate.status == status)
            
            # Execute query and return results
            return query.all()
            
        except Exception as e:
            logger.error(f"Error retrieving rates for firm {firm_id}: {str(e)}")
            raise
    
    def get_by_negotiation(self, negotiation_id: str) -> List[Rate]:
        """
        Retrieves rates associated with a specific negotiation
        
        Args:
            negotiation_id: UUID of the negotiation
            
        Returns:
            List of Rate instances
        """
        try:
            # Query rates associated with the negotiation through the association table
            query = self.session.query(Rate).join(
                "negotiations"
            ).filter(
                Rate.negotiations.any(id=uuid.UUID(negotiation_id))
            )
            
            # Execute query and return results
            return query.all()
            
        except Exception as e:
            logger.error(f"Error retrieving rates for negotiation {negotiation_id}: {str(e)}")
            raise
    
    def get_rate_history(self, attorney_id: str, client_id: str, 
                        start_date: Optional[date] = None, 
                        end_date: Optional[date] = None) -> List[Rate]:
        """
        Retrieves the history of rate changes for an attorney-client pair
        
        Args:
            attorney_id: UUID of the attorney
            client_id: UUID of the client
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            List of Rate instances ordered by effective_date
        """
        try:
            # Build query for attorney-client rate history
            query = self.session.query(Rate).filter(
                Rate.attorney_id == uuid.UUID(attorney_id),
                Rate.client_id == uuid.UUID(client_id)
            )
            
            # Add date filters if provided
            if start_date:
                query = query.filter(Rate.effective_date >= start_date)
            
            if end_date:
                query = query.filter(
                    or_(
                        Rate.effective_date <= end_date,
                        and_(
                            Rate.expiration_date != None,
                            Rate.expiration_date <= end_date
                        )
                    )
                )
            
            # Order by effective date descending
            query = query.order_by(desc(Rate.effective_date))
            
            # Execute query and return results
            return query.all()
            
        except Exception as e:
            logger.error(f"Error retrieving rate history for attorney {attorney_id} with client {client_id}: {str(e)}")
            raise
    
    def get_current_rates(self, client_id: Optional[str] = None, firm_id: Optional[str] = None,
                         office_id: Optional[str] = None, staff_class_id: Optional[str] = None,
                         status: Optional[str] = None, as_of_date: Optional[date] = None) -> List[Rate]:
        """
        Retrieves current effective rates based on filters
        
        Args:
            client_id: Optional UUID of the client to filter by
            firm_id: Optional UUID of the law firm to filter by
            office_id: Optional UUID of the office to filter by
            staff_class_id: Optional UUID of the staff class to filter by
            status: Optional status to filter by
            as_of_date: Optional date to get rates effective on that date
            
        Returns:
            List of current Rate instances
        """
        try:
            # Determine the as_of_date (default to current date)
            if as_of_date is None:
                as_of_date = get_current_date()
            
            # Build base query for effective rates
            query = self.session.query(Rate).filter(
                Rate.effective_date <= as_of_date,
                or_(
                    Rate.expiration_date >= as_of_date,
                    Rate.expiration_date == None
                )
            )
            
            # Add additional filters if provided
            if client_id:
                query = query.filter(Rate.client_id == uuid.UUID(client_id))
            
            if firm_id:
                query = query.filter(Rate.firm_id == uuid.UUID(firm_id))
            
            if office_id:
                query = query.filter(Rate.office_id == uuid.UUID(office_id))
            
            if staff_class_id:
                query = query.filter(Rate.staff_class_id == uuid.UUID(staff_class_id))
            
            if status:
                query = query.filter(Rate.status == status)
            
            # Execute query and return results
            return query.all()
            
        except Exception as e:
            logger.error(f"Error retrieving current rates: {str(e)}")
            raise
    
    def get_rates_for_approval(self, client_id: Optional[str] = None, firm_id: Optional[str] = None,
                              status_list: Optional[List[str]] = None) -> List[Rate]:
        """
        Retrieves rates pending approval based on filters
        
        Args:
            client_id: Optional UUID of the client to filter by
            firm_id: Optional UUID of the law firm to filter by
            status_list: Optional list of statuses to filter by
            
        Returns:
            List of Rate instances pending approval
        """
        try:
            # Default status list for pending approval if not provided
            if not status_list:
                status_list = ['SUBMITTED', 'UNDER_REVIEW']
            
            # Build query for rates pending approval
            query = self.session.query(Rate).filter(
                Rate.status.in_(status_list)
            )
            
            # Add additional filters if provided
            if client_id:
                query = query.filter(Rate.client_id == uuid.UUID(client_id))
            
            if firm_id:
                query = query.filter(Rate.firm_id == uuid.UUID(firm_id))
            
            # Execute query and return results
            return query.all()
            
        except Exception as e:
            logger.error(f"Error retrieving rates for approval: {str(e)}")
            raise
    
    def update_status(self, rate_id: str, status: str, user_id: Optional[str] = None, 
                     message: Optional[str] = None) -> Optional[Rate]:
        """
        Updates the status of a rate record
        
        Args:
            rate_id: UUID of the rate to update
            status: New status value
            user_id: Optional UUID of the user making the change
            message: Optional message explaining the status change
            
        Returns:
            Updated Rate instance if found, None otherwise
        """
        try:
            # Get the rate by ID
            rate = self.get_by_id(rate_id)
            
            if not rate:
                logger.warning(f"Attempted to update status of non-existent rate with ID {rate_id}")
                return None
            
            # Save previous values for history
            previous_amount = rate.amount
            previous_status = rate.status.value if hasattr(rate.status, 'value') else str(rate.status)
            previous_type = rate.type.value if hasattr(rate.type, 'value') else str(rate.type)
            
            # Update status
            rate.status = status
            
            # Add history entry if user_id is provided
            if user_id:
                rate.add_history_entry(
                    previous_amount=previous_amount,
                    previous_status=previous_status,
                    previous_type=previous_type,
                    user_id=uuid.UUID(user_id),
                    message=message or f"Status updated to {status}"
                )
            
            self.session.commit()
            logger.info(f"Updated status of rate {rate_id} to {status}")
            
            return rate
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating status for rate {rate_id}: {str(e)}")
            raise
    
    def add_counter_proposal(self, rate_id: str, counter_amount: float, user_id: str,
                            message: Optional[str] = None) -> Optional[Rate]:
        """
        Adds a counter-proposal to a rate
        
        Args:
            rate_id: UUID of the rate to counter-propose
            counter_amount: Proposed counter rate amount
            user_id: UUID of the user making the counter-proposal
            message: Optional message explaining the counter-proposal
            
        Returns:
            Updated Rate instance if found, None otherwise
        """
        try:
            # Get the rate by ID
            rate = self.get_by_id(rate_id)
            
            if not rate:
                logger.warning(f"Attempted to counter-propose non-existent rate with ID {rate_id}")
                return None
            
            # Save previous values for history
            previous_amount = rate.amount
            previous_status = rate.status.value if hasattr(rate.status, 'value') else str(rate.status)
            previous_type = rate.type.value if hasattr(rate.type, 'value') else str(rate.type)
            
            # Determine if this is a client or firm counter-proposal based on the current status
            if previous_status in ['SUBMITTED', 'UNDER_REVIEW', 'FIRM_COUNTER_PROPOSED']:
                new_status = 'CLIENT_COUNTER_PROPOSED'
            else:
                new_status = 'FIRM_COUNTER_PROPOSED'
            
            # Update rate with counter-proposal data
            rate.status = new_status
            
            # Create history entry with counter-proposal details
            history_message = message or f"Counter-proposed rate of {counter_amount} {rate.currency}"
            counter_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': str(user_id),
                'previous_amount': str(previous_amount),
                'counter_amount': str(counter_amount),
                'previous_status': previous_status,
                'new_status': new_status,
                'previous_type': previous_type,
                'message': history_message
            }
            
            # Initialize history if it doesn't exist
            if rate.history is None:
                rate.history = []
            
            # Add counter-proposal to history
            rate.history.append(counter_entry)
            
            self.session.commit()
            logger.info(f"Added counter-proposal of {counter_amount} for rate {rate_id}")
            
            return rate
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error adding counter-proposal for rate {rate_id}: {str(e)}")
            raise
    
    def accept_counter_proposal(self, rate_id: str, user_id: str, 
                               message: Optional[str] = None) -> Optional[Rate]:
        """
        Accepts a counter-proposal for a rate
        
        Args:
            rate_id: UUID of the rate with the counter-proposal
            user_id: UUID of the user accepting the counter-proposal
            message: Optional message explaining the acceptance
            
        Returns:
            Updated Rate instance if found, None otherwise
        """
        try:
            # Get the rate by ID
            rate = self.get_by_id(rate_id)
            
            if not rate:
                logger.warning(f"Attempted to accept counter-proposal for non-existent rate with ID {rate_id}")
                return None
            
            # Check if there is a counter-proposal to accept
            if rate.status not in ['CLIENT_COUNTER_PROPOSED', 'FIRM_COUNTER_PROPOSED']:
                logger.warning(f"Rate {rate_id} does not have a pending counter-proposal")
                return rate
            
            # Save previous values for history
            previous_amount = rate.amount
            previous_status = rate.status.value if hasattr(rate.status, 'value') else str(rate.status)
            previous_type = rate.type.value if hasattr(rate.type, 'value') else str(rate.type)
            
            # Find the latest counter-proposal in history
            counter_amount = None
            for entry in reversed(rate.history):
                if isinstance(entry, dict) and 'counter_amount' in entry:
                    counter_amount = float(entry['counter_amount'])
                    break
            
            if not counter_amount:
                logger.warning(f"No counter-proposal amount found in history for rate {rate_id}")
                return rate
            
            # Determine new status based on who is accepting
            if previous_status == 'CLIENT_COUNTER_PROPOSED':
                new_status = 'FIRM_ACCEPTED'
            else:  # FIRM_COUNTER_PROPOSED
                new_status = 'CLIENT_ACCEPTED'
            
            # Update rate with accepted counter-proposal
            rate.amount = counter_amount
            rate.status = new_status
            
            # Add history entry for acceptance
            history_message = message or f"Accepted counter-proposal of {counter_amount} {rate.currency}"
            rate.add_history_entry(
                previous_amount=previous_amount,
                previous_status=previous_status,
                previous_type=previous_type,
                user_id=uuid.UUID(user_id),
                message=history_message
            )
            
            self.session.commit()
            logger.info(f"Accepted counter-proposal for rate {rate_id}, new amount: {counter_amount}")
            
            return rate
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error accepting counter-proposal for rate {rate_id}: {str(e)}")
            raise
    
    def get_rate_analytics(self, client_id: Optional[str] = None, firm_id: Optional[str] = None,
                          start_date: Optional[date] = None, end_date: Optional[date] = None,
                          currency: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieves rate data for analytics purposes
        
        Args:
            client_id: Optional UUID of the client to filter by
            firm_id: Optional UUID of the law firm to filter by
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            currency: Optional currency to convert all amounts to
            
        Returns:
            Dictionary containing analytics data
        """
        try:
            # Build base query
            query = self.session.query(Rate)
            
            # Add filters if provided
            if client_id:
                query = query.filter(Rate.client_id == uuid.UUID(client_id))
            
            if firm_id:
                query = query.filter(Rate.firm_id == uuid.UUID(firm_id))
            
            if start_date:
                query = query.filter(Rate.effective_date >= start_date)
            
            if end_date:
                query = query.filter(
                    or_(
                        Rate.effective_date <= end_date,
                        and_(
                            Rate.expiration_date != None,
                            Rate.expiration_date <= end_date
                        )
                    )
                )
            
            # Execute query
            rates = query.all()
            
            # Process rates for analytics
            analytics = {
                'total_rates': len(rates),
                'currency_breakdown': {},
                'average_rates': {},
                'rate_increases': {},
                'staff_class_breakdown': {},
                'office_breakdown': {}
            }
            
            # Group by currency for aggregation
            rates_by_currency = {}
            for rate in rates:
                if rate.currency not in rates_by_currency:
                    rates_by_currency[rate.currency] = []
                rates_by_currency[rate.currency].append(rate)
            
            # Process rates in each currency
            for curr, curr_rates in rates_by_currency.items():
                # Count rates in this currency
                analytics['currency_breakdown'][curr] = len(curr_rates)
                
                # Calculate average rate
                total_amount = sum(r.amount for r in curr_rates)
                average_rate = total_amount / len(curr_rates) if curr_rates else 0
                analytics['average_rates'][curr] = average_rate
                
                # Calculate rates by staff class
                staff_class_rates = {}
                for rate in curr_rates:
                    staff_class_id = str(rate.staff_class_id)
                    if staff_class_id not in staff_class_rates:
                        staff_class_rates[staff_class_id] = []
                    staff_class_rates[staff_class_id].append(rate.amount)
                
                for staff_class_id, amounts in staff_class_rates.items():
                    avg = sum(amounts) / len(amounts) if amounts else 0
                    if 'staff_class' not in analytics['average_rates']:
                        analytics['average_rates']['staff_class'] = {}
                    if curr not in analytics['average_rates']['staff_class']:
                        analytics['average_rates']['staff_class'][curr] = {}
                    analytics['average_rates']['staff_class'][curr][staff_class_id] = avg
            
            # Convert analytics to target currency if specified
            if currency:
                converted_analytics = {
                    'total_rates': analytics['total_rates'],
                    'currency_breakdown': analytics['currency_breakdown'],
                    'average_rates': {},
                    'rate_increases': {},
                    'staff_class_breakdown': {},
                    'office_breakdown': {}
                }
                
                # Convert average rates
                for curr, avg in analytics['average_rates'].items():
                    if isinstance(avg, dict):
                        # Handle nested dictionaries like staff_class breakdown
                        converted_analytics['average_rates'][curr] = {}
                        for key, value in avg.items():
                            if isinstance(value, dict):
                                converted_analytics['average_rates'][curr][key] = {}
                                for subkey, subvalue in value.items():
                                    converted_amount = convert_currency(subvalue, curr, currency)
                                    converted_analytics['average_rates'][curr][key][subkey] = converted_amount
                            else:
                                converted_amount = convert_currency(value, curr, currency)
                                converted_analytics['average_rates'][curr][key] = converted_amount
                    else:
                        # Handle direct currency values
                        converted_amount = convert_currency(avg, curr, currency)
                        converted_analytics['average_rates'][curr] = converted_amount
                
                analytics = converted_analytics
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating rate analytics: {str(e)}")
            raise
    
    def bulk_update_status(self, rate_ids: List[str], status: str, 
                          user_id: Optional[str] = None, message: Optional[str] = None) -> int:
        """
        Updates the status of multiple rate records
        
        Args:
            rate_ids: List of UUIDs of rates to update
            status: New status value
            user_id: Optional UUID of the user making the change
            message: Optional message explaining the status change
            
        Returns:
            Number of rates updated
        """
        try:
            updated_count = 0
            
            # Update each rate one by one to ensure history is properly tracked
            for rate_id in rate_ids:
                rate = self.update_status(rate_id, status, user_id, message)
                if rate:
                    updated_count += 1
            
            logger.info(f"Bulk updated status to {status} for {updated_count} rates")
            return updated_count
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error in bulk status update: {str(e)}")
            raise
    
    def import_rates(self, rate_data: List[Dict[str, Any]], import_type: str,
                    user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Imports multiple rate records from structured data
        
        Args:
            rate_data: List of dictionaries containing rate information
            import_type: Type of import (e.g., 'NEW', 'UPDATE')
            user_id: Optional UUID of the user performing the import
            
        Returns:
            Import results summary
        """
        try:
            results = {
                'total': len(rate_data),
                'successful': 0,
                'failed': 0,
                'errors': []
            }
            
            # Process each rate record
            for index, data in enumerate(rate_data):
                try:
                    # Check for required fields
                    required_fields = ['attorney_id', 'client_id', 'firm_id', 'amount', 'currency', 'effective_date']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                        results['errors'].append({
                            'index': index,
                            'error': error_msg,
                            'data': data
                        })
                        results['failed'] += 1
                        continue
                    
                    # Check if this is an update or new record
                    if import_type == 'UPDATE' and 'id' in data:
                        # Update existing rate
                        rate = self.update(data['id'], data)
                        if rate:
                            results['successful'] += 1
                        else:
                            results['errors'].append({
                                'index': index,
                                'error': f"Rate with ID {data['id']} not found",
                                'data': data
                            })
                            results['failed'] += 1
                    else:
                        # Create new rate
                        rate = self.create(
                            attorney_id=data['attorney_id'],
                            client_id=data['client_id'],
                            firm_id=data['firm_id'],
                            office_id=data.get('office_id'),
                            staff_class_id=data.get('staff_class_id'),
                            amount=data['amount'],
                            currency=data.get('currency', 'USD'),
                            type=data.get('type', 'STANDARD'),
                            effective_date=data['effective_date'],
                            expiration_date=data.get('expiration_date'),
                            status=data.get('status', 'DRAFT')
                        )
                        results['successful'] += 1
                
                except Exception as e:
                    # Log the error and continue with next record
                    error_msg = str(e)
                    results['errors'].append({
                        'index': index,
                        'error': error_msg,
                        'data': data
                    })
                    results['failed'] += 1
            
            # Commit all successful changes
            self.session.commit()
            logger.info(f"Imported {results['successful']} rates, {results['failed']} failed")
            
            return results
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error importing rates: {str(e)}")
            raise
    
    def export_rates(self, client_id: Optional[str] = None, firm_id: Optional[str] = None,
                    status: Optional[str] = None, export_format: Optional[str] = None,
                    currency: Optional[str] = None) -> Dict[str, Any]:
        """
        Exports rate data based on filters
        
        Args:
            client_id: Optional UUID of the client to filter by
            firm_id: Optional UUID of the law firm to filter by
            status: Optional status to filter by
            export_format: Optional format for the export (e.g., 'JSON', 'CSV')
            currency: Optional currency to convert all amounts to
            
        Returns:
            Exported rate data
        """
        try:
            # Build query based on filters
            query = self.session.query(Rate)
            
            if client_id:
                query = query.filter(Rate.client_id == uuid.UUID(client_id))
            
            if firm_id:
                query = query.filter(Rate.firm_id == uuid.UUID(firm_id))
            
            if status:
                query = query.filter(Rate.status == status)
            
            # Execute query
            rates = query.all()
            
            # Format rates for export
            export_data = []
            for rate in rates:
                rate_dict = {
                    'id': str(rate.id),
                    'attorney_id': str(rate.attorney_id),
                    'client_id': str(rate.client_id),
                    'firm_id': str(rate.firm_id),
                    'office_id': str(rate.office_id) if rate.office_id else None,
                    'staff_class_id': str(rate.staff_class_id) if rate.staff_class_id else None,
                    'amount': float(rate.amount),
                    'currency': rate.currency,
                    'type': rate.type.value if hasattr(rate.type, 'value') else str(rate.type),
                    'effective_date': rate.effective_date.isoformat(),
                    'expiration_date': rate.expiration_date.isoformat() if rate.expiration_date else None,
                    'status': rate.status.value if hasattr(rate.status, 'value') else str(rate.status),
                    'created_at': rate.created_at.isoformat(),
                    'updated_at': rate.updated_at.isoformat()
                }
                
                # Convert amount to target currency if specified
                if currency and rate.currency != currency:
                    rate_dict['original_amount'] = rate_dict['amount']
                    rate_dict['original_currency'] = rate_dict['currency']
                    rate_dict['amount'] = float(convert_currency(rate.amount, rate.currency, currency))
                    rate_dict['currency'] = currency
                
                export_data.append(rate_dict)
            
            # Create result object
            result = {
                'count': len(export_data),
                'data': export_data,
                'format': export_format or 'JSON',
                'filters': {
                    'client_id': client_id,
                    'firm_id': firm_id,
                    'status': status,
                    'currency': currency
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Format based on export_format if needed
            if export_format == 'CSV':
                # In a real implementation, we would convert to CSV format here
                # but for this example we'll just note it in the result
                result['format_note'] = 'CSV conversion would be implemented here'
            
            logger.info(f"Exported {len(export_data)} rates")
            return result
            
        except Exception as e:
            logger.error(f"Error exporting rates: {str(e)}")
            raise