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
    std::string basename = file_path.substr(file_path.find_last_of("/\\") + 1);
    std::transform(basename.begin(), basename.end(), basename.begin(), ::toupper);
    std::replace_if(basename.begin(), basename.end(), [](char c) { return !std::isalnum(c); }, '_');
    return basename + "_H";
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
