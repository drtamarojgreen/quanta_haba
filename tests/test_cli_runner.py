import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os
import io

# Add the root directory to the path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock selenium and its submodules to avoid import errors in a test environment
selenium_mock = MagicMock()
sys.modules['selenium'] = selenium_mock
sys.modules['selenium.webdriver'] = MagicMock()
sys.modules['selenium.webdriver.firefox'] = MagicMock()
sys.modules['selenium.webdriver.firefox.options'] = MagicMock()

# We need to import the cli_runner module to test its main function
from src.p import cli_runner

class TestCliRunner(unittest.TestCase):

    @patch('src.p.cli_runner.ScriptRunner')
    @patch('builtins.open', new_callable=mock_open, read_data="<script_layer>console.log('test');</script_layer>")
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_main_with_tasks(self, mock_stdout, mock_file, mock_script_runner):
        # Arrange
        mock_runner_instance = MagicMock()
        mock_script_runner.return_value = mock_runner_instance
        mock_runner_instance.run_script.return_value = (['"test"'], [{'type': 'todo', 'description': 'TODO: test', 'details': ''}])

        test_args = ["cli_runner.py", "dummy.haba"]
        with patch.object(sys, 'argv', test_args):
            # Act
            cli_runner.main()

        # Assert
        output = mock_stdout.getvalue()
        self.assertIn("--- Console Output ---", output)
        self.assertIn('"test"', output)
        self.assertIn("--- Actionable Tasks ---", output)
        self.assertIn("[TODO] TODO: test", output)

    @patch('src.p.cli_runner.ScriptRunner')
    @patch('builtins.open', new_callable=mock_open, read_data="<script_layer>console.log('test');</script_layer>")
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_main_no_tasks(self, mock_stdout, mock_file, mock_script_runner):
        # Arrange
        mock_runner_instance = MagicMock()
        mock_script_runner.return_value = mock_runner_instance
        mock_runner_instance.run_script.return_value = (['"test"'], [])

        test_args = ["cli_runner.py", "dummy.haba"]
        with patch.object(sys, 'argv', test_args):
            # Act
            cli_runner.main()

        # Assert
        output = mock_stdout.getvalue()
        self.assertIn("No actionable tasks found.", output)

    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_main_file_not_found(self, mock_stdout, mock_file):
        # Arrange
        test_args = ["cli_runner.py", "non_existent.haba"]
        with patch.object(sys, 'argv', test_args):
            with self.assertRaises(SystemExit) as cm:
                # Act
                cli_runner.main()
        
        # Assert
        self.assertEqual(cm.exception.code, 1)
        output = mock_stdout.getvalue()
        self.assertIn("Error: File not found", output)

if __name__ == '__main__':
    unittest.main()
