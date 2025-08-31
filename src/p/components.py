import tkinter as tk
from tkinter import ttk
import re

class SymbolOutlinePanel(tk.Frame):
    """
    A panel to display an outline of symbols (functions, classes) found in the script.
    """
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.label = tk.Label(self, text="Symbol Outline")
        self.label.pack(fill=tk.X, padx=5, pady=2)
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True)

    def update_symbols(self, text_content):
        """
        Parses the text content for symbols and updates the listbox.
        """
        self.listbox.delete(0, tk.END)
        # Regex to find function declarations and class definitions in JavaScript
        symbol_pattern = re.compile(
            r"^(?:function\s+([a-zA-Z0-9_]+)\s*\(|class\s+([A-Z][a-zA-Z0-9_]*))",
            re.MULTILINE
        )
        for match in symbol_pattern.finditer(text_content):
            symbol_name = match.group(1) or match.group(2)
            if symbol_name:
                self.listbox.insert(tk.END, symbol_name)

class TodoExplorerPanel(tk.Frame):
    """
    A panel to display TODO and FIXME comments from the script.
    """
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.label = tk.Label(self, text="TODO/FIXME Explorer")
        self.label.pack(fill=tk.X, padx=5, pady=2)
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True)

    def update_todos(self, text_content):
        """
        Scans the text content for TODO/FIXME comments and updates the listbox.
        """
        self.listbox.delete(0, tk.END)
        todo_pattern = re.compile(r"//.*(TODO|FIXME):(.*)", re.IGNORECASE)
        for i, line in enumerate(text_content.splitlines()):
            match = todo_pattern.search(line)
            if match:
                self.listbox.insert(tk.END, f"{i+1}: {match.group(1).upper()}{match.group(2)}")
