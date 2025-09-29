import unittest
import os
import sys
from unittest.mock import MagicMock, patch

# To import the editor module from 'src', we need to add the 'src' directory to the path.
# This finds the 'src' directory relative to this test file.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

# We must mock tkinter before it's imported by the editor module.
# This prevents actual GUI windows from being created during tests.
mock_tk = MagicMock()
# We need to mock specific constants and classes from tkinter
mock_tk.END = "end"
mock_tk.WORD = "word"
mock_tk.DISABLED = "disabled"
mock_tk.NORMAL = "normal"
mock_tk.RAISED = "raised"
mock_tk.VERTICAL = "vertical"
mock_tk.HORIZONTAL = "horizontal"
mock_tk.BOTH = "both"
mock_tk.X = "x"
mock_tk.W = "w"
mock_tk.LEFT = "left"

sys.modules['tkinter'] = mock_tk
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.font'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()

# Now it's safe to import the editor
from p import editor

class TestEditorFunctionality(unittest.TestCase):
    """
    BDD-style tests for the Haba Editor's functionality.
    """

    def setUp(self):
        """
        Given the editor application is running.
        This setup method creates a mocked instance of the HabaEditor.
        """
        # We need a root window for the editor, which we can mock.
        self.root = MagicMock()
        with patch('p.editor.HabaParser'), \
             patch('p.editor.ScriptRunner'), \
             patch('p.editor.HtmlExporter'):
            self.app = editor.HabaEditor(master=self.root)

    def test_editor_initialization(self):
        """
        Feature: Editor Startup
        Scenario: The editor initializes successfully.
        When the HabaEditor is created
        Then its title should be "Haba Editor".
        """
        self.app.master.title.assert_called_with("Haba Editor")

    def test_linting_for_trailing_whitespace(self):
        """
        Feature: JavaScript Linter
        Scenario: A line contains trailing whitespace.
        Given a line of code with trailing spaces
        When the linter is run
        Then the linter should identify and tag the whitespace.
        """
        # Given a script with trailing whitespace
        script_content = "var name = 'Haba';  "
        self.app.script_text.get.return_value = script_content
        self.app.script_text.tag_remove = MagicMock()
        self.app.script_text.tag_add = MagicMock()

        # When the linter is run
        editor.lint_javascript_text(self.app.script_text)

        # Then the trailing whitespace is tagged
        self.app.script_text.tag_add.assert_any_call("trailing_whitespace", "1.20", "1.22")

    def test_linting_for_missing_semicolon(self):
        """
        Feature: JavaScript Linter
        Scenario: A line is missing a semicolon.
        Given a line of code that should end with a semicolon but doesn't
        When the linter is run
        Then the linter should identify and tag the missing semicolon.
        """
        # Given
        script_content = "var x = 1"
        self.app.script_text.get.return_value = script_content
        self.app.script_text.tag_add = MagicMock()

        # When
        editor.lint_javascript_text(self.app.script_text)

        # Then
        self.app.script_text.tag_add.assert_any_call("missing_semicolon", "1.10", "1.11")


class TestCLI(unittest.TestCase):
    """
    BDD-style tests for the Command-Line Interface.
    """
    DUMMY_FILE_PATH = "test_cli_file.haba"
    DUMMY_FILE_CONTENT = "Content from CLI-loaded file."

    def setUp(self):
        """
        Given a dummy file exists on the filesystem.
        """
        with open(self.DUMMY_FILE_PATH, "w") as f:
            f.write(self.DUMMY_FILE_CONTENT)

    def tearDown(self):
        """
        Clean up the dummy file after the test.
        """
        if os.path.exists(self.DUMMY_FILE_PATH):
            os.remove(self.DUMMY_FILE_PATH)

    @patch('sys.argv')
    @patch('p.editor.tk.Tk')
    @patch('p.editor.HabaEditor')
    def test_loading_file_from_cli(self, mock_haba_editor_class, mock_tk_class, mock_argv):
        """
        Feature: CLI File Loading
        Scenario: The user provides a valid file path as an argument.
        Given the application is started with a file path argument
        When the main function is executed
        Then the file's content should be loaded into the editor's raw text widget.
        """
        # Given
        mock_argv.__getitem__.side_effect = lambda x: ['editor.py', self.DUMMY_FILE_PATH][x]
        mock_argv.__len__.return_value = 2

        mock_editor_instance = MagicMock()
        mock_haba_editor_class.return_value = mock_editor_instance

        # When
        editor.main()

        # Then
        mock_editor_instance.raw_text.delete.assert_called_with("1.0", mock_tk.END)
        mock_editor_instance.raw_text.insert.assert_called_with("1.0", self.DUMMY_FILE_CONTENT)
        mock_editor_instance.render_preview.assert_called_once()

    @patch('sys.argv')
    @patch('p.editor.tk.Tk')
    @patch('p.editor.HabaEditor')
    @patch('p.editor.messagebox')
    def test_loading_nonexistent_file_from_cli(self, mock_messagebox, mock_haba_editor_class, mock_tk_class, mock_argv):
        """
        Feature: CLI File Loading
        Scenario: The user provides an invalid file path.
        Given the application is started with a path to a non-existent file
        When the main function is executed
        Then a warning message should be shown to the user.
        """
        # Given
        non_existent_file = "no_such_file.haba"
        mock_argv.__getitem__.side_effect = lambda x: ['editor.py', non_existent_file][x]
        mock_argv.__len__.return_value = 2

        # When
        editor.main()

        # Then
        mock_messagebox.showwarning.assert_called_with("File Not Found", f"The specified file does not exist: {non_existent_file}")


if __name__ == '__main__':
    # This allows running the tests directly from the command line
    unittest.main(verbosity=2)