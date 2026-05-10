import unittest
import sys
import os
from io import StringIO
from unittest.mock import patch

# Add src/p to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'p'))

from cli_runner import main

class TestCliRunner(unittest.TestCase):
    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.argv', ['cli_runner.py', 'non_existent.haba'])
    def test_main_file_not_found(self, mock_stdout):
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("Error: File not found", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_main_success(self, mock_stdout):
        # Create a temporary .haba file
        with open('test_temp.haba', 'w') as f:
            f.write("<content_layer>CLI Test</content_layer>")

        try:
            with patch('sys.argv', ['cli_runner.py', 'test_temp.haba']):
                main()

            output = mock_stdout.getvalue()
            self.assertIn("Running script from 'test_temp.haba'...", output)
            self.assertIn("--- Actionable Tasks ---", output)
        finally:
            if os.path.exists('test_temp.haba'):
                os.remove('test_temp.haba')

if __name__ == '__main__':
    unittest.main()
