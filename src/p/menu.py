import tkinter as tk
from tkinter import messagebox

class MenuBar:
    """
    Manages the creation of the menu bar and its associated commands for the QuantaDemoWindow.
    """
    def __init__(self, demo_window):
        """
        Initializes the MenuBar.

        Args:
            demo_window: An instance of the QuantaDemoWindow class.
        """
        self.demo = demo_window
        self.create_menu()

    def create_menu(self):
        """
        Creates the main menu bar for the demo window.
        """
        self.menubar = tk.Menu(self.demo.master)
        self.demo.master.config(menu=self.menubar)

        # --- File Menu ---
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Prompt", command=self.demo.new_prompt)
        file_menu.add_command(label="Load Prompt...", command=self.demo.load_prompt)
        file_menu.add_command(label="Save Prompt As...", command=self.demo.save_prompt)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.demo.master.quit)

        # --- Edit Menu ---
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=lambda: self.demo.prompt_text.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self.demo.prompt_text.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.demo.prompt_text.event_generate("<<Paste>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", command=self.demo.find_text)
        edit_menu.add_command(label="Replace...", command=self.demo.replace_text)

        # --- LLM Assistant Menu ---
        llm_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="LLM Assistant", menu=llm_menu)
        llm_menu.add_command(label="Process Next TODO", command=self.demo.process_next_task)
        llm_menu.add_separator()
        llm_menu.add_command(label="Start Automation", command=self.demo.start_automation)
        llm_menu.add_command(label="Stop Automation", command=self.demo.stop_automation)
        llm_menu.add_separator()
        llm_menu.add_command(label="Record Macro...", command=self.demo.record_macro)
        llm_menu.add_command(label="Edit Macro...", command=self.demo.edit_macro)
        llm_menu.add_command(label="Load Macro...", command=self.demo.load_macro)
        llm_menu.add_separator()
        llm_menu.add_command(label="Clear Console Log", command=self.demo.clear_console)
        llm_menu.add_command(label="Re-initialize Model", command=self.demo.initialize_model)

        # --- Help Menu ---
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="LLM Assistant Guide", command=self.show_llm_guide)
        help_menu.add_command(label="About", command=self.show_about)

    def show_llm_guide(self):
        messagebox.showinfo(
            "LLM Assistant Guide",
            "The LLM Assistant processes tasks in the Prompt Editor.\n\n"
            "1. Write tasks starting with 'TODO:'.\n"
            "2. Use 'Process Next TODO' to run one task.\n"
            "3. Use 'Start Automation' to run all tasks sequentially.\n"
            "4. The model will replace 'TODO:' with 'DONE:' upon completion."
        )

    def show_about(self):
        messagebox.showinfo(
            "About Quanta Haba Demo",
            "Quanta Haba Demo\n\nVersion 1.1\n\nA demonstration of a text editor with LLM-powered automation."
        )