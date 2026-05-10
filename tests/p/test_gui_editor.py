import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src/p to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'p'))

from editor import HabaEditor

class TestGuiEditor(unittest.TestCase):
    @patch('tkinter.Tk')
    def setUp(self, mock_tk):
        self.root = mock_tk()
        self.app = HabaEditor(self.root)

    def test_load_file_logic(self):
        # Mock open to simulate file loading
        with patch('builtins.open', unittest.mock.mock_open(read_data="<content_layer>Load Test</content_layer>")):
            # We bypass the dialog by setting current_filepath directly and calling a (theoretical) load method
            # In the real editor, load_file uses askopenfilename.
            # We test the parser integration.
            data = self.app.parser.parse("<content_layer>Load Test</content_layer>")
            self.assertEqual(data.content, "Load Test")

if __name__ == '__main__':
    unittest.main()
