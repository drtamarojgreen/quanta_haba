#ifndef EDITOR_LOGIC_H
#define EDITOR_LOGIC_H

#include <string>
#include <vector>

struct EditorState {
    std::string file_path;
    std::vector<std::string> lines;
    int cursor_line = 0;
    bool ci_mode = false;
};

void toggle_comment(EditorState& state);
std::string generate_guard_symbol(const std::string& file_path);
void add_include_guard(EditorState& state);

#endif
