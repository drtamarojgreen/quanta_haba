import tkinter as tk
from tkinter import messagebox, font as tkFont
import os
import subprocess

class MenuBar:
    """
    Manages the creation of the menu bar and its associated commands.
    """
    def __init__(self, editor):
        """
        Initializes the MenuBar.

        Args:
            editor: An instance of the HabaEditor class.
        """
        self.editor = editor
        self.language_var = tk.StringVar(value=self.editor.language)
        self.create_menu()

    def set_language(self):
        """Calls the editor's method to update the language."""
        self.editor.set_language(self.language_var.get())

    def create_menu(self):
        """
        Creates the main menu bar for the editor.
        """
        self.menubar = tk.Menu(self.editor.master)
        self.editor.master.config(menu=self.menubar)

        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load", command=self.editor.load_file)
        file_menu.add_command(label="Save", command=self.editor.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.editor.master.quit)

        # Language menu
        language_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Language", menu=language_menu)
        language_menu.add_radiobutton(label="JavaScript", variable=self.language_var, value='javascript', command=self.set_language)
        language_menu.add_radiobutton(label="Python", variable=self.language_var, value='python', command=self.set_language)

        # Edit menu
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Toggle Comment", command=self.editor.toggle_comment, accelerator="Ctrl+/")

        # Git menu
        git_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Git", menu=git_menu)
        git_menu.add_command(label="Status", command=self.git_status)
        git_menu.add_command(label="Stage Current File", command=self.git_stage_file)
        git_menu.add_command(label="Commit", command=self.git_commit)
        git_menu.add_command(label="Log", command=self.git_log)

    # --- Git Feature Methods ---

    def _find_git_root(self, path):
        if not path or not os.path.exists(os.path.dirname(os.path.abspath(path))):
            return None
        current_dir = os.path.dirname(os.path.abspath(path))
        while True:
            if ".git" in os.listdir(current_dir):
                return current_dir
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:  # Reached root
                return None
            current_dir = parent_dir

    def _show_git_status_dialog(self, status_text):
        status_window = tk.Toplevel(self.editor.master)
        status_window.title("Git Status")
        status_window.geometry("600x400")

        text_widget = tk.Text(status_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, status_text)
        text_widget.config(state=tk.DISABLED)

        close_button = tk.Button(status_window, text="Close", command=status_window.destroy)
        close_button.pack(pady=10)

    def git_status(self):
        if not self.editor.current_filepath:
            messagebox.showerror("Error", "No file opened. Please open a file in a git repository.")
            return

        repo_root = self._find_git_root(self.editor.current_filepath)
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
        if not self.editor.current_filepath:
            messagebox.showerror("Error", "No file opened. Please open a file to stage.")
            return

        repo_root = self._find_git_root(self.editor.current_filepath)
        if not repo_root:
            messagebox.showerror("Error", "The current file is not in a git repository.")
            return

        try:
            filepath_to_stage = os.path.abspath(self.editor.current_filepath)
            subprocess.run(
                ["git", "add", filepath_to_stage],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            messagebox.showinfo("Success", f"File '{os.path.basename(self.editor.current_filepath)}' staged successfully.")

        except FileNotFoundError:
            messagebox.showerror("Error", "Git command not found. Make sure git is installed and in your PATH.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error staging file:\n{e.stderr}")

    def _show_commit_dialog(self, repo_root):
        commit_window = tk.Toplevel(self.editor.master)
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
        if not self.editor.current_filepath:
            messagebox.showerror("Error", "No file opened. Please open a file in a git repository.")
            return

        repo_root = self._find_git_root(self.editor.current_filepath)
        if not repo_root:
            messagebox.showerror("Error", "The current file is not in a git repository.")
            return

        self._show_commit_dialog(repo_root)

    def _show_git_log_dialog(self, log_text):
        log_window = tk.Toplevel(self.editor.master)
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
        if not self.editor.current_filepath:
            messagebox.showerror("Error", "No file opened. Please open a file in a git repository.")
            return

        repo_root = self._find_git_root(self.editor.current_filepath)
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
