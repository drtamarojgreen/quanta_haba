import tkinter as tk
from tkinter import messagebox

class MenuBar:
    """
    Manages the creation of the menu bar and its associated commands for the QuantaDemoWindow.
    """
    def __init__(self, window):
        """
        Initializes the MenuBar.

        Args:
            window: An instance of the HabaEditor or QuantaDemoWindow class.
        """
        self.window = window
        self.menubar = tk.Menu(self.window.master)
        self.window.master.config(menu=self.menubar)

        # Determine which menu to create based on the window type
        if type(self.window).__name__ == 'QuantaDemoWindow':
            self.create_demo_menu()
        else: # Default to HabaEditor menu
            self.language_var = tk.StringVar(value=self.window.language)
            self.create_editor_menu()

    def create_demo_menu(self):
        """Creates the menu for the QuantaDemoWindow."""
        # --- File Menu ---
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Prompt", command=self.window.new_prompt)
        file_menu.add_command(label="Load Prompt...", command=self.window.load_prompt)
        file_menu.add_command(label="Save Prompt As...", command=self.window.save_prompt)
        file_menu.add_separator()
        file_menu.add_command(label="Launch Code Editor", command=self.window.launch_haba_editor)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.window.master.quit)

        # --- Edit Menu ---
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=lambda: self.window.prompt_text.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self.window.prompt_text.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.window.prompt_text.event_generate("<<Paste>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", command=self.window.find_text)
        edit_menu.add_command(label="Replace...", command=self.window.replace_text)

        # --- LLM Assistant Menu ---
        llm_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="LLM Assistant", menu=llm_menu)
        llm_menu.add_command(label="Process Next TODO", command=self.window.process_next_task)
        llm_menu.add_separator()
        llm_menu.add_command(label="Start Automation", command=self.window.start_automation)
        llm_menu.add_command(label="Stop Automation", command=self.window.stop_automation)
        llm_menu.add_separator()
        llm_menu.add_checkbutton(label="Record Macro", onvalue=True, offvalue=False, variable=self.window.is_recording_macro, command=self.window.record_macro)
        llm_menu.add_command(label="Play Macro", command=self.window.play_macro)
        llm_menu.add_separator()
        llm_menu.add_command(label="Clear Console Log", command=self.window.clear_console)
        llm_menu.add_command(label="Re-initialize Model", command=self.window.initialize_model)

        # --- Help Menu ---
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="LLM Assistant Guide", command=self.show_llm_guide)
        help_menu.add_command(label="About", command=self.show_about_demo)

    def create_editor_menu(self):
        """Creates the menu for the HabaEditor."""
        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load", command=self.window.load_file)
        file_menu.add_command(label="Save", command=self.window.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.window.master.quit)

        # --- Edit Menu ---
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        # Note: HabaEditor doesn't have these methods yet, they would need to be implemented
        # edit_menu.add_command(label="Toggle Comment", command=self.window.toggle_comment, accelerator="Ctrl+/")
        # edit_menu.add_command(label="Sort Imports", command=self.window.sort_imports)
        # edit_menu.add_command(label="Upgrade String Formatting", command=self.window.upgrade_string_formatting)

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

    def set_language(self):
        """Calls the editor's method to update the language."""
        self.window.set_language(self.language_var.get())

    def show_llm_guide(self):
        messagebox.showinfo(
            "LLM Assistant Guide",
            "The LLM Assistant processes tasks in the Prompt Editor.\n\n"
            "1. Write tasks starting with 'TODO:'.\n"
            "2. Use 'Process Next TODO' to run one task.\n"
            "3. Use 'Start Automation' to run all tasks sequentially.\n"
            "4. The model will replace 'TODO:' with 'DONE:' upon completion."
        )

    def show_about_demo(self):
        messagebox.showinfo(
            "About Quanta Haba Demo",
            "Quanta Haba Demo\n\nVersion 1.2\n\nA demonstration of a text editor with LLM-powered automation."
        )

    # --- Git Feature Methods (should only be called from HabaEditor context) ---

    def show_llm_guide(self):
        messagebox.showinfo(
            "LLM Assistant Guide",
            "The LLM Assistant processes tasks in the Prompt Editor.\n\n"
            "1. Write tasks starting with 'TODO:'.\n"
            "2. Use 'Process Next TODO' to run one task.\n"
            "3. Use 'Start Automation' to run all tasks sequentially.\n"
            "4. The model will replace 'TODO:' with 'DONE:' upon completion."
        )

    def _show_git_status_dialog(self, status_text):
        status_window = tk.Toplevel(self.window.master)
        status_window.title("Git Status")
        status_window.geometry("600x400")

        text_widget = tk.Text(status_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, status_text)
        text_widget.config(state=tk.DISABLED)

        close_button = tk.Button(status_window, text="Close", command=status_window.destroy)
        close_button.pack(pady=10)

    def git_status(self):
        if not self.window.current_filepath:
            messagebox.showerror("Error", "No file opened. Please open a file in a git repository.")
            return

        repo_root = self._find_git_root(self.window.current_filepath)
        if not repo_root:
            messagebox.showerror("Error", "The current file is not in a git repository.")
            return

        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            status_output = result.stdout
            if not status_output:
                status_output = "Working tree clean."
            self._show_git_status_dialog(status_output)

        except FileNotFoundError:
            messagebox.showerror("Error", "Git command not found. Make sure git is installed and in your PATH.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error running git status:\n{e.stderr}")

    def git_stage_file(self):
        if not self.window.current_filepath:
            messagebox.showerror("Error", "No file opened. Please open a file to stage.")
            return

        repo_root = self._find_git_root(self.window.current_filepath)
        if not repo_root:
            messagebox.showerror("Error", "The current file is not in a git repository.")
            return

        try:
            filepath_to_stage = os.path.abspath(self.window.current_filepath)
            subprocess.run(
                ["git", "add", filepath_to_stage],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            messagebox.showinfo("Success", f"File '{os.path.basename(self.window.current_filepath)}' staged successfully.")

        except FileNotFoundError:
            messagebox.showerror("Error", "Git command not found. Make sure git is installed and in your PATH.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error staging file:\n{e.stderr}")

    def _show_commit_dialog(self, repo_root):
        commit_window = tk.Toplevel(self.window.master)
        commit_window.title("Git Commit")
        commit_window.geometry("500x300")

        label = tk.Label(commit_window, text="Enter commit message:")
        label.pack(pady=5)

        commit_message_text = tk.Text(commit_window, height=10, width=60)
        commit_message_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        def do_commit():
            commit_message = commit_message_text.get("1.0", tk.END).strip()
            if not commit_message:
                messagebox.showerror("Error", "Commit message cannot be empty.", parent=commit_window)
                return

            try:
                subprocess.run(
                    ["git", "commit", "-m", commit_message],
                    cwd=repo_root,
                    capture_output=True,
                    text=True,
                    check=True
                )
                commit_window.destroy()
                messagebox.showinfo("Success", "Changes committed successfully.")

            except FileNotFoundError:
                messagebox.showerror("Error", "Git command not found. Make sure git is installed and in your PATH.", parent=commit_window)
            except subprocess.CalledProcessError as e:
                if "nothing to commit" in e.stderr:
                    messagebox.showinfo("Info", e.stderr, parent=commit_window)
                else:
                    messagebox.showerror("Error", f"Error committing changes:\n{e.stderr}", parent=commit_window)

        button_frame = tk.Frame(commit_window)
        button_frame.pack(pady=10)

        commit_button = tk.Button(button_frame, text="Commit", command=do_commit)
        commit_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(button_frame, text="Cancel", command=commit_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=10)

    def git_commit(self):
        if not self.window.current_filepath:
            messagebox.showerror("Error", "No file opened. Please open a file in a git repository.")
            return

        repo_root = self._find_git_root(self.window.current_filepath)
        if not repo_root:
            messagebox.showerror("Error", "The current file is not in a git repository.")
            return

        self._show_commit_dialog(repo_root)

    def _show_git_log_dialog(self, log_text):
        log_window = tk.Toplevel(self.window.master)
        log_window.title("Git Log")
        log_window.geometry("800x600")

        text_frame = tk.Frame(log_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        text_widget = tk.Text(text_frame, wrap=tk.NONE)

        ys = tk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
        xs = tk.Scrollbar(text_frame, orient='horizontal', command=text_widget.xview)
        text_widget['yscrollcommand'] = ys.set
        text_widget['xscrollcommand'] = xs.set

        ys.pack(side=tk.RIGHT, fill=tk.Y)
        xs.pack(side=tk.BOTTOM, fill=tk.X)
        text_widget.pack(fill=tk.BOTH, expand=True)

        log_font = tkFont.Font(family="monospace", size=10)
        text_widget.config(font=log_font)

        text_widget.insert(tk.END, log_text)
        text_widget.config(state=tk.DISABLED)

        close_button = tk.Button(log_window, text="Close", command=log_window.destroy)
        close_button.pack(pady=10)

    def git_log(self):
        if not self.window.current_filepath:
            messagebox.showerror("Error", "No file opened. Please open a file in a git repository.")
            return

        repo_root = self._find_git_root(self.window.current_filepath)
        if not repo_root:
            messagebox.showerror("Error", "The current file is not in a git repository.")
            return

        try:
            result = subprocess.run(
                ["git", "log", "--graph", "--oneline", "--decorate", "--all"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            log_output = result.stdout
            if not log_output:
                log_output = "No commits in repository."
            self._show_git_log_dialog(log_output)

        except FileNotFoundError:
            messagebox.showerror("Error", "Git command not found. Make sure git is installed and in your PATH.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error getting git log:\n{e.stderr}")
