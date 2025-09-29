# Comprehensive Guide to OAuth 2.0 Integration for Quanta Haba

This document provides a complete guide for understanding, implementing, and integrating external language models with the Quanta Haba editor using the OAuth 2.0 protocol.

## 1. Introduction: What is OAuth?

OAuth 2.0 is a security standard that allows an application (like the Quanta Haba editor) to access resources from an external service (like a language model provider) on behalf of a user, without ever handling the user's password. It provides secure, delegated access, meaning the user grants specific permissions to the application without sharing their login credentials.

This is the preferred and most secure method for connecting the editor to third-party services.

## 2. The User Experience: How the OAuth Flow Works

From a user's perspective, connecting their external model account to the editor is a simple and secure process.

1.  **Initiate Connection**: The user selects an option in the editor menu, like "Connect to External Model."
2.  **Browser Redirect**: The editor opens the user's default web browser and sends them to the model provider's secure login page.
3.  **Grant Permission**: The user logs into their account (if they aren't already) and is shown a consent screen. This screen asks for permission for the "Quanta Haba" application to perform specific actions (e.g., "use language models"). The user clicks "Allow" or "Authorize."
4.  **Automatic Redirect**: The provider's website sends the browser back to a special local address that the editor is temporarily listening on. This redirect includes a one-time, temporary "authorization code."
5.  **Background Magic**: The editor receives this code and, in the background, exchanges it directly with the provider for a secure "access token."
6.  **Secure Storage**: This access token is stored securely in the operating system's native credential manager (e.g., Windows Credential Manager, macOS Keychain). It is never stored in a plain text file.
7.  **Ready to Go**: The connection is complete. The editor can now use this token to make secure API calls to the model on the user's behalf. The token is automatically refreshed when needed, so the user doesn't have to log in again.

## 3. Developer's Guide: Integrating a New Model

This section outlines the standard process for integrating a new external model that supports OAuth 2.0.

### Step 1: Evaluate the External Model

Before integration, ensure the model meets key criteria:
*   **Authentication**: Must support **OAuth 2.0**. This is our primary requirement.
*   **API Quality**: Should have a well-documented, stable REST-based API.
*   **Functionality**: Must provide the required text generation or analysis capabilities.
*   **Terms of Service**: Data privacy and licensing terms must be acceptable.

### Step 2: Register the Application

*   In the model provider's developer portal, register a new application for "Quanta Haba."
*   Obtain the **Client ID** and **Client Secret**. These are the application's credentials.
*   Configure the **Redirect URI** (also known as a callback URL). For our desktop application, this must be set to `http://localhost:8080/callback`.

### Step 3: Implement the Integration

Our editor already has a robust OAuth 2.0 client. Your main task is to configure it for the new provider.

#### Configuration

The `OAuthClient` requires a configuration dictionary. Add a new configuration for your provider:

```python
# Example for a new provider "MegaModel"
config = {
    "client_id": "your_megamodel_client_id",
    "client_secret": "your_megamodel_client_secret",
    "authorization_url": "https://megamodel.com/oauth/authorize",
    "token_url": "https://megamodel.com/oauth/token",
    "api_base_url": "https://api.megamodel.com/v1",
    "scopes": ["model.read", "model.write"], # Scopes required by the provider
    "redirect_uri": "http://localhost:8080/callback",
    "use_pkce": True # Always prefer PKCE
}
```

**Configuration Parameters**

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


#### Using the Client

Once configured, using the client is straightforward.

**Python Example:**
```python
from oauth_client import OAuthClient

# Create OAuth client with the new provider's config
client = OAuthClient(config, provider_name="MegaModel")

# Check if already authenticated
if not client.is_authenticated():
    # If not, start the authorization flow
    httpd = client.initiate_authorization()

    # Wait for the user to finish in the browser
    # The client handles the callback and token exchange
    success = client.finish_authorization(httpd, timeout=300)

    if not success:
        print("Authentication failed.")
        return

# Make API calls
response = client.call_model("This is a test prompt.")
print(response)
```

**C++ Example:**
```cpp
#include "OAuthClient.h"

// Configure OAuth client
OAuthClient::OAuthConfig config;
config.client_id = "your_client_id";
config.client_secret = "your_client_secret";
config.authorization_url = "https://provider.com/oauth/authorize";
config.token_url = "https://provider.com/oauth/token";
config.api_base_url = "https://api.provider.com";

// Create OAuth client
OAuthClient client(config);

// The C++ client encapsulates the full flow
if (client.authenticate()) {
    std::cout << "Authentication successful!" << std::endl;

    // Make API call
    std::string response = client.callModel("Hello, world!");
    std::cout << "Response: " << response << std::endl;
}
```

## 4. Security Features

Our OAuth implementation includes critical security features by default.

*   **PKCE (Proof Key for Code Exchange)**: Protects against authorization code interception attacks. This is enabled by default (`use_pkce: True`) and should always be used.
*   **State Parameter**: A unique, randomly generated value is used in each authorization request to prevent Cross-Site Request Forgery (CSRF) attacks.
*   **Secure Token Storage**: Access and refresh tokens are never stored in plain text. They are managed by the operating system's native credential store (keyring).
*   **Automatic Token Refresh**: The client handles the transparent renewal of expired access tokens using the refresh token, ensuring a seamless user experience.

## 5. Testing and Troubleshooting

### Running Tests

To ensure the core OAuth logic is working, run the built-in test suite:

```bash
cd src/p
python test_oauth.py
```

### Manual Testing Flow

1.  Configure a test OAuth provider (e.g., using your own GitHub or Google developer account).
2.  Run the editor and add the provider's configuration.
3.  Trigger the "Connect" flow and complete the authorization in the browser.
4.  Verify that the connection is successful and tokens are stored.
5.  Test an API call.
6.  Restart the editor and verify that it remains authenticated.
7.  Use the "Logout" functionality to clear the stored tokens.

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Configuration Missing` | OAuth settings not configured properly. | Double-check your configuration dictionary. |
| `Authorization timeout` | User didn't complete auth in time. | Retry the authentication process. |
| `State parameter mismatch` | Possible CSRF attempt or bug. | Clear stored data and retry. |
| `Token exchange failed` | Invalid code, client secret, or redirect URI. | Verify your provider settings in the dev portal. |
| `Failed to start local server` | Port 8080 is in use by another application. | Change `redirect_uri` port in config (e.g., 8081). |
| `Keyring access denied`| The application lacks permission to the OS credential store. | Check system permissions for the app. |

## 6. Best Practices Summary

*   **Always use PKCE.**
*   **Never hardcode credentials** in source code. Use a secure configuration method.
*   **Store tokens securely** using the provided `SecureTokenStorage` which leverages the system keyring.
*   **Handle errors gracefully** to provide clear feedback to the user.
*   **Provide a clear "Logout"** or "Disconnect" option for the user to revoke credentials.
*   **Keep dependencies up to date**, especially `requests`, `requests-oauthlib`, and `keyring`.