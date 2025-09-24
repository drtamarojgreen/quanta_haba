import tkinter as tk
from tkinter import ttk, filedialog, font as tkFont, messagebox
import re
import os
import numpy as np
try:
    from quanta_tissu.tisslm.core.model import QuantaTissu
    from quanta_tissu.tisslm.core.tokenizer import Tokenizer
    from quanta_tissu.tisslm.core.generate_text import generate_text
    from quanta_tissu.tisslm.config import model_config
    QUANTA_TISSU_AVAILABLE = True
except ImportError:
    QUANTA_TISSU_AVAILABLE = False


class QuantaDemoWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Quanta Haba Demo")
        self.geometry("1000x700")
        
        # Initialize variables
        self.model = None
        self.tokenizer = None
        self.work_products = []
        
        # Create widgets first, then initialize model
        self.create_widgets()
        self.initialize_model()
        
        # Start demo after everything is set up
        self.after(500, self.start_quanta_demo)

    def initialize_model(self):
        if not QUANTA_TISSU_AVAILABLE:
            self.log_to_console("Error: `quanta_tissu` package not found. Demo will use stubbed responses.")
            return

        # Get the absolute path to the models directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        models_dir = os.path.join(project_root, "models")
        
        TOKENIZER_PATH = models_dir  # The tokenizer files are in the models directory
        CHECKPOINT_PATH = os.path.join(models_dir, "quanta_tissu.npz")

        try:
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
        try:
            prompt_file_path = os.path.join(os.path.dirname(__file__), 'default_prompt.txt')
            with open(prompt_file_path, "r") as f:
                content = f.read()
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert("1.0", content)
            self.log_to_console(f"Loaded prompt file: {prompt_file_path}")
            self.after(500, self.process_next_task)
        except FileNotFoundError:
            self.log_to_console(f"Error: 'default_prompt.txt' not found in 'src/p/'.")
            self.prompt_text.insert("1.0", "Error: 'default_prompt.txt' not found in 'src/p/'.")

    def process_next_task(self):
        content = self.prompt_text.get("1.0", tk.END)
        lines = content.splitlines()

        task_line_index = -1
        for i, line in enumerate(lines):
            if line.strip().startswith("TODO:"):
                task_line_index = i
                break

        if task_line_index == -1:
            self.log_to_console("All tasks completed!")
            return

        line_text = lines[task_line_index]
        task = line_text.strip().replace("TODO:", "").strip()
        line_num_str = f"{task_line_index + 1}"

        self.prompt_text.tag_remove("highlight", "1.0", tk.END)
        self.prompt_text.tag_add("highlight", f"{line_num_str}.0", f"{line_num_str}.end")
        self.log_to_console(f"Processing task: {task}")

        self.call_quanta_model(task, task_line_index)

    def call_quanta_model(self, task, line_index):
        import datetime
        
        # Generate model response
        if self.model and self.tokenizer:
            try:
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
            model_response = f"Stubbed response for '{task}'"
            is_stubbed = True

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

        self.after(1000, self.process_next_task)


# Handle both relative and absolute imports
try:
    from .haba_parser import HabaParser, HabaData
    from .components import SymbolOutlinePanel, TodoExplorerPanel
    from .script_runner import ScriptRunner
    from .html_exporter import HtmlExporter
except ImportError:
    from haba_parser import HabaParser, HabaData
    from components import SymbolOutlinePanel, TodoExplorerPanel
    from script_runner import ScriptRunner
    from html_exporter import HtmlExporter

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


class HabaEditor(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Haba Editor")
        self.pack(fill=tk.BOTH, expand=True)
        self.parser = HabaParser()
        self.script_runner = ScriptRunner()
        self.html_exporter = HtmlExporter()
        self.language = 'javascript' # Default language for the script panel
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

        self.run_button = tk.Button(top_frame, text="Run Script", command=self.run_script)
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.export_button = tk.Button(top_frame, text="Export HTML", command=self.export_html)
        self.export_button.pack(side=tk.LEFT, padx=5)

        self.quanta_demo_button = tk.Button(top_frame, text="Quanta Demo", command=self.launch_quanta_demo)
        self.quanta_demo_button.pack(side=tk.LEFT, padx=5)

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

    def launch_quanta_demo(self):
        demo_window = QuantaDemoWindow(self.master)

    def lint_script_text(self):
        lint_javascript_text(self.script_text)

    def run_script(self):
        """
        Runs the script and updates the console and task panels.
        """
        haba_content = self.raw_text.get("1.0", tk.END)
        
        # To show that the process is running, you could disable the button
        self.run_button.config(state=tk.DISABLED, text="Running...")
        self.update()

        logs, tasks = self.script_runner.run_script(haba_content)

        # Re-enable the button
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
    # Hide the root window
    root.withdraw()
    app = QuantaDemoWindow(master=root)
    app.mainloop()

if __name__ == '__main__':
    main()