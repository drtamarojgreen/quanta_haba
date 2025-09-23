import tkinter as tk
import subprocess
import json
import os

def lint_javascript(script_text_widget):
    """
    Performs linting on the script text widget for JavaScript code using ESLint.
    """
    # Clear existing linting tags
    for tag in script_text_widget.tag_names():
        if tag.startswith("lint_"):
            script_text_widget.tag_remove(tag, "1.0", tk.END)

    script_content = script_text_widget.get("1.0", tk.END)
    
    # ESLint needs a file to work with
    temp_filepath = "temp_script.js"
    with open(temp_filepath, "w") as f:
        f.write(script_content)

    try:
        # Path to the local eslint executable
        eslint_path = os.path.join("node_modules", ".bin", "eslint")
        
        # Run ESLint and capture JSON output
        result = subprocess.run(
            [eslint_path, temp_filepath, "--format", "json"],
            capture_output=True,
            text=True,
            check=False 
        )
        
        # Configure tags for highlighting
        script_text_widget.tag_configure("lint_error", background="#FFDDDD", underline=True, underline_color="red")
        script_text_widget.tag_configure("lint_warning", background="#FFFFD4", underline=True, underline_color="orange")

        if result.stdout:
            lint_results = json.loads(result.stdout)
            if lint_results and lint_results[0]['messages']:
                for issue in lint_results[0]['messages']:
                    line = issue.get('line', 1)
                    col_start = issue.get('column', 1) - 1
                    col_end = issue.get('endColumn', col_start + 1) -1
                    
                    tag_name = "lint_error" if issue.get('severity') == 2 else "lint_warning"
                    
                    # Add a tooltip-like message on hover
                    # Note: This requires a more complex setup, for now we just highlight
                    
                    script_text_widget.tag_add(tag_name, f"{line}.{col_start}", f"{line}.{col_end}")

    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Handle cases where eslint isn't found or output isn't valid JSON
        print(f"Error during linting: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
