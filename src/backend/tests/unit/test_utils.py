"""
Unit tests for utility functions in the backend of the Justice Bid Rate Negotiation System
that validate core helper functionality used throughout the application
"""
import pytest  # pytest v7.3.1
import unittest.mock  # unittest v3.11.0
from freezegun import freeze_time  # freezegun v1.2.2

from src.backend.utils import validators  # Import validation utility functions to test
from src.backend.utils import security  # Import security utility functions to test
from src.backend.utils import encryption  # Import encryption utility functions to test
from src.backend.utils import datetime_utils  # Import date and time utility functions to test
from src.backend.utils import formatting  # Import formatting utility functions to test
from src.backend.utils import currency  # Import currency utility functions to test
from src.backend.utils import file_handling  # Import file handling utility functions to test
from src.backend.utils import storage  # Import storage utility functions to test
from src.backend.utils import email  # Import email utility functions to test
from src.backend.utils import cache  # Import cache utility functions to test


@pytest.mark.parametrize('email,expected', [
    ('valid@example.com', True),
    ('invalid-email', False),
    ('missing@domain', False),
    ('special@characters!.com', False)
])
def test_validate_email(email, expected):
    """Tests the email validation function for various email formats"""
    # Take the parametrized email and expected result
    # Call the validators.validate_email function with the email
    result = validators.validate_email(email, 'email')
    # Assert that the result matches the expected output
    assert result == expected


@pytest.mark.parametrize('password,expected', [
    ('Weak1!', False),
    ('StrongPassword1!', True),
    ('nouppercase1!', False),
    ('NOLOWERCASE1!', False),
    ('NoNumbers!', False),
    ('NoSpecialChars123', False)
])
def test_validate_password_strength(password, expected):
    """Tests the password strength validation function for various passwords"""
    # Take the parametrized password and expected result
    # Call the validators.validate_password_strength function with the password
    result, _ = validators.validate_password_strength(password)
    # Assert that the result matches the expected output
    assert result == expected


def test_hash_password():
    """Tests the password hashing function to ensure it properly hashes passwords"""
    # Create a test password
    password = 'TestPassword123!'
    # Call the security.hash_password function to hash the password
    hashed_password = security.hash_password(password)
    # Assert that the result is a string and not equal to the original password
    assert isinstance(hashed_password, str)
    assert hashed_password != password

    # Assert that hashing the same password again produces a different hash (due to salt)
    hashed_password2 = security.hash_password(password)
    assert hashed_password != hashed_password2


def test_verify_password():
    """Tests the password verification function with correct and incorrect passwords"""
    # Create a test password
    password = 'TestPassword123!'
    # Hash the password using security.hash_password
    hashed_password = security.hash_password(password)
    # Verify that security.verify_password returns True for the correct password and hash
    assert security.verify_password(password, hashed_password) is True
    # Verify that security.verify_password returns False for an incorrect password with the same hash
    assert security.verify_password('WrongPassword', hashed_password) is False


def test_encrypt_decrypt():
    """Tests the encryption and decryption functions to ensure data can be encrypted and correctly decrypted"""
    # Create a test string to encrypt
    test_string = 'This is a secret message!'
    # Encrypt the string using encryption.encrypt
    encrypted_string = encryption.encrypt_string(test_string)
    # Assert that the encrypted value is different from the original
    assert encrypted_string != test_string
    # Decrypt the encrypted string using encryption.decrypt
    decrypted_string = encryption.decrypt_string(encrypted_string)
    # Assert that the decrypted value matches the original string
    assert decrypted_string == test_string


@pytest.mark.parametrize('date_str,date_format,expected', [
    ('2023-01-01', '%Y-%m-%d', 'Jan 1, 2023'),
    ('2023/01/01', '%Y/%m/%d', 'Jan 1, 2023'),
    ('01-01-2023', '%m-%d-%Y', 'Jan 1, 2023')
])
def test_format_date(date_str, date_format, expected):
    """Tests the date formatting function with various date formats"""
    # Take the parametrized date string, format, and expected result
    # Call the datetime_utils.format_date function with the date string and format
    date_obj = datetime_utils.parse_date(date_str, date_format)
    formatted_date = datetime_utils.format_date(date_obj, "%b %-d, %Y")
    # Assert that the result matches the expected output
    assert formatted_date == expected


def test_is_date_in_range():
    """Tests the function that checks if a date is within a specified range"""
    # Create test dates: start_date, test_date (in range), and end_date
    start_date = datetime_utils.parse_date('2023-01-01')
    test_date = datetime_utils.parse_date('2023-01-15')
    end_date = datetime_utils.parse_date('2023-01-31')

    # Assert that datetime_utils.is_date_in_range returns True when test_date is between start_date and end_date
    assert datetime_utils.is_date_between(test_date, start_date, end_date) is True
    # Assert that datetime_utils.is_date_in_range returns False when test_date is before start_date
    assert datetime_utils.is_date_between(datetime_utils.parse_date('2022-12-31'), start_date, end_date) is False
    # Assert that datetime_utils.is_date_in_range returns False when test_date is after end_date
    assert datetime_utils.is_date_between(datetime_utils.parse_date('2023-02-01'), start_date, end_date) is False


def test_calculate_date_difference():
    """Tests the function that calculates the difference between two dates"""
    # Create two test dates with a known difference
    date1 = datetime_utils.parse_date('2023-01-01')
    date2 = datetime_utils.parse_date('2023-01-10')
    # Call datetime_utils.calculate_date_difference with the two dates
    difference = datetime_utils.date_diff_days(date1, date2)
    # Assert that the result is the expected number of days
    assert difference == 9


@pytest.mark.parametrize('amount,currency_code,expected', [
    (1000, 'USD', '$1,000.00'),
    (1000, 'EUR', '€1,000.00'),
    (1000, 'GBP', '£1,000.00'),
    (1000.50, 'USD', '$1,000.50')
])
def test_format_currency(amount, currency_code, expected):
    """Tests the currency formatting function with various currencies and amounts"""
    # Take the parametrized amount, currency code, and expected result
    # Call the currency.format_currency function with the amount and currency code
    formatted_currency = currency.format_currency(amount, currency_code)
    # Assert that the result matches the expected output
    assert formatted_currency == expected


def test_convert_currency():
    """Tests the currency conversion function using mocked exchange rates"""
    # Mock the currency.get_exchange_rate function to return a known rate
    with unittest.mock.patch('src.backend.utils.currency.get_exchange_rate') as mock_get_exchange_rate:
        mock_get_exchange_rate.return_value = 1.20  # 1 USD = 1.20 EUR
        # Call currency.convert_currency with an amount, source currency, and target currency
        converted_amount = currency.convert_currency(100, 'USD', 'EUR')
        # Assert that the conversion uses the mocked exchange rate correctly
        assert converted_amount == 120.00


@pytest.mark.parametrize('filename,allowed_extensions,expected', [
    ('test.pdf', ['pdf', 'docx'], True),
    ('test.doc', ['pdf', 'docx'], False),
    ('test', ['pdf', 'docx'], False)
])
def test_validate_file_type(filename, allowed_extensions, expected):
    """Tests the file type validation function with various file extensions"""
    # Take the parametrized filename, allowed extensions, and expected result
    # Call the file_handling.validate_file_type function with the filename and allowed extensions
    result = file_handling.validate_file_extension(filename, allowed_extensions)
    # Assert that the result matches the expected output
    assert result == expected


def test_generate_unique_filename():
    """Tests the unique filename generation function"""
    # Create a test filename
    filename = 'test.pdf'
    # Call the file_handling.generate_unique_filename function with the filename
    unique_filename = file_handling.generate_unique_filename(filename)
    # Assert that the result contains the original filename but is different from it
    assert filename in unique_filename
    assert filename != unique_filename

    # Assert that calling the function again with the same filename produces a different result
    unique_filename2 = file_handling.generate_unique_filename(filename)
    assert unique_filename != unique_filename2


@pytest.mark.parametrize('value,decimal_places,expected', [
    (0.1234, 2, '12.34%'),
    (0.05, 1, '5.0%'),
    (1.5, 0, '150%')
])
def test_format_percentage(value, decimal_places, expected):
    """Tests the percentage formatting function with various values and decimal places"""
    # Take the parametrized value, decimal places, and expected result
    # Call the formatting.format_percentage function with the value and decimal places
    formatted_percentage = formatting.format_percentage(value, decimal_places)
    # Assert that the result matches the expected output
    assert formatted_percentage == expected


@pytest.mark.parametrize('value,expected', [
    (1000, '1,000'),
    (1000000, '1,000,000'),
    (1234.56, '1,234.56')
])
def test_format_large_number(value, expected):
    """Tests the large number formatting function with various numeric values"""
    # Take the parametrized value and expected result
    # Call the formatting.format_large_number function with the value
    formatted_number = formatting.format_large_number(value)
    # Assert that the result matches the expected output
    assert formatted_number == expected


def test_send_email():
    """Tests the email sending function with mocked email service"""
    # Mock the email service
    with unittest.mock.patch('src.backend.utils.email.smtplib.SMTP') as mock_smtp:
        # Call the email.send_email function with test parameters
        result = email.send_email(
            to_email='test@example.com',
            subject='Test Email',
            body='This is a test email.'
        )
        # Assert that the email service was called with the correct parameters
        assert mock_smtp.called
        assert result is True


def test_get_cached_value():
    """Tests the cache retrieval function with mocked cache service"""
    # Mock the cache backend
    with unittest.mock.patch('src.backend.utils.cache.get_redis_client') as mock_get_redis_client:
        mock_redis = unittest.mock.Mock()
        mock_get_redis_client.return_value = mock_redis
        mock_redis.get.return_value = b'0:\"test_value\"'  # Mock a JSON serialized value
        # Configure the mock to return a known value for a test key
        # Call the cache.get_cached_value function with the test key
        cached_value = cache.get_cache('test_key')
        # Assert that the function returns the expected cached value
        assert cached_value == 'test_value'
        # Assert that the cache backend was called with the correct key
        mock_redis.get.assert_called_with('test_key')


def test_set_cached_value():
    """Tests the cache setting function with mocked cache service"""
    # Mock the cache backend
    with unittest.mock.patch('src.backend.utils.cache.get_redis_client') as mock_get_redis_client:
        mock_redis = unittest.mock.Mock()
        mock_get_redis_client.return_value = mock_redis
        # Call the cache.set_cached_value function with a test key and value
        cache.set_cache('test_key', 'test_value', ttl=60)
        # Assert that the cache backend was called with the correct key, value, and expiration time
        mock_redis.setex.assert_called_with('test_key', 60, b'0:"test_value"')


def test_upload_file_to_storage():
    """Tests the file upload function with mocked storage service"""
    # Mock the storage backend
    with unittest.mock.patch('src.backend.utils.storage.upload_file') as mock_upload_file:
        mock_upload_file.return_value = 'http://example.com/test.pdf'
        # Create a test file-like object
        test_file = io.BytesIO(b'test content')
        # Call the storage.upload_file function with the test file and path
        file_url = storage.upload_file(test_file, 'test.pdf')
        # Assert that the storage backend was called with the correct file and path
        assert mock_upload_file.called
        # Assert that the function returns the expected URL
        assert file_url == 'http://example.com/test.pdf'


def test_download_file_from_storage():
    """Tests the file download function with mocked storage service"""
    # Mock the storage backend
    with unittest.mock.patch('src.backend.utils.storage.download_file') as mock_download_file:
        mock_download_file.return_value = b'test content'
        # Configure the mock to return test file content
        # Call the storage.download_file function with a test path
        file_content = storage.download_file('test.pdf')
        # Assert that the storage backend was called with the correct path
        assert mock_download_file.called
        # Assert that the function returns the expected file content
        assert file_content == b'test content'


def test_format_percentage():
    """Tests the percentage formatting function with various values and decimal places"""
    assert formatting.format_percentage(0.1234, 2) == "12.34%"
    assert formatting.format_percentage(0.05, 1) == "5.0%"
    assert formatting.format_percentage(1.5, 0) == "150%"


def test_format_large_number():
    """Tests the large number formatting function with various numeric values"""
    assert formatting.format_large_number(1000) == "1,000"
    assert formatting.format_large_number(1000000) == "1,000,000"
    assert formatting.format_large_number(1234.56) == "1,234.56"


def test_send_email():
    """Tests the email sending function with mocked email service"""
    with unittest.mock.patch('src.backend.utils.email.smtplib.SMTP') as mock_smtp:
        email.send_email(to_email='test@example.com', subject='Test Email', body='This is a test email.')
        assert mock_smtp.called


def test_get_cached_value():
    """Tests the cache retrieval function with mocked cache service"""
    with unittest.mock.patch('src.backend.utils.cache.get_redis_client') as mock_get_redis_client:
        mock_redis = unittest.mock.Mock()
        mock_get_redis_client.return_value = mock_redis
        mock_redis.get.return_value = b'0:"test_value"'
        assert cache.get_cache('test_key') == "test_value"
        mock_redis.get.assert_called_with('test_key')


def test_set_cached_value():
    """Tests the cache setting function with mocked cache service"""
    with unittest.mock.patch('src.backend.utils.cache.get_redis_client') as mock_get_redis_client:
        mock_redis = unittest.mock.Mock()
        mock_get_redis_client.return_value = mock_redis
        cache.set_cache('test_key', 'test_value', ttl=60)
        mock_redis.setex.assert_called_with('test_key', 60, b'0:"test_value"')


def test_upload_file_to_storage():
    """Tests the file upload function with mocked storage service"""
    with unittest.mock.patch('src.backend.utils.storage.upload_file') as mock_upload_file:
        mock_upload_file.return_value = 'http://example.com/test.pdf'
        test_file = io.BytesIO(b'test content')
        file_url = storage.upload_file(test_file, 'test.pdf')
        assert mock_upload_file.called
        assert file_url == 'http://example.com/test.pdf'


def test_download_file_from_storage():
    """Tests the file download function with mocked storage service"""
    with unittest.mock.patch('src.backend.utils.storage.download_file') as mock_download_file:
        mock_download_file.return_value = b'test content'
        file_content = storage.download_file('test.pdf')
        assert mock_download_file.called
        assert file_content == b'test content'