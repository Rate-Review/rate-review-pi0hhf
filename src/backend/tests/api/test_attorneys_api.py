"""
Test suite for the attorney API endpoints in the Justice Bid Rate Negotiation System.
Covers CRUD operations, staff class assignment, rate retrieval, and UniCourt integration.
"""
import pytest  # pytest version: ^7.0.0
import json  # standard library
import uuid  # standard library
import datetime  # standard library
from unittest import mock  # standard library

from flask import Flask  # flask==2.0.1
from pytest import fixture  # pytest==7.0.0

from ...db.models.attorney import Attorney  # src/backend/db/models/attorney.py
from ...api.schemas.attorneys import AttorneyCreate, AttorneyUpdate, AttorneySearchParams, StaffClassAssignment, TimekeeperIdUpdate, UniCourtAttorneyMapping  # src/backend/api/schemas/attorneys.py
from ...api.endpoints.attorneys import attorneys_bp, initialize_dependencies  # src/backend/api/endpoints/attorneys.py
from ...db.repositories.attorney_repository import AttorneyRepository  # src/backend/db/repositories/attorney_repository.py
from ..conftest import app, client, db_session, law_firm_organization, client_organization, attorney, law_firm_token, client_token, admin_token  # src/backend/tests/conftest.py


def setup_module():
    """Set up the test module by initializing dependencies"""
    # Register the attorneys blueprint with the test app
    app.register_blueprint(attorneys_bp)
    # Initialize dependencies for the attorney endpoints
    initialize_dependencies(g.db)


def test_get_attorneys(client, attorney, law_firm_token):
    """Test retrieving attorneys with default parameters"""
    # Make a GET request to /api/v1/attorneys with valid token
    response = client.get('/api/v1/attorneys', headers={'Authorization': f'Bearer {law_firm_token}'})
    # Assert response status code is 200
    assert response.status_code == 200
    # Assert response contains expected attorney data
    data = response.get_json()
    assert len(data['items']) == 1
    assert data['items'][0]['name'] == attorney.name
    # Assert pagination metadata is correct
    assert data['total'] == 1
    assert data['page'] == 1
    assert data['size'] == 20


def test_get_attorneys_with_filters(client, attorney, law_firm_organization, law_firm_token):
    """Test retrieving attorneys with query filters"""
    # Make a GET request with name and organization_id filters
    response = client.get(
        f'/api/v1/attorneys?name={attorney.name}&organization_id={law_firm_organization.id}',
        headers={'Authorization': f'Bearer {law_firm_token}'}
    )
    # Assert response status code is 200
    assert response.status_code == 200
    # Assert response contains only filtered attorneys
    data = response.get_json()
    assert len(data['items']) == 1
    assert data['items'][0]['name'] == attorney.name

    # Test with additional filters: bar_date_after, bar_date_before, office_ids, active_only
    # TODO: Add more comprehensive filter tests
    # response = client.get(
    #     f'/api/v1/attorneys?bar_date_after=2000-01-01&bar_date_before=2020-01-01&office_ids={attorney.office_id}&active_only=true',
    #     headers={'Authorization': f'Bearer {law_firm_token}'}
    # )
    # assert response.status_code == 200


def test_get_attorney_by_id(client, attorney, law_firm_token):
    """Test retrieving a specific attorney by ID"""
    # Make a GET request to /api/v1/attorneys/{attorney_id}
    response = client.get(f'/api/v1/attorneys/{attorney.id}', headers={'Authorization': f'Bearer {law_firm_token}'})
    # Assert response status code is 200
    assert response.status_code == 200
    # Assert response contains expected attorney details
    data = response.get_json()
    assert data['name'] == attorney.name

    # Test with non-existent ID returns 404
    response = client.get('/api/v1/attorneys/nonexistent_id', headers={'Authorization': f'Bearer {law_firm_token}'})
    assert response.status_code == 404


def test_create_attorney(client, law_firm_organization, law_firm_token):
    """Test creating a new attorney"""
    # Create attorney data with required fields
    attorney_data = {
        'name': 'Jane Smith',
        'organization_id': str(law_firm_organization.id),
        'bar_date': '2012-01-01',
        'graduation_date': '2009-06-01'
    }
    # Make a POST request to /api/v1/attorneys with data
    response = client.post(
        '/api/v1/attorneys',
        json=attorney_data,
        headers={'Authorization': f'Bearer {law_firm_token}'}
    )
    # Assert response status code is 201
    assert response.status_code == 201
    # Assert response contains created attorney details
    data = response.get_json()
    assert data['name'] == 'Jane Smith'
    assert data['organization_id'] == str(law_firm_organization.id)

    # Test validation errors with invalid data
    response = client.post(
        '/api/v1/attorneys',
        json={'name': '', 'organization_id': str(law_firm_organization.id)},
        headers={'Authorization': f'Bearer {law_firm_token}'}
    )
    assert response.status_code == 400

    # Test unauthorized access returns 401/403
    # TODO: Implement unauthorized access tests


def test_update_attorney(client, attorney, law_firm_token):
    """Test updating an existing attorney"""
    # Create updated attorney data
    update_data = {'name': 'Updated Name'}
    # Make a PUT request to /api/v1/attorneys/{attorney_id}
    response = client.put(
        f'/api/v1/attorneys/{attorney.id}',
        json=update_data,
        headers={'Authorization': f'Bearer {law_firm_token}'}
    )
    # Assert response status code is 200
    assert response.status_code == 200
    # Assert response contains updated attorney details
    data = response.get_json()
    assert data['name'] == 'Updated Name'

    # Verify database was updated with changes
    # TODO: Implement database verification

    # Test with non-existent ID returns 404
    response = client.put(
        '/api/v1/attorneys/nonexistent_id',
        json=update_data,
        headers={'Authorization': f'Bearer {law_firm_token}'}
    )
    assert response.status_code == 404

    # Test unauthorized access returns 401/403
    # TODO: Implement unauthorized access tests


def test_delete_attorney(client, attorney, law_firm_token):
    """Test deleting an attorney"""
    # Make a DELETE request to /api/v1/attorneys/{attorney_id}
    response = client.delete(f'/api/v1/attorneys/{attorney.id}', headers={'Authorization': f'Bearer {law_firm_token}'})
    # Assert response status code is 200
    assert response.status_code == 200
    # Assert response contains success message
    data = response.get_json()
    assert data['message'] == 'Attorney deleted successfully'

    # Verify attorney no longer exists in database
    # TODO: Implement database verification

    # Test with non-existent ID returns 404
    response = client.delete('/api/v1/attorneys/nonexistent_id', headers={'Authorization': f'Bearer {law_firm_token}'})
    assert response.status_code == 404

    # Test unauthorized access returns 401/403
    # TODO: Implement unauthorized access tests


def test_get_attorney_rates(client, attorney, client_organization, law_firm_token, db_session):
    """Test retrieving rates for a specific attorney"""
    # Create test rates for the attorney
    from ...db.models.rate import Rate
    rate1 = Rate(attorney_id=attorney.id, client_id=client_organization.id, firm_id=attorney.organization_id, office_id=attorney.office_id, staff_class_id=attorney.staff_class_id, amount=500.00, currency='USD', effective_date=datetime.date(2023, 1, 1))
    rate2 = Rate(attorney_id=attorney.id, client_id=client_organization.id, firm_id=attorney.organization_id, office_id=attorney.office_id, staff_class_id=attorney.staff_class_id, amount=600.00, currency='USD', effective_date=datetime.date(2024, 1, 1))
    db_session.add_all([rate1, rate2])
    db_session.commit()

    # Make a GET request to /api/v1/attorneys/{attorney_id}/rates
    response = client.get(f'/api/v1/attorneys/{attorney.id}/rates', headers={'Authorization': f'Bearer {law_firm_token}'})
    # Assert response status code is 200
    assert response.status_code == 200
    # Assert response contains attorney with rates
    data = response.get_json()
    assert data['attorney']['name'] == attorney.name
    assert len(data['rates']) == 2

    # Test optional client_id parameter filtering
    response = client.get(f'/api/v1/attorneys/{attorney.id}/rates?client_id={client_organization.id}', headers={'Authorization': f'Bearer {law_firm_token}'})
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['rates']) == 2

    # Test with non-existent ID returns 404
    response = client.get('/api/v1/attorneys/nonexistent_id/rates', headers={'Authorization': f'Bearer {law_firm_token}'})
    assert response.status_code == 404

    # Test unauthorized access returns 401/403
    # TODO: Implement unauthorized access tests


def test_add_timekeeper_id(client, attorney, client_organization, law_firm_token):
    """Test adding a client-specific timekeeper ID for an attorney"""
    # Create timekeeper ID update data
    timekeeper_data = {
        'attorney_id': str(attorney.id),
        'client_id': str(client_organization.id),
        'timekeeper_id': 'TK123'
    }
    # Make a POST request to /api/v1/attorneys/timekeeper-id
    response = client.post(
        '/api/v1/attorneys/timekeeper-id',
        json=timekeeper_data,
        headers={'Authorization': f'Bearer {law_firm_token}'}
    )
    # Assert response status code is 200
    assert response.status_code == 200
    # Assert response contains updated attorney with timekeeper ID
    data = response.get_json()
    assert data['timekeeper_ids'][str(client_organization.id)] == 'TK123'

    # Test with non-existent attorney ID returns 404
    timekeeper_data['attorney_id'] = 'nonexistent_id'
    response = client.post(
        '/api/v1/attorneys/timekeeper-id',
        json=timekeeper_data,
        headers={'Authorization': f'Bearer {law_firm_token}'}
    )
    assert response.status_code == 404

    # Test unauthorized access returns 401/403
    # TODO: Implement unauthorized access tests


def test_assign_staff_class(client, attorney, db_session, law_firm_token):
    """Test assigning a staff class to an attorney"""
    # Create test staff class
    from ...db.models.staff_class import StaffClass, ExperienceType
    staff_class = StaffClass(organization_id=attorney.organization_id, name='Associate', experience_type=ExperienceType.BAR_YEAR, min_experience=2)
    db_session.add(staff_class)
    db_session.commit()

    # Create staff class assignment data
    staff_class_data = {
        'attorney_id': str(attorney.id),
        'staff_class_id': str(staff_class.id)
    }
    # Make a POST request to /api/v1/attorneys/staff-class
    response = client.post(
        '/api/v1/attorneys/staff-class',
        json=staff_class_data,
        headers={'Authorization': f'Bearer {law_firm_token}'}
    )
    # Assert response status code is 200
    assert response.status_code == 200
    # Assert response contains updated attorney with staff class
    data = response.get_json()
    assert data['staff_class_id'] == str(staff_class.id)

    # Test with non-existent attorney ID returns 404
    staff_class_data['attorney_id'] = 'nonexistent_id'
    response = client.post(
        '/api/v1/attorneys/staff-class',
        json=staff_class_data,
        headers={'Authorization': f'Bearer {law_firm_token}'}
    )
    assert response.status_code == 404

    # Test with non-existent staff class ID returns 404
    staff_class_data['attorney_id'] = str(attorney.id)
    staff_class_data['staff_class_id'] = 'nonexistent_id'
    response = client.post(
        '/api/v1/attorneys/staff-class',
        json=staff_class_data,
        headers={'Authorization': f'Bearer {law_firm_token}'}
    )
    assert response.status_code == 404

    # Test unauthorized access returns 401/403
    # TODO: Implement unauthorized access tests


def test_get_attorneys_without_staff_class(client, attorney, law_firm_organization, law_firm_token):
    """Test retrieving attorneys without assigned staff classes"""
    # Ensure attorney has no staff class
    attorney.staff_class_id = None
    g.db.commit()

    # Make a GET request to /api/v1/attorneys/without-staff-class?organization_id={org_id}
    response = client.get(
        f'/api/v1/attorneys/without-staff-class?organization_id={law_firm_organization.id}',
        headers={'Authorization': f'Bearer {law_firm_token}'}
    )
    # Assert response status code is 200
    assert response.status_code == 200
    # Assert response contains attorneys without staff class
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['name'] == attorney.name

    # Test with invalid organization_id returns 400
    response = client.get(
        '/api/v1/attorneys/without-staff-class?organization_id=invalid_uuid',
        headers={'Authorization': f'Bearer {law_firm_token}'}
    )
    assert response.status_code == 400

    # Test unauthorized access returns 401/403
    # TODO: Implement unauthorized access tests


def test_auto_assign_staff_class(client, attorney, law_firm_organization, client_organization, db_session, law_firm_token):
    """Test automatically finding and assigning an eligible staff class"""
    # Create test staff classes with different experience criteria
    from ...db.models.staff_class import StaffClass, ExperienceType
    staff_class1 = StaffClass(organization_id=attorney.organization_id, name='Associate', experience_type=ExperienceType.BAR_YEAR, min_experience=2, max_experience=5)
    staff_class2 = StaffClass(organization_id=attorney.organization_id, name='Senior Associate', experience_type=ExperienceType.BAR_YEAR, min_experience=5, max_experience=10)
    db_session.add_all([staff_class1, staff_class2])
    db_session.commit()

    # Make a POST request to /api/v1/attorneys/{attorney_id}/auto-assign-staff-class?organization_id={org_id}
    response = client.post(
        f'/api/v1/attorneys/{attorney.id}/auto-assign-staff-class?organization_id={law_firm_organization.id}',
        headers={'Authorization': f'Bearer {law_firm_token}'}
    )
    # Assert response status code is 200
    assert response.status_code == 200
    # Assert response contains attorney with assigned staff class
    data = response.get_json()
    assert data['staff_class_id'] is not None

    # Test with non-existent attorney ID returns 404
    response = client.post(
        '/api/v1/attorneys/nonexistent_id/auto-assign-staff-class?organization_id={law_firm_organization.id}',
        headers={'Authorization': f'Bearer {law_firm_token}'}
    )
    assert response.status_code == 404

    # Test with no eligible staff class returns appropriate message
    # TODO: Implement test for no eligible staff class

    # Test unauthorized access returns 401/403
    # TODO: Implement unauthorized access tests


@mock.patch('src.backend.api.endpoints.attorneys.UniCourtClient.search_attorneys')
def test_unicourt_search(mock_search_attorneys, client, admin_token):
    """Test searching for attorneys in UniCourt"""
    # Mock the UniCourtClient.search_attorneys method
    mock_search_attorneys.return_value = [{'name': 'UniCourt Attorney'}]

    # Create search parameters
    search_params = {'name': 'Test'}
    # Make a POST request to /api/v1/attorneys/unicourt/search
    response = client.post(
        '/api/v1/attorneys/unicourt/search',
        json=search_params,
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    # Assert response status code is 200
    assert response.status_code == 200
    # Assert response contains expected search results
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['name'] == 'UniCourt Attorney'

    # Test with invalid parameters returns 400
    response = client.post(
        '/api/v1/attorneys/unicourt/search',
        json={},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 400

    # Test integration error handling
    # TODO: Implement integration error handling test

    # Test unauthorized access returns 401/403
    # TODO: Implement unauthorized access tests


@mock.patch('src.backend.api.endpoints.attorneys.UniCourtClient.get_attorney_details')
def test_get_unicourt_attorney(mock_get_attorney_details, client, admin_token):
    """Test retrieving attorney details from UniCourt"""
    # Mock the UniCourtClient.get_attorney_details method
    mock_get_attorney_details.return_value = {'name': 'UniCourt Attorney Details'}

    # Make a GET request to /api/v1/attorneys/unicourt/{unicourt_id}
    response = client.get(
        '/api/v1/attorneys/unicourt/unicourt_id',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    # Assert response status code is 200
    assert response.status_code == 200
    # Assert response contains expected attorney details
    data = response.get_json()
    assert data['name'] == 'UniCourt Attorney Details'

    # Test integration error handling
    # TODO: Implement integration error handling test

    # Test unauthorized access returns 401/403
    # TODO: Implement unauthorized access tests


@mock.patch('src.backend.api.endpoints.attorneys.UniCourtClient.get_attorney_performance')
def test_get_unicourt_attorney_performance(mock_get_attorney_performance, client, admin_token):
    """Test retrieving attorney performance data from UniCourt"""
    # Mock the UniCourtClient.get_attorney_performance method
    mock_get_attorney_performance.return_value = {'win_rate': 0.8}

    # Make a GET request to /api/v1/attorneys/unicourt/{unicourt_id}/performance
    response = client.get(
        '/api/v1/attorneys/unicourt/unicourt_id/performance',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    # Assert response status code is 200
    assert response.status_code == 200
    # Assert response contains expected performance data
    data = response.get_json()
    assert data['win_rate'] == 0.8

    # Test integration error handling
    # TODO: Implement integration error handling test

    # Test unauthorized access returns 401/403
    # TODO: Implement unauthorized access tests


@mock.patch('src.backend.api.endpoints.attorneys.UniCourtClient.sync_attorney_data')
def test_map_attorney_to_unicourt(mock_sync_attorney_data, client, attorney, admin_token):
    """Test mapping a Justice Bid attorney to a UniCourt attorney"""
    # Mock the UniCourtClient.sync_attorney_data method
    mock_sync_attorney_data.return_value = {'name': 'Mapped Attorney'}

    # Create mapping data
    mapping_data = {
        'attorney_id': str(attorney.id),
        'unicourt_id': 'unicourt_id',
        'fetch_performance_data': True
    }
    # Make a POST request to /api/v1/attorneys/unicourt/map
    response = client.post(
        '/api/v1/attorneys/unicourt/map',
        json=mapping_data,
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    # Assert response status code is 200
    assert response.status_code == 200
    # Assert response contains updated attorney with UniCourt ID
    data = response.get_json()
    assert data['name'] == 'Mapped Attorney'

    # Test with fetch_performance_data=True and fetch_performance_data=False
    # TODO: Implement fetch_performance_data tests

    # Test with non-existent attorney ID returns 404
    mapping_data['attorney_id'] = 'nonexistent_id'
    response = client.post(
        '/api/v1/attorneys/unicourt/map',
        json=mapping_data,
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 404

    # Test unauthorized access returns 401/403
    # TODO: Implement unauthorized access tests


def test_bulk_import(client, law_firm_organization, law_firm_token):
    """Test bulk importing attorneys for an organization"""
    # Create array of attorney data for import
    attorneys_data = [
        {'name': 'Bulk Attorney 1', 'bar_date': '2015-01-01', 'graduation_date': '2012-01-01'},
        {'name': 'Bulk Attorney 2', 'bar_date': '2016-01-01', 'graduation_date': '2013-01-01'}
    ]
    # Make a POST request to /api/v1/attorneys/bulk-import?organization_id={org_id}
    response = client.post(
        f'/api/v1/attorneys/bulk-import?organization_id={law_firm_organization.id}',
        json=attorneys_data,
        headers={'Authorization': f'Bearer {law_firm_token}'}
    )
    # Assert response status code is 200
    assert response.status_code == 200
    # Assert response contains import summary with success count
    data = response.get_json()
    assert data['successful'] == 2

    # Test with auto_assign_staff_class=True and auto_assign_staff_class=False
    # TODO: Implement auto_assign_staff_class tests

    # Test with invalid data returns appropriate error messages
    # TODO: Implement invalid data tests

    # Test with invalid organization_id returns 400
    response = client.post(
        '/api/v1/attorneys/bulk-import?organization_id=invalid_uuid',
        json=attorneys_data,
        headers={'Authorization': f'Bearer {law_firm_token}'}
    )
    assert response.status_code == 400

    # Test unauthorized access returns 401/403
    # TODO: Implement unauthorized access tests