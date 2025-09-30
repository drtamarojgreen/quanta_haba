import tkinter as tk
from tkinter import ttk, filedialog, font as tkFont, messagebox
import re
import os
import sys
import json
import numpy as np
try:
    from quanta_tissu.tisslm.core.model import QuantaTissu
    from quanta_tissu.tisslm.core.tokenizer import Tokenizer
    from quanta_tissu.tisslm.core.generate_text import generate_text
    QUANTA_TISSU_AVAILABLE = True
except ImportError:
    QUANTA_TISSU_AVAILABLE = False

# Handle both relative and absolute imports
try:
    from .menu import MenuBar
    from .haba_parser import HabaParser, HabaData
    from .components import SymbolOutlinePanel, TodoExplorerPanel
    from .script_runner import ScriptRunner
    from .html_exporter import HtmlExporter
    from .oauth_client import OAuthClient
    from .config_manager import ConfigManager
except ImportError:
    from menu import MenuBar
    from haba_parser import HabaParser, HabaData
    from components import SymbolOutlinePanel, TodoExplorerPanel
    from script_runner import ScriptRunner
    from html_exporter import HtmlExporter
    from oauth_client import OAuthClient
    from config_manager import ConfigManager


class QuantaDemoWindow(tk.Toplevel):
    def __init__(self, master=None, external_model_client=None):
        super().__init__(master)
        self.title("Quanta Haba Demo")
        self.geometry("1000x700")
        
        # Initialize managers and variables
        self.config_manager = ConfigManager()
        self.model = None
        self.tokenizer = None
        self.work_products = []
        self.is_automating = False
        self.is_recording_macro = tk.BooleanVar(value=False)
        self.recorded_macro = []
        self.external_model_client = external_model_client
        self.active_profile_name = None

        # Create widgets first, then initialize model
        self.create_widgets()
        self.initialize_model()
        self.menu_bar = MenuBar(self)
        
        # Start demo after everything is set up
        self.after(500, self.start_quanta_demo)

    def initialize_model(self):
        if not QUANTA_TISSU_AVAILABLE:
            self.log_to_console("Error: `quanta_tissu` package not found. Demo will use stubbed responses.")
            return

        # Get the absolute path to the configuration directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        config_dir = os.path.join(project_root, "configuration")
        
        TOKENIZER_PATH = config_dir  # The tokenizer files are in the configuration directory
        CHECKPOINT_PATH = os.path.join(config_dir, "quanta_tissu.npz")
        CONFIG_PATH = os.path.join(config_dir, "model_config.json")

        try:
            with open(CONFIG_PATH, 'r') as f:
                model_config = json.load(f)

            self.tokenizer = Tokenizer(tokenizer_path=TOKENIZER_PATH)
            model_config["vocab_size"] = self.tokenizer.get_vocab_size()
            self.model = QuantaTissu(model_config)
            self.model.load_weights(CHECKPOINT_PATH)
            self.log_to_console("Quanta Tissu model initialized successfully.")
        except FileNotFoundError as e:
            self.log_to_console(f"Model Error: {e}. Check paths. Demo will use stubbed responses.")
            self.model = None
            self.tokenizer = None
        except Exception as e:
            self.log_to_console(f"An unexpected error occurred during model initialization: {e}")
            self.model = None
            self.tokenizer = None


    def create_widgets(self):
        # Main content area with three panels
        main_paned_window = tk.PanedWindow(self, orient=tk.VERTICAL, sashrelief=tk.RAISED)
        main_paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Top pane with two horizontal panels
        top_paned_window = tk.PanedWindow(main_paned_window, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        main_paned_window.add(top_paned_window, stretch="always", height=400)

        # Left panel for prompt editing
        left_frame = tk.Frame(top_paned_window)
        prompt_label = tk.Label(left_frame, text="Prompt Editor")
        prompt_label.pack(anchor=tk.W)
        self.prompt_text = tk.Text(left_frame, wrap=tk.WORD, undo=True)
        self.prompt_text.pack(fill=tk.BOTH, expand=True)
        self.prompt_text.tag_configure("highlight", background="yellow")
        self.prompt_text.bind("<KeyPress>", self._handle_key_press)
        top_paned_window.add(left_frame, stretch="always", width=450)

        # Right panel for model responses
        right_frame = tk.Frame(top_paned_window)
        responses_label = tk.Label(right_frame, text="Model Responses")
        responses_label.pack(anchor=tk.W)
        self.dashboard_listbox = tk.Listbox(right_frame)
        self.dashboard_listbox.pack(fill=tk.BOTH, expand=True)
        top_paned_window.add(right_frame, stretch="always", width=450)

        # Bottom panel for console logs
        console_frame = tk.Frame(main_paned_window)
        console_label = tk.Label(console_frame, text="Console Log")
        console_label.pack(anchor=tk.W)
        self.console_log = tk.Text(console_frame, wrap=tk.WORD, state=tk.DISABLED, height=8)
        self.console_log.pack(fill=tk.BOTH, expand=True)
        main_paned_window.add(console_frame, stretch="always")
        
        # Initialize work products storage
        self.work_products = []

    def log_to_console(self, message):
        """Log a message to the console panel."""
        if not hasattr(self, 'console_log'):
            return
        self.console_log.config(state=tk.NORMAL)
        self.console_log.insert(tk.END, message + "\n")
        self.console_log.see(tk.END)
        self.console_log.config(state=tk.DISABLED)

    def start_quanta_demo(self):
        self.log_to_console("Starting Quanta Haba Demo...")
        self.load_prompt()

    def process_next_task(self, automated=False):
        if not self.is_automating and automated:
            return # Stop if automation was turned off

        content = self.prompt_text.get("1.0", tk.END)
        lines = content.splitlines()

        task_line_index = -1
        for i, line in enumerate(lines):
            if line.strip().startswith("TODO:"):
                task_line_index = i
                break

        if task_line_index == -1:
            self.log_to_console("All tasks completed!")
            self.is_automating = False
            return

        line_text = lines[task_line_index]
        task = line_text.strip().replace("TODO:", "").strip()
        line_num_str = f"{task_line_index + 1}"

        self.prompt_text.tag_remove("highlight", "1.0", tk.END)
        self.prompt_text.tag_add("highlight", f"{line_num_str}.0", f"{line_num_str}.end")
        self.log_to_console(f"Processing task: {task}")

        self.call_quanta_model(task, task_line_index)

        if self.is_automating:
            self.after(1000, self.process_next_task, True)

    def call_quanta_model(self, task, line_index):
        import datetime
        
        model_response = f"Stubbed response for '{task}'"
        is_stubbed = True

        # Try external model first if available and authenticated
        if self.external_model_client and self.external_model_client.is_authenticated():
            try:
                self.log_to_console("Calling external model...")
                response_data = self.external_model_client.call_model(task)
                # Handle different response formats
                if 'choices' in response_data:
                    model_response = response_data['choices'][0].get('text', 'No response text found.')
                elif 'response' in response_data:
                    model_response = response_data['response']
                elif 'text' in response_data:
                    model_response = response_data['text']
                else:
                    model_response = str(response_data)
                is_stubbed = False
                self.log_to_console("External model call successful.")
            except Exception as e:
                self.log_to_console(f"External model error: {e}. Falling back.")
                model_response = f"External model failed: {e}"
                is_stubbed = True

        # Fallback to local model
        elif self.model and self.tokenizer:
            try:
                self.log_to_console("Calling local Quanta Tissu model...")
                model_response = generate_text(
                    model=self.model,
                    tokenizer=self.tokenizer,
                    prompt=task,
                    length=50
                )
                is_stubbed = False
            except Exception as e:
                model_response = f"Stubbed response for '{task}'"
                is_stubbed = True
        else:
            # This is the final fallback
            self.log_to_console("No models available. Using stubbed response.")

        # Create work product entry
        work_product = {
            "id": len(self.work_products) + 1,
            "timestamp": datetime.datetime.now().isoformat(),
            "task": task,
            "prompt": task,
            "model_response": model_response,
            "toolkit_result": f"Processed: {model_response}",
            "status": "completed",
            "is_stubbed": is_stubbed,
            "line_index": line_index
        }
        
        # Add to work products and log to console
        self.work_products.append(work_product)
        
        # Log to console
        self.log_to_console(f"  > Prompt sent: '{task}'")
        self.log_to_console(f"  > Model response: '{model_response}'")
        self.log_to_console(f"  > Toolkit result: 'Processed: {model_response}'")
        
        # Update dashboard
        status_icon = "✓" if not is_stubbed else "⚠"
        self.dashboard_listbox.insert(tk.END, f"{status_icon} {task} → {model_response}")

        # Update prompt text
        line_num_str = f"{line_index + 1}"
        original_line = self.prompt_text.get(f"{line_num_str}.0", f"{line_num_str}.end")
        new_line = original_line.replace("TODO:", "DONE:", 1)
        self.prompt_text.delete(f"{line_num_str}.0", f"{line_num_str}.end")
        self.prompt_text.insert(f"{line_num_str}.0", new_line)

    # --- Menu Commands ---
    def new_prompt(self):
        self.prompt_text.delete("1.0", tk.END)
        self.log_to_console("New prompt created.")

    def load_prompt(self, filepath=None):
        if not filepath:
            filepath = filedialog.askopenfilename(
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                title="Load Prompt"
            )
        if not filepath:
            # Try loading default if user cancels dialog
            try:
                filepath = os.path.join(os.path.dirname(__file__), 'default_prompt.txt')
            except FileNotFoundError:
                self.log_to_console("Load cancelled. No default prompt found.")
                return

        try:
            with open(filepath, "r") as f:
                content = f.read()
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert("1.0", content)
            self.log_to_console(f"Loaded prompt file: {filepath}")
        except FileNotFoundError:
            self.log_to_console(f"Error: '{os.path.basename(filepath)}' not found.")
        except Exception as e:
            self.log_to_console(f"Error loading file: {e}")


    def save_prompt(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save Prompt As"
        )
        if not filepath:
            return
        try:
            with open(filepath, "w") as f:
                f.write(self.prompt_text.get("1.0", tk.END))
            self.log_to_console(f"Prompt saved to: {filepath}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file:\n{e}")

    def find_text(self):
        # Simple find dialog
        dialog = tk.Toplevel(self)
        dialog.title("Find")
        tk.Label(dialog, text="Find:").pack(side=tk.LEFT, padx=5, pady=5)
        entry = tk.Entry(dialog)
        entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        def find():
            term = entry.get()
            if term:
                self.prompt_text.tag_remove('found', '1.0', tk.END)
                start_pos = '1.0'
                while True:
                    start_pos = self.prompt_text.search(term, start_pos, stopindex=tk.END)
                    if not start_pos:
                        break
                    end_pos = f"{start_pos}+{len(term)}c"
                    self.prompt_text.tag_add('found', start_pos, end_pos)
                    start_pos = end_pos
                self.prompt_text.tag_config('found', background='yellow')
            dialog.destroy()

        button = tk.Button(dialog, text="Find", command=find)
        button.pack(padx=5, pady=5)
        entry.focus_set()

    def replace_text(self):
        # Simple replace dialog
        dialog = tk.Toplevel(self)
        dialog.title("Replace")
        tk.Label(dialog, text="Find:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        find_entry = tk.Entry(dialog, width=40)
        find_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(dialog, text="Replace:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        replace_entry = tk.Entry(dialog, width=40)
        replace_entry.grid(row=1, column=1, padx=5, pady=5)

        def replace():
            find_term = find_entry.get()
            replace_term = replace_entry.get()
            if find_term:
                content = self.prompt_text.get('1.0', tk.END)
                new_content = content.replace(find_term, replace_term)
                self.prompt_text.delete('1.0', tk.END)
                self.prompt_text.insert('1.0', new_content)
            dialog.destroy()

        button = tk.Button(dialog, text="Replace All", command=replace)
        button.grid(row=2, column=1, pady=10, sticky="e")
        find_entry.focus_set()

    def start_automation(self):
        if self.is_automating:
            return
        self.is_automating = True
        self.log_to_console("Starting automation...")
        self.process_next_task(automated=True)

    def stop_automation(self):
        self.is_automating = False
        self.log_to_console("Automation stopped.")

    def clear_console(self):
        self.console_log.config(state=tk.NORMAL)
        self.console_log.delete("1.0", tk.END)
        self.console_log.config(state=tk.DISABLED)

    def record_macro(self):
        self.is_recording_macro.set(not self.is_recording_macro.get())
        if self.is_recording_macro.get():
            self.recorded_macro = []
            self.log_to_console("Macro recording started.")
        else:
            self.log_to_console(f"Macro recording stopped. {len(self.recorded_macro)} actions recorded.")

    def _handle_key_press(self, event):
        if self.is_recording_macro.get():
            # Record character insertion
            if event.char and event.char.isprintable():
                self.recorded_macro.append(('insert', self.prompt_text.index(tk.INSERT), event.char))
            # Record backspace
            elif event.keysym == 'BackSpace':
                # Get the index before the deletion occurs
                index = self.prompt_text.index(tk.INSERT)
                if self.prompt_text.tag_ranges(tk.SEL):
                    # If there's a selection, record deletion of the selection
                    start, end = self.prompt_text.tag_ranges(tk.SEL)
                    self.recorded_macro.append(('delete', start, end))
                else:
                    # Record deletion of a single character
                    self.recorded_macro.append(('delete', f"{index}-1c", index))
            # Record newline
            elif event.keysym == 'Return':
                self.recorded_macro.append(('insert', self.prompt_text.index(tk.INSERT), '\n'))

    def edit_macro(self):
        messagebox.showinfo("Not Implemented", "Edit Macro feature is not yet implemented.")

    def load_macro(self):
        messagebox.showinfo("Not Implemented", "Load Macro feature is not yet implemented.")

    def play_macro(self):
        if not self.recorded_macro:
            self.log_to_console("No macro recorded.")
            return

        self.log_to_console(f"Playing back {len(self.recorded_macro)} actions...")
        for action, *params in self.recorded_macro:
            if action == 'insert':
                index, text = params
                self.prompt_text.insert(index, text)
            elif action == 'delete':
                start, end = params
                self.prompt_text.delete(start, end)
        self.log_to_console("Macro playback finished.")

    def launch_haba_editor(self):
        haba_editor = HabaEditor(tk.Toplevel(self.master))

    def open_config_dialog(self, event=None):
        """Open OAuth configuration dialog for demo window"""
        dialog = ConfigDialog(self, self.config_manager)
        # Dialog manages its own saving, but we need to update the menu
        self.menu_bar.update_external_models_menu()


    def connect_external_model(self):
        """Connect to external model using OAuth for demo window"""
        if not self.active_profile_name:
            messagebox.showwarning("No Profile Selected", "Please select an active profile from the External Models menu or configure one first.")
            return

        config = self.config_manager.get_config(self.active_profile_name)
        if not config:
            messagebox.showerror("Configuration Error", f"Could not load configuration for profile: {self.active_profile_name}")
            return
        
        try:
            # Create OAuth client with the selected profile's configuration
            self.external_model_client = OAuthClient(config, provider_name=self.active_profile_name)
            
            # Check if already authenticated
            if self.external_model_client.is_authenticated():
                status = self.external_model_client.get_auth_status()
                messagebox.showinfo("Already Authenticated", 
                    f"Already authenticated with '{self.active_profile_name}'.\n"
                    f"Token expires in {status.get('expires_in_minutes', 'unknown')} minutes.")
                return
            
            # Start OAuth flow
            self.log_to_console(f"Starting OAuth authentication for '{self.active_profile_name}'...")
            httpd = self.external_model_client.initiate_authorization()
            self.after(100, self.check_auth_status, httpd)
            
        except Exception as e:
            messagebox.showerror("Authentication Error", f"Failed to start authentication: {e}")
            self.log_to_console(f"Authentication error: {e}")

    def check_auth_status(self, httpd):
        """Check OAuth authentication status with timeout for demo window"""
        if httpd.auth_code or httpd.error:
            # Authentication completed (success or failure)
            success = self.external_model_client.finish_authorization(httpd)
            if success:
                status = self.external_model_client.get_auth_status()
                messagebox.showinfo("Authentication Successful", 
                    f"External model authenticated successfully!\n"
                    f"Token expires in {status.get('expires_in_minutes', 'unknown')} minutes.")
                self.log_to_console("OAuth authentication successful.")
            else:
                messagebox.showwarning("Authentication Failed", 
                    "Could not authenticate with the external model. Please check your configuration.")
                self.log_to_console("OAuth authentication failed.")
        else:
            # Still waiting for callback
            self.after(100, self.check_auth_status, httpd)

    def disconnect_external_model(self):
        """Disconnect and clear OAuth tokens for demo window"""
        if hasattr(self, 'external_model_client') and self.external_model_client:
            self.external_model_client.logout()
            messagebox.showinfo("Disconnected", f"Disconnected from '{self.external_model_client.provider_name}' and cleared tokens.")
            self.log_to_console(f"External model '{self.external_model_client.provider_name}' disconnected.")
            self.external_model_client = None
        else:
            messagebox.showinfo("Not Connected", "No external model connection to disconnect.")

    def check_auth_status_info(self):
        """Display current authentication status for demo window"""
        if not hasattr(self, 'external_model_client') or not self.external_model_client:
            messagebox.showinfo("Authentication Status", "No external model client configured or connected.")
            return
        
        status = self.external_model_client.get_auth_status()
        if status["authenticated"]:
            expires_info = ""
            if "expires_in_minutes" in status:
                expires_info = f"\nToken expires in {status['expires_in_minutes']} minutes"
            messagebox.showinfo("Authentication Status", f"✓ Authenticated to '{self.external_model_client.provider_name}'{expires_info}")
        else:
            messagebox.showinfo("Authentication Status", f"✗ Not authenticated to '{self.external_model_client.provider_name}'")

# --- HabaEditor and other classes remain unchanged for now ---

def lint_javascript_text(script_text_widget):
    """
    Performs linting on the given script text widget for JavaScript code.
    """
    # Clear existing tags
    for tag in ["trailing_whitespace", "missing_semicolon", "use_of_var", "use_of_double_equals", "long_line", "many_parameters"]:
        script_text_widget.tag_remove(tag, "1.0", tk.END)

    lines = script_text_widget.get("1.0", tk.END).splitlines()
    for i, line in enumerate(lines):
        line_num_str = f"{i + 1}"

        # Check for long lines (e.g., > 80 characters)
        if len(line) > 80:
            script_text_widget.tag_add("long_line", f"{line_num_str}.0", f"{line_num_str}.{len(line)}")

        # Check for trailing whitespace
        match = re.search(r'(\s+)$', line)
        if match:
            start_pos = match.start(1)
            script_text_widget.tag_add("trailing_whitespace", f"{line_num_str}.{start_pos}", f"{line_num_str}.{len(line)}")

        # Check for `var` keyword
        for match in re.finditer(r'\bvar\b', line):
            script_text_widget.tag_add("use_of_var", f"{line_num_str}.{match.start()}", f"{line_num_str}.{match.end()}")

        # Check for `==` or `!=`
        comment_pos = line.find('//')
        for match in re.finditer(r'==|!=', line):
            # If there is a comment, and the match is inside it, ignore it
            if comment_pos != -1 and match.start() > comment_pos:
                continue
            script_text_widget.tag_add("use_of_double_equals", f"{line_num_str}.{match.start()}", f"{line_num_str}.{match.end()}")
        
        # Check for functions with too many parameters (e.g., > 5)
        match = re.search(r'function\s*\w*\s*\(([^)]*)\)', line)
        if match:
            params = match.group(1).split(',')
            if len(params) > 5:
                script_text_widget.tag_add("many_parameters", f"{line_num_str}.{match.start()}", f"{line_num_str}.{match.end()}")

        # Check for missing semicolon (basic heuristic)
        stripped_line = line.strip()
        if stripped_line and not stripped_line.startswith(("//", "/*")) and not stripped_line.endswith(("{", "}", ";", ",")):
            script_text_widget.tag_add("missing_semicolon", f"{line_num_str}.{len(stripped_line)-1}", f"{line_num_str}.{len(stripped_line)}")


class ConfigDialog(tk.Toplevel):
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.title("External Model OAuth Configuration")
        self.transient(parent)
        self.grab_set()

        self.config_manager = config_manager
        self.entries = {}
        self.profile_var = tk.StringVar()

        self.create_widgets()
        self.load_profiles()
        self.wait_window(self)

    def create_widgets(self):
        main_frame = tk.Frame(self, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Profile Management Section ---
        profile_frame = ttk.LabelFrame(main_frame, text="Configuration Profiles", padding=(10, 5))
        profile_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        ttk.Label(profile_frame, text="Profile:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.profile_combobox = ttk.Combobox(profile_frame, textvariable=self.profile_var)
        self.profile_combobox.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.profile_combobox.bind("<<ComboboxSelected>>", self._on_profile_select)

        profile_frame.grid_columnconfigure(1, weight=1)

        # --- Settings Section ---
        settings_frame = ttk.LabelFrame(main_frame, text="Profile Settings", padding=(10, 5))
        settings_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.fields = {
            "client_id": "Client ID:", "client_secret": "Client Secret:",
            "authorization_url": "Authorization URL:", "token_url": "Token URL:",
            "api_base_url": "API Base URL:", "scopes": "Scopes (comma-separated):",
            "redirect_uri": "Redirect URI:", "use_pkce": "Use PKCE:"
        }

        for i, (key, text) in enumerate(self.fields.items()):
            label = ttk.Label(settings_frame, text=text)
            label.grid(row=i, column=0, sticky="w", pady=2, padx=5)
            
            if key == "use_pkce":
                var = tk.BooleanVar()
                entry = ttk.Checkbutton(settings_frame, variable=var)
                entry.var = var
            else:
                entry = ttk.Entry(settings_frame, width=60)
            
            entry.grid(row=i, column=1, sticky="ew", pady=2, padx=5)
            self.entries[key] = entry

        settings_frame.grid_columnconfigure(1, weight=1)

        # --- Action Buttons ---
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=2, column=1, sticky="e", pady=10)

        self.save_button = ttk.Button(button_frame, text="Save Profile", command=self._save_profile)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = ttk.Button(button_frame, text="Delete Profile", command=self._delete_profile)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        close_button = ttk.Button(button_frame, text="Close", command=self.destroy)
        close_button.pack(side=tk.LEFT, padx=5)

    def load_profiles(self):
        profiles = self.config_manager.get_profile_names()
        self.profile_combobox['values'] = ["<New Profile>"] + profiles
        if profiles:
            self.profile_combobox.set(profiles[0])
        else:
            self.profile_combobox.set("<New Profile>")
        self._on_profile_select()

    def _on_profile_select(self, event=None):
        profile_name = self.profile_var.get()
        if profile_name == "<New Profile>":
            self._clear_form()
            self.delete_button.config(state="disabled")
        else:
            config = self.config_manager.get_config(profile_name)
            if config:
                self._populate_form(config)
                self.delete_button.config(state="normal")

    def _clear_form(self):
        for key, entry in self.entries.items():
            if key == "use_pkce":
                entry.var.set(True)
            else:
                entry.delete(0, tk.END)
        # Set default values for new profiles
        self.entries["scopes"].insert(0, "read")
        self.entries["redirect_uri"].insert(0, "http://localhost:8080/callback")

    def _populate_form(self, config):
        for key, entry in self.entries.items():
            value = config.get(key)
            if key == "use_pkce":
                entry.var.set(value if isinstance(value, bool) else True)
            else:
                entry.delete(0, tk.END)
                if value:
                    # Join list of scopes back into a string
                    if key == "scopes" and isinstance(value, list):
                        entry.insert(0, ", ".join(value))
                    else:
                        entry.insert(0, value)

    def _save_profile(self):
        profile_name = self.profile_var.get()
        if not profile_name or profile_name == "<New Profile>":
            messagebox.showerror("Invalid Name", "Please enter a profile name.", parent=self)
            return

        config_data = {}
        for key, entry in self.entries.items():
            if key == "use_pkce":
                config_data[key] = entry.var.get()
            elif key == "scopes":
                scopes_str = entry.get().strip()
                config_data[key] = [s.strip() for s in scopes_str.split(",")] if scopes_str else []
            else:
                config_data[key] = entry.get().strip()

        if self.config_manager.save_config(profile_name, config_data):
            messagebox.showinfo("Success", f"Profile '{profile_name}' saved successfully.", parent=self)
            self.load_profiles() # Refresh list
            self.profile_combobox.set(profile_name) # Keep the saved profile selected
        else:
            messagebox.showerror("Error", "Failed to save profile.", parent=self)

    def _delete_profile(self):
        profile_name = self.profile_var.get()
        if not profile_name or profile_name == "<New Profile>":
            messagebox.showwarning("No Profile Selected", "Please select a profile to delete.", parent=self)
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the profile '{profile_name}'?", parent=self):
            if self.config_manager.delete_config(profile_name):
                messagebox.showinfo("Success", f"Profile '{profile_name}' deleted.", parent=self)
                self.load_profiles() # Refresh list and select "<New Profile>"
            else:
                messagebox.showerror("Error", f"Failed to delete profile '{profile_name}'.", parent=self)


class HabaEditor(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Haba Editor")
        self.pack(fill=tk.BOTH, expand=True)

        # Initialize managers and variables
        self.config_manager = ConfigManager()
        self.parser = HabaParser()
        self.script_runner = ScriptRunner()
        self.html_exporter = HtmlExporter()
        self.language = 'javascript' # Default language for the script panel
        self.external_model_client = None
        self.active_profile_name = None
        self.external_model_config = {}
        self.demo_window = None
        self.create_widgets()
        self.menu_bar = MenuBar(self)

    def open_config_dialog(self, event=None):
        dialog = ConfigDialog(self, self.config_manager)
        # Dialog is now self-contained, but we should update the menu
        # in case profiles were added/deleted.
        self.menu_bar.update_external_models_menu()

    def create_widgets(self):
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
        self.script_text.bind("<<Modified>>", self.on_script_text_change)
        main_paned_window.add(script_frame, stretch="always")

        # Configure tags for linting
        self.script_text.tag_configure("trailing_whitespace", background="orange red")
        self.script_text.tag_configure("missing_semicolon", background="yellow")
        self.script_text.tag_configure("use_of_var", background="#FFDDC1") # Light orange
        self.script_text.tag_configure("use_of_double_equals", background="#C1FFD7") # Light green
        self.script_text.tag_configure("long_line", background="#E0E0E0") # Light grey
        self.script_text.tag_configure("many_parameters", background="#FFC1F5") # Light pink

        # Bind keyboard shortcut for config dialog
        self.master.bind("<Control-m>", self.open_config_dialog)


    def on_text_change(self, event=None):
        self.render_preview()
        self.raw_text.edit_modified(False)

    def on_script_text_change(self, event=None):
        if not self.script_text.edit_modified():
            return
        script_content = self.script_text.get("1.0", tk.END)
        self.symbol_outline_panel.update_symbols(script_content, self.language)
        self.todo_explorer_panel.update_todos(script_content, self.language)
        self.lint_script_text()
        self.script_text.edit_modified(False)

    def connect_external_model(self):
        if not self.active_profile_name:
            messagebox.showwarning("No Profile Selected", "Please select an active profile from the External Models menu or configure one first.")
            return

        config = self.config_manager.get_config(self.active_profile_name)
        if not config:
            messagebox.showerror("Configuration Error", f"Could not load configuration for profile: {self.active_profile_name}")
            return
        
        try:
            # Create OAuth client with the selected profile's configuration
            self.external_model_client = OAuthClient(config, provider_name=self.active_profile_name)
            
            # Check if already authenticated
            if self.external_model_client.is_authenticated():
                status = self.external_model_client.get_auth_status()
                messagebox.showinfo("Already Authenticated", 
                    f"Already authenticated with '{self.active_profile_name}'.\n"
                    f"Token expires in {status.get('expires_in_minutes', 'unknown')} minutes.")
                return
            
            # Start OAuth flow
            self.log_to_console(f"Starting OAuth authentication for '{self.active_profile_name}'...")
            httpd = self.external_model_client.initiate_authorization()
            self.after(100, self.check_auth_status, httpd)
            
        except Exception as e:
            messagebox.showerror("Authentication Error", f"Failed to start authentication: {e}")
            self.log_to_console(f"Authentication error: {e}")

    def check_auth_status(self, httpd):
        """Check OAuth authentication status with timeout"""
        if httpd.auth_code or httpd.error:
            # Authentication completed (success or failure)
            success = self.external_model_client.finish_authorization(httpd)
            if success:
                status = self.external_model_client.get_auth_status()
                messagebox.showinfo("Authentication Successful", 
                    f"External model authenticated successfully!\n"
                    f"Token expires in {status.get('expires_in_minutes', 'unknown')} minutes.")
                self.log_to_console("OAuth authentication successful.")
            else:
                messagebox.showwarning("Authentication Failed", 
                    "Could not authenticate with the external model. Please check your configuration.")
                self.log_to_console("OAuth authentication failed.")
        else:
            # Still waiting for callback
            self.after(100, self.check_auth_status, httpd)

    def disconnect_external_model(self):
        """Disconnect and clear OAuth tokens"""
        if self.external_model_client:
            provider_name = self.external_model_client.provider_name
            self.external_model_client.logout()
            messagebox.showinfo("Disconnected", f"Disconnected from '{provider_name}' and cleared tokens.")
            self.log_to_console(f"External model '{provider_name}' disconnected.")
            self.external_model_client = None
        else:
            messagebox.showinfo("Not Connected", "No external model connection to disconnect.")

    def check_auth_status_info(self):
        """Display current authentication status"""
        if not self.external_model_client:
            messagebox.showinfo("Authentication Status", "No external model client configured or connected.")
            return
        
        status = self.external_model_client.get_auth_status()
        if status["authenticated"]:
            expires_info = ""
            if "expires_in_minutes" in status:
                expires_info = f"\nToken expires in {status['expires_in_minutes']} minutes"
            messagebox.showinfo("Authentication Status", f"✓ Authenticated to '{self.external_model_client.provider_name}'{expires_info}")
        else:
            messagebox.showinfo("Authentication Status", f"✗ Not authenticated to '{self.external_model_client.provider_name}'")

    def launch_quanta_demo(self):
        if self.demo_window and self.demo_window.winfo_exists():
            self.demo_window.lift()
            return
        self.demo_window = QuantaDemoWindow(self.master, external_model_client=self.external_model_client)

    def lint_script_text(self):
        lint_javascript_text(self.script_text)

    def run_script(self):
        """
        Runs the script and updates the console and task panels.
        """
        haba_content = self.raw_text.get("1.0", tk.END)
        
        # Check if run_button exists before trying to use it
        if hasattr(self, 'run_button'):
            self.run_button.config(state=tk.DISABLED, text="Running...")
            self.update()

        logs, tasks = self.script_runner.run_script(haba_content)

        # Re-enable the button if it exists
        if hasattr(self, 'run_button'):
            self.run_button.config(state=tk.NORMAL, text="Run Script")

        # Update console output panel
        self.console_output_text.config(state=tk.NORMAL)
        self.console_output_text.delete("1.0", tk.END)
        for log in logs:
            self.console_output_text.insert(tk.END, f"{log}\n")
        self.console_output_text.config(state=tk.DISABLED)

        # Update actionable tasks panel
        self.tasks_listbox.delete(0, tk.END)
        for task in tasks:
            self.tasks_listbox.insert(tk.END, f"[{task['type'].upper()}] {task['description']}")

    def log_to_console(self, message):
        """Log a message to the console panel for HabaEditor"""
        if hasattr(self, 'console_output_text'):
            self.console_output_text.config(state=tk.NORMAL)
            self.console_output_text.insert(tk.END, message + "\n")
            self.console_output_text.see(tk.END)
            self.console_output_text.config(state=tk.DISABLED)
        else:
            print(f"Console: {message}")  # Fallback to stdout

    def load_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Haba Files", "*.haba"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        self.current_filepath = filepath
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

    def export_html(self):
        """
        Exports the current .haba content to an HTML file.
        """
        try:
            # Parse the current content
            raw_content = self.raw_text.get("1.0", tk.END)
            haba_data = self.parser.parse(raw_content)
            
            # Get the script content from the script editor
            script_content = self.script_text.get("1.0", tk.END)
            haba_data.script = script_content.strip()
            
            # Ask user for output file
            filepath = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")],
                title="Export to HTML"
            )
            
            if not filepath:
                return
            
            # Export to HTML
            title = os.path.splitext(os.path.basename(filepath))[0]
            self.html_exporter.export_to_file(haba_data, filepath, title)
            
            # Show success message
            messagebox.showinfo("Export Successful", f"HTML file exported successfully to:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export HTML:\n{str(e)}")

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
    root.title("Haba Editor")
    app = HabaEditor(master=root)

    # Check for command-line arguments
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if os.path.exists(filepath):
            try:
                app.current_filepath = filepath
                with open(filepath, "r") as f:
                    content = f.read()
                app.raw_text.delete("1.0", tk.END)
                app.raw_text.insert("1.0", content)
                app.render_preview()
            except Exception as e:
                messagebox.showerror("File Load Error", f"Could not load file: {e}")
        else:
            messagebox.showwarning("File Not Found", f"The specified file does not exist: {filepath}")

    root.mainloop()

if __name__ == '__main__':
    main()
