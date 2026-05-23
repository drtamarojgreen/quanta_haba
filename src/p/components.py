import tkinter as tk
from tkinter import ttk
import re

SYMBOL_PATTERNS = {
    'python': re.compile(r"^\s*(?:def|class)\s+([a-zA-Z0-9_]+)", re.MULTILINE),
    'cpp': re.compile(r"^(?:class|struct)\s+([a-zA-Z0-9_]+)|(?:[a-zA-Z0-9_:]+)\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*(?:const)?\s*{", re.MULTILINE),
    'javascript': re.compile(r"^(?:function\s+([a-zA-Z0-9_]+)\s*\(|class\s+([A-Z][a-zA-Z0-9_]*)|(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*\(.*\)\s*=>)", re.MULTILINE),
    'java': re.compile(r"^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:class|interface)\s+([a-zA-Z0-9_]+)|(?:[a-zA-Z0-9_<>\[\]]+)\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*{", re.MULTILINE)
}

def extract_symbols(text_content, language):
    """
    Exposed logic for symbol extraction to support headless testing.
    """
    symbols = []
    pattern = SYMBOL_PATTERNS.get(language)
    if not pattern:
        return symbols

    for match in pattern.finditer(text_content):
        symbol_name = next((s for s in match.groups() if s), None)
        if symbol_name:
            symbols.append(symbol_name)
    return symbols

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

    def update_symbols(self, text_content, language):
        """
        Parses the text content for symbols and updates the listbox.
        """
        self.listbox.delete(0, tk.END)
        symbols = extract_symbols(text_content, language)
        for symbol in symbols:
            self.listbox.insert(tk.END, symbol)

TODO_PATTERNS = {
    'python': re.compile(r"#.*(TODO|FIXME):(.*)", re.IGNORECASE),
    'c_style': re.compile(r"//.*(TODO|FIXME):(.*)|/\*[\s\S]*?(TODO|FIXME):([\s\S]*?)\*/", re.IGNORECASE)
}
TODO_LANG_MAP = {
    'python': 'python',
    'cpp': 'c_style',
    'javascript': 'c_style',
    'java': 'c_style'
}

def extract_todos(text_content, language):
    """
    Exposed logic for TODO extraction to support headless testing.
    """
    todos = []
    lang_type = TODO_LANG_MAP.get(language)
    if not lang_type:
        return todos

    pattern = TODO_PATTERNS.get(lang_type)
    if not pattern:
        return todos

    for match in pattern.finditer(text_content):
        line_num = text_content.count('\n', 0, match.start()) + 1

        if match.group(1):  # Matched // comment
            keyword = match.group(1)
            message = match.group(2)
        else:  # Matched /* */ comment
            keyword = match.group(3)
            message = match.group(4)

        message = ' '.join(message.strip().replace('*/', '').split())
        todos.append(f"{line_num}: {keyword.upper()}: {message}")
    return todos

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

    def update_todos(self, text_content, language):
        """
        Scans the text content for TODO/FIXME comments and updates the listbox.
        """
        self.listbox.delete(0, tk.END)
        todos = extract_todos(text_content, language)
        for todo in todos:
            self.listbox.insert(tk.END, todo)