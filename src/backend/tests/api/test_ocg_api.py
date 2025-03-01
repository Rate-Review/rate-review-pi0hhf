import json
from uuid import UUID

import pytest  # pytest version: latest

from src.backend.db.models.ocg import OCG
from src.backend.db.models.organization import Organization
from src.backend.api.schemas.ocg import OCGCreate, OCGSectionCreate


def test_create_ocg(client, auth_headers, db_session):
    """Test creating a new OCG document"""
    # Create a test client organization
    client_org = Organization(name="Test Client", type="client", domain="test.com")
    db_session.add(client_org)
    db_session.commit()

    # Prepare valid OCG data with sections and alternatives
    ocg_data = {
        "name": "Test OCG",
        "client_id": str(client_org.id),
        "version": 1,
        "total_points": 10,
        "default_firm_point_budget": 5,
        "sections": []
    }

    # Make a POST request to /api/v1/ocg endpoint with the OCG data
    response = client.post("/api/v1/ocg", headers=auth_headers, data=json.dumps(ocg_data))

    # Assert that the response status code is 201 (Created)
    assert response.status_code == 201

    # Assert that the response JSON contains the expected OCG data
    response_data = response.get_json()
    assert response_data["name"] == "Test OCG"
    assert response_data["client_id"] == str(client_org.id)
    assert response_data["version"] == 1
    assert response_data["total_points"] == 10
    assert response_data["default_firm_point_budget"] == 5

    # Assert that the OCG has been created in the database
    ocg = db_session.query(OCG).filter(OCG.id == response_data["id"]).first()
    assert ocg is not None
    assert ocg.name == "Test OCG"
    assert str(ocg.client_id) == str(client_org.id)


def test_get_ocg(client, auth_headers, db_session):
    """Test retrieving an existing OCG document"""
    # Create a test OCG in the database
    client_org = Organization(name="Test Client", type="client", domain="test.com")
    db_session.add(client_org)
    db_session.commit()
    test_ocg = OCG(client_id=client_org.id, name="Test OCG")
    db_session.add(test_ocg)
    db_session.commit()

    # Make a GET request to /api/v1/ocg/{ocg_id}
    response = client.get(f"/api/v1/ocg/{test_ocg.id}", headers=auth_headers)

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the response JSON contains the expected OCG data
    response_data = response.get_json()
    assert response_data["id"] == str(test_ocg.id)
    assert response_data["name"] == "Test OCG"


def test_update_ocg(client, auth_headers, db_session):
    """Test updating an existing OCG document"""
    # Create a test OCG in the database
    client_org = Organization(name="Test Client", type="client", domain="test.com")
    db_session.add(client_org)
    db_session.commit()
    test_ocg = OCG(client_id=client_org.id, name="Test OCG")
    db_session.add(test_ocg)
    db_session.commit()

    # Prepare update data with modified OCG properties
    update_data = {"name": "Updated OCG Name", "total_points": 15}

    # Make a PUT request to /api/v1/ocg/{ocg_id} with the update data
    response = client.put(f"/api/v1/ocg/{test_ocg.id}", headers=auth_headers, data=json.dumps(update_data))

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the response JSON contains the updated OCG data
    response_data = response.get_json()
    assert response_data["id"] == str(test_ocg.id)
    assert response_data["name"] == "Updated OCG Name"
    assert response_data["total_points"] == 15

    # Assert that the OCG has been updated in the database
    updated_ocg = db_session.query(OCG).filter(OCG.id == test_ocg.id).first()
    assert updated_ocg.name == "Updated OCG Name"
    assert updated_ocg.total_points == 15


def test_delete_ocg(client, auth_headers, db_session):
    """Test deleting an OCG document"""
    # Create a test OCG in the database
    client_org = Organization(name="Test Client", type="client", domain="test.com")
    db_session.add(client_org)
    db_session.commit()
    test_ocg = OCG(client_id=client_org.id, name="Test OCG")
    db_session.add(test_ocg)
    db_session.commit()

    # Make a DELETE request to /api/v1/ocg/{ocg_id}
    response = client.delete(f"/api/v1/ocg/{test_ocg.id}", headers=auth_headers)

    # Assert that the response status code is 204 (No Content)
    assert response.status_code == 200

    # Assert that the OCG has been deleted from the database
    deleted_ocg = db_session.query(OCG).filter(OCG.id == test_ocg.id).first()
    assert deleted_ocg is None


def test_list_ocgs(client, auth_headers, db_session):
    """Test listing OCG documents"""
    # Create multiple test OCGs in the database
    client_org = Organization(name="Test Client", type="client", domain="test.com")
    db_session.add(client_org)
    db_session.commit()
    test_ocg1 = OCG(client_id=client_org.id, name="Test OCG 1")
    test_ocg2 = OCG(client_id=client_org.id, name="Test OCG 2")
    db_session.add_all([test_ocg1, test_ocg2])
    db_session.commit()

    # Make a GET request to /api/v1/ocg
    response = client.get("/api/v1/ocg", headers=auth_headers)

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the response JSON contains a list of OCGs
    response_data = response.get_json()
    assert isinstance(response_data, list)

    # Assert that the correct number of OCGs is returned
    assert len(response_data) == 2


def test_add_ocg_section(client, auth_headers, db_session):
    """Test adding a section to an existing OCG"""
    # Create a test OCG in the database
    client_org = Organization(name="Test Client", type="client", domain="test.com")
    db_session.add(client_org)
    db_session.commit()
    test_ocg = OCG(client_id=client_org.id, name="Test OCG")
    db_session.add(test_ocg)
    db_session.commit()

    # Prepare section data with title, content, and negotiable flag
    section_data = {"title": "Test Section", "content": "Test Content", "is_negotiable": True}

    # Make a POST request to /api/v1/ocg/{ocg_id}/sections with the section data
    response = client.post(f"/api/v1/ocg/{test_ocg.id}/sections", headers=auth_headers, data=json.dumps(section_data))

    # Assert that the response status code is 201 (Created)
    assert response.status_code == 201

    # Assert that the response JSON contains the new section data
    response_data = response.get_json()
    assert response_data["title"] == "Test Section"
    assert response_data["content"] == "Test Content"
    assert response_data["is_negotiable"] == True

    # Assert that the section has been added to the OCG in the database
    added_section = db_session.query(OCGSection).filter(OCGSection.id == response_data["id"]).first()
    assert added_section is not None
    assert added_section.title == "Test Section"


def test_update_ocg_section(client, auth_headers, db_session):
    """Test updating a section in an OCG"""
    # Create a test OCG with sections in the database
    client_org = Organization(name="Test Client", type="client", domain="test.com")
    db_session.add(client_org)
    db_session.commit()
    test_ocg = OCG(client_id=client_org.id, name="Test OCG")
    db_session.add(test_ocg)
    db_session.commit()
    test_section = OCGSection(ocg_id=test_ocg.id, title="Test Section", content="Test Content", is_negotiable=False)
    db_session.add(test_section)
    db_session.commit()

    # Prepare update data for a section
    update_data = {"title": "Updated Section", "content": "Updated Content", "is_negotiable": True}

    # Make a PUT request to /api/v1/ocg/{ocg_id}/sections/{section_id} with the update data
    response = client.put(f"/api/v1/ocg/{test_ocg.id}/sections/{test_section.id}", headers=auth_headers, data=json.dumps(update_data))

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the response JSON contains the updated section data
    response_data = response.get_json()
    assert response_data["title"] == "Updated Section"
    assert response_data["content"] == "Updated Content"
    assert response_data["is_negotiable"] == True

    # Assert that the section has been updated in the database
    updated_section = db_session.query(OCGSection).filter(OCGSection.id == test_section.id).first()
    assert updated_section.title == "Updated Section"
    assert updated_section.content == "Updated Content"
    assert updated_section.is_negotiable == True


def test_delete_ocg_section(client, auth_headers, db_session):
    """Test deleting a section from an OCG"""
    # Create a test OCG with sections in the database
    client_org = Organization(name="Test Client", type="client", domain="test.com")
    db_session.add(client_org)
    db_session.commit()
    test_ocg = OCG(client_id=client_org.id, name="Test OCG")
    db_session.add(test_ocg)
    db_session.commit()
    test_section = OCGSection(ocg_id=test_ocg.id, title="Test Section", content="Test Content", is_negotiable=False)
    db_session.add(test_section)
    db_session.commit()

    # Make a DELETE request to /api/v1/ocg/{ocg_id}/sections/{section_id}
    response = client.delete(f"/api/v1/ocg/{test_ocg.id}/sections/{test_section.id}", headers=auth_headers)

    # Assert that the response status code is 204 (No Content)
    assert response.status_code == 200

    # Assert that the section has been removed from the OCG in the database
    deleted_section = db_session.query(OCGSection).filter(OCGSection.id == test_section.id).first()
    assert deleted_section is None


def test_add_section_alternative(client, auth_headers, db_session):
    """Test adding an alternative to a negotiable OCG section"""
    # Create a test OCG with a negotiable section in the database
    client_org = Organization(name="Test Client", type="client", domain="test.com")
    db_session.add(client_org)
    db_session.commit()
    test_ocg = OCG(client_id=client_org.id, name="Test OCG")
    db_session.add(test_ocg)
    db_session.commit()
    test_section = OCGSection(ocg_id=test_ocg.id, title="Test Section", content="Test Content", is_negotiable=True)
    db_session.add(test_section)
    db_session.commit()

    # Prepare alternative data with title, content, and points
    alternative_data = {"title": "Test Alternative", "content": "Test Alternative Content", "points": 2}

    # Make a POST request to /api/v1/ocg/{ocg_id}/sections/{section_id}/alternatives with the alternative data
    response = client.post(f"/api/v1/ocg/{test_ocg.id}/sections/{test_section.id}/alternatives", headers=auth_headers, data=json.dumps(alternative_data))

    # Assert that the response status code is 201 (Created)
    assert response.status_code == 201

    # Assert that the response JSON contains the new alternative data
    response_data = response.get_json()
    assert response_data["title"] == "Test Alternative"
    assert response_data["content"] == "Test Alternative Content"
    assert response_data["points"] == 2

    # Assert that the alternative has been added to the section in the database
    added_alternative = db_session.query(OCGAlternative).filter(OCGAlternative.id == response_data["id"]).first()
    assert added_alternative is not None
    assert added_alternative.title == "Test Alternative"


def test_update_section_alternative(client, auth_headers, db_session):
    """Test updating an alternative for a negotiable OCG section"""
    # Create a test OCG with a negotiable section and alternatives in the database
    client_org = Organization(name="Test Client", type="client", domain="test.com")
    db_session.add(client_org)
    db_session.commit()
    test_ocg = OCG(client_id=client_org.id, name="Test OCG")
    db_session.add(test_ocg)
    db_session.commit()
    test_section = OCGSection(ocg_id=test_ocg.id, title="Test Section", content="Test Content", is_negotiable=True)
    db_session.add(test_section)
    db_session.commit()
    test_alternative = OCGAlternative(section_id=test_section.id, title="Test Alternative", content="Test Alternative Content", points=2)
    db_session.add(test_alternative)
    db_session.commit()

    # Prepare update data for an alternative
    update_data = {"title": "Updated Alternative", "content": "Updated Alternative Content", "points": 3}

    # Make a PUT request to /api/v1/ocg/{ocg_id}/sections/{section_id}/alternatives/{alternative_id} with the update data
    response = client.put(f"/api/v1/ocg/{test_ocg.id}/sections/{test_section.id}/alternatives/{test_alternative.id}", headers=auth_headers, data=json.dumps(update_data))

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the response JSON contains the updated alternative data
    response_data = response.get_json()
    assert response_data["title"] == "Updated Alternative"
    assert response_data["content"] == "Updated Alternative Content"
    assert response_data["points"] == 3

    # Assert that the alternative has been updated in the database
    updated_alternative = db_session.query(OCGAlternative).filter(OCGAlternative.id == test_alternative.id).first()
    assert updated_alternative.title == "Updated Alternative"
    assert updated_alternative.content == "Updated Alternative Content"
    assert updated_alternative.points == 3


def test_delete_section_alternative(client, auth_headers, db_session):
    """Test deleting an alternative from a negotiable OCG section"""
    # Create a test OCG with a negotiable section and alternatives in the database
    client_org = Organization(name="Test Client", type="client", domain="test.com")
    db_session.add(client_org)
    db_session.commit()
    test_ocg = OCG(client_id=client_org.id, name="Test OCG")
    db_session.add(test_ocg)
    db_session.commit()
    test_section = OCGSection(ocg_id=test_ocg.id, title="Test Section", content="Test Content", is_negotiable=True)
    db_session.add(test_section)
    db_session.commit()
    test_alternative = OCGAlternative(section_id=test_section.id, title="Test Alternative", content="Test Alternative Content", points=2)
    db_session.add(test_alternative)
    db_session.commit()

    # Make a DELETE request to /api/v1/ocg/{ocg_id}/sections/{section_id}/alternatives/{alternative_id}
    response = client.delete(f"/api/v1/ocg/{test_ocg.id}/sections/{test_section.id}/alternatives/{test_alternative.id}", headers=auth_headers)

    # Assert that the response status code is 204 (No Content)
    assert response.status_code == 200

    # Assert that the alternative has been removed from the section in the database
    deleted_alternative = db_session.query(OCGAlternative).filter(OCGAlternative.id == test_alternative.id).first()
    assert deleted_alternative is None


def test_publish_ocg(client, auth_headers, db_session):
    """Test publishing an OCG document"""
    # Create a test OCG with Draft status in the database
    client_org = Organization(name="Test Client", type="client", domain="test.com")
    db_session.add(client_org)
    db_session.commit()
    test_ocg = OCG(client_id=client_org.id, name="Test OCG", status="draft")
    db_session.add(test_ocg)
    db_session.commit()

    # Make a PUT request to /api/v1/ocg/{ocg_id}/publish
    response = client.post(f"/api/v1/ocg/{test_ocg.id}/publish", headers=auth_headers)

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the response JSON contains the OCG with Published status
    response_data = response.get_json()
    assert response_data["status"] == "published"

    # Assert that the OCG status has been updated in the database
    published_ocg = db_session.query(OCG).filter(OCG.id == test_ocg.id).first()
    assert published_ocg.status == "published"


def test_select_ocg_alternatives(client, auth_headers, db_session):
    """Test law firm selecting alternatives for an OCG"""
    # Create a test OCG with negotiable sections and alternatives in the database
    client_org = Organization(name="Test Client", type="client", domain="test.com")
    firm_org = Organization(name="Test Firm", type="law_firm", domain="testfirm.com")
    db_session.add_all([client_org, firm_org])
    db_session.commit()
    test_ocg = OCG(client_id=client_org.id, name="Test OCG")
    db_session.add(test_ocg)
    db_session.commit()
    test_section = OCGSection(ocg_id=test_ocg.id, title="Test Section", content="Test Content", is_negotiable=True)
    db_session.add(test_section)
    db_session.commit()
    test_alternative1 = OCGAlternative(section_id=test_section.id, title="Test Alternative 1", content="Test Alternative Content 1", points=2)
    test_alternative2 = OCGAlternative(section_id=test_section.id, title="Test Alternative 2", content="Test Alternative Content 2", points=3)
    db_session.add_all([test_alternative1, test_alternative2])
    db_session.commit()

    # Prepare selection data with section and alternative IDs, and point usage
    selection_data = {"firm_id": str(firm_org.id), "section_selections": {str(test_section.id): str(test_alternative1.id)}}

    # Make a PUT request to /api/v1/ocg/{ocg_id}/select with the selection data
    response = client.put(f"/api/v1/ocg/{test_ocg.id}/select", headers=auth_headers, data=json.dumps(selection_data))

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the response JSON contains the updated OCG with selections
    response_data = response.get_json()
    assert str(test_section.id) in response_data["firm_selections"][str(firm_org.id)]
    assert response_data["firm_selections"][str(firm_org.id)][str(test_section.id)] == str(test_alternative1.id)

    # Assert that the firm selections have been updated in the database
    updated_ocg = db_session.query(OCG).filter(OCG.id == test_ocg.id).first()
    assert str(test_section.id) in updated_ocg.firm_selections[str(firm_org.id)]
    assert updated_ocg.firm_selections[str(firm_org.id)][str(test_section.id)] == str(test_alternative1.id)


def test_sign_ocg(client, auth_headers, db_session):
    """Test signing an OCG document after negotiation"""
    # Create a test OCG with Negotiating status in the database
    client_org = Organization(name="Test Client", type="client", domain="test.com")
    db_session.add(client_org)
    db_session.commit()
    test_ocg = OCG(client_id=client_org.id, name="Test OCG", status="negotiating")
    db_session.add(test_ocg)
    db_session.commit()

    # Make a PUT request to /api/v1/ocg/{ocg_id}/sign
    response = client.put(f"/api/v1/ocg/{test_ocg.id}/sign", headers=auth_headers)

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the response JSON contains the OCG with Signed status
    response_data = response.get_json()
    assert response_data["status"] == "signed"

    # Assert that the OCG status has been updated in the database
    signed_ocg = db_session.query(OCG).filter(OCG.id == test_ocg.id).first()
    assert signed_ocg.status == "signed"


def test_create_ocg_invalid_data(client, auth_headers):
    """Test error handling when creating an OCG with invalid data"""
    # Prepare invalid OCG data (missing required fields)
    invalid_ocg_data = {"version": 1, "total_points": 10}

    # Make a POST request to /api/v1/ocg endpoint with the invalid data
    response = client.post("/api/v1/ocg", headers=auth_headers, data=json.dumps(invalid_ocg_data))

    # Assert that the response status code is 422 (Unprocessable Entity)
    assert response.status_code == 400

    # Assert that the response contains validation error details
    response_data = response.get_json()
    assert "error" in response_data
    assert "message" in response_data
    assert "client_id" in response_data["message"]
    assert "name" in response_data["message"]


def test_get_ocg_not_found(client, auth_headers):
    """Test error handling when retrieving a non-existent OCG"""
    # Generate a random UUID for a non-existent OCG
    non_existent_id = UUID('3fa85f64-5717-4562-b3fc-2c963f66afa6')

    # Make a GET request to /api/v1/ocg/{non_existent_id}
    response = client.get(f"/api/v1/ocg/{non_existent_id}", headers=auth_headers)

    # Assert that the response status code is 404 (Not Found)
    assert response.status_code == 404

    # Assert that the response contains an error message
    response_data = response.get_json()
    assert "error" in response_data
    assert "message" in response_data
    assert "OCG not found" in response_data["message"]


def test_unauthorized_access(client):
    """Test error handling when accessing OCG endpoints without authentication"""
    # Make a GET request to /api/v1/ocg without authentication headers
    response = client.get("/api/v1/ocg")

    # Assert that the response status code is 401 (Unauthorized)
    assert response.status_code == 401

    # Assert that the response contains an error message
    response_data = response.get_json()
    assert "error" in response_data
    assert "message" in response_data
    assert "Authentication required" in response_data["message"]


def test_forbidden_access(client, auth_headers, db_session):
    """Test error handling when accessing an OCG owned by another organization"""
    # Create a test organization
    other_org = Organization(name="Other Org", type="client", domain="other.com")
    db_session.add(other_org)
    db_session.commit()

    # Create a test OCG owned by the test organization
    test_ocg = OCG(client_id=other_org.id, name="Test OCG")
    db_session.add(test_ocg)
    db_session.commit()

    # Make a GET request to /api/v1/ocg/{ocg_id} with auth headers for a different organization
    response = client.get(f"/api/v1/ocg/{test_ocg.id}", headers=auth_headers)

    # Assert that the response status code is 403 (Forbidden)
    assert response.status_code == 403

    # Assert that the response contains an error message
    response_data = response.get_json()
    assert "error" in response_data
    assert "message" in response_data
    assert "Forbidden" in response_data["message"]


def test_exceed_point_budget(client, auth_headers, db_session):
    """Test error handling when law firm exceeds point budget in OCG negotiation"""
    # Create a test OCG with negotiable sections, alternatives, and a point budget in the database
    client_org = Organization(name="Test Client", type="client", domain="test.com")
    firm_org = Organization(name="Test Firm", type="law_firm", domain="testfirm.com")
    db_session.add_all([client_org, firm_org])
    db_session.commit()
    test_ocg = OCG(client_id=client_org.id, name="Test OCG", total_points=5, default_firm_point_budget=3)
    db_session.add(test_ocg)
    db_session.commit()
    test_section = OCGSection(ocg_id=test_ocg.id, title="Test Section", content="Test Content", is_negotiable=True)
    db_session.add(test_section)
    db_session.commit()
    test_alternative1 = OCGAlternative(section_id=test_section.id, title="Test Alternative 1", content="Test Alternative Content 1", points=2)
    test_alternative2 = OCGAlternative(section_id=test_section.id, title="Test Alternative 2", content="Test Alternative Content 2", points=3)
    db_session.add_all([test_alternative1, test_alternative2])
    db_session.commit()

    # Prepare selection data that exceeds the point budget
    selection_data = {"firm_id": str(firm_org.id), "section_selections": {str(test_section.id): str(test_alternative2.id)}}

    # Make a PUT request to /api/v1/ocg/{ocg_id}/select with the selection data
    response = client.put(f"/api/v1/ocg/{test_ocg.id}/select", headers=auth_headers, data=json.dumps(selection_data))

    # Assert that the response status code is 400 (Bad Request)
    assert response.status_code == 400

    # Assert that the response contains an error message about exceeding the point budget
    response_data = response.get_json()
    assert "error" in response_data
    assert "message" in response_data
    assert "exceed" in response_data["message"]