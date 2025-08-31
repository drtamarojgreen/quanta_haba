#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <windows.h> // For Windows console functions

// Function to clear the console screen
void clearScreen() {
    system("cls"); // For Windows
}

// Function to set the cursor position
void setCursorPosition(int x, int y) {
    COORD coord;
    coord.X = x;
    coord.Y = y;
    SetConsoleCursorPosition(GetStdHandle(STD_OUTPUT_HANDLE), coord);
}

void display_editor(const std::vector<std::string>& lines, int cursor_x, int cursor_y, const std::string& status_message) {
    clearScreen();

    // Display content
    for (size_t i = 0; i < lines.size(); ++i) {
        setCursorPosition(0, i);
        std::cout << lines[i];
    }

    // Display status bar
    setCursorPosition(0, 24); // Assuming a console height of 25 lines
    std::cout << "--------------------------------------------------------------------------------";
    setCursorPosition(0, 25); // Status message on the next line
    std::cout << status_message;

    // Set cursor to current editing position
    setCursorPosition(cursor_x, cursor_y);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        std::cout << "Usage: tui_editor <file_path>" << std::endl;
        return 1;
    }

    std::string file_path = argv[1];
    std::ifstream file(file_path);
    std::vector<std::string> lines;
    std::string line;

    if (file.is_open()) {
        while (std::getline(file, line)) {
            lines.push_back(line);
        }
        file.close();
    } else {
        lines.push_back(""); // Start with an empty line if file not found
    }

    int cursor_x = 0;
    int cursor_y = 0;
    std::string status_message = "Welcome to Haba TUI Editor! Press ESC to quit.";

    display_editor(lines, cursor_x, cursor_y, status_message);

    // Basic input loop (very simplified)
    while (true) {
        if (GetAsyncKeyState(VK_ESCAPE) & 0x8000) { // ESC key
            break;
        }
        // In a real editor, you'd handle character input, arrow keys, etc.
        // For this basic example, we'll just wait for ESC.
    }

    // Save on exit (simplified)
    std::ofstream outfile(file_path);
    for (const auto& l : lines) {
        outfile << l << std::endl;
    }
    outfile.close();

    clearScreen(); // Clear screen before exiting
    std::cout << "File saved and editor exited.\n";

    return 0;
}
