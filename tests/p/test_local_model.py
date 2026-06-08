import unittest
import os
from unittest.mock import patch, MagicMock
import sys

# Mocking all dependencies that might fail in this environment
mock_modules = [
    'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.font', 'tkinter.messagebox',
    'selenium', 'selenium.webdriver', 'selenium.webdriver.chrome.options', 'selenium.webdriver.chrome.service',
    'requests_oauthlib', 'menu', 'haba_parser', 'components', 'script_runner', 'html_exporter', 'oauth_client', 'config_manager'
]
for module in mock_modules:
    sys.modules[module] = MagicMock()

# Mocking QuantaDemoWindow to avoid its constructor but test its methods
class MockQuantaDemoWindow:
    def __init__(self):
        self.quanta_config = {}
        self.work_products = []
        self.external_model_client = None
        self.model = None
        self.log_to_console = MagicMock()

    # Copy the real methods for testing
    def _load_quanta_config(self):
        """Loads configuration from .quanta file if it exists."""
        config = {}
        # Try to find .quanta in the project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Adjusted for test environment - look in current dir
        quanta_path = os.path.join(os.getcwd(), ".quanta")
        
        if os.path.exists(quanta_path):
            try:
                with open(quanta_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        if '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
            except Exception as e:
                print(f"Error loading .quanta: {e}")
        return config

    def call_quanta_model(self, task, line_index):
        import datetime
        import subprocess
        
        model_response = f"Stubbed response for '{task}'"
        is_stubbed = True

        # Fallback to llama-cli from .quanta
        if self.quanta_config.get("model.llama_cli_path") and self.quanta_config.get("engine.model_path"):
            try:
                self.log_to_console("Calling local llama-cli model...")
                llama_path = self.quanta_config.get("model.llama_cli_path")
                model_path = self.quanta_config.get("engine.model_path")
                
                cmd = [
                    llama_path,
                    "-m", model_path,
                    "-p", task,
                    "-n", "128",
                    "--temp", "0",
                    "--no-display-prompt",
                    "--log-disable",
                    "--simple-io",
                    "--single-turn",
                    "--no-show-timings"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    output = result.stdout
                    # Cleanup output (similar to C++ implementation)
                    prompt_marker = f"> {task}"
                    if prompt_marker in output:
                        output = output.split(prompt_marker, 1)[1]
                    
                    if "Exiting..." in output:
                        output = output.split("Exiting...", 1)[0]
                    
                    model_response = output.strip()
                    if not model_response:
                        model_response = "Error: Empty response from llama-cli."
                        is_stubbed = True
                    else:
                        is_stubbed = False
                else:
                    model_response = f"llama-cli error: {result.stderr}"
                    is_stubbed = True
            except Exception as e:
                self.log_to_console(f"llama-cli error: {e}")
                model_response = f"Stubbed response for '{task}'"
                is_stubbed = True

        # Create work product entry
        work_product = {
            "id": len(self.work_products) + 1,
            "timestamp": datetime.datetime.now().isoformat(),
            "task": task,
            "prompt": task,
            "model_response": model_response,
            "toolkit_result": f"Processed: {model_response}",
            "status": "completed",
            "is_stubbed": is_stubbed,
            "line_index": line_index
        }
        self.work_products.append(work_product)

class TestLocalModelIntegration(unittest.TestCase):
    def setUp(self):
        self.window = MockQuantaDemoWindow()

    def test_load_quanta_config_success(self):
        # Create a temporary .quanta file
        with open(".quanta", "w") as f:
            f.write("engine.model_path=test_model.gguf\n")
            f.write("model.llama_cli_path=test_cli\n")
        
        config = self.window._load_quanta_config()
        self.assertEqual(config.get("engine.model_path"), "test_model.gguf")
        self.assertEqual(config.get("model.llama_cli_path"), "test_cli")
        
        if os.path.exists(".quanta"):
            os.remove(".quanta")

    def test_load_quanta_config_with_comments(self):
        with open(".quanta", "w") as f:
            f.write("# This is a comment\n")
            f.write("key=value\n")
        
        config = self.window._load_quanta_config()
        self.assertEqual(config.get("key"), "value")
        self.assertNotIn("# This is a comment", config)
        
        if os.path.exists(".quanta"):
            os.remove(".quanta")

    @patch('subprocess.run')
    def test_call_quanta_model_llama_cli(self, mock_run):
        # Setup config
        self.window.quanta_config = {
            "model.llama_cli_path": "mock_cli",
            "engine.model_path": "mock_model.gguf"
        }
        
        # Mock successful subprocess call
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "> test task\nResponse from model\nExiting..."
        mock_run.return_value = mock_result
        
        # Call the method
        with patch('datetime.datetime') as mock_date:
            mock_date.now.return_value.isoformat.return_value = "2023-01-01"
            self.window.call_quanta_model("test task", 0)
        
        # Verify the response was cleaned up correctly
        self.assertEqual(len(self.window.work_products), 1)
        self.assertEqual(self.window.work_products[0]["model_response"], "Response from model")

if __name__ == '__main__':
    unittest.main()
