import requests
import json

class APIClient:
    """
    A client for interacting with a large language model API.
    """
    def __init__(self, api_base_url, api_key=None):
        """
        Initializes the API client.

        Args:
            api_base_url (str): The base URL for the API.
            api_key (str, optional): The API key for authentication. Defaults to None.
        """
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def post(self, endpoint, data):
        """
        Sends a POST request to the specified API endpoint.

        Args:
            endpoint (str): The API endpoint to send the request to.
            data (dict): The data to send in the request body.

        Returns:
            dict: The JSON response from the API.
        """
        url = f"{self.api_base_url}/{endpoint}"
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def call_model_with_tools(self, messages, tools):
        """
        Sends a request to the model with a list of available tools.

        Args:
            messages (list): A list of message dictionaries.
            tools (list): A list of tool definitions.

        Returns:
            dict: The JSON response from the API.
        """
        # This is a placeholder for a more complex implementation
        # that would involve formatting the tools and messages correctly.
        data = {
            "messages": messages,
            "tools": tools
        }
        return self.post("chat/completions", data)