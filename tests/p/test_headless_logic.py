import unittest
import sys
import os

# Add src/p to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/p')))

from components import extract_symbols, extract_todos
from editor import analyze_javascript_line

class TestHeadlessLogic(unittest.TestCase):
    def test_extract_symbols_python(self):
        code = "def my_func():\n    pass\nclass MyClass:\n    pass"
        symbols = extract_symbols(code, 'python')
        self.assertEqual(len(symbols), 2)
        self.assertIn("my_func", symbols)
        self.assertIn("MyClass", symbols)

    def test_extract_todos_js(self):
        code = "// TODO: fix this\n/* FIXME: important */"
        todos = extract_todos(code, 'javascript')
        self.assertEqual(len(todos), 2)
        self.assertTrue(any("FIX THIS" in t.upper() for t in todos))
        self.assertTrue(any("IMPORTANT" in t.upper() for t in todos))

    def test_analyze_js_line_long(self):
        line = "a" * 81
        issues = analyze_javascript_line(line, 0)
        self.assertTrue(any(issue[0] == "long_line" for issue in issues))

    def test_analyze_js_line_var(self):
        line = "var x = 1;"
        issues = analyze_javascript_line(line, 0)
        self.assertTrue(any(issue[0] == "use_of_var" for issue in issues))

if __name__ == "__main__":
    unittest.main()
