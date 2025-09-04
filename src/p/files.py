import tkinter as tk
from tkinter import filedialog

class FileHandler:
    """
    Handles loading and saving of .haba files.
    """
    def __init__(self, editor):
        """
        Initializes the FileHandler.

        Args:
            editor: An instance of the HabaEditor class.
        """
        self.editor = editor

    def load_file(self):
        """
        Opens a file dialog to load a .haba file and populates the editor.
        """
        filepath = filedialog.askopenfilename(
            filetypes=[("Haba Files", "*.haba"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        self.editor.current_filepath = filepath
        with open(filepath, "r") as f:
            content = f.read()

        self.editor.display.raw_text.delete("1.0", tk.END)
        self.editor.display.raw_text.insert("1.0", content)
        self.editor.render_preview()

    def save_file(self):
        """
        Opens a file dialog to save the content of the editor to a .haba file.
        """
        filepath = filedialog.asksaveasfilename(
            defaultextension="haba",
            filetypes=[("Haba Files", "*.haba"), ("All Files", "*.*")],
        )
        if not filepath:
            return

        self.editor.current_filepath = filepath

        # Parse the raw text to get the content and presentation layers
        raw_content = self.editor.display.raw_text.get("1.0", tk.END)
        haba_data = self.editor.parser.parse(raw_content)

        # Get the script content from the script editor
        script_content = self.editor.display.script_text.get("1.0", tk.END)
        haba_data.script = script_content.strip()

        # Build the final .haba content string
        final_content = self.editor.parser.build(haba_data)

        with open(filepath, "w") as f:
            f.write(final_content)
