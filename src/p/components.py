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
            'javascript': re.compile(r"^(?:function\s+([a-zA-Z0-9_]+)\s*\(|class\s+([A-Z][a-zA-Z0-9_]*)|(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*\(.*\)\s*=>)", re.MULTILINE),
            'java': re.compile(r"^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:class|interface)\s+([a-zA-Z0-9_]+)|(?:[a-zA-Z0-9_<>\[\]]+)\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*{", re.MULTILINE)
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
            'c_style': re.compile(r"//.*(TODO|FIXME):(.*)|/\*[\s\S]*?(TODO|FIXME):([\s\S]*?)\*/", re.IGNORECASE)
        }
        self.lang_map = {
            'python': 'python',
            'cpp': 'c_style',
            'javascript': 'c_style',
            'java': 'c_style'
        }

    def update_todos(self, text_content, language):
        """
        Scans the text content for TODO/FIXME comments and updates the listbox.
        """
        self.listbox.delete(0, tk.END)

        lang_type = self.lang_map.get(language)
        if not lang_type:
            return

        pattern = self.patterns.get(lang_type)
        if not pattern:
            return

        for match in pattern.finditer(text_content):
            line_num = text_content.count('\n', 0, match.start()) + 1

            if match.group(1):  # Matched // comment
                keyword = match.group(1)
                message = match.group(2)
            else:  # Matched /* */ comment
                keyword = match.group(3)
                message = match.group(4)

            # Clean up message from multi-line comments
            message = ' '.join(message.strip().replace('*/', '').split())
            self.listbox.insert(tk.END, f"{line_num}: {keyword.upper()}: {message}")