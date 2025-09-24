# Quanta Haba - Possible Enhancements (No New Libraries)

This document lists 25 potential enhancements for the `quanta_haba` editor that can be implemented using only standard Python and the Tkinter library.

### UI/UX Enhancements

1.  **Theme Selection**: Add a menu option to switch between a user-selectable light and dark theme.
2.  **Font Size Control**: Implement menu items or keyboard shortcuts (Ctrl +/-, Ctrl+MouseWheel) to adjust the font size in all text panels.
3.  **Line Number Gutter**: Add a line number display to the left of the main prompt editor.
4.  **Status Bar**: Create a status bar at the bottom of the window to display the current task status, line/column number, and other contextual information.
5.  **Clear Panels**: Add buttons or menu items to clear the contents of the Dashboard and Console panels.
6.  **Resizable Panels**: Convert the layout to use `tk.PanedWindow` to allow the user to click and drag the boundaries between panels to resize them.
7.  **Basic Syntax Highlighting**: Automatically color the `TODO:`, `DONE:`, and `FAILED:` prefixes in the editor to make them more distinct.
8.  **Word Wrap Toggle**: Add a menu option to enable or disable word wrapping in the editor and console text widgets.
9.  **Context Menu**: Implement a right-click context menu in the text panels for basic actions like Cut, Copy, and Paste.
10. **Progress Bar**: Display a simple progress bar in the status bar that visually tracks the completion of the task list.

### Workflow & Functionality Enhancements

11. **File I/O Menu**: Implement a full File menu with `Open`, `Save`, `Save As`, and `Exit` functionalities for handling different prompt files.
12. **Workflow Controls**: Add toolbar buttons (e.g., with icons) to allow the user to manually `Run`, `Pause`, and `Reset` the automated task processing.
13. **Manual Task Trigger**: Allow a user to right-click any `TODO:` line and select "Run this task" to process it immediately, out of sequence.
14. **Re-run Tasks**: Allow a user to right-click a `DONE:` line and revert it to `TODO:`, enabling it to be run again.
15. **Step-Through Debug Mode**: Add a "Step" button that processes only one task and then waits for the user to click "Step" again, for a more controlled execution.
16. **Text Search**: Implement a simple "Find" dialog (Ctrl+F) to search for text within the main prompt editor.
17. **Auto-Save Option**: Add a setting to automatically save the contents of the prompt editor each time a task is completed.
18. **Configurable Task Prefixes**: Allow the user to define custom prefixes (e.g., `URGENT:`, `NOTE:`) in a simple settings window.
19. **Session Persistence**: Automatically save the state of the editor, dashboard, and console on exit and reload it on the next launch.
20. **Undo/Redo Stack**: Implement a basic undo/redo functionality for the prompt editor text widget.

### Feedback & Logging Enhancements

21. **Timestamped Logging**: Prepend every entry in the Console Log with a `[HH:MM:SS]` timestamp.
22. **Exportable Logs**: Add a menu option to export the contents of the Dashboard and Console panels to separate `.txt` or `.log` files.
23. **Visual Task Status Icons**: Use icons (e.g., `✓` for success, `✗` for failure, `⌛` for in-progress) in the Dashboard for clearer visual feedback.
24. **Graceful Error Handling**: If the language model call fails, catch the exception, log the error message to the console, and mark the task as `FAILED:` in the editor instead of crashing.
25. **Confirmation Dialogs**: Add "Are you sure?" confirmation dialogs for critical actions like resetting the workflow or closing the application with unsaved changes.
