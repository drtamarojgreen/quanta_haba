import re
import tkinter as tk

def lint_javascript(script_text_widget):
    """
    Performs linting on the script text widget for JavaScript code.
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
