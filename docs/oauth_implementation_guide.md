# OAuth 2.0 Implementation Guide for Quanta Haba

This document provides a comprehensive guide to the OAuth 2.0 implementation in the Quanta Haba editor, enabling secure authentication with external language model providers.

## Overview

The OAuth 2.0 implementation allows the Quanta Haba editor to securely authenticate with external language model providers without handling user credentials directly. This implementation follows OAuth 2.0 best practices and includes support for PKCE (Proof Key for Code Exchange) for enhanced security.

## Architecture

### Components

1. **Python Implementation** (`src/p/oauth_client.py`)
   - `OAuthClient`: Main OAuth 2.0 client with PKCE support
   - `SecureTokenStorage`: Secure token storage using system keyring
   - `OAuth2CallbackHandler`: HTTP callback handler for authorization flow

2. **C++ Implementation** (`src/c/include/OAuthClient.h`, `src/c/source/OAuthClient.cpp`)
   - Cross-platform OAuth 2.0 client implementation
   - Windows Credential Manager integration
   - Built-in HTTP server for callback handling

3. **Editor Integration** (`src/p/editor.py`, `src/p/menu.py`)
   - Menu integration for OAuth configuration and management
   - Seamless integration with existing editor workflow

## Features

### Security Features

- **PKCE (Proof Key for Code Exchange)**: Enhanced security for public clients
- **State Parameter**: CSRF protection during authorization flow
- **Secure Token Storage**: System keyring integration for token persistence
- **Automatic Token Refresh**: Seamless token renewal without user intervention
- **Timeout Protection**: Configurable timeouts for authorization flow

### User Experience Features

- **Browser Integration**: Automatic browser opening for authorization
- **Visual Feedback**: Clear status messages and progress indicators
- **Error Handling**: Comprehensive error messages and recovery options
- **Configuration Management**: Easy-to-use configuration dialogs

## Installation and Setup

### Python Dependencies

Install the required Python packages:

```bash
pip install -r src/p/requirements.txt
```

Required packages:
- `requests`: HTTP client library
- `requests-oauthlib`: OAuth 2.0 support for requests
- `keyring`: Secure credential storage

### C++ Dependencies (Windows)

For the C++ implementation, you'll need:
- OpenSSL library for cryptographic functions
- JsonCpp library for JSON parsing
- Windows SDK for credential management

## Configuration

### OAuth Provider Configuration

Configure your external model provider with the following parameters:

```python
config = {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret", 
    "authorization_url": "https://provider.com/oauth/authorize",
    "token_url": "https://provider.com/oauth/token",
    "api_base_url": "https://api.provider.com",
    "scopes": ["read", "write"],
    "redirect_uri": "http://localhost:8080/callback",
    "use_pkce": True
}
```

### Configuration Parameters

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `client_id` | OAuth client identifier | Yes | - |
| `client_secret` | OAuth client secret | Yes | - |
| `authorization_url` | Provider's authorization endpoint | Yes | - |
| `token_url` | Provider's token endpoint | Yes | - |
| `api_base_url` | Base URL for API calls | Yes | - |
| `scopes` | Requested OAuth scopes | No | `["read"]` |
| `redirect_uri` | OAuth callback URI | No | `http://localhost:8080/callback` |
| `use_pkce` | Enable PKCE for enhanced security | No | `True` |

## Usage

### Python Implementation

#### Basic Usage

```python
from oauth_client import OAuthClient

# Configure OAuth client
config = {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "authorization_url": "https://provider.com/oauth/authorize",
    "token_url": "https://provider.com/oauth/token",
    "api_base_url": "https://api.provider.com"
}

# Create OAuth client
client = OAuthClient(config, provider_name="my_provider")

# Check if already authenticated
if client.is_authenticated():
    print("Already authenticated!")
else:
    # Start OAuth flow
    httpd = client.initiate_authorization()
    
    # Wait for user to complete authorization in browser
    success = client.finish_authorization(httpd, timeout=300)
    
    if success:
        print("Authentication successful!")
    else:
        print("Authentication failed.")

# Make API calls
if client.is_authenticated():
    response = client.call_model("Hello, world!")
    print(response)
```

#### Advanced Usage

```python
# Check authentication status
status = client.get_auth_status()
if status["authenticated"]:
    print(f"Token expires in {status['expires_in_minutes']} minutes")

# Manual token refresh
if client.is_authenticated():
    # Token refresh is automatic, but you can check status
    print("Token is valid and will auto-refresh when needed")

# Logout and clear tokens
client.logout()
```

### Editor Integration

#### Menu Access

1. Open the Quanta Haba editor
2. Navigate to **External Models** menu
3. Select **Configure OAuth...** to set up provider credentials
4. Select **Connect to External Model** to authenticate
5. Use **Check Authentication Status** to verify connection

#### Keyboard Shortcuts

- `Ctrl+M`: Open OAuth configuration dialog

### C++ Implementation

```cpp
#include "OAuthClient.h"

// Configure OAuth client
OAuthClient::OAuthConfig config;
config.client_id = "your_client_id";
config.client_secret = "your_client_secret";
config.authorization_url = "https://provider.com/oauth/authorize";
config.token_url = "https://provider.com/oauth/token";
config.api_base_url = "https://api.provider.com";
config.scopes = {"read", "write"};

// Create OAuth client
OAuthClient client(config);

// Start OAuth flow
if (client.initiateAuthorization()) {
    // Wait for authorization to complete
    if (client.finishAuthorization(300)) {
        std::cout << "Authentication successful!" << std::endl;
        
        // Make API call
        std::string response = client.callModel("Hello, world!");
        std::cout << "Response: " << response << std::endl;
    }
}
```

## OAuth Flow Details

### Step-by-Step Process

1. **Configuration**: User configures OAuth provider settings
2. **Authorization Request**: Application generates authorization URL with PKCE
3. **User Consent**: Browser opens to provider's authorization page
4. **Callback Handling**: Local server receives authorization code
5. **Token Exchange**: Authorization code exchanged for access/refresh tokens
6. **Secure Storage**: Tokens stored in system keyring
7. **API Access**: Authenticated API calls using access token
8. **Token Refresh**: Automatic token renewal using refresh token

### Security Considerations

#### PKCE Implementation

The implementation uses PKCE (RFC 7636) for enhanced security:

1. **Code Verifier**: Random 128-character string
2. **Code Challenge**: SHA256 hash of verifier, base64url encoded
3. **Challenge Method**: S256 (SHA256)

#### State Parameter

A random state parameter is generated for each authorization request to prevent CSRF attacks.

#### Token Storage

Tokens are stored securely using the system's credential manager:
- **Windows**: Windows Credential Manager
- **macOS**: Keychain (future implementation)
- **Linux**: Secret Service (future implementation)

## Error Handling

### Common Errors and Solutions

#### Authentication Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Configuration Missing` | OAuth settings not configured | Configure provider settings via menu |
| `Authorization timeout` | User didn't complete auth in time | Retry authentication process |
| `State parameter mismatch` | Possible CSRF attack | Clear stored data and retry |
| `Token exchange failed` | Invalid authorization code | Check provider configuration |

#### Network Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Failed to start local server` | Port 8080 in use | Change redirect URI port |
| `Empty response from API` | Network connectivity issues | Check internet connection |
| `API call failed` | Invalid or expired token | Re-authenticate with provider |

#### Storage Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Error storing tokens` | Keyring access denied | Check system permissions |
| `Error retrieving tokens` | Corrupted keyring data | Clear stored tokens and re-auth |

### Debugging

Enable debug logging by setting environment variable:

```bash
export QUANTA_OAUTH_DEBUG=1
```

## Testing

### Running Tests

Execute the OAuth test suite:

```bash
cd src/p
python test_oauth.py
```

### Test Coverage

The test suite covers:
- Secure token storage functionality
- OAuth client creation and configuration
- PKCE code generation
- OAuth flow simulation
- Configuration validation

### Manual Testing

1. Configure a test OAuth provider (e.g., GitHub, Google)
2. Run the editor and configure OAuth settings
3. Test the complete authentication flow
4. Verify token storage and retrieval
5. Test API calls with authenticated client

## Provider-Specific Configurations

### Google OAuth 2.0

```python
config = {
    "client_id": "your_google_client_id.googleusercontent.com",
    "client_secret": "your_google_client_secret",
    "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
    "token_url": "https://oauth2.googleapis.com/token",
    "api_base_url": "https://your-api-endpoint.googleapis.com",
    "scopes": ["openid", "email", "profile"]
}
```

### GitHub OAuth

```python
config = {
    "client_id": "your_github_client_id",
    "client_secret": "your_github_client_secret", 
    "authorization_url": "https://github.com/login/oauth/authorize",
    "token_url": "https://github.com/login/oauth/access_token",
    "api_base_url": "https://api.github.com",
    "scopes": ["repo", "user"]
}
```

### OpenAI (Hypothetical)

```python
config = {
    "client_id": "your_openai_client_id",
    "client_secret": "your_openai_client_secret",
    "authorization_url": "https://auth.openai.com/oauth/authorize", 
    "token_url": "https://auth.openai.com/oauth/token",
    "api_base_url": "https://api.openai.com/v1",
    "scopes": ["model.read", "model.write"]
}
```

## Best Practices

### Security Best Practices

1. **Never hardcode credentials** in source code
2. **Use PKCE** for all OAuth flows
3. **Validate state parameters** to prevent CSRF
4. **Store tokens securely** using system keyring
5. **Implement proper timeout handling**
6. **Use HTTPS** for all OAuth endpoints

### User Experience Best Practices

1. **Provide clear status messages** during authentication
2. **Handle errors gracefully** with helpful error messages
3. **Allow easy re-authentication** when tokens expire
4. **Show token expiration information** to users
5. **Provide logout functionality** to clear stored tokens

### Development Best Practices

1. **Test with multiple providers** to ensure compatibility
2. **Implement comprehensive error handling**
3. **Use proper logging** for debugging
4. **Follow OAuth 2.0 specifications** strictly
5. **Keep dependencies up to date**

## Troubleshooting

### Common Issues

#### Port Already in Use

If port 8080 is already in use, modify the redirect URI:

```python
config["redirect_uri"] = "http://localhost:8081/callback"
```

#### Keyring Access Issues

On some systems, keyring access may require additional setup:

```bash
# Linux: Install keyring backend
sudo apt-get install python3-keyring

# macOS: Keyring should work out of the box
# Windows: Uses Windows Credential Manager automatically
```

#### Browser Not Opening

If the browser doesn't open automatically, manually navigate to the authorization URL displayed in the console.

### Getting Help

1. Check the console logs for detailed error messages
2. Run the test suite to verify basic functionality
3. Verify OAuth provider configuration
4. Check network connectivity and firewall settings
5. Consult the OAuth provider's documentation

## Future Enhancements

### Planned Features

1. **Multi-provider support**: Manage multiple OAuth providers simultaneously
2. **Token encryption**: Additional encryption layer for stored tokens
3. **Offline access**: Support for offline token refresh
4. **Custom scopes**: Dynamic scope selection based on use case
5. **Audit logging**: Detailed logging of OAuth operations

### Platform Support

1. **macOS keychain integration**: Native credential storage for macOS
2. **Linux Secret Service**: Integration with Linux credential managers
3. **Cross-platform GUI**: Unified configuration interface

## Conclusion

The OAuth 2.0 implementation in Quanta Haba provides a secure, user-friendly way to authenticate with external language model providers. By following OAuth 2.0 best practices and implementing modern security features like PKCE, the system ensures both security and usability.

For additional support or questions, please refer to the project documentation or submit an issue on the project repository.
