import unittest
import sys
import os
import tkinter as tk
from unittest.mock import patch, MagicMock

# Add src/p to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'p'))

from components import SymbolOutlinePanel, TodoExplorerPanel


class TestSymbolOutlinePanel(unittest.TestCase):
    """Unit tests for SymbolOutlinePanel class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.panel = SymbolOutlinePanel(self.root)
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    def test_panel_initialization(self):
        """Test that panel initializes correctly"""
        self.assertIsInstance(self.panel, SymbolOutlinePanel)
        self.assertIsInstance(self.panel, tk.Frame)
        
    def test_update_symbols_python_functions(self):
        """Test updating symbols with Python functions"""
        python_code = """
def function_one():
    pass

def function_two(param1, param2):
    return param1 + param2

class MyClass:
    def method_one(self):
        pass
"""
        
        self.panel.update_symbols(python_code, 'python')
        
        # Get items from listbox
        items = [self.panel.listbox.get(i) for i in range(self.panel.listbox.size())]
        
        self.assertIn('function_one', items)
        self.assertIn('function_two', items)
        self.assertIn('MyClass', items)
        self.assertIn('method_one', items)
        
    def test_update_symbols_javascript_functions(self):
        """Test updating symbols with JavaScript functions"""
        javascript_code = """
function regularFunction() {
    return true;
}

class TestClass {
    constructor() {
        this.value = 0;
    }
}

const arrowFunction = () => {
    console.log('arrow function');
};
"""
        
        self.panel.update_symbols(javascript_code, 'javascript')
        
        # Get items from listbox
        items = [self.panel.listbox.get(i) for i in range(self.panel.listbox.size())]
        
        self.assertIn('regularFunction', items)
        self.assertIn('TestClass', items)
        
    def test_update_symbols_cpp_functions(self):
        """Test updating symbols with C++ functions"""
        cpp_code = """
class Rectangle {
private:
    int width, height;
public:
    Rectangle(int w, int h);
    int area();
};

struct Point {
    int x, y;
};

int calculateDistance(Point p1, Point p2) {
    return 0;
}
"""
        
        self.panel.update_symbols(cpp_code, 'cpp')
        
        # Get items from listbox
        items = [self.panel.listbox.get(i) for i in range(self.panel.listbox.size())]
        
        self.assertIn('Rectangle', items)
        self.assertIn('Point', items)
        
    def test_update_symbols_unsupported_language(self):
        """Test updating symbols with unsupported language"""
        code = "some code in unknown language"
        
        self.panel.update_symbols(code, 'unknown')
        
        # Should have no items
        self.assertEqual(self.panel.listbox.size(), 0)
        
    def test_update_symbols_empty_code(self):
        """Test updating symbols with empty code"""
        self.panel.update_symbols("", 'python')
        
        # Should have no items
        self.assertEqual(self.panel.listbox.size(), 0)


class TestTodoExplorerPanel(unittest.TestCase):
    """Unit tests for TodoExplorerPanel class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.panel = TodoExplorerPanel(self.root)
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    def test_panel_initialization(self):
        """Test that panel initializes correctly"""
        self.assertIsInstance(self.panel, TodoExplorerPanel)
        self.assertIsInstance(self.panel, tk.Frame)
        
    def test_update_todos_python_comments(self):
        """Test updating TODOs with Python comments"""
        python_code = """
# TODO: Implement this function
def incomplete_function():
    pass

# FIXME: This calculation is wrong
def calculate_something():
    return 42  # TODO: Use correct formula

# This is just a regular comment
def working_function():
    return True
"""
        
        self.panel.update_todos(python_code, 'python')
        
        # Get items from listbox
        items = [self.panel.listbox.get(i) for i in range(self.panel.listbox.size())]
        
        # Should find TODO and FIXME items with line numbers
        todo_items = [item for item in items if 'TODO' in item.upper()]
        fixme_items = [item for item in items if 'FIXME' in item.upper()]
        
        self.assertEqual(len(todo_items), 2)  # Two TODO items
        self.assertEqual(len(fixme_items), 1)  # One FIXME item
        
        # Check line numbers are included
        self.assertTrue(any('2:' in item for item in items))  # Line 2
        self.assertTrue(any('6:' in item for item in items))  # Line 6
        self.assertTrue(any('8:' in item for item in items))  # Line 8
        
    def test_update_todos_javascript_comments(self):
        """Test updating TODOs with JavaScript comments"""
        javascript_code = """
// TODO: Add error handling
function processData(data) {
    return data;
}

// FIXME: Memory leak here
function createObjects() {
    // TODO: Optimize this loop
    for (let i = 0; i < 1000; i++) {
        // Regular comment
        console.log(i);
    }
}
"""
        
        self.panel.update_todos(javascript_code, 'javascript')
        
        # Get items from listbox
        items = [self.panel.listbox.get(i) for i in range(self.panel.listbox.size())]
        
        todo_items = [item for item in items if 'TODO' in item.upper()]
        fixme_items = [item for item in items if 'FIXME' in item.upper()]
        
        self.assertEqual(len(todo_items), 2)  # Two TODO items
        self.assertEqual(len(fixme_items), 1)  # One FIXME item
        
    def test_update_todos_cpp_comments(self):
        """Test updating TODOs with C++ comments"""
        cpp_code = """
// TODO: Implement proper error handling
class Calculator {
private:
    int value;
    
public:
    // FIXME: This constructor doesn't validate input
    Calculator(int v) : value(v) {}
    
    int getValue() {
        // TODO: Add bounds checking
        return value;
    }
};
"""
        
        self.panel.update_todos(cpp_code, 'cpp')
        
        # Get items from listbox
        items = [self.panel.listbox.get(i) for i in range(self.panel.listbox.size())]
        
        todo_items = [item for item in items if 'TODO' in item.upper()]
        fixme_items = [item for item in items if 'FIXME' in item.upper()]
        
        self.assertEqual(len(todo_items), 2)  # Two TODO items
        self.assertEqual(len(fixme_items), 1)  # One FIXME item
        
    def test_update_todos_case_insensitive(self):
        """Test that TODO/FIXME detection is case insensitive"""
        code = """
# todo: lowercase todo
# FIXME: uppercase fixme
# Todo: mixed case todo
# fixme: lowercase fixme
"""
        
        self.panel.update_todos(code, 'python')
        
        # Get items from listbox
        items = [self.panel.listbox.get(i) for i in range(self.panel.listbox.size())]
        
        self.assertEqual(len(items), 4)  # Should find all variants
        
    def test_update_todos_unsupported_language(self):
        """Test updating TODOs with unsupported language"""
        code = "// TODO: This should not be found"
        
        self.panel.update_todos(code, 'unknown')
        
        # Should have no items
        self.assertEqual(self.panel.listbox.size(), 0)
        
    def test_update_todos_empty_code(self):
        """Test updating TODOs with empty code"""
        self.panel.update_todos("", 'python')
        
        # Should have no items
        self.assertEqual(self.panel.listbox.size(), 0)


class TestComponentsBDD(unittest.TestCase):
    """BDD-style tests for Components"""
    
    def setUp(self):
        self.root = tk.Tk()
        
    def tearDown(self):
        self.root.destroy()
        
    def test_given_python_code_when_symbols_updated_then_extracts_functions_and_classes(self):
        """
        Given: Python code with functions and classes
        When: Symbols are updated
        Then: Extracts function and class names
        """
        # Given
        panel = SymbolOutlinePanel(self.root)
        python_code = """
def helper_function():
    pass

class DataProcessor:
    def __init__(self):
        self.data = []
        
    def process(self):
        return self.data
"""
        
        # When
        panel.update_symbols(python_code, 'python')
        
        # Then
        items = [panel.listbox.get(i) for i in range(panel.listbox.size())]
        self.assertIn('helper_function', items)
        self.assertIn('DataProcessor', items)
        self.assertIn('__init__', items)
        self.assertIn('process', items)
        
    def test_given_code_with_todos_when_todos_updated_then_extracts_todo_comments(self):
        """
        Given: Code with TODO and FIXME comments
        When: TODOs are updated
        Then: Extracts TODO/FIXME comments with line numbers
        """
        # Given
        panel = TodoExplorerPanel(self.root)
        code_with_todos = """
def function_one():
    # TODO: Implement validation
    pass

def function_two():
    # FIXME: Handle edge case
    return None
"""
        
        # When
        panel.update_todos(code_with_todos, 'python')
        
        # Then
        items = [panel.listbox.get(i) for i in range(panel.listbox.size())]
        self.assertEqual(len(items), 2)
        
        # Check that line numbers and content are included
        todo_item = next(item for item in items if 'TODO' in item)
        fixme_item = next(item for item in items if 'FIXME' in item)
        
        self.assertIn('3:', todo_item)  # Line number
        self.assertIn('Implement validation', todo_item)
        self.assertIn('6:', fixme_item)  # Line number
        self.assertIn('Handle edge case', fixme_item)
        
    def test_given_mixed_language_code_when_symbols_updated_then_extracts_appropriate_symbols(self):
        """
        Given: Code in different languages
        When: Symbols are updated for each language
        Then: Extracts appropriate symbols for each language
        """
        # Given
        symbol_panel = SymbolOutlinePanel(self.root)
        
        # JavaScript code
        js_code = """
function jsFunction() {
    return true;
}

class JSClass {
    constructor() {}
}
"""
        
        # C++ code
        cpp_code = """
class CppClass {
public:
    void method();
};

struct CppStruct {
    int value;
};
"""
        
        # When & Then - JavaScript
        symbol_panel.update_symbols(js_code, 'javascript')
        js_items = [symbol_panel.listbox.get(i) for i in range(symbol_panel.listbox.size())]
        self.assertIn('jsFunction', js_items)
        self.assertIn('JSClass', js_items)
        
        # When & Then - C++
        symbol_panel.update_symbols(cpp_code, 'cpp')
        cpp_items = [symbol_panel.listbox.get(i) for i in range(symbol_panel.listbox.size())]
        self.assertIn('CppClass', cpp_items)
        self.assertIn('CppStruct', cpp_items)


class TestComponentsIntegration(unittest.TestCase):
    """Integration tests for Components"""
    
    def setUp(self):
        self.root = tk.Tk()
        
    def tearDown(self):
        self.root.destroy()
        
    def test_symbol_and_todo_panels_work_together(self):
        """Test that symbol and TODO panels can work with the same code"""
        symbol_panel = SymbolOutlinePanel(self.root)
        todo_panel = TodoExplorerPanel(self.root)
        
        code = """
# TODO: Add documentation
def calculate_area(radius):
    # FIXME: Validate input
    return 3.14159 * radius * radius

class Circle:
    def __init__(self, radius):
        # TODO: Add radius validation
        self.radius = radius
        
    def area(self):
        return calculate_area(self.radius)
"""
        
        # Update both panels
        symbol_panel.update_symbols(code, 'python')
        todo_panel.update_todos(code, 'python')
        
        # Check symbols
        symbol_items = [symbol_panel.listbox.get(i) for i in range(symbol_panel.listbox.size())]
        self.assertIn('calculate_area', symbol_items)
        self.assertIn('Circle', symbol_items)
        self.assertIn('__init__', symbol_items)
        self.assertIn('area', symbol_items)
        
        # Check TODOs
        todo_items = [todo_panel.listbox.get(i) for i in range(todo_panel.listbox.size())]
        self.assertEqual(len(todo_items), 3)  # Three TODO/FIXME items
        
        # Verify content
        todo_contents = ' '.join(todo_items)
        self.assertIn('Add documentation', todo_contents)
        self.assertIn('Validate input', todo_contents)
        self.assertIn('Add radius validation', todo_contents)


if __name__ == '__main__':
    unittest.main()
