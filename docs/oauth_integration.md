# Process for Integrating External Models via OAuth

This document outlines a standardized process for selecting and integrating external, third-party language models into the `quanta_haba` demonstration application. The focus is on ensuring security, stability, and a seamless integration experience.

## 1. Model Selection Framework

Before integration, any potential external model must be evaluated against a set of key criteria.

#### a. Functionality and Performance
- **Capability Match**: Does the model provide the specific text generation, summarization, or other capabilities required by our use cases?
- **Performance Metrics**: What are the model's average latency, throughput, and accuracy? Is it performant enough for an interactive desktop application?
- **Sandbox/Trial Access**: Is there a free tier or sandbox environment available for evaluation and development?

#### b. API Quality and Documentation
- **API Standard**: Does the API adhere to common standards (e.g., REST, JSON-RPC)? A clean, predictable API is crucial.
- **Documentation**: Is the API documentation clear, comprehensive, and up-to-date? Does it include practical examples?
- **SDK/Client Libraries**: Does the provider offer official or community-supported client libraries for Python?

#### c. Authentication and Security
- **Authentication Method**: What mechanism is used for authentication? Strong preference is given to models that support the **OAuth 2.0 protocol**.
- **OAuth 2.0 Support**: This is the preferred method as it allows the application to access the API on behalf of a user without handling their credentials directly. It provides secure, delegated access.
- **API Key Fallback**: If OAuth is not available, the use of simple API keys is a less secure alternative and requires robust measures for key storage and rotation.

#### d. Cost and Quotas
- **Pricing Model**: Is the cost based on tokens, per-call, or a subscription? Is the pricing transparent and predictable?
- **Rate Limiting**: What are the API rate limits and usage quotas? Are they sufficient for the demo's expected usage patterns?

#### e. Terms of Service and Licensing
- **Data Privacy**: How is the data sent to the model handled? Does the provider's privacy policy meet our standards?
- **Licensing**: Are the model's terms of use and licensing compatible with the intended use in this project?

## 2. Standard Integration Process (OAuth 2.0 Example)

Once a model is selected, the following process should be followed for integration.

#### Step 1: Application Registration
- Register the `quanta_haba` application with the external model provider's developer portal.
- Obtain the necessary OAuth 2.0 credentials, typically a `Client ID` and a `Client Secret`.
- Configure the allowed `redirect URIs` (callback URLs) for the application. For a desktop app, this might be a `localhost` address.

#### Step 2: Implement the OAuth 2.0 Flow
- **Authorization Request**: When a user wants to connect their account, the application will open a browser window to the provider's authorization URL, passing the `Client ID` and requested scopes.
- **User Consent**: The user logs into their account on the provider's site and grants the application permission.
- **Authorization Code**: The provider redirects the user back to the specified `redirect URI` with a temporary `authorization code`.
- **Token Exchange**: The `quanta_haba` application backend (or a secure local process) sends the `authorization code`, `Client ID`, and `Client Secret` to the provider's token endpoint.
- **Receive Tokens**: The provider returns an `access token` and a `refresh token`.

#### Step 3: Secure Storage and API Calls
- **Token Storage**: The `access token` and `refresh token` must be stored securely. For a desktop application, this means using the operating system's credential manager (e.g., Windows Credential Manager, macOS Keychain).
- **Making API Calls**: The `access token` is included in the `Authorization` header of every API request to the model.
- **Token Refresh**: The `access token` is short-lived. When it expires, the application must use the long-lived `refresh token` to request a new access token without requiring the user to log in again.

#### Step 4: Build an API Client Wrapper
- Create a dedicated Python class (`e.g., ExternalModelClient`) within `quanta_haba` to encapsulate all interaction with the external API.
- This wrapper should handle:
  - Making API requests with the correct headers.
  - Automatically managing the token refresh logic.
  - Translating API errors into application-specific exceptions.

#### Step 5: Prototyping and Testing
- Develop the integration on a separate feature branch.
- Thoroughly test the entire end-to-end flow, from initial user authorization to successful API calls and token refreshes.
- Validate that all credentials are being stored securely and are never exposed in logs or plain text files.

## 3. OAuth Implementation

This section provides a step-by-step explanation of how the OAuth 2.0 integration works within the Quanta Haba editor. The goal is to allow the editor to securely access external language models on behalf of the user.

### Step 1: The User Initiates the Connection

It all starts with the user. Inside the Quanta Haba editor, the user will find an option in the menu to connect to an external model (e.g., "Connect to GPT-4"). When the user clicks this, the editor kicks off the OAuth 2.0 authorization process.

### Step 2: The Editor Opens a Browser Window

The editor, through the `ExternalModelClient` class, opens the user's default web browser and directs them to the external model provider's website (e.g., Google, OpenAI). The web address includes special information, like the editor's `Client ID`, which tells the provider which application is trying to connect.

### Step 3: The User Grants Permission

On the provider's website, the user is asked to log in to their account (if they aren't already). They are then presented with a consent screen that asks if they want to grant the Quanta Haba editor permission to access their data (in this case, to use the language model). By clicking "Allow" or "Authorize," the user is giving their consent.

### Step 4: The Provider Sends a Temporary Code

Once the user grants permission, the provider's website redirects the user's browser back to a special, pre-configured web address that the editor is listening to. This address is usually `http://localhost:8080/callback`. Appended to this address is a temporary `authorization code`.

To catch this code, the editor starts a small, temporary web server on the user's computer. This server's only job is to listen for this one specific redirect and grab the authorization code from the URL.

### Step 5: The Editor Exchanges the Code for an Access Token

Now that the editor has the temporary authorization code, it sends a direct, secure, behind-the-scenes request to the provider's server. This request includes the authorization code, the editor's `Client ID`, and a `Client Secret` (which is a secret password that only the editor and the provider know).

If everything checks out, the provider returns two important pieces of information: an `access token` and a `refresh token`.

*   **Access Token:** This is a short-lived token that gives the editor permission to make API calls to the language model on the user's behalf. It's like a temporary key card.
*   **Refresh Token:** This is a long-lived token that can be used to get a new access token when the old one expires. This way, the user doesn't have to go through the whole login and consent process every time the access token expires.

### Step 6: Securely Storing the Tokens

The editor needs to store the access and refresh tokens so it can use them later. For security, these tokens are not stored in a plain text file. Instead, they are stored in the operating system's secure credential manager (like the Windows Credential Manager or macOS Keychain). This is the same place your web browser stores your saved passwords.

### Step 7: Making Authenticated API Calls

Now, whenever the user wants to use the external language model, the editor retrieves the access token from the secure storage and includes it in the API request. The provider sees the valid access token and processes the request.

If the access token has expired, the `ExternalModelClient` automatically uses the refresh token to get a new access token from the provider, and then retries the API request. This all happens seamlessly in the background, without the user even knowing.
