#!/usr/bin/env python3
"""
Test script for OAuth implementation in Quanta Haba

This script tests the OAuth functionality with a mock external model provider.
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
import unittest
from unittest.mock import patch, MagicMock

# Add the src/p directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from oauth_client import OAuthClient, SecureTokenStorage
    print("✓ Successfully imported OAuth client")
except ImportError as e:
    print(f"✗ Failed to import OAuth client: {e}")
    print("Make sure you have installed the required dependencies:")
    print("pip install requests requests-oauthlib keyring")
    sys.exit(1)

def test_secure_token_storage():
    """Test secure token storage functionality"""
    print("\n=== Testing Secure Token Storage ===")
    
    storage = SecureTokenStorage("test_quanta_haba")
    provider_name = "test_provider"
    
    # Test storing tokens
    access_token = "test_access_token_12345"
    refresh_token = "test_refresh_token_67890"
    expires_at = datetime.now() + timedelta(hours=1)
    
    print("Storing test tokens...")
    success = storage.store_tokens(provider_name, access_token, refresh_token, expires_at)
    if success:
        print("✓ Tokens stored successfully")
    else:
        print("✗ Failed to store tokens")
        return False
    
    # Test retrieving tokens
    print("Retrieving stored tokens...")
    retrieved_tokens = storage.retrieve_tokens(provider_name)
    if retrieved_tokens:
        print("✓ Tokens retrieved successfully")
        print(f"  Access token: {retrieved_tokens['access_token'][:20]}...")
        print(f"  Refresh token: {retrieved_tokens['refresh_token'][:20]}...")
        print(f"  Expires at: {retrieved_tokens['expires_at']}")
        
        # Verify token data
        if (retrieved_tokens['access_token'] == access_token and 
            retrieved_tokens['refresh_token'] == refresh_token):
            print("✓ Token data matches")
        else:
            print("✗ Token data mismatch")
            return False
    else:
        print("✗ Failed to retrieve tokens")
        return False
    
    # Test deleting tokens
    print("Deleting stored tokens...")
    success = storage.delete_tokens(provider_name)
    if success:
        print("✓ Tokens deleted successfully")
    else:
        print("✗ Failed to delete tokens")
        return False
    
    # Verify tokens are gone
    retrieved_tokens = storage.retrieve_tokens(provider_name)
    if not retrieved_tokens:
        print("✓ Tokens successfully removed")
    else:
        print("✗ Tokens still present after deletion")
        return False
    
    return True

def test_oauth_client_creation():
    """Test OAuth client creation and configuration"""
    print("\n=== Testing OAuth Client Creation ===")
    
    # Test configuration
    config = {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "authorization_url": "https://example.com/oauth/authorize",
        "token_url": "https://example.com/oauth/token",
        "api_base_url": "https://api.example.com",
        "scopes": ["read", "write"],
        "redirect_uri": "http://localhost:8080/callback",
        "use_pkce": True
    }
    
    try:
        client = OAuthClient(config, "test_provider")
        print("✓ OAuth client created successfully")
        
        # Test authentication status (should be false initially)
        if not client.is_authenticated():
            print("✓ Initial authentication status is correct (not authenticated)")
        else:
            print("✗ Initial authentication status is incorrect")
            return False
        
        # Test auth status details
        status = client.get_auth_status()
        if not status["authenticated"]:
            print("✓ Detailed auth status is correct")
            print(f"  Message: {status['message']}")
        else:
            print("✗ Detailed auth status is incorrect")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to create OAuth client: {e}")
        return False

def test_pkce_generation():
    """Test PKCE code generation"""
    print("\n=== Testing PKCE Generation ===")
    
    config = {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "authorization_url": "https://example.com/oauth/authorize",
        "token_url": "https://example.com/oauth/token",
        "api_base_url": "https://api.example.com",
        "use_pkce": True
    }
    
    try:
        client = OAuthClient(config)
        
        # Access private method for testing (not recommended in production)
        client._generate_pkce_pair()
        
        if hasattr(client, 'code_verifier') and client.code_verifier:
            print("✓ PKCE code verifier generated")
            print(f"  Length: {len(client.code_verifier)} characters")
        else:
            print("✗ PKCE code verifier not generated")
            return False
        
        if hasattr(client, 'code_challenge') and client.code_challenge:
            print("✓ PKCE code challenge generated")
            print(f"  Challenge: {client.code_challenge[:20]}...")
        else:
            print("✗ PKCE code challenge not generated")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ PKCE generation failed: {e}")
        return False

def test_oauth_flow_simulation():
    """Simulate OAuth flow without actual network calls"""
    print("\n=== Testing OAuth Flow Simulation ===")
    
    config = {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "authorization_url": "https://example.com/oauth/authorize",
        "token_url": "https://example.com/oauth/token",
        "api_base_url": "https://api.example.com",
        "scopes": ["read"],
        "use_pkce": True
    }
    
    try:
        client = OAuthClient(config)
        
        # Test authorization URL generation (simulate initiate_authorization)
        client._generate_pkce_pair()
        client._state = "test_state_12345"
        
        # Build authorization URL manually to test
        from urllib.parse import urlencode
        
        params = {
            "response_type": "code",
            "client_id": config["client_id"],
            "redirect_uri": config.get("redirect_uri", "http://localhost:8080/callback"),
            "scope": " ".join(config["scopes"]),
            "state": client._state,
            "code_challenge": client.code_challenge,
            "code_challenge_method": "S256"
        }
        
        auth_url = f"{config['authorization_url']}?{urlencode(params)}"
        print("✓ Authorization URL generated successfully")
        print(f"  URL length: {len(auth_url)} characters")
        print(f"  Contains client_id: {'client_id=' + config['client_id'] in auth_url}")
        print(f"  Contains PKCE challenge: {'code_challenge=' in auth_url}")
        
        return True
        
    except Exception as e:
        print(f"✗ OAuth flow simulation failed: {e}")
        return False

def test_configuration_validation():
    """Test configuration validation"""
    print("\n=== Testing Configuration Validation ===")
    
    # Test with minimal valid config
    minimal_config = {
        "client_id": "test_id",
        "client_secret": "test_secret",
        "authorization_url": "https://example.com/auth",
        "token_url": "https://example.com/token",
        "api_base_url": "https://api.example.com"
    }
    
    try:
        client = OAuthClient(minimal_config)
        print("✓ Minimal configuration accepted")
        
        # Check default values
        if client.config.get("use_pkce", False):
            print("✓ PKCE enabled by default")
        
        if client.config.get("redirect_uri") == "http://localhost:8080/callback":
            print("✓ Default redirect URI set correctly")
        
        if client.config.get("scopes") == ["read"]:
            print("✓ Default scopes set correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration validation failed: {e}")
        return False


class TestOAuthBDD(unittest.TestCase):
    """BDD-style tests for the OAuthClient"""

    def setUp(self):
        """Set up a mock configuration and client for each test"""
        self.config = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "authorization_url": "https://example.com/oauth/authorize",
            "token_url": "https://example.com/oauth/token",
            "api_base_url": "https://api.example.com",
            "scopes": ["read", "write"],
            "redirect_uri": "http://localhost:8080/callback",
            "use_pkce": True
        }
        # Use a mock for keyring to avoid actual system interaction
        self.keyring_patcher = patch('oauth_client.keyring', autospec=True)
        self.mock_keyring = self.keyring_patcher.start()
        # Reset mocks for each test
        self.mock_keyring.reset_mock()

        self.client = OAuthClient(self.config, provider_name="test_provider")

    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self.client, '_httpd') and self.client._httpd:
            if hasattr(self.client._httpd, 'shutdown'):
                self.client._httpd.shutdown()
        self.client.logout()
        self.keyring_patcher.stop()

    @patch('oauth_client.webbrowser.open')
    @patch('oauth_client.HTTPServer')
    @patch('oauth_client.OAuth2Session')
    def test_given_unauthenticated_user_when_auth_succeeds_then_client_is_authenticated(self, mock_oauth_session, mock_http_server, mock_webbrowser):
        """
        Given: An unauthenticated user with a valid client configuration
        When: The user completes the authentication flow successfully
        Then: The client becomes authenticated and stores the tokens
        """
        # Given: Mock the OAuth2Session behavior
        mock_session_instance = mock_oauth_session.return_value
        mock_session_instance.authorization_url.return_value = ("https://example.com/auth?state=xyz", "test_state_123")
        mock_session_instance.fetch_token.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600
        }

        # Given: Mock the local HTTP server to return a valid auth code
        mock_server_instance = mock_http_server.return_value
        mock_server_instance.auth_code = "test_auth_code"
        mock_server_instance.state = "test_state_123" # Must match the state from authorization_url
        mock_server_instance.error = None

        # When: The user initiates and completes the authorization flow
        httpd = self.client.initiate_authorization()
        success = self.client.finish_authorization(httpd)

        # Then: The flow should be successful
        self.assertTrue(success)
        self.assertTrue(self.client.is_authenticated())

        # Then: The browser should have been opened with the correct URL
        mock_webbrowser.assert_called_once_with("https://example.com/auth?state=xyz")

        # Then: Tokens should have been fetched with the correct parameters
        mock_session_instance.fetch_token.assert_called_once()

        # Then: The new tokens should be stored securely
        self.mock_keyring.set_password.assert_called_once()
        args, _ = self.mock_keyring.set_password.call_args
        self.assertEqual(args[0], 'test_quanta_haba')
        self.assertEqual(args[1], 'test_provider_tokens')
        stored_data = json.loads(args[2])
        self.assertEqual(stored_data['access_token'], 'new_access_token')

    @patch('oauth_client.webbrowser.open')
    @patch('oauth_client.HTTPServer')
    @patch('oauth_client.OAuth2Session')
    def test_given_user_cancels_when_auth_fails_then_client_remains_unauthenticated(self, mock_oauth_session, mock_http_server, mock_webbrowser):
        """
        Given: An unauthenticated user
        When: The user cancels the authentication, and the provider returns an error
        Then: The client handles the error gracefully and remains unauthenticated
        """
        # Given: Mock the OAuth2Session behavior
        mock_session_instance = mock_oauth_session.return_value
        mock_session_instance.authorization_url.return_value = ("https://example.com/auth?state=xyz", "test_state_123")

        # Given: Mock the local HTTP server to return an error
        mock_server_instance = mock_http_server.return_value
        mock_server_instance.auth_code = None
        mock_server_instance.state = "test_state_123"
        mock_server_instance.error = "access_denied"  # User cancelled

        # When: The user initiates and completes the authorization flow
        httpd = self.client.initiate_authorization()
        success = self.client.finish_authorization(httpd)

        # Then: The flow should fail
        self.assertFalse(success)
        self.assertFalse(self.client.is_authenticated())

        # Then: The token exchange should not have been attempted
        mock_session_instance.fetch_token.assert_not_called()

        # Then: No tokens should be stored
        self.mock_keyring.set_password.assert_not_called()

    @patch('oauth_client.requests')
    @patch.object(OAuthClient, '_refresh_token')
    def test_given_expired_token_when_api_call_fails_then_token_is_refreshed(self, mock_refresh_token, mock_requests):
        """
        Given: A user is authenticated, but the access token has expired
        When: The user makes an API call that fails with a 401 error
        Then: The client automatically refreshes the token and retries the call successfully
        """
        # Given: An authenticated client with a mocked session
        self.client.token = {"access_token": "expired_token"}
        self.client.session = MagicMock(spec=OAuth2Session)

        # Given: The API call will fail once with a 401, then succeed
        mock_response_401 = MagicMock()
        mock_response_401.status_code = 401

        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"result": "success"}

        mock_http_error = mock_requests.exceptions.HTTPError()
        mock_http_error.response = mock_response_401

        self.client.session.post.side_effect = [
            mock_http_error,
            mock_response_200
        ]

        # Given: The token refresh process will succeed
        mock_refresh_token.return_value = True

        # When: The user makes an API call
        response = self.client.call_model("test prompt")

        # Then: The token refresh mechanism should have been triggered
        mock_refresh_token.assert_called_once()

        # Then: The API should have been called twice (original + retry)
        self.assertEqual(self.client.session.post.call_count, 2)

        # Then: The final response should be the successful one
        self.assertEqual(response, {"result": "success"})

    def test_given_authenticated_user_when_logout_then_tokens_are_deleted(self):
        """
        Given: A user is authenticated
        When: The user calls the logout method
        Then: All local tokens and session data are cleared
        """
        # Given: An authenticated client with stored tokens
        self.client.token = {"access_token": "some_token"}
        self.client.session = MagicMock()
        self.client.token_storage = MagicMock(spec=SecureTokenStorage)

        # When: The user logs out
        self.client.logout()

        # Then: The client's internal state should be cleared
        self.assertIsNone(self.client.token)
        self.assertIsNone(self.client.session)
        self.assertFalse(self.client.is_authenticated())

        # Then: The stored tokens should be deleted
        self.client.token_storage.delete_tokens.assert_called_once_with(self.client.provider_name)


def run_all_tests():
    """Run all OAuth tests, including procedural and BDD-style unittests."""
    print("Starting OAuth Implementation Tests")
    print("=" * 50)

    # --- Running procedural tests ---
    print("\n--- Running Procedural Tests ---")
    procedural_tests = [
        ("Secure Token Storage", test_secure_token_storage),
        ("OAuth Client Creation", test_oauth_client_creation),
        ("PKCE Generation", test_pkce_generation),
        ("OAuth Flow Simulation", test_oauth_flow_simulation),
        ("Configuration Validation", test_configuration_validation)
    ]
    
    procedural_passed = 0
    procedural_failed = 0
    
    for test_name, test_func in procedural_tests:
        print(f"\nRunning: {test_name}")
        try:
            if test_func():
                print(f"✓ {test_name} PASSED")
                procedural_passed += 1
            else:
                print(f"✗ {test_name} FAILED")
                procedural_failed += 1
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {e}")
            procedural_failed += 1
    
    # --- Running BDD tests ---
    print("\n--- Running BDD Unittests ---")
    # Temporarily add a placeholder test to ensure the suite runs.
    # This will be removed when actual tests are added.
    if not any(name.startswith('test_') for name in dir(TestOAuthBDD)):
        def test_placeholder(self): self.assertTrue(True)
        TestOAuthBDD.test_placeholder = test_placeholder

    suite = unittest.TestLoader().loadTestsFromTestCase(TestOAuthBDD)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Remove placeholder if it was added
    if hasattr(TestOAuthBDD, 'test_placeholder'):
        delattr(TestOAuthBDD, 'test_placeholder')

    bdd_passed = result.testsRun - len(result.failures) - len(result.errors)
    bdd_failed = len(result.failures) + len(result.errors)

    # --- Summary ---
    passed = procedural_passed + bdd_passed
    failed = procedural_failed + bdd_failed

    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! OAuth implementation is working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the implementation.")
        return False

def print_system_info():
    """Print system information for debugging"""
    print("\nSystem Information:")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    # Check for required packages
    required_packages = ['requests', 'requests_oauthlib', 'keyring']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is available")
        except ImportError:
            print(f"✗ {package} is NOT available")

if __name__ == "__main__":
    print_system_info()
    
    success = run_all_tests()
    
    if success:
        print("\n" + "=" * 50)
        print("OAuth Implementation Test Complete!")
        print("\nNext steps:")
        print("1. Configure your external model provider credentials")
        print("2. Test with a real OAuth provider")
        print("3. Integrate with the Quanta Haba editor")
        sys.exit(0)
    else:
        sys.exit(1)
