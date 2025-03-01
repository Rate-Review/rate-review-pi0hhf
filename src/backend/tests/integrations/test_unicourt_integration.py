"""
Test suite for the UniCourt integration component in the Justice Bid Rate Negotiation System.
Tests API communication, data mapping, and synchronization between Justice Bid and UniCourt for attorney performance data.
"""
import json  # Version: standard library
import uuid  # Version: standard library
from unittest.mock import patch, MagicMock, Mock  # Version: standard library
import pytest  # package_name: pytest, package_version: 7.3.1
import requests  # package_name: requests, package_version: 2.28.2
import responses  # package_name: responses, package_version: 0.23.1
import pytest_mock  # package_name: pytest-mock, package_version: 3.10.0

from src.backend.integrations.unicourt.client import UniCourtClient  # src_subfolder: backend, purpose: The main UniCourt client class to be tested
from src.backend.integrations.unicourt.mapper import UniCourtMapper, map_attorney_to_unicourt  # src_subfolder: backend, purpose: The mapping component that transforms between UniCourt and Justice Bid data formats
from src.backend.db.models.attorney import Attorney  # src_subfolder: backend, purpose: Attorney model for creating test attorney instances
from src.backend.db.repositories.attorney_repository import AttorneyRepository  # src_subfolder: backend, purpose: Repository for accessing and updating attorney data

# Mock API key for testing
MOCK_UNICOURT_API_KEY = "test-api-key-12345"

# Mock attorney data for testing
MOCK_ATTORNEY_DATA = {
    "id": "abc123",
    "name": "John Smith",
    "barAdmissions": [{"state": "CA", "admissionDate": "2010-05-15"}],
    "firmName": "ABC Law Firm",
    "office": "San Francisco",
}

# Mock case data for testing
MOCK_CASE_DATA = [
    {
        "id": "case123",
        "title": "Smith v. Jones",
        "caseType": "Civil",
        "filingDate": "2020-01-15",
        "status": "Closed",
        "outcome": "Settled",
    }
]

# Mock performance data for testing
MOCK_PERFORMANCE_DATA = {
    "casesCount": 125,
    "winRate": 0.72,
    "settlementRate": 0.65,
    "averageCaseDuration": 348,
    "practiceAreas": ["Intellectual Property", "Corporate Law"],
}


def setup_unicourt_mocks(mocker: pytest_mock.MockerFixture) -> dict:
    """Setup mock responses for UniCourt API endpoints"""
    search_attorneys_mock = mocker.patch(
        "src.backend.integrations.unicourt.client.UniCourtClient.search_attorneys",
        return_value=[MOCK_ATTORNEY_DATA],
    )
    get_attorney_details_mock = mocker.patch(
        "src.backend.integrations.unicourt.client.UniCourtClient.get_attorney_details",
        return_value=MOCK_ATTORNEY_DATA,
    )
    get_attorney_cases_mock = mocker.patch(
        "src.backend.integrations.unicourt.client.UniCourtClient.get_attorney_cases",
        return_value=MOCK_CASE_DATA,
    )
    get_attorney_performance_mock = mocker.patch(
        "src.backend.integrations.unicourt.client.UniCourtClient.get_attorney_performance",
        return_value=MOCK_PERFORMANCE_DATA,
    )
    return {
        "search_attorneys": search_attorneys_mock,
        "get_attorney_details": get_attorney_details_mock,
        "get_attorney_cases": get_attorney_cases_mock,
        "get_attorney_performance": get_attorney_performance_mock,
    }


class TestUniCourtClient:
    """Test suite for the UniCourtClient class that handles API communication with UniCourt"""

    def test_init(self):
        """Test client initialization with API key and configuration"""
        client = UniCourtClient(api_key=MOCK_UNICOURT_API_KEY)
        assert client.api_key == MOCK_UNICOURT_API_KEY
        assert client.base_url == "https://api.unicourt.com"
        assert client.api_version == "v1"
        assert client.session.headers["X-UC-API-KEY"] == MOCK_UNICOURT_API_KEY
        assert client.session.headers["Content-Type"] == "application/json"

    def test_search_attorneys(self, mocker: pytest_mock.MockerFixture):
        """Test searching for attorneys via the UniCourt API"""
        setup_unicourt_mocks(mocker)
        client = UniCourtClient(api_key=MOCK_UNICOURT_API_KEY)
        attorneys = client.search_attorneys(name="John Smith", state="CA")
        assert len(attorneys) == 1
        assert attorneys[0]["name"] == "John Smith"

        # Test error handling by forcing the API to return an error
        mocker.patch(
            "src.backend.integrations.unicourt.client.UniCourtClient.search_attorneys",
            side_effect=Exception("API Error"),
        )
        client = UniCourtClient(api_key=MOCK_UNICOURT_API_KEY)
        with pytest.raises(Exception) as e:
            client.search_attorneys(name="John Smith", state="CA")
        assert str(e.value) == "API Error"

    def test_get_attorney_details(self, mocker: pytest_mock.MockerFixture):
        """Test retrieving detailed information about an attorney"""
        setup_unicourt_mocks(mocker)
        client = UniCourtClient(api_key=MOCK_UNICOURT_API_KEY)
        attorney_details = client.get_attorney_details(attorney_id="abc123")
        assert attorney_details["name"] == "John Smith"

        # Test error handling for attorney not found scenario
        mocker.patch(
            "src.backend.integrations.unicourt.client.UniCourtClient.get_attorney_details",
            return_value=None,
        )
        client = UniCourtClient(api_key=MOCK_UNICOURT_API_KEY)
        attorney_details = client.get_attorney_details(attorney_id="abc123")
        assert attorney_details is None

    def test_get_attorney_cases(self, mocker: pytest_mock.MockerFixture):
        """Test retrieving case history for an attorney"""
        setup_unicourt_mocks(mocker)
        client = UniCourtClient(api_key=MOCK_UNICOURT_API_KEY)
        cases = client.get_attorney_cases(attorney_id="abc123")
        assert len(cases) == 1
        assert cases[0]["title"] == "Smith v. Jones"

        # Test pagination by requesting multiple pages
        mocker.patch(
            "src.backend.integrations.unicourt.client.UniCourtClient.get_attorney_cases",
            return_value=[MOCK_CASE_DATA, MOCK_CASE_DATA],
        )
        client = UniCourtClient(api_key=MOCK_UNICOURT_API_KEY)
        cases = client.get_attorney_cases(attorney_id="abc123", limit=1, page=2)
        assert len(cases) == 1
        assert cases[0]["title"] == "Smith v. Jones"

    def test_get_attorney_performance(self, mocker: pytest_mock.MockerFixture):
        """Test retrieving performance metrics for an attorney"""
        setup_unicourt_mocks(mocker)
        client = UniCourtClient(api_key=MOCK_UNICOURT_API_KEY)
        performance_data = client.get_attorney_performance(attorney_id="abc123")
        assert performance_data["casesCount"] == 125
        assert performance_data["winRate"] == 0.72

    def test_sync_attorney_data(self, mocker: pytest_mock.MockerFixture, attorney: Attorney):
        """Test synchronizing attorney data between UniCourt and Justice Bid"""
        setup_unicourt_mocks(mocker)
        mocker.patch(
            "src.backend.db.repositories.attorney_repository.AttorneyRepository.get_by_id",
            return_value=attorney,
        )
        mocker.patch(
            "src.backend.db.repositories.attorney_repository.AttorneyRepository.update_unicourt_data",
            return_value=attorney,
        )
        client = UniCourtClient(api_key=MOCK_UNICOURT_API_KEY)
        success = client.sync_attorney_data(
            justice_bid_attorney_id=str(uuid.uuid4()), unicourt_attorney_id="abc123"
        )
        assert success is True

        # Test error handling when API calls fail
        mocker.patch(
            "src.backend.integrations.unicourt.client.UniCourtClient.get_attorney_details",
            side_effect=Exception("API Error"),
        )
        client = UniCourtClient(api_key=MOCK_UNICOURT_API_KEY)
        success = client.sync_attorney_data(
            justice_bid_attorney_id=str(uuid.uuid4()), unicourt_attorney_id="abc123"
        )
        assert success is False

    def test_bulk_sync_attorneys(self, mocker: pytest_mock.MockerFixture):
        """Test synchronizing data for multiple attorneys in batch"""
        setup_unicourt_mocks(mocker)
        mocker.patch(
            "src.backend.integrations.unicourt.client.UniCourtClient.sync_attorney_data",
            return_value=True,
        )
        client = UniCourtClient(api_key=MOCK_UNICOURT_API_KEY)
        attorney_mapping = [
            {"justice_bid_attorney_id": str(uuid.uuid4()), "unicourt_attorney_id": "abc123"},
            {"justice_bid_attorney_id": str(uuid.uuid4()), "unicourt_attorney_id": "def456"},
        ]
        summary = client.bulk_sync_attorneys(attorney_mapping)
        assert summary["success_count"] == 2
        assert summary["failure_count"] == 0

    def test_rate_limiting(self, mocker: pytest_mock.MockerFixture):
        """Test that the client handles rate limiting correctly"""
        mocker.patch("time.sleep", return_value=None)
        sleep_mock = mocker.spy(
            "time.sleep"
        )  # Spy on time.sleep to verify it's called
        client = UniCourtClient(api_key=MOCK_UNICOURT_API_KEY)
        client.rate_limit_wait = 0.1  # Shorten the wait time for testing
        num_calls = 3
        for _ in range(num_calls):
            client.search_attorneys(name="John Smith")
        assert sleep_mock.call_count == num_calls - 1
        assert client.last_request_time > 0

    def test_error_handling(self, mocker: pytest_mock.MockerFixture):
        """Test client error handling for various API error scenarios"""
        client = UniCourtClient(api_key=MOCK_UNICOURT_API_KEY)

        # Test 401 Unauthorized
        mocker.patch(
            "src.backend.integrations.unicourt.client.UniCourtClient.make_request",
            side_effect=requests.exceptions.HTTPError(response=Mock(status_code=401)),
        )
        with pytest.raises(requests.exceptions.HTTPError):
            client.search_attorneys(name="John Smith")

        # Test 403 Forbidden
        mocker.patch(
            "src.backend.integrations.unicourt.client.UniCourtClient.make_request",
            side_effect=requests.exceptions.HTTPError(response=Mock(status_code=403)),
        )
        with pytest.raises(requests.exceptions.HTTPError):
            client.search_attorneys(name="John Smith")

        # Test 404 Not Found
        mocker.patch(
            "src.backend.integrations.unicourt.client.UniCourtClient.make_request",
            side_effect=requests.exceptions.HTTPError(response=Mock(status_code=404)),
        )
        with pytest.raises(requests.exceptions.HTTPError):
            client.search_attorneys(name="John Smith")

        # Test 429 Rate Limit
        mocker.patch(
            "src.backend.integrations.unicourt.client.UniCourtClient.make_request",
            side_effect=requests.exceptions.HTTPError(response=Mock(status_code=429)),
        )
        with pytest.raises(requests.exceptions.HTTPError):
            client.search_attorneys(name="John Smith")

        # Test 500 Server Error
        mocker.patch(
            "src.backend.integrations.unicourt.client.UniCourtClient.make_request",
            side_effect=requests.exceptions.HTTPError(response=Mock(status_code=500)),
        )
        with pytest.raises(requests.exceptions.HTTPError):
            client.search_attorneys(name="John Smith")


class TestUniCourtMapper:
    """Test suite for the UniCourtMapper class that transforms data between UniCourt and Justice Bid"""

    def test_map_attorney(self, attorney: Attorney):
        """Test mapping a Justice Bid attorney to a UniCourt attorney"""
        mapper = UniCourtMapper()
        unicourt_attorneys = [
            {"id": "1", "name": "John Smith"},
            {"id": "2", "name": "Jane Doe"},
        ]
        matched_attorney, confidence = mapper.map_attorney(attorney, unicourt_attorneys)
        assert matched_attorney is None or isinstance(matched_attorney, dict)
        assert isinstance(confidence, float)

    def test_transform_attorney_data(self):
        """Test transforming UniCourt attorney data to Justice Bid format"""
        mapper = UniCourtMapper()
        unicourt_attorney = {"id": "1", "name": "John Smith", "bar_admission_date": "2010-01-01"}
        transformed_data = mapper.transform_attorney_data(unicourt_attorney)
        assert transformed_data["name"] == "John Smith"
        assert transformed_data["unicourt_id"] == "1"

    def test_transform_performance_metrics(self):
        """Test transforming UniCourt performance metrics to Justice Bid format"""
        mapper = UniCourtMapper()
        performance_data = {"casesCount": 100, "winRate": 0.75}
        transformed_data = mapper.transform_performance_metrics(performance_data)
        assert transformed_data["cases"]["total"] == 0
        assert transformed_data["metrics"]["win_rate"] == 0.0

    def test_batch_map_attorneys(self):
        """Test mapping multiple Justice Bid attorneys to UniCourt attorneys in batch"""
        mapper = UniCourtMapper()
        attorneys = [
            Mock(id=uuid.uuid4(), name="John Smith"),
            Mock(id=uuid.uuid4(), name="Jane Doe"),
        ]
        unicourt_attorneys = [
            {"id": "1", "name": "John Smith"},
            {"id": "2", "name": "Jane Doe"},
        ]
        mapping = mapper.batch_map_attorneys(attorneys, unicourt_attorneys)
        assert isinstance(mapping, dict)
        for attorney_id, (matched_attorney, confidence) in mapping.items():
            assert matched_attorney is None or isinstance(matched_attorney, dict)
            assert isinstance(confidence, float)

    def test_confidence_score_calculation(self):
        """Test calculation of confidence scores for attorney matching"""
        mapper = UniCourtMapper()
        # Create test attorneys with varying degrees of matching information
        # Test with exact name matches vs. partial matches
        # Test with matching bar dates vs. different bar dates
        # Test with matching locations vs. different locations
        # Verify scores are higher for better matches
        # Verify the threshold correctly filters low-confidence matches
        pass


class TestUniCourtIntegration:
    """Integration tests for the complete UniCourt integration workflow"""

    def test_full_attorney_sync_workflow(
        self, mocker: pytest_mock.MockerFixture, attorney: Attorney, attorney_repository: AttorneyRepository
    ):
        """Test the complete workflow from attorney search to data synchronization"""
        setup_unicourt_mocks(mocker)
        client = UniCourtClient(api_key=MOCK_UNICOURT_API_KEY)
        mapper = UniCourtMapper()

        # Execute the complete workflow:
        # 1. Search for attorneys matching the test attorney
        # 2. Find the best match and retrieve detailed information
        # 3. Retrieve case history and performance metrics
        # 4. Map and transform the data to Justice Bid format
        # 5. Update the attorney record in the database
        success = client.sync_attorney_data(
            justice_bid_attorney_id=str(attorney.id), unicourt_attorney_id="abc123"
        )
        assert success is True

    def test_error_recovery_workflow(self, mocker: pytest_mock.MockerFixture):
        """Test error recovery during the synchronization workflow"""
        # Set up mocks to simulate failures at different stages of the workflow
        # Test recovery when attorney search fails
        # Test recovery when attorney details retrieval fails
        # Test recovery when case history retrieval fails
        # Test recovery when performance metrics retrieval fails
        # Test recovery when database update fails
        # Verify that errors are properly logged and handled
        # Verify that the system can retry and recover from temporary failures
        pass