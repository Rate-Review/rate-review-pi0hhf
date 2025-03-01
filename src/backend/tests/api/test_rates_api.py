import pytest
import json
from datetime import datetime, date
import uuid

from src.backend.app.app import app
from src.backend.tests.conftest import create_test_client, create_test_rate, create_test_user, create_test_organization, create_test_attorney, create_test_staff_class, authenticate_client

pytestmark = pytest.mark.asyncio

# Test listing rates
async def test_list_rates(client, auth_headers, create_test_rate):
    # Create some test rates
    rate1 = await create_test_rate()
    rate2 = await create_test_rate()
    rate3 = await create_test_rate()

    # Send GET request to /api/v1/rates with no filters
    response = client.get('/api/v1/rates', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['items']) == 3

    # Test filtering by attorney_id
    response = client.get(f'/api/v1/rates?attorney_id={rate1.attorney_id}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['items']) == 1
    assert data['items'][0]['attorney_id'] == str(rate1.attorney_id)

    # Test filtering by client_id
    response = client.get(f'/api/v1/rates?client_id={rate2.client_id}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['items']) == 1
    assert data['items'][0]['client_id'] == str(rate2.client_id)

    # Test filtering by firm_id
    response = client.get(f'/api/v1/rates?firm_id={rate3.firm_id}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['items']) == 1
    assert data['items'][0]['firm_id'] == str(rate3.firm_id)

    # Test filtering by status
    response = client.get(f'/api/v1/rates?status=approved', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['items']) == 0

    # Test filtering by effective_date range
    response = client.get(f'/api/v1/rates?effective_date_from=2023-01-01&effective_date_to=2023-01-31', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['items']) == 3

    # Test pagination parameters
    response = client.get('/api/v1/rates?page=1&page_size=2', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['items']) == 2
    assert data['total'] == 3
    assert data['page'] == 1
    assert data['size'] == 2

    # Test sorting parameters
    response = client.get('/api/v1/rates?sort_by=amount&sort_order=desc', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['items']) == 3
    assert data['items'][0]['amount'] >= data['items'][1]['amount']

    # Test combination of multiple filters
    response = client.get(f'/api/v1/rates?attorney_id={rate1.attorney_id}&status=draft&page=1&page_size=1', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['items']) == 1
    assert data['total'] == 1
    assert data['page'] == 1
    assert data['size'] == 1
    assert data['items'][0]['attorney_id'] == str(rate1.attorney_id)
    assert data['items'][0]['status'] == 'draft'

# Test retrieving a single rate by ID
async def test_get_rate_by_id(client, auth_headers, create_test_rate):
    # Create a test rate
    test_rate = await create_test_rate()

    # Send GET request to /api/v1/rates/{test_rate.id}
    response = client.get(f'/api/v1/rates/{test_rate.id}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == str(test_rate.id)
    assert data['amount'] == test_rate.amount
    assert data['currency'] == test_rate.currency

    # Test with non-existent ID returns 404
    response = client.get('/api/v1/rates/nonexistentid', headers=auth_headers)
    assert response.status_code == 404

    # Test with invalid ID format returns 422
    response = client.get('/api/v1/rates/invalid-id-format', headers=auth_headers)
    assert response.status_code == 422

    # Test access control - user without permission receives 403
    # TODO: Implement access control tests

# Test creating a new rate
async def test_create_rate(client, auth_headers, create_test_attorney, create_test_client_org, create_test_firm_org):
    # Create test data with valid attributes (attorney_id, client_id, firm_id, amount, currency, effective_date)
    test_attorney = await create_test_attorney(organization_id=create_test_firm_org.id)
    rate_data = {
        'attorney_id': str(test_attorney.id),
        'client_id': str(create_test_client_org.id),
        'firm_id': str(create_test_firm_org.id),
        'amount': 750.00,
        'currency': 'USD',
        'effective_date': '2023-01-01'
    }

    # Send POST request to /api/v1/rates with rate data
    response = client.post('/api/v1/rates', json=rate_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.get_json()
    assert data['attorney_id'] == str(test_attorney.id)
    assert data['client_id'] == str(create_test_client_org.id)
    assert data['firm_id'] == str(create_test_firm_org.id)
    assert data['amount'] == 750.00
    assert data['currency'] == 'USD'
    assert data['effective_date'] == '2023-01-01'

    # Test with missing required fields returns 422
    rate_data_missing_fields = {
        'client_id': str(create_test_client_org.id),
        'firm_id': str(create_test_firm_org.id),
        'amount': 750.00,
        'currency': 'USD',
        'effective_date': '2023-01-01'
    }
    response = client.post('/api/v1/rates', json=rate_data_missing_fields, headers=auth_headers)
    assert response.status_code == 422

    # Test with invalid data types returns 422
    rate_data_invalid_data_types = {
        'attorney_id': 123,
        'client_id': str(create_test_client_org.id),
        'firm_id': str(create_test_firm_org.id),
        'amount': 'abc',
        'currency': 'USD',
        'effective_date': '2023-01-01'
    }
    response = client.post('/api/v1/rates', json=rate_data_invalid_data_types, headers=auth_headers)
    assert response.status_code == 422

    # Test with negative rates returns 422
    rate_data_negative_rates = {
        'attorney_id': str(test_attorney.id),
        'client_id': str(create_test_client_org.id),
        'firm_id': str(create_test_firm_org.id),
        'amount': -750.00,
        'currency': 'USD',
        'effective_date': '2023-01-01'
    }
    response = client.post('/api/v1/rates', json=rate_data_negative_rates, headers=auth_headers)
    assert response.status_code == 422

    # Test access control - user without permission receives 403
    # TODO: Implement access control tests

# Test updating an existing rate
async def test_update_rate(client, auth_headers, create_test_rate):
    # Create a test rate
    test_rate = await create_test_rate()

    # Create updated rate data with new amount and effective date
    updated_rate_data = {
        'amount': 800.00,
        'effective_date': '2023-02-01'
    }

    # Send PUT request to /api/v1/rates/{test_rate.id} with updated data
    response = client.put(f'/api/v1/rates/{test_rate.id}', json=updated_rate_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == str(test_rate.id)
    assert data['amount'] == 800.00
    assert data['effective_date'] == '2023-02-01'

    # Test with non-existent ID returns 404
    response = client.put('/api/v1/rates/nonexistentid', json=updated_rate_data, headers=auth_headers)
    assert response.status_code == 404

    # Test with invalid data returns 422
    updated_rate_data_invalid_data = {
        'amount': 'abc',
        'effective_date': 'invalid-date'
    }
    response = client.put(f'/api/v1/rates/{test_rate.id}', json=updated_rate_data_invalid_data, headers=auth_headers)
    assert response.status_code == 422

    # Test access control - user without permission receives 403
    # TODO: Implement access control tests

# Test retrieving the history of a rate
async def test_get_rate_history(client, auth_headers, create_test_rate):
    # Create a test rate
    test_rate = await create_test_rate()

    # Create multiple versions of a rate through updates
    updated_rate_data1 = {
        'amount': 800.00,
        'effective_date': '2023-02-01'
    }
    response = client.put(f'/api/v1/rates/{test_rate.id}', json=updated_rate_data1, headers=auth_headers)
    assert response.status_code == 200

    updated_rate_data2 = {
        'amount': 900.00,
        'effective_date': '2023-03-01'
    }
    response = client.put(f'/api/v1/rates/{test_rate.id}', json=updated_rate_data2, headers=auth_headers)
    assert response.status_code == 200

    # Send GET request to /api/v1/rates/{test_rate.id}/history
    response = client.get(f'/api/v1/rates/{test_rate.id}/history', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 3  # Initial rate + 2 updates
    assert data[0]['amount'] == 500.00  # Initial amount
    assert data[1]['amount'] == 800.00  # First update
    assert data[2]['amount'] == 900.00  # Second update

    # Test with non-existent ID returns 404
    response = client.get('/api/v1/rates/nonexistentid/history', headers=auth_headers)
    assert response.status_code == 404

    # Test access control - user without permission receives 403
    # TODO: Implement access control tests

# Test approving a rate
async def test_approve_rate(client, auth_headers, create_test_rate):
    # Set up test_rate with Submitted status
    test_rate = await create_test_rate()
    test_rate.status = 'submitted'

    # Send POST request to /api/v1/rates/{test_rate.id}/approve
    response = client.post(f'/api/v1/rates/{test_rate.id}/approve', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == str(test_rate.id)
    assert data['status'] == 'approved'

    # Test with non-existent ID returns 404
    response = client.post('/api/v1/rates/nonexistentid/approve', headers=auth_headers)
    assert response.status_code == 404

    # Test with already approved rate returns 400
    test_rate.status = 'approved'
    response = client.post(f'/api/v1/rates/{test_rate.id}/approve', headers=auth_headers)
    assert response.status_code == 400

    # Test with rate in invalid state (Draft) returns 400
    test_rate.status = 'draft'
    response = client.post(f'/api/v1/rates/{test_rate.id}/approve', headers=auth_headers)
    assert response.status_code == 400

    # Test access control - only client users can approve rates
    # TODO: Implement access control tests

# Test rejecting a rate
async def test_reject_rate(client, auth_headers, create_test_rate):
    # Set up test_rate with Submitted status
    test_rate = await create_test_rate()
    test_rate.status = 'submitted'

    # Send POST request to /api/v1/rates/{test_rate.id}/reject with rejection reason
    rejection_data = {'reason': 'Too expensive'}
    response = client.post(f'/api/v1/rates/{test_rate.id}/reject', json=rejection_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == str(test_rate.id)
    assert data['status'] == 'rejected'

    # Test with non-existent ID returns 404
    response = client.post('/api/v1/rates/nonexistentid/reject', json=rejection_data, headers=auth_headers)
    assert response.status_code == 404

    # Test with already rejected rate returns 400
    test_rate.status = 'rejected'
    response = client.post(f'/api/v1/rates/{test_rate.id}/reject', json=rejection_data, headers=auth_headers)
    assert response.status_code == 400

    # Test with rate in invalid state (Draft) returns 400
    test_rate.status = 'draft'
    response = client.post(f'/api/v1/rates/{test_rate.id}/reject', json=rejection_data, headers=auth_headers)
    assert response.status_code == 400

    # Test access control - only client users can reject rates
    # TODO: Implement access control tests

# Test counter-proposing a rate
async def test_counter_propose_rate(client, auth_headers, create_test_rate):
    # Set up test_rate with Submitted status
    test_rate = await create_test_rate()
    test_rate.status = 'submitted'

    # Create counter-proposal data with lower amount
    counter_proposal_data = {'counter_amount': 700.00}
    response = client.post(f'/api/v1/rates/{test_rate.id}/counter', json=counter_proposal_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == str(test_rate.id)
    assert data['amount'] == 700.00
    assert data['status'] == 'counter_proposed'

    # Test with non-existent ID returns 404
    response = client.post('/api/v1/rates/nonexistentid/counter', json=counter_proposal_data, headers=auth_headers)
    assert response.status_code == 404

    # Test with invalid counter-proposal data returns 422
    counter_proposal_data_invalid_data = {'counter_amount': 'abc'}
    response = client.post(f'/api/v1/rates/{test_rate.id}/counter', json=counter_proposal_data_invalid_data, headers=auth_headers)
    assert response.status_code == 422

    # Test with rate in invalid state (Draft) returns 400
    test_rate.status = 'draft'
    response = client.post(f'/api/v1/rates/{test_rate.id}/counter', json=counter_proposal_data, headers=auth_headers)
    assert response.status_code == 400

    # Test access control - only client users can counter-propose rates
    # TODO: Implement access control tests

# Test rate validation rules
async def test_rate_validation_rules(client, auth_headers, create_test_client_org, create_test_attorney):
    # Configure test client organization with rate rules (5% max increase, 90-day notice, Q4 submission window)
    client_org = create_test_client_org
    client_org.settings = {
        'rate_rules': {
            'max_increase': 5.0,
            'notice_period': 90,
            'submission_window': {
                'start_month': 10,
                'start_day': 1,
                'end_month': 12,
                'end_day': 31
            }
        }
    }

    # Create current rate for attorney with known amount
    test_attorney = await create_test_attorney(organization_id=client_org.id)
    current_rate_data = {
        'attorney_id': str(test_attorney.id),
        'client_id': str(client_org.id),
        'firm_id': str(test_attorney.organization_id),
        'amount': 750.00,
        'currency': 'USD',
        'effective_date': '2023-01-01'
    }
    response = client.post('/api/v1/rates', json=current_rate_data, headers=auth_headers)
    assert response.status_code == 201
    current_rate_id = response.get_json()['id']

    # Attempt to create a new rate exceeding maximum increase percentage (>5%)
    new_rate_data_exceeds_max_increase = {
        'attorney_id': str(test_attorney.id),
        'client_id': str(client_org.id),
        'firm_id': str(test_attorney.organization_id),
        'amount': 800.00,
        'currency': 'USD',
        'effective_date': '2024-01-01'
    }
    response = client.post('/api/v1/rates', json=new_rate_data_exceeds_max_increase, headers=auth_headers)
    assert response.status_code == 422
    assert 'exceeds maximum allowed increase' in response.get_json()['message']

    # Attempt to create a rate during freeze period
    new_rate_data_freeze_period = {
        'attorney_id': str(test_attorney.id),
        'client_id': str(client_org.id),
        'firm_id': str(test_attorney.organization_id),
        'amount': 760.00,
        'currency': 'USD',
        'effective_date': '2023-06-01'
    }
    response = client.post('/api/v1/rates', json=new_rate_data_freeze_period, headers=auth_headers)
    assert response.status_code == 422
    assert 'within the rate freeze period' in response.get_json()['message']

    # Attempt to create a rate with effective date not meeting notice requirement
    new_rate_data_notice_period = {
        'attorney_id': str(test_attorney.id),
        'client_id': str(client_org.id),
        'firm_id': str(test_attorney.organization_id),
        'amount': 760.00,
        'currency': 'USD',
        'effective_date': '2023-11-01'
    }
    response = client.post('/api/v1/rates', json=new_rate_data_notice_period, headers=auth_headers)
    assert response.status_code == 422
    assert 'Insufficient notice period provided' in response.get_json()['message']

    # Attempt to submit outside of submission window
    new_rate_data_submission_window = {
        'attorney_id': str(test_attorney.id),
        'client_id': str(client_org.id),
        'firm_id': str(test_attorney.organization_id),
        'amount': 760.00,
        'currency': 'USD',
        'effective_date': '2024-01-01'
    }
    response = client.post('/api/v1/rates', json=new_rate_data_submission_window, headers=auth_headers)
    assert response.status_code == 422
    assert 'outside the allowed submission window' in response.get_json()['message']

# Test bulk operations on rates
async def test_bulk_rate_operations(client, auth_headers, create_test_rate):
    # Create multiple test rates with Submitted status
    test_rate1 = await create_test_rate()
    test_rate1.status = 'submitted'
    test_rate2 = await create_test_rate()
    test_rate2.status = 'submitted'
    test_rate3 = await create_test_rate()
    test_rate3.status = 'submitted'

    # Send POST request to /api/v1/rates/bulk/approve with list of rate IDs
    rate_ids_to_approve = [str(test_rate1.id), str(test_rate2.id)]
    bulk_approve_data = {'rate_ids': rate_ids_to_approve}
    response = client.post('/api/v1/rates/bulk/approve', json=bulk_approve_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    for rate in data:
        assert rate['status'] == 'approved'

    # Create multiple new test rates with Submitted status
    test_rate4 = await create_test_rate()
    test_rate4.status = 'submitted'
    test_rate5 = await create_test_rate()
    test_rate5.status = 'submitted'
    test_rate6 = await create_test_rate()
    test_rate6.status = 'submitted'

    # Send POST request to /api/v1/rates/bulk/reject with list of rate IDs and reason
    rate_ids_to_reject = [str(test_rate4.id), str(test_rate5.id)]
    bulk_reject_data = {'rate_ids': rate_ids_to_reject, 'reason': 'Not justified'}
    response = client.post('/api/v1/rates/bulk/reject', json=bulk_reject_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    for rate in data:
        assert rate['status'] == 'rejected'

    # Create multiple new test rates with Submitted status
    test_rate7 = await create_test_rate()
    test_rate7.status = 'submitted'
    test_rate8 = await create_test_rate()
    test_rate8.status = 'submitted'
    test_rate9 = await create_test_rate()
    test_rate9.status = 'submitted'

    # Send POST request to /api/v1/rates/bulk/counter with list of rate IDs and counter amounts
    rate_ids_to_counter = [str(test_rate7.id), str(test_rate8.id)]
    bulk_counter_data = {'rate_ids': rate_ids_to_counter, 'counter_amount': 650.00}
    response = client.post('/api/v1/rates/bulk/counter', json=bulk_counter_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    for rate in data:
        assert rate['amount'] == 650.00
        assert rate['status'] == 'counter_proposed'

    # Test with mix of valid and invalid IDs returns partial success
    # TODO: Implement test with mix of valid and invalid IDs

    # Test access control - only users with appropriate permissions can perform bulk operations
    # TODO: Implement access control tests

# Test creating and retrieving rates for staff classes
async def test_staff_class_rates(client, auth_headers, create_test_staff_class, create_test_client_org, create_test_firm_org):
    # Create valid staff class rate data
    test_staff_class = await create_test_staff_class(organization_id=create_test_client_org.id)
    staff_class_rate_data = {
        'staff_class_id': str(test_staff_class.id),
        'client_id': str(create_test_client_org.id),
        'firm_id': str(create_test_firm_org.id),
        'amount': 400.00,
        'currency': 'USD',
        'effective_date': '2023-01-01'
    }

    # Send POST request to /api/v1/rates/staff_class with staff class rate data
    response = client.post('/api/v1/rates/staff_class', json=staff_class_rate_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.get_json()
    assert data['staff_class_id'] == str(test_staff_class.id)
    assert data['client_id'] == str(create_test_client_org.id)
    assert data['firm_id'] == str(create_test_firm_org.id)
    assert data['amount'] == 400.00
    assert data['currency'] == 'USD'
    assert data['effective_date'] == '2023-01-01'

    # Send GET request to /api/v1/rates/staff_class/{staff_class_id}
    response = client.get(f'/api/v1/rates/staff_class/{test_staff_class.id}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['staff_class_id'] == str(test_staff_class.id)
    assert data['client_id'] == str(create_test_client_org.id)
    assert data['firm_id'] == str(create_test_firm_org.id)
    assert data['amount'] == 400.00
    assert data['currency'] == 'USD'
    assert data['effective_date'] == '2023-01-01'

    # Test filtering staff class rates by client, firm, and staff class
    # TODO: Implement filtering tests

    # Test staff class rate validation rules (similar to attorney rates)
    # TODO: Implement validation tests

    # Test staff class rate approval, rejection and counter-proposal workflows
    # TODO: Implement workflow tests