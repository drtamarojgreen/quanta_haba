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

let anotherArrow = (a,b) => a + b;
var finalArrow = () => {};
"""
        
        self.panel.update_symbols(javascript_code, 'javascript')
        
        # Get items from listbox
        items = [self.panel.listbox.get(i) for i in range(self.panel.listbox.size())]
        
        self.assertIn('regularFunction', items)
        self.assertIn('TestClass', items)
        self.assertIn('arrowFunction', items)
        self.assertIn('anotherArrow', items)
        self.assertIn('finalArrow', items)

    def test_update_symbols_java_classes_and_methods(self):
        """Test updating symbols with Java classes and methods"""
        java_code = """
public class Animal {
    private String name;

    public Animal(String name) {
        this.name = name;
    }

    public void makeSound() {
        System.out.println("The animal makes a sound");
    }
}

interface Vehicle {
    void start();
    void stop();
}
"""

        self.panel.update_symbols(java_code, 'java')

        # Get items from listbox
        items = [self.panel.listbox.get(i) for i in range(self.panel.listbox.size())]

        self.assertIn('Animal', items)
        self.assertIn('Animal', items) # Constructor
        self.assertIn('makeSound', items)
        self.assertIn('Vehicle', items)
        self.assertIn('start', items)
        self.assertIn('stop', items)
        
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
    /* FIXME: This constructor
     * doesn't validate input */
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
        
        self.assertEqual(len(todo_items), 2)
        self.assertEqual(len(fixme_items), 1)
        self.assertTrue(any('7:' in item and 'This constructor' in item for item in items))

    def test_update_todos_java_comments(self):
        """Test updating TODOs with Java comments"""
        java_code = """
// TODO: Add a new feature
public class Main {
    /*
     * FIXME: Refactor this method.
     * It is too complex.
     */
    public void complexMethod() {
        // Just a regular comment
    }
}
"""
        self.panel.update_todos(java_code, 'java')
        items = [self.panel.listbox.get(i) for i in range(self.panel.listbox.size())]

        self.assertEqual(len(items), 2)
        self.assertTrue(any('2:' in item and 'Add a new feature' in item for item in items))
        self.assertTrue(any('4:' in item and 'Refactor this method' in item for item in items))
        
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
        code_with_todos = """def function_one():
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
        
        self.assertIn('2:', todo_item)  # Line number
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

    def test_given_java_code_with_symbols_and_todos_when_updated_then_extracts_all(self):
        """
        Given: Java code with classes, methods, and TODOs
        When: Symbols and TODOs are updated
        Then: Extracts all relevant items correctly
        """
        # Given
        symbol_panel = SymbolOutlinePanel(self.root)
        todo_panel = TodoExplorerPanel(self.root)
        java_code = """
public class BankAccount {
    // TODO: Add account number validation
    private double balance;

    public BankAccount(double initialBalance) {
        this.balance = initialBalance;
    }

    /* FIXME: This could be more efficient */
    public void deposit(double amount) {
        this.balance += amount;
    }
}
"""
        # When
        symbol_panel.update_symbols(java_code, 'java')
        todo_panel.update_todos(java_code, 'java')

        # Then - Symbols
        symbol_items = [symbol_panel.listbox.get(i) for i in range(symbol_panel.listbox.size())]
        self.assertIn('BankAccount', symbol_items)
        self.assertIn('BankAccount', symbol_items) # Constructor
        self.assertIn('deposit', symbol_items)

        # Then - TODOs
        todo_items = [todo_panel.listbox.get(i) for i in range(todo_panel.listbox.size())]
        self.assertEqual(len(todo_items), 2)
        self.assertTrue(any('3:' in item and 'Add account number validation' in item for item in todo_items))
        self.assertTrue(any('9:' in item and 'This could be more efficient' in item for item in todo_items))

    def test_given_unsupported_language_when_updated_then_no_items_extracted(self):
        """
        Given: An unsupported language
        When: Symbols and TODOs are updated
        Then: No items are extracted
        """
        # Given
        symbol_panel = SymbolOutlinePanel(self.root)
        todo_panel = TodoExplorerPanel(self.root)
        some_code = "let x = 1;"

        # When
        symbol_panel.update_symbols(some_code, 'rust')
        todo_panel.update_todos(some_code, 'rust')

        # Then
        self.assertEqual(symbol_panel.listbox.size(), 0)
        self.assertEqual(todo_panel.listbox.size(), 0)


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

    def test_symbol_and_todo_panels_work_together_java(self):
        """Test that symbol and TODO panels can work together with Java code"""
        symbol_panel = SymbolOutlinePanel(self.root)
        todo_panel = TodoExplorerPanel(self.root)

        java_code = """
package com.example;

// TODO: Add full Javadoc for this class
public class AdvancedProcessor {

    /* FIXME: This needs to be thread-safe */
    public List<String> process(List<String> data) {
        // TODO: Implement the actual processing logic
        return data;
    }

    interface ResultHandler {
        void onSuccess();
        void onError();
    }
}
"""
        # Update both panels
        symbol_panel.update_symbols(java_code, 'java')
        todo_panel.update_todos(java_code, 'java')

        # Check symbols
        symbol_items = [symbol_panel.listbox.get(i) for i in range(symbol_panel.listbox.size())]
        self.assertIn('AdvancedProcessor', symbol_items)
        self.assertIn('process', symbol_items)
        self.assertIn('ResultHandler', symbol_items)
        self.assertIn('onSuccess', symbol_items)
        self.assertIn('onError', symbol_items)

        # Check TODOs
        todo_items = [todo_panel.listbox.get(i) for i in range(todo_panel.listbox.size())]
        self.assertEqual(len(todo_items), 3)
        self.assertTrue(any('4:' in item and 'Add full Javadoc' in item for item in todo_items))
        self.assertTrue(any('7:' in item and 'This needs to be thread-safe' in item for item in todo_items))
        self.assertTrue(any('9:' in item and 'Implement the actual processing logic' in item for item in todo_items))


if __name__ == '__main__':
    unittest.main()