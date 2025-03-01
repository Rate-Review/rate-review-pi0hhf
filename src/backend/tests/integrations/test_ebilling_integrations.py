"""Test suite for eBilling system integrations including TeamConnect, Onit, LegalTracker, and BrightFlag.
Tests API interactions, data mapping, and error handling.
"""
import pytest  # package_version: ^7.0.0
from unittest.mock import patch  # package_version: Built-in
import requests  # package_version: ^2.28.0
import json  # package_version: Built-in
import xml.etree.ElementTree as ET  # package_version: Built-in

from src.backend.integrations.ebilling.teamconnect import TeamConnectClient  # Internal import
from src.backend.integrations.ebilling.onit import OnitClient  # Internal import
from src.backend.integrations.ebilling.legal_tracker import LegalTrackerClient  # Internal import
from src.backend.integrations.ebilling.brightflag import BrightFlagClient  # Internal import
from src.backend.integrations.common.adapter import IntegrationAdapter  # Internal import
from src.backend.integrations.common.mapper import FieldMapper  # Internal import

# Mock configurations for different eBilling systems
MOCK_TEAMCONNECT_CONFIG = '{"base_url": "https://api.teamconnect.example.com", "api_key": "test_key", "client_id": "test_client"}'
MOCK_ONIT_CONFIG = '{"base_url": "https://api.onit.example.com", "api_key": "test_key", "client_id": "test_client"}'
MOCK_LEGALTRACKER_CONFIG = '{"base_url": "https://api.legaltracker.example.com", "api_key": "test_key", "client_id": "test_client"}'
MOCK_BRIGHTFLAG_CONFIG = '{"base_url": "https://api.brightflag.example.com", "api_key": "test_key", "client_id": "test_client"}'

# Mock data for rates and attorneys
MOCK_RATE_DATA = '[{"attorney_id": "12345", "rate": 750.00, "currency": "USD", "effective_date": "2023-01-01"}]'
MOCK_ATTORNEY_DATA = '[{"id": "12345", "name": "John Smith", "email": "john.smith@example.com", "bar_date": "2010-01-01"}]'

@pytest.fixture
def mock_teamconnect_config():
    """Pytest fixture that provides mock TeamConnect configuration"""
    return json.loads(MOCK_TEAMCONNECT_CONFIG)

@pytest.fixture
def mock_onit_config():
    """Pytest fixture that provides mock Onit configuration"""
    return json.loads(MOCK_ONIT_CONFIG)

@pytest.fixture
def mock_legal_tracker_config():
    """Pytest fixture that provides mock LegalTracker configuration"""
    return json.loads(MOCK_LEGALTRACKER_CONFIG)

@pytest.fixture
def mock_brightflag_config():
    """Pytest fixture that provides mock BrightFlag configuration"""
    return json.loads(MOCK_BRIGHTFLAG_CONFIG)

@pytest.fixture
def mock_rate_data():
    """Pytest fixture that provides mock rate data"""
    return json.loads(MOCK_RATE_DATA)

@pytest.fixture
def mock_attorney_data():
    """Pytest fixture that provides mock attorney data"""
    return json.loads(MOCK_ATTORNEY_DATA)

@pytest.mark.integration
def test_teamconnect_client_initialization(mock_teamconnect_config):
    """Test initialization of TeamConnect client with valid configuration"""
    # Create a config dictionary with required parameters
    config = mock_teamconnect_config

    # Initialize TeamConnectClient with the config
    client = TeamConnectClient(config)

    # Assert that the client has the correct base URL and authentication details
    assert client.base_url == config["base_url"]
    assert client.api_key == config["api_key"]
    assert client.client_id == config["client_id"]

@pytest.mark.integration
@patch('requests.get')
def test_teamconnect_client_get_rates(mock_get, mock_teamconnect_config, mock_rate_data):
    """Test fetching rates from TeamConnect API"""
    # Set up mock response for the rates endpoint
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"rates": json.loads(mock_rate_data)}

    # Create a TeamConnectClient instance
    client = TeamConnectClient(mock_teamconnect_config)

    # Call get_rates method
    rates = client.get_rates({})

    # Assert that the correct endpoint was called
    mock_get.assert_called_with(f'{mock_teamconnect_config["base_url"]}/api/rates', params={})

    # Assert that the returned data matches the expected format
    assert len(rates) == 1
    assert rates[0]["attorney_id"] == "12345"
    assert rates[0]["rate"] == 750.00
    assert rates[0]["currency"] == "USD"

@pytest.mark.integration
@patch('requests.post')
def test_teamconnect_client_update_rates(mock_post, mock_teamconnect_config, mock_rate_data):
    """Test updating rates through TeamConnect API"""
    # Set up mock response for the update rates endpoint
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}

    # Create a TeamConnectClient instance
    client = TeamConnectClient(mock_teamconnect_config)

    # Call update_rates method with mock rate data
    rates = json.loads(MOCK_RATE_DATA)
    response = client.update_rates(rates[0])

    # Assert that the correct endpoint was called with correct data
    mock_post.assert_called_with(f'{mock_teamconnect_config["base_url"]}/api/rates', json=rates[0])

    # Assert that the returned response indicates success
    assert response["success"] == True

@pytest.mark.integration
@patch('requests.get')
def test_teamconnect_client_error_handling(mock_get, mock_teamconnect_config):
    """Test error handling in TeamConnect client"""
    # Set up mock response with error status code
    mock_response = mock_get.return_value
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Bad Request", response=mock_response)

    # Create a TeamConnectClient instance
    client = TeamConnectClient(mock_teamconnect_config)

    # Call get_rates method and assert it raises appropriate exception
    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        client.get_rates({})
    assert "Bad Request" in str(excinfo.value)

    # Verify error details are correctly captured
    assert mock_get.call_count == 1

@pytest.mark.integration
def test_onit_client_initialization(mock_onit_config):
    """Test initialization of Onit client with valid configuration"""
    # Create a config dictionary with required parameters
    config = mock_onit_config

    # Initialize OnitClient with the config
    client = OnitClient(config)

    # Assert that the client has the correct base URL and authentication details
    assert client.base_url == config["base_url"]
    assert client.api_key == config["api_key"]
    assert client.client_id == config["client_id"]

@pytest.mark.integration
@patch('requests.get')
def test_onit_client_get_rates(mock_get, mock_onit_config, mock_rate_data):
    """Test fetching rates from Onit API"""
    # Set up mock response for the rates endpoint
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"rates": json.loads(mock_rate_data)}

    # Create an OnitClient instance
    client = OnitClient(mock_onit_config)

    # Call get_rates method
    rates = client.get_rates({})

    # Assert that the correct endpoint was called
    mock_get.assert_called_with(f'{mock_onit_config["base_url"]}/api/rates', params={})

    # Assert that the returned data matches the expected format
    assert len(rates) == 1
    assert rates[0]["attorney_id"] == "12345"
    assert rates[0]["rate"] == 750.00
    assert rates[0]["currency"] == "USD"

@pytest.mark.integration
@patch('requests.post')
def test_onit_client_update_rates(mock_post, mock_onit_config, mock_rate_data):
    """Test updating rates through Onit API"""
    # Set up mock response for the update rates endpoint
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}

    # Create an OnitClient instance
    client = OnitClient(mock_onit_config)

    # Call update_rates method with mock rate data
    rates = json.loads(MOCK_RATE_DATA)
    response = client.update_rates(rates[0])

    # Assert that the correct endpoint was called with correct data
    mock_post.assert_called_with(f'{mock_onit_config["base_url"]}/api/rates', json=rates[0])

    # Assert that the returned response indicates success
    assert response["success"] == True

@pytest.mark.integration
def test_legal_tracker_client_initialization(mock_legal_tracker_config):
    """Test initialization of LegalTracker client with valid configuration"""
    # Create a config dictionary with required parameters
    config = mock_legal_tracker_config

    # Initialize LegalTrackerClient with the config
    client = LegalTrackerClient(config)

    # Assert that the client has the correct base URL and authentication details
    assert client.base_url == config["base_url"]
    assert client.api_key == config["api_key"]

@pytest.mark.integration
@patch('requests.get')
def test_legal_tracker_client_get_rates(mock_get, mock_legal_tracker_config, mock_rate_data):
    """Test fetching rates from LegalTracker API"""
    # Set up mock response for the rates endpoint
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"rates": json.loads(mock_rate_data)}

    # Create a LegalTrackerClient instance
    client = LegalTrackerClient(mock_legal_tracker_config)

    # Call get_rates method
    rates = client.get_rates({})

    # Assert that the correct endpoint was called
    mock_get.assert_called_with(f'{mock_legal_tracker_config["base_url"]}/api/rates', params={})

    # Assert that the returned data matches the expected format
    assert len(rates) == 1
    assert rates[0]["attorney_id"] == "12345"
    assert rates[0]["rate"] == 750.00
    assert rates[0]["currency"] == "USD"

@pytest.mark.integration
@patch('requests.post')
def test_legal_tracker_client_update_rates(mock_post, mock_legal_tracker_config, mock_rate_data):
    """Test updating rates through LegalTracker API"""
    # Set up mock response for the update rates endpoint
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}

    # Create a LegalTrackerClient instance
    client = LegalTrackerClient(mock_legal_tracker_config)

    # Call update_rates method with mock rate data
    rates = json.loads(MOCK_RATE_DATA)
    response = client.update_rates(rates[0])

    # Assert that the correct endpoint was called with correct data
    mock_post.assert_called_with(f'{mock_legal_tracker_config["base_url"]}/api/rates', json=rates[0])

    # Assert that the returned response indicates success
    assert response["success"] == True

@pytest.mark.integration
def test_brightflag_client_initialization(mock_brightflag_config):
    """Test initialization of BrightFlag client with valid configuration"""
    # Create a config dictionary with required parameters
    config = mock_brightflag_config

    # Initialize BrightFlagClient with the config
    client = BrightFlagClient(config["api_key"], config["client_id"])

    # Assert that the client has the correct base URL and authentication details
    assert client.base_url == "https://api.brightflag.com/v1"
    assert client.api_key == config["api_key"]
    assert client.client_id == config["client_id"]

@pytest.mark.integration
@patch('requests.get')
def test_brightflag_client_get_rates(mock_get, mock_brightflag_config, mock_rate_data):
    """Test fetching rates from BrightFlag API"""
    # Set up mock response for the rates endpoint
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = json.loads(mock_rate_data)

    # Create a BrightFlagClient instance
    client = BrightFlagClient(mock_brightflag_config["api_key"], mock_brightflag_config["client_id"])

    # Call get_rates method
    rates = client.get_rates("vendor123", datetime(2023, 1, 1), datetime(2023, 1, 31))

    # Assert that the correct endpoint was called
    mock_get.assert_called_with('https://api.brightflag.com/v1/vendors/vendor123/rates', params={'start_date': '2023-01-01', 'end_date': '2023-01-31'})

    # Assert that the returned data matches the expected format
    assert len(rates) == 1
    assert rates[0]["attorney_id"] == "12345"
    assert rates[0]["rate"] == 750.00
    assert rates[0]["currency"] == "USD"

@pytest.mark.integration
@patch('requests.post')
def test_brightflag_client_update_rates(mock_post, mock_brightflag_config, mock_rate_data):
    """Test updating rates through BrightFlag API"""
    # Set up mock response for the update rates endpoint
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}

    # Create a BrightFlagClient instance
    client = BrightFlagClient(mock_brightflag_config["api_key"], mock_brightflag_config["client_id"])

    # Call update_rates method with mock rate data
    rates = json.loads(MOCK_RATE_DATA)
    response = client.update_rates(rates)

    # Assert that the correct endpoint was called with correct data
    mock_post.assert_called_with('/rates/bulk_update', json={'rates': rates})

    # Assert that the returned response indicates success
    assert response["success"] == True

@pytest.mark.integration
def test_integration_adapter_validation():
    """Test validation method of integration adapter"""
    # Create a mock integration adapter
    class MockIntegrationAdapter(IntegrationAdapter):
        def __init__(self, base_url, auth_credentials):
            super().__init__(base_url=base_url, auth_credentials=auth_credentials)

        def validate_connection(self):
            if self.base_url == "valid_url" and self.auth_credentials == {"api_key": "valid_key"}:
                return True
            else:
                raise ValueError("Invalid configuration")

    # Test validation with valid configuration
    adapter = MockIntegrationAdapter(base_url="valid_url", auth_credentials={"api_key": "valid_key"})
    assert adapter.validate_connection() == True

    # Test validation with invalid configuration
    adapter = MockIntegrationAdapter(base_url="invalid_url", auth_credentials={"api_key": "invalid_key"})
    with pytest.raises(ValueError) as excinfo:
        adapter.validate_connection()
    assert "Invalid configuration" in str(excinfo.value)

class TestTeamConnectIntegration:
    """Test class for TeamConnect integration functionality"""
    @pytest.mark.integration
    def setup_method(self, method):
        """Set up test environment before each test method"""
        # Create mock configuration for TeamConnect client
        self.config = {
            "base_url": "https://api.teamconnect.example.com",
            "api_key": "test_key",
            "client_id": "test_client"
        }
        # Initialize necessary test data
        self.rate_data = json.loads(MOCK_RATE_DATA)
        self.attorney_data = json.loads(MOCK_ATTORNEY_DATA)

    @pytest.mark.integration
    @patch('requests.get')
    def test_get_attorneys(self, mock_get):
        """Test fetching attorney data from TeamConnect"""
        # Mock the HTTP response for attorney endpoint
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"timekeepers": self.attorney_data}

        # Initialize TeamConnect client
        client = TeamConnectClient(self.config)

        # Call get_attorneys method
        attorneys = client.get_timekeepers({})

        # Verify correct endpoint was called
        mock_get.assert_called_with(f'{self.config["base_url"]}/api/timekeepers', params={})

        # Verify response data mapping
        assert len(attorneys) == 1
        assert attorneys[0]["name"] == "John Smith"
        assert attorneys[0]["email"] == "john.smith@example.com"

    @pytest.mark.integration
    def test_rate_data_mapping(self):
        """Test mapping between system rate data and TeamConnect format"""
        # Create sample internal rate data
        internal_rate_data = {
            "attorney_id": "123",
            "rate_amount": 750.00,
            "currency": "USD",
            "effective_date": "2023-01-01"
        }

        # Initialize FieldMapper with TeamConnect mappings
        field_mappings = {
            "timekeeperID": "attorney_id",
            "amount": "rate_amount",
            "currency": "currency",
            "effectiveDate": "effective_date"
        }
        mapper = FieldMapper(field_mappings)

        # Call mapping function to convert to TeamConnect format
        teamconnect_rate_data = mapper.map_data(internal_rate_data)

        # Verify field mappings are correct
        assert teamconnect_rate_data["timekeeperID"] == "123"
        assert teamconnect_rate_data["amount"] == 750.00
        assert teamconnect_rate_data["currency"] == "USD"
        assert teamconnect_rate_data["effectiveDate"] == "2023-01-01"

        # Test reverse mapping from TeamConnect to internal format
        reverse_mapped_data = mapper.reverse_map_data(teamconnect_rate_data)
        assert reverse_mapped_data["attorney_id"] == "123"
        assert reverse_mapped_data["rate_amount"] == 750.00
        assert reverse_mapped_data["currency"] == "USD"
        assert reverse_mapped_data["effective_date"] == "2023-01-01"

    @pytest.mark.integration
    @patch('requests.get')
    def test_connection_retry(self, mock_get):
        """Test connection retry logic for TeamConnect client"""
        # Mock HTTP errors for first N attempts
        mock_response = mock_get.return_value
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = [requests.exceptions.HTTPError("Server Error", response=mock_response)] * 2 + [None]
        mock_response.json.return_value = {"rates": []}

        # Configure client with retry settings
        config = self.config.copy()
        config["max_retries"] = 3
        client = TeamConnectClient(config)

        # Call an API method
        rates = client.get_rates({})

        # Verify retry behavior and successful response after retries
        assert mock_get.call_count == 3
        assert rates == []

class TestOnitIntegration:
    """Test class for Onit integration functionality"""
    @pytest.mark.integration
    def setup_method(self, method):
        """Set up test environment before each test method"""
        # Create mock configuration for Onit client
        self.config = {
            "base_url": "https://api.onit.example.com",
            "api_key": "test_key",
            "client_id": "test_client"
        }
        # Initialize necessary test data
        self.rate_data = json.loads(MOCK_RATE_DATA)
        self.attorney_data = json.loads(MOCK_ATTORNEY_DATA)

    @pytest.mark.integration
    @patch('requests.get')
    def test_get_attorneys(self, mock_get):
        """Test fetching attorney data from Onit"""
        # Mock the HTTP response for attorney endpoint
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"timekeepers": self.attorney_data}

        # Initialize Onit client
        client = OnitClient(self.config)

        # Call get_attorneys method
        attorneys = client.get_timekeepers({})

        # Verify correct endpoint was called
        mock_get.assert_called_with(f'{self.config["base_url"]}/api/timekeepers', params={})

        # Verify response data mapping
        assert len(attorneys) == 1
        assert attorneys[0]["name"] == "John Smith"
        assert attorneys[0]["email"] == "john.smith@example.com"

    @pytest.mark.integration
    def test_rate_data_mapping(self):
        """Test mapping between system rate data and Onit format"""
        # Create sample internal rate data
        internal_rate_data = {
            "attorney_id": "123",
            "rate_amount": 750.00,
            "currency": "USD",
            "effective_date": "2023-01-01"
        }

        # Initialize FieldMapper with Onit mappings
        field_mappings = {
            "timekeeperID": "attorney_id",
            "amount": "rate_amount",
            "currency": "currency",
            "effectiveDate": "effective_date"
        }
        mapper = FieldMapper(field_mappings)

        # Call mapping function to convert to Onit format
        onit_rate_data = mapper.map_data(internal_rate_data)

        # Verify field mappings are correct
        assert onit_rate_data["timekeeperID"] == "123"
        assert onit_rate_data["amount"] == 750.00
        assert onit_rate_data["currency"] == "USD"
        assert onit_rate_data["effectiveDate"] == "2023-01-01"

        # Test reverse mapping from Onit to internal format
        reverse_mapped_data = mapper.reverse_map_data(onit_rate_data)
        assert reverse_mapped_data["attorney_id"] == "123"
        assert reverse_mapped_data["rate_amount"] == 750.00
        assert reverse_mapped_data["currency"] == "USD"
        assert reverse_mapped_data["effective_date"] == "2023-01-01"

class TestLegalTrackerIntegration:
    """Test class for LegalTracker integration functionality"""
    @pytest.mark.integration
    def setup_method(self, method):
        """Set up test environment before each test method"""
        # Create mock configuration for LegalTracker client
        self.config = {
            "base_url": "https://api.legaltracker.example.com",
            "api_key": "test_key",
            "client_id": "test_client"
        }
        # Initialize necessary test data
        self.rate_data = json.loads(MOCK_RATE_DATA)
        self.attorney_data = json.loads(MOCK_ATTORNEY_DATA)

    @pytest.mark.integration
    @patch('requests.get')
    def test_get_attorneys(self, mock_get):
        """Test fetching attorney data from LegalTracker"""
        # Mock the HTTP response for attorney endpoint
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"timekeepers": self.attorney_data}

        # Initialize LegalTracker client
        client = LegalTrackerClient(self.config)

        # Call get_attorneys method
        attorneys = client.get_timekeepers({})

        # Verify correct endpoint was called
        mock_get.assert_called_with(f'{self.config["base_url"]}/api/timekeepers', params={})

        # Verify response data mapping
        assert len(attorneys) == 1
        assert attorneys[0]["name"] == "John Smith"
        assert attorneys[0]["email"] == "john.smith@example.com"

    @pytest.mark.integration
    @patch('requests.get')
    def test_xml_response_handling(self, mock_get):
        """Test handling of XML responses from LegalTracker"""
        # Mock XML response from LegalTracker API
        xml_response = """
        <timekeepers>
            <timekeeper>
                <id>123</id>
                <firstName>John</firstName>
                <lastName>Smith</lastName>
                <emailAddress>john.smith@example.com</emailAddress>
            </timekeeper>
        </timekeepers>
        """
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.text = xml_response

        # Initialize LegalTracker client
        client = LegalTrackerClient(self.config)

        # Call client method that processes XML
        # Verify correct parsing and data extraction
        # This test assumes that the get_timekeepers method is adapted to handle XML responses
        # and that the client has a method to parse XML
        pass

class TestBrightFlagIntegration:
    """Test class for BrightFlag integration functionality"""
    @pytest.mark.integration
    def setup_method(self, method):
        """Set up test environment before each test method"""
        # Create mock configuration for BrightFlag client
        self.config = {
            "base_url": "https://api.brightflag.example.com",
            "api_key": "test_key",
            "client_id": "test_client"
        }
        # Initialize necessary test data
        self.rate_data = json.loads(MOCK_RATE_DATA)
        self.attorney_data = json.loads(MOCK_ATTORNEY_DATA)

    @pytest.mark.integration
    @patch('requests.get')
    def test_get_attorneys(self, mock_get):
        """Test fetching attorney data from BrightFlag"""
        # Mock the HTTP response for attorney endpoint
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = self.attorney_data

        # Initialize BrightFlag client
        client = BrightFlagClient(self.config["api_key"], self.config["client_id"])

        # Call get_attorneys method
        attorneys = client.get_timekeepers("vendor123")

        # Verify correct endpoint was called
        mock_get.assert_called_with('https://api.brightflag.example.com/v1/vendors/vendor123/timekeepers')

        # Verify response data mapping
        assert len(attorneys) == 1
        assert attorneys[0]["name"] == "John Smith"
        assert attorneys[0]["email"] == "john.smith@example.com"

    @pytest.mark.integration
    @patch('requests.get')
    def test_analytics_data_retrieval(self, mock_get):
        """Test fetching analytics data from BrightFlag"""
        # Mock the HTTP response for analytics endpoint
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"analytics_data": []}

        # Initialize BrightFlag client
        client = BrightFlagClient(self.config["api_key"], self.config["client_id"])

        # Call get_analytics method
        analytics_data = client.get_billing_data("vendor123", datetime(2023, 1, 1), datetime(2023, 1, 31))

        # Verify correct endpoint was called
        mock_get.assert_called_with('https://api.brightflag.example.com/v1/vendors/vendor123/billing_data', params={'start_date': '2023-01-01', 'end_date': '2023-01-31'})

        # Verify response data mapping
        assert analytics_data == []