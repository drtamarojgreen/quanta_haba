import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the root directory to the path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.p.script_runner import ScriptRunner

class TestScriptRunner(unittest.TestCase):

    @patch('src.p.script_runner.webdriver.Firefox')
    @patch('src.p.script_runner.tempfile.NamedTemporaryFile')
    @patch('src.p.script_runner.os.remove')
    @patch('src.p.script_runner.os.path.exists', return_value=True)
    def test_run_script_and_parse_tasks(self, mock_path_exists, mock_os_remove, mock_tempfile, mock_firefox):
        # Arrange
        # Mock the webdriver
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver
        
        # Mock the return values for console logs and errors
        mock_driver.execute_script.side_effect = [
            ['"Hello, World!"', '"TODO: Finish this feature"'],  # Mocked console logs
            {'name': 'TypeError', 'message': 'x is not a function', 'stack': '...'} # Mocked JS error
        ]
        
        # Mock the temporary file
        mock_file = MagicMock()
        mock_file.__enter__.return_value.name = "/tmp/fake_file.html"
        mock_tempfile.return_value = mock_file

        haba_content = """
        <content_layer>
            <div>Test</div>
        </content_layer>
        <script_layer>
            console.log("Hello, World!");
            console.log("TODO: Finish this feature");
            x(); // This will cause a TypeError
        </script_layer>
        """
        
        runner = ScriptRunner()

        # Act
        logs, tasks = runner.run_script(haba_content)

        # Assert
        mock_firefox.assert_called_once()
        mock_driver.get.assert_called_once_with("file:///tmp/fake_file.html")
        self.assertEqual(mock_driver.execute_script.call_count, 2)
        
        # Check logs
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0], '"Hello, World!"')

        # Check tasks
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]['type'], 'error')
        self.assertEqual(tasks[0]['description'], 'TypeError: x is not a function')
        self.assertEqual(tasks[1]['type'], 'todo')
        self.assertEqual(tasks[1]['description'], 'TODO: Finish this feature')
        
        # Check that the temporary file was removed
        mock_os_remove.assert_called_once_with("/tmp/fake_file.html")

if __name__ == '__main__':
    unittest.main()
