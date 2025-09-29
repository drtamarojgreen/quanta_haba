import tkinter as tk
from tkinter import ttk
import re

class SymbolOutlinePanel(tk.Frame):
    """
    A panel to display an outline of symbols based on the language.
    """
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.label = tk.Label(self, text="Symbol Outline")
        self.label.pack(fill=tk.X, padx=5, pady=2)
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True)

        self.patterns = {
            'python': re.compile(r"^\s*(?:def|class)\s+([a-zA-Z0-9_]+)", re.MULTILINE),
            'cpp': re.compile(r"^(?:class|struct)\s+([a-zA-Z0-9_]+)|(?:[a-zA-Z0-9_:]+)\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*(?:const)?\s*{", re.MULTILINE),
            'javascript': re.compile(r"^(?:function\s+([a-zA-Z0-9_]+)\s*\(|class\s+([A-Z][a-zA-Z0-9_]*))", re.MULTILINE)
        }

    def update_symbols(self, text_content, language):
        """
        Parses the text content for symbols and updates the listbox.
        """
        self.listbox.delete(0, tk.END)
        pattern = self.patterns.get(language)
        if not pattern:
            return

        for match in pattern.finditer(text_content):
            # Find the first non-empty group
            symbol_name = next((s for s in match.groups() if s), None)
            if symbol_name:
                self.listbox.insert(tk.END, symbol_name)

class TodoExplorerPanel(tk.Frame):
    """
    A panel to display TODO and FIXME comments based on the language.
    """
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.label = tk.Label(self, text="TODO/FIXME Explorer")
        self.label.pack(fill=tk.X, padx=5, pady=2)
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True)

        self.patterns = {
            'python': re.compile(r"#.*(TODO|FIXME):(.*)", re.IGNORECASE),
            'cpp': re.compile(r"//.*(TODO|FIXME):(.*)", re.IGNORECASE),
            'javascript': re.compile(r"//.*(TODO|FIXME):(.*)", re.IGNORECASE)
        }

    def update_todos(self, text_content, language):
        """
        Scans the text content for TODO/FIXME comments and updates the listbox.
        """
        self.listbox.delete(0, tk.END)
        pattern = self.patterns.get(language)
        if not pattern:
            return

        for i, line in enumerate(text_content.splitlines()):
            match = pattern.search(line)
            if match:
                self.listbox.insert(tk.END, f"{i+1}: {match.group(1).upper()}{match.group(2)}")
