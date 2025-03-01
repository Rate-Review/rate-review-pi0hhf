import json
import pytest
from flask import Flask
from flask_testing import TestCase
from src.backend.db.models.user import User
from src.backend.services.auth.jwt import create_access_token, decode_token
from src.backend.tests.conftest import client, test_db, create_test_user  # Adjust import path as needed
from src.backend.app.app import app  # Adjust import path as needed

def test_register_user(client, test_db):
    """Tests the user registration endpoint for successful user creation"""
    user_data = {
        'email': 'newuser@example.com',
        'name': 'New User',
        'password': 'newpassword',
        'organization_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6'  # Example UUID
    }
    response = client.post('/api/v1/auth/register', json=user_data)
    assert response.status_code == 201
    assert 'message' in response.json
    assert response.json['message'] == 'User registered successfully'
    user = test_db.query(User).filter_by(email=user_data['email']).first()
    assert user is not None
    assert user.email == user_data['email']

def test_register_duplicate_email(client, test_db, create_test_user):
    """Tests the user registration endpoint rejects duplicate email addresses"""
    user = create_test_user
    duplicate_data = {
        'email': user.email,
        'name': 'Another User',
        'password': 'anotherpassword',
        'organization_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6'  # Example UUID
    }
    response = client.post('/api/v1/auth/register', json=duplicate_data)
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'message' in response.json
    assert response.json['message'] == f"User with email {user.email} already exists"

def test_login_success(client, test_db, create_test_user):
    """Tests successful user login with valid credentials"""
    user = create_test_user
    login_data = {
        'email': user.email,
        'password': 'secure_password'
    }
    response = client.post('/api/v1/auth/login', json=login_data)
    assert response.status_code == 200
    assert 'access_token' in response.json
    assert 'user' in response.json
    token = response.json['access_token']
    payload = decode_token(token)
    assert payload['user_id'] == str(user.id)

def test_login_invalid_credentials(client, test_db, create_test_user):
    """Tests login endpoint rejects invalid credentials"""
    user = create_test_user
    login_data = {
        'email': user.email,
        'password': 'wrong_password'
    }
    response = client.post('/api/v1/auth/login', json=login_data)
    assert response.status_code == 401
    assert 'message' in response.json
    assert response.json['message'] == 'Invalid credentials'

def test_password_reset_request(client, test_db, create_test_user):
    """Tests the password reset request endpoint"""
    user = create_test_user
    reset_data = {
        'email': user.email
    }
    response = client.post('/api/v1/auth/password-reset-request', json=reset_data)
    assert response.status_code == 200
    assert 'message' in response.json
    assert response.json['message'] == 'Password reset email sent'
    # TODO: Add assertion to check that reset token is created in database

def test_password_reset_confirm(client, test_db, create_test_user):
    """Tests the password reset confirmation endpoint"""
    user = create_test_user
    # TODO: Generate password reset token for the user
    reset_data = {
        'token': 'valid_reset_token',
        'new_password': 'new_secure_password'
    }
    response = client.post('/api/v1/auth/password-reset-confirm', json=reset_data)
    assert response.status_code == 200
    assert 'message' in response.json
    assert response.json['message'] == 'Password reset successful'
    # TODO: Add assertion to check that user can log in with new password

def test_refresh_token(client, test_db, create_test_user):
    """Tests the token refresh endpoint"""
    user = create_test_user
    login_data = {
        'email': user.email,
        'password': 'secure_password'
    }
    login_response = client.post('/api/v1/auth/login', json=login_data)
    refresh_token = login_response.json['refresh_token']
    refresh_data = {
        'refresh_token': refresh_token
    }
    response = client.post('/api/v1/auth/refresh', json=refresh_data)
    assert response.status_code == 200
    assert 'access_token' in response.json
    new_token = response.json['access_token']
    payload = decode_token(new_token)
    assert payload['user_id'] == str(user.id)

def test_mfa_setup(client, test_db, create_test_user):
    """Tests the MFA setup endpoint"""
    user = create_test_user
    login_data = {
        'email': user.email,
        'password': 'secure_password'
    }
    login_response = client.post('/api/v1/auth/login', json=login_data)
    access_token = login_response.json['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.post('/api/v1/auth/mfa/setup', headers=headers)
    assert response.status_code == 200
    assert 'secret' in response.json
    assert 'qr_code' in response.json
    # TODO: Add assertion to check that MFA is pending setup in user record

def test_mfa_verify(client, test_db, create_test_user):
    """Tests the MFA verification endpoint"""
    user = create_test_user
    # TODO: Set up MFA for user with known secret
    verification_data = {
        'code': '123456'  # Example TOTP code
    }
    response = client.post('/api/v1/auth/mfa/verify', json=verification_data)
    assert response.status_code == 200
    assert 'message' in response.json
    assert response.json['message'] == 'MFA setup verified'
    # TODO: Add assertion to check that MFA is enabled in user record

def test_logout(client, test_db, create_test_user):
    """Tests the logout endpoint"""
    user = create_test_user
    login_data = {
        'email': user.email,
        'password': 'secure_password'
    }
    login_response = client.post('/api/v1/auth/login', json=login_data)
    access_token = login_response.json['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.post('/api/v1/auth/logout', headers=headers)
    assert response.status_code == 200
    assert 'message' in response.json
    assert response.json['message'] == 'Logout successful'
    # TODO: Add assertion to check that token is blacklisted in database