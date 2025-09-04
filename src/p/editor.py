import tkinter as tk
from tkinter import font as tkFont
import re

from haba_parser import HabaParser
from files import FileHandler
from display import Display
from menu import MenuBar

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

        # Application state
        self.language = 'javascript'
        self.current_filepath = None

        # Modular components
        # Note: The order of initialization can be important.
        self.file_handler = FileHandler(self)

        # UI components are initialized last, as they may need to reference the handlers.
        # Pass `self` as the master frame for the widgets.
        self.display = Display(self, self)
        self.menu_bar = MenuBar(self)

    # --- Delegating Methods ---

    def load_file(self):
        """Delegates file loading to the FileHandler."""
        self.file_handler.load_file()

    def save_file(self):
        """Delegates file saving to the FileHandler."""
        self.file_handler.save_file()

    # --- Core Application Logic / Event Handlers ---

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
        # Clear existing tags
        self.display.script_text.tag_remove("trailing_whitespace", "1.0", tk.END)
        self.display.script_text.tag_remove("missing_semicolon", "1.0", tk.END)

        lines = self.display.script_text.get("1.0", tk.END).splitlines()
        for i, line in enumerate(lines):
            line_num_str = f"{i + 1}.0"

            # Check for trailing whitespace
            if re.search(r'\s+$', line):
                self.display.script_text.tag_add("trailing_whitespace", f"{line_num_str}", f"{line_num_str} lineend")

            # Check for missing semicolon (basic heuristic)
            stripped_line = line.strip()
            if stripped_line and not stripped_line.startswith("//") and not stripped_line.endswith(("{", "}", ";")):
                self.display.script_text.tag_add("missing_semicolon", f"{line_num_str}", f"{line_num_str} lineend")

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
                    pass # Ignore invalid font sizes
        self.display.preview_text.tag_configure(tag_name, **options)

    def render_preview(self):
        raw_content = self.display.raw_text.get("1.0", tk.END)
        try:
            haba_data = self.parser.parse(raw_content)
        except Exception as e:
            # If parsing fails, show error in preview
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

        # Update script text editor and explorer panels
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
