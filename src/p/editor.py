import tkinter as tk
from tkinter import ttk, filedialog, font as tkFont
import re
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

        # Modular components
        self.file_handler = FileHandler(self)
        self.display = Display(self, self) # Pass self (editor) and master frame
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
        self.lint_script_text()
        self.display.script_text.edit_modified(False)

    def lint_script_text(self):
        """
        Delegates linting to the lint_javascript function.
        """
        lint_javascript(self.display.script_text)

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
