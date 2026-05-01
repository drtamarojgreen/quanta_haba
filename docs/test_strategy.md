# QuantaHaba Testing Strategy

## 1. Introduction

This document outlines the comprehensive testing strategy for the QuantaHaba project, ensuring the reliability and quality of all its components. It is a living document, intended to evolve with the project.

## 2. Guiding Principles

- **Automation First**: We prioritize automated testing for efficiency and repeatability.
- **The Test Pyramid**: Our strategy relies on a strong foundation of unit tests, complemented by integration and E2E tests.
- **Clarity Through Behavior**: We leverage Behavior-Driven Development (BDD) to ensure our tests are clear, tied to user requirements, and serve as living documentation.
- **Shift-Left Testing**: Quality is a shared responsibility, with developers integrating testing early and often.

## 3. Testing Levels and Methodologies

### 3.1. Unit Testing
- **Objective**: To verify the smallest testable parts of the application (a single function or class) in isolation.
- **Implementation**:
    - **C++**: A lightweight, custom C++ test framework (`tests/c/simple_test_framework.h`).
    - **Python**: The standard `unittest` framework and `unittest.mock` library.

### 3.2. Behavior-Driven Development (BDD): A Comprehensive Guide

#### 3.2.1. What is BDD? The Core Philosophy
Behavior-Driven Development is a software development methodology that evolved from Test-Driven Development (TDD). Its primary goal is **not just to test code, but to foster collaboration and create a shared understanding** among all project stakeholders—including developers, QA engineers, product managers, and business analysts.

At its heart, BDD is a conversation. It uses structured, natural language to describe a feature's desired behavior from the user's perspective. This process helps to eliminate ambiguity and ensures that what is built is what is actually needed.

#### 3.2.2. Our "Lite" BDD Implementation
To maximize clarity without introducing unnecessary complexity or dependencies (like `Behave` or `pytest-bdd`), this project adopts a **"BDD-style" testing approach within the standard Python `unittest` framework**.

Here's how it works:
1.  **Specification in Docstrings**: The behavior of a feature is described in a test method's docstring using the Gherkin `Given-When-Then` syntax. This docstring becomes the official, human-readable specification for that piece of behavior.
2.  **Implementation in Code**: The body of the test method implements the specification described in the docstring. The code directly maps to the `Given`, `When`, and `Then` steps.

This approach gives us the primary benefits of BDD—clarity and documentation—while keeping our test suite simple, fast, and easy to maintain.

#### 3.2.3. A Gallery of BDD Scenarios

The following examples from the codebase illustrate how we apply our BDD style to different kinds of tests.

---

**Example 1: High-Level User Interaction (CLI File Loading)**

This test describes a core feature of the command-line interface: loading a file at startup.

*   **The Specification (Docstring)**:
    ```python
    """
    Feature: CLI File Loading
    Scenario: The user provides a valid file path as an argument.
    Given the application is started with a valid file path argument
    When the main function is executed
    Then the file's content should be loaded into the editor's raw text widget
    And the preview should be rendered.
    """
    ```

*   **The Implementation (Test Code)**:
    ```python
    # We patch dependencies to isolate our test.
    @patch('sys.argv')
    @patch('p.editor.HabaEditor')
    def test_loading_file_from_cli(self, mock_haba_editor_class, mock_argv):
        # GIVEN the application is started with a valid file path argument:
        # We create a mock file on the filesystem for the test.
        # We manipulate sys.argv to simulate the user's command.
        mock_argv.__getitem__.side_effect = lambda x: ['editor.py', self.DUMMY_FILE_PATH][x]
        mock_argv.__len__.return_value = 2
        mock_editor_instance = MagicMock()
        mock_haba_editor_class.return_value = mock_editor_instance

        # WHEN the main function is executed:
        editor.main()

        # THEN the file's content should be loaded...
        # We assert that the editor's text widget was cleared and then filled with the file content.
        mock_editor_instance.raw_text.delete.assert_called_with("1.0", "end")
        mock_editor_instance.raw_text.insert.assert_called_with("1.0", self.DUMMY_FILE_CONTENT)

        # AND the preview should be rendered.
        # We assert that the render function was called exactly once.
        mock_editor_instance.render_preview.assert_called_once()
    ```

---

**Example 2: Detailed Technical Rule (JavaScript Linter)**

This test describes a specific, technical rule within the editor's linter.

*   **The Specification (Docstring)**:
    ```python
    """
    Feature: JavaScript Linter
    Scenario: A line contains trailing whitespace.
    Given a line of code with trailing spaces
    When the linter is run on that line
    Then the linter should identify and tag the exact range of the trailing whitespace.
    """
    ```

*   **The Implementation (Test Code)**:
    ```python
    def test_linting_for_trailing_whitespace(self):
        # GIVEN a line of code with trailing spaces:
        # We prepare the input string and mock the editor's text widget.
        script_content = "var name = 'Haba';  "
        self.app.script_text.get.return_value = script_content
        self.app.script_text.tag_add = MagicMock() # This will record calls to it.

        # WHEN the linter is run on that line:
        editor.lint_javascript_text(self.app.script_text)

        # THEN the linter should identify and tag the exact range...
        # We assert that the 'tag_add' method was called with the correct tag name ('trailing_whitespace')
        # and the precise start ('1.20') and end ('1.22') positions of the whitespace.
        self.app.script_text.tag_add.assert_any_call("trailing_whitespace", "1.20", "1.22")
    ```

---

**Example 3: Handling User Error (CLI)**

This test describes how the system should behave when the user makes a mistake.

*   **The Specification (Docstring)**:
    ```python
    """
    Feature: CLI File Loading
    Scenario: The user provides a path to a non-existent file.
    Given the application is started with a path to a file that does not exist
    When the main function is executed
    Then a warning message should be shown to the user
    And the editor should not attempt to load any content.
    """
    ```

*   **The Implementation (Test Code)**:
    ```python
    @patch('p.editor.messagebox') # We patch the message box to check if it's called.
    @patch('p.editor.HabaEditor')
    def test_loading_nonexistent_file_from_cli(self, mock_haba_editor_class, mock_messagebox):
        # GIVEN the application is started with a path to a file that does not exist:
        # We simulate the CLI arguments with a path we know is invalid.
        # (Setup for sys.argv is similar to the first example)

        # WHEN the main function is executed:
        editor.main()

        # THEN a warning message should be shown to the user:
        # We assert that the showwarning function was called with the expected title and message.
        mock_messagebox.showwarning.assert_called_with("File Not Found", "The specified file does not exist...")

        # AND the editor should not attempt to load any content.
        # We get the mock editor instance and assert its 'insert' method was never called.
        mock_editor_instance = mock_haba_editor_class.return_value
        mock_editor_instance.raw_text.insert.assert_not_called()
    ```
---

### 3.3. Integration and End-to-End (E2E) Testing
- **Integration Testing**: Verifies that different components work together correctly (e.g., the C++ `haba-converter` interacting with the file system).
- **E2E Testing**: Tests the entire application flow from a user's perspective within the QuantaHaba web editor, using a tool like Playwright.

## 4. Finalizing the Strategy
This comprehensive BDD approach ensures that our tests are not just checks on the code, but are clear, maintainable, and serve as the ultimate documentation for the QuantaHaba project's behavior.
## 5. CDD Test Edge Cases and Failure Modes

This project includes CDD-style cards/facts under `tests/chai/cdd/`. To make these tests more robust and diagnostic, we should explicitly cover the following edge cases and failure classes.

### 5.1 Input and Fact Integrity Edge Cases

- Missing fact files in `CHAI_FACTS_DIR` (directory exists but specific `.facts` file absent).
- Corrupted fact entries (invalid delimiters, malformed key/value pairs, truncated lines).
- Empty fact files that still load successfully but produce false confidence.
- Duplicate fact keys where last-write-wins behavior may hide unintended overrides.
- UTF-8 and newline variance (`\n` vs `\r\n`) that can affect parser assumptions.

### 5.2 Parser and Contract Edge Cases

- Unterminated or nested `.haba` sections (e.g., malformed `[[SCRIPT]]` boundaries).
- Unexpected ordering of sections (script before content/style) and whether order is guaranteed.
- Excess whitespace/indentation around tokens and headers.
- Very large script/content blocks that stress memory assumptions.
- Presence of embedded markers inside string literals that should not terminate sections.

### 5.3 Runtime/Environment Failure Modes

- Build mismatch between test cards and implementation headers/sources.
- Relative include path breakage from Makefile execution in different working directories.
- Silent pass risk when a card binary exits 0 without asserting expected facts.
- Environment variable misconfiguration (`CHAI_FACTS_DIR` points to wrong location).
- Platform/compiler differences (GCC/Clang, libstdc++ variations) altering behavior.

### 5.4 Observability and Diagnosis Improvements

- Ensure each failed assertion prints: fact file, fact key, expected value, actual value.
- Include deterministic card execution ordering in test output.
- Emit summary counts: cards run, assertions run, pass/fail totals.
- Distinguish setup failure (fact load/build) from behavior failure (assert mismatch).

### 5.5 Recommended Additions to CDD Suite

1. Add dedicated “invalid facts” fixtures and assert clean failure messages.
2. Add cross-language parity facts to validate C++ and Python parser outputs match for canonical samples.
3. Add stress fixtures for long content/script sections.
4. Add CI job that runs `tests/chai/cdd/Makefile` with at least two fact directories: normal + intentionally broken.
5. Add regression facts for previously fixed parser bugs to prevent reintroduction.
