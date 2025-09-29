#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <iomanip>
#include <algorithm>
#include <cctype>
#include <limits>

// Represents the state of the editor
struct EditorState {
    std::string file_path;
    std::vector<std::string> lines;
    int cursor_line = 0;
};

void print_usage() {
    std::cout << "Usage: cli_editor <file_path>" << std::endl;
}

void display_file(const EditorState& state) {
    const std::string red_bg = "\033[41m";
    const std::string reset_color = "\033[0m";

    system("clear");
    std::cout << "--- Haba CLI Editor ---" << std::endl;
    std::cout << "File: " << state.file_path << std::endl;
    std::cout << "-----------------------" << std::endl;
    for (int i = 0; i < state.lines.size(); ++i) {
        std::string line_to_display = state.lines[i];
        size_t last_char = line_to_display.find_last_not_of(" \t");
        if (last_char != std::string::npos && last_char < line_to_display.length() - 1) {
            line_to_display.insert(last_char + 1, red_bg);
            line_to_display += reset_color;
        }

        if (i == state.cursor_line) {
            std::cout << std::setw(4) << std::right << i + 1 << " > " << line_to_display << std::endl;
        } else {
            std::cout << std::setw(4) << std::right << i + 1 << " | " << line_to_display << std::endl;
        }
    }
    std::cout << "-----------------------" << std::endl;
    std::cout << "Commands:" << std::endl;
    std::cout << "  :q        - Quit the editor" << std::endl;
    std::cout << "  :w        - Write (save) the file" << std::endl;
    std::cout << "  :n / :p   - Navigate down / up" << std::endl;
    std::cout << "  :comment  - Toggle comment on the current line" << std::endl;
    std::cout << "  :guard    - Add include guards (for .h/.hpp files)" << std::endl;
    std::cout << "  :demo     - Run the Quanta model demo on TODOs" << std::endl;
    std::cout << "  (any other text) - Insert line below cursor" << std::endl;
}

void save_file(const EditorState& state) {
    std::ofstream outfile(state.file_path);
    for (const auto& l : state.lines) {
        outfile << l << std::endl;
    }
    outfile.close();
    std::cout << "File saved." << std::endl;
}

void toggle_comment(EditorState& state) {
    if (state.cursor_line < 0 || state.cursor_line >= state.lines.size()) {
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
        std::cout << "Not a header file (.h or .hpp)." << std::endl;
        return;
    }

    std::string guard_symbol = generate_guard_symbol(file_path);

    state.lines.insert(state.lines.begin(), "#ifndef " + guard_symbol);
    state.lines.insert(state.lines.begin() + 1, "#define " + guard_symbol);
    state.lines.push_back("#endif // " + guard_symbol);

    state.cursor_line += 2;
}

/**
 * @brief Simulates a call to the Quanta model.
 * @param task The task description to send to the model.
 * @return A stubbed model response.
 */
std::string call_quanta_model(const std::string& task) {
    std::cout << "  > Model processing task: '" << task << "'" << std::endl;
    // In a real scenario, this would involve a complex operation.
    // Here, we just return a fixed, stubbed response.
    return "Completed: " + task;
}

/**
 * @brief Runs the model demo on the currently loaded lines.
 * @param state The current editor state.
 */
void run_model_demo(EditorState& state) {
    std::cout << "--- Running Quanta Model Demo ---" << std::endl;
    bool task_found = false;
    for (size_t i = 0; i < state.lines.size(); ++i) {
        std::string& line = state.lines[i];
        size_t todo_pos = line.find("TODO:");
        if (todo_pos != std::string::npos) {
            task_found = true;
            std::string task = line.substr(todo_pos + 5);
            task.erase(0, task.find_first_not_of(" \t")); // Trim whitespace

            std::string model_response = call_quanta_model(task);

            line.replace(todo_pos, 5, "DONE:");
            line += " // " + model_response;
        }
    }

    if (task_found) {
        std::cout << "--- Model Demo Finished ---" << std::endl;
    } else {
        std::cout << "No 'TODO:' tasks found to process." << std::endl;
    }

    // Pause to allow user to see the output
    std::cout << "Press Enter to continue..." << std::endl;
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
}

void process_command(const std::string& command, EditorState& state, bool& running) {
    if (command[0] == ':') {
        std::string cmd = command.substr(1);
        if (cmd == "q") {
            running = false;
        } else if (cmd == "w") {
            save_file(state);
        } else if (cmd == "n") {
            if (state.cursor_line < state.lines.size() - 1) {
                state.cursor_line++;
            }
        } else if (cmd == "p") {
            if (state.cursor_line > 0) {
                state.cursor_line--;
            }
        } else if (cmd == "comment") {
            toggle_comment(state);
        } else if (cmd == "guard") {
            add_include_guard(state);
        } else if (cmd == "demo") {
            run_model_demo(state);
        } else {
            std::cout << "Unknown command: " << cmd << std::endl;
        }
    } else {
        if (state.cursor_line >= 0 && state.cursor_line < state.lines.size()) {
            state.lines.insert(state.lines.begin() + state.cursor_line + 1, command);
            state.cursor_line++;
        } else {
            state.lines.push_back(command);
            state.cursor_line = state.lines.size() - 1;
        }
    }
}

void editor_loop(EditorState& state) {
    bool running = true;
    std::string command;

    while (running) {
        display_file(state);
        std::cout << "> ";
        std::getline(std::cin, command);
        process_command(command, state, running);
    }
}

void load_file(EditorState& state) {
    std::ifstream file(state.file_path);
    if (file.is_open()) {
        std::string line;
        while (std::getline(file, line)) {
            state.lines.push_back(line);
        }
        file.close();
    } else {
        std::cout << "File not found. A new file will be created." << std::endl;
    }
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        print_usage();
        return 1;
    }

    EditorState state;
    state.file_path = argv[1];

    load_file(state);

    editor_loop(state);

    return 0;
}
