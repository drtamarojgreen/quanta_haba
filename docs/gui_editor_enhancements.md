# C++ GUI Editor Enhancements

This document summarizes the features and enhancements implemented in the `gui_editor.cpp` source file. Each feature is a self-contained static analysis or linting tool, demonstrated within the `main` function of the program.

---

## 1. `printf` Format String Checker (Enhancement #15)

### Description
This feature provides a basic linter to catch common errors in `printf` statements. It performs a simple check to ensure the number of format specifiers (e.g., `%d`, `%s`) in the format string matches the number of arguments supplied to the function.

### Implementation
A C++ function `checkPrintfFormat(const std::string&)` was added. It uses regex to:
1.  Extract the format string from a `printf` call.
2.  Count the number of valid format specifiers, correctly ignoring escaped `%%`.
3.  Count the number of arguments passed to the function.
4.  Compare the counts to find mismatches.

---

## 2. Trailing Whitespace Highlighter (Enhancement #42)

### Description
This is a simple code quality feature that detects unnecessary and invisible trailing whitespace at the end of a line of code.

### Implementation
A C++ function `hasTrailingWhitespace(const std::string&)` was added. It uses the regex `\s+$` to efficiently check for one or more whitespace characters at the end of a given string.

---

## 3. Cyclomatic Complexity Hinting (Enhancement #41)

### Description
This feature provides an approximation of the cyclomatic complexity for a given C++ function, a metric used to measure the complexity of a program's control flow. A higher number indicates a more complex function that may be difficult to test and maintain.

### Implementation
A C++ function `calculateCyclomaticComplexity(const std::string&)` was implemented. It approximates the complexity by:
1.  Starting with a base complexity of 1 for the function's entry point.
2.  Using regex to find and count all branching keywords (`if`, `for`, `while`, `case`, `else if`) and logical operators (`&&`, `||`).
3.  Summing the base and the count of branching points to produce the final complexity score.

---

## 4. Unused Variable Highlighting (Enhancement #44)

### Description
This static analysis feature helps identify and clean up dead code by detecting local variables that are declared but never used within a function's scope.

### Implementation
A C++ function `findUnusedVariables(const std::string&)` was added. It uses a simplified, regex-based approach to:
1.  Identify all local variable declarations for simple types within a string of code.
2.  For each declared variable, count its occurrences throughout the code.
3.  If a variable is only found once (at its declaration), it is marked as unused.
