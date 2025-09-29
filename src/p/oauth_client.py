"""
OAuth 2.0 Client for External Model Integration

This module provides a comprehensive OAuth 2.0 implementation for securely
authenticating with external language model providers.
"""

import webbrowser
import requests
from requests_oauthlib import OAuth2Session
import os
import threading
import json
import base64
import hashlib
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import keyring
import time
from datetime import datetime, timedelta


class OAuth2CallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth 2.0 callback"""
    
    def do_GET(self):
        """Handle GET request from OAuth provider redirect"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        # Send success page
        success_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Successful</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
                .success { color: #28a745; }
                .container { max-width: 500px; margin: 0 auto; padding: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="success">✓ Authentication Successful!</h1>
                <p>You have successfully authenticated with the external model provider.</p>
                <p>You can now close this window and return to the Quanta Haba editor.</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(success_html.encode())
        
        # Extract authorization code and state from URL
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        if 'code' in query_params:
            self.server.auth_code = query_params['code'][0]
        if 'state' in query_params:
            self.server.state = query_params['state'][0]
        if 'error' in query_params:
            self.server.error = query_params['error'][0]
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


class SecureTokenStorage:
    """Secure token storage using system keyring"""
    
    def __init__(self, service_name="quanta_haba_oauth"):
        self.service_name = service_name
    
    def store_tokens(self, provider_name, access_token, refresh_token, expires_at=None):
        """Store OAuth tokens securely"""
        token_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "stored_at": datetime.now().isoformat()
        }
        
        try:
            keyring.set_password(
                self.service_name, 
                f"{provider_name}_tokens", 
                json.dumps(token_data)
            )
            return True
        except Exception as e:
            print(f"Error storing tokens: {e}")
            return False
    
    def retrieve_tokens(self, provider_name):
        """Retrieve OAuth tokens from secure storage"""
        try:
            token_json = keyring.get_password(self.service_name, f"{provider_name}_tokens")
            if token_json:
                return json.loads(token_json)
            return None
        except Exception as e:
            print(f"Error retrieving tokens: {e}")
            return None
    
    def delete_tokens(self, provider_name):
        """Delete stored tokens"""
        try:
            keyring.delete_password(self.service_name, f"{provider_name}_tokens")
            return True
        except Exception as e:
            print(f"Error deleting tokens: {e}")
            return False


class OAuthClient:
    """
    Enhanced OAuth 2.0 client with PKCE support and secure token management
    """
    
    def __init__(self, config, provider_name="external_model"):
        self.config = config
        self.provider_name = provider_name
        self.client_id = config.get("client_id", "")
        self.client_secret = config.get("client_secret", "")
        self.authorization_url = config.get("authorization_url", "")
        self.token_url = config.get("token_url", "")
        self.api_base_url = config.get("api_base_url", "")
        self.scopes = config.get("scopes", ["read"])
        self.redirect_uri = config.get("redirect_uri", "http://localhost:8080/callback")
        
        # PKCE support
        self.use_pkce = config.get("use_pkce", True)
        self.code_verifier = None
        self.code_challenge = None
        
        # OAuth session and tokens
        self.session = None
        self.token = None
        self.token_storage = SecureTokenStorage()
        
        # Server management
        self._httpd = None
        self._httpd_thread = None
        
        # Load existing tokens
        self._load_stored_tokens()
    
    def _generate_pkce_pair(self):
        """Generate PKCE code verifier and challenge"""
        self.code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        challenge_bytes = hashlib.sha256(self.code_verifier.encode('utf-8')).digest()
        self.code_challenge = base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').rstrip('=')
    
    def _load_stored_tokens(self):
        """Load tokens from secure storage"""
        stored_tokens = self.token_storage.retrieve_tokens(self.provider_name)
        if stored_tokens:
            # Check if tokens are still valid
            expires_at_str = stored_tokens.get("expires_at")
            if expires_at_str:
                expires_at = datetime.fromisoformat(expires_at_str)
                if datetime.now() < expires_at:
                    self.token = {
                        "access_token": stored_tokens["access_token"],
                        "refresh_token": stored_tokens["refresh_token"],
                        "expires_at": expires_at
                    }
                    # Create OAuth session with stored token
                    self.session = OAuth2Session(
                        self.client_id,
                        token=self.token,
                        auto_refresh_url=self.token_url,
                        auto_refresh_kwargs={
                            "client_id": self.client_id,
                            "client_secret": self.client_secret
                        },
                        token_updater=self._token_updater
                    )
    
    def _token_updater(self, token):
        """Callback to update tokens when they are refreshed"""
        self.token = token
        expires_at = None
        if "expires_in" in token:
            expires_at = datetime.now() + timedelta(seconds=token["expires_in"])
        
        self.token_storage.store_tokens(
            self.provider_name,
            token["access_token"],
            token.get("refresh_token"),
            expires_at
        )
    
    def _start_local_server(self):
        """Start local HTTP server to handle OAuth callback"""
        try:
            # Parse redirect URI to get port
            parsed_uri = urlparse(self.redirect_uri)
            port = parsed_uri.port or 8080
            
            server_address = ('localhost', port)
            self._httpd = HTTPServer(server_address, OAuth2CallbackHandler)
            self._httpd.auth_code = None
            self._httpd.state = None
            self._httpd.error = None
            
            self._httpd_thread = threading.Thread(target=self._httpd.serve_forever)
            self._httpd_thread.daemon = True
            self._httpd_thread.start()
            
            return self._httpd
        except Exception as e:
            raise Exception(f"Failed to start local server: {e}")
    
    def initiate_authorization(self):
        """
        Start OAuth 2.0 authorization flow
        Returns the HTTP server instance for polling
        """
        try:
            # Start local server
            httpd = self._start_local_server()
            
            # Generate PKCE pair if enabled
            extra_params = {}
            if self.use_pkce:
                self._generate_pkce_pair()
                extra_params["code_challenge"] = self.code_challenge
                extra_params["code_challenge_method"] = "S256"
            
            # Create OAuth session
            oauth = OAuth2Session(
                self.client_id,
                scope=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            # Generate authorization URL
            authorization_url, state = oauth.authorization_url(
                self.authorization_url,
                **extra_params
            )
            
            # Store state for verification
            self._state = state
            
            # Open browser
            webbrowser.open(authorization_url)
            
            return httpd
            
        except Exception as e:
            if self._httpd:
                self._httpd.shutdown()
            raise Exception(f"Failed to initiate authorization: {e}")
    
    def finish_authorization(self, httpd, timeout=300):
        """
        Complete OAuth authorization flow
        
        Args:
            httpd: HTTP server instance from initiate_authorization
            timeout: Maximum time to wait for callback (seconds)
        
        Returns:
            bool: True if authorization successful, False otherwise
        """
        try:
            # Wait for authorization code with timeout
            start_time = time.time()
            while not httpd.auth_code and not httpd.error:
                if time.time() - start_time > timeout:
                    raise Exception("Authorization timeout")
                time.sleep(0.1)
            
            # Stop the server
            httpd.shutdown()
            if self._httpd_thread:
                self._httpd_thread.join(timeout=5)
            
            # Check for errors
            if httpd.error:
                raise Exception(f"Authorization error: {httpd.error}")
            
            if not httpd.auth_code:
                raise Exception("No authorization code received")
            
            # Verify state parameter
            if hasattr(self, '_state') and httpd.state != self._state:
                raise Exception("State parameter mismatch - possible CSRF attack")
            
            # Exchange code for tokens
            return self._exchange_code_for_tokens(httpd.auth_code)
            
        except Exception as e:
            print(f"Authorization failed: {e}")
            return False
    
    def _exchange_code_for_tokens(self, auth_code):
        """Exchange authorization code for access tokens"""
        try:
            # Prepare token request
            oauth = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri)
            
            token_params = {
                "code": auth_code,
                "client_secret": self.client_secret
            }
            
            # Add PKCE verifier if used
            if self.use_pkce and self.code_verifier:
                token_params["code_verifier"] = self.code_verifier
            
            # Fetch tokens
            self.token = oauth.fetch_token(
                self.token_url,
                **token_params
            )
            
            # Calculate expiration time
            expires_at = None
            if "expires_in" in self.token:
                expires_at = datetime.now() + timedelta(seconds=self.token["expires_in"])
            
            # Store tokens securely
            self.token_storage.store_tokens(
                self.provider_name,
                self.token["access_token"],
                self.token.get("refresh_token"),
                expires_at
            )
            
            # Create authenticated session
            self.session = OAuth2Session(
                self.client_id,
                token=self.token,
                auto_refresh_url=self.token_url,
                auto_refresh_kwargs={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                },
                token_updater=self._token_updater
            )
            
            return True
            
        except Exception as e:
            print(f"Token exchange failed: {e}")
            return False
    
    def is_authenticated(self):
        """Check if client has valid authentication"""
        if not self.token or not self.session:
            return False
        
        # Check token expiration
        if "expires_at" in self.token:
            if datetime.now() >= self.token["expires_at"]:
                # Try to refresh token
                return self._refresh_token()
        
        return True
    
    def _refresh_token(self):
        """Refresh access token using refresh token"""
        if not self.token or not self.token.get("refresh_token"):
            return False
        
        try:
            # The OAuth2Session will automatically refresh the token
            # when making a request if auto_refresh_url is set
            return True
        except Exception as e:
            print(f"Token refresh failed: {e}")
            # Clear invalid tokens
            self.logout()
            return False
    
    def call_model(self, prompt, **kwargs):
        """
        Make authenticated API call to external model
        
        Args:
            prompt: Text prompt for the model
            **kwargs: Additional API parameters
        
        Returns:
            dict: API response
        """
        if not self.is_authenticated():
            raise Exception("Client not authenticated. Please authenticate first.")
        
        try:
            # Prepare API request
            api_endpoint = f"{self.api_base_url}/completions"
            payload = {
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", 50),
                **kwargs
            }
            
            # Make authenticated request
            response = self.session.post(api_endpoint, json=payload)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                # Token might be expired, try refresh
                if self._refresh_token():
                    # Retry the request
                    response = self.session.post(api_endpoint, json=payload)
                    response.raise_for_status()
                    return response.json()
                else:
                    raise Exception("Authentication expired. Please re-authenticate.")
            else:
                raise Exception(f"API call failed: {e}")
        except Exception as e:
            raise Exception(f"Model call failed: {e}")
    
    def logout(self):
        """Clear authentication and stored tokens"""
        self.token = None
        self.session = None
        self.token_storage.delete_tokens(self.provider_name)
    
    def get_auth_status(self):
        """Get detailed authentication status"""
        if not self.token:
            return {"authenticated": False, "message": "Not authenticated"}
        
        status = {"authenticated": True}
        
        if "expires_at" in self.token:
            expires_at = self.token["expires_at"]
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at)
            
            time_remaining = expires_at - datetime.now()
            status["expires_at"] = expires_at.isoformat()
            status["expires_in_seconds"] = int(time_remaining.total_seconds())
            status["expires_in_minutes"] = int(time_remaining.total_seconds() / 60)
        
        return status
