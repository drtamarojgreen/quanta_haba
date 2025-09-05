import sys
import unittest
from unittest.mock import MagicMock

# Add the root directory to the Python path to allow imports from src
sys.path.insert(0, '.')

# Mock the tkinter module and its dependencies to run in a headless environment
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.font'] = MagicMock()

# Now that tkinter is mocked, we can safely import the linter function
from src.p.linter import lint_javascript

class TestLinter(unittest.TestCase):
    
    def test_linter_rules(self):
        # The test script containing all the issues our linter should find
        test_script = (
            "var x = 10; // use of var\n"
            "if (x == '10') { // use of ==\n"
            '    console.log("This is a very long line that should be flagged by the linter because it is over 80 characters long.");\n'
            "}\n"
            "function tooManyParams(a, b, c, d, e, f) { // too many parameters\n"
            "    // empty function\n"
            "}\n"
            "// This line has trailing whitespace.    \n"
            "let y = 20 // missing semicolon\n"
        )
        
        # Configure the mock script_text widget
        script_text_mock = MagicMock()
        script_text_mock.get.return_value = test_script
        
        # Call the linting function directly, passing the mock widget
        lint_javascript(script_text_mock)

        # Get the list of calls to tag_add
        calls = script_text_mock.tag_add.call_args_list
        
        # Extract the names of the tags that were added
        added_tags = {call.args[0] for call in calls}
        
        # Define the set of tags we expect to have been added
        expected_tags = {
            "use_of_var",
            "use_of_double_equals",
            "long_line",
            "many_parameters",
            "trailing_whitespace",
            "missing_semicolon"
        }
        
        # Assert that the set of added tags is exactly what we expect
        self.assertEqual(added_tags, expected_tags)

if __name__ == '__main__':
    unittest.main()
