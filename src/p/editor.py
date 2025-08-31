import tkinter as tk
from tkinter import ttk, filedialog, font as tkFont
from haba_parser import HabaParser, HabaData
from components import SymbolOutlinePanel, TodoExplorerPanel
import re

class HabaEditor(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Haba Editor")
        self.pack(fill=tk.BOTH, expand=True)
        self.parser = HabaParser()
        self.create_widgets()

    def create_widgets(self):
        # Top frame for buttons
        top_frame = tk.Frame(self)
        top_frame.pack(fill=tk.X, padx=5, pady=5)

        self.load_button = tk.Button(top_frame, text="Load", command=self.load_file)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(top_frame, text="Save", command=self.save_file)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.render_button = tk.Button(top_frame, text="Render", command=self.render_preview)
        self.render_button.pack(side=tk.LEFT, padx=5)

        self.lint_button = tk.Button(top_frame, text="Lint", command=self.lint_script_text)
        self.lint_button.pack(side=tk.LEFT, padx=5)

        # Main content area with three panels
        main_paned_window = tk.PanedWindow(self, orient=tk.VERTICAL)
        main_paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Top pane with two horizontal panels for raw text and preview
        top_paned_window = tk.PanedWindow(main_paned_window, orient=tk.HORIZONTAL)
        main_paned_window.add(top_paned_window, stretch="always")

        # Left panel for raw text editing
        left_frame = tk.Frame(top_paned_window)
        raw_label = tk.Label(left_frame, text="Raw .haba Text")
        raw_label.pack(anchor=tk.W)
        self.raw_text = tk.Text(left_frame, wrap=tk.WORD, undo=True)
        self.raw_text.pack(fill=tk.BOTH, expand=True)
        self.raw_text.bind("<<Modified>>", self.on_text_change)
        top_paned_window.add(left_frame, stretch="always")

        # Right panel with a notebook for different views
        right_notebook = ttk.Notebook(top_paned_window)
        top_paned_window.add(right_notebook, stretch="always")

        # WYSIWYG Preview Tab
        preview_frame = tk.Frame(right_notebook)
        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        right_notebook.add(preview_frame, text="WYSIWYG Preview")

        # Symbol Outline Tab
        self.symbol_outline_panel = SymbolOutlinePanel(right_notebook)
        right_notebook.add(self.symbol_outline_panel, text="Symbol Outline")

        # TODO Explorer Tab
        self.todo_explorer_panel = TodoExplorerPanel(right_notebook)
        right_notebook.add(self.todo_explorer_panel, text="TODO Explorer")

        # Bottom panel for script editing
        script_frame = tk.Frame(main_paned_window)
        script_label = tk.Label(script_frame, text="Script Layer (.js)")
        script_label.pack(anchor=tk.W)
        self.script_text = tk.Text(script_frame, wrap=tk.WORD, undo=True)
        self.script_text.pack(fill=tk.BOTH, expand=True)
        self.script_text.bind("<<Modified>>", self.on_script_text_change)
        main_paned_window.add(script_frame, stretch="always")

        # Configure tags for linting
        self.script_text.tag_configure("trailing_whitespace", background="orange red")
        self.script_text.tag_configure("missing_semicolon", background="yellow")

    def on_text_change(self, event=None):
        self.render_preview()
        self.raw_text.edit_modified(False)

    def on_script_text_change(self, event=None):
        if not self.script_text.edit_modified():
            return
        script_content = self.script_text.get("1.0", tk.END)
        self.symbol_outline_panel.update_symbols(script_content)
        self.todo_explorer_panel.update_todos(script_content)
        self.lint_script_text()
        self.script_text.edit_modified(False)

    def lint_script_text(self):
        # Clear existing tags
        self.script_text.tag_remove("trailing_whitespace", "1.0", tk.END)
        self.script_text.tag_remove("missing_semicolon", "1.0", tk.END)

        lines = self.script_text.get("1.0", tk.END).splitlines()
        for i, line in enumerate(lines):
            line_num_str = f"{i + 1}.0"

            # Check for trailing whitespace
            if re.search(r'\s+$', line):
                self.script_text.tag_add("trailing_whitespace", f"{line_num_str}", f"{line_num_str} lineend")

            # Check for missing semicolon (basic heuristic)
            stripped_line = line.strip()
            if stripped_line and not stripped_line.startswith("//") and not stripped_line.endswith(("{", "}", ";")):
                self.script_text.tag_add("missing_semicolon", f"{line_num_str}", f"{line_num_str} lineend")

    def load_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Haba Files", "*.haba"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        with open(filepath, "r") as f:
            content = f.read()
        self.raw_text.delete("1.0", tk.END)
        self.raw_text.insert("1.0", content)
        self.render_preview()

    def save_file(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension="haba",
            filetypes=[("Haba Files", "*.haba"), ("All Files", "*.*")],
        )
        if not filepath:
            return

        # Parse the raw text to get the content and presentation layers
        raw_content = self.raw_text.get("1.0", tk.END)
        haba_data = self.parser.parse(raw_content)

        # Get the script content from the script editor
        script_content = self.script_text.get("1.0", tk.END)
        haba_data.script = script_content.strip()

        # Build the final .haba content string
        final_content = self.parser.build(haba_data)

        with open(filepath, "w") as f:
            f.write(final_content)

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
                    font = tkFont.Font(font=self.preview_text.cget("font"))
                    font.configure(size=size)
                    options['font'] = font
                except ValueError:
                    pass # Ignore invalid font sizes
        self.preview_text.tag_configure(tag_name, **options)

    def render_preview(self):
        raw_content = self.raw_text.get("1.0", tk.END)
        try:
            haba_data = self.parser.parse(raw_content)
        except Exception as e:
            # If parsing fails, show error in preview
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete('1.0', tk.END)
            self.preview_text.insert('1.0', f"Error parsing .haba file:\n{e}")
            self.preview_text.config(state=tk.DISABLED)
            return

        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)

        content_lines = haba_data.content.split('\n')

        for i, line in enumerate(content_lines):
            tag_name = f"style_{i}"
            style_str = ""
            if i < len(haba_data.presentation_items):
                # Using the style from the presentation item tuple (container, style)
                style_str = haba_data.presentation_items[i][1]

            # Configure the tag for this line
            self._apply_styles(style_str, tag_name)

            # Insert the line with its corresponding tag
            self.preview_text.insert(tk.END, line + "\n", (tag_name,))

        self.preview_text.config(state=tk.DISABLED)

        # Update script text editor and explorer panels
        self.script_text.delete("1.0", tk.END)
        self.script_text.insert("1.0", haba_data.script)
        self.on_script_text_change()


def main():
    root = tk.Tk()
    root.geometry("1000x700")
    app = HabaEditor(master=root)
    app.mainloop()

if __name__ == '__main__':
    main()
