# Quanta Haba - Detailed Implementation Plan

This document provides a step-by-step plan for developing the `quanta_haba` demo application.

### Phase 1: Project Setup & Dependencies

1.  **Initialize Project Structure**:
    - Create the root directory: `quanta_haba/`.
    - Create a main application file: `quanta_haba/main.py`.
    - Create a `requirements.txt` file in the root.

2.  **Define Dependencies**:
    - Add the following line to `requirements.txt` to include the language model package:
      ```
      -e git+https://github.com/drtamarojgreen/quanta_tissu
      ```

3.  **Create Default Prompt File**:
    - Create a file named `default_prompt.txt` in the root.
    - Populate it with the initial task list:
      ```
      TODO: Generate project title
      TODO: Suggest 3 features
      TODO: Write short summary
      ```

### Phase 2: UI Scaffolding (Tkinter)

1.  **Main Application Window**:
    - In `main.py`, create a main class `QuantaHabaApp` that inherits from `tk.Tk`.
    - Set the window title to "Quanta Haba Editor".
    - Configure the main window geometry.

2.  **Layout Panels**:
    - Create three `tk.Frame` widgets for the left, right, and bottom panels.
    - Use `pack()` or `grid()` to arrange them in the desired layout. A `PanedWindow` could also be used for resizable panels.

3.  **Create Widgets**:
    - **Left Panel (Editor)**: Add a `tk.Text` widget.
    - **Right Panel (Dashboard)**: Add a `tk.Text` widget (or a `Frame` to hold future widgets).
    - **Bottom Panel (Console)**: Add a `tk.Text` widget.
    - Add scrollbars to all `Text` widgets.

### Phase 3: Core Workflow Logic

1.  **File Loading**:
    - Implement a method `load_prompt_file()` that reads the content of `default_prompt.txt` and inserts it into the editor Text widget on application startup.

2.  **State Management**:
    - Create a simple list or dictionary to hold the status of each line/task (e.g., `['todo', 'todo', 'todo']`).
    - Implement a method `find_next_task()` which iterates through the state manager to find the index of the next task marked 'todo'. It should return the line number (or `None` if all are done).

3.  **Line Highlighting**:
    - Implement a method `highlight_line(line_number)` that applies a visual tag (e.g., a background color) to the specified line in the editor Text widget.
    - Implement a method to remove the highlight from the previous line.

### Phase 4: Language Model Integration & Automation

1.  **Main Workflow Loop**:
    - Create a method `process_workflow_step()`. This will be the heart of the automation.

2.  **Workflow Step Execution**:
    - Inside `process_workflow_step()`:
      a. Call `find_next_task()` to get the current task's line number.
      b. If no task is found, stop the loop.
      c. Get the text content of that line from the editor widget.
      d. **Call Language Model**: `response = quanta_tissu.generate(task_text)`.
      e. **Call Toolkit (Stub)**: `toolkit_result = f"Toolkit processed: {response}"`.
      f. **Log to Console**: Append the prompt, response, and toolkit result to the console Text widget.
      g. **Update Dashboard**: Append a formatted summary (`✓ Task → Response`) to the dashboard Text widget.
      h. **Update Editor**: Modify the line in the editor widget, changing `TODO:` to `DONE:`.
      i. **Update State**: Update the task's status to 'done' in the state manager.
      j. **Schedule Next Step**: Use `root.after(1000, self.process_workflow_step)` to pause for a second and then trigger the next iteration, creating a visible, step-by-step flow.

3.  **Initiate Workflow**:
    - After the UI is initialized and the prompt file is loaded, make an initial call to `process_workflow_step()` to kick off the automation.

### Phase 5: Refinement and Finalization

1.  **Error Handling**: Add `try...except` blocks around the language model call to handle potential API errors.
2.  **UI Polish**: Adjust fonts, colors, and padding to improve readability.
3.  **Read-only Widgets**: Set the dashboard and console Text widgets to a disabled state so the user cannot edit them.
4.  **Code Documentation**: Add docstrings and comments to explain the functionality of each method.
5.  **Graceful Exit**: Ensure the application closes cleanly.
