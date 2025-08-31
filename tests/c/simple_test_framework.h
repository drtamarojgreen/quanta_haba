#ifndef SIMPLE_TEST_FRAMEWORK_H
#define SIMPLE_TEST_FRAMEWORK_H

#include <iostream>
#include <vector>
#include <string>
#include <functional>

// Simple assertion macros
#define ASSERT_TRUE(condition) \
    do { \
        if (!(condition)) { \
            std::cerr << "Assertion failed: " << #condition \
                      << " (File: " << __FILE__ << ", Line: " << __LINE__ << ")" << std::endl; \
            return false; \
        } \
    } while (0)

#define ASSERT_EQ(expected, actual) \
    do { \
        if (!((expected) == (actual))) { \
            std::cerr << "Assertion failed: Expected " << (expected) \
                      << ", got " << (actual) \
                      << " (File: " << __FILE__ << ", Line: " << __LINE__ << ")" << std::endl; \
            return false; \
        } \
    } while (0)

// Test case function pointer type
typedef bool (*TestFunction)();

// Test case structure
struct TestCase {
    std::string name;
    TestFunction func;
};

// Global vector to store test cases
std::vector<TestCase>* g_test_cases = nullptr;

// Function to add a test case
void add_test_case(const std::string& name, TestFunction func) {
    if (!g_test_cases) {
        g_test_cases = new std::vector<TestCase>();
    }
    g_test_cases->push_back({name, func});
}

// Function to run all tests
int run_all_tests() {
    if (!g_test_cases) {
        std::cout << "No tests found." << std::endl;
        return 0;
    }

    int passed_tests = 0;
    int failed_tests = 0;

    std::cout << "Running " << g_test_cases->size() << " tests..." << std::endl;

    for (const auto& test_case : *g_test_cases) {
        std::cout << "  Running " << test_case.name << "... ";
        if (test_case.func()) {
            std::cout << "PASSED" << std::endl;
            passed_tests++;
        } else {
            std::cout << "FAILED" << std::endl;
            failed_tests++;
        }
    }

    std::cout << "\nTest Results:" << std::endl;
    std::cout << "  Passed: " << passed_tests << std::endl;
    std::cout << "  Failed: " << failed_tests << std::endl;

    delete g_test_cases; // Clean up dynamically allocated vector
    g_test_cases = nullptr;

    return failed_tests;
}

#endif // SIMPLE_TEST_FRAMEWORK_H