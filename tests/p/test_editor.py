import unittest
from unittest.mock import MagicMock, call
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from p.editor import lint_javascript_text

class TestLintJavaScriptText(unittest.TestCase):

    def setUp(self):
        """Set up a mock text widget for each test."""
        self.mock_text_widget = MagicMock()
        self.mock_text_widget.get.return_value = ""
        self.mock_text_widget.tag_remove.return_value = None
        self.mock_text_widget.tag_add.return_value = None

    def test_linting_empty_text(self):
        """Test that no tags are added for empty text."""
        self.mock_text_widget.get.return_value = ""
        lint_javascript_text(self.mock_text_widget)
        self.mock_text_widget.tag_add.assert_not_called()

    def test_trailing_whitespace(self):
        """Test that trailing whitespace is correctly identified."""
        self.mock_text_widget.get.return_value = "const x = 10;  "
        lint_javascript_text(self.mock_text_widget)
        self.mock_text_widget.tag_add.assert_called_with("trailing_whitespace", "1.14", "1.16")

    def test_use_of_var(self):
        """Test that 'var' keyword usage is identified."""
        self.mock_text_widget.get.return_value = "var y = 20;"
        lint_javascript_text(self.mock_text_widget)
        self.mock_text_widget.tag_add.assert_called_with("use_of_var", "1.0", "1.3")

    def test_long_line(self):
        """Test that long lines are correctly identified."""
        long_line = "a" * 81
        self.mock_text_widget.get.return_value = long_line
        lint_javascript_text(self.mock_text_widget)
        self.mock_text_widget.tag_add.assert_called_with("long_line", "1.0", f"1.{len(long_line)}")

    def test_missing_semicolon(self):
        """Test that a missing semicolon is identified."""
        self.mock_text_widget.get.return_value = "const z = 30"
        lint_javascript_text(self.mock_text_widget)
        # The tag should be on the last character of the stripped line
        self.mock_text_widget.tag_add.assert_any_call("missing_semicolon", "1.11", "1.12")


class TestLintJavaScriptTextBDD(unittest.TestCase):
    """BDD-style tests for the JavaScript linter."""

    def setUp(self):
        """Set up a mock text widget for each test."""
        self.mock_text_widget = MagicMock()
        self.mock_text_widget.get.return_value = ""
        self.mock_text_widget.tag_remove.return_value = None
        self.mock_text_widget.tag_add.return_value = None
        self.calls = []

    def tearDown(self):
        """Clear calls after each test."""
        self.calls = []

    def record_tag_add(self, tag, start, end):
        """Record calls to tag_add."""
        self.calls.append({'tag': tag, 'start': start, 'end': end})

    def test_scenario_double_equals_in_code(self):
        """
        Scenario: Using double equals in JavaScript code.
        Given a line of JavaScript code with a '==' comparison.
        When the linter is run.
        Then a 'use_of_double_equals' tag should be applied.
        """
        # Given
        code = "if (a == b) { console.log('hello'); }"
        self.mock_text_widget.get.return_value = code
        self.mock_text_widget.tag_add.side_effect = self.record_tag_add

        # When
        lint_javascript_text(self.mock_text_widget)

        # Then
        expected_call = {'tag': 'use_of_double_equals', 'start': '1.7', 'end': '1.9'}
        self.assertIn(expected_call, self.calls)

    def test_scenario_many_parameters_in_function(self):
        """
        Scenario: A function with too many parameters.
        Given a JavaScript function with more than 5 parameters.
        When the linter is run.
        Then a 'many_parameters' tag should be applied.
        """
        # Given
        code = "function tooManyParams(a, b, c, d, e, f) { return; }"
        self.mock_text_widget.get.return_value = code
        self.mock_text_widget.tag_add.side_effect = self.record_tag_add

        # When
        lint_javascript_text(self.mock_text_widget)

        # Then
        expected_call = {'tag': 'many_parameters', 'start': '1.0', 'end': '1.44'}
        self.assertIn(expected_call, self.calls)

    def test_scenario_clean_code(self):
        """
        Scenario: Linting clean JavaScript code.
        Given a clean line of JavaScript code.
        When the linter is run.
        Then no tags should be applied.
        """
        # Given
        code = "const clean = () => 'hello';"
        self.mock_text_widget.get.return_value = code
        self.mock_text_widget.tag_add.side_effect = self.record_tag_add

        # When
        lint_javascript_text(self.mock_text_widget)

        # Then
        self.assertEqual(len(self.calls), 0)


if __name__ == '__main__':
    unittest.main()