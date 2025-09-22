#include <iostream>
#include <string>
#include <vector>
#include <regex>

/**
 * @brief Enhancement #15: `printf` Format String Checker.
 *
 * This function uses regex to approximate checking a printf statement.
 * It counts the number of format specifiers and compares it to the number of arguments.
 * Note: This is a simplified implementation for demonstration. It doesn't handle
 * all edge cases (e.g., commas within arguments).
 *
 * @param printf_statement A string containing a C-style printf statement.
 * @return true if the number of specifiers matches the argument count, false otherwise.
 */
bool checkPrintfFormat(const std::string& printf_statement) {
    // 1. Extract the format string literal itself.
    std::smatch format_match;
    // This regex captures the content between the quotes of printf("...").
    std::regex format_regex(R"(printf\s*\(\s*\"((?:\\\"|[^"])*)\")");
    if (!std::regex_search(printf_statement, format_match, format_regex) || format_match.size() < 2) {
        return true; // Not a standard printf call we can analyze, assume it's OK.
    }
    std::string format_string = format_match[1].str();

    // 2. Count format specifiers (e.g., %d, %s), ignoring escaped '%%'.
    // This regex finds a '%' that is not followed by another '%'.
    std::regex specifier_regex(R"(%([^%]))");
    auto specifiers_begin = std::sregex_iterator(format_string.begin(), format_string.end(), specifier_regex);
    auto specifiers_end = std::sregex_iterator();
    long specifier_count = std::distance(specifiers_begin, specifiers_end);

    // 3. Extract the arguments part of the string.
    std::smatch args_match;
    // This regex captures the part after the format string and comma.
    std::regex args_regex(R"(printf\s*\(\s*\".*?\"\s*,\s*(.*)\s*\)\s*;)");
    if (!std::regex_search(printf_statement, args_match, args_regex) || args_match.size() < 2) {
        // No arguments found after the format string.
        return (specifier_count == 0);
    }
    std::string args_string = args_match[1].str();

    // If the captured group is empty, there are no arguments.
    if (args_string.empty()) {
        return (specifier_count == 0);
    }

    // 4. Count the arguments by counting the commas.
    long arg_count = 1;
    for (char c : args_string) {
        if (c == ',') {
            arg_count++;
        }
    }

    return specifier_count == arg_count;
}

/**
 * @brief Enhancement #42: Trailing Whitespace Highlighter.
 *
 * This function checks if a given line of text has trailing whitespace.
 *
 * @param line The line of text to check.
 * @return true if trailing whitespace is found, false otherwise.
 */
bool hasTrailingWhitespace(const std::string& line) {
    // Regex to find one or more whitespace characters at the end of a string.
    std::regex trailing_ws_regex(R"(\s+$)");
    return std::regex_search(line, trailing_ws_regex);
}

/**
 * @brief Enhancement #41: Cyclomatic Complexity Hinting.
 *
 * Approximates the cyclomatic complexity of a function's code.
 * It does this by counting branching keywords (if, for, while, case)
 * and logical operators (&&, ||). The complexity is 1 + this count.
 *
 * @param function_code A string containing the body of a C++ function.
 * @return The calculated cyclomatic complexity score.
 */
int calculateCyclomaticComplexity(const std::string& function_code) {
    // Regex to find all branching keywords and operators
    std::regex branching_regex(R"(\b(if|for|while|case|else if)\b|(&&|\|\|))");

    auto words_begin = std::sregex_iterator(function_code.begin(), function_code.end(), branching_regex);
    auto words_end = std::sregex_iterator();

    // The complexity is 1 (for the function entry) + the number of branches.
    return 1 + std::distance(words_begin, words_end);
}

/**
 * @brief Enhancement #44: Unused Variable Highlighting.
 *
 * Performs a simple static analysis to find unused local variables in a function.
 * Note: This is a simplified implementation. It doesn't handle scope correctly
 * (e.g., variables in inner blocks) and has a naive definition of "use".
 *
 * @param function_code A string containing the body of a C++ function.
 * @return A vector of strings, where each string is an unused variable name.
 */
std::vector<std::string> findUnusedVariables(const std::string& function_code) {
    std::vector<std::string> unused_vars;

    // This regex finds variable declarations for simple types.
    std::regex decl_regex(R"(\b(int|float|double|char|bool|std::string)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(;|=))");

    auto decl_begin = std::sregex_iterator(function_code.begin(), function_code.end(), decl_regex);
    auto decl_end = std::sregex_iterator();

    for (std::sregex_iterator i = decl_begin; i != decl_end; ++i) {
        std::smatch match = *i;
        std::string var_name = match[2];

        // Heuristic: Count occurrences. If only 1, it's the declaration and thus unused.
        std::regex use_regex(R"(\b)" + var_name + R"(\b)");

        auto use_begin = std::sregex_iterator(function_code.begin(), function_code.end(), use_regex);
        auto use_end = std::sregex_iterator();

        if (std::distance(use_begin, use_end) <= 1) {
            unused_vars.push_back(var_name);
        }
    }

    return unused_vars;
}

int main() {
    std::cout << "C++ GUI Editor Placeholder\n";
    std::cout << "--- --- --- ---\n\n";
    std::cout << "Demonstrating Enhancement #15: printf Format String Checker.\n\n";

    // Test cases for printf checker
    std::string valid_statement = "printf(\"Hello %s, your ID is %d!\", name, id);";
    std::string invalid_statement_too_many = "printf(\"Error on line %d\", lineNumber, file);";

    std::cout << "Testing statement: \"" << valid_statement << "\"\n";
    std::cout << "  -> Expected: OK, Got: " << (checkPrintfFormat(valid_statement) ? "OK" : "MISMATCH") << "\n\n";

    std::cout << "Testing statement: \"" << invalid_statement_too_many << "\"\n";
    std::cout << "  -> Expected: MISMATCH, Got: " << (checkPrintfFormat(invalid_statement_too_many) ? "OK" : "MISMATCH") << "\n\n";

    std::cout << "\n--- --- --- ---\n\n";
    std::cout << "Demonstrating Enhancement #42: Trailing Whitespace Highlighter.\n\n";

    // Test cases for whitespace
    std::string clean_line = "int x = 5;";
    std::string dirty_line = "int y = 10;  "; // Note the trailing spaces

    std::cout << "Testing line: \"" << clean_line << "\"\n";
    std::cout << "  -> Expected: NO, Got: " << (hasTrailingWhitespace(clean_line) ? "YES" : "NO") << "\n\n";

    std::cout << "Testing line: \"" << dirty_line << "\"\n";
    std::cout << "  -> Expected: YES, Got: " << (hasTrailingWhitespace(dirty_line) ? "YES" : "NO") << "\n\n";

    std::cout << "\n--- --- --- ---\n\n";
    std::cout << "Demonstrating Enhancement #41: Cyclomatic Complexity Hinting.\n\n";

    // Test case for cyclomatic complexity
    std::string sample_function_complexity = R"(
        void process_data(int data) {
            if (data > 10) { for (int i = 0; i < data; ++i) { if (i % 2 == 0 && data != 0) { std::cout << "Even"; } } } else if (data > 5 || data < 0) { std::cout << "Middle"; }
        }
    )";
    int complexity = calculateCyclomaticComplexity(sample_function_complexity);
    std::cout << "Analyzing sample function for complexity...\n";
    std::cout << "  -> Calculated Cyclomatic Complexity: " << complexity << " (Expected: 7)\n\n";

    std::cout << "\n--- --- --- ---\n\n";
    std::cout << "Demonstrating Enhancement #44: Unused Variable Highlighting.\n\n";

    // Test case for unused variable analysis
    std::string func_with_vars = R"(
        void process_values() {
            int used_var = 5;
            int unused_var = 10;
            std::string message = "Hello";
            bool is_active;
            if (used_var > 0) {
                std::cout << message;
            }
        }
    )";

    std::vector<std::string> unused = findUnusedVariables(func_with_vars);
    std::cout << "Analyzing sample function for unused variables...\n";
    std::cout << "  -> Found " << unused.size() << " unused variables (Expected: 2):\n";
    for (const auto& var : unused) {
        std::cout << "    - " << var << "\n";
    }
    std::cout << "\n";

    return 0;
}

