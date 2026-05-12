#include "EditorLogic.h"
#include <algorithm>
#include <cctype>

void toggle_comment(EditorState& state) {
    if (state.cursor_line < 0 || state.cursor_line >= (int)state.lines.size()) {
        return;
    }
    std::string& line = state.lines[state.cursor_line];
    if (line.rfind("//", 0) == 0) {
        line = line.substr(2);
    } else {
        line = "//" + line;
    }
}

std::string generate_guard_symbol(const std::string& file_path) {
    std::string uppercase_path = file_path;
    std::transform(uppercase_path.begin(), uppercase_path.end(), uppercase_path.begin(), ::toupper);
    std::replace_if(uppercase_path.begin(), uppercase_path.end(), [](char c) { return !std::isalnum(c); }, '_');
    return uppercase_path;
}

void add_include_guard(EditorState& state) {
    std::string file_path = state.file_path;
    if (file_path.size() < 3 || (file_path.substr(file_path.size() - 2) != ".h" && file_path.substr(file_path.size() - 4) != ".hpp")) {
        return;
    }

    std::string guard_symbol = generate_guard_symbol(file_path);

    state.lines.insert(state.lines.begin(), "#ifndef " + guard_symbol);
    state.lines.insert(state.lines.begin() + 1, "#define " + guard_symbol);
    state.lines.push_back("#endif // " + guard_symbol);

    state.cursor_line += 2;
}
