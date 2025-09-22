import tkinter as tk
from tkinter import ttk, filedialog, font as tkFont
import re
import os
import json
from .haba_parser import HabaParser, HabaData
from .files import FileHandler
from .display import Display
from .menu import MenuBar
from .script_runner import ScriptRunner, run_python_script
from .linter import lint_javascript
from .imports import sort_imports_logic
from . import search

class HabaEditor(tk.Frame):
    """
    The main application class for the Haba Editor.
    Acts as a controller that coordinates the different modules.
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Haba Editor")
        self.pack(fill=tk.BOTH, expand=True)

        # Core components
        self.parser = HabaParser()
        self.script_runner = ScriptRunner()

        # Application state
        self.language = 'javascript'
        self.current_filepath = None
        self.virtual_env = os.path.basename(os.environ.get('VIRTUAL_ENV', ''))

        # Modular components
        self.file_handler = FileHandler(self)
        self.display = Display(self, self, virtual_env=self.virtual_env) # Pass self (editor) and master frame
        self.menu_bar = MenuBar(self)
        self._load_snippets()
        self._load_launch_config()

    def _load_launch_config(self):
        """Finds and loads .editor/launch.json from the project root."""
        self.launch_config = None
        try:
            # A simple upward search for the .editor directory
            current_dir = os.getcwd()
            while True:
                config_dir = os.path.join(current_dir, '.editor')
                if os.path.isdir(config_dir):
                    config_file = os.path.join(config_dir, 'launch.json')
                    if os.path.isfile(config_file):
                        with open(config_file, 'r') as f:
                            self.launch_config = json.load(f)
                        print(f"Loaded launch configuration from {config_file}")
                    return

                parent_dir = os.path.dirname(current_dir)
                if parent_dir == current_dir:
                    break
                current_dir = parent_dir
        except Exception as e:
            print(f"Could not load launch configuration: {e}")

    def _load_snippets(self):
        """Loads code snippets from the snippets.json file."""
        self.snippets = {}
        try:
            base_dir = os.path.dirname(__file__)
            snippet_file_path = os.path.join(base_dir, 'snippets.json')
            with open(snippet_file_path, 'r') as f:
                self.snippets = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load snippets file. {e}")

    def load_file(self):
        """Delegates file loading to the FileHandler."""
        self.file_handler.load_file()

    def save_file(self):
        """Delegates file saving to the FileHandler."""
        self.file_handler.save_file()

    def on_text_change(self, event=None):
        self.render_preview()
        self.display.raw_text.edit_modified(False)

    def on_script_text_change(self, event=None):
        if not self.display.script_text.edit_modified():
            return

        search.update_file_stats(self.display.script_text, self.display.stats_label)

        script_content = self.display.script_text.get("1.0", tk.END)
        self.display.symbol_outline_panel.update_symbols(script_content, self.language)
        self.display.todo_explorer_panel.update_todos(script_content, self.language)

        if self.language == 'python':
            search.highlight_decorators(self.display.script_text)
            search.highlight_trailing_whitespace(self.display.script_text)
            search.check_indentation_consistency(self.display.script_text, self.display.indent_warning_label)
            search.check_main_guard(self.display.script_text, self.display.main_guard_hint_label)
            search.highlight_old_string_formats(self.display.script_text)
        else:
            # Clear python-specific tags and warnings if switching away from python
            self.display.script_text.tag_remove("decorator", "1.0", tk.END)
            self.display.script_text.tag_remove("trailing_whitespace", "1.0", tk.END)
            self.display.script_text.tag_remove("old_string_format", "1.0", tk.END)
            self.display.indent_warning_label.config(text="")
            self.display.main_guard_hint_label.config(text="")
            self.lint_script_text()

        self.display.script_text.edit_modified(False)

    def lint_script_text(self):
        """
        Delegates linting to the lint_javascript function.
        """
        lint_javascript(self.display.script_text)

    def on_quote_release(self, event):
        """
        Event handler for when the user releases the quote key.
        Checks if a docstring stub should be generated.
        """
        if self.language != 'python':
            return

        # Check if the character just inserted is a quote
        cursor_index = self.display.script_text.index(tk.INSERT)
        char_before_cursor = self.display.script_text.get(f"{cursor_index}-1c", cursor_index)

        if char_before_cursor == '"':
            # Check if we have three quotes now
            line_num, col_num = map(int, cursor_index.split('.'))
            line_start = f"{line_num}.0"
            line_text = self.display.script_text.get(line_start, f"{line_num}.end")
            if line_text.strip() == '"""':
                search.generate_docstring_stub(self.display.script_text)

    def on_return_key_press(self, event):
        """
        Handles the return key press to implement auto-indentation for Python.
        """
        if self.language != 'python':
            return # Allow default behavior for other languages

        text_widget = self.display.script_text

        # Get current line and its indentation
        cursor_index = text_widget.index(tk.INSERT)
        line_num, _ = map(int, cursor_index.split('.'))
        current_line = text_widget.get(f"{line_num}.0", f"{line_num}.end")

        indent_match = re.match(r"^(\s*)", current_line)
        current_indent = indent_match.group(1) if indent_match else ""

        # Determine next line's indentation
        next_indent = current_indent
        if current_line.strip().endswith(':'):
            next_indent += "    " # Add one level of indentation

        # Insert the newline and the calculated indentation
        text_widget.insert(tk.INSERT, f"\n{next_indent}")

        # Prevents the default newline behavior
        return "break"

    def on_tab_key_press(self, event):
        """
        Handles Tab key presses to expand snippets or insert a standard tab.
        """
        if self.language != 'python':
            # For non-python languages, just insert a standard tab for now
            self.display.script_text.insert(tk.INSERT, "    ")
            return "break"

        text_widget = self.display.script_text

        # Get the word before the cursor
        cursor_index = text_widget.index(tk.INSERT)
        line_start = text_widget.index(f"{cursor_index} linestart")
        line_text_before_cursor = text_widget.get(line_start, cursor_index)

        # Find the last word in the text before the cursor
        match = re.search(r'(\w+)$', line_text_before_cursor)

        if not match:
            # No word before cursor, insert a standard tab
            text_widget.insert(tk.INSERT, "    ")
            return "break"

        keyword = match.group(1)

        if keyword in self.snippets:
            # We have a snippet match
            snippet = self.snippets[keyword]
            body = "\n".join(snippet['body'])

            # Replace the keyword with the snippet body
            keyword_start_index = text_widget.index(f"{cursor_index} - {len(keyword)}c")
            text_widget.delete(keyword_start_index, cursor_index)
            text_widget.insert(keyword_start_index, body)

            return "break" # Prevent default tab behavior
        else:
            # No snippet found, insert a normal tab
            text_widget.insert(tk.INSERT, "    ")
            return "break"

    def toggle_comment(self, event=None):
        """
        Toggles the comment state for the selected lines or the current line for Python.
        """
        if self.language != 'python':
            return "break" # Only implement for Python for now

        text_widget = self.display.script_text
        try:
            # Get the range of selected lines
            start_index = text_widget.index("sel.first")
            end_index = text_widget.index("sel.last")
            start_line = int(start_index.split('.')[0])
            # If selection ends at the start of a line, don't include that line
            end_line_col = int(end_index.split('.')[1])
            end_line = int(end_index.split('.')[0])
            if end_line_col == 0:
                end_line -= 1

        except tk.TclError:
            # If no selection, use the current line
            start_index = text_widget.index(tk.INSERT)
            start_line = end_line = int(start_index.split('.')[0])

        # Determine if we are commenting or uncommenting based on the first line
        first_line_content = text_widget.get(f"{start_line}.0", f"{start_line}.end")

        # Heuristic: if the first non-whitespace character is '#', uncomment
        if first_line_content.strip().startswith('#'):
            # --- UNCOMMENT ---
            for i in range(start_line, end_line + 1):
                line_content = text_widget.get(f"{i}.0", f"{i}.end")
                # Find the first '#' and remove it, keeping leading space
                match = re.search(r"^(\s*)#\s?", line_content)
                if match:
                    new_line = match.group(1) + line_content[match.end(0):]
                    text_widget.delete(f"{i}.0", f"{i}.end")
                    text_widget.insert(f"{i}.0", new_line)
        else:
            # --- COMMENT ---
            for i in range(start_line, end_line + 1):
                line_content = text_widget.get(f"{i}.0", f"{i}.end")
                if line_content.strip():  # Don't comment empty lines
                    indent_match = re.match(r"^(\s*)", line_content)
                    indent = indent_match.group(1) if indent_match else ""
                    text_widget.insert(f"{i}.{len(indent)}", "# ")

        return "break"  # Prevents default behavior

    def sort_imports(self, event=None):
        """
        Wrapper to call the import sorting logic and update the text widget.
        """
        if self.language != 'python':
            return "break"

        text_widget = self.display.script_text
        original_content = text_widget.get("1.0", "end-1c")

        sorted_content = sort_imports_logic(original_content)

        if original_content != sorted_content:
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", sorted_content)

        return "break"

    def upgrade_string_formatting(self, event=None):
        """
        Calls the f-string conversion logic and updates the text widget.
        """
        if self.language != 'python':
            return "break"

        text_widget = self.display.script_text
        original_content = text_widget.get("1.0", "end-1c")

        converted_content = search.convert_to_f_strings(original_content)

        if original_content != converted_content:
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", converted_content)

        return "break"

    def build_project(self, event=None):
        """
        Finds the build command, displays a dry run message, and then
        parses a sample of build error output to demonstrate error parsing.
        """
        console = self.display.console_output_text
        tasks_listbox = self.display.tasks_listbox

        console.config(state=tk.NORMAL)
        console.delete("1.0", tk.END)
        tasks_listbox.delete(0, tk.END)

        if not self.launch_config or 'configurations' not in self.launch_config:
            console.insert(tk.END, "No valid launch.json configuration found.")
            console.config(state=tk.DISABLED)
            return "break"

        build_command = None
        for config in self.launch_config.get('configurations', []):
            if config.get('request') == 'build':
                build_command = config.get('command')
                break

        if build_command:
            message = (
                "--- Build Dry Run ---\n"
                "Per AI Agent instructions, compilation is prohibited.\n"
                f"Would have run command: '{build_command}'\n\n"
                "--- Parsing Sample Build Output ---"
            )
            console.insert(tk.END, message)

            # Sample error output for demonstration
            sample_output = (
                "src/main.c:10:5: error: 'x' undeclared (first use in this function)\n"
                "src/main.c:15:2: warning: implicit declaration of function 'printf' [-Wimplicit-function-declaration]\n"
                "src/utils.h:5:1: error: expected ';' before '}' token"
            )
            console.insert(tk.END, "\n" + sample_output)

            # Regex to parse 'file:line:col: type: message'
            error_pattern = re.compile(r"^(.*?):(\d+):(\d+):\s+(error|warning):\s+(.*)$")

            parsed_errors = 0
            for line in sample_output.splitlines():
                match = error_pattern.match(line)
                if match:
                    file, lnum, cnum, etype, msg = match.groups()
                    task_text = f"[{etype.upper()}] {os.path.basename(file)}:{lnum} - {msg}"
                    tasks_listbox.insert(tk.END, task_text)
                    parsed_errors += 1

            console.insert(tk.END, f"\n\n--- Found {parsed_errors} issues ---")

        else:
            console.insert(tk.END, "No 'build' request found in launch.json configurations.")

        console.config(state=tk.DISABLED)
        return "break"

    def set_language(self, language):
        """Sets the active language for the editor."""
        self.language = language
        # Future: Trigger re-linting or other language-specific updates
        print(f"Language switched to: {self.language}")
        # For now, we can just clear the old linting when switching
        self.lint_script_text()

    def run_script(self):
        """
        Runs the script using the appropriate runner based on the current language.
        """
        script_content = self.display.script_text.get("1.0", tk.END)

        self.display.run_button.config(state=tk.DISABLED, text="Running...")
        self.master.update()

        if self.language == 'python':
            logs, tasks = run_python_script(script_content)
        else:  # Default to javascript
            # The JS runner needs the full haba content, not just the script part
            haba_content = self.display.raw_text.get("1.0", tk.END)
            logs, tasks = self.script_runner.run_script(haba_content)

        self.display.run_button.config(state=tk.NORMAL, text="Run Script")

        # Update console output panel
        self.display.console_output_text.config(state=tk.NORMAL)
        self.display.console_output_text.delete("1.0", tk.END)
        if logs:
            # Join with newline for display
            self.display.console_output_text.insert(tk.END, "\n".join(logs))
        self.display.console_output_text.config(state=tk.DISABLED)

        # Update actionable tasks panel
        self.display.tasks_listbox.delete(0, tk.END)
        for task in tasks:
            self.display.tasks_listbox.insert(tk.END, f"[{task['type'].upper()}] {task['description']}")

    def _apply_styles(self, style_str, tag_name):
        """
        Parses a style string and applies it as a tag in the preview widget.
        """
        options = {}
        pairs = re.findall(r"([\w-]+)\s*:\s*'([^']*)'", style_str)
        for key, value in pairs:
            if key == 'color':
                options['foreground'] = value
            elif key == 'font-size':
                try:
                    size = int(re.sub(r'\D', '', value))
                    font = tkFont.Font(font=self.display.preview_text.cget("font"))
                    font.configure(size=size)
                    options['font'] = font
                except ValueError:
                    pass
        self.display.preview_text.tag_configure(tag_name, **options)

    def render_preview(self):
        raw_content = self.display.raw_text.get("1.0", tk.END)
        try:
            haba_data = self.parser.parse(raw_content)
        except Exception as e:
            self.display.preview_text.config(state=tk.NORMAL)
            self.display.preview_text.delete('1.0', tk.END)
            self.display.preview_text.insert('1.0', f"Error parsing .haba file:\n{e}")
            self.display.preview_text.config(state=tk.DISABLED)
            return

        self.display.preview_text.config(state=tk.NORMAL)
        self.display.preview_text.delete("1.0", tk.END)

        content_lines = haba_data.content.split('\n')

        for i, line in enumerate(content_lines):
            tag_name = f"style_{i}"
            style_str = ""
            if i < len(haba_data.presentation_items):
                style_str = haba_data.presentation_items[i][1]

            self._apply_styles(style_str, tag_name)
            self.display.preview_text.insert(tk.END, line + "\n", (tag_name,))

        self.display.preview_text.config(state=tk.DISABLED)

        self.display.script_text.delete("1.0", tk.END)
        self.display.script_text.insert("1.0", haba_data.script)
        self.on_script_text_change()


def main():
    root = tk.Tk()
    root.geometry("1000x700")
    app = HabaEditor(master=root)
    app.mainloop()

if __name__ == '__main__':
    main()
