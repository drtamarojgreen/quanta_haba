import os
import sys
import tkinter as tk
from PIL import ImageGrab

# Add src/p to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'p'))

from editor import HabaEditor

def run_app_and_capture():
    # Make sure we run in a window of a good size
    root = tk.Tk()
    root.title("QuantaHaba Design Editor")
    root.geometry("1200x800")

    # Instantiate the real editor
    app = HabaEditor(master=root)

    # Load demo.haba
    demo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'demo.haba'))
    if os.path.exists(demo_path):
        app.current_filepath = demo_path
        with open(demo_path, "r") as f:
            content = f.read()
        app.raw_text.delete("1.0", tk.END)
        app.raw_text.insert("1.0", content)
        # Programmatic edit modified needs to be set to True for script panel changes to register
        app.script_text.edit_modified(True)
        app.render_preview()

    def take_screenshot():
        # Update idle tasks to make sure all widgets are drawn and styled
        root.update_idletasks()
        root.update()

        # Grab screen
        im = ImageGrab.grab()

        # Save to docs/images/demo_screenshot.png
        out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docs', 'images'))
        os.makedirs(out_dir, exist_ok=True)
        screenshot_path = os.path.join(out_dir, 'demo_screenshot.png')

        im.save(screenshot_path)
        print(f"Screenshot successfully saved to: {screenshot_path}")

        # Stop tkinter event loop and close
        root.destroy()

    # Schedule screenshot after 2 seconds to allow the GUI to fully render and lay out
    root.after(2000, take_screenshot)
    root.mainloop()

if __name__ == "__main__":
    run_app_and_capture()
