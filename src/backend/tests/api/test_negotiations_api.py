import json  # Handle JSON serialization/deserialization in API requests/responses
import pytest  # Python testing framework
import pytest_asyncio  # Support for testing async code in pytest

from src.backend.db import db  # Database access for test setup and verification
from src.backend.db.models.negotiation import NegotiationModel  # Access to negotiation data model for test verification
from src.backend.db.models.rate import RateModel  # Access to rate data model for test verification
from src.backend.tests.conftest import client  # Test client fixture for making API requests
from src.backend.tests.conftest import auth_headers  # Authentication headers fixture for authenticated API requests
from src.backend.tests.conftest import create_user  # Fixture for creating test users
from src.backend.tests.conftest import create_organization  # Fixture for creating test organizations
from src.backend.tests.conftest import create_negotiation  # Fixture for creating test negotiations
from src.backend.tests.conftest import create_rate  # Fixture for creating test rates
from src.backend.api.schemas.negotiations import NegotiationCreate  # Schema for creating negotiations in tests
from src.backend.api.schemas.negotiations import NegotiationUpdate  # Schema for updating negotiations in tests


@pytest.mark.asyncio
async def test_list_negotiations(client, auth_headers, create_user, create_organization, create_negotiation):
    # Create test organizations (client and law firm)
    client_org = await create_organization(name="Client Org")
    law_firm_org = await create_organization(name="Law Firm Org", org_type="law_firm")

    # Create test users for each organization
    client_user = await create_user(organization_id=client_org.id)
    law_firm_user = await create_user(organization_id=law_firm_org.id)

    # Create multiple test negotiations with different statuses
    negotiation1 = await create_negotiation(client_org_id=client_org.id, firm_org_id=law_firm_org.id, status="in_progress")
    negotiation2 = await create_negotiation(client_org_id=client_org.id, firm_org_id=law_firm_org.id, status="completed")
    negotiation3 = await create_negotiation(client_org_id=client_org.id, firm_org_id=law_firm_org.id, status="rejected")

    # Make GET request to /api/v1/negotiations with different query parameters
    response1 = await client.get("/api/v1/negotiations", headers=auth_headers(client_user))
    response2 = await client.get("/api/v1/negotiations?status=in_progress", headers=auth_headers(client_user))
    response3 = await client.get("/api/v1/negotiations?page=2&page_size=1", headers=auth_headers(client_user))

    # Verify response status code is 200
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200

    # Verify the correct negotiations are returned based on filters
    data1 = response1.json()
    assert len(data1["items"]) == 3
    data2 = response2.json()
    assert len(data2["items"]) == 1
    assert data2["items"][0]["status"] == "in_progress"

    # Verify pagination works correctly
    data3 = response3.json()
    assert data3["page"] == 2
    assert data3["size"] == 1
    assert data3["total"] == 3
    assert len(data3["items"]) == 1

    # Test that a user can only see negotiations related to their organization
    unauthorized_user = await create_user()
    response4 = await client.get("/api/v1/negotiations", headers=auth_headers(unauthorized_user))
    assert response4.status_code == 200
    data4 = response4.json()
    assert len(data4["items"]) == 0


@pytest.mark.asyncio
async def test_get_negotiation_by_id(client, auth_headers, create_user, create_organization, create_negotiation):
    # Create test organizations (client and law firm)
    client_org = await create_organization(name="Client Org")
    law_firm_org = await create_organization(name="Law Firm Org", org_type="law_firm")

    # Create test users for each organization
    client_user = await create_user(organization_id=client_org.id)
    law_firm_user = await create_user(organization_id=law_firm_org.id)

    # Create a test negotiation
    negotiation = await create_negotiation(client_org_id=client_org.id, firm_org_id=law_firm_org.id)

    # Make GET request to /api/v1/negotiations/{id}
    response1 = await client.get(f"/api/v1/negotiations/{negotiation.id}", headers=auth_headers(client_user))

    # Verify response status code is 200
    assert response1.status_code == 200

    # Verify correct negotiation details are returned
    data1 = response1.json()
    assert data1["id"] == str(negotiation.id)
    assert data1["client_id"] == str(client_org.id)
    assert data1["firm_id"] == str(law_firm_org.id)

    # Test that a user from an unrelated organization gets a 403 error
    unauthorized_user = await create_user()
    response2 = await client.get(f"/api/v1/negotiations/{negotiation.id}", headers=auth_headers(unauthorized_user))
    assert response2.status_code == 403

    # Test that a non-existent negotiation ID returns a 404 error
    invalid_id = "00000000-0000-0000-0000-000000000000"
    response3 = await client.get(f"/api/v1/negotiations/{invalid_id}", headers=auth_headers(client_user))
    assert response3.status_code == 404


@pytest.mark.asyncio
async def test_create_negotiation(client, auth_headers, create_user, create_organization):
    # Create test organizations (client and law firm)
    client_org = await create_organization(name="Client Org")
    law_firm_org = await create_organization(name="Law Firm Org", org_type="law_firm")

    # Create test users for each organization
    client_user = await create_user(organization_id=client_org.id)
    law_firm_user = await create_user(organization_id=law_firm_org.id)

    # Prepare negotiation creation payload with client_id, firm_id, and other required fields
    payload = {
        "client_id": str(client_org.id),
        "firm_id": str(law_firm_org.id),
        "request_date": "2024-01-01"
    }

    # Make POST request to /api/v1/negotiations
    response1 = await client.post("/api/v1/negotiations", headers=auth_headers(client_user), data=json.dumps(payload))

    # Verify response status code is 201
    assert response1.status_code == 201

    # Verify negotiation is created with correct status
    data1 = response1.json()
    assert data1["client_id"] == str(client_org.id)
    assert data1["firm_id"] == str(law_firm_org.id)
    assert data1["status"] == "requested"

    # Verify response contains negotiation ID
    assert "id" in data1

    # Test validation errors with invalid data
    payload2 = {
        "client_id": "invalid-uuid",
        "firm_id": str(law_firm_org.id),
        "request_date": "2024-01-01"
    }
    response2 = await client.post("/api/v1/negotiations", headers=auth_headers(client_user), data=json.dumps(payload2))
    assert response2.status_code == 400

    # Test permission checks for different user roles
    response3 = await client.post("/api/v1/negotiations", headers=auth_headers(law_firm_user), data=json.dumps(payload))
    assert response3.status_code == 403


@pytest.mark.asyncio
async def test_update_negotiation_status(client, auth_headers, create_user, create_organization, create_negotiation):
    # Create test organizations (client and law firm)
    client_org = await create_organization(name="Client Org")
    law_firm_org = await create_organization(name="Law Firm Org", org_type="law_firm")

    # Create test users for each organization
    client_user = await create_user(organization_id=client_org.id)
    law_firm_user = await create_user(organization_id=law_firm_org.id)

    # Create a test negotiation
    negotiation = await create_negotiation(client_org_id=client_org.id, firm_org_id=law_firm_org.id)

    # Prepare status update payload
    payload = {
        "status": "in_progress"
    }

    # Make PUT request to /api/v1/negotiations/{id}/status
    response1 = await client.put(f"/api/v1/negotiations/{negotiation.id}/status", headers=auth_headers(client_user), data=json.dumps(payload))

    # Verify response status code is 200
    assert response1.status_code == 200

    # Verify negotiation status is updated correctly
    data1 = response1.json()
    assert data1["status"] == "in_progress"

    # Test invalid state transitions return appropriate errors
    payload2 = {
        "status": "completed"
    }
    response2 = await client.put(f"/api/v1/negotiations/{negotiation.id}/status", headers=auth_headers(client_user), data=json.dumps(payload2))
    assert response2.status_code == 422

    # Test permission checks for different user roles
    response3 = await client.put(f"/api/v1/negotiations/{negotiation.id}/status", headers=auth_headers(law_firm_user), data=json.dumps(payload))
    assert response3.status_code == 403


@pytest.mark.asyncio
async def test_submit_rates_for_negotiation(client, auth_headers, create_user, create_organization, create_negotiation, create_rate):
    # Create test organizations (client and law firm)
    client_org = await create_organization(name="Client Org")
    law_firm_org = await create_organization(name="Law Firm Org", org_type="law_firm")

    # Create test users for each organization
    client_user = await create_user(organization_id=client_org.id)
    law_firm_user = await create_user(organization_id=law_firm_org.id)

    # Create a test negotiation in 'Requested' status
    negotiation = await create_negotiation(client_org_id=client_org.id, firm_org_id=law_firm_org.id, status="requested")

    # Create test rates for submission
    rate1 = await create_rate(client_org_id=client_org.id, firm_org_id=law_firm_org.id)
    rate2 = await create_rate(client_org_id=client_org.id, firm_org_id=law_firm_org.id)

    # Prepare rate submission payload
    payload = {
        "rate_ids": [str(rate1.id), str(rate2.id)]
    }

    # Make POST request to /api/v1/negotiations/{id}/submit
    response1 = await client.post(f"/api/v1/negotiations/{negotiation.id}/submit", headers=auth_headers(law_firm_user), data=json.dumps(payload))

    # Verify response status code is 200
    assert response1.status_code == 200

    # Verify negotiation status is updated to 'Submitted'
    data1 = response1.json()
    assert data1["status"] == "in_progress"

    # Verify rates are associated with the negotiation
    # TODO: Implement database check

    # Test validation against rate rules (maximum increase, etc.)
    # TODO: Implement rate rule validation

    # Test submission with invalid negotiation status returns error
    negotiation2 = await create_negotiation(client_org_id=client_org.id, firm_org_id=law_firm_org.id, status="in_progress")
    response2 = await client.post(f"/api/v1/negotiations/{negotiation2.id}/submit", headers=auth_headers(law_firm_user), data=json.dumps(payload))
    assert response2.status_code == 422


@pytest.mark.asyncio
async def test_approve_negotiation(client, auth_headers, create_user, create_organization, create_negotiation, create_rate):
    # Create test organizations (client and law firm)
    client_org = await create_organization(name="Client Org")
    law_firm_org = await create_organization(name="Law Firm Org", org_type="law_firm")

    # Create test users for each organization including approvers
    client_user = await create_user(organization_id=client_org.id)
    law_firm_user = await create_user(organization_id=law_firm_org.id)

    # Create a test negotiation with submitted rates
    negotiation = await create_negotiation(client_org_id=client_org.id, firm_org_id=law_firm_org.id, status="in_progress")
    rate1 = await create_rate(client_org_id=client_org.id, firm_org_id=law_firm_org.id)
    rate2 = await create_rate(client_org_id=client_org.id, firm_org_id=law_firm_org.id)

    # Make POST request to /api/v1/negotiations/{id}/approve
    response1 = await client.post(f"/api/v1/negotiations/{negotiation.id}/approve", headers=auth_headers(client_user))

    # Verify response status code is 200
    assert response1.status_code == 200

    # Verify negotiation status is updated to 'Approved'
    data1 = response1.json()
    assert data1["status"] == "completed"

    # Verify rates are marked as approved
    # TODO: Implement database check

    # Test approval workflow with multiple approvers if configured
    # TODO: Implement approval workflow test

    # Test approval permission checks for different user roles
    # TODO: Implement permission checks


@pytest.mark.asyncio
async def test_reject_negotiation(client, auth_headers, create_user, create_organization, create_negotiation, create_rate):
    # Create test organizations (client and law firm)
    client_org = await create_organization(name="Client Org")
    law_firm_org = await create_organization(name="Law Firm Org", org_type="law_firm")

    # Create test users for each organization
    client_user = await create_user(organization_id=client_org.id)
    law_firm_user = await create_user(organization_id=law_firm_org.id)

    # Create a test negotiation with submitted rates
    negotiation = await create_negotiation(client_org_id=client_org.id, firm_org_id=law_firm_org.id, status="in_progress")
    rate1 = await create_rate(client_org_id=client_org.id, firm_org_id=law_firm_org.id)
    rate2 = await create_rate(client_org_id=client_org.id, firm_org_id=law_firm_org.id)

    # Prepare rejection payload with reason
    payload = {
        "reason": "Rates are too high"
    }

    # Make POST request to /api/v1/negotiations/{id}/reject
    response1 = await client.post(f"/api/v1/negotiations/{negotiation.id}/reject", headers=auth_headers(client_user), data=json.dumps(payload))

    # Verify response status code is 200
    assert response1.status_code == 200

    # Verify negotiation status is updated to 'Rejected'
    data1 = response1.json()
    assert data1["status"] == "rejected"

    # Test rejection permission checks for different user roles
    # TODO: Implement permission checks
    response2 = await client.post(f"/api/v1/negotiations/{negotiation.id}/reject", headers=auth_headers(law_firm_user), data=json.dumps(payload))
    assert response2.status_code == 403


@pytest.mark.asyncio
async def test_counter_propose_rates(client, auth_headers, create_user, create_organization, create_negotiation, create_rate):
    # Create test organizations (client and law firm)
    client_org = await create_organization(name="Client Org")
    law_firm_org = await create_organization(name="Law Firm Org", org_type="law_firm")

    # Create test users for each organization
    client_user = await create_user(organization_id=client_org.id)
    law_firm_user = await create_user(organization_id=law_firm_org.id)

    # Create a test negotiation with submitted rates
    negotiation = await create_negotiation(client_org_id=client_org.id, firm_org_id=law_firm_org.id, status="in_progress")
    rate1 = await create_rate(client_org_id=client_org.id, firm_org_id=law_firm_org.id)
    rate2 = await create_rate(client_org_id=client_org.id, firm_org_id=law_firm_org.id)

    # Prepare counter-proposal payload with rate IDs and counter values
    payload = {
        "counter_proposals": [
            {"rate_id": str(rate1.id), "counter_amount": 450.00},
            {"rate_id": str(rate2.id), "counter_amount": 550.00}
        ]
    }

    # Make POST request to /api/v1/negotiations/{id}/counter
    response1 = await client.post(f"/api/v1/negotiations/{negotiation.id}/counter", headers=auth_headers(client_user), data=json.dumps(payload))

    # Verify response status code is 200
    assert response1.status_code == 200

    # Verify negotiation status is updated to 'ClientCounterProposed' or 'FirmCounterProposed'
    data1 = response1.json()
    assert data1["status"] in ["client_counter_proposed", "firm_counter_proposed"]

    # Verify rates have counter-proposed values
    # TODO: Implement database check

    # Test counter-proposal permission checks for different user roles
    # TODO: Implement permission checks


@pytest.mark.asyncio
async def test_get_negotiation_rates(client, auth_headers, create_user, create_organization, create_negotiation, create_rate):
    # Create test organizations (client and law firm)
    client_org = await create_organization(name="Client Org")
    law_firm_org = await create_organization(name="Law Firm Org", org_type="law_firm")

    # Create test users for each organization
    client_user = await create_user(organization_id=client_org.id)
    law_firm_user = await create_user(organization_id=law_firm_org.id)

    # Create a test negotiation with associated rates
    negotiation = await create_negotiation(client_org_id=client_org.id, firm_org_id=law_firm_org.id, status="in_progress")
    rate1 = await create_rate(client_org_id=client_org.id, firm_org_id=law_firm_org.id)
    rate2 = await create_rate(client_org_id=client_org.id, firm_org_id=law_firm_org.id)

    # Make GET request to /api/v1/negotiations/{id}/rates
    response1 = await client.get(f"/api/v1/negotiations/{negotiation.id}/rates", headers=auth_headers(client_user))

    # Verify response status code is 200
    assert response1.status_code == 200

    # Verify correct rates are returned
    data1 = response1.json()
    assert len(data1) == 0  # No rates associated yet

    # Test filtering options for rates
    # TODO: Implement rate filtering

    # Test permission checks for different user roles
    # TODO: Implement permission checks


@pytest.mark.asyncio
async def test_negotiation_state_transitions(client, auth_headers, create_user, create_organization, create_negotiation):
    # Create test organizations (client and law firm)
    client_org = await create_organization(name="Client Org")
    law_firm_org = await create_organization(name="Law Firm Org", org_type="law_firm")

    # Create test users for each organization
    client_user = await create_user(organization_id=client_org.id)
    law_firm_user = await create_user(organization_id=law_firm_org.id)

    # Create a test negotiation in 'Requested' status
    negotiation = await create_negotiation(client_org_id=client_org.id, firm_org_id=law_firm_org.id, status="requested")

    # Test valid state transitions (e.g., Requested -> Submitted -> UnderReview)
    # TODO: Implement state transition tests

    # Test invalid state transitions return appropriate errors
    # TODO: Implement invalid state transition tests

    # Verify state transition rules are enforced
    # TODO: Implement state transition rule verification

    # Test complete negotiation workflow from request to approval
    # TODO: Implement complete workflow test
    pass


@pytest.mark.asyncio
async def test_negotiation_unauthorized_access(client, auth_headers, create_user, create_organization, create_negotiation):
    # Create test organizations (client and law firm)
    client_org = await create_organization(name="Client Org")
    law_firm_org = await create_organization(name="Law Firm Org", org_type="law_firm")

    # Create test users with different roles and organizations
    client_user = await create_user(organization_id=client_org.id)
    law_firm_user = await create_user(organization_id=law_firm_org.id)
    unauthorized_user = await create_user()

    # Create a test negotiation
    negotiation = await create_negotiation(client_org_id=client_org.id, firm_org_id=law_firm_org.id)

    # Test accessing negotiation with unauthorized user returns 403
    response1 = await client.get(f"/api/v1/negotiations/{negotiation.id}", headers=auth_headers(unauthorized_user))
    assert response1.status_code == 403

    # Test accessing negotiation from unrelated organization returns 403
    response2 = await client.get(f"/api/v1/negotiations/{negotiation.id}", headers=auth_headers(law_firm_user))
    assert response2.status_code == 403

    # Test client user actions on a law firm's behalf returns 403
    payload = {
        "status": "in_progress"
    }
    response3 = await client.put(f"/api/v1/negotiations/{negotiation.id}/status", headers=auth_headers(law_firm_user), data=json.dumps(payload))
    assert response3.status_code == 403

    # Test law firm user actions on a client's behalf returns 403
    response4 = await client.put(f"/api/v1/negotiations/{negotiation.id}/status", headers=auth_headers(client_user), data=json.dumps(payload))
    assert response4.status_code == 403

    # Test unauthenticated access returns 401
    response5 = await client.get(f"/api/v1/negotiations/{negotiation.id}")
    assert response5.status_code == 401