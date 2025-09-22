import tkinter as tk
from tkinter import ttk, filedialog, font as tkFont
import re
import os
from .haba_parser import HabaParser, HabaData
from .files import FileHandler
from .display import Display
from .menu import MenuBar
from .script_runner import ScriptRunner, run_python_script
from .linter import lint_javascript

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
        script_content = self.display.script_text.get("1.0", tk.END)
        self.display.symbol_outline_panel.update_symbols(script_content, self.language)
        self.display.todo_explorer_panel.update_todos(script_content, self.language)

        if self.language == 'python':
            self._highlight_decorators(self.display.script_text)
            self._highlight_trailing_whitespace(self.display.script_text)
        else:
            # Clear python-specific tags if switching away from python
            self.display.script_text.tag_remove("decorator", "1.0", tk.END)
            self.display.script_text.tag_remove("trailing_whitespace", "1.0", tk.END)
            self.lint_script_text()

        self.display.script_text.edit_modified(False)

    def lint_script_text(self):
        """
        Delegates linting to the lint_javascript function.
        """
        lint_javascript(self.display.script_text)

    def _highlight_decorators(self, text_widget):
        """
        Applies syntax highlighting for Python decorators.
        """
        # Remove any existing tags first
        text_widget.tag_remove("decorator", "1.0", tk.END)

        # Get all lines of text
        lines = text_widget.get("1.0", tk.END).splitlines()

        for i, line in enumerate(lines):
            # Simple regex to find lines starting with a decorator
            if re.match(r"^\s*@", line):
                line_num = i + 1
                text_widget.tag_add("decorator", f"{line_num}.0", f"{line_num}.end")

    def _highlight_trailing_whitespace(self, text_widget):
        """
        Finds and highlights trailing whitespace on each line.
        """
        text_widget.tag_remove("trailing_whitespace", "1.0", tk.END)

        lines = text_widget.get("1.0", tk.END).splitlines()
        for i, line in enumerate(lines):
            match = re.search(r'(\s+)$', line)
            if match:
                line_num = i + 1
                start_col = match.start(1)
                end_col = match.end(1)
                text_widget.tag_add("trailing_whitespace", f"{line_num}.{start_col}", f"{line_num}.{end_col}")

    def _check_magic_comment(self, text_widget):
        """
        Checks for misplaced magic encoding comments and applies a warning tag.
        """
        text_widget.tag_remove("magic_comment_warning", "1.0", tk.END)
        lines = text_widget.get("1.0", tk.END).splitlines()

        # PEP 263: The encoding comment must be on line 1 or 2
        for i, line in enumerate(lines):
            line_num = i + 1
            if re.search(r"# -\*- coding: .*- -\*-", line):
                if line_num > 2:
                    text_widget.tag_add("magic_comment_warning", f"{line_num}.0", f"{line_num}.end")

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
                self._generate_docstring_stub()

    def _generate_docstring_stub(self):
        """
        If the cursor is on a line after a function definition, this method
        generates and inserts a docstring stub.
        """
        text_widget = self.display.script_text
        cursor_index = text_widget.index(tk.INSERT)
        line_num, col_num = map(int, cursor_index.split('.'))

        # Get the previous line which should contain the function definition
        if line_num <= 1:
            return

        prev_line_text = text_widget.get(f"{line_num - 1}.0", f"{line_num - 1}.end")

        # Regex to parse function definition
        match = re.search(r"^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\):", prev_line_text)
        if not match:
            return

        func_name = match.group(1)
        args_str = match.group(2)

        # Clean up and split arguments, removing type hints and default values for simplicity
        params = [p.split('=')[0].split(':')[0].strip() for p in args_str.split(',') if p.strip() and p.strip() != 'self']

        # Build the docstring
        indent = re.match(r"^\s*", prev_line_text).group(0)
        stub = f'{indent}"""{func_name}: One-line summary of the function.\n\n'
        if params:
            stub += f"{indent}Args:\n"
            for param in params:
                stub += f"{indent}    {param}: Description of the parameter.\n"

        stub += f"\n{indent}Returns:\n{indent}    Description of the return value.\n"
        stub += f'{indent}"""'

        # Replace the triple quotes with the full stub
        text_widget.delete(f"{line_num}.0", f"{line_num}.end")
        text_widget.insert(f"{line_num}.0", stub)

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

    def _find_and_highlight_matching_bracket(self, event=None):
        """
        Finds and highlights the matching bracket to the one under the cursor.
        """
        text_widget = self.display.script_text
        text_widget.tag_remove("bracket_match", "1.0", "end")

        # Check the character immediately before the cursor
        cursor_index = text_widget.index(tk.INSERT)
        char_before_index = f"{cursor_index}-1c"
        char = text_widget.get(char_before_index)

        pairs = {'(': ')', '[': ']', '{': '}'}

        if char in pairs:  # It's an opening bracket, search forward
            match_char = pairs[char]
            direction = 1
        elif char in pairs.values():  # It's a closing bracket, search backward
            match_char = [k for k, v in pairs.items() if v == char][0]
            direction = -1
        else:
            return # Not a bracket

        balance = direction
        search_index = text_widget.index(f"{char_before_index} + {direction}c")

        while True:
            if direction == 1 and text_widget.compare(search_index, ">=", "end"):
                break
            if direction == -1 and text_widget.compare(search_index, "<", "1.0"):
                break

            current_char = text_widget.get(search_index)
            if current_char == char:
                balance += direction
            elif current_char == match_char:
                balance -= direction

            if balance == 0:
                text_widget.tag_add("bracket_match", char_before_index, f"{char_before_index}+1c")
                text_widget.tag_add("bracket_match", search_index, f"{search_index}+1c")
                break

            search_index = text_widget.index(f"{search_index} + {direction}c")

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
