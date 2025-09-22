import tkinter as tk
from tkinter import ttk
from .components import SymbolOutlinePanel, TodoExplorerPanel

class Display:
    """
    Manages the creation of the main UI components for the Haba Editor.
    """
    def __init__(self, editor, master, virtual_env=None):
        """
        Initializes the Display.
        Args:
            editor: An instance of the HabaEditor class.
            master: The root tkinter widget.
            virtual_env (str, optional): The name of the detected virtual environment.
        """
        self.editor = editor
        self.master = master
        self.virtual_env = virtual_env
        self.create_widgets()

    def create_widgets(self):
        """
        Creates and packs all the UI widgets for the editor.
        """
        # Top frame for buttons
        top_frame = tk.Frame(self.master)
        top_frame.pack(fill=tk.X, padx=5, pady=5)

        self.load_button = tk.Button(top_frame, text="Load", command=self.editor.load_file)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(top_frame, text="Save", command=self.editor.save_file)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.render_button = tk.Button(top_frame, text="Render", command=self.editor.render_preview)
        self.render_button.pack(side=tk.LEFT, padx=5)

        self.lint_button = tk.Button(top_frame, text="Lint", command=self.editor.lint_script_text)
        self.lint_button.pack(side=tk.LEFT, padx=5)

        self.run_button = tk.Button(top_frame, text="Run Script", command=self.editor.run_script)
        self.run_button.pack(side=tk.LEFT, padx=5)

        # Main content area with three panels
        main_paned_window = tk.PanedWindow(self.master, orient=tk.VERTICAL)
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
        self.raw_text.bind("<<Modified>>", self.editor.on_text_change)
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

        # Console Output Tab
        console_frame = tk.Frame(right_notebook)
        self.console_output_text = tk.Text(console_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.console_output_text.pack(fill=tk.BOTH, expand=True)
        right_notebook.add(console_frame, text="Console Output")

        # Actionable Tasks Tab
        tasks_frame = tk.Frame(right_notebook)
        self.tasks_listbox = tk.Listbox(tasks_frame)
        self.tasks_listbox.pack(fill=tk.BOTH, expand=True)
        right_notebook.add(tasks_frame, text="Actionable Tasks")

        # Bottom panel for script editing
        script_frame = tk.Frame(main_paned_window)
        script_label = tk.Label(script_frame, text="Script Layer (.js)")
        script_label.pack(anchor=tk.W)
        self.script_text = tk.Text(script_frame, wrap=tk.WORD, undo=True)
        self.script_text.pack(fill=tk.BOTH, expand=True)
        self.script_text.bind("<<Modified>>", self.editor.on_script_text_change)
        self.script_text.bind("<KeyRelease-quotedbl>", self.editor.on_quote_release)
        main_paned_window.add(script_frame, stretch="always")

        # Configure tags for linting
        self.script_text.tag_configure("trailing_whitespace", background="orange red")
        self.script_text.tag_configure("missing_semicolon", background="yellow")
        self.script_text.tag_configure("use_of_var", background="#FFDDC1")
        self.script_text.tag_configure("use_of_double_equals", background="#C1FFD7")
        self.script_text.tag_configure("long_line", background="#E0E0E0")
        self.script_text.tag_configure("many_parameters", background="#FFC1F5")

        # Status bar
        status_bar = tk.Frame(self.master, bd=1, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        if self.virtual_env:
            venv_text = f"venv: {self.virtual_env}"
        else:
            venv_text = "venv: None"

        self.venv_label = tk.Label(status_bar, text=venv_text, relief=tk.FLAT, anchor=tk.W)
        self.venv_label.pack(side=tk.LEFT, padx=5)
