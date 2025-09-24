import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add src/p to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'p'))

from script_runner import ScriptRunner, run_python_script
from haba_parser import HabaParser, HabaData


class TestScriptRunner(unittest.TestCase):
    """Unit tests for ScriptRunner class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.script_runner = ScriptRunner()
        self.parser = HabaParser()
        
    def test_script_runner_initialization(self):
        """Test that ScriptRunner initializes correctly"""
        self.assertIsInstance(self.script_runner, ScriptRunner)
        
    @patch('script_runner.webdriver')
    def test_run_script_with_empty_haba_content(self, mock_webdriver):
        """Test running script with empty .haba content"""
        haba_content = ""
        
        logs, tasks = self.script_runner.run_script(haba_content)
        
        self.assertEqual(logs, [])
        self.assertEqual(tasks, [])
        
    @patch('script_runner.webdriver')
    def test_run_script_with_no_script_layer(self, mock_webdriver):
        """Test running script with .haba content but no script layer"""
        haba_content = """Hello World
This has no script layer.
"""
        
        logs, tasks = self.script_runner.run_script(haba_content)
        
        self.assertEqual(logs, [])
        self.assertEqual(tasks, [])
        
    @patch('script_runner.webdriver')
    def test_run_script_with_javascript(self, mock_webdriver):
        """Test running script with JavaScript code"""
        # Mock the webdriver
        mock_driver = MagicMock()
        mock_webdriver.Firefox.return_value = mock_driver
        mock_driver.execute_script.side_effect = [
            ['Test log message'],  # console_logs
            None  # js_error
        ]
        
        haba_content = """Test Content

---SCRIPT---
console.log('Test log message');
"""
        
        logs, tasks = self.script_runner.run_script(haba_content)
        
        self.assertEqual(logs, ['Test log message'])
        self.assertEqual(len(tasks), 0)
        mock_driver.quit.assert_called_once()
        
    @patch('script_runner.webdriver')
    def test_run_script_with_javascript_error(self, mock_webdriver):
        """Test running script with JavaScript that has errors"""
        # Mock the webdriver
        mock_driver = MagicMock()
        mock_webdriver.Firefox.return_value = mock_driver
        mock_driver.execute_script.side_effect = [
            [],  # console_logs
            {'name': 'ReferenceError', 'message': 'undefined variable', 'stack': 'stack trace'}  # js_error
        ]
        
        haba_content = """Test Content

---SCRIPT---
console.log(undefinedVariable);
"""
        
        logs, tasks = self.script_runner.run_script(haba_content)
        
        self.assertEqual(logs, [])
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['type'], 'error')
        self.assertIn('ReferenceError', tasks[0]['description'])
        self.assertIn('undefined variable', tasks[0]['description'])
        
    @patch('script_runner.webdriver')
    def test_run_script_with_todo_comments(self, mock_webdriver):
        """Test running script that logs TODO comments"""
        # Mock the webdriver
        mock_driver = MagicMock()
        mock_webdriver.Firefox.return_value = mock_driver
        mock_driver.execute_script.side_effect = [
            ['TODO: Fix this function', 'FIXME: Handle edge case'],  # console_logs
            None  # js_error
        ]
        
        haba_content = """Test Content

---SCRIPT---
console.log('TODO: Fix this function');
console.log('FIXME: Handle edge case');
"""
        
        logs, tasks = self.script_runner.run_script(haba_content)
        
        self.assertEqual(len(logs), 2)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]['type'], 'todo')
        self.assertEqual(tasks[0]['description'], 'TODO: Fix this function')
        self.assertEqual(tasks[1]['type'], 'todo')
        self.assertEqual(tasks[1]['description'], 'FIXME: Handle edge case')
        
    @patch('script_runner.webdriver')
    def test_run_script_webdriver_exception(self, mock_webdriver):
        """Test handling of webdriver exceptions"""
        # Mock webdriver to raise exception
        mock_webdriver.Firefox.side_effect = Exception("WebDriver error")
        
        haba_content = """Test Content

---SCRIPT---
console.log('This should fail');
"""
        
        # Should not raise exception, should handle gracefully
        logs, tasks = self.script_runner.run_script(haba_content)
        
        # Should return empty results when webdriver fails
        self.assertEqual(logs, [])
        self.assertEqual(tasks, [])


class TestRunPythonScript(unittest.TestCase):
    """Unit tests for run_python_script function"""
    
    @patch('script_runner.subprocess.run')
    def test_run_python_script_success(self, mock_run):
        """Test running Python script successfully"""
        # Mock successful subprocess run
        mock_result = MagicMock()
        mock_result.stdout = "Hello World\nScript executed successfully"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        script_content = "print('Hello World')\nprint('Script executed successfully')"
        
        logs, tasks = run_python_script(script_content)
        
        self.assertEqual(len(logs), 2)
        self.assertIn("Hello World", logs)
        self.assertIn("Script executed successfully", logs)
        self.assertEqual(len(tasks), 0)
        
    @patch('script_runner.subprocess.run')
    def test_run_python_script_with_error(self, mock_run):
        """Test running Python script with error"""
        # Mock subprocess run with error
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = "NameError: name 'undefined_var' is not defined"
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        script_content = "print(undefined_var)"
        
        logs, tasks = run_python_script(script_content)
        
        self.assertEqual(len(logs), 1)
        self.assertIn("NameError", logs[0])
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['type'], 'error')
        self.assertIn("NameError", tasks[0]['description'])
        
    @patch('script_runner.subprocess.run')
    def test_run_python_script_timeout(self, mock_run):
        """Test running Python script that times out"""
        # Mock subprocess timeout
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired('python', 10)
        
        script_content = "import time\ntime.sleep(20)"
        
        logs, tasks = run_python_script(script_content)
        
        self.assertEqual(len(logs), 1)
        self.assertIn("timed out", logs[0])
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['type'], 'error')
        self.assertIn("timed out", tasks[0]['description'])
        
    @patch('script_runner.subprocess.run')
    def test_run_python_script_exception(self, mock_run):
        """Test handling of unexpected exceptions"""
        # Mock subprocess to raise exception
        mock_run.side_effect = Exception("Unexpected error")
        
        script_content = "print('This should fail')"
        
        logs, tasks = run_python_script(script_content)
        
        self.assertEqual(len(logs), 1)
        self.assertIn("Failed to run python script", logs[0])
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['type'], 'error')
        self.assertIn("Unexpected error", tasks[0]['description'])


class TestScriptRunnerBDD(unittest.TestCase):
    """BDD-style tests for ScriptRunner"""
    
    def setUp(self):
        self.script_runner = ScriptRunner()
        
    @patch('script_runner.webdriver')
    def test_given_haba_content_with_script_when_run_then_executes_javascript(self, mock_webdriver):
        """
        Given: .haba content with JavaScript in script layer
        When: The script is run
        Then: Executes JavaScript and returns logs
        """
        # Given
        mock_driver = MagicMock()
        mock_webdriver.Firefox.return_value = mock_driver
        mock_driver.execute_script.side_effect = [
            ['JavaScript executed successfully'],
            None
        ]
        
        haba_content = """Test Document

---SCRIPT---
console.log('JavaScript executed successfully');
"""
        
        # When
        logs, tasks = self.script_runner.run_script(haba_content)
        
        # Then
        self.assertEqual(logs, ['JavaScript executed successfully'])
        self.assertEqual(len(tasks), 0)
        mock_driver.quit.assert_called_once()
        
    @patch('script_runner.webdriver')
    def test_given_javascript_with_error_when_run_then_creates_error_task(self, mock_webdriver):
        """
        Given: JavaScript code with runtime error
        When: The script is run
        Then: Creates error task with error details
        """
        # Given
        mock_driver = MagicMock()
        mock_webdriver.Firefox.return_value = mock_driver
        mock_driver.execute_script.side_effect = [
            [],
            {'name': 'TypeError', 'message': 'Cannot read property', 'stack': 'Error stack'}
        ]
        
        haba_content = """Test Document

---SCRIPT---
var obj = null;
console.log(obj.property);
"""
        
        # When
        logs, tasks = self.script_runner.run_script(haba_content)
        
        # Then
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['type'], 'error')
        self.assertIn('TypeError', tasks[0]['description'])
        self.assertIn('Cannot read property', tasks[0]['description'])
        
    @patch('script_runner.webdriver')
    def test_given_javascript_with_todos_when_run_then_creates_todo_tasks(self, mock_webdriver):
        """
        Given: JavaScript code that logs TODO/FIXME comments
        When: The script is run
        Then: Creates todo tasks for each TODO/FIXME
        """
        # Given
        mock_driver = MagicMock()
        mock_webdriver.Firefox.return_value = mock_driver
        mock_driver.execute_script.side_effect = [
            ['TODO: Implement feature X', 'FIXME: Bug in calculation'],
            None
        ]
        
        haba_content = """Test Document

---SCRIPT---
console.log('TODO: Implement feature X');
console.log('FIXME: Bug in calculation');
"""
        
        # When
        logs, tasks = self.script_runner.run_script(haba_content)
        
        # Then
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]['type'], 'todo')
        self.assertEqual(tasks[0]['description'], 'TODO: Implement feature X')
        self.assertEqual(tasks[1]['type'], 'todo')
        self.assertEqual(tasks[1]['description'], 'FIXME: Bug in calculation')
        
    @patch('script_runner.subprocess.run')
    def test_given_python_script_when_run_then_executes_and_returns_output(self, mock_run):
        """
        Given: Python script content
        When: The script is run
        Then: Executes Python and returns output
        """
        # Given
        mock_result = MagicMock()
        mock_result.stdout = "Python script output\nSecond line"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        script_content = """
print('Python script output')
print('Second line')
"""
        
        # When
        logs, tasks = run_python_script(script_content)
        
        # Then
        self.assertEqual(len(logs), 2)
        self.assertIn('Python script output', logs)
        self.assertIn('Second line', logs)
        self.assertEqual(len(tasks), 0)
        
    @patch('script_runner.subprocess.run')
    def test_given_python_script_with_error_when_run_then_creates_error_task(self, mock_run):
        """
        Given: Python script with syntax/runtime error
        When: The script is run
        Then: Creates error task with error message
        """
        # Given
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = "SyntaxError: invalid syntax"
        mock_run.return_value = mock_result
        
        script_content = "print('Hello World'"  # Missing closing parenthesis
        
        # When
        logs, tasks = run_python_script(script_content)
        
        # Then
        self.assertEqual(len(logs), 1)
        self.assertIn('SyntaxError', logs[0])
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['type'], 'error')
        self.assertIn('SyntaxError', tasks[0]['description'])


class TestScriptRunnerIntegration(unittest.TestCase):
    """Integration tests for ScriptRunner with HabaParser"""
    
    def setUp(self):
        self.script_runner = ScriptRunner()
        self.parser = HabaParser()
        
    @patch('script_runner.webdriver')
    def test_parse_then_run_workflow(self, mock_webdriver):
        """Test complete workflow: parse .haba content then run script"""
        # Mock webdriver
        mock_driver = MagicMock()
        mock_webdriver.Firefox.return_value = mock_driver
        mock_driver.execute_script.side_effect = [
            ['Integration test log'],
            None
        ]
        
        # Create complete .haba content
        haba_content = """Integration Test Document
This tests parsing and script execution.

---PRESENTATION---
h1: color: 'blue'
p: font-size: '14px'

---SCRIPT---
console.log('Integration test log');
function testFunction() {
    return 'success';
}
"""
        
        # Parse the content (to verify it works)
        haba_data = self.parser.parse(haba_content)
        self.assertEqual(haba_data.content.strip(), "Integration Test Document\nThis tests parsing and script execution.")
        self.assertIn("console.log('Integration test log');", haba_data.script)
        
        # Run the script
        logs, tasks = self.script_runner.run_script(haba_content)
        
        # Verify script execution
        self.assertEqual(logs, ['Integration test log'])
        self.assertEqual(len(tasks), 0)
        mock_driver.quit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
