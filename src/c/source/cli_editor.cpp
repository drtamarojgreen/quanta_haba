#include <iostream>
#include <fstream>
#include <vector>
#include <string>

void print_usage() {
    std::cout << "Usage: cli_editor <file_path>" << std::endl;
}

void display_file(const std::vector<std::string>& lines) {
    for (const auto& line : lines) {
        std::cout << line << std::endl;
    }
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        print_usage();
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
        std::cout << "File not found. A new file will be created." << std::endl;
    }

    std::cout << "--- Haba CLI Editor ---" << std::endl;
    std::cout << "Type ':q' to quit, ':w' to save." << std::endl;
    std::cout << "-----------------------" << std::endl;

    display_file(lines);

    std::string command;
    while (true) {
        std::cout << ":";
        std::getline(std::cin, command);

        if (command == "q") {
            break;
        } else if (command == "w") {
            std::ofstream outfile(file_path);
            for (const auto& l : lines) {
                outfile << l << std::endl;
            }
            outfile.close();
            std::cout << "File saved." << std::endl;
        } else {
            lines.push_back(command);
        }
    }

    return 0;
}
