# 100 Enhancement Ideas for the Haba Demo Editor

This document outlines 100 potential enhancements for the Haba editor in `src/p/`. The ideas are designed to be implemented without new external frameworks or libraries, focusing on improving the core editing experience for both the `.haba`/JavaScript format and for Python scripting.

---

### Category 1: Core Editor & UI Enhancements (1-15)

**1. Unified UI Component Model**
- **Description:** Refactor `editor.py` and `display.py` to remove duplicated UI code into a single, reusable component model.
- **Challenge:** Merging two similar but slightly different UI implementations without breaking existing functionality.
- **Mitigation:** Create a single `UIView` class that handles all widget creation and layout. The `HabaEditor` class will instantiate and manage this view, passing itself as the controller.

**2. Customizable UI Theme Engine**
- **Description:** Allow users to change editor colors (background, text, highlights) via a `theme.json` file.
- **Challenge:** `tkinter` styling is cumbersome, and managing dynamic color changes for all widgets is complex.
- **Mitigation:** Define all colors in a central dictionary. Create a `ThemeManager` that reads a JSON file and applies these colors to widget configurations. Provide a "Reload Theme" command to apply changes without restarting.

**3. Tabbed File Editing**
- **Description:** Allow multiple files to be open in tabs within the main editor panel.
- **Challenge:** Managing the state (text content, undo/redo stack, file path) for multiple open files.
- **Mitigation:** Use a `ttk.Notebook` widget for the main editor area. Each tab will hold a frame containing a text widget and its associated metadata in a custom class.

**4. Split View Editing**
- **Description:** Allow side-by-side editing of the same file or two different files.
- **Challenge:** Synchronizing scrolling and edits if it's the same file; managing two independent editor instances otherwise.
- **Mitigation:** Use a `tk.PanedWindow`. For the same file, have one text buffer shared by two text widgets. For different files, create two independent editor frames.

**5. Command Palette**
- **Description:** An overlay input box (like in VS Code) to quickly access all editor commands by name.
- **Challenge:** Implementing a non-blocking, searchable overlay window in `tkinter`.
- **Mitigation:** Create a `Toplevel` window without decorations. Add a Listbox that is filtered based on input in an Entry widget. Bind a keyboard shortcut to open it and execute commands.

**6. Minimap**
- **Description:** A small graphical outline of the entire file's content for quick navigation.
- **Challenge:** Rendering a scaled-down version of the text efficiently and keeping it in sync without performance loss.
- **Mitigation:** Use a `tk.Canvas` widget. On text change (with debouncing), draw small rectangles representing lines of text. Map clicks on the canvas to scroll positions in the main text widget.

**7. Smooth Pixel-Based Scrolling**
- **Description:** Implement pixel-based scrolling instead of the default line-based scrolling for a smoother feel.
- **Challenge:** `tkinter`'s default Text widget scrolling is line-based and can feel jerky.
- **Mitigation:** Intercept mouse wheel events and manually call the `yview_scroll` method with smaller, calculated increments to simulate smoother motion.

**8. Dynamic Status Bar**
- **Description:** Enhance the status bar to show dynamic information like cursor position (Line, Column), file encoding, and language type.
- **Challenge:** Efficiently updating the status bar on every cursor move or selection change without performance penalty.
- **Mitigation:** Bind to `<KeyRelease>` and `<ButtonRelease>` events. In the event handler, get the cursor position (`text.index(tk.INSERT)`) and update the status bar label. Use debouncing if performance is an issue.

**9. Configurable Font Settings**
- **Description:** Allow users to change the editor font family and size from a settings menu.
- **Challenge:** Applying font changes to all relevant text widgets and ensuring the UI resizes gracefully.
- **Mitigation:** Store font settings in a central config file. Create a settings dialog that allows users to pick a font. On save, update the font configuration for all text widgets programmatically.

**10. Drag-and-Drop File Opening**
- **Description:** Allow users to drag a file from their operating system and drop it onto the editor window to open it.
- **Challenge:** Requires integration with platform-specific drag-and-drop protocols, which can be complex in `tkinter`.
- **Mitigation:** The most robust "no-library" approach is difficult. A simpler mitigation is to have a prominent "Drop file here" area that, when clicked, opens a standard file dialog. A more advanced approach involves platform-specific `ctypes` calls.

**11. Session Persistence**
- **Description:** Remember open files, active tab, and panel layouts between application sessions.
- **Challenge:** Saving and restoring the complete state of the application accurately.
- **Mitigation:** On close, save a JSON file (`session.json`) containing a list of open file paths, the current active tab, and the positions of the paned window sashes. On startup, read this file and restore the state.

**12. High-DPI Display Support**
- **Description:** Ensure the UI scales correctly and looks sharp on high-resolution monitors.
- **Challenge:** `tkinter` can have issues with DPI scaling, leading to blurry fonts or incorrectly sized widgets.
- **Mitigation:** Use the `ctypes` library on Windows to make the application DPI-aware (`ctypes.windll.shcore.SetProcessDpiAwareness(1)`). For other platforms, use Tk's built-in scaling factor.

**13. Integrated Terminal Panel**
- **Description:** Add a terminal emulator inside a new panel at the bottom of the window.
- **Challenge:** Embedding a fully functional, interactive terminal is extremely complex.
- **Mitigation:** Create a "pseudo-terminal". Use a `Text` widget for output and an `Entry` widget for input. Use `subprocess` to run commands and redirect their stdout/stderr to the Text widget. This won't support interactive applications like `vim` but is fine for most CLI tools.

**14. Non-Blocking Notifications System**
- **Description:** A non-blocking way to show info, warnings, or errors to the user without interrupting their workflow.
- **Challenge:** `messagebox` is blocking. A custom solution is needed.
- **Mitigation:** Create a `Toplevel` window that appears in a corner of the screen for a few seconds. Use `after()` to automatically destroy it. A queue can manage displaying multiple notifications sequentially.

**15. Workspace Management**
- **Description:** Allow saving and loading different sets of open files and settings as named "workspaces".
- **Challenge:** Abstracting session state to be saved to and loaded from different named files.
- **Mitigation:** Extend the session persistence logic. Instead of a single `session.json`, allow saving/loading named workspace files (e.g., `my_project.habaworkspace`) that contain the same state information.

---

### Category 2: JavaScript & .haba Language Features (16-35)

**16. Live HTML Preview in Browser**
- **Description:** Render the exported HTML and automatically open it in the user's default web browser.
- **Challenge:** `tkinter` has no built-in web browser widget, and creating one is out of scope.
- **Mitigation:** Write the generated HTML to a temporary file and use Python's built-in `webbrowser.open()` to launch it in the user's default browser. The "Render" button would trigger this action.

**17. CSS Color Gutter Preview**
- **Description:** Show a small color swatch in the gutter next to CSS color definitions (`#RRGGBB`, `rgb(...)`).
- **Challenge:** `tkinter`'s `Text` widget doesn't have a gutter. It must be simulated.
- **Mitigation:** Create a narrow `tk.Canvas` widget to the left of the `Text` widget. On text change, parse for color codes, get the line number, and draw a colored rectangle on the canvas at the corresponding vertical position.

**18. Enhanced JS Symbol Outline**
- **Description:** Improve the Symbol Outline to distinguish between functions, classes, and variables.
- **Challenge:** Requires more than simple regex; needs a basic understanding of JS syntax structure.
- **Mitigation:** Enhance the parsing regex to capture keywords like `function`, `class`, or `const/let/var` at the top level. Use this information to add icons or prefixes to the entries in the outline.

**19. JS Autocompletion Engine**
- **Description:** Provide context-aware autocompletion for JavaScript objects and keywords.
- **Challenge:** Building a JS parser and type inference engine from scratch is a massive undertaking.
- **Mitigation:** Implement a simple text-based autocompletion. On `.` key press, scan the entire document for words following the object's name and suggest them. For global objects like `document`, pre-populate a list of common properties (`.getElementById`, `.querySelector`).

**20. Pluggable ESLint Linter**
- **Description:** Properly integrate the `linter.py` module as the default linter, replacing the regex-based one.
- **Challenge:** The user might not have Node.js or ESLint installed.
- **Mitigation:** In the settings, allow the user to specify the path to their `eslint` executable. The editor can check for `eslint` in common locations. If not found, it gracefully falls back to the built-in regex linter and shows a message in the status bar.

**21. Quick Fixes for Linter Errors**
- **Description:** Provide context menu actions to fix simple linting issues (e.g., "Remove trailing whitespace").
- **Challenge:** Applying changes from the linter back to the text widget accurately and safely.
- **Mitigation:** For simple, line-based issues, the linter can provide a "fix" object. A right-click context menu on a highlighted error would show a "Quick Fix" option that applies the text modification for that line.

**22. .haba Section Code Folding**
- **Description:** Allow folding of `---CONTENT---`, `---PRESENTATION---`, and `---SCRIPT---` sections in `.haba` files.
- **Challenge:** Hiding and showing large blocks of text in a `tkinter` Text widget.
- **Mitigation:** Use tags with the `elide` option (`text.tag_config("hidden", elide=True)`). Add clickable `[+]` and `[-]` icons in the gutter canvas to toggle the `elide` state for the tags covering those sections.

**23. JS Snippet Library Expansion**
- **Description:** Expand the `snippets.json` file with more useful JS snippets (e.g., `for` loop, `fetch` request, `try...catch`).
- **Challenge:** Creating a user-friendly way to browse and insert snippets.
- **Mitigation:** When the user types a snippet keyword and presses Tab, replace the keyword with the snippet body. A command in the Command Palette could open a listbox showing all available snippets for selection.

**24. Emmet-Style HTML Abbreviations**
- **Description:** In the `.haba` content section, allow writing CSS selectors like `div#page>ul>li*5` and expanding them into HTML.
- **Challenge:** Implementing an Emmet-style parser and generator from scratch is non-trivial.
- **Mitigation:** Implement a simplified version with regex for basic cases like `tag#id.class`. A full implementation is a significant task but possible with a custom recursive descent parser.

**25. Bracket/Pair Auto-Closing**
- **Description:** Automatically insert a closing `}`, `]`, `)`, or `"` when the user types the opening one.
- **Challenge:** Handling cases where the user *doesn't* want the pair, and allowing easy typing over the auto-inserted character.
- **Mitigation:** Bind to the key press event for `(`, `{`, `[`, `"`. In the handler, insert both characters and move the cursor back between them. If the user then types the closing character, just move the cursor forward one space instead of inserting another character.

**26. Intelligent Line Duplication**
- **Description:** Add a command (e.g., `Ctrl+D`) to duplicate the current line or selected block of lines downwards.
- **Challenge:** Getting the content of the current line(s) and inserting it below.
- **Mitigation:** Get the start and end indices of the current line or selection. Get the text content. Insert a newline and the content at the end of the line/selection.

**27. JS "Go to Definition"**
- **Description:** For a JS variable or function, jump the cursor to where it was defined.
- **Challenge:** Requires a symbol table for the entire script.
- **Mitigation:** On text change, run a background task to parse the JS (with regex) and build a simple symbol table (a dictionary mapping names to their `(line, column)` definition). "Go to Definition" would look up the symbol under the cursor and jump to that location.

**28. JS "Find All References"**
- **Description:** For a JS variable or function, show all places it is used in the script.
- **Challenge:** Requires a full-text search scoped to the current symbol, avoiding substrings.
- **Mitigation:** Get the word under the cursor. Perform a full-text search for that word, ensuring it's a whole word match (using regex boundaries `\b`). Present the results in a listbox. Clicking an item jumps to that line.

**29. JS "Rename Symbol"**
- **Description:** Rename a variable and all its references within the script at once.
- **Challenge:** Safely finding and replacing all references without accidentally renaming substrings in other words or comments.
- **Mitigation:** Use the "Find All References" logic. Once all references are found, iterate through them (from bottom to top to avoid index changes) and replace each instance. This requires a more robust parser than simple text search to be truly safe.

**30. JSDoc Stub Generation**
- **Description:** After typing `/**` above a function, auto-generate a JSDoc comment block with `@param` and `@returns` tags.
- **Challenge:** Parsing the function signature below the comment.
- **Mitigation:** When the user types `/**` and hits Enter, read the next line. Use regex to parse the function signature (`function name(param1, param2)`). Use the extracted info to generate the comment block.

**31. .haba Presentation Helper UI**
- **Description:** A UI to visually build the presentation rules instead of typing them manually.
- **Challenge:** Creating a UI for CSS-like properties and serializing them into the `.haba` format.
- **Mitigation:** Create a new tab in the right-hand notebook. Add entry fields for common properties like `color`, `font-size`. A color picker button could be added. When values change, update the `---PRESENTATION---` section programmatically.

**32. Inline Value Preview Tooltips**
- **Description:** When the cursor is on a color hex code, show it in a tooltip. When on an image URL, show a thumbnail.
- **Challenge:** Creating and placing tooltips over text and loading images asynchronously without blocking the UI.
- **Mitigation:** On hover (or cursor move), check the word under the cursor. If it's a hex code, create a `Toplevel` window with that background color near the cursor. If it's a URL, start a thread to download the image and then display it in the tooltip. Destroy the tooltip on cursor leave.

**33. Rule-Based JS Code Formatting**
- **Description:** Integrate a simple, rule-based JS formatter to enforce a consistent style.
- **Challenge:** Building a full-fledged formatter like Prettier is a huge project.
- **Mitigation:** Implement a few basic formatting rules from scratch: enforce consistent indentation (using a basic parser to understand block levels), ensure spaces around operators, and normalize brace style. This can be done with a tokenizer and a set of post-processing rules.

**34. Live Regex Tester**
- **Description:** A UI to test JavaScript regular expressions with live highlighting of matches in a sample text.
- **Challenge:** Safely and efficiently running regex from user input on sample text.
- **Mitigation:** Add a new panel with two text boxes: one for the regex and one for the sample text. On text change in either, use Python's `re` module (which is very similar to JS's) to find all matches and apply a highlight tag to the sample text widget.

**35. DOM Tree Viewer**
- **Description:** Parse the `.haba` content layer and display it as a navigable tree view, similar to a browser's developer tools.
- **Challenge:** Requires an HTML parser.
- **Mitigation:** Python's built-in `html.parser` can be used as it is not an external framework. Feed the `.haba` content to it and build a `ttk.Treeview` based on the start/end tag events it emits.

---

### Category 3: Python Language Features (36-55)

**36. Python Syntax Highlighting**
- **Description:** Implement syntax highlighting for Python code when the script editor is in Python mode.
- **Challenge:** The editor seems hard-coded for JS. It needs a language abstraction layer.
- **Mitigation:** Create a `SyntaxHighlighter` base class. Implement `JSSyntaxHighlighter` and `PythonSyntaxHighlighter` subclasses. Add a language toggle that swaps out the active highlighter. The highlighter would use regex to find keywords, strings, comments, etc., and apply `tkinter` tags.

**37. Pyflakes Linter Integration**
- **Description:** Integrate the `pyflakes` linter for Python code analysis.
- **Challenge:** Running an external tool and parsing its output.
- **Mitigation:** Use `subprocess` to run `pyflakes` on the content of the script buffer. `pyflakes` is a good choice as it's a single file and has no dependencies. Its output format can be parsed with regex to get line numbers and messages for highlighting.

**38. Basic PEP 8 Style Checker**
- **Description:** Implement checks for basic PEP 8 rules not covered by `pyflakes`.
- **Challenge:** Implementing all of PEP 8 is a large task.
- **Mitigation:** Focus on easy-to-check rules hinted at in `display.py`: line length > 79 chars, mixed tabs and spaces, trailing whitespace. These can be done with simple regex on a per-line basis.

**39. Virtual Environment Manager**
- **Description:** Allow creating and selecting a Python virtual environment for the project.
- **Challenge:** Managing `venv` creation and activation from within a `tkinter` app.
- **Mitigation:** Use `subprocess` to run `python -m venv .venv`. In settings, allow the user to select the Python executable from the `.venv/bin` directory. This executable would then be used for running scripts and linters.

**40. "Run Python Script" Command**
- **Description:** Add a button to execute the current script using the selected Python interpreter.
- **Challenge:** Capturing stdout/stderr and displaying it in the console panel in real-time.
- **Mitigation:** Use `subprocess.Popen` to run the script. Read from its `stdout` and `stderr` pipes in a separate thread to avoid blocking the GUI, and append the output to the console `Text` widget.

**41. PDB Debugger Integration**
- **Description:** Provide a simple graphical interface for the built-in `pdb` debugger.
- **Challenge:** Two-way communication with an interactive `pdb` subprocess.
- **Mitigation:** Run the Python script with `python -m pdb my_script.py`. Send `pdb` commands (`n`, `c`, `p var`) to its `stdin` and parse the output from its `stdout`. Create UI buttons for "Continue", "Next", "Step", and a watch window that sends `p var` commands.

**42. Auto-Import for Standard Library**
- **Description:** Suggest and add imports for unresolved names that are part of the Python standard library.
- **Challenge:** Knowing what to import and where to get it from without heavy analysis.
- **Mitigation:** Maintain a pre-scanned index of the standard library modules. If the linter finds an "undefined name" error, check if that name exists in the index. If so, offer a quick fix to add the `import` statement at the top of the file.

**43. "Sort Imports" Command**
- **Description:** A command to automatically sort imports according to PEP 8 (standard library, third party, local).
- **Challenge:** Categorizing imports correctly without external tools.
- **Mitigation:** Maintain a list of Python's standard library modules. Parse the block of imports at the top of the file. Any import not in the std lib list is considered third-party/local. Sort each group alphabetically and rewrite the import block.

**44. Python Docstring Generator**
- **Description:** Generate a docstring stub for a Python function, respecting its signature.
- **Challenge:** Parsing the function signature, including arguments and type hints.
- **Mitigation:** When the user types `"""` after a `def` line, use regex to parse the function signature. Use the extracted info to generate a standard docstring format (e.g., reST or Google style) with placeholders.

**45. Type Hinting Syntax Highlighting**
- **Description:** Add distinct syntax highlighting for Python type hints to differentiate them from variables.
- **Challenge:** Distinguishing types from variables in the syntax highlighter regex.
- **Mitigation:** Update the Python syntax highlighting regex to specifically look for the `->` token and the `var: type` pattern within function definitions. Give these matches a special `tkinter` tag.

**46. "Go to Definition" (Python)**
- **Description:** Jump to the definition of a function, class, or variable within the project.
- **Challenge:** Requires parsing Python code across multiple files and building a symbol table.
- **Mitigation:** Use Python's built-in `ast` module. Parse the current file and any imported project files into an AST on file change. Traverse the trees to find all definitions and store their locations. "Go to Definition" then searches this table.

**47. "Find All References" (Python)**
- **Description:** Show all usages of a Python variable, function, or class.
- **Challenge:** Requires a more advanced AST traversal to find all name usages and understand scope.
- **Mitigation:** Use the `ast` module. Traverse the tree and find all `ast.Name` nodes. Check if the `id` of the node matches the symbol under the cursor and it's in the correct scope. Collect the line numbers of all matches.

**48. "Rename Symbol" (Python)**
- **Description:** Safely rename a Python symbol and all its references across the project.
- **Challenge:** This is a high-risk operation that requires perfect accuracy to avoid breaking code.
- **Mitigation:** Use the "Find All References" logic from the `ast` traversal. This is much safer than regex, as it understands scope. Iterate through all found nodes and perform the rename operation.

**49. Implement `__main__` Guard Hint**
- **Description:** The `if __name__ == "__main__"` hint is in `display.py` but needs a working implementation.
- **Challenge:** Heuristically determining when a script needs a main guard.
- **Mitigation:** On save, use the `ast` module to check if there are function/class definitions and also executable code at the top-level module scope. If so, display the hint in the status bar.

**50. Dead Code Highlighting**
- **Description:** Highlight code that appears after a `return`, `raise`, or `break` statement in a way that makes it obvious it won't be executed.
- **Challenge:** Requires basic control flow analysis within a block.
- **Mitigation:** In a function body, after seeing a `return`, `raise`, or `continue`/`break` at the top level of a block, tag all subsequent lines within that same block with a "dead code" style (e.g., greyed out or faded).

**51. Cyclomatic Complexity Analyzer**
- **Description:** Calculate and display the cyclomatic complexity of each function as a code metric.
- **Challenge:** A true calculation requires a full control-flow graph.
- **Mitigation:** Use an approximation. For each function, use the `ast` module to count the number of control flow-changing nodes (`If`, `For`, `While`, `And`, `Or`, `Except`). The final count is a good proxy for complexity and can be shown on hover.

**52. Refactoring: Extract Variable**
- **Description:** Select an expression, and have it automatically replaced with a new variable declaration on the preceding line.
- **Challenge:** Safely modifying the code and inserting the new line at the correct indentation level.
- **Mitigation:** Get the selected text. Prompt the user for a variable name. Replace the selection with the variable name. Find the start of the current line and insert `variable_name = selected_text\n` above it, respecting indentation.

**53. Refactoring: Extract Method/Function**
- **Description:** Select a block of code and turn it into a new function, replacing the original code with a call to it.
- **Challenge:** Very complex. Needs to identify input variables that become parameters and variables that need to be returned.
- **Mitigation:** Implement a simplified version. The user selects a block of code and is prompted for a function name. The tool creates a new function with the selected code as the body and replaces the original selection with a call to the new function. It does *not* attempt to figure out parameters or return values, leaving that to the user to fix manually.

**54. Python Code Cell Execution (`# %%`)**
- **Description:** Execute blocks of Python code separated by `# %%` comments, similar to a Jupyter notebook, in an interactive session.
- **Challenge:** Requires a persistent, interactive Python process to maintain state between cell runs.
- **Mitigation:** Start a Python subprocess with the `-i` flag. When the user "runs" a cell, send that block of text to the subprocess's `stdin`. Capture and display the output in the console panel.

**55. Python Variable Explorer**
- **Description:** When debugging with PDB or running in cell mode, show a table of current variables and their values.
- **Challenge:** Getting variable state from the Python subprocess without complex debugging protocols.
- **Mitigation:** After each PDB step or cell execution, send the command `p locals()` to the subprocess. Parse the string output (it's a dict representation) and display the key-value pairs in a `ttk.Treeview` widget.

---

### Category 4: File & Project Management (56-70)

**56. File System Tree View**
- **Description:** A panel on the left showing the files and folders in the current project directory, allowing for easy navigation.
- **Challenge:** Populating and updating the tree view efficiently, especially for large directories with many files.
- **Mitigation:** Use a `ttk.Treeview` widget. On startup, populate it by recursively walking the project directory with `os.walk`. For performance, only populate subdirectories when the user clicks to expand them.

**57. File Operations from Tree View**
- **Description:** Allow creating, deleting, and renaming files and folders directly from the tree view's context menu.
- **Challenge:** Performing file system operations safely and updating the tree view UI accordingly without a full refresh.
- **Mitigation:** Use Python's `os` and `shutil` modules. Add a right-click context menu to the tree view. The menu actions call functions that perform the file operation and then refresh only the relevant parent node in the tree.

**58. "Find in Files" Feature**
- **Description:** A project-wide search feature that finds all occurrences of a string or regex in the project folder.
- **Challenge:** Searching thousands of files quickly without blocking the UI.
- **Mitigation:** Use a background thread to iterate through files (`os.walk`). For each file, read its content and search for the string/regex. Post results back to the main thread to be displayed in a listbox.

**59. `.gitignore` Support**
- **Description:** When searching or listing files in the tree view, respect the rules defined in a `.gitignore` file.
- **Challenge:** Correctly parsing and applying `.gitignore` patterns, including negations.
- **Mitigation:** Implement a simple parser for `.gitignore` rules (handling `*`, `?`, and `!`). When walking the file tree for search or display, check each file and directory against these patterns and skip if matched.

**60. Quick File Switcher**
- **Description:** A searchable popup (`Ctrl+P`) to quickly open any file in the project by typing parts of its name.
- **Challenge:** Indexing all project files and providing a fast, fuzzy search UI.
- **Mitigation:** On startup, get a list of all file paths in the project and store it. The "Quick Switcher" command opens a dialog with a listbox that is filtered as the user types, implementing a simple fuzzy-finding algorithm.

**61. "Save All" Command**
- **Description:** A button or command to save all modified and currently open files at once.
- **Challenge:** Tracking the "dirty" (modified) state of each open file tab.
- **Mitigation:** In the data model for each open tab, include a boolean `is_dirty` flag. Set it to `True` on any text modification. The "Save" action resets it to `False`. The "Save All" command iterates through all open tabs and saves the ones where `is_dirty` is `True`.

**62. Auto-Save on Idle**
- **Description:** Automatically save files after a configurable period of user inactivity.
- **Challenge:** Managing timers and detecting inactivity without being intrusive or causing performance issues.
- **Mitigation:** On each text modification (`<<Modified>>` event), cancel any pending `after` job and schedule a new one for a few seconds in the future. If the `after` job is allowed to run, it means the user has been idle, and the file can be saved.

**63. File Encoding Support**
- **Description:** Allow opening and saving files with different text encodings (e.g., UTF-8, Latin-1, UTF-16).
- **Challenge:** Detecting encoding on open and letting the user choose on save.
- **Mitigation:** When opening a file, try to decode with UTF-8 first. If it fails, try a common fallback like `latin-1`. Add an option in the "Save As" dialog to select the encoding. The status bar should display the current file's encoding.

**64. New File from Template**
- **Description:** A feature to create new files based on predefined templates (e.g., a new Python script with a main guard, a new `.haba` file).
- **Challenge:** Managing the templates in a user-friendly way.
- **Mitigation:** Create a `templates` directory in the editor's config folder. The "New File from Template" command would show a list of files from this directory. Selecting one copies its content into a new, unsaved buffer.

**65. "Reveal in File Explorer"**
- **Description:** A context menu option on a file tab or in the file tree to open the file's containing folder in the OS file explorer.
- **Challenge:** This is an OS-specific operation.
- **Mitigation:** Use `subprocess.run` with `explorer` on Windows, `open` on macOS, and `xdg-open` on Linux. The argument should be the directory path (`os.path.dirname(filepath)`).

**66. "Copy File Path" Command**
- **Description:** A context menu option to copy the absolute or relative path of a file to the clipboard.
- **Challenge:** A small but highly useful quality-of-life feature.
- **Mitigation:** Add the option to the file context menu. The handler gets the file path associated with the item and uses `tkinter`'s built-in clipboard methods (`clipboard_clear()`, `clipboard_append()`) to copy it.

**67. Project-Specific Settings**
- **Description:** Allow some settings (like linter configs or build commands) to be stored in a file within the project directory (e.g., `.editor/settings.json`).
- **Challenge:** Merging global user settings with project-specific overrides in a predictable way.
- **Mitigation:** When the editor opens a project, look for a settings file in the root. Load its settings and use them to override any corresponding global user settings for the current session.

**68. External File Change Watcher**
- **Description:** Automatically refresh the file tree or reload an open file if it's changed on disk by an external program.
- **Challenge:** Efficiently monitoring the file system for changes without a library like `watchdog`.
- **Mitigation:** In a background thread, periodically walk the file tree and check the last modified timestamp (`os.path.getmtime`) of files and folders against a stored state. If a change is detected, prompt the user to reload the file or refresh the tree.

**69. Automatic Backup Files on Save**
- **Description:** When saving a file, keep a copy of the previous version of the file as a backup.
- **Challenge:** Managing backup files to avoid cluttering the project directory.
- **Mitigation:** On save, before writing the new content, rename the existing file to `filename.bak`. A setting could control whether this feature is enabled and how many backups to keep.

**70. Local File History**
- **Description:** Keep a local history of changes for each file, allowing the user to view diffs and revert to previous versions.
- **Challenge:** Storing snapshots efficiently and computing diffs without high overhead.
- **Mitigation:** On every save, store a copy of the file in a hidden `.history` directory with a timestamped name. Use Python's built-in `difflib` module to generate a diff between the current version and a selected history snapshot for viewing. Reverting just replaces the current file content with the snapshot content.

---

### Category 5: Build, Run & Debugging (71-80)

**71. Configurable Build System**
- **Description:** A UI to define and run project build commands (like `make`, `npm run build`, `gcc ...`).
- **Challenge:** The "No-Compile Mandate" prohibits the agent from running compilation, but not from building the feature for the user.
- **Mitigation:** Provide a UI in the project settings where the user can define a build command. The "Build" button will execute this command in the integrated terminal using `subprocess`, showing the output. This empowers the user without the agent performing compilation.

**72. Build Error Parser**
- **Description:** Parse errors from build tool output and display them in a clickable "Problems" panel.
- **Challenge:** Build output formats from different tools are highly variable.
- **Mitigation:** Create a "Problems" panel. Use a set of configurable regex patterns to parse common `file:line:column: error` formats from the build output. Clicking an error in the panel jumps to the corresponding location in the file.

**73. Launch Configurations**
- **Description:** A `launch.json` file to define how to run or debug different targets within a project.
- **Challenge:** Designing a flexible but simple JSON schema for users to understand.
- **Mitigation:** Define a schema with configurations for "run" and "debug". Each config would specify the command to run, arguments, and environment variables. A dropdown in the UI would let the user select which configuration to launch.

**74. Attach to Running Process (Debugger)**
- **Description:** Allow attaching the Python debugger to an already running Python process.
- **Challenge:** Requires process IDs and signalling, which is OS-specific and complex.
- **Mitigation:** This is very advanced. A simplified approach uses a remote debugger pattern. The user manually adds code like `import debugpy; debugpy.listen(5678)` to their script. The editor then has an "Attach" command that connects to that port. (`debugpy` is a library, so a pure-pdb solution would be much harder and is likely out of scope).

**75. Python Conditional Breakpoints**
- **Description:** Set breakpoints that only trigger execution to pause when a specific expression is true.
- **Challenge:** Passing the condition expression from the UI to the `pdb` instance.
- **Mitigation:** `pdb` supports this natively. The UI would allow right-clicking a breakpoint to add a condition string. The command sent to `pdb` would be `condition <bp_number> <expression>`.

**76. Logpoints**
- **Description:** Breakpoints that don't pause execution but instead log a message (or the value of an expression) to the console.
- **Challenge:** `pdb` does not have a native "logpoint" concept.
- **Mitigation:** Emulate it. When `pdb` hits a breakpoint that is marked as a logpoint, the editor's debugger integration would immediately send a `p <expression>` command to print the log message, followed by a `continue` command. The user sees the log message, but the debugger doesn't stay paused.

**77. Exception Breakpoints**
- **Description:** Automatically pause the debugger on caught or uncaught exceptions, even if no breakpoint is set on that line.
- **Challenge:** Configuring this behavior in the debugger.
- **Mitigation:** `pdb` can do this with post-mortem debugging (`pdb.pm()`). For live debugging, a command can be set to break on exceptions. The UI would have checkboxes for "Break on Uncaught Exceptions" and "Break on Caught Exceptions".

**78. "Run with Arguments" Prompt**
- **Description:** A UI to prompt for command-line arguments before running a script.
- **Challenge:** A simple but necessary UI flow for interactive script testing.
- **Mitigation:** Before running a script via a "Run with args" command, open a simple dialog box with an entry field. The text entered there is appended to the `subprocess` command when launching the script.

**79. "Stop/Kill Process" Button**
- **Description:** A button in the UI to terminate the currently running script or debug session.
- **Challenge:** Gracefully and, if necessary, forcefully killing a subprocess without orphaning it.
- **Mitigation:** Store the `subprocess.Popen` object for the running process. The "Stop" button would first try `process.terminate()` (sends SIGTERM) and, if that fails after a short timeout, `process.kill()` (sends SIGKILL).

**80. Environment Variable Editor**
- **Description:** A UI to set environment variables for specific run/debug configurations in `launch.json`.
- **Challenge:** A simple but clear key-value editor UI is needed.
- **Mitigation:** In the launch configuration editor UI, provide a simple table or list of entry fields for key-value pairs. These are then passed as the `env` argument to `subprocess.Popen`.

---

### Category 6: Quality & Analysis Tools (81-90)

**81. Project-Wide TODO/FIXME Explorer**
- **Description:** The existing `TodoExplorerPanel` should be enhanced to scan and list TODOs from the entire project, not just the open file.
- **Challenge:** Searching all project files for comments can be slow.
- **Mitigation:** Use the same background "Find in Files" mechanism. It would specifically search for lines containing "TODO:", "FIXME:", etc., and populate the explorer panel. Results should be grouped by file.

**82. Code Metrics Panel**
- **Description:** A dedicated panel showing static analysis statistics for the current file (line count, character count, cyclomatic complexity of functions).
- **Challenge:** Calculating these metrics efficiently on each change can be performance-intensive.
- **Mitigation:** On file save, run the analysis. Use `len(text.splitlines())` for line count and the `ast`-based cyclomatic complexity analyzer. Display the results in a dedicated panel that updates on save.

**83. Spell Checker for Comments & Strings**
- **Description:** Add spell checking within comments and string literals for both Python and JavaScript.
- **Challenge:** Requires a dictionary and efficient checking to avoid slowing down the editor.
- **Mitigation:** Use a common word list file (e.g., from `/usr/share/dict/words` on Linux/macOS, or a bundled one). On text change (debounced), extract text from comment/string tags, split into words, and check against a hash set of dictionary words. Highlight misspelled words.

**84. Code Duplication Finder**
- **Description:** A tool to find duplicated blocks of code within the project to identify refactoring opportunities.
- **Challenge:** This is a complex analysis task; perfect detection is very hard.
- **Mitigation:** A simple, non-semantic approach: create a sliding window (e.g., 5 lines long). For each 5-line block, create a hash of its content (ignoring whitespace). Store these hashes in a dictionary mapping the hash to a list of locations. If a hash is already in the dict, you've found a potential duplicate.

**85. Python Function Call Graph**
- **Description:** A tool to visualize how functions in a Python script call each other.
- **Challenge:** Requires static analysis to build the graph, and a way to render it.
- **Mitigation:** Use the `ast` module to traverse a Python file. For each `ast.Call` node inside a function, record a directed edge from the current function to the function being called. Use a `tkinter.Canvas` to draw a simple node-and-edge diagram of the resulting graph.

**86. Git Gutter Status**
- **Description:** Show added, modified, or deleted lines relative to the last commit, right in the editor's gutter.
- **Challenge:** Requires running `git diff` in the background and parsing the output efficiently.
- **Mitigation:** Run `git diff --unified=0 HEAD -- path/to/file` on the current file in a background process. Parse the hunk headers (`@@ -l,s +l,s @@`) to identify changed, added, and deleted lines. Draw colored indicators in the gutter canvas next to these lines.

**87. "Git Blame" on Hover**
- **Description:** Show the last commit that modified each line of code when the user hovers over the gutter.
- **Challenge:** Running `git blame` and displaying the info without cluttering the UI.
- **Mitigation:** Run `git blame --porcelain path/to/file` which has a stable, machine-readable format. On hover over the gutter, show the blame info (author, date, commit hash) for that line in the status bar or a tooltip.

**88. `unittest` Test Runner Integration**
- **Description:** A UI to discover and run tests written with Python's built-in `unittest` framework.
- **Challenge:** Discovering tests and running them individually while parsing the results.
- **Mitigation:** Use `subprocess` to run `python -m unittest discover`. Parse the output to find test names. Display them in a tree view in a "Testing" panel. A "Run" button next to each test would run that specific test (`python -m unittest path.to.TestClass.test_method`).

**89. Test Coverage Highlighting**
- **Description:** After running tests with coverage enabled, highlight lines in the editor that were not executed.
- **Challenge:** Requires a coverage tool and parsing its data format.
- **Mitigation:** Run tests with `coverage.py` (`coverage run -m unittest ...`). Then run `coverage json` to get a report. Parse the JSON report to find which lines in which files were missed. Apply a semi-transparent highlight tag to those lines in the editor.

**90. Simple Automated Refactoring**
- **Description:** A tool to automatically apply simple Python refactorings, like converting old `"%s" % var` string formatting to f-strings.
- **Challenge:** Safely modifying the code's structure without breaking it.
- **Mitigation:** Use the `ast` module to find nodes representing old-style string formatting. A "Quick Fix" would replace the `ast.BinOp` node with an `ast.JoinedStr` (f-string) node and then use a custom unparser (or a bundled one like `astor`) to write the modified AST back to code.

---

### Category 7: Quanta LLM Integration & Extensibility (91-100)

**91. Interactive Quanta Demo Window**
- **Description:** Allow the user to edit the prompt in the Quanta Demo window and re-run the model on demand.
- **Challenge:** The current demo is a one-shot, automated process.
- **Mitigation:** Add a "Run" button to the Quanta Demo window. When clicked, it would take the current text from the prompt editor, find the next `TODO`, and call the model. This makes it an interactive tool rather than a passive demo.

**92. "Send Selection to Quanta"**
- **Description:** Select text in the main editor, right-click, and "Send to Quanta" to use it as a prompt in the demo window.
- **Challenge:** Communication between the main editor window and the Quanta Demo window.
- **Mitigation:** The main editor can open the Quanta Demo window and pass the selected text as an argument to its constructor. The demo window would then use this text as the initial prompt.

**93. AI-Powered Code Generation**
- **Description:** In the Python editor, use the Quanta LLM to generate a function based on a comment.
- **Challenge:** Integrating the LLM call into the main editor workflow and providing sufficient context.
- **Mitigation:** The user writes a comment like `# function that takes a url and returns the html as a string`. A right-click command "Generate Code with Quanta" would send the comment text to the model and insert the returned code block below.

**94. AI-Powered Docstring Writing**
- **Description:** Use the Quanta LLM to write a comprehensive docstring for an existing Python function.
- **Challenge:** Providing the model with the necessary context (the function's code).
- **Mitigation:** A command on a function would take the entire function's source code as a prompt for the LLM, with the instruction "Write a comprehensive docstring for this function in Google format." The result would be inserted into the function.

**95. AI-Based Refactoring Suggestions**
- **Description:** Send a function to the Quanta LLM and ask for refactoring suggestions or code improvements.
- **Challenge:** Displaying the suggestions in a useful, non-intrusive way.
- **Mitigation:** The model would be prompted to "Suggest refactorings for this Python code to improve readability and performance." The response could be a list of suggestions shown in a side panel or as comments, not automatically applied.

**96. Keyboard Shortcut Editor**
- **Description:** A graphical UI to view and customize all keyboard shortcuts for editor commands.
- **Challenge:** Abstracting all key bindings to be configurable rather than hard-coded.
- **Mitigation:** Store all key bindings in a JSON config file, mapping command IDs to key sequences (e.g., `"file.save": "Control-s"`). The editor reads this on startup. A settings UI would provide a graphical way to edit this file.

**97. Simple Plugin System**
- **Description:** A simple plugin system where a "plugin" is a single Python file with a predefined entry point function.
- **Challenge:** Safely loading and running third-party code without a complex API.
- **Mitigation:** The editor looks for scripts in a `plugins` directory. Each script must have a `register(editor_instance)` function. On startup, the editor calls this function, passing its own instance so the plugin can add menu items, bind shortcuts, etc. This is not sandboxed but is a simple starting point.

**98. Portable Mode**
- **Description:** An option to store all settings, logs, and history in the same directory as the application, allowing it to be run from a USB drive.
- **Challenge:** Overriding default configuration paths based on a startup flag.
- **Mitigation:** On startup, check for a file named `portable.flag` in the application directory. If it exists, all config files, history, etc., are read from and written to subdirectories there instead of the user's home directory.

**99. Editor Usage Analytics (Local)**
- **Description:** An opt-in feature to collect usage data (e.g., most used commands) to help the user understand their own workflow.
- **Challenge:** Collecting and storing data without any privacy concerns.
- **Mitigation:** Make it strictly opt-in. If enabled, append command IDs to a local log file (`analytics.log`). A command could then parse this file and show the user their own usage stats. No data is sent anywhere externally, ensuring privacy.

**100. Interactive Onboarding Tour**
- **Description:** A guided tour for new users that highlights key UI elements and features on their first launch.
- **Challenge:** Creating an engaging and non-intrusive tour overlay in `tkinter`.
- **Mitigation:** On first launch, show a series of highlighted areas with tooltips. A `Toplevel` window would contain the explanation and "Next" / "Previous" buttons. The tour would sequentially move a highlight box (a semi-transparent frame) and update the explanation text.
