"""
Unit tests for the database models in the Justice Bid Rate Negotiation System.
Tests model initialization, attribute validation, relationships between models, and model methods to ensure proper functionality and data integrity.
"""
import pytest  # package_version: latest
import uuid  # package_version: standard library
import datetime  # package_version: standard library
import decimal  # package_version: standard library

from src.backend.db.models.user import User  # type: ignore
from src.backend.db.models.organization import Organization, Office, Department  # type: ignore
from src.backend.db.models.attorney import Attorney  # type: ignore
from src.backend.db.models.rate import Rate  # type: ignore
from src.backend.db.models.staff_class import StaffClass  # type: ignore
from src.backend.db.models.common import TimestampMixin, AuditMixin, SoftDeleteMixin, OrganizationScopedMixin, BaseModel  # type: ignore
from src.backend.utils.constants import UserRole, OrganizationType, RATE_STATUSES, RATE_TYPES  # type: ignore


def test_base_model():
    """Test the BaseModel class functionality"""
    # Create a BaseModel instance
    model = BaseModel()

    # Verify the ID is a valid UUID
    assert isinstance(model.id, uuid.UUID)

    # Test as_dict method returns correct dictionary
    model_dict = model.as_dict()
    assert isinstance(model_dict, dict)
    assert 'id' in model_dict
    assert model_dict['id'] == model.id

    # Test from_dict method correctly updates model attributes
    new_data = {'new_attribute': 'test_value'}
    model.from_dict(new_data)
    assert not hasattr(model, 'new_attribute')  # Should not add new attributes


def test_timestamp_mixin():
    """Test the TimestampMixin functionality"""
    # Create a model instance with TimestampMixin
    class TestModel(TimestampMixin):
        pass

    model = TestModel()

    # Verify created_at is set to a datetime
    assert isinstance(model.created_at, datetime.datetime)

    # Verify updated_at is set to the same value initially
    assert isinstance(model.updated_at, datetime.datetime)
    assert model.created_at == model.updated_at

    # Modify the model and verify updated_at changes
    old_updated_at = model.updated_at
    model.updated_at = datetime.datetime.utcnow()
    assert model.updated_at > old_updated_at


def test_audit_mixin():
    """Test the AuditMixin functionality"""
    # Create a model instance with AuditMixin
    class TestModel(AuditMixin):
        pass

    model = TestModel()

    # Set created_by_id and updated_by_id
    created_by_id = uuid.uuid4()
    updated_by_id = uuid.uuid4()
    model.created_by_id = created_by_id
    model.updated_by_id = updated_by_id

    # Verify the audit fields are correctly stored
    assert model.created_by_id == created_by_id
    assert model.updated_by_id == updated_by_id


def test_soft_delete_mixin():
    """Test the SoftDeleteMixin functionality"""
    # Create a model instance with SoftDeleteMixin
    class TestModel(SoftDeleteMixin):
        pass

    model = TestModel()

    # Verify is_deleted is False by default
    assert model.is_deleted is False
    assert model.deleted_at is None
    assert model.deleted_by_id is None

    # Call delete method with a user_id
    user_id = uuid.uuid4()
    model.delete(user_id=user_id)

    # Verify is_deleted is True and deleted timestamps are set
    assert model.is_deleted is True
    assert isinstance(model.deleted_at, datetime.datetime)
    assert model.deleted_by_id == user_id

    # Call restore method
    model.restore()

    # Verify is_deleted is False and deleted fields are cleared
    assert model.is_deleted is False
    assert model.deleted_at is None
    assert model.deleted_by_id is None


def test_organization_scoped_mixin():
    """Test the OrganizationScopedMixin functionality"""
    # Create a model instance with OrganizationScopedMixin
    class TestModel(OrganizationScopedMixin):
        pass

    model = TestModel()

    # Set organization_id
    organization_id = uuid.uuid4()
    model.organization_id = organization_id

    # Verify the organization_id is correctly stored
    assert model.organization_id == organization_id


def test_user_model_init():
    """Test User model initialization"""
    # Create a User instance with all required attributes
    email = "test@example.com"
    name = "Test User"
    password = "secure_password"
    organization_id = uuid.uuid4()
    user = User(email=email, name=name, password=password, organization_id=organization_id)

    # Verify all attributes are correctly set
    assert user.email == email
    assert user.name == name
    assert user.organization_id == organization_id
    assert user.password_hash is not None  # Password should be hashed
    assert user.role == UserRole.STANDARD_USER  # Default role
    assert user.is_active is True  # Default is_active

    # Verify default values are set for optional attributes
    assert user.last_login is None
    assert user.mfa_enabled is False
    assert user.mfa_secret is None
    assert user.password_changed_at is not None
    assert user.permissions == {}
    assert user.preferences == {}

    # Verify is_active is True by default


def test_user_password_methods():
    """Test User model password handling methods"""
    # Create a User with a password
    email = "test@example.com"
    name = "Test User"
    password = "secure_password"
    organization_id = uuid.uuid4()
    user = User(email=email, name=name, password=password, organization_id=organization_id)

    # Verify password is hashed, not stored as plaintext
    assert user.password_hash != password

    # Test verify_password returns True for correct password
    assert user.verify_password(password) is True

    # Test verify_password returns False for incorrect password
    assert user.verify_password("wrong_password") is False

    # Change password with set_password
    new_password = "new_secure_password"
    user.set_password(new_password)

    # Verify old password no longer works
    assert user.verify_password(password) is False

    # Verify new password works
    assert user.verify_password(new_password) is True

    # Verify password_changed_at is updated
    assert user.password_changed_at is not None


def test_user_permission_methods():
    """Test User model permission management methods"""
    # Create a User with no permissions
    email = "test@example.com"
    name = "Test User"
    password = "secure_password"
    organization_id = uuid.uuid4()
    user = User(email=email, name=name, password=password, organization_id=organization_id)

    # Verify has_permission returns False for any permission
    assert user.has_permission("some_permission") is False

    # Add a permission with add_permission
    user.add_permission("test_permission")

    # Verify has_permission returns True for that permission
    assert user.has_permission("test_permission") is True

    # Verify has_permission returns False for other permissions
    assert user.has_permission("another_permission") is False

    # Remove the permission with remove_permission
    user.remove_permission("test_permission")

    # Verify has_permission returns False for that permission
    assert user.has_permission("test_permission") is False

    # Test add_permission returns False when permission already exists
    assert user.add_permission("test_permission") is True
    assert user.add_permission("test_permission") is False

    # Test remove_permission returns False when permission doesn't exist
    assert user.remove_permission("nonexistent_permission") is False


def test_user_role_methods():
    """Test User model role-based methods"""
    # Create a User with STANDARD_USER role
    email = "test@example.com"
    name = "Test User"
    password = "secure_password"
    organization_id = uuid.uuid4()
    user = User(email=email, name=name, password=password, organization_id=organization_id)

    # Verify is_administrator returns False
    assert user.is_administrator() is False

    # Change role to ORGANIZATION_ADMINISTRATOR
    user.role = UserRole.ORGANIZATION_ADMINISTRATOR

    # Verify is_administrator returns True
    assert user.is_administrator() is True

    # Change role to SYSTEM_ADMINISTRATOR
    user.role = UserRole.SYSTEM_ADMINISTRATOR

    # Verify is_administrator returns True
    assert user.is_administrator() is True


def test_user_mfa_methods():
    """Test User model MFA methods"""
    # Create a User with MFA disabled
    email = "test@example.com"
    name = "Test User"
    password = "secure_password"
    organization_id = uuid.uuid4()
    user = User(email=email, name=name, password=password, organization_id=organization_id)

    # Verify mfa_enabled is False
    assert user.mfa_enabled is False
    assert user.mfa_secret is None

    # Enable MFA with a secret
    mfa_secret = "test_mfa_secret"
    user.enable_mfa(mfa_secret)

    # Verify mfa_enabled is True and secret is stored
    assert user.mfa_enabled is True
    assert user.mfa_secret == mfa_secret

    # Disable MFA
    user.disable_mfa()

    # Verify mfa_enabled is False and secret is None
    assert user.mfa_enabled is False
    assert user.mfa_secret is None


def test_user_preference_methods():
    """Test User model preference methods"""
    # Create a User with no preferences
    email = "test@example.com"
    name = "Test User"
    password = "secure_password"
    organization_id = uuid.uuid4()
    user = User(email=email, name=name, password=password, organization_id=organization_id)

    # Set a preference with set_preference
    user.set_preference("test_key", "test_value")

    # Verify get_preference returns the correct value
    assert user.get_preference("test_key") == "test_value"

    # Verify get_preference returns default value for missing preferences
    assert user.get_preference("missing_key", "default_value") == "default_value"

    # Update an existing preference
    user.set_preference("test_key", "updated_value")

    # Verify the preference was updated
    assert user.get_preference("test_key") == "updated_value"


def test_organization_model_init():
    """Test Organization model initialization"""
    # Create an Organization with all required attributes
    name = "Test Organization"
    type = OrganizationType.LAW_FIRM
    organization = Organization(name=name, type=type)

    # Verify all attributes are correctly set
    assert organization.name == name
    assert organization.type == type

    # Verify default values are set for optional attributes
    assert organization.domain is None
    assert organization.is_active is True
    assert organization.settings == {}


def test_organization_type_methods():
    """Test Organization type methods"""
    # Create an Organization with LAW_FIRM type
    name = "Test Law Firm"
    organization = Organization(name=name, type=OrganizationType.LAW_FIRM)

    # Verify is_law_firm returns True
    assert organization.is_law_firm() is True

    # Verify is_client returns False
    assert organization.is_client() is False

    # Change type to CLIENT
    organization.type = OrganizationType.CLIENT

    # Verify is_law_firm returns False
    assert organization.is_law_firm() is False

    # Verify is_client returns True
    assert organization.is_client() is True

    # Change type to ADMIN
    organization.type = OrganizationType.ADMIN

    # Verify is_admin returns True
    assert organization.is_admin() is True

    # Verify is_law_firm and is_client return False
    assert organization.is_law_firm() is False
    assert organization.is_client() is False


def test_organization_settings_methods():
    """Test Organization settings methods"""
    # Create an Organization with no settings
    name = "Test Organization"
    type = OrganizationType.LAW_FIRM
    organization = Organization(name=name, type=type)

    # Set a setting with set_setting
    organization.set_setting("test_key", "test_value")

    # Verify get_setting returns the correct value
    assert organization.get_setting("test_key") == "test_value"

    # Verify get_setting returns default value for missing settings
    assert organization.get_setting("missing_key", "default_value") == "default_value"

    # Update an existing setting
    organization.set_setting("test_key", "updated_value")

    # Verify the setting was updated
    assert organization.get_setting("test_key") == "updated_value"

    # Test rate rules methods
    rate_rules = {"max_increase": 5, "notice_period": 90}
    organization.set_rate_rules(rate_rules)
    assert organization.get_rate_rules() == rate_rules


def test_organization_structure_methods():
    """Test Organization structure methods (departments, offices)"""
    # Create an Organization
    name = "Test Organization"
    type = OrganizationType.LAW_FIRM
    organization = Organization(name=name, type=type)

    # Add a department with add_department
    department_name = "Litigation"
    department_metadata = {"head": "John Doe"}
    department = organization.add_department(name=department_name, metadata=department_metadata)

    # Verify department was created with correct attributes
    assert department.name == department_name
    assert department.metadata == department_metadata
    assert department.organization_id == organization.id

    # Verify organization-department relationship is established
    assert department in organization.departments

    # Add an office with add_office
    office_name = "New York Office"
    office_city = "New York"
    office_state = "NY"
    office_country = "USA"
    office = organization.add_office(name=office_name, city=office_city, state=office_state, country=office_country)

    # Verify office was created with correct attributes
    assert office.name == office_name
    assert office.city == office_city
    assert office.state == office_state
    assert office.country == office_country
    assert office.organization_id == organization.id

    # Verify organization-office relationship is established
    assert office in organization.offices


def test_organization_status_methods():
    """Test Organization status methods"""
    # Create an Organization (active by default)
    name = "Test Organization"
    type = OrganizationType.LAW_FIRM
    organization = Organization(name=name, type=type)

    # Verify is_active is True
    assert organization.is_active is True

    # Deactivate the organization
    organization.deactivate()

    # Verify is_active is False
    assert organization.is_active is False

    # Activate the organization
    organization.activate()

    # Verify is_active is True
    assert organization.is_active is True


def test_attorney_model_init():
    """Test Attorney model initialization"""
    # Create an Attorney with all required attributes
    organization_id = uuid.uuid4()
    name = "Test Attorney"
    attorney = Attorney(organization_id=organization_id, name=name)

    # Verify all attributes are correctly set
    assert attorney.organization_id == organization_id
    assert attorney.name == name

    # Verify default values are set for optional attributes
    assert attorney.bar_date is None
    assert attorney.graduation_date is None
    assert attorney.promotion_date is None
    assert attorney.office_ids == []
    assert attorney.timekeeper_ids == {}
    assert attorney.unicourt_id is None
    assert attorney.performance_data == {}
    assert attorney.staff_class_id is None


def test_attorney_timekeeper_methods():
    """Test Attorney timekeeper ID methods"""
    # Create an Attorney with no timekeeper IDs
    organization_id = uuid.uuid4()
    name = "Test Attorney"
    attorney = Attorney(organization_id=organization_id, name=name)

    # Add a timekeeper ID for a specific client
    client_id = "client123"
    timekeeper_id = "tk456"
    attorney.add_timekeeper_id(client_id=client_id, timekeeper_id=timekeeper_id)

    # Verify get_timekeeper_id returns the correct ID for that client
    assert attorney.get_timekeeper_id(client_id=client_id) == timekeeper_id

    # Verify get_timekeeper_id returns None for other clients
    assert attorney.get_timekeeper_id(client_id="other_client") is None

    # Update a timekeeper ID for an existing client
    new_timekeeper_id = "tk789"
    attorney.add_timekeeper_id(client_id=client_id, timekeeper_id=new_timekeeper_id)

    # Verify the timekeeper ID was updated
    assert attorney.get_timekeeper_id(client_id=client_id) == new_timekeeper_id


def test_attorney_performance_data():
    """Test Attorney performance data methods"""
    # Create an Attorney with no performance data
    organization_id = uuid.uuid4()
    name = "Test Attorney"
    attorney = Attorney(organization_id=organization_id, name=name)

    # Update performance data with update_performance_data
    new_data = {"win_rate": 0.85, "avg_settlement": 100000}
    attorney.update_performance_data(new_data)

    # Verify the performance data was correctly stored
    assert attorney.performance_data == new_data

    # Update with additional performance data
    additional_data = {"cases_won": 50}
    attorney.update_performance_data(additional_data)

    # Verify the data was merged, not overwritten
    assert attorney.performance_data["win_rate"] == 0.85
    assert attorney.performance_data["avg_settlement"] == 100000
    assert attorney.performance_data["cases_won"] == 50


def test_attorney_rate_methods():
    """Test Attorney rate methods"""
    # Create an Attorney
    organization_id = uuid.uuid4()
    name = "Test Attorney"
    attorney = Attorney(organization_id=organization_id, name=name)

    # Create multiple Rate objects for the attorney with different date ranges
    from src.backend.db.models.rate import Rate
    from datetime import date
    from decimal import Decimal

    rate1 = Rate(attorney_id=attorney.id, client_id=uuid.uuid4(), firm_id=organization_id, office_id=uuid.uuid4(), staff_class_id=uuid.uuid4(), amount=Decimal(100), currency="USD", effective_date=date(2023, 1, 1), expiration_date=date(2023, 6, 30))
    rate2 = Rate(attorney_id=attorney.id, client_id=uuid.uuid4(), firm_id=organization_id, office_id=uuid.uuid4(), staff_class_id=uuid.uuid4(), amount=Decimal(120), currency="USD", effective_date=date(2023, 7, 1), expiration_date=date(2023, 12, 31))
    rate3 = Rate(attorney_id=attorney.id, client_id=uuid.uuid4(), firm_id=organization_id, office_id=uuid.uuid4(), staff_class_id=uuid.uuid4(), amount=Decimal(150), currency="USD", effective_date=date(2024, 1, 1), expiration_date=None)

    # Call get_current_rates
    attorney.rates = [rate1, rate2, rate3]
    current_rates = attorney.get_current_rates()

    # Verify only rates that are currently active are returned
    assert len(current_rates) == 0

    # Test with a specific reference date
    from datetime import datetime
    reference_date = datetime(2023, 8, 1).date()
    current_rates = attorney.get_current_rates()

    # Verify rates active on that date are returned
    assert len(current_rates) == 0


def test_rate_model_init():
    """Test Rate model initialization"""
    # Create a Rate with all required attributes
    attorney_id = uuid.uuid4()
    client_id = uuid.uuid4()
    firm_id = uuid.uuid4()
    office_id = uuid.uuid4()
    staff_class_id = uuid.uuid4()
    amount = decimal.Decimal(100.00)
    currency = "USD"
    effective_date = datetime.date(2023, 1, 1)
    rate = Rate(attorney_id=attorney_id, client_id=client_id, firm_id=firm_id, office_id=office_id, staff_class_id=staff_class_id, amount=amount, currency=currency, effective_date=effective_date)

    # Verify all attributes are correctly set
    assert rate.attorney_id == attorney_id
    assert rate.client_id == client_id
    assert rate.firm_id == firm_id
    assert rate.office_id == office_id
    assert rate.staff_class_id == staff_class_id
    assert rate.amount == amount
    assert rate.currency == currency
    assert rate.effective_date == effective_date

    # Verify default values are set for optional attributes
    assert rate.expiration_date is None
    assert rate.history == []
    assert rate.status.value == 'draft'
    assert rate.type.value == 'standard'


def test_rate_validation():
    """Test Rate model validation methods"""
    # Create a Rate with all required attributes
    attorney_id = uuid.uuid4()
    client_id = uuid.uuid4()
    firm_id = uuid.uuid4()
    office_id = uuid.uuid4()
    staff_class_id = uuid.uuid4()
    amount = decimal.Decimal(100.00)
    currency = "USD"
    effective_date = datetime.date(2023, 1, 1)
    rate = Rate(attorney_id=attorney_id, client_id=client_id, firm_id=firm_id, office_id=office_id, staff_class_id=staff_class_id, amount=amount, currency=currency, effective_date=effective_date)

    # Test validate_currency with valid and invalid currencies
    with pytest.raises(ValueError):
        rate.currency = "invalid"
        rate.validate_currency('currency', rate.currency)

    rate.currency = "USD"
    assert rate.validate_currency('currency', rate.currency) == "USD"

    # Test validate_amount with positive and non-positive values
    with pytest.raises(ValueError):
        rate.amount = 0
        rate.validate_amount('amount', rate.amount)

    rate.amount = decimal.Decimal(100.00)
    assert rate.validate_amount('amount', rate.amount) == decimal.Decimal(100.00)

    # Test validate_dates with valid and invalid date ranges
    with pytest.raises(ValueError):
        rate.expiration_date = datetime.date(2022, 1, 1)
        rate.validate_dates('expiration_date', rate.expiration_date)

    rate.expiration_date = datetime.date(2024, 1, 1)
    assert rate.validate_dates('expiration_date', rate.expiration_date) == datetime.date(2024, 1, 1)


def test_rate_date_methods():
    """Test Rate date-related methods"""
    # Create a Rate with specific effective and expiration dates
    attorney_id = uuid.uuid4()
    client_id = uuid.uuid4()
    firm_id = uuid.uuid4()
    office_id = uuid.uuid4()
    staff_class_id = uuid.uuid4()
    amount = decimal.Decimal(100.00)
    currency = "USD"
    effective_date = datetime.date(2023, 1, 1)
    expiration_date = datetime.date(2023, 12, 31)
    rate = Rate(attorney_id=attorney_id, client_id=client_id, firm_id=firm_id, office_id=office_id, staff_class_id=staff_class_id, amount=amount, currency=currency, effective_date=effective_date, expiration_date=expiration_date)

    # Test is_active with different reference dates
    # Verify is_active returns True for dates between effective and expiration
    assert rate.is_active(reference_date=datetime.date(2023, 6, 1)) is True

    # Verify is_active returns False for dates outside the range
    assert rate.is_active(reference_date=datetime.date(2022, 12, 31)) is False
    assert rate.is_active(reference_date=datetime.date(2024, 1, 1)) is False


def test_rate_history_methods():
    """Test Rate history methods"""
    # Create a Rate with no history
    attorney_id = uuid.uuid4()
    client_id = uuid.uuid4()
    firm_id = uuid.uuid4()
    office_id = uuid.uuid4()
    staff_class_id = uuid.uuid4()
    amount = decimal.Decimal(100.00)
    currency = "USD"
    effective_date = datetime.date(2023, 1, 1)
    rate = Rate(attorney_id=attorney_id, client_id=client_id, firm_id=firm_id, office_id=office_id, staff_class_id=staff_class_id, amount=amount, currency=currency, effective_date=effective_date)

    # Add history entries with add_history_entry
    user_id = uuid.uuid4()
    rate.add_history_entry(previous_amount=decimal.Decimal(90.00), previous_status="Draft", previous_type="Standard", user_id=user_id, message="Initial rate")
    rate.add_history_entry(previous_amount=decimal.Decimal(100.00), previous_status="Submitted", previous_type="Proposed", user_id=user_id, message="Rate increase")

    # Verify entries are correctly added to history list
    assert len(rate.history) == 2
    assert rate.history[0]['message'] == "Initial rate"
    assert rate.history[1]['message'] == "Rate increase"

    # Call get_history_timeline
    timeline = rate.get_history_timeline()

    # Verify timeline includes creation and all history entries
    assert len(timeline) == 3
    assert timeline[0]['event_type'] == "creation"
    assert timeline[1]['message'] == "Initial rate"
    assert timeline[2]['message'] == "Rate increase"

    # Verify timeline is sorted by timestamp
    assert timeline[0]['timestamp'] < timeline[1]['timestamp']
    assert timeline[1]['timestamp'] < timeline[2]['timestamp']


def test_rate_calculation_methods():
    """Test Rate calculation methods"""
    # Create a Rate with a specific amount
    attorney_id = uuid.uuid4()
    client_id = uuid.uuid4()
    firm_id = uuid.uuid4()
    office_id = uuid.uuid4()
    staff_class_id = uuid.uuid4()
    amount = decimal.Decimal(100.00)
    currency = "USD"
    effective_date = datetime.date(2023, 1, 1)
    rate = Rate(attorney_id=attorney_id, client_id=client_id, firm_id=firm_id, office_id=office_id, staff_class_id=staff_class_id, amount=amount, currency=currency, effective_date=effective_date)

    # Test calculate_increase_percentage with various previous rates
    # Verify correct percentage calculation for increases
    assert rate.calculate_increase_percentage(previous_rate=decimal.Decimal(90.00)) == 11.11

    # Verify correct percentage calculation for decreases
    assert rate.calculate_increase_percentage(previous_rate=decimal.Decimal(110.00)) == -9.09

    # Verify handling of zero or None previous rates
    assert rate.calculate_increase_percentage(previous_rate=0) is None
    assert rate.calculate_increase_percentage(previous_rate=None) is None


def test_rate_approval_methods():
    """Test Rate approval methods"""
    # Create a Rate with status 'Draft'
    attorney_id = uuid.uuid4()
    client_id = uuid.uuid4()
    firm_id = uuid.uuid4()
    office_id = uuid.uuid4()
    staff_class_id = uuid.uuid4()
    amount = decimal.Decimal(100.00)
    currency = "USD"
    effective_date = datetime.date(2023, 1, 1)
    rate = Rate(attorney_id=attorney_id, client_id=client_id, firm_id=firm_id, office_id=office_id, staff_class_id=staff_class_id, amount=amount, currency=currency, effective_date=effective_date, status="Draft")

    # Verify is_approved returns False
    assert rate.is_approved() is False

    # Change status to 'Approved'
    rate.status = "Approved"

    # Verify is_approved returns True
    assert rate.is_approved() is False

    # Change status to other values
    rate.status = "Rejected"

    # Verify is_approved returns False for non-approved statuses
    assert rate.is_approved() is False