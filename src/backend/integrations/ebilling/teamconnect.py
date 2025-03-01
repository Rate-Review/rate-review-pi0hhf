"""
TeamConnect eBilling system integration adapter for Justice Bid.

This adapter handles API communication, data import/export, and field mapping between
Justice Bid and TeamConnect eBilling system.
"""

import requests
import jwt
import datetime
import json
from typing import Dict, List, Any, Optional, Union, Tuple

from ..common.adapter import AbstractEBillingAdapter
from ..common.client import APIClient
from ..common.mapper import DataMapper
from ...utils.logging import logger
from ...utils.validators import validate_date, validate_rate
from ...utils.constants import Integration

class TeamConnectAdapter(AbstractEBillingAdapter):
    """
    Adapter for integrating with TeamConnect eBilling system, handling API communication,
    data import/export, and field mapping.
    """
    
    # TeamConnect API constants
    API_VERSION = "v3"
    BASE_URL = "api/v3"
    
    def __init__(self, config: Dict):
        """
        Initialize the TeamConnect adapter with client-specific configuration.
        
        Args:
            config: Configuration dictionary containing connection parameters,
                   API keys, and client-specific settings.
        """
        super().__init__(config)
        logger.info(f"Initializing TeamConnect adapter")
        
        # Extract configuration values with defaults
        self.base_url = config.get('base_url', f"https://api.teamconnect.example.com/{self.API_VERSION}")
        self.api_key = config.get('api_key')
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')
        self.jwt_token = None
        self.token_expiry = None
        
        # Initialize API client
        self.client = APIClient(
            base_url=self.base_url,
            auth_config={
                'api_key': self.api_key,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            },
            auth_method='api_key',
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=config.get('timeout', 30),
            verify_ssl=config.get('verify_ssl', True)
        )
        
        # Set up API endpoints
        self._endpoints = {
            'auth': 'auth',
            'rates': 'rates',
            'timekeepers': 'timekeepers',
            'invoices': 'invoices',
            'matters': 'matters',
            'health': 'health'
        }
        
        # Define field mappings between TeamConnect and Justice Bid
        self._field_mappings = {
            # Rate mappings
            'rate': {
                'timekeeper_id': 'timekeeperID',
                'attorney_id': 'attorneyID',
                'rate_amount': 'amount',
                'currency': 'currency',
                'effective_date': 'effectiveDate',
                'expiration_date': 'expirationDate',
                'status': 'status',
                'client_id': 'clientID',
                'firm_id': 'firmID',
                'office_id': 'officeID',
                'practice_area': 'practiceArea',
                'staff_class': 'staffClass'
            },
            # Timekeeper mappings
            'timekeeper': {
                'timekeeper_id': 'timekeeperID',
                'name': 'name',
                'first_name': 'firstName',
                'last_name': 'lastName',
                'email': 'email',
                'firm_id': 'firmID',
                'office_id': 'officeID',
                'staff_class': 'staffClass',
                'bar_date': 'barDate',
                'graduation_date': 'graduationDate',
                'title': 'title',
                'practice_area': 'practiceArea'
            },
            # Billing data mappings
            'billing': {
                'invoice_id': 'invoiceID',
                'timekeeper_id': 'timekeeperID',
                'matter_id': 'matterID',
                'client_id': 'clientID',
                'firm_id': 'firmID',
                'hours': 'hours',
                'fees': 'fees',
                'date': 'date',
                'is_afa': 'isAFA',
                'currency': 'currency',
                'description': 'description'
            }
        }
        
        # Initialize data mapper
        self.mapper = DataMapper(self._field_mappings)
        
        logger.debug(f"TeamConnect adapter initialized with base URL: {self.base_url}")

    def authenticate(self) -> bool:
        """
        Authenticate with the TeamConnect API using API key and JWT.
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        # Check if we have a valid token that hasn't expired
        if self.jwt_token and self.token_expiry and datetime.datetime.now() < self.token_expiry:
            logger.debug("Using existing JWT token for TeamConnect authentication")
            return True
            
        try:
            logger.debug("Authenticating with TeamConnect API")
            
            # Prepare authentication payload
            auth_payload = {
                'api_key': self.api_key,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            # Make authentication request
            response = self.client.post(
                self._endpoints['auth'],
                json_data=auth_payload
            )
            
            if 'token' not in response:
                logger.error("Authentication failed: No token in response")
                return False
                
            # Store JWT token and set expiry
            self.jwt_token = response['token']
            
            # Parse expiry from token or set default (1 hour)
            try:
                token_data = jwt.decode(self.jwt_token, options={"verify_signature": False})
                if 'exp' in token_data:
                    self.token_expiry = datetime.datetime.fromtimestamp(token_data['exp'])
                else:
                    self.token_expiry = datetime.datetime.now() + datetime.timedelta(hours=1)
            except Exception as e:
                logger.warning(f"Could not parse token expiry: {str(e)}")
                self.token_expiry = datetime.datetime.now() + datetime.timedelta(hours=1)
            
            # Update client headers with token
            self.client.session.headers.update({
                'Authorization': f'Bearer {self.jwt_token}'
            })
            
            logger.info("Successfully authenticated with TeamConnect")
            return True
            
        except Exception as e:
            logger.error(f"TeamConnect authentication failed: {str(e)}")
            return False

    def test_connection(self) -> Dict:
        """
        Test the connection to the TeamConnect API.
        
        Returns:
            dict: Connection status with success flag and message
        """
        try:
            logger.debug("Testing connection to TeamConnect API")
            
            # Authenticate first
            if not self.authenticate():
                return {
                    'success': False,
                    'message': "Authentication failed"
                }
            
            # Try to call a simple endpoint to verify connection
            response = self.client.get(
                self._endpoints['health'],
                params={'check': 'basic'}
            )
            
            # Check for a successful response
            if isinstance(response, dict) and response.get('status') == 'ok':
                logger.info("TeamConnect connection test successful")
                return {
                    'success': True,
                    'message': "Successfully connected to TeamConnect API"
                }
            else:
                logger.warning(f"TeamConnect connection test failed with response: {response}")
                return {
                    'success': False,
                    'message': "Connection failed: Invalid response from health endpoint"
                }
                
        except Exception as e:
            logger.error(f"TeamConnect connection test failed: {str(e)}")
            return {
                'success': False,
                'message': f"Connection failed: {str(e)}"
            }

    def get_rates(self, params: Dict = None) -> List[Dict]:
        """
        Retrieve historical rate data from TeamConnect.
        
        Args:
            params: Query parameters for filtering rates
                   (e.g., timekeeper_ids, effective_dates, etc.)
        
        Returns:
            List[Dict]: List of rate data dictionaries in Justice Bid format
        """
        try:
            logger.debug(f"Retrieving rates from TeamConnect with params: {params}")
            
            # Ensure we're authenticated
            if not self.authenticate():
                logger.error("Failed to authenticate for rate retrieval")
                return []
            
            # Prepare query parameters for TeamConnect API
            query_params = {}
            if params:
                # Map Justice Bid parameter names to TeamConnect parameter names
                if 'timekeeper_ids' in params:
                    query_params['timekeeperID'] = ','.join(params['timekeeper_ids'])
                if 'firm_id' in params:
                    query_params['firmID'] = params['firm_id']
                if 'client_id' in params:
                    query_params['clientID'] = params['client_id']
                if 'effective_after' in params:
                    query_params['effectiveAfter'] = params['effective_after']
                if 'effective_before' in params:
                    query_params['effectiveBefore'] = params['effective_before']
                if 'status' in params:
                    query_params['status'] = params['status']
                if 'limit' in params:
                    query_params['limit'] = params['limit']
                if 'offset' in params:
                    query_params['offset'] = params['offset']
            
            # Make API request to get rates
            response = self.client.get(
                self._endpoints['rates'],
                params=query_params
            )
            
            # Process response
            if not response or 'rates' not in response:
                logger.warning("No rates returned from TeamConnect API")
                return []
            
            # Map each rate from TeamConnect format to Justice Bid format
            mapped_rates = []
            for rate_data in response['rates']:
                try:
                    mapped_rate = self.map_rate_from_teamconnect(rate_data)
                    if mapped_rate:
                        mapped_rates.append(mapped_rate)
                except Exception as e:
                    logger.error(f"Error mapping rate data: {str(e)}")
                    continue
            
            logger.info(f"Retrieved and mapped {len(mapped_rates)} rates from TeamConnect")
            return mapped_rates
            
        except Exception as e:
            logger.error(f"Error retrieving rates from TeamConnect: {str(e)}")
            return []

    def get_timekeepers(self, params: Dict = None) -> List[Dict]:
        """
        Retrieve timekeeper (attorney) data from TeamConnect.
        
        Args:
            params: Query parameters for filtering timekeepers
                   (e.g., firm_id, timekeeper_ids, etc.)
        
        Returns:
            List[Dict]: List of timekeeper data dictionaries in Justice Bid format
        """
        try:
            logger.debug(f"Retrieving timekeepers from TeamConnect with params: {params}")
            
            # Ensure we're authenticated
            if not self.authenticate():
                logger.error("Failed to authenticate for timekeeper retrieval")
                return []
            
            # Prepare query parameters for TeamConnect API
            query_params = {}
            if params:
                # Map Justice Bid parameter names to TeamConnect parameter names
                if 'timekeeper_ids' in params:
                    query_params['timekeeperID'] = ','.join(params['timekeeper_ids'])
                if 'firm_id' in params:
                    query_params['firmID'] = params['firm_id']
                if 'name' in params:
                    query_params['name'] = params['name']
                if 'email' in params:
                    query_params['email'] = params['email']
                if 'staff_class' in params:
                    query_params['staffClass'] = params['staff_class']
                if 'limit' in params:
                    query_params['limit'] = params['limit']
                if 'offset' in params:
                    query_params['offset'] = params['offset']
            
            # Make API request to get timekeepers
            response = self.client.get(
                self._endpoints['timekeepers'],
                params=query_params
            )
            
            # Process response
            if not response or 'timekeepers' not in response:
                logger.warning("No timekeepers returned from TeamConnect API")
                return []
            
            # Map each timekeeper from TeamConnect format to Justice Bid format
            mapped_timekeepers = []
            for timekeeper_data in response['timekeepers']:
                try:
                    mapped_timekeeper = self.map_timekeeper_from_teamconnect(timekeeper_data)
                    if mapped_timekeeper:
                        mapped_timekeepers.append(mapped_timekeeper)
                except Exception as e:
                    logger.error(f"Error mapping timekeeper data: {str(e)}")
                    continue
            
            logger.info(f"Retrieved and mapped {len(mapped_timekeepers)} timekeepers from TeamConnect")
            return mapped_timekeepers
            
        except Exception as e:
            logger.error(f"Error retrieving timekeepers from TeamConnect: {str(e)}")
            return []

    def get_billing_data(self, params: Dict = None) -> List[Dict]:
        """
        Retrieve historical billing data from TeamConnect.
        
        Args:
            params: Query parameters for filtering invoices
                   (e.g., date_range, timekeeper_ids, matter_ids, etc.)
        
        Returns:
            List[Dict]: List of billing data dictionaries in Justice Bid format
        """
        try:
            logger.debug(f"Retrieving billing data from TeamConnect with params: {params}")
            
            # Ensure we're authenticated
            if not self.authenticate():
                logger.error("Failed to authenticate for billing data retrieval")
                return []
            
            # Prepare query parameters for TeamConnect API
            query_params = {}
            if params:
                # Map Justice Bid parameter names to TeamConnect parameter names
                if 'timekeeper_ids' in params:
                    query_params['timekeeperID'] = ','.join(params['timekeeper_ids'])
                if 'firm_id' in params:
                    query_params['firmID'] = params['firm_id']
                if 'client_id' in params:
                    query_params['clientID'] = params['client_id']
                if 'matter_ids' in params:
                    query_params['matterID'] = ','.join(params['matter_ids'])
                if 'start_date' in params:
                    query_params['dateFrom'] = params['start_date']
                if 'end_date' in params:
                    query_params['dateTo'] = params['end_date']
                if 'is_afa' in params:
                    query_params['isAFA'] = str(params['is_afa']).lower()
                if 'limit' in params:
                    query_params['limit'] = params['limit']
                if 'offset' in params:
                    query_params['offset'] = params['offset']
            
            # Make API request to get invoice line items
            response = self.client.get(
                self._endpoints['invoices'],
                params=query_params
            )
            
            # Process response
            if not response or 'invoices' not in response:
                logger.warning("No billing data returned from TeamConnect API")
                return []
            
            # Map each billing item from TeamConnect format to Justice Bid format
            mapped_billing_data = []
            for invoice in response['invoices']:
                if 'lineItems' not in invoice:
                    continue
                    
                for line_item in invoice['lineItems']:
                    try:
                        # Combine invoice metadata with line item data
                        billing_data = {
                            'invoiceID': invoice.get('invoiceID'),
                            'matterID': invoice.get('matterID'),
                            'clientID': invoice.get('clientID'),
                            'firmID': invoice.get('firmID'),
                            'date': invoice.get('date'),
                            'isAFA': invoice.get('isAFA', False),
                            'currency': invoice.get('currency', 'USD'),
                            # Add line item specific data
                            'timekeeperID': line_item.get('timekeeperID'),
                            'hours': line_item.get('hours', 0),
                            'fees': line_item.get('fees', 0),
                            'description': line_item.get('description', '')
                        }
                        
                        mapped_billing = self.map_billing_from_teamconnect(billing_data)
                        if mapped_billing:
                            mapped_billing_data.append(mapped_billing)
                    except Exception as e:
                        logger.error(f"Error mapping billing data: {str(e)}")
                        continue
            
            logger.info(f"Retrieved and mapped {len(mapped_billing_data)} billing records from TeamConnect")
            return mapped_billing_data
            
        except Exception as e:
            logger.error(f"Error retrieving billing data from TeamConnect: {str(e)}")
            return []

    def export_rates(self, rates: List[Dict]) -> Dict:
        """
        Export approved rates to TeamConnect.
        
        Args:
            rates: List of approved rate dictionaries in Justice Bid format
        
        Returns:
            Dict: Export results with success count, failure count, and errors
        """
        if not rates:
            logger.warning("No rates provided for export to TeamConnect")
            return {
                'success': False,
                'message': "No rates provided for export",
                'success_count': 0,
                'failure_count': 0,
                'errors': []
            }
        
        # Ensure we're authenticated
        if not self.authenticate():
            logger.error("Failed to authenticate for rate export")
            return {
                'success': False,
                'message': "Failed to authenticate with TeamConnect",
                'success_count': 0,
                'failure_count': len(rates),
                'errors': ["Authentication failed"]
            }
        
        success_count = 0
        failure_count = 0
        errors = []
        
        logger.info(f"Exporting {len(rates)} rates to TeamConnect")
        
        for rate in rates:
            try:
                # Validate required fields
                if not rate.get('timekeeper_id') or not rate.get('rate_amount'):
                    error_msg = f"Missing required fields in rate: {rate.get('timekeeper_id', 'unknown')}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    failure_count += 1
                    continue
                
                # Validate rate effective date
                if 'effective_date' in rate:
                    try:
                        validate_date(rate['effective_date'], 'effective_date')
                    except Exception as e:
                        error_msg = f"Invalid effective_date for timekeeper {rate.get('timekeeper_id')}: {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                        failure_count += 1
                        continue
                
                # Validate rate amount
                try:
                    validate_rate(rate['rate_amount'], 'rate_amount', rate.get('currency', 'USD'))
                except Exception as e:
                    error_msg = f"Invalid rate_amount for timekeeper {rate.get('timekeeper_id')}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    failure_count += 1
                    continue
                
                # Map Justice Bid rate format to TeamConnect format
                tc_rate = self.map_rate_to_teamconnect(rate)
                
                # Determine if we need to create a new rate or update an existing one
                # Try to get existing rate by timekeeper ID and effective date
                existing_rates = self.client.get(
                    self._endpoints['rates'],
                    params={
                        'timekeeperID': tc_rate['timekeeperID'],
                        'effectiveDate': tc_rate['effectiveDate']
                    }
                )
                
                existing_rate_id = None
                if existing_rates and 'rates' in existing_rates and existing_rates['rates']:
                    existing_rate_id = existing_rates['rates'][0].get('id')
                
                # Either update or create rate
                if existing_rate_id:
                    # Update existing rate
                    response = self.client.put(
                        f"{self._endpoints['rates']}/{existing_rate_id}",
                        json_data=tc_rate
                    )
                    logger.debug(f"Updated existing rate for timekeeper {tc_rate['timekeeperID']}")
                else:
                    # Create new rate
                    response = self.client.post(
                        self._endpoints['rates'],
                        json_data=tc_rate
                    )
                    logger.debug(f"Created new rate for timekeeper {tc_rate['timekeeperID']}")
                
                # Check for successful response
                if response and ('id' in response or 'rate_id' in response):
                    success_count += 1
                else:
                    error_msg = f"Failed to export rate for timekeeper {tc_rate['timekeeperID']}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    failure_count += 1
            
            except Exception as e:
                timekeeper_id = rate.get('timekeeper_id', 'unknown')
                error_msg = f"Error exporting rate for timekeeper {timekeeper_id}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
                failure_count += 1
        
        # Determine overall success
        success = success_count > 0 and failure_count == 0
        
        result = {
            'success': success,
            'message': f"Exported {success_count} rates with {failure_count} failures",
            'success_count': success_count,
            'failure_count': failure_count,
            'errors': errors
        }
        
        logger.info(f"Rate export completed: {success_count} successes, {failure_count} failures")
        return result

    def map_rate_to_teamconnect(self, rate_data: Dict) -> Dict:
        """
        Map Justice Bid rate data to TeamConnect format.
        
        Args:
            rate_data: Rate data in Justice Bid format
        
        Returns:
            Dict: Rate data in TeamConnect format
        """
        tc_rate = {}
        
        # Map fields using the field mappings
        for jb_field, tc_field in self._field_mappings['rate'].items():
            if jb_field in rate_data:
                tc_rate[tc_field] = rate_data[jb_field]
        
        # Ensure required fields are present
        if 'timekeeperID' not in tc_rate and 'attorneyID' in tc_rate:
            tc_rate['timekeeperID'] = tc_rate['attorneyID']
        
        # Format dates correctly for TeamConnect
        if 'effectiveDate' in tc_rate and isinstance(tc_rate['effectiveDate'], datetime.date):
            tc_rate['effectiveDate'] = tc_rate['effectiveDate'].isoformat()
        
        if 'expirationDate' in tc_rate and isinstance(tc_rate['expirationDate'], datetime.date):
            tc_rate['expirationDate'] = tc_rate['expirationDate'].isoformat()
        
        # Default currency if not provided
        if 'currency' not in tc_rate:
            tc_rate['currency'] = 'USD'
        
        # Add type field expected by TeamConnect
        tc_rate['type'] = 'standard'
        
        return tc_rate

    def map_rate_from_teamconnect(self, rate_data: Dict) -> Dict:
        """
        Map TeamConnect rate data to Justice Bid format.
        
        Args:
            rate_data: Rate data in TeamConnect format
        
        Returns:
            Dict: Rate data in Justice Bid format
        """
        jb_rate = {}
        
        # Map fields using the field mappings (reversed)
        for jb_field, tc_field in self._field_mappings['rate'].items():
            if tc_field in rate_data:
                jb_rate[jb_field] = rate_data[tc_field]
        
        # Ensure attorney_id is set if only timekeeper_id is available
        if 'attorney_id' not in jb_rate and 'timekeeper_id' in jb_rate:
            jb_rate['attorney_id'] = jb_rate['timekeeper_id']
        
        # Parse dates from strings to date objects if necessary
        if 'effective_date' in jb_rate and isinstance(jb_rate['effective_date'], str):
            try:
                jb_rate['effective_date'] = datetime.datetime.fromisoformat(jb_rate['effective_date']).date()
            except ValueError:
                logger.warning(f"Could not parse effective_date: {jb_rate['effective_date']}")
        
        if 'expiration_date' in jb_rate and isinstance(jb_rate['expiration_date'], str):
            try:
                jb_rate['expiration_date'] = datetime.datetime.fromisoformat(jb_rate['expiration_date']).date()
            except ValueError:
                logger.warning(f"Could not parse expiration_date: {jb_rate['expiration_date']}")
        
        # Add source system information
        jb_rate['source_system'] = 'TeamConnect'
        jb_rate['integration_type'] = Integration.TEAMCONNECT.value
        
        return jb_rate

    def map_timekeeper_from_teamconnect(self, timekeeper_data: Dict) -> Dict:
        """
        Map TeamConnect timekeeper data to Justice Bid attorney format.
        
        Args:
            timekeeper_data: Timekeeper data in TeamConnect format
        
        Returns:
            Dict: Attorney data in Justice Bid format
        """
        jb_attorney = {}
        
        # Map fields using the field mappings
        for jb_field, tc_field in self._field_mappings['timekeeper'].items():
            if tc_field in timekeeper_data:
                jb_attorney[jb_field] = timekeeper_data[tc_field]
        
        # Construct full name if only first/last name are provided
        if 'name' not in jb_attorney and 'first_name' in jb_attorney and 'last_name' in jb_attorney:
            jb_attorney['name'] = f"{jb_attorney['first_name']} {jb_attorney['last_name']}"
        
        # Parse dates from strings to date objects if necessary
        if 'bar_date' in jb_attorney and isinstance(jb_attorney['bar_date'], str):
            try:
                jb_attorney['bar_date'] = datetime.datetime.fromisoformat(jb_attorney['bar_date']).date()
            except ValueError:
                logger.warning(f"Could not parse bar_date: {jb_attorney['bar_date']}")
        
        if 'graduation_date' in jb_attorney and isinstance(jb_attorney['graduation_date'], str):
            try:
                jb_attorney['graduation_date'] = datetime.datetime.fromisoformat(jb_attorney['graduation_date']).date()
            except ValueError:
                logger.warning(f"Could not parse graduation_date: {jb_attorney['graduation_date']}")
        
        # Add source system information
        jb_attorney['source_system'] = 'TeamConnect'
        jb_attorney['integration_type'] = Integration.TEAMCONNECT.value
        
        # Add timekeeper IDs in the format expected by Justice Bid
        if 'timekeeper_id' in jb_attorney:
            jb_attorney['timekeeper_ids'] = {
                'teamconnect': jb_attorney['timekeeper_id']
            }
        
        return jb_attorney

    def map_billing_from_teamconnect(self, billing_data: Dict) -> Dict:
        """
        Map TeamConnect billing data to Justice Bid format.
        
        Args:
            billing_data: Billing data in TeamConnect format
        
        Returns:
            Dict: Billing data in Justice Bid format
        """
        jb_billing = {}
        
        # Map fields using the field mappings
        for jb_field, tc_field in self._field_mappings['billing'].items():
            if tc_field in billing_data:
                jb_billing[jb_field] = billing_data[tc_field]
        
        # Parse dates from strings to date objects if necessary
        if 'date' in jb_billing and isinstance(jb_billing['date'], str):
            try:
                jb_billing['date'] = datetime.datetime.fromisoformat(jb_billing['date']).date()
            except ValueError:
                logger.warning(f"Could not parse billing date: {jb_billing['date']}")
        
        # Convert numeric fields to appropriate types
        if 'hours' in jb_billing and not isinstance(jb_billing['hours'], float):
            try:
                jb_billing['hours'] = float(jb_billing['hours'])
            except (ValueError, TypeError):
                jb_billing['hours'] = 0.0
        
        if 'fees' in jb_billing and not isinstance(jb_billing['fees'], float):
            try:
                jb_billing['fees'] = float(jb_billing['fees'])
            except (ValueError, TypeError):
                jb_billing['fees'] = 0.0
        
        # Add source system information
        jb_billing['source_system'] = 'TeamConnect'
        jb_billing['integration_type'] = Integration.TEAMCONNECT.value
        
        return jb_billing

    def handle_error(self, error: Exception, operation: str) -> Dict:
        """
        Handle TeamConnect API errors.
        
        Args:
            error: Exception that occurred
            operation: Operation being performed when error occurred
        
        Returns:
            Dict: Error details with message and status
        """
        error_msg = f"TeamConnect error during {operation}: {str(error)}"
        logger.error(error_msg)
        
        # Try to extract response details if it's an API error
        status_code = None
        details = {}
        
        if hasattr(error, 'response') and error.response is not None:
            status_code = error.response.status_code
            
            try:
                error_data = error.response.json()
                details = error_data
                if 'message' in error_data:
                    error_msg = f"TeamConnect API error: {error_data['message']}"
            except (ValueError, AttributeError):
                # Couldn't parse JSON from response
                pass
        
        return {
            'success': False,
            'message': error_msg,
            'status_code': status_code,
            'details': details
        }