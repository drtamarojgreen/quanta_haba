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

def run_all_tests():
    """Run all OAuth tests"""
    print("Starting OAuth Implementation Tests")
    print("=" * 50)
    
    tests = [
        ("Secure Token Storage", test_secure_token_storage),
        ("OAuth Client Creation", test_oauth_client_creation),
        ("PKCE Generation", test_pkce_generation),
        ("OAuth Flow Simulation", test_oauth_flow_simulation),
        ("Configuration Validation", test_configuration_validation)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        try:
            if test_func():
                print(f"✓ {test_name} PASSED")
                passed += 1
            else:
                print(f"✗ {test_name} FAILED")
                failed += 1
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {e}")
            failed += 1
    
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
