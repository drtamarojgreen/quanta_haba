import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import tkinter as tk

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from p.editor import QuantaDemoWindow

# Since this is a tkinter application, we need a root window for tests, but we will not run the mainloop.
class MockRoot(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # Hide the window

class TestQuantaDemoWindow(unittest.TestCase):
    def setUp(self):
        # Create a mock root window
        self.root = MockRoot()
        # Patch the tkinter Toplevel to avoid creating real windows
        with patch('tkinter.Toplevel'):
            self.app = QuantaDemoWindow(master=self.root)

    def tearDown(self):
        # Destroy the root window after each test
        self.root.destroy()

    @patch('p.editor.QUANTA_TISSU_AVAILABLE', True)
    @patch('p.editor.Tokenizer')
    @patch('p.editor.QuantaTissu')
    @patch('builtins.open', new_callable=mock_open, read_data='{"embedding_dim": 128}')
    @patch('os.path.join', return_value='/fake/path/to/config')
    def test_initialize_model_success(self, mock_join, mock_file, mock_qt, mock_tokenizer):
        """Test successful model initialization."""
        self.app.initialize_model()
        self.app.log_to_console.assert_any_call("Quanta Tissu model initialized successfully.")
        self.assertIsNotNone(self.app.model)
        self.assertIsNotNone(self.app.tokenizer)

    @patch('p.editor.QUANTA_TISSU_AVAILABLE', False)
    def test_initialize_model_no_quanta_tissu(self, mock_qt_available):
        """Test model initialization when quanta_tissu is not available."""
        self.app.initialize_model()
        self.app.log_to_console.assert_any_call("Error: `quanta_tissu` package not found. Demo will use stubbed responses.")
        self.assertIsNone(self.app.model)
        self.assertIsNone(self.app.tokenizer)

    @patch('p.editor.QUANTA_TISSU_AVAILABLE', True)
    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('os.path.join', return_value='/fake/path/to/config')
    def test_initialize_model_file_not_found(self, mock_join, mock_open):
        """Test model initialization when a config file is not found."""
        self.app.initialize_model()
        self.app.log_to_console.assert_any_call("Model Error: [Errno 2] No such file or directory: '/fake/path/to/config'. Check paths. Demo will use stubbed responses.")
        self.assertIsNone(self.app.model)
        self.assertIsNone(self.app.tokenizer)

    def test_process_next_task_found(self):
        """Test processing when a TODO task is found."""
        self.app.prompt_text = MagicMock()
        self.app.prompt_text.get.return_value = "Line 1\nTODO: A task\nLine 3"
        self.app.call_quanta_model = MagicMock()

        self.app.process_next_task()

        self.app.prompt_text.tag_add.assert_called_with("highlight", "2.0", "2.end")
        self.app.log_to_console.assert_any_call("Processing task: A task")
        self.app.call_quanta_model.assert_called_with("A task", 1)

    def test_process_next_task_not_found(self):
        """Test processing when no TODO task is found."""
        self.app.prompt_text = MagicMock()
        self.app.prompt_text.get.return_value = "Line 1\nLine 2\nLine 3"
        self.app.call_quanta_model = MagicMock()

        self.app.process_next_task()

        self.app.log_to_console.assert_any_call("All tasks completed!")
        self.app.call_quanta_model.assert_not_called()

    @patch('p.editor.generate_text', return_value="A generated response.")
    def test_call_quanta_model_with_model(self, mock_generate_text):
        """Test calling the Quanta model when it's initialized."""
        self.app.model = MagicMock()
        self.app.tokenizer = MagicMock()
        self.app.prompt_text = MagicMock()
        self.app.dashboard_listbox = MagicMock()
        self.app.after = MagicMock()

        self.app.call_quanta_model("A task", 0)

        self.assertEqual(len(self.app.work_products), 1)
        self.assertEqual(self.app.work_products[0]['task'], "A task")
        self.assertEqual(self.app.work_products[0]['model_response'], "A generated response.")
        self.assertFalse(self.app.work_products[0]['is_stubbed'])
        self.app.dashboard_listbox.insert.assert_called_with(tk.END, "✓ A task → A generated response.")

    def test_call_quanta_model_stubbed(self):
        """Test calling the Quanta model when it's not initialized (stubbed response)."""
        self.app.model = None
        self.app.tokenizer = None
        self.app.prompt_text = MagicMock()
        self.app.dashboard_listbox = MagicMock()
        self.app.after = MagicMock()

        self.app.call_quanta_model("A task", 0)

        self.assertEqual(len(self.app.work_products), 1)
        self.assertEqual(self.app.work_products[0]['task'], "A task")
        self.assertEqual(self.app.work_products[0]['model_response'], "Stubbed response for 'A task'")
        self.assertTrue(self.app.work_products[0]['is_stubbed'])
        self.app.dashboard_listbox.insert.assert_called_with(tk.END, "⚠ A task → Stubbed response for 'A task'")


if __name__ == '__main__':
    unittest.main()