"""
Pytest configuration file containing fixtures for testing the Justice Bid Rate Negotiation System backend.
"""
import pytest  # pytest version: ^7.3.1
from sqlalchemy import create_engine  # SQLAlchemy version: ^2.0.0
from sqlalchemy.orm import sessionmaker  # SQLAlchemy version: ^2.0.0
from flask import Flask  # Flask version: ^2.3.0
import json  # standard library
import uuid  # standard library
import datetime  # standard library
import tempfile  # standard library
import os  # standard library

from ..app.app import create_app  # Import the Flask application factory function
from ..db.base import Base  # Import the SQLAlchemy Base class
from ..db.session import db_session  # Import the database session
from ..db.models.user import User  # Import the User model
from ..db.models.organization import Organization  # Import the Organization model
from ..db.models.attorney import Attorney  # Import the Attorney model
from ..db.models.rate import Rate  # Import the Rate model
from ..db.models.negotiation import Negotiation  # Import the Negotiation model
from ..services.auth.jwt import create_access_token  # Import JWT token creation function


def request_ctx(app, path, **kwargs):
    """Utility function to create a request context for testing.

    Args:
        app: app
        path: path
        kwargs: kwargs

    Returns:
        Flask request context for testing
    """
    # Create a test request context with the given path
    ctx = app.test_request_context(path)
    # Update context with any additional kwargs
    ctx.request.kwargs = kwargs
    # Return the context for use in tests
    return ctx


@pytest.fixture(scope='session')
def app():
    """Fixture that creates a Flask application configured for testing."""
    # Create a Flask application with test configuration
    app = create_app(env_name='testing')
    # Configure the app for testing (DEBUG=True, TESTING=True)
    app.config.update({
        'DEBUG': True,
        'TESTING': True,
    })
    # Configure a test database URI using SQLite in-memory database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    # Set up application context
    with app.app_context():
        # Yield the application for tests
        yield app

    # Clean up application context after tests


@pytest.fixture(scope='function')
def client(app):
    """Fixture that creates a Flask test client for making requests to the application."""
    # Create a test client from the app fixture
    client = app.test_client()
    # Configure the client to handle JSON requests and responses
    client.environ_base['CONTENT_TYPE'] = 'application/json'

    # Yield the client for tests
    yield client

    # Clean up after tests


@pytest.fixture(scope='session')
def db(app):
    """Fixture that sets up a test database and yields a session for database operations."""
    # Create all tables in the test database
    with app.app_context():
        Base.metadata.create_all(bind=app.engine)

        # Yield the database session for tests
        yield app.db_session

        # Roll back any changes after each test
        app.db_session.rollback()

        # Drop all tables after all tests are done
        Base.metadata.drop_all(bind=app.engine)


@pytest.fixture(scope='function')
def db_session(db):
    """Fixture that provides a fresh database session for each test function."""
    # Create a new database session
    connection = db.engine.connect()
    transaction = connection.begin()
    session = db
    # Yield the session for the test
    yield session

    # Roll back any changes after the test
    transaction.rollback()
    connection.close()


@pytest.fixture(scope='function')
def admin_user(db_session):
    """Fixture that creates an admin user for testing."""
    # Create user data with admin role
    user_data = {
        'email': 'admin@example.com',
        'name': 'Admin User',
        'password': 'secure_password',
        'organization_id': uuid.uuid4(),
        'role': 'system_administrator'
    }
    # Create a new admin user in the database
    user = User(email=user_data['email'], name=user_data['name'], password=user_data['password'], organization_id=user_data['organization_id'], role=user_data['role'])
    # Set password using secure hashing
    user.set_password(user_data['password'])
    # Commit the changes
    db_session.add(user)
    db_session.commit()
    # Yield the user for tests
    yield user

    # Roll back changes after the test
    db_session.rollback()


@pytest.fixture(scope='function')
def client_user(db_session, client_organization):
    """Fixture that creates a client user for testing."""
    # Create user data with client role
    user_data = {
        'email': 'client@example.com',
        'name': 'Client User',
        'password': 'secure_password',
        'organization_id': client_organization.id,
        'role': 'standard_user'
    }
    # Create a new client user in the database
    user = User(email=user_data['email'], name=user_data['name'], password=user_data['password'], organization_id=user_data['organization_id'], role=user_data['role'])
    # Associate the user with a client organization
    user.organization = client_organization
    # Set password using secure hashing
    user.set_password(user_data['password'])
    # Commit the changes
    db_session.add(user)
    db_session.commit()
    # Yield the user for tests
    yield user

    # Roll back changes after the test
    db_session.rollback()


@pytest.fixture(scope='function')
def law_firm_user(db_session, law_firm_organization):
    """Fixture that creates a law firm user for testing."""
    # Create user data with law firm role
    user_data = {
        'email': 'lawfirm@example.com',
        'name': 'Law Firm User',
        'password': 'secure_password',
        'organization_id': law_firm_organization.id,
        'role': 'rate_administrator'
    }
    # Create a new law firm user in the database
    user = User(email=user_data['email'], name=user_data['name'], password=user_data['password'], organization_id=user_data['organization_id'], role=user_data['role'])
    # Associate the user with a law firm organization
    user.organization = law_firm_organization
    # Set password using secure hashing
    user.set_password(user_data['password'])
    # Commit the changes
    db_session.add(user)
    db_session.commit()
    # Yield the user for tests
    yield user

    # Roll back changes after the test
    db_session.rollback()


@pytest.fixture(scope='function')
def client_organization(db_session):
    """Fixture that creates a client organization for testing."""
    # Create organization data with client type
    org_data = {
        'name': 'Acme Corporation',
        'type': 'client',
        'domain': 'acme.com'
    }
    # Create a new client organization in the database
    organization = Organization(name=org_data['name'], type=org_data['type'], domain=org_data['domain'])
    # Set up default rate rules and settings
    organization.settings = {
        'rate_rules': {
            'max_increase': 5.0,
            'notice_period': 60
        }
    }
    # Commit the changes
    db_session.add(organization)
    db_session.commit()
    # Yield the organization for tests
    yield organization

    # Roll back changes after the test
    db_session.rollback()


@pytest.fixture(scope='function')
def law_firm_organization(db_session):
    """Fixture that creates a law firm organization for testing."""
    # Create organization data with law firm type
    org_data = {
        'name': 'Smith & Jones',
        'type': 'law_firm',
        'domain': 'smithjones.com'
    }
    # Create a new law firm organization in the database
    organization = Organization(name=org_data['name'], type=org_data['type'], domain=org_data['domain'])
    # Set up default settings
    organization.settings = {
        'billing_system': 'LEDES'
    }
    # Commit the changes
    db_session.add(organization)
    db_session.commit()
    # Yield the organization for tests
    yield organization

    # Roll back changes after the test
    db_session.rollback()


@pytest.fixture(scope='function')
def attorney(db_session, law_firm_organization):
    """Fixture that creates an attorney for testing."""
    # Create attorney data with required fields
    attorney_data = {
        'name': 'John Doe',
        'organization_id': law_firm_organization.id,
        'bar_date': datetime.date(2010, 1, 1),
        'graduation_date': datetime.date(2007, 6, 1)
    }
    # Create a new attorney in the database
    attorney = Attorney(name=attorney_data['name'], organization_id=attorney_data['organization_id'], bar_date=attorney_data['bar_date'], graduation_date=attorney_data['graduation_date'])
    # Associate the attorney with a law firm organization
    attorney.organization = law_firm_organization
    # Set up professional information (bar date, practice areas)
    attorney.bar_date = datetime.date(2010, 1, 1)
    attorney.practice_areas = ['Litigation', 'Arbitration']
    # Commit the changes
    db_session.add(attorney)
    db_session.commit()
    # Yield the attorney for tests
    yield attorney

    # Roll back changes after the test
    db_session.rollback()


@pytest.fixture(scope='function')
def rate(db_session, attorney, client_organization):
    """Fixture that creates a rate for testing."""
    # Create rate data with amount, currency, and dates
    rate_data = {
        'attorney_id': attorney.id,
        'client_id': client_organization.id,
        'firm_id': attorney.organization_id,
        'office_id': attorney.office_id,
        'staff_class_id': attorney.staff_class_id,
        'amount': 500.00,
        'currency': 'USD',
        'effective_date': datetime.date(2023, 1, 1),
        'expiration_date': datetime.date(2023, 12, 31)
    }
    # Create a new rate in the database
    rate = Rate(attorney_id=rate_data['attorney_id'], client_id=rate_data['client_id'], firm_id=rate_data['firm_id'], office_id=rate_data['office_id'], staff_class_id=rate_data['staff_class_id'], amount=rate_data['amount'], currency=rate_data['currency'], effective_date=rate_data['effective_date'], expiration_date=rate_data['expiration_date'])
    # Associate the rate with an attorney and client organization
    rate.attorney = attorney
    rate.client = client_organization
    # Set appropriate effective and expiration dates
    rate.effective_date = datetime.date(2023, 1, 1)
    rate.expiration_date = datetime.date(2023, 12, 31)
    # Commit the changes
    db_session.add(rate)
    db_session.commit()
    # Yield the rate for tests
    yield rate

    # Roll back changes after the test
    db_session.rollback()


@pytest.fixture(scope='function')
def negotiation(db_session, client_organization, law_firm_organization):
    """Fixture that creates a negotiation for testing."""
    # Create negotiation data with status and dates
    negotiation_data = {
        'client_id': client_organization.id,
        'firm_id': law_firm_organization.id,
        'status': 'in_progress',
        'request_date': datetime.date(2023, 1, 1),
        'submission_deadline': datetime.date(2023, 6, 30)
    }
    # Create a new negotiation in the database
    negotiation = Negotiation(client_id=negotiation_data['client_id'], firm_id=negotiation_data['firm_id'], status=negotiation_data['status'], request_date=negotiation_data['request_date'], submission_deadline=negotiation_data['submission_deadline'])
    # Associate the negotiation with a client and law firm organization
    negotiation.client = client_organization
    negotiation.firm = law_firm_organization
    # Set appropriate request date and submission deadline
    negotiation.request_date = datetime.date(2023, 1, 1)
    negotiation.submission_deadline = datetime.date(2023, 6, 30)
    # Commit the changes
    db_session.add(negotiation)
    db_session.commit()
    # Yield the negotiation for tests
    yield negotiation

    # Roll back changes after the test
    db_session.rollback()


@pytest.fixture(scope='function')
def admin_token(admin_user):
    """Fixture that creates a JWT token for an admin user."""
    # Create a JWT token for the admin user with admin claims
    token = create_access_token(admin_user)
    # Use create_access_token from jwt service
    # Include appropriate claims (user ID, role, etc.)
    # Set appropriate expiration time
    # Yield the token for tests
    yield token


@pytest.fixture(scope='function')
def client_token(client_user):
    """Fixture that creates a JWT token for a client user."""
    # Create a JWT token for the client user with client role claims
    token = create_access_token(client_user)
    # Use create_access_token from jwt service
    # Include organization ID in claims
    # Set appropriate expiration time
    # Yield the token for tests
    yield token


@pytest.fixture(scope='function')
def law_firm_token(law_firm_user):
    """Fixture that creates a JWT token for a law firm user."""
    # Create a JWT token for the law firm user with law firm role claims
    token = create_access_token(law_firm_user)
    # Use create_access_token from jwt service
    # Include organization ID in claims
    # Set appropriate expiration time
    # Yield the token for tests
    yield token


@pytest.fixture(scope='function')
def auth_client(client, admin_token):
    """Fixture that creates an authenticated client for testing endpoints that require authentication."""
    # Create a test client from the app fixture
    # Set the Authorization header with the admin token
    client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer ' + admin_token
    # Format the header as 'Bearer {token}'
    # Yield the authenticated client for tests
    yield client

    # Clean up after tests


@pytest.fixture(scope='session')
def test_data():
    """Fixture that provides sample test data for various entities."""
    # Create a dictionary with test data for users
    # Create test data for organizations (both client and law firm)
    # Create test data for attorneys with various experience levels
    # Create test data for rates with different amounts and dates
    # Create test data for negotiations in different states
    data = {
        'user': {
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'secure_password'
        },
        'client_org': {
            'name': 'Test Client',
            'type': 'client',
            'domain': 'testclient.com'
        },
        'law_firm_org': {
            'name': 'Test Law Firm',
            'type': 'law_firm',
            'domain': 'testlawfirm.com'
        },
        'attorney': {
            'name': 'Test Attorney',
            'bar_date': datetime.date(2015, 1, 1),
            'graduation_date': datetime.date(2012, 5, 1)
        },
        'rate': {
            'amount': 600.00,
            'currency': 'USD',
            'effective_date': datetime.date(2023, 1, 1),
            'expiration_date': datetime.date(2023, 12, 31)
        },
        'negotiation': {
            'status': 'in_progress',
            'request_date': datetime.date(2023, 1, 1),
            'submission_deadline': datetime.date(2023, 6, 30)
        }
    }
    # Yield the test data for tests
    yield data