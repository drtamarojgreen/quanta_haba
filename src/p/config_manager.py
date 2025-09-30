import os
import json
from tkinter import messagebox

class ConfigManager:
    """
    Manages loading and saving of OAuth configurations to a JSON file.
    """
    def __init__(self, config_filename="oauth_configs.json"):
        """
        Initializes the ConfigManager.

        Args:
            config_filename (str): The name of the configuration file.
        """
        self.config_dir = os.path.join(os.path.expanduser("~"), ".quanta_haba")
        self.config_filepath = os.path.join(self.config_dir, config_filename)
        self._ensure_config_dir_exists()
        self.configs = self.load_configs()

    def _ensure_config_dir_exists(self):
        """Ensures the configuration directory exists."""
        if not os.path.exists(self.config_dir):
            try:
                os.makedirs(self.config_dir)
            except OSError as e:
                messagebox.showerror("Configuration Error", f"Could not create config directory: {e}")

    def load_configs(self):
        """
        Loads all configurations from the JSON file.

        Returns:
            dict: A dictionary of configuration profiles, with profile names as keys.
        """
        if not os.path.exists(self.config_filepath):
            return {}
        try:
            with open(self.config_filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            messagebox.showerror("Configuration Error", f"Failed to load config file: {e}")
            return {}

    def save_configs(self):
        """Saves all configurations to the JSON file."""
        try:
            with open(self.config_filepath, 'w') as f:
                json.dump(self.configs, f, indent=4)
        except IOError as e:
            messagebox.showerror("Configuration Error", f"Failed to save config file: {e}")

    def get_config(self, profile_name):
        """
        Retrieves a specific configuration profile.

        Args:
            profile_name (str): The name of the profile to retrieve.

        Returns:
            dict or None: The configuration dictionary or None if not found.
        """
        return self.configs.get(profile_name)

    def save_config(self, profile_name, config_data):
        """
        Saves or updates a specific configuration profile.

        Args:
            profile_name (str): The name of the profile to save.
            config_data (dict): The configuration data to save.
        """
        if not profile_name.strip():
            messagebox.showerror("Invalid Name", "Profile name cannot be empty.")
            return False

        self.configs[profile_name] = config_data
        self.save_configs()
        return True

    def delete_config(self, profile_name):
        """
        Deletes a specific configuration profile.

        Args:
            profile_name (str): The name of the profile to delete.
        """
        if profile_name in self.configs:
            del self.configs[profile_name]
            self.save_configs()
            return True
        return False

    def get_profile_names(self):
        """
        Returns a list of all saved profile names.

        Returns:
            list: A list of strings.
        """
        return list(self.configs.keys())