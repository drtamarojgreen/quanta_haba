import webbrowser
import requests
from requests_oauthlib import OAuth2Session
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Placeholder credentials - in a real application, these would be stored securely
# and not hardcoded.
REDIRECT_URI = "http://localhost:8080/callback"

class OAuth2CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Handles the redirect from the OAuth provider.
        Extracts the authorization code and state.
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Authentication Successful!</h1>")
        self.wfile.write(b"<p>You can close this window now.</p>")

        # The server attribute is set by the ExternalModelClient
        if 'code' in self.path:
            self.server.auth_code = self.path.split('code=')[1].split('&')[0]

class ExternalModelClient:
    def __init__(self, config):
        self.config = config
        self.client_id = self.config.get("client_id", "")
        self.client_secret = self.config.get("client_secret", "")
        self.authorization_url = self.config.get("authorization_url", "")
        self.token_url = self.config.get("token_url", "")
        self.api_base_url = self.config.get("api_base_url", "")

        self.session = None
        self.token = None
        self._httpd_thread = None

    def _start_local_server(self):
        """
        Starts a local HTTP server in a separate thread to handle the OAuth redirect.
        """
        server_address = ('localhost', 8080)
        httpd = HTTPServer(server_address, OAuth2CallbackHandler)
        httpd.auth_code = None # To store the received auth code

        self._httpd_thread = threading.Thread(target=httpd.serve_forever)
        self._httpd_thread.daemon = True
        self._httpd_thread.start()

        return httpd

    def initiate_authorization(self):
        """
        Starts the OAuth 2.0 authorization flow by opening the browser.
        Returns the httpd server instance that is listening for the callback.
        This is non-blocking. The caller is responsible for polling the
        httpd instance for the auth_code.
        """
        # Step 1: Start local server to catch redirect
        httpd = self._start_local_server()

        # Step 2: User authorization
        oauth = OAuth2Session(self.client_id, redirect_uri=REDIRECT_URI)
        authorization_url, state = oauth.authorization_url(self.authorization_url)

        webbrowser.open(authorization_url)

        return httpd

    def finish_authorization(self, httpd):
        """
        Finishes the authorization flow once the auth code is available.
        This should be called after the local server has received the code.
        """
        if httpd.auth_code is None:
            # This should not happen if called correctly
            return False

        auth_code = httpd.auth_code

        # The server thread should be stopped by the caller.
        # In a more robust implementation, the server would be managed better.

        # Step 4: Fetch the access token
        try:
            self._fetch_token(auth_code)
            return True
        except Exception as e:
            # This is a simplified error handling.
            print(f"Error fetching token: {e}")
            return False

    def _fetch_token(self, auth_code):
        """
        Exchanges the authorization code for an access token.
        """
        oauth = OAuth2Session(self.client_id, redirect_uri=REDIRECT_URI)
        self.token = oauth.fetch_token(
            self.token_url,
            code=auth_code,
            client_secret=self.client_secret
        )
        self.session = oauth

    def call_model(self, prompt):
        """
        Makes a call to the external model's API.
        """
        if not self.session or not self.token:
            raise Exception("Client not authenticated. Please call initiate_authorization() first.")

        # Example API call
        response = self.session.post(
            f"{self.api_base_url}/completions",
            json={"prompt": prompt, "max_tokens": 50}
        )
        response.raise_for_status()
        return response.json()

    def is_authenticated(self):
        """
        Checks if the client has a valid token.
        """
        return self.token is not None
