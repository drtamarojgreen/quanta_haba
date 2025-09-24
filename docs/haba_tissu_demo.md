# Quanta Haba TISSLM C++ Demo Implementation

This document outlines the design and implementation of a C++ demonstration application for the Quanta Haba TISSLM model. The C++ demo is designed to mirror the functionality of the existing Python editor demo, providing a familiar user experience while showcasing the capabilities of the C++ `quanta_tissu` library.

## 1. Overview

The primary goal of this demo is to showcase the integration of the `quanta_tissu` C++ library into a native desktop application. The demo will feature a graphical user interface (GUI) that allows users to interact with the TISSLM model, providing prompts and viewing the generated output in real-time.

## 2. User Interface (UI)

The C++ demo will replicate the three-panel layout of the Python demo to ensure consistency and ease of use for existing users.

*   **Panel 1: Prompt Editor (Left)**
    *   A text area where users can load, edit, and write prompts.
    *   The demo will load a default prompt file (e.g., `default_prompt.txt`) on startup.
    *   The editor will highlight the currently processing `TODO:` task.

*   **Panel 2: Dashboard (Top-Right)**
    *   A read-only display area that shows the final, formatted output from the model.
    *   This panel will be updated as each `TODO:` task is completed.

*   **Panel 3: Console (Bottom-Right)**
    *   A log area that displays real-time status updates, model outputs, and any errors that occur during processing.
    *   This provides transparency into the model's operations.

## 3. Launching the Demo

Similar to the Python implementation, the C++ demo will be launched from the main editor application.

*   A **"Quanta C++ Demo"** button will be added to the main toolbar.
*   Clicking this button will launch the demo in a separate, self-contained window, ensuring that the main editor's functionality remains unaffected.

## 4. C++ Backend Implementation

The core of the demo will be the C++ backend, which will handle the logic for interacting with the `quanta_tissu` library.

### Key Components:

*   **`QuantaDemoWindow` Class:** A class responsible for managing the GUI, including the three panels, window state, and user interactions.
*   **`TissuModel` Class:** A wrapper class that handles the integration with the `quanta_tissu` C++ library. This class will be responsible for:
    *   Loading the TISSLM model and tokenizer from specified paths.
    *   Providing a simple interface for text generation (e.g., a `generate` method).
    *   Managing model resources.

### Workflow:

1.  **Initialization:** When the demo window is launched, it will instantiate the `TissuModel` class.
2.  **Model Loading:** The `TissuModel` class will attempt to load the `quanta_tissu` model and tokenizer from predefined or user-specified paths.
3.  **Prompt Processing:** The application will read the `default_prompt.txt` file and process each `TODO:` task sequentially.
4.  **Text Generation:** For each task, the application will call the `TissuModel::generate` method, passing the prompt text.
5.  **UI Updates:** The generated text will be displayed in the Console panel, and the formatted output will be shown in the Dashboard.

## 5. Error Handling

The C++ demo will include robust error handling to ensure a smooth user experience, even when dependencies are missing.

*   **Library Not Found:** If the `quanta_tissu` library is not found, the application will display an error message in the Console and fall back to a "stub" mode, where it will return pre-defined responses. This ensures the UI remains interactive.
*   **Model/Tokenizer Not Found:** If the model or tokenizer files are not found at the specified paths, the application will log an error and enter stub mode.
*   **Invalid Prompts:** The application will handle malformed or empty prompts gracefully.

By following this design, the C++ demo will provide a powerful and intuitive way to showcase the capabilities of the `quanta_tissu` C++ library, while maintaining a consistent user experience with the existing Python demo.