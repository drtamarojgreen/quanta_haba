#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include "HabaParser.h"
#include "HabaData.h"

#ifdef _WIN32
#include <windows.h>
#include <conio.h>
#else
#include <termios.h>
#include <unistd.h>
#include <sys/ioctl.h>
#endif

class TUIEditor {
private:
    std::vector<std::string> lines;
    std::string file_path;
    int cursor_x, cursor_y;
    int scroll_offset;
    std::string status_message;
    HabaParser parser;
    bool modified;
    
    enum Mode {
        EDIT_MODE,
        COMMAND_MODE,
        PREVIEW_MODE
    } current_mode;

public:
    TUIEditor(const std::string& path) : file_path(path), cursor_x(0), cursor_y(0), 
                                        scroll_offset(0), modified(false), current_mode(EDIT_MODE) {
        loadFile();
        status_message = "Haba TUI Editor - F1:Help F2:Preview F3:Export ESC:Quit";
    }

    void loadFile() {
        std::ifstream file(file_path);
        lines.clear();
        
        if (file.is_open()) {
            std::string line;
            while (std::getline(file, line)) {
                lines.push_back(line);
            }
            file.close();
        }
        
        if (lines.empty()) {
            lines.push_back("");
        }
    }

    void saveFile() {
        std::ofstream file(file_path);
        if (file.is_open()) {
            for (const auto& line : lines) {
                file << line << std::endl;
            }
            file.close();
            modified = false;
            status_message = "File saved successfully!";
        } else {
            status_message = "Error: Could not save file!";
        }
    }

    void exportHTML() {
        try {
            std::stringstream content;
            for (const auto& line : lines) {
                content << line << "\n";
            }
            
            HabaData data = parser.parse(content.str());
            std::string html = generateHTML(data);
            
            std::string html_path = file_path;
            size_t dot_pos = html_path.rfind('.');
            if (dot_pos != std::string::npos) {
                html_path.replace(dot_pos, std::string::npos, ".html");
            } else {
                html_path += ".html";
            }
            
            std::ofstream html_file(html_path);
            if (html_file.is_open()) {
                html_file << html;
                html_file.close();
                status_message = "HTML exported to: " + html_path;
            } else {
                status_message = "Error: Could not export HTML!";
            }
        } catch (const std::exception& e) {
            status_message = "Export error: " + std::string(e.what());
        }
    }

    std::string generateHTML(const HabaData& data) {
        std::stringstream html;
        
        html << "<!DOCTYPE html>\n";
        html << "<html lang=\"en\">\n";
        html << "<head>\n";
        html << "    <meta charset=\"UTF-8\">\n";
        html << "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n";
        html << "    <title>Haba Output</title>\n";
        html << "    <style>\n";
        
        for (size_t i = 0; i < data.presentation_items.size(); ++i) {
            html << "        .haba-container-" << i << " " << data.presentation_items[i].second << "\n";
        }
        
        html << "        body { font-family: Arial, sans-serif; margin: 20px; }\n";
        html << "        .haba-content { max-width: 800px; margin: 0 auto; }\n";
        html << "    </style>\n";
        html << "</head>\n";
        html << "<body>\n";
        html << "    <div class=\"haba-content\">\n";

        std::string content_with_containers = data.content;
        for (int i = data.presentation_items.size() - 1; i >= 0; --i) {
            std::stringstream temp_stream;
            std::string container_tag = data.presentation_items[i].first;
            size_t first_space = container_tag.find('>');
            if (first_space != std::string::npos) {
                container_tag.insert(first_space, " class=\"haba-container-" + std::to_string(i) + "\"");
            }

            temp_stream << container_tag << "\n" << content_with_containers << "\n";

            size_t tag_name_start = container_tag.find('<') + 1;
            size_t tag_name_end = container_tag.find_first_of(" >");
            std::string tag_name = container_tag.substr(tag_name_start, tag_name_end - tag_name_start);
            temp_stream << "</" << tag_name << ">";

            content_with_containers = temp_stream.str();
        }
        
        html << "        " << content_with_containers << "\n";
        html << "    </div>\n";

        if (!data.script.empty()) {
            html << "    <script>\n" << data.script << "\n    </script>\n";
        }

        html << "</body>\n";
        html << "</html>\n";

        return html.str();
    }

    void showPreview() {
        try {
            std::stringstream content;
            for (const auto& line : lines) {
                content << line << "\n";
            }
            
            HabaData data = parser.parse(content.str());
            
            clearScreen();
            std::cout << "=== HABA PREVIEW ===\n\n";
            std::cout << "Content:\n" << data.content << "\n\n";
            
            std::cout << "Presentation Items:\n";
            for (size_t i = 0; i < data.presentation_items.size(); ++i) {
                std::cout << "  Container " << i << ": " << data.presentation_items[i].first << "\n";
                std::cout << "  Style " << i << ": " << data.presentation_items[i].second << "\n\n";
            }
            
            if (!data.script.empty()) {
                std::cout << "Script:\n" << data.script << "\n\n";
            }
            
            std::cout << "Press any key to return to editor...";
            getch();
            
        } catch (const std::exception& e) {
            clearScreen();
            std::cout << "Parse Error: " << e.what() << "\n\n";
            std::cout << "Press any key to return to editor...";
            getch();
        }
    }

    void showHelp() {
        clearScreen();
        std::cout << "=== HABA TUI EDITOR HELP ===\n\n";
        std::cout << "Navigation:\n";
        std::cout << "  Arrow Keys    - Move cursor\n";
        std::cout << "  Home/End      - Beginning/End of line\n";
        std::cout << "  Page Up/Down  - Scroll up/down\n\n";
        std::cout << "Editing:\n";
        std::cout << "  Type          - Insert text\n";
        std::cout << "  Backspace     - Delete character\n";
        std::cout << "  Delete        - Delete character forward\n";
        std::cout << "  Enter         - New line\n\n";
        std::cout << "Commands:\n";
        std::cout << "  Ctrl+S        - Save file\n";
        std::cout << "  F1            - Show this help\n";
        std::cout << "  F2            - Preview parsed content\n";
        std::cout << "  F3            - Export to HTML\n";
        std::cout << "  ESC           - Quit editor\n\n";
        std::cout << "Press any key to return to editor...";
        getch();
    }

#ifdef _WIN32
    void clearScreen() {
        system("cls");
    }

    void setCursorPosition(int x, int y) {
        COORD coord;
        coord.X = x;
        coord.Y = y;
        SetConsoleCursorPosition(GetStdHandle(STD_OUTPUT_HANDLE), coord);
    }

    int getch() {
        return _getch();
    }
#else
    void clearScreen() {
        system("clear");
    }

    void setCursorPosition(int x, int y) {
        printf("\033[%d;%dH", y + 1, x + 1);
    }

    int getch() {
        struct termios oldt, newt;
        int ch;
        tcgetattr(STDIN_FILENO, &oldt);
        newt = oldt;
        newt.c_lflag &= ~(ICANON | ECHO);
        tcsetattr(STDIN_FILENO, TCSANOW, &newt);
        ch = getchar();
        tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
        return ch;
    }
#endif

    void display() {
        clearScreen();
        
        // Display file content
        int display_lines = 20; // Reserve space for status
        for (int i = 0; i < display_lines && (i + scroll_offset) < lines.size(); ++i) {
            setCursorPosition(0, i);
            if (i + scroll_offset < lines.size()) {
                std::cout << lines[i + scroll_offset];
            }
        }
        
        // Display status bar
        setCursorPosition(0, 22);
        std::cout << std::string(80, '-');
        setCursorPosition(0, 23);
        std::cout << status_message;
        setCursorPosition(0, 24);
        std::cout << "Line: " << (cursor_y + 1) << " Col: " << (cursor_x + 1);
        if (modified) std::cout << " [Modified]";
        
        // Set cursor to editing position
        setCursorPosition(cursor_x, cursor_y - scroll_offset);
    }

    void handleInput() {
        int ch = getch();
        
#ifdef _WIN32
        if (ch == 0 || ch == 224) { // Extended key
            ch = getch();
            switch (ch) {
                case 72: // Up arrow
                    if (cursor_y > 0) cursor_y--;
                    break;
                case 80: // Down arrow
                    if (cursor_y < lines.size() - 1) cursor_y++;
                    break;
                case 75: // Left arrow
                    if (cursor_x > 0) cursor_x--;
                    break;
                case 77: // Right arrow
                    if (cursor_x < lines[cursor_y].length()) cursor_x++;
                    break;
                case 59: // F1
                    showHelp();
                    break;
                case 60: // F2
                    showPreview();
                    break;
                case 61: // F3
                    exportHTML();
                    break;
            }
        } else
#endif
        {
            switch (ch) {
                case 27: // ESC
                    return; // Exit
                case 8: // Backspace
                case 127:
                    if (cursor_x > 0) {
                        lines[cursor_y].erase(cursor_x - 1, 1);
                        cursor_x--;
                        modified = true;
                    }
                    break;
                case 13: // Enter
                case 10:
                    lines.insert(lines.begin() + cursor_y + 1, 
                                lines[cursor_y].substr(cursor_x));
                    lines[cursor_y].erase(cursor_x);
                    cursor_y++;
                    cursor_x = 0;
                    modified = true;
                    break;
                case 19: // Ctrl+S
                    saveFile();
                    break;
                default:
                    if (ch >= 32 && ch <= 126) { // Printable characters
                        lines[cursor_y].insert(cursor_x, 1, ch);
                        cursor_x++;
                        modified = true;
                    }
                    break;
            }
        }
        
        // Adjust cursor position
        if (cursor_x > lines[cursor_y].length()) {
            cursor_x = lines[cursor_y].length();
        }
        
        // Adjust scroll
        if (cursor_y < scroll_offset) {
            scroll_offset = cursor_y;
        } else if (cursor_y >= scroll_offset + 20) {
            scroll_offset = cursor_y - 19;
        }
    }

    void run() {
        while (true) {
            display();
            handleInput();
            
            // Check if we should exit
            if (GetAsyncKeyState(VK_ESCAPE) & 0x8000) {
                break;
            }
        }
        
        if (modified) {
            clearScreen();
            std::cout << "Save changes before exiting? (y/n): ";
            char choice = getch();
            if (choice == 'y' || choice == 'Y') {
                saveFile();
            }
        }
        
        clearScreen();
        std::cout << "Haba TUI Editor exited.\n";
    }
};

int main(int argc, char *argv[]) {
    if (argc != 2) {
        std::cout << "Usage: tui_editor <file_path>" << std::endl;
        return 1;
    }

    TUIEditor editor(argv[1]);
    editor.run();
    
    return 0;
}
