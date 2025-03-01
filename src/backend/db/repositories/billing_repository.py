"""
Repository class for handling database operations related to billing data.
Provides methods for creating, retrieving, updating, and deleting billing records,
as well as specialized queries to support rate impact analysis and historical analytics.
"""

import uuid
from typing import List, Dict, Optional, Tuple, Union, Any
from datetime import datetime, date, timedelta
from decimal import Decimal

import sqlalchemy
from sqlalchemy import func, and_, or_, desc, asc, text
from sqlalchemy.orm import Session, aliased
import pandas as pd

from ..models.billing import BillingHistory, MatterBillingSummary
from ..session import session_scope, get_db, get_read_db
from ...utils.logging import get_logger
from ...utils.validators import validate_required, validate_positive_number, validate_currency

# Set up logger
logger = get_logger(__name__, 'repository')

class BillingRepository:
    """
    Repository class for managing billing history data in the database,
    providing an abstraction layer for all billing-related operations.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize a new BillingRepository instance with a database session
        
        Args:
            db_session: SQLAlchemy database session
        """
        self._db = db_session
        logger.debug("BillingRepository initialized")
    
    def get_by_id(self, billing_id: uuid.UUID) -> Optional[BillingHistory]:
        """
        Retrieve a billing history record by its ID
        
        Args:
            billing_id: UUID of the billing record to retrieve
            
        Returns:
            BillingHistory object if found, None otherwise
        """
        try:
            return self._db.query(BillingHistory).filter(BillingHistory.id == billing_id).first()
        except Exception as e:
            logger.error(f"Error retrieving billing record {billing_id}: {str(e)}")
            return None
    
    def get_by_attorney(self, attorney_id: uuid.UUID, 
                      start_date: Optional[date] = None, 
                      end_date: Optional[date] = None,
                      client_id: Optional[uuid.UUID] = None,
                      limit: int = 100,
                      offset: int = 0) -> List[BillingHistory]:
        """
        Get billing records for a specific attorney
        
        Args:
            attorney_id: UUID of the attorney
            start_date: Optional start date filter
            end_date: Optional end date filter
            client_id: Optional client ID filter
            limit: Maximum number of records to return
            offset: Offset for pagination
            
        Returns:
            List of BillingHistory objects for the attorney
        """
        try:
            query = self._db.query(BillingHistory).filter(BillingHistory.attorney_id == attorney_id)
            
            if client_id:
                query = query.filter(BillingHistory.client_id == client_id)
            
            if start_date:
                query = query.filter(BillingHistory.billing_date >= start_date)
                
            if end_date:
                query = query.filter(BillingHistory.billing_date <= end_date)
            
            return query.order_by(desc(BillingHistory.billing_date)).limit(limit).offset(offset).all()
        except Exception as e:
            logger.error(f"Error retrieving billing records for attorney {attorney_id}: {str(e)}")
            return []
    
    def get_by_client(self, client_id: uuid.UUID, 
                    start_date: Optional[date] = None, 
                    end_date: Optional[date] = None,
                    matter_id: Optional[uuid.UUID] = None,
                    limit: int = 100,
                    offset: int = 0) -> List[BillingHistory]:
        """
        Get billing records for a specific client
        
        Args:
            client_id: UUID of the client
            start_date: Optional start date filter
            end_date: Optional end date filter
            matter_id: Optional matter ID filter
            limit: Maximum number of records to return
            offset: Offset for pagination
            
        Returns:
            List of BillingHistory objects for the client
        """
        try:
            query = self._db.query(BillingHistory).filter(BillingHistory.client_id == client_id)
            
            if matter_id:
                query = query.filter(BillingHistory.matter_id == matter_id)
            
            if start_date:
                query = query.filter(BillingHistory.billing_date >= start_date)
                
            if end_date:
                query = query.filter(BillingHistory.billing_date <= end_date)
            
            return query.order_by(desc(BillingHistory.billing_date)).limit(limit).offset(offset).all()
        except Exception as e:
            logger.error(f"Error retrieving billing records for client {client_id}: {str(e)}")
            return []
    
    def get_by_matter(self, matter_id: uuid.UUID, 
                    start_date: Optional[date] = None, 
                    end_date: Optional[date] = None,
                    limit: int = 100,
                    offset: int = 0) -> List[BillingHistory]:
        """
        Get billing records for a specific matter
        
        Args:
            matter_id: UUID of the matter
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of records to return
            offset: Offset for pagination
            
        Returns:
            List of BillingHistory objects for the matter
        """
        try:
            query = self._db.query(BillingHistory).filter(BillingHistory.matter_id == matter_id)
            
            if start_date:
                query = query.filter(BillingHistory.billing_date >= start_date)
                
            if end_date:
                query = query.filter(BillingHistory.billing_date <= end_date)
            
            return query.order_by(desc(BillingHistory.billing_date)).limit(limit).offset(offset).all()
        except Exception as e:
            logger.error(f"Error retrieving billing records for matter {matter_id}: {str(e)}")
            return []
    
    def get_by_firm_client(self, firm_id: uuid.UUID, 
                         client_id: uuid.UUID, 
                         start_date: Optional[date] = None, 
                         end_date: Optional[date] = None,
                         limit: int = 100,
                         offset: int = 0) -> List[BillingHistory]:
        """
        Get billing records for a specific law firm and client relationship
        
        Args:
            firm_id: UUID of the law firm
            client_id: UUID of the client
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of records to return
            offset: Offset for pagination
            
        Returns:
            List of BillingHistory objects for the firm-client relationship
        """
        try:
            # This query requires joining with attorneys to filter by firm_id
            Attorney = aliased(BillingHistory.attorney.property.entity.class_)
            
            query = self._db.query(BillingHistory).join(
                Attorney, BillingHistory.attorney_id == Attorney.id
            ).filter(
                BillingHistory.client_id == client_id,
                Attorney.organization_id == firm_id
            )
            
            if start_date:
                query = query.filter(BillingHistory.billing_date >= start_date)
                
            if end_date:
                query = query.filter(BillingHistory.billing_date <= end_date)
            
            return query.order_by(desc(BillingHistory.billing_date)).limit(limit).offset(offset).all()
        except Exception as e:
            logger.error(f"Error retrieving billing records for firm {firm_id} and client {client_id}: {str(e)}")
            return []
    
    def create(self, attorney_id: uuid.UUID, 
              client_id: uuid.UUID, 
              matter_id: uuid.UUID, 
              hours: Decimal, 
              fees: Decimal, 
              billing_date: date, 
              is_afa: bool = False, 
              currency: str = "USD", 
              department_id: Optional[uuid.UUID] = None, 
              practice_area: Optional[str] = None, 
              office_id: Optional[uuid.UUID] = None, 
              office_location: Optional[str] = None) -> BillingHistory:
        """
        Create a new billing history record
        
        Args:
            attorney_id: UUID of the attorney
            client_id: UUID of the client
            matter_id: UUID of the matter
            hours: Number of hours billed
            fees: Amount of fees billed
            billing_date: Date of the billing
            is_afa: Whether this is an Alternative Fee Arrangement
            currency: Currency code
            department_id: Optional UUID of the department
            practice_area: Optional practice area
            office_id: Optional UUID of the office
            office_location: Optional office location
            
        Returns:
            Newly created BillingHistory object
            
        Raises:
            ValueError: If validation fails
        """
        try:
            # Validate required fields
            validate_required(attorney_id, "attorney_id")
            validate_required(client_id, "client_id")
            validate_required(matter_id, "matter_id")
            validate_required(hours, "hours")
            validate_required(fees, "fees")
            validate_required(billing_date, "billing_date")
            
            # Validate numeric fields
            validate_positive_number(hours, "hours")
            validate_positive_number(fees, "fees")
            
            # Validate currency
            validate_currency(currency, "currency")
            
            # Create and add the billing record
            billing_record = BillingHistory(
                attorney_id=attorney_id,
                client_id=client_id,
                matter_id=matter_id,
                hours=hours,
                fees=fees,
                billing_date=billing_date,
                is_afa=is_afa,
                currency=currency,
                department_id=department_id,
                practice_area=practice_area,
                office_id=office_id,
                office_location=office_location
            )
            
            self._db.add(billing_record)
            self._db.commit()
            
            logger.info(f"Created billing record: {billing_record.id} for attorney {attorney_id}, client {client_id}")
            return billing_record
            
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error creating billing record: {str(e)}")
            raise
    
    def update(self, billing_id: uuid.UUID, update_data: dict) -> Optional[BillingHistory]:
        """
        Update an existing billing history record
        
        Args:
            billing_id: UUID of the billing record to update
            update_data: Dictionary of fields to update
            
        Returns:
            Updated BillingHistory object if found, None otherwise
            
        Raises:
            ValueError: If validation fails
        """
        try:
            billing_record = self.get_by_id(billing_id)
            if not billing_record:
                logger.warning(f"Billing record {billing_id} not found for update")
                return None
            
            # Validate numeric fields if provided
            if 'hours' in update_data:
                validate_positive_number(update_data['hours'], "hours")
                
            if 'fees' in update_data:
                validate_positive_number(update_data['fees'], "fees")
                
            if 'currency' in update_data:
                validate_currency(update_data['currency'], "currency")
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(billing_record, key):
                    setattr(billing_record, key, value)
            
            self._db.commit()
            logger.info(f"Updated billing record: {billing_id}")
            return billing_record
            
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error updating billing record {billing_id}: {str(e)}")
            raise
    
    def delete(self, billing_id: uuid.UUID) -> bool:
        """
        Delete a billing history record
        
        Args:
            billing_id: UUID of the billing record to delete
            
        Returns:
            True if deleted successfully, False if record not found
        """
        try:
            billing_record = self.get_by_id(billing_id)
            if not billing_record:
                logger.warning(f"Billing record {billing_id} not found for deletion")
                return False
            
            self._db.delete(billing_record)
            self._db.commit()
            logger.info(f"Deleted billing record: {billing_id}")
            return True
            
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error deleting billing record {billing_id}: {str(e)}")
            return False
    
    def bulk_create(self, billing_records: List[dict]) -> List[BillingHistory]:
        """
        Create multiple billing history records in bulk
        
        Args:
            billing_records: List of dictionaries containing billing record data
            
        Returns:
            List of created BillingHistory objects
            
        Raises:
            ValueError: If validation fails for any record
        """
        created_records = []
        
        try:
            # Validate and create each record
            for record_data in billing_records:
                # Validate required fields
                attorney_id = record_data.get('attorney_id')
                client_id = record_data.get('client_id')
                matter_id = record_data.get('matter_id')
                hours = record_data.get('hours')
                fees = record_data.get('fees')
                billing_date = record_data.get('billing_date')
                
                validate_required(attorney_id, "attorney_id")
                validate_required(client_id, "client_id")
                validate_required(matter_id, "matter_id")
                validate_required(hours, "hours")
                validate_required(fees, "fees")
                validate_required(billing_date, "billing_date")
                
                # Validate numeric fields
                validate_positive_number(hours, "hours")
                validate_positive_number(fees, "fees")
                
                # Validate currency if provided
                currency = record_data.get('currency', 'USD')
                validate_currency(currency, "currency")
                
                # Create billing record object
                billing_record = BillingHistory(
                    attorney_id=attorney_id,
                    client_id=client_id,
                    matter_id=matter_id,
                    hours=hours,
                    fees=fees,
                    billing_date=billing_date,
                    is_afa=record_data.get('is_afa', False),
                    currency=currency,
                    department_id=record_data.get('department_id'),
                    practice_area=record_data.get('practice_area'),
                    office_id=record_data.get('office_id'),
                    office_location=record_data.get('office_location')
                )
                
                self._db.add(billing_record)
                created_records.append(billing_record)
            
            # Commit all records
            self._db.commit()
            logger.info(f"Created {len(created_records)} billing records in bulk")
            return created_records
            
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error creating billing records in bulk: {str(e)}")
            raise
    
    def get_attorney_hours_for_rate_impact(self, client_id: uuid.UUID, 
                                         firm_id: uuid.UUID, 
                                         start_date: date, 
                                         end_date: date,
                                         attorney_ids: Optional[List[uuid.UUID]] = None) -> Dict[uuid.UUID, Decimal]:
        """
        Get billing hours by attorney for rate impact analysis
        
        Args:
            client_id: UUID of the client
            firm_id: UUID of the law firm
            start_date: Start date for the analysis period
            end_date: End date for the analysis period
            attorney_ids: Optional list of specific attorney IDs to include
            
        Returns:
            Dictionary mapping attorney_ids to their total hours
        """
        try:
            # Create join with Attorney model to filter by firm
            Attorney = aliased(BillingHistory.attorney.property.entity.class_)
            
            query = self._db.query(
                BillingHistory.attorney_id,
                func.sum(BillingHistory.hours).label('total_hours')
            ).join(
                Attorney, BillingHistory.attorney_id == Attorney.id
            ).filter(
                BillingHistory.client_id == client_id,
                Attorney.organization_id == firm_id,
                BillingHistory.billing_date >= start_date,
                BillingHistory.billing_date <= end_date
            )
            
            # Filter by specific attorneys if provided
            if attorney_ids:
                query = query.filter(BillingHistory.attorney_id.in_(attorney_ids))
            
            # Group by attorney
            query = query.group_by(BillingHistory.attorney_id)
            
            # Execute query and convert to dictionary
            results = query.all()
            return {row.attorney_id: row.total_hours for row in results}
            
        except Exception as e:
            logger.error(f"Error retrieving attorney hours for rate impact analysis: {str(e)}")
            return {}
    
    def get_staff_class_hours_for_rate_impact(self, client_id: uuid.UUID, 
                                            firm_id: uuid.UUID, 
                                            start_date: date, 
                                            end_date: date,
                                            staff_class_ids: Optional[List[uuid.UUID]] = None) -> Dict[uuid.UUID, Decimal]:
        """
        Get billing hours by staff class for rate impact analysis
        
        Args:
            client_id: UUID of the client
            firm_id: UUID of the law firm
            start_date: Start date for the analysis period
            end_date: End date for the analysis period
            staff_class_ids: Optional list of specific staff class IDs to include
            
        Returns:
            Dictionary mapping staff_class_ids to their total hours
        """
        try:
            # Create aliases for the join tables
            Attorney = aliased(BillingHistory.attorney.property.entity.class_)
            
            query = self._db.query(
                Attorney.staff_class_id,
                func.sum(BillingHistory.hours).label('total_hours')
            ).join(
                Attorney, BillingHistory.attorney_id == Attorney.id
            ).filter(
                BillingHistory.client_id == client_id,
                Attorney.organization_id == firm_id,
                BillingHistory.billing_date >= start_date,
                BillingHistory.billing_date <= end_date
            )
            
            # Filter by specific staff classes if provided
            if staff_class_ids:
                query = query.filter(Attorney.staff_class_id.in_(staff_class_ids))
            
            # Group by staff class
            query = query.group_by(Attorney.staff_class_id)
            
            # Execute query and convert to dictionary
            results = query.all()
            return {row.staff_class_id: row.total_hours for row in results}
            
        except Exception as e:
            logger.error(f"Error retrieving staff class hours for rate impact analysis: {str(e)}")
            return {}
    
    def get_total_hours_and_fees(self, client_id: uuid.UUID, 
                                firm_id: Optional[uuid.UUID] = None,
                                start_date: date = None, 
                                end_date: date = None) -> Tuple[Decimal, Decimal]:
        """
        Get total hours and fees for a specific client and optional firm
        
        Args:
            client_id: UUID of the client
            firm_id: Optional UUID of the law firm
            start_date: Start date for the analysis period
            end_date: End date for the analysis period
            
        Returns:
            Tuple of (total_hours, total_fees)
        """
        try:
            # Start building the query
            query = self._db.query(
                func.sum(BillingHistory.hours).label('total_hours'),
                func.sum(BillingHistory.fees).label('total_fees')
            ).filter(
                BillingHistory.client_id == client_id
            )
            
            # Add firm filter if provided
            if firm_id:
                Attorney = aliased(BillingHistory.attorney.property.entity.class_)
                query = query.join(
                    Attorney, BillingHistory.attorney_id == Attorney.id
                ).filter(
                    Attorney.organization_id == firm_id
                )
            
            # Add date filters if provided
            if start_date:
                query = query.filter(BillingHistory.billing_date >= start_date)
                
            if end_date:
                query = query.filter(BillingHistory.billing_date <= end_date)
            
            # Execute query
            result = query.first()
            
            # Handle None values
            total_hours = result.total_hours if result and result.total_hours is not None else Decimal('0.0')
            total_fees = result.total_fees if result and result.total_fees is not None else Decimal('0.0')
            
            return (total_hours, total_fees)
            
        except Exception as e:
            logger.error(f"Error retrieving total hours and fees: {str(e)}")
            return (Decimal('0.0'), Decimal('0.0'))
    
    def get_afa_percentage(self, client_id: uuid.UUID, 
                         firm_id: Optional[uuid.UUID] = None,
                         start_date: date = None, 
                         end_date: date = None) -> Dict[str, Decimal]:
        """
        Calculate percentage of fees from Alternative Fee Arrangements
        
        Args:
            client_id: UUID of the client
            firm_id: Optional UUID of the law firm
            start_date: Start date for the analysis period
            end_date: End date for the analysis period
            
        Returns:
            Dictionary with hours_percentage and fees_percentage
        """
        try:
            # First get total hours and fees
            total_hours, total_fees = self.get_total_hours_and_fees(
                client_id, firm_id, start_date, end_date
            )
            
            # If totals are zero, return zero percentages
            if total_hours == 0 or total_fees == 0:
                return {
                    'hours_percentage': Decimal('0.0'),
                    'fees_percentage': Decimal('0.0')
                }
            
            # Now get AFA hours and fees
            query = self._db.query(
                func.sum(BillingHistory.hours).label('afa_hours'),
                func.sum(BillingHistory.fees).label('afa_fees')
            ).filter(
                BillingHistory.client_id == client_id,
                BillingHistory.is_afa == True
            )
            
            # Add firm filter if provided
            if firm_id:
                Attorney = aliased(BillingHistory.attorney.property.entity.class_)
                query = query.join(
                    Attorney, BillingHistory.attorney_id == Attorney.id
                ).filter(
                    Attorney.organization_id == firm_id
                )
            
            # Add date filters if provided
            if start_date:
                query = query.filter(BillingHistory.billing_date >= start_date)
                
            if end_date:
                query = query.filter(BillingHistory.billing_date <= end_date)
            
            # Execute query
            result = query.first()
            
            # Handle None values
            afa_hours = result.afa_hours if result and result.afa_hours is not None else Decimal('0.0')
            afa_fees = result.afa_fees if result and result.afa_fees is not None else Decimal('0.0')
            
            # Calculate percentages
            hours_percentage = (afa_hours / total_hours) * 100 if total_hours > 0 else Decimal('0.0')
            fees_percentage = (afa_fees / total_fees) * 100 if total_fees > 0 else Decimal('0.0')
            
            return {
                'hours_percentage': round(hours_percentage, 2),
                'fees_percentage': round(fees_percentage, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating AFA percentages: {str(e)}")
            return {
                'hours_percentage': Decimal('0.0'),
                'fees_percentage': Decimal('0.0')
            }
    
    def get_historical_trends(self, client_id: uuid.UUID, 
                           firm_id: Optional[uuid.UUID] = None,
                           start_date: date = None, 
                           end_date: date = None,
                           interval: str = 'monthly') -> pd.DataFrame:
        """
        Get historical trends for hours, fees, and effective rates over time
        
        Args:
            client_id: UUID of the client
            firm_id: Optional UUID of the law firm
            start_date: Start date for the analysis period
            end_date: End date for the analysis period
            interval: Time interval for grouping ('monthly', 'quarterly', 'yearly')
            
        Returns:
            Pandas DataFrame with trend data grouped by time interval
        """
        try:
            # Get all billing records for the period
            query = self._db.query(BillingHistory).filter(
                BillingHistory.client_id == client_id
            )
            
            # Add firm filter if provided
            if firm_id:
                Attorney = aliased(BillingHistory.attorney.property.entity.class_)
                query = query.join(
                    Attorney, BillingHistory.attorney_id == Attorney.id
                ).filter(
                    Attorney.organization_id == firm_id
                )
            
            # Add date filters if provided
            if start_date:
                query = query.filter(BillingHistory.billing_date >= start_date)
                
            if end_date:
                query = query.filter(BillingHistory.billing_date <= end_date)
            
            # Execute query and convert to DataFrame
            billing_records = query.all()
            if not billing_records:
                # Return empty DataFrame with expected columns
                return pd.DataFrame(columns=[
                    'period', 'total_hours', 'total_fees', 'effective_rate',
                    'afa_hours', 'afa_fees', 'afa_percentage'
                ])
            
            # Convert billing records to a pandas DataFrame
            data = []
            for record in billing_records:
                data.append({
                    'billing_date': record.billing_date,
                    'hours': float(record.hours),
                    'fees': float(record.fees),
                    'is_afa': record.is_afa,
                    'currency': record.currency
                })
            
            df = pd.DataFrame(data)
            
            # Convert billing_date to datetime if it's not already
            if not pd.api.types.is_datetime64_any_dtype(df['billing_date']):
                df['billing_date'] = pd.to_datetime(df['billing_date'])
            
            # Define time period based on interval
            if interval == 'monthly':
                df['period'] = df['billing_date'].dt.to_period('M')
            elif interval == 'quarterly':
                df['period'] = df['billing_date'].dt.to_period('Q')
            elif interval == 'yearly':
                df['period'] = df['billing_date'].dt.to_period('Y')
            else:
                # Default to monthly
                df['period'] = df['billing_date'].dt.to_period('M')
            
            # Group by period and calculate metrics
            grouped = df.groupby('period').agg({
                'hours': 'sum',
                'fees': 'sum',
                'is_afa': lambda x: sum(x)  # Count of AFA records
            }).reset_index()
            
            # Add derived metrics
            grouped['effective_rate'] = grouped['fees'] / grouped['hours']
            grouped['total_hours'] = grouped['hours']
            grouped['total_fees'] = grouped['fees']
            
            # Calculate AFA metrics
            afa_df = df[df['is_afa']].groupby('period').agg({
                'hours': 'sum',
                'fees': 'sum'
            }).reset_index()
            
            if not afa_df.empty:
                # Rename columns
                afa_df = afa_df.rename(columns={'hours': 'afa_hours', 'fees': 'afa_fees'})
                
                # Merge with main grouped data
                grouped = pd.merge(grouped, afa_df, on='period', how='left')
                grouped['afa_hours'] = grouped['afa_hours'].fillna(0)
                grouped['afa_fees'] = grouped['afa_fees'].fillna(0)
                
                # Calculate AFA percentage
                grouped['afa_percentage'] = (grouped['afa_hours'] / grouped['total_hours']) * 100
            else:
                # Add empty AFA columns
                grouped['afa_hours'] = 0
                grouped['afa_fees'] = 0
                grouped['afa_percentage'] = 0
            
            # Convert period to string for easier serialization
            grouped['period'] = grouped['period'].astype(str)
            
            # Calculate year-over-year changes if data spans multiple years
            if interval == 'yearly' and len(grouped) > 1:
                grouped['hours_yoy_change'] = grouped['total_hours'].pct_change() * 100
                grouped['fees_yoy_change'] = grouped['total_fees'].pct_change() * 100
                grouped['rate_yoy_change'] = grouped['effective_rate'].pct_change() * 100
            
            return grouped
            
        except Exception as e:
            logger.error(f"Error calculating historical trends: {str(e)}")
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=[
                'period', 'total_hours', 'total_fees', 'effective_rate',
                'afa_hours', 'afa_fees', 'afa_percentage'
            ])
    
    def create_matter_billing_summary(self, matter_id: uuid.UUID, 
                                    client_id: uuid.UUID, 
                                    start_date: date, 
                                    end_date: date) -> MatterBillingSummary:
        """
        Create or update a matter billing summary
        
        Args:
            matter_id: UUID of the matter
            client_id: UUID of the client
            start_date: Start date for the summary period
            end_date: End date for the summary period
            
        Returns:
            Created or updated MatterBillingSummary object
        """
        try:
            # Get all billing records for the matter within the date range
            billing_records = self.get_by_matter(
                matter_id=matter_id,
                start_date=start_date,
                end_date=end_date,
                limit=10000  # Set high limit to get all records
            )
            
            if not billing_records:
                logger.warning(f"No billing records found for matter {matter_id} in the date range")
                # Create empty summary
                summary = MatterBillingSummary(
                    matter_id=matter_id,
                    client_id=client_id,
                    start_date=start_date,
                    end_date=end_date,
                    total_hours=Decimal('0.0'),
                    total_fees=Decimal('0.0'),
                    afa_hours=Decimal('0.0'),
                    afa_fees=Decimal('0.0'),
                    attorney_count=0,
                    currency='USD'
                )
                self._db.add(summary)
                self._db.commit()
                return summary
            
            # Calculate summary metrics
            total_hours = sum(record.hours for record in billing_records)
            total_fees = sum(record.fees for record in billing_records)
            afa_hours = sum(record.hours for record in billing_records if record.is_afa)
            afa_fees = sum(record.fees for record in billing_records if record.is_afa)
            
            # Get unique attorneys
            attorney_ids = set(record.attorney_id for record in billing_records)
            attorney_count = len(attorney_ids)
            
            # Get most common currency
            currencies = [record.currency for record in billing_records]
            most_common_currency = max(set(currencies), key=currencies.count)
            
            # Check if a summary already exists for this matter and date range
            existing_summary = self._db.query(MatterBillingSummary).filter(
                MatterBillingSummary.matter_id == matter_id,
                MatterBillingSummary.start_date == start_date,
                MatterBillingSummary.end_date == end_date
            ).first()
            
            if existing_summary:
                # Update existing summary
                existing_summary.total_hours = total_hours
                existing_summary.total_fees = total_fees
                existing_summary.afa_hours = afa_hours
                existing_summary.afa_fees = afa_fees
                existing_summary.attorney_count = attorney_count
                existing_summary.currency = most_common_currency
                
                # Update additional metrics
                metrics = {
                    'effective_rate': float(total_fees / total_hours) if total_hours > 0 else 0,
                    'afa_percentage': float((afa_hours / total_hours) * 100) if total_hours > 0 else 0,
                    'afa_fees_percentage': float((afa_fees / total_fees) * 100) if total_fees > 0 else 0,
                    'updated_at': datetime.utcnow().isoformat()
                }
                existing_summary.metrics = metrics
                
                self._db.commit()
                logger.info(f"Updated billing summary for matter {matter_id}")
                return existing_summary
            else:
                # Create new summary
                metrics = {
                    'effective_rate': float(total_fees / total_hours) if total_hours > 0 else 0,
                    'afa_percentage': float((afa_hours / total_hours) * 100) if total_hours > 0 else 0,
                    'afa_fees_percentage': float((afa_fees / total_fees) * 100) if total_fees > 0 else 0,
                    'created_at': datetime.utcnow().isoformat()
                }
                
                summary = MatterBillingSummary(
                    matter_id=matter_id,
                    client_id=client_id,
                    start_date=start_date,
                    end_date=end_date,
                    total_hours=total_hours,
                    total_fees=total_fees,
                    afa_hours=afa_hours,
                    afa_fees=afa_fees,
                    attorney_count=attorney_count,
                    currency=most_common_currency,
                    metrics=metrics
                )
                
                self._db.add(summary)
                self._db.commit()
                logger.info(f"Created billing summary for matter {matter_id}")
                return summary
                
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error creating matter billing summary: {str(e)}")
            raise
    
    def get_matter_billing_summary(self, matter_id: uuid.UUID, 
                                start_date: Optional[date] = None, 
                                end_date: Optional[date] = None) -> Optional[MatterBillingSummary]:
        """
        Get billing summary for a specific matter
        
        Args:
            matter_id: UUID of the matter
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            MatterBillingSummary object if found, None otherwise
        """
        try:
            query = self._db.query(MatterBillingSummary).filter(
                MatterBillingSummary.matter_id == matter_id
            )
            
            if start_date and end_date:
                # Look for exact date range match
                query = query.filter(
                    MatterBillingSummary.start_date == start_date,
                    MatterBillingSummary.end_date == end_date
                )
            elif start_date:
                # Find summary that includes the start date
                query = query.filter(
                    MatterBillingSummary.start_date <= start_date,
                    MatterBillingSummary.end_date >= start_date
                )
            elif end_date:
                # Find summary that includes the end date
                query = query.filter(
                    MatterBillingSummary.start_date <= end_date,
                    MatterBillingSummary.end_date >= end_date
                )
            
            # Get the most recent summary if multiple match
            return query.order_by(desc(MatterBillingSummary.end_date)).first()
            
        except Exception as e:
            logger.error(f"Error retrieving matter billing summary: {str(e)}")
            return None
    
    def get_practice_area_breakdown(self, client_id: uuid.UUID, 
                                  firm_id: Optional[uuid.UUID] = None,
                                  start_date: date = None, 
                                  end_date: date = None) -> Dict[str, Dict]:
        """
        Get breakdown of hours and fees by practice area
        
        Args:
            client_id: UUID of the client
            firm_id: Optional UUID of the law firm
            start_date: Start date for the analysis period
            end_date: End date for the analysis period
            
        Returns:
            Dictionary with practice areas as keys and hours/fees metrics as values
        """
        try:
            # Start building the query
            query = self._db.query(
                BillingHistory.practice_area,
                func.sum(BillingHistory.hours).label('total_hours'),
                func.sum(BillingHistory.fees).label('total_fees'),
                func.count(BillingHistory.id).label('record_count')
            ).filter(
                BillingHistory.client_id == client_id
            )
            
            # Add firm filter if provided
            if firm_id:
                Attorney = aliased(BillingHistory.attorney.property.entity.class_)
                query = query.join(
                    Attorney, BillingHistory.attorney_id == Attorney.id
                ).filter(
                    Attorney.organization_id == firm_id
                )
            
            # Add date filters if provided
            if start_date:
                query = query.filter(BillingHistory.billing_date >= start_date)
                
            if end_date:
                query = query.filter(BillingHistory.billing_date <= end_date)
            
            # Group by practice area
            query = query.group_by(BillingHistory.practice_area)
            
            # Execute query
            results = query.all()
            
            # Convert to dictionary with calculated metrics
            practice_area_breakdown = {}
            for row in results:
                practice_area = row.practice_area or "Unspecified"
                effective_rate = float(row.total_fees / row.total_hours) if row.total_hours > 0 else 0
                
                practice_area_breakdown[practice_area] = {
                    'total_hours': float(row.total_hours),
                    'total_fees': float(row.total_fees),
                    'effective_rate': effective_rate,
                    'record_count': row.record_count
                }
            
            return practice_area_breakdown
            
        except Exception as e:
            logger.error(f"Error getting practice area breakdown: {str(e)}")
            return {}
    
    def get_office_breakdown(self, client_id: uuid.UUID, 
                          firm_id: Optional[uuid.UUID] = None,
                          start_date: date = None, 
                          end_date: date = None) -> Dict[str, Dict]:
        """
        Get breakdown of hours and fees by office location
        
        Args:
            client_id: UUID of the client
            firm_id: Optional UUID of the law firm
            start_date: Start date for the analysis period
            end_date: End date for the analysis period
            
        Returns:
            Dictionary with offices as keys and hours/fees metrics as values
        """
        try:
            # Start building the query
            query = self._db.query(
                BillingHistory.office_location,
                func.sum(BillingHistory.hours).label('total_hours'),
                func.sum(BillingHistory.fees).label('total_fees'),
                func.count(BillingHistory.id).label('record_count')
            ).filter(
                BillingHistory.client_id == client_id
            )
            
            # Add firm filter if provided
            if firm_id:
                Attorney = aliased(BillingHistory.attorney.property.entity.class_)
                query = query.join(
                    Attorney, BillingHistory.attorney_id == Attorney.id
                ).filter(
                    Attorney.organization_id == firm_id
                )
            
            # Add date filters if provided
            if start_date:
                query = query.filter(BillingHistory.billing_date >= start_date)
                
            if end_date:
                query = query.filter(BillingHistory.billing_date <= end_date)
            
            # Group by office location
            query = query.group_by(BillingHistory.office_location)
            
            # Execute query
            results = query.all()
            
            # Convert to dictionary with calculated metrics
            office_breakdown = {}
            for row in results:
                office = row.office_location or "Unspecified"
                effective_rate = float(row.total_fees / row.total_hours) if row.total_hours > 0 else 0
                
                office_breakdown[office] = {
                    'total_hours': float(row.total_hours),
                    'total_fees': float(row.total_fees),
                    'effective_rate': effective_rate,
                    'record_count': row.record_count
                }
            
            return office_breakdown
            
        except Exception as e:
            logger.error(f"Error getting office breakdown: {str(e)}")
            return {}
    
    def search_billing_records(self, filters: dict, limit: int = 100, offset: int = 0) -> Tuple[List[BillingHistory], int]:
        """
        Search billing records with various filters
        
        Args:
            filters: Dictionary of filter conditions
            limit: Maximum number of records to return
            offset: Offset for pagination
            
        Returns:
            Tuple of (list of matching BillingHistory objects, total count)
        """
        try:
            # Start building the query
            query = self._db.query(BillingHistory)
            
            # Apply filters
            if filters.get('client_id'):
                query = query.filter(BillingHistory.client_id == filters['client_id'])
                
            if filters.get('firm_id'):
                Attorney = aliased(BillingHistory.attorney.property.entity.class_)
                query = query.join(
                    Attorney, BillingHistory.attorney_id == Attorney.id
                ).filter(
                    Attorney.organization_id == filters['firm_id']
                )
                
            if filters.get('attorney_id'):
                query = query.filter(BillingHistory.attorney_id == filters['attorney_id'])
                
            if filters.get('matter_id'):
                query = query.filter(BillingHistory.matter_id == filters['matter_id'])
                
            if filters.get('start_date'):
                query = query.filter(BillingHistory.billing_date >= filters['start_date'])
                
            if filters.get('end_date'):
                query = query.filter(BillingHistory.billing_date <= filters['end_date'])
                
            if filters.get('is_afa') is not None:
                query = query.filter(BillingHistory.is_afa == filters['is_afa'])
                
            if filters.get('practice_area'):
                query = query.filter(BillingHistory.practice_area == filters['practice_area'])
                
            if filters.get('office_location'):
                query = query.filter(BillingHistory.office_location == filters['office_location'])
                
            if filters.get('currency'):
                query = query.filter(BillingHistory.currency == filters['currency'])
            
            # Get total count before applying pagination
            total_count = query.count()
            
            # Apply pagination and get results
            query = query.order_by(desc(BillingHistory.billing_date))
            results = query.limit(limit).offset(offset).all()
            
            return results, total_count
            
        except Exception as e:
            logger.error(f"Error searching billing records: {str(e)}")
            return [], 0