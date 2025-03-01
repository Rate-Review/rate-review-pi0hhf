"""
Provides Single Sign-On (SSO) integration functionality for the Justice Bid Rate Negotiation System,
supporting both SAML 2.0 and OAuth 2.0 protocols for enterprise user authentication from law firm and client identity providers.
"""

import typing
from typing import Optional, Dict

import saml2  # python3-saml 1.15.0
from authlib.integrations.requests_client import OAuth2Session  # Authlib 1.2.0
import requests  # requests 2.28.1
import uuid
import abc
import base64

from ..auth.jwt import create_access_token, create_refresh_token
from ...db.repositories.user_repository import UserRepository
from ...db.repositories.organization_repository import OrganizationRepository
from ...utils.logging import get_logger
from ...api.core.config import get_config
from ...utils.constants import UserRole

# Initialize logger
logger = get_logger(__name__)

# Get application config
config = get_config()

# Global dictionary to store initialized SSO providers
SSO_PROVIDERS: Dict[str, 'SSOProvider'] = {}


def init_sso_providers() -> Dict[str, 'SSOProvider']:
    """
    Initialize SSO providers from configuration settings.

    Returns:
        dict: Dictionary of initialized SSO providers
    """
    global SSO_PROVIDERS
    SSO_PROVIDERS = {}  # Reset providers

    sso_config = config.get("SSO_CONFIG", {})
    if not sso_config:
        logger.info("No SSO providers configured.")
        return SSO_PROVIDERS

    for provider_id, provider_settings in sso_config.items():
        provider_type = provider_settings.get("type")
        provider_name = provider_settings.get("name", provider_id)

        try:
            if provider_type == "saml":
                provider = SAMLProvider(provider_id, provider_name, provider_settings)
            elif provider_type == "oauth":
                # Determine specific OAuth provider type
                oauth_type = provider_settings.get("oauth_type", "generic")
                if oauth_type == "google":
                    provider = GoogleOAuthProvider(provider_id, provider_name, provider_settings)
                elif oauth_type == "microsoft":
                    provider = MicrosoftOAuthProvider(provider_id, provider_name, provider_settings)
                else:
                    provider = OAuthProvider(provider_id, provider_name, provider_settings)
            else:
                logger.warning(f"Unsupported SSO provider type: {provider_type} for provider {provider_id}")
                continue

            SSO_PROVIDERS[provider_id] = provider
            logger.info(f"Initialized SSO provider: {provider_id} ({provider_type})")

        except Exception as e:
            logger.error(f"Failed to initialize SSO provider {provider_id}: {str(e)}")

    return SSO_PROVIDERS


def get_sso_provider(provider_id: str) -> Optional['SSOProvider']:
    """
    Get an SSO provider by ID.

    Args:
        provider_id: The ID of the SSO provider

    Returns:
        Optional[SSOProvider]: The requested SSO provider or None if not found
    """
    if not SSO_PROVIDERS:
        init_sso_providers()

    return SSO_PROVIDERS.get(provider_id)


def process_saml_login(provider_id: str, return_to: str) -> Dict:
    """
    Process a SAML login request by generating a SAML authentication request.

    Args:
        provider_id: The ID of the SAML provider
        return_to: The URL to return to after authentication

    Returns:
        dict: SAML authentication request details (redirect URL and parameters)
    """
    provider = get_sso_provider(provider_id)
    if not provider or not isinstance(provider, SAMLProvider):
        raise ValueError(f"Invalid SAML provider ID: {provider_id}")

    auth_request = provider.get_auth_request(return_to)
    return auth_request


def process_saml_callback(provider_id: str, request_data: Dict) -> Dict:
    """
    Process a SAML callback after successful authentication at the IdP.

    Args:
        provider_id: The ID of the SAML provider
        request_data: The request data from the SAML callback

    Returns:
        dict: Authentication result with user info and tokens
    """
    provider = get_sso_provider(provider_id)
    if not provider or not isinstance(provider, SAMLProvider):
        raise ValueError(f"Invalid SAML provider ID: {provider_id}")

    user_info = provider.validate_callback(request_data)
    user_repo = UserRepository(get_db())
    org_repo = OrganizationRepository(get_db())
    user = find_or_create_user(user_info, user_repo, org_repo)

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    return {
        "user": user,
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def process_oauth_login(provider_id: str, redirect_uri: str) -> Dict:
    """
    Process an OAuth login request by generating an OAuth authorization URL.

    Args:
        provider_id: The ID of the OAuth provider
        redirect_uri: The URL to redirect to after authorization

    Returns:
        dict: OAuth authorization details (URL and state)
    """
    provider = get_sso_provider(provider_id)
    if not provider or not isinstance(provider, OAuthProvider):
        raise ValueError(f"Invalid OAuth provider ID: {provider_id}")

    auth_details = provider.get_auth_request(redirect_uri)
    return auth_details


def process_oauth_callback(provider_id: str, request_data: Dict) -> Dict:
    """
    Process an OAuth callback after successful authorization at the provider.

    Args:
        provider_id: The ID of the OAuth provider
        request_data: The request data from the OAuth callback

    Returns:
        dict: Authentication result with user info and tokens
    """
    provider = get_sso_provider(provider_id)
    if not provider or not isinstance(provider, OAuthProvider):
        raise ValueError(f"Invalid OAuth provider ID: {provider_id}")

    user_info = provider.validate_callback(request_data)
    user_repo = UserRepository(get_db())
    org_repo = OrganizationRepository(get_db())
    user = find_or_create_user(user_info, user_repo, org_repo)

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    return {
        "user": user,
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def find_or_create_user(user_attrs: Dict, user_repo: UserRepository, org_repo: OrganizationRepository) -> Dict:
    """
    Find an existing user by email or create a new one from SSO attributes.

    Args:
        user_attrs: Dictionary of user attributes from SSO
        user_repo: UserRepository instance
        org_repo: OrganizationRepository instance

    Returns:
        dict: User information including database ID
    """
    email = user_attrs.get("email")
    name = user_attrs.get("name")

    if not email or not name:
        raise ValueError("Email and name are required attributes from SSO")

    user = user_repo.get_by_email(email)

    if user:
        # Update user info if needed
        if user.name != name:
            user = user_repo.update(user.id, {"name": name})
            if not user:
                raise ValueError(f"Could not update user name for user {email}")
        logger.info(f"SSO login for existing user: {email}")
    else:
        # Determine organization from email domain
        domain = email.split("@")[1]
        org = org_repo.get_by_domain(domain)
        if not org:
            raise ValueError(f"No organization found for domain: {domain}")

        # Create a new user
        try:
            user = user_repo.create(email=email, name=name, password=uuid.uuid4().hex,
                                    organization_id=org.id, role=UserRole.STANDARD_USER)
            logger.info(f"SSO login: Created new user {email} in organization {org.id}")
        except Exception as e:
            logger.error(f"Error creating user {email}: {str(e)}")
            raise

    return {
        "id": user.id,
        "email": user.email,
        "organization_id": user.organization_id,
        "role": user.role
    }


def map_saml_attributes(saml_attributes: Dict) -> Dict:
    """
    Map SAML assertion attributes to standard user attributes.

    Args:
        saml_attributes: Dictionary of SAML attributes

    Returns:
        dict: Standardized user attributes
    """
    # This is a placeholder - adjust based on your SAML provider's attribute names
    email = saml_attributes.get("emailAddress", [None])[0] or saml_attributes.get("email", [None])[0]
    name = saml_attributes.get("displayName", [None])[0] or saml_attributes.get("name", [None])[0]

    return {
        "email": email,
        "name": name
    }


def map_oauth_attributes(oauth_userinfo: Dict, provider_type: str) -> Dict:
    """
    Map OAuth provider user info to standard user attributes.

    Args:
        oauth_userinfo: Dictionary of user info from OAuth provider
        provider_type: Type of OAuth provider (e.g., "google", "microsoft")

    Returns:
        dict: Standardized user attributes
    """
    if provider_type == "google":
        email = oauth_userinfo.get("email")
        name = oauth_userinfo.get("name")
    elif provider_type == "microsoft":
        email = oauth_userinfo.get("userPrincipalName")
        name = oauth_userinfo.get("displayName")
    else:
        email = oauth_userinfo.get("email")
        name = oauth_userinfo.get("name")

    return {
        "email": email,
        "name": name
    }


@abc.ABC
class SSOProvider:
    """
    Abstract base class for all SSO providers.
    """
    @abc.abstractmethod
    def get_auth_request(self, return_to: str) -> Dict:
        """
        Generate an authentication request.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def validate_callback(self, request_data: Dict) -> Dict:
        """
        Validate the callback data from the identity provider.
        """
        raise NotImplementedError

    def __init__(self, provider_id: str, provider_name: str, settings: Dict):
        """
        Initialize a new SSO provider.
        """
        self.provider_id = provider_id
        self.provider_name = provider_name
        self.settings = settings
        self._validate_settings()

    def _validate_settings(self):
        """
        Validate required settings.
        """
        if not self.provider_id or not self.provider_name or not self.settings:
            raise ValueError("Provider ID, name, and settings are required")


class SAMLProvider(SSOProvider):
    """
    SAML 2.0 SSO provider implementation.
    """
    def __init__(self, provider_id: str, provider_name: str, settings: Dict):
        """
        Initialize a new SAML provider.
        """
        super().__init__(provider_id, provider_name, settings)
        self.auth = None  # Initialize auth property as None (will be set per request)
        self._validate_saml_settings()

    def _validate_saml_settings(self):
        """
        Validate SAML-specific settings.
        """
        required_settings = ["idp_metadata", "sp_entity_id", "assertion_consumer_service_url"]
        for setting in required_settings:
            if setting not in self.settings:
                raise ValueError(f"Missing required SAML setting: {setting}")

        # Prepare SAML settings dictionary
        self.saml_settings = {
            "metadata": {
                "remote": [self.settings["idp_metadata"]]
            },
            "entityid": self.settings["sp_entity_id"],
            "service": {
                "assertion_consumer_service": [
                    {
                        "binding": saml2.BINDING_HTTP_POST,
                        "url": self.settings["assertion_consumer_service_url"]
                    }
                ],
                "single_logout_service": [
                    {
                        "binding": saml2.BINDING_HTTP_REDIRECT,
                        "url": self.settings.get("single_logout_service_url")
                    }
                ]
            },
            "attribute_map_dir": config.BASE_DIR + "/saml_attribute_maps",
            "allow_unsolicited": True,
            "force_authn": True,
            "name_identifier_format": saml2.NAMEID_FORMAT_EMAILADDRESS,
            "metadata_cache_max_age": 3600,
            "organization": {
                "en": {
                    "name": "Justice Bid",
                    "display_name": "Justice Bid Rate Negotiation System",
                    "url": "https://www.justicebid.com"
                }
            },
            "contact_person": [
                {
                    "given_name": "Support",
                    "sur_name": "Justice Bid",
                    "company": "Justice Bid",
                    "email_address": "support@justicebid.com",
                    "contact_type": "technical"
                }
            ]
        }

    def get_auth_request(self, return_to: str) -> Dict:
        """
        Generate a SAML authentication request.
        """
        auth = self.init_auth({})
        (login_url, relay_state) = auth.prepare_for_authenticate(relay_state=return_to)
        return {"login_url": login_url, "relay_state": relay_state}

    def validate_callback(self, request_data: Dict) -> Dict:
        """
        Validate the SAML response and extract user information.
        """
        auth = self.init_auth(request_data)

        # Process SAML response
        try:
            auth.process_response(binding=saml2.BINDING_HTTP_POST,
                                   relay_state=request_data.get("RelayState"))
        except Exception as e:
            logger.error(f"Error processing SAML response: {str(e)}")
            raise ValueError("Invalid SAML response")

        # Check if authentication is valid
        if auth.is_authn_response():
            # Extract SAML attributes
            saml_attributes = auth.get_attributes()
            logger.debug(f"SAML attributes: {saml_attributes}")

            # Map SAML attributes to standard user attributes
            user_info = map_saml_attributes(saml_attributes)
            return user_info
        else:
            logger.warning("SAML authentication failed")
            raise ValueError("SAML authentication failed")

    def init_auth(self, request_data: Dict) -> saml2.auth.Auth:
        """
        Initialize the SAML auth object for a request.
        """
        client_address = request_data.get("client_address", "127.0.0.1")
        auth = saml2.auth.Auth(
            settings=self.saml_settings,
            metadata=None,
            session_id=None
        )
        self.auth = auth
        return auth


class OAuthProvider(SSOProvider):
    """
    OAuth 2.0 SSO provider implementation.
    """
    def __init__(self, provider_id: str, provider_name: str, settings: Dict):
        """
        Initialize a new OAuth provider.
        """
        super().__init__(provider_id, provider_name, settings)
        self._validate_oauth_settings()

    def _validate_oauth_settings(self):
        """
        Validate OAuth-specific settings.
        """
        required_settings = ["client_id", "client_secret", "authorization_endpoint", "token_endpoint", "userinfo_endpoint", "scope"]
        for setting in required_settings:
            if setting not in self.settings:
                raise ValueError(f"Missing required OAuth setting: {setting}")

        self.oauth_config = {
            "client_id": self.settings["client_id"],
            "client_secret": self.settings["client_secret"],
            "authorization_endpoint": self.settings["authorization_endpoint"],
            "token_endpoint": self.settings["token_endpoint"],
            "userinfo_endpoint": self.settings["userinfo_endpoint"],
            "scope": self.settings["scope"],
            "provider_type": self.settings.get("oauth_type", "generic")
        }

    def get_auth_request(self, redirect_uri: str) -> Dict:
        """
        Generate an OAuth authorization request.
        """
        # Generate a random state parameter
        state = generate_token(32)

        # Build authorization URL
        client = OAuth2Session(self.oauth_config["client_id"], self.oauth_config["client_secret"],
                               scope=self.oauth_config["scope"], redirect_uri=redirect_uri)
        authorization_url, state = client.create_authorization_url(self.oauth_config["authorization_endpoint"], state=state)

        return {"authorization_url": authorization_url, "state": state}

    def validate_callback(self, request_data: Dict) -> Dict:
        """
        Validate the OAuth callback and exchange code for tokens.
        """
        # Validate state parameter to prevent CSRF
        state = request_data.get("state")
        if not state:
            raise ValueError("Missing state parameter in OAuth callback")

        # Extract authorization code
        code = request_data.get("code")
        if not code:
            raise ValueError("Missing code parameter in OAuth callback")

        # Exchange code for access token
        token_response = self.exchange_code_for_token(code, request_data.get("redirect_uri"))
        access_token = token_response.get("access_token")
        if not access_token:
            raise ValueError("Failed to retrieve access token from OAuth provider")

        # Fetch user information
        user_info = self.get_user_info(access_token)

        # Map provider-specific user info to standard attributes
        user_info = map_oauth_attributes(user_info, self.oauth_config["provider_type"])
        return user_info

    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict:
        """
        Exchange authorization code for access token.
        """
        client = OAuth2Session(self.oauth_config["client_id"], self.oauth_config["client_secret"],
                               scope=self.oauth_config["scope"], redirect_uri=redirect_uri)

        try:
            token_url = self.oauth_config["token_endpoint"]
            token_response = client.fetch_token(token_url, code=code, client_secret=self.oauth_config["client_secret"])
            return token_response
        except Exception as e:
            logger.error(f"Error exchanging code for token: {str(e)}")
            raise ValueError("Failed to exchange code for token")

    def get_user_info(self, access_token: str) -> Dict:
        """
        Fetch user information using access token.
        """
        client = OAuth2Session(self.oauth_config["client_id"], token={"access_token": access_token})
        try:
            userinfo_url = self.oauth_config["userinfo_endpoint"]
            response = client.get(userinfo_url)
            response.raise_for_status()
            user_info = response.json()
            return user_info
        except Exception as e:
            logger.error(f"Error fetching user info: {str(e)}")
            raise ValueError("Failed to retrieve user information from OAuth provider")


class GoogleOAuthProvider(OAuthProvider):
    """
    Google-specific OAuth 2.0 provider implementation.
    """
    def __init__(self, provider_id: str, provider_name: str, settings: Dict):
        """
        Initialize a new Google OAuth provider.
        """
        super().__init__(provider_id, provider_name, settings)

        # Add Google-specific scopes and endpoints
        self.oauth_config["scope"] = "openid profile email"
        self.oauth_config["authorization_endpoint"] = "https://accounts.google.com/o/oauth2/v2/auth"
        self.oauth_config["token_endpoint"] = "https://oauth2.googleapis.com/token"
        self.oauth_config["userinfo_endpoint"] = "https://www.googleapis.com/oauth2/v3/userinfo"

    def map_user_info(self, user_info: Dict) -> Dict:
        """
        Map Google-specific user info to standard attributes.
        """
        email = user_info.get("email")
        name = user_info.get("name")
        return {
            "email": email,
            "name": name
        }


class MicrosoftOAuthProvider(OAuthProvider):
    """
    Microsoft-specific OAuth 2.0 provider implementation.
    """
    def __init__(self, provider_id: str, provider_name: str, settings: Dict):
        """
        Initialize a new Microsoft OAuth provider.
        """
        super().__init__(provider_id, provider_name, settings)

        # Add Microsoft-specific scopes and endpoints
        self.oauth_config["scope"] = "openid profile email User.Read"
        self.oauth_config["authorization_endpoint"] = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        self.oauth_config["token_endpoint"] = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        self.oauth_config["userinfo_endpoint"] = "https://graph.microsoft.com/v1.0/me"

    def map_user_info(self, user_info: Dict) -> Dict:
        """
        Map Microsoft-specific user info to standard attributes.
        """
        email = user_info.get("userPrincipalName")
        name = user_info.get("displayName")
        return {
            "email": email,
            "name": name
        }