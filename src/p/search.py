import tkinter as tk
import re

def highlight_decorators(text_widget):
    """Applies syntax highlighting for Python decorators."""
    text_widget.tag_remove("decorator", "1.0", tk.END)
    lines = text_widget.get("1.0", "end-1c").splitlines()
    for i, line in enumerate(lines):
        if re.match(r"^\s*@", line):
            line_num = i + 1
            text_widget.tag_add("decorator", f"{line_num}.0", f"{line_num}.end")

def highlight_trailing_whitespace(text_widget):
    """Finds and highlights trailing whitespace on each line."""
    text_widget.tag_remove("trailing_whitespace", "1.0", tk.END)
    lines = text_widget.get("1.0", "end-1c").splitlines()
    for i, line in enumerate(lines):
        match = re.search(r'(\s+)$', line)
        if match:
            line_num = i + 1
            start_col = match.start(1)
            end_col = match.end(1)
            text_widget.tag_add("trailing_whitespace", f"{line_num}.{start_col}", f"{line_num}.{end_col}")

def update_file_stats(text_widget, stats_label):
    """Calculates and displays file statistics in the provided label."""
    content = text_widget.get("1.0", "end-1c")
    if not content:
        line_count = 0
        word_count = 0
    else:
        line_count = content.count('\n') + 1
        word_count = len(content.split())
    stats_text = f"Lines: {line_count} | Words: {word_count}"
    stats_label.config(text=stats_text)

def check_indentation_consistency(text_widget, indent_warning_label):
    """Checks for mixed tabs and spaces and updates a warning label."""
    lines = text_widget.get("1.0", "end-1c").splitlines()
    uses_tabs = False
    uses_spaces = False
    for line in lines:
        if not line: continue
        if line[0] == ' ': uses_spaces = True
        elif line[0] == '\t': uses_tabs = True
        if uses_tabs and uses_spaces: break
    if uses_tabs and uses_spaces:
        indent_warning_label.config(text="[Warning: Mixed Tabs and Spaces]")
    else:
        indent_warning_label.config(text="")

def check_magic_comment(text_widget):
    """Checks for misplaced magic encoding comments."""
    text_widget.tag_remove("magic_comment_warning", "1.0", tk.END)
    lines = text_widget.get("1.0", "end-1c").splitlines()
    for i, line in enumerate(lines):
        line_num = i + 1
        if re.search(r"# -\*- coding: .*- -\*-", line) and line_num > 2:
            text_widget.tag_add("magic_comment_warning", f"{line_num}.0", f"{line_num}.end")

def check_main_guard(text_widget, main_guard_hint_label):
    """Checks if a __name__ == '__main__' guard might be needed."""
    lines = text_widget.get("1.0", "end-1c").splitlines()
    has_defs = any(line.strip().startswith(('def ', 'class ')) for line in lines)
    has_main_guard = any('if __name__' in line and '__main__' in line for line in lines)
    has_toplevel_code = any(
        not line.startswith((' ', '\t', '#', 'import ', 'from ', 'def ', 'class ')) and line.strip()
        for line in lines
    )
    if has_defs and has_toplevel_code and not has_main_guard:
        main_guard_hint_label.config(text="Hint: Consider `if __name__ == '__main__'` guard")
    else:
        main_guard_hint_label.config(text="")

def find_and_highlight_matching_bracket(text_widget):
    """Finds and highlights the matching bracket to the one under the cursor."""
    text_widget.tag_remove("bracket_match", "1.0", "end")
    cursor_index = text_widget.index(tk.INSERT)
    char_before_index = f"{cursor_index}-1c"
    char = text_widget.get(char_before_index)
    pairs = {'(': ')', '[': ']', '{': '}'}
    if char in pairs:
        match_char, direction = pairs[char], 1
    elif char in pairs.values():
        match_char, direction = [k for k, v in pairs.items() if v == char][0], -1
    else:
        return
    balance = direction
    search_index = text_widget.index(f"{char_before_index} + {direction}c")
    while True:
        if direction == 1 and text_widget.compare(search_index, ">=", "end"): break
        if direction == -1 and text_widget.compare(search_index, "<", "1.0"): break
        current_char = text_widget.get(search_index)
        if current_char == char: balance += direction
        elif current_char == match_char: balance -= direction
        if balance == 0:
            text_widget.tag_add("bracket_match", char_before_index, f"{char_before_index}+1c")
            text_widget.tag_add("bracket_match", search_index, f"{search_index}+1c")
            break
        search_index = text_widget.index(f"{search_index} + {direction}c")

def generate_docstring_stub(text_widget):
    """Generates and inserts a docstring stub after a function definition."""
    cursor_index = text_widget.index(tk.INSERT)
    line_num, _ = map(int, cursor_index.split('.'))
    if line_num <= 1: return
    prev_line_text = text_widget.get(f"{line_num - 1}.0", f"{line_num - 1}.end")
    match = re.search(r"^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\):", prev_line_text)
    if not match: return
    func_name, args_str = match.group(1), match.group(2)
    params = [p.split('=')[0].split(':')[0].strip() for p in args_str.split(',') if p.strip() and p.strip() != 'self']
    indent = re.match(r"^\s*", prev_line_text).group(0)
    stub = f'{indent}"""{func_name}: One-line summary of the function.\n\n'
    if params:
        stub += f"{indent}Args:\n"
        for param in params:
            stub += f"{indent}    {param}: Description of the parameter.\n"
    stub += f"\n{indent}Returns:\n{indent}    Description of the return value.\n{indent}\"\"\""
    text_widget.delete(f"{line_num}.0", f"{line_num}.end")
    text_widget.insert(f"{line_num}.0", stub)

def highlight_old_string_formats(text_widget):
    """Highlights old-style string formatting (`%` and `.format()`)."""
    text_widget.tag_remove("old_string_format", "1.0", tk.END)
    lines = text_widget.get("1.0", "end-1c").splitlines()
    for i, line in enumerate(lines):
        line_num = i + 1
        for match in re.finditer(r'\.format\s*\(', line):
            text_widget.tag_add("old_string_format", f"{line_num}.{match.start()}", f"{line_num}.{match.end()}")
        for match in re.finditer(r'(".*?"|\'.*?\')\s*%', line):
            next_char = line[match.end(0):].lstrip()
            if next_char and next_char[0] in '=(,':
                text_widget.tag_add("old_string_format", f"{line_num}.{match.end() - 1}", f"{line_num}.{match.end()}")


def convert_to_f_strings(full_text_content):
    """
    Converts simple .format() and %-style string formatting to f-strings.
    This is a basic implementation and does not handle all edge cases.
    """
    lines = full_text_content.splitlines()
    new_lines = []

    for line in lines:
        # --- Handle .format() ---
        # Matches "..." or '...'.format(var1, var2)
        match = re.search(r'(["\'])(.*?)\1\.format\((.*?)\)', line)
        if match:
            quote_char = match.group(1)
            original_string_content = match.group(2)
            args = [arg.strip() for arg in match.group(3).split(',')]

            # This simple version just replaces {} with the variables in order
            new_string_content = original_string_content
            for i, arg in enumerate(args):
                new_string_content = new_string_content.replace('{}', f'{{{arg}}}', 1)

            # Construct the new f-string
            new_f_string = f'f{quote_char}{new_string_content}{quote_char}'

            # Replace the whole .format() expression
            line = line.replace(match.group(0), new_f_string)

        # --- Handle %-formatting ---
        # Matches "..." % var or "..." % (var1, var2)
        match = re.search(r'(["\'])(.*?)\1\s*%\s*\(?(.*?)\)?$', line.strip())
        if match and any(spec in match.group(2) for spec in ['%s', '%d', '%r', '%f']):
            quote_char = match.group(1)
            original_string_content = match.group(2)
            args_str = match.group(3)
            # Handle single variable case where there are no parens
            if ',' not in args_str and ' ' not in args_str:
                args = [args_str.strip()]
            else:
                args = [arg.strip() for arg in args_str.split(',')]

            new_string_content = original_string_content
            for arg in args:
                # Replace the first available format specifier
                new_string_content = re.sub(r'%[sdfr]', f'{{{arg}}}', new_string_content, 1)

            new_f_string = f'f{quote_char}{new_string_content}{quote_char}'
            line = line.replace(match.group(0), new_f_string)

        new_lines.append(line)

    return "\n".join(new_lines)
