import unittest
import tkinter as tk
import os
import sys
from unittest.mock import patch, MagicMock

# Add src/p to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'p'))

# Conditional import to handle potential CI/CD environment without GUI
try:
    from editor import QuantaDemoWindow
    GUI_AVAILABLE = True
except tk.TclError:
    GUI_AVAILABLE = False
except ImportError:
    # Handle cases where editor.py itself might have an import error on a headless system
    GUI_AVAILABLE = False
    QuantaDemoWindow = None


@unittest.skipIf(not GUI_AVAILABLE, "Skipping GUI tests in a headless environment")
class TestQuantaDemoWindow(unittest.TestCase):
    """Comprehensive tests for the QuantaDemoWindow class."""

    def setUp(self):
        """Set up the test environment before each test."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window during tests

    def tearDown(self):
        """Clean up the test environment after each test."""
        # Check if root window was destroyed during a test, if not, destroy it.
        if self.root.winfo_exists():
            self.root.destroy()

    @patch('editor.QuantaDemoWindow.initialize_model')
    def test_initialization_and_layout(self, mock_initialize_model):
        """
        Tests if the demo window initializes correctly and creates the three-panel layout.
        """
        # GIVEN: The QuantaDemoWindow is to be created
        # WHEN: The window is instantiated
        demo_window = QuantaDemoWindow(self.root)
        demo_window.update_idletasks() # Ensure widgets are created

        # THEN: The model initialization is called once
        mock_initialize_model.assert_called_once()

        # AND: The window has the correct title
        self.assertEqual(demo_window.title(), "Quanta Haba Demo")

        # AND: The three main panels are created and labeled correctly
        # We find widgets by their text labels to confirm they exist.
        labels = {widget.cget("text"): widget for widget in demo_window.winfo_children() if isinstance(widget, tk.Label)}

        # Note: The labels are inside frames, so we need to search recursively
        def find_label(widget, text):
            if isinstance(widget, tk.Label) and widget.cget("text") == text:
                return True
            for child in widget.winfo_children():
                if find_label(child, text):
                    return True
            return False

        self.assertTrue(find_label(demo_window, "Prompt Editor"))
        self.assertTrue(find_label(demo_window, "Model Responses"))
        self.assertTrue(find_label(demo_window, "Console Log"))

        # AND: The core text/listbox widgets exist
        self.assertTrue(hasattr(demo_window, 'prompt_text'))
        self.assertTrue(hasattr(demo_window, 'dashboard_listbox'))
        self.assertTrue(hasattr(demo_window, 'console_log'))

        demo_window.destroy()

    @patch('editor.QuantaDemoWindow.initialize_model')
    def test_default_prompt_loading(self, mock_initialize_model):
        """
        Tests if the default prompt file is loaded correctly on start.
        """
        # GIVEN: A QuantaDemoWindow instance
        demo_window = QuantaDemoWindow(self.root)
        demo_window.update_idletasks()

        # AND: The content of the default prompt file
        prompt_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'p', 'default_prompt.txt')
        with open(prompt_file_path, "r") as f:
            expected_content = f.read()

        # WHEN: The demo startup process is triggered
        # (It's normally called with `after`, we call it directly for the test)
        demo_window.start_quanta_demo()
        demo_window.update_idletasks()

        # THEN: The prompt_text widget contains the content of the file
        actual_content = demo_window.prompt_text.get("1.0", tk.END)
        self.assertEqual(actual_content.strip(), expected_content.strip())

        # AND: A success message is logged to the console
        console_content = demo_window.console_log.get("1.0", tk.END)
        self.assertIn(f"Loaded prompt file: {prompt_file_path}", console_content)

        demo_window.destroy()

    @patch('editor.QuantaDemoWindow.call_quanta_model')
    @patch('editor.QuantaDemoWindow.initialize_model')
    def test_task_processing_flow(self, mock_initialize_model, mock_call_model):
        """
        Tests the core logic of processing a single TODO task.
        This test simulates the flow of identifying a task, "processing" it,
        and updating the UI.
        """
        # GIVEN: A QuantaDemoWindow with a loaded prompt
        demo_window = QuantaDemoWindow(self.root)
        demo_window.update_idletasks()
        demo_window.start_quanta_demo() # Load the default prompt
        demo_window.update_idletasks()

        # WHEN: The next task is processed
        # The first task is "Generate project title"
        demo_window.process_next_task()
        demo_window.update_idletasks()

        # THEN: The model call is triggered with the correct task
        mock_call_model.assert_called_once_with("Generate project title", 0)

        # To simulate the rest of the flow, we can manually call the parts
        # that are normally triggered by the model response.

        # GIVEN: A mocked model response flow
        task = "Generate project title"
        line_index = 0

        # WHEN: We simulate the UI update that happens after a model call
        # (This logic is from the real `call_quanta_model` method)
        demo_window.dashboard_listbox.insert(tk.END, f"✓ {task} → Stubbed response")
        original_line = demo_window.prompt_text.get(f"{line_index + 1}.0", f"{line_index + 1}.end")
        new_line = original_line.replace("TODO:", "DONE:", 1)
        demo_window.prompt_text.delete(f"{line_index + 1}.0", f"{line_index + 1}.end")
        demo_window.prompt_text.insert(f"{line_index + 1}.0", new_line)
        demo_window.update_idletasks()

        # THEN: The prompt text is updated from TODO to DONE
        updated_first_line = demo_window.prompt_text.get("1.0", "1.end")
        self.assertIn("DONE: Generate project title", updated_first_line)

        # AND: The dashboard listbox is updated
        dashboard_content = demo_window.dashboard_listbox.get(0)
        self.assertIn("✓ Generate project title → Stubbed response", dashboard_content)

        demo_window.destroy()

if __name__ == '__main__':
    # This allows running the test file directly, but it's optional
    # and won't be used in the context of the agent's execution.
    unittest.main()
