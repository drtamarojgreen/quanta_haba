#!/usr/bin/env python3
"""
Comprehensive test runner for QuantaHaba Python implementation.
Runs all unit tests and BDD tests using only the unittest library.
"""

import unittest
import sys
import os
import time
from io import StringIO

# Add src/p to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'p'))

# Import all test modules
from test_haba_parser import TestHabaParser, TestHabaData, TestHabaParserBDD
from test_html_exporter import TestHtmlExporter, TestHtmlExporterBDD, TestHtmlExporterIntegration
from test_script_runner import TestScriptRunner, TestRunPythonScript, TestScriptRunnerBDD, TestScriptRunnerIntegration
from test_components import TestSymbolOutlinePanel, TestTodoExplorerPanel, TestComponentsBDD, TestComponentsIntegration

from test_quanta_demo import TestQuantaDemoWindow


class TestResults:
    """Helper class to collect and display test results"""
    
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.error_tests = 0
        self.skipped_tests = 0
        self.failures = []
        self.errors = []
        self.start_time = None
        self.end_time = None
        
    def start_timing(self):
        self.start_time = time.time()
        
    def end_timing(self):
        self.end_time = time.time()
        
    def get_duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0
        
    def add_result(self, result):
        self.total_tests += result.testsRun
        self.failed_tests += len(result.failures)
        self.error_tests += len(result.errors)
        self.skipped_tests += len(result.skipped)
        self.passed_tests = self.total_tests - self.failed_tests - self.error_tests - self.skipped_tests
        
        self.failures.extend(result.failures)
        self.errors.extend(result.errors)
        
    def print_summary(self):
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests Run: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Errors: {self.error_tests}")
        print(f"Skipped: {self.skipped_tests}")
        print(f"Duration: {self.get_duration():.2f} seconds")
        
        if self.failed_tests > 0 or self.error_tests > 0:
            print(f"\nSuccess Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        else:
            print(f"\nSuccess Rate: 100.0%")
            
        if self.failures:
            print(f"\nFAILURES ({len(self.failures)}):")
            print("-" * 50)
            for test, traceback in self.failures:
                print(f"FAIL: {test}")
                print(traceback)
                print("-" * 50)
                
        if self.errors:
            print(f"\nERRORS ({len(self.errors)}):")
            print("-" * 50)
            for test, traceback in self.errors:
                print(f"ERROR: {test}")
                print(traceback)
                print("-" * 50)


def run_test_suite(test_class, suite_name):
    """Run a specific test suite and return results"""
    print(f"\nRunning {suite_name}...")
    print("-" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(test_class)
    
    # Run tests with custom result collector
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    
    # Print individual test results
    output = stream.getvalue()
    print(output)
    
    return result


def run_all_tests():
    """Run all test suites and collect results"""
    print("QuantaHaba Python Implementation - Comprehensive Test Suite")
    print("=" * 70)
    print("Running all unit tests and BDD tests...")
    
    results = TestResults()
    results.start_timing()
    
    # Define all test suites
    test_suites = [
        # HabaParser Tests
        (TestHabaParser, "HabaParser Unit Tests"),
        (TestHabaData, "HabaData Unit Tests"),
        (TestHabaParserBDD, "HabaParser BDD Tests"),
        
        # HtmlExporter Tests
        (TestHtmlExporter, "HtmlExporter Unit Tests"),
        (TestHtmlExporterBDD, "HtmlExporter BDD Tests"),
        (TestHtmlExporterIntegration, "HtmlExporter Integration Tests"),
        
        # ScriptRunner Tests
        (TestScriptRunner, "ScriptRunner Unit Tests"),
        (TestRunPythonScript, "Python Script Runner Tests"),
        (TestScriptRunnerBDD, "ScriptRunner BDD Tests"),
        (TestScriptRunnerIntegration, "ScriptRunner Integration Tests"),
        
        # Components Tests
        (TestSymbolOutlinePanel, "SymbolOutlinePanel Unit Tests"),
        (TestTodoExplorerPanel, "TodoExplorerPanel Unit Tests"),
        (TestComponentsBDD, "Components BDD Tests"),
        (TestComponentsIntegration, "Components Integration Tests"),

        # Editor Tests
        (TestQuantaDemoWindow, "QuantaDemoWindow Unit Tests"),
    ]
    
    # Run each test suite
    for test_class, suite_name in test_suites:
        try:
            result = run_test_suite(test_class, suite_name)
            results.add_result(result)
        except Exception as e:
            print(f"ERROR: Failed to run {suite_name}: {e}")
            results.error_tests += 1
    
    results.end_timing()
    results.print_summary()
    
    return results


def run_specific_tests():
    """Run specific test categories"""
    print("QuantaHaba Python Implementation - Specific Test Categories")
    print("=" * 70)
    
    categories = {
        '1': ('Unit Tests', [TestHabaParser, TestHabaData, TestHtmlExporter,
                            TestScriptRunner, TestRunPythonScript,
                            TestSymbolOutlinePanel, TestTodoExplorerPanel,
                            TestQuantaDemoWindow]),
        '2': ('BDD Tests', [TestHabaParserBDD, TestHtmlExporterBDD,
                           TestScriptRunnerBDD, TestComponentsBDD]),
        '3': ('Integration Tests', [TestHtmlExporterIntegration, 
                                   TestScriptRunnerIntegration, 
                                   TestComponentsIntegration]),
        '4': ('Parser Tests Only', [TestHabaParser, TestHabaData, TestHabaParserBDD]),
        '5': ('Exporter Tests Only', [TestHtmlExporter, TestHtmlExporterBDD, 
                                     TestHtmlExporterIntegration]),
        '6': ('Script Runner Tests Only', [TestScriptRunner, TestRunPythonScript, 
                                          TestScriptRunnerBDD, TestScriptRunnerIntegration]),
        '7': ('Component Tests Only', [TestSymbolOutlinePanel, TestTodoExplorerPanel, 
                                      TestComponentsBDD, TestComponentsIntegration]),
    }
    
    print("Available test categories:")
    for key, (name, _) in categories.items():
        print(f"  {key}. {name}")
    print("  0. Run all tests")
    
    choice = input("\nSelect category (0-7): ").strip()
    
    if choice == '0':
        return run_all_tests()
    elif choice in categories:
        category_name, test_classes = categories[choice]
        print(f"\nRunning {category_name}...")
        
        results = TestResults()
        results.start_timing()
        
        for test_class in test_classes:
            result = run_test_suite(test_class, test_class.__name__)
            results.add_result(result)
            
        results.end_timing()
        results.print_summary()
        return results
    else:
        print("Invalid choice. Running all tests...")
        return run_all_tests()


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--interactive':
            return run_specific_tests()
        elif sys.argv[1] == '--help':
            print("QuantaHaba Test Runner")
            print("Usage:")
            print("  python run_all_tests.py           # Run all tests")
            print("  python run_all_tests.py --interactive  # Interactive mode")
            print("  python run_all_tests.py --help    # Show this help")
            return
    
    # Run all tests by default
    results = run_all_tests()
    
    # Exit with appropriate code
    if results.failed_tests > 0 or results.error_tests > 0:
        print(f"\nTests completed with {results.failed_tests + results.error_tests} failures/errors.")
        sys.exit(1)
    else:
        print(f"\nAll {results.total_tests} tests passed successfully!")
        sys.exit(0)


if __name__ == '__main__':
    main()
